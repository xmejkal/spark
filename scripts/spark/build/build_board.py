"""
The build as an Operation on the core (P804): a requirements file in, a board that builds out, and what --keep and
--sim-dir keep. check_spine.py is its CLI, and its `--json` line is the flat one (`FlatJsonLine`): the dict check_spine
printed, so no golden changed. `render`, the verdict's text, moved here from check_spine.py.
"""

import shutil
from pathlib import Path

from spark.bench import board_envelope
from spark.breadboard import tabbed_page
from spark.build import build_codes
from spark.build.build_service import findings_of, verdict
from spark.build.kept_files import KeepAsked, keep_all, left_off, simulation_dir
from spark.build.requirements_build import RequirementsBuildService
from spark.build.stage_help_table import StageHelpTable
from spark.build.stages import BUILD_STAGES, skipped_the_build
from spark.core import outcomes
from spark.core.operation import ASKS, COMMON_ARGUMENTS, FETCHES, READS, RUNS, WRITES, Argument, Operation
from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, OK, PROBLEMS, COULD_NOT_RUN, SKIPPED, STATUS_FOR
from spark.core.renderers import FlatJsonLine
from spark.core.result import NextStep, OperationResult
from spark.core.text_guards import guard_lines
from spark.design import loader
from spark.records import store
from spark.flow.write_flow_page import write_kept_page

#: What the closing line adds when a full build's simulation stage is skipped: every part's record skips the simulation (P778).
EVERY_PART_SKIPPED_LINE = "; every part is skipped from the simulation, so the diagram holds none of the project's parts"
#: The closing line's addition by the skipped simulation stage's code: a board with no Wokwi part (P1207) says its code's
#: own meaning. A skipped stage with any other code, or none, says EVERY_PART_SKIPPED_LINE.
SKIPPED_SIMULATION_LINES = {build_codes.EVERY_PART_SKIPPED: EVERY_PART_SKIPPED_LINE,
                            build_codes.BOARD_NOT_IN_WOKWI: "; " + build_codes.BOARD_NOT_IN_WOKWI.meaning}


def skipped_line(stages):
    """What the closing line of an ok full build adds for its skipped stage, or "" when no stage is skipped."""
    return next((SKIPPED_SIMULATION_LINES.get(stage.code, EVERY_PART_SKIPPED_LINE) for stage in stages if stage.status == SKIPPED), "")


def render(stages, code, unserved=()):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????", SKIPPED: "--  "}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation", ""]
    for stage in stages:
        lines.append("  [%s] %-16s %s" % (mark[stage.status], stage.name, stage.detail))
    lines.append("")
    lines.append({
        EXIT_OK: "  the chain runs end to end" + (" for the board alone: nothing to wire, so no board was built" if skipped_the_build(stages)
                                                  else skipped_line(stages)),
        EXIT_PROBLEMS: "  the chain is broken",
        EXIT_COULD_NOT_RUN: "  the chain was NOT exercised — this is not a pass",
    }[code] + (" — but not every need is on the board: %s" % ", ".join(unserved) if unserved and code == EXIT_OK else ""))
    return "\n".join(lines) + "\n"


#: Why a build names the research step next (P945): the breadboard picture cannot draw a part before its facts are found.
WHY_DRAWING_NEXT = "find the physical facts that draw this part on the breadboard picture, before you wire it"


def drawing_next_steps(kept, project):
    """The `next` of a build whose breadboard picture lacks a part's facts: one research step per record a kept entry
    names (the entry's `record`, P945), with `--project` when the build ran in a project. [] when every part is drawn."""
    records = list(dict.fromkeys(entry["record"] for entry in kept or [] if entry.get("record")))
    where = ["--project", str(project)] if project else []
    return [outcomes.add_env(outcomes.step("research", ["--part", record] + where, WHY_DRAWING_NEXT,
                                           effects=(READS, WRITES, ASKS, FETCHES)), store.read_given_env())
            for record in records]


def project_of(requirements):
    """The project folder a requirements file belongs to, or None for none given or the plugin's own library."""
    project = loader.project_for(requirements) if requirements else None
    return None if project is None or loader.is_library(project) else project


# --- MVP ---
def said_of(stages, code, requirements, kept):
    """
    The dict `check_spine.py --json` prints: check, status and stages, with the needs the requirements file leaves off the
    board (`unserved`, `left_off`) and the facts the board record lacks (`missing_facts`, P464) when there are any, and
    with --keep or --sim-dir what was kept (`kept`, P124), each entry without its `line`,
    which the person reads on stderr. A stage that has a code has its `code` too, after its detail; an ok stage has none
    (P936, the PO 2026-11-20: "Every stage with a code"). The next steps (P517) are the result's `next`, which
    `FlatJsonLine` writes as the last key (P1035).
    """
    said = {"check": "spine", "status": STATUS_FOR[code],
            "stages": [{"name": s.name, "status": s.status, "detail": s.detail, **({"code": s.code} if s.code else {})} for s in stages],
            **({"unserved": requirements["unserved"]} if left_off(requirements) else {}),
            **({"missing_facts": held} if (held := [item for entry in kept or [] for item in entry.get("missing_facts", [])]) else {})}
    if kept is not None:
        said["kept"] = [{key: value for key, value in entry.items() if key != "line"} for entry in kept]
    return said


class BuildBoard(Operation):
    """
    Operation: the build. It runs the chain on a requirements file (None: the reference design) with the
    RequirementsBuildService it was given, keeps what --keep and --sim-dir ask for (`kept_files.keep_all`) and removes
    the work folder, after a crash in its own steps too; the service removes one it raised past (P939). Its data is the
    dict check_spine printed with --json (`said_of`), its `next` its own steps (the drawing's research, the firmware's
    look), and with --keep the project it kept into is its written project (P1035), its lines the verdict's text, its diagnostics each kept entry's
    line, after the service's own lines (the service gives them to `outside.add_diagnostics`, so a crash later keeps
    them, P840, P938), and its Findings `build_service.findings_of` the stages.
    """

    name = "build-board"
    summary = "The one thing that has to work: a module list in, a board that builds out."
    stages = BUILD_STAGES
    details = StageHelpTable.render(stages)
    arguments = (Argument(("requirements",), "requirements", str, "a requirements.json; omit for the reference design. "
                          "\"board_only\": true with no parts builds the board alone. A file that names no board takes the "
                          "project's board: its requirements.json's, else boards/active.json's", nargs="?"),
                 COMMON_ARGUMENTS["json"]._replace(help="the verdict as one JSON object: check, status, stages, kept with --keep or --sim-dir, "
                                                   "and next last (the firmware step after an ok build in a project; with --keep and an ok "
                                                   "build, then the step that flow.py show names now, P1035)"),
                 Argument(("--keep",), "keep", Path,
                          "write the built board into DIR: board.tsx, its footprint and "
                          "dist/, where every check already looks; after a build that left no dist/board/circuit.json, an earlier dist/ stays and is named as an earlier build's here, and check_all says the last build did not write it (P816); a build that left it replaces dist/ whole (P1088). After a build whose build stage ended ok, a board.tsx that spark wrote and nobody changed is `replaced` "
                          "(its previous version is .spark/previous/board.tsx.txt), or `unchanged` when this build made the "
                          "same board. Other .tsx files are left alone and named, and so is one when the build did not finish or the replace failed; "
                                                    "`traces differ` names the traces that differ from this build's; with --json, each file is listed under kept. With a requirements "
                          "file it also writes breadboard.md, the parts and how to wire them on a breadboard, "
                          "breadboard.json, the same wiring drawn on a Wokwi breadboard (the XIAO ESP32-C6 today; a part "
                          "you moved in it, a resistor or a jumper too, stays where you put it, or the build names it as "
                          "`move not kept`; an end the drawing joins differently from the points is a `drawing differs` entry), "
                          "breadboard.svg, that drawing as a picture, "
                          "a rebuild also lists what to change on the bench (one `changed` entry for each line), page.html, in a project the flow's phases "
                          "with their status words and the breadboard, schematic and PCB, else the three in tabs, to open in a browser, firmware/pins.py, the pins the firmware imports, with one "
                          "`missing_facts` item for each fact the board record lacks; a refused requirements file leaves the earlier one, named (P1109). In a project it writes .spark/build.json, which flow.py reads, "
                          "the reference design's too, with `requirements` null (P1095). A reference-design build names an earlier breadboard.md, its drawings and spark's firmware/pins.py as an earlier build's (P1114, P1121). "
                          "The simulation project goes to DIR/sim", metavar="DIR"),
                 Argument(("--sim-dir",), "sim_dir", Path, "keep the simulation project here instead of DIR/sim: diagram.json, "
                          "wokwi.toml, the chips", metavar="DIR"),
                 Argument(("--firmware",), "firmware", str, "the flash image wokwi.toml names, relative to the sim dir (flash_image.py "
                          "writes one); without it, the image a kept wokwi.toml names is kept", metavar="IMAGE"))
    effects = (READS, RUNS, WRITES)
    json_renderer = FlatJsonLine

    def __init__(self, service=None):
        self.service = service or RequirementsBuildService()

    def written_project(self, values):
        return Path(values["keep"]) if values.get("keep") else None

    def run(self, requirements=None, keep=None, sim_dir=None, firmware=None, *, outside):
        """The build of `requirements` (a path as given, or None), `keep` and `sim_dir` each a str, a Path or None."""
        keep, sim_dir = (Path(keep) if keep else None), (Path(sim_dir) if sim_dir else None)
        built = self.service.build(requirements, firmware, simulation_dir(sim_dir, keep), add_diagnostics=outside.add_diagnostics)
        try:
            code = verdict(built.stages)
            kept = keep_all(built.stages, built.workdir, KeepAsked(requirements, keep, sim_dir), tabbed_page.TscircuitExport(built.toolchain), write_kept_page)
            # P945: find the facts that draw a part before the wiring, then P517: write the firmware next
            own_steps = (drawing_next_steps(kept, project_of(requirements))
                         + board_envelope.firmware_next_steps(code == EXIT_OK, requirements))
            text = guard_lines(render(built.stages, code, left_off(built.requirements)) + board_envelope.next_text(own_steps))
            return OperationResult(said_of(built.stages, code, built.requirements, kept), findings_of(built.stages),
                                   [NextStep(**step) for step in own_steps],
                                   lines=text[:-1].split("\n"),  # the one final newline is `print`'s
                                   diagnostics=["  %s" % entry["line"] for entry in kept or []])
        finally:
            if built.workdir is not None:
                shutil.rmtree(built.workdir, ignore_errors=True)
# --- end MVP ---
