"""
The project's own tests, counted (P1208): the tests in PROJECT/tests that the conversation wrote for the firmware, run with
CPython's unittest in a child of their own (`own_tests_child.py`). They run on this machine and are not the sim: no
`sim/`, no board, no token. A reader of one thing that may be absent (the rule of `outcomes`): it never raises, and its
Value says RECORDED, NONE_RECORDED (no tests/ folder) or NOT_CHECKED (it could not count, or no test ran or passed: an empty
tests/ or every test skipped, and says why).
"""

import json
from collections import namedtuple
from pathlib import Path

from spark.core.outcomes import NONE_RECORDED, NOT_CHECKED, RECORDED
from spark.firmware.isolated_python import IsolatedPython

TESTS_FOLDER = "tests"
CHILD = Path(__file__).resolve().parent / "own_tests_child.py"
#: How long the project's tests may run, in seconds. A constant, not a setting: the free checks always run (P1208). The
#: clock's 35 tests take 0.006 s.
OWN_TESTS_TIMEOUT_S = 60

# --- MVP ---
#: Value: the project's own tests counted. `state` is RECORDED, NONE_RECORDED or NOT_CHECKED. With RECORDED: `total` the
#: tests run, `failed` the id of each test that failed, raised or succeeded when it was expected to fail, `skipped` the
#: count of tests skipped, `passed` the rest, and `reasons` the last line of each failed test's traceback by its id. With
#: NONE_RECORDED or NOT_CHECKED the numbers are None, never 0, and NOT_CHECKED has a `why`.
OwnTests = namedtuple("OwnTests", "state passed total failed skipped why reasons", defaults=(None, None, None, None, None, None))


def not_checked(why):
    return OwnTests(NOT_CHECKED, why=why)


def count_of(stdout):
    """The child's count, the JSON object on the last line of STDOUT, or None when there is none or it has no shape of one."""
    last = stdout.strip().splitlines()[-1:]
    try:
        said = json.loads(last[0]) if last else None
    except ValueError:
        return None
    if not (isinstance(said, dict) and isinstance(said.get("total"), int) and isinstance(said.get("skipped"), int)
            and isinstance(said.get("failed"), list)
            and all(isinstance(each, dict) and isinstance(each.get("id"), str) and isinstance(each.get("line"), str)
                    for each in said["failed"])):
        return None
    return said


class UnittestReader:
    """Strategy: reads the project's own tests with unittest discovery of PROJECT/tests. A second runner (pytest) is a second
    Strategy with the same `read`, and none is written until a project needs it."""

    def __init__(self, timeout_s=OWN_TESTS_TIMEOUT_S):
        self.timeout_s = timeout_s

    def read(self, project, outside):
        """The OwnTests of PROJECT, its child started through `outside.run`. The reader takes the whole OutsideWorld, so a
        runner of another kind (a MicroPython host runner) can find its tool with `outside.find_tool`."""
        project = Path(project).resolve()
        if not (project / TESTS_FOLDER).is_dir():
            return OwnTests(NONE_RECORDED)
        done = IsolatedPython(outside.run).call(CHILD, [project, TESTS_FOLDER], project, self.timeout_s)
        if done.timed_out:
            return not_checked("the tests did not finish within %g s: a test loops or waits" % self.timeout_s)
        count = count_of(done.stdout)
        if count is None:
            return not_checked("the tests gave no count (the run exited with code %s)" % done.returncode)
        if count["total"] == 0:
            return not_checked("%s/ holds no test: nothing ran, so there is no count" % TESTS_FOLDER)
        if count["total"] <= count["skipped"]:
            return not_checked("every test in %s/ was skipped: nothing passed and nothing failed, so there is no count" % TESTS_FOLDER)
        failed = [each["id"] for each in count["failed"]]
        return OwnTests(RECORDED, max(count["total"] - len(failed) - count["skipped"], 0), count["total"], failed,
                        count["skipped"], reasons={each["id"]: each["line"] for each in count["failed"]})
# --- end MVP ---
