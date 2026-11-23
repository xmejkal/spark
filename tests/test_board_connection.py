"""P215 (#196), the council's step 1: BoardConnection is the one mpremote connection to a board, and it keeps mpremote's words."""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import board_connection  # noqa: E402

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


def quiet(run, port="/dev/ttyX"):
    return board_connection.QuietBoardConnection(["py", "-m", "mpremote"], ["py"], port, run, timeout_s=20)


class QuietBoardConnectionTest(unittest.TestCase):
    """P1007: on Espressif's USB-Serial/JTAG, mpremote runs through QUIET_MPREMOTE, and keeps its words."""

    def test_each_call_runs_mpremote_s_own_arguments_through_the_quiet_script(self):
        run = Mpremote("42\n")
        self.assertEqual(quiet(run).run_code("print(6*7)"), "42\n")
        self.assertEqual(run.ran[0][0], ["py", "-c", board_connection.QUIET_MPREMOTE, "2.5", "10",
                                         "connect", "/dev/ttyX", "exec", "print(6*7)"])

    def test_the_time_limit_holds_the_settle_and_a_vanished_port_s_wait(self):
        run = Mpremote("")
        quiet(run).read_file("pins.py")
        quiet(run).run_code("import main", keep_running_for=20)
        self.assertEqual([limit for _, limit in run.ran], [36.0, 36.0])

    def test_a_refused_raw_repl_and_a_board_traceback_split_as_mpremote_s(self):
        with self.assertRaises(board_connection.BoardUnreachableError) as refused:
            quiet(Mpremote(fails=NO_RAW_REPL)).run_code("pass")
        self.assertIn("could not enter raw repl", str(refused.exception))
        raised = ("Traceback (most recent call last):\nZeroDivisionError: divide by zero\n", "")
        with self.assertRaises(board_connection.BoardCodeError):
            quiet(Mpremote(fails=raised)).run_code("1/0")

    def test_the_output_until_the_time_limit_is_the_answer_of_code_left_running(self):
        going = subprocess.TimeoutExpired(["py"], 36, output=b"ready\r\n")
        self.assertEqual(quiet(Mpremote(raises=going)).run_code("import main", keep_running_for=20).strip(), "ready")

    def test_the_person_s_repl_stays_mpremote_s(self):
        self.assertEqual(quiet(Mpremote()).repl_command(), ["py", "-m", "mpremote", "connect", "/dev/ttyX", "repl"])

    def test_the_quiet_script_compiles(self):
        compile(board_connection.QUIET_MPREMOTE, "QUIET_MPREMOTE", "exec")


#: A fake pyserial whose first open vanishes during the settle; with GONE set, the port never comes back (P1007). With
#: KEEP set, the first open stays. HEARD is what the board prints in the settle (P1022).
FAKE_SERIAL = """import os
class SerialException(OSError):
    pass
class Serial:
    opens = 0
    def __init__(self):
        self.dtr = self.rts = True
    def open(self):
        Serial.opens += 1
        if Serial.opens > 1 and os.environ.get("GONE"):
            raise SerialException("gone")
        print("open dtr=%s rts=%s" % (self.dtr, self.rts))
    @property
    def in_waiting(self):
        if Serial.opens == 1 and not os.environ.get("KEEP"):
            raise OSError(6, "Device not configured")
        return len(os.environ.get("HEARD", ""))
    def read(self, size):
        return os.environ.get("HEARD", "").encode()[:size]
    def close(self):
        pass
"""
#: A fake mpremote that opens its port and enters the raw REPL, as mpremote's exec does.
FAKE_MAIN = """import serial, sys
from mpremote.transport_serial import SerialTransport
def main():
    transport = SerialTransport()
    transport.device_name, transport.serial = sys.argv[2], serial.Serial()
    transport.serial.open()
    transport.enter_raw_repl()
    print("entered")
    return 0
"""

#: A fake mpremote transport whose raw REPL, with REFUSE set, raises as mpremote's does when the board is silent (P1022).
FAKE_TRANSPORT = """import os
class SerialTransport:
    def enter_raw_repl(self):
        if os.environ.get("REFUSE"):
            raise RuntimeError("could not enter raw repl")
"""
#: The fake's last line of stderr on a refused raw REPL: the line mpremote's error message is read from.
REFUSED = "RuntimeError: could not enter raw repl"


class QuietScriptTest(unittest.TestCase):
    """P1007: QUIET_MPREMOTE itself, run against fake modules: DTR and RTS off, and one reopen of a vanished port."""

    def run_script(self, gone=False, **switches):
        import os
        import tempfile
        here = Path(tempfile.mkdtemp())
        (here / "mpremote").mkdir()
        (here / "mpremote" / "__init__.py").write_text("")
        (here / "mpremote" / "main.py").write_text(FAKE_MAIN)
        (here / "mpremote" / "transport_serial.py").write_text(FAKE_TRANSPORT)
        (here / "serial.py").write_text(FAKE_SERIAL)
        port = here / "port"
        port.write_text("")
        env = dict(os.environ, PYTHONPATH=str(here), **({"GONE": "1"} if gone else {}), **switches)
        return subprocess.run([sys.executable, "-c", board_connection.QUIET_MPREMOTE, "0", "0.1", "connect", str(port), "exec", "x"],
                              capture_output=True, text=True, env=env, timeout=30)

    def test_a_port_that_vanished_is_opened_again_with_dtr_and_rts_off(self):
        done = self.run_script(gone=False)
        self.assertEqual((done.returncode, done.stdout.split("\n")), (0, ["open dtr=False rts=False"] * 2 + ["entered", ""]))
        self.assertEqual(done.stderr, "")

    def test_a_port_that_does_not_come_back_is_mpremote_s_failed_to_access(self):
        done = self.run_script(gone=True)
        self.assertEqual(done.returncode, 1)
        self.assertTrue(done.stderr.startswith("failed to access "), done.stderr)

    def test_a_refused_raw_repl_keeps_what_the_settle_heard_on_stderr(self):
        done = self.run_script(KEEP="1", HEARD="entry 0x4086b910\r\nready\r\n", REFUSE="1")
        note = next((line for line in done.stderr.splitlines() if line.startswith("spark: ")), "")
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertTrue(note.startswith("spark: the 0 s settle heard "), done.stderr)
        self.assertIn("entry 0x4086b910", note)
        self.assertNotIn("vanished", note)
        self.assertEqual(done.stderr.splitlines()[-1], REFUSED)
        self.assertNotIn("spark: ", done.stdout)

    def test_the_note_keeps_only_the_last_400_bytes_of_a_read(self):
        done = self.run_script(KEEP="1", HEARD="boot head " + "x" * 400 + " ready tail", REFUSE="1")
        note = next((line for line in done.stderr.splitlines() if line.startswith("spark: ")), "")
        self.assertIn("ready tail", note)
        self.assertNotIn("boot head", note)

    def test_a_port_that_vanished_and_then_refused_says_it_came_back(self):
        done = self.run_script(REFUSE="1")
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertRegex(done.stderr, r"spark: the 0 s settle heard \(its port vanished and came back after [0-9.]+ s\)")
        self.assertEqual(done.stderr.splitlines()[-1], REFUSED)


if __name__ == "__main__":
    unittest.main()
