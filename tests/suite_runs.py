"""
The suite's two runs (P425): the quick run on the push hook, the full run before a PR is ready.

A test that costs more than about 2 s, with a reason anyone can check, wears `@slow(reason)`. The reason names
what the test runs and its measured seconds with the date. `SPARK_SUITE=quick` skips every marked test, and
`tools/check_commit.py` sets it for its quick run; a plain `python3 -m unittest discover -s tests` runs all.
The skip's reason starts with SLOW_PREFIX, so the gate counts the slow skips apart from the real ones
(a missing tool, a missing program).
`needs_littlefs` skips with its own reason, not SLOW_PREFIX.
This module is not named `test_*.py`, so the suite never loads it as tests.
"""

import importlib.util
import os
import time
import unittest
from pathlib import Path

#: What every slow mark's skip reason starts with; the gate counts the skips that start with it, and no others.
SLOW_PREFIX = "slow: "

#: Whether this process is a quick run.
QUICK = os.environ.get("SPARK_SUITE") == "quick"


def slow(reason):
    """Mark a test method or class as slow: the quick run skips it, setUpClass included. The reason is required."""
    if not reason.strip():
        raise ValueError("a slow mark needs its reason: what the test runs and its measured seconds")
    return unittest.skipIf(QUICK, SLOW_PREFIX + reason)


#: A test that builds or checks a flash image needs the littlefs package (P452); data/tools.json holds how to install it.
needs_littlefs = unittest.skipUnless(importlib.util.find_spec("littlefs"), "the littlefs package is not installed: run /spark:setup")


def planted_folder(parent, name, age):
    """A folder `name` with a file in it under `parent`, last touched `age` seconds before now (P435)."""
    folder = Path(parent) / name
    folder.mkdir()
    (folder / "f.txt").write_text("x")
    when = time.time() - age
    os.utime(folder, (when, when))
    return folder
