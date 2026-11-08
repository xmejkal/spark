#!/usr/bin/env python3
"""
Import a project's firmware on the Mac, without running main.py (P59, #7).

    import_firmware.py [PROJECT] [--json] [--timeout SECONDS]

Example, in a project after `/spark:build` and the firmware are written:

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/import_firmware.py"

It imports each PROJECT/firmware/*.py and each package there (a folder holding __init__.py) except the boot files,
main.py and boot.py. PROJECT defaults to `.`. Each import is a process of its own, with spark's machine stand-in first on
sys.path, then firmware/ and firmware/lib, where MicroPython looks for drivers. The stand-ins are in scripts/spark/firmware/stand_in/:
`machine` (a Pin that remembers its level, a PWM that keeps its last frequency and duty, and an ADC, SPI, SoftSPI, I2C,
SoftI2C and I2S that keep their arguments and return fixed values), `micropython` and `framebuf`. A driver that ships
its own `framebuf.py` or `micropython.py` in firmware/ or firmware/lib gets its own, because those two stand-ins come
last on sys.path. Per module the answer is one of:
  - imported;
  - raised: the exception's last line, which names the stand-in and the first name it lacks, for example UART;
  - timed out: it did not return within the timeout (5 s by default). Something at module level loops or waits.
    Put it in a function that main.py calls.

An `imported` proves that the names exist and the module-level calls ran. It does not prove that their arguments are
right (the stand-ins take any), that a pin, a wire, a rate or a driver works, or that a device answers: a bus finds no
device, so a module-level `assert 0x3C in i2c.scan()` fails here. Keep such a check in a function that main.py calls.
A name a stand-in lacks is an AttributeError, so a driver's `hasattr(machine, "X")` probe is False. `from machine import X`
is an ImportError with the stand-in file and the action, because the child gives the stand-in's words back (P443).
A driver that sleeps in its constructor imports, because the child gives `time` MicroPython's sleep_ms, sleep_us, ticks_ms,
ticks_us, ticks_add and ticks_diff with fixed values (P443, see import_child.py). A sleep never waits, and ticks_ms() is
always 0, so a driver's wait loop on it times out here.

The boot files are left unrun on purpose: main.py starts the loop, so a two-line main.py over an importable module is
the shape that can be tested. When firmware/ holds nothing to import but the boot files and pins.py, that is a
problem, not a pass: the firmware cannot be imported without running main.py, so move the code out of main.py into a
module that main.py calls. No firmware/ folder is could-not-run.

Exit 0: every module imported; 1: one did not, or there is nothing to import; 2: no firmware/ folder to look in.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.firmware.import_probe import look  # noqa: E402
from spark.core.outcomes import EXIT_FOR, answer  # noqa: E402

#: How long one module may take to import, unless --timeout says.
DEFAULT_TIMEOUT_S = 5.0


def render(result):
    """The text answer: a line per module, then the `-` problems and `!` unchecked lines of the other scripts."""
    lines = ["%-9s %s%s" % (entry["status"], entry["module"], "  " + entry["detail"] if entry["detail"] else "")
             for entry in result["modules"]]
    lines += ["- " + problem for problem in result["problems"]] + ["! " + gap for gap in result["unchecked"]]
    return "\n".join(lines + [result["status"]])


def main(argv=None):
    parser = argparse.ArgumentParser(prog="import_firmware.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", nargs="?", default=".", help="the project folder (default: .)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S, metavar="SECONDS",
                        help="how long one module may take to import (default: %g)" % DEFAULT_TIMEOUT_S)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    modules, problems, unchecked = look(Path(args.project), args.timeout)
    result = dict(answer(problems, unchecked), tool="import_firmware", modules=modules)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return EXIT_FOR[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
