"""
The board doctor (P282, #326): when esptool or mpremote cannot get into a board, a few named checks say what is true
and one next step for the person's hands. It never waits for the person and never runs the tool again: the agent or
the person does that (the PO's split, 2026-10-17).

A library. look.py and grant.py call it when esptool's read failed, reach.py and live.py when mpremote never got into
the board. The steps and their sources are in docs/discovery/2026-10-17-p282-troubleshoot/research.md.

    BoardCheckStrategy     one named check: run(port, silent_step) -> CheckResult.
    PortListedBoardCheck   `mpremote devs` lists the port, with its USB serial.
    ConsoleBoardCheck      two seconds of the console, opened with the port's lock: busy, download mode, a boot, or
                           silence. The open itself can restart a C6 (P251, AT187), so a boot is said as such.
    BoardDoctorService     runs BOARD_CHECKS in order and stops at the first that names a step.

The step for a silent board is the tool's own `silent_step` in the tools list (data/tools.json, which the person and
the project can change in their own layers): esptool needs download mode, mpremote a press of R.
"""

from collections import namedtuple

import tools
from board_console import KIND_BUSY, KIND_READ, ConsoleProbe, shows_boot
from board_look import LookStop, PortFinder
from download_mode import DOWNLOAD_MODE

#: The next steps, one code each. The sources are in MESSAGE_FOR's comments.
NEXT_PLUG_IN, NEXT_CLOSE_OTHER, NEXT_PRESS_RESET = "plug_in", "close_other", "press_reset"
NEXT_RUN_AGAIN, NEXT_HOLD_BOOT, NEXT_REPLUG = "run_again", "hold_boot", "replug"
#: The codes a tool entry's `silent_step` may name.
STEP_CODES = (NEXT_HOLD_BOOT, NEXT_PRESS_RESET)
#: The sentence of each step.
MESSAGE_FOR = {
    # board_look's own stop when mpremote devs does not list the board (P218).
    NEXT_PLUG_IN: "plug the board straight into the computer with a data cable, not a hub that gives power only, "
                  "and run it again",
    # mpremote and esptool lock the port while they run (mpremote 1.29 transport_serial.py:52).
    NEXT_CLOSE_OTHER: "another program holds the port: close it (a serial monitor, mpremote, esptool) and run it again",
    # A board that waited in download mode booted after one press of R (the P236 bench, AT157).
    NEXT_PRESS_RESET: "press the board's R (reset) button once and run it again",
    # The doctor's own open restarted the board (the P251 cure, AT187), so the first failure tells little now.
    NEXT_RUN_AGAIN: "the doctor's look at the console restarted the board: run it again",
    # esptool got in after the PO pressed BOOT and R (p238 finding.md:52, n = 1).
    NEXT_HOLD_BOOT: "hold the board's BOOT (B) button, press and release R, release BOOT, and run it again. After "
                    "it, press R once so the firmware starts",
    # 7 of 10 replugs reached a silent board (the P235 reach test); a replug also wakes a C6 from light sleep (esp-idf).
    NEXT_REPLUG: "unplug the board, plug it in again, and run it again",
}
#: The step to take when a step did not help. Only where a source backs it; every other step has none.
IF_NOT_HELPED = {NEXT_PRESS_RESET: NEXT_REPLUG}

#: Result: one check's `name`, whether it `passed`, the `fact` it found, and the `next_step` it names, or None.
CheckResult = namedtuple("CheckResult", "name passed fact next_step")
#: Result: each CheckResult in order, `tool_said` (the tool's own line of the failure, or None), the `next_step` code
#: (None when no check could look), and `if_not_helped`, the step after it, or None. Never a pass.
BoardDoctorResult = namedtuple("BoardDoctorResult", "checks tool_said next_step if_not_helped")


class UnknownStepError(ValueError):
    """Error: a tools list names a `silent_step` that is none of STEP_CODES."""


def silent_step_of(tool):
    """The tool entry's `silent_step`, one of STEP_CODES. UnknownStepError for any other value or none."""
    step = tool.entry.get("silent_step")
    if step not in STEP_CODES:
        raise UnknownStepError("the tools list gives %s the silent_step %r, and it must be one of %s"
                               % (tool.name, step, ", ".join(STEP_CODES)))
    return step


class BoardCheckStrategy:
    """Strategy: one named check of a board that did not answer. `run` returns a CheckResult."""

    name = None

    def run(self, port, silent_step):
        raise NotImplementedError


class PortListedBoardCheck(BoardCheckStrategy):
    """`mpremote devs` lists the port. It never opens the port. `finder` is a board_look.PortFinder."""

    name = "port-listed"

    def __init__(self, finder):
        self.finder = finder

    def run(self, port, silent_step):
        try:
            boards = self.finder.boards()
        except LookStop as cannot:
            return CheckResult(self.name, False, "could not list the boards: %s" % cannot, None)
        listed = [board for board in boards if board.device == port]
        if not listed:
            others = ", ".join(board.device for board in boards) or "none"
            return CheckResult(self.name, False, "mpremote devs does not list %s (it lists: %s)" % (port, others),
                               NEXT_PLUG_IN)
        return CheckResult(self.name, True, "mpremote devs lists %s, USB serial %s" % (port, listed[0].serial), None)


class ConsoleBoardCheck(BoardCheckStrategy):
    """Two seconds of the console, with the port's lock. `probe` is a board_console.ConsoleProbe, or None when
    mpremote is not a Python package here: then the console is not read, and the step is the tool's silent step."""

    name = "console"

    def __init__(self, probe):
        self.probe = probe

    def run(self, port, silent_step):
        if self.probe is None:
            return CheckResult(self.name, False, "not read: mpremote is not a Python package here", silent_step)
        read = self.probe.console()
        if read.kind == KIND_BUSY:
            return CheckResult(self.name, False, "another program holds the port: %s" % read.why, NEXT_CLOSE_OTHER)
        if read.kind != KIND_READ:
            return CheckResult(self.name, False, "could not read the console: %s" % read.why, None)
        if DOWNLOAD_MODE in read.printed:
            return CheckResult(self.name, False, "the board waits in download mode", NEXT_PRESS_RESET)
        if shows_boot(read.printed):
            return CheckResult(self.name, False, "the board booted when the doctor opened its port", NEXT_RUN_AGAIN)
        heard = read.printed.strip()
        fact = "the console printed: %s" % heard.splitlines()[-1] if heard else "the console was silent for 2 s"
        return CheckResult(self.name, False, fact, silent_step)


class BoardDoctorService:
    """Service: runs its checks in order on a board that did not answer, and stops at the first that names a step."""

    def __init__(self, checks):
        self.checks = tuple(checks)

    @classmethod
    def for_board(cls, finder, probe):
        """The doctor with BOARD_CHECKS: the port first, then the console."""
        return cls((PortListedBoardCheck(finder), ConsoleBoardCheck(probe)))

    def examine(self, port, tool, tool_said=None):
        """The BoardDoctorResult for the board on `port` after `tool` (a tools.Tool) failed and said `tool_said`.
        UnknownStepError when the tools list gives the tool no known silent_step."""
        silent_step, results = silent_step_of(tool), []
        for check in self.checks:
            results.append(check.run(port, silent_step))
            if results[-1].next_step:
                break
        step = results[-1].next_step if results else None
        return BoardDoctorResult(tuple(results), tool_said, step, IF_NOT_HELPED.get(step))


def after_esptool(stop, project, run):
    """The BoardDoctorResult for a board_look.LookStop from esptool's read, or None when the stop names no port (it
    was no failed read). The tools come from the project's tools list. tools.ToolProblem and UnknownStepError pass up."""
    if stop.port is None:
        return None
    shell = tools.find("board-shell", project)
    doctor = BoardDoctorService.for_board(PortFinder(shell, run), ConsoleProbe.for_tool(shell, stop.port, run))
    return doctor.examine(stop.port, tools.find("flasher", project), stop.tool_said)


def stop_lines(script, stop, project, run):
    """The lines a script prints when esptool's look stopped with `stop`. After a failed read, the board doctor's facts
    and next step follow, and the next step is the last line."""
    try:
        result = after_esptool(stop, project, run)
    except (tools.ToolProblem, UnknownStepError) as cannot:
        return ["%s: %s (no doctor: %s)" % (script, stop, cannot)]
    if result is None:
        return ["%s: %s" % (script, stop)]
    return ["%s: could not read the board on %s" % (script, stop.port)] + ["  " + line for line in describe(result)]


def describe(result):
    """The lines a person reads for a BoardDoctorResult, without indent."""
    out = ["said    %s" % result.tool_said] if result.tool_said else []
    out += ["check   %s: %s" % (check.name, check.fact) for check in result.checks]
    out.append("next    %s" % (MESSAGE_FOR[result.next_step] if result.next_step else "no step: the doctor could not look"))
    if result.if_not_helped:
        out.append("if not  %s" % MESSAGE_FOR[result.if_not_helped])
    return out


def as_dict(result):
    """A BoardDoctorResult as plain JSON values."""
    return dict(result._asdict(), checks=[check._asdict() for check in result.checks])
