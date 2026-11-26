"""
Spark's section of a person's file (P1150): a block of text between two marker lines, which spark rewrites on each run
while the person's text around it stays. `AGENTS.md` uses it with `<!-- -->` markers and `.gitignore` with `#` markers.
"""

import re


class SparkSection:
    """Value: the three marker strings of one kind of file. It calculates and writes nothing: `placed` gives the new text
    and the caller writes it. A marker counts by its prefix at the start of a line, whatever the rest of the line says, so
    an old section is found after its first line changed, and a marker named inside a sentence is no marker."""

    def __init__(self, prefix, begin_line, end_line):
        self.begin_line, self.end_line = begin_line, end_line
        self.begin_at = re.compile("^" + re.escape(prefix), re.M)
        self.end_at = re.compile("^" + re.escape(end_line), re.M)

    def block(self, body):
        """The begin line, `body` (whole lines) and the end line, with a final newline."""
        return "%s\n%s%s\n" % (self.begin_line, body, self.end_line)

    def found(self, text):
        """Whether `text` has a begin marker."""
        return self.begin_at.search(text) is not None

    def placed(self, text, body):
        """(the text with the section, None), or (None, why not). No begin marker adds the block at the end after one blank
        line (an empty text gets two newlines first, as AGENTS.md always did). A begin marker with no end marker below it
        gives a reason. Else the text from the begin marker to the end marker is replaced and the rest stays byte for byte."""
        block = self.block(body)
        begin = self.begin_at.search(text)
        if begin is None:
            return text + ("" if text.endswith("\n") else "\n") + "\n" + block, None
        end = self.end_at.search(text, begin.end())
        if end is None:
            return None, "has spark's begin marker but no end marker"
        return text[:begin.start()] + block.rstrip("\n") + text[end.end():], None
