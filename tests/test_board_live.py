"""P247 (#267): the live try checks the grant and the pins before it sends anything, and resets after any code that got in."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_grant  # noqa: E402
import board_live  # noqa: E402
from board_connection import BoardCodeError, BoardTimeoutError, BoardUnreachableError  # noqa: E402
from board_console import Cure  # noqa: E402
from fakes import FakeBoardConnection, FakeConsoleProbe  # noqa: E402

#: The XIAO ESP32-C6's record, with its usb and flash pins (P254).
C6 = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
PORT = "/dev/cu.usbmodem1101"
REFUSED = BoardUnreachableError("mpremote.transport.TransportError: could not enter raw repl")
RESTART = Cure("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n", None, True, True)


class FakeGrants:
    """A fake GrantService: answers `result` and keeps each port and script it checked."""

    def __init__(self, result):
        self.result, self.checked = result, []

    def check(self, port=None, script="grant.py"):
        self.checked.append((port, script))
        return self.result


GRANTED = board_grant.GrantCheckResult(True, None, None)
EXPIRED = board_grant.GrantCheckResult(False, None, board_grant.WHY_EXPIRED)


class UntouchableBoard(FakeBoardConnection):
    """A connection that fails the test when anything reaches the board."""

    def run_code(self, code, keep_running_for=None):
        raise AssertionError("code reached the board: %s" % code)

    def reset(self):
        raise AssertionError("the board was reset")


def live(code, *answers, grants=None, board=C6, probe=None, reset_raises=None, connection=None):
    """(LiveTryResult, the connection, the grants) of one live try with fakes."""
    grants = grants or FakeGrants(GRANTED)
    connection = connection or FakeBoardConnection(*answers, reset_raises=reset_raises)
    result = board_live.LiveTryService(grants, connection, probe or FakeConsoleProbe(cured=RESTART), board).run(code, PORT)
    return result, connection, grants


class RefusalTest(unittest.TestCase):
    def test_no_grant_refuses_with_the_grant_s_code_and_sends_nothing(self):
        result, _, grants = live("print(1)", grants=FakeGrants(EXPIRED), connection=UntouchableBoard())
        self.assertEqual((result.answer, result.grant_why, result.reset), (board_live.REFUSED_NO_GRANT, "expired", None))
        self.assertEqual(result.why, board_grant.MESSAGE_FOR[board_grant.WHY_EXPIRED])
        self.assertEqual(grants.checked, [(PORT, "live.py")])
        self.assertEqual(board_live.exit_code(result), 1)

    def test_a_restricted_pin_is_refused_and_sends_nothing(self):
        result, _, _ = live("from machine import Pin\nPin(12, Pin.OUT)", connection=UntouchableBoard())
        self.assertEqual(result.answer, board_live.REFUSED_PIN)
        self.assertIn("GPIO12", result.why)
        self.assertEqual(board_live.exit_code(result), 1)

    def test_code_that_does_not_parse_is_refused_and_sends_nothing(self):
        result, _, _ = live("print(", connection=UntouchableBoard())
        self.assertEqual((result.answer, board_live.exit_code(result)), (board_live.REFUSED_NO_PARSE, 1))

    def test_the_grant_is_checked_before_the_pins(self):
        result, _, _ = live("Pin(12)", grants=FakeGrants(EXPIRED), connection=UntouchableBoard())
        self.assertEqual(result.answer, board_live.REFUSED_NO_GRANT)

    def test_a_broken_record_raises_and_sends_nothing(self):
        broken = dict(C6, pin_roles={"usb": {"gpio": "12", "note": "x"}})
        with self.assertRaises(ValueError):
            live("print(1)", board=broken, connection=UntouchableBoard())


class RunTest(unittest.TestCase):
    def test_print_1_runs_on_the_c6_and_the_board_is_reset(self):
        result, connection, _ = live("print(1)", "1\n")
        self.assertEqual((result.answer, result.why, result.output, result.reset),
                         (board_live.RAN, None, "1\n", board_live.RESET_DONE))
        self.assertEqual((connection.ran, connection.resets), ([("print(1)", None)], 1))
        self.assertEqual(board_live.exit_code(result), 0)

    def test_an_empty_answer_still_counts_as_ran(self):
        result, _, _ = live("x = 1", "")
        self.assertEqual(result.answer, board_live.RAN)

    def test_code_that_raised_is_reset_and_exits_1(self):
        result, connection, _ = live("x", BoardCodeError("Traceback\nNameError: name 'x' isn't defined\n", 1))
        self.assertEqual((result.answer, connection.resets), (board_live.RAISED, 1))
        self.assertIn("NameError", result.why)
        self.assertEqual(board_live.exit_code(result), 1)

    def test_code_that_never_ends_is_not_reached_but_still_reset(self):
        result, connection, _ = live("while True: pass", BoardTimeoutError("no answer in 20 s"))
        self.assertEqual((result.answer, connection.resets), (board_live.NOT_REACHED, 1))
        self.assertEqual(board_live.exit_code(result), 2)

    def test_a_board_that_never_let_mpremote_in_is_not_reset_and_names_both_causes(self):
        connection = FakeBoardConnection(REFUSED, REFUSED, reset_raises=AssertionError("the board was reset"))
        result, _, _ = live("print(1)", connection=connection)
        self.assertEqual((result.answer, result.reset, result.cure), (board_live.NOT_REACHED, None, RESTART))
        self.assertIn("USB output", result.why)
        self.assertIn("does not read its console", result.why)
        self.assertEqual(board_live.exit_code(result), 2)

    def test_a_busy_port_is_not_reached_with_mpremote_s_words_and_no_reset(self):
        busy = BoardUnreachableError("failed to access /dev/cu.usbmodem1101 (it may be in use by another program)")
        result, connection, _ = live("print(1)", busy)
        self.assertEqual((result.answer, result.why, connection.resets), (board_live.NOT_REACHED, str(busy), 0))

    def test_a_failed_reset_after_a_clean_run_exits_2_and_says_the_firmware_may_be_stopped(self):
        result, _, _ = live("print(1)", "1\n", reset_raises=BoardUnreachableError("[Errno 6] Device not configured"))
        self.assertEqual((result.answer, result.reset), (board_live.RAN, board_live.RESET_FAILED))
        self.assertIn("the firmware may be stopped", result.why)
        self.assertIn("Device not configured", result.why)
        self.assertEqual(board_live.exit_code(result), 2)


class PinFactsTest(unittest.TestCase):
    def test_the_gpio_numbers_in_the_code_are_listed_and_over_claim(self):
        result, _, _ = live("from machine import Pin\nPin(15, Pin.OUT).value(0)\nprint(1)", "1\n")
        self.assertEqual(result.gpio_numbers_in_code, [0, 1, 15])
        self.assertTrue(result.pins_checked)

    def test_a_record_with_no_restricted_pin_says_the_pins_were_not_checked(self):
        bare = dict(C6, pin_roles={})
        result, _, _ = live("print(12)", "12\n", board=bare)
        self.assertEqual((result.answer, result.pins_checked), (board_live.RAN, False))


if __name__ == "__main__":
    unittest.main()
