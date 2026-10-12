#!/usr/bin/env python3
"""
Run one scenario of a built project in Wokwi, and keep a log of the run with its date (P130).

    run_scenario.py sim/scenarios/<name>.scenario.yaml        # in the project folder, after check_spine.py --keep .

The ready contract: the firmware prints `ready` once its setup is done, and nothing else containing that word before.
This adds a wait for the first serial text containing `ready` before the scenario's first step, because a step sent
earlier reaches a board that is still booting. So a scenario holds only behaviour: the conversation writes it from the
person's words, and spark ships none.

Each run first puts MicroPython and the project's firmware/ into a new flash image, so a run never tests an older
firmware. When the build named no image (no --firmware), this names flash-with-firmware.bin in sim/wokwi.toml, as
--firmware would have: wokwi-cli refuses a wokwi.toml that names none.

The log goes to sim/runs/<name>.log: the date, the verdict, the scenario as run, and what wokwi-cli printed, which is the
board's serial output among the scenario's progress. A run spends Wokwi CI minutes and needs WOKWI_CLI_TOKEN. The tests
use a fake wokwi-cli.
"""

import argparse
import datetime
import itertools
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import flash_image
import sim_project
import tools
from outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN, EXIT_FOR, OK, PROBLEMS

READY = "ready"
READY_STEP = '- wait-serial: "%s"' % READY
#: wokwi-cli's line when a wait-serial step matched (0.27.1): the proof that the ready text arrived.
MATCHED = "Expected text matched:"
#: wokwi-cli's own exit code for a run that reached --timeout (its --timeout-exit-code default).
TIMEOUT_EXIT = 42
DEFAULT_TIMEOUT_MS = 60000
#: The image named in wokwi.toml when the build named none.
DEFAULT_IMAGE = "flash-with-firmware.bin"
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
    if first is None or not lines[first].lstrip().startswith("- "):
        raise ValueError("it has no steps: list with a '- ' item under it")
    steps = [line.split("#")[0] for line in lines[first:] if line.lstrip().startswith("-")]
    if any("wait-serial" in step and READY in step
           for step in itertools.takewhile(lambda step: "set-control" not in step, steps)):
        return scenario
    step = lines[first].lstrip()
    lines.insert(first, lines[first][:len(lines[first]) - len(step)] + READY_STEP)
    return "\n".join(lines) + "\n"


def image_in(toml):
    """The flash image wokwi.toml names. When the build named none, this names DEFAULT_IMAGE there first."""
    text = toml.read_text()
    if sim_project.firmware_in(toml) is None and sim_project.UNNAMED_FIRMWARE in text:
        toml.write_text(text.replace(sim_project.UNNAMED_FIRMWARE, "\n".join(sim_project.firmware_lines(DEFAULT_IMAGE))))
    return toml.parent / (sim_project.firmware_in(toml) or DEFAULT_IMAGE)


def verdict(code, serial, out, err, timeout_ms):
    """
    (status, sentence) for one finished run, from wokwi-cli's exit code, the board's serial log, its stdout (the serial
    output line by line, among the scenario's progress) and its stderr (wokwi-cli's own errors).
    """
    if code == 0:
        return OK, "passed"
    errors = err.strip().splitlines()
    why = next((line for line in errors if "Error" in line), errors[-1] if errors else "no reason given")
    if "API Error" in why:
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


def run(project, scenario, cli, micropython=None, timeout_ms=DEFAULT_TIMEOUT_MS):
    """Run the scenario in the project's sim/ with the firmware as it is now: (status, sentence, the log or None)."""
    project, scenario = Path(project), Path(scenario)
    sim = project / "sim"
    log = sim / "runs" / (scenario.name.removesuffix(".yaml").removesuffix(".scenario") + ".log")
    log.unlink(missing_ok=True)  # an older run's verdict must not outlive a run that could not start
    if not all((sim / name).is_file() for name in ("diagram.json", "wokwi.toml")) or not (project / "firmware").is_dir():
        return (COULD_NOT_RUN, "no sim/ or no firmware/ in %s: build first with check_spine.py requirements.json --keep ."
                % project, None)
    try:
        steps = with_ready_wait(scenario.read_text())
        tools.find("littlefs")
        image = image_in(sim / "wokwi.toml")
        if sim.resolve() not in image.resolve().parents:
            raise ValueError("wokwi.toml names %s, outside sim/, and a run writes its image only inside sim/" % image)
        image.write_bytes(flash_image.image(flash_image.interpreter_path(micropython).read_bytes(),
                                            flash_image.files_under(project / "firmware")))
    except (OSError, ValueError, tools.ToolProblem) as cannot:
        return COULD_NOT_RUN, "%s: %s" % (scenario.name, cannot), None
    with tempfile.TemporaryDirectory() as scratch:
        as_run, serial_log = Path(scratch) / scenario.name, Path(scratch) / "serial.log"
        as_run.write_text(steps)
        try:
            done = subprocess.run(list(cli) + [str(sim), "--scenario", str(as_run), "--timeout", str(timeout_ms),
                                               "--serial-log-file", str(serial_log)],
                                  capture_output=True, encoding="utf-8", errors="replace",
                                  timeout=timeout_ms / 1000 + STARTUP_ALLOWANCE_S)
        except (OSError, subprocess.TimeoutExpired) as cannot:
            return COULD_NOT_RUN, "wokwi-cli did not finish: %s" % cannot, None
        serial = serial_log.read_text(errors="replace") if serial_log.is_file() else ""
    status, sentence = verdict(done.returncode, serial, done.stdout, done.stderr, timeout_ms)
    log.parent.mkdir(exist_ok=True)
    log.write_text("# %s, run %s, timeout %d ms\nverdict: %s\n\n--- the scenario as run ---\n%s\n--- wokwi-cli printed ---\n%s\n"
                   % (scenario.name, datetime.datetime.now().isoformat(timespec="seconds"), timeout_ms, sentence, steps,
                      (done.stdout + done.stderr).strip()))
    return status, sentence, log


def main(argv=None):
    parser = argparse.ArgumentParser(prog="run_scenario.py", description=__doc__.strip().split("\n\n")[0])
    parser.add_argument("scenario", type=Path, help="the scenario file, for example sim/scenarios/<name>.scenario.yaml")
    parser.add_argument("--project", type=Path, default=Path("."), help="the project folder with sim/ and firmware/ (default: here)")
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="simulated time the run may take")
    parser.add_argument("--micropython", type=Path, help="the interpreter .bin; omitted, the tools list's firmware-image download")
    args = parser.parse_args(argv)
    if not os.environ.get("WOKWI_CLI_TOKEN"):
        print("run_scenario.py: WOKWI_CLI_TOKEN is not set: get one at https://wokwi.com/dashboard/ci "
              "(a run spends Wokwi CI minutes)", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        cli = tools.find("simulator", args.project).command
    except tools.ToolProblem as missing:
        print("run_scenario.py: %s" % missing, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    status, sentence, log = run(args.project, args.scenario, cli, args.micropython, args.timeout_ms)
    print("%s: %s%s" % (args.scenario.name, sentence, "\nlog: %s" % log if log else ""),
          file=sys.stdout if status == OK else sys.stderr)
    return EXIT_FOR[status]


if __name__ == "__main__":
    sys.exit(main())
