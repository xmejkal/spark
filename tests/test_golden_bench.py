"""P380 (#487): what look, deploy, grant --check, live and reach print today stays what they print, so no move breaks it."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

import golden_bench  # noqa: E402


class BenchGoldenTest(unittest.TestCase):
    """Each Case of golden_bench.CASES is one test, named after its golden, run in one project built for the class."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.project = golden_bench.build_project(cls.folder)
        look_ok = next(case for case in golden_bench.CASES if case.golden == "look-ok.json")
        code, out = golden_bench.run_script(look_ok, cls.project, Path(tempfile.mkdtemp(dir=cls.folder)))
        cls.token = (json.loads(out)["data"] or {}).get("token") if code == 0 else None

    def check(self, case):
        store = Path(tempfile.mkdtemp(dir=self.folder))  # each Case its own store, so that no grant leaks
        code, out = golden_bench.run_script(case, self.project, store, self.token)
        self.assertEqual(code, case.exit_code, out)
        why = golden_bench.check_golden(case, golden_bench.scrub(out, golden_bench.places_of(self.project, store)))
        self.assertIsNone(why, why)

    def test_no_golden_holds_a_home_path(self):
        for golden in sorted(golden_bench.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            self.assertNotIn(str(Path.home()), text, golden.name)
            self.assertNotIn("/Users/", text, golden.name)


for _case in golden_bench.CASES:
    setattr(BenchGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.check(case))


if __name__ == "__main__":
    unittest.main()
