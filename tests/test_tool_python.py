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

from spark.bench import board_connection  # noqa: E402
from spark.bench import board_look  # noqa: E402
from spark.bench import deploy_image  # noqa: E402
from spark.bench import firmware_platform  # noqa: E402
from spark.bench import look_at_board  # noqa: E402
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

    def test_only_tool_finder_and_versions_import_tool_python(self):
        """C7: one door. Red: a module outside the two read the finder."""
        importers = sorted(path.stem for path in (ROOT / "scripts").rglob("*.py")
                           if "tool_python" in "".join(line for line in path.read_text().splitlines()
                                                       if line.startswith(("import ", "from ")) or line.startswith("    from "))
                           and path.stem != "tool_python")
        self.assertEqual(importers, ["tool_finder", "versions"])


class TheFinderUsesItTest(TheVenvTest):
    """The card's tests: a tool found on the PATH and not in the running Python counts as installed."""

    def setUp(self):
        super().setUp()
        self.nobody = Path(tempfile.mkdtemp(dir=self.root)) / "absent.json"
        self.project = self.project_with(ENTRY)

    def project_with(self, entry):
        root = Path(tempfile.mkdtemp(dir=self.root))
        (root / ".spark").mkdir()
        (root / ".spark" / "tools.json").write_text(json.dumps({"p1264-tool": entry, "roles": {"board-shell": "p1264-tool"}}))
        return root

    def row(self):
        rows = tool_finder.status(self.project, self.nobody)
        return next(row for row in rows if row[1] == "board-shell")

    def test_a_tool_found_on_the_path_and_not_in_the_running_python_counts_as_installed(self):
        """THE CARD'S TEST. Red: ToolMissingError, because only the running Python was asked."""
        self.path("bin")
        tool = tool_finder.find("board-shell", self.project, self.nobody)
        self.assertEqual(tool.command, [self.python])
        self.assertEqual(tool_finder.command_for(tool), [self.python, "-m", "p1264_mod"])
        self.assertEqual(self.row(), ("ok", "board-shell", "p1264-tool 1.29.0, runs with %s (found through %s)" % (self.python, self.exe)))

    def test_a_tool_found_nowhere_still_says_how_to_install_it(self):
        """THE CARD'S TEST. Red: the sentence did not say where spark looked."""
        self.path("pybin")
        with self.assertRaises(tool_finder.ToolMissingError) as missing:
            tool_finder.find("board-shell", self.project, self.nobody)
        self.assertEqual(str(missing.exception),
                         "board-shell (p1264-tool) is not installed — install: python3 -m pip install --user p1264-mod==1.29.0"
                         ". Spark looked for the p1264_mod module in %s, the Python that runs spark, and for p1264-exe on the PATH."
                         % sys.executable)
        self.assertEqual(missing.exception.code, "tool_missing")

    def test_a_tool_on_the_path_whose_pythons_hold_no_module_says_so_and_ends_with_one_step_to_copy(self):
        """C2. Red: the sentence said "is not installed" and gave an install line for a Python that was not asked."""
        self.path("bare")
        project = self.project_with(dict(ENTRY, exe="p1264-bare"))
        with self.assertRaises(tool_finder.ToolMissingError) as missing:
            tool_finder.find("board-shell", project, self.nobody)
        self.assertEqual(str(missing.exception),
                         "p1264-bare is on your PATH (%s), but no Python spark asked holds its module: %s holds no p1264_mod "
                         "module. Copy this step: %s -m pip install --user p1264-mod==1.29.0" % (self.bare, sys.executable, sys.executable))
        self.assertEqual(missing.exception.code, "tool_missing")
        self.assertEqual(self.row_of(project)[0], "missing")

    def row_of(self, project):
        return next(row for row in tool_finder.status(project, self.nobody) if row[1] == "board-shell")

    def test_the_floor_holds_on_the_tools_python(self):
        """Red: the release was read in the running Python only, so the floor never fired."""
        self.path("bin")
        project = self.project_with(dict(ENTRY, oldest_version="2.0"))
        with self.assertRaises(tool_finder.ToolError) as old:
            tool_finder.find("board-shell", project, self.nobody)
        self.assertEqual(old.exception.code, "tool_too_old")
        self.assertIn("p1264-tool 1.29.0 is too old: spark needs 2.0 or newer.", str(old.exception))

    def test_the_pin_holds_on_the_tools_python_and_the_plan_says_already_here(self):
        """Red: the pin compared None to the pin."""
        self.path("bin")
        command = tool_finder.find("board-shell", self.project, self.nobody).command
        self.assertEqual(tool_finder.pin_differences(self.entry(), command), [])
        self.assertEqual(tool_finder.pin_differences(self.entry(version="1.30.0"), command), [("version", "1.29.0", "1.30.0")])
        steps = tool_finder.plan(["p1264-tool"], self.project, self.nobody)
        self.assertEqual(steps[-1]["here"], "the p1264_mod module of %s" % self.python)
        self.assertEqual(versions.installed_release(self.entry()), "1.29.0")

    def test_to_install_leaves_out_a_tool_found_through_the_path_and_names_one_that_is_not(self):
        """Red: the tool was offered for install."""
        self.path("bin")
        self.assertNotIn("p1264-tool", tool_finder.to_install(self.project, self.nobody))
        self.path("pybin")
        tool_python.TOOL_PYTHONS.forget()
        self.assertIn("p1264-tool", tool_finder.to_install(self.project, self.nobody))

    def test_the_running_python_still_wins_and_runs_no_child(self):
        """Red: the PATH was asked first, and a child ran."""
        self.path("bin")
        reader = CountingReader()
        self.addCleanup(setattr, tool_python.TOOL_PYTHONS, "reader", None)
        tool_python.TOOL_PYTHONS.reader = reader
        project = self.project_with(dict(ENTRY, module="json"))
        self.assertEqual(tool_finder.find("board-shell", project, self.nobody).command, [sys.executable])
        self.assertEqual(reader.count, 0)

    def test_an_empty_exe_turns_the_path_lookup_off(self):
        """The setting `exe` (project layer). Red: an empty `exe` was looked for as a name."""
        self.path("bin")
        project = self.project_with(dict(ENTRY, exe=""))
        with self.assertRaises(tool_finder.ToolError) as lacking:
            tool_finder.find("board-shell", project, self.nobody)
        self.assertEqual(lacking.exception.code, "tool_missing")

    def test_the_release_of_the_row_is_the_one_locate_kept_and_no_second_child_runs(self):
        """C8. Red: installed_release asked a second child."""
        self.path("bin")
        reader = CountingReader()
        self.addCleanup(setattr, tool_python.TOOL_PYTHONS, "reader", None)
        tool_python.TOOL_PYTHONS.reader = reader
        self.row()
        self.assertEqual(reader.count, 1)

    def test_install_forgets_what_was_kept(self):
        """Red: a tool installed by /spark:setup was still missing for the process."""
        self.path("bin")
        project = self.project_with(dict(ENTRY, version="1.30.0"))
        tool_finder.find("board-shell", project, self.nobody)
        self.assertTrue(tool_python.TOOL_PYTHONS.kept)
        tool_finder.install(["p1264-tool"], project, self.nobody, run=lambda argv, **kw: None)
        self.assertFalse(tool_python.TOOL_PYTHONS.kept)


class TheLookTheFlashAndTheSetupReportAgreeTest(TheVenvTest):
    """The look, the deploy and `tools.py --status` all ask `find`, so they run the tool's Python and say one sentence."""

    def setUp(self):
        super().setUp()
        self.project = Path(tempfile.mkdtemp(dir=self.root))
        (self.project / ".spark").mkdir()
        (self.project / ".spark" / "tools.json").write_text(
            json.dumps({"p1264-tool": ENTRY, "roles": {"board-shell": "p1264-tool"}}))
        self.platform = firmware_platform.MicroPythonPlatform(self.project)

    def test_the_flash_and_the_look_use_the_tools_python(self):
        """Red: the port finder, the quiet connection and the console probe took the running Python."""
        self.path("bin")
        run = subprocess.run
        self.assertEqual(self.platform.make_port_finder(run).command, [self.python, "-m", "p1264_mod", "devs"])
        quiet = self.platform.make_connection(["p1264_mod"], "/dev/null", run, usb=board_connection.USB_SERIAL_JTAG)
        self.assertIsInstance(quiet, board_connection.QuietBoardConnection)
        self.assertEqual(quiet.command[:3], [self.python, "-c", board_connection.QUIET_MPREMOTE])
        self.assertEqual(self.platform.make_console_probe("/dev/null", run).python, [self.python])

    def test_the_three_say_one_sentence_for_one_missing_tool(self):
        """Red: each place made its own sentence, or one of them left out where spark looked."""
        self.path("pybin")
        with self.assertRaises(board_look.LookStopError) as looked:
            board_look.looker(self.platform)
        with self.assertRaises(tool_finder.ToolError) as deployed:
            self.platform.make_shell_command()
        row = next(row for row in tool_finder.status(self.project, self.project / "absent.json") if row[1] == "board-shell")
        self.assertEqual(row[0], "missing")
        self.assertEqual(str(looked.exception), row[2])
        self.assertEqual(str(deployed.exception), row[2])
        self.assertIn("Spark looked for the p1264_mod module in", row[2])

    def test_the_one_help_sentence_is_in_the_look_and_the_deploy(self):
        """Red: the two `--help` texts said it twice, in two wordings, or not at all."""
        said = firmware_platform.FINDING_THE_TOOLS
        self.assertEqual(said, "Spark finds mpremote and esptool in the Python that runs it. When that Python lacks one, spark "
                               "asks the Python of the one on your PATH. When neither has it, the stop says where spark looked.")
        self.assertIn(said, look_at_board.DETAILS)
        self.assertIn(said, deploy_image.DETAILS)


if __name__ == "__main__":
    unittest.main()
