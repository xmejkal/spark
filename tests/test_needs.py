"""P96: a goal's needs, and the store's candidates for each (docs/2026-10-04-store-design.md §5.3, §6.2, §8 S and M)."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import parts  # noqa: E402


def run(argv):
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


def a_file(items):
    path = Path(tempfile.mkdtemp()) / "needs.json"
    path.write_text(json.dumps(items))
    return str(path)


class TheNeedsFileTest(unittest.TestCase):
    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def saved(self):
        return json.loads((self.project / ".spark" / "needs.json").read_text())

    def test_a_goal_s_needs_are_written_and_the_folder_made(self):
        said, code = run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture", "condition": "indoor pot, short probe; low power"},
            {"id": "board", "does": "compute", "what": "microcontroller", "condition": "deep sleep"}])])
        self.assertEqual((code, said["data"]["written"]), (0, True))
        self.assertEqual(self.saved(), {"schema": 1, "needs": [
            {"id": "soil", "does": "sense", "what": "soil-moisture", "condition": "indoor pot, short probe; low power"},
            {"id": "board", "does": "compute", "what": "microcontroller", "condition": "deep sleep"}]})

    def test_a_mark_is_set_and_a_retried_write_changes_nothing(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        marked = a_file([{"id": "soil", "mark": "have"}])
        said, _ = run(["--needs-set", str(self.project), marked])
        self.assertEqual(said["data"]["changes"], [{"need": "soil", "new": False, "was": {"mark": None}, "now": {"mark": "have"}}])
        self.assertEqual(run(["--needs-set", str(self.project), marked])[0]["data"]["changes"], [])

    def test_a_need_holds_no_reason_count_place_or_pick(self):
        for extra in ({"why": "owned"}, {"count": 8}, {"place": "box 3"}, {"pick": [{"part": "x"}]}):
            with self.subTest(extra=extra):
                said, code = run(["--needs-set", str(self.project), a_file([dict({"id": "soil", "does": "sense", "what": "x"}, **extra)])])
                self.assertEqual((said["status"], code), ("problems", 1))
        self.assertFalse((self.project / ".spark" / "needs.json").exists())

    def test_a_wrong_verb_or_mark_refuses_the_whole_write(self):
        said, code = run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "beep", "what": "alarm"}])])
        self.assertEqual(code, 1)
        self.assertFalse((self.project / ".spark" / "needs.json").exists())
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        self.assertEqual(run(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "maybe"}])])[1], 1)

    def test_a_dry_run_writes_nothing(self):
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "x"}]), "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse(self.project.exists())

    def test_a_needs_file_in_the_wrong_shape_is_named_not_a_traceback(self):
        (self.project / ".spark").mkdir(parents=True)
        (self.project / ".spark" / "needs.json").write_text('{"needs": "soil"}')
        said, code = run(["--needs", str(self.project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("needs.json", said["unchecked"][0]["sentence"])


def a_store_with_a_drawer():
    """A scratch store: a soil probe in the catalog (owned ×8), a speaker owned without a record, a dead part, a board."""
    home = Path(tempfile.mkdtemp())
    for folder in ("catalog", "drawer"):
        (home / folder).mkdir()
    (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Capacitive soil moisture sensor",
                                                              "kind": "sensor", "function": [{"does": "sense", "what": "soil-moisture"}]}))
    (home / "catalog" / "x-other.json").write_text(json.dumps({"schema": 1, "id": "x-other", "name": "A gas sensor", "kind": "sensor",
                                                               "function": [{"does": "sense", "what": "gas"}]}))
    entries = {"probe": {"label": "soil probe", "count": 8, "is": {"part": "x-soil"}},
               "speaker": {"label": "3 W speaker", "count": 2, "function": [{"does": "sound", "what": "speaker"}]},
               "dead": {"label": "an old buzzer", "count": 1, "function": [{"does": "sound", "what": "buzzer"}], "skip": "dead"},
               "mp3": {"label": "MP3 mini module", "count": 1, "function": [{"does": "sound", "what": "mp3-player"}], "unsure": True},
               "dead-probe": {"label": "a burnt gas sensor", "count": 3, "is": {"part": "x-other"}, "skip": "dead"},
               "old-amp": {"label": "an old amp", "count": 1, "is": {"part": "gone-part"}, "function": [{"does": "sound", "what": "amplifier"}]},
               "board": {"label": "FireBeetle", "count": 1, "is": {"board": "firebeetle2-esp32s3"}, "used_in": {"smartbin-local": 1}},
               "buttons": {"label": "a bag of buttons", "count": "many", "is": {"part": "tactile-button"}}}
    for key, entry in entries.items():
        (home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1}, **entry)))
    return home


class TheMatcherTest(unittest.TestCase):
    """§6.2's code half, §8 M: candidates by verb, store first, owned first, with owned and free counts and what each owes."""

    def setUp(self):
        self.home, self.project = a_store_with_a_drawer(), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "sound", "what": "alarm"},
            {"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "input", "does": "input", "what": "button"},
            {"id": "keep", "does": "store", "what": "logs"}])])
        said, self.code = run(["--match", str(self.project)])
        self.needs = {need["need"]: need for need in said["data"]["needs"]}

    def test_owned_first_with_counts_and_what_it_owes(self):
        first = self.needs["soil"]["candidates"][0]
        self.assertEqual((first["id"], first["in"], first["owned"], first["free"], first["what_matches"]), ("x-soil", "catalog", 8, 8, True))
        self.assertIn("footprint", first["owes"])
        ids = [c["id"] for c in self.needs["soil"]["candidates"]]
        self.assertLess(ids.index("x-soil"), ids.index("x-other"), "a same-verb record that is not owned comes after")

    def test_a_reservation_is_not_free(self):
        board = [c for c in self.needs["board"]["candidates"] if c["id"] == "firebeetle2-esp32s3"][0]
        self.assertEqual((board["owned"], board["free"], board["in"]), (1, 0, "library"))

    def test_an_owned_part_without_a_record_is_a_candidate_and_unsure_says_so(self):
        alarm = {c["entry"]: c for c in self.needs["alarm"]["candidates"] if c["entry"]}
        self.assertEqual((alarm["speaker"]["owned"], alarm["speaker"]["in"]), (2, "drawer"))
        self.assertTrue(alarm["mp3"]["unsure"])

    def smell(self):
        """The candidates for one more need, matched alone: the setUp needs fill a 4 KB page."""
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "smell", "does": "sense", "what": "gas"}]}))
        said, _ = run(["--match", str(self.project)])
        return [n for n in said["data"]["needs"] if n["need"] == "smell"][0]["candidates"]

    def test_an_owned_candidate_beats_a_better_worded_one_that_is_not_owned(self):
        ids = [c["id"] for c in self.smell()]
        self.assertEqual(ids[0], "x-soil", "x-soil is owned and its `what` is not gas; every unowned record, x-other included, comes after")
        self.assertIn("x-other", ids)

    def test_an_entry_whose_record_is_gone_is_still_offered_from_the_drawer(self):
        amp = {c["entry"]: c for c in self.needs["alarm"]["candidates"] if c["entry"]}["old-amp"]
        self.assertEqual((amp["in"], amp["owned"], amp["id"]), ("drawer", 1, None))

    def test_a_dead_part_is_never_owned_nor_a_candidate(self):
        other = [c for c in self.smell() if c["id"] == "x-other"][0]
        self.assertEqual((other["owned"], other["free"]), (0, 0), "three burnt sensors are not three sensors")
        self.assertNotIn("dead", [c["entry"] for c in self.needs["alarm"]["candidates"]])

    def test_many_stays_many(self):
        button = [c for c in self.needs["input"]["candidates"] if c["id"] == "tactile-button"][0]
        self.assertEqual((button["owned"], button["free"]), ("many", "many"))

    def test_a_verb_nothing_has_is_an_empty_answer(self):
        self.assertEqual((self.code, self.needs["keep"]["candidates"]), (0, []))

    def test_a_need_with_no_verb_is_named(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "x", "what": "y"}]}))
        said, code = run(["--match", str(self.project)])
        self.assertEqual((said["status"], code), ("problems", 1))


if __name__ == "__main__":
    unittest.main()
