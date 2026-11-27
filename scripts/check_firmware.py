#!/usr/bin/env python3
"""
Check a project's firmware for free: import it on this machine, and run the project's own tests (P59, #7; P1208, #1757).

    check_firmware.py [--project PROJECT] [--json]

Example, in a project after `/spark:build` and the firmware are written:

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_firmware.py"

The check is the Operation `spark/firmware/firmware_check.CheckFirmware` (op `check-firmware`), which says what it checks, and
this CLI hands the arguments to the core, which parses them and prints. Its `--help` is the Operation's text and the EPILOG
here. It needs no sim/, no board and no token, and it writes nothing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402
from spark.firmware.firmware_check import CheckFirmware  # noqa: E402

#: The CLI's own text in `--help`, after the Operation's details: its exit codes.
EPILOG = """Exit codes: 0 every module imported and every test passed, or the project has no tests/; 1 a module did not import, there is
nothing to import, or a test failed or raised; 2 there is no firmware/ folder, or the tests gave no count or ran no test
(an empty tests/, or every test skipped)."""


def main(argv=None, outside=None, operation=None):
    """Run the free checks and print the text, or with --json the envelope. `outside` is the OutsideWorld a test gives,
    `operation` the CheckFirmware a test gives with its own timeouts. Returns the exit code."""
    return run_cli(HelpText("check_firmware.py", epilog=EPILOG), operation or CheckFirmware(), argv,
                   outside_builder=build_bare_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
