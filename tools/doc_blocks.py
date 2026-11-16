#!/usr/bin/env python3
"""
Write the page blocks that come from an Operation (P481): what stands between `<!-- spark:operation NAME -->` and
`<!-- /spark:operation NAME -->`, each marker on a line of its own, is `OperationHelpTable`'s text for the Operation NAME,
so a page says what its `--help` says.

    python3 tools/doc_blocks.py    # writes every stale block; tests/test_doc_blocks.py fails while one is stale

A start without its end, an end that names another Operation and a name no table holds are refused, with the page and
the name, and that page is not written.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from spark.bench import OPERATIONS  # noqa: E402
from spark.core.operation_help_table import OperationHelpTable  # noqa: E402

# --- MVP ---
#: The pages that may hold a block, as globs from the root.
PAGES = ("*.md", "commands/*.md", "agents/*.md", "skills/**/*.md", "docs/guide/**/*.md")
START = re.compile(r"^<!-- spark:operation ([\w-]+) -->$", re.M)
END = re.compile(r"^<!-- /spark:operation ([\w-]+) -->$", re.M)
NO_END_MESSAGE = "%s: the block of %s has no end marker"
WRONG_END_MESSAGE = "%s: the block of %s ends with the marker of %s"
UNKNOWN_MESSAGE = "%s: no Operation is named %s"
STALE_MESSAGE = "%s: a block differs from its Operation, so run python3 tools/doc_blocks.py"
WROTE_MESSAGE = "wrote %s"


class BlockError(ValueError):
    """A page's markers that cannot be written: the sentence names the page and the Operation."""


def fresh_text(page, text, operations=OPERATIONS):
    """`text` with each block between its markers rendered anew from `operations` (an op name to its class). Raises
    BlockError for a start without its end, an end that names another Operation, or a name `operations` lacks."""
    pieces, at = [], 0
    for start in START.finditer(text):
        name, end = start.group(1), END.search(text, start.end())
        if end is None or START.search(text, start.end(), end.start()):
            raise BlockError(NO_END_MESSAGE % (page, name))
        if end.group(1) != name:
            raise BlockError(WRONG_END_MESSAGE % (page, name, end.group(1)))
        if name not in operations:
            raise BlockError(UNKNOWN_MESSAGE % (page, name))
        pieces += [text[at:start.end()], "\n\n", OperationHelpTable.render(operations[name]), "\n\n"]
        at = end.start()
    return "".join(pieces) + text[at:]


def pages_with_blocks(root=ROOT):
    """(name from the root, text) of each page that holds a start marker."""
    found = sorted({path for pattern in PAGES for path in root.glob(pattern) if path.is_file()})
    pages = [(path.relative_to(root).as_posix(), path.read_text()) for path in found]
    return [(page, text) for page, text in pages if START.search(text)]


def stale_pages(root=ROOT, operations=OPERATIONS):
    """A sentence for each page whose block differs from what its Operation renders or whose markers are refused. It
    writes nothing."""
    said = []
    for page, text in pages_with_blocks(root):
        try:
            said += [STALE_MESSAGE % page] if fresh_text(page, text, operations) != text else []
        except BlockError as refused:
            said.append(str(refused))
    return said


def write_pages(root=ROOT, operations=OPERATIONS):
    """(written, refused): the pages whose blocks were written anew, and a sentence for each page refused, which is not
    written."""
    written, refused = [], []
    for page, text in pages_with_blocks(root):
        try:
            fresh = fresh_text(page, text, operations)
        except BlockError as error:
            refused.append(str(error))
            continue
        if fresh != text:
            (root / page).write_text(fresh)
            written.append(page)
    return written, refused
# --- end MVP ---


def main():
    written, refused = write_pages()
    for line in [WROTE_MESSAGE % page for page in written] + refused:
        print(line)
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
