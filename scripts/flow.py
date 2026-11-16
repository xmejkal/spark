#!/usr/bin/env python3
"""Say where a project stands, phase by phase from the idea to the deploy, and what each phase offers next (P825)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.cli import HelpText, run_cli
from spark.core.outside import build_bare_outside_world
from spark.flow.show_flow import ShowFlow

#: The verbs, each the Operation it runs. With no verb word, flow.py shows. `page` and `run-request` come with P827 and P829.
VERBS = {"show": ShowFlow}
DEFAULT_VERB = "show"

EPILOG = """flow.py show reads the project's files and the store, and writes nothing. It says nine phases in order: idea,
needs, parts, requirements, build, breadboard, firmware, simulate and deploy. Each phase has a status (ok, problems,
could-not-run, not-started, partial or stale; idea, firmware and simulate have none), who does it (you, claude or your
terminal), its facts and its offers. An offer is a key, such as pick:soil:x-led, with one line that says what taking it
does. flow.py runs no offer. The last line names the first phase that is not done.

The build phase reads .spark/build.json, which check_spine.py --keep writes when its folder is a project. It is stale when
requirements.json changed after that build.

With --json it prints one envelope: data.phases and data.stands_at (docs/guide/agents/flow.md).

Exit codes: 0 no phase holds problems or could not run, 1 a phase holds problems (a need that cannot be matched,
requirements the picks cannot give, a build that failed), 2 a phase could not be read or its last build could not run,
or an argument is wrong. Every phase answers either way."""


def operation_for(argv):
    """(the Operation class `argv` asks for, argv without its verb word): the first word when it is a verb in VERBS, else
    `show` with argv as it is, so a word that is no verb fails in argparse."""
    return (VERBS[argv[0]], argv[1:]) if argv and argv[0] in VERBS else (VERBS[DEFAULT_VERB], argv)


def main(argv=None, outside=None):
    """Run the verb `argv` names and print its lines, or with --json its envelope. `outside` is the OutsideWorld a test
    gives. Returns the exit code."""
    operation, argv = operation_for(sys.argv[1:] if argv is None else list(argv))
    return run_cli(HelpText("flow.py", __doc__.strip(), EPILOG, tool="flow"), operation(), argv,
                   outside_builder=build_bare_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
