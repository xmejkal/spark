"""
Proof that nothing ships unused, and that the product stays the size a person can hold.

On 2026-09-29 a third of this repository was deleted: a findings store that never resolved a
finding, an eval harness nobody re-ran, a second file format for a design, a check neither
project ran, three agents nothing routed to, a skill with no code. Every one had tests, so every
one looked alive. Nothing asked "who calls this?" — this does, at every commit (W15).

    python3 -m unittest discover -s tests
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

#: Modules that are imported, never run: they earn their place by being imported.
LIBRARIES = {"copper", "outcomes", "design"}

#: The budget for the product's scripts, in CODE lines: docstrings, comments and blank lines do
#: not count. It counted every line until 2026-09-30, which charged the most valuable thing in
#: this repository — 1,973 lines of prose recording why each defect's fix is shaped as it is —
#: against the same ceiling as complexity, so a well-explained function cost more budget than a
#: cryptic one. The PO asked the right question: "if it's code, could it be refactored?" So the
#: ceiling is on the code, and the order when it pinches is **refactor, delete, raise** — each
#: written down. 3,550 code lines on the day it changed (6,536 total); 4,000 leaves room for the
#: sprint's five items, which are about 250.
SCRIPTS_CODE_BUDGET = 4_000


def code_lines(path):
    """A file's lines that are neither docstring, comment nor blank."""
    import ast
    import io
    import tokenize
    source = path.read_text()
    total = len(source.splitlines())
    blank = sum(1 for line in source.splitlines() if not line.strip())
    comments = sum(token.string.count("\n") + 1 for token in tokenize.generate_tokens(io.StringIO(source).readline)
                   if token.type == tokenize.COMMENT)
    docs = 0
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            written = ast.get_docstring(node, clean=False)
            if written:
                docs += written.count("\n") + 1
    return total - blank - comments - docs


def routes():
    """Every document a user or a project is routed by: commands, skills, agents, README, Makefiles."""
    files = list((ROOT / "commands").glob("*.md")) + list((ROOT / "skills").glob("*/SKILL.md")) \
        + list((ROOT / "agents").glob("*.md")) + [ROOT / "README.md"]
    for project in ("smartbin-local", "rc-car"):
        makefile = ROOT.parent / project / "Makefile"
        if makefile.is_file():
            files.append(makefile)
    return "\n".join(path.read_text() for path in files)


def imports_in(scripts):
    """Every module name another script imports, by reading the import lines of each script."""
    named = set()
    for path in scripts:
        for line in path.read_text().splitlines():
            match = re.match(r"\s*(?:import|from)\s+([a-z_]+)", line)
            if match:
                named.add(match.group(1))
    return named


class NothingShipsUnusedTest(unittest.TestCase):
    def test_every_script_is_routed_to_or_imported(self):
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        text, imported = routes(), imports_in(scripts)
        orphans = [path.name for path in scripts
                   if path.stem not in LIBRARIES and path.name not in text
                   and path.stem not in imported]
        self.assertEqual(orphans, [], "no command, skill, agent, README or project Makefile names "
                                      "these, and no script imports them: %s" % orphans)

    def test_every_library_is_imported_by_a_script(self):
        imported = imports_in(list((ROOT / "scripts").glob("*.py")))
        unused = sorted(LIBRARIES - imported)
        self.assertEqual(unused, [], "libraries nothing imports: %s" % unused)

    def test_every_skill_and_agent_is_named_somewhere_a_user_looks(self):
        text = "\n".join((ROOT / name).read_text() for name in ("README.md",)) \
            + "\n".join(p.read_text() for p in (ROOT / "commands").glob("*.md")) \
            + "\n".join(p.read_text() for p in (ROOT / "skills").glob("*/SKILL.md"))
        skills = [p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")]
        agents = [p.stem for p in (ROOT / "agents").glob("*.md")]
        unnamed = [name for name in skills + agents if name not in text]
        self.assertEqual(unnamed, [], "skills or agents nothing routes to: %s" % unnamed)

    def test_the_scripts_stay_within_their_code_budget(self):
        counted = {path.name: code_lines(path) for path in sorted((ROOT / "scripts").glob("*.py"))}
        total = sum(counted.values())
        biggest = sorted(counted.items(), key=lambda pair: -pair[1])[:3]
        self.assertLessEqual(total, SCRIPTS_CODE_BUDGET,
                             "scripts/ is %d code lines against a budget of %d: refactor, delete, or raise the "
                             "number here with a reason. Biggest: %s"
                             % (total, SCRIPTS_CODE_BUDGET, ", ".join("%s %d" % pair for pair in biggest)))

    def test_every_open_backlog_item_names_the_design_that_needs_it(self):
        # W14: pull, never push. An item without a design behind it is not built.
        text = (ROOT / "scrum" / "PRODUCT_BACKLOG.md").read_text()
        sections = re.split(r"\n(?=### )", text)
        missing = []
        for section in sections:
            head = section.splitlines()[0] if section else ""
            if head.startswith("### ") and "~~" not in head and "**Needed by:**" not in section:
                missing.append(head[4:60])
        self.assertEqual(missing, [], "open items with no `**Needed by:**` line: %s" % missing)


if __name__ == "__main__":
    unittest.main()
