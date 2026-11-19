"""
P852: the build's stages come from one table, `stages.BUILD_STAGES`. Each ending's code is one build_codes knows, each
message is filled with % (council D5), a definition makes only the Stages of its own endings, and `check_spine.py --help`
lists the table.
"""

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
from spark.build import build_codes  # noqa: E402
from spark.build.stages import (BOARD, BUILD_STAGES, DESIGN_ERROR, FOOTPRINT, NO_PARTS_ENDING, PARTS, SCHEMATIC,  # noqa: E402
                                STAGE_NAMED, StageEnding)
from spark.core.outcomes import COULD_NOT_RUN, OK, SKIPPED  # noqa: E402
from spark.design.loader import DesignError  # noqa: E402

#: Every ending of the table, once, with a stage that has it.
ENDINGS = {ending: definition for definition in BUILD_STAGES for ending in definition.endings}


class TheTableTest(unittest.TestCase):
    def test_each_ending_names_a_code_build_codes_knows_or_is_a_skip_or_the_design_error(self):
        for ending in ENDINGS:
            if ending.code is None:
                self.assertTrue(ending.status == SKIPPED or ending is DESIGN_ERROR, ending)
            else:
                self.assertIn(ending.code, build_codes.CODES, ending)
            self.assertNotEqual(ending.status, OK, ending)

    def test_each_name_is_one_stage_s(self):
        self.assertEqual(len(STAGE_NAMED), len(BUILD_STAGES))
        self.assertIs(STAGE_NAMED["schematic"], SCHEMATIC)


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
        said = " ".join(printed.getvalue().split())  # argparse wraps nothing here, the table wraps at 120
        for definition in BUILD_STAGES:
            self.assertIn("%s %s" % (definition.name, definition.summary), said)
        for code in {ending.code for ending in ENDINGS if ending.code}:
            self.assertIn("%s: %s" % (code, " ".join(build_codes.CODES[code].split())), said)
        self.assertIn("skipped every part is skipped from the simulation, so the diagram holds none of the project's parts, …", said)


if __name__ == "__main__":
    unittest.main()
