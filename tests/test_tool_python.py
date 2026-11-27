"""P1264: a Python tool is found where the person's shell finds it, in the Python that holds its module.

The fixture is real. A venv made in a temporary folder holds the module `p1264_mod` (release 1.29.0). An executable on a
PATH names that venv's Python on its first line, and a shim is a `#!/bin/sh` script that runs it. No home path is written.
Each test names its red: the module missing from the running Python, then the wrong answer.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records import tool_finder  # noqa: E402
from spark.records import tool_python  # noqa: E402
from spark.records import versions  # noqa: E402

INSTALL = "python3 -m pip install --user p1264-mod=={version}"
ENTRY = {"for": "a test", "kind": "python", "module": "p1264_mod", "exe": "p1264-exe", "version": "1.29.0",
         "install": {"pip": INSTALL}}


def write_script(path, first_line, body=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("%s\n%s" % (first_line, body))
    path.chmod(0o755)
    return str(path)


class CountingReader(tool_python.ModuleReader):
    """A ModuleReader that counts the children it starts."""

    def __init__(self):
        super().__init__(run=self.counted)
        self.count = 0

    def counted(self, *args, **kwargs):
        self.count += 1
        return subprocess.run(*args, **kwargs)


class TheVenvTest(unittest.TestCase):
    """The base: one venv with the module, and a PATH of folders the tests choose."""

    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="p1264-")).resolve()  # macOS: /var is /private/var
        try:
            subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(cls.root / "venv")], check=True,
                           capture_output=True)
        except (OSError, subprocess.CalledProcessError) as cannot:
            raise unittest.SkipTest("python3 -m venv is not available here: %s" % cannot)
        cls.python = str(cls.root / "venv" / "bin" / "python3")
        site = next((cls.root / "venv" / "lib").glob("python*/site-packages"))
        cls.site = site
        (site / "p1264_mod.py").write_text("VALUE = 1\n")
        (site / "p1264_mod-1.29.0.dist-info").mkdir()
        (site / "p1264_mod-1.29.0.dist-info" / "METADATA").write_text("Metadata-Version: 2.1\nName: p1264_mod\nVersion: 1.29.0\n")
        cls.exe = write_script(cls.root / "bin" / "p1264-exe", "#!" + cls.python)
        cls.bare = write_script(cls.root / "bare" / "p1264-bare", "#!" + sys.executable)
        cls.shim = write_script(cls.root / "shims" / "p1264-shim", "#!/bin/sh", 'exec "%s" "$@"\n' % cls.python)
        write_script(cls.root / "shims" / "python3", "#!/bin/sh", 'exec "%s" "$@"\n' % cls.python)
        (cls.root / "pybin").mkdir()
        (cls.root / "pybin" / "python3").symlink_to(sys.executable)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def setUp(self):
        tool_python.TOOL_PYTHONS.forget()
        self.addCleanup(tool_python.TOOL_PYTHONS.forget)

    def path(self, *folders):
        """A PATH of these folders of the fixture, then the folder that holds a python3."""
        patcher = mock.patch.dict(os.environ, {"PATH": os.pathsep.join([str(self.root / f) for f in folders] + [str(self.root / "pybin")])})
        patcher.start()
        self.addCleanup(patcher.stop)

    def entry(self, **fields):
        return dict(ENTRY, **fields)


class TheToolPythonIsFoundTest(TheVenvTest):
    def test_a_first_line_python_that_holds_the_module_is_the_tools_python(self):
        """Red: the module missing from the running Python gave None. Then the wrong release or executable."""
        self.path("bin")
        found = tool_python.ToolPythonFinder().find(self.entry())
        self.assertEqual(found, tool_python.ToolPython(self.python, "1.29.0", self.exe))

    def test_a_shim_is_asked_through_the_python3_beside_it_and_the_answer_is_the_childs_own_python(self):
        """Red: no python3 beside the shim, then the shim's path given as the Python."""
        self.path("shims")
        found = tool_python.ToolPythonFinder().find(self.entry(exe="p1264-shim"))
        self.assertEqual(found, tool_python.ToolPython(self.python, "1.29.0", self.shim))
        self.assertNotEqual(found.python, str(self.root / "shims" / "python3"))

    def test_an_executable_whose_pythons_do_not_hold_the_module_gives_none_and_the_sentence_says_which_were_asked(self):
        """Red: the sentence named no Python."""
        self.path("bare")
        finder = tool_python.ToolPythonFinder()
        entry = self.entry(exe="p1264-bare")
        self.assertIsNone(finder.find(entry))
        self.assertEqual(finder.on_path(entry, "python3 -m pip install --user p1264-mod==1.29.0"),
                         "p1264-bare is on your PATH (%s), but no Python spark asked holds its module: %s holds no p1264_mod "
                         "module. Copy this step: %s -m pip install --user p1264-mod==1.29.0"
                         % (self.bare, sys.executable, sys.executable))

    def test_a_child_that_times_out_prints_no_json_or_cannot_start_says_spark_cannot_ask_it(self):
        """Red: each read as "holds no module"."""
        self.path("bin")
        said = {}
        answers = {"a timeout": subprocess.TimeoutExpired("x", 1), "no start": FileNotFoundError(2, "No such file"),
                   "no json": subprocess.CompletedProcess([], 0, stdout="not json", stderr="")}
        for name, answer in answers.items():
            def run(*args, **kwargs):
                if isinstance(answer, Exception):
                    raise answer
                return answer
            finder = tool_python.ToolPythonFinder(reader=tool_python.ModuleReader(run=run, timeout_s=7))
            self.assertIsNone(finder.find(self.entry()))
            said[name] = finder.on_path(self.entry(), "python3 -m pip install --user p1264-mod==1.29.0")
        self.assertIn("%s did not answer in 7 s." % self.python, said["a timeout"])
        self.assertIn("%s cannot be started (No such file)." % self.python, said["no start"])
        self.assertIn("%s gave an answer spark cannot read." % self.python, said["no json"])
        self.assertTrue(all("holds no p1264_mod module" not in line for line in said.values()))

    def test_an_entry_with_no_exe_is_never_looked_for_on_the_path(self):
        """Red: an import tool with no `exe` was looked for as its module's name."""
        asked = []
        finder = tool_python.ToolPythonFinder(which=lambda exe: asked.append(exe))
        entry = self.entry()
        del entry["exe"]
        self.assertIsNone(finder.find(entry))
        self.assertIsNone(finder.find(dict(entry, exe="")))
        self.assertEqual(asked, [])

    def test_two_finds_of_one_tool_run_one_child(self):
        """Red: a child for each find."""
        self.path("bin")
        reader = CountingReader()
        finder = tool_python.ToolPythonFinder(reader=reader)
        first, second = finder.find(self.entry()), finder.find(self.entry())
        self.assertEqual((first, reader.count), (second, 1))
        finder.forget()
        finder.find(self.entry())
        self.assertEqual(reader.count, 2)

    def test_a_which_answer_that_is_no_file_gives_no_candidate_and_runs_no_child(self):
        """Red: a child was started for a path that is not there."""
        reader = CountingReader()
        for answer in (str(self.root / "absent"), str(self.root / "bin")):
            finder = tool_python.ToolPythonFinder(reader=reader, which=lambda exe, answer=answer: answer)
            self.assertIsNone(finder.find(self.entry()))
        self.assertEqual(reader.count, 0)

    def test_a_not_found_answer_is_never_kept_so_a_module_installed_later_is_found(self):
        """Red: the first None was kept for the process."""
        self.path("bare")
        shutil.copy(self.bare, self.root / "bare" / "p1264-late")
        (self.root / "bare" / "p1264-late").write_text("#!%s\n" % self.python)
        (self.root / "bare" / "p1264-late").chmod(0o755)
        entry = self.entry(exe="p1264-late", module="p1264_late")
        finder = tool_python.ToolPythonFinder()
        self.assertIsNone(finder.find(entry))
        late = self.site / "p1264_late.py"
        late.write_text("VALUE = 2\n")
        self.addCleanup(late.unlink)
        self.assertEqual(finder.find(entry).python, self.python)

    def test_the_default_finder_looks_up_which_and_the_reader_when_it_asks(self):
        """Red: shutil.which was bound at import, so a test that set it saw nothing."""
        finder = tool_python.ToolPythonFinder()
        self.assertEqual((finder.which, finder.reader), (None, None))
        real = shutil.which
        self.addCleanup(setattr, shutil, "which", real)
        shutil.which = lambda exe: self.exe
        self.assertEqual(finder.find(self.entry()).executable, self.exe)

    def test_the_sentence_with_no_executable_on_the_path_is_empty_and_the_looked_clause_names_both_places(self):
        """Red: the clause named only one place."""
        self.path("pybin")
        finder = tool_python.ToolPythonFinder()
        self.assertEqual(finder.on_path(self.entry(), "python3 -m pip install --user p1264-mod==1.29.0"), "")
        self.assertEqual(finder.looked(self.entry()),
                         ". Spark looked for the p1264_mod module in %s, the Python that runs spark, and for p1264-exe on the PATH."
                         % sys.executable)
        self.assertEqual(finder.looked(dict(self.entry(), exe="")), "")



if __name__ == "__main__":
    unittest.main()
