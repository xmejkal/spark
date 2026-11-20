#!/usr/bin/env python3
"""
Write the page blocks that come from an Operation (P481, P936): what stands between `<!-- spark:KIND NAME -->` and
`<!-- /spark:KIND NAME -->`, each marker a whole line of its own outside a code fence, is rendered from the Operation
NAME by its KIND (`KINDS`): `operation` is `OperationHelpTable`'s text, so a page says what its `--help` says, and
`stages` is `StageMarkdownTable`'s table of the Operation's `stages`. It reads README.md, AGENTS.md and the other pages
at the root, and the pages in commands/, agents/, skills/ and docs/guide/ (`PAGES`).

    python3 tools/doc_blocks.py    # writes every stale block; tests/test_doc_blocks.py fails while one is stale

It exits 0 when every block was written or already current, and 1 when it refused a page, which it then leaves as it
is: a start without its end, an end without its start, naming another Operation or of another kind, a name no table
holds, an Operation with nothing for its kind to show (a summary, stages), or a line that starts `<!--` and holds a
marker word (`spark:operation`, `spark:stages`) but is no marker (a typo, a space at its end, a Windows line end). The
sentence names the page and the line.
"""

import re
import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# --- MVP ---
#: The pages that may hold a block, as globs from the root.
PAGES = ("*.md", "commands/*.md", "agents/*.md", "skills/**/*.md", "docs/guide/**/*.md")
COMMENT_START = "<!--"
FENCE = "```"
NO_END_MESSAGE = "%s line %d: the block of %s has no end marker"
NO_START_MESSAGE = "%s line %d: the end marker of %s has no start marker"
WRONG_END_MESSAGE = "%s line %d: the block of %s ends with the marker of %s"
WRONG_KIND_MESSAGE = "%s line %d: the %s block of %s ends with a marker of the kind %s"
UNKNOWN_MESSAGE = "%s line %d: no Operation is named %s"
NOTHING_TO_SHOW_MESSAGE = "%s line %d: the Operation %s has no %s to show"
NOT_A_MARKER_MESSAGE = "%s line %d: this line names %s but is no marker"
STALE_MESSAGE = "%s: a block differs from its Operation, so run python3 tools/doc_blocks.py"
WROTE_MESSAGE = "wrote %s"


def block_operations():
    """The Operations a block may name: the bench's table and the build's, imported only here, so that `import
    doc_blocks` for its markers (tools/check_docs.py reads END, P855) loads no spark module."""
    from spark.bench import OPERATIONS
    from spark.build.build_operations import OPERATIONS as BUILD_OPERATIONS
    return {**OPERATIONS, **BUILD_OPERATIONS}


def _operation_help(operation):
    from spark.core.operation_help_table import OperationHelpTable
    return OperationHelpTable.render(operation)


def _stage_table(operation):
    from spark.build.stage_help_table import StageMarkdownTable
    return StageMarkdownTable.render(operation.stages)


#: Strategy: what one kind of block shows: the attribute of the Operation it renders (a block of an Operation whose
#: attribute is empty is refused) and the function that renders the Operation's block.
BlockKind = namedtuple("BlockKind", "attribute render")
#: Each kind of block by the word after `spark:` in its markers.
KINDS = {"operation": BlockKind("summary", _operation_help), "stages": BlockKind("stages", _stage_table)}
START = re.compile(r"<!-- spark:(%s) ([\w-]+) -->" % "|".join(KINDS))
END = re.compile(r"<!-- /spark:(%s) ([\w-]+) -->" % "|".join(KINDS))
#: A line that starts a comment and holds one of these words means a marker, so one that is no marker is refused.
MARKER_WORDS = tuple("spark:%s" % kind for kind in KINDS)


class BlockError(ValueError):
    """A page's markers that cannot be written: the sentence names the page, the line and the Operation."""


def _marker(page, number, line):
    """(START or END, the kind, the name) of a marker line, None for a line that is no marker. Raises BlockError for a
    line that starts a comment and holds a marker word but matches neither marker whole."""
    words = [word for word in MARKER_WORDS if word in line]
    if not (line.lstrip().startswith(COMMENT_START) and words):
        return None
    for pattern in (START, END):
        found = pattern.fullmatch(line)
        if found:
            return (pattern,) + found.groups()
    raise BlockError(NOT_A_MARKER_MESSAGE % (page, number, words[0]))


def fresh_text(page, text, operations=None):
    """`text` with each block between its markers rendered anew by its kind from `operations` (an op name to its class;
    None for `block_operations()`). A line in a code fence is never a marker. Raises BlockError, see the module's
    docstring."""
    operations = block_operations() if operations is None else operations
    kept, kind, name, opened_at, fenced = [], None, None, None, False
    for number, line in enumerate(text.split("\n"), 1):
        if name is None and line.lstrip().startswith(FENCE):
            fenced = not fenced
        marker = None if fenced else _marker(page, number, line)
        if marker is None:
            kept += [line] if name is None else []
            continue
        pattern, marked_kind, marked = marker
        if pattern is START:
            if name is not None:
                raise BlockError(NO_END_MESSAGE % (page, opened_at, name))
            kind, name, opened_at = marked_kind, marked, number
            if name not in operations:
                raise BlockError(UNKNOWN_MESSAGE % (page, number, name))
            if not getattr(operations[name], KINDS[kind].attribute):
                raise BlockError(NOTHING_TO_SHOW_MESSAGE % (page, number, name, KINDS[kind].attribute))
            kept.append(line)
        elif name is None:
            raise BlockError(NO_START_MESSAGE % (page, number, marked))
        elif marked != name:
            raise BlockError(WRONG_END_MESSAGE % (page, number, name, marked))
        elif marked_kind != kind:
            raise BlockError(WRONG_KIND_MESSAGE % (page, number, kind, name, marked_kind))
        else:
            kept += ["", KINDS[kind].render(operations[name]), "", line]
            name = None
    if name is not None:
        raise BlockError(NO_END_MESSAGE % (page, opened_at, name))
    return "\n".join(kept)


def pages_with_blocks(root=ROOT):
    """(name from the root, text) of each page that holds a marker word."""
    found = sorted({path for pattern in PAGES for path in root.glob(pattern) if path.is_file()})
    pages = [(path.relative_to(root).as_posix(), path.read_text()) for path in found]
    return [(page, text) for page, text in pages if any(word in text for word in MARKER_WORDS)]


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
