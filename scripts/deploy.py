#!/usr/bin/env python3
"""
Put the flash image onto the board: one that a passed run names (P192), or, with --no-simulation, firmware/ (P337).

    deploy.py --dry-run                          # in the project folder: print what it would run, run nothing
    look.py                                      # read the board on USB and print its token
    deploy.py --token 3f9a-0c1e                  # look again, ask yes in your terminal, erase, then write the image
    deploy.py --no-simulation --token 3f9a-0c1e  # the same for an image no simulation tested (--help)

The image is the one the `firmware = ` line of sim/wokwi.toml names. A build writes that line as a comment, so until
a scenario run writes it, the image is sim/flash-with-firmware.bin. run_scenario.py writes the image, MicroPython and the project's firmware/ in one
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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import download_mode
import ready_check
from image_evidence import NO_SIMULATION_CAVEAT
from spark.bench import build_project_outside_world
from spark.bench.deploy_image import DeployImage
from spark.core.cli import HelpText, run_cli
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_OK  # noqa: F401  (the tests read deploy's exit codes here)

#: What --help says beyond the arguments.
EPILOG = """It flashes only an image that a passed run names (sim/runs/*.log), and no log there may name another image
(--ignore-older-runs flashes anyway).

--no-simulation flashes an image that no simulation tested, as the board is the test. Build the image first with
`flash_image.py --project . --files firmware -o <the image: sim/flash-with-firmware.bin until a scenario run writes
the `firmware = ` line of sim/wokwi.toml>`. Then look.py and deploy.py both need
--no-simulation. deploy.py refuses when firmware/main.py is missing, a .py file under firmware/ does not compile (or kills
the compiler, or takes over 30 s), a run in
sim/runs/ failed on this image, or the image is not firmware/ as it is now. It does not run the firmware, so a
firmware that fails on the board shows only after the flash. The question starts with "%s", only a typed yes
answers it (a deploy grant never does), and the spark.json, the board log, the store record and the --json data say
`simulation: none`. It cannot be given with --ignore-older-runs.

It erases the board's flash first. If the erase stops with esptool's exit 2,
it makes one retry after 5 s and prints `retry in 5 s: ...` (P290).
When the board refuses mpremote's raw REPL for the facts copy after the flash, that copy gets one retry after 2 s (P420).

The gate: run look.py first and pass its token. deploy.py looks at the board again (the board restarts) and refuses a
stop (another chip, a flash too small for the image) or a token that is not this board's and this image's. Then it
asks in your terminal, naming every warning: type yes to accept them and erase. Only a real terminal can answer.
A pipe, a script or Claude Code's ! is none, so deploy.py prints the line to run in your own terminal window. It
starts with SPARK_HOME=<your store> when this run had one, so the new window finds the same MicroPython build and
grants. With --json, each step in `next` carries the same store as `env` for a caller to set. "Go ahead"
in a chat is not the yes, and the token is not the yes. --dry-run never touches USB: it does not look.

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
files, ready is unknown, never seen. The write restarts the chip with esptool's `--after watchdog-reset` (esptool's troubleshooting
page says the ESP32-S3 then leaves download mode; not yet run on a board that was entered with BOOT; the C6 and the classic ESP32 fall
back to a hard reset), and deploy.py finds the board's port again by its MAC,
for the port can change its name and its USB id. If ready is unknown and the passed log names files, deploy.py reads the
look's port with DTR and RTS off, unless that is 303a:4001 (MicroPython's own USB). If it reads `waiting for download`, the board waits in its download mode: deploy.py asks you to
press the board's RESET once (with its place when the board record has it) and waits %d s. A restart counts only when
mpremote answers after it: a restart that left the board in download mode is said and not counted. At the end of the wait
ready is unknown with the code `download_mode_stayed`, or `port_gone` when the port was not listed or did not come back
(then there is no REPL line). If it reads the firmware's `ready`, the board finished its restart late, and deploy.py reads
it again at once. What the port printed, `nothing`, or why it could not be read goes in the board log.

--json prints one envelope on stdout (docs/guide/agents/json.md): the token, the look, the stage the run reached, the yes, the
board log and the store record in `data`, and in `next` the step that waits for the person (`needs_yes`). Every line above
then goes to stderr, and so does the flash tool's own output. Exit codes do not change; the envelope's status is the exit
code's. Every `problems` and `unchecked` item has a `code` (scripts/board_codes.py). A bad flag with --json prints an envelope
(status could-not-run, code bad_argument, exit 2); without --json it prints the usage and the error on stderr and exits 2.

Exit codes: 0 ready seen (with --dry-run: printed), 1 the look found a stop, or the board's files differ or no `ready`
came, 2 it could not run, you answered no, there was no terminal, or ready is unknown, and the sentence says why.""" % (
    NO_SIMULATION_CAVEAT, ready_check.READY_WAIT_S, download_mode.RESET_WAIT_S)




def main(argv=None, outside=None, operation=None):
    """Print the flash commands (--dry-run) or look, pass the gate and run them, erase first. `outside` is the OutsideWorld
    a test gives (a run builds the project's), `operation` the DeployImage a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("deploy.py", __doc__.strip().split("\n\n")[0], EPILOG), operation or DeployImage(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
