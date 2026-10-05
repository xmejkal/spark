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

    def catalog(self, *records):
        for record in records:
            (self.home / "catalog" / (record["id"] + ".json")).write_text(json.dumps(dict({"schema": 1, "kind": "sensor"}, **record)))

    def alone(self, need):
        """One need, matched alone (a full page holds few needs): the need's answer, with its candidates and `more`."""
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [need]}))
        said, _ = run(["--match", str(self.project)])
        return said["data"]["needs"][0]

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

    def test_a_board_owes_nothing_and_is_never_broken_here(self):
        board = [c for c in self.needs["board"]["candidates"] if c["id"] == "firebeetle2-esp32s3"][0]
        self.assertEqual((board["owes"], board["broken"]), ([], False))

    def test_a_project_s_own_record_shadows_the_same_id_elsewhere(self):
        (self.project / "parts").mkdir(parents=True)
        (self.project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Our probe", "kind": "sensor",
                                                                         "function": [{"does": "sense", "what": "soil-moisture"}]}))
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

    def test_a_verb_nothing_has_is_an_empty_answer(self):
        self.assertEqual((self.code, self.needs["keep"]["candidates"]), (0, []))

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


class TheIdeaCommandTest(unittest.TestCase):
    """commands/idea.md is followed as written (R4.2): the project is named where a command takes it as a flag, and only there."""

    def test_it_names_the_project_where_a_command_takes_it_and_only_there(self):
        lines = (ROOT / "commands" / "idea.md").read_text().splitlines()
        flagged = [line for line in lines if "--audit" in line or "--function-set" in line]
        self.assertTrue(flagged)
        for line in flagged:
            self.assertIn("--project <project>", line, line)
        for line in lines:
            if "--needs-set" in line or "--match" in line:
                self.assertNotIn("--project", line, "--needs-set and --match take the project as their argument: " + line)


if __name__ == "__main__":
    unittest.main()
