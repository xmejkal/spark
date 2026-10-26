#!/usr/bin/env python3
"""
Run one scenario of a built project in Wokwi, and keep a log of the run with its date (P130).

    run_scenario.py sim/scenarios/<name>.scenario.yaml        # in the project folder, after /spark:build --keep .

The ready contract: the firmware prints `ready` once its setup is done, and nothing else containing that word before.
This adds a wait for the first serial text containing `ready` before the scenario's first step, because a step sent
earlier reaches a board that is still booting. So a scenario holds only behaviour: the conversation writes it from the
person's words, and spark ships none.

A run spends Wokwi CI minutes, so every check that costs nothing comes first: the simulation project, firmware/main.py,
the scenario's steps, littlefs, MicroPython and the image's place. Only then the tool, the token and the paid run. Each
run puts MicroPython and the project's firmware/ into a new flash image, so a run never tests an older firmware. When the
build named no image (no --firmware), this names flash-with-firmware.bin in sim/wokwi.toml, as --firmware would have:
wokwi-cli refuses a wokwi.toml that names none.

The log goes to sim/runs/<name>.log: the date with its zone, the verdict, the step counts by kind (P345), the sha256 of
the image it tested and of each file in that image, what the simulation cannot show, the scenario as run, and what
wokwi-cli printed, which is the board's serial output among the scenario's
progress. deploy.py reads the verdict and the sha256s from the log's header (run_record, file_hashes). The tests use a fake wokwi-cli.
"""

import argparse
import datetime
import hashlib
import itertools
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import flash_image
import sim_project
import tools
from outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, EXIT_FOR, OK, PROBLEMS
from text_guards import guard_lines

# --- MVP ---
#: The kinds of wokwi-cli scenario step that this reads by name: the one that sets a control, the one that reads a pin
#: and the one that waits for serial text.
SET_CONTROL, EXPECT_PIN, WAIT_SERIAL = "set-control", "expect-pin", "wait-serial"
READY = "ready"
READY_STEP = '- %s: "%s"' % (WAIT_SERIAL, READY)
#: wokwi-cli's line when a wait-serial step matched (0.27.1): the proof that the ready text arrived.
MATCHED = "Expected text matched:"
#: wokwi-cli's stderr: a line with ERROR_WORD is its reason, and API_ERROR in it means the simulator was lost (0.27.1).
ERROR_WORD, API_ERROR = "Error", "API Error"
#: A YAML list item, as a scenario's step begins.
STEP_ITEM = "- "
#: wokwi-cli's own exit code for a run that reached --timeout (its --timeout-exit-code default).
TIMEOUT_EXIT = 42
DEFAULT_TIMEOUT_MS = 60000
#: The image named in wokwi.toml when the build named none.
DEFAULT_IMAGE = "flash-with-firmware.bin"
#: How long wokwi-cli may take beyond the simulated time: connecting, sending the image.
STARTUP_ALLOWANCE_S = 120
#: The log's line that names the image a run tested, by its sha256 (P192): deploy.py flashes only an image a passed run names.
IMAGE_LINE = "image sha256: "
#: The log's line for each file in the image, its sha256 then its path inside the image (P215, D20): the board's files
#: are checked against these after a flash.
FILE_LINE = "file sha256: "
#: The log's line that counts the scenario's steps by kind (P345): what a passed run did, read by the look and the deploy question.
STEP_COUNTS_LINE = "step counts: "
#: What the line says when the steps could not be counted: a step has no key, so a kind would be a guess.
STEPS_NOT_READ = "not read"
#: The log's section that holds the simulation's limits note, when the project has one (P396).
LIMITS_SECTION = "--- what this simulation cannot show ---"
#: What --help says beyond the arguments: the cost, the token, the contract and the exit codes.
EPILOG = """A run spends Wokwi CI minutes: ask the person before each run, whatever your permissions allow.
It needs a Wokwi CI token (wokwi.com/dashboard/ci) in WOKWI_CLI_TOKEN: export WOKWI_CLI_TOKEN=...
The firmware must print `ready` once its setup is done (the ready contract, commands/build.md).

Exit codes: 0 the scenario passed, 1 it failed, 2 it could not run. The log is sim/runs/<name>.log."""


def with_ready_wait(scenario):
    """
    The scenario's text with a wait for the ready text before its first step, at that step's indent. A scenario that
    already waits for text containing `ready` before its first input is left as it is: a second wait would never match,
    because a wait sees only the text that arrives after its step begins.
    """
    lines = scenario.splitlines()
    start = next((i for i, line in enumerate(lines) if line.split("#")[0].rstrip() == "steps:"), None)
    first = None if start is None else next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() and not lines[i].lstrip().startswith("#")), None)
    if first is None or not lines[first].lstrip().startswith(STEP_ITEM):
        raise ValueError("it has no steps: list with a '- ' item under it")
    steps = [line.split("#")[0] for line in lines[first:] if line.lstrip().startswith("-")]
    if any(WAIT_SERIAL in step and READY in step
           for step in itertools.takewhile(lambda step: SET_CONTROL not in step, steps)):
        return scenario
    step = lines[first].lstrip()
    lines.insert(first, lines[first][:len(lines[first]) - len(step)] + READY_STEP)
    return "\n".join(lines) + "\n"


# --- MVP ---
class ScenarioSteps:
    """
    Value: the steps of a scenario counted by kind. `counts` maps a step kind (the key of a step, such as `set-control`) to
    how many steps have it. `unread` is True when the steps could not be counted: a log with no counts line, or a step
    with no key. Nothing is derived from an unread count.
    """

    #: A key at the start of a step's text, plain or quoted. Anchored, so a kind named inside a value is no key.
    KEY = re.compile(r"""^\s*(?:"([\w-]+)"|'([\w-]+)'|([\w-]+))\s*:""")
    ITEM = re.compile(r"^(\s*)-(?:\s|$)")
    #: The one key a step carries beside its kind: wokwi-cli prints it as the step's name (TestScenario.ts, validStepKeys).
    NAME_KEY = "name"

    def __init__(self, counts, unread=False):
        self.counts, self.unread = dict(counts), unread

    @classmethod
    def from_text(cls, steps):
        """The ScenarioSteps of a scenario's text, comments cut as with_ready_wait cuts them. Only the items at the indent of the first step count."""
        lines = [line.split("#")[0].rstrip() for line in steps.splitlines()]
        start = next((i for i, line in enumerate(lines) if line == "steps:"), None)
        body = [] if start is None else [line for line in lines[start + 1:] if line.strip()]
        first = next((cls.ITEM.match(line) for line in body if cls.ITEM.match(line)), None)
        if first is None:
            return cls({}, unread=True)
        width, steps = len(first.group(1)), []
        for line in body:
            item = cls.ITEM.match(line)
            if item and len(item.group(1)) == width:
                steps.append([line[item.end():].lstrip().lstrip("{")])
            elif len(line) - len(line.lstrip()) <= width:
                break  # the steps list ended: a key of the scenario at its own indent
            elif steps:
                steps[-1].append(line)
        counts, unread = {}, False
        for step in steps:
            kind = cls._kind(step)
            if kind:
                counts[kind] = counts.get(kind, 0) + 1
            else:
                unread = True
        return cls(counts, unread)

    @classmethod
    def _kind(cls, step):
        """A step's kind: the first key of its lines that is not `name`, or None. The flow form keeps its keys on one line."""
        for text in step[0].split(",") + step[1:]:
            key = cls.KEY.match(text)
            kind = key and (key.group(1) or key.group(2) or key.group(3))
            if kind and kind != cls.NAME_KEY:
                return kind
        return None

    @classmethod
    def from_log(cls, log):
        """The ScenarioSteps a log's header counts. A log with no counts line (older), a malformed one or a file that cannot be read is unread."""
        try:
            said = next((line[len(STEP_COUNTS_LINE):] for line in _header(log) if line.startswith(STEP_COUNTS_LINE)), None)
        except OSError:
            said = None
        if said is None or said == STEPS_NOT_READ:
            return cls({}, unread=True)
        counts = {}
        for each in said.split(", "):
            kind, _, number = each.partition(" ")
            if not re.fullmatch(r"[\w-]+", kind) or not number.isascii() or not number.isdigit() or kind in counts:
                return cls({}, unread=True)
            counts[kind] = int(number)
        return cls(counts)

    def count(self, kind):
        """How many steps have this kind."""
        return self.counts.get(kind, 0)

    def line(self):
        """The log's counts line: every kind, sorted, with the two kinds that matter always shown, or `not read`."""
        if self.unread:
            return STEP_COUNTS_LINE + STEPS_NOT_READ
        kinds = sorted(set(self.counts) | {SET_CONTROL, EXPECT_PIN})
        return STEP_COUNTS_LINE + ", ".join("%s %d" % (kind, self.count(kind)) for kind in kinds)


def image_in(toml):
    """The flash image wokwi.toml names. When the build named none, this names DEFAULT_IMAGE there first."""
    text = toml.read_text()
    if sim_project.firmware_in(toml) is None and sim_project.UNNAMED_FIRMWARE in text:
        toml.write_text(text.replace(sim_project.UNNAMED_FIRMWARE, "\n".join(sim_project.firmware_lines(DEFAULT_IMAGE))))
    named = sim_project.firmware_in(toml)
    if named is None and any(line.lstrip().startswith("firmware") for line in toml.read_text().splitlines()):
        raise ValueError('wokwi.toml names its firmware in a form this cannot read: write it as firmware = "name.bin"')
    return toml.parent / (named or DEFAULT_IMAGE)


def verdict(code, serial, out, err, timeout_ms):
    """
    (status, sentence) for one finished run, from wokwi-cli's exit code, the board's serial log, its stdout (the serial
    output line by line, among the scenario's progress) and its stderr (wokwi-cli's own errors).
    """
    if code == 0:
        return OK, "passed"
    errors = err.strip().splitlines()
    why = next((line for line in errors if ERROR_WORD in line), errors[-1] if errors else "no reason given")
    if API_ERROR in why:
        return COULD_NOT_RUN, "wokwi-cli lost the simulator (exit %d): %s" % (code, why)
    if not serial.strip():
        if code == TIMEOUT_EXIT:
            return COULD_NOT_RUN, ("the board printed nothing in %d ms: does diagram.json wire its TX and RX to "
                                   "$serialMonitor (P190)?" % timeout_ms)
        return COULD_NOT_RUN, "wokwi-cli stopped before the board started (exit %d): %s" % (code, why)
    # wokwi-cli's own line is the proof that the wait matched: the wait matches any text containing READY, and the serial
    # log file joins MicroPython's lines with no line break between them (wokwi-cli 0.27.1, 2026-10-12).
    if not any(MATCHED in line and READY in line for line in out.splitlines()):
        return PROBLEMS, ("the firmware never printed %r: print it once setup is done (the ready contract, "
                          "commands/build.md)" % READY)
    if code == TIMEOUT_EXIT:
        return PROBLEMS, "timed out after %d ms: a step waited for something that never came" % timeout_ms
    return PROBLEMS, "failed (wokwi-cli exit %d): %s" % (code, why)


class ScenarioRun:
    """
    One run of one scenario in a project's sim/. problem() makes every check that costs nothing, so a run that cannot
    pass is refused before it spends a Wokwi minute; run() then makes the image, runs wokwi-cli and writes the log.
    """

    def __init__(self, project, scenario, micropython=None, timeout_ms=DEFAULT_TIMEOUT_MS):
        self.project = Path(project)
        self.scenario = self.project / scenario  # a relative path is the project's; an absolute one stays as it is
        self.sim = self.project / "sim"
        self.micropython, self.timeout_ms = micropython, timeout_ms
        self.log = self.sim / "runs" / (self.scenario.name.removesuffix(".yaml").removesuffix(".scenario") + ".log")
        self.steps = self.flash = self.image = self.files = None

    def problem(self):
        """Why this run cannot pass, found before any Wokwi minute is spent, or None."""
        if not all((self.sim / name).is_file() for name in ("diagram.json", "wokwi.toml")):
            return "no simulation project in %s: build first with /spark:build --keep ." % self.sim
        if not (self.project / "firmware" / "main.py").is_file():
            return NO_MAIN % (self.project, READY)
        try:
            self.steps = with_ready_wait(self.scenario.read_text())
            tools.find("littlefs")
            self.image = image_in(self.sim / "wokwi.toml")
            self.files = flash_image.files_under(self.project / "firmware")
            self.flash = flash_image.interpreter_for(self.micropython, self.project).image(self.files)
        except (OSError, ValueError, tools.ToolProblem) as cannot:
            return "%s: %s" % (self.scenario.name, cannot)
        if self.sim.resolve() not in self.image.resolve().parents:
            return "wokwi.toml names %s, outside sim/, and a run writes its image only inside sim/" % self.image
        return None

    def run(self, cli):
        """Run it with the firmware as it is now: (status, sentence, the log or None). Every paid run leaves a log."""
        self.log.unlink(missing_ok=True)  # an older run's verdict must not outlive a run that could not start
        problem = self.problem()
        if problem:
            return COULD_NOT_RUN, problem, None
        self.image.write_bytes(self.flash)
        # Beside the original, so a step's own path (a screenshot to compare with) resolves where its author wrote it.
        as_run = self.scenario.absolute().parent / (".as-run." + self.scenario.name)  # wokwi-cli reads a relative one from sim/
        with tempfile.TemporaryDirectory() as scratch:
            serial_log = Path(scratch) / "serial.log"
            try:
                as_run.write_text(self.steps)
                done = subprocess.run(list(cli) + [str(self.sim), "--scenario", str(as_run), "--timeout",
                                                   str(self.timeout_ms), "--serial-log-file", str(serial_log)],
                                      capture_output=True, encoding="utf-8", errors="replace",
                                      timeout=self.timeout_ms / 1000 + STARTUP_ALLOWANCE_S)
            except subprocess.TimeoutExpired as late:
                sentence = "wokwi-cli did not finish in %d s" % late.timeout
                return COULD_NOT_RUN, sentence, self.write_log(sentence, "\n".join(map(printed_text, (late.stdout, late.stderr))))
            except OSError as cannot:
                return COULD_NOT_RUN, "wokwi-cli could not start: %s" % cannot, None
            finally:
                as_run.unlink(missing_ok=True)
            serial = serial_log.read_text(errors="replace") if serial_log.is_file() else ""
        status, sentence = verdict(done.returncode, serial, done.stdout, done.stderr, self.timeout_ms)
        return status, sentence, self.write_log(sentence, done.stdout + done.stderr)

    def write_log(self, sentence, said):
        """
        The log of a run that reached wokwi-cli. Its header, which run_record, file_hashes and ScenarioSteps.from_log read,
        holds the date with its zone, the verdict, the step counts and the sha256 of the image and of each file in it. After
        the header come what the simulation cannot show (when sim/ holds that note), the scenario as run and what
        wokwi-cli printed. A note that cannot be read is left out, so the paid run's verdict is still written.
        """
        self.log.parent.mkdir(exist_ok=True)
        files = "".join("%s%s %s\n" % (FILE_LINE, hashlib.sha256(data).hexdigest(), name) for name, data in self.files)
        limits = self.sim / "WHAT-THIS-CANNOT-SHOW.md"
        try:
            shown = "%s\n%s\n\n" % (LIMITS_SECTION, limits.read_text(errors="replace").rstrip("\n")) if limits.is_file() else ""
        except OSError:
            shown = ""
        self.log.write_text("# %s, run %s, timeout %d ms\nverdict: %s\n%s\n%s%s\n%s\n%s--- the scenario as run ---\n%s\n"
                            "--- wokwi-cli printed ---\n%s\n"
                            % (self.scenario.name, datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                               self.timeout_ms, sentence, ScenarioSteps.from_text(self.steps).line(), IMAGE_LINE,
                               hashlib.sha256(self.flash).hexdigest(), files, shown, self.steps, said.strip()))
        return self.log


def printed_text(output):
    """What a killed process printed, as text: subprocess hands it back as bytes, as text or as nothing."""
    return output.decode("utf-8", "replace") if isinstance(output, bytes) else (output or "")


def _header(log):
    """The log's header: the lines before the first blank line. What the board printed comes later, so it is never read."""
    return Path(log).read_text(errors="replace").split("\n\n", 1)[0].splitlines()


def run_record(log):
    """
    (verdict, the tested image's sha256 or None) of one run log, read from its header, so a firmware that prints
    `verdict: passed` cannot pass a run.
    """
    header = _header(log)

    def field(prefix):
        """The text after the first header line that starts with this prefix, or None."""
        return next((line[len(prefix):].strip() for line in header if line.startswith(prefix)), None)

    return field("verdict: "), field(IMAGE_LINE)


#: Why a project with no firmware/main.py cannot go on a board: %s are the project and READY.
NO_MAIN = "no firmware/main.py in %s: the board would boot to a bare prompt and never print %r"


def file_hashes(log):
    """{path inside the image: sha256} of each file the run's image held, from the header; {} for an older log."""
    return dict(reversed(line[len(FILE_LINE):].split(" ", 1)) for line in _header(log) if line.startswith(FILE_LINE))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="run_scenario.py", description=__doc__.strip().split("\n\n")[0],
                                     epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenario", type=Path,
                        help="the scenario file, relative to the project: sim/scenarios/<name>.scenario.yaml")
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder with sim/ and firmware/ (default: here)")
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="simulated time the run may take")
    parser.add_argument("--micropython", type=Path, help="the interpreter .bin; omitted, the one /spark:setup downloads")
    args = parser.parse_args(argv)
    run = ScenarioRun(args.project, args.scenario, args.micropython, args.timeout_ms)
    run.log.unlink(missing_ok=True)  # an older run's verdict must not outlive a run refused here
    try:  # what costs nothing first, then the tool, then the token: a person learns of a missing build before an account
        problem = run.problem()
        simulator = None if problem else tools.find("simulator", args.project)
    except tools.ToolProblem as missing:
        problem, simulator = str(missing), None
    token = simulator.entry.get("account_env", "WOKWI_CLI_TOKEN") if simulator else None
    if token and not os.environ.get(token):
        problem = "%s is not set: %s (a run spends Wokwi CI minutes)" % (
            token, simulator.entry.get("needs_account", "get one at wokwi.com/dashboard/ci"))
    if problem:
        print(guard_lines("run_scenario.py: %s" % problem), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    status, sentence, log = run.run(simulator.command)
    print(guard_lines("%s: %s%s" % (args.scenario.name, sentence, "\nlog: %s" % log if log else "")),
          file=sys.stdout if status == OK else sys.stderr)  # the log file in sim/runs keeps the raw text
    return EXIT_FOR[status]


if __name__ == "__main__":
    sys.exit(main())
