"""
The page's script (P829 PR 3, #1187): runs its own tests, tests/flow_script/page_script.test.js, with `node --test`.
Without node the test skips, and the gate stops a story run that holds this module (`check_commit.needs_node`): a skip is
not a pass.
The script's source is page_script.ts (P1061): tsc compiles it to the committed page_script.js, which the node tests load
and the gate compares with tsc's output (`check_commit.script_drift`). TS_SOURCES names the source and its settings, so a
change of each runs this module; the compiled output keeps async and await, with no tsc helper.

    python3 -m unittest tests.test_flow_script
"""

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
#: The script's own tests, named here so tools/story_tests.py maps a change of either file to this module.
JS_TESTS = ROOT / "tests" / "flow_script" / "page_script.test.js"
NODE = shutil.which("node")
FLOW = ROOT / "scripts" / "spark" / "flow"
#: The compiled output that the page ships and the node tests load (P1061): committed, never written by hand.
PAGE_SCRIPT = FLOW / "page_script.js"
#: The script's TypeScript source and its compile settings (P1061), named so tools/story_tests.py maps a change of each
#: to this module. With the compiled .js they are the gate's check_commit.SCRIPT_SOURCES.
TS_SOURCES = (FLOW / "page_script.ts", FLOW / "tsconfig.json", FLOW / "artifact_runtime.d.ts")


class PageScriptTest(unittest.TestCase):

    @unittest.skipIf(NODE is None, "node is not installed: check_commit stops a story run that holds this test")
    def test_the_page_script_s_own_tests_pass(self):
        run = subprocess.run([NODE, "--test", "--test-reporter=tap", str(JS_TESTS)], capture_output=True, text=True, cwd=str(ROOT), timeout=120)
        said = run.stdout + run.stderr
        self.assertEqual(run.returncode, 0, said)
        self.assertIn("# pass 31\n", said)  # P1122: three tests of a chat offer's Copy; P1067: nine of several picks; P1135: two; P1286: two of the run block's Copy
        self.assertIn("# fail 0\n", said)


class TheCompiledScriptTest(unittest.TestCase):
    """P1061: what tsc writes from page_script.ts, read as text; no node and no tsc, so these never skip."""

    def test_the_compiled_script_keeps_async_with_no_helper(self):
        # a target below ES2017 rewrites async and await into tsc's helper __awaiter (and __generator below ES2015)
        text = PAGE_SCRIPT.read_text()
        for helper in ("__awaiter", "__generator"):
            self.assertEqual(text.count(helper), 0, helper)

    def test_the_sources_are_the_gate_s(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import check_commit
        self.assertEqual({source.relative_to(ROOT).as_posix() for source in TS_SOURCES + (PAGE_SCRIPT,)},
                         set(check_commit.SCRIPT_SOURCES))


if __name__ == "__main__":
    unittest.main()
