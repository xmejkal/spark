"""
The breadboard sheet (P191, #143): from the board that was built, what to put on a breadboard and how to wire it, in
the board's printed labels and the parts' legs.

The fixture is the journey's button-and-LED project as built on 2026-10-11: its requirements, and the parts, ports,
traces and nets of its built circuit (tests/data/breadboard/button-light/README.md).

    python3 -m unittest tests.test_breadboard
"""

import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import breadboard  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"


def a_copy():
    """The fixture project in a folder of its own, so a run may write its sheet there."""
    project = Path(tempfile.mkdtemp()) / "button-light"
    shutil.copytree(FIXTURE, project)
    return project


def in_store(home):
    return mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})


class TheSheetTest(unittest.TestCase):
    def setUp(self):
        self.project = a_copy()
        self.home = Path(tempfile.mkdtemp())
        with in_store(self.home):
            self.text = breadboard.sheet(self.project / "requirements.json")

    def connections(self):
        return [line for line in self.text.splitlines() if re.match(r"^\d+\. ", line)]

    def test_each_point_of_the_built_circuit_is_one_line(self):
        # Five points: D3 with the button and the pull-up, 3V3 with the pull-up's other end, ground with the button and
        # the LED's cathode, A5 with the LED resistor, and the LED resistor's other end with the anode.
        self.assertEqual(len(self.connections()), 5, self.text)

    def test_a_point_names_the_board_s_printed_label_and_every_part_on_it(self):
        d3 = next(line for line in self.connections() if "board D3" in line)
        self.assertIn("TactileButton A", d3)
        self.assertIn("10kΩ pull-up, end 1", d3)
        a5 = next(line for line in self.connections() if "board A5" in line)
        self.assertIn("330Ω, end 1", a5)

    def test_the_board_s_ground_pads_are_one_point(self):
        grounds = [line for line in self.connections() if "board GND" in line]
        self.assertEqual(len(grounds), 1, self.text)
        self.assertNotRegex(self.text, r"GND\d")
        self.assertIn("LedRed5mm K", grounds[0])

    def test_a_leg_the_record_describes_is_named(self):
        self.assertIn("LedRed5mm A (the anode, the longer leg)", self.text)
        self.assertIn("LedRed5mm K (the cathode, the shorter leg", self.text)

    def test_the_parts_list_names_the_board_each_part_and_each_resistor_with_its_purpose(self):
        self.assertIn("DFRobot FireBeetle 2 ESP32-S3", self.text)
        self.assertIn("10kΩ resistor", self.text)
        self.assertIn("pull-up on TactileButton A", self.text)
        self.assertIn("330Ω resistor", self.text)
        self.assertIn("in series with LedRed5mm A", self.text)
        self.assertIn("a breadboard and jumper wires", self.text)


class WhatYouOwnTest(unittest.TestCase):
    def test_a_part_your_drawer_holds_for_this_project_is_yours_and_the_rest_to_get(self):
        project, home = a_copy(), Path(tempfile.mkdtemp())
        (home / "drawer").mkdir()
        (home / "drawer" / "firebeetle-2-esp32-s3.json").write_text(json.dumps(
            {"schema": 1, "label": "FireBeetle 2 ESP32-S3", "count": 1, "is": {"board": "firebeetle2-esp32s3"},
             "used_in": {"button-light": 1}}))
        (home / "projects.json").write_text(json.dumps({"button-light": str(project)}))
        with in_store(home):
            text = breadboard.sheet(project / "requirements.json")
        board = next(line for line in text.splitlines() if "DFRobot FireBeetle 2 ESP32-S3" in line and "|" in line)
        self.assertIn("yours", board)
        led = next(line for line in text.splitlines() if "L-7113ID" in line and "|" in line)
        self.assertIn("to get", led)


class TheCommandLineTest(unittest.TestCase):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with in_store(Path(tempfile.mkdtemp())), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = breadboard.main(list(argv))
        return code, out.getvalue() + err.getvalue()

    def test_it_writes_the_sheet_into_the_project(self):
        project = a_copy()
        code, said = self.run_main(str(project / "requirements.json"))
        self.assertEqual(code, 0, said)
        self.assertIn("board D3", (project / "breadboard.md").read_text())
        self.assertIn("wrote", said)

    def test_without_a_built_circuit_it_says_to_build_first(self):
        project = a_copy()
        shutil.rmtree(project / "dist")
        code, said = self.run_main(str(project / "requirements.json"))
        self.assertEqual(code, 2)
        self.assertIn("check_spine.py requirements.json --keep .", said)
        self.assertFalse((project / "breadboard.md").exists())


if __name__ == "__main__":
    unittest.main()
