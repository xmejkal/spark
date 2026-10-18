"""P239 PR 2 (#238): the fakes of the deploy area's swappable parts, one per part of spark's core."""

import datetime
import os
import time


class FakeBoardConnection:
    """A fake BoardConnection: run_code and read_file give or raise each of `answers` in turn, and copy_to_board
    raises `copy_raises` or keeps each copy. reset raises `reset_raises` or counts the reset in `resets`.
    Raises IndexError when a test asks for more answers than it gave."""

    def __init__(self, *answers, copy_raises=None, reset_raises=None):
        self.answers, self.copy_raises, self.copied, self.ran = list(answers), copy_raises, [], []
        self.reset_raises, self.resets = reset_raises, 0

    def _next(self):
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def run_code(self, code, keep_running_for=None):
        self.ran.append((code, keep_running_for))
        return self._next()

    def read_file(self, remote):
        return self._next()

    def copy_to_board(self, local, remote):
        if self.copy_raises:
            raise self.copy_raises
        self.copied.append((local, remote))

    def reset(self):
        if self.reset_raises:
            raise self.reset_raises
        self.resets += 1


class FakeConsent:
    """A fake ConsentStrategy: answers `answer` and keeps each question. A test that must act while the question
    waits subclasses it and overrides `ask`."""

    #: Who said yes, as the store's record keeps it.
    who = "a test"

    def __init__(self, answer):
        self.answer, self.asked = answer, []

    def require_ready(self):
        """The fake can always ask."""

    def ask(self, question):
        self.asked.append(question)
        return self.answer


class FakeClock:
    """A fake clock: `sleep` moves `now` on at once and keeps each sleep."""

    def __init__(self, now=0.0):
        self.now, self.slept = now, []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.now += seconds


def pin_time_zone(case, zone="Europe/Prague"):
    """Run `case` in one time zone, so a time said in the machine's zone reads the same on every machine (P291)."""
    before = os.environ.get("TZ")
    os.environ["TZ"] = zone
    time.tzset()

    def restore():
        if before is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = before
        time.tzset()
    case.addCleanup(restore)


class FakeLocalClock:
    """A fake clock for board_grant: calling it gives `now` (a time with its zone), and `advance` moves it on."""

    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, **kw):
        """Move the clock on by a datetime.timedelta's keyword arguments, for example minutes=30."""
        self.now += datetime.timedelta(**kw)


class FakeConsoleProbe:
    """A fake ConsoleProbe: the console prints `printed`, and wait_for_reset answers `reset` after it calls
    `on_reset` (a test's way to make the board answer again), and the console read calls `on_console`. cure() calls
    `on_cure` and gives `cured`, a board_console.Cure. Keeps how often each was asked."""

    def __init__(self, printed="", reset=True, on_reset=None, on_console=None, cured=None, on_cure=None):
        self.printed, self.reset, self.on_reset, self.asked = printed, reset, on_reset, []
        self.on_console, self.cured, self.on_cure = on_console, cured, on_cure

    def console(self):
        """The board doctor's read: `printed`, read with the port's lock."""
        self.asked.append("console")
        from board_console import ConsoleReadResult  # scripts/ is on the path once a test imports spark
        return ConsoleReadResult("read", self.printed, None)

    def waits_in_download_mode(self):
        self.asked.append("console")
        if self.on_console:
            self.on_console()
        from download_mode import DOWNLOAD_MODE  # scripts/ is on the path once a test imports spark
        return DOWNLOAD_MODE in self.printed, self.printed

    def wait_for_reset(self):
        self.asked.append("reset")
        if self.on_reset:
            self.on_reset()
        return self.reset

    def cure(self):
        self.asked.append("cure")
        if self.on_cure:
            self.on_cure()
        return self.cured


class FakePartPictures:
    """Fake: stands in for part_pictures.PartPictures, giving every type the same marked square, so a test sees which
    parts of a drawing come from the pictures source and which do not."""

    def picture(self, wokwi_type):
        import part_pictures
        return part_pictures.Picture('<rect width="10" height="10" fill="#123456"/>', (0.0, 0.0, 10.0, 10.0),
                                     "fake picture of %s" % wokwi_type)


class FakeTscircuitExport:
    """Fake: stands in for tabbed_page.TscircuitExport, giving each form the result a test sets, or a small marked SVG,
    and keeping the circuit paths it was asked for."""

    def __init__(self, results=None):
        self.results = results or {}
        self.asked = []

    def export_svg(self, circuit_path, form):
        import tabbed_page
        self.asked.append((str(circuit_path), form))
        return self.results.get(form, tabbed_page.SvgExportResult(
            '<svg xmlns="http://www.w3.org/2000/svg"><title>fake %s</title></svg>' % form, None))
