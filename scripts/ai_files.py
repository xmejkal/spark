"""
The files that AI tools read in a project that uses spark (P216 step 6), written by `/spark:init`.

- `AGENTS.md`: spark's section, between two marker lines. Spark rewrites only that section, and the person's text
  around it stays.
- `CLAUDE.md`: one line, `@AGENTS.md`, because a `CLAUDE.local.md` stops Claude Code from reading `AGENTS.md`.
  A `CLAUDE.md` that the person wrote is left alone, and the note names the line to add.
- `CLAUDE.local.md`: a link to `rules.md` in the person's store, kept out of git. A link, not an import, because an
  import from outside the project wants an approval that `claude -p` never gives.
"""

import os
import re
from pathlib import Path

import store

#: The markers in a person's AGENTS.md are a contract: an old section is found by these, whatever its first line says.
BEGIN = "<!-- spark:begin"
BEGIN_LINE = BEGIN + ". /spark:init writes this section and rewrites it on each run. Edit outside the markers. -->"
END = "<!-- spark:end -->"
BEGIN_AT, END_AT = (re.compile("^" + re.escape(marker), re.M) for marker in (BEGIN, END))  # at a line's start only
SECTION = (Path(__file__).resolve().parent.parent / "data" / "agents-section.md").read_text()
IMPORT = "@AGENTS.md"
CLAUDE_MD = "<!-- /spark:init wrote this file. It is yours now: spark never rewrites it. -->\n%s\n" % IMPORT
LOCAL = "CLAUDE.local.md"


class AiFiles:
    """The three files for one project. `write()` returns whether anything changed, and one note per file."""

    def __init__(self, project, store_home=None):
        self.project = Path(project)
        self.rules = Path(store_home if store_home is not None else store.home()).absolute() / "rules.md"

    def write(self):
        results = [self.agents_md(), self.claude_md(), self.claude_local_md()]
        return any(did for did, _ in results), [note for _, note in results]

    def agents_md(self):
        path = self.project / "AGENTS.md"
        block = "%s\n%s%s\n" % (BEGIN_LINE, SECTION, END)
        if path.is_symlink():  # a link to a file in the project, such as CLAUDE.md, is followed
            path = path.resolve()
            if not path.is_file() or self.project.resolve() not in path.parents:
                return False, "AGENTS.md is a link out of the project or to nothing, so it is left alone"
        if not path.exists():
            store.write_file(path, block)
            return True, "wrote AGENTS.md with spark's section"
        text = read(path)
        if text is None:
            return False, "AGENTS.md is not UTF-8 text, so it is left alone"
        begin = BEGIN_AT.search(text)
        if begin is None:
            store.write_file(path, text + ("" if text.endswith("\n") else "\n") + "\n" + block)
            return True, "added spark's section to the end of your AGENTS.md"
        end = END_AT.search(text, begin.end())
        if end is None:
            return False, "AGENTS.md has spark's begin marker but no end marker, so it is left alone: fix the markers"
        if store.write_file(path, text[:begin.start()] + block.rstrip("\n") + text[end.end():]):
            return True, "rewrote spark's section of AGENTS.md"
        return False, "AGENTS.md already has spark's section"

    def claude_md(self):
        path = self.project / "CLAUDE.md"
        agents = self.project / "AGENTS.md"
        if path.exists() and agents.exists() and path.resolve() == agents.resolve():
            return False, "CLAUDE.md and AGENTS.md are one file, so Claude Code already reads AGENTS.md"
        if os.path.lexists(path) and not path.exists():
            return False, "CLAUDE.md is a link to nothing, so it is left alone. It needs the line %s" % IMPORT
        if not path.exists():
            store.write_file(path, CLAUDE_MD)
            return True, "wrote CLAUDE.md: %s" % IMPORT
        text = read(path)
        if text is None:
            return False, "CLAUDE.md is not UTF-8 text, so it is left alone. It needs the line %s" % IMPORT
        if IMPORT in text.split():  # Claude Code imports an @path anywhere in a line
            return False, "CLAUDE.md already imports AGENTS.md"
        return False, ("CLAUDE.md is yours, so it is left alone. It does not import AGENTS.md, so Claude Code does not "
                       "read AGENTS.md: add the line %s to it" % IMPORT)

    def claude_local_md(self):
        path = self.project / LOCAL
        if path.is_symlink():
            if path.resolve() == self.rules.resolve():
                return self.excluded(False, "%s already links your rules in %s" % (LOCAL, self.rules))
            return False, ("%s links to %s, not to your rules in %s: remove it and run init again"
                           % (LOCAL, os.readlink(path), self.rules))
        if os.path.lexists(path):
            return False, "%s is yours, so it is left alone. Spark would link your rules in %s" % (LOCAL, self.rules)
        if not self.rules.is_file():
            return False, ("no rules file at %s, so no %s: write your rules for spark projects there and run init "
                           "again" % (self.rules, LOCAL))
        path.symlink_to(self.rules)
        return self.excluded(True, "linked %s to your rules in %s" % (LOCAL, self.rules))

    def excluded(self, did, note):
        """Keep the private link out of git: one line in the repository's own `.git/info/exclude`."""
        top = store.inside_git(self.project)
        if top is None:
            return did, note
        if not (top / ".git").is_dir():
            return did, note + ". Add %s to your git ignore list: %s/.git is not a folder" % (LOCAL, top)
        exclude = top / ".git" / "info" / "exclude"
        lines = exclude.read_text().splitlines() if exclude.exists() else []
        if LOCAL in lines:
            return did, note
        exclude.parent.mkdir(parents=True, exist_ok=True)
        store.write_file(exclude, "\n".join(lines + [LOCAL]) + "\n")
        return True, note + ", kept out of git"


def read(path):
    """
    A file's text as it is on disk: no line endings changed, so a person's CRLF stays outside spark's section. None
    for a file that is not UTF-8, which spark leaves alone.
    """
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None
