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
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
import check_all  # noqa: E402
import check_footprints  # noqa: E402
import check_physics  # noqa: E402
import check_spine  # noqa: E402
import check_vendor_pins  # noqa: E402
import compare_design  # noqa: E402
import emit_footprint  # noqa: E402
import outcomes  # noqa: E402
import parts  # noqa: E402

BOARD = "firebeetle2-esp32s3"

#: P95 (§6.4.1 of docs/2026-10-04-store-design.md): every parts.py --json answer is this one envelope.
ENVELOPE = ["data", "envelope", "next", "op", "problems", "status", "tool", "truncated", "unchecked"]

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
            ["resolved", "results", "status", "tool"])

    def test_check_vendor_pins(self):
        # A BARE LIST, not an envelope: no tool, no overall status, and each entry's status word
        # may be `mismatch`, a fourth word outcomes.py does not know. Both are P43's.
        code, payload = payload_of(lambda: check_vendor_pins.main(
            ["--offline", "--json", str(ROOT / "boards" / (BOARD + ".json"))]))
        self.assertIsInstance(payload, list, "it emits a bare list today; if that changed, P43 did it")
        self.assertEqual(sorted(payload[0]), ["board", "compared", "not_recorded", "problems", "source", "status"])
        self.assertIn(payload[0]["status"], (outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN, "mismatch"))
        self.assertIn(code, (outcomes.EXIT_OK, outcomes.EXIT_PROBLEMS, outcomes.EXIT_COULD_NOT_RUN))

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

    def test_the_flag_is_honoured_wherever_it_is_offered(self):
        """`parts.py --catalog --json` printed prose and ignored the flag (P43); since P95 it is the envelope."""
        _, payload = payload_of(lambda: parts.main(["--catalog", "--json"]))
        self.assertEqual(sorted(payload), ENVELOPE)


if __name__ == "__main__":
    unittest.main()
