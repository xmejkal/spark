"""
The build's stages as text for `check_spine.py --help` (P852): `BuildBoard.details` renders `stages.BUILD_STAGES` with
it, so the help lists each stage and how it can end from the table the build runs by.
"""

import textwrap

from spark.build import build_codes
from spark.core.outcomes import SKIPPED

# --- MVP ---
#: The help's first line.
HEAD = "The stages, in the order the build runs them; it stops at the first that cannot feed the next:"
#: What the help says of the ending a design error stops a stage with: its sentence and code are the error's own.
DESIGN_ERROR_LINE = "a design error, with its own code (design_codes)"
#: The width the help is wrapped at, in characters, and the indent of an ending's line.
WIDTH, INDENT = 120, 6


class StageHelpTable:
    """Renderer: each stage's name and summary, then one line for each status and code it can end with, the code's
    meaning from `build_codes.CODES`. A skip has no code yet, so its line is its message, each value as `…`. It takes
    StageDefinitions and decides nothing again."""

    @staticmethod
    def render(definitions):
        """The text, one stage after another, wrapped at WIDTH."""
        lines = [HEAD]
        for definition in definitions:
            lines.append("  %-16s %s" % (definition.name, definition.summary))
            said = dict.fromkeys("%-14s %s" % (ending.status, _said_of(ending)) for ending in definition.endings)
            lines += [textwrap.fill(line, WIDTH, initial_indent=" " * INDENT, subsequent_indent=" " * (INDENT + 15), break_on_hyphens=False)
                      for line in said]
        return "\n".join(lines)


def _said_of(ending):
    """What the help says of one ending: its code and meaning, a skip's message or DESIGN_ERROR_LINE."""
    if ending.code:
        return "%s: %s" % (ending.code, build_codes.CODES[ending.code])
    return ending.message.replace("%s", "…") if ending.status == SKIPPED else DESIGN_ERROR_LINE
# --- end MVP ---
