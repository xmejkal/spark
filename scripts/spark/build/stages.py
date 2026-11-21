"""
The build's stages as one table (P852), and the outcome of one stage (P705): `BUILD_STAGES`, a `StageDefinition` per
stage in run order, each with its name, its summary and its endings, and `Stage`, which a definition makes, so no call
site writes a stage's name, status or code. `board_engine`, `build_service` and `requirements_build` read it, the flow
and `kept_files` read the names, `stage_help_table.StageHelpTable` renders it for `check_spine.py --help`, and
`StageMarkdownTable` for how-it-works.md (P936). A later frontend (`--describe`, MCP) reads `BuildBoard.stages`, which
is `BUILD_STAGES`, never the rendered text. Every importer imports the names, never the module: `stages` is a list of
Stages in `run`, `main` and the tests.

The page's cell of a stage's endings may hold 300 characters (tools/check_docs.py's CELL_LIMIT), and the simulation's
is near it: an ending added there may need a shorter message, or check_docs fails. Its advice to move the text below
the table does not apply, because the block is generated.
"""

from collections import namedtuple

from spark.build import build_codes
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS, SKIPPED

# --- MVP ---
#: What a build stopped at the footprint stage still gives, after the gaps `footprint_emitter.why_no_footprint` lists (P407).
NO_FOOTPRINT_HINT = ("The schematic was not tried. The pin map needs no footprint: with --keep, the kept lines say "
                     "whether firmware/pins.py was written. The breadboard sheet and the simulation read the built "
                     "board, so they wait for the footprint.")


class Stage:
    """Value: one link, what became of it, and the `code` (build_codes, or the design's own) of one that did not end ok."""

    def __init__(self, name, status, detail="", code=None):
        self.name, self.status, self.detail, self.code = name, status, detail, code

    def __repr__(self):
        return "Stage(%r, %r)" % (self.name, self.status)


class StageEnding(namedtuple("StageEnding", "code status message")):
    """
    Value: one way a stage ends that is not ok: its `code` (build_codes), its status, and `message`, the template of the
    stage's detail. The code is None only for DESIGN_ERROR, whose code is the design error's own. Every message
    is filled with %, so a literal % is written %%.
    """


class StageDefinition(namedtuple("StageDefinition", "name summary endings")):
    """Value: one stage of the build, a row of BUILD_STAGES: its name, one sentence for the help, and its endings. It
    makes the stage's Stage; `ended` and `stopped_by` raise ValueError for an ending the stage does not have."""

    def ok(self, detail):
        """The Stage of this stage that ended ok, with `detail`."""
        return Stage(self.name, OK, detail)

    def ended(self, ending, *values):
        """The Stage of `ending`, its message filled with `values` (TypeError for a value missing or one too many).
        ValueError for an ending this stage does not have, or one with no code (DESIGN_ERROR)."""
        self._require(ending)
        if ending.code is None:
            raise ValueError("%s: a stage that does not end ok names its code; a design error's is its own (stopped_by)"
                             % self.name)
        return Stage(self.name, ending.status, ending.message % values, ending.code)

    def stopped_by(self, found, hint=""):
        """The Stage of a design error `found`, which this stage could not run past: its sentence (`str`) and then `hint`,
        and its own `code`. ValueError when a design error cannot stop this stage."""
        self._require(DESIGN_ERROR)
        return Stage(self.name, COULD_NOT_RUN, str(found) + hint, found.code)

    def _require(self, ending):
        if ending not in self.endings:
            raise ValueError("the %s stage has no ending %r" % (self.name, ending))


#: The design error's own sentence and code: a requirements file that is not a design, a part record, a refused input.
DESIGN_ERROR = StageEnding(None, COULD_NOT_RUN, "%s")
#: A project that runs on the board alone (P236): every stage between the board and the simulation.
BOARD_ONLY_ENDING = StageEnding(build_codes.BOARD_ONLY, SKIPPED, "board only: nothing to wire")
#: A tool the build ran, past its limit (P664): the sentence names the command.
TIMED_OUT_ENDING = StageEnding(build_codes.STAGE_TIMED_OUT, COULD_NOT_RUN, "%s")

BOARD_UNUSABLE_ENDING = StageEnding(build_codes.BOARD_UNUSABLE, COULD_NOT_RUN, "%s")
BOARD_ONLY_WITH_PARTS_ENDING = StageEnding(build_codes.BOARD_ONLY_WITH_PARTS, COULD_NOT_RUN,
                                           "the requirements say board_only and name parts: say one")
NO_PARTS_ENDING = StageEnding(build_codes.NO_PARTS, COULD_NOT_RUN,
                              "the requirements name no parts, so there is nothing to build; a board holding only the "
                              'microcontroller proves nothing. A project that runs on the board alone says "%s": true')
#: A crash in an emitter is a stage (P430, F5): its kind and its message, raw; guarded when it is printed.
BOARD_EMITTER_CRASHED_ENDING = StageEnding(build_codes.STAGE_CRASHED, COULD_NOT_RUN, "the board emitter crashed: %s: %s")
FOOTPRINT_EMITTER_CRASHED_ENDING = StageEnding(build_codes.STAGE_CRASHED, COULD_NOT_RUN, "the footprint emitter crashed: %s: %s")
SCHEMATIC_REFUSED_ENDING = StageEnding(build_codes.SCHEMATIC_REFUSED, COULD_NOT_RUN, "%s")
SCHEMATIC_NOTED_ENDING = StageEnding(build_codes.SCHEMATIC_NOTED, PROBLEMS, "%s")
ENGINE_MISSING_ENDING = StageEnding(build_codes.TOOL_MISSING, COULD_NOT_RUN,
                                    "%s — so the chain was not exercised; /spark:setup installs it")
TOOL_CANNOT_BUILD_ENDING = StageEnding(build_codes.TOOL_CANNOT_BUILD, COULD_NOT_RUN,
                                       "%s (%s) cannot build even a trivial board from here, so this is the toolchain, not "
                                       "the design. Use the project's own tsci (npm i @tscircuit/cli in the project) or one "
                                       "that builds on its own.\n%s")
NO_CIRCUIT_ENDING = StageEnding(build_codes.DESIGN_NOT_BUILT, PROBLEMS,
                                "no circuit.json was produced by %s (%s), which does build a trivial board\n%s")
CIRCUIT_ERRORS_ENDING = StageEnding(build_codes.DESIGN_NOT_BUILT, PROBLEMS, "%d error(s): %s; first: %s")
PART_STRANDED_ENDING = StageEnding(build_codes.PART_STRANDED, PROBLEMS,
                                   "%s. A board builds, routes and reports no error with a component joined to nothing — "
                                   "the parts around it are wired to nets it is simply not on")
#: The failure the build stage was written for: everything is placed, nothing is connected, and nothing raised.
NOT_ROUTED_ENDING = StageEnding(build_codes.NOT_ROUTED, PROBLEMS,
                                "built with 0 pcb_traces — every component is placed and no copper joins any of them. "
                                "tscircuit skips routing entirely when one net is unroutable, and that does not raise")
CONVERTER_MISSING_ENDING = StageEnding(build_codes.TOOL_MISSING, COULD_NOT_RUN, "%s")
FACT_MISSING_ENDING = StageEnding(build_codes.SIMULATION_FACT_MISSING, COULD_NOT_RUN, "%s")
NO_WOKWI_PART_TYPE_ENDING = StageEnding(build_codes.BOARD_NOT_IN_WOKWI, COULD_NOT_RUN,
                                        "the board record names no wokwi_part_type")
CHIP_NOT_COMPILED_ENDING = StageEnding(build_codes.CHIP_NOT_COMPILED, COULD_NOT_RUN, "%s")
#: A limit of the converter's mapping, not a defect in the design (audit B11): the converter's words follow.
CONVERTER_LACKS_PART_ENDING = StageEnding(build_codes.CONVERTER_LACKS_PART, COULD_NOT_RUN,
                                          "the converter has no Wokwi part for a component on this board — a mapping to "
                                          "add to its lib/mapping.ts, not a defect in the design, which built\n%s")
NO_DIAGRAM_ENDING = StageEnding(build_codes.NO_DIAGRAM, PROBLEMS, "no diagram was produced\n%s")
#: The same failure shape as a board with no copper: every part placed, nothing joined.
DIAGRAM_UNWIRED_ENDING = StageEnding(build_codes.DIAGRAM_UNWIRED, PROBLEMS,
                                     "a diagram with 0 connections. Every part is placed and none is wired, which is what "
                                     "an unmapped component looks like once the converter has given up on it")
#: Every part's record skips the simulation (P778): the diagram holds none of the project's parts, which is no defect.
EVERY_PART_SKIPPED_ENDING = StageEnding(build_codes.EVERY_PART_SKIPPED, SKIPPED, "every part is skipped from the simulation, "
                                                                           "so the diagram holds none of the project's parts, %s")
#: Anything no stage caught: could-not-run, never problems, because the tool failed, not the chain.
CHECK_SPINE_CRASHED_ENDING = StageEnding(build_codes.STAGE_CRASHED, COULD_NOT_RUN, "%s: %s")

REQUIREMENTS = StageDefinition("requirements", "the requirements file, read as a design before any folder is made",
                               (DESIGN_ERROR,))
BOARD = StageDefinition("board", "the board record the requirements name, from the project or spark's library",
                        (BOARD_UNUSABLE_ENDING,))
PARTS = StageDefinition("parts", "the part records the requirements name; listed only when it does not end ok",
                        (BOARD_ONLY_WITH_PARTS_ENDING, NO_PARTS_ENDING, DESIGN_ERROR, BOARD_ONLY_ENDING))
SCHEMATIC = StageDefinition("schematic", "board.tsx, written by the board emitter with the pin map made inside it",
                            (DESIGN_ERROR, BOARD_EMITTER_CRASHED_ENDING, SCHEMATIC_REFUSED_ENDING, BOARD_ONLY_ENDING))
SCHEMATIC_NOTES = StageDefinition("schematic-notes", "what the board emitter notes about a board it wrote; listed only "
                                                     "when there is a note, and the build goes on", (SCHEMATIC_NOTED_ENDING,))
FOOTPRINT = StageDefinition("footprint", "the board's footprint that board.tsx imports, drawn with the design's rules",
                            (DESIGN_ERROR, FOOTPRINT_EMITTER_CRASHED_ENDING, BOARD_ONLY_ENDING))
BUILD = StageDefinition("build", "the board engine (tsci) builds board.tsx, and the copper is counted",
                        (ENGINE_MISSING_ENDING, TIMED_OUT_ENDING, TOOL_CANNOT_BUILD_ENDING, NO_CIRCUIT_ENDING,
                         PART_STRANDED_ENDING, CIRCUIT_ERRORS_ENDING, NOT_ROUTED_ENDING, BOARD_ONLY_ENDING))
SIMULATION = StageDefinition("simulation", "the Wokwi diagram, its chips and wokwi.toml; no simulation runs",
                             (CONVERTER_MISSING_ENDING, FACT_MISSING_ENDING, NO_WOKWI_PART_TYPE_ENDING,
                              CHIP_NOT_COMPILED_ENDING, TIMED_OUT_ENDING, CONVERTER_LACKS_PART_ENDING, NO_DIAGRAM_ENDING,
                              DIAGRAM_UNWIRED_ENDING, EVERY_PART_SKIPPED_ENDING))
CHECK_SPINE = StageDefinition("check_spine", "not a stage the build runs: an error of the run itself that no stage caught",
                              (CHECK_SPINE_CRASHED_ENDING,))

#: The stages the build reports, in the order it runs them, and check_spine for a crash no stage caught.
BUILD_STAGES = (REQUIREMENTS, BOARD, PARTS, SCHEMATIC, SCHEMATIC_NOTES, FOOTPRINT, BUILD, SIMULATION, CHECK_SPINE)
#: Each definition by its name, for a design error that names the stage it stopped (`RefusedInputError.stage`).
STAGE_NAMED = {definition.name: definition for definition in BUILD_STAGES}


def skipped_the_build(stages):
    """Whether `stages` are a board-only build's (`build_service.board_alone`): its build stage is SKIPPED, so no board was built.
    A full build whose simulation stage is SKIPPED (every part skipped, P778) built its board, so it is not."""
    return any(stage.name == BUILD.name and stage.status == SKIPPED for stage in stages)
