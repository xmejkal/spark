#!/usr/bin/env python3
"""Research one part record from ordered sources (P737): find the geometry gaps the chain needs, keep the documents a DFRobot module's wiki page lists, ask one question per gap that cites the kept drawing, and write the replies as facts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.cli import HelpText, run_cli
from spark.sourcing.research import build_research_outside_world
from spark.sourcing.research.research_part import ResearchPart

EPILOG = """research.py --part <id> reads the record from the project's parts/ or your shelf, never from spark's own library.
It lists the facts that data/fact-needs.json says the chain reads and the record lacks (the outline, the thickness, the
mounting holes, the header), minus what physical_proof.not_published names. With no gap, it asks no source. Else it asks
the sources in order, and folds each answer into the record before the next source looks:
  1 dfrobot-wiki (web, free): for a record whose vendor is dfrobot, it fetches the wiki page https://wiki.dfrobot.com/<sku>/
    once per record (never again once the URL is in the record's sources), reads the page's document list, keeps each
    PDF, PNG, JPEG, WebP or SVG in your store (at most twelve) and writes it into documents; a zip or a STEP file is
    listed with kept: false, with no fetch. A page that lists no documents spark can read is read again next run. When the
    page lists no dimension drawing, the thickness, holes and header go into physical_proof.not_published. A page that
    does not answer is one unchecked item (url_unreachable); a record with no sku is one too (no_sku).
  2 kept-documents (local): when the record keeps a dimension drawing in your store, each gap becomes one question
    that cites that drawing at page 1.
A gap no source can place becomes a question with no citation.

Run 1 writes the documents and the sources it found, and answers no question itself. In a terminal without --json it asks
you each question that is not an agent's (one with no cited drawing), one at a time: Enter leaves it open, Ctrl-C keeps
what you typed so far. Then it writes the template
<project>/.spark/research-replies.json with a null value per question, prints the questions in data.open, one unchecked
item per question with the code needs_reply, and exits 2. Exit 2 here means "run again with replies", not "broken".
Read the cited drawing, fill the values, and invent no key. A value the drawing does not give stays null and its
question stays open; a size the vendor did not publish goes into physical_proof.not_published with parts.py --fact-set.

Run 2, with --replies <file>, reads the file, writes each value as a fact (verified: false, with the document, the page
and who read it as its source), validates the record and writes it in place. A key no question has, or a reply that
changes a fact the record holds, is a problem (unknown_reply) and nothing is written. A value the record's contract
refuses (part_contract_broken) is a problem too. An id no record has is no_such_part. A rerun with the same file adds
nothing twice.

The store is SPARK_HOME (default ~/.local/share/spark). The wiki source reaches the network through spark's one door,
so no command pre-approves research.py: Claude Code asks before it runs, and that answer is the yes.
Exit codes: 0 every gap is filled or not published, 1 a problem in the replies or the record, 2 questions are open, a
page did not answer, or research.py could not run. docs/guide/agents/replies.md has the file's shape and the codes."""


def main(argv=None, outside=None):
    """Research one record. `outside` is the OutsideWorld a test gives (a run builds the project's). Returns the exit code."""
    return run_cli(HelpText("research.py", __doc__.strip(), EPILOG), ResearchPart(), argv,
                   outside_builder=build_research_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
