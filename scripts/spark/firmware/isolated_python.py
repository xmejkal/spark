"""
One isolated Python child, started once for the firmware area (P1208): the import check starts one per module and the
project's own tests one for the whole run. Both reach it through the `run` of an OutsideWorld, so a test gives a Fake.
"""

import subprocess
import sys
from collections import namedtuple

# --- MVP ---
#: Value: what one child did. `timed_out` is True when it did not return in time, and then `returncode` is None and the
#: streams are empty; else `returncode`, `stdout` and `stderr` are the child's.
ChildRun = namedtuple("ChildRun", "timed_out returncode stdout stderr")


class IsolatedPython:
    """
    Adapter: starts `python3 -I -B SCRIPT ARGS...` through `run`, which runs a program as `subprocess.run` does
    (`OutsideWorld.run`), and says how it ended. -B: no __pycache__ in the person's folder. -I: the child's own folder and
    the current folder stay off sys.path, so a project cannot import the child's file. The child has no stdin to read.
    """

    def __init__(self, run):
        self._run = run

    def call(self, script, args, cwd, timeout_s):
        """The ChildRun of SCRIPT with ARGS inside the folder CWD, cut off after TIMEOUT_S seconds."""
        command = [sys.executable, "-I", "-B", str(script)] + [str(argument) for argument in args]
        try:
            done = self._run(command, cwd=str(cwd), capture_output=True, text=True, errors="replace",
                             stdin=subprocess.DEVNULL, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return ChildRun(True, None, "", "")
        return ChildRun(False, done.returncode, done.stdout, done.stderr)
# --- end MVP ---
