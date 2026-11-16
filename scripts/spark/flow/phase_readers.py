"""
The readers of the nine phases of a project (P825): each reads the files one stage wrote and says where that phase
stands, with its facts and the offers a person or Claude may take next. A library for `show_flow`. Nothing here writes,
and no offer runs: P829 rebuilds the command from the key.
"""

import datetime
import json
from collections import namedtuple
from pathlib import Path

from spark.build.build_record import BuildRecordStore, sha256_of
from spark.breadboard import sheet
from spark.design import need_requirements, needs
from spark.firmware.project_image import DeployError, ProjectImage
from spark.flow import flow_codes
from spark.records import records_codes
from spark.core.errors import CodedMessageError, SparkError
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
from spark.core.zone_time import stamp

# --- MVP ---
#: The project's requirements file, as every stage names it.
REQUIREMENTS_FILE = "requirements.json"
#: The firmware Claude writes, as `/spark:build`'s next step names it.
MAIN_FILE = Path("firmware") / "main.py"
#: How each status reads: (the word in a line, the glyph a page shows). None is a phase with no status of its own.
MARKS = {OK: ("ok", "✓"), PROBLEMS: ("problems", "✗"), COULD_NOT_RUN: ("could not run", "?"),
         flow_codes.NOT_STARTED: ("not started", "○"), flow_codes.PARTIAL: ("partly done", "◐"),
         flow_codes.STALE: ("out of date", "↻"), None: (None, "·")}
#: Value: one offer of a phase: its key (`pick:soil:x-led`) and the line that says what taking it does.
Offer = namedtuple("Offer", "key effect")


class Phase(namedtuple("Phase", "phase status mark by facts offers")):
    """Value: where one phase of a project stands: its name, its status (an outcome, a phase word of `flow_codes`, or None),
    its glyph from MARKS, who does it, its facts (a null one reads `unknown`) and its Offers."""

    def to_dict(self):
        return dict(self._asdict(), offers=[offer._asdict() for offer in self.offers])


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

    def phase(self, status, facts, offers=()):
        return Phase(self.PHASE, status, MARKS[status][1], self.BY,
                     [flow_codes.UNKNOWN if fact is None else fact for fact in facts], list(offers))


class IdeaReader(PhaseReader):
    """Strategy: the idea is said in the chat, so the phase has no status and one fact."""

    PHASE, BY = flow_codes.IDEA, flow_codes.BY_YOU

    def read(self, project):
        return self.phase(None, [flow_codes.IDEA_FACT])


class NeedsReader(PhaseReader):
    """Strategy: the project's needs (`.spark/needs.json`), each offered to be dropped."""

    PHASE, BY = flow_codes.NEEDS, flow_codes.BY_CLAUDE

    def read(self, project):
        ids = [need["id"] for need in needs.read(project)]
        if not ids:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_NEEDS_FACT])
        drops = [Offer("%s:%s" % (flow_codes.NEEDS_DROP, need), flow_codes.DROP_EFFECT % need) for need in ids]
        return self.phase(OK, [flow_codes.NEEDS_FACT % (len(ids), ", ".join(ids))], drops)


def pick_effect(need, candidate):
    """The effect line of picking `candidate` (a row of `needs.match`) for `need`: what it replaces, how many the person
    has (`owned`: a number, "many" or "unknown") and, when none is free, which projects hold them."""
    owned = candidate["owned"]
    said = [flow_codes.PICK_EFFECT % need,
            flow_codes.OWNED_UNKNOWN_EFFECT if owned == "unknown" else flow_codes.OWNED_EFFECT % owned]
    if candidate.get("free") == 0 and candidate.get("held_by"):
        said.append(flow_codes.HELD_EFFECT % ", ".join(candidate["held_by"]))
    return "; ".join(said)


class PartsReader(PhaseReader):
    """Strategy: the picks of the needs (`needs.match`): problems when a need cannot be matched, partial while some need
    has no pick, and every candidate offered as a pick."""

    PHASE, BY = flow_codes.PARTS, flow_codes.BY_YOU

    def read(self, project):
        matched, problems = needs.match(project)
        if problems:
            return self.phase(PROBLEMS, ["%s: %s" % (problem["subject"], problem["sentence"]) for problem in problems])
        if not matched:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_NEEDS_FACT])
        picked = sum(1 for need in matched if need.get("pick"))
        status = OK if picked == len(matched) else flow_codes.PARTIAL if picked else flow_codes.NOT_STARTED
        picks = [Offer("%s:%s:%s" % (flow_codes.PICK, need["need"], candidate["id"] or candidate["entry"]), pick_effect(need["need"], candidate))
                 for need in matched for candidate in need["candidates"]]
        return self.phase(status, [flow_codes.PICKED_FACT % (picked, len(matched))], picks)


def read_requirements(project):
    """The project's requirements.json as JSON, or None when there is none. A SparkError when it is no JSON."""
    path = Path(project) / REQUIREMENTS_FILE
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as broken:
        raise SparkError("%s is not JSON (%s)", path, broken, code=records_codes.RECORD_FILE_BROKEN)


class RequirementsReader(PhaseReader):
    """Strategy: requirements.json against what the picks give (`need_requirements.requirements`): stale when they differ,
    problems when the picks cannot give one. A file with no needs beside it was written by hand and is ok."""

    PHASE, BY = flow_codes.REQUIREMENTS, flow_codes.BY_CLAUDE

    def read(self, project):
        held, listed = read_requirements(project), needs.read(project)
        offers = [Offer(flow_codes.WRITE_REQUIREMENTS, flow_codes.REQUIREMENTS_EFFECT)] if listed else []
        if held is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_REQUIREMENTS_FACT], offers)
        if not listed:
            return self.phase(OK, [flow_codes.HAND_WRITTEN_FACT])
        given = need_requirements.requirements(project)
        if given.problems:
            return self.phase(PROBLEMS, ["%s: %s" % (problem["subject"], problem["sentence"]) for problem in given.problems], offers)
        if given.content != held:
            return self.phase(flow_codes.STALE, [flow_codes.REQUIREMENTS_STALE_FACT], offers)
        return self.phase(OK, [REQUIREMENTS_FILE], offers)


def why_build_stale(project, record):
    """The fact that says the requirements file changed after the build `record` was made, or None when it did not."""
    named = Path(record.get("requirements") or REQUIREMENTS_FILE)
    path = named if named.is_absolute() else Path(project) / named
    if not path.is_file() or sha256_of(path) != record.get("requirements_sha256"):
        return flow_codes.BUILD_STALE_FACT % named
    return None


class BuildReader(PhaseReader):
    """Strategy: the record of the last build (`.spark/build.json`): its status, or stale when the requirements file it was
    built from changed after it."""

    PHASE, BY = flow_codes.BUILD, flow_codes.BY_CLAUDE

    def read(self, project):
        record = BuildRecordStore(project).read()
        offers = [Offer(flow_codes.BUILD_BOARD, flow_codes.BUILD_EFFECT)] if (project / REQUIREMENTS_FILE).is_file() else []
        if record is None:
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_BUILD_FACT], offers)
        facts = [flow_codes.BUILT_FACT % (record.get("at") or flow_codes.UNKNOWN, record.get("status") or flow_codes.UNKNOWN)]
        facts += ["%s: %s" % (stage.get("name"), stage.get("status")) for stage in record.get("stages") or [] if stage.get("status") != OK]
        facts += [flow_codes.MISSING_FACTS_FACT % len(record["missing_facts"])] if record.get("missing_facts") else []
        stale = why_build_stale(project, record)
        if stale:
            return self.phase(flow_codes.STALE, [stale] + facts, offers)
        return self.phase(record.get("status") if record.get("status") in (OK, PROBLEMS) else COULD_NOT_RUN, facts, offers)


class BreadboardReader(PhaseReader):
    """Strategy: the breadboard sheet: stale when the build is, or when the requirements it was built from
    (`dist/board/built-from.json`) are not the file's now."""

    PHASE, BY = flow_codes.BREADBOARD, flow_codes.BY_YOU

    def read(self, project):
        if not (project / sheet.SHEET).is_file():
            return self.phase(flow_codes.NOT_STARTED, [flow_codes.NO_SHEET_FACT])
        record, built_from = BuildRecordStore(project).read(), project / sheet.BUILT_FROM
        try:
            recorded = json.loads(built_from.read_text(encoding="utf-8")).get("requirements") if built_from.is_file() else None
        except (ValueError, AttributeError):
            recorded = None
        if (record and why_build_stale(project, record)) or recorded != read_requirements(project):
            return self.phase(flow_codes.STALE, [flow_codes.SHEET_STALE_FACT])
        return self.phase(OK, [sheet.SHEET])


class FirmwareReader(PhaseReader):
    """Strategy: firmware/main.py, which Claude writes in the chat: whether it is there and when it was last written,
    in the machine's zone."""

    PHASE, BY = flow_codes.FIRMWARE, flow_codes.BY_CLAUDE

    def read(self, project):
        main = project / MAIN_FILE
        if not main.is_file():
            return self.phase(None, [flow_codes.NO_FIRMWARE_FACT])
        return self.phase(None, [flow_codes.FIRMWARE_FACT % stamp(datetime.datetime.fromtimestamp(main.stat().st_mtime))])


class SimulateReader(PhaseReader):
    """Strategy: the image sim/wokwi.toml names and the runs that tested it (`ProjectImage`): a pass on an older image
    never reads as current. A log that cannot be read is could-not-run."""

    PHASE, BY = flow_codes.SIMULATE, flow_codes.BY_TERMINAL

    def read(self, project):
        try:
            image = ProjectImage(project)
        except DeployError as missing:
            return self.phase(None, [str(missing), flow_codes.SCENARIO_LINE])
        try:
            facts = [image.why_untested() or flow_codes.TESTED_FACT]
        except DeployError as unread:
            raise SparkError("%s", unread, code=unread.reason)
        newer = image.find_newer_files()
        facts += [flow_codes.NEWER_FACT % ", ".join(newer)] if newer else []
        return self.phase(None, facts + [flow_codes.SCENARIO_LINE])


class DeployReader(PhaseReader):
    """Strategy: the deploy is done in the person's terminal, after Claude looked at the board, so it is not started here."""

    PHASE, BY = flow_codes.DEPLOY, flow_codes.BY_TERMINAL

    def read(self, project):
        return self.phase(flow_codes.NOT_STARTED, [flow_codes.LOOK_FIRST_FACT, flow_codes.DEPLOY_LINE])


#: The readers of the nine phases, in the order of `flow_codes.PHASES`.
READERS = (IdeaReader(), NeedsReader(), PartsReader(), RequirementsReader(), BuildReader(), BreadboardReader(),
           FirmwareReader(), SimulateReader(), DeployReader())
# --- end MVP ---
