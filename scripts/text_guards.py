"""
The guards for text that spark shows, stores or writes into a file (P403, OC8): `printable` for the screen, `clean`
for the store, `one_line` for a generated file's comment. It imports nothing of spark, so every reader can use it
(`tests/test_imports.py`).
"""

import re


# --- MVP ---
#: A label is shown and matched, never obeyed (§6.4.6): `clean` turns each run of control and bidi characters into a space,
#: and the label stops at 160 characters. The line and paragraph separators (U+2028/9) are in the set: a terminal prints them
#: as `?`, and a file name must not hold them (`store.file_name_problem` reads this set too, P423).
LABEL_MAX = 160
CONTROL = re.compile("[\x00-\x1f\x7f-\x9f\u200e\u200f\u2028\u2029\u202a-\u202e\u2066-\u2069]+")

#: What an entry or a record says of itself for a chooser (P211): one sentence and a paragraph, each capped — data, never obeyed.
TEXT_MAX = {"about": 200, "description": 1000}
#: At most this many tags, each a lowercase word or two (P211).
TAGS_MAX = 12

#: What `one_line` turns into a space: what a line comment in a generated file cannot hold. A line break ends it: `\n` and `\r` end Python's `#`, and JavaScript's
#: `//` ends at U+2028 and U+2029 too, and U+0085 is one to editors. Any other control character, such as NUL, stops the file
#: from compiling. A lone surrogate stops it from being written as UTF-8. Not `CONTROL`: a comment holds a bidi mark.
COMMENT_UNSAFE = re.compile(r"[\x00-\x1f\x7f-\x9f\u2028\u2029\ud800-\udfff]")


def printable(text):
    """The text with each character that a terminal does not print as itself, such as a newline, shown as `?`."""
    return "".join(each if each.isprintable() else "?" for each in text)


def guard_lines(text):
    """
    The text for a terminal, line by line (P423): each line through `printable`, its own newlines kept. A script prints text
    that holds intended line breaks (a paragraph, a rendered verdict) through this; a name that can hold a newline of its own
    goes through `printable` where it is put into a line. A non-string raises.
    """
    return "\n".join(printable(line) for line in text.split("\n"))


def clean(text, cap=LABEL_MAX):
    """Words from a shop or a person, made safe to show: control and bidi characters become a space; at most `cap` characters."""
    return CONTROL.sub(" ", str(text)).strip()[:cap]


def one_line(text):
    """
    Words a generated file keeps in a `#` or `//` line comment, on that one line (concern 1, P87's line-comment half): every
    line break, other control character and lone surrogate a space. The pin map the firmware imports and the footprint the
    board imports carry a board's name, a role's note, a pad's alias, a board's id; a line break in one ended the comment,
    and what followed was code.
    """
    return COMMENT_UNSAFE.sub(" ", str(text))
