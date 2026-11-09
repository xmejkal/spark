#!/usr/bin/env python3
"""
Run one scenario of a built project in Wokwi, and keep a log of the run with its date (P130).

    run_scenario.py sim/scenarios/<name>.scenario.yaml        # in the project folder, after /spark:build --keep .

The ready contract: the firmware prints `ready` once its setup is done, and nothing else containing that word before.
This adds a wait for the first serial text containing `ready` before the scenario's first step, because a step sent
earlier reaches a board that is still booting. So a scenario holds only behaviour: the conversation writes it from the
person's words, and spark ships none.

A run spends Wokwi CI minutes, so every check that costs nothing comes first: the simulation project, firmware/main.py,
the scenario's steps, the component ids its steps name against sim/diagram.json, littlefs, MicroPython and the image's
place. Only then the tool, the token and the paid run. A step whose id cannot be read, or a diagram that cannot be read,
prints `not checked` and the run goes on (P399).

Each run puts MicroPython and the project's firmware/ into a new flash image, so a run never tests an older firmware. When
the build named no image (no --firmware), a real run names flash-with-firmware.bin in sim/wokwi.toml, as --firmware would
have: wokwi-cli refuses a wokwi.toml that names none.

--dry-run makes the free checks alone: it needs no token, starts no run and writes nothing (P399).

A step's own `name:` key may hold a must line of the brief (copied exactly): the log's header names every step (P345),
and the look lists the must lines that no passed scenario named.

The log goes to sim/runs/<name>.log: the date with its zone, the verdict, the step counts by kind and the step names
(P345), the sha256 of the image it tested and of each file in that image, what the simulation cannot show, the scenario
as run, and what wokwi-cli printed, which is the board's serial output among the scenario's progress. deploy.py reads
the verdict and the sha256s from the log's header (run_record, file_hashes). The tests use a fake wokwi-cli.

A pass whose scenario has no set-control step prints the look's rule in its own words, "passed, but it has no set-control
step (...)", and one whose steps cannot be counted prints "passed, but its steps were not counted: <why>" (P485). The log's
verdict stays `passed`.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.firmware.scenario_run import DEFAULT_TIMEOUT_MS, ScenarioRun, free_checks
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_FOR, OK
from spark.core.text_guards import guard_lines

#: What --help says beyond the arguments: the cost, the token, the contract and the exit codes.
EPILOG = """A run spends Wokwi CI minutes: ask the person before each run, whatever your permissions allow.
It needs a Wokwi CI token (wokwi.com/dashboard/ci) in WOKWI_CLI_TOKEN: export WOKWI_CLI_TOKEN=...
The firmware must print `ready` once its setup is done (the ready contract, commands/build.md).

--dry-run makes the same free checks: it needs no token, starts no run and writes nothing.

Exit codes: 0 the scenario passed (with --dry-run, the free checks passed), 1 it failed, 2 it could not run. The log is sim/runs/<name>.log."""

#: The arguments: (flags, what argparse needs for them).
ARGUMENTS = (
    (("scenario",), {"type": Path, "help": "the scenario file, relative to the project: sim/scenarios/<name>.scenario.yaml"}),
    (("--project",), {"type": Path, "default": Path("."), "help": "the project folder with sim/ and firmware/ (default: here)"}),
    (("--timeout-ms",), {"type": int, "default": DEFAULT_TIMEOUT_MS, "help": "simulated time the run may take"}),
    (("--micropython",), {"type": Path, "help": "the interpreter .bin; omitted, the one /spark:setup downloads"}),
    (("--dry-run",), {"action": "store_true", "help": "make the free checks only: no token, no run, nothing written"}),
)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="run_scenario.py", description=__doc__.strip().split("\n\n")[0],
                                     epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flags, options in ARGUMENTS:
        parser.add_argument(*flags, **options)
    args = parser.parse_args(argv)
    run = ScenarioRun(args.project, args.scenario, args.micropython, args.timeout_ms)
    if args.dry_run:  # before the unlink: a dry run leaves an older log in place
        status, said = run.dry_run()
        print(guard_lines("\n".join(map(str, said))), file=sys.stdout if status == OK else sys.stderr)
        return EXIT_FOR[status]
    run.log.unlink(missing_ok=True)  # an older run's verdict must not outlive a run refused here
    simulator, said = free_checks(run, args.project)
    if said:
        print(guard_lines("\n".join("run_scenario.py: %s" % each for each in said)), file=sys.stderr)
    if simulator is None:
        return EXIT_COULD_NOT_RUN
    status, sentence, log = run.run(simulator.command)
    print(guard_lines("%s: %s%s" % (args.scenario.name, sentence, "\nlog: %s" % log if log else "")),
          file=sys.stdout if status == OK else sys.stderr)  # the log file in sim/runs keeps the raw text
    return EXIT_FOR[status]


if __name__ == "__main__":
    sys.exit(main())
