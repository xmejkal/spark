"""
The sheet lists what to change on the bench after a rebuild (P300, #366): `breadboard.write()` keeps a wiring record
beside the sheet, compares it with the new steps, and says each difference in the sheet and on stderr.

    python3 -m unittest tests.test_breadboard_record
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import breadboard  # noqa: E402
import breadboard_changes  # noqa: E402
from test_breadboard_keep import BUTTON_ONLY, FULL, LED_ONLY, build, change_requirements, new_project  # noqa: E402

SECTION = "### Changes since the last build"


def record(project):
    return json.loads((project / breadboard_changes.WiringRecord.FILE_NAME).read_text())


def section(project):
    """The lines of the sheet's changes section, else None."""
    text = (project / "breadboard.md").read_text()
    if SECTION not in text:
        return None
    return [line for line in text.split(SECTION, 1)[1].split("\n### ", 1)[0].splitlines() if line.strip()]


class FirstBuildTest(unittest.TestCase):
    def test_a_first_build_writes_a_record_and_no_changes_section(self):
        project = new_project(FULL)
        written = build(project)
        self.assertEqual(written.changes, [])
        self.assertIsNone(section(project))
        self.assertEqual(len(record(project)["steps"]), 9)


class RebuildTest(unittest.TestCase):
    def test_a_rebuild_with_nothing_changed_says_so(self):
        project = new_project(FULL)
        build(project)
        written = build(project)
        self.assertEqual(written.changes, [])
        self.assertEqual(section(project), ["Nothing to change on the bench."])

    def test_adding_the_led_lists_what_to_put_in_the_sheet_and_the_result(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        written = build(project)
        lines = breadboard_changes.ChangeList().render(written.changes)
        self.assertEqual(lines[0], "Put LedRed5mm in the breadboard.")
        self.assertIn("Put R1 end 1 in a free row.", lines)
        self.assertEqual([one.code for one in written.changes], [breadboard_changes.ADDED] * 5 + [breadboard_changes.REROUTED])
        self.assertEqual(lines[-1], "Move the green jumper from board GND: it now goes to the row of LedRed5mm K "
                                    "(it went to the row of TactileButton B).")
        self.assertEqual(section(project), ["- " + line for line in lines])
        self.assertEqual(len(record(project)["steps"]), 9)

    def test_the_section_comes_before_the_steps(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        build(project)
        text = (project / "breadboard.md").read_text()
        self.assertLess(text.index(SECTION), text.index("### Steps"))

    def test_the_lines_name_the_colors_the_earlier_sheet_showed(self):
        project = new_project(FULL)
        build(project)
        change_requirements(project, BUTTON_ONLY)
        written = build(project)
        jumper = next(breadboard_changes.ChangeList().line(one) for one in written.changes
                      if one.code == breadboard_changes.REMOVED and one.kind == breadboard_changes.JUMPER)
        self.assertRegex(jumper, r"^Take out the (red|orange|gold|green|cyan|blue|purple|magenta) jumper from ")

    def test_the_command_prints_each_change_on_stderr(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        errors = io.StringIO()
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}), contextlib.redirect_stderr(errors), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(breadboard.main([str(project / "requirements.json")]), breadboard.EXIT_OK)
        self.assertIn("change: Put LedRed5mm in the breadboard.", errors.getvalue())

    def test_a_record_that_cannot_be_read_is_said_and_written_again(self):
        project = new_project(FULL)
        build(project)
        (project / breadboard_changes.WiringRecord.FILE_NAME).write_text("{not json")
        written = build(project)
        self.assertEqual(written.changes, [])
        self.assertRegex(" ".join(section(project)), r"cannot be compared.*cannot be read")
        self.assertEqual(len(record(project)["steps"]), 9)


class WriteOrderTest(unittest.TestCase):
    def test_the_record_is_written_right_after_the_sheet_so_a_failed_drawing_leaves_them_agreeing(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        (project / "breadboard.svg").unlink()
        (project / "breadboard.svg").mkdir()  # the picture cannot be written over a folder
        with self.assertRaises(OSError):
            build(project)
        self.assertEqual(len(record(project)["steps"]), 9)
        self.assertIn("LedRed5mm", (project / "breadboard.md").read_text())

    def test_a_renderer_that_fails_leaves_the_earlier_sheet_and_record_alone(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        earlier = (project / breadboard_changes.WiringRecord.FILE_NAME).read_text()
        with mock.patch.object(breadboard.DRAWING_RENDERERS[1], "text", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                build(project)
        self.assertEqual((project / breadboard_changes.WiringRecord.FILE_NAME).read_text(), earlier)

    def test_a_circuit_that_cannot_be_drawn_still_keeps_a_record_without_colors(self):
        project = new_project(LED_ONLY)
        with mock.patch.object(breadboard, "_plan_layout", side_effect=breadboard.breadboard_drawing.NotDrawn("no room")):
            build(project)
        self.assertTrue(all(step["color"] is None for step in record(project)["steps"]))


if __name__ == "__main__":
    unittest.main()
