"""P239 PR 2 (#238): the fakes of the deploy area's swappable parts, one per part of spark's core."""

import datetime
import os
import sys
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import store  # noqa: E402
from firmware_platform import FirmwarePlatform, MicroPythonPlatform  # noqa: E402

#: The store the suite started with: the constants of board_grant (the grant lines) were made with it, at import (P463).
IMPORT_HOME = os.environ["SPARK_HOME"]


def line_made_at_import(line):
    """`line` led by the store of the import, as board_grant's constants are."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": IMPORT_HOME}):
        return store.prefix_home(line)


class FakeBoardConnection:
    """A fake BoardConnection: run_code and read_file give or raise each of `answers` in turn, and copy_to_board
    raises `copy_raises` (or, given a list, its next entry) or keeps each copy. reset raises `reset_raises` or counts the reset in `resets`.
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
        raises = self.copy_raises.pop(0) if isinstance(self.copy_raises, list) else self.copy_raises
        if raises:
            raise raises
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
    """A fake clock, one for all of the code's clocks: `now` gives a time with its zone, `monotonic` gives `elapsed`, and
    `sleep` keeps each wait and moves both on at once. `advance` moves them on without a wait."""

    def __init__(self, now=datetime.datetime(2026, 10, 17, 9, 0, tzinfo=datetime.timezone.utc), elapsed=0.0):
        self.moment, self.elapsed, self.slept = now, elapsed, []

    def now(self):
        return self.moment

    def monotonic(self):
        return self.elapsed

    def advance(self, **kw):
        """Move the clock on by a datetime.timedelta's keyword arguments, for example minutes=30."""
        step = datetime.timedelta(**kw)
        self.moment, self.elapsed = self.moment + step, self.elapsed + step.total_seconds()

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.advance(seconds=seconds)


class FakePortFinder:
    """A fake board_look.PortFinder: each `nodes` call gives the next of `looks`, a list of Ports (or a LookStop to raise),
    and the last one for good."""

    def __init__(self, *looks):
        self.looks = list(looks)

    def nodes(self):
        look = self.looks.pop(0) if len(self.looks) > 1 else self.looks[0]
        if isinstance(look, Exception):
            raise look
        return look


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


class FakeConsoleProbe:
    """A fake ConsoleProbe: the console prints `printed`, and the console read calls `on_console` (a test's way to make
    the board answer again). cure() calls `on_cure` and gives `cured`, a board_console.Cure. Keeps how often each was asked."""

    def __init__(self, printed="", on_console=None, cured=None, on_cure=None):
        self.printed, self.asked = printed, []
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

    def cure(self):
        self.asked.append("cure")
        if self.on_cure:
            self.on_cure()
        return self.cured


class FakeBoardReader:
    """A fake board_look.BoardReader: each `read` gives the next of `readings` (a BoardReading, or a LookStop to raise), and
    the last one for good. Keeps each port it was asked for in `read_ports`."""

    def __init__(self, *readings):
        self.readings, self.read_ports = list(readings), []

    def read(self, port):
        self.read_ports.append(port)
        reading = self.readings.pop(0) if len(self.readings) > 1 else self.readings[0]
        if isinstance(reading, Exception):
            raise reading
        return reading


class FakeFirmwarePlatform(FirmwarePlatform):
    """A fake FirmwarePlatform: each part is the object a test gives, or the exception it raises when the code asks for
    it. A part left out raises AssertionError when asked for. `hints` keeps the hint of each `make_board_reader`, and
    `roles` the role of each `find_tool`."""

    def __init__(self, project=Path("."), flasher=None, shell_command=None, port_finder=None, board_reader=None,
                 connection=None, ready_check=None, console_probe=None, tool=None):
        super().__init__(project)
        self.parts = {"flasher": flasher, "shell_command": shell_command, "port_finder": port_finder,
                      "board_reader": board_reader, "connection": connection, "ready_check": ready_check,
                      "console_probe": console_probe, "tool": tool}
        self.hints, self.roles = [], []

    def _part(self, name):
        part = self.parts[name]
        assert part is not None, "the test gave no %s, and the code asked for it" % name
        if isinstance(part, Exception):
            raise part
        return part

    def find_tool(self, role):
        self.roles.append(role)
        return self._part("tool")

    def make_flasher(self):
        return self._part("flasher")

    def make_shell_command(self):
        return self._part("shell_command")

    def make_port_finder(self, run):
        return self._part("port_finder")

    def make_board_reader(self, run, hint):
        self.hints.append(hint)
        return self._part("board_reader")

    def make_connection(self, command, port, run):
        return self._part("connection")

    def make_ready_check(self, connection):
        return self._part("ready_check")

    def make_console_probe(self, port, run):
        return self._part("console_probe")


class FakeProbePlatform(MicroPythonPlatform):
    """A fake MicroPythonPlatform for a test that runs the real finder, reader and flasher over a fake `run`: the console
    probe is `probe` (or raised, when it is an exception), and the tools come from `find_tool` (a role -> tools.Tool; the
    project's tools list when None)."""

    def __init__(self, project, probe, find_tool=None):
        super().__init__(project, find_tool)
        self.probe = probe

    def make_console_probe(self, port, run):
        if isinstance(self.probe, Exception):
            raise self.probe
        return self.probe


class FakeDeployRecordStore:
    """A fake deploy_record_store.DeployRecordStore: `write_deploy` keeps each call in `written` and gives `path`, or raises
    `raises` (for example store.StoreProblem)."""

    def __init__(self, path=Path("record.json"), raises=None):
        self.path, self.raises, self.written = path, raises, []

    def write_deploy(self, facts, verdict, who):
        if self.raises:
            raise self.raises
        self.written.append((facts, verdict, who))
        return self.path


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


class FakeOutsideWorld:
    """Fake OutsideWorld (spark.core.outside): `run` answers a command as `subprocess.run` would, with the callable a test
    gives, and keeps each command in `ran`; `find_tool` gives a tools.Tool by its name with the callable given (a dict's
    `get`, or test_deploy's `found`). A test that gives neither gets an AssertionError on the first call, never a program."""

    def __init__(self, run=None, find_tool=None):
        self.ran, self._run, self._find_tool = [], run, find_tool

    def run(self, command, **options):
        self.ran.append(command)
        assert self._run, "the test gave no run, and the Operation asked to run %r" % (command,)
        return self._run(command, **options)

    def find_tool(self, name, **where):
        assert self._find_tool, "the test gave no find_tool, and the Operation asked for %r" % (name,)
        return self._find_tool(name, **where)
