"""
The suite's two runs (P425): the quick run on the push hook, the full run before a PR is ready.

A test that costs more than about 2 s, with a reason anyone can check, wears `@slow(reason)`. The reason names
what the test runs and its measured seconds with the date. `SPARK_SUITE=quick` skips every marked test, and
`tools/check_commit.py` sets it for its quick run; a plain `python3 -m unittest discover -s tests` runs all.
The skip's reason starts with SLOW_PREFIX, so the gate counts the slow skips apart from the real ones
(a missing tool, a missing program). It is not named `test_*.py`, so the suite never loads it as tests.
"""

import os
import unittest

#: What every slow mark's skip reason starts with; the gate counts the skips that start with it, and no others.
SLOW_PREFIX = "slow: "

#: Whether this process is a quick run.
QUICK = os.environ.get("SPARK_SUITE") == "quick"


def slow(reason):
    """Mark a test method or class as slow: the quick run skips it, setUpClass included. The reason is required."""
    if not reason.strip():
        raise ValueError("a slow mark needs its reason: what the test runs and its measured seconds")
    return unittest.skipIf(QUICK, SLOW_PREFIX + reason)
