"""
The converter that moved into this plugin (P32a) is tested by this gate, not only by hand.

It is TypeScript, so `unittest` cannot reach inside it; what this does is run its own suite and
fail when that fails. Without this the move would have taken 1,300 lines of the product out of
reach of every guard here — the verification lens's own words about it while it still lived in the
smart bin: "1,645 TS lines and 50 tests sit outside this repo, so this gate never runs them."

`bun` may reasonably be absent on a contributor's machine, so a missing runtime SKIPS rather than
fails. That is the one place in this repository where "could not look" is allowed to read as green,
and it is bounded: `tools/check_commit.py` is where the run is mandatory before a push.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path


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


class TheConvertersOwnSuiteTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("bun"), "bun is not installed; check_commit.py insists on it")
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
        return subprocess.run(["bun", "run", "cli.ts", *args], cwd=str(CONVERTER),
                              capture_output=True, text=True, timeout=120, env=env)

    @unittest.skipUnless(shutil.which("bun"), "bun is not installed")
    def test_no_board_named_is_refused_with_a_sentence(self):
        said = self.run_cli(["--circuit", "x", "--out", "y", "--chips", "z"], env_board=False)
        self.assertNotEqual(said.returncode, 0, "it converted without knowing which board")
        self.assertIn("SPARK_BOARD_JSON", said.stderr + said.stdout)

    @unittest.skipUnless(shutil.which("bun"), "bun is not installed")
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


if __name__ == "__main__":
    unittest.main()
