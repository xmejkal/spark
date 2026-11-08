"""P686 (#924, W6-B1): what breadboard.py prints today, and the files it writes beside the sheet, stays what it prints, so
the breadboard codes and the move break nothing. breadboard.py runs no tool, so nothing is faked."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

import golden_bench  # noqa: E402
import golden_breadboard  # noqa: E402


class BreadboardChildTest(unittest.TestCase):
    """A child carries no Wokwi token, and every Case belongs to the op `breadboard`."""

    def test_a_child_run_carries_no_wokwi_token(self):
        folder = Path(tempfile.mkdtemp())
        probe = folder / "probe.py"  # an absolute script: run_child runs it in place of one in scripts/
        probe.write_text("import os\nprint(os.environ.get('WOKWI_CLI_TOKEN'))\n")
        case = golden_breadboard.CASES[0]._replace(script=str(probe), argv=[])
        with mock.patch.dict(os.environ, {"WOKWI_CLI_TOKEN": "a-pretend-token"}):
            done = golden_breadboard.run_child(case, folder, folder / "store")
        self.assertEqual(done.stdout, "None\n", done.stderr)

    def test_the_op_of_every_case_is_breadboard(self):
        self.assertEqual({golden_bench.op_of(case) for case in golden_breadboard.CASES}, {"breadboard"})


class BreadboardGoldenTest(unittest.TestCase):
    """Each Case of golden_breadboard.CASES is one test, named after its golden, run in its own copy of its fixture."""

    def run_case(self, case):
        work = Path(tempfile.mkdtemp())
        project, store = golden_breadboard.copy_project(case, work), work / "store"
        code, text = golden_breadboard.run_script(case, project, store)
        self.assertEqual(code, case.exit_code, text)
        scrubbed = golden_bench.scrub(text, golden_bench.replacements_of(project, store))
        self.assertIsNone(golden_bench.check_golden(case, scrubbed, golden_dir=golden_breadboard.GOLDEN_DIR))

    def test_no_golden_holds_a_path_of_this_machine(self):
        for golden in sorted(golden_breadboard.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            for path in (str(Path.home()), "/Users/", tempfile.gettempdir(), str(golden_bench.ROOT)):
                self.assertNotIn(path, text, golden.name)

    def test_every_golden_has_its_case(self):
        written = {golden.name for golden in golden_breadboard.GOLDEN_DIR.iterdir()}
        self.assertEqual(written, {case.golden for case in golden_breadboard.CASES})


for _case in golden_breadboard.CASES:
    setattr(BreadboardGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.run_case(case))


if __name__ == "__main__":
    unittest.main()
