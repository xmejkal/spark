#!/usr/bin/env python3
"""
The child process of check_firmware.py's own-tests run (P1208): it runs a project's tests/ with unittest and prints the
count as one line of JSON, last on stdout.

    python3 -I -B own_tests_child.py PROJECT TESTS_FOLDER

PROJECT is the folder that holds the tests, TESTS_FOLDER the name of it (own_tests.py writes the name once, and passes it). The child puts it first on sys.path, so a test imports from firmware/ as the project
wrote it, and discovers the tests: a tests/ with an __init__.py is a package (the start folder is `tests`, the top folder
PROJECT, so relative and package imports work), else tests/ is the top folder, as `python3 -m unittest discover -s tests`
does. The tests' prints go to stderr, because the count is the one thing on stdout: the child points sys.stdout at stderr
while they run, then writes a newline and the line. check_firmware.py runs it with -I, so its own folder and the current
folder stay off sys.path, and it imports nothing of spark (the twin of import_child.py).

The line: `total` (the tests run, a failing test once), `failed` (a list of {"id", "line"}: the id of each test that failed,
raised or succeeded when it was expected to fail, and the last line of its traceback) and `skipped` (a test with three skipped
subtests once). Right after the count the child ends with os._exit, so nothing a test registered with atexit runs after it.
"""

import json
import os
import sys
import unittest
from pathlib import Path


def discover(project, folder):
    """The TestSuite of PROJECT/FOLDER: a package from the project's folder, else a folder of modules."""
    tests = project / folder
    loader = unittest.defaultTestLoader
    if (tests / "__init__.py").is_file():
        return loader.discover(str(tests), top_level_dir=str(project))
    return loader.discover(str(tests))


def last_line(trace):
    """The last non-empty line of a traceback, the exception's own line."""
    lines = [line for line in trace.strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""


def failures_of(result):
    """The failed tests of RESULT as [{"id", "line"}], each test once, in the order they failed: a failure, an error, and an
    unexpected success (its line says so). A test with three failing subtests is one."""
    seen, failed = set(), []
    for test, trace in list(result.failures) + list(result.errors) + [(test, "unexpected success") for test in result.unexpectedSuccesses]:
        test = getattr(test, "test_case", test)
        if test.id() not in seen:
            seen.add(test.id())
            failed.append({"id": test.id(), "line": last_line(trace)})
    return failed


def skipped_of(result):
    """The count of the tests of RESULT that were skipped, each test once: a test with three skipped subtests is one."""
    return len({getattr(test, "test_case", test).id() for test, _ in result.skipped})


def count_tests(project, folder):
    """The dict of the run of PROJECT/FOLDER: {"total", "failed", "skipped"}. A test that raised outside any test (setUpClass)
    has no count of its own, so it is added to the total."""
    result = unittest.TextTestRunner(verbosity=0).run(discover(project, folder))  # the runner's stream is stderr
    failed = failures_of(result)
    outside = sum(1 for test, _ in result.errors + result.failures if not isinstance(getattr(test, "test_case", test), unittest.TestCase))
    return {"total": result.testsRun + outside, "failed": failed, "skipped": skipped_of(result)}


class CountRenderer:
    """Renderer: says the count as the one line last on stdout, and keeps what the tests print off it."""

    def quietly(self, work):
        """What WORK returns, called with sys.stdout pointed at stderr, so no print of a test lands beside the count."""
        real, sys.stdout = sys.stdout, sys.stderr
        try:
            return work()
        finally:
            sys.stdout = real

    def render(self, count):
        """A newline, then COUNT as one line of JSON: a test's own text with no newline cannot join the line. Then the child
        ends at once: what a test registered with atexit cannot write another line after the count."""
        sys.stdout.write("\n" + json.dumps(count) + "\n")
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)


def say_count(argv):
    project, folder = Path(argv[0]).resolve(), argv[1]
    sys.path.insert(0, str(project))
    renderer = CountRenderer()
    renderer.render(renderer.quietly(lambda: count_tests(project, folder)))


if __name__ == "__main__":
    say_count(sys.argv[1:])
