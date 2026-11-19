"""P927: the structure block in AGENTS.md follows the code, and the token budget's table follows the agents' files."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import map as area_map  # noqa: E402  (not `map`: that is a built-in)

AGENTS_PAGE = ROOT / "AGENTS.md"
BUDGET_PAGE = ROOT / "scrum" / "README.md"
AGENT_FOLDER = ROOT / ".claude" / "agents"
#: The pages that the structure block sends a reader to.
LINKED_PAGES = ("scrum/VISION.md", "docs/guide/map.md", "docs/guide/how-it-works.md")
BUDGET_HEADING = "## The token budget"
#: The agents whose files the token budget's table links. A new row with a link joins this list on purpose.
LINKED_AGENTS = ("architect", "refuter")

AREA = re.compile(r"scripts/spark/([a-z_]+)")
MODEL_WORD = re.compile(r"\b(fable|opus|sonnet|haiku)\b")
AGENT_LINK = re.compile(r"\.claude/agents/([a-z-]+)\.md")
MODEL_LINE = re.compile(r"^model:\s*(\S+)", re.MULTILINE)


def named_areas(text):
    """The sorted set of the areas that a text names as `scripts/spark/<area>`."""
    return sorted(set(AREA.findall(text)))


def row_model(table_row):
    """The first model word in a table row's last cell, in lower case, or None when the cell names no model."""
    found = MODEL_WORD.search(table_row.strip().strip("|").split("|")[-1].lower())
    return found.group(1) if found else None


def agent_rows(text):
    """[(agent, row)] for each table row under the token budget's heading that links an agent's file."""
    section = text.split(BUDGET_HEADING, 1)[1].split("\n## ", 1)[0]
    return [(link.group(1), line) for line in section.splitlines() if line.lstrip().startswith("|")
            for link in AGENT_LINK.finditer(line)]


class NamedAreasTest(unittest.TestCase):
    def test_each_area_is_given_once_and_in_order(self):
        text = "`scripts/spark/core` holds the base, `scripts/spark/bench` the board, and `scripts/spark/core` again."
        self.assertEqual(named_areas(text), ["bench", "core"])

    def test_a_text_that_lacks_an_area_does_not_equal_the_code(self):
        self.assertNotEqual(named_areas("only `scripts/spark/core/` is here"), ["bench", "core"])

    def test_the_placeholder_is_no_area(self):
        self.assertEqual(named_areas("each area is `scripts/spark/<area>`"), [])


class RowModelTest(unittest.TestCase):
    def test_the_first_model_word_of_the_last_cell_in_lower_case(self):
        self.assertEqual(row_model("| the refuter | an agent | Opus, and Fable for a design |"), "opus")

    def test_a_row_with_another_model(self):
        self.assertEqual(row_model("  | a builder of docs | an agent | Sonnet |"), "sonnet")

    def test_a_model_word_in_the_job_is_not_the_rows_model(self):
        self.assertEqual(row_model("| the plan that Fable wrote | the main session | Opus |"), "opus")

    def test_a_row_that_names_no_model(self):
        self.assertIsNone(row_model("| spark's own agents | each | the model its file names |"))


TABLE_TEXT = ("## Before\n\n| a job | the [`early`](../.claude/agents/early.md) agent | Opus |\n\n"
              "## The token budget\n\nThe [`prose`](../.claude/agents/prose.md) agent is named in a sentence.\n\n"
              "  | the job | who runs it | model |\n"
              "  | a design | the [`first`](../.claude/agents/first.md#top) agent | Fable |\n"
              "  | a check | [`second`](/.claude/agents/second.md) and [`third`](../.claude/agents/third.md) | Opus |\n\n"
              "## After\n\n| a job | the [`late`](../.claude/agents/late.md) agent | Sonnet |\n")


class AgentRowsTest(unittest.TestCase):
    def test_each_link_of_each_table_row_under_the_heading_and_no_other(self):
        self.assertEqual([agent for agent, _ in agent_rows(TABLE_TEXT)], ["first", "second", "third"])

    def test_a_link_comes_with_its_whole_row(self):
        self.assertEqual(row_model(dict(agent_rows(TABLE_TEXT))["first"]), "fable")


class TheStructureBlockTest(unittest.TestCase):
    def test_agents_md_names_the_areas_that_the_code_has(self):
        said = named_areas(AGENTS_PAGE.read_text(encoding="utf-8"))
        real = sorted(area[0] for area in area_map.AreaMap.of(ROOT).areas)
        self.assertEqual(said, real, "AGENTS.md lacks %s and names %s, which the code does not have"
                         % (sorted(set(real) - set(said)) or "no area", sorted(set(said) - set(real)) or "no area"))

    def test_agents_md_links_the_vision_the_map_and_how_it_works(self):
        text = AGENTS_PAGE.read_text(encoding="utf-8")
        self.assertEqual([page for page in LINKED_PAGES if "](%s" % page not in text], [])


class TheModelTableTest(unittest.TestCase):
    def test_a_row_that_links_an_agents_file_names_the_files_model(self):
        rows = agent_rows(BUDGET_PAGE.read_text(encoding="utf-8"))
        self.assertEqual(sorted(agent for agent, _ in rows), list(LINKED_AGENTS))
        for agent, row in rows:
            in_file = MODEL_LINE.search((AGENT_FOLDER / ("%s.md" % agent)).read_text(encoding="utf-8"))
            self.assertIsNotNone(in_file, "the %s agent's file names no model" % agent)
            self.assertEqual(row_model(row), in_file.group(1).lower(),
                             "the table's row for the %s agent and the model in its file differ" % agent)


if __name__ == "__main__":
    unittest.main()
