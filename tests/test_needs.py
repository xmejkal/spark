"""P96: a goal's needs, and the store's candidates for each (docs/2026-10-04-store-design.md §5.3, §6.2, §8 S and M)."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import design  # noqa: E402
import emit_board  # noqa: E402
import needs  # noqa: E402
import parts  # noqa: E402
import store  # noqa: E402


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

    def test_a_retried_needs_set_is_carried_out_with_nothing_to_change(self):
        given = a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])
        run(["--needs-set", str(self.project), given])
        said, code = run(["--needs-set", str(self.project), given])
        self.assertEqual((code, said["data"]["written"], said["data"]["changes"]), (0, True, []))

    def test_the_file_is_refused_on_read_for_what_a_write_refuses(self):
        (self.project / ".spark").mkdir(parents=True)
        for need in ({"id": "soil", "does": "fly", "what": "x"}, {"id": "soil", "does": None, "what": "x"},
                     {"id": "soil", "does": "sense", "what": "x", "condition": ""}):
            with self.subTest(need=need):
                (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [need]}))
                said, code = run(["--needs", str(self.project)])
                self.assertEqual(code, 2)
                self.assertIn("needs.json", said["unchecked"][0]["sentence"])

    def test_a_key_the_needs_file_does_not_hold_is_refused_not_dropped(self):
        (self.project / ".spark").mkdir(parents=True)
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [], "goal": "a thirsty plant"}))
        said, code = run(["--needs", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("goal", said["unchecked"][0]["sentence"])

    def test_a_refused_item_is_named_by_its_place_and_its_value(self):
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "x"},
                                                                    {"id": "Soil2", "does": "sense", "what": "x"}])])
        self.assertEqual((code, said["problems"][0]["subject"]), (1, "item 2"))
        self.assertIn('"Soil2"', said["problems"][0]["sentence"])

    def test_a_refused_write_does_not_also_say_nothing_to_change(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "Soil2"}])])
        self.assertNotIn("nothing to change", out.getvalue())

    def test_a_later_item_sees_what_an_earlier_one_set(self):
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"},
                                                                    {"id": "soil", "mark": "have"}])])
        self.assertEqual(code, 0)
        self.assertEqual(self.saved()["needs"], [{"id": "soil", "does": "sense", "what": "soil-moisture", "mark": "have"}])

    def test_a_new_need_with_no_what_is_refused(self):
        self.assertEqual(run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense"}])])[1], 1)

    def test_a_needs_write_says_what_each_value_was(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}]), "--dry-run"])
        self.assertEqual(out.getvalue(), '  would set soil: mark null → "have"\n')

    def test_a_needs_write_over_a_set_value_says_what_it_was(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}])])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "know"}]), "--dry-run"])
        self.assertEqual(out.getvalue(), '  would set soil: mark "have" → "know"\n')

    def test_a_new_need_is_said_value_by_value(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "alarm", "does": "indicate", "what": "alarm"}])])
        self.assertEqual(out.getvalue(), '  set alarm: does null → "indicate"; what null → "alarm"\n')

    def test_a_needs_write_that_fails_halfway_leaves_the_file_whole(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        before = self.saved()
        with mock.patch.object(Path, "replace", side_effect=OSError("the disk is full")):
            _, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}])])
        self.assertEqual((code, self.saved()), (2, before))

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

    def a_needs_file(self, text):
        (self.project / ".spark").mkdir(parents=True, exist_ok=True)
        (self.project / ".spark" / "needs.json").write_text(text if isinstance(text, str) else json.dumps(text))

    def test_a_need_with_no_what_is_named_by_match_not_a_traceback(self):
        self.a_needs_file({"schema": 1, "needs": [{"id": "soil", "does": "sense"}]})
        said, code = run(["--match", str(self.project)])
        self.assertEqual((said["status"], code, said["problems"][0]["subject"]), ("problems", 1, "soil"))
        self.assertIn("`what`", said["problems"][0]["sentence"])

    def test_a_file_the_matcher_cannot_trust_is_could_not_run_naming_it(self):
        good = {"id": "soil", "does": "sense", "what": "x"}
        for name, text in (("what is 5", {"schema": 1, "needs": [dict(good, what=5)]}),
                           ("condition is 5", {"schema": 1, "needs": [dict(good, condition=5)]}),
                           ("mark is maybe", {"schema": 1, "needs": [dict(good, mark="maybe")]}),
                           ("a stray field", {"schema": 1, "needs": [dict(good, why="owned 8")]}),
                           ("a duplicate id", {"schema": 1, "needs": [good, dict(good, does="sound")]}),
                           ("a bad id", {"schema": 1, "needs": [dict(good, id="Soil!")]}),
                           ("schema 2", {"schema": 2, "needs": [good]})):
            self.a_needs_file(text)
            for flag in ("--needs", "--match"):
                with self.subTest(name=name, flag=flag):
                    said, code = run([flag, str(self.project)])
                    self.assertEqual((said["status"], code), ("could-not-run", 2))
                    self.assertIn("needs.json", said["unchecked"][0]["sentence"])

    def test_a_needs_set_over_a_file_with_a_stray_field_changes_nothing(self):
        text = json.dumps({"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "x", "why": "owned 8"}]})
        self.a_needs_file(text)
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}])])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual((self.project / ".spark" / "needs.json").read_text(), text)

    def test_text_mode_says_why_a_needs_set_was_refused(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = parts.main(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "x", "why": "owned"}])])
        self.assertEqual(code, 1)
        self.assertIn("  refused, so nothing was written: soil — why: not a need's field", out.getvalue())


def a_store_with_a_drawer():
    """A scratch store: a soil probe in the catalog (owned ×8), a speaker owned without a record, a dead part, a board."""
    home = Path(tempfile.mkdtemp())
    for folder in ("catalog", "drawer"):
        (home / folder).mkdir()
    (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Capacitive soil moisture sensor",
                                                              "kind": "sensor", "function": [{"does": "sense", "what": "soil-moisture"}]}))
    (home / "catalog" / "x-other.json").write_text(json.dumps({"schema": 1, "id": "x-other", "name": "A gas sensor", "kind": "sensor",
                                                               "function": [{"does": "sense", "what": "gas"}]}))
    (home / "catalog" / "x-silent.json").write_text(json.dumps({"schema": 1, "id": "x-silent", "name": "A mystery sensor", "kind": "sensor"}))
    entries = {"silent": {"label": "a mystery sensor", "count": 2, "is": {"part": "x-silent"}},
               "probe": {"label": "soil probe", "count": 8, "is": {"part": "x-soil"}},
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
            {"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "input", "does": "input", "what": "button"}])])
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

    def catalog(self, *records):
        for record in records:
            (self.home / "catalog" / (record["id"] + ".json")).write_text(json.dumps(dict({"schema": 1, "kind": "sensor"}, **record)))

    def alone(self, need):
        """One need, matched alone (a full page holds few needs): the need's answer, with its candidates and `more`."""
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [need]}))
        said, _ = run(["--match", str(self.project)])
        return said["data"]["needs"][0]

    def test_a_project_s_own_board_is_a_candidate(self):
        (self.project / "boards").mkdir(parents=True)
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        (self.project / "boards" / "my-own-board.json").write_text(json.dumps(dict(board, id="my-own-board")))
        found = [c["in"] for c in self.alone({"id": "mcu", "does": "compute", "what": "microcontroller"})["candidates"] if c["id"] == "my-own-board"]
        self.assertEqual(found, ["project"])

    def test_what_matches_only_through_a_function_with_the_need_s_verb(self):
        self.catalog({"id": "a-combo", "name": "A combo board", "function": [{"does": "sense", "what": "temperature"},
                                                                            {"does": "indicate", "what": "light"}]},
                     {"id": "b-light", "name": "B ambient sensor", "function": [{"does": "sense", "what": "light"}]})
        found = {c["id"]: c for c in self.alone({"id": "lux", "does": "sense", "what": "light"})["candidates"] if c["id"]}
        self.assertEqual((found["a-combo"]["what_matches"], found["b-light"]["what_matches"]), (False, True))

    def test_the_need_s_words_match_a_function_however_they_are_written(self):
        self.catalog({"id": "y-probe", "name": "SEN0193", "function": [{"does": "sense", "what": "soil-moisture"}]})
        for what in ("soil moisture", "Soil Moisture ", "soil-moisture"):
            with self.subTest(what=what):
                found = {c["id"]: c for c in self.alone({"id": "wet", "does": "sense", "what": what})["candidates"] if c["id"]}
                self.assertTrue(found["y-probe"]["what_matches"])

    def test_an_alias_matches_other_words_do_not_and_an_alias_that_is_no_list_is_ignored(self):
        self.catalog({"id": "z-dist", "name": "VL53L0X", "also_known_as": ["time of flight distance sensor"],
                      "function": [{"does": "sense", "what": "tof"}]},
                     {"id": "z-seven", "name": "Z", "also_known_as": 7, "function": [{"does": "sense", "what": "distance"}]})
        found = {c["id"]: c for c in self.alone({"id": "far", "does": "sense", "what": "distance"})["candidates"] if c["id"]}
        self.assertTrue(found["z-dist"]["what_matches"])
        self.assertTrue(found["z-seven"]["what_matches"], "matched by its function; the stray alias is passed over")
        self.assertFalse(found["x-other"]["what_matches"], "a gas sensor is not a distance sensor")

    def test_a_search_by_words_passes_over_an_alias_that_is_no_list(self):
        self.catalog({"id": "y-seven", "name": "Quirky probe", "also_known_as": 7},
                     {"id": "y-mixed", "name": "Mixed probe", "also_known_as": ["QZ5520", 7]})
        said, code = run(["--need", "quirky"])
        self.assertEqual((code, said["data"]["catalog"]), (0, [{"id": "y-seven", "kind": "sensor", "name": "Quirky probe"}]))
        said, code = run(["--need", "qz5520"])
        self.assertEqual((code, said["data"]["catalog"]), (0, [{"id": "y-mixed", "kind": "sensor", "name": "Mixed probe"}]),
                         "the word in the list names it; the 7 beside it is passed over")

    def test_a_used_up_part_without_a_record_is_not_offered(self):
        (self.home / "drawer" / "used-up.json").write_text(json.dumps({"schema": 1, "label": "an old buzzer", "count": 0,
                                                                       "function": [{"does": "sound", "what": "buzzer"}]}))
        self.assertNotIn("used-up", [c["entry"] for c in self.alone({"id": "alarm", "does": "sound", "what": "alarm"})["candidates"]])

    def test_a_candidate_with_the_need_s_words_is_never_cut_by_the_cap(self):
        for number in range(9):
            (self.home / "drawer" / ("t%d.json" % number)).write_text(json.dumps(
                {"schema": 1, "label": "thermometer %d" % number, "count": 1, "function": [{"does": "sense", "what": "temperature"}]}))
        self.catalog({"id": "y-probe", "name": "SEN0193", "function": [{"does": "sense", "what": "soil-moisture"}]})
        self.assertIn("y-probe", [c["id"] for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"]],
                      "ten owned thermometers and probes come first; the unowned record that fits still shows")

    def test_text_mode_shows_what_each_candidate_does(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "soil-moisture"}]}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        lines = out.getvalue().splitlines()
        self.assertIn("soil-moisture", next(line for line in lines if "x-soil (catalog)" in line))
        self.assertIn("gas [other words]", next(line for line in lines if "x-other (catalog)" in line))

    def test_a_board_owes_nothing_and_a_sound_one_is_not_broken(self):
        board = [c for c in self.needs["board"]["candidates"] if c["id"] == "firebeetle2-esp32s3"][0]
        self.assertEqual((board["owes"], board["broken"]), ([], False))

    def test_a_broken_board_is_marked_broken(self):
        (self.project / "boards").mkdir(parents=True)
        (self.project / "boards" / "half-board.json").write_text(json.dumps({"schema": 1, "id": "half-board", "name": "Half a board"}))
        found = [c["broken"] for c in self.alone({"id": "mcu", "does": "compute", "what": "microcontroller"})["candidates"]
                 if c["id"] == "half-board"]
        self.assertEqual(found, [True])

    def test_a_project_s_own_reservation_is_free_to_it(self):
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        (self.home / "drawer" / "probe.json").write_text(json.dumps({"schema": 1, "label": "soil probe", "count": 8, "is": {"part": "x-soil"},
                                                                    "used_in": {"plant-alarm": 1, "smartbin-local": 2}}))
        soil = [c for c in self.alone({"id": "soil", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "x-soil"][0]
        self.assertEqual((soil["owned"], soil["free"]), (8, 6), "what plant-alarm holds is free to it; what the bin holds is not")

    def test_a_project_s_own_reservation_is_free_to_it_on_an_entry_with_no_record_too(self):
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        (self.home / "drawer" / "buzzers.json").write_text(json.dumps({"schema": 1, "label": "piezo buzzers", "count": 3,
                                                                      "function": [{"does": "sound", "what": "alarm"}],
                                                                      "used_in": {"plant-alarm": 1, "smartbin-local": 1}}))
        buzzers = [c for c in self.alone({"id": "alarm", "does": "sound", "what": "alarm"})["candidates"] if c["entry"] == "buzzers"][0]
        self.assertEqual((buzzers["owned"], buzzers["free"]), (3, 2), "one held by plant-alarm is free to it; one held by the bin is not")

    def test_a_project_is_found_on_the_list_by_its_folder_however_the_path_is_spelled(self):
        """Another project is listed first; the list names the folder through a link, or the question does."""
        link = Path(tempfile.mkdtemp()) / "plant-alarm-link"
        link.symlink_to(self.project)
        (self.home / "drawer" / "probe.json").write_text(json.dumps({"schema": 1, "label": "soil probe", "count": 8, "is": {"part": "x-soil"},
                                                                    "used_in": {"plant-alarm": 1, "smartbin-local": 2}}))
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "soil-moisture"}]}))
        for listed, asked in ((link, self.project), (self.project, link)):
            with self.subTest(listed=listed.name, asked=asked.name):
                (self.home / "projects.json").write_text(json.dumps({"smartbin-local": tempfile.mkdtemp(), "plant-alarm": str(listed)}))
                said, _ = run(["--match", str(asked)])
                soil = [c for c in said["data"]["needs"][0]["candidates"] if c["id"] == "x-soil"][0]
                self.assertEqual((soil["owned"], soil["free"]), (8, 6))

    def test_a_candidate_is_said_whole_and_only_for_the_need_s_verb(self):
        self.catalog({"id": "y-combo", "name": "A combo board", "function": [{"does": "sense", "what": "temperature"},
                                                                            {"does": "indicate", "what": "light"}]})
        (self.home / "drawer" / "ntc.json").write_text(json.dumps({"schema": 1, "label": "an NTC thermistor", "count": 3,
                                                                    "function": [{"does": "sense", "what": "temperature"},
                                                                                 {"does": "sound", "what": "beeper"}]}))
        found = {c["id"] or c["entry"]: c for c in self.alone({"id": "heat", "does": "sense", "what": "temperature"})["candidates"]}
        self.assertEqual(found["ntc"], {"id": None, "kind": None, "entry": "ntc", "owes": [], "broken": False, "proof": [], "in": "drawer",
                                        "label": "an NTC thermistor", "what": ["temperature"], "what_matches": True,
                                        "owned": 3, "free": 3, "unsure": False})
        combo = found["y-combo"]
        self.assertEqual((combo["kind"], combo["entry"], combo["in"], combo["label"], combo["what"], combo["proof"], combo["what_matches"]),
                         ("part", None, "catalog", "A combo board", ["temperature"], [], True))

    def test_a_project_s_own_record_shadows_the_same_id_elsewhere(self):
        (self.project / "parts").mkdir(parents=True)
        (self.project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Our probe", "kind": "sensor",
                                                                         "function": [{"does": "sense", "what": "soil-moisture"}]}))
        found = [c["in"] for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "x-soil"]
        self.assertEqual(found, ["project"])

    def test_a_project_on_the_person_s_list_still_offers_its_records_as_the_project(self):
        (self.project / "parts").mkdir(parents=True)
        (self.project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Our probe", "kind": "sensor",
                                                                         "function": [{"does": "sense", "what": "soil-moisture"}]}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project)}))
        found = [c["in"] for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "x-soil"]
        self.assertEqual(found, ["project"])

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

    def test_a_count_nobody_gave_is_owned_count_unknown(self):
        self.catalog({"id": "y-probe", "name": "Probe Y", "function": [{"does": "sense", "what": "soil-moisture"}]})
        (self.home / "drawer" / "y.json").write_text(json.dumps({"schema": 1, "label": "some probes", "is": {"part": "y-probe"}}))
        found = [c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "y-probe"][0]
        self.assertEqual((found["owned"], found["free"]), ("unknown", "unknown"))

    def test_a_count_nobody_gave_outweighs_the_counted_entries_beside_it(self):
        self.catalog({"id": "y-probe", "name": "Probe Y", "function": [{"does": "sense", "what": "soil-moisture"}]})
        (self.home / "drawer" / "a.json").write_text(json.dumps({"schema": 1, "label": "probes, counted", "count": 3, "is": {"part": "y-probe"}}))
        (self.home / "drawer" / "b.json").write_text(json.dumps({"schema": 1, "label": "probes, not counted", "is": {"part": "y-probe"}}))
        found = [c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "y-probe"][0]
        self.assertEqual((found["owned"], found["free"]), ("unknown", "unknown"), "three and some more are not three")

    def test_many_still_wins_over_a_count_nobody_gave(self):
        self.catalog({"id": "y-probe", "name": "Probe Y", "function": [{"does": "sense", "what": "soil-moisture"}]})
        (self.home / "drawer" / "a.json").write_text(json.dumps({"schema": 1, "label": "probes, not counted", "is": {"part": "y-probe"}}))
        (self.home / "drawer" / "b.json").write_text(json.dumps({"schema": 1, "label": "a bag of probes", "count": "many", "is": {"part": "y-probe"}}))
        found = [c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "y-probe"][0]
        self.assertEqual((found["owned"], found["free"]), ("many", "many"))

    def test_an_entry_with_no_record_and_no_count_is_still_offered_and_keeps_its_doubt(self):
        (self.home / "drawer" / "buzzers.json").write_text(json.dumps({"schema": 1, "label": "some buzzers", "unsure": True,
                                                                      "function": [{"does": "sound", "what": "alarm"}]}))
        buzzers = [c for c in self.alone({"id": "alarm", "does": "sound", "what": "alarm"})["candidates"] if c["entry"] == "buzzers"][0]
        self.assertEqual((buzzers["owned"], buzzers["free"], buzzers["unsure"]), ("unknown", "unknown", True))

    def test_a_verb_nothing_has_is_an_empty_answer(self):
        keep = self.alone({"id": "keep", "does": "store", "what": "logs"})
        self.assertEqual((self.code, keep["candidates"]), (0, []))

    def test_an_owned_part_that_says_nothing_of_what_it_does_is_no_candidate(self):
        self.assertNotIn("x-silent", [c["id"] for c in self.needs["soil"]["candidates"]])

    def test_a_dead_entry_s_function_does_not_make_its_record_a_candidate(self):
        (self.home / "drawer" / "dead-silent.json").write_text(json.dumps({"schema": 1, "label": "burnt", "count": 1, "skip": "dead",
                                                                           "is": {"part": "x-silent"}, "function": [{"does": "sense", "what": "gas"}]}))
        self.assertNotIn("x-silent", [c["id"] for c in self.smell()])

    def test_an_entry_pointing_at_a_record_that_does_not_parse_is_offered_from_the_drawer(self):
        (self.home / "catalog" / "x-broken.json").write_text("{")
        (self.home / "drawer" / "pointing.json").write_text(json.dumps({"schema": 1, "label": "a sensor I own", "count": 1,
                                                                        "is": {"part": "x-broken"}, "function": [{"does": "sense", "what": "gas"}]}))
        offered = [c for c in self.smell() if c["entry"] == "pointing"]
        self.assertEqual([c["in"] for c in offered], ["drawer"])

    def test_an_entry_pointing_at_a_record_that_parses_is_offered_through_the_record_only(self):
        (self.home / "drawer" / "pointing.json").write_text(json.dumps({"schema": 1, "label": "a probe I own", "count": 1,
                                                                        "is": {"part": "x-soil"}, "function": [{"does": "sense", "what": "gas"}]}))
        self.assertEqual([c for c in self.smell() if c["entry"] == "pointing"], [])

    def test_a_record_whose_function_is_malformed_is_matched_by_its_kind(self):
        for key, function in (("x-nowhat", [{"does": "sense"}]), ("x-string", "sense")):
            (self.home / "catalog" / (key + ".json")).write_text(json.dumps({"schema": 1, "id": key, "name": key, "kind": "sensor", "function": function}))
        said, code = run(["--match", str(self.project)])
        self.assertEqual(code, 0)
        soil = [c["id"] for c in next(n for n in said["data"]["needs"] if n["need"] == "soil")["candidates"]]
        self.assertNotIn("x-nowhat", soil, "a sensor's kind says nothing, and a function with no `what` is not one")
        said, code = run(["--audit"])
        self.assertEqual(sorted(b["id"] for b in said["data"]["broken"] if b["id"] in ("x-nowhat", "x-string")), ["x-nowhat", "x-string"])

    def test_a_malformed_record_is_named_broken_never_a_traceback(self):
        soil = [{"does": "sense", "what": "soil-moisture"}]
        self.catalog({"id": "m-kind", "name": "m", "kind": ["sensor", "rtc"]},
                     {"id": "m-needs", "name": "m", "needs": ["SIG"], "function": soil},
                     {"id": "m-facts", "name": "m", "facts": [1, 2], "function": soil})
        found = {c["id"]: c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"]}
        self.assertEqual((found["m-needs"]["broken"], found["m-facts"]["broken"]), (True, True))
        said, code = run(["--audit"])
        self.assertEqual(code, 1)
        self.assertLessEqual({"m-needs", "m-facts"}, {b["id"] for b in said["data"]["broken"]})
        self.assertIn("m-kind", said["data"]["no_function"], "a kind that is a list says nothing, and crashes nothing")

    def test_text_mode_prints_a_need_that_cannot_be_matched(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "x", "what": "y"}]}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        self.assertIn("  x: a need with no `does` cannot be matched", out.getvalue())

    def test_a_candidate_nobody_owns_has_no_stray_semicolon(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        self.assertNotIn(" ; ", out.getvalue())
        self.assertNotRegex(out.getvalue(), r"; owes")

    def test_a_need_with_no_verb_is_named(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "x", "what": "y"}]}))
        said, code = run(["--match", str(self.project)])
        self.assertEqual((said["status"], code), ("problems", 1))


class ThePicksTest(unittest.TestCase):
    """P97, §8 C: a pick per need; what you own is reserved, never past what another project holds; a reason is kept."""

    def setUp(self):
        self.home, self.project = a_store_with_a_drawer(), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "sound", "what": "alarm"},
            {"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "input", "does": "input", "what": "button"}])])

    def entry(self, key):
        return json.loads((self.home / "drawer" / (key + ".json")).read_text())

    def picks(self):
        return {need["id"]: need.get("pick") for need in json.loads((self.project / ".spark" / "needs.json").read_text())["needs"]}

    def history(self):
        path = self.home / "history.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []

    def text(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            parts.main(argv)
        return out.getvalue()

    def test_the_bin_s_only_board_is_refused_naming_who_holds_it(self):
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("1 owned, held by smartbin-local", said["problems"][0]["sentence"])
        self.assertIn("--drawer-set board", said["problems"][0]["fix"])
        self.assertEqual((self.picks()["board"], self.entry("board")["used_in"]), (None, {"smartbin-local": 1}))

    def test_a_pick_reserves_one_piece_and_the_history_says_it_was_reused(self):
        _, code = run(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"])
        self.assertEqual(code, 0)
        self.assertEqual((self.picks()["soil"], self.picks()["alarm"]), ([{"part": "x-soil"}], [{"entry": "speaker"}]))
        self.assertEqual((self.entry("probe")["used_in"], self.entry("speaker")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))
        self.assertEqual(self.history(), [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"},
                                          {"event": "reused", "project": "plant-alarm", "need": "alarm", "entry": "speaker"}])

    def test_freed_by_the_person_the_board_is_reserved_for_this_project(self):
        run(["--drawer-set", a_file([{"entry": "board", "used_in": {}}])])
        _, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((code, self.entry("board")["used_in"]), (0, {"plant-alarm": 1}))

    def test_a_refused_pick_writes_nothing_at_all(self):
        _, code = run(["--pick", str(self.project), "soil=x-soil", "board=firebeetle2-esp32s3"])
        self.assertEqual(code, 1)
        self.assertEqual((self.picks()["soil"], self.entry("probe").get("used_in"), self.history()), (None, None, []))

    def test_a_re_pick_frees_what_it_no_longer_picks(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        _, code = run(["--pick", str(self.project), "soil=x-other"])
        self.assertEqual((code, self.picks()["soil"], self.entry("probe")["used_in"]), (0, [{"part": "x-other"}], {}))

    def test_a_pick_nobody_owns_is_to_get_and_reserves_nothing(self):
        self.assertIn("x-other: to get — known, not owned", self.text(["--pick", str(self.project), "soil=x-other"]))

    def test_an_unsure_pick_says_check_the_drawer_first(self):
        self.assertIn("mp3: maybe owned — check the drawer first", self.text(["--pick", str(self.project), "alarm=mp3"]))

    def test_a_count_nobody_gave_is_reserved_and_said(self):
        (self.home / "drawer" / "probes.json").write_text(json.dumps({"schema": 1, "label": "some probes"}))
        self.assertIn("probes: count unknown — check the drawer", self.text(["--pick", str(self.project), "soil=probes"]))
        self.assertEqual(self.entry("probes")["used_in"], {"plant-alarm": 1})

    def test_many_is_reserved_one_piece_at_a_time(self):
        run(["--pick", str(self.project), "input=tactile-button"])
        self.assertEqual(self.entry("buttons")["used_in"], {"plant-alarm": 1})

    def test_a_part_passed_over_keeps_its_reason_once(self):
        reasons = a_file([{"need": "soil", "id": "x-other", "why": "a gas sensor does not sense soil", "by": "person"}])
        for _ in range(2):
            run(["--pick", str(self.project), "soil=x-soil", "--passed-over", reasons])
        self.assertEqual([event for event in self.history() if event["event"] == "passed_over"],
                         [{"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x-other",
                           "why": "a gas sensor does not sense soil", "by": "person"}])

    def test_a_retried_pick_changes_nothing(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        said, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, said["data"]["reserved"], self.entry("probe")["used_in"]), (0, [], {"plant-alarm": 1}))

    def test_a_need_or_an_id_spark_does_not_have_is_named(self):
        said, code = run(["--pick", str(self.project), "smell=x-soil", "soil=no-such-thing"])
        self.assertEqual((code, [p["subject"] for p in said["problems"]]), (1, ["smell", "soil"]))

    def test_a_pick_names_ids_only(self):
        said, code = run(["--pick", str(self.project), "soil"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))

    def test_a_hand_edited_pick_of_the_wrong_shape_is_named(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps(
            {"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "x", "pick": [{"part": 7}]}]}))
        said, code = run(["--needs", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("needs.json", said["unchecked"][0]["sentence"])

    # The rest pin one behaviour each: what a pick says, what it reserves and frees, what it refuses, and what it leaves alone.

    def test_a_hand_edited_pick_is_read_only_in_the_shape_a_pick_has(self):
        def with_pick(pick):
            (self.project / ".spark" / "needs.json").write_text(json.dumps(
                {"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "x", "pick": pick}]}))
        for pick in ([{"part": "a-part"}], [{"board": "a-board"}, {"entry": "an-entry"}, {"part": "b"}]):
            with self.subTest(pick=pick):
                with_pick(pick)
                self.assertEqual(run(["--needs", str(self.project)])[1], 0)
        for pick in ("x-soil", {"part": "x-soil"}, [{"part": "x-soil", "board": "y"}], [{"thing": "x-soil"}], [{"part": "X Soil"}],
                     ["x-soil"], [{}], [{"part": None}]):
            with self.subTest(pick=pick):
                with_pick(pick)
                said, code = run(["--needs", str(self.project)])
                self.assertEqual(code, 2)
                self.assertIn("`pick` is a list of", said["unchecked"][0]["sentence"])

    def test_a_pick_says_what_it_changed_what_it_picked_and_what_it_noted_in_that_order(self):
        self.assertEqual(self.text(["--pick", str(self.project), "soil=x-soil", "alarm=mp3"]), "\n".join([
            '  set mp3: used_in null → {"plant-alarm": 1}',
            '  set probe: used_in null → {"plant-alarm": 1}',
            "  soil: x-soil",
            "  alarm: mp3",
            "  mp3: maybe owned — check the drawer first", ""]))

    def test_a_refused_pick_says_its_notes_between_what_it_would_have_changed_and_what_it_refused(self):
        self.assertEqual(self.text(["--pick", str(self.project), "alarm=mp3", "board=firebeetle2-esp32s3"]), "\n".join([
            '  refused, not written: set mp3: used_in null → {"plant-alarm": 1}',
            "  mp3: maybe owned — check the drawer first",
            "  refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here", ""]))

    def test_a_history_that_cannot_be_read_stops_a_pick_before_anything_is_written(self):
        (self.home / "history.jsonl").write_text("this is not an event\n")
        for extra in ([], ["--dry-run"]):
            with self.subTest(extra=extra):
                said, code = run(["--pick", str(self.project), "soil=x-soil"] + extra)
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertIn("history.jsonl", said["unchecked"][0]["sentence"])
                self.assertEqual((self.picks()["soil"], self.entry("probe").get("used_in")), (None, None))
                self.assertFalse((self.home / "projects.json").exists())
        self.assertEqual((self.home / "history.jsonl").read_text(), "this is not an event\n")

    def test_asking_for_a_plan_with_no_reasons_is_asking_for_no_reasons(self):
        _, _, events, _, problems = needs.plan_pick(self.project, [("soil", "x-soil")])
        self.assertEqual((problems, events), ([], [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"}]))

    def test_a_pick_answers_with_the_project_what_it_picked_what_it_reserved_and_that_it_was_written(self):
        said, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, said["data"]), (0, {"project": "plant-alarm", "picks": [{"need": "soil", "pick": [{"part": "x-soil"}]}],
                                                     "reserved": [{"entry": "probe", "used_in": {"plant-alarm": 1}}], "written": True}))

    def test_a_dry_run_says_what_it_would_do_and_writes_nothing(self):
        said, code = run(["--pick", str(self.project), "soil=x-soil", "--dry-run"])
        self.assertEqual((code, said["data"]["written"], said["data"]["reserved"]),
                         (0, False, [{"entry": "probe", "used_in": {"plant-alarm": 1}}]))
        self.assertEqual((self.picks()["soil"], self.entry("probe").get("used_in"), self.history()), (None, None, []))
        self.assertFalse((self.home / "projects.json").exists())
        self.assertEqual(self.text(["--pick", str(self.project), "soil=x-soil", "--dry-run"]),
                         '  would set probe: used_in null → {"plant-alarm": 1}\n  soil: x-soil\n')

    def test_a_pick_puts_the_project_on_the_list_so_what_it_reserved_stays_free_to_it(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual(json.loads((self.home / "projects.json").read_text()), {"plant-alarm": str(self.project.resolve())})
        said, _ = run(["--match", str(self.project)])
        soil = [c for c in said["data"]["needs"][0]["candidates"] if c["id"] == "x-soil"][0]
        self.assertEqual((said["data"]["needs"][0]["need"], soil["owned"], soil["free"]), ("soil", 8, 8))

    def test_a_need_the_pick_does_not_name_keeps_its_pick_and_its_reservation(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        run(["--pick", str(self.project), "alarm=speaker"])
        self.assertEqual((self.picks()["soil"], self.entry("probe")["used_in"], self.entry("speaker")["used_in"]),
                         ([{"part": "x-soil"}], {"plant-alarm": 1}, {"plant-alarm": 1}))

    def test_a_reservation_leaves_what_other_projects_hold_as_it_was(self):
        (self.home / "drawer" / "probe.json").write_text(json.dumps({"schema": 1, "label": "soil probe", "count": 8, "is": {"part": "x-soil"},
                                                                    "used_in": {"smartbin-local": 2}}))
        run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual(self.entry("probe")["used_in"], {"smartbin-local": 2, "plant-alarm": 1})

    def test_a_need_takes_every_pick_it_is_given_once_each_and_reserves_one_piece_for_each(self):
        run(["--pick", str(self.project), "alarm=speaker", "alarm=mp3", "alarm=speaker"])
        self.assertEqual(self.picks()["alarm"], [{"entry": "speaker"}, {"entry": "mp3"}])
        self.assertEqual((self.entry("speaker")["used_in"], self.entry("mp3")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))
        self.assertEqual([event["entry"] for event in self.history()], ["speaker", "mp3"])

    def test_the_refusal_names_only_the_others_and_counts_what_this_project_picked(self):
        (self.home / "drawer" / "board.json").write_text(json.dumps({"schema": 1, "label": "FireBeetle", "count": 2, "is": {"board": "firebeetle2-esp32s3"},
                                                                    "used_in": {"smartbin-local": 1, "plant-alarm": 1}}))
        run(["--needs-set", str(self.project), a_file([{"id": "spare", "does": "compute", "what": "microcontroller"}])])
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3", "spare=firebeetle2-esp32s3"])
        self.assertEqual((code, said["problems"][0]["sentence"], said["problems"][0]["fix"]), (
            1, "2 owned, held by smartbin-local — 2 picked here",
            "free it — --drawer-set board with `used_in` leaving out smartbin-local, after a dry run — or pick another"))

    def test_more_picked_than_is_owned_is_refused_though_nobody_else_holds_any(self):
        run(["--needs-set", str(self.project), a_file([{"id": "chime", "does": "sound", "what": "alarm"}])])
        said, code = run(["--pick", str(self.project), "alarm=mp3", "chime=mp3"])
        self.assertEqual((code, said["problems"][0]["sentence"]), (1, "1 owned — 2 picked here"))

    def a_stock_pointed_at_twice(self, count, used_in=None):
        """One record and the drawer entry of it, `count` owned; the project has two needs of its own, `soil` and `deep`."""
        (self.home / "catalog" / "x-solo.json").write_text(json.dumps({"schema": 1, "id": "x-solo", "name": "A lone sensor", "kind": "sensor",
                                                                      "function": [{"does": "sense", "what": "soil-moisture"}]}))
        (self.home / "drawer" / "solo.json").write_text(json.dumps(dict({"schema": 1, "label": "my sensors", "count": count, "is": {"part": "x-solo"}},
                                                                        **({"used_in": used_in} if used_in else {}))))
        run(["--needs-set", str(self.project), a_file([{"id": "deep", "does": "sense", "what": "soil-moisture"}])])

    def test_one_stock_picked_as_its_record_and_as_its_drawer_entry_is_counted_once_against_what_is_owned(self):
        self.a_stock_pointed_at_twice(1)
        said, code = run(["--pick", str(self.project), "soil=x-solo", "deep=solo"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual(said["problems"][0]["sentence"], "1 owned — 2 picked here")
        self.assertEqual((self.picks()["soil"], self.picks()["deep"], self.entry("solo").get("used_in"), self.history()), (None, None, None, []))

    def test_one_stock_picked_both_ways_is_reserved_twice_when_two_are_owned(self):
        self.a_stock_pointed_at_twice(2)
        _, code = run(["--pick", str(self.project), "soil=x-solo", "deep=solo"])
        self.assertEqual((code, self.picks()["soil"], self.picks()["deep"], self.entry("solo")["used_in"]),
                         (0, [{"part": "x-solo"}], [{"entry": "solo"}], {"plant-alarm": 2}))

    def test_one_stock_picked_both_ways_never_goes_past_what_another_project_holds(self):
        self.a_stock_pointed_at_twice(2, {"smartbin-local": 1})
        said, code = run(["--pick", str(self.project), "soil=x-solo", "deep=solo"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual(said["problems"][0]["sentence"], "2 owned, held by smartbin-local — 2 picked here")
        self.assertEqual((self.picks()["soil"], self.entry("solo")["used_in"], self.history()), (None, {"smartbin-local": 1}, []))

    def test_a_record_owned_over_two_entries_serves_a_pick_of_the_first_by_key_and_a_pick_of_the_record(self):
        (self.home / "drawer" / "board.json").unlink()
        for key in ("a-board", "b-board"):
            (self.home / "drawer" / (key + ".json")).write_text(json.dumps({"schema": 1, "label": key, "count": 1, "is": {"board": "firebeetle2-esp32s3"}}))
        run(["--needs-set", str(self.project), a_file([{"id": "spare", "does": "compute", "what": "microcontroller"}])])
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3", "spare=a-board"])
        self.assertEqual((code, said["problems"]), (0, []))
        self.assertEqual((self.entry("a-board")["used_in"], self.entry("b-board")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))

    def test_a_retried_pick_of_the_only_one_is_not_held_against_its_own_project(self):
        run(["--drawer-set", a_file([{"entry": "board", "used_in": {}}])])
        run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((code, said["data"]["reserved"], self.entry("board")["used_in"]), (0, [], {"plant-alarm": 1}))

    def test_two_picks_of_one_part_take_what_is_free_of_one_entry_and_the_rest_from_the_next(self):
        (self.home / "drawer" / "probe.json").write_text(json.dumps({"schema": 1, "label": "soil probe", "count": 8, "is": {"part": "x-soil"},
                                                                    "used_in": {"smartbin-local": 7}}))
        (self.home / "drawer" / "spare-probe.json").write_text(json.dumps({"schema": 1, "label": "spare soil probes", "count": 4,
                                                                          "is": {"part": "x-soil"}}))
        run(["--needs-set", str(self.project), a_file([{"id": "deep", "does": "sense", "what": "soil-moisture"}])])
        _, code = run(["--pick", str(self.project), "soil=x-soil", "deep=x-soil"])
        self.assertEqual((code, self.entry("probe")["used_in"], self.entry("spare-probe")["used_in"]),
                         (0, {"smartbin-local": 7, "plant-alarm": 1}, {"plant-alarm": 1}))

    def test_many_is_never_held_up_by_what_another_project_holds(self):
        (self.home / "drawer" / "buttons.json").write_text(json.dumps({"schema": 1, "label": "a bag of buttons", "count": "many",
                                                                      "is": {"part": "tactile-button"}, "used_in": {"smartbin-local": 2}}))
        _, code = run(["--pick", str(self.project), "input=tactile-button"])
        self.assertEqual((code, self.entry("buttons")["used_in"]), (0, {"smartbin-local": 2, "plant-alarm": 1}))

    def test_a_part_another_project_holds_more_of_than_is_owned_is_refused_not_a_crash(self):
        (self.home / "drawer" / "board.json").write_text(json.dumps({"schema": 1, "label": "FireBeetle", "count": 1, "is": {"board": "firebeetle2-esp32s3"},
                                                                    "used_in": {"smartbin-local": 3}}))
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((said["status"], code, self.entry("board")["used_in"]), ("problems", 1, {"smartbin-local": 3}))

    def test_an_id_that_is_a_record_is_the_record_even_when_a_drawer_entry_has_the_same_key(self):
        (self.home / "drawer" / "x-soil.json").write_text(json.dumps({"schema": 1, "label": "loose probes", "count": 3}))
        run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((self.picks()["soil"], self.entry("probe")["used_in"], self.entry("x-soil").get("used_in")),
                         ([{"part": "x-soil"}], {"plant-alarm": 1}, None))

    def test_an_id_that_is_a_part_and_a_board_is_the_part(self):
        (self.project / "parts").mkdir()
        (self.project / "parts" / "firebeetle2-esp32s3.json").write_text(json.dumps(
            {"schema": 1, "id": "firebeetle2-esp32s3", "name": "Our own sheet for the board", "kind": "sensor"}))
        _, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((code, self.picks()["board"], self.entry("board")["used_in"]),
                         (0, [{"part": "firebeetle2-esp32s3"}], {"smartbin-local": 1}))

    def test_a_dead_entry_is_to_get_and_reserves_nothing(self):
        self.assertIn("dead: to get — known, not owned", self.text(["--pick", str(self.project), "alarm=dead"]))
        self.assertIsNone(self.entry("dead").get("used_in"))

    def test_a_drawer_entry_whose_key_is_not_plain_cannot_be_picked_and_nothing_is_written(self):
        (self.home / "drawer" / "Piezo_Buzzer.json").write_text(json.dumps({"schema": 1, "label": "a buzzer", "count": 1,
                                                                           "function": [{"does": "sound", "what": "alarm"}]}))
        for extra in ([], ["--dry-run"]):
            with self.subTest(extra=extra):
                said, code = run(["--pick", str(self.project), "soil=x-soil", "alarm=Piezo_Buzzer"] + extra)
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertIn("'Piezo_Buzzer' is not a plain key", said["unchecked"][0]["sentence"])
                self.assertEqual((self.picks()["soil"], self.picks()["alarm"], self.entry("probe").get("used_in"),
                                  self.entry("Piezo_Buzzer").get("used_in"), self.history()), (None, None, None, None, []))
                self.assertFalse((self.home / "projects.json").exists())
                self.assertEqual(run(["--needs", str(self.project)])[1], 0)

    def test_a_record_whose_id_is_not_plain_cannot_be_picked_and_nothing_is_written(self):
        (self.project / "parts").mkdir()
        (self.project / "parts" / "Lone_Sensor.json").write_text(json.dumps({"schema": 1, "id": "Lone_Sensor", "name": "A lone sensor", "kind": "sensor"}))
        for extra in ([], ["--dry-run"]):
            with self.subTest(extra=extra):
                said, code = run(["--pick", str(self.project), "soil=Lone_Sensor", "alarm=speaker"] + extra)
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertIn("'Lone_Sensor' is not a plain key", said["unchecked"][0]["sentence"])
                self.assertEqual((self.picks()["soil"], self.picks()["alarm"], self.entry("speaker").get("used_in"), self.history()),
                                 (None, None, None, []))
                self.assertFalse((self.home / "projects.json").exists())
                self.assertEqual(run(["--needs", str(self.project)])[1], 0)

    def test_an_id_nothing_has_is_named_even_when_it_is_not_plain(self):
        said, code = run(["--pick", str(self.project), "soil=No_Such_Part"])
        self.assertEqual((said["status"], code, said["problems"][0]["sentence"]),
                         ("problems", 1, "no record or drawer entry called No_Such_Part — --match lists the candidates"))

    def test_a_store_that_refuses_the_history_leaves_the_project_file_untouched_and_a_retry_finishes_the_pick(self):
        needs_file = self.project / ".spark" / "needs.json"
        before, real = needs_file.read_text(), store._make_ready

        def refuse_the_history(name, target):
            if name == "history":
                raise store.StoreProblem("%s would be inside the git work tree — what you own stays out of every repository" % target)
            return real(name, target)
        with mock.patch.object(store, "_make_ready", side_effect=refuse_the_history):
            said, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("inside the git work tree", said["unchecked"][0]["sentence"])
        self.assertEqual((needs_file.read_text(), self.history()), (before, []))
        _, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, self.picks()["soil"], self.entry("probe")["used_in"], self.history()),
                         (0, [{"part": "x-soil"}], {"plant-alarm": 1}, [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"}]))

    def test_a_re_pick_to_another_owned_part_moves_the_reservation_in_one_write(self):
        run(["--pick", str(self.project), "alarm=speaker"])
        _, code = run(["--pick", str(self.project), "alarm=mp3"])
        self.assertEqual((code, self.picks()["alarm"], self.entry("speaker")["used_in"], self.entry("mp3")["used_in"]),
                         (0, [{"entry": "mp3"}], {}, {"plant-alarm": 1}))

    def test_a_pick_nobody_owns_is_still_a_pick_and_still_reused_from_the_store(self):
        run(["--pick", str(self.project), "soil=x-other"])
        self.assertEqual((self.picks()["soil"], self.history()),
                         ([{"part": "x-other"}], [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-other"}]))

    def test_a_reason_is_the_person_s_unless_it_says_the_agent_and_may_pass_over_an_entry(self):
        reasons = a_file([{"need": "soil", "id": "x-other", "why": "a gas sensor does not sense soil"},
                          {"need": "alarm", "id": "mp3", "why": "not sure it is here\nand old", "by": "agent"}])
        run(["--pick", str(self.project), "soil=x-soil", "--passed-over", reasons])
        self.assertEqual([event for event in self.history() if event["event"] == "passed_over"], [
            {"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x-other",
             "why": "a gas sensor does not sense soil", "by": "person"},
            {"event": "passed_over", "project": "plant-alarm", "need": "alarm", "entry": "mp3",
             "why": "not sure it is here and old", "by": "agent"}])

    def test_a_part_passed_over_that_is_not_one_is_named_and_nothing_is_written(self):
        good = {"need": "soil", "id": "x-other", "why": "a gas sensor does not sense soil"}
        for name, reasons in (("a need the project has not", [dict(good, need="smell")]), ("an id spark has not", [dict(good, id="nothing")]),
                              ("no reason", [{key: value for key, value in good.items() if key != "why"}]),
                              ("an empty reason", [dict(good, why="  ")]), ("a reason that is not words", [dict(good, why=7)]),
                              ("nobody", [dict(good, by="robot")]), ("not an object", ["x-other"]), ("not a list", good), ("null", None)):
            with self.subTest(name=name):
                said, code = run(["--pick", str(self.project), "soil=x-soil", "--passed-over", a_file(reasons)])
                self.assertEqual((code, said["problems"][0]["subject"]), (1, "passed over 1"))
                self.assertEqual((self.picks()["soil"], self.entry("probe").get("used_in"), self.history()), (None, None, []))

    def test_a_reasons_file_that_cannot_be_read_stops_the_pick(self):
        said, code = run(["--pick", str(self.project), "soil=x-soil", "--passed-over", str(self.project / "no-such-file.json")])
        self.assertEqual((said["status"], code, self.picks()["soil"], self.history()), ("could-not-run", 2, None, []))

    def test_one_word_that_is_not_need_equals_id_refuses_the_whole_pick(self):
        for argv in (["soil=x-soil", "alarm"], []):
            with self.subTest(argv=argv):
                said, code = run(["--pick", str(self.project)] + argv)
                self.assertEqual((said["status"], code, self.picks()["soil"]), ("could-not-run", 2, None))

    def test_a_pick_waits_while_another_holds_the_store(self):
        with store.locked():
            picker = subprocess.Popen([sys.executable, str(ROOT / "scripts" / "parts.py"), "--pick", str(self.project), "soil=x-soil"],
                                      env=dict(os.environ), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
            self.assertIsNone(self.picks()["soil"], "it wrote while another held the store")
        self.assertEqual(picker.wait(timeout=60), 0)
        self.assertEqual(self.picks()["soil"], [{"part": "x-soil"}])


def a_project_with_picks(picks):
    """A scratch store holding a catalog record that owes nothing (the library's LED, as x-led) and one that owes facts,
    and a project whose needs pick `picks` — [(need id, [pick])]."""
    home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
    (home / "catalog").mkdir()
    led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
    (home / "catalog" / "x-led.json").write_text(json.dumps(dict(led, id="x-led")))
    (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor", "needs": []}))
    (project / ".spark").mkdir(parents=True)
    (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
        {"id": need_id, "does": "sense", "what": "x", "pick": pick} for need_id, pick in picks]}))
    return home, project


class TheRequirementsFileTest(unittest.TestCase):
    """P97, §8 L: the picks become a requirements file — the board and each part pick with a record that owes nothing."""

    BOARD = ("board", [{"board": "firebeetle2-esp32s3"}])
    #: The build page's example as a person extends it by hand: a part's own rail, the inlet no need picks, two buttons given
    #: names of their own, a signal no part claims.
    BY_HAND = {"board": "firebeetle2-esp32s3",
               "parts": [{"part": "l9110s-module", "rails": {"VCC": "traction"}}, "jst-ph-2-power-inlet",
                         {"part": "tactile-button", "name": "BtnOpen"}, {"part": "tactile-button", "name": "BtnMode"}],
               "signals": [{"name": "LED_STATUS", "needs": []}]}
    #: The picks that explain all of BY_HAND but the inlet.
    DRIVER_AND_TWO_BUTTONS = [BOARD, ("drive", [{"part": "l9110s-module"}]), ("open-lid", [{"part": "tactile-button"}]),
                              ("mode", [{"part": "tactile-button"}])]

    def project(self, picks):
        home, project = a_project_with_picks(picks)
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        return home, project

    def picking(self, project, picks):
        """The person changes their mind: from now on the project's needs pick `picks`."""
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": need_id, "does": "sense", "what": "x", "pick": pick} for need_id, pick in picks]}))

    def written(self, project):
        return json.loads((project / "requirements.json").read_text())

    def text(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(argv)
        return out.getvalue()

    def test_the_picks_become_the_board_and_the_parts_with_records(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}]), ("alarm", [{"entry": "speaker"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)), (0, {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]}))
        self.assertEqual(said["data"]["unplaced"], ["speaker"])

    def test_a_pick_that_owes_facts_is_named_and_nothing_is_written(self):
        _, project = self.project([self.BOARD, ("soil", [{"part": "x-soil"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("owes footprint", said["problems"][0]["sentence"])
        self.assertFalse((project / "requirements.json").exists())

    def test_a_catalog_pick_that_owes_nothing_goes_onto_the_shelf(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        run(["--requirements", str(project)])
        shelved = json.loads((home / "shelf" / "x-led.json").read_text())
        self.assertEqual((shelved["id"], "based_on" in shelved, self.written(project)["parts"]), ("x-led", False, ["x-led"]))

    def test_one_board_is_picked(self):
        for picks in ([("light", [{"part": "led-red-5mm"}])], [self.BOARD, ("other", [{"board": "xiao-esp32-c6"}])]):
            with self.subTest(picks=picks):
                _, project = self.project(picks)
                said, code = run(["--requirements", str(project)])
                self.assertEqual((code, said["problems"][0]["subject"]), (1, "board"))

    def test_a_part_picked_for_two_needs_is_named_after_each(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        run(["--requirements", str(project)])
        self.assertEqual(self.written(project)["parts"], [{"part": "tactile-button", "name": "OpenLid"},
                                                          {"part": "tactile-button", "name": "Mode"}])

    def test_what_the_person_added_to_the_file_stays(self):
        _, project = self.project(self.DRIVER_AND_TWO_BUTTONS)
        (project / "requirements.json").write_text(json.dumps(self.BY_HAND))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)), (0, self.BY_HAND))
        self.assertEqual(said["data"]["kept"], [{"part": "jst-ph-2-power-inlet", "name": None}])

    def test_a_dry_run_writes_nothing(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        said, code = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse((project / "requirements.json").exists() or (home / "shelf").exists())

    def test_a_pick_from_spark_s_library_is_not_copied_onto_the_shelf(self):
        # the shelf is nearer than the library, so a copy there would hide every later improvement to the library's record
        home, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        run(["--requirements", str(project)])
        self.assertFalse((home / "shelf").exists())

    def test_a_part_already_on_the_shelf_is_not_replaced_by_the_catalog_s_copy(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        (home / "shelf").mkdir()
        (home / "shelf" / "x-led.json").write_text(json.dumps(dict(json.loads((home / "catalog" / "x-led.json").read_text()),
                                                                   name="the shelf's own name")))
        before = (home / "shelf" / "x-led.json").read_text()
        said, _ = run(["--requirements", str(project)])
        self.assertEqual(((home / "shelf" / "x-led.json").read_text(), said["data"]["shelved"], self.written(project)["parts"]),
                         (before, [], ["x-led"]))

    def test_a_pick_from_another_project_goes_onto_the_shelf_saying_which(self):
        home, project = self.project([self.BOARD, ("water", [{"part": "x-valve"}])])
        other = Path(tempfile.mkdtemp()) / "irrigation"
        (other / "parts").mkdir(parents=True)
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        (other / "parts" / "x-valve.json").write_text(json.dumps(dict(led, id="x-valve")))
        (home / "projects.json").write_text(json.dumps({"irrigation": str(other)}))
        said, code = run(["--requirements", str(project)])
        shelved = json.loads((home / "shelf" / "x-valve.json").read_text())
        self.assertEqual((code, said["data"]["shelved"], said["data"]["written"], self.written(project)["parts"]),
                         (0, ["x-valve"], True, ["x-valve"]))
        self.assertEqual((shelved["based_on"]["project"], len(shelved["based_on"]["digest"])), ("irrigation", 64))

    def test_a_pick_whose_record_is_gone_or_broken_is_named_and_nothing_is_written(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-gone"}]), ("alarm", [{"part": "x-broken"}])])
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        (home / "catalog" / "x-broken.json").write_text(json.dumps(dict(led, id="x-broken", needs="five pins")))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, sorted({p["subject"] for p in said["problems"]})), ("problems", 1, ["x-broken", "x-gone"]))
        self.assertIn("no record called x-gone any more", said["problems"][0]["sentence"])
        self.assertFalse((project / "requirements.json").exists() or (home / "shelf").exists())

    def test_a_catalog_part_picked_for_two_needs_goes_onto_the_shelf_once(self):
        _, project = self.project([self.BOARD, ("left", [{"part": "x-led"}]), ("right", [{"part": "x-led"}])])
        said, _ = run(["--requirements", str(project)])
        self.assertEqual((said["data"]["shelved"], self.written(project)["parts"]),
                         (["x-led"], [{"part": "x-led", "name": "Left"}, {"part": "x-led", "name": "Right"}]))

    def test_a_part_that_owes_facts_is_refused_once_however_many_needs_pick_it(self):
        _, project = self.project([self.BOARD, ("soil", [{"part": "x-soil"}]), ("moisture", [{"part": "x-soil"}])])
        said, _ = run(["--requirements", str(project)])
        self.assertEqual([p["subject"] for p in said["problems"]], ["x-soil"])

    def test_a_pick_with_no_record_is_said_once_however_many_needs_pick_it(self):
        _, project = self.project([self.BOARD, ("alarm", [{"entry": "speaker"}]), ("backup", [{"entry": "speaker"}])])
        said, _ = run(["--requirements", str(project)])
        self.assertEqual(said["data"]["unplaced"], ["speaker"])

    def test_a_requirements_file_that_cannot_be_read_is_named_and_nothing_is_written(self):
        for broken in (b"{not json", b"\xff\xfe{"):
            with self.subTest(broken=broken):
                home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
                (project / "requirements.json").write_bytes(broken)
                said, code = run(["--requirements", str(project)])
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertIn("requirements.json is not JSON", said["unchecked"][0]["sentence"])
                self.assertEqual(((project / "requirements.json").read_bytes(), (home / "shelf").exists()), (broken, False))

    def test_text_mode_says_a_refusal_and_nothing_of_a_write(self):
        _, project = self.project([self.BOARD, ("soil", [{"part": "x-soil"}]), ("alarm", [{"entry": "speaker"}])])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--requirements", str(project)])
        self.assertEqual(out.getvalue(), "  refused, so nothing was written: x-soil — owes footprint, pin_order, pin_order_proof, body_mm, "
                                         "simulation — fill it in its own home with --fact-set\n")

    def test_text_mode_says_what_it_wrote_what_went_onto_the_shelf_and_what_is_reserved(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}]),
                                   ("light", [{"part": "x-led"}]), ("alarm", [{"entry": "speaker"}])])
        for extra, verb in ((["--dry-run"], "would write"), ([], "wrote")):  # in this order: a real run puts x-led on the shelf
            with self.subTest(extra=extra):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    parts.main(["--requirements", str(project)] + extra)
                self.assertEqual(out.getvalue(), "  %s %s: board firebeetle2-esp32s3; parts tactile-button (OpenLid), tactile-button (Mode), x-led\n"
                                 "  onto the shelf, so every project builds with it: x-led\n"
                                 "  reserved, not placed — no record: speaker\n" % (verb, project / "requirements.json"))

    # --- a re-run keeps what the person did by hand (the PO, 2026-10-08) ---

    def test_the_dry_run_says_what_it_would_keep_and_the_board_it_would_change(self):
        _, project = self.project(self.DRIVER_AND_TWO_BUTTONS)
        (project / "requirements.json").write_text(json.dumps(dict(self.BY_HAND, board="xiao-esp32-c6")))
        before = (project / "requirements.json").read_text()
        self.assertEqual(self.text(["--requirements", str(project), "--dry-run"]),
                         "  would write %s: board firebeetle2-esp32s3; parts l9110s-module, jst-ph-2-power-inlet, "
                         "tactile-button (BtnOpen), tactile-button (BtnMode)\n"
                         '  board: "xiao-esp32-c6" → "firebeetle2-esp32s3"\n'
                         "  kept, not from a pick: jst-ph-2-power-inlet\n" % (project / "requirements.json"))
        self.assertEqual((project / "requirements.json").read_text(), before)

    def test_a_board_that_changes_is_said_from_and_to_and_one_that_does_not_is_not(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        said, _ = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((said["data"]["board_was"], said["data"]["requirements"]["board"]), ("xiao-esp32-c6", "firebeetle2-esp32s3"))
        self.assertIn('  board: "xiao-esp32-c6" → "firebeetle2-esp32s3"\n', self.text(["--requirements", str(project)]))
        self.assertNotIn("→", self.text(["--requirements", str(project)]))

    def test_a_second_run_with_the_same_picks_changes_nothing(self):
        _, project = self.project(self.DRIVER_AND_TWO_BUTTONS + [("light", [{"part": "x-led"}])])
        first_said, _ = run(["--requirements", str(project)])
        first = (project / "requirements.json").read_text()
        said, code = run(["--requirements", str(project)])
        self.assertEqual((first_said["data"]["shelved"], first_said["data"]["board_was"], code, (project / "requirements.json").read_text(),
                          said["data"]["kept"], said["data"]["shelved"], said["data"]["board_was"]),
                         (["x-led"], None, 0, first, [], [], "firebeetle2-esp32s3"))

    def test_the_names_it_checks_are_the_ones_the_generator_gives(self):
        for part_id, name in (("tactile-button", None), ("led-1", None), ("led1", None), ("jst_ph_2", None), ("tactile-button", "BtnOpen")):
            with self.subTest(part_id=part_id, name=name):
                instance = {"_instance": name} if name else {}
                self.assertEqual(needs._called(part_id, name), emit_board.component_name(dict({"id": part_id}, **instance)))

    def test_a_re_pick_leaves_the_old_part_listed_as_kept(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        run(["--requirements", str(project)])
        self.picking(project, [self.BOARD, ("light", [{"part": "x-led"}])])
        said, _ = run(["--requirements", str(project)])
        self.assertEqual((self.written(project)["parts"], said["data"]["kept"]),
                         (["led-red-5mm", "x-led"], [{"part": "led-red-5mm", "name": None}]))
        self.assertIn("  kept, not from a pick: led-red-5mm\n", self.text(["--requirements", str(project), "--dry-run"]))

    def test_a_part_picked_for_two_needs_when_the_file_holds_one_of_it_adds_only_the_other(self):
        for held in ({"part": "tactile-button", "name": "BtnOpen"}, "tactile-button"):
            with self.subTest(held=held):
                _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
                (project / "requirements.json").write_text(json.dumps({"parts": [held]}))
                said, _ = run(["--requirements", str(project)])
                self.assertEqual((self.written(project)["parts"], said["data"]["kept"]),
                                 ([held, {"part": "tactile-button", "name": "Mode"}], []))
                self.assertEqual(emit_board.duplicate_component_names(design.parts_of(self.written(project), project)), [])

    def test_an_entry_named_after_a_need_is_that_need_s_own(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        (project / "requirements.json").write_text(json.dumps({"parts": [{"part": "tactile-button", "name": "Mode"}]}))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["kept"]),
                         (0, [{"part": "tactile-button", "name": "Mode"}, {"part": "tactile-button", "name": "OpenLid"}], []))

    def test_of_two_instances_the_one_no_pick_explains_is_the_one_kept(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        run(["--requirements", str(project)])
        self.picking(project, [self.BOARD, ("open-lid", [{"part": "led-red-5mm"}]), ("mode", [{"part": "tactile-button"}])])
        said, _ = run(["--requirements", str(project)])
        self.assertEqual((self.written(project)["parts"], said["data"]["kept"]),
                         ([{"part": "tactile-button", "name": "OpenLid"}, {"part": "tactile-button", "name": "Mode"}, "led-red-5mm"],
                          [{"part": "tactile-button", "name": "OpenLid"}]))

    def test_two_needs_whose_ids_make_one_name_are_refused_by_need_id_and_a_name_by_hand_settles_it(self):
        home, project = self.project([self.BOARD, ("led-1", [{"part": "led-red-5mm"}]), ("led1", [{"part": "led-red-5mm"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, [p["subject"] for p in said["problems"]]), ("problems", 1, ["led1"]))
        self.assertIn("Led1", said["problems"][0]["sentence"])
        self.assertIn("led-1", said["problems"][0]["sentence"])
        self.assertFalse((project / "requirements.json").exists())
        (project / "requirements.json").write_text(json.dumps({"parts": [{"part": "led-red-5mm", "name": "Led2"}]}))
        _, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"]),
                         (0, [{"part": "led-red-5mm", "name": "Led2"}, {"part": "led-red-5mm", "name": "Led1"}]))

    def test_a_new_name_that_the_file_already_gives_another_part_is_refused_by_need_id(self):
        home, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        held = json.dumps({"parts": [{"part": "jst-ph-2-power-inlet", "name": "Mode"}]})
        (project / "requirements.json").write_text(held)
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, [p["subject"] for p in said["problems"]]), (1, ["mode"]))
        self.assertIn("jst-ph-2-power-inlet", said["problems"][0]["sentence"])
        self.assertEqual((project / "requirements.json").read_text(), held)

    def test_one_need_picking_two_parts_that_other_needs_pick_too_is_refused_by_need_id(self):
        home, project = self.project([self.BOARD, ("alarm", [{"part": "x-led"}, {"part": "led-red-5mm"}]),
                                      ("backup", [{"part": "x-led"}]), ("status", [{"part": "led-red-5mm"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, [p["subject"] for p in said["problems"]]), (1, ["alarm"]))
        self.assertFalse((project / "requirements.json").exists() or (home / "shelf").exists())

    def test_a_pick_whose_record_does_not_parse_is_said_so_and_is_not_called_gone(self):
        for garbled in ("{", "[]"):
            with self.subTest(garbled=garbled):
                home, project = self.project([self.BOARD, ("light", [{"part": "x-garbled"}])])
                (home / "catalog" / "x-garbled.json").write_text(garbled)
                said, code = run(["--requirements", str(project)])
                self.assertEqual((said["status"], code, [p["subject"] for p in said["problems"]]), ("problems", 1, ["x-garbled"]))
                self.assertIn("does not parse", said["problems"][0]["sentence"])
                self.assertNotIn("any more", said["problems"][0]["sentence"])

    def test_a_parts_list_that_is_no_list_is_refused_and_left_alone(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        held = json.dumps({"parts": "tactile-button"})
        (project / "requirements.json").write_text(held)
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("requirements.json", said["unchecked"][0]["sentence"])
        self.assertIn("`parts`", said["unchecked"][0]["sentence"])
        self.assertEqual(((project / "requirements.json").read_text(), (home / "shelf").exists()), (held, False))

    def test_an_entry_that_names_no_part_is_kept_and_said(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / "requirements.json").write_text(json.dumps({"parts": [5, {"name": "Orphan"}]}))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["kept"]),
                         (0, [5, {"name": "Orphan"}, "led-red-5mm"], [{"part": None, "name": None}, {"part": None, "name": "Orphan"}]))
        self.assertIn("  kept, not from a pick: an entry that names no part, an entry that names no part (Orphan)\n",
                      self.text(["--requirements", str(project)]))


class WhatTheDrawerHoldsTest(unittest.TestCase):
    """§6.7: a pick is owned when a live drawer entry holds it with a count above 0, many, or a count nobody gave."""

    ENTRIES = {"zero": {"label": "a spent pack", "count": 0, "is": {"part": "x-zero"}},
               "many": {"label": "a bag", "count": "many", "is": {"part": "x-many"}},
               "unknown": {"label": "a box", "is": {"part": "x-unknown"}},
               "dead": {"label": "a broken one", "count": 2, "is": {"part": "x-dead"}, "skip": "it died"},
               "split-a": {"label": "one of two", "count": 0, "is": {"part": "x-split"}},
               "split-b": {"label": "the other", "count": 2, "is": {"part": "x-split"}},
               "speaker": {"label": "a speaker", "count": 1}}

    def test_a_count_above_zero_many_and_a_count_nobody_gave_are_owned(self):
        for pick in ({"part": "x-many"}, {"part": "x-unknown"}, {"part": "x-split"}, {"entry": "speaker"}):
            with self.subTest(pick=pick):
                self.assertTrue(needs.owned(pick, self.ENTRIES))

    def test_a_count_of_zero_a_dead_entry_and_a_record_nobody_holds_are_not_owned(self):
        for pick in ({"part": "x-zero"}, {"part": "x-dead"}, {"entry": "dead"}, {"entry": "missing"}, {"board": "no-board"}):
            with self.subTest(pick=pick):
                self.assertFalse(needs.owned(pick, self.ENTRIES))


class TheIdeaCommandTest(unittest.TestCase):
    """commands/idea.md is followed as written (R4.2): the project is named where a command takes it as a flag, and only there."""

    def test_it_names_the_project_where_a_command_takes_it_and_only_there(self):
        lines = (ROOT / "commands" / "idea.md").read_text().splitlines()
        flagged = [line for line in lines if any(op in line for op in ("--audit", "--function-set", "--fact-set"))]
        self.assertTrue(flagged)
        for line in flagged:
            self.assertIn("--project <project>", line, line)
        for line in lines:
            if any(op in line for op in ("--needs-set", "--match", "--pick", "--requirements", "--step", "--tally")):
                self.assertNotIn("--project", line, "--needs-set and --match take the project as their argument: " + line)

    def test_it_marks_its_steps_and_ends_with_the_tally(self):
        idea = " ".join((ROOT / "commands" / "idea.md").read_text().split())
        self.assertIn("At the start of each step below — S, M, C and L — mark it", idea)
        self.assertIn("scripts/parts.py --step <project> S", idea)
        self.assertIn("## T — the tally", idea)
        self.assertIn("scripts/parts.py --tally <project>", idea)

    def test_section_l_and_the_build_page_say_what_a_later_run_keeps(self):
        idea = " ".join((ROOT / "commands" / "idea.md").read_text().split())
        build = " ".join((ROOT / "commands" / "build.md").read_text().split())
        self.assertIn("A later run keeps everything already in the file", idea)
        self.assertIn("says which entries no pick explains (`kept, not from a pick`)", idea)
        self.assertIn("run again, it keeps whatever you added to the file by hand and adds only the parts your picks still lack", build)


if __name__ == "__main__":
    unittest.main()
