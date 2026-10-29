"""
The guards for text that spark shows, stores or writes into a file (P403, OC8): `printable` for the screen, `clean`
for the store, `one_line` for a generated file's comment. It imports nothing of spark, so every reader can use it
(rule U1 of `tests/test_architecture.py`).
"""

import re


# --- MVP ---
#: A label is shown and matched, never obeyed (§6.4.6): `clean` turns each run of control and bidi characters and lone surrogates (P445) into a space,
#: and the label stops at 160 characters. The line and paragraph separators (U+2028/9) are in the set: a terminal prints them
#: as `?`, and a file name must not hold them (`store.file_name_problem` reads this set too, P423).
LABEL_MAX = 160
CONTROL = re.compile("[\x00-\x1f\x7f-\x9f\u200e\u200f\u2028\u2029\u202a-\u202e\u2066-\u2069\ud800-\udfff]+")

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
    return "".join(each if each.isprintable() else "?" for each in str(text))


# --- MVP ---
#: What a `%` in a template converts: `%%` (the group is empty, and it takes no value) or a conversion letter (P444).
CONVERSION = re.compile(r"%%|%[-#0 +]*[0-9.]*([a-zA-Z])")


class ValueMessageError(Exception):
    """
    Error: a message made of a template and its values (P444). Each value goes into the template on one line: a number, and a
    value for `%r` (whose `repr` already escapes control characters and surrogates), stay as they are; any other goes through
    `printable`. The template keeps its own line breaks. The values as they were stay in `values`. The error classes that
    put a path, a name or a record's field into a sentence inherit from it, and a raise passes the values as arguments.
    """

    def __init__(self, template, *values):
        self.values = values
        kinds = [kind for kind in CONVERSION.findall(template) if kind]
        shown = tuple(value if isinstance(value, (int, float)) or kind == "r" else printable(value)
                      for value, kind in zip(values, kinds + ["s"] * len(values)))
        super().__init__(template % shown if values else template)

    @classmethod
    def of_lines(cls, lines, **keywords):
        """The error of several sentences, one per line: each is a value, flattened, and the line breaks between them stay."""
        return cls("\n".join(["%s"] * len(lines)), *lines, **keywords)


def guard_lines(text):
    """
    The text for a terminal, line by line (P423): each line through `printable`, its own newlines kept. A script prints text
    that holds intended line breaks (a paragraph, a rendered verdict) through this; a name that can hold a newline of its own
    goes through `printable` where it is put into a line. A non-string raises.
    """
    return "\n".join(printable(line) for line in text.split("\n"))


# --- MVP ---
def guard_sentence(text, *flat):
    """
    A sentence for a terminal that holds names the person typed, such as a `--port` or a `--project` (P430): each value in
    `flat` (a string, a path, or an empty value that is skipped) is put on one line first, as `printable` does, then the text
    goes through `guard_lines`. A name with its own newline cannot fake a line of the sentence. Only the value as it stands in
    the text is found, so give the value as the script holds it.
    """
    for each in flat:
        text = text.replace(str(each), printable(str(each))) if each else text
    return guard_lines(text)


def clean(text, cap=LABEL_MAX):
    """Words from a shop or a person, made safe to show: control and bidi characters become a space; at most `cap` characters."""
    return CONTROL.sub(" ", str(text)).strip()[:cap]


def list_key_problems(where, value):
    """
    Every key at any depth in `value` that is no string or holds a control or bidi character (P374), as sentences that name
    the key's path from `where`. A key is refused and never cleaned, because two cleaned keys can merge into one.
    """
    if isinstance(value, list):
        return [problem for index, item in enumerate(value) for problem in list_key_problems("%s[%d]" % (where, index), item)]
    problems = []
    for key, item in (value.items() if isinstance(value, dict) else ()):
        here = "%s[%r]" % (where, key)
        if not isinstance(key, str) or CONTROL.search(key):
            problems.append("%s is a key that is no string or holds a control or bidi character: refused, never cleaned, "
                            "because two cleaned keys could merge" % here)
        problems += list_key_problems(here, item)
    return problems


def one_line(text):
    """
    Words a generated file keeps in a `#` or `//` line comment, on that one line (concern 1, P87's line-comment half): every
    line break, other control character and lone surrogate a space. The pin map the firmware imports and the footprint the
    board imports carry a board's name, a role's note, a pad's alias, a board's id; a line break in one ended the comment,
    and what followed was code.
    """
    return COMMENT_UNSAFE.sub(" ", str(text))
