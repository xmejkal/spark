"""
The readers of the nine phases of a project (P825): each reads the files one stage wrote and says where that phase
stands, with its sentences and the offers a person or Claude may take next. A library for `show_flow`. Nothing here
writes, and no offer runs: P829 rebuilds the command from the key.
"""

import datetime
import json
from collections import namedtuple
from pathlib import Path

from spark.build.build_record import BUILD_RECORD_FILE, BuildRecordStore, sha256_of
from spark.build.stages import BUILD, SIMULATION
from spark.breadboard import sheet
from spark.design import need_requirements, needs
from spark.firmware import firmware_codes
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import flow_codes
from spark.records import records_codes, store
from spark.core.errors import CodedMessageError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS, SKIPPED
from spark.core.zone_time import stamp

# --- MVP ---
#: The project's requirements file, as every stage names it.
REQUIREMENTS_FILE = "requirements.json"
#: The firmware Claude writes, as `/spark:build`'s next step names it.
MAIN_FILE = Path("firmware") / "main.py"
#: How each status reads: (the word in a person's line, the glyph a page shows). The mark alone says ok, and None is a
#: phase with no status of its own.
MARKS = {OK: (None, "✓"), PROBLEMS: ("problems", "✗"), COULD_NOT_RUN: ("could not run", "?"),
         flow_codes.NOT_STARTED: ("not started", "○"), flow_codes.PARTIAL: ("partly done", "◐"),
         flow_codes.STALE: ("out of date", "↻"), None: (None, "·")}
#: The reasons of a ProjectImage that say only that nothing was simulated yet, each with its sentences; any other reason is a
#: problem. Never the library's own sentence: it names a store, a project and a script path (P979).
NOT_SIMULATED_SAYS = {firmware_codes.NO_SIM_TOML: [flow_codes.NO_SIM_MESSAGE],
                      firmware_codes.NO_IMAGE: [flow_codes.NO_IMAGE_MESSAGE, flow_codes.SCENARIO_HINT]}
#: Value: one offer of a phase: its key (`pick:soil:x-led`), its label (the words of its button), its effect (plain
#: sentences that name every write taking it makes) and `makes_stale`, the phases it can make out of date (P829).
Offer = namedtuple("Offer", "key label effect makes_stale")
#: The parts phase offers at most this many picks per need (P976, the PO, 2026-11-21: "so many unrelated things").
OFFERS_PER_NEED = 3
#: The verb of the need a board serves (`needs`' board need): a board is a plausible pick for it whatever its words.
COMPUTE = "compute"
#: The file whose presence says a phase holds something now, for `makes_stale`.
HELD_FILES = {flow_codes.REQUIREMENTS: Path(REQUIREMENTS_FILE), flow_codes.BUILD: BUILD_RECORD_FILE,
              flow_codes.BREADBOARD: Path(sheet.SHEET)}


class Phase(namedtuple("Phase", "phase status mark by says offers")):
    """Value: where one phase of a project stands: its name, its status (an outcome, a phase word of `flow_codes`, or None),
    its glyph from MARKS, who does it, what it says (sentences for a person; a null value reads `unknown`) and its Offers."""

    def to_dict(self):
        return dict(self._asdict(), offers=[dict(offer._asdict(), makes_stale=list(offer.makes_stale)) for offer in self.offers])


class PhaseReader:
    """
    Strategy: reads one phase of a project folder. A subclass gives PHASE, BY and `read(project)`, which returns a Phase
    made by `phase`. `answer` turns a CodedMessageError (a SparkError, a StoreError) or an OSError into the phase's
    could-not-run with the sentence, so one bad file never hides the other phases.
    """

    PHASE = BY = None

    def read(self, project):
        raise NotImplementedError

    def answer(self, project):
        try:
            return self.read(Path(project))
        except (CodedMessageError, OSError) as unread:
            return self.phase(COULD_NOT_RUN, [str(unread)])

    def phase(self, status, says, offers=()):
        return Phase(self.PHASE, status, MARKS[status][1], self.BY,
                     [flow_codes.UNKNOWN if said is None else said for said in says], list(offers))


def read_requirements(project):
    """The project's requirements.json as JSON, or None when there is none. A store.StoreError when it is no JSON."""
    path = Path(project) / REQUIREMENTS_FILE
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as broken:
        raise store.StoreError("%s is not JSON (%s)", path, broken, code=records_codes.RECORD_FILE_BROKEN)


def read_built_from(project):
    """The requirements the last finished build was built from (`dist/board/built-from.json`), or None when it recorded none
    or the file cannot be read: either way the sheet is not from the requirements now."""
    path = Path(project) / sheet.BUILT_FROM
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("requirements") if path.is_file() else None
    except (ValueError, AttributeError):
        return None


def makes_stale(project, kind):
    """The phases an offer of `kind` can make out of date in `project`: those of `flow_codes.MAKES_STALE` that hold
    something now (`HELD_FILES`). A phase that holds nothing cannot go out of date."""
    held = {phase for phase, name in HELD_FILES.items() if (Path(project) / name).is_file()}
    return tuple(phase for phase in flow_codes.MAKES_STALE[kind] if phase in held)


def problem_lines(problems):
    """Each problem item ({subject, sentence, …}) as one line, `subject: sentence`."""
    return ["%s: %s" % (problem["subject"], problem["sentence"]) for problem in problems]


def without_needs(project):
    """(status, sentence) of the needs and parts of a project with no needs: a hand-written project (requirements.json and
    no needs) has nothing open there, so its status is None; any other is not started."""
    if (Path(project) / REQUIREMENTS_FILE).is_file():
        return None, flow_codes.HAND_WRITTEN_MESSAGE
    return flow_codes.NOT_STARTED, flow_codes.NO_NEEDS_MESSAGE


class IdeaReader(PhaseReader):
    """Strategy: the idea is said in the chat, so the phase has no status and one sentence."""

    PHASE, BY = flow_codes.IDEA, flow_codes.BY_YOU

    def read(self, project):
        return self.phase(None, [flow_codes.IDEA_MESSAGE])


class NeedsReader(PhaseReader):
    """Strategy: the project's needs (`.spark/needs.json`), each offered to be dropped."""

    PHASE, BY = flow_codes.NEEDS, flow_codes.BY_CLAUDE

    def read(self, project):
        ids = [need["id"] for need in needs.read(project)]
        if not ids:
            status, said = without_needs(project)
            return self.phase(status, [said])
        # a drop is asked in the chat (P829), so its offer names no phase that goes out of date
        drops = [Offer("%s:%s" % (flow_codes.NEEDS_DROP, need), flow_codes.DROP_LABEL % need, flow_codes.DROP_MESSAGE % need, ())
                 for need in ids]
        return self.phase(OK, [flow_codes.NEEDS_MESSAGE % (len(ids), ", ".join(ids))], drops)


def reserve_sentence(need, candidate):
    """What a pick of `candidate` (a row of `needs.match`) does with what the person owns (`owned`: a number, "many" or
    "unknown"): uses one, or puts it on the list to get when they own none."""
    owned, label = candidate["owned"], candidate_label(candidate)
    if owned == "unknown":
        return flow_codes.RESERVE_UNKNOWN_MESSAGE % (label, need)
    if owned == "many":
        return flow_codes.RESERVE_MANY_MESSAGE % (label, need)
    return flow_codes.RESERVE_MESSAGE % (owned, label, need) if owned else flow_codes.TO_GET_MESSAGE


def candidate_label(candidate):
    """The part's own name, or its id when its record names none."""
    return candidate.get("label") or candidate["id"] or candidate["entry"]


def is_listed(project):
    """True when the project is on the person's list, False when it is not, None when the list cannot be read: then the
    build's history sentence is left out and the build is still offered."""
    try:
        return store.find_listed_name(project) is not None
    except store.StoreError:
        return None


def other_pick_sentence(plan, need, problems):
    """The sentence of a pick refused because another need's pick cannot get its part: the part by its name, and the
    problem's own sentence."""
    other = problems[0]
    return flow_codes.OTHER_PICK_MESSAGE % (", ".join(plan.needs_picking(other["subject"], need)) or "another need",
                                            plan.name_of(other["subject"]), other["sentence"])


def pick_id_of(candidate):
    """The id a pick of `candidate` names: its record's, or its drawer entry's key."""
    return candidate["id"] or candidate["entry"]


def is_plausible(need, candidate):
    """True when `candidate` holds the need's words or the matcher scores it above 0 (P976): owned junk takes no place. A
    board is plausible for a compute need whatever its words: the board is what a compute need picks."""
    if need["does"] == COMPUTE and candidate["kind"] == "board":
        return True
    return bool(candidate["what_matches"]) or candidate["score"] > 0


def counted_words(count, words):
    """The word of `words` (one, many) that goes with `count`."""
    return words[0] if count == 1 else words[1]


def left_out_lines(need, more, refused):
    """The says lines of a need with picks left out (P976): how many more, how many refused; a count of 0 is left out."""
    if more > 0 and refused:
        said = flow_codes.MORE_AND_REFUSED_MESSAGE % (need, more, counted_words(more, flow_codes.PICK_WORDS), refused)
    elif more > 0:
        said = flow_codes.MORE_PICKS_MESSAGE % (need, more, counted_words(more, flow_codes.PICK_WORDS))
    elif refused:
        said = flow_codes.REFUSED_PICKS_MESSAGE % (refused, counted_words(refused, flow_codes.PICK_WORDS), need,
                                                   counted_words(refused, flow_codes.BE_WORDS))
    else:
        return []
    return [said + " " + flow_codes.LIST_PICKS_MESSAGE]


def need_picks(project, need, plan, listed):
    """(the pick Offers of one matched `need`, its says lines), P976: its plausible candidates in the matcher's order, but
    its current pick and those `plan` refuses, at most OFFERS_PER_NEED. A need with candidates and none plausible, or one
    whose pick another need's pick refuses, gets no offers and one line that says why."""
    plausible = [candidate for candidate in need["candidates"] if is_plausible(need, candidate)]
    if need["candidates"] and not plausible:
        return [], [flow_codes.NO_PLAUSIBLE_MESSAGE % need["need"]]
    offered, refused = [], 0
    for candidate in (c for c in plausible if not plan.is_current(need["need"], pick_id_of(c))):
        picked, changes, problems = plan.holds(need["need"], pick_id_of(candidate))
        own = next((problem for problem in problems if problem["subject"] == picked), None)
        if own:
            refused += 1
        elif problems:
            return [], [flow_codes.NEED_REFUSED_LINE % (need["need"], other_pick_sentence(plan, need["need"], problems))]
        else:
            offered.append(pick_offer(project, need["need"], candidate, listed, plan.freed(changes, need["need"])))
    return offered[:OFFERS_PER_NEED], left_out_lines(need["need"], len(offered) - OFFERS_PER_NEED, refused)


def pick_offer(project, need, candidate, listed, freed):
    """The Offer to pick `candidate` for `need`, one the project's `needs.PickPlan` does not refuse. `freed` is what its
    `freed` gave for the pick's drawer changes: a pick that lets a hold go says whose it was. `listed` says whether the
    project is on the person's list."""
    pick_id = pick_id_of(candidate)
    key, label = "%s:%s:%s" % (flow_codes.PICK, need, pick_id), flow_codes.PICK_LABEL % (candidate_label(candidate), need)
    said = [flow_codes.PICK_MESSAGE % (candidate_label(candidate), need), reserve_sentence(need, candidate)]
    of_old, unpicked = freed
    said += [flow_codes.FREES_MESSAGE] if of_old else []
    said += [flow_codes.FREES_UNPICKED_MESSAGE] if unpicked else []
    said += [] if listed else [flow_codes.LIST_PROJECT_MESSAGE]
    return Offer(key, label, " ".join(said + [flow_codes.PICK_HISTORY_MESSAGE]), makes_stale(project, flow_codes.PICK))


def counted(listed):
    """The needs that count for the parts (P977): each with a pick, and each the person did not set aside. `listed` are
    needs as `needs.read` or `needs.match` gives them; the guide reads the same rule."""
    return [need for need in listed if need.get("pick") or not need.get("aside")]


def set_aside(listed):
    """The needs the person set aside (P977), picked or not: a picked one still counts as picked."""
    return [need for need in listed if need.get("aside")]


class PartsReader(PhaseReader):
    """Strategy: the picks of the needs (`needs.match`): problems when a need cannot be matched, partial while some need
    that counts has no pick, and every candidate offered as a pick. A need set aside with no pick does not count, has no
    pick offer and is named (P977)."""

    PHASE, BY = flow_codes.PARTS, flow_codes.BY_YOU

    def read(self, project):
        matched, problems = needs.match(project)
        if problems:
            return self.phase(PROBLEMS, problem_lines(problems))
        if not matched:
            status, said = without_needs(project)
            return self.phase(status, [said])
        open_needs, aside = counted(matched), [need["need"] for need in set_aside(matched)]
        picked = sum(1 for need in open_needs if need.get("pick"))
        status = OK if picked == len(open_needs) else flow_codes.PARTIAL if picked else flow_codes.NOT_STARTED
        # the list is read as the pick reads it: one that cannot be read stops this phase, as needs.match does
        plan, listed = needs.PickPlan(project), store.find_listed_name(project) is not None
        picks = []
        said = [flow_codes.PICKED_MESSAGE % (picked, len(open_needs))] + ([flow_codes.ASIDE_MESSAGE % ", ".join(aside)] if aside else [])
        for need in open_needs:
            offered, lines = need_picks(project, need, plan, listed)
            picks, said = picks + offered, said + lines
        return self.phase(status, said, picks)


class RequirementsReader(PhaseReader):
    """Strategy: requirements.json against what the picks give (`need_requirements.requirements`): stale when they differ,
    problems when the picks cannot give one. A file with no needs beside it was written by hand: nothing is compared, so
    it has no status (P878)."""

    PHASE, BY = flow_codes.REQUIREMENTS, flow_codes.BY_CLAUDE

    def read(self, project):
        held, listed = read_requirements(project), needs.read(project)
        effect = " ".join((flow_codes.REQUIREMENTS_MESSAGE, flow_codes.SHELVE_MESSAGE, flow_codes.ORIGIN_MESSAGE))
        offers = [Offer(flow_codes.WRITE_REQUIREMENTS, flow_codes.REQUIREMENTS_LABEL, effect,
                        makes_stale(project, flow_codes.WRITE_REQUIREMENTS))] if listed else []
        if held is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_REQUIREMENTS_MESSAGE], offers)
        if not listed:
            return self.phase(None, [flow_codes.NOTHING_TO_COMPARE_MESSAGE])
        given = need_requirements.requirements(project)
        if given.problems:
            return self.phase(PROBLEMS, problem_lines(given.problems), offers)
        if given.content != held:
            return self.phase(flow_codes.STALE, [flow_codes.REQUIREMENTS_STALE_MESSAGE], offers)
        return self.phase(OK, [REQUIREMENTS_FILE], offers)


def why_build_stale(project, record):
    """The sentence that says the requirements file changed after the build `record` was made, or None when it did not."""
    named = Path(record.get("requirements") or REQUIREMENTS_FILE)
    path = named if named.is_absolute() else Path(project) / named
    if not path.is_file() or sha256_of(path) != record.get("requirements_sha256"):
        return flow_codes.BUILD_STALE_MESSAGE % named
    return None


def is_board_only(project):
    """True when requirements.json says board_only and names no part, so the build builds the board alone (P387). A file
    that cannot be read says no: the requirements phase reports it."""
    try:
        held = read_requirements(project)
    except store.StoreError:
        return False
    return isinstance(held, dict) and held.get(need_requirements.BOARD_ONLY) is True and not held.get("parts")


def build_effect(project):
    """The effect of the build offer in `project`: what it saves, what it replaces or deletes, the history note of a
    project on the person's list, and that it runs no simulation. A board-only parts list saves less and deletes dist/."""
    if is_board_only(project):
        said = [flow_codes.BOARD_ONLY_BUILD_EFFECT, flow_codes.BUILD_REFUSED_MESSAGE]
        said += [flow_codes.DIST_REMOVED_MESSAGE] if (Path(project) / "dist").is_dir() else []
    else:
        said = [flow_codes.BUILD_MESSAGE, flow_codes.REPLACE_MESSAGE, flow_codes.BUILD_REFUSED_MESSAGE, flow_codes.NO_TOOL_MESSAGE]
        said += [flow_codes.BUILT_HISTORY_MESSAGE] if is_listed(project) else []
    return " ".join(said + [flow_codes.NO_SIMULATION_MESSAGE])


def skipped_stages(record):
    """The names of the stages the build `record` skipped, in the record's order."""
    return [stage.get("name") for stage in record.get("stages") or [] if stage.get("status") == SKIPPED]


class BuildReader(PhaseReader):
    """Strategy: the record of the last build (`.spark/build.json`): its status, or stale when the requirements file it was
    built from changed after it. A skipped stage is no pass (P878): an ok build on the board alone, or one whose simulation
    alone was skipped, says so and has no status, because a rebuild skips the same; any other skipped stage is partial."""

    PHASE, BY = flow_codes.BUILD, flow_codes.BY_CLAUDE

    def read(self, project):
        record = BuildRecordStore(project).read()
        offers = ([Offer(flow_codes.BUILD_BOARD, flow_codes.BUILD_LABEL, build_effect(project), makes_stale(project, flow_codes.BUILD_BOARD))]
                  if (project / REQUIREMENTS_FILE).is_file() else [])
        if record is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_BUILD_MESSAGE], offers)
        says = [flow_codes.BUILT_MESSAGE % (record.get("at") or flow_codes.UNKNOWN, record.get("status") or flow_codes.UNKNOWN)]
        says += ["%s: %s" % (stage.get("name"), stage.get("status")) for stage in record.get("stages") or [] if stage.get("status") != OK]
        says += [flow_codes.MISSING_FACTS_MESSAGE % len(record["missing_facts"])] if record.get("missing_facts") else []
        stale = why_build_stale(project, record)
        if stale:
            return self.phase(flow_codes.STALE, [stale] + says, offers)
        skipped = skipped_stages(record) if record.get("status") == OK else []
        if BUILD.name in skipped:
            return self.phase(None, [flow_codes.BOARD_ONLY_BUILD_MESSAGE])  # no offer: a rebuild skips the same stages
        if skipped == [SIMULATION.name]:
            return self.phase(None, says + [flow_codes.SIMULATION_SKIPPED_MESSAGE], offers)
        if skipped:
            return self.phase(flow_codes.PARTIAL, says, offers)
        return self.phase(record.get("status") if record.get("status") in (OK, PROBLEMS) else COULD_NOT_RUN, says, offers)


class BreadboardReader(PhaseReader):
    """Strategy: the breadboard sheet: stale when the build is, or when the requirements it was built from
    (`dist/board/built-from.json`) are not the file's now. A current sheet has no status, because spark does not judge
    the wiring, and a current build on the board alone has nothing to wire, however its simulation ended (P878)."""

    PHASE, BY = flow_codes.BREADBOARD, flow_codes.BY_YOU

    def read(self, project):
        kept = (project / sheet.SHEET).is_file()
        try:
            record = BuildRecordStore(project).read()
        except (CodedMessageError, OSError):
            if kept:
                raise
            record = None  # no sheet and no record to read: not started, and the build phase says the record's sentence
        stale = why_build_stale(project, record) if record else None
        if record and not stale and BUILD.name in skipped_stages(record):
            return self.phase(None, [flow_codes.BOARD_ONLY_MESSAGE])
        if not kept:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_SHEET_MESSAGE])
        if stale or read_built_from(project) != read_requirements(project):
            return self.phase(flow_codes.STALE, [flow_codes.SHEET_STALE_MESSAGE])
        return self.phase(None, [flow_codes.SHEET_NOT_JUDGED_MESSAGE])


class FirmwareReader(PhaseReader):
    """Strategy: firmware/main.py, which Claude writes in the chat: not started when it is not there, else when it was last
    written, in the machine's zone, with no status, because spark cannot judge the firmware."""

    PHASE, BY = flow_codes.FIRMWARE, flow_codes.BY_CLAUDE

    def read(self, project):
        main = project / MAIN_FILE
        if not main.is_file():
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_FIRMWARE_MESSAGE])
        return self.phase(None, [flow_codes.FIRMWARE_MESSAGE % stamp(datetime.datetime.fromtimestamp(main.stat().st_mtime))])


class SimulateReader(PhaseReader):
    """Strategy: the image sim/wokwi.toml names and the runs that tested it (`ProjectImage`): not started with no
    sim/wokwi.toml or no image, problems with a firmware line spark cannot use, and else no status, with what the runs
    say: a pass on an older image never reads as current. A log that cannot be read is could-not-run."""

    PHASE, BY = flow_codes.SIMULATE, flow_codes.BY_TERMINAL

    def read(self, project):
        try:
            image = ProjectImage(project)
        except DeployError as missing:
            if missing.reason in NOT_SIMULATED_SAYS:
                return self.phase(flow_codes.NOT_STARTED, NOT_SIMULATED_SAYS[missing.reason])
            return self.phase(PROBLEMS, [str(missing), flow_codes.SCENARIO_HINT])
        try:
            says = [image.why_untested() or flow_codes.TESTED_MESSAGE]
            if says != [flow_codes.TESTED_MESSAGE] and not image.failed_runs():
                says = [flow_codes.IMAGE_UNTESTED_MESSAGE]  # keyed on the fact: no run named this image
        except DeployError as unread:
            raise CodedMessageError("%s", unread, code=unread.reason)
        newer = image.find_newer_files()
        says += [flow_codes.NEWER_MESSAGE % ", ".join(newer)] if newer else []
        return self.phase(None, says + [flow_codes.SCENARIO_HINT])


class DeployReader(PhaseReader):
    """Strategy: the deploy is done in the person's terminal, after Claude looked at the board, so it is not started here."""

    PHASE, BY = flow_codes.DEPLOY, flow_codes.BY_TERMINAL

    def read(self, project):
        return self.phase(flow_codes.NOT_STARTED, [flow_codes.LOOK_FIRST_MESSAGE, flow_codes.DEPLOY_HINT])


#: The readers of the nine phases, in the order of `flow_codes.PHASES`.
READERS = (IdeaReader(), NeedsReader(), PartsReader(), RequirementsReader(), BuildReader(), BreadboardReader(),
           FirmwareReader(), SimulateReader(), DeployReader())
# --- end MVP ---
