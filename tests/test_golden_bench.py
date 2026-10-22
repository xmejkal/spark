"""P380 (#487): what look, deploy, grant --check, live and reach print today stays what they print, so no move breaks it."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

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
        assert cls.token, "look-ok gave no token, so no deploy Case can run: %s" % out

    def run_case(self, case):
        store = Path(tempfile.mkdtemp(dir=self.folder))  # each Case its own store, so that no grant leaks
        code, out = golden_bench.run_script(case, self.project, store, self.token)
        self.assertEqual(code, case.exit_code, out)
        why = golden_bench.check_golden(case, golden_bench.scrub(out, golden_bench.replacements_of(self.project, store)))
        self.assertIsNone(why, why)

    def test_no_golden_holds_a_path_of_this_machine(self):
        for golden in sorted(golden_bench.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            for path in (str(Path.home()), "/Users/", tempfile.gettempdir(), str(golden_bench.ROOT)):
                self.assertNotIn(path, text, golden.name)

    def test_every_golden_has_its_case(self):
        written = {golden.name for golden in golden_bench.GOLDEN_DIR.iterdir()}
        self.assertEqual(written, {case.golden for case in golden_bench.CASES})

    def test_the_token_ends_in_the_image_hash(self):
        # The goldens print the image half as <image>, so this pins it: the first 4 hex of the image's sha256.
        image = next(self.project.glob("sim/*.bin"))
        self.assertTrue(self.token.endswith("-" + hashlib.sha256(image.read_bytes()).hexdigest()[:4]), self.token)


for _case in golden_bench.CASES:
    setattr(BenchGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.run_case(case))


if __name__ == "__main__":
    unittest.main()
