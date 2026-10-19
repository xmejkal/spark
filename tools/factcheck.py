"""
Check a plan's claims against the repository (P324). A plan holds some wrong claims however often it is reviewed, so
this script checks the ones a script can: every `file:line` reference, the code names in backticks that appear nowhere
in the repository, and the sentences that state a count. It reads only the files git tracks.

    python3 tools/factcheck.py docs/discovery/<folder>/design.md

Exit 1 when a reference names no file, a line past its end, or a file name two files share; 0 otherwise. The names
and the counts are listed for a person to judge: a name a plan proposes is new by design, and a count needs its
command.
"""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: A reference such as `scripts/boards.py:253` or `boards.py:253`.
REFERENCE = re.compile(r"([\w./-]+\.(?:py|md|json|mjs|tsx)):(\d+)")
#: A name in backticks counts as code when it has an underscore, a dot, or a capital inside a word (CamelCase).
CODE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")
#: A sentence that states a count: a number of two digits or more beside a word that counts things.
COUNT_WORDS = re.compile(r"\b(importers?|uses?|rows|files|tests|lines|classes|modules|paths|calls|sites)\b")
#: Names from Python itself that a plan may quote.
STANDARD = {"os.environ", "sys.exit", "sys.path", "time.time", "mock.patch", "Exception"}
#: Folders that hold no tracked file, skipped when there is no git to ask.
UNTRACKED = {".git", "node_modules", "__pycache__", ".claude"}
OK, MISSING, PAST_END, AMBIGUOUS = "ok", "missing", "past end", "ambiguous"


class PlanCheck:
    """Service: checks one plan's text against the tracked files under `root`."""

    def __init__(self, root, files):
        self.root, self.files = root, files
        self.by_name = {}
        for path in files:
            self.by_name.setdefault(path.name, []).append(path)
        self.defined = self._defined_names()

    @classmethod
    def for_repository(cls, root=ROOT):
        """The files git tracks under `root`. Without git (the push gate tests an archive of the commit), every file
        outside the folders git ignores here."""
        listed = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
        if listed.returncode == 0:
            return cls(root, [root / line for line in listed.stdout.splitlines() if (root / line).is_file()])
        return cls(root, [p for p in root.rglob("*") if p.is_file() and not UNTRACKED.intersection(p.relative_to(root).parts)])

    def _defined_names(self):
        names = set()
        for path in self.files:
            if path.suffix != ".py":
                continue
            names.add(path.stem)
            try:
                tree = ast.parse(path.read_text())
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.add(node.name)
                elif isinstance(node, ast.Assign):
                    names.update(t.id for t in node.targets if isinstance(t, ast.Name))
                    names.update(t.attr for t in node.targets if isinstance(t, ast.Attribute))
        return names

    def references(self, text):
        """(reference, verdict, the line's text or the candidates) for each distinct `file:line` in `text`."""
        found = []
        for name, number in sorted(set(REFERENCE.findall(text))):
            line = int(number)
            exact = [p for p in self.files if p.relative_to(self.root).as_posix() == name]
            hits = exact or self.by_name.get(Path(name).name, [])
            if not hits:
                found.append(("%s:%d" % (name, line), MISSING, ""))
            elif len(hits) > 1:
                found.append(("%s:%d" % (name, line), AMBIGUOUS,
                              ", ".join(p.relative_to(self.root).as_posix() for p in hits)))
            else:
                lines = hits[0].read_text(errors="replace").splitlines()
                if line > len(lines):
                    found.append(("%s:%d" % (name, line), PAST_END, "the file has %d lines" % len(lines)))
                else:
                    found.append(("%s:%d" % (name, line), OK, lines[line - 1].strip()))
        return found

    def unknown_names(self, text, plan_folder):
        """The code names in backticks that no tracked file outside `plan_folder` defines or mentions."""
        corpus = "\n".join(p.read_text(errors="replace") for p in self.files
                           if p.suffix in (".py", ".md", ".json") and plan_folder not in p.parents)
        unknown = []
        for quoted in sorted(set(re.findall(r"`([^`\n]+)`", text))):
            for token in CODE_NAME.findall(quoted):
                last = token.split(".")[-1]
                looks_like_code = "_" in last or "." in token or (last[:1].isupper() and any(c.islower() for c in last[1:]))
                if (not looks_like_code or token in STANDARD or last in self.defined or token in self.by_name
                        or re.search(r"\b%s\b" % re.escape(last), corpus) or token in unknown):
                    continue
                unknown.append(token)
        return unknown

    @staticmethod
    def counts(text):
        """The sentences of `text` that state a count."""
        sentences = re.split(r"(?<=[.!?])\s+|\n", text)
        return [s.strip() for s in sentences if re.search(r"\b\d{2,}\b", s) and COUNT_WORDS.search(s)]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check a plan's file:line references, new names and counts against the repository.",
                                     epilog="Exit 1 when a file:line reference is broken; the names and counts are for a person.")
    parser.add_argument("plan", type=Path, help="the plan or design file to check")
    args = parser.parse_args(argv)
    plan = args.plan.resolve()
    text = plan.read_text()
    check = PlanCheck.for_repository()
    broken = 0
    print("file:line references")
    for reference, verdict, said in check.references(text):
        broken += verdict != OK
        print("  %-10s %s  %s" % (verdict, reference, said[:90]))
    print("names in backticks that appear nowhere else (each must be one the plan proposes)")
    for name in check.unknown_names(text, plan.parent):
        print("  " + name)
    print("sentences with a count (each needs its command, or the word estimate)")
    for sentence in check.counts(text):
        print("  " + sentence[:150])
    print("%d broken reference(s)" % broken)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
