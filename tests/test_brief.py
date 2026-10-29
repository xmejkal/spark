"""
Proof that `Brief.from_project` reads `.spark/project.json` once and never raises.

    python3 -m unittest tests.test_brief
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from brief import Brief  # noqa: E402


def brief_of(text):
    """The Brief of a project folder whose project.json holds this text (None: no file)."""
    folder = Path(tempfile.mkdtemp())
    if text is not None:
        (folder / ".spark").mkdir()
        (folder / ".spark" / "project.json").write_text(text)
    return Brief.from_project(folder)


class BriefTest(unittest.TestCase):
    def test_every_field_is_read(self):
        brief = brief_of('{"must": ["A", "B"], "prefer": ["Seeed"], "sellers": ["GME", "Hadex"]}')
        self.assertEqual(brief.must, ["A", "B"])
        self.assertEqual(brief.prefer, ("seeed",))
        self.assertEqual(brief.sellers, ("gme", "hadex"))

    def test_no_project_a_missing_file_and_bad_json_read_as_empty(self):
        for brief in (Brief.from_project(None), brief_of(None), brief_of("{not json"), brief_of("[1]")):
            self.assertEqual((brief.must, brief.prefer, brief.sellers), ([], None, None))

    def test_a_must_that_is_not_a_list_reads_as_empty(self):
        for text in ('{"must": "A"}', '{"must": 3}', '{"must": {"a": "b"}}', '{"must": null}'):
            self.assertEqual(brief_of(text).must, [])

    def test_a_non_string_inside_must_is_dropped(self):
        self.assertEqual(brief_of('{"must": ["A", 3, null, ["B"], "C"]}').must, ["A", "C"])

    def test_prefer_and_sellers_need_a_non_empty_list_of_strings(self):
        for text in ('{"prefer": []}', '{"prefer": "x"}', '{"prefer": ["x", 1]}', '{"sellers": [2]}'):
            brief = brief_of(text)
            self.assertEqual((brief.prefer, brief.sellers), (None, None))


if __name__ == "__main__":
    unittest.main()
