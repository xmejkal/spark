#!/usr/bin/env python3
"""
Put a tested flash image onto the board on USB (P192).

Its `--help` sentence and paragraphs are DeployImage's (P855), and EPILOG is the CLI's own text.

    deploy.py --dry-run                          # in the project folder: print what it would run, run nothing
    look.py                                      # read the board on USB and print its token
    deploy.py --token 3f9a-0c1e                  # look again, ask yes in your terminal, erase, then write the image
    deploy.py --no-simulation --token 3f9a-0c1e  # the same for an image no simulation tested (--help)

The image is the one the `firmware = ` line of sim/wokwi.toml names. A build writes that line as a comment, so until
a scenario run writes it, the image is sim/flash-with-firmware.bin. run_scenario.py writes the image, MicroPython and the project's firmware/ in one
flash image, and tests it: each run's log names the image's sha256. This flashes the image only when a run that passed
names it and no run with another verdict does. esptool erases the flash and writes the image at 0x0, where the
simulator loaded it. Then deploy.py copies a facts file, spark.json, to the board and reads it back (board_facts.py,
P215), and reads the board with mpremote (ready_probe.py): each file's sha256, then the firmware's start, which prints
`ready` (the ready contract, commands/build.md). The board's log goes to sim/runs/board/, and the store keeps a record
of the board by its MAC.

Before the erase, deploy.py looks at the board as look.py does (P219). Before that read it asks the board question of
look.py for a board that spark cannot tell, and stops for another board or a project that keeps no board (P892). It
refuses a stop, a token that is not this board's and this image's, and a deploy with no yes: one typed in the person's own terminal, or the standing yes of a
deploy grant (deploy_gate.py, board_grant.py). The chip comes from
the project's board (requirements.json's `board`), and esptool refuses a board with another chip too.
When each of the five stages starts (plan, look, gate, flash, verify), deploy.py prints one `why:` line that says why
the stage happens (P476). With --json these lines go to stderr, like every line a person reads.
esptool and mpremote are the tools list's `flasher` and `board-shell`, which /spark:setup installs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.deploy_image import DeployImage
from spark.core.cli import HelpText, run_cli
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_OK  # noqa: F401  (the tests read deploy's exit codes here)

#: The CLI's own text in `--help`, after DeployImage's details (P855): its --json, its exit codes, and the stages'
#: `why:` lines, which follow the exit codes, so they stay here and `--help` stays as it was.
EPILOG = """--json prints one envelope on stdout (docs/guide/agents/json.md): the token, the look, the stage the run reached, the
yes, the board log and the store record in `data`, and in `next` the step that waits for the person (`needs_yes`). Every
line above then goes to stderr, and so does the flash tool's own output. Exit codes do not change; the envelope's status
is the exit code's. Every `problems` and `unchecked` item has a `code` (scripts/spark/bench/board_codes.py). A bad flag
with --json prints an envelope (status could-not-run, code bad_argument, exit 2); without --json it prints the usage and
the error on stderr and exits 2.

Exit codes: 0 ready seen (with --dry-run: printed), 1 the look found a stop, or the board's files differ or no `ready`
came, 2 it could not run, you answered no, the board question waits for a reply (needs_reply), the board is not the
kept one (other_board) or none is kept (no_known_board), there was no terminal, or ready is unknown, and the sentence says why.

Each stage prints a `why:` line when it starts (plan, look, gate, flash, verify)."""


def main(argv=None, outside=None, operation=None):
    """Print the flash commands (--dry-run) or look, pass the gate and run them, erase first. `outside` is the OutsideWorld
    a test gives (a run builds the project's), `operation` the DeployImage a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("deploy.py", epilog=EPILOG), operation or DeployImage(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
