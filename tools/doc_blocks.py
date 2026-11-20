#!/usr/bin/env python3
"""
Write the page blocks that come from an Operation (P481): what stands between `<!-- spark:operation NAME -->` and
`<!-- /spark:operation NAME -->`, each marker a whole line of its own outside a code fence, is `OperationHelpTable`'s text
for the Operation NAME, so a page says what its `--help` says. It reads README.md, AGENTS.md and the other pages at the
root, and the pages in commands/, agents/, skills/ and docs/guide/ (`PAGES`).

    python3 tools/doc_blocks.py    # writes every stale block; tests/test_doc_blocks.py fails while one is stale

It exits 0 when every block was written or already current, and 1 when it refused a page, which it then leaves as it
is: a start without its end, an end without its start or naming another Operation, a name no table holds, an Operation
with no summary, or a line that starts `<!--` and holds `spark:operation` but is no marker (a typo, a space at its end,
a Windows line end). The sentence names the page and the line.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# --- MVP ---
#: The pages that may hold a block, as globs from the root.
PAGES = ("*.md", "commands/*.md", "agents/*.md", "skills/**/*.md", "docs/guide/**/*.md")
START = re.compile(r"<!-- spark:operation ([\w-]+) -->")
END = re.compile(r"<!-- /spark:operation ([\w-]+) -->")
#: A line that starts a comment and holds this word means a marker, so one that is no marker is refused.
MARKER_WORD = "spark:operation"
COMMENT_START = "<!--"
FENCE = "```"
NO_END_MESSAGE = "%s line %d: the block of %s has no end marker"
NO_START_MESSAGE = "%s line %d: the end marker of %s has no start marker"
WRONG_END_MESSAGE = "%s line %d: the block of %s ends with the marker of %s"
UNKNOWN_MESSAGE = "%s line %d: no Operation is named %s"
NO_SUMMARY_MESSAGE = "%s line %d: the Operation %s has no summary to show"
NOT_A_MARKER_MESSAGE = "%s line %d: this line names spark:operation but is no marker"
STALE_MESSAGE = "%s: a block differs from its Operation, so run python3 tools/doc_blocks.py"
WROTE_MESSAGE = "wrote %s"


def bench_operations():
    """The Operations a block may name: the bench's table, imported only here, so that `import doc_blocks` for its markers
    (tools/check_docs.py reads END, P855) loads no spark module."""
    from spark.bench import OPERATIONS
    return OPERATIONS


class BlockError(ValueError):
    """A page's markers that cannot be written: the sentence names the page, the line and the Operation."""


def _marker(page, number, line):
    """(START or END, the name) of a marker line, None for a line that is no marker. Raises BlockError for a line that
    starts a comment and holds MARKER_WORD but matches neither marker whole."""
    if not (line.lstrip().startswith(COMMENT_START) and MARKER_WORD in line):
        return None
    for kind in (START, END):
        found = kind.fullmatch(line)
        if found:
            return kind, found.group(1)
    raise BlockError(NOT_A_MARKER_MESSAGE % (page, number))


def fresh_text(page, text, operations=None):
    """`text` with each block between its markers rendered anew from `operations` (an op name to its class; None for
    `bench_operations()`). A line in a code fence is never a marker. Raises BlockError, see the module's docstring."""
    from spark.core.operation_help_table import OperationHelpTable
    operations = bench_operations() if operations is None else operations
    kept, name, opened_at, fenced = [], None, None, False
    for number, line in enumerate(text.split("\n"), 1):
        if name is None and line.lstrip().startswith(FENCE):
            fenced = not fenced
        marker = None if fenced else _marker(page, number, line)
        if marker is None:
            kept += [line] if name is None else []
        elif marker[0] is START:
            if name is not None:
                raise BlockError(NO_END_MESSAGE % (page, opened_at, name))
            name, opened_at = marker[1], number
            if name not in operations:
                raise BlockError(UNKNOWN_MESSAGE % (page, number, name))
            if operations[name].summary is None:
                raise BlockError(NO_SUMMARY_MESSAGE % (page, number, name))
            kept.append(line)
        elif name is None:
            raise BlockError(NO_START_MESSAGE % (page, number, marker[1]))
        elif marker[1] != name:
            raise BlockError(WRONG_END_MESSAGE % (page, number, name, marker[1]))
        else:
            kept += ["", OperationHelpTable.render(operations[name]), "", line]
            name = None
    if name is not None:
        raise BlockError(NO_END_MESSAGE % (page, opened_at, name))
    return "\n".join(kept)


def pages_with_blocks(root=ROOT):
    """(name from the root, text) of each page that holds MARKER_WORD."""
    found = sorted({path for pattern in PAGES for path in root.glob(pattern) if path.is_file()})
    pages = [(path.relative_to(root).as_posix(), path.read_text()) for path in found]
    return [(page, text) for page, text in pages if MARKER_WORD in text]


def stale_pages(root=ROOT, operations=None):
    """A sentence for each page whose block differs from what its Operation renders or whose markers are refused. It
    writes nothing."""
    said = []
    for page, text in pages_with_blocks(root):
        try:
            said += [STALE_MESSAGE % page] if fresh_text(page, text, operations) != text else []
        except BlockError as refused:
            said.append(str(refused))
    return said


def write_pages(root=ROOT, operations=None):
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
