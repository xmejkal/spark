"""
Proof that setting a project up guesses nothing.

`findings.py` told people to "Run `spark init`", and that command existed nowhere but inside the
error message. So the first thing a second project hit was a remedy that did not exist, and two
of the deterministic checks plus every reviewer depend on files nothing created.

What is tested here is mostly what it REFUSES to write. An init that inferred a rail's current
from a part name would poison the one check that does arithmetic, in a tool whose whole thesis is
that an unchecked thing must not look like a checked one. So every value is null, and the list of
nulls is the output rather than a shortfall.

    python3 -m unittest discover -s tests -t tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_physics  # noqa: E402
import init_project  # noqa: E402


def a_project(nets=("V33", "GND", "MOTOR6V", "SDA", "SCL")):
    root = Path(tempfile.mkdtemp())
    circuit = root / "dist" / "board" / "circuit.json"
    circuit.parent.mkdir(parents=True)
    circuit.write_text(json.dumps(
        [{"type": "source_net", "source_net_id": net, "name": net} for net in nets]))
    return root


class WhatItWritesTest(unittest.TestCase):
    def setUp(self):
        self.root = a_project()
        init_project.main(["--project", str(self.root)])
        self.rules = json.loads((self.root / ".spark" / "rules.json").read_text())

    def test_the_rails_are_named_from_the_design_that_exists(self):
        # Typing them again is a chance to get one wrong, and a rule keyed on a net name that is
        # not in the design never fires — which looks exactly like a rule that passes.
        self.assertEqual(set(self.rules["physics"]["rails"]), {"V33", "GND", "MOTOR6V"})

    def test_a_bus_is_not_also_listed_as_a_rail(self):
        self.assertEqual(set(self.rules["i2c_buses"]), {"SDA", "SCL"})
        self.assertNotIn("SDA", self.rules["physics"]["rails"])

    def test_the_brief_is_written_too(self):
        # No script reads it; every reviewer does, and it is what consequence is judged against.
        brief = json.loads((self.root / ".spark" / "project.json").read_text())
        self.assertIn("must", brief)

    def test_an_existing_file_is_not_overwritten(self):
        (self.root / ".spark" / "rules.json").write_text('{"mine": true}')
        init_project.main(["--project", str(self.root)])
        self.assertEqual(json.loads((self.root / ".spark" / "rules.json").read_text()),
                         {"mine": True})


class WhatItRefusesToGuessTest(unittest.TestCase):
    """The design. Everything here is about values NOT being invented."""

    def setUp(self):
        self.root = a_project()
        init_project.main(["--project", str(self.root)])
        self.rules = json.loads((self.root / ".spark" / "rules.json").read_text())

    def test_every_rail_current_is_null(self):
        for name, rail in self.rules["physics"]["rails"].items():
            with self.subTest(rail=name):
                self.assertIsNone(rail["max_current_a"])
                self.assertIsNone(rail["nominal_volts"])

    def test_a_null_rail_makes_physics_report_it_rather_than_pass_it(self):
        # The reason nulls are safe, asserted rather than assumed. If a null ever became a pass,
        # this whole design would be worse than writing a plausible number.
        circuit = json.loads((self.root / "dist" / "board" / "circuit.json").read_text())
        findings = check_physics.run(circuit, self.rules)
        self.assertTrue(findings, "a design with no stated currents was reported as fine")
        self.assertTrue(all(f.severity != "problem" for f in findings))

    def test_it_lists_every_field_nobody_answered(self):
        unanswered = init_project.nulls_in(self.rules)
        self.assertIn("physics.rails.V33.max_current_a", unanswered)
        self.assertIn("physics.i2c_hz", unanswered)

    def test_the_one_value_it_does_set_is_a_decision_not_a_measurement(self):
        # A temperature rise is a choice about how hot you will let a trace get. It is the only
        # number here that can be defaulted honestly, and the file says it is a decision.
        self.assertEqual(self.rules["physics"]["trace_temperature_rise_c"], 10)
        self.assertIn("DECISION", self.rules["physics"]["//trace_temperature_rise_c"])


class WithoutABuiltDesignTest(unittest.TestCase):
    def test_it_still_writes_the_files_and_says_the_rails_are_empty(self):
        root = Path(tempfile.mkdtemp())
        self.assertEqual(init_project.main(["--project", str(root)]), init_project.EXIT_OK)
        rules = json.loads((root / ".spark" / "rules.json").read_text())
        self.assertEqual(rules["physics"]["rails"], {})

    def test_a_directory_that_does_not_exist_is_refused(self):
        self.assertEqual(init_project.main(["--project", "/nonexistent/project"]),
                         init_project.EXIT_COULD_NOT_RUN)

    def test_a_board_that_does_not_exist_is_refused_rather_than_written(self):
        root = a_project()
        self.assertEqual(init_project.main(["--project", str(root), "--board", "no-such-board"]),
                         init_project.EXIT_COULD_NOT_RUN)
        self.assertFalse((root / "boards" / "active.json").exists())


class TheCommandThatNamesItExistsTest(unittest.TestCase):
    def test_the_error_message_names_something_real(self):
        """
        The original defect: `findings.py` told the user to run `spark init`, and that string
        appeared nowhere else in the repository. An instruction to run a command that does not
        exist is worse than no instruction, because it is followed.
        """
        import findings  # noqa: PLC0415 - imported here to keep this file standalone
        try:
            findings.project_root(Path(tempfile.mkdtemp()))
        except SystemExit as refusal:
            named = str(refusal)
        else:
            self.skipTest("a .spark directory was found above the temporary directory")

        self.assertIn("/spark:init", named)
        self.assertTrue((ROOT / "commands" / "init.md").is_file(),
                        "the error names /spark:init and no such command file exists")


if __name__ == "__main__":
    unittest.main()
