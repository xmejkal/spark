"""
One run of one scenario in a project's sim/ (moved from run_scenario.py, P685): the checks that cost nothing, the image,
wokwi-cli and the log. run_scenario.py is its CLI. The log's words and their reader are in scenario_steps.py.
"""

import datetime
import hashlib
import itertools
import os
import subprocess
import tempfile
from pathlib import Path

from spark.core import outcomes
from spark.core.outcomes import COULD_NOT_RUN, OK, PROBLEMS
from spark.firmware import image_builder, sim_project
from spark.firmware.firmware_codes import (BOARD_NOT_STARTED, BOARD_SILENT, FIRMWARE_LINE_BAD, NEVER_READY, NO_MAIN_PY,
                                           NO_SIM_PROJECT, NO_TOKEN, RUN_INPUT_UNUSABLE, SIMULATOR_CANNOT_START,
                                           SIMULATOR_HUNG, SIMULATOR_LOST, STEP_FAILED, STEP_TIMEOUT, TOOL_MISSING, Refusal)
from spark.firmware.scenario_steps import (FILE_LINE, IMAGE_LINE, NO_MAIN, PASSED, READY, READY_STEP, SET_CONTROL, WAIT_SERIAL,
                                           ScenarioSteps, printed_text)
import tools


#: wokwi-cli's line when a wait-serial step matched (0.27.1): the proof that the ready text arrived.
MATCHED = "Expected text matched:"
#: wokwi-cli's stderr: a line with ERROR_WORD is its reason, and API_ERROR in it means the simulator was lost (0.27.1).
ERROR_WORD, API_ERROR = "Error", "API Error"
#: A YAML list item, as a scenario's step begins.
STEP_ITEM = "- "
#: wokwi-cli's own exit code for a run that reached --timeout (its --timeout-exit-code default).
TIMEOUT_EXIT = 42
DEFAULT_TIMEOUT_MS = 60000
#: How long wokwi-cli may take beyond the simulated time: connecting, sending the image.
STARTUP_ALLOWANCE_S = 120


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


def image_in(toml):
    """The flash image wokwi.toml names. When the build named none, this names sim_project.DEFAULT_IMAGE there first."""
    text = toml.read_text()
    if sim_project.firmware_in(toml).state == outcomes.NONE_RECORDED and sim_project.UNNAMED_FIRMWARE in text:
        toml.write_text(text.replace(sim_project.UNNAMED_FIRMWARE, "\n".join(sim_project.firmware_lines(sim_project.DEFAULT_IMAGE))))
    named = sim_project.firmware_in(toml)
    if named.state == outcomes.NOT_CHECKED:
        raise ValueError("wokwi.toml %s%s" % (named.why, named.fix()))
    return toml.parent / (named.name or sim_project.DEFAULT_IMAGE)


def verdict(code, serial, out, err, timeout_ms):
    """(status, sentence) for one finished run, from wokwi-cli's exit code, the board's serial log, its stdout (the serial
    output line by line, among the scenario's progress) and its stderr (wokwi-cli's own errors)."""
    if code == 0:
        return OK, PASSED
    errors = err.strip().splitlines()
    why = next((line for line in errors if ERROR_WORD in line), errors[-1] if errors else "no reason given")
    if API_ERROR in why:
        return COULD_NOT_RUN, Refusal("wokwi-cli lost the simulator (exit %d): %s" % (code, why), SIMULATOR_LOST)
    if not serial.strip():
        if code == TIMEOUT_EXIT:
            return COULD_NOT_RUN, Refusal("the board printed nothing in %d ms: does diagram.json wire its TX and RX to "
                                          "$serialMonitor (P190)?" % timeout_ms, BOARD_SILENT)
        return COULD_NOT_RUN, Refusal("wokwi-cli stopped before the board started (exit %d): %s" % (code, why), BOARD_NOT_STARTED)
    # wokwi-cli's own line is the proof that the wait matched: the wait matches any text containing READY, and the serial
    # log file joins MicroPython's lines with no line break between them (wokwi-cli 0.27.1, 2026-10-12).
    if not any(MATCHED in line and READY in line for line in out.splitlines()):
        return PROBLEMS, Refusal("the firmware never printed %r: print it once setup is done (the ready contract, "
                                 "commands/build.md)" % READY, NEVER_READY)
    if code == TIMEOUT_EXIT:
        return PROBLEMS, Refusal("timed out after %d ms: a step waited for something that never came" % timeout_ms, STEP_TIMEOUT)
    return PROBLEMS, Refusal("failed (wokwi-cli exit %d): %s" % (code, why), STEP_FAILED)


class ScenarioRun:
    """
    Service: one run of one scenario in a project's sim/. problem() makes every check that costs nothing, so a run that cannot
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
        """Why this run cannot pass, found before any Wokwi minute is spent, as a Refusal, or None."""
        if not all((self.sim / name).is_file() for name in ("diagram.json", "wokwi.toml")):
            return Refusal("no simulation project in %s: build first with /spark:build --keep ." % self.sim, NO_SIM_PROJECT)
        if not (self.project / "firmware" / "main.py").is_file():
            return Refusal(NO_MAIN % (self.project, READY), NO_MAIN_PY)
        try:
            self.steps = with_ready_wait(self.scenario.read_text())
            tools.find("littlefs", self.project)  # P457: a project's tools file that turns it off is named
            self.image = image_in(self.sim / "wokwi.toml")
            self.files = image_builder.files_under(self.project / "firmware")
            self.flash = image_builder.interpreter_for(self.micropython, self.project).image(self.files)
        except (OSError, ValueError, tools.ToolProblem) as cannot:  # a missing tool or a bad build: image_builder's codes
            code = TOOL_MISSING if isinstance(cannot, tools.ToolProblem) else getattr(cannot, "code", RUN_INPUT_UNUSABLE)
            return Refusal("%s: %s" % (self.scenario.name, cannot), code)
        outside = sim_project.why_outside_sim(self.sim, self.image)
        return Refusal(outside, FIRMWARE_LINE_BAD) if outside else None

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
                sentence = Refusal("wokwi-cli did not finish in %d s" % late.timeout, SIMULATOR_HUNG)
                return COULD_NOT_RUN, sentence, self.write_log(sentence, "\n".join(map(printed_text, (late.stdout, late.stderr))))
            except OSError as cannot:
                return COULD_NOT_RUN, Refusal("wokwi-cli could not start: %s" % cannot, SIMULATOR_CANNOT_START), None
            finally:
                as_run.unlink(missing_ok=True)
            serial = serial_log.read_text(errors="replace") if serial_log.is_file() else ""
        status, sentence = verdict(done.returncode, serial, done.stdout, done.stderr, self.timeout_ms)
        log = self.write_log(sentence, done.stdout + done.stderr)  # the log's verdict stays `passed`: deploy reads it
        return status, ScenarioSteps.from_text(self.steps).passed_sentence() if status == OK else sentence, log

    def write_log(self, sentence, said):
        """
        The log of a run that reached wokwi-cli. Its header, which run_record, file_hashes and ScenarioSteps.from_log read,
        holds the date with its zone, the verdict, the step counts and the sha256 of the image and of each file in it. After
        the header come what the simulation cannot show (when sim/ holds that note), the scenario as run and what
        wokwi-cli printed. A note that cannot be read is left out, so the paid run's verdict is still written.
        """
        self.log.parent.mkdir(exist_ok=True)
        files = "".join("%s%s %s\n" % (FILE_LINE, hashlib.sha256(data).hexdigest(), name) for name, data in self.files)
        limits = self.sim / sim_project.LIMITS_NOTE
        try:
            shown = "%s\n%s\n\n" % (sim_project.LIMITS_SECTION, limits.read_text(errors="replace").rstrip("\n")) if limits.is_file() else ""
        except OSError:
            shown = ""
        self.log.write_text("# %s, run %s, timeout %d ms\nverdict: %s\n%s\n%s%s\n%s\n%s%s\n%s\n"
                            "--- wokwi-cli printed ---\n%s\n"
                            % (self.scenario.name, datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                               self.timeout_ms, sentence, ScenarioSteps.from_text(self.steps).log_lines(), IMAGE_LINE,
                               hashlib.sha256(self.flash).hexdigest(), files, shown, sim_project.SCENARIO_SECTION, self.steps, said.strip()))
        return self.log


def find_simulator(project, find_tool=None):  # --- MVP --- (P684)
    """(the simulator, None) or (None, a Refusal): no simulator, or its token unset. `find_tool`: tools.find when None."""
    try:
        simulator = (find_tool or tools.find)("simulator", project)
    except tools.ToolProblem as missing:
        return None, Refusal(str(missing), TOOL_MISSING)
    token = simulator.entry.get("account_env", "WOKWI_CLI_TOKEN")
    if token and not os.environ.get(token):
        return None, Refusal("%s is not set: %s (a run spends Wokwi CI minutes)" % (
            token, simulator.entry.get("needs_account", "get one at wokwi.com/dashboard/ci")), NO_TOKEN)
    return simulator, None

