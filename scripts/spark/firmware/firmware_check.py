"""
check-firmware as an Operation on the core (P1208, #1757): the free checks of a project's firmware in one call, with no sim/ and
no board. They are the import check (`import_probe.look`: each firmware module imported on this machine over the stand-ins)
and the project's own tests (`own_tests`: PROJECT/tests run with unittest). `check_firmware.py` is its CLI. It writes
nothing, so it blocks no deploy: the deploy reads the logs of sim/runs/ only.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, RUNS, Argument, Operation
from spark.core.outcomes import COULD_NOT_RUN, NONE_RECORDED, NOT_CHECKED, PROBLEMS, RECORDED
from spark.core.result import Finding, OperationResult
from spark.firmware import firmware_codes
from spark.firmware.import_probe import IMPORT_TIMEOUT_S, IMPORTED, look
from spark.firmware.own_tests import OWN_TESTS_TIMEOUT_S, TESTS_FOLDER, UnittestReader

# --- MVP ---
#: The notes and lines of the answer, one sentence each.
NO_TESTS_NOTE = "no tests/ folder: this project has no own tests"
IMPORTS_LINE, IMPORTS_NOT_CHECKED_LINE = "imports: %d of %d imported", "imports: not checked (no firmware/ folder)"
TESTS_LINE, SKIPPED_PART = "tests: %d of %d passed (%s/)", ", %d skipped"
NO_TESTS_LINE, TESTS_NOT_CHECKED_LINE = "tests: none (no %s/ folder)", "tests: not checked (%s)"
#: The subject of an import problem that names no module (`nothing_to_import`).
FIRMWARE_SUBJECT = "firmware"

#: What `--help` says after the arguments (P481).
DETAILS = """It imports each PROJECT/firmware/*.py and each package there (a folder holding __init__.py) except the boot files, main.py
and boot.py, on this machine and each in a process of its own, with spark's machine stand-in first on sys.path, and runs
the project's own tests: PROJECT/tests, with unittest, in a process of its own, %g s at most. The tests' code runs on this
machine too, in the project folder, and can write files there: spark writes nothing. Each import is cut off after %g s. It
needs no sim/, no board and no token.

An `imported` proves that the names exist and the module-level calls ran. It does not prove that their arguments are right (the
stand-ins take any), that a pin, a wire, a rate or a driver works, or that a device answers. A passing own test proves what the
test asserts of the firmware's code on this machine, never the wiring.""" % (OWN_TESTS_TIMEOUT_S, IMPORT_TIMEOUT_S)


class CheckFirmware(Operation):
    """
    Operation: the free checks of a project's firmware, the import check and the project's own tests, in one answer. Its data
    is `project`, `imports` ({"imported", "total"}, or {} when firmware/ is not there), `modules` (what `import_probe.look`
    gives: `module`, `status`, `detail`, and `code` for one not imported) and `tests` (the OwnTests: `state`, and `passed`,
    `total`, `failed` and `skipped` only when recorded). A module not imported and a failed own test are problems; a firmware/
    that is not there and a run of tests that gave no count are could-not-run, never ok; a project with no tests/ is a note.
    It reads files, runs children on this machine and writes none.
    """

    name = "check-firmware"
    summary = "Check the firmware for free: its imports and the project's own tests, with no sim/ and no board."
    details = DETAILS
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder with firmware/ and tests/ (default: here)"),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, RUNS)
    data_keys = ("project", "imports", "modules", "tests")

    def __init__(self, import_timeout_s=IMPORT_TIMEOUT_S, tests_timeout_s=OWN_TESTS_TIMEOUT_S, own_tests_reader=None):
        """The timeouts are constants of the firmware area, no setting; a test gives a shorter one. `own_tests_reader` is the
        Strategy that reads the own tests (`read(project, run)`): unittest's, until a second runner exists."""
        self.import_timeout_s = import_timeout_s
        self.reader = own_tests_reader or UnittestReader(tests_timeout_s)

    def run(self, project, *, outside):
        """The imports and the own tests of PROJECT, each child started through `outside.run`."""
        modules, import_problems, unchecked = look(project, self.import_timeout_s, outside.run)
        tests = self.reader.read(project, outside.run)
        findings = self.import_findings(modules, import_problems, unchecked) + self.own_test_findings(tests)
        data = {"project": str(project), "imports": self.imports_of(modules, unchecked), "modules": modules, "tests": self.tests_data(tests)}
        notes = [NO_TESTS_NOTE] if tests.state == NONE_RECORDED else None
        return OperationResult(data, findings, lines=self.lines_of(modules, unchecked, tests), notes=notes)

    @staticmethod
    def import_findings(modules, problems, unchecked):
        """A Finding for each import problem, named by its module when it has one, and one for each unchecked item."""
        not_imported = [entry["module"] for entry in modules if entry["status"] != IMPORTED]
        found = [Finding.of(PROBLEMS, not_imported[at] if at < len(not_imported) else FIRMWARE_SUBJECT, problem.code, str(problem),
                            firmware_codes.FIXES[problem.code]) for at, problem in enumerate(problems)]
        return found + [Finding.of(COULD_NOT_RUN, None, gap.code, str(gap), firmware_codes.FIXES[gap.code]) for gap in unchecked]

    @staticmethod
    def own_test_findings(tests):
        """A problem for each failed test, with the last line of its traceback, or one could-not-run when the tests gave no count."""
        if tests.state == NOT_CHECKED:
            return [Finding.of(COULD_NOT_RUN, None, firmware_codes.OWN_TESTS_NOT_RUN, tests.why,
                               firmware_codes.FIXES[firmware_codes.OWN_TESTS_NOT_RUN])]
        return [Finding.of(PROBLEMS, test_id, firmware_codes.OWN_TEST_FAILED, "%s failed: %s" % (test_id, tests.reasons[test_id]),
                           firmware_codes.FIXES[firmware_codes.OWN_TEST_FAILED]) for test_id in tests.failed or ()]

    @staticmethod
    def imports_of(modules, unchecked):
        """The import count, or {} when firmware/ was not there: a number nobody took is no number."""
        return {} if unchecked else {"imported": sum(entry["status"] == IMPORTED for entry in modules), "total": len(modules)}

    @staticmethod
    def tests_data(tests):
        """The own tests as JSON: the numbers only for a state that has them."""
        if tests.state != RECORDED:
            return {"state": tests.state}
        return {"state": tests.state, "passed": tests.passed, "total": tests.total, "failed": tests.failed, "skipped": tests.skipped}

    @staticmethod
    def lines_of(modules, unchecked, tests):
        """The text: a line per module, then the imports line and the tests line."""
        lines = ["%-9s %s%s" % (entry["status"], entry["module"], "  " + entry["detail"] if entry["detail"] else "") for entry in modules]
        lines.append(IMPORTS_NOT_CHECKED_LINE if unchecked else IMPORTS_LINE % (sum(entry["status"] == IMPORTED for entry in modules), len(modules)))
        if tests.state == NONE_RECORDED:
            return lines + [NO_TESTS_LINE % TESTS_FOLDER]
        if tests.state == NOT_CHECKED:
            return lines + [TESTS_NOT_CHECKED_LINE % tests.why]
        return lines + [TESTS_LINE % (tests.passed, tests.total, TESTS_FOLDER) + (SKIPPED_PART % tests.skipped if tests.skipped else "")]
# --- end MVP ---
