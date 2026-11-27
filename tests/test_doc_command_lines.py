"""P1256: a command line in a docs code block holds no unquoted `<word>`.

A shell reads `<word>` as a redirection from a file, so a pasted `deploy.py --project <project>` fails, and
`... --token xxxx <spark>` can empty a file. A placeholder in quotes ('<project>') is safe. A line of a block that is
no command (a file's text, a table, an answer) is not checked.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent

#: How a command line starts, after an optional `$ `.
COMMAND_START = re.compile(
    r"^(\$ |python3? |SPARK_HOME=|\$\{CLAUDE_PLUGIN_ROOT\}|\"\$\{CLAUDE_PLUGIN_ROOT\}\"|<spark>/scripts/|"
    r"'<spark>'/scripts/|[\w./-]*scripts/[\w./-]+\.py|[\w-]+\.py )"
)
PLACEHOLDER = re.compile(r"<[A-Za-z][^<>]*>")


def unquoted_placeholder(line):
    """The first `<word>` outside single and double quotes in `line`, or None."""
    quote = None
    for i, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "<" and PLACEHOLDER.match(line, i):
            return PLACEHOLDER.match(line, i).group(0)
    return None


def command_lines(text):
    """Each (line number, line) of a command inside a fenced block of `text`."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            fence = None if fence else stripped
            continue
        if fence and COMMAND_START.match(stripped):
            yield number, stripped


def hits():
    found = []
    pages = sorted((ROOT / "docs" / "guide").rglob("*.md")) + sorted((ROOT / "commands").glob("*.md"))
    for path in pages:
        for number, line in command_lines(path.read_text()):
            word = unquoted_placeholder(line)
            if word:
                found.append(f"{path.relative_to(ROOT)}:{number}: unquoted {word} in: {line}")
    return found


class TheCheckTest(unittest.TestCase):
    def test_a_quoted_placeholder_passes_and_an_unquoted_one_is_found(self):
        self.assertIsNone(unquoted_placeholder("$ deploy.py --project '<project>'"))
        self.assertIsNone(unquoted_placeholder('$ deploy.py --project "<project>" --x'))
        self.assertEqual(unquoted_placeholder("$ deploy.py --project <project> --token x"), "<project>")
        self.assertIsNone(unquoted_placeholder("$ a 2 < 3"))

    def test_only_command_lines_of_a_fenced_block_are_read(self):
        text = "<a> prose\n```\n$ run <x>\nname: <y>\n```\n$ run <z>\n"
        self.assertEqual(list(command_lines(text)), [(3, "$ run <x>")])


class TheDocsTest(unittest.TestCase):
    def test_no_command_line_in_the_docs_holds_an_unquoted_placeholder(self):
        self.assertEqual(hits(), [], "quote each placeholder: '<project>'")


if __name__ == "__main__":
    unittest.main()
