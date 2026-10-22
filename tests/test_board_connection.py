"""P215 (#196), the council's step 1: BoardConnection is the one mpremote connection to a board, and it keeps mpremote's words."""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_connection  # noqa: E402

#: What mpremote 1.29.0 printed at the P215 bench when the board did not answer (stdout, then the end of stderr).
NO_RAW_REPL = ("b''\n", "Traceback (most recent call last):\n  File \"mpremote/transport_serial.py\", line 195, in "
               "enter_raw_repl\nmpremote.transport.TransportError: could not enter raw repl\n")


class Mpremote:
    """A fake subprocess.run for mpremote: answers `out`, or exits 1 with `stdout`/`stderr`, or raises `raises`."""

    def __init__(self, out="", fails=None, raises=None):
        self.out, self.fails, self.raises, self.ran = out, fails, raises, []

    def __call__(self, command, check=False, timeout=None, **kw):
        self.ran.append((command, timeout))
        if self.raises:
            raise self.raises
        if self.fails:
            raise subprocess.CalledProcessError(1, command, *self.fails)
        return subprocess.CompletedProcess(command, 0, self.out, "")


def connection(run):
    return board_connection.BoardConnection(["mpremote"], "/dev/ttyX", run, timeout_s=20)


class BoardConnectionTest(unittest.TestCase):
    def test_each_command_names_the_port(self):
        run = Mpremote("hi\n")
        self.assertEqual(connection(run).run_code("print('hi')"), "hi\n")
        self.assertEqual(run.ran[0], (["mpremote", "connect", "/dev/ttyX", "exec", "print('hi')"], 20))

    def test_a_board_that_does_not_answer_is_board_unreachable_with_mpremote_s_words(self):
        with self.assertRaises(board_connection.BoardUnreachableError) as said:
            connection(Mpremote(fails=NO_RAW_REPL)).run_code("pass")
        self.assertEqual(str(said.exception), "mpremote.transport.TransportError: could not enter raw repl")
        self.assertIn("b''", said.exception.output)

    def test_code_that_raises_on_the_board_is_the_firmware_stopping(self):
        board = ("ready\nTraceback (most recent call last):\n  File \"light.py\", line 9\nOSError: [Errno 19] ENODEV\n", "")
        with self.assertRaises(board_connection.BoardCodeError) as said:
            connection(Mpremote(fails=board)).run_code("import main")
        self.assertEqual(str(said.exception), "OSError: [Errno 19] ENODEV")
        self.assertTrue(said.exception.output.startswith("ready\n"))

    def test_mpremote_s_own_traceback_is_the_board_unreachable_never_the_firmware(self):
        dropped = ("", "Traceback (most recent call last):\n  File \"mpremote/main.py\"\nserial.serialutil.SerialException:"
                       " device reports readiness to read but returned no data\n")
        for step in (lambda c: c.run_code("pass"), lambda c: c.copy_to_board("/tmp/x", "x"), lambda c: c.read_file("x")):
            with self.assertRaises(board_connection.BoardUnreachableError) as said:
                step(connection(Mpremote(fails=dropped)))
            self.assertIn("SerialException", str(said.exception))

    def test_a_failure_with_no_traceback_is_the_board_unreachable_with_its_words(self):
        with self.assertRaises(board_connection.BoardUnreachableError) as said:
            connection(Mpremote(fails=("", "failed to access /dev/ttyX\n"))).run_code("pass")
        self.assertEqual(str(said.exception), "failed to access /dev/ttyX")

    def test_a_failure_that_prints_only_to_stdout_and_no_traceback_is_the_board_unreachable(self):
        with self.assertRaises(board_connection.BoardUnreachableError) as said:
            connection(Mpremote(fails=("b''\n", ""))).run_code("pass")
        self.assertEqual(str(said.exception), "b''")

    def test_a_copy_that_fails_with_a_board_traceback_is_still_unreachable(self):
        with self.assertRaises(board_connection.BoardUnreachableError):
            connection(Mpremote(fails=("Traceback (most recent call last):\nOSError: 28\n", ""))).copy_to_board("/tmp/x", "x")

    def test_a_run_that_is_still_going_when_the_time_is_up_gives_what_it_printed(self):
        going = subprocess.TimeoutExpired(["mpremote"], 20, output=b"ready\nLED on\n")
        self.assertEqual(connection(Mpremote(raises=going)).run_code("import main", keep_running_for=20), "ready\nLED on\n")

    def test_no_answer_in_time_is_board_unreachable(self):
        with self.assertRaises(board_connection.BoardUnreachableError) as said:
            connection(Mpremote(raises=subprocess.TimeoutExpired(["mpremote"], 20))).run_code("pass")
        self.assertEqual(str(said.exception), "no answer in 20 s")

    def test_a_reset_runs_mpremote_reset_on_the_port(self):
        run = Mpremote()
        connection(run).reset()
        self.assertEqual(run.ran, [(["mpremote", "connect", "/dev/ttyX", "reset"], 20)])

    def test_a_reset_that_fails_or_drops_the_port_is_board_unreachable(self):
        for run in (Mpremote(fails=NO_RAW_REPL), Mpremote(raises=subprocess.TimeoutExpired(["mpremote"], 20)),
                    Mpremote(raises=OSError("[Errno 6] Device not configured"))):
            with self.assertRaises(board_connection.BoardUnreachableError):
                connection(run).reset()

    def test_no_mpremote_is_board_unreachable(self):
        with self.assertRaises(board_connection.BoardUnreachableError):
            connection(Mpremote(raises=FileNotFoundError("mpremote"))).run_code("pass")

    def test_copy_and_cat_name_the_board_s_file(self):
        run = Mpremote("{}\n")
        connection(run).copy_to_board("/tmp/spark.json", "spark.json")
        self.assertEqual(connection(run).read_file("spark.json"), "{}\n")
        self.assertEqual([c[0][3:] for c in run.ran], [["fs", "cp", "/tmp/spark.json", ":spark.json"],
                                                       ["fs", "cat", ":spark.json"]])


if __name__ == "__main__":
    unittest.main()
