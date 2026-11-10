#!/usr/bin/env python3
"""Research one part record from ordered sources (P737): find the geometry gaps the chain needs, ask one question per gap that cites the kept drawing, and write the replies as facts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.cli import HelpText, run_cli
from spark.sourcing.research import build_research_outside_world
from spark.sourcing.research.research_part import ResearchPart

EPILOG = """research.py --part <id> reads the record from the project's parts/ or your shelf, never from spark's own library.
It lists the facts that data/fact-needs.json says the chain reads and the record lacks (the outline, the thickness, the
mounting holes, the header), minus what physical_proof.not_published names. Then it asks each source in order. Today the
one source is kept-documents: when the record keeps a dimension drawing in your store, each gap becomes one question
that cites that drawing at page 1. A gap no source can place becomes a question with no citation.

Run 1 answers nothing itself. It writes the template <project>/.spark/research-replies.json with a null value per
question, prints the questions in data.open, one unchecked item per question with the code needs_reply, and exits 2.
Exit 2 here means "run again with replies", not "broken". Read the cited drawing, fill the values, invent no key, and
leave a value null when the drawing does not give it.

Run 2, with --replies <file>, reads the file, writes each value as a fact (verified: false, with the document, the page
and who read it as its source), validates the record and writes it in place. A key no question has, or a reply that
would change a fact the record holds, is a problem (unknown_reply) and nothing is written. A value the record's
contract refuses (part_contract_broken) is a problem too. A rerun with the same file adds nothing twice.

The store is SPARK_HOME (default ~/.local/share/spark). No network: the DFRobot wiki source is step 5 of P737.
Exit codes: 0 every gap is filled or not published, 1 a problem in the replies or the record, 2 questions are open or
research.py could not run. docs/guide/agents/replies.md has the file's shape and the codes."""


def main(argv=None, outside=None):
    """Research one record. `outside` is the OutsideWorld a test gives (a run builds the project's). Returns the exit code."""
    return run_cli(HelpText("research.py", __doc__.strip(), EPILOG), ResearchPart(), argv,
                   outside_builder=build_research_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
