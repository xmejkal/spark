"""P239 PR 2 (#238): the fakes that the deploy area's tests share, one per swappable part of spark's core."""


class FakeBoardConnection:
    """A fake BoardConnection: run_code and read_file give or raise each of `answers` in turn, and copy_to_board
    raises `copy_raises` or keeps each copy."""

    def __init__(self, *answers, copy_raises=None):
        self.answers, self.copy_raises, self.copied = list(answers), copy_raises, []

    def _next(self):
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def run_code(self, code, keep_running_for=None):
        return self._next()

    def read_file(self, remote):
        return self._next()

    def copy_to_board(self, local, remote):
        if self.copy_raises:
            raise self.copy_raises
        self.copied.append((local, remote))


class FakeConsent:
    """A fake consent: answers `answer` and keeps each question."""

    def __init__(self, answer):
        self.answer, self.asked = answer, []

    def ask(self, question):
        self.asked.append(question)
        return self.answer
