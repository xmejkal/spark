#!/usr/bin/env python3
"""
Put the flash image that passed the simulation onto the board (P192).

    deploy.py --dry-run                          # in the project folder: print what it would run, run nothing
    look.py                                      # read the board on USB and print its token
    deploy.py --token 3f9a-0c1e                  # look again, ask yes in your terminal, erase, then write the image

The image is the one sim/wokwi.toml names. run_scenario.py writes it, MicroPython and the project's firmware/ in one
flash image, and tests it: each run's log names the image's sha256. This flashes the image only when a run that passed
names it and no run with another verdict does. esptool erases the flash and writes the image at 0x0, where the
simulator loaded it. Then deploy.py copies a facts file, spark.json, to the board and reads it back (board_facts.py,
P215), and reads the board with mpremote (ready_check.py): each file's sha256 against the passed run's log, then the
firmware's start, which prints `ready` (the ready contract, commands/build.md). The board's log goes to
sim/runs/board/, and the store keeps a record of the board by its MAC.

Before the erase, deploy.py looks at the board as look.py does (P219). It refuses a stop, a token that is not this
board's and this image's, and a person who does not type yes in their own terminal (deploy_gate.py). The chip comes from
the project's board (requirements.json's `board`), and esptool refuses a board with another chip too.
esptool and mpremote are the tools list's `flasher` and `board-shell`, which /spark:setup installs.
"""

import argparse
import collections
import datetime
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

import board_facts
import board_connection
import board_look
import ready_check
import boards
import deploy_gate
import board_console
import download_mode
import look
import store
import tools
from image_check import (BOOT_HINT, DeployProblem, image_of, passed_log, run_logs, runnable,  # noqa: F401
                         tested_another, untested)
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS
from run_scenario import file_hashes

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

The gate: run look.py first and pass its token. deploy.py looks at the board again (the board restarts) and refuses a
stop (another chip, a flash too small for the image) or a token that is not this board's and this image's. Then it
asks in your terminal, naming every warning: type yes to accept them and erase. Only a real terminal can answer.
A pipe, a script or Claude Code's ! is none, so deploy.py prints the line to run in your own terminal window. "Go
ahead" in a chat is not the yes, and the token is not the yes. --dry-run never touches USB: it does not look.

After the flash it copies spark.json to the board: spark's version, the project, the board type, the MAC, the image's
sha256 and each file's sha256. The board log names the file's sha256, and the store's boards/<MAC>.json adds this
deploy with its verdict and whose yes it was. Then it reads the board: ready seen means the board's files match the
passed run's sha256s and the firmware printed `ready` within %d s. The board's log goes to sim/runs/board/. A firmware
that stops with an error is not seen. If mpremote cannot reach the board, for example because its port changed after
the flash, or the passed run's log is from before P215 and names no files, ready is unknown, never seen.
If ready is unknown and the passed log names files, deploy.py reads the port with DTR and RTS off. If it reads `waiting for download`, the
board waits in its download mode: deploy.py asks you to press the board's R (reset) button once, waits %d s for the
port to go and come back under the same name, and reads the board again. If it reads the firmware's `ready`, the
board finished its restart late, and deploy.py reads it again at once. What the port printed, `nothing`, or why it could
not be read goes in the board log.

Exit codes: 0 ready seen (with --dry-run: printed), 1 the look found a stop, or the board's files differ or no `ready`
came, 2 it could not run, you answered no, there was no terminal, or ready is unknown, and the sentence says why.""" % (
    ready_check.READY_WAIT_S, download_mode.RESET_WAIT_S)


def newer_files(project, image):
    """The files under firmware/ changed after the image was made, as project paths. The board gets the image, not them."""
    made = image.stat().st_mtime
    return sorted(str(path.relative_to(project)) for path in (project / "firmware").rglob("*")
                  if path.is_file() and "__pycache__" not in path.parts and path.stat().st_mtime > made)


def board_of(project):
    """The project's board type, requirements.json's `board` (D35)."""
    return json.loads((project / "requirements.json").read_text()).get("board")


def chip_of(project):
    """The board's chip as esptool names it, from requirements.json's board (P192: no chip table)."""
    requirements = project / "requirements.json"
    try:
        return boards.get(project, "chip", board_of(project))
    except (OSError, ValueError, AttributeError, boards.BoardError) as cannot:
        raise DeployProblem("the board's chip cannot be read from %s: %s" % (requirements, cannot))


def flash_commands(flasher, chip, image, port=None):
    """esptool's two commands: erase the board's flash, then write the image at IMAGE_OFFSET."""
    base = runnable(flasher) + ["--chip", chip] + (["--port", port] if port else [])
    return [base + [ERASE], base + [WRITE, IMAGE_OFFSET, str(image)]]


#: Result: what `plan` returns. `commands` are the two flash commands, `mpremote` is mpremote's command, and `notes` are
#: sentences for the person.
DeployPlan = collections.namedtuple("DeployPlan", "commands mpremote notes")


class BoardLog(collections.namedtuple("BoardLog", "moment port image_sha256 facts_line verdict sentence heard")):
    """Value: the facts of the board's log after a flash. `heard` is the console text, then what the board printed."""

    def text(self):
        """The log file's text."""
        return "# deploy %s on %s\nimage sha256: %s\n%s\n%s: %s\n\n%s\n" % (
            self.moment.isoformat(timespec="seconds"), self.port, self.image_sha256, self.facts_line, self.verdict,
            self.sentence, self.heard)


def write_board_log(project, log, moment):
    """The board's log (a BoardLog) in sim/runs/board/ beside the run logs, whose *.log glob does not reach it. Returns
    its path."""
    path = project / "sim" / "runs" / "board" / ("%s.log" % moment.strftime("%Y-%m-%dT%H-%M-%S"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(log.text())
    return path


def put_facts(project, report, connection, expected, moment):
    """(the facts, the board log's line about the facts file): copied to the board and read back (D22)."""
    said = board_facts.facts(project, board_of(project), report.reading.mac, image_of(project), expected, moment)
    why = board_facts.FactsFile(connection).write(said)
    if why:
        return said, "facts file: not written: %s" % why
    return said, "facts file %s sha256: %s" % (board_facts.FACTS_FILE,
                                              hashlib.sha256(board_facts.facts_text(said).encode()).hexdigest())


def plan(project, port=None, ignore_older_runs=False):
    """
    A DeployPlan (the flash commands, mpremote's command, notes) for this project. Nothing runs here. A DeployProblem or a
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
    flasher, mpremote = tools.find("flasher", project), tools.find("board-shell", project)
    changed = newer_files(project, image)
    notes = ["%s changed after this image was made: the board gets the image that passed, not the change. Run its "
             "scenario again to test it." % ", ".join(changed)] if changed else []
    notes += [other] if other else []
    return DeployPlan(flash_commands(flasher, chip, image, port), runnable(mpremote), notes)


def rerun_line(args, port):
    """The line that runs this deploy again, for the person's own terminal."""
    line = ["--project", args.project.resolve(), "--token", args.token or "", "--port", port]
    return deploy_gate.format_rerun_line(__file__, line + (["--ignore-older-runs"] if args.ignore_older_runs else []))


def read_board(project, report, connection, expected, moment):
    """(the facts, the facts line, a ReadyResult) after a flash: the facts, then ready."""
    facts, facts_line = put_facts(project, report, connection, expected, moment)
    return facts, facts_line, ready_check.ReadyCheck(connection).check(expected)


def main(argv=None, run=None, consent=None, probe=None, clock=None):
    """
    Print the flash commands (--dry-run) or look, pass the gate and run them, erase first. `run` is how a command runs,
    `consent` how the person says yes (default: in this terminal), `probe` how a board in download mode is found
    (default: board_console.ConsoleProbe), `clock` how the time is read (default: datetime.datetime.now, called once).
    Returns the exit code.
    """
    parser = argparse.ArgumentParser(prog="deploy.py", description=__doc__.strip().split("\n\n")[0], epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder with sim/ and requirements.json (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on "
                        "USB: the look lists them")
    parser.add_argument("--token", help="the token look.py printed for this board and this image")
    parser.add_argument("--ignore-older-runs", action="store_true",
                        help="flash even when a log in sim/runs/ tested another image, and name it in a note "
                        "(default: refuse)")
    parser.add_argument("--dry-run", action="store_true", help="print each command and run nothing")
    args = parser.parse_args(argv)
    run = run or subprocess.run
    try:
        planned = plan(args.project, args.port, args.ignore_older_runs)
    except (DeployProblem, tools.ToolProblem) as cannot:
        print("deploy.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    for note in planned.notes:
        print("  note: %s" % note)
    if args.dry_run:
        print("\n".join("  would run: %s" % shlex.join(command) for command in planned.commands))
        print("  board: not looked at: run look.py")
        print("  " + WATCH % shlex.join(board_connection.BoardConnection(planned.mpremote, args.port).repl_command()))
        return EXIT_OK
    try:
        report = board_look.looker(args.project, run).run(args.project, args.port, args.ignore_older_runs)
        print("\n".join(look.lines(report, token=False)), flush=True)
        consent = consent or deploy_gate.TerminalConsentStrategy(rerun_line(args, report.port))
        deploy_gate.require_open_gate(report, args.token, consent, image_of(args.project).relative_to(args.project))
        planned = plan(args.project, report.port, args.ignore_older_runs)
        if report.token() != args.token:  # AT116: the image changed while the person answered
            raise DeployProblem("the image changed after your yes: run look.py again. not flashed.")
    except (board_look.LookStop, DeployProblem, tools.ToolProblem) as cannot:
        print("deploy.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    except deploy_gate.GateClosedError as shut:
        print("deploy.py: %s" % shut, file=sys.stderr)
        return shut.code
    for command in planned.commands:
        print("  running: %s" % shlex.join(command), flush=True)
        try:
            run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as failed:
            print("deploy.py: `%s` failed (%s): %s" % (shlex.join(command), failed, BOOT_HINT), file=sys.stderr)
            return EXIT_COULD_NOT_RUN
    image = image_of(args.project)
    passed = passed_log(image, args.project / "sim" / "runs")
    expected = file_hashes(passed) if passed else {}
    connection = board_connection.BoardConnection(planned.mpremote, report.port, run)
    moment = (clock or datetime.datetime.now)()  # once: the facts file and the board log share it
    facts, facts_line, ready = read_board(args.project, report, connection, expected, moment)
    heard = ""
    if ready.verdict == ready_check.UNKNOWN and expected:  # P243: silent after the flash, maybe in download mode
        probe = probe or board_console.ConsoleProbe.for_tool(tools.find("board-shell", args.project),
                                                                    report.port, run)
        if probe:  # P244: what the console said goes in the log, download mode or not
            waits, console = probe.waits_in_download_mode()
            heard = "console with DTR and RTS off: %s\n" % (console.strip() or "nothing")
            if waits:
                print("  %s" % download_mode.PRESS_RESET, flush=True)
                reset = probe.wait_for_reset()
                if reset:
                    facts, facts_line, ready = read_board(args.project, report, connection, expected, moment)
                else:
                    ready = ready._replace(sentence=download_mode.NO_RESET)
                heard += "reset seen\n" if reset else "no reset\n"
            elif download_mode.booted(console):  # P245: mpremote asked while the board still restarted
                facts, facts_line, ready = read_board(args.project, report, connection, expected, moment)
                heard += download_mode.READ_AGAIN + "\n"
    log = write_board_log(args.project, BoardLog(moment, report.port, hashlib.sha256(image.read_bytes()).hexdigest(),
                                                 facts_line, ready.verdict, ready.sentence, heard + ready.log), moment)
    print("  %s\n  %s: %s\n  board log: %s" % (facts_line, ready.verdict, ready.sentence, log))
    try:
        print("  store record: %s" % board_facts.record_deploy(facts, ready.verdict, consent.who))
    except (OSError, store.StoreProblem) as cannot:
        print("  store record: not written: %s" % cannot)
    if ready.verdict == ready_check.UNKNOWN:
        print("  " + WATCH % shlex.join(connection.repl_command()))
        return EXIT_COULD_NOT_RUN
    return EXIT_OK if ready.verdict == ready_check.SEEN else EXIT_PROBLEMS


if __name__ == "__main__":
    sys.exit(main())
