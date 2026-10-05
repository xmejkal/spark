"""
Proof that nothing ships unused. (How big the product is, the pre-push gate says at every push — P99.)

On 2026-09-29 a third of this repository was deleted: a findings store that never resolved a
finding, an eval harness nobody re-ran, a second file format for a design, a check neither
project ran, three agents nothing routed to, a skill with no code. Every one had tests, so every
one looked alive. Nothing asked "who calls this?" — this does, at every commit (W15).

    python3 -m unittest discover -s tests
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

#: Modules that are imported, never run: they earn their place by being imported.
LIBRARIES = {"copper", "outcomes", "design", "store", "drawer", "needs"}

def routes():
    """Every document a user or a project is routed by: commands, skills, agents, README, Makefiles."""
    files = list((ROOT / "commands").glob("*.md")) + list((ROOT / "skills").glob("*/SKILL.md")) \
        + list((ROOT / "agents").glob("*.md")) + [ROOT / "README.md"] \
        + sorted((ROOT / "docs" / "guide").glob("*.md")) + [path for path in [ROOT / "AGENTS.md"] if path.is_file()]
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
            + "\n".join(path.read_text() for path in sorted((ROOT / "docs" / "guide").glob("*.md")) + [path for path in [ROOT / "AGENTS.md"] if path.is_file()]) \
            + "\n".join(p.read_text() for p in (ROOT / "commands").glob("*.md")) \
            + "\n".join(p.read_text() for p in (ROOT / "skills").glob("*/SKILL.md"))
        skills = [p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")]
        agents = [p.stem for p in (ROOT / "agents").glob("*.md")]
        unnamed = [name for name in skills + agents if name not in text]
        self.assertEqual(unnamed, [], "skills or agents nothing routes to: %s" % unnamed)

    #: Scripts that still name a tool's executable, until their task moves them to tools.find (P82).
    NOT_YET_MOVED = {}  # empty since the final review: a project's own cli.ts runs under the ts-runtime role

    def test_no_script_but_tools_names_a_tool_s_executable(self):
        names = {entry.get("exe") for key, entry in json.loads((ROOT / "data" / "tools.json").read_text()).items()
                 if isinstance(entry, dict) and entry.get("exe")} | {"bun"}
        named = {}
        for path in sorted((ROOT / "scripts").glob("*.py")):
            if path.name == "tools.py":
                continue
            text = path.read_text()
            found = {name for name in names if '"%s"' % name in text}
            if found - self.NOT_YET_MOVED.get(path.name, set()):
                named[path.name] = sorted(found - self.NOT_YET_MOVED.get(path.name, set()))
        self.assertEqual(named, {}, "ask tools.find for the tool instead (P82)")

    def test_every_script_still_allowed_to_name_a_tool_still_does(self):
        stale = {name: sorted(tools_named) for name, tools_named in self.NOT_YET_MOVED.items()
                 if not all('"%s"' % tool in (ROOT / "scripts" / name).read_text() for tool in tools_named)}
        self.assertEqual(stale, {}, "a moved script left in NOT_YET_MOVED")

    def test_nothing_shipped_names_one_persons_home(self):
        # P44: an agent file named a path in its author's home for the catalog; on anyone else's machine that
        # is a path to nothing. docs/ and scrum/ are records of what happened, and may quote one.
        home = re.compile(r"/Users/[A-Za-z]|/home/[A-Za-z]|[A-Z]:\\\\Users")
        named = ["%s:%d" % (path.relative_to(ROOT), number)
                 for folder in ("commands", "skills", "agents", "scripts", "boards", "catalog", "data", "tests")
                 for path in sorted((ROOT / folder).rglob("*")) if path.is_file() and path.suffix in (".md", ".py", ".json", ".ts")
                 and "mutations" not in path.parts  # a mutation table plants the defect on purpose
                 for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1) if home.search(line)]
        self.assertEqual(named, [], "a shipped file names one person's home directory")

    def test_the_archive_holds_no_open_item(self):
        # P102a: the backlog lives in GitHub Projects; the Markdown file is the frozen archive, and every heading in it
        # says where its item went (MOVED to an issue) or how it ended.
        closed = re.compile(r"MOVED|DONE|ANSWERED|CLOSED|PARKED|MERGED|DELETED|SPLIT|~~")
        text = (ROOT / "scrum" / "PRODUCT_BACKLOG.md").read_text()
        self.assertIn("This is the archive", text.split("\n### ")[0])
        unmarked = [line[4:60] for line in text.splitlines() if line.startswith("### ") and not closed.search(line)]
        self.assertEqual(unmarked, [], "archive headings with no MOVED/closed marker: %s" % unmarked)

class TheGlossaryDefinesWordsThisRepositoryActuallyUsesTest(unittest.TestCase):
    """
    P48. A glossary drifts in one direction: it keeps defining what the code stopped doing.

    So the test is not that every word is defined — that cannot be scoped — but that every word it
    DOES define is still used here. A term that has left the code takes its entry with it.
    """

    #: Words the glossary explains as plain English inside an entry rather than as repository
    #: vocabulary, so nothing outside is expected to say them.
    NOT_VOCABULARY = {"The three outcomes", "The words this repository uses"}

    @staticmethod
    def terms():
        text = (ROOT / "GLOSSARY.md").read_text()
        for line in text.splitlines():
            if line.startswith("### "):
                # "### Anchor, and re-anchoring" -> "Anchor"; "### `verified`" -> "verified"
                head = line[4:].split(" — ")[0]
                for term in re.split(r",| and ", head):
                    term = re.sub(r"^(or|and) ", "", term.strip()).strip("`")
                    if term:
                        yield term

    def test_the_glossary_exists_and_the_readme_points_at_it(self):
        self.assertTrue((ROOT / "GLOSSARY.md").is_file())
        self.assertIn("GLOSSARY.md", (ROOT / "README.md").read_text(),
                      "a document nobody is sent to is a document nobody opens")

    def test_every_word_it_defines_is_used_somewhere_else(self):
        # NOT tests/mutations: a table quotes the text it mutates, so a glossary entry would
        # prove itself real by appearing in the mutation written to break it. Found by that
        # mutation escaping.
        haystack = "\n".join(
            path.read_text() for folder in ("scripts", "scrum", "tests", "commands", "skills")
            for path in (ROOT / folder).rglob("*")
            if path.is_file() and path.suffix in (".py", ".md", ".json")
            and "mutations" not in path.parts)
        haystack += (ROOT / "README.md").read_text()
        haystack += "\n".join(path.read_text() for path in sorted((ROOT / "docs" / "guide").glob("*.md")) + [path for path in [ROOT / "AGENTS.md"] if path.is_file()])
        stale = [term for term in self.terms()
                 if term not in self.NOT_VOCABULARY and term.lower() not in haystack.lower()]
        self.assertEqual(stale, [], "the glossary defines words this repository no longer uses: %s"
                                    % stale)

    def test_it_defines_the_terms_the_product_owner_had_to_ask_about(self):
        # The question that made this an item, on 2026-09-30: what is a mutation, an anchor, a gate.
        defined = " ".join(self.terms()).lower()
        for asked in ("mutation", "anchor", "gate"):
            self.assertIn(asked, defined, "%s is why this file exists" % asked)


if __name__ == "__main__":
    unittest.main()
