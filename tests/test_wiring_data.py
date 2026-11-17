"""
The wiring of one build as data (P826, #1184): the numbered steps and what must be true before power is applied, which a
page reads, equal to what breadboard.md prints. The expected sheets of the fixtures are the reference, never a
renderer's output.

    python3 -m unittest tests.test_wiring_data
"""

import html
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
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from fakes import amplifier_alone  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import before_power  # noqa: E402
from spark.breadboard import sheet  # noqa: E402
import parts  # noqa: E402

FIXTURES = ROOT / "tests" / "data" / "breadboard"


def in_store(home):
    return mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})


def a_copy(name):
    """A fixture project in a folder of its own."""
    project = Path(tempfile.mkdtemp()) / name
    shutil.copytree(FIXTURES / name, project)
    return project


def expected_steps(text):
    """[(number, words)] of the numbered lines under "### Steps" of a sheet."""
    section = text.split("### Steps", 1)[1].split("### Diagram", 1)[0]
    return [(int(found.group(1)), found.group(2)) for found in re.finditer(r"^(\d+)\. (.*)$", section, re.MULTILINE)]


def expected_before_power(text):
    """The lines of a sheet's "Before you power it" section, after its heading's blank line."""
    return text.split("## Before you power it\n\n", 1)[1].rstrip("\n").split("\n")


class TheDataReadsAsTheSheetTest(unittest.TestCase):
    """On both fixtures: the steps and the before-power lines equal the expected sheet's, line for line."""

    def test_the_steps_and_the_before_power_lines_equal_the_sheet_s(self):
        for name in ("motor", "button-light"):
            with self.subTest(fixture=name):
                project = a_copy(name)
                with in_store(Path(tempfile.mkdtemp())):
                    data = sheet.wiring_data(project / "requirements.json")
                expected = (FIXTURES / name / "breadboard.expected.md").read_text()
                self.assertEqual([(step.number, step.words) for step in data.steps], expected_steps(expected))
                self.assertEqual(before_power.BeforePowerList().render(data.before_power), expected_before_power(expected))


class TheMotorDataTest(unittest.TestCase):
    """The motor fixture holds every kind, and the tactile button twice, so its host requirements are said once."""

    @classmethod
    def setUpClass(cls):
        with in_store(Path(tempfile.mkdtemp())):
            cls.data = sheet.wiring_data(a_copy("motor") / "requirements.json")
        cls.items = cls.data.before_power.items

    def test_each_item_reads_as_the_expected_section(self):
        # Written from the "Before you power it" section of motor/breadboard.expected.md.
        l9110s, inlet, button = "L9110S dual motor driver module", "JST PH 2-pin power inlet", "6x6 mm tactile push button"
        self.assertEqual([(item.kind, item.subject, item.pin, item.record) for item in self.items], [
            ("off-board-supply", "MOTOR6V", None, None),
            ("conflict", "L9110sModule", "AIA", "l9110s-module"),
            ("conflict", "L9110sModule", "AIB", "l9110s-module"),
            ("unused-pin", "L9110sModule", "BIA", "l9110s-module"),
            ("unused-pin", "L9110sModule", "BIB", "l9110s-module"),
            ("host-requirement", l9110s, None, "l9110s-module"),
            ("host-requirement", l9110s, None, "l9110s-module"),
            ("host-requirement", inlet, None, "jst-ph-2-power-inlet"),
            ("host-requirement", inlet, None, "jst-ph-2-power-inlet"),
            ("host-requirement", inlet, None, "jst-ph-2-power-inlet"),
            ("host-requirement", inlet, None, "jst-ph-2-power-inlet"),
            ("firmware-pull", "BtnOpen", "A", "tactile-button"),
            ("host-requirement", button, None, "tactile-button"),
            ("host-requirement", button, None, "tactile-button"),
            ("firmware-pull", "BtnMode", "A", "tactile-button"),
        ])

    def test_a_supply_names_its_users_sorted_and_says_nothing_of_its_own(self):
        supply = self.items[0]
        self.assertEqual(supply.users, ("JstPh2PowerInlet", "L9110sModule"))
        self.assertIsNone(supply.said)
        self.assertEqual({item.users for item in self.items[1:]}, {()})

    def test_each_kind_says_the_record_s_own_words(self):
        said = {item.kind: item.said for item in reversed(self.items)}  # the first item of each kind, by its kind's word
        self.assertTrue(said["conflict"].startswith("AIA: the board's 10000 ohm pull-down"), said)
        self.assertEqual(said["unused-pin"],
                         "channel B is unused in a one-motor design and must not float — tie it to the driver's own ground")
        self.assertTrue(said["host-requirement"].startswith("Pull both inputs down in HARDWARE."), said)
        self.assertIsNone(said["firmware-pull"])

    def test_the_records_are_the_ids_of_the_line_that_names_each_record_whole(self):
        self.assertEqual(self.data.before_power.records, ["jst-ph-2-power-inlet", "l9110s-module", "tactile-button"])

    def test_the_supply_s_step_has_its_edge_and_a_placing_step_has_none(self):
        self.assertEqual(self.data.steps[19].number, 20)
        self.assertEqual(self.data.steps[19].edge, ("MOTOR6V supply", "JstPh2PowerInlet VCC"))
        self.assertIsNone(self.data.steps[0].edge)


class AnUnusedPinWithNoNoteTest(unittest.TestCase):
    """A made-up part: an unused pin with no note, no firmware pulls and no CONFLICT. The sheet printed its line with
    nothing after the colon, so the item says "", not None."""

    def test_it_says_nothing_after_the_colon(self):
        part = {"id": "made-up-module", "name": "Made-up module", "unused_pins": [{"pin": "EN"}]}
        data = before_power.BeforePower.of([part], {})
        self.assertEqual([item.said for item in data.items], [""])
        line = before_power.BeforePowerList().render(data)[0]
        self.assertTrue(line.endswith(" EN: "), line)


class TheHtmlLinesTest(unittest.TestCase):
    """The page's lines (P828): the sheet's words in HTML, and a record's own words stay text."""

    @staticmethod
    def as_text(line):
        return html.unescape(re.sub(r"<[^>]+>", "", line))

    def test_the_html_before_power_line_holds_the_sheet_s_words_for_every_kind(self):
        with in_store(Path(tempfile.mkdtemp())):
            data = sheet.wiring_data(a_copy("motor") / "requirements.json")
        self.assertEqual({item.kind for item in data.before_power.items}, {
            "off-board-supply", "conflict", "firmware-pull", "unused-pin", "host-requirement"})
        markdown = before_power.BeforePowerList().render(data.before_power)[:len(data.before_power.items)]
        lines = before_power.BeforePowerHtmlList().items([item._asdict() for item in data.before_power.items])
        self.assertEqual([self.as_text(line) for line in lines],
                         [line.removeprefix("- ").replace("**", "").replace("`", "") for line in markdown])
        self.assertTrue(all(line.startswith("<li>") and line.endswith("</li>") for line in lines))
        self.assertIn("<strong>CONFLICT</strong>", "".join(lines))
        self.assertIn("<code>parts.py --show</code>", "".join(lines))

    def test_a_record_s_own_marks_and_signs_come_out_as_text(self):
        said = "2**8 or 2**9, a lone ` tick, a & b and x <= y <b>"
        item = {"kind": "conflict", "subject": "A&B", "pin": "X", "record": "r", "said": said, "users": ()}
        line = before_power.BeforePowerHtmlList().items([item])[0]
        self.assertEqual(line, "<li><strong>CONFLICT</strong> on A&amp;B: 2**8 or 2**9, a lone ` tick, a &amp; b and x &lt;= y &lt;b&gt;</li>")

    def test_the_records_line_names_each_record_whole(self):
        line = before_power.BeforePowerHtmlList().records_line(["a-b", "c<d"])
        self.assertEqual(line, "<p>Each record whole, with what it asks of the board: "
                               "<code>parts.py --show a-b</code>, <code>parts.py --show c&lt;d</code>.</p>")


class TheAmplifierAloneTest(unittest.TestCase):
    """
    P864 (#1230): the DFR0954 with no speaker terminal listed. Its circuit is the amplifier fixture's real build, cut by hand
    (`fakes.amplifier_alone`): no real build of the amplifier alone is proved. The sheet tells the person about the module's own
    socket, in the record's own state of proof.
    """

    UNVERIFIED = ("- Max98357aDfr0954 SPK_P, SPK_N: the record says that the module has its own socket for the speaker, and nobody "
                  "has looked at a real module yet. Look for it first. If it is there, plug only the speaker into it: never a supply, "
                  "and never ground. If it is not there, wire the speaker to the SPK_P, SPK_N pads.")
    VERIFIED = ("- Max98357aDfr0954 SPK_P, SPK_N end in the module's own socket: plug only the speaker into it, never a supply "
                "and never ground.")

    def alone(self, part_id="max98357a-dfr0954"):
        project = a_copy("amplifier")
        requirements = {"board": "firebeetle2-esp32s3", "parts": [part_id]}
        (project / "requirements.json").write_text(json.dumps(requirements))
        (project / "dist" / "board" / "built-from.json").write_text(json.dumps({"requirements": requirements}))
        circuit = project / "dist" / "board" / "circuit.json"
        circuit.write_text(json.dumps(amplifier_alone(json.loads(circuit.read_text()))))
        return project

    def test_the_sheet_says_to_plug_the_speaker_into_the_module_s_own_socket_and_never_a_supply(self):
        project = self.alone()
        with in_store(Path(tempfile.mkdtemp())):
            text = sheet.sheet(project / "requirements.json")
            data = sheet.wiring_data(project / "requirements.json")
        self.assertIn(self.UNVERIFIED, expected_before_power(text))
        self.assertEqual(before_power.BeforePowerList().render(data.before_power)[:-2], expected_before_power(text)[:-2])
        html_lines = before_power.BeforePowerHtmlList().items([item._asdict() for item in data.before_power.items])
        self.assertIn(self.UNVERIFIED.removeprefix("- "), [html.unescape(re.sub(r"<[^>]+>", "", line)) for line in html_lines])
        for net in ("SPEAKER_P", "SPEAKER_N"):
            self.assertNotIn("%s comes from off the board" % net, text)

    def test_a_fact_write_of_own_socket_makes_the_sheet_say_it_as_a_fact(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        record = json.loads((ROOT / "parts" / "max98357a-dfr0954.json").read_text())
        (home / "catalog" / "x-amp.json").write_text(json.dumps(dict(record, id="x-amp")))
        bench = dict(record["own_socket"], verified=True, source="bench, 2026-11-20, meter on the owned module, Petr Smejkal")
        given = Path(tempfile.mkdtemp()) / "facts.json"
        given.write_text(json.dumps({"own_socket": bench}))
        project = self.alone("x-amp")
        with in_store(home):
            self.assertEqual(parts.main(["--fact-set", "x-amp", str(given), "--json"]), 0)
            text = sheet.sheet(project / "requirements.json")
        self.assertIn(self.VERIFIED, expected_before_power(text))
        self.assertNotIn("nobody has looked", text)

    def test_with_a_speaker_terminal_listed_the_sheet_has_no_line_about_a_socket(self):
        # a pin: the terminal receives both outputs, so the record's fact adds nothing for it
        project = a_copy("amplifier")
        with in_store(Path(tempfile.mkdtemp())):
            text = sheet.sheet(project / "requirements.json")
            data = sheet.wiring_data(project / "requirements.json")
        self.assertNotIn("own socket", text)
        self.assertEqual({item.kind for item in data.before_power.items}, {"unused-pin", "host-requirement"})


class NoBuildIsRefusedTest(unittest.TestCase):
    def test_a_project_with_no_build_is_refused_as_the_sheet_refuses_it(self):
        project = a_copy("motor")
        shutil.rmtree(project / "dist")
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(sheet.NotBuiltError) as said:
            sheet.wiring_data(project / "requirements.json")
        self.assertEqual(said.exception.code, "not_built")


if __name__ == "__main__":
    unittest.main()
