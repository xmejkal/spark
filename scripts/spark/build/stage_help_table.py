"""
The build's stages as text (P852, P936): `BuildBoard.details` renders `stages.BUILD_STAGES` with `StageHelpTable` for
`check_spine.py --help`, and `tools/doc_blocks.py` with `StageMarkdownTable` for how-it-works.md, each from the same
endings (`_endings`), so the help and the page list each stage and how it can end from the table the build runs by.
"""

import textwrap

from spark.build import build_codes
from spark.core.operation_help_table import table_cell
from spark.core.outcomes import SKIPPED

# --- MVP ---
#: The help's first line.
HEAD = ("The stages the build reports, in the order it runs them; the first that could not run or found problems ends "
        "the build, but schematic-notes does not:")
#: What the help says of the ending a design error stops a stage with: its sentence and code are the error's own.
DESIGN_ERROR_LINE = "a design error, with its own code (design_codes)"
#: The width the help is wrapped at, the indent of an ending's line and the width of its status column, in characters.
WIDTH, INDENT, STATUS_WIDTH = 120, 6, 14
#: The page table's head: one row per stage, its summary and its endings by status.
TABLE_HEAD = ("| stage | what it is | how it ends when not ok |", "|---|---|---|")


class StageHelpTable:
    """Renderer: each stage's name and summary, then one line for each status and code it can end with, the code's
    meaning from `build_codes.CODES`. A skip has no code yet, so its line is its message, each value as `…`. It takes
    StageDefinitions and decides nothing again."""

    @staticmethod
    def render(definitions):
        """The text, one stage after another, wrapped at WIDTH."""
        lines = [textwrap.fill(HEAD, WIDTH)]
        for definition in definitions:
            lines.append("  %-16s %s" % (definition.name, definition.summary))
            said = ["%-*s %s" % (STATUS_WIDTH, status, words) for status, words in _endings(definition, _code_and_meaning)]
            lines += [textwrap.fill(line, WIDTH, initial_indent=" " * INDENT, break_on_hyphens=False,
                                    subsequent_indent=" " * (INDENT + STATUS_WIDTH + 1)) for line in said]
        return "\n".join(lines)


class StageMarkdownTable:
    """Renderer: a Markdown table of the stages for a page, one row per stage: its name, its summary, and its endings by
    status, each code in backticks without its meaning, which the help gives. It takes StageDefinitions and decides
    nothing again."""

    @staticmethod
    def render(definitions):
        """The table, one line per row."""
        rows = []
        for definition in definitions:
            by_status = {}
            for status, words in _endings(definition, "`%s`".__mod__):
                by_status.setdefault(status, []).append(words)
            ends = "; ".join("%s: %s" % (status, ", ".join(said)) for status, said in by_status.items())
            rows.append("| %s | %s | %s |" % (definition.name, table_cell(definition.summary), table_cell(ends)))
        return "\n".join(list(TABLE_HEAD) + rows)


def _endings(definition, code_said):
    """(status, words) for each ending of `definition`, in its order, once each: two endings said alike are one."""
    return list(dict.fromkeys((ending.status, _said_of(ending, code_said)) for ending in definition.endings))


def _code_and_meaning(code):
    return "%s: %s" % (code, build_codes.CODES[code])


def _said_of(ending, code_said):
    """What is said of one ending: its code as `code_said` says it, a skip's message or DESIGN_ERROR_LINE."""
    if ending.code:
        return code_said(ending.code)
    return ending.message.replace("%s", "…") if ending.status == SKIPPED else DESIGN_ERROR_LINE
# --- end MVP ---
