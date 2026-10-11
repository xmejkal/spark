#!/usr/bin/env python3
"""
Import a project's firmware on the Mac, without running it (P59, #7).

    import_firmware.py [PROJECT] [--json] [--timeout SECONDS]

Example, in a project after `/spark:build` and the firmware are written:

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/import_firmware.py"

It imports each PROJECT/firmware/*.py (PROJECT defaults to `.`) except main.py, each in a process of its own, with
spark's `machine` stand-in (scripts/stand_in/machine.py: a Pin that remembers its level, nothing else) and
PROJECT/firmware first on sys.path. Per module the answer is one of:
  - imported;
  - raised: the exception's last line, which names the stand-in when the firmware wants more than a Pin;
  - timed out: it did not return within the timeout (5 s by default). Something at module level loops or waits.
    Put it in a function that main.py calls.

main.py is left unrun on purpose: it is the boot file that starts the loop, so a two-line main.py over an importable
module is the shape that can be tested. When firmware/ holds nothing to import but main.py and pins.py, that is a
problem, not a pass: the firmware cannot be imported without running it, so move the code out of main.py into a
module that main.py calls. No firmware/ folder is could-not-run.

Exit 0: every module imported; 1: one did not, or there is nothing to import; 2: no firmware/ folder to look in.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from outcomes import EXIT_FOR, answer  # noqa: E402

STAND_IN = Path(__file__).resolve().parent / "stand_in"
#: The files MicroPython runs at boot, never imported (main.py starts the loop), and the pin map the build writes, which
#: is not firmware someone wrote.
BOOT_FILE, PIN_MAP, PIN_MODULE = "main.py", "pins.py", "pins"
BOOT_FILES = ("boot.py", BOOT_FILE)
DEFAULT_TIMEOUT_S = 5.0
IMPORTED, RAISED, TIMED_OUT = "imported", "raised", "timed out"
#: What each child runs: import the module argv[1], with the folders argv[2:] first on sys.path.
IMPORT_ONE = "import importlib, sys; sys.path[:0] = sys.argv[2:]; importlib.import_module(sys.argv[1])"
NOTHING_TO_IMPORT = ("firmware/ holds nothing to import but %s, %s and %s. The firmware cannot be imported without "
                     "running %s: move the code out of %s into a module that %s calls"
                     % (BOOT_FILES + (PIN_MAP, BOOT_FILE, BOOT_FILE, BOOT_FILE)))


def import_one(name, firmware, timeout_s):
    """One module imported in a process of its own, as (status word, detail); the detail is empty when it imported."""
    command = [sys.executable, "-B", "-c", IMPORT_ONE, name, str(STAND_IN), str(firmware)]  # -B: no __pycache__ in the folder
    try:
        done = subprocess.run(command, cwd=str(firmware), capture_output=True, text=True, errors="replace",
                              stdin=subprocess.DEVNULL, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return TIMED_OUT, ("did not return within %g s: something at module level loops or waits; "
                           "put it in a function that %s calls" % (timeout_s, BOOT_FILE))
    if done.returncode == 0:
        return IMPORTED, ""
    last = done.stderr.strip().splitlines()[-1:]
    return RAISED, last[0] if last else "exited with code %d" % done.returncode


def look(project, timeout_s):
    """Every module of PROJECT/firmware imported: (modules, problems, unchecked)."""
    firmware = (project / "firmware").resolve()  # whole: the child runs inside it, so a relative path would name nothing
    if not firmware.is_dir():
        return [], [], ["no firmware/ folder in %s: there is nothing to import" % project]
    names = sorted({path.stem for path in firmware.glob("*.py") if path.name not in BOOT_FILES}
                   | {path.parent.name for path in firmware.glob("*/__init__.py")})  # a package, the bin's shape
    modules = []
    for name in names:
        status, detail = import_one(name, firmware, timeout_s)
        modules.append({"module": name, "status": status, "detail": detail})
    problems = ["%s %s: %s" % (entry["module"], entry["status"], entry["detail"])
                for entry in modules if entry["status"] != IMPORTED]
    if not set(names) - {PIN_MODULE}:
        problems.append(NOTHING_TO_IMPORT)
    return modules, problems, []


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
