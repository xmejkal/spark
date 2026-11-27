"""
The readers of the nine phases of a project (P825): each reads the files one stage wrote and says where that phase
stands, with its sentences and the offers a person or Claude may take next. A library for `show_flow`. Nothing here
writes, and no offer runs: P829 rebuilds the command from the key.
"""

import datetime
import json
from collections import namedtuple
from pathlib import Path

from spark.build.build_record import BUILD_RECORD_FILE, BuildRecordStore, earlier_dist, sha256_of
from spark.build.stages import BUILD, SIMULATION
from spark.breadboard import sheet
from spark.design import entry_origin, need_requirements, needs, needs_basis
from spark.firmware import firmware_codes
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import deploy_reading, flow_codes, offer_steps
from spark.flow.no_model import stops_only_for_no_model
from spark.records import record_kind, records_codes, store
from spark.records.brief import Brief
from spark.core.errors import CodedMessageError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS, SKIPPED
from spark.core.zone_time import stamp

# --- MVP ---
#: The project's requirements file, as every stage names it.
REQUIREMENTS_FILE = offer_steps.REQUIREMENTS_FILE
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
#: Value: one offer of a phase: its key (`pick:soil:x-led`), its label (its button's words), its effect (sentences that
#: name every write it makes), `makes_stale` (P829), `step`, its NextStep (P1030), and a pick's `part` (P1067) and `have`
#: (`sheet.have_of`, P1135), else None. The JSON of `data` holds all but the step, which is in `next`.
Offer = namedtuple("Offer", "key label effect makes_stale step part have", defaults=(None, None))
#: Value (P1135): a need of the parts phase that counts: its id, `picked` (its picks by name) and `says`, its own lines.
PartsNeed = namedtuple("PartsNeed", "need picked says")
#: The parts phase offers at most this many picks per need (P976, the PO, 2026-11-21: "so many unrelated things").
OFFERS_PER_NEED = 3
#: The verb of the need a board serves (`needs`' board need): a board is a plausible pick for it whatever its words.
COMPUTE = "compute"
#: The file whose presence says a phase holds something now, for `makes_stale`.
HELD_FILES = {flow_codes.REQUIREMENTS: Path(REQUIREMENTS_FILE), flow_codes.BUILD: BUILD_RECORD_FILE,
              flow_codes.BREADBOARD: Path(sheet.SHEET)}


class Phase(namedtuple("Phase", "phase status mark by says offers needs", defaults=(None,))):
    """Value: where one phase of a project stands: its name, its status (an outcome, a phase word of `flow_codes`, or None),
    its glyph from MARKS, who does it, what it says (a null value reads `unknown`), its Offers and its PartsNeeds (P1135)."""

    def to_dict(self):
        return dict(self._asdict(), offers=[dict(key=offer.key, label=offer.label, effect=offer.effect, makes_stale=list(offer.makes_stale),
                                                 part=offer.part, have=offer.have) for offer in self.offers],
                    needs=None if self.needs is None else [need._asdict() for need in self.needs])


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

    def phase(self, status, says, offers=(), needs=None):
        return Phase(self.PHASE, status, MARKS[status][1], self.BY,
                     [flow_codes.UNKNOWN if said is None else said for said in says], list(offers), None if needs is None else list(needs))


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


def without_needs(project, phase):
    """(status, sentence) of the `phase` (needs or parts) of a project with no needs. With requirements.json there is
    nothing open there, so its status is None, and the sentence says what is true: needs.json holds no need (the last
    was dropped), or there is no needs file (a hand-written project). Any other project is not started."""
    if (Path(project) / REQUIREMENTS_FILE).is_file():
        if (Path(project) / needs.FILE).is_file():
            return None, flow_codes.NO_NEED_LEFT_MESSAGE if phase == flow_codes.NEEDS else flow_codes.NO_PICK_BEHIND_MESSAGE
        return None, flow_codes.HAND_WRITTEN_MESSAGE
    return flow_codes.NOT_STARTED, flow_codes.NO_NEEDS_MESSAGE


class IdeaReader(PhaseReader):
    """Strategy: the idea is the brief's goal. A need dropped after the must lines were last gone through makes it out of date
    (P1027, slice 2), with the dropped ids and what Claude asks. A needs file that cannot be read is the needs phase's to say,
    so it reads as no drop here. Else a goal makes it ok and says the goal, whatever the rest of the brief holds (P1142). With
    no goal it has no status: it says why the brief cannot be read, or that the brief holds none."""

    PHASE, BY = flow_codes.IDEA, flow_codes.BY_YOU

    def read(self, project):
        try:
            ids = needs_basis.dropped(project, [need["id"] for need in needs.read(project)])
        except (store.StoreError, OSError, RecursionError):
            ids = []
        if ids:
            return self.phase(flow_codes.STALE, [flow_codes.NEEDS_DROPPED_MESSAGE % ", ".join(ids),
                                                 flow_codes.MUST_ASK_MESSAGE])
        brief, why = Brief.read(project)
        if brief.has_goal:
            return self.phase(OK, [flow_codes.GOAL_MESSAGE % brief.goal])
        return self.phase(None, [flow_codes.BRIEF_UNREADABLE % why if why else flow_codes.NO_GOAL_MESSAGE])


class NeedsReader(PhaseReader):
    """Strategy: the project's needs (`.spark/needs.json`), each offered to be dropped."""

    PHASE, BY = flow_codes.NEEDS, flow_codes.BY_CLAUDE

    def read(self, project):
        ids = [need["id"] for need in needs.read(project)]
        if not ids:
            status, said = without_needs(project, self.PHASE)
            return self.phase(status, [said])
        # a drop is asked in the chat (P829), so its offer names no phase that goes out of date
        drops = [Offer("%s:%s" % (flow_codes.NEEDS_DROP, need), flow_codes.DROP_LABEL % need, flow_codes.DROP_MESSAGE % need, (),
                       offer_steps.drop_step(project, need))
                 for need in ids]
        stale, said = basis_says(project)
        return self.phase(flow_codes.STALE if stale else OK, [flow_codes.NEEDS_MESSAGE % (len(ids), ", ".join(ids))] + said, drops)


def basis_says(project):
    """(stale, the lines after the needs line) of the goal and the must lines the needs were written from (P1027). No record
    (a project written before P1027) or a brief with no goal gives (False, []). A record or a brief that cannot be read gives
    one line that spark cannot tell, with the reason. Another stamp gives what changed and the review line. It reads only."""
    held = needs_basis.NeedsBasisStore(project).held()
    if held is None:
        return False, []
    if held == needs_basis.BROKEN:
        return False, [flow_codes.BASIS_UNKNOWN_MESSAGE % flow_codes.BASIS_BROKEN]
    brief, why = Brief.read(project)
    if why:
        return False, [flow_codes.BASIS_UNKNOWN_MESSAGE % (flow_codes.BRIEF_UNREADABLE % why)]
    now = needs_basis.stamp_of(brief)
    parts = needs_basis.changed(held, now) if now else []
    if not parts:
        return False, []
    return True, [flow_codes.NEEDS_STALE_MESSAGE % " and ".join(flow_codes.CHANGED_WORDS[part] for part in parts),
                  flow_codes.NEEDS_REVIEW_MESSAGE]


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
    """The says line of `need` when another need's pick cannot get its part (P993): no new pick can be saved for it, the
    part by its name, and the problem's own sentence."""
    other = problems[0]
    return flow_codes.NO_NEW_PICK_MESSAGE % (need, ", ".join(plan.needs_picking(other["subject"], need)) or "another need",
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


def refused_part(candidate):
    """A pick its own part refuses, as the says line names it (P991 review, the PO: "even if taken"): its name, none or
    too few free, and the other projects that hold it (`held_by`)."""
    held = flow_codes.HELD_BY % ", ".join(candidate["held_by"]) if candidate["held_by"] else ""
    return flow_codes.REFUSED_PART % (candidate_label(candidate),
                                      flow_codes.NONE_FREE if candidate["free"] == 0 else flow_codes.TOO_FEW_FREE, held)


def left_out_lines(need, more, refused):
    """The says lines of a need with picks left out (P976): how many more, and each refused candidate by name (P991
    review); a count of 0 is left out."""
    names = "; ".join(refused_part(candidate) for candidate in refused)
    if more > 0 and refused:
        said = flow_codes.MORE_AND_REFUSED_MESSAGE % (need, more, counted_words(more, flow_codes.PICK_WORDS), names)
    elif more > 0:
        said = flow_codes.MORE_PICKS_MESSAGE % (need, more, counted_words(more, flow_codes.PICK_WORDS))
    elif refused:
        said = flow_codes.REFUSED_PICKS_MESSAGE % (need, names)
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
    offered, refused = [], []
    for candidate in (c for c in plausible if not plan.is_current(need["need"], pick_id_of(c))):
        picked, changes, problems = plan.holds(need["need"], pick_id_of(candidate))
        own = next((problem for problem in problems if problem["subject"] == picked), None)
        if own:
            refused.append(candidate)
        elif problems:
            return [], [other_pick_sentence(plan, need["need"], problems)]
        else:
            offered.append(pick_offer(project, need["need"], candidate, listed, pick_notes(project, plan, need, candidate, changes)))
    return offered[:OFFERS_PER_NEED], left_out_lines(need["need"], len(offered) - OFFERS_PER_NEED, refused)


def pick_notes(project, plan, need, candidate, changes):
    """The sentences the project's `needs.PickPlan` gives of a pick of `candidate` for the matched `need`, with its drawer
    `changes`: a hold it lets go says whose it was (`freed`), and a board the parts list would refuse says so (P991)."""
    of_old, unpicked = plan.freed(changes, need["need"])
    refusal = board_file_refusal(project, plan, need, candidate)
    return (([flow_codes.FREES_MESSAGE] if of_old else []) + ([flow_codes.FREES_UNPICKED_MESSAGE] if unpicked else [])
            + ([flow_codes.NO_BOARD_FILE_MESSAGE % candidate_label(candidate)] if refusal else []))


def board_file_refusal(project, plan, need, candidate):
    """The sentence with which the parts list would refuse a pick of `candidate` for a compute `need` (P991), or None: only for a
    drawer entry that is no record spark knows, and only when the refusal names it — with a board picked by another need,
    the parts list places that board and refuses nothing; with two, it asks for one board. None for any other pick."""
    pick = plan.resolve(pick_id_of(candidate)) if need["does"] == COMPUTE else None
    if not pick or "entry" not in pick:
        return None
    problems = need_requirements.board_problems(plan.after(need["need"], pick), plan.known, plan.entries, project)
    return next((problem["sentence"] for problem in problems if problem["subject"] == pick["entry"]), None)


def picked_names(plan, need):
    """The names of the need's picks (P991, P1135): each by the name a person reads (`PickPlan.name_of`), a drawer entry
    of a record spark knows by the record's; [] for a need with no pick."""
    return [plan.name_of(next(iter(needs.as_record(pick, plan.known, plan.entries).values())))
            for pick in need.get("pick") or []]


def pick_offer(project, need, candidate, listed, notes):
    """The Offer to pick `candidate` for `need`, one the project's `needs.PickPlan` does not refuse. `notes` are the
    sentences `pick_notes` gave of it. `listed` says whether the project is on the person's list."""
    pick_id = pick_id_of(candidate)
    key, label = "%s:%s:%s" % (flow_codes.PICK, need, pick_id), flow_codes.PICK_LABEL % (candidate_label(candidate), need)
    said = [flow_codes.PICK_MESSAGE % (candidate_label(candidate), need), reserve_sentence(need, candidate)] + notes
    said += [] if listed else [flow_codes.LIST_PROJECT_MESSAGE]
    return Offer(key, label, " ".join(said + [flow_codes.PICK_HISTORY_MESSAGE]), makes_stale(project, flow_codes.PICK),
                 offer_steps.pick_step(project, need, pick_id, candidate_label(candidate)), candidate_label(candidate),
                 sheet.have_of(candidate))


def pick_need(key):
    """The need of a pick offer's key, as `pick_offer` makes it (`pick:<need>:<pick id>`), else None (P1062): the page
    puts each pick in its need's row, and the key's format keeps this one owner."""
    rest = key.partition(":")[2]
    return rest.split(":", 1)[0] if flow_codes.kind_of(key) == flow_codes.PICK and ":" in rest else None


def counted(listed):
    """The needs that count for the parts (P977): each with a pick, and each the person did not set aside. `listed` are
    needs as `needs.read` or `needs.match` gives them; the guide reads the same rule."""
    return [need for need in listed if need.get("pick") or not need.get("aside")]


def is_all_picked(listed):
    """True when some need counts and each that counts has a pick (P993): the parts phase is done, so what refuses the
    parts list is the requirements phase's own problem."""
    open_needs = counted(listed)
    return bool(open_needs) and all(need.get("pick") for need in open_needs)


def owed_facts(plan, key):
    """The facts the record of the part pick `key` owes that the circuit needs (P993), as the parts list's rule reads
    them; [] when spark has no readable record of it."""
    path = plan.paths.get(("part", key))
    record = record_kind._parse(path) if path else None
    passed = need_requirements.LAYOUT_FACTS + need_requirements.SIMULATION_FACTS  # P996: neither refuses the parts list
    return [fact for fact in record_kind.owes(record) if fact not in passed] if isinstance(record, dict) else []


def named_pick(plan, key):
    """A part pick as a person reads it: “<name>” for <needs>, or “<name>” when no need's pick is that record. `key` is a
    part record's id (the parts list's part picks), so only the needs that pick that part count (P1141)."""
    named, by = "“%s”" % plan.name_of(key), ", ".join(plan.picked_for(key, "part"))
    return flow_codes.PICKED_BY % (named, by) if by else named


def no_stance_lines(project, unsimulated):
    """One warning line per part pick the parts list takes that spark cannot simulate yet (P996), or none."""
    plan = needs.PickPlan(project) if unsimulated else None
    return [flow_codes.NO_STANCE_MESSAGE % named_pick(plan, key) for key, _how in unsimulated]


def blocker_lines(project, problems):
    """The parts list's problems as the person reads them (P993): a pick that owes a fact by its name, the needs that pick
    it and what it owes, in plain words; any other as its own line (`problem_lines`). The record decides, never the
    rule's sentence: a part pick whose record owes a fact the circuit needs has that one problem from the rule."""
    plan, said = needs.PickPlan(project), []
    for problem in problems:
        owed = owed_facts(plan, problem["subject"])
        said += ([flow_codes.OWED_MESSAGE % (named_pick(plan, problem["subject"]), ", ".join(owed))] if owed
                 else problem_lines([problem]))
    return said


def set_aside(listed):
    """The needs the person set aside (P977), picked or not: a picked one still counts as picked."""
    return [need for need in listed if need.get("aside")]


class PartsReader(PhaseReader):
    """Strategy: the picks of the needs (`needs.match`): problems when a need cannot be matched, partial while some need
    that counts has no pick, and every candidate offered as a pick. A need set aside with no pick does not count, has no
    pick offer and is named (P977). Each need that counts is a PartsNeed with its picks and its own lines (P1135)."""

    PHASE, BY = flow_codes.PARTS, flow_codes.BY_YOU

    def read(self, project):
        matched, problems = needs.match(project)
        if problems:
            return self.phase(PROBLEMS, problem_lines(problems))
        if not matched:
            status, said = without_needs(project, self.PHASE)
            return self.phase(status, [said], needs=[])
        open_needs, aside = counted(matched), [need["need"] for need in set_aside(matched)]
        picked = sum(1 for need in open_needs if need.get("pick"))
        status = OK if picked == len(open_needs) else flow_codes.PARTIAL if picked else flow_codes.NOT_STARTED
        # the list is read as the pick reads it: one that cannot be read stops this phase, as needs.match does
        plan, listed = needs.PickPlan(project), store.find_listed_name(project) is not None
        picks, parts = [], []
        said = [flow_codes.PICKED_MESSAGE % (picked, len(open_needs))] + ([flow_codes.ASIDE_MESSAGE % ", ".join(aside)] if aside else [])
        for need in open_needs:
            offered, lines = need_picks(project, need, plan, listed)
            picks += offered
            parts.append(PartsNeed(need["need"], picked_names(plan, need), lines))
        return self.phase(status, said, picks, parts)


class RequirementsReader(PhaseReader):
    """Strategy: requirements.json against what the picks give (`need_requirements.requirements`): stale when they differ,
    problems when the picks cannot give one. A file with no needs beside it was written by hand: nothing is compared, so
    it has no status (P878). P993: the parts list is offered only when its own rule refuses nothing; before a file, a
    refusal is problems once every need that counts has a pick, else the parts phase holds the blocker (not started). A file
    changed after spark last wrote it says so (P1140)."""

    PHASE, BY = flow_codes.REQUIREMENTS, flow_codes.BY_CLAUDE

    def read(self, project):
        held, listed = read_requirements(project), needs.read(project)
        if not listed and held is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_REQUIREMENTS_MESSAGE])
        if not listed:
            return self.phase(None, [flow_codes.NOTHING_TO_COMPARE_MESSAGE])
        given = need_requirements.requirements(project)
        if given.problems:  # P993: the parts list would refuse and write nothing, so it is no offer, and its lines say why
            said = ([flow_codes.NO_REQUIREMENTS_MESSAGE] if held is None else []) + blocker_lines(project, given.problems)
            return self.phase(PROBLEMS if held is not None or is_all_picked(listed) else flow_codes.NOT_STARTED, said)
        effect = " ".join((flow_codes.REQUIREMENTS_MESSAGE, flow_codes.SHELVE_MESSAGE, flow_codes.ORIGIN_MESSAGE))
        offers = [Offer(flow_codes.WRITE_REQUIREMENTS, flow_codes.REQUIREMENTS_LABEL, effect,
                        makes_stale(project, flow_codes.WRITE_REQUIREMENTS), offer_steps.requirements_step(project))]
        warned = no_stance_lines(project, given.unsimulated)  # P996: said, never a blocker
        if held is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_REQUIREMENTS_MESSAGE] + warned, offers)
        if given.content != held:
            said = flow_codes.STALE_REQUIREMENTS[entry_origin.EntryOriginStore(project).is_as_written(held)][0]
            return self.phase(flow_codes.STALE, [said] + warned, offers)
        return self.phase(OK, [REQUIREMENTS_FILE] + warned, offers)


def why_build_stale(project, record):
    """The sentence that says the requirements file changed after the build `record`, or that it was the reference design's (P1095), or None."""
    if "requirements" in record and record["requirements"] is None:  # P1095: the reference design's build, from no file
        return flow_codes.REFERENCE_BUILD_MESSAGE % REQUIREMENTS_FILE
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
        said = [flow_codes.BOARD_ONLY_BUILD_EFFECT, flow_codes.BOARD_ONLY_REFUSED_MESSAGE]
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
        offers = ([Offer(flow_codes.BUILD_BOARD, flow_codes.BUILD_LABEL, build_effect(project), makes_stale(project, flow_codes.BUILD_BOARD),
                         offer_steps.build_step(project))]
                  if (project / REQUIREMENTS_FILE).is_file() else [])
        if record is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_BUILD_MESSAGE], offers)
        says = [flow_codes.BUILT_MESSAGE % (record.get("at") or flow_codes.UNKNOWN, record.get("status") or flow_codes.UNKNOWN)]
        says += ["%s: %s" % (stage.get("name"), stage.get("status")) for stage in record.get("stages") or [] if stage.get("status") != OK]
        says += [flow_codes.MISSING_FACTS_MESSAGE % len(record["missing_facts"])] if record.get("missing_facts") else []
        says += [line for line in [earlier_dist(project)] if line]  # P1088: a dist/ the last build did not write (P816)
        stale = why_build_stale(project, record)
        if stale:
            return self.phase(flow_codes.STALE, [stale] + says, offers)
        skipped = skipped_stages(record) if record.get("status") == OK else []
        if BUILD.name in skipped:
            return self.phase(None, [flow_codes.BOARD_ONLY_BUILD_MESSAGE])  # no offer: a rebuild skips the same stages
        if skipped == [SIMULATION.name] and stops_only_for_no_model(record):
            return self.phase(None, says + [flow_codes.NO_SIMULATION_NOW], offers)  # P1207: Wokwi has no model of the board
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
    """Strategy: the deploy is done in the person's terminal, after Claude looked at the board. It reads the newest board
    log in sim/runs/board/ (P1043, `deploy_reading`): its time, image, verdict and cause, never its port, facts line,
    console or a tool's text. With no log it is not started. Only ready seen on the image the project holds now is ok; a
    log that cannot be read is could-not-run."""

    PHASE, BY = flow_codes.DEPLOY, flow_codes.BY_TERMINAL

    def __init__(self, state=None):
        self.state = state  # the DeployState of one run (the review of #1579), or None to read it here

    def read(self, project):
        state = self.state or deploy_reading.read_deploy(project)
        if state.error:
            raise state.error
        if state.logged is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.LOOK_FIRST_MESSAGE, flow_codes.DEPLOY_HINT])
        return self.phase(state.status, deploy_reading.deployed_says(state.count, state.logged, state.fact))


#: The readers of the nine phases, in the order of `flow_codes.PHASES`.
READERS = (IdeaReader(), NeedsReader(), PartsReader(), RequirementsReader(), BuildReader(), BreadboardReader(),
           FirmwareReader(), SimulateReader(), DeployReader())
# --- end MVP ---
