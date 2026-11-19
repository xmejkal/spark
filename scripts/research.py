#!/usr/bin/env python3
"""The research's CLI (P737): its `--help` sentence and paragraphs are ResearchPart's (P855), and EPILOG is the CLI's own text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.cli import HelpText, run_cli
from spark.sourcing.research import build_research_outside_world
from spark.sourcing.research.research_part import ResearchPart

#: The CLI's own text in `--help`, after ResearchPart's details (P855): the store, why no command pre-approves it,
#: and its exit codes.
EPILOG = """The store is SPARK_HOME (default ~/.local/share/spark). The wiki source reaches the network through spark's one door,
so no command pre-approves research.py: Claude Code asks before it runs, and that answer is the yes.
Exit codes: 0 every gap is filled or not published, 1 a problem in the replies or the record, 2 questions are open, a
page did not answer, or research.py could not run. docs/guide/agents/replies.md has the file's shape and the codes."""


def main(argv=None, outside=None):
    """Research one record. `outside` is the OutsideWorld a test gives (a run builds the project's). Returns the exit code."""
    return run_cli(HelpText("research.py", epilog=EPILOG), ResearchPart(), argv,
                   outside_builder=build_research_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
