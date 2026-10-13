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
from pathlib import Path

import store

BEGIN = "<!-- spark:begin. /spark:init writes this section and rewrites it on each run. Edit outside the markers. -->"
END = "<!-- spark:end -->"
SECTION = (Path(__file__).resolve().parent.parent / "data" / "agents-section.md").read_text()
IMPORT = "@AGENTS.md"
LOCAL = "CLAUDE.local.md"


class AiFiles:
    """The three files for one project. `write()` returns whether anything changed, and one note per file."""

    def __init__(self, project, store_home=None):
        self.project = Path(project)
        self.rules = Path(store_home if store_home is not None else store.home()) / "rules.md"

    def write(self):
        results = [self.agents_md(), self.claude_md(), self.claude_local_md()]
        return any(did for did, _ in results), [note for _, note in results]

    def agents_md(self):
        path = self.project / "AGENTS.md"
        block = "%s\n%s%s\n" % (BEGIN, SECTION, END)
        if not path.exists():
            store.write_file(path, block)
            return True, "wrote AGENTS.md with spark's section"
        text = path.read_text()
        if BEGIN not in text:
            store.write_file(path, text.rstrip("\n") + "\n\n" + block)
            return True, "added spark's section to the end of your AGENTS.md"
        start, end = text.index(BEGIN), text.find(END, text.index(BEGIN))
        if end < 0:
            return False, "AGENTS.md has spark's begin marker but no end marker, so it is left alone: fix the markers"
        if store.write_file(path, text[:start] + block.rstrip("\n") + text[end + len(END):]):
            return True, "rewrote spark's section of AGENTS.md"
        return False, "AGENTS.md already has spark's section"

    def claude_md(self):
        path = self.project / "CLAUDE.md"
        if not path.exists():
            store.write_file(path, IMPORT + "\n")
            return True, "wrote CLAUDE.md: %s" % IMPORT
        if IMPORT in path.read_text().split():
            return False, "CLAUDE.md already imports AGENTS.md"
        return False, ("CLAUDE.md is yours and does not import AGENTS.md, so it is left alone and Claude Code does not "
                       "read AGENTS.md: add the line %s to it" % IMPORT)

    def claude_local_md(self):
        path = self.project / LOCAL
        if path.is_symlink() and path.resolve() == self.rules.resolve():
            return self.excluded(False, "%s already links your rules in %s" % (LOCAL, self.rules))
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
