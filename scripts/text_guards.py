"""
The guards for text that spark shows, stores or writes into a file (P403, OC8): `printable` for the screen, `clean`
for the store, `one_line` for a generated file's comment. It imports nothing of spark, so every reader can use it
(`tests/test_imports.py`).
"""

import re


# --- MVP ---
#: A label is shown and matched, never obeyed (§6.4.6): control and bidi characters go, and it stops at 160 characters.
LABEL_MAX = 160
CONTROL = re.compile("[\x00-\x1f\x7f-\x9f\u200e\u200f\u202a-\u202e\u2066-\u2069]+")

#: What an entry or a record says of itself for a chooser (P211): one sentence and a paragraph, each capped — data, never obeyed.
TEXT_MAX = {"about": 200, "description": 1000}
#: At most this many tags, each a lowercase word or two (P211).
TAGS_MAX = 12

#: What a line comment in a generated file cannot hold. A line break ends it: `\n` and `\r` end Python's `#`, and JavaScript's
#: `//` ends at U+2028 and U+2029 too, and U+0085 is one to editors. Any other control character, such as NUL, stops the file
#: from compiling. A lone surrogate stops it from being written as UTF-8.
COMMENT_UNSAFE = re.compile(r"[\x00-\x1f\x7f-\x9f\u2028\u2029\ud800-\udfff]")


def printable(text):
    """The text with each character that a terminal does not print as itself, such as a newline, shown as `?`."""
    return "".join(each if each.isprintable() else "?" for each in text)


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
