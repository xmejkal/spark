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

#: The line budget for the product's scripts. A change that would exceed it deletes something
#: first; raising the number is a decision, made here, with a reason beside it.
SCRIPTS_LINE_BUDGET = 6_600    # 5,731 after the cut of 2026-09-29; 6,020 after the catalog (PO's keep-everything
                               # rule); 6,500 for P31, the simulation from records — ordered by the PO on
                               # 2026-09-29 night with "you can also increase the limit"; 6,600 for P6 the same
                               # night (host parts placed and wired). Still a ceiling: a change that would pass
                               # it deletes something first, or says here why not.


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

    def test_the_scripts_stay_within_their_line_budget(self):
        lines = sum(len(path.read_text().splitlines()) for path in (ROOT / "scripts").glob("*.py"))
        self.assertLessEqual(lines, SCRIPTS_LINE_BUDGET,
                             "scripts/ is %d lines against a budget of %d: delete something, or "
                             "raise the budget here with a reason" % (lines, SCRIPTS_LINE_BUDGET))

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
