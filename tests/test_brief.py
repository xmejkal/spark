"""
Proof that `Brief.from_project` reads `.spark/project.json` on each call: the default for a missing file, a non-file, bad JSON or a non-object; an unreadable file raises OSError.

    python3 -m unittest tests.test_brief
"""

import os
import subprocess
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
        self.assertEqual(brief.must, ("A", "B"))
        self.assertEqual(brief.prefer, ("seeed",))
        self.assertEqual(brief.sellers, ("gme", "hadex"))

    def test_no_project_a_missing_file_and_bad_json_read_as_empty(self):
        for brief in (Brief.from_project(None), brief_of(None), brief_of("{not json"), brief_of("[1]")):
            self.assertEqual((brief.must, brief.prefer, brief.sellers), ((), None, None))

    def test_a_must_that_is_not_a_list_reads_as_empty(self):
        for text in ('{"must": "A"}', '{"must": 3}', '{"must": {"a": "b"}}', '{"must": null}'):
            self.assertEqual(brief_of(text).must, ())

    def test_a_non_string_inside_must_is_dropped(self):
        self.assertEqual(brief_of('{"must": ["A", 3, null, ["B"], "C"]}').must, ("A", "C"))

    def test_prefer_and_sellers_need_a_non_empty_list_of_strings(self):
        for text in ('{"prefer": []}', '{"prefer": "x"}', '{"prefer": ["x", 1]}', '{"sellers": [2]}'):
            brief = brief_of(text)
            self.assertEqual((brief.prefer, brief.sellers), (None, None))

    @unittest.skipIf(os.geteuid() == 0, "root reads any file")
    def test_an_unreadable_file_raises_oserror(self):
        folder = Path(tempfile.mkdtemp())
        (folder / ".spark").mkdir()
        path = folder / ".spark" / "project.json"
        path.write_text("{}")
        path.chmod(0)
        self.addCleanup(path.chmod, 0o600)
        with self.assertRaises(OSError):
            Brief.from_project(folder)

    def test_a_fifo_is_no_file_and_is_not_read(self):
        folder = Path(tempfile.mkdtemp())
        (folder / ".spark").mkdir()
        os.mkfifo(folder / ".spark" / "project.json")
        code = "import sys; sys.path.insert(0, %r); from brief import Brief; print(Brief.from_project(%r).must)" % (str(ROOT / "scripts"), str(folder))
        try:
            done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            self.fail("T1: reading a fifo blocked")
        self.assertEqual(done.stdout.strip(), "()")


if __name__ == "__main__":
    unittest.main()
