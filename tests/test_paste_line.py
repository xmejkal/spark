"""
P1286: the line a page offers (`renderers.copy_line`) runs as printed when a person pastes it into zsh or bash. The home
folder is a resolved temp folder with a space in its name, never the person's. Its scripts folder holds `look.py`, a
`/bin/sh` stub that prints `$0` and each argument, NUL apart, and writes nothing. No Python runs in the child, and no
board is needed. A missing shell is a skip with its reason, and the gate stops a story run that holds this module
without zsh or bash (`check_commit.shell_refusal`).

    python3 -m unittest tests.test_paste_line
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core.privacy import Privacy  # noqa: E402
from spark.core.renderers import copy_line  # noqa: E402
from spark.core.result import NextStep  # noqa: E402

#: The stub of look.py: its own path, then each argument, each ended by a NUL.
STUB = "#!/bin/sh\nprintf '%s\\0' \"$0\" \"$@\"\n"
#: The shells a person pastes into, and the variables that would make them read a file of the person's.
SHELLS = ("zsh", "bash")
STARTUP_VARIABLES = ("ZDOTDIR", "BASH_ENV", "ENV")


def snapshot(folder):
    """{relative path: (size, mtime_ns)} of every file and folder under `folder`."""
    return {str(path.relative_to(folder)): (path.lstat().st_size, path.lstat().st_mtime_ns) for path in folder.rglob("*")}


class ThePastedLineRunsTest(unittest.TestCase):
    """The deploy's look step as its line: pasted into each shell, it runs the stub with the whole paths, and adds,
    removes or changes no file under the home folder or the working folder."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.home = self.tmp / "h o"
        self.scripts = self.home / "spark" / "scripts"
        self.scripts.mkdir(parents=True)
        stub = self.scripts / "look.py"
        stub.write_text(STUB)
        stub.chmod(0o755)
        self.project = self.home / "my lamp"
        self.project.mkdir()
        self.cwd = self.tmp / "cwd"
        self.cwd.mkdir()
        self.step = NextStep("look", ["--project", str(self.project), "--no-simulation"], "why", None, False, True, None)

    def env(self):
        env = {name: value for name, value in os.environ.items() if name not in STARTUP_VARIABLES}
        return dict(env, HOME=str(self.home))

    def test_each_shell_runs_the_line_as_printed_and_writes_nothing(self):
        line = copy_line(self.step, self.home, Privacy.of(self.project, self.tmp / "store", self.home, ()), self.scripts)
        self.assertTrue(line and line.startswith('"$HOME"/'), line)
        for name in SHELLS:
            with self.subTest(shell=name):
                shell = shutil.which(name)
                if shell is None:
                    self.skipTest("%s is not installed, so the line cannot be pasted into it" % name)
                before = (snapshot(self.home), snapshot(self.cwd))
                ran = subprocess.run([shell, "-c", line], cwd=self.cwd, env=self.env(), capture_output=True, timeout=30)
                self.assertEqual(ran.returncode, 0, ran.stderr)
                self.assertEqual(ran.stdout.decode().split("\0")[:-1],
                                 [str(self.scripts / "look.py"), "--project", str(self.project), "--no-simulation"])
                self.assertEqual((snapshot(self.home), snapshot(self.cwd)), before)


if __name__ == "__main__":
    unittest.main()
