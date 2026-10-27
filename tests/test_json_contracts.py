"""
P41: what every machine-readable payload looks like, pinned.

Ten scripts declare `--json`. Before this file, exactly one test passed the flag and it asserted
only the exit code — so any key in any payload could have been renamed and the whole suite would
have stayed green. These are **characterisation** tests: they record the shape each script emits
today, so a refactor that moves code cannot change what a caller reads without saying so, and a
change that is deliberate shows up here as a failing assertion to update.

They assert key SETS and the status word, never values, so they survive a behaviour change and
fail on a shape change. They are also the only tests that enter five of these `main()`s at all.

The shapes disagree today — five different envelopes, and `check_spine` and `emit_footprint` call
their first key `check` where the others say `tool`. That disagreement is P43's to fix; this file
is what makes fixing it safe, and its expectations are what P43 will update.
"""

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
import check_all  # noqa: E402
import check_footprints  # noqa: E402
import check_physics  # noqa: E402
import check_spine  # noqa: E402
import board_codes  # noqa: E402
import board_grant  # noqa: E402
import board_look  # noqa: E402
import check_vendor_pins  # noqa: E402
import compare_design  # noqa: E402
import deploy_gate  # noqa: E402
import emit_footprint  # noqa: E402
import grant  # noqa: E402
import import_firmware  # noqa: E402
import outcomes  # noqa: E402
import parts  # noqa: E402
import test_deploy_gate  # noqa: E402
import tools  # noqa: E402
from suite_runs import slow  # noqa: E402

BOARD = "firebeetle2-esp32s3"

#: P95 (§6.4.1 of docs/2026-10-04-store-design.md): every parts.py --json answer is this one envelope.
#: parts.py's envelope. `notes` and `assumptions` joined in P124 (#58): what its text said and its JSON left out.
ENVELOPE = ["assumptions", "data", "envelope", "next", "notes", "op", "problems", "status", "tool", "truncated", "unchecked"]

#: A netlist small enough to read, real enough to walk: one component, grounded.
CIRCUIT = [
    {"type": "source_component", "source_component_id": "c1", "name": "U1", "ftype": "simple_chip"},
    {"type": "source_net", "source_net_id": "n1", "name": "GND"},
    {"type": "source_port", "source_port_id": "p1", "source_component_id": "c1", "name": "GND"},
    {"type": "source_trace", "source_trace_id": "t1",
     "connected_source_port_ids": ["p1"], "connected_source_net_ids": ["n1"]},
]


def a_project():
    """A project with a board chosen, a rules file, a circuit and the documented requirements."""
    root = Path(tempfile.mkdtemp())
    (root / ".spark").mkdir()
    (root / "boards").mkdir()
    (root / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": BOARD}))
    (root / ".spark" / "rules.json").write_text(json.dumps(
        {"i2c_buses": [], "must_not_float": [], "physics": {"rails": {}}}))
    (root / "circuit.json").write_text(json.dumps(CIRCUIT))
    example = re.search(r"```json\n(.*?)```", (ROOT / "commands" / "build.md").read_text(), re.S)
    (root / "requirements.json").write_text(example.group(1))
    return root


def payload_of(call):
    """Run a `main`, parse its stdout as JSON, and hand back (exit code, payload)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = call()
    return code, json.loads(out.getvalue())


class EveryJsonPayloadKeepsItsShapeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = a_project()
        cls.circuit = str(cls.project / "circuit.json")
        cls.rules = str(cls.project / ".spark" / "rules.json")
        cls.requirements = str(cls.project / "requirements.json")

    def _check(self, name, call, keys, status_expected=True):
        code, payload = payload_of(call)
        self.assertIsInstance(payload, dict, "%s emits a bare %s, which a caller cannot extend"
                              % (name, type(payload).__name__))
        self.assertEqual(sorted(payload), sorted(keys), "%s's top-level keys changed" % name)
        self.assertIn(code, (outcomes.EXIT_OK, outcomes.EXIT_PROBLEMS, outcomes.EXIT_COULD_NOT_RUN))
        if status_expected:
            self.assertIn(payload["status"], (outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN),
                          "%s's status is not one of the three words: %r" % (name, payload["status"]))
        return payload

    def test_assign_pins(self):
        # No `status` key at all, and `unverified` is 80% of the bytes — both P43's.
        self._check("assign_pins", lambda: assign_pins.main([self.requirements, "--json"]),
                    ["assignments", "board", "free", "tool", "unverified"], status_expected=False)

    def test_check_physics(self):
        self._check("check_physics", lambda: check_physics.main([self.circuit, "--rules", self.rules, "--json"]),
                    ["design", "findings", "status", "tool"])

    def test_check_footprints(self):
        self._check("check_footprints", lambda: check_footprints.main([self.circuit, "--json"]),
                    ["findings", "status", "tool"])

    def test_compare_design(self):
        # P34 changed this shape deliberately: a rules file naming no rule is now a refusal, which
        # carries `reason` and `fix` instead of `problems`. The old key set is in this file's
        # history, which is the point of characterising it.
        self._check("compare_design", lambda: compare_design.main([self.circuit, "--rules", self.rules, "--json"]),
                    ["checked", "design", "fix", "reason", "status", "tool"])

    def test_compare_design_with_rules_to_compare(self):
        rules = self.project / "real-rules.json"
        rules.write_text(json.dumps({"i2c_buses": [], "must_not_float": [["U1", "GND"]], "physics": {"rails": {}}}))
        self._check("compare_design", lambda: compare_design.main([self.circuit, "--rules", str(rules), "--json"]),
                    ["checked", "design", "problems", "status", "tool"])

    def test_check_all(self):
        self._check("check_all", lambda: check_all.main(
            ["--project", str(self.project), "--circuit", self.circuit, "--json"]),
            ["project", "resolved", "results", "status", "tool", "unmeasured"])

    def test_import_firmware(self):
        # P59: this project holds no firmware/ folder, so the shape is the could-not-run one, with its `modules` empty.
        self._check("import_firmware", lambda: import_firmware.main([str(self.project), "--json"]),
                    ["modules", "problems", "status", "tool", "unchecked"])

    def test_check_vendor_pins(self):
        # A BARE LIST, not an envelope: no tool, no overall status, and each entry's status word
        # may be `mismatch`, a fourth word outcomes.py does not know. Both are P43's.
        code, payload = payload_of(lambda: check_vendor_pins.main(
            ["--offline", "--json", str(ROOT / "boards" / (BOARD + ".json"))]))
        self.assertIsInstance(payload, list, "it emits a bare list today; if that changed, P43 did it")
        self.assertEqual(sorted(payload[0]), ["board", "compared", "not_recorded", "problems", "source", "status"])
        self.assertIn(payload[0]["status"], (outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN, "mismatch"))
        self.assertIn(code, (outcomes.EXIT_OK, outcomes.EXIT_PROBLEMS, outcomes.EXIT_COULD_NOT_RUN))

    def test_check_vendor_pins_live(self):
        # P179: a live run adds `wrote`, the file it kept the fetched header in. The board is a copy
        # in a project of this test's own and the fetch is patched, so nothing reaches the network
        # or spark's folder.
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / "boards").mkdir()
        shipped = ROOT / "boards" / (BOARD + ".json")
        board = project / "boards" / shipped.name
        board.write_text(shipped.read_text())
        variant = json.loads(shipped.read_text())["vendor"]["arduino_variant"]
        header = (ROOT / ".spark" / "cache" / ("%s.pins_arduino.h" % variant)).read_text()
        # spark's folder is a stand-in too: were the P179 bug back, the write would land there,
        # not in the real tracked header (the refuter showed this test rewrote it under that mutation).
        stand_in = Path(tempfile.mkdtemp())
        with mock.patch.object(check_vendor_pins, "fetch_variant_header", return_value=header), \
                mock.patch.object(check_vendor_pins, "PLUGIN_ROOT", stand_in):
            code, payload = payload_of(lambda: check_vendor_pins.main(["--json", str(board)]))
        self.assertEqual(sorted(payload[0]),
                         ["board", "compared", "not_recorded", "problems", "source", "status", "wrote"])
        self.assertTrue(payload[0]["source"].endswith("variants/%s/pins_arduino.h" % variant), payload[0]["source"])
        self.assertEqual(code, outcomes.EXIT_OK)

    def test_check_vendor_pins_could_not_run(self):
        # P181: the agent guide says a could-not-run entry carries only `board`, `status` and `reason`,
        # and that a live run refused before it kept a header has no `wrote`. Both refusals, pinned.
        loose = Path(tempfile.mkdtemp())
        board = loose / "loose.json"
        board.write_text(json.dumps({"pins": {"D3": 38}, "vendor": {"arduino_variant": "p181_unshipped"}}))
        stand_in = Path(tempfile.mkdtemp())
        for argv in (["--offline", "--json", str(board)], ["--json", str(board)]):
            with self.subTest(argv=argv), mock.patch.object(check_vendor_pins, "PLUGIN_ROOT", stand_in), \
                    mock.patch.object(check_vendor_pins, "fetch_variant_header", side_effect=AssertionError("fetched")):
                code, payload = payload_of(lambda: check_vendor_pins.main(argv))
            self.assertEqual(sorted(payload[0]), ["board", "reason", "status"])
            self.assertEqual(code, outcomes.EXIT_COULD_NOT_RUN)

    def test_emit_footprint(self):
        # Says `check`, not `tool`.
        self._check("emit_footprint", lambda: emit_footprint.main(
            ["--board", BOARD, "-o", str(self.project / "fp.tsx"), "--json"]),
            ["check", "message", "status"])

    def test_parts(self):
        payload = self._check("parts", lambda: parts.main(["--list", "--json"]), ENVELOPE)
        self.assertEqual(sorted(payload["data"]), ["parts"])

    def test_check_spine(self):
        # Says `check`, not `tool`. The toolchain is withheld so the chain stops at `build`
        # without needing tscircuit, which the suite must never depend on.
        with mock.patch.object(check_spine, "find_toolchain", return_value=None):
            self._check("check_spine", lambda: check_spine.main([self.requirements, "--json"]),
                        ["check", "stages", "status"])

    def test_grant_check(self):
        """P253: grant.py --check --json, here for a board with no grant. No status word: granted is the answer."""
        devs = "/dev/cu.usbmodem101 8c:bf:ea:xx:xx:xx 303a:1001 Espressif USB JTAG/serial debug unit\n"
        run = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, devs, "")  # noqa: E731
        with mock.patch.object(tools, "find"), mock.patch.dict("os.environ", {"SPARK_HOME": tempfile.mkdtemp()}):
            self._check("grant", lambda: grant.main(["--check", "--json"], run=run), ["granted", "grant", "why"],
                        status_expected=False)

    def test_the_flag_is_honoured_wherever_it_is_offered(self):
        """`parts.py --catalog --json` printed prose and ignored the flag (P43); since P95 it is the envelope."""
        _, payload = payload_of(lambda: parts.main(["--catalog", "--json"]))
        self.assertEqual(sorted(payload), ENVELOPE)


class TheBenchCodesTableTest(unittest.TestCase):
    """P433: every code that look.py and deploy.py write is in board_codes.CODES, which says it in one sentence."""

    def test_the_table_holds_each_constant_of_the_module_once_with_a_sentence(self):
        constants = {name: value for name, value in vars(board_codes).items() if name.isupper() and isinstance(value, str)}
        self.assertEqual(sorted(constants.values()), sorted(board_codes.CODES))
        sentences = list(board_codes.CODES.values())
        self.assertTrue(all(sentence.strip() for sentence in sentences))
        self.assertEqual(len(set(sentences)), len(sentences))

    @slow("runs the look, gate, grant and doctor test modules once more under a spy, 1 test, 6 s on 2026-10-27")
    def test_every_reason_raised_is_in_the_table(self):
        raised = set()

        def spying(original):
            def init(error, *args, **kwargs):
                original(error, *args, **kwargs)
                raised.add(error.reason)
            return init

        suite = unittest.TestSuite()
        for name in ("test_board_look", "test_board_doctor", "test_board_grant"):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName("TheGateTest", test_deploy_gate))
        with mock.patch.object(board_look.LookStop, "__init__", spying(board_look.LookStop.__init__)), \
                mock.patch.object(deploy_gate.GateClosedError, "__init__", spying(deploy_gate.GateClosedError.__init__)):
            result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)
        self.assertTrue(raised, "the spy saw no raise")
        self.assertEqual(sorted(raised - set(board_codes.CODES)), [])

    def test_agents_md_names_every_code(self):
        text = (ROOT / "docs" / "guide" / "agents.md").read_text()
        self.assertEqual([code for code in board_codes.CODES if "`%s`" % code not in text], [])

    def test_a_grant_refusal_has_the_reason_and_the_exit_code_of_its_why(self):
        for why, reason, code in (("not a grant", "not_a_grant", 1), ("answered no", "answered_no", 1), ("bad minutes", "bad_minutes", 2),
                                  ("bad scope", "bad_scope", 2), ("no mac", "no_mac", 2), ("serial not mac", "serial_not_mac", 1)):
            refusal = board_grant.GrantRefusedError(why)
            self.assertEqual((refusal.reason, refusal.code, reason in board_codes.CODES), (reason, code, True), why)


if __name__ == "__main__":
    unittest.main()
