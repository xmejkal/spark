"""
The page's script (P829 PR 3, #1187): runs its own tests, tests/flow_script/page_script.test.js, with `node --test`.
Without node the test skips, and the gate stops a story run that holds this module (`check_commit.needs_node`): a skip is
not a pass.

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


class PageScriptTest(unittest.TestCase):

    @unittest.skipIf(NODE is None, "node is not installed: check_commit stops a story run that holds this test")
    def test_the_page_script_s_own_tests_pass(self):
        run = subprocess.run([NODE, "--test", str(JS_TESTS)], capture_output=True, text=True, cwd=str(ROOT), timeout=120)
        said = run.stdout + run.stderr
        self.assertEqual(run.returncode, 0, said)
        self.assertIn("# pass 12\n", said)
        self.assertIn("# fail 0\n", said)


if __name__ == "__main__":
    unittest.main()
