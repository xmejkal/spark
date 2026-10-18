"""P296: findings rows live in one file per PR, so parallel PRs never conflict in docs/observations/INDEX.md."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "docs" / "observations" / "INDEX.md"
ROWS = ROOT / "docs" / "observations" / "rows"
INDEX_ROWS = 1067  # frozen on 2026-10-18 at AT459; an old row's status may change, but no row is added
HEADER = "| # | claim | source | status | evidence / where it went |"
FILE_NAME = re.compile(r"[a-z0-9-]+\.md")


def section(text, heading):
    """The lines under a '## heading', up to the next one."""
    lines = text.splitlines()
    start = lines.index(heading) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def table_rows(lines):
    return [line for line in lines if line.startswith("| ") and not line.startswith(("| ---", "| # ", "| status "))]


def statuses(index_text):
    """The status words, from INDEX.md's own status table, so they are written once."""
    return [re.match(r"\| `(\w+)`", row).group(1)
            for row in table_rows(section(index_text, "## Status, and what each one obliges"))]


def rows_file_problems(name, text, words):
    """What breaks the one form of a rows file, or nothing."""
    problems = [] if FILE_NAME.fullmatch(name) else [f"{name}: name is not [a-z0-9-]+.md"]
    if HEADER not in text.splitlines():
        problems.append(f"{name}: no header {HEADER}")
    for number, row in enumerate(table_rows(text.splitlines()), 1):
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if cells[0] != str(number):
            problems.append(f"{name}: row {number} is numbered {cells[0]!r}")
        if len(cells) != 5 or not cells[3].split(" ")[0].strip(",:;") in words:
            problems.append(f"{name}: row {number} has no status word from {words}")
    return problems


class ObservationRowsTest(unittest.TestCase):
    def setUp(self):
        self.index = INDEX.read_text()
        self.words = statuses(self.index)

    def test_the_status_words_come_from_the_index_status_table(self):
        self.assertEqual(self.words, ["raised", "verified", "acted", "rejected", "closed"])

    def test_the_index_takes_no_new_rows(self):
        self.assertEqual(len(table_rows(section(self.index, "## The table"))), INDEX_ROWS,
                         "new rows go to docs/observations/rows/<card>-<topic>.md, not INDEX.md")

    def test_each_rows_file_has_the_one_form(self):
        files = sorted(ROWS.glob("*.md"))
        self.assertTrue(files, f"no rows file in {ROWS}")
        for rows_file in files:
            self.assertEqual(rows_file_problems(rows_file.name, rows_file.read_text(), self.words), [])

    def test_the_form_check_refuses_a_gap_a_bad_word_and_a_bad_name(self):
        text = f"{HEADER}\n| --- | --- | --- | --- | --- |\n| 1 | a | b | raised | c |\n| 3 | a | b | maybe | c |\n"
        self.assertEqual(rows_file_problems("P1_x.md", text, self.words), [
            "P1_x.md: name is not [a-z0-9-]+.md",
            "P1_x.md: row 2 is numbered '3'",
            f"P1_x.md: row 2 has no status word from {self.words}"])


if __name__ == "__main__":
    unittest.main()
