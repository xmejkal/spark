#!/usr/bin/env python3
"""The look's CLI (P219): its `--help` sentence and paragraphs are LookAtBoard's (P481), and EPILOG is the CLI's own text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.look_at_board import LookAtBoard
from spark.core.cli import HelpText, run_cli

EPILOG = """--json prints one envelope on stdout (docs/guide/agents/json.md): the look in `data`, the stops and warnings as
`problems`, the unknown fields, a missing token and a last deploy it could not check as `unchecked`, and, when there is
a token, the deploy step with `needs_yes`. The board doctor's lines still go to stderr. Every `problems` and `unchecked`
item has a `code` (scripts/spark/bench/board_codes.py). A bad flag with --json prints an envelope (status could-not-run,
code bad_argument, exit 2); without --json it prints the usage and the error on stderr and exits 2. Exit codes do not
change; the envelope's status is the exit code's.

Without --json the text starts with the status line: a mark, `look:`, the status and one sentence. The marks are ✓ ok,
✗ stop, ! warning and ? not checked (OK, STOP, WARN and ? where the terminal cannot show them). The facts under Board and
Image come next, then the problems and the items not checked, each with its fix, then a note. The last part is Next,
with the command alone on the last line. Two things give colour: a terminal whose TERM is not dumb, and a rich package
that imports. NO_COLOR (not empty) removes it and wins over FORCE_COLOR. FORCE_COLOR (not empty) adds it, also in a pipe
and with TERM=dumb. Claude's shell, a pipe and a file get the same lines with no codes. A stop and the board question print as before. --json and stderr do not change (P1032).

Exit codes: 0 every field matches, there is a token and the last deploy was checked, 1 a field differs or the look found a stop, 2 it could not run
or could not check something (a field unknown, no token, a last deploy it could not check), or it asks the person's yes before it reads
(needs_reply), the person said no (answered_no), or another board is on USB (other_board), and the sentence says why. A crash is 2 too: with --json
an envelope with one unchecked item, code crash; on stderr `look: crashed, <class>`, what to do, and the traceback. Without --json the same
on stderr and nothing on stdout."""


def main(argv=None, outside=None, operation=None):
    """Print the look. `outside` is the OutsideWorld a test gives (a run builds the project's), `operation` the
    LookAtBoard a test gives. Returns the exit code."""
    return run_cli(HelpText("look.py", epilog=EPILOG), operation or LookAtBoard(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
