"""
P852: the build's stages come from one table, `stages.BUILD_STAGES`. Each ending's code is one build_codes knows, each
message is filled with % (council D5), a definition makes only the Stages of its own endings, and `check_spine.py --help`
lists the table.
"""

import ast
import contextlib
import io
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_spine  # noqa: E402
from spark.build import build_codes, stages as stage_table  # noqa: E402
from spark.build.build_board import BuildBoard  # noqa: E402
from spark.build.stage_help_table import StageHelpTable, StageMarkdownTable  # noqa: E402
from spark.build.stages import (BOARD, BUILD_STAGES, DESIGN_ERROR, FOOTPRINT, NO_PARTS_ENDING, PARTS, SCHEMATIC,  # noqa: E402
                                STAGE_NAMED, StageDefinition, StageEnding)
from spark.core.outcomes import COULD_NOT_RUN, OK, SKIPPED  # noqa: E402
from spark.design import board_emitter  # noqa: E402
from spark.design.loader import DesignError  # noqa: E402

#: Every ending of the table, once, with a stage that has it.
ENDINGS = {ending: definition for definition in BUILD_STAGES for ending in definition.endings}


#: Each ending of each stage by the ending's name in stages.py, with its code and status. A literal, so a code or a status
#: swapped in the table fails here.
ENDS_AS = {
    ("requirements", "DESIGN_ERROR"): (None, "could-not-run"),
    ("board", "BOARD_UNUSABLE_ENDING"): ("board_unusable", "could-not-run"),
    ("parts", "BOARD_ONLY_WITH_PARTS_ENDING"): ("board_only_with_parts", "could-not-run"),
    ("parts", "NO_PARTS_ENDING"): ("no_parts", "could-not-run"),
    ("parts", "DESIGN_ERROR"): (None, "could-not-run"),
    ("parts", "BOARD_ONLY_ENDING"): ("board_only", "skipped"),
    ("schematic", "DESIGN_ERROR"): (None, "could-not-run"),
    ("schematic", "BOARD_EMITTER_CRASHED_ENDING"): ("stage_crashed", "could-not-run"),
    ("schematic", "SCHEMATIC_REFUSED_ENDING"): ("schematic_refused", "could-not-run"),
    ("schematic", "BOARD_ONLY_ENDING"): ("board_only", "skipped"),
    ("schematic-notes", "SCHEMATIC_NOTED_ENDING"): ("schematic_noted", "problems"),
    ("footprint", "DESIGN_ERROR"): (None, "could-not-run"),
    ("footprint", "FOOTPRINT_EMITTER_CRASHED_ENDING"): ("stage_crashed", "could-not-run"),
    ("footprint", "BOARD_ONLY_ENDING"): ("board_only", "skipped"),
    ("build", "ENGINE_MISSING_ENDING"): ("tool_missing", "could-not-run"),
    # P1058: a tools file the engine lookup cannot read, or one that is no tools list, keeps its own code
    ("build", "TOOLS_FILE_REFUSED_ENDING"): ("file_refused", "could-not-run"),
    ("build", "TOOLS_LIST_BROKEN_ENDING"): ("tools_list_broken", "could-not-run"),
    ("build", "TIMED_OUT_ENDING"): ("stage_timed_out", "could-not-run"),
    ("build", "TOOL_CANNOT_BUILD_ENDING"): ("tool_cannot_build", "could-not-run"),
    ("build", "NO_CIRCUIT_ENDING"): ("design_not_built", "problems"),
    ("build", "PART_STRANDED_ENDING"): ("part_stranded", "problems"),
    ("build", "CIRCUIT_ERRORS_ENDING"): ("design_not_built", "problems"),
    ("build", "NOT_ROUTED_ENDING"): ("not_routed", "problems"),
    ("build", "BOARD_ONLY_ENDING"): ("board_only", "skipped"),
    ("simulation", "CONVERTER_MISSING_ENDING"): ("tool_missing", "could-not-run"),
    ("simulation", "FACT_MISSING_ENDING"): ("simulation_fact_missing", "could-not-run"),
    # P977: a board Wokwi has no model of has its own code, so the flow's guide can pass that build and no other
    ("simulation", "NO_WOKWI_PART_TYPE_ENDING"): ("board_not_in_wokwi", "could-not-run"),
    ("simulation", "CHIP_NOT_COMPILED_ENDING"): ("chip_not_compiled", "could-not-run"),
    ("simulation", "TIMED_OUT_ENDING"): ("stage_timed_out", "could-not-run"),
    ("simulation", "CONVERTER_LACKS_PART_ENDING"): ("converter_lacks_part", "could-not-run"),
    ("simulation", "NO_DIAGRAM_ENDING"): ("no_diagram", "problems"),
    ("simulation", "DIAGRAM_UNWIRED_ENDING"): ("diagram_unwired", "problems"),
    ("simulation", "EVERY_PART_SKIPPED_ENDING"): ("every_part_skipped", "skipped"),
    ("check_spine", "CHECK_SPINE_CRASHED_ENDING"): ("stage_crashed", "could-not-run"),
}


class TheTableTest(unittest.TestCase):
    def test_each_stage_ends_each_way_with_the_code_and_status_it_always_had(self):
        named = {value: name for name, value in vars(stage_table).items() if isinstance(value, StageEnding)}
        self.assertEqual({(definition.name, named[ending]): (ending.code, ending.status)
                          for definition in BUILD_STAGES for ending in definition.endings}, ENDS_AS)

    def test_each_ending_names_a_code_build_codes_knows_or_is_the_design_error(self):
        # P936, the PO 2026-11-20: a skip has its code too, so only the design error, whose code is its own, has none
        for ending in ENDINGS:
            if ending.code is None:
                self.assertIs(ending, DESIGN_ERROR)
            else:
                # P935 PR 5: by identity, so an ending holds the table's Code, never a plain word of the same letters
                self.assertTrue(any(ending.code is held for held in build_codes.CODES), ending)
            self.assertNotEqual(ending.status, OK, ending)

    def test_each_ending_is_named_and_a_call_site_ends_a_stage_with_it(self):
        """An ending no call site uses would still show in --help: each is a constant of stages.py that a call in scripts/
        hands to `ended`, the design error's to `stopped_by`."""
        named = {value: name for name, value in vars(stage_table).items() if isinstance(value, StageEnding)}
        self.assertLessEqual(set(ENDINGS), set(named))
        calls = [node for path in (ROOT / "scripts").rglob("*.py") if path.name != "stages.py"
                 for node in ast.walk(ast.parse(path.read_text())) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        used = {node.args[0].id for node in calls if node.func.attr == "ended" and isinstance(node.args[0], ast.Name)}
        used |= {"DESIGN_ERROR" for node in calls if node.func.attr == "stopped_by"}
        self.assertEqual(sorted(named[ending] for ending in ENDINGS if named[ending] not in used), [])

    def test_each_name_is_one_stage_s_and_the_emitter_names_the_table_s(self):
        self.assertEqual(len(STAGE_NAMED), len(BUILD_STAGES))
        self.assertIs(STAGE_NAMED["schematic"], SCHEMATIC)
        # a refused input names its stage with these, so STAGE_NAMED[refused.stage] finds it
        self.assertEqual([STAGE_NAMED[board_emitter.SCHEMATIC_STAGE], STAGE_NAMED[board_emitter.FOOTPRINT_STAGE]], [SCHEMATIC, FOOTPRINT])


class EachMessageIsFilledWithPercentTest(unittest.TestCase):
    """Council D5: every message is filled with %, so a value too few, one too many and a lone % all raise."""

    def test_each_ending_fills_with_one_value_per_placeholder_and_no_other_count(self):
        for ending, definition in ENDINGS.items():
            if ending is DESIGN_ERROR:
                continue
            placeholders = re.findall(r"%(.)", ending.message.replace("%%", ""))
            self.assertLessEqual(set(placeholders), {"s", "d"}, ending)  # a literal % is written %%
            values = [7 if placeholder == "d" else "<value>" for placeholder in placeholders]
            stage = definition.ended(ending, *values)
            self.assertEqual((stage.name, stage.status, stage.code), (definition.name, ending.status, ending.code))
            self.assertEqual(stage.detail.count("<value>"), placeholders.count("s"), ending)
            with self.assertRaises(TypeError):
                definition.ended(ending, *values, "one too many")
            if values:
                with self.assertRaises(TypeError):
                    definition.ended(ending, *values[1:])

    def test_a_lone_percent_raises(self):
        lone = StageEnding("no_parts", COULD_NOT_RUN, "100% of it")
        with self.assertRaises((TypeError, ValueError)):
            PARTS._replace(endings=(lone,)).ended(lone)


class ADefinitionMakesOnlyItsOwnStagesTest(unittest.TestCase):
    def test_an_ending_of_another_stage_raises(self):
        with self.assertRaises(ValueError):
            BOARD.ended(NO_PARTS_ENDING, "board_only")

    def test_a_skip_with_no_code_raises(self):
        # P936: every ending but the design error names its code, a skip too
        uncoded = StageEnding(None, SKIPPED, "nothing to do")
        with self.assertRaises(ValueError):
            PARTS._replace(endings=(uncoded,)).ended(uncoded)

    def test_the_design_error_is_made_by_stopped_by_alone_and_only_where_one_can_stop(self):
        with self.assertRaises(ValueError):
            PARTS.ended(DESIGN_ERROR, "a sentence")
        with self.assertRaises(ValueError):
            BOARD.stopped_by(DesignError("no part called %r", "x", code="part_unusable"))

    def test_stopped_by_gives_the_error_s_sentence_and_code_and_then_the_hint(self):
        stage = FOOTPRINT.stopped_by(DesignError("no footprint for %s", "x", code="board_unusable"), "\nhint")
        self.assertEqual((stage.name, stage.status, stage.detail, stage.code),
                         ("footprint", COULD_NOT_RUN, "no footprint for x\nhint", "board_unusable"))


class TheHelpListsTheTableTest(unittest.TestCase):
    def test_check_spine_help_names_each_stage_its_summary_and_each_code_with_its_meaning(self):
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed), self.assertRaises(SystemExit):
            check_spine.main(["--help"])
        self.assertIn(StageHelpTable.render(BUILD_STAGES), printed.getvalue())
        said = " ".join(printed.getvalue().split())  # argparse wraps nothing here, the table wraps at 120
        for definition in BUILD_STAGES:
            self.assertIn("%s %s" % (definition.name, definition.summary), said)
        for code in {ending.code for ending in ENDINGS if ending.code}:
            self.assertIn("%s: %s" % (code, " ".join(build_codes.CODES[code].split())), said)
        # P936: a skip says its code and meaning, board_only once for each of its four stages
        for code, times in (("board_only", 4), ("every_part_skipped", 1)):
            self.assertEqual(said.count("skipped %s: %s" % (code, " ".join(build_codes.CODES[code].split()))), times, code)
        self.assertNotIn("…", said)
        self.assertEqual(said.count("design_not_built:"), 1)  # two endings of the build stage, one status and one code


class TheMarkdownTableTest(unittest.TestCase):
    """P936: how-it-works.md's stage table is StageMarkdownTable's text, from the same endings as the help."""

    def test_a_row_per_stage_its_summary_escaped_and_its_codes_grouped_by_status_once(self):
        definitions = (StageDefinition("one", "the first | stage", (DESIGN_ERROR, NO_PARTS_ENDING, stage_table.BOARD_ONLY_ENDING)),
                       StageDefinition("two", "the second", (stage_table.CIRCUIT_ERRORS_ENDING, stage_table.NO_CIRCUIT_ENDING,
                                                             stage_table.NOT_ROUTED_ENDING, stage_table.TIMED_OUT_ENDING)))
        self.assertEqual(StageMarkdownTable.render(definitions).splitlines(), [
            "| stage | what it is | how it ends when not ok |", "|---|---|---|",
            "| one | the first \\| stage | could-not-run: a design error, with its own code (design_codes), `no_parts`; "
            "skipped: `board_only` |",
            "| two | the second | problems: `design_not_built`, `not_routed`; could-not-run: `stage_timed_out` |"])

    def test_the_build_operation_holds_the_table_as_data(self):
        # P936: --describe and MCP read BuildBoard.stages, never the rendered help
        self.assertIs(BuildBoard.stages, BUILD_STAGES)
        self.assertEqual(BuildBoard.details, StageHelpTable.render(BUILD_STAGES))


if __name__ == "__main__":
    unittest.main()
