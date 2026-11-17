"""
The sheet lists what to change on the bench after a rebuild (P300, #366): `sheet.write()` keeps a wiring record
beside the sheet, compares it with the new steps, and says each difference in the sheet and on stderr.

    python3 -m unittest tests.test_breadboard_record
"""

import argparse
import contextlib
import datetime
import shutil
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

from spark.breadboard import sheet  # noqa: E402
from spark.breadboard import bench_changes  # noqa: E402
import check_spine  # noqa: E402
from spark.build.stages import Stage  # noqa: E402
from fakes import run_build_board  # noqa: E402
from test_breadboard_keep import BUTTON_ONLY, FULL, LED_ONLY, build, change_requirements, new_project  # noqa: E402

SECTION = "### Changes since"
#: The times the tests give the sheets: a test sets `at` of a record, so the heading names a time the test knows.
TIME_A, TIME_B = "2026-03-04T10:32:00+01:00", "2026-03-05T11:47:00+01:00"
HEADING = "### Changes since the sheet spark wrote on "
OLD_HEADING = "### Changes since the last build"
NO_TIME_HEADING = "### Changes since the last sheet spark wrote"


def record(project):
    return json.loads((project / bench_changes.WiringLog.FILE_NAME).read_text())


def set_record(project, **keys):
    """A test setup: the record with these keys changed (the time of its sheet, for one)."""
    path = project / bench_changes.WiringLog.FILE_NAME
    path.write_text(json.dumps(dict(json.loads(path.read_text()), **keys)))


def said(at):
    """A time of a record as the heading says it: local, to the minute."""
    return datetime.datetime.fromisoformat(at).astimezone().strftime("%Y-%m-%d %H:%M")


def heading(project):
    """The line that heads the changes section, else None."""
    return next((line for line in (project / "breadboard.md").read_text().splitlines() if line.startswith(SECTION)), None)


def section(project):
    """The list lines of the sheet's changes section, else None."""
    text = (project / "breadboard.md").read_text()
    if SECTION not in text:
        return None
    return [line for line in text.split(SECTION, 1)[1].split("\n### ", 1)[0].splitlines() if line.startswith("- ")]


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
        self.assertEqual(section(project), ["- Nothing to change on the bench."])

    def test_adding_the_led_lists_what_to_put_in_the_sheet_and_the_result(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        written = build(project)
        lines = bench_changes.ChangeList().render(written.changes)
        self.assertEqual(lines[0], "Put LedRed5mm in the breadboard.")
        self.assertIn("Put R1 end 1 (in series with LedRed5mm A) in a free row.", lines)
        self.assertEqual([one.code for one in written.changes], ["added"] * 5 + ["rerouted"])
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
        jumper = next(bench_changes.ChangeList().line(one) for one in written.changes
                      if one.code == "removed" and one.kind == "jumper")
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
        (project / bench_changes.WiringLog.FILE_NAME).write_text("{not json")
        written = build(project)
        self.assertEqual(written.changes, [])
        self.assertRegex(" ".join(section(project)), r"cannot be compared.*cannot be read")
        self.assertEqual(len(record(project)["steps"]), 9)


class DrawnJumpersTest(unittest.TestCase):
    def test_a_first_build_records_every_jumper_spark_drew(self):
        project = new_project(FULL)
        build(project)
        self.assertEqual(record(project)["drawn_jumpers"],
                         [["12t.a", "17b.h"], ["14t.a", "6b.j"], ["17b.g", "8b.j"], ["24b.f", "4b.j"]])

    def test_a_jumper_the_person_moved_and_the_build_kept_is_not_recorded_as_spark_s(self):
        from test_breadboard_keep import edit
        project = new_project(FULL)
        build(project)
        edit(project, lambda drawn: drawn["connections"][1].__setitem__(1, "bb1:14t.b"))
        build(project)
        self.assertNotIn(["14t.b", "6b.j"], record(project)["drawn_jumpers"])
        self.assertEqual(len(record(project)["drawn_jumpers"]), 3)


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
        earlier = (project / bench_changes.WiringLog.FILE_NAME).read_text()
        with mock.patch.object(sheet.DRAWING_RENDERERS[1], "text", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                build(project)
        self.assertEqual((project / bench_changes.WiringLog.FILE_NAME).read_text(), earlier)

    def test_a_circuit_that_cannot_be_drawn_still_keeps_a_record_without_colors(self):
        project = new_project(LED_ONLY)
        with mock.patch.object(sheet, "_plan_layout", side_effect=sheet.drawing.NotDrawnError("no room", sheet.drawing.NO_HOLE_LEFT)):
            build(project)
        self.assertTrue(all(step["color"] is None for step in record(project)["steps"]))


class BaseTest(unittest.TestCase):
    """The list counts from the last sheet spark wrote for another design, and the heading says when that was (P875)."""

    def built(self, *designs):
        """A project built once for each design in turn; the record of each sheet is given a time the test knows."""
        project = new_project(designs[0])
        for number, design in enumerate(designs):
            if number:
                change_requirements(project, design)
            build(project)
            set_record(project, at=(TIME_A, TIME_B)[number % 2])
        return project

    def test_a_changed_design_built_twice_still_lists_the_changes_and_the_time_of_the_sheet_it_counts_from(self):
        project = self.built(BUTTON_ONLY)
        change_requirements(project, FULL)
        first = build(project)
        first_lines = section(project)
        set_record(project, at=TIME_B)
        again = build(project)
        self.assertEqual(section(project), first_lines)
        self.assertEqual(again.changes, first.changes)
        self.assertEqual(heading(project), HEADING + said(TIME_A))

    def test_a_third_design_lists_the_changes_from_the_second_design_s_sheet_only(self):
        project = self.built(BUTTON_ONLY, FULL)
        change_requirements(project, LED_ONLY)
        build(project)
        self.assertEqual(heading(project), HEADING + said(TIME_B))
        self.assertTrue(section(project))
        self.assertNotIn("- Put LedRed5mm in the breadboard.", section(project))

    def test_going_back_to_the_first_design_counts_from_the_second_design_s_sheet(self):
        project = self.built(BUTTON_ONLY, FULL)
        change_requirements(project, BUTTON_ONLY)
        written = build(project)
        self.assertEqual(heading(project), HEADING + said(TIME_B))
        self.assertIn("Take out LedRed5mm.", bench_changes.ChangeList().render(written.changes))

    def test_the_section_says_since_the_sheet_spark_wrote_on_a_time_and_never_the_bench(self):
        project = self.built(BUTTON_ONLY)
        change_requirements(project, FULL)
        build(project)
        text = (project / "breadboard.md").read_text()
        part = text[text.index(SECTION):text.index("### Steps")]
        self.assertTrue(part.startswith(HEADING + said(TIME_A) + "\n"))
        self.assertNotIn("bench", part)
        self.assertIn("Count from that sheet only if you wired it.", part)
        self.assertLess(part.index("Count from"), part.index("\n- "))

    def test_a_first_design_built_twice_keeps_the_first_design_heading(self):
        project = self.built(FULL)
        build(project)
        self.assertEqual(heading(project), OLD_HEADING)

    def test_a_record_from_before_the_base_lists_the_changes_and_says_no_time(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        old = {key: value for key, value in record(project).items() if key not in ("at", "base")}
        (project / bench_changes.WiringLog.FILE_NAME).write_text(json.dumps(old))
        change_requirements(project, FULL)
        written = build(project)
        self.assertEqual(heading(project), NO_TIME_HEADING)
        self.assertEqual(section(project), ["- " + line for line in bench_changes.ChangeList().render(written.changes)])
        self.assertTrue(written.changes)
        self.assertIsNone(written.since)
        self.assertIsNone(record(project)["base"]["at"])
        self.assertTrue(record(project)["at"])

    def test_a_broken_base_is_said_and_no_list_is_made(self):
        project = self.built(BUTTON_ONLY)
        set_record(project, base={"steps": "none", "at": None})
        written = build(project)
        self.assertEqual(written.changes, [])
        self.assertRegex(" ".join(section(project)), r"cannot be compared.*cannot be read")
        self.assertIsNone(record(project)["base"])

    def test_a_leftover_stage_file_stops_the_sheet_and_is_left_as_it_was(self):
        project = self.built(BUTTON_ONLY)
        change_requirements(project, FULL)
        earlier = ((project / "breadboard.md").read_text(), (project / bench_changes.WiringLog.FILE_NAME).read_text())
        leftover = project / (bench_changes.WiringLog.FILE_NAME + ".new")
        leftover.write_text("mine")
        with self.assertRaises(OSError) as stopped:
            build(project)
        self.assertIn("wiring-record.json.new is in the way: delete it if it is not yours", str(stopped.exception))
        self.assertEqual(leftover.read_text(), "mine")
        self.assertEqual(((project / "breadboard.md").read_text(), (project / bench_changes.WiringLog.FILE_NAME).read_text()), earlier)

    def test_a_link_at_the_stage_name_is_not_written_through(self):
        project = self.built(BUTTON_ONLY)
        change_requirements(project, FULL)
        outside = Path(tempfile.mkdtemp()) / "outside.txt"
        outside.write_text("outside")
        (project / (bench_changes.WiringLog.FILE_NAME + ".new")).symlink_to(outside)
        with self.assertRaises(OSError):
            build(project)
        self.assertEqual(outside.read_text(), "outside")
        self.assertTrue((project / (bench_changes.WiringLog.FILE_NAME + ".new")).is_symlink())

    def test_a_sheet_that_cannot_be_written_leaves_the_record_and_no_stage(self):
        project = self.built(BUTTON_ONLY)
        change_requirements(project, FULL)
        earlier = (project / bench_changes.WiringLog.FILE_NAME).read_text()
        (project / "breadboard.md").unlink()
        (project / "breadboard.md").mkdir()  # the sheet cannot be written over a folder
        with self.assertRaises(OSError):
            build(project)
        self.assertEqual((project / bench_changes.WiringLog.FILE_NAME).read_text(), earlier)
        self.assertEqual(sorted(one.name for one in project.glob("*.new")), [])


class CheckSpineTest(unittest.TestCase):
    """`check_spine --keep` carries each change as a kept entry, and --json carries the entry's fields."""

    def keep(self, project, variant, stages=None, as_json=True):
        work = Path(tempfile.mkdtemp())
        (work / "dist" / "board").mkdir(parents=True)
        shutil.copy(variant / "dist" / "board" / "circuit.json", work / "dist" / "board" / "circuit.json")
        args = argparse.Namespace(json=as_json, keep=project, requirements=str(project / "requirements.json"))
        stages = stages or [Stage("build", check_spine.OK, "fine")]
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}), contextlib.redirect_stdout(
                io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            run_build_board(stages, args, work)
        return (json.loads(out.getvalue())["kept"] if as_json else None), err.getvalue()

    def rebuilt(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        change_requirements(project, FULL)
        return project

    def test_each_change_is_a_kept_entry_with_its_fields(self):
        project = self.rebuilt()
        kept, said = self.keep(project, FULL)
        changed = [entry for entry in kept if entry["did"] == "changed"]
        self.assertEqual([entry["code"] for entry in changed], ["added"] * 5 + ["rerouted"])
        self.assertEqual(changed[0], {"file": str(project / "breadboard.md"), "did": "changed", "code": "added",
                                      "subject": "LedRed5mm", "color": None,
                                      "why": "Put LedRed5mm in the breadboard."})
        self.assertEqual(changed[2]["color"], "cyan")
        self.assertIn("  changed: Put LedRed5mm in the breadboard.", said)

    def test_json_keeps_every_field_of_a_kept_entry_but_the_line(self):
        project = new_project(FULL)
        build(project)
        from test_breadboard_keep import edit, move
        edit(project, move("LedRed5mm", dy=-500))
        kept, _ = self.keep(project, FULL)
        named = next(entry for entry in kept if entry["did"] == "move not kept")
        self.assertEqual((named["subject"], named["code"]), ("LedRed5mm", "pin-off-holes"))
        self.assertNotIn("line", named)

    def test_a_build_that_did_not_finish_keeps_the_record(self):
        project = self.rebuilt()
        earlier = (project / bench_changes.WiringLog.FILE_NAME).read_text()
        self.keep(project, FULL, [Stage("build", check_spine.PROBLEMS, "1 error")])
        self.assertFalse((project / "breadboard.md").exists())
        self.assertEqual((project / bench_changes.WiringLog.FILE_NAME).read_text(), earlier)

    def test_a_build_that_did_not_finish_keeps_the_list_for_the_next_build(self):
        project = self.rebuilt()
        first, _ = self.keep(project, FULL)
        self.keep(project, FULL, [Stage("build", check_spine.PROBLEMS, "1 error")])
        again, _ = self.keep(project, FULL)
        changed = [entry for entry in again if entry["did"] == "changed"]
        self.assertEqual([entry["code"] for entry in changed], ["added"] * 5 + ["rerouted"])
        self.assertEqual(changed, [entry for entry in first if entry["did"] == "changed"])

    def test_the_sheet_s_entry_names_the_time_of_the_sheet_it_counts_from(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        set_record(project, at=TIME_A)
        change_requirements(project, FULL)
        kept, _ = self.keep(project, FULL)
        sheet_entry = next(entry for entry in kept if entry["did"] == "wrote" and entry["file"].endswith("breadboard.md"))
        self.assertEqual(sheet_entry["since"], TIME_A)
        self.assertEqual(sheet_entry["since"], record(project)["base"]["at"])


if __name__ == "__main__":
    unittest.main()
