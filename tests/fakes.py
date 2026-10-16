"""P239 PR 2 (#238): the fakes of the deploy area's swappable parts, one per part of spark's core."""


class FakeBoardConnection:
    """A fake BoardConnection: run_code and read_file give or raise each of `answers` in turn, and copy_to_board
    raises `copy_raises` or keeps each copy.
    Raises IndexError when a test asks for more answers than it gave."""

    def __init__(self, *answers, copy_raises=None):
        self.answers, self.copy_raises, self.copied, self.ran = list(answers), copy_raises, [], []

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


class FakeConsent:
    """A fake ConsentStrategy: answers `answer` and keeps each question. A test that must act while the question
    waits subclasses it and overrides `ask`."""

    def __init__(self, answer):
        self.answer, self.asked = answer, []

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


class FakeConsoleProbe:
    """A fake ConsoleProbe: the console prints `printed`, and wait_for_reset answers `reset` after it calls
    `on_reset` (a test's way to make the board answer again), and the console read calls `on_console`. cure() calls
    `on_cure` and gives `cured`, a board_console.Cure. Keeps how often each was asked."""

    def __init__(self, printed="", reset=True, on_reset=None, on_console=None, cured=None, on_cure=None):
        self.printed, self.reset, self.on_reset, self.asked = printed, reset, on_reset, []
        self.on_console, self.cured, self.on_cure = on_console, cured, on_cure

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
