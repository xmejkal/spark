"""
The help of an Operation as a Markdown block for a page (P481): `tools/doc_blocks.py` writes it between a page's
markers, so a page says what `--help` says, from the same class attributes.
"""

from spark.core.operation import JSON_DEST

# --- MVP ---
#: The table's head: one row per Argument, its flags, the word for its value and its help.
TABLE_HEAD = ("| flag | value | what it does |", "|---|---|---|")


class OperationHelpTable:
    """Renderer: an Operation's `summary`, then a Markdown table of its Arguments but `--json`, which is the frontend's. It
    reads the class attributes only, so it takes the class or an instance, and it decides nothing again."""

    @staticmethod
    def render(operation):
        """The block's text, one line per row, without the markers. A bool Argument has no value, and the value of any
        other is its metavar, its choices as argparse prints them, or its dest in capitals, as `--help` shows it."""
        rows = ["| %s | %s | %s |" % (", ".join("`%s`" % flag for flag in argument.flags), _value_of(argument),
                                      argument.help.replace("|", "\\|"))
                for argument in operation.arguments if argument.dest != JSON_DEST]
        return "\n".join([operation.summary, ""] + list(TABLE_HEAD) + rows)


def _value_of(argument):
    """The word `--help` shows for the value of `argument`, in backticks, or "" for a bool flag."""
    if argument.kind is bool:
        return ""
    shown = argument.metavar or ("{%s}" % ",".join(argument.choices) if argument.choices else argument.dest.upper())
    return "`%s`" % shown
# --- end MVP ---
