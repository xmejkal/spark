"""P226: the journey picture on the README's front page follows the README's status table."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import journey  # noqa: E402

TABLE = "| [Drawer](docs/guide/journey/drawer.md) | **partly**: what you own, run on 2026-10-08 |\n" \
        "| [Build](docs/guide/journey/build.md) | **works**: a board, run on 2026-10-11 |\n"


def readme(table, before="", after=""):
    return before + "\n## What works today\n\n" + table + "\n## Before you start\n" + after


class TheJourneyPictureTest(unittest.TestCase):
    def setUp(self):
        self.status = {step[0]: step[5] for step in journey.STEPS}

    def test_each_step_takes_its_status_from_the_what_works_today_table_only(self):
        elsewhere = "| [Build](docs/guide/journey/build.md) | **partly**: an old row |\n"
        self.assertEqual(journey.statuses(readme(TABLE, before=elsewhere, after=elsewhere)),
                         {"Drawer": "partly", "Build": "works"})

    def test_a_row_that_links_the_old_single_page_gives_no_status(self):
        old = "| [Build](docs/guide/journey.md#build) | **works**: a board, run on 2026-10-11 |\n"
        self.assertEqual(journey.statuses(readme(old)), {})

    def test_a_row_that_links_another_steps_page_gives_no_status(self):
        wrong = "| [Build](docs/guide/journey/drawer.md) | **works**: a board, run on 2026-10-11 |\n"
        self.assertEqual(journey.statuses(readme(wrong)), {})

    def test_the_picture_is_dated_by_the_newest_run_in_that_section(self):
        self.assertEqual(journey.runs_up_to(readme(TABLE, after="2027-01-01")), "2026-10-11")

    def test_a_step_the_table_does_not_name_is_refused(self):
        del self.status["Bench"]
        with self.assertRaises(SystemExit):
            journey.svg(self.status, "2026-10-12")

    def test_a_step_the_picture_does_not_have_is_refused(self):
        self.status["Order"] = "not yet"
        with self.assertRaises(SystemExit):
            journey.svg(self.status, "2026-10-12")

    def test_a_status_whose_note_was_written_for_another_is_refused(self):
        self.status["Bench"] = "works"
        with self.assertRaises(SystemExit):
            journey.svg(self.status, "2026-10-12")

    def test_the_committed_picture_is_the_one_the_readme_table_draws(self):
        text = (ROOT / "README.md").read_text()
        self.assertEqual((ROOT / journey.PICTURE).read_text(),
                         journey.svg(journey.statuses(text), journey.runs_up_to(text)),
                         "docs/guide/journey.svg is stale: run python3 tools/journey.py")


if __name__ == "__main__":
    unittest.main()
