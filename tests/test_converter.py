"""
The converter that moved into this plugin (P32a) is tested by this gate, not only by hand.

It is TypeScript, so `unittest` cannot reach inside it; what this does is run its own suite and
fail when that fails. Without this the move would have taken 1,300 lines of the product out of
reach of every guard here — the verification lens's own words about it while it still lived in the
smart bin: "1,645 TS lines and 50 tests sit outside this repo, so this gate never runs them."

`bun` and the converter's `node_modules` may reasonably be absent on a contributor's machine — a
fresh clone has neither — so its own suite SKIPS rather than fails. That is the one place in this
repository where "could not look" is allowed to read as green, and it is bounded:
`tools/check_commit.py` lends `node_modules` and runs it before a push. What ships is the bundle
(B10), and the refusals below run that, on Node.
"""

import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit


def code_of(path):
    """
    The TypeScript with its comments removed.

    These assertions are about what the code DOES, and this repository's comments quote the paths
    they explain the removal of — `board.ts` names `../../../.spark/board.json` in the paragraph
    saying why it is gone. Asserting over the raw text made the explanation fail the test.
    """
    text = re.sub(r"/\*.*?\*/", "", path.read_text(), flags=re.S)
    return "\n".join(line for line in text.splitlines() if not line.strip().startswith("//"))

import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
CONVERTER = ROOT / "tools" / "circuit-to-wokwi"
BUNDLE = CONVERTER / "dist" / "converter.mjs"


def node():
    """The command that runs the bundle, from spark's own list — or None when Node is not here.

    Not the person's file: a personal `{"node": {"on": false}}` skipped four of these tests, and a skip
    reads green (the final review of P82)."""
    import tempfile
    import tools
    try:
        return tools.find("js-runtime", None, Path(tempfile.mkdtemp()) / "absent.json").command
    except tools.ToolProblem:
        return None


class TheConvertersOwnSuiteTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("bun"), "bun is not installed; check_commit.py insists on it")
    @unittest.skipUnless((CONVERTER / "node_modules").is_dir(),
                         "development only: run `bun install` in tools/circuit-to-wokwi")
    def test_it_passes(self):
        result = subprocess.run(["bun", "run", "test"], cwd=str(CONVERTER),
                                capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0,
                         "the converter's own suite is red:\n%s" % result.stdout[-2000:])

    def test_it_is_here_at_all(self):
        # If the converter is not in the plugin, `check_spine` cannot simulate for anyone who has
        # not got one beside their project — which is the whole of what P32a bought.
        self.assertTrue((CONVERTER / "cli.ts").is_file())
        self.assertTrue(list((CONVERTER / "tests").glob("*.test.ts")))

    def test_it_takes_its_board_from_the_caller_and_never_from_its_own_location(self):
        # The fallback that made this tool unmovable: `../../../.spark/board.json`, resolved
        # against its own file, i.e. "whichever repository I happen to sit in".
        board = code_of(CONVERTER / "lib" / "board.ts")
        self.assertIn("SPARK_BOARD_JSON", board)
        self.assertNotIn("../../../.spark/board.json", board)

    def test_it_has_no_default_paths_shaped_like_one_project(self):
        cli = code_of(CONVERTER / "cli.ts")
        for gone in ("../../dist/board/circuit.json", "../../firmware/micropython/sim"):
            self.assertNotIn(gone, cli, "a default path into one project's layout is back")


class ItRefusesToGuessTest(unittest.TestCase):
    """
    The three defects that let this tool work only where its author kept it.

    Each is exercised by RUNNING it, because each lives in a path the converter's own suite never
    takes: that suite sets `SPARK_BOARD_JSON` and passes every argument, so the missing cases are
    invisible to it by construction. All three escaped a green suite first time round.
    """

    def run_cli(self, args, env_board=True):
        import os
        env = dict(os.environ)
        env.pop("SPARK_BOARD_JSON", None)
        if env_board:
            env["SPARK_BOARD_JSON"] = str(ROOT / "boards" / "firebeetle2-esp32s3.json")
        return subprocess.run(node() + [str(BUNDLE), *args], cwd=str(CONVERTER),
                              capture_output=True, text=True, timeout=120, env=env)

    @unittest.skipUnless(node(), "node is not installed")
    def test_no_board_named_is_refused_with_a_sentence(self):
        said = self.run_cli(["--circuit", "x", "--out", "y", "--chips", "z"], env_board=False)
        self.assertNotEqual(said.returncode, 0, "it converted without knowing which board")
        self.assertIn("SPARK_BOARD_JSON", said.stderr + said.stdout)

    @unittest.skipUnless(node(), "node is not installed")
    def test_no_paths_given_is_refused_with_a_sentence(self):
        said = self.run_cli([])
        self.assertNotEqual(said.returncode, 0, "it ran with no design to convert")
        self.assertIn("required", said.stderr + said.stdout)

    def test_the_search_names_no_other_repository(self):
        # It named `../smartbin-local/tools/circuit-to-wokwi/cli.ts` — one person's checkout,
        # beside which the chain's last stage was the only place it worked.
        import check_spine
        for entry in check_spine.CONVERTER_PATHS:
            self.assertNotIn("..", entry,
                             "a search path that climbs out of the project names somebody's "
                             "machine: %r" % entry)



class TheBundleConvertsOnNodeTest(unittest.TestCase):
    """
    What ships converts, on Node — not only loads. The first bundle passed every refusal and then
    said "Bun is not defined" on the quickstart's board: cli.ts read and wrote with Bun.file and
    Bun.write, which the refusals never reach (2026-10-03, P82 task 4). An empty circuit takes
    every file path the converter has: read the circuit, read the diagram it would merge, write, check.
    """

    def convert(self, *extra):
        import os, tempfile
        env = dict(os.environ, SPARK_BOARD_JSON=str(ROOT / "boards" / "firebeetle2-esp32s3.json"))
        return subprocess.run(node() + [str(BUNDLE), "--circuit", str(self.circuit), "--out", str(self.out),
                                        "--chips", str(self.chips), *extra],
                              cwd=str(self.chips.parent), capture_output=True, text=True, timeout=120, env=env)

    @unittest.skipUnless(node(), "node is not installed")
    def test_it_writes_a_diagram_and_then_finds_it_up_to_date(self):
        import tempfile
        here = Path(tempfile.mkdtemp())
        self.circuit, self.out, self.chips = here / "circuit.json", here / "diagram.json", here / "chips"
        self.chips.mkdir()
        self.circuit.write_text("[]")
        wrote = self.convert()
        self.assertEqual(wrote.returncode, 0, wrote.stderr + wrote.stdout)
        self.assertTrue(self.out.is_file())
        again = self.convert()
        self.assertEqual(again.returncode, 0, "converting over its own diagram: " + again.stderr + again.stdout)
        checked = self.convert("--check")
        self.assertIn("up to date", checked.stdout, checked.stderr)

    @unittest.skipUnless(node(), "node is not installed")
    def test_a_part_record_s_mapping_reaches_the_diagram(self):
        # The second bundle converted, and ignored the records: bun put two copies of lib/mapping.ts
        # in it, cli.ts loaded the records into one and the emitter read the other — the quickstart's
        # resistors came out as RGB LEDs (2026-10-03). The same circuit as the converter's own
        # mapping-file.test.ts, through the shipped file.
        import json, tempfile
        here = Path(tempfile.mkdtemp())
        self.circuit, self.out, self.chips = here / "circuit.json", here / "diagram.json", here / "chips"
        self.chips.mkdir()
        parts = {"Mcu": ["SDA", "GND1"], "Valve1": ["SIGNAL", "GND"], "DcBarrelJack12vInlet": ["VIN", "GND"]}
        nets = [("VALVE1", ["Mcu:SDA", "Valve1:SIGNAL"]),
                ("GND", ["Mcu:GND1", "Valve1:GND", "DcBarrelJack12vInlet:GND"])]
        elements, port_ids = [], {}
        for index, (name, pins) in enumerate(parts.items()):
            elements.append({"type": "source_component", "source_component_id": "source_component_%d" % index,
                             "name": name, "ftype": "simple_chip"})
            for number, pin in enumerate(pins, 1):
                port = "source_port_%d_%d" % (index, number)
                port_ids["%s:%s" % (name, pin)] = port
                elements.append({"type": "source_port", "source_port_id": port,
                                 "source_component_id": "source_component_%d" % index, "name": "pin%d" % number,
                                 "pin_number": number, "port_hints": [pin, "pin%d" % number]})
        for index, (net_name, members) in enumerate(nets):
            elements.append({"type": "source_net", "source_net_id": "source_net_%d" % index, "name": net_name})
            elements.append({"type": "source_trace", "source_trace_id": "source_trace_%d" % index,
                             "connected_source_port_ids": [port_ids[m] for m in members],
                             "connected_source_net_ids": ["source_net_%d" % index]})
        self.circuit.write_text(json.dumps(elements))
        mapping = here / "wokwi-mapping.json"
        mapping.write_text(json.dumps({
            "Valve1": {"wokwiType": "wokwi-led", "pins": {"SIGNAL": "A", "GND": "C", "VCC": None}},
            "DcBarrelJack12vInlet": {"skip": "a connector is wiring, not a part to simulate"}}))
        done = self.convert("--mapping", str(mapping))
        self.assertEqual(done.returncode, 0, done.stderr + done.stdout)
        diagram = json.loads(self.out.read_text())
        self.assertIn("wokwi-led", [part["type"] for part in diagram["parts"]])
        self.assertTrue(any("valve1:A" in "%s-%s" % (wire[0], wire[1]) for wire in diagram["connections"]),
                        "the record's pin map did not reach the wires")

if __name__ == "__main__":
    unittest.main()
