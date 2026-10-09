"""
One temp folder per test process, removed when the process exits (P172).

One run of the suite on main c49a17e left 2,291 entries, 26 MB, in an empty temp folder, and the pre-push
hook runs the suite at every push: 254 `tempfile.mkdtemp()` calls in 28 test files, many in helpers
outside any test, a lock file per scratch store, a scratch store per process. Removing each where it
is made would be 254 edits, and the next test written would leak again. Instead every test module
imports this first: it makes ONE folder under whatever temp folder the process inherited, points
`tempfile` at it — and TMPDIR too, so every script a test starts writes there as well — and removes
it at exit. `tests/test_suite_temp.py` pins that every test module asks for it before anything else.

It is not named `test_*.py`, so the suite never loads it as tests; every way the suite is run imports
it under this one name — `discover -s tests` and `tools/mutate.py` (which runs from `tests/`) find it
on the path already, and `python3 -m unittest tests.test_x` through the `sys.path` line each test module has.
"""

import atexit
import os
import shutil
import tempfile

#: The folder this process's temp files go under; a script a test starts inherits it through TMPDIR.
ROOT = tempfile.mkdtemp(prefix="spark-tests-")
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
