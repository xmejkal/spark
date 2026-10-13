#!/usr/bin/env python3
"""
Put the flash image that passed the simulation onto the board (P192).

    deploy.py --dry-run                          # in the project folder: print what it would run, run nothing
    deploy.py --port /dev/cu.usbmodem1101        # erase the board's flash, then write the image

The image is the one sim/wokwi.toml names. run_scenario.py writes it, MicroPython and the project's firmware/ in one
flash image, and tests it: each run's log names the image's sha256. This flashes the image only when a run that passed
names it and no run with another verdict does. esptool erases the flash and writes the image at 0x0, where the
simulator loaded it. Then mpremote's REPL shows the board start: press Ctrl-C, then Ctrl-D, and the firmware prints
`ready` (the ready contract, commands/build.md).

The chip comes from the project's board (requirements.json's `board`), and esptool refuses a board with another chip.
esptool and mpremote are the tools list's `flasher` and `board-shell`, which /spark:setup installs.
"""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

import boards
import tools
from image_check import (BOOT_HINT, DeployProblem, image_of, run_logs, runnable, tested_another,  # noqa: F401
                         untested)
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK

#: Where the image goes: it is the whole flash from its first byte, as the simulator loaded it.
IMAGE_OFFSET = "0x0"
#: esptool's commands with underscores: esptool 3 and 4 know only these, and 5.x still accepts them with a deprecation
#: line (esptool 5.5.0's cli_util.py, read 2026-10-12). The tools list finds any installed esptool, not only its pin.
ERASE, WRITE = "erase_flash", "write_flash"
#: The last line: how the person sees the firmware start.
WATCH = "then, to see it start: %s, press Ctrl-C, then Ctrl-D: the firmware prints `ready`"
#: How a refusal for a run that tested another image ends: what to do instead (the PO, 2026-10-12: refuse by default).
OLDER_RUNS_WAY_OUT = (". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, pass "
                      "--ignore-older-runs, and deploy.py names the log in a note")
#: What --help says beyond the arguments.
EPILOG = """It flashes only an image that a passed run names (sim/runs/*.log), and no log there may name another image
(--ignore-older-runs flashes anyway). It erases the board's flash first.

Exit codes: 0 done (with --dry-run: printed), 2 it could not run, and the sentence says why."""


def newer_files(project, image):
    """The files under firmware/ changed after the image was made, as project paths. The board gets the image, not them."""
    made = image.stat().st_mtime
    return sorted(str(path.relative_to(project)) for path in (project / "firmware").rglob("*")
                  if path.is_file() and "__pycache__" not in path.parts and path.stat().st_mtime > made)


def chip_of(project):
    """The board's chip as esptool names it, from requirements.json's board (P192: no chip table)."""
    requirements = project / "requirements.json"
    try:
        return boards.get(project, "chip", json.loads(requirements.read_text()).get("board"))
    except (OSError, ValueError, AttributeError, boards.BoardError) as cannot:
        raise DeployProblem("the board's chip cannot be read from %s: %s" % (requirements, cannot))


def flash_commands(flasher, chip, image, port=None):
    """esptool's two commands: erase the board's flash, then write the image at IMAGE_OFFSET."""
    base = runnable(flasher) + ["--chip", chip] + (["--port", port] if port else [])
    return [base + [ERASE], base + [WRITE, IMAGE_OFFSET, str(image)]]


def watch_command(shell, port=None):
    """mpremote's REPL on the board, where the person sees the firmware print `ready`."""
    return runnable(shell) + (["connect", port] if port else []) + ["repl"]


def plan(project, port=None, ignore_older_runs=False):
    """
    (the flash commands, the watch command, notes) for this project. Nothing runs here. A DeployProblem or a
    tools.ToolProblem says why the image cannot go on the board yet: what costs nothing is checked before the tools.
    A run log that tested another image refuses the flash, unless `ignore_older_runs` makes it a note.
    """
    image = image_of(project)
    runs = project / "sim" / "runs"  # run_scenario.py writes every log here, in whichever sub-folder of sim/ the image is
    why = untested(image, runs)
    if why:
        raise DeployProblem(why)
    other = tested_another(image, runs)
    if other and not ignore_older_runs:
        raise DeployProblem(other + OLDER_RUNS_WAY_OUT)
    chip = chip_of(project)
    flasher, shell = tools.find("flasher", project), tools.find("board-shell", project)
    changed = newer_files(project, image)
    notes = ["%s changed after this image was made: the board gets the image that passed, not the change. Run its "
             "scenario again to test it." % ", ".join(changed)] if changed else []
    notes += [other] if other else []
    return flash_commands(flasher, chip, image, port), watch_command(shell, port), notes


def main(argv=None, run=None):
    """Print the flash commands (--dry-run) or run them, erase first. `run` is how a command runs. Returns the exit code."""
    parser = argparse.ArgumentParser(prog="deploy.py", description=__doc__.strip().split("\n\n")[0], epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder with sim/ and requirements.json (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Omitted, esptool tries each port")
    parser.add_argument("--ignore-older-runs", action="store_true",
                        help="flash even when a log in sim/runs/ tested another image, and name it in a note "
                        "(default: refuse)")
    parser.add_argument("--dry-run", action="store_true", help="print each command and run nothing")
    args = parser.parse_args(argv)
    run = run or subprocess.run
    try:
        commands, watch, notes = plan(args.project, args.port, args.ignore_older_runs)
    except (DeployProblem, tools.ToolProblem) as cannot:
        print("deploy.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    for note in notes:
        print("  note: %s" % note)
    for command in commands:
        if args.dry_run:
            print("  would run: %s" % shlex.join(command))
            continue
        print("  running: %s" % shlex.join(command), flush=True)
        try:
            run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as failed:
            print("deploy.py: `%s` failed (%s): %s" % (shlex.join(command), failed, BOOT_HINT), file=sys.stderr)
            return EXIT_COULD_NOT_RUN
    print("  " + WATCH % shlex.join(watch))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
