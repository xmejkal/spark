#!/usr/bin/env python3
"""
Run one scenario of a built project in Wokwi, and keep a log of the run with its date (P130; on the core, P1078, #1582).

    run_scenario.py sim/scenarios/<name>.scenario.yaml --dry-run --json   # the free checks first: no token, nothing spent
    run_scenario.py sim/scenarios/<name>.scenario.yaml --json             # the paid run, in the project after /spark:build --keep .

The run is the Operation `spark/firmware/firmware_scenario.RunScenario` (op `run-scenario`), which says what it checks and
what it writes, and this CLI hands the arguments to the core, which parses them and prints. Its `--help` is the Operation's
text and the EPILOG here. After a paid run the flow's follow-up names the next step and writes page.html again. The tests
use a fake wokwi-cli.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.firmware.firmware_scenario import RunScenario  # noqa: E402
from spark.flow.now_follow_up import FlowFollowUp  # noqa: E402
from spark.records.tool_finder import build_tool_outside_world  # noqa: E402

#: What --help says after the Operation's text: the cost, the token, the contract and the exit codes.
EPILOG = """A run spends Wokwi CI minutes: ask the person before each run, whatever your permissions allow.
It needs a Wokwi CI token (wokwi.com/dashboard/ci) in WOKWI_CLI_TOKEN: export WOKWI_CLI_TOKEN=...
The firmware must print `ready` once its setup is done (the ready contract, commands/build.md).

--dry-run makes the same free checks: it needs no token, starts no run and writes nothing.

Exit codes: 0 the scenario passed (with --dry-run, the free checks passed), 1 it failed, 2 it could not run. The log is sim/runs/<name>.log."""


def main(argv=None, outside_builder=None, operation=None):
    """Run the scenario and print the text, or with --json the envelope. `outside_builder` is a test's builder of the world
    (None: `build_tool_outside_world`), `operation` a test's RunScenario. Returns the exit code."""
    return run_cli(HelpText("run_scenario.py", epilog=EPILOG, follow_up=FlowFollowUp()), operation or RunScenario(), argv,
                   outside_builder=outside_builder or build_tool_outside_world)


if __name__ == "__main__":
    sys.exit(main())
