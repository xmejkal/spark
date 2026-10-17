"""P215 step 2 (#196): ReadyCheck reads the board on its own port, and a board it cannot reach is unknown, never judged."""

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_connection  # noqa: E402
import board_facts  # noqa: E402
import ready_check  # noqa: E402
from fakes import FakeBoardConnection  # noqa: E402

MAIN = {"/main.py": hashlib.sha256(b"print('ready')\n").hexdigest()}



class HashFilesTest(unittest.TestCase):
    def test_the_board_prints_file_then_the_hash_then_the_path(self):
        """P260: HASH_LINE names one word for the writer and the reader; this pins the word the board prints."""
        code = ready_check.HASH_FILES % ["main.py"]
        self.assertIn("print('file', binascii.hexlify(h.digest()).decode(), p)", code)
        self.assertIn("print('file', 'missing', p)", code)

class Unreachable:
    """mpremote with no board on the port: exit 1, nothing printed, as subprocess.run reports it. Keeps each command."""

    def __init__(self):
        self.ran = []

    def __call__(self, command, check=False, **kw):
        self.ran.append(command)
        if check:
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 1, "", "")


class ReadyCheckTest(unittest.TestCase):
    def test_a_board_that_cannot_be_reached_is_unknown_not_a_file_that_differs(self):
        verdict, _, _ = ready_check.ReadyCheck(board_connection.BoardConnection(["mpremote"], "/dev/ttyX", Unreachable())).check(MAIN)
        self.assertEqual(verdict, "ready unknown")

    def test_a_check_returns_a_ready_result_that_is_read_by_name(self):
        result = ready_check.ReadyCheck(FakeBoardConnection(board_connection.BoardCodeError("Traceback\n", 1))).check(MAIN)
        self.assertIsInstance(result, ready_check.ReadyResult)
        self.assertEqual((result.verdict, result.sentence, result.log),
                         ("ready unknown", "mpremote could not read the board's files: Traceback", "Traceback\n"))

    def test_a_passed_log_with_no_files_is_a_ready_result_too(self):
        result = ready_check.ReadyCheck(FakeBoardConnection()).check({})
        self.assertEqual((result.verdict, result.log), ("ready unknown", ""))

    def test_each_read_names_the_board_s_port(self):
        run = Unreachable()
        ready_check.ReadyCheck(board_connection.BoardConnection(["mpremote"], "/dev/ttyX", run)).check(MAIN)
        self.assertEqual(run.ran[0][:4], ["mpremote", "connect", "/dev/ttyX", "exec"])


class WhatTheBoardSaysTest(unittest.TestCase):
    def test_hash_code_that_raises_on_the_board_is_unknown_with_its_output(self):
        raised = board_connection.BoardCodeError("Traceback\nImportError: hashlib\n", 1)
        verdict, _, log = board_ready_check(FakeBoardConnection(raised))
        self.assertEqual((verdict, log), ("ready unknown", "Traceback\nImportError: hashlib\n"))

    def test_a_board_gone_after_the_hashes_is_unknown_and_keeps_both_outputs(self):
        hashes = "file %s /main.py\n" % MAIN["/main.py"]
        verdict, _, log = board_ready_check(FakeBoardConnection(hashes, board_connection.BoardUnreachableError("could not enter raw repl", "x")))
        self.assertEqual((verdict, log), ("ready unknown", hashes + "x"))

    def test_a_facts_copy_that_raises_on_the_board_is_said_not_raised(self):
        facts = board_facts.FactsFile(FakeBoardConnection(copy_raises=board_connection.BoardCodeError("Traceback\nOSError: 28\n", 1)))
        self.assertEqual(facts.write({"a": 1}), "mpremote could not copy it: OSError: 28")


def board_ready_check(connection):
    return ready_check.ReadyCheck(connection).check(MAIN)


if __name__ == "__main__":
    unittest.main()
