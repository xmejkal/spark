"""
One temp folder per test process, removed when the process exits (P172).

One run of the suite on main c49a17e left 2,291 entries, 26 MB, in an empty temp folder, and the pre-push
hook runs the suite at every push: 281 `tempfile.mkdtemp()` calls in 28 test files (an AST count at
c49a17e), many in helpers outside any test, a lock file per scratch store, a scratch store per process.
Removing each where it is made would be 281 edits, and the next test written would leak again. Instead
every test module imports this first: it removes the old folders a killed run left (P435), makes ONE folder under whatever temp folder the process
inherited, points `tempfile` at it — and TMPDIR too, so every script a test starts writes there as well —
and removes it at exit. `tests/test_suite_temp.py` pins that every test module has, after its
standard-library imports and before anything else, the two lines

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import suite_temp

It is not named `test_*.py`, so the suite never loads it as tests. Every way the suite is run imports it
under this one name: `discover -s tests` puts tests/ on the path itself; `tools/mutate.py` runs from
`tests/` when it names test modules and runs `discover -s tests` from the root when it does not; and
`python3 -m unittest tests.test_x` from the root finds it only through that `sys.path` line.
"""

import atexit
import os
import shutil
import sys
import tempfile
import time

#: The name every suite folder starts with; the sweep below removes only such folders.
SUITE_PREFIX = "spark-tests-"

# P435: a run that was killed never reached its `atexit`. The next run removes the old folders it left, in the temp
# folder this process inherited, before it makes its own. `scratch` is standard library only, as this module is.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import scratch  # noqa: E402

sys.path.pop(0)
scratch.remove_old_folders(tempfile.gettempdir(), SUITE_PREFIX, time.time())

#: The folder this process's temp files go under; a script a test starts inherits it through TMPDIR.
ROOT = tempfile.mkdtemp(prefix=SUITE_PREFIX)
_MADE, _MADE_BY = ROOT, os.getpid()


def remove(folder):
    """
    Remove `folder` — only when it is the one this module made, in the process that made it; True when it did.
    A forked child exits through here too, and must never take its parent's folder from under it.
    """
    if folder != _MADE or os.getpid() != _MADE_BY:
        return False
    shutil.rmtree(folder, ignore_errors=True)
    return True


tempfile.tempdir = ROOT
os.environ["TMPDIR"] = ROOT
atexit.register(remove, ROOT)
