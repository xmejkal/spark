"""
The import check of a project's firmware on the computer, one module per child Python (moved from import_firmware.py,
P685). The stand-ins and import_child.py sit beside this file, so the paths below stay.
"""

import subprocess
import sys
from pathlib import Path

from spark.core.result import Refusal
from spark.firmware import firmware_codes

STAND_IN = Path(__file__).resolve().parent / "stand_in"
#: framebuf and micropython, which a driver may ship itself: they come after the firmware's own folders on sys.path.
FALLBACK = STAND_IN / "fallback"
#: The files MicroPython runs at boot, never imported (main.py starts the loop), and the pin map the build writes, which
#: is not firmware someone wrote.
BOOT_FILE, PIN_MAP, PIN_MODULE = "main.py", "pins.py", "pins"
BOOT_FILES = ("boot.py", BOOT_FILE)
IMPORTED, RAISED, TIMED_OUT = "imported", "raised", "timed out"
#: What each child runs (P443): import the module that is its first argument, with the folders after it first on sys.path,
#: in that order. They are the machine stand-in, firmware/, firmware/lib (where MicroPython looks for drivers) and the
#: fallback stand-ins.
CHILD = Path(__file__).resolve().parent / "import_child.py"
NOTHING_TO_IMPORT = ("firmware/ holds nothing to import but %s, %s and %s. The firmware cannot be imported without "
                     "running %s: move the code out of %s into a module that %s calls"
                     % (BOOT_FILES + (PIN_MAP, BOOT_FILE, BOOT_FILE, BOOT_FILE)))


def import_one(name, firmware, timeout_s):
    """One module imported in a process of its own, as (status word, detail); the detail is empty when it imported, else a
    Refusal whose code names why not."""
    # -B: no __pycache__ in the person's folder. -I: the child's own folder and the current folder stay off sys.path
    command = [sys.executable, "-I", "-B", str(CHILD), name,
               str(STAND_IN), str(firmware), str(firmware / "lib"), str(FALLBACK)]
    try:
        done = subprocess.run(command, cwd=str(firmware), capture_output=True, text=True, errors="replace",
                              stdin=subprocess.DEVNULL, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return TIMED_OUT, Refusal("did not return within %g s: something at module level loops or waits; "
                                  "put it in a function that %s calls" % (timeout_s, BOOT_FILE), firmware_codes.IMPORT_TIMEOUT)
    if done.returncode == 0:
        return IMPORTED, ""
    last = done.stderr.strip().splitlines()[-1:]
    return RAISED, Refusal(last[0] if last else "exited with code %d" % done.returncode, firmware_codes.IMPORT_FAILED)


def look(project, timeout_s):
    """Every module of PROJECT/firmware imported: (modules, problems, unchecked). A module not imported carries its `code`
    (P684), and each problem and unchecked item is a Refusal."""
    firmware = (project / "firmware").resolve()  # whole: the child runs inside it, so a relative path would name nothing
    if not firmware.is_dir():
        return [], [], [Refusal("no firmware/ folder in %s: there is nothing to import" % project,
                                firmware_codes.NO_FIRMWARE_FOLDER)]
    names = sorted({path.stem for path in firmware.glob("*.py") if path.name not in BOOT_FILES}
                   | {path.parent.name for path in firmware.glob("*/__init__.py")})  # a package, the bin's shape
    modules = []
    for name in names:
        status, detail = import_one(name, firmware, timeout_s)
        modules.append({"module": name, "status": status, "detail": detail})
        if status != IMPORTED:  # --- MVP --- an agent decides on the code, never on the detail's words
            modules[-1]["code"] = detail.code
    problems = [Refusal("%s %s: %s" % (entry["module"], entry["status"], entry["detail"]), entry["code"])
                for entry in modules if entry["status"] != IMPORTED]
    if not set(names) - {PIN_MODULE}:
        problems.append(Refusal(NOTHING_TO_IMPORT, firmware_codes.NOTHING_TO_IMPORT))
    return modules, problems, []
