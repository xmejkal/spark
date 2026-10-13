"""P226: the journey picture on the README's front page follows the README's status table."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT =Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import journey  # noqa: E402


class TheJourneyPictureTest(unittest.TestCase):
    def test_each_step_takes_its_status_from_the_readme_table(self):
        table = "| [Drawer](docs/guide/journey.md#drawer) | **partly**: what you own |\n" \
                "| [Build](docs/guide/journey.md#build) | **works**: a board |\n"
        self.assertEqual(journey.statuses(table), {"Drawer": "partly", "Build": "works"})

    def test_a_step_the_table_does_not_name_is_refused(self):
        with self.assertRaises(SystemExit):
            journey.svg({"Drawer": "partly"})

    def test_the_committed_picture_is_the_one_the_readme_table_draws(self):
        drawn = journey.svg(journey.statuses((ROOT / "README.md").read_text()))
        self.assertEqual((ROOT / journey.PICTURE).read_text(), drawn,
                         "docs/guide/journey.svg is stale: run python3 tools/journey.py")


if __name__ == "__main__":
    unittest.main()
