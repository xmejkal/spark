"""
Proof that the suite leaves nothing in the temp folder (P172).

One run of the suite on main c49a17e left 2,291 entries, 26 MB, in an empty temp folder: 254
`tempfile.mkdtemp()` calls in 28 test files, many in helpers outside any test, and nobody removed what
they made. Removing each by hand would be 254 edits and the 255th test would leak again. So every test
process makes ONE folder (`suite_temp.py`), points the temp folder at it — its own and its children's —
and removes it when it exits. These tests pin that every test module asks for it first, and that a
process which does leaves nothing behind.

    python3 -m unittest discover -s tests
"""

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402  P172: this process's temp folder, removed at exit

TESTS = Path(__file__).resolve().parent


def is_sparks(name):
    """Whether a top-level module name is spark's own: `scripts/`, `tools/` or `tests/` holds `<name>.py`."""
    return any((TESTS.parent / folder / (name + ".py")).is_file() for folder in ("scripts", "tools", "tests"))


def asks_first(source):
    """
    Whether `import suite_temp` comes before anything but the docstring, imports of modules that are not spark's and
    a `sys.path.insert`: a spark module imported first, or a helper run first, would make its temp files elsewhere.
    """
    for node in ast.parse(source).body:
        if isinstance(node, ast.Import) and any(alias.name == "suite_temp" for alias in node.names):
            return True
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if not any(is_sparks(name.split(".")[0]) for name in names):
                continue
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        elif isinstance(node, ast.Expr) and ast.unparse(node.value).startswith("sys.path.insert("):
            continue
        return False
    return False


class EveryTestModuleAsksForItFirstTest(unittest.TestCase):
    def test_every_test_module_imports_it_before_anything_else_it_runs(self):
        late = [path.name for path in sorted(TESTS.glob("test_*.py")) if not asks_first(path.read_text())]
        self.assertEqual(late, [], "these import a spark module or run code before `import suite_temp`")

    def test_the_reading_tells_first_from_late(self):
        self.assertTrue(asks_first('"""doc"""\nimport os\nsys.path.insert(0, "x")\nimport suite_temp\nimport store\n'))
        self.assertFalse(asks_first("import os\nimport store\nimport suite_temp\n"))
        self.assertFalse(asks_first("import os\nX = os.getcwd()\nimport suite_temp\n"))
        self.assertFalse(asks_first("import os\n"))


class InsideATestTheTempFolderIsTheSuitesTest(unittest.TestCase):
    def test_this_process_and_its_children_make_their_temp_files_in_the_one_folder(self):
        self.assertEqual(tempfile.gettempdir(), suite_temp.ROOT)
        self.assertEqual(Path(tempfile.mkdtemp()).parent, Path(suite_temp.ROOT))
        self.assertEqual(os.environ.get("TMPDIR"), suite_temp.ROOT, "a script a test starts reads TMPDIR")
        self.assertTrue(Path(suite_temp.ROOT).name.startswith("spark-tests-"))


class AProcessThatAsksLeavesNothingTest(unittest.TestCase):
    def test_a_test_process_and_the_script_it_starts_leave_the_temp_folder_empty(self):
        fresh = tempfile.mkdtemp()
        child = ("import sys; sys.path.insert(0, %r); import suite_temp, subprocess, tempfile; tempfile.mkdtemp(); "
                 "subprocess.run([sys.executable, '-c', 'import tempfile; tempfile.mkdtemp()'], check=True)" % str(TESTS))
        done = subprocess.run([sys.executable, "-c", child], env=dict(os.environ, TMPDIR=fresh),
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(os.listdir(fresh), [])

    def test_it_removes_nothing_but_the_folder_it_made_in_the_process_that_made_it(self):
        other = Path(tempfile.mkdtemp())
        (other / "kept").write_text("somebody else's\n")
        self.assertFalse(suite_temp.remove(str(other)))
        self.assertTrue((other / "kept").is_file())
        with mock.patch.object(suite_temp.os, "getpid", return_value=os.getpid() + 1):
            self.assertFalse(suite_temp.remove(suite_temp.ROOT), "a forked child never removes its parent's folder")
        self.assertTrue(Path(suite_temp.ROOT).is_dir())


if __name__ == "__main__":
    unittest.main()
