"""
check-firmware as an Operation on the core (P1208, #1757): the free checks of a project's firmware in one call, with no sim/ and
no board. They are the import check (`import_probe.look`: each firmware module imported on this machine over the stand-ins)
and the project's own tests (`own_tests`: PROJECT/tests run with unittest). `check_firmware.py` is its CLI. It keeps its
answer in one file, the check record `.spark/check-firmware.json` (P1209, `records/check_record`), which `flow.py show` and
the page read. No gate reads it, so it blocks no deploy: the deploy reads the logs of sim/runs/ only.
"""

from pathlib import Path

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, RUNS, WRITES, Operation
from spark.core.outcomes import COULD_NOT_RUN, NONE_RECORDED, NOT_CHECKED, PROBLEMS, RECORDED
from spark.core.result import Finding, OperationResult
from spark.core.zone_time import stamp
from spark.firmware import firmware_codes
from spark.firmware.import_probe import IMPORT_TIMEOUT_S, IMPORTED, look
from spark.firmware.own_tests import OWN_TESTS_TIMEOUT_S, TESTS_FOLDER, UnittestReader
from spark.firmware.project_secrets import FIRMWARE_FOLDER, is_secret_path
from spark.records.check_record import CheckRecordStore

# --- MVP ---
#: The notes and lines of the answer, one sentence each.
NO_TESTS_NOTE = "no tests/ folder: this project has no own tests"
#: What a run that could not keep its check record says, as a note and a line, with the class of what failed (P1209).
NOT_KEPT_SENTENCE = "did not keep the check record: %s"
#: The folders the free checks read, which the check record hashes and its older line names, and the keys of `data` it keeps.
INPUTS, KEPT_KEYS = (FIRMWARE_FOLDER + "/", TESTS_FOLDER + "/"), ("imports", "tests")
IMPORTS_LINE, IMPORTS_NOT_CHECKED_LINE = "imports: %d of %d imported", "imports: not checked (no firmware/ folder)"
TESTS_LINE, SKIPPED_PART = "tests: %d of %d passed (%s/)", ", %d skipped"
NO_TESTS_LINE, TESTS_NOT_CHECKED_LINE = "tests: none (no %s/ folder)", "tests: not checked (%s)"
#: The subject of an import problem that names no module (`nothing_to_import`).
FIRMWARE_SUBJECT = "firmware"

#: What `--help` says after the arguments (P481).
DETAILS = """It needs no sim/, no board and no token. It writes one file, .spark/check-firmware.json, the check record that
`flow.py show` and the page read: the status, the counts, the two result lines, the time and the sha256 of each file
under firmware/ and tests/ (the secrets files left out), kept only when firmware/ is there. No gate reads it, so it
blocks no deploy. When the project has a page.html, it writes that page again.

The import check imports each PROJECT/firmware/*.py and each package there (a folder holding __init__.py) except the boot
files, main.py and boot.py. PROJECT defaults to `.`. Each import is a process of its own, with spark's machine stand-in first
on sys.path, then firmware/ and firmware/lib, where MicroPython looks for drivers. The stand-ins are in
scripts/spark/firmware/stand_in/: `machine` (a Pin that remembers its level, a PWM that keeps its last frequency and duty, and an
ADC, SPI, SoftSPI, I2C, SoftI2C and I2S that keep their arguments and return fixed values), `micropython` and `framebuf`. A
driver that ships its own `framebuf.py` or `micropython.py` in firmware/ or firmware/lib gets its own, because those two stand-ins
come last on sys.path. Per module the answer is one of:
  - imported;
  - raised: the exception's last line, which names the stand-in and the first name it lacks, for example UART;
  - timed out: it did not return within %g s. Something at module level loops or waits.
    Put it in a function that main.py calls.

An `imported` proves that the names exist and the module-level calls ran. It does not prove that their arguments are
right (the stand-ins take any), that a pin, a wire, a rate or a driver works, or that a device answers: a bus finds no
device, so a module-level `assert 0x3C in i2c.scan()` fails here. Keep such a check in a function that main.py calls.
A name a stand-in lacks is an AttributeError, so a driver's `hasattr(machine, "X")` probe is False. `from machine import X`
is an ImportError with the stand-in file and the action, because the child gives the stand-in's words back (P443).
A driver that sleeps in its constructor imports, because the child gives `time` MicroPython's sleep_ms, sleep_us, ticks_ms,
ticks_us, ticks_add and ticks_diff with fixed values (P443, see import_child.py). A sleep never waits, and ticks_ms() is
always 0, so a driver's wait loop on it times out here.

The boot files are left unrun on purpose: main.py starts the loop, so a two-line main.py over an importable module is
the shape that can be tested. When firmware/ holds nothing to import but the boot files and pins.py, that is a
problem, not a pass: the firmware cannot be imported without running main.py, so move the code out of main.py into a
module that main.py calls. No firmware/ folder is could-not-run.

The own tests are PROJECT/tests, run with unittest in a process of their own (`own_tests_child.py`), %g s at most.
The tests' code runs on this machine too, in the project folder, and can write files there: spark writes only its record. The
answer's `data.tests` holds `passed` of `total` and the ids of the tests that failed. A failed or raising test is a problem
(`own_test_failed`). A run that timed out, gave no count or ran no test is could-not-run (`own_tests_not_run`), never ok. No
tests/ folder is a note and `data.tests.state` `none-recorded`. A test that passes proves what it asserts, on this machine,
and never the wiring.""" % (IMPORT_TIMEOUT_S, OWN_TESTS_TIMEOUT_S)


class CheckFirmware(Operation):
    """
    Operation: the free checks of a project's firmware, the import check and the project's own tests, in one answer. Its data
    is `project`, `imports` ({"imported", "total"}, or {"state": "not-checked"} when firmware/ is not there), `modules` (what `import_probe.look`
    gives: `module`, `status`, `detail`, and `code` for one not imported) and `tests` (the OwnTests: `state`, and `passed`,
    `total`, `failed` and `skipped` only when recorded). A module not imported and a failed own test are problems; a firmware/
    that is not there and a run of tests that gave no count are could-not-run, never ok; a project with no tests/ is a note.
    It reads files, runs children on this machine and writes one file, the check record (P1209): `data.written` says
    whether this run wrote it, and a write that failed is a note and a line, never a finding.
    """

    name = "check-firmware"
    summary = "Check the firmware for free: its imports and the project's own tests, with no sim/ and no board."
    details = DETAILS
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder with firmware/ and tests/ (default: here)"),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, RUNS, WRITES)
    data_keys = ("project", "imports", "modules", "tests", "written")

    def __init__(self, import_timeout_s=IMPORT_TIMEOUT_S, tests_timeout_s=None, own_tests_reader=None):
        """The timeouts are constants of the firmware area, no setting; a test gives a shorter one. `own_tests_reader` is the
        Strategy that reads the own tests (`read(project, outside)`): unittest's, until a second runner exists. The tests'
        timeout belongs to the reader: `tests_timeout_s` builds the default UnittestReader with it, and a reader given
        together with it is refused (ValueError), never silently left without it."""
        if own_tests_reader is not None and tests_timeout_s is not None:
            raise ValueError("tests_timeout_s is the default reader's: give it to your own_tests_reader instead")
        self.import_timeout_s = import_timeout_s
        self.reader = own_tests_reader or UnittestReader(OWN_TESTS_TIMEOUT_S if tests_timeout_s is None else tests_timeout_s)

    def run(self, project, *, outside):
        """The imports and the own tests of PROJECT, each child started through `outside.run`."""
        modules, import_problems, unchecked = look(project, self.import_timeout_s, outside.run)
        tests = self.reader.read(project, outside)
        findings = self.import_findings(modules, import_problems, unchecked) + self.own_test_findings(tests)
        imports = self.imports_of(modules, unchecked)
        data = {"project": str(project), "imports": imports, "modules": modules, "tests": self.tests_data(tests)}
        notes = [{"subject": TESTS_FOLDER, "sentence": NO_TESTS_NOTE}] if tests.state == NONE_RECORDED else None
        kept_lines = self.result_lines(imports, tests)
        result = OperationResult(data, findings, lines=self.module_lines(modules) + kept_lines, notes=notes)
        return self.keep(project, result, kept_lines, outside)

    def keep(self, project, result, kept_lines, outside):
        """`result` with `data.written`, after its check record is saved (P1209): its status, the data of KEPT_KEYS and
        `kept_lines`, at `outside.clock`'s time. With no firmware/ nothing is kept. A write that fails adds its sentence
        as a note and a line, and the result stands."""
        if result.data["imports"].get("state") == NOT_CHECKED:
            return result._replace(data=dict(result.data, written=False))
        answer = {"status": result.status(), "data": {key: result.data[key] for key in KEPT_KEYS}, "lines": kept_lines}
        records = CheckRecordStore(project, self.name, leave_out=is_secret_path)
        try:
            records.save(INPUTS, stamp(outside.clock.now()), answer)
        except OSError as failed:
            sentence = NOT_KEPT_SENTENCE % type(failed).__name__
            return result._replace(data=dict(result.data, written=False), lines=list(result.lines) + [sentence],
                                   notes=list(result.notes or []) + [{"subject": records.path.relative_to(project).as_posix(), "sentence": sentence}])
        return result._replace(data=dict(result.data, written=True))

    def written_project(self, values):
        """The project whose check record a run writes, so the core writes its page again (P1035)."""
        return Path(values["project"])

    @staticmethod
    def import_findings(modules, problems, unchecked):
        """A Finding for each module that did not import, built from its entry (`module`, `code`, `detail`), one for the problem
        that names no module (nothing to import), and one for each unchecked item."""
        found = [Finding.of(PROBLEMS, entry["module"], entry["code"], "%s %s: %s" % (entry["module"], entry["status"], entry["detail"]))
                 for entry in modules if entry["status"] != IMPORTED]
        found += [Finding.of(PROBLEMS, FIRMWARE_SUBJECT, problem.code, str(problem)) for problem in problems
                  if problem.code == firmware_codes.NOTHING_TO_IMPORT]
        return found + [Finding.of(COULD_NOT_RUN, None, gap.code, str(gap)) for gap in unchecked]

    @staticmethod
    def own_test_findings(tests):
        """A problem for each failed test, with the last line of its traceback, or one could-not-run when the tests gave no count."""
        if tests.state == NOT_CHECKED:
            return [Finding.of(COULD_NOT_RUN, None, firmware_codes.OWN_TESTS_NOT_RUN, tests.why)]
        return [Finding.of(PROBLEMS, test_id, firmware_codes.OWN_TEST_FAILED, "%s failed: %s" % (test_id, tests.reasons[test_id]))
                for test_id in tests.failed or ()]

    @staticmethod
    def imports_of(modules, unchecked):
        """The import count, or {"state": "not-checked"} when firmware/ was not there, as `tests` says it: a number nobody took
        is no number."""
        return {"state": NOT_CHECKED} if unchecked else {"imported": sum(entry["status"] == IMPORTED for entry in modules), "total": len(modules)}

    @staticmethod
    def tests_data(tests):
        """The own tests as JSON: the numbers only for a state that has them."""
        if tests.state != RECORDED:
            return {"state": tests.state}
        return {"state": tests.state, "passed": tests.passed, "total": tests.total, "failed": tests.failed, "skipped": tests.skipped}

    @staticmethod
    def module_lines(modules):
        """The text's first lines: one per module, its status, its name and its detail."""
        return ["%-9s %s%s" % (entry["status"], entry["module"], "  " + entry["detail"] if entry["detail"] else "") for entry in modules]

    @staticmethod
    def result_lines(imports, tests):
        """The text's last two lines, which the check record keeps too (P1209): the imports line (`imports_of`'s count) and
        the tests line."""
        lines = [IMPORTS_NOT_CHECKED_LINE if imports.get("state") == NOT_CHECKED else IMPORTS_LINE % (imports["imported"], imports["total"])]
        if tests.state == NONE_RECORDED:
            return lines + [NO_TESTS_LINE % TESTS_FOLDER]
        if tests.state == NOT_CHECKED:
            return lines + [TESTS_NOT_CHECKED_LINE % tests.why]
        return lines + [TESTS_LINE % (tests.passed, tests.total, TESTS_FOLDER) + (SKIPPED_PART % tests.skipped if tests.skipped else "")]
# --- end MVP ---
