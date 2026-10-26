#!/usr/bin/env python3
"""
Put the flash image onto the board: one that a passed run names (P192), or, with --no-simulation, firmware/ (P337).

    deploy.py --dry-run                          # in the project folder: print what it would run, run nothing
    look.py                                      # read the board on USB and print its token
    deploy.py --token 3f9a-0c1e                  # look again, ask yes in your terminal, erase, then write the image
    deploy.py --no-simulation --token 3f9a-0c1e  # the same for an image no simulation tested (--help)

The image is the one sim/wokwi.toml names. run_scenario.py writes it, MicroPython and the project's firmware/ in one
flash image, and tests it: each run's log names the image's sha256. This flashes the image only when a run that passed
names it and no run with another verdict does. esptool erases the flash and writes the image at 0x0, where the
simulator loaded it. Then deploy.py copies a facts file, spark.json, to the board and reads it back (board_facts.py,
P215), and reads the board with mpremote (ready_check.py): each file's sha256, then the firmware's start, which prints
`ready` (the ready contract, commands/build.md). The board's log goes to sim/runs/board/, and the store keeps a record
of the board by its MAC.

Before the erase, deploy.py looks at the board as look.py does (P219). It refuses a stop, a token that is not this
board's and this image's, and a deploy with no yes: one typed in the person's own terminal, or the standing yes of a
deploy grant (deploy_gate.py, board_grant.py). The chip comes from
the project's board (requirements.json's `board`), and esptool refuses a board with another chip too.
esptool and mpremote are the tools list's `flasher` and `board-shell`, which /spark:setup installs.
"""

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

import board_doctor
import board_envelope
import board_grant
import board_look
import boards
import deploy_gate
import download_mode
import ready_check
import store
import tools
from board_console import LEAVE_CONSOLE
from deploy_service import DeployService, FlashError
from firmware_platform import FirmwarePlatform
from image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_CAVEAT, NO_SIMULATION_FLAG, evidence_for
from project_image import DeployError
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS

#: The line after a deploy that names the image on the board and whose yes erased it (P213, card A).
DEPLOYED_LINE = "image sha256: %s, yes: %s"
#: The last line: how the person sees the firmware start.
WATCH = ("then, to see it start: %%s, press Ctrl-C, then Ctrl-D: the firmware prints `ready`. Then %s: an open "
         "console holds the port, and the next deploy cannot open it" % LEAVE_CONSOLE)
#: What --help says beyond the arguments.
EPILOG = """It flashes only an image that a passed run names (sim/runs/*.log), and no log there may name another image
(--ignore-older-runs flashes anyway).

--no-simulation flashes an image that no simulation tested, as the board is the test. Build the image first with
`flash_image.py --project . --files firmware -o <the image sim/wokwi.toml names>`. Then look.py and deploy.py both need
--no-simulation. deploy.py refuses when firmware/main.py is missing, a .py file under firmware/ does not compile, a run
in sim/runs/ failed on this image, or the image is not firmware/ as it is now. It does not run the firmware, so a
firmware that fails on the board shows only after the flash. The question starts with "%s", only a typed yes
answers it (a deploy grant never does), and the spark.json, the board log, the store record and the --json data say
`simulation: none`. It cannot be given with --ignore-older-runs.

It erases the board's flash first. If the erase stops with esptool's exit 2,
it makes one retry after 5 s and prints `retry in 5 s: ...` (P290).

The gate: run look.py first and pass its token. deploy.py looks at the board again (the board restarts) and refuses a
stop (another chip, a flash too small for the image) or a token that is not this board's and this image's. Then it
asks in your terminal, naming every warning: type yes to accept them and erase. Only a real terminal can answer.
A pipe, a script or Claude Code's ! is none, so deploy.py prints the line to run in your own terminal window. "Go
ahead" in a chat is not the yes, and the token is not the yes. --dry-run never touches USB: it does not look.

The one other yes is a deploy grant: you ran `grant.py --scope deploy --minutes N` once in your own terminal, for this
board's MAC. While it lasts, deploy.py takes it as the yes, prints `yes: standing yes typed by ...` and erases with no
question, but only when the look matched the board record (no warning, no unknown field, no stop) and neither
--ignore-older-runs nor --no-simulation is given. Then the token and the check that the image did not change still hold.
For anything else, or with no grant or an ended one, deploy.py asks in the terminal as above and says why it did not use
the grant. The grant covers any passed image of any project on that board. The store's record names whose yes it was.

After the flash it copies spark.json to the board: spark's version, the project, the board type, the MAC, the image's
sha256, each file's sha256 and `simulation` (passed or none). The board log names the file's sha256 and the simulation,
and the store's boards/<MAC>.json adds this deploy with its verdict, its simulation and whose yes it was. Then it reads
the board: ready seen means the board's files match the evidence's sha256s and the firmware printed `ready` within %d s.
The board's log goes to sim/runs/board/. A firmware that stops with an error is not seen. If mpremote cannot reach the
board, for example because its port changed after the flash, or the passed run's log is from before P215 and names no
files, ready is unknown, never seen. If ready is unknown and the passed log names files, deploy.py reads the port with
DTR and RTS off. If it reads `waiting for download`, the board waits in its download mode: deploy.py asks you to press
the board's RESET once (with its place when the board record has it), waits %d s for the port to go and come back under
the same name, and reads the board again. If it reads the firmware's `ready`, the board finished its restart late, and
deploy.py reads it again at once. What the port printed, `nothing`, or why it could not be read goes in the board log.

--json prints one envelope on stdout (docs/guide/agents.md): the token, the look, the stage the run reached, the yes, the
board log and the store record in `data`, and in `next` the step that waits for the person (`needs_yes`). Every line above
then goes to stderr, and so does the flash tool's own output. Exit codes do not change; the envelope's status is the exit
code's. An argument error prints usage on stderr and no envelope.

Exit codes: 0 ready seen (with --dry-run: printed), 1 the look found a stop, or the board's files differ or no `ready`
came, 2 it could not run, you answered no, there was no terminal, or ready is unknown, and the sentence says why.""" % (
    NO_SIMULATION_CAVEAT, ready_check.READY_WAIT_S, download_mode.RESET_WAIT_S)


def rerun_line(args, port, evidence):
    """The line that runs this deploy again, for the person's own terminal."""
    return deploy_gate.format_rerun_line(__file__, board_envelope.deploy_argv(args.project.resolve(), args.token, port,
                                                                            evidence))


def grant_argv(args, port, minutes="N"):
    """The arguments of grant.py that give a deploy grant for this board."""
    return ["--scope", board_grant.SCOPE_DEPLOY, "--minutes", minutes, "--project", str(args.project.resolve()), "--port", port]


def grant_hint(args, port):
    """The text added to the no-terminal line when a deploy grant could make the yes unnecessary: the line the person
    runs once in their own terminal to give it."""
    line = deploy_gate.format_rerun_line(Path(__file__).resolve().with_name("grant.py"), grant_argv(args, port))
    return ("\nOr, to let Claude deploy this board for N minutes (1 to 1440) with no yes each time, run this once. It "
            "allows an erase of ALL of the flash and any passed image of any project:\n  %s" % line)


def choose_consent(args, report, grant_service, evidence, out=None):
    """The ConsentStrategy for this deploy, after the look: the standing yes of a valid deploy grant when the look
    matched and the evidence allows it (a passed run's, with no ignored older run), else a yes typed in this terminal.
    Prints one line that says which, and why not when it is the terminal."""
    line = rerun_line(args, report.port, evidence)
    if board_grant.grant_may_cover(report, evidence):
        line += grant_hint(args, report.port)
    chosen = grant_service.consent_for_deploy(report, evidence, deploy_gate.TerminalConsentStrategy(line, stdout=out))
    if chosen.why not in (None, board_grant.WHY_NO_GRANT):  # a person with no grant is told only by the no-terminal text
        said = board_grant.DEPLOY_MESSAGE_FOR.get(chosen.why) or board_grant.MESSAGE_FOR[chosen.why]
        print("  standing yes: not used: %s" % said, flush=True, file=out)
    return chosen.consent


def show_line(line, out=None):
    """How the service's lines reach the person: printed at once, because a step is still running."""
    print(line, flush=True, file=out)


def main(argv=None, run=None, consent=None, probe=None, clock=None, grant_service=None):
    """
    Print the flash commands (--dry-run) or look, pass the gate and run them, erase first. `run` is how a command runs,
    `consent` how the person says yes (default: in this terminal), `probe` how a board in download mode is found
    (default: board_console.ConsoleProbe), `clock` how the time is read (default: board_grant.read_local_time, called once),
    `grant_service` the board_grant.GrantService that finds a deploy grant (default: the store's). A `consent` given always
    wins: the grant is read only when none is given. Returns the exit code.
    """
    parser = argparse.ArgumentParser(prog="deploy.py", description=__doc__.strip().split("\n\n")[0], epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder with sim/ and requirements.json (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on "
                        "USB: the look lists them")
    parser.add_argument("--token", help="the token look.py printed for this board and this image")
    which = parser.add_mutually_exclusive_group()
    which.add_argument(IGNORE_OLDER_RUNS_FLAG, action="store_true",
                       help="flash even when a log in sim/runs/ tested another image, and name it in a note "
                       "(default: refuse)")
    which.add_argument(NO_SIMULATION_FLAG, action="store_true",
                       help="flash an image that no simulation tested: firmware/ must have a main.py, compile and be "
                       "what the image holds. Needs look.py --no-simulation. The person's typed yes names the caveat")
    parser.add_argument("--dry-run", action="store_true", help="print each command and run nothing")
    parser.add_argument("--json", action="store_true", help="print one envelope on stdout, the lines a person reads on "
                        "stderr (docs/guide/agents.md)")
    args = parser.parse_args(argv)
    evidence = evidence_for(args.project, args.no_simulation, args.ignore_older_runs)
    reached = {"project": args.project.resolve(), "token": args.token, "port": args.port, "stage": board_envelope.STAGE_PLAN,
            "evidence": evidence, "dry_run": args.dry_run}
    code = _deploy(args, evidence, run or subprocess.run, consent, probe, clock, grant_service, sys.stderr if args.json else None, reached)
    if args.json:
        print(board_envelope.dumps(board_envelope.deploy_envelope(reached, code)))
    return code


def who_said_yes(consent):
    """Whose yes it was, as a phrase, read once. getpass can find no user (OSError since Python 3.13, KeyError before
    it), and then the phrase says so; the store record names the error itself."""
    try:
        return consent.who
    except (OSError, KeyError) as cannot:
        return "not known (%s)" % cannot


def _deploy(args, evidence, run, consent, probe, clock, grant_service, out, reached):
    """The deploy main parses for. Every line a person reads goes to `out` (None: stdout). What `--json` reports it puts in
    `reached`. Returns the exit code."""
    def say(line):
        print(line, file=out)

    service = DeployService(args.project, FirmwarePlatform.micropython(args.project), evidence, run,
                            clock, probe, echo_to=None if out is None else 2)
    try:
        planned = service.plan(args.port)
    except (DeployError, tools.ToolProblem) as cannot:
        reached["refusal"] = str(cannot)
        print("deploy.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    reached["plan"] = planned
    for note in planned.notes:
        say("  note: %s" % note)
    if args.dry_run:
        say("\n".join("  would run: %s" % shlex.join(command) for command in planned.commands))
        say("  board: not looked at: run look.py")
        say("  " + WATCH % shlex.join(service.platform.make_connection(planned.mpremote, args.port).repl_command()))
        return EXIT_OK
    try:
        reached["stage"] = board_envelope.STAGE_LOOK
        report = reached["report"] = service.look(args.port)
        print("\n".join(board_look.report_lines(report, token=False)), flush=True, file=out)
        reached["port"] = report.port
        consent = consent or choose_consent(args, report, grant_service or board_grant.GrantService(), evidence, out)
        yes_kind = "grant" if isinstance(consent, board_grant.StandingConsentStrategy) else "typed"
        reached["stage"] = board_envelope.STAGE_GATE
        planned = service.deploy(report, args.token, consent, lambda line: show_line(line, out))
        # the gate is passed: only now is there a yes to report
        reached.update(consent=consent, yes_kind=yes_kind, who=who_said_yes(consent))
    except (board_look.LookStop, DeployError, tools.ToolProblem) as cannot:
        if isinstance(cannot, FlashError):
            reached.update(stage=board_envelope.STAGE_FLASH, consent=consent, yes_kind=yes_kind,
                           who=who_said_yes(consent))
        reached["refusal"] = str(cannot)
        lines = ["deploy.py: %s" % cannot]
        if isinstance(cannot, board_look.LookStop):  # P354: a failed read gets the doctor, a busy port its step
            lines, reached["doctor"] = board_doctor.stop_answer("deploy.py", cannot, args.project, run)
        print("\n".join(lines), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    except deploy_gate.GateClosedError as shut:
        reached.update(refusal=str(shut), next_op=shut.next_op)
        if shut.next_op == deploy_gate.NEXT_DEPLOY:
            reached["run_in_terminal"] = rerun_line(args, report.port, evidence)
            if board_grant.grant_may_cover(report, evidence):
                reached["grant_argv"] = grant_argv(args, report.port, "60")
        print("deploy.py: %s" % shut, file=sys.stderr)
        return shut.code
    reached["stage"] = board_envelope.STAGE_VERIFY
    result = reached["result"] = service.verify(report, planned, lambda line: show_line(line, out))
    ready = result.ready
    reached["person_action"] = download_mode.press_reset(boards.ButtonPlaces.of_project(args.project))
    if ready.verdict != ready_check.SEEN:
        reached["refusal"] = ready.sentence
    who = reached["who"]
    say("  %s\n  %s\n  %s: %s\n  board log: %s" % (result.facts_line, DEPLOYED_LINE % (result.image_sha256, who),
                                                ready.verdict, ready.sentence, result.log_path))
    try:
        reached["store_record"] = str(service.record(result, consent))
        say("  store record: %s" % reached["store_record"])
    except (OSError, KeyError, store.StoreProblem) as cannot:  # KeyError: getpass before Python 3.13
        reached["store_record_error"] = str(cannot)
        reached["notes"] = ["the store record was not written: %s" % cannot]
        say("  store record: not written: %s" % cannot)
    if ready.verdict == ready_check.UNKNOWN:
        say("  " + WATCH % shlex.join(result.repl_command))
        return EXIT_COULD_NOT_RUN
    return EXIT_OK if ready.verdict == ready_check.SEEN else EXIT_PROBLEMS


if __name__ == "__main__":
    sys.exit(main())
