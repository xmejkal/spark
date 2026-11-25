"""P478 (#656) slice 2: the spinner under a wait's line. `NO_SPINNER` draws nothing, `TerminalSpinner` draws a frame and
the seconds after a second and erases them on `stop`, and `ThreadTicker` calls its tick from a thread it always joins."""

import contextlib
import io
import re
import sys
import threading
import time
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from fakes import FakeClock, FakeTicker, Stream  # noqa: E402
from spark.core.renderers import PlainPainter, RichPainter, import_rich, painter_for  # noqa: E402
from spark.core.spinner import NO_SPINNER, TerminalSpinner, ThreadTicker  # noqa: E402
from spark.core.text_style import TextStyle  # noqa: E402
from suite_runs import needs_rich  # noqa: E402

#: An SGR code, the only escape code that the colour adds.
SGR = re.compile(r"\x1b\[[0-9;]*m")
#: The style of a terminal, with the marks' symbols and without them.
SYMBOLS, NO_SYMBOLS = TextStyle(True, True, True), TextStyle(True, True, False)


class BrokenStream(Stream):
    """A terminal that was closed once: its first write raises OSError, and later ones are kept."""

    def __init__(self):
        super().__init__()
        self.broken = True

    def write(self, text):
        if self.broken:
            self.broken = False
            raise OSError("the terminal is gone")
        return super().write(text)


class SpinnerCase(unittest.TestCase):
    def spinner(self, painter=PlainPainter, style=SYMBOLS, stream=None, ticker=None):
        self.stream, self.clock = stream or Stream(tty=True), FakeClock()
        self.ticker = ticker or FakeTicker()
        return TerminalSpinner(self.stream, painter, style, self.clock, self.ticker)

    def tick(self, seconds=0.0):
        """The bytes of one tick after the clock moved on by `seconds`."""
        self.clock.advance(seconds=seconds)
        before = self.stream.getvalue()
        self.ticker.tick()
        return self.stream.getvalue()[len(before):]


class TheNoSpinnerTest(unittest.TestCase):
    """Test 3: the Null Object draws nothing."""

    def test_start_and_stop_write_nothing(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            NO_SPINNER.start()
            NO_SPINNER.stop()
        self.assertEqual((out.getvalue(), err.getvalue()), ("", ""))


class TheTerminalSpinnerTest(SpinnerCase):
    """Tests 4, 5, 7 and 9, and C2: the bytes of the row, the erase, the cursor and a stop that a Ctrl-C cut."""

    def test_nothing_before_a_second_then_the_frame_and_the_seconds_and_the_next_frame(self):
        spinner = self.spinner()
        spinner.start()
        self.assertEqual(self.tick(0.5), "")
        self.assertEqual(self.tick(5.5), "\r\x1b[2K\x1b[?25l  ⠋ 6 s")
        self.assertEqual(self.tick(0.1), "\r\x1b[2K  ⠙ 6 s")

    def test_stop_erases_a_drawn_row_and_shows_the_cursor_and_a_stop_with_none_writes_nothing(self):
        spinner = self.spinner()
        spinner.start()
        spinner.stop()
        self.assertEqual(self.stream.getvalue(), "")
        spinner.start()
        self.tick(6)
        before = self.stream.getvalue()
        spinner.stop()
        self.assertEqual(self.stream.getvalue()[len(before):], "\r\x1b[2K\x1b[?25h")

    def test_a_stream_that_cannot_encode_the_marks_gets_the_ascii_frames(self):
        spinner = self.spinner(style=NO_SYMBOLS)
        spinner.start()
        self.assertEqual((self.tick(2), self.tick(0.1)), ("\r\x1b[2K\x1b[?25l  | 2 s", "\r\x1b[2K  / 2 s"))

    def test_a_closed_stream_ends_the_drawing_with_no_exception(self):
        spinner = self.spinner(stream=BrokenStream())
        spinner.start()
        self.assertEqual(self.tick(2), "")  # the OSError is caught in the tick
        self.assertEqual(self.tick(1), "")  # and no tick draws again

    def test_a_start_while_a_row_is_open_stops_the_old_ticker_and_counts_from_zero(self):
        spinner = self.spinner()
        spinner.start()
        self.tick(6)
        stopped = self.ticker.stopped
        spinner.start()
        self.assertEqual((self.ticker.stopped, self.ticker.started), (stopped + 1, 2))
        self.assertEqual(self.tick(1)[-5:], "⠋ 1 s")

    def test_a_stop_that_a_ctrl_c_cut_stops_the_ticker_again_and_erases_only_then(self):
        # C2: the first stop is cut in the ticker's join, so the row stays; the next stop joins and erases
        spinner = self.spinner()
        spinner.start()
        self.tick(6)
        self.ticker.interrupt, stopped, before = True, self.ticker.stopped, self.stream.getvalue()
        with self.assertRaises(KeyboardInterrupt):
            spinner.stop()
        self.assertEqual(self.stream.getvalue(), before)
        spinner.stop()
        self.assertEqual((self.ticker.stopped - stopped, self.stream.getvalue()[len(before):]), (2, "\r\x1b[2K\x1b[?25h"))


class TheColourTest(SpinnerCase):
    """Test 6: the frame is cyan through rich, and the row without its codes is the plain row."""

    @needs_rich
    def test_the_frame_is_cyan_and_the_row_without_codes_is_the_plain_row(self):
        self.spinner(painter=painter_for(SYMBOLS, import_rich)).start()
        coloured = self.tick(6)
        self.assertIn("\x1b[36m⠋", coloured)
        self.assertEqual(SGR.sub("", coloured), "\r\x1b[2K\x1b[?25l  ⠋ 6 s")

    def test_a_rich_that_raises_gives_the_plain_row(self):
        def console(**settings):
            raise TypeError("__init__() got an unexpected keyword argument 'soft_wrap'")
        self.spinner(painter=RichPainter(types.SimpleNamespace(Console=console, Text=object))).start()
        self.assertEqual(self.tick(6), "\r\x1b[2K\x1b[?25l  ⠋ 6 s")


class TheThreadTickerTest(unittest.TestCase):
    """Tests 8 and 8b: a real thread, always joined, also after a stop that a Ctrl-C cut before its join."""

    def test_it_ticks_from_a_thread_and_stop_joins_it_and_a_second_stop_does_nothing(self):
        ticked, counted = threading.Event(), []

        def tick():
            counted.append(1)
            ticked.set()
        ticker = ThreadTicker()
        ticker.start(tick)
        thread = ticker.thread
        self.assertTrue(ticked.wait(1))
        ticker.stop()
        count = len(counted)
        time.sleep(0.05)
        self.assertEqual((thread.is_alive(), len(counted), ticker.thread), (False, count, None))
        ticker.stop()

    def test_a_stop_after_one_that_a_ctrl_c_cut_before_its_join_still_waits_for_the_tick(self):
        entered, release, ended = threading.Event(), threading.Event(), []

        def tick():
            entered.set()
            release.wait(1)
            ended.append(1)
        ticker = ThreadTicker()
        ticker.start(tick)
        thread = ticker.thread
        self.assertTrue(entered.wait(1))
        ticker.stopped.set()  # as a stop leaves it that a Ctrl-C cut before its join: the thread is still held
        timer = threading.Timer(0.05, release.set)
        timer.start()
        ticker.stop()
        self.assertEqual((ended, thread.is_alive()), ([1], False))
        timer.join()


if __name__ == "__main__":
    unittest.main()
