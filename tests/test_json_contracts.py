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

import ast
import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import types
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
from spark.build import board_engine  # noqa: E402
from spark.bench import board_codes  # noqa: E402
from spark.records import records_codes  # noqa: E402
from spark.sourcing import sourcing_codes  # noqa: E402
from spark.build import build_codes  # noqa: E402
from spark.checks import check_codes  # noqa: E402
from spark.design import design_codes  # noqa: E402
from spark.breadboard import breadboard_codes  # noqa: E402
from spark.core import codes  # noqa: E402
from spark.core.codes import Code  # noqa: E402
from spark.idea import idea_codes  # noqa: E402
from spark.bench import board_grant  # noqa: E402
from spark.bench import board_look  # noqa: E402
import check_vendor_pins  # noqa: E402
from spark.checks import vendor_pins_check  # noqa: E402
import compare_design  # noqa: E402
from spark.bench import deploy_gate  # noqa: E402
import emit_footprint  # noqa: E402
from spark.firmware import firmware_codes  # noqa: E402
import grant  # noqa: E402
import import_firmware  # noqa: E402
from spark.core import outcomes  # noqa: E402
import parts  # noqa: E402
import test_deploy_gate  # noqa: E402
from suite_runs import slow  # noqa: E402
from fakes import FakeOutsideWorld  # noqa: E402
from test_deploy import found  # noqa: E402

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

    def test_import_firmware_a_module_not_imported(self):
        # P684 (W6-F2): such an entry gains `code`; an imported one keeps its three keys
        firmware = Path(tempfile.mkdtemp()) / "firmware"
        firmware.mkdir()
        (firmware / "broken.py").write_text("raise KeyError('k')\n")
        payload = self._check("import_firmware", lambda: import_firmware.main([str(firmware.parent), "--json"]),
                              ["modules", "problems", "status", "tool", "unchecked"])
        self.assertEqual(sorted(payload["modules"][0]), ["code", "detail", "module", "status"])
        self.assertEqual(payload["modules"][0]["code"], "import_failed")

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
        with mock.patch.object(vendor_pins_check, "fetch_variant_header", return_value=header), \
                mock.patch.object(vendor_pins_check, "PLUGIN_ROOT", stand_in):
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
            with self.subTest(argv=argv), mock.patch.object(vendor_pins_check, "PLUGIN_ROOT", stand_in), \
                    mock.patch.object(vendor_pins_check, "fetch_variant_header", side_effect=AssertionError("fetched")):
                code, payload = payload_of(lambda: check_vendor_pins.main(argv))
            self.assertEqual(sorted(payload[0]), ["board", "code", "reason", "status"])  # P688: the code beside the reason
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
        with mock.patch.object(board_engine, "find_toolchain", return_value=None):
            self._check("check_spine", lambda: check_spine.main([self.requirements, "--json"]),
                        ["check", "stages", "status"])

    def test_check_spine_adds_missing_facts_beside_status_only_when_the_record_lacks_a_level(self):
        # P464: the verdict stays ok, and the facts are a top-level key like `unserved`
        from test_missing_facts import levelless
        project = Path(tempfile.mkdtemp())
        (project / "boards").mkdir()
        (project / ".spark").mkdir()
        board = dict(levelless(), id="levelless-board")
        (project / "boards" / "levelless-board.json").write_text(json.dumps(board))
        requirements = project / "requirements.json"
        requirements.write_text(json.dumps({"board": "levelless-board", "parts": [], "board_only": True}))
        payload = self._check("check_spine", lambda: check_spine.main([str(requirements), "--keep", str(project / "kept"), "--json"]),
                              ["check", "kept", "missing_facts", "next", "stages", "status"])
        self.assertEqual([item["code"] for item in payload["missing_facts"]], ["missing_fact"] * 2)
        self.assertEqual(sorted(payload["missing_facts"][0]), ["code", "fix", "sentence", "subject"])

    def test_grant_check(self):
        """P253: grant.py --check --json, here for a board with no grant. No status word: granted is the answer."""
        devs = "/dev/cu.usbmodem101 8c:bf:ea:xx:xx:xx 303a:1001 Espressif USB JTAG/serial debug unit\n"
        outside = FakeOutsideWorld(run=lambda argv, **kw: subprocess.CompletedProcess(argv, 0, devs, ""), find_tool=found)
        with mock.patch.dict("os.environ", {"SPARK_HOME": tempfile.mkdtemp()}):
            self._check("grant", lambda: grant.main(["--check", "--json"], outside=outside), ["granted", "grant", "why"],
                        status_expected=False)

    def test_the_flag_is_honoured_wherever_it_is_offered(self):
        """`parts.py --catalog --json` printed prose and ignored the flag (P43); since P95 it is the envelope."""
        _, payload = payload_of(lambda: parts.main(["--catalog", "--json"]))
        self.assertEqual(sorted(payload), ENVELOPE)


#: P684: the codes board_codes and firmware_codes both hold, as equal literals in two leaves. project_image raises the
#: first four from firmware_codes, deploy reports them, and the bench raises TOOL_MISSING itself (P685).
SHARED_CODES = ("NO_SIM_TOML", "FIRMWARE_LINE_BAD", "NO_IMAGE", "LOG_UNREADABLE", "TOOL_MISSING")


class TheBenchCodesTableTest(unittest.TestCase):
    """P433: every code that look.py and deploy.py write is in board_codes.CODES or the core's codes.CODES (P442), which say
    it in one sentence. P684: the firmware's are in firmware_codes.CODES. P692: the breadboard sheet's in
    breadboard_codes.CODES. P693: the checks' in check_codes.CODES. P700: the design's in design_codes.CODES. P701: the
    build's in build_codes.CODES. P716: the records' in records_codes.CODES. P717: sourcing's in
    sourcing_codes.CODES."""

    def test_the_tables_hold_each_constant_of_their_module_once_with_a_sentence_and_share_no_code(self):
        for module in (board_codes, codes, firmware_codes, breadboard_codes, check_codes, design_codes, build_codes,
                       records_codes, sourcing_codes, idea_codes):
            # P935: a variant, a Code named after its parent (BAD_ARGUMENT_REPLIES_UNREADABLE), is the second constant
            # of its word; EveryCodeHoldsItsFixTest holds it to its word's meaning and to a fix of its own
            constants = {name: value for name, value in vars(module).items() if name.isupper() and isinstance(value, str)
                         and not (isinstance(value, Code) and name.startswith(value.upper() + "_"))}
            self.assertEqual(sorted(constants.values()), sorted(module.CODES))
            sentences = list(module.CODES.values())
            self.assertTrue(all(sentence.strip() for sentence in sentences))
            self.assertEqual(len(set(sentences)), len(sentences))
        self.assertEqual(set(board_codes.CODES) & set(codes.CODES), set())
        self.assertEqual(set(firmware_codes.CODES) & set(codes.CODES), set())
        self.assertEqual(set(breadboard_codes.CODES) & (set(codes.CODES) | set(firmware_codes.CODES)), set())
        self.assertEqual(set(check_codes.CODES) & (set(board_codes.CODES) | set(codes.CODES) | set(firmware_codes.CODES)
                                                   | set(breadboard_codes.CODES)), set())
        self.assertEqual(set(design_codes.CODES) & (set(board_codes.CODES) | set(codes.CODES) | set(firmware_codes.CODES)
                                                    | set(breadboard_codes.CODES)), set())
        # P700: a refused rules file is one code in design_codes and check_codes, an equal literal with the same meaning
        self.assertEqual(sorted(set(design_codes.CODES) & set(check_codes.CODES)), ["rules_refused"])
        self.assertEqual(design_codes.CODES["rules_refused"], check_codes.CODES["rules_refused"])
        self.assertEqual(design_codes.RULES_REFUSED.fix, check_codes.RULES_REFUSED.fix)  # P935 PR 4: the pair holds one fix
        # P701: four build codes are equal literals of another leaf, with the same sentence; no other code is shared
        shared = {"board_unusable": design_codes, "no_project_folder": design_codes, "tool_missing": board_codes,
                  "input_ambiguous": check_codes}
        others = (board_codes, codes, firmware_codes, breadboard_codes, check_codes, design_codes)
        self.assertEqual(sorted(code for code in build_codes.CODES if any(code in other.CODES for other in others)),
                         sorted(shared))
        self.assertEqual([build_codes.CODES[code] for code in shared], [table.CODES[code] for code, table in shared.items()])
        self.assertEqual(build_codes.CODES["tool_missing"], firmware_codes.CODES["tool_missing"])
        # P716: two records codes are equal literals of another leaf, with the same sentence; no other code is shared
        others += (build_codes,)
        self.assertEqual(sorted(code for code in records_codes.CODES if any(code in other.CODES for other in others)),
                         ["missing_fact", "tool_missing"])
        self.assertEqual([records_codes.CODES[code] for code in ("missing_fact", "tool_missing")],
                         [board_codes.CODES["missing_fact"], board_codes.CODES["tool_missing"]])
        # P717: no sourcing code is an equal literal of another leaf
        tables = others + (records_codes,)
        self.assertEqual(set(sourcing_codes.CODES) & set().union(*(other.CODES for other in tables)), set())
        # P853: no idea code is an equal literal of another leaf
        self.assertEqual(set(idea_codes.CODES) & set().union(*(other.CODES for other in tables + (sourcing_codes,))), set())
        # P692: a store problem is one code in both leaves, an equal literal with the same meaning
        self.assertEqual(sorted(set(breadboard_codes.CODES) & set(board_codes.CODES)), ["store_problem"])
        self.assertEqual(breadboard_codes.CODES["store_problem"], board_codes.CODES["store_problem"])
        self.assertEqual(sorted(set(firmware_codes.CODES) & set(board_codes.CODES)),
                         sorted(getattr(firmware_codes, name) for name in SHARED_CODES))

    def test_the_shared_codes_are_equal_in_both_leaves(self):
        self.assertEqual([getattr(board_codes, name) for name in SHARED_CODES],
                         ["no_sim_toml", "firmware_line_bad", "no_image", "log_unreadable", "tool_missing"])
        self.assertEqual([getattr(firmware_codes, name) for name in SHARED_CODES],
                         [getattr(board_codes, name) for name in SHARED_CODES])

    @slow("runs the look, gate, grant and doctor test modules once more under a spy, 1 test, 15.7 s on 2026-10-27")
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
        with mock.patch.object(board_look.LookStopError, "__init__", spying(board_look.LookStopError.__init__)), \
                mock.patch.object(deploy_gate.GateClosedError, "__init__", spying(deploy_gate.GateClosedError.__init__)):
            result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)
        self.assertTrue(raised, "the spy saw no raise")
        self.assertEqual(sorted(raised - set(board_codes.CODES)), [])

    def test_agents_md_names_every_code(self):
        guide = ROOT / "docs" / "guide"
        text = "".join(page.read_text() for page in [guide / "agents.md"] + sorted((guide / "agents").glob("*.md")))
        named = list(board_codes.CODES) + list(codes.CODES) + list(firmware_codes.CODES)
        self.assertEqual([code for code in named if "`%s`" % code not in text], [])

    def test_every_why_a_site_raises_a_grant_refusal_with_has_a_code(self):
        tree = ast.parse(Path(board_grant.__file__).read_text())
        raised = {node.args[0].id for node in ast.walk(tree) if isinstance(node, ast.Call) and node.args
                  and getattr(node.func, "id", "") == "GrantRefusedError" and isinstance(node.args[0], ast.Name)}
        self.assertTrue(raised, "the scan found no raise site")
        self.assertEqual(sorted(name for name in raised if getattr(board_grant, name) not in board_grant.CODE_FOR_WHY), [])

    def test_a_grant_refusal_has_the_reason_and_the_exit_code_of_its_why(self):
        for why, reason, code in (("not a grant", "not_a_grant", 1), ("answered no", "answered_no", 1), ("bad minutes", "bad_minutes", 2),
                                  ("bad scope", "bad_scope", 2), ("no mac", "no_mac", 2), ("serial not mac", "serial_not_mac", 1),
                                  ("relayed yes", "relayed_yes_refused", 1)):
            refusal = board_grant.GrantRefusedError(why)
            self.assertEqual((refusal.reason, refusal.code, reason in board_codes.CODES), (reason, code, True), why)


#: P853: each area whose codes are Codes, with its table. An area joins when its codes take their fix (P935).
AREAS_WITH_FIXES = {"idea": idea_codes, "core": codes, "records": records_codes, "sourcing": sourcing_codes, "design": design_codes,
                   "checks": check_codes}
#: P935: the tables whose Codes an area names besides its own: the core's, which every Operation writes, and the records'.
NAMED_TOO = {"records": (codes,), "sourcing": (records_codes, codes), "design": (records_codes, codes),
            "checks": (codes,)}
#: P935: the one given fix that is no Code's: the override a CLI injects through `HelpText` (parts.py's describe route).
INJECTED_FIXES = {"text.bad_argument_fix"}
#: P935: each fix given with the code of a refusal its site caught, by the site (the file in its area and the function)
#: and the fix: the code is the refusal's, so no variant can hold the fix (research's sources, after the store's refusal).
CAUGHT_FIXES = {("research/research_source.py", "_problem", "cls.RETRY_FIX")}
#: P853: the errors that take a code, by class name; a subclass the area defines, at any depth, takes one too.
CODED_ERRORS = {"SparkError", "CodedMessageError", "StoreError"}


def dotted(node):
    """`a.b.c` of a Name or an Attribute chain, else ''."""
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return base and base + "." + node.attr
    return node.id if isinstance(node, ast.Name) else ""


def resolver(tree):
    """The dotted name of a node, its first name resolved through the module's imports."""
    imported = {alias.asname or alias.name: ("%s.%s" % (node.module, alias.name) if isinstance(node, ast.ImportFrom) else alias.name)
                for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}

    def resolved(node):
        first, dot, rest = dotted(node).partition(".")
        return imported.get(first, first) + dot + rest
    return resolved


def coded_errors(trees, roots=CODED_ERRORS):
    """P853: the `roots` and every class the trees define on one of them, a subclass of a subclass too, until none is added."""
    classes = [(cls.name, {resolver(tree)(base).rpartition(".")[2] for base in cls.bases})
               for tree in trees for cls in ast.walk(tree) if isinstance(cls, ast.ClassDef)]
    errors = set(roots)
    while True:
        more = {name for name, bases in classes if bases & errors} - errors
        if not more:
            return errors
        errors |= more


def fix_parts(node, filled=False):
    """P935: the parts of a given fix that must each be a Code's fix, each with whether a % fills it: the fix itself, the
    left of a % (its values may be anything) and each side of an `or`."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return fix_parts(node.left, True)
    if isinstance(node, ast.BoolOp):
        return [part for value in node.values for part in fix_parts(value)]
    return [(node, filled)]


def foreign_fix(fix, word, table, resolved):
    """P935: the parts of a given `fix` that are neither the `.fix` of a Code of `table` with the call's `word` (a
    variant's too), filled with % when it is a template, nor an injected fix."""
    def codes_own(part, filled):
        if not (isinstance(part, ast.Attribute) and part.attr == "fix"):
            return False
        module, _, name = resolved(part.value).rpartition(".")
        code = getattr(table, name, None) if module == table.__name__ else None
        if not isinstance(code, Code) or code != word:
            return False
        return filled or "%" not in code.fix
    return [part for part, filled in fix_parts(fix) if not codes_own(part, filled) and ast.unparse(part) not in INJECTED_FIXES]


def made_from_its_own_fix(call, fix):
    """P935: a `_replace` whose `fix` holds its receiver's own `.fix`, as the Privacy mask's does."""
    receiver = ast.unparse(call.func.value) if isinstance(call.func, ast.Attribute) else None
    return any(isinstance(node, ast.Attribute) and node.attr == "fix" and ast.unparse(node.value) == receiver for node in ast.walk(fix))


def meanings_off_their_word(table, also=()):
    """P935: the Code constants of `table` whose meaning is not their word's in `table.CODES`; a variant, named past its
    word, may take the meaning of the word in the core's table or in a table `also` holds (design's audit variant of a
    records word)."""
    def word_s_meaning(name, code):
        found = [one.CODES[code] for one in (table,) + (tuple(also) + (codes,) if name != code.upper() else ()) if code in one.CODES]
        return found[0] if found else None
    return [name for name, code in vars(table).items() if isinstance(code, Code) and word_s_meaning(name, code) != code.meaning]


def variants_off_their_parent(table, also=()):
    """P935: the Code constants of `table` named past their word that are no variant. A variant is named after its parent,
    the constant named by its word (`<PARENT>_...`) in `table`, the core's or a table `also` holds, and holds a fix of its
    own, so an alias of a code is none."""
    broken = []
    for name, code in vars(table).items():
        if not isinstance(code, Code) or name == code.upper():
            continue
        parent = next((found for one in (table, codes) + tuple(also) if (found := getattr(one, code.upper(), None))), None)
        if not name.startswith(code.upper() + "_") or parent is None:
            broken.append("%s is not named after its parent %s" % (name, code.upper()))
        elif code.fix == parent.fix:
            broken.append("%s holds its parent's fix" % name)
    return broken


def forwards(code, fix):
    """P935: a forward passes on the code and the fix of one thing it did not make (`x.code` with `x.fix`): a SparkError's."""
    return (isinstance(code, ast.Attribute) and code.attr == "code" and isinstance(fix, ast.Attribute) and fix.attr == "fix"
            and ast.unparse(code.value) == ast.unparse(fix.value))


def caught_names(tree, resolved, fixless):
    """P935: the names an `except E as x` of the tree binds where every E is one of `fixless`, a coded error the area
    raises that holds no fix (never Exception, never a SparkError)."""
    types = {}
    for handler in (node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler) and node.name):
        caught = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
        types.setdefault(handler.name, set()).update(resolved(one).rpartition(".")[2] for one in caught)
    return {name for name, classes in types.items() if classes <= fixless}


def functions_of(tree):
    """P935: the innermost function of each node of the tree, by the node's id: the site a CAUGHT_FIXES entry names."""
    owner = {}
    for function in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
        owner.update((id(node), function.name) for node in ast.walk(function))  # ast.walk meets an inner one later
    return owner


def passes_on_a_refusal(site, code, fix, caught):
    """P935: a call that passes on the code of a refusal its site caught (`x.code`): with no fix when `x` is one of
    `caught`, or with the fix CAUGHT_FIXES names for the site, (the file in its area, the function)."""
    if not (isinstance(code, ast.Attribute) and code.attr == "code" and isinstance(code.value, ast.Name)):
        return False
    return code.value.id in caught if fix is None else site + (ast.unparse(fix),) in CAUGHT_FIXES


def passes_on_an_item(call):
    """P935: a plain Finding whose code and fix are one item's own, `x.get("code")` and `x.get("fix")`: a forward of a
    dict made elsewhere (`Answer.to_result`, whose items carry no Code's fix until P941, #1343)."""
    got = [arg for arg in call.args[2:5:2] if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "get"]
    return (len(got) == 2 and [ast.unparse(one.args[0]) for one in got] == ["'code'", "'fix'"]
            and ast.unparse(got[0].func.value) == ast.unparse(got[1].func.value))


def own_classes(tree):
    """P935 PR 4: the names of the classes a file defines at its top level with no bases, and that nothing else in the file binds
    (an assignment, a walrus or loop target, a parameter, an import, a nested class or one with a base): a call of one makes no
    core Finding. Any `import *` may bind any name, so then there are none."""
    top = [node for node in tree.body if isinstance(node, ast.ClassDef) and not node.bases]
    bound = [alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) for alias in node.names]
    if "*" in bound:
        return set()
    bound += [(alias.asname or alias.name).partition(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    bound += [node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)]
    bound += [node.arg for node in ast.walk(tree) if isinstance(node, ast.arg)]
    bound += [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and not any(node is one for one in top)]
    return {node.name for node in top} - set(bound)


def calls_off_the_table(sources, table, also=()):
    """
    P853: (the calls that take a code, each rule a call breaks as 'file:line N: the rule'), over the area's `sources`
    ({file name: text}). A Finding is made by `Finding.of` alone, and no name aliases Finding; an error of `coded_errors`
    and `Finding.of` name a Code of `table` (aliases resolved through the module's imports) and pass no keywords by **.
    P935: a given fix is the `.fix` of a Code of the call's word, filled with % or after an injected fix's `or`
    (`fix_parts`); a forward passes `x.code` with `x.fix`; a `_replace` gives no code, and a fix only made from the
    receiver's own (the Privacy mask). A Code of a table `also` holds counts as `table`'s; a caught refusal's code is
    passed on as `passes_on_a_refusal` says, and an item's as `passes_on_an_item` says.
    P935 PR 4: a call of a class the file defines with no bases and does not import (build_check's own `class Finding`) makes
    no core Finding; `own_classes` says which names that holds for.
    """
    trees = {name: ast.parse(text) for name, text in sources.items()}
    errors, calls, broken = coded_errors(trees.values()), 0, []
    fixless = errors - coded_errors(trees.values(), {"SparkError"})
    for file, tree in trees.items():
        resolved, owner = resolver(tree), functions_of(tree)
        caught = caught_names(tree, resolved, fixless)
        own = own_classes(tree)
        for alias in (node for node in ast.walk(tree) if isinstance(node, ast.Assign) and resolved(node.value).endswith("Finding")):
            broken.append("%s:line %d: %s aliases Finding: Finding.of takes the fix from its Code" % (file, alias.lineno, ast.unparse(alias.targets[0])))
        for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
            name, keywords = resolved(call.func), {keyword.arg: keyword.value for keyword in call.keywords}
            said = "%s:line %d: %s" % (file, call.lineno, name.rpartition(".")[2] if name.rpartition(".")[2] in errors else name)
            of, replaces = name.endswith("Finding.of"), name.endswith("_replace")
            made_by = name.rpartition(".")[0].rpartition(".")[2] if name.endswith((".of_error", ".of_lines")) else name.rpartition(".")[2]
            coded = of or made_by in errors  # P935 PR 3: `E.of_error(...)` and `E.of_lines(...)` take their keywords like `E(...)`
            if None in keywords and (coded or replaces):
                broken.append(said + " passes keywords by **")
            if (name.endswith(("Finding", "Finding._make", "Finding.__new__")) and name.partition(".")[0] not in own
                    and not passes_on_an_item(call)):
                broken.append(said + " makes a Finding: Finding.of takes the fix from its Code")
            elif replaces:
                if "code" in keywords:
                    broken.append(said + " gives a code")
                if "fix" in keywords and not made_from_its_own_fix(call, keywords["fix"]):
                    broken.append(said + " gives a fix")
            elif coded:
                calls += 1
                code = keywords.get("code", call.args[2] if of and len(call.args) > 2 else None)
                fix = keywords.get("fix", call.args[4] if of and len(call.args) > 4 else None)
                if forwards(code, fix) or passes_on_a_refusal((file, owner.get(id(call))), code, fix, caught):
                    continue
                module, _, word = resolved(code).rpartition(".")
                named = next((one for one in (table,) + tuple(also) if one.__name__ == module), None)
                if not isinstance(getattr(named, word, None), Code):
                    broken.append(said + " names its code as %r, not a Code of %s" % (ast.unparse(code) if code else None, table.__name__))
                elif fix is not None and foreign_fix(fix, getattr(named, word), named, resolved):
                    broken.append(said + " gives a fix")
    return calls, broken


class EveryCodeHoldsItsFixTest(unittest.TestCase):
    """P853: in an area whose codes are Codes, each holds its meaning and its fix, and every Finding and error the area
    makes names one of them and gives no fix of its own, so none goes out without the code's fix."""

    def test_each_code_of_the_table_holds_its_meaning_and_a_fix(self):
        for table in AREAS_WITH_FIXES.values():
            for code, meaning in table.CODES.items():
                self.assertEqual((type(code), code.meaning), (Code, meaning))
                self.assertTrue(code.fix.strip(), code)

    #: P935 PR 4: the fix of each of the checks' 19 codes, as the PO read it (the plan check changed seven)
    CHECK_FIXES = {
        "no_circuit":
            "give the path of the built circuit, usually dist/board/circuit.json, or build the board first with /spark:build",
        "no_rules_file":
            "give --rules the path of a rules file, or write .spark/rules.json with /spark:init",
        "rules_refused":
            "fix the value the sentence names in the rules file, then run again",
        "input_ambiguous":
            "pick one of the files the sentence lists and give it with the flag the sentence names, then run again",
        "check_crashed":
            "if the sentence names your input file, fix that file and run again, or else report it at https://github.com/xmejkal/spark/issues with the sentence and the command you ran",
        "project_unusable":
            "give --project a folder that exists, or leave out --project and give each input with its own flag",
        "check_found_problems":
            "fix each problem the check lists, then run check_all.py again",
        "check_could_not_look":
            "fix what the sentence names for this check, then run check_all.py again",
        "nothing_asked":
            "run again with --project and your project folder, or give the inputs with --circuit, --rules, --package or --boards",
        "circuit_not_json":
            "build the board again with /spark:build, or give the path of the circuit.json that a build wrote",
        "no_rule_stated":
            "ask the person which I2C lines and which pins must not float, name them in i2c_buses and must_not_float in the rules file, then run again",
        "no_vendor_variant":
            "ask the person for the board's folder under variants/ in the Arduino core and add it to the board file as vendor.arduino_variant, or say in the board file why it has no vendor header, then run again",
        "no_cached_header":
            "run check_vendor_pins.py once without --offline on a board file that a project owns, so that it fetches and keeps the header",
        "header_has_no_pins":
            "make sure vendor.arduino_variant names this board's variant, or compare the pins with the header by hand",
        "board_has_no_project":
            "put the board file in the boards/ folder of a project that /spark:init set up, then run again",
        "header_not_fetched":
            "fix what gh says in the sentence (`gh auth status` shows your sign-in), then run again",
        "header_not_kept":
            "make the folder that holds the file the sentence names writable, then run again",
        "no_package":
            "in the project folder, give the path of the fab package, or export one with `npx --no tsci export board.tsx -f gerbers -o board-gerbers.zip`",
        "no_bom_in_package":
            "in the project folder, export the package again with `npx --no tsci export board.tsx -f gerbers -o board-gerbers.zip`, which writes bom.csv",
    }

    def test_the_checks_codes_hold_the_fix_the_po_read(self):
        self.assertEqual({str(code): code.fix for code in check_codes.CODES}, self.CHECK_FIXES)
        self.assertEqual(len(check_codes.CODES), 19)

    def test_each_code_constant_of_the_table_is_a_word_of_codes_with_that_word_s_meaning(self):
        # P935: a variant (BAD_ARGUMENT_REPLIES_UNREADABLE) is another Code of its parent's word and meaning, never a new word;
        # an area's variant of the core's word (BAD_ARGUMENT_IN_LIBRARY) has the core's meaning
        for table in AREAS_WITH_FIXES.values():
            also = NAMED_TOO.get(next(area for area, held in AREAS_WITH_FIXES.items() if held is table), ())
            self.assertEqual(meanings_off_their_word(table, also), [], table.__name__)
            self.assertEqual(variants_off_their_parent(table, also), [], table.__name__)

    def test_a_code_of_the_core_s_word_named_by_its_word_in_an_area_s_table_is_named(self):
        # P935 PR 2's review: only a variant, named past its word, takes the core's meaning; a second BAD_ARGUMENT does not
        planted = types.ModuleType("planted")
        planted.BAD_ARGUMENT = Code("bad_argument", "an argument that the script cannot run with", "a second fix")
        planted.BAD_ARGUMENT_HERE = Code("bad_argument", "an argument that the script cannot run with", "look here")
        planted.CODES = {}
        self.assertEqual(meanings_off_their_word(planted), ["BAD_ARGUMENT"])

    def test_a_variant_named_off_its_parent_or_holding_its_parent_s_fix_is_named(self):
        # P935: the review's `CRASH_TOO = CRASH`, an alias that passed as a variant
        planted, gone = types.ModuleType("planted"), Code("x_gone", "m", "f")
        planted.X_GONE, planted.X_GONE_TOO, planted.X_GONE_SEEN = gone, gone, Code(gone, "m", "look")
        planted.OTHER, planted.LOST_X = Code(gone, "m", "look"), Code("lost", "m", "f")
        self.assertEqual(variants_off_their_parent(planted), ["X_GONE_TOO holds its parent's fix", "OTHER is not named after its parent X_GONE",
                                                              "LOST_X is not named after its parent LOST"])

    def test_an_area_s_variant_of_the_core_s_word_has_the_core_s_code_as_its_parent(self):
        # P935 PR 2: sourcing's BAD_ARGUMENT_IN_LIBRARY
        planted = types.ModuleType("planted")
        planted.BAD_ARGUMENT_HERE = Code("bad_argument", "m", "look here")
        planted.BAD_ARGUMENT_SAME = Code("bad_argument", "m", "%s --help lists the arguments")
        planted.HERE_CRASH = Code("crash", "m", "look")
        self.assertEqual(variants_off_their_parent(planted), ["BAD_ARGUMENT_SAME holds its parent's fix",
                                                              "HERE_CRASH is not named after its parent CRASH"])

    def test_an_area_s_variant_of_another_area_s_word_takes_that_word_s_meaning_and_parent(self):
        # P935 PR 3: design's RECORD_FILE_BROKEN_AUDIT, a variant of a records word, read through NAMED_TOO
        other, planted = types.ModuleType("other"), types.ModuleType("planted")
        other.RECORD_GONE = Code("record_gone", "a record is gone", "look")
        other.CODES = {"record_gone": "a record is gone"}
        planted.RECORD_GONE_HERE = Code("record_gone", "a record is gone", "look here")
        planted.RECORD_GONE_SAME = Code("record_gone", "a record is gone", "look")
        planted.RECORD_GONE_WORDS = Code("record_gone", "another meaning", "look there")
        planted.CODES = {}
        self.assertEqual(meanings_off_their_word(planted, (other,)), ["RECORD_GONE_WORDS"])
        self.assertEqual(meanings_off_their_word(planted), ["RECORD_GONE_HERE", "RECORD_GONE_SAME", "RECORD_GONE_WORDS"])
        self.assertEqual(variants_off_their_parent(planted, (other,)), ["RECORD_GONE_SAME holds its parent's fix"])

    def test_every_finding_and_error_of_the_area_names_a_code_of_the_table_and_gives_no_fix(self):
        scanned = set()
        for area, table in AREAS_WITH_FIXES.items():
            root = ROOT / "scripts" / "spark" / area  # P935: its subfolders too, each file by its path in the area
            sources = {str(path.relative_to(root)): path.read_text() for path in sorted(root.rglob("*.py"))}
            calls, broken = calls_off_the_table(sources, table, NAMED_TOO.get(area, ()))
            self.assertTrue(calls, "the scan found no call in %s" % area)
            self.assertEqual(broken, [])
            scanned |= set(sources)
        # P935 PR 2's review: each site CAUGHT_FIXES names is a file the scan read, so a stale entry or a narrower read fails
        self.assertEqual([site for site in CAUGHT_FIXES if site[0] not in scanned], [])

    def test_the_scan_names_each_rule_a_call_breaks(self):
        drop = ("from spark.core.result import Finding as F\nfrom spark.core.errors import SparkError\nfrom spark.records import store\n"
                "from spark.idea import idea_codes as ic\n\n\nclass DropError(SparkError):\n    pass\n\n\n"
                "F.of(1, 2, ic.NEED_UNKNOWN, 's')\nF(1, 2, ic.NEED_UNKNOWN, 's', 'f')\nF._make([])\n"
                "F.of(1, 2, ic.NEED_UNKNOWN, 's', 'f')\nF.of(1, 2, 'need_unknown', 's')\nSparkError('x', code=ic.CODES)\n"
                "store.StoreError('x', code=ic.DROP_UNWRITTEN, fix='f')\nDropError('x', code=reason)\nfound._replace(fix='f')\n"
                "from spark.idea.errors import LostError\nLostError('x', code=reason)\n")
        # a subclass of a subclass, defined in another file of the area
        errors = ("from spark.idea.drop import DropError\n\n\nclass GoneError(DropError):\n    pass\n\n\n"
                  "class LostError(GoneError):\n    pass\n")
        self.assertEqual(calls_off_the_table({"drop.py": drop, "errors.py": errors}, idea_codes), (7, [
            "drop.py:line 12: spark.core.result.Finding makes a Finding: Finding.of takes the fix from its Code",
            "drop.py:line 13: spark.core.result.Finding._make makes a Finding: Finding.of takes the fix from its Code",
            "drop.py:line 14: spark.core.result.Finding.of gives a fix",
            "drop.py:line 15: spark.core.result.Finding.of names its code as \"'need_unknown'\", not a Code of spark.idea.idea_codes",
            "drop.py:line 16: SparkError names its code as 'ic.CODES', not a Code of spark.idea.idea_codes",
            "drop.py:line 17: StoreError gives a fix",
            "drop.py:line 18: DropError names its code as 'reason', not a Code of spark.idea.idea_codes",
            "drop.py:line 19: found._replace gives a fix",
            "drop.py:line 21: LostError names its code as 'reason', not a Code of spark.idea.idea_codes"]))

    def test_the_scan_takes_a_filled_or_injected_fix_of_the_call_s_code_and_a_forward_and_names_the_rest(self):
        # P935: the core's forms, and the gaps P853's review raised (rows 8 and 9)
        cli = ("from spark.core import codes\nfrom spark.core.result import Finding\nfrom spark.core.errors import SparkError\n\n"
               "Finding.of(1, None, codes.BAD_ARGUMENT, 's', text.bad_argument_fix or codes.BAD_ARGUMENT.fix % text.prog)\n"
               "Finding.of(1, None, codes.UNKNOWN_REPLY_NEAR, 's', codes.UNKNOWN_REPLY_NEAR.fix % near)\n"
               "SparkError('x', code=codes.BAD_ARGUMENT_REPLIES_UNREADABLE)\n"
               "Finding.of(refused.status, None, refused.code, str(refused), refused.fix)\n"
               "found._replace(fix=mask(found.fix))\n"
               "Finding.of(1, None, codes.BAD_ARGUMENT, 's', codes.CRASH.fix)\n"
               "Finding.of(1, None, codes.BAD_ARGUMENT, 's', other or codes.BAD_ARGUMENT.fix % prog)\n"
               "Finding.of(1, None, codes.BAD_ARGUMENT, 's', 'see ' + codes.BAD_ARGUMENT.fix)\n"
               "Finding.of(1, None, refused.code, 's', other.fix)\n"
               "SparkError('x', **{'code': codes.CRASH, 'fix': 'f'})\n"
               "Finding.__new__(Finding, 1, None, codes.CRASH, 's', 'f')\n"
               "make = Finding\n"
               "found._replace(code='crash')\n"
               "found._replace(fix=other.fix)\n"
               "Finding.of(1, None, codes.BAD_ARGUMENT, 's', codes.BAD_ARGUMENT.fix)\n")
        self.assertEqual(calls_off_the_table({"cli.py": cli}, codes), (10, [
            "cli.py:line 16: make aliases Finding: Finding.of takes the fix from its Code",
            "cli.py:line 10: spark.core.result.Finding.of gives a fix",
            "cli.py:line 11: spark.core.result.Finding.of gives a fix",
            "cli.py:line 12: spark.core.result.Finding.of gives a fix",
            "cli.py:line 13: spark.core.result.Finding.of names its code as 'refused.code', not a Code of spark.core.codes",
            "cli.py:line 14: SparkError passes keywords by **",
            "cli.py:line 14: SparkError names its code as None, not a Code of spark.core.codes",
            "cli.py:line 15: spark.core.result.Finding.__new__ makes a Finding: Finding.of takes the fix from its Code",
            "cli.py:line 17: found._replace gives a code",
            "cli.py:line 18: found._replace gives a fix",
            "cli.py:line 19: spark.core.result.Finding.of gives a fix"]))

    def test_the_scan_takes_the_tables_an_area_reads_a_caught_refusal_s_code_and_an_item_s_and_names_the_rest(self):
        # P935 PR 2: the sourcing and records forms; the plan check's and the review's limits (a SparkError's or an
        # Exception's code with no fix, a caught fix off its site)
        head = ("from spark.core import codes\nfrom spark.core.errors import SparkError\nfrom spark.core.result import Finding\n"
                "from spark.records import records_codes\nfrom spark.records.store import StoreError\nfrom spark.sourcing import sourcing_codes\n\n")
        caught = ("try:\n    pass\nexcept StoreError as refused:\n    SparkError('x', code=refused.code)\n"
                  "except (ValueError, SparkError) as said:\n    SparkError('x', code=said.code)\n"
                  "except Exception as broad:\n    SparkError('x', code=broad.code)\n"
                  "SparkError('x', code=error.code)\nSparkError('x', code=error.code, fix=cls.RETRY_FIX)\n"
                  "StoreError('x', code=records_codes.URL_UNREACHABLE)\nSparkError('x', code=sourcing_codes.BAD_ARGUMENT_IN_LIBRARY)\n"
                  "SparkError('x', code=codes.CRASH)\nSparkError('x', code=records_codes.CODES)\n\n\n"
                  "class Source:\n    def _problem(cls, error):\n        return SparkError('x', code=error.code, fix=cls.RETRY_FIX)\n\n"
                  "    def _other(cls, error):\n        return SparkError('x', code=error.code, fix=cls.RETRY_FIX)\n")
        item = ("Finding(1, None, item.get('code'), 's', item.get('fix'))\nFinding(1, None, item.get('code'), 's', other.get('fix'))\n"
                "Finding(1, None, item.get('word'), 's', item.get('help'))\n")
        sources = {"research/research_source.py": head + caught, "research/other.py": head + caught, "other.py": head + item}
        named = "SparkError names its code as '%s', not a Code of spark.sourcing.sourcing_codes"
        # ast.walk reads a module's own lines before those in a try or a class
        self.assertEqual(calls_off_the_table(sources, sourcing_codes, NAMED_TOO["sourcing"]), (22, [
            "research/research_source.py:line 16: " + named % "error.code", "research/research_source.py:line 17: " + named % "error.code",
            "research/research_source.py:line 21: " + named % "records_codes.CODES", "research/research_source.py:line 13: " + named % "said.code",
            "research/research_source.py:line 15: " + named % "broad.code", "research/research_source.py:line 29: " + named % "error.code",
            "research/other.py:line 16: " + named % "error.code", "research/other.py:line 17: " + named % "error.code",
            "research/other.py:line 21: " + named % "records_codes.CODES", "research/other.py:line 13: " + named % "said.code",
            "research/other.py:line 15: " + named % "broad.code", "research/other.py:line 26: " + named % "error.code",
            "research/other.py:line 29: " + named % "error.code",
            "other.py:line 9: spark.core.result.Finding makes a Finding: Finding.of takes the fix from its Code",
            "other.py:line 10: spark.core.result.Finding makes a Finding: Finding.of takes the fix from its Code"]))

    def test_the_scan_reads_the_of_error_and_of_lines_of_a_coded_error_like_its_constructor(self):
        # P935 PR 3: DesignError.of_error (loader.py) was not seen: the call's name ends in of_error, not in the class's
        head = ("from spark.core.errors import CodedMessageError\nfrom spark.design import design_codes\n\n\n"
                "class DesignError(CodedMessageError):\n    pass\n\n\n")
        calls = ("DesignError.of_error(e, code=design_codes.PART_UNUSABLE)\n"
                 "DesignError.of_lines(lines, code=design_codes.BOARD_UNUSABLE, fix='f')\n"
                 "DesignError.of_error(e, code=reason)\n"
                 "DesignError.of_lines(lines, **kw)\n"
                 "Other.of_error(e, code=reason)\n")
        self.assertEqual(calls_off_the_table({"design.py": head + calls}, design_codes), (4, [
            "design.py:line 10: DesignError.of_lines gives a fix",
            "design.py:line 11: DesignError.of_error names its code as 'reason', not a Code of spark.design.design_codes",
            "design.py:line 12: DesignError.of_lines passes keywords by **",
            "design.py:line 12: DesignError.of_lines names its code as None, not a Code of spark.design.design_codes"]))

    def test_the_scan_takes_a_class_the_file_defines_with_no_bases_for_no_core_finding(self):
        # P935 PR 4: build_check.py and physics_check.py define their own `class Finding`; the refuter's two near misses stay flagged
        own = "class Finding:\n    pass\n\n\nFinding('a', 'b', 'c')\n"
        copied = ("from collections import namedtuple\n\n\nclass Finding(namedtuple('F', 'a b c d e')):\n    pass\n\n\n"
                  "Finding(1, None, 'x', 's', None)\n")
        derived = "from spark.core import result\n\n\nclass Finding(result.Finding):\n    pass\n\n\nFinding(1, None, 'x', 's', None)\n"
        rebound = ("from spark.core import result\n\n\nclass Finding:\n    pass\n\n\nFinding = getattr(result, 'Finding')\n"
                   "Finding(1, None, 'x', 's', None)\n")
        nested = "def make():\n    class Finding:\n        pass\n\n\nFinding(1, None, 'x', 's', None)\n"
        core = "from spark.core.result import Finding\n\n\nFinding(1, None, 'x', 's', None)\n"
        rule = "Finding makes a Finding: Finding.of takes the fix from its Code"
        self.assertEqual(calls_off_the_table({"own.py": own}, check_codes)[1], [])
        self.assertEqual(calls_off_the_table({"copied.py": copied}, check_codes)[1], ["copied.py:line 8: " + rule])
        self.assertEqual(calls_off_the_table({"derived.py": derived}, check_codes)[1], ["derived.py:line 8: " + rule])
        self.assertEqual(calls_off_the_table({"rebound.py": rebound}, check_codes)[1], ["rebound.py:line 9: " + rule])
        self.assertEqual(calls_off_the_table({"nested.py": nested}, check_codes)[1], ["nested.py:line 6: " + rule])
        self.assertEqual(calls_off_the_table({"core.py": core}, check_codes)[1], ["core.py:line 4: spark.core.result." + rule])


class TheDrawingCodeTest(unittest.TestCase):
    """P945: no_drawing_fact is a Code, so a build's kept entry gives its fix filled with the record that lacks the fact."""

    def test_no_drawing_fact_is_a_code_whose_fix_names_the_research_of_the_record(self):
        from spark.breadboard import drawing
        self.assertIsInstance(drawing.NO_DRAWING_FACT, Code)
        self.assertEqual(drawing.NO_DRAWING_FACT, "no_drawing_fact")
        self.assertEqual(drawing.NO_DRAWING_FACT.fix % "x-module", "research.py --part x-module --project . asks for the physical facts that draw it")
        self.assertEqual(drawing.CODES["no_drawing_fact"], drawing.NO_DRAWING_FACT.meaning)
        with self.assertRaises(TypeError):
            codes.fix_of(drawing.NO_DRAWING_FACT)  # a template: its site fills it, never a raw %s

    def test_a_kept_entry_with_no_record_has_no_fix_and_never_says_part_none(self):
        from spark.breadboard import drawing
        from spark.build import kept_files
        from spark.breadboard import svg_diagram
        renderer = svg_diagram.SvgBreadboardDiagram()
        board = kept_files.not_written_entry(drawing.NotWritten(Path("breadboard.svg"), renderer, drawing.NO_DRAWING_FACT,
                                                                "board-x", "nothing says how to draw the board board-x"))
        self.assertEqual([key for key in ("record", "fix") if key in board], [])
        part = kept_files.not_written_entry(drawing.NotWritten(Path("breadboard.svg"), renderer, drawing.NO_DRAWING_FACT,
                                                               "XModule", "why", "x-module"))
        self.assertEqual((part["record"], part["fix"]), ("x-module", "research.py --part x-module --project . asks for the physical facts that draw it"))


if __name__ == "__main__":
    unittest.main()
