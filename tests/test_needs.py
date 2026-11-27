"""P96: a goal's needs, and the store's candidates for each (docs/2026-10-04-store-design.md §5.3, §6.2, §8 S and M)."""

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import slow  # noqa: E402
from board_library import board_missing  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records import board_records, onboard_parts  # noqa: E402
import check_spine  # noqa: E402
from spark.build import board_engine  # noqa: E402
from spark.design import loader  # noqa: E402
from spark.sourcing import drawer  # noqa: E402
from spark.design import board_components  # noqa: E402
from spark.design import needs  # noqa: E402
from spark.design import need_requirements  # noqa: E402
import parts  # noqa: E402
from spark.records import record_kind  # noqa: E402
from spark.records import store  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.core import text_guards  # noqa: E402
from spark.idea.drop_need import DropNeed  # noqa: E402
from flat_message import NASTY, assert_flat  # noqa: E402

#: The fix of a drop that was not planned or written, as an agent reads it (P853 pins each fix of the idea area).
UNWRITTEN_FIX = "check the disk and the store folder, then run the same drop again: the drawer is written first and the needs file last"


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

    def test_a_newline_in_the_project_path_gives_one_line_in_a_needs_file_that_is_no_json(self):
        project = self.project.parent / NASTY
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "needs.json").write_text("{not json")
        with self.assertRaises(store.StoreError) as caught:
            needs.read(project)
        assert_flat(self, caught.exception)
        self.assertEqual(caught.exception.code, "record_file_broken")

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

    def test_a_need_set_aside_on_the_person_s_word_keeps_it_on_a_later_write(self):
        """P977: `aside: true` says the person left the need out of this board. It is a field, not a mark."""
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "aside": True}])])
        self.assertEqual((code, said["data"]["changes"]), (0, [{"need": "soil", "new": False, "was": {"aside": None}, "now": {"aside": True}}]))
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "gap"}])])
        self.assertEqual(self.saved()["needs"], [{"id": "soil", "does": "sense", "what": "soil-moisture", "aside": True, "mark": "gap"}])

    def test_the_needs_and_match_text_show_a_need_set_aside(self):
        """P977: list_needs and match_needs print `[aside]` on the line of a need set aside."""
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture", "aside": True},
                                                       {"id": "wet", "does": "sense", "what": "soil-moisture"}])])
        for flag in ("--needs", "--match"):
            with self.subTest(flag=flag):
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    parts.main([flag, str(self.project)])
                lines = out.getvalue().splitlines()
                soil = [line for line in lines if line.lstrip().startswith("soil")]
                self.assertEqual(len(soil), 1, lines)
                self.assertTrue(soil[0].endswith("  [aside]"), soil)
                self.assertFalse([line for line in lines if line.lstrip().startswith("wet") and "[aside]" in line])

    def test_aside_is_true_or_null_and_anything_else_refuses_the_write(self):
        for aside in ("yes", False, 1):
            with self.subTest(aside=aside):
                said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "x", "aside": aside}])])
                self.assertEqual((said["status"], code), ("problems", 1))
                self.assertIn("`aside` is true, or null", json.dumps(said["problems"]))
        self.assertFalse((self.project / ".spark" / "needs.json").exists())

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


class TheMatchReadsThePicksTest(unittest.TestCase):
    """P1141 (#1676), the PO's P829 walk: after a pick, --match says how many pieces the project holds and which needs pick
    each candidate, and --needs says each need's pick. `free` keeps its meaning: free to this project (P403)."""

    def setUp(self):
        self.home, self.project = a_store_with_a_drawer(), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def with_needs(self, needs):
        (self.project / ".spark").mkdir(parents=True, exist_ok=True)
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": needs}))

    def candidates(self):
        """{need: {id or entry and kind: candidate}} of --match, every page."""
        said, code = run(["--match", str(self.project)])
        self.assertEqual(code, 0, said)
        matched = list(said["data"]["needs"])
        while said["truncated"] and said["truncated"]["next"]:
            said, _ = run(["--match", str(self.project), "--from", str(len(matched))])
            matched += said["data"]["needs"]
        return {need["need"]: {(c["id"] or c["entry"], c["kind"]): c for c in need["candidates"]} for need in matched}

    def text(self, flag):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            parts.main([flag, str(self.project)])
        return out.getvalue().splitlines()

    def test_a_picked_record_says_the_pieces_held_here_and_the_needs_that_pick_it(self):
        self.with_needs([{"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "wet", "does": "sense", "what": "soil-moisture"},
                         {"id": "alarm", "does": "sound", "what": "speaker"}])
        run(["--pick", str(self.project), "soil=x-soil", "wet=x-soil", "alarm=speaker"])
        found = self.candidates()
        soil, speaker = found["soil"][("x-soil", "part")], found["alarm"][("speaker", None)]
        self.assertEqual((soil["owned"], soil["free"], soil["held_here"], soil["picked_for"]), (8, 8, 2, ["soil", "wet"]))
        self.assertEqual((speaker["held_here"], speaker["picked_for"]), (1, ["alarm"]))
        line = next(line for line in self.text("--match") if "x-soil (catalog)" in line)
        self.assertIn("  free 8 (2 held by this project)  owes ", line)
        self.assertTrue(line.endswith("  [picked for soil, wet]"), line)

    def test_one_board_for_three_needs_is_one_piece_held_and_each_need_is_named(self):
        # the walk: board, button and light each picked the T-Display, and --match said only "free 1"
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}}))
        self.with_needs([{"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "light", "does": "indicate", "what": "light"},
                         {"id": "blink", "does": "indicate", "what": "light"}])
        run(["--pick", str(self.project), "board=xiao-esp32-c6", "light=xiao-esp32-c6", "blink=xiao-esp32-c6"])
        xiao = self.candidates()["light"][("xiao-esp32-c6", "board")]
        self.assertEqual((xiao["owned"], xiao["free"], xiao["held_by"], xiao["held_here"], xiao["picked_for"]),
                         (1, 1, [], 1, ["board", "light", "blink"]))
        line = next(line for line in self.text("--match") if "xiao-esp32-c6 (library)" in line)
        self.assertIn("free 1 (1 held by this project)  [picked for board, light, blink]", line)

    def test_the_pieces_held_here_come_before_the_other_holders(self):
        # the PR lens: "free 3, held by alarm2 (1 held by this project)" read as the other project's hold
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 3, "is": {"board": "xiao-esp32-c6"},
                                                                    "used_in": {"door-bell": 1}}))
        self.with_needs([{"id": "board", "does": "compute", "what": "microcontroller"}])
        run(["--pick", str(self.project), "board=xiao-esp32-c6"])
        line = next(line for line in self.text("--match") if "xiao-esp32-c6 (library)" in line)
        self.assertIn("free 2 (1 held by this project), held by door-bell  [picked for board]", line)

    def test_a_many_count_a_hold_with_no_pick_and_a_part_nobody_holds(self):
        (self.home / "drawer" / "buttons.json").write_text(json.dumps({"schema": 1, "label": "a bag of buttons", "count": "many",
                                                                        "is": {"part": "tactile-button"}, "used_in": {"plant-alarm": 1}}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        self.with_needs([{"id": "input", "does": "input", "what": "button"}, {"id": "soil", "does": "sense", "what": "soil-moisture"}])
        found = self.candidates()
        button, soil = found["input"][("tactile-button", "part")], found["soil"][("x-soil", "part")]
        self.assertEqual((button["free"], button["held_here"], "picked_for" in button), ("many", 1, False))
        self.assertFalse({"held_here", "picked_for"} & set(soil), "a key only when this project holds or picks it")
        lines = self.text("--match")
        self.assertTrue(next(line for line in lines if "tactile-button (" in line).endswith("free many (1 held by this project)"))
        soil_line = next(line for line in lines if "x-soil (catalog)" in line)
        self.assertIn("  free 8  owes ", soil_line)
        self.assertNotIn("this project", soil_line)
        self.assertNotIn("[picked", soil_line)

    def test_a_record_and_a_drawer_entry_of_one_key_are_two_candidates_and_only_the_picked_one_is_marked(self):
        # the refuter's R2-2: a pick names a kind, so an entry "led" is not the record "led"
        self.catalog_led()
        (self.home / "drawer" / "led.json").write_text(json.dumps({"schema": 1, "label": "loose LEDs", "count": 5,
                                                                    "function": [{"does": "indicate", "what": "light"}]}))
        self.with_needs([{"id": "light", "does": "indicate", "what": "light", "pick": [{"entry": "led"}]}])
        found = self.candidates()["light"]
        self.assertEqual((found[("led", None)]["picked_for"], found[("led", "part")].get("picked_for")), (["light"], None))

    def catalog_led(self):
        (self.home / "catalog" / "led.json").write_text(json.dumps({"schema": 1, "id": "led", "name": "A red LED", "kind": "led",
                                                                    "function": [{"does": "indicate", "what": "light"}]}))

    def test_a_pick_of_a_record_s_drawer_entry_and_a_need_set_aside_with_its_pick_are_named(self):
        self.with_needs([{"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "probe"}]},
                         {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True, "pick": [{"part": "x-soil"}]}])
        self.assertEqual(self.candidates()["soil"][("x-soil", "part")]["picked_for"], ["soil", "wet"])
        plan = needs.PickPlan(self.project)
        self.assertEqual((plan.picked_for("x-soil"), plan.picked_for("x-soil", "part"), plan.picked_for("x-soil", "entry"),
                          plan.picked_for("probe", "entry")), (["soil", "wet"], ["soil", "wet"], [], []))
        self.assertEqual(plan.needs_picking("x-soil", "wet"), ["soil"])  # C1: one rule; an old entry pick of a record counts
        # the PR refuter: a refused hold names the stored key, here the entry, so a pick with no kind matches it too
        self.assertEqual((plan.picked_for("probe"), plan.needs_picking("probe", "wet")), (["soil"], ["soil"]))

    def test_a_part_named_for_the_parts_list_counts_only_the_needs_that_pick_that_part(self):
        # the fix refuter: a record id equal to another record's drawer entry key named the entry's need too
        from spark.flow.phase_readers import named_pick
        (self.home / "catalog" / "probe.json").write_text(json.dumps({"schema": 1, "id": "probe", "name": "A pH probe", "kind": "sensor",
                                                                      "function": [{"does": "sense", "what": "acidity"}]}))
        self.with_needs([{"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "probe"}]},
                         {"id": "acid", "does": "sense", "what": "acidity", "pick": [{"part": "probe"}]}])
        plan = needs.PickPlan(self.project)
        self.assertEqual((named_pick(plan, "probe"), named_pick(plan, "x-soil")),
                         ("“A pH probe” for acid", "“Capacitive soil moisture sensor” for soil"))

    def test_the_needs_text_says_each_pick_before_the_aside_tag(self):
        self.with_needs([{"id": "soil", "does": "sense", "what": "soil-moisture", "mark": "have", "pick": [{"part": "x-soil"}]},
                         {"id": "alarm", "does": "sound", "what": "speaker", "pick": [{"entry": "speaker"}, {"entry": "mp3"}]},
                         {"id": "wet", "does": "sense", "what": "soil-moisture", "aside": True, "pick": [{"part": "x-soil"}]},
                         {"id": "dry", "does": "sense", "what": "soil-moisture"}])
        lines = {line.split()[0]: line for line in self.text("--needs")}
        self.assertTrue(lines["soil"].endswith("[have]  picked: x-soil"), lines["soil"])
        self.assertTrue(lines["alarm"].endswith("  picked: speaker, mp3"), lines["alarm"])
        self.assertTrue(lines["wet"].endswith("  picked: x-soil  [aside]"), lines["wet"])
        self.assertNotIn("picked", lines["dry"])


class TheConditionOrdersTest(unittest.TestCase):
    """P1015: a need's condition orders its candidates and leaves every score as it is (the walk p934-display's screen)."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "a-screen"
        for folder in ("catalog", "drawer"):
            (self.home / folder).mkdir()
        records = {"x-board": {"name": "A board", "function": [{"does": "indicate", "what": "onboard display screen"}]},
                   "x-tft": {"name": "A TFT", "function": [{"does": "indicate", "what": "display"}]},
                   "x-epaper": {"name": "A 2.9 inch module", "about": "A three-colour display screen."}}
        for key, record in records.items():
            (self.home / "catalog" / (key + ".json")).write_text(json.dumps(dict({"schema": 1, "id": key, "kind": "display"}, **record)))
            entry = {"schema": 1, "label": key, "count": 1, "is": {"part": key}}
            if key == "x-epaper":  # the e-paper's words are in its drawer entry's function, as in the walk
                entry["function"] = [{"does": "indicate", "what": "a 2.9 inch three-colour e-paper picture"}]
            (self.home / "drawer" / (key + ".json")).write_text(json.dumps(entry))
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        screen = {"does": "indicate", "what": "display screen"}
        run(["--needs-set", str(self.project), a_file([dict(screen, id="screen", condition="e-paper"), dict(screen, id="plain")])])

    def first_three(self, need):
        said, _ = run(["--match", str(self.project)])
        matched = list(said["data"]["needs"])
        while said["truncated"] and said["truncated"]["next"]:
            said, _ = run(["--match", str(self.project), "--from", str(len(matched))])
            matched += said["data"]["needs"]
        return [(c["id"], c["score"]) for c in [n for n in matched if n["need"] == need][0]["candidates"][:3]]

    def test_the_condition_puts_the_owned_e_paper_first_and_keeps_each_score(self):
        self.assertEqual(self.first_three("plain"), [("x-board", 1.0), ("x-tft", 0.5), ("x-epaper", 0.4)])
        self.assertEqual(self.first_three("screen"), [("x-epaper", 0.4), ("x-board", 1.0), ("x-tft", 0.5)])


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
        self.needs, self.code = self.matched_needs()

    def matched_needs(self):
        """Every need with its candidates, however many pages the library's growth takes, and the first page's exit code."""
        said, code = run(["--match", str(self.project)])
        matched = list(said["data"]["needs"])
        while said["truncated"] and said["truncated"]["next"]:
            said, _ = run(["--match", str(self.project), "--from", str(len(matched))])
            matched += said["data"]["needs"]
        return {need["need"]: need for need in matched}, code

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

    # P991: what the person owns with a record comes before what they own with none, and another project's record ranks
    # with the shelf (the PO at the p934-display page, 2026-11-22: "the beetle 2 c6 that we created is not even there")
    def test_an_owned_record_ranks_before_an_owned_entry_with_no_record_at_the_same_score(self):
        self.catalog({"id": "y-speaker", "name": "A small speaker", "kind": "actuator", "function": [{"does": "sound", "what": "speaker"}]})
        (self.home / "drawer" / "y-spk.json").write_text(json.dumps({"schema": 1, "label": "small speaker", "count": 1, "is": {"part": "y-speaker"}}))
        found = [(c["id"] or c["entry"], c["owned"], c["score"]) for c in self.alone({"id": "alarm", "does": "sound", "what": "speaker"})["candidates"]]
        self.assertEqual(found[:2], [("y-speaker", 1, 1.0), ("speaker", 2, 1.0)])

    def test_an_owned_entry_with_the_need_s_words_ranks_before_an_owned_record_with_none(self):
        self.catalog({"id": "y-buzzer", "name": "A buzzer", "kind": "actuator", "function": [{"does": "sound", "what": "buzzer"}]})
        (self.home / "drawer" / "y-buz.json").write_text(json.dumps({"schema": 1, "label": "buzzer", "count": 1, "is": {"part": "y-buzzer"}}))
        found = [(c["id"] or c["entry"], c["score"] > 0) for c in self.alone({"id": "alarm", "does": "sound", "what": "mp3-player"})["candidates"]]
        self.assertLess(found.index(("mp3", True)), found.index(("y-buzzer", False)))

    def test_a_record_in_another_listed_project_ranks_with_the_shelf_before_the_library(self):
        other = Path(tempfile.mkdtemp()) / "other"
        (other / "boards").mkdir(parents=True)
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        (other / "boards" / "my-c6.json").write_text(json.dumps(dict(board, id="my-c6")))
        (self.home / "projects.json").write_text(json.dumps({"other": str(other)}))
        (self.home / "drawer" / "c6.json").write_text(json.dumps({"schema": 1, "label": "my C6", "count": 1, "is": {"board": "my-c6"}}))
        found = [(c["id"], c["in"], c["owned"]) for c in self.alone({"id": "mcu", "does": "compute", "what": "microcontroller"})["candidates"]]
        self.assertEqual(found[:2], [("my-c6", "other", 1), ("firebeetle2-esp32s3", "library", 1)])

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
        self.assertEqual((code, [(c["id"], c["kind"], c["name"], c["in"]) for c in said["data"]["catalog"]]), (0, [("y-seven", "sensor", "Quirky probe", "catalog")]))
        said, code = run(["--need", "qz5520"])
        self.assertEqual((code, [(c["id"], c["kind"], c["name"]) for c in said["data"]["catalog"]]), (0, [("y-mixed", "sensor", "Mixed probe")]),
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

    # --- MVP --- P389: a board is offered for a need its own LED, buttons or display serve
    def light(self):
        """The candidates for a need of light, matched alone: the XIAO's own LED serves it."""
        return {c["id"]: c for c in self.alone({"id": "blink", "does": "indicate", "what": "light"})["candidates"] if c["id"]}

    def test_a_board_with_an_onboard_led_is_offered_for_a_need_of_light(self):
        xiao = self.light()["xiao-esp32-c6"]
        self.assertTrue(xiao["what_matches"])
        said, _ = run(["--offer", "xiao-esp32-c6"])
        self.assertIn({"does": "indicate", "what": "onboard LED light"}, said["data"]["offer"]["functions"])

    def test_the_word_led_finds_the_same_board(self):
        found = {c["id"]: c for c in self.alone({"id": "blink", "does": "indicate", "what": "led"})["candidates"] if c["id"]}
        self.assertTrue(found["xiao-esp32-c6"]["what_matches"])

    def test_a_board_with_an_onboard_button_but_no_onboard_led_is_not_offered_for_light(self):
        board = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
        del board["pin_roles"]["onboard_led"]
        (self.project / "boards").mkdir(parents=True)
        (self.project / "boards" / "no-led.json").write_text(json.dumps(dict(board, id="no-led")))
        self.assertNotIn("no-led", self.light())

    def test_a_board_with_its_own_display_is_offered_for_a_need_of_a_display_or_a_screen(self):
        (self.project / "boards").mkdir(parents=True)
        shutil.copy(ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json", self.project / "boards")
        for what in ("display", "screen"):
            with self.subTest(what=what):
                found = {c["id"]: c for c in self.alone({"id": "show", "does": "indicate", "what": what})["candidates"] if c["id"]}
                self.assertEqual((found["lilygo-t-display"]["in"], found["lilygo-t-display"]["what_matches"]), ("project", True))

    def test_buttons_on_two_gpios_with_no_labels_get_no_name_in_pins_py_and_are_not_offered(self):
        board = json.loads((ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json").read_text())
        offered = lambda: [c["id"] for c in self.alone({"id": "press", "does": "input", "what": "button"})["candidates"]]  # noqa: E731
        (self.project / "boards").mkdir(parents=True)
        (self.project / "boards" / "lilygo-t-display.json").write_text(json.dumps(board))
        self.assertIn("lilygo-t-display", offered())
        del board["pin_roles"]["onboard_button"]["labels"]
        (self.project / "boards" / "lilygo-t-display.json").write_text(json.dumps(board))
        self.assertNotIn("lilygo-t-display", offered())

    def power_candidates(self, does, what):
        (self.project / "boards").mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json", self.project / "boards")
        found = {c["id"]: c for c in self.alone({"id": "p", "does": does, "what": what})["candidates"] if c["id"]}
        return found.get("lilygo-t-display")

    def test_a_board_with_its_own_charger_regulator_battery_input_or_battery_level_is_offered_for_that_need(self):
        for does, what in (("power", "charger"), ("power", "voltage regulator"), ("connect", "battery input"),
                           ("sense", "battery level")):
            with self.subTest(need=(does, what)):
                found = self.power_candidates(does, what)
                self.assertEqual((found["in"], found["what_matches"]), ("project", True))

    def test_a_need_for_the_battery_itself_or_for_a_voltage_is_not_met_by_the_boards_own_power_parts(self):
        for does, what in (("power", "battery"), ("power", "battery charger"), ("sense", "voltage")):
            with self.subTest(need=(does, what)):
                found = self.power_candidates(does, what)
                self.assertFalse(found and found["what_matches"], found)

    def test_a_board_picked_for_the_mcu_need_and_offered_for_light_is_free_and_held_by_nobody(self):
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({
            "schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}, "used_in": {"plant-alarm": 1}}))
        xiao = self.light()["xiao-esp32-c6"]
        self.assertEqual((xiao["owned"], xiao["free"], xiao["held_by"]), (1, 1, []))
    # --- end MVP ---

    # --- MVP --- P403: --match names who holds the stock that is not free
    def hold_the_xiao(self, *holders):
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({
            "schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}, "used_in": {who: 1 for who in holders}}))

    def board_text(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        return next(line for line in out.getvalue().splitlines() if "xiao-esp32-c6 (" in line)

    def xiao(self):
        board = [c for c in self.matched_needs()[0]["board"]["candidates"] if c["id"] == "xiao-esp32-c6"]
        return board[0]

    def test_a_match_names_who_holds_a_board_and_the_asking_project_is_left_out(self):
        self.hold_the_xiao("reaction-game", "plant-alarm", "plant-alarm-2")
        self.assertEqual(self.xiao()["held_by"], ["plant-alarm-2", "reaction-game"])
        self.assertIn("free 0 (1 held by this project), held by plant-alarm-2, reaction-game", self.board_text())  # P1141

    def test_a_candidate_nobody_holds_says_no_holder(self):
        self.assertEqual(self.xiao()["held_by"], [])
        self.assertNotIn("held by", self.board_text())

    def test_an_unlisted_project_is_not_named_as_holding_its_own_board(self):
        # a moved or renamed folder leaves projects.json without it, and --pick still holds under the folder's name
        (self.home / "projects.json").write_text("{}")
        own = store.plan_listed_name(self.project)
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({
            "schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}, "used_in": {own: 1}}))
        self.assertEqual(self.xiao()["held_by"], [])
        self.assertNotIn(", held by", self.board_text())  # P1141: the line says the project's own piece in its own words
        self.assertIn("free 1 (1 held by this project)", self.board_text())

    def test_a_holder_name_with_a_newline_shows_a_question_mark_in_the_match_text(self):
        self.hold_the_xiao("reaction\ngame")
        self.assertIn("free 0, held by reaction?game", self.board_text())

    def test_a_board_owes_nothing_and_a_sound_one_is_not_broken(self):
        board = [c for c in self.needs["board"]["candidates"] if c["id"] == "firebeetle2-esp32s3"][0]
        self.assertEqual((board["owes"], board["broken"]), ([], False))

    def test_a_board_whose_file_has_no_header_geometry_says_it_stops_at_the_footprint(self):
        # C-7 (the council on PR #98): a board without header geometry was offered like the S3, and the chain stops at its footprint stage (P121)
        out = io.StringIO()
        with board_missing("physical.header"):  # setUp matched with the real library, where the XIAO builds
            needs, _ = self.matched_needs()
            with contextlib.redirect_stdout(out):
                parts.main(["--match", str(self.project)])
        boards_offered = {c["id"]: c for c in needs["board"]["candidates"] if c["kind"] == "board"}
        self.assertEqual((boards_offered["xiao-esp32-c6"]["stops_at"], boards_offered["firebeetle2-esp32s3"]["stops_at"]), ("footprint", None))
        lines = out.getvalue().splitlines()
        self.assertIn("  stops at the footprint stage (P121): its board file lacks physical.header", next(line for line in lines if "xiao-esp32-c6 (library)" in line))
        self.assertEqual(boards_offered["xiao-esp32-c6"]["stops_why"], "xiao-esp32-c6 cannot have a footprint generated — these are not recorded, and none of "
                         "them can be derived from the rest:\n  physical.header (no header geometry at all)")
        self.assertNotIn("stops_why", boards_offered["firebeetle2-esp32s3"])  # a board that builds gains no key
        self.assertNotIn("stop_line", boards_offered["firebeetle2-esp32s3"])
        self.assertNotIn("stop_line", boards_offered["xiao-esp32-c6"])  # only the text shows the line
        self.assertNotIn("stops at", next(line for line in lines if "firebeetle2-esp32s3 (library)" in line))

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
        # P976: the default matcher is word-overlap (the PO's yes, 2026-11-21), so `why` names where each word is
        self.assertEqual(found["ntc"], {"id": None, "kind": None, "entry": "ntc", "owes": [], "broken": False, "proof": [], "in": "drawer",
                                        "label": "an NTC thermistor", "what": ["temperature"], "what_matches": True,
                                        "score": 1.0, "why": ["temperature: in functions"], "held_by": [], "owned": 3, "free": 3, "unsure": False,
                                        "limits": []})
        combo = found["y-combo"]
        self.assertEqual((combo["kind"], combo["entry"], combo["in"], combo["label"], combo["what"], combo["proof"], combo["what_matches"]),
                         ("part", None, "catalog", "A combo board", ["temperature"], [], True))

    def test_a_candidate_has_a_score_and_why_and_the_text_shows_its_about(self):
        self.catalog({"id": "y-range", "name": "A rangefinder", "function": [{"does": "sense", "what": "distance"}],
                      "about": "Tells how far away a thing is."})
        found = {c["id"]: c for c in self.alone({"id": "far", "does": "sense", "what": "distance"})["candidates"] if c["id"]}
        # P976: the default matcher is word-overlap (the PO's yes, 2026-11-21), so `why` names where each word is
        self.assertEqual((found["y-range"]["score"], found["y-range"]["why"]), (1.0, ["distance: in functions"]))
        self.assertNotIn("about", found["y-range"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        self.assertIn("Tells how far away a thing is.", out.getvalue())

    def test_word_overlap_finds_a_part_filed_under_other_words(self):
        self.catalog({"id": "y-range", "name": "A rangefinder", "function": [{"does": "sense", "what": "distance"}], "tags": ["range"]})
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "far", "does": "sense", "what": "range"}]}))
        said, _ = run(["--match", str(self.project), "--matcher", "word-overlap"])
        first = [c for c in said["data"]["needs"][0]["candidates"] if c["id"] == "y-range"][0]
        self.assertEqual((first["score"], first["why"], first["what_matches"]), (0.8, ["range: in tags"], False))

    def test_word_overlap_is_the_default_matcher(self):
        # P976 (the PO's yes, 2026-11-21): --match with no --matcher finds a part by its tags
        self.catalog({"id": "y-range", "name": "A rangefinder", "function": [{"does": "sense", "what": "distance"}], "tags": ["range"]})
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "far", "does": "sense", "what": "range"}]}))
        said, _ = run(["--match", str(self.project)])
        first = [c for c in said["data"]["needs"][0]["candidates"] if c["id"] == "y-range"][0]
        self.assertEqual((first["score"], first["why"]), (0.8, ["range: in tags"]))

    def test_the_score_orders_candidates_that_tie_on_owned_and_layer(self):
        self.catalog({"id": "y-aaa", "name": "Alpha probe", "function": [{"does": "sense", "what": "distance"}], "tags": ["range"]},
                     {"id": "y-zzz", "name": "Zulu probe", "function": [{"does": "sense", "what": "range"}]})
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "far", "does": "sense", "what": "range"}]}))
        said, _ = run(["--match", str(self.project), "--matcher", "word-overlap"])
        found = [(c["id"], c["score"]) for c in said["data"]["needs"][0]["candidates"] if c["id"] in ("y-aaa", "y-zzz")]
        self.assertEqual(found, [("y-zzz", 1.0), ("y-aaa", 0.8)], "unowned, both in the catalog: the id would put y-aaa first")

    def test_the_next_page_keeps_the_matcher(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": "n%d" % n, "does": "sense", "what": "soil-moisture"} for n in range(12)]}))
        said, _ = run(["--match", str(self.project), "--matcher", "word-overlap"])
        self.assertIn("word-overlap", said["truncated"]["next"]["argv"])

    def test_a_malformed_record_text_is_ignored(self):
        self.catalog({"id": "y-odd", "name": "An odd probe", "function": [{"does": "sense", "what": "distance"}], "tags": "knob", "about": 5})
        found = [c for c in self.alone({"id": "far", "does": "sense", "what": "distance"})["candidates"] if c["id"] == "y-odd"]
        self.assertEqual((len(found), found[0]["score"]), (1, 1.0))

    def test_a_matcher_that_does_not_serve_match_is_refused(self):
        said, code = run(["--match", str(self.project), "--matcher", "name-contains"])
        self.assertEqual((code, said["status"]), (2, "could-not-run"))
        self.assertIn("same-words, word-overlap", said["unchecked"][0]["sentence"])

    def test_offer_prints_what_a_record_says_of_itself(self):
        self.catalog({"id": "y-range", "name": "A rangefinder", "about": "Tells how far away a thing is.", "tags": ["range"]})
        said, code = run(["--offer", "y-range"])
        self.assertEqual((code, said["data"]["offer"]["about"], said["data"]["offer"]["tags"]), (0, "Tells how far away a thing is.", ["range"]))

    def test_the_cut_line_says_what_the_hidden_candidates_are(self):
        for number in range(9):
            (self.home / "drawer" / ("t%d.json" % number)).write_text(json.dumps(
                {"schema": 1, "label": "thermometer %d" % number, "count": 1, "function": [{"does": "sense", "what": "temperature"}]}))
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "wet", "does": "sense", "what": "soil-moisture"}]}))
        # P976 (the PO's yes, 2026-11-21): word-overlap is the default, so same-words is named and the default says the scores
        for extra, said in ((["--matcher", "same-words"], "more, none with the need's words"), ([], "more, each scoring under 0.5"),
                            (["--matcher", "word-overlap"], "more, each scoring under 0.5")):
            with self.subTest(extra=extra):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    parts.main(["--match", str(self.project)] + extra)
                self.assertRegex(out.getvalue(), r"… \d+ " + re.escape(said))

    def test_offer_with_a_project_reads_the_project_s_own_record(self):
        (self.project / "parts").mkdir(parents=True)
        (self.project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Our probe", "kind": "sensor",
                                                                         "about": "The project one.",
                                                                         "function": [{"does": "sense", "what": "soil-moisture"}]}))
        said, _ = run(["--offer", "x-soil", "--project", str(self.project)])
        self.assertEqual(said["data"]["offer"]["about"], "The project one.")
        said, _ = run(["--offer", "x-soil"])
        self.assertNotEqual(said["data"]["offer"]["about"], "The project one.", "without --project the project's records are not read")

    def test_offer_json_fits_the_page_however_long_a_record_s_power_note_is(self):
        self.catalog({"id": "y-hungry", "name": "A hungry probe", "power": {"note": "3V3\u202e only " + "x" * 6000}})
        for key in ("y-hungry", "firebeetle2-esp32s3"):
            with self.subTest(key=key):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    parts.main(["--offer", key, "--json"])
                self.assertLessEqual(len(out.getvalue()), 3400)
                self.assertNotIn("\u202e", out.getvalue())
                self.assertEqual(json.loads(out.getvalue())["data"]["offer"]["key"], key)

    # --- MVP --- P782: the onboard parts' facts are in the board's offer, the power text whole (p389 row 4, G9)
    def test_the_xiao_s_offer_holds_its_onboard_power_facts_whole(self):
        record = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())["power"]
        said, _ = run(["--offer", "xiao-esp32-c6"])
        power = json.loads(said["data"]["offer"]["facts"]["power"])
        self.assertEqual({key: power[key]["value"] for key in ("charger", "regulator", "battery_input")},
                         {key: record[key]["value"] for key in ("charger", "regulator", "battery_input")})
    # --- end MVP ---

    def test_an_entry_that_is_a_record_offers_the_record(self):
        (self.home / "drawer" / "my-probe.json").write_text(json.dumps({"schema": 1, "label": "my probe", "count": 1,
                                                                        "is": {"part": "x-soil"}, "tags": ["garden"]}))
        said, code = run(["--offer", "my-probe"])
        self.assertEqual((code, said["data"]["offer"]["key"]), (0, "x-soil"))
        self.assertIn("garden", said["data"]["offer"]["tags"])

    def test_an_offer_nobody_has_is_a_problem(self):
        said, code = run(["--offer", "unobtainium"])
        self.assertEqual((code, said["status"]), (1, "problems"))

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

    def next_line(self):
        """The next: line a pick that wrote ends with (P1141): the flow's parts step for the needs it leaves open."""
        from spark.flow.now_follow_up import FlowFollowUp
        from spark.flow.show_flow import flow_and_guide, now_steps
        step = now_steps(self.project, *flow_and_guide(self.project))[0]
        self.assertTrue(step.op == "pick" and all(pair.endswith("=<part>") for pair in step.argv[2:]), step)
        return FlowFollowUp().line(step)

    def test_the_bin_s_only_board_is_refused_naming_who_holds_it(self):
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("1 owned, held by smartbin-local", said["problems"][0]["sentence"])
        self.assertIn('[{"entry": "board", "used_in": …}]', said["problems"][0]["fix"])
        self.assertEqual((self.picks()["board"], self.entry("board")["used_in"]), (None, {"smartbin-local": 1}))

    def test_a_holder_name_with_a_newline_shows_a_question_mark_in_the_refusal_and_its_fix(self):
        (self.home / "drawer" / "board.json").write_text(json.dumps({
            "schema": 1, "label": "FireBeetle", "count": 1, "is": {"board": "firebeetle2-esp32s3"}, "used_in": {"smart\nbin": 1}}))
        said, _ = run(["--pick", str(self.project), "board=firebeetle2-esp32s3", "--dry-run"])
        self.assertIn("held by smart?bin", said["problems"][0]["sentence"])
        self.assertIn("without smart?bin", said["problems"][0]["fix"])
        self.assertNotIn("\n", said["problems"][0]["sentence"] + said["problems"][0]["fix"])

    def test_the_board_picked_for_two_needs_takes_one_piece(self):
        # P387: the board's own LED or button serves a need, so the one board a person owns is picked for it as well
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}}))
        said, code = run(["--pick", str(self.project), "board=xiao-esp32-c6", "input=xiao-esp32-c6"])
        self.assertEqual((said["status"], code), ("ok", 0))
        self.assertEqual((self.picks()["input"], self.entry("xiao")["used_in"]), ([{"board": "xiao-esp32-c6"}], {"plant-alarm": 1}))

    def test_a_board_picked_for_a_need_of_light_leaves_that_need_served_in_the_requirements(self):
        # P389: the board's own LED serves the need, so the build is not told the need has nothing on the board
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}}))
        run(["--needs-set", str(self.project), a_file([{"id": "blink", "does": "indicate", "what": "light"}])])
        run(["--pick", str(self.project), "board=xiao-esp32-c6", "blink=xiao-esp32-c6"])
        said, code = run(["--requirements", str(self.project)])
        self.assertEqual((code, [each["need"] for each in said["data"]["unserved"]]), (0, ["soil", "alarm", "input"]))

    def test_a_board_an_older_pick_held_twice_is_held_once_after_a_re_pick(self):
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 2, "is": {"board": "xiao-esp32-c6"},
                                                                    "used_in": {"plant-alarm": 2}}))
        run(["--pick", str(self.project), "board=xiao-esp32-c6", "input=xiao-esp32-c6"])
        self.assertEqual(self.entry("xiao")["used_in"], {"plant-alarm": 1})

    def test_a_pick_reserves_one_piece_and_the_history_says_it_was_reused(self):
        _, code = run(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"])
        self.assertEqual(code, 0)
        self.assertEqual((self.picks()["soil"], self.picks()["alarm"]), ([{"part": "x-soil"}], [{"entry": "speaker"}]))
        self.assertEqual((self.entry("probe")["used_in"], self.entry("speaker")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))
        self.assertEqual(self.history(), [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"},
                                          {"event": "reused", "project": "plant-alarm", "need": "alarm", "entry": "speaker"}])

    def test_a_pick_of_a_record_the_project_keeps_itself_is_not_a_reuse_of_the_store(self):
        (self.project / "parts").mkdir(parents=True)
        (self.project / "parts" / "x-own.json").write_text(json.dumps({"schema": 1, "id": "x-own", "name": "Own sensor", "kind": "sensor"}))
        _, code = run(["--pick", str(self.project), "soil=x-own", "alarm=speaker"])
        self.assertEqual((code, self.picks()["soil"]), (0, [{"part": "x-own"}]))
        self.assertEqual(self.history(), [{"event": "reused", "project": "plant-alarm", "need": "alarm", "entry": "speaker"}])

    def test_a_pick_of_a_board_the_project_keeps_itself_is_not_a_reuse_of_the_store_either(self):
        (self.project / "boards").mkdir(parents=True)
        (self.project / "boards" / "my-board.json").write_text(json.dumps({"id": "my-board"}))
        _, code = run(["--pick", str(self.project), "board=my-board"])
        self.assertEqual((code, self.picks()["board"], self.history()), (0, [{"board": "my-board"}], []))

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

    def test_a_hold_no_pick_of_the_project_explains_is_released_and_said(self):
        # C-4 (the council on PR #98): a pick rebuilt the project's holds and dropped a hand-given one behind a bare `set … → {}`
        run(["--drawer-set", a_file([{"entry": "speaker", "used_in": {"plant-alarm": 1}}])])
        dry, _ = run(["--pick", str(self.project), "soil=x-soil", "--dry-run"])
        dry_text = self.text(["--pick", str(self.project), "soil=x-soil", "--dry-run"])
        said, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, dry["data"]["released"], said["data"]["released"], self.entry("speaker")["used_in"]),
                         (0, [{"entry": "speaker", "was": 1, "now": 0}], [{"entry": "speaker", "was": 1, "now": 0}], {}))
        self.assertIn("\n  would release: speaker — no pick of this project explains it\n", dry_text)

    def test_a_re_pick_says_what_it_releases(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        self.assertIn("\n  released: probe — no pick of this project explains it\n", self.text(["--pick", str(self.project), "soil=x-other"]))

    def test_part_of_a_hold_released_says_how_many_of_how_many(self):
        run(["--drawer-set", a_file([{"entry": "speaker", "used_in": {"plant-alarm": 2}}])])
        said = self.text(["--pick", str(self.project), "alarm=speaker"])
        self.assertIn("\n  released 1 of 2: speaker — no pick of this project explains it\n", said)

    def test_a_pick_that_keeps_every_hold_releases_nothing(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        said, _ = run(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"])
        self.assertEqual(said["data"]["released"], [])
        self.assertNotIn("release", self.text(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"]))

    @board_missing("physical.header")
    def test_a_board_that_stops_at_the_footprint_is_picked_saying_so_and_one_that_builds_is_not(self):
        # F12 (C-7): the XIAO was picked without a word, and the person learnt it when the build stopped; warned, never refused
        said = self.text(["--pick", str(self.project), "board=xiao-esp32-c6"])
        self.assertIn("  board xiao-esp32-c6: stops at the footprint stage (P121): its board file lacks physical.header",
                      said.splitlines())
        said, _ = run(["--pick", str(self.project), "board=xiao-esp32-c6", "--dry-run"])
        self.assertIn({"subject": "board xiao-esp32-c6", "sentence": "stops at the footprint stage (P121): its board file lacks physical.header"},
                      said["notes"])  # P411: the colon of the line must not cut the note at the wrong place
        self.assertEqual(self.picks()["board"], [{"board": "xiao-esp32-c6"}])
        run(["--drawer-set", a_file([{"entry": "board", "used_in": {}}])])
        self.assertNotIn("stops at", self.text(["--pick", str(self.project), "board=firebeetle2-esp32s3"]))

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

    # --- what the store keeps of a pick, and what the pick says it wrote (C-17; the PO, 2026-10-08) ---

    def test_a_reason_is_kept_without_its_urls_and_prices(self):
        # §5.7 (W21): the history keeps the person's reasons, never a URL or a price — and a reason kept both, as typed
        for given, kept in (("a gas sensor does not sense soil — https://shop.example/x", "a gas sensor does not sense soil"),
                            ("too dear: 12 EUR", "too dear"),
                            ("costs €12,50, see www.shop.example/a?b=1", "costs see"),
                            ("300 Kč and $5 more than the other", "and more than the other"),
                            ("CZK 300 is too much", "is too much"),
                            # F14: any scheme, a bare host with a path, the bracket around a URL; a currency glued to the
                            # number on either side, thousands spaced (a space, a no-break space), a Czech ,- with or without Kč
                            ("ftp://example.com/file", ""),
                            ("see example.com/item/123 instead", "see instead"),
                            ("cheaper on aliexpress.com/item/1005006.html", "cheaper on"),
                            ("see <https://example.com/x>", "see"),
                            ("see (https://example.com/x) instead", "see instead"),
                            ("too dear at 12EUR", "too dear at"),
                            ("300Kč at the shop", "at the shop"),
                            ("costs 300Kc here", "costs here"),
                            ("1 200 Kč", ""),
                            ("1\u00a0200 Kč", ""),
                            ("costs 300,- Kč here", "costs here"),
                            ("costs 300,- here", "costs here"),
                            # the controller's cases, as given: a symbol may be glued in front, a code only after
                            ("12EUR", ""), ("300Kč", ""), ("€12", ""), ("$5", ""), ("EUR 12", ""),
                            ("aliexpress.com/item/1005006.html", ""), ("www.x.cz/y", ""),
                            # the re-check: a URL takes a closing bracket only with its opener, so the text's own stay
                            # balanced; a bracketed run inside an address goes with it
                            ("(see aliexpress.com/x)", "(see)"), ("a (b aliexpress.com/x) c", "a (b) c"),
                            ("see https://en.wikipedia.org/wiki/Foo_(bar) there", "see there")):
            with self.subTest(given=given):
                self.assertEqual(text_guards.kept_reason(given), (kept, True))
        for given in ("a 3 W speaker is loud enough", "it senses distance, not moisture.", "2 of them are dead",
                      "it runs at 3.3/5V only", "board v1.1/v1.2 differ",
                      # a currency code glued before a number is a part number, not a price; a bare host is a URL only
                      # when its last label is a common TLD — png is a file's
                      "the KC868 has no free pins", "not the GBP10 variant", "pinout.png/page 2",
                      "EUR12 is too much", "USD5", "kč300"):
            with self.subTest(given=given):
                self.assertEqual(text_guards.kept_reason(given), (given, False))

    def test_a_reason_s_url_and_price_never_reach_the_history_and_the_pick_says_so(self):
        reasons = a_file([{"need": "soil", "id": "x-other", "why": "a gas sensor does not sense soil — 12 EUR at https://shop.example/x",
                           "by": "person"}])
        said = self.text(["--pick", str(self.project), "soil=x-soil", "--passed-over", reasons])
        self.assertEqual([event["why"] for event in self.history() if event["event"] == "passed_over"], ["a gas sensor does not sense soil — at"])
        self.assertIn("\n  x-other: the reason is kept without the URL or price in it — your history keeps words, never a URL or a price\n",
                      said)

    def test_a_reason_is_said_noted_and_a_second_for_the_same_part_already_noted(self):
        first = a_file([{"need": "soil", "id": "x-other", "why": "a gas sensor does not sense soil", "by": "person"}])
        self.assertIn("\n  would note why you passed over x-other (soil)\n",
                      self.text(["--pick", str(self.project), "soil=x-soil", "--passed-over", first, "--dry-run"]))
        self.assertIn("\n  noted why you passed over x-other (soil)\n", self.text(["--pick", str(self.project), "soil=x-soil", "--passed-over", first]))
        second = a_file([{"need": "soil", "id": "x-other", "why": "the wrong sensor altogether", "by": "person"}])
        said = self.text(["--pick", str(self.project), "soil=x-soil", "--passed-over", second])
        self.assertIn("\n  already noted, not changed: why you passed over x-other (soil) — your history keeps the first reason\n", said)
        self.assertEqual([event["why"] for event in self.history() if event["event"] == "passed_over"], ["a gas sensor does not sense soil"])

    def test_a_pick_that_writes_a_drawer_entry_s_key_into_needs_json_says_so_once(self):
        dry = self.text(["--pick", str(self.project), "alarm=speaker", "--dry-run"])
        first = self.text(["--pick", str(self.project), "alarm=speaker"])
        again = self.text(["--pick", str(self.project), "alarm=speaker", "soil=x-soil"])
        self.assertIn("\n  needs.json would name your drawer entry speaker — a key made from your label, in the project's own file\n", dry)
        self.assertIn("\n  needs.json names your drawer entry speaker — a key made from your label, in the project's own file\n", first)
        self.assertNotIn("needs.json", again)

    def test_a_pick_says_it_listed_the_project_and_what_it_wrote_to_the_history(self):
        dry = self.text(["--pick", str(self.project), "soil=x-soil", "input=tactile-button", "--dry-run"])
        first = self.text(["--pick", str(self.project), "soil=x-soil", "input=tactile-button"])
        again = self.text(["--pick", str(self.project), "soil=x-soil", "input=tactile-button"])
        self.assertIn("\n  would list plant-alarm on your projects\n  would write to your history: 2 reused\n", dry)
        self.assertIn("\n  listed plant-alarm on your projects\n  wrote to your history: 2 reused\n", first)
        self.assertNotIn("projects", again)
        self.assertNotIn("history", again)

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
            "  mp3: maybe owned — check the drawer first",
            "  listed plant-alarm on your projects",
            "  wrote to your history: 2 reused",
            "  needs.json names your drawer entry mp3 — a key made from your label, in the project's own file", self.next_line(), ""]))

    def test_a_refused_pick_says_its_notes_between_what_it_would_have_changed_and_what_it_refused(self):
        self.assertEqual(self.text(["--pick", str(self.project), "alarm=mp3", "board=firebeetle2-esp32s3"]), "\n".join([
            '  not written: set mp3: used_in null → {"plant-alarm": 1}',
            "  mp3: maybe owned — check the drawer first",
            "  refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here",
            '  fix for firebeetle2-esp32s3: free it — a file holding [{"entry": "board", "used_in": …}] without smartbin-local, given to '
            "--drawer-set <file> after a dry run — or pick another", ""]))  # P124 (#58): its fix, which the text left out

    def test_a_pick_s_notes_reach_the_envelope_as_they_reach_the_text(self):
        said, code = run(["--pick", str(self.project), "soil=x-soil", "alarm=mp3"])
        self.assertEqual(code, 0)
        self.assertIn({"subject": "mp3", "sentence": "maybe owned — check the drawer first"}, said["notes"])

    def test_a_refused_pick_prints_its_fix_in_text(self):
        said, _ = run(["--pick", str(self.project), "alarm=mp3", "board=firebeetle2-esp32s3", "--dry-run"])
        text = self.text(["--pick", str(self.project), "alarm=mp3", "board=firebeetle2-esp32s3"])
        self.assertIn(said["problems"][0]["fix"], text)

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

    def test_a_history_a_hand_edit_left_ending_in_a_blank_line_does_not_stop_a_pick(self):
        (self.home / "history.jsonl").write_text('{"event":"reused","project":"irrigation","need":"water","part":"x-valve"}\n\n')
        _, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, self.picks()["soil"]), (0, [{"part": "x-soil"}]))
        self.assertEqual(json.loads((self.home / "history.jsonl").read_text().splitlines()[-1]),
                         {"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"})

    def test_asking_for_a_plan_with_no_reasons_is_asking_for_no_reasons(self):
        _, _, events, _, problems = needs.plan_pick(self.project, [("soil", "x-soil")])
        self.assertEqual((problems, events), ([], [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"}]))

    def test_a_plan_given_a_drawer_plans_on_that_drawer_and_not_on_the_store_s(self):
        """P1124: `entries=` is the drawer the plan reads (the move's drawer after the other project's release)."""
        given = dict(drawer.entries(), probe=dict(drawer.entries()["probe"], count=1, used_in={"other-gadget": 1}))
        _, _, _, _, problems = needs.plan_pick(self.project, [("soil", "x-soil")], entries=given)
        self.assertEqual([problem["subject"] for problem in problems], ["x-soil"])
        _, changes, _, _, problems = needs.plan_pick(self.project, [("soil", "x-soil")])
        self.assertEqual((problems, [change["entry"] for change in changes]), ([], ["probe"]))

    def test_a_pick_answers_with_the_project_what_it_picked_what_it_reserved_and_that_it_was_written(self):
        said, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, said["data"]), (0, {"project": "plant-alarm", "picks": [{"need": "soil", "pick": [{"part": "x-soil"}]}],
                                                     "reserved": [{"entry": "probe", "used_in": {"plant-alarm": 1}}], "released": [],
                                                     "written": True, "adopted": []}))

    def test_a_dry_run_says_what_it_would_do_and_writes_nothing(self):
        said, code = run(["--pick", str(self.project), "soil=x-soil", "--dry-run"])
        self.assertEqual((code, said["data"]["written"], said["data"]["reserved"]),
                         (0, False, [{"entry": "probe", "used_in": {"plant-alarm": 1}}]))
        self.assertEqual((self.picks()["soil"], self.entry("probe").get("used_in"), self.history()), (None, None, []))
        self.assertFalse((self.home / "projects.json").exists())
        self.assertEqual(self.text(["--pick", str(self.project), "soil=x-soil", "--dry-run"]),
                         '  would set probe: used_in null → {"plant-alarm": 1}\n  soil: x-soil\n'
                         "  would list plant-alarm on your projects\n  would write to your history: 1 reused\n")

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
        # a part, not the board: a project has one board however many needs pick it (P387)
        (self.home / "drawer" / "silent.json").write_text(json.dumps({"schema": 1, "label": "a mystery sensor", "count": 2, "is": {"part": "x-silent"},
                                                                     "used_in": {"smartbin-local": 1, "plant-alarm": 1}}))
        run(["--needs-set", str(self.project), a_file([{"id": "spare", "does": "sense", "what": "x"}])])
        said, code = run(["--pick", str(self.project), "soil=x-silent", "spare=x-silent"])
        self.assertEqual((code, said["problems"][0]["sentence"], said["problems"][0]["fix"]), (
            1, "2 owned, held by smartbin-local — 2 picked here",
            'free it — a file holding [{"entry": "silent", "used_in": …}] without smartbin-local, given to --drawer-set <file> after '
            "a dry run — or pick another"))

    def test_more_picked_than_is_owned_is_refused_though_nobody_else_holds_any(self):
        run(["--needs-set", str(self.project), a_file([{"id": "chime", "does": "sound", "what": "alarm"}])])
        said, code = run(["--pick", str(self.project), "alarm=mp3", "chime=mp3"])
        self.assertEqual((code, said["problems"][0]["sentence"], said["problems"][0]["fix"]), (
            1, "1 owned — 2 picked here",
            'pick fewer, or another — or, if you own more, a file holding [{"entry": "mp3", "count": …}], given to --drawer-set '
            "<file> after a dry run"))

    def test_a_drawer_entry_of_a_record_picked_by_its_key_is_a_pick_of_that_record(self):
        said = self.text(["--pick", str(self.project), "soil=probe", "alarm=old-amp"])
        self.assertEqual((self.picks()["soil"], self.picks()["alarm"], self.entry("probe")["used_in"], self.entry("old-amp")["used_in"]),
                         ([{"part": "x-soil"}], [{"entry": "old-amp"}], {"plant-alarm": 1}, {"plant-alarm": 1}))
        self.assertEqual(self.history(), [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"},
                                          {"event": "reused", "project": "plant-alarm", "need": "alarm", "entry": "old-amp"}])
        self.assertEqual(said, "\n".join([
            '  set old-amp: used_in null → {"plant-alarm": 1}',
            '  set probe: used_in null → {"plant-alarm": 1}',
            "  soil: x-soil",
            "  alarm: old-amp",
            "  probe: the drawer entry of x-soil — picked as that record",
            "  listed plant-alarm on your projects",
            "  wrote to your history: 2 reused",
            "  needs.json names your drawer entry old-amp — a key made from your label, in the project's own file", self.next_line(), ""]))

    def test_a_drawer_entry_of_a_board_picked_by_its_key_is_a_pick_of_that_board(self):
        run(["--drawer-set", a_file([{"entry": "board", "used_in": {}}])])
        _, code = run(["--pick", str(self.project), "board=board"])
        self.assertEqual((code, self.picks()["board"], self.entry("board")["used_in"]),
                         (0, [{"board": "firebeetle2-esp32s3"}], {"plant-alarm": 1}))

    def test_a_board_picked_from_the_drawer_with_no_record_is_reserved_and_said_to_need_a_board_file(self):
        (self.home / "drawer" / "beetle-c6.json").write_text(json.dumps({"schema": 1, "label": "Beetle ESP32 C6 Mini", "count": 3}))
        self.assertEqual(self.text(["--pick", str(self.project), "board=beetle-c6", "alarm=speaker"]), "\n".join([
            '  set beetle-c6: used_in null → {"plant-alarm": 1}',
            '  set speaker: used_in null → {"plant-alarm": 1}',
            "  alarm: speaker",
            "  board: beetle-c6",
            "  beetle-c6: a board needs a board file — a record in boards/ — before spark can build with it",
            "  listed plant-alarm on your projects",
            "  wrote to your history: 2 reused",
            "  needs.json names your drawer entries beetle-c6, speaker — a key made from your label, in the project's own file", self.next_line(), ""]))

    def a_needs_file_from_before(self, need_id, pick):
        """The needs file as one written before a pick of an entry key became its record's — or edited by hand: `need_id`
        picks `pick`. A pick names no other need, so what such a file holds stays, and is reserved as it says."""
        needs_file = self.project / ".spark" / "needs.json"
        written = json.loads(needs_file.read_text())
        needs_file.write_text(json.dumps(dict(written, needs=[dict(need, pick=[pick]) if need["id"] == need_id else need
                                                              for need in written["needs"]])))

    def test_a_board_picked_by_its_entry_s_key_before_is_not_said_to_need_a_board_file(self):
        self.a_needs_file_from_before("board", {"entry": "board"})
        run(["--drawer-set", a_file([{"entry": "board", "used_in": {}}])])
        said = self.text(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((self.entry("board")["used_in"], "board file" in said), ({"plant-alarm": 1}, False))

    def test_a_pick_kept_as_the_drawer_entry_of_a_record_shares_one_stock_with_a_pick_of_that_record(self):
        self.a_stock_pointed_at_twice(1)
        self.a_needs_file_from_before("deep", {"entry": "solo"})
        said, code = run(["--pick", str(self.project), "soil=x-solo"])
        self.assertEqual((said["status"], code, said["problems"][0]["sentence"]), ("problems", 1, "1 owned — 2 picked here"))
        self.assertEqual((self.picks()["soil"], self.entry("solo").get("used_in"), self.history()), (None, None, []))

    def test_a_pick_kept_as_the_drawer_entry_of_a_record_and_a_pick_of_that_record_take_two_when_two_are_owned(self):
        self.a_stock_pointed_at_twice(2)
        self.a_needs_file_from_before("deep", {"entry": "solo"})
        _, code = run(["--pick", str(self.project), "soil=x-solo"])
        self.assertEqual((code, self.picks()["soil"], self.picks()["deep"], self.entry("solo")["used_in"]),
                         (0, [{"part": "x-solo"}], [{"entry": "solo"}], {"plant-alarm": 2}))

    def test_a_pick_kept_as_one_entry_of_a_record_takes_that_entry_before_the_record_takes_another(self):
        (self.home / "drawer" / "board.json").unlink()
        for key in ("a-board", "b-board"):
            (self.home / "drawer" / (key + ".json")).write_text(json.dumps({"schema": 1, "label": key, "count": 1, "is": {"board": "firebeetle2-esp32s3"}}))
        run(["--needs-set", str(self.project), a_file([{"id": "spare", "does": "compute", "what": "microcontroller"}])])
        self.a_needs_file_from_before("spare", {"entry": "a-board"})
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((code, said["problems"]), (0, []))
        self.assertEqual((self.entry("a-board")["used_in"], self.entry("b-board")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))

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
                         (0, [{"part": "x-solo"}], [{"part": "x-solo"}], {"plant-alarm": 2}))

    def test_one_stock_picked_both_ways_never_goes_past_what_another_project_holds(self):
        self.a_stock_pointed_at_twice(2, {"smartbin-local": 1})
        said, code = run(["--pick", str(self.project), "soil=x-solo", "deep=solo"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual(said["problems"][0]["sentence"], "2 owned, held by smartbin-local — 2 picked here")
        self.assertEqual((self.picks()["soil"], self.entry("solo")["used_in"], self.history()), (None, {"smartbin-local": 1}, []))

    def test_a_record_owned_over_two_entries_serves_a_pick_of_the_first_by_key_and_a_pick_of_the_record(self):
        (self.home / "drawer" / "silent.json").unlink()  # a part, not the board: one board serves however many needs (P387)
        for key in ("a-silent", "b-silent"):
            (self.home / "drawer" / (key + ".json")).write_text(json.dumps({"schema": 1, "label": key, "count": 1, "is": {"part": "x-silent"}}))
        run(["--needs-set", str(self.project), a_file([{"id": "spare", "does": "sense", "what": "x"}])])
        said, code = run(["--pick", str(self.project), "soil=x-silent", "spare=a-silent"])
        self.assertEqual((code, said["problems"]), (0, []))
        self.assertEqual((self.entry("a-silent")["used_in"], self.entry("b-silent")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))

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

    def test_a_key_given_and_the_record_it_is_must_both_be_plain_and_nothing_is_written(self):
        # the key given is checked, and so is the id written: a needs file holding a key that is not plain cannot be read again
        (self.project / "parts").mkdir()
        (self.project / "parts" / "Lone_Sensor.json").write_text(json.dumps({"schema": 1, "id": "Lone_Sensor", "name": "A lone sensor", "kind": "sensor"}))
        (self.home / "drawer" / "lone.json").write_text(json.dumps({"schema": 1, "label": "a lone sensor", "count": 1, "is": {"part": "Lone_Sensor"}}))
        (self.home / "drawer" / "Old_Probe.json").write_text(json.dumps({"schema": 1, "label": "an old probe", "count": 1, "is": {"part": "x-soil"}}))
        for given, named in (("lone", "'Lone_Sensor'"), ("Old_Probe", "'Old_Probe'")):
            with self.subTest(given=given):
                said, code = run(["--pick", str(self.project), "soil=" + given])
                self.assertEqual((said["status"], code), ("could-not-run", 2))
                self.assertIn(named + " is not a plain key", said["unchecked"][0]["sentence"])
                self.assertEqual((self.picks()["soil"], self.entry("lone").get("used_in"), self.entry("probe").get("used_in"),
                                  self.history()), (None, None, None, []))
                self.assertFalse((self.home / "projects.json").exists())

    def test_an_id_nothing_has_is_named_even_when_it_is_not_plain(self):
        said, code = run(["--pick", str(self.project), "soil=No_Such_Part"])
        self.assertEqual((said["status"], code, said["problems"][0]["sentence"]),
                         ("problems", 1, "no record or drawer entry called No_Such_Part — --match lists the candidates"))

    def test_a_store_that_refuses_the_history_leaves_the_project_file_untouched_and_a_retry_finishes_the_pick(self):
        needs_file = self.project / ".spark" / "needs.json"
        before, real = needs_file.read_text(), store._make_ready

        def refuse_the_history(name, target):
            if name == "history":
                raise store.StoreError("%s would be inside the git work tree — what you own stays out of every repository" % target, code="store_in_repository")
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
                              ("a reason that is only a URL and a price", [dict(good, why="https://shop.example/x 12 EUR")]),
                              ("a price with its thousands spaced", [dict(good, why="1 200 Kč")]),
                              ("a reason with no letter left", [dict(good, why="#3: $5")]),
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


# --- MVP --- P990: --match offers a board for a need of a radio of its chip
class TheBoardsChipRadiosAreOfferedTest(unittest.TestCase):
    """P990: the need communicate / wifi finds both C6 boards and the library's S3. The need communicate / zigbee finds the
    C6 boards, and the S3 stays a candidate whose words do not match. P1013: the Wi-Fi words show the chip's band."""

    C6 = ["onboard 802.15.4 radio (Thread, Zigbee)", "onboard Bluetooth LE radio (BLE)", "onboard Wi-Fi radio (WiFi; 2.4 GHz only)"]
    S3 = ["onboard Bluetooth LE radio (BLE)", "onboard Wi-Fi radio (WiFi; 2.4 GHz only)"]

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "radio-project"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        run(["--needs-set", str(self.project), a_file([{"id": "wifi", "does": "communicate", "what": "wifi"},
                                                        {"id": "mesh", "does": "communicate", "what": "zigbee"}])])
        (self.project / "boards").mkdir()
        shutil.copy(ROOT / "boards" / "xiao-esp32-c6.json", self.project / "boards")
        shutil.copy(ROOT / "tests" / "data" / "breadboard" / "walk-c6" / "boards" / "firebeetle2-esp32c6.json", self.project / "boards")

    def candidates(self, need_id):
        """The need's candidates by id, each as (what, what_matches, score, why, limits), over every page of --match --json."""
        said, _ = run(["--match", str(self.project)])
        matched = list(said["data"]["needs"])
        while said["truncated"] and said["truncated"]["next"]:
            said, _ = run(["--match", str(self.project), "--from", str(len(matched))])
            matched += said["data"]["needs"]
        need = next(need for need in matched if need["need"] == need_id)
        return {c["id"]: (c["what"], c["what_matches"], c["score"], c["why"], c["limits"]) for c in need["candidates"]}

    def test_a_wifi_need_finds_every_board_whose_chip_has_wifi(self):
        self.assertEqual(self.candidates("wifi"), {
            "firebeetle2-esp32c6": (self.C6, True, 1.0, ["wifi: in functions"], []),
            "xiao-esp32-c6": (self.C6, True, 1.0, ["wifi: in functions"], []),
            "firebeetle2-esp32s3": (self.S3, True, 1.0, ["wifi: in functions"], [])})

    def test_a_zigbee_need_finds_the_c6_boards_and_not_the_s3(self):
        self.assertEqual(self.candidates("mesh"), {
            "firebeetle2-esp32c6": (self.C6, True, 1.0, ["zigbee: in functions"], []),
            "xiao-esp32-c6": (self.C6, True, 1.0, ["zigbee: in functions"], []),
            "firebeetle2-esp32s3": (self.S3, False, 0.0, [], [])})

    def test_the_text_names_the_radios_of_each_board(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        lines = out.getvalue().splitlines()
        self.assertIn("                 xiao-esp32-c6 (project)                        onboard 802.15.4 radio (Thread, Zigbee), "
                      "onboard Bluetooth LE radio (BLE), onboard Wi-Fi radio (WiFi; 2.4 GHz only)", lines)
        self.assertIn("                 firebeetle2-esp32s3 (library)                  onboard Bluetooth LE radio (BLE), "
                      "onboard Wi-Fi radio (WiFi; 2.4 GHz only) [other words]", lines)
        self.assertIn("                 firebeetle2-esp32c6 (project)                  onboard 802.15.4 radio (Thread, Zigbee), "
                      "onboard Bluetooth LE radio (BLE), onboard Wi-Fi radio (WiFi; 2.4 GHz only)", lines)


# --- MVP --- P397: a pick, or --match, that gives a need to a board's own part says what a passed run does not test of it
class TheBoardsLimitsNoteTest(unittest.TestCase):
    """P397: the note of a pick that gives a button, a light or a display to the board, and the same sentences in --match."""

    NEEDS = {"press": {"id": "press", "does": "input", "what": "button"}, "blink": {"id": "blink", "does": "indicate", "what": "light"},
             "show": {"id": "show", "does": "indicate", "what": "display"}, "charge": {"id": "charge", "does": "power", "what": "charger"},
             "joy": {"id": "joy", "does": "input", "what": "joystick"}}
    PINS = '{"pins": {"D0": {"target": "GPIO0"}, "$gpio15": {"target": "GPIO15"}}}'
    NO_PIN = ("the Wokwi definition of xiao-esp32-c6 has no pin on GPIO9, so spark knows no way for a scenario to press it. "
              "Test it on the board.")
    NOT_KEPT = ("not checked: spark's store lacks the Wokwi definition that the board record names, its sha256 differs, or it "
                "does not parse. Test it on the board.")
    NOT_NAMED = "not checked: the board record names no Wokwi definition. Test it on the board."
    DISPLAY = ("spark adds no part to the diagram for the board's own display, so a passed run does not test what it shows. "
               "Test it on the board.")
    OTHER = "The other choice: tactile-button on a header pad, which has a Wokwi model."
    ALL_HELD = "Every other part with a Wokwi model for press is held by another project."
    TDISPLAY = ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json"

    def setUp(self):
        self.home, self.project = a_store_with_a_drawer(), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        run(["--needs-set", str(self.project), a_file(list(self.NEEDS.values()))])
        self.keep_the_xiao(self.PINS)

    def keep_the_xiao(self, text, edit=lambda board: None):
        """The XIAO's record in the project, with the Wokwi definition `text` kept in the scratch store under its sha256."""
        board = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
        board["documents"][board_records.WOKWI_DEFINITION].update(
            sha256=store.keep(text.encode(), "wokwi-test.board.json"), file="wokwi-test.board.json")
        edit(board)
        (self.project / "boards").mkdir(parents=True, exist_ok=True)
        (self.project / "boards" / "xiao-esp32-c6.json").write_text(json.dumps(board))

    def keep_the_t_display(self):
        (self.project / "boards").mkdir(parents=True, exist_ok=True)
        shutil.copy(self.TDISPLAY, self.project / "boards" / "lilygo-t-display.json")

    def simulate(self, part_id, simulation):
        """The project's record of `part_id` with this `simulation` table."""
        path = self.project / "parts" / (part_id + ".json")
        path.write_text(json.dumps(dict(json.loads(path.read_text()), simulation=simulation)))

    def own_skipped_screen(self):
        """A display part the person owns, the dfr0664 record as x-screen, whose record skips the simulation (P778)."""
        self.own("screens", "x-screen", function=[{"does": "indicate", "what": "display"}], simulated=False)
        record = json.loads((ROOT / "tests" / "data" / "parts" / "dfr0664-tft-2in.json").read_text())
        (self.project / "parts" / "x-screen.json").write_text(json.dumps(dict(record, id="x-screen", name="A screen x-screen",
                                                                             function=[{"does": "indicate", "what": "display"}])))
        self.simulate("x-screen", {"skip": "no glass in Wokwi"})

    def own(self, entry, part_id, simulated=True, function=None, **fields):
        """A button part (or the `function` given) in the project, owned in the drawer under `entry`, with a Wokwi stand-in unless `simulated` is False."""
        record = {"schema": 1, "id": part_id, "name": ("A part " if function else "A button ") + part_id, "kind": "button"}
        record.update({"function": function} if function else {})
        record.update({"simulation": {"wokwi": {"part": "wokwi-pushbutton", "pins": {"A": "1.l", "B": "2.l"}, "stand_in": "x"}}} if simulated else {})
        (self.project / "parts").mkdir(parents=True, exist_ok=True)
        (self.project / "parts" / (part_id + ".json")).write_text(json.dumps(record))
        (self.home / "drawer" / (entry + ".json")).write_text(json.dumps(dict({"schema": 1, "label": entry, "count": 2, "is": {"part": part_id}},
                                                                              **fields)))

    def hold_the_bag_of_buttons(self):
        """All of the person's tactile buttons are held by another project."""
        (self.home / "drawer" / "buttons.json").write_text(json.dumps({"schema": 1, "label": "a bag of buttons", "count": 3,
                                                                       "is": {"part": "tactile-button"}, "used_in": {"smartbin-local": 3}}))

    def pick(self, *picks):
        """A dry-run pick's notes about a board, as {subject: sentence}."""
        said, code = run(["--pick", str(self.project)] + list(picks) + ["--dry-run"])
        self.assertEqual((code, said["status"]), (0, "ok"), said)
        return {note["subject"]: note["sentence"] for note in said["notes"] if note["subject"] and note["subject"].startswith("board ") and " for " in note["subject"]}

    def matched(self, need_id, board="xiao-esp32-c6"):
        """The board's candidate for one need, matched alone, as --match --json says it."""
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [self.NEEDS[need_id]]}))
        said, _ = run(["--match", str(self.project)])
        return next(c for c in said["data"]["needs"][0]["candidates"] if c["id"] == board)

    def test_the_pick_prints_the_bench_and_the_first_candidate_with_free_stock(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--pick", str(self.project), "press=xiao-esp32-c6", "--dry-run"])
        self.assertIn("  board xiao-esp32-c6 for press: " + self.NO_PIN + " " + self.OTHER, out.getvalue().splitlines())

    def test_a_pin_on_the_buttons_gpio_gives_no_note_and_no_pin_gives_one(self):
        self.assertEqual(list(self.pick("press=xiao-esp32-c6")), ["board xiao-esp32-c6 for press"])
        self.keep_the_xiao('{"pins": {"D9": {"target": "GPIO9"}, "$gpio15": {"target": "GPIO15"}}}')
        self.assertEqual((self.pick("press=xiao-esp32-c6"), self.matched("press")["limits"]), ({}, []))

    def test_an_led_need_on_the_xiao_has_no_note_while_its_gpio_has_a_pin_and_one_when_it_has_none(self):
        self.assertEqual((self.pick("blink=xiao-esp32-c6"), self.matched("blink")["limits"]), ({}, []))
        self.keep_the_xiao(self.PINS, lambda board: board["pin_roles"]["onboard_led"].update(gpio=[3]))
        sentence = ("the Wokwi definition of xiao-esp32-c6 has no pin on GPIO3, so spark knows no way for a scenario to read it. "
                    "Test it on the board.")
        # the FireBeetle's LED is a board, not a part to wire to a pad: no choice is named, and none is said to be held
        self.assertEqual(self.pick("blink=xiao-esp32-c6"), {"board xiao-esp32-c6 for blink": sentence})
        self.assertEqual(self.matched("blink")["limits"], [sentence])

    def test_the_picked_board_s_sentence_is_the_builds_sentence(self):
        board = json.loads((self.project / "boards" / "xiao-esp32-c6.json").read_text())
        built = [sentence for _, sentence in board_records.onboard_limits(board)]
        self.assertEqual(built, [self.NO_PIN])
        self.assertTrue(self.pick("press=xiao-esp32-c6")["board xiao-esp32-c6 for press"].startswith(built[0]))

    def test_the_other_choice_is_the_first_owned_part_with_free_stock_that_the_simulation_can_reach(self):
        self.hold_the_bag_of_buttons()
        self.own("seen", "x-seen")
        self.assertEqual(self.pick("press=xiao-esp32-c6"),
                         {"board xiao-esp32-c6 for press": self.NO_PIN + " " + self.OTHER.replace("tactile-button", "x-seen")})

    def test_a_part_with_no_wokwi_model_is_not_the_other_choice_and_is_not_counted_as_held_or_free(self):
        self.hold_the_bag_of_buttons()
        self.own("unseen", "x-unseen", simulated=False)  # free, matches, no Wokwi model: the sentence says "with a Wokwi model", so it stays true
        self.assertEqual(self.pick("press=xiao-esp32-c6"), {"board xiao-esp32-c6 for press": self.NO_PIN + " " + self.ALL_HELD})

    def test_a_free_part_that_matches_no_word_of_the_need_is_never_the_other_choice(self):
        self.hold_the_bag_of_buttons()
        self.own("stick", "x-stick", function=[{"does": "input", "what": "joystick"}])
        self.assertEqual(self.matched("press", "x-stick")["score"], 0.0)
        self.assertEqual(self.pick("press=xiao-esp32-c6"), {"board xiao-esp32-c6 for press": self.NO_PIN + " " + self.ALL_HELD})
        (self.home / "drawer" / "buttons.json").unlink()
        self.assertEqual(self.pick("press=xiao-esp32-c6"), {"board xiao-esp32-c6 for press": self.NO_PIN})

    def test_every_owned_candidate_held_by_another_project_is_said_so_and_none_is_named(self):
        self.hold_the_bag_of_buttons()
        self.assertEqual(self.pick("press=xiao-esp32-c6"), {"board xiao-esp32-c6 for press": self.NO_PIN + " " + self.ALL_HELD})
        self.own("spare", "x-spare")
        (self.home / "drawer" / "spare.json").unlink()  # a part to get: a candidate the person does not own
        self.assertEqual(self.pick("press=xiao-esp32-c6"), {"board xiao-esp32-c6 for press": self.NO_PIN + " " + self.ALL_HELD})

    def test_a_part_to_get_is_never_the_other_choice_and_nothing_owned_says_nothing_of_a_choice(self):
        for entry in ("buttons", "board"):
            (self.home / "drawer" / (entry + ".json")).unlink()
        self.assertEqual(self.pick("press=xiao-esp32-c6"), {"board xiao-esp32-c6 for press": self.NO_PIN})

    def test_a_footprint_stop_is_said_before_the_note_of_the_button(self):
        self.keep_the_xiao(self.PINS, lambda board: board["physical"].pop("header"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--pick", str(self.project), "press=xiao-esp32-c6", "--dry-run"])
        self.assertEqual([line for line in out.getvalue().splitlines() if line.startswith("  board ")],
                         ["  board xiao-esp32-c6: stops at the footprint stage (P121): its board file lacks physical.header",
                          "  board xiao-esp32-c6 for press: " + self.NO_PIN + " " + self.OTHER])

    def test_a_board_whose_definition_is_not_kept_says_not_checked_then_the_bench_and_no_other_choice(self):
        (self.project / "boards" / "xiao-esp32-c6.json").unlink()  # the library's XIAO: its definition is not in this store
        said, _ = run(["--pick", str(self.project), "press=xiao-esp32-c6", "--dry-run"])
        note = next(note for note in said["notes"] if note["subject"] == "board xiao-esp32-c6 for press")
        self.assertEqual(note, {"subject": "board xiao-esp32-c6 for press", "sentence": self.NOT_KEPT})
        self.assertTrue(note["sentence"].startswith("not checked: spark's store"), "the subject ends at the first colon, so the sentence stays whole")

    def test_a_board_that_names_no_definition_says_that_and_the_bench(self):
        self.keep_the_t_display()
        self.assertEqual(self.pick("press=lilygo-t-display"), {"board lilygo-t-display for press": self.NOT_NAMED})

    def test_a_display_need_gets_the_display_sentence_alone_and_a_power_need_gets_none(self):
        self.keep_the_t_display()
        self.own("screens", "x-screen", function=[{"does": "indicate", "what": "display"}])
        self.assertEqual(self.pick("show=lilygo-t-display", "charge=lilygo-t-display"),
                         {"board lilygo-t-display for show": self.DISPLAY})
        self.assertEqual(self.matched("show", "lilygo-t-display")["limits"], [self.DISPLAY])
        self.assertEqual(self.matched("charge", "lilygo-t-display")["limits"], [])

    STAND_IN_BUTTON = "Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled"
    WIRED_BUTTON = ("the Wokwi stand-in has no button on GPIO47, so spark wires Wokwi's pushbutton to GPIO47 in its place: a "
                    "scenario presses that part, not the board's own button. Test it on the board.")

    def test_a_board_admitted_by_the_verb_alone_has_no_limits_and_a_part_has_its_record_s(self):
        # P778: a part's limits are its record's own words, as the build prints them; a real Wokwi part has none
        self.assertEqual(self.matched("joy")["limits"], [])
        self.assertEqual(self.matched("press", "tactile-button")["limits"], [self.STAND_IN_BUTTON])
        self.assertEqual(self.matched("press")["limits"], [self.NO_PIN])
        self.own_skipped_screen()
        self.own("real", "x-real")
        self.simulate("x-real", {"wokwi": {"part": "wokwi-pushbutton", "pins": {"A": "1.l", "B": "2.l"}}})
        self.assertEqual(self.matched("show", "x-screen")["limits"], ["not simulated at all: no glass in Wokwi"])
        self.assertEqual(self.matched("press", "x-real")["limits"], [])

    def test_the_firebeetle_s_button_is_the_wired_stand_in_in_the_pick_as_in_the_build(self):
        # P778 (walk 4 row 10): the pick says what the board-only build says, from `onboard_parts.limits_of_board`
        self.assertEqual(self.WIRED_BUTTON, onboard_parts.ONBOARD_PARTS[board_records.ONBOARD_BUTTON].wired % {"gpio": 47})
        self.assertEqual(self.matched("press", "firebeetle2-esp32s3")["limits"], [self.NOT_KEPT, self.WIRED_BUTTON])
        said, _ = run(["--pick", str(self.project), "press=firebeetle2-esp32s3", "--dry-run"])  # the drawer's one is held: the note is said all the same
        self.assertIn({"subject": "board firebeetle2-esp32s3 for press", "sentence": self.NOT_KEPT + " " + self.WIRED_BUTTON}, said["notes"])

    def test_a_picked_part_with_a_skip_gets_a_note_and_a_line_in_the_requirements(self):
        # P778 (walk 4 row 28): the pick and --requirements say the display's skip, in the record's words
        self.own_skipped_screen()
        said, code = run(["--pick", str(self.project), "press=xiao-esp32-c6", "show=x-screen"])
        self.assertEqual(code, 0, said)
        self.assertIn({"subject": "part x-screen for show", "sentence": "not simulated at all: no glass in Wokwi"}, said["notes"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--requirements", str(self.project), "--dry-run"])
        self.assertIn("  part x-screen: not simulated at all: no glass in Wokwi", out.getvalue().splitlines())

    def test_the_text_of_match_shows_each_sentence_on_a_line_under_the_board(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [self.NEEDS["press"]]}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        lines = out.getvalue().splitlines()
        after = lines.index(next(line for line in lines if "xiao-esp32-c6 (project)" in line))
        self.assertEqual(lines[after + 1], "          " + self.NO_PIN)

    def test_a_not_checked_sentence_in_match_is_followed_by_the_bench(self):
        (self.project / "boards" / "xiao-esp32-c6.json").unlink()
        self.assertEqual(self.matched("press")["limits"], [self.NOT_KEPT])

    def test_the_definition_of_a_board_is_read_once_for_every_need_of_a_match_and_of_a_pick(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [self.NEEDS["press"], self.NEEDS["blink"]]}))
        with mock.patch.object(board_records, "read_simulated_part", wraps=board_records.read_simulated_part) as read:
            run(["--match", str(self.project)])
        self.assertEqual(sorted(call.args[0]["id"] for call in read.call_args_list), ["firebeetle2-esp32s3", "xiao-esp32-c6"])
        with mock.patch.object(board_records, "read_simulated_part", wraps=board_records.read_simulated_part) as read:
            run(["--pick", str(self.project), "press=xiao-esp32-c6", "blink=xiao-esp32-c6", "--dry-run"])
        self.assertEqual([call.args[0]["id"] for call in read.call_args_list], ["xiao-esp32-c6"])

    def test_a_need_is_served_by_the_boards_part_of_its_verb_that_shares_any_word_of_the_need(self):
        functions = [{"does": "input", "what": "onboard button", "role": "onboard_button"},
                     {"does": "indicate", "what": "onboard LED light", "role": "onboard_led"},
                     {"does": "indicate", "what": "onboard display screen", "role": "onboard_display"},
                     {"does": "power", "what": "onboard charger"}]
        for does, what, roles in (("input", "press button", ["onboard_button"]), ("input", "input button", ["onboard_button"]),
                                  ("input", "boot button", ["onboard_button"]), ("indicate", "status led", ["onboard_led"]),
                                  ("indicate", "light", ["onboard_led"]), ("indicate", "screen", ["onboard_display"]),
                                  ("input", "joystick", []), ("sense", "button", []), ("power", "charger", [])):
            with self.subTest(need=(does, what)):
                self.assertEqual(needs.serving_roles({"does": does, "what": what}, functions), roles)

    def test_the_sentences_cost_the_page_of_match_what_they_weigh_and_no_need_is_lost(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            dict(self.NEEDS["press"], id="press%d" % number) for number in range(6)]}))
        (self.project / "boards" / "xiao-esp32-c6.json").unlink()
        pages, seen, start = [], [], 0
        while True:
            # P976: word-overlap is the default since the PO's yes (2026-11-21); these weights are same-words' candidates
            said, _ = run(["--match", str(self.project), "--matcher", "same-words"] + (["--from", str(start)] if start else []))
            pages.append(len(json.dumps(said["data"]["needs"])))
            seen += [need["need"] for need in said["data"]["needs"]]
            if not (said["truncated"] and said["truncated"]["next"]):
                break
            start = len(seen)
        self.assertEqual(seen, ["press%d" % number for number in range(6)])
        self.assertEqual(len(pages), 3, "each need weighs a sentence for each board, so a page holds two needs and not three")
        self.assertTrue(all(size <= 3400 for size in pages), pages)
# --- end MVP ---


# --- MVP --- P514: --needs-drop takes a need and its pick out of the needs file and releases the holds only that pick explained
class TheNeedsDropTest(unittest.TestCase):
    """P514 (#710): `--needs-drop PROJECT NEED`, a core Operation (spark/idea/drop_need.py) behind parts.py."""

    def setUp(self):
        self.home, self.project = a_store_with_a_drawer(), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "sound", "what": "alarm"},
            {"id": "input", "does": "input", "what": "button"}])])
        run(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"])

    def entry(self, key):
        return json.loads((self.home / "drawer" / (key + ".json")).read_text())

    def need_ids(self):
        return [need["id"] for need in json.loads((self.project / ".spark" / "needs.json").read_text())["needs"]]

    def picks(self):
        return {need["id"]: need.get("pick") for need in json.loads((self.project / ".spark" / "needs.json").read_text())["needs"]}

    def held_by(self, key):
        said, _ = run(["--drawer"])
        return next(entry["held_by"] for entry in said["data"]["entries"] if entry["entry"] == key)

    def digest(self):
        import hashlib
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for root in (self.home, self.project.parent) for path in sorted(root.rglob("*")) if path.is_file()}

    def test_a_need_dropped_leaves_the_others_in_order_and_releases_the_hold_only_it_explained(self):
        self.assertEqual(self.entry("speaker")["used_in"], {"plant-alarm": 1})
        said, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((said["status"], code), ("ok", 0))
        self.assertEqual((self.need_ids(), self.entry("speaker")["used_in"], self.entry("probe")["used_in"]),
                         (["soil", "input"], {}, {"plant-alarm": 1}))
        self.assertEqual((said["data"]["project"], said["data"]["need"], said["data"]["written"]), ("plant-alarm", "alarm", True))
        self.assertEqual(said["data"]["dropped"], {"id": "alarm", "does": "sound", "what": "alarm", "pick": [{"entry": "speaker"}]})
        self.assertEqual(said["data"]["released"], [{"entry": "speaker", "was": 1, "now": 0}])

    def test_the_dry_run_changes_no_byte_and_says_what_it_would_do(self):
        before = self.digest()
        said, code = run(["--needs-drop", str(self.project), "alarm", "--dry-run"])
        self.assertEqual((code, said["data"]["written"], said["data"]["released"]), (0, False, [{"entry": "speaker", "was": 1, "now": 0}]))
        self.assertEqual(self.digest(), before)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            parts.main(["--needs-drop", str(self.project), "alarm", "--dry-run"])
        self.assertIn("would drop alarm", out.getvalue())
        self.assertIn("would release 1 of 1: speaker — its need is dropped", out.getvalue())

    def test_another_projects_hold_on_the_same_entry_stays(self):
        run(["--drawer-set", a_file([{"entry": "speaker", "used_in": {"plant-alarm": 1, "other-gadget": 1}}])])
        self.assertEqual(self.held_by("speaker"), ["other-gadget", "plant-alarm"])
        said, _ = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((self.entry("speaker")["used_in"], self.held_by("speaker")), ({"other-gadget": 1}, ["other-gadget"]))
        self.assertEqual(said["data"]["released"], [{"entry": "speaker", "was": 1, "now": 0}])

    def test_a_hold_only_this_project_has_shows_in_the_drawer_before_and_not_after(self):
        self.assertEqual(self.held_by("speaker"), ["plant-alarm"])
        run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual(self.held_by("speaker"), [])

    def test_a_board_picked_by_two_needs_keeps_its_hold_when_one_is_dropped(self):
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}}))
        run(["--pick", str(self.project), "input=xiao-esp32-c6", "alarm=xiao-esp32-c6"])
        said, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((code, said["data"]["released"], self.entry("xiao")["used_in"]), (0, [], {"plant-alarm": 1}))

    def test_a_need_that_is_not_there_exits_1_naming_the_needs_and_a_second_drop_too(self):
        before = self.digest()
        said, code = run(["--needs-drop", str(self.project), "light"])
        self.assertEqual((said["status"], code, self.digest()), ("problems", 1, before))
        self.assertEqual(said["problems"][0]["subject"], "light")
        self.assertEqual(said["data"], {"project": "plant-alarm", "need": "light", "needs": ["soil", "alarm", "input"],
                                         "dropped": None, "released": [], "written": False})
        self.assertIn("no need called light: it was never there or is already dropped. --needs lists them: soil, alarm, input",
                      said["problems"][0]["sentence"])
        self.assertEqual(said["problems"][0]["fix"], "drop a need that --needs lists")
        run(["--needs-drop", str(self.project), "alarm"])
        again, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((again["status"], code, again["data"]["needs"]), ("problems", 1, ["soil", "input"]))

    def test_a_needs_file_that_is_no_json_exits_2_with_no_crash(self):
        (self.project / ".spark" / "needs.json").write_text("{not json")
        said, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("needs.json", said["unchecked"][0]["sentence"])
        self.assertEqual(said["unchecked"][0]["fix"], "drop the need again once the file is fixed")

    def test_a_project_list_that_is_no_json_exits_2_with_the_fix_of_an_unwritten_drop_and_writes_nothing(self):
        (self.home / "projects.json").write_text("{not json")
        before = self.digest()
        said, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((said["status"], code, said["unchecked"][0]["code"], self.digest()), ("could-not-run", 2, "drop_unwritten", before))
        self.assertIn("the project's name could not be read: ", said["unchecked"][0]["sentence"])
        self.assertEqual(said["unchecked"][0]["fix"], UNWRITTEN_FIX)

    def test_requirements_that_still_list_the_dropped_part_get_a_note_that_says_who_runs_what(self):
        (self.project / "requirements.json").write_text(json.dumps({"parts": [{"part": "x-soil"}]}))
        said, _ = run(["--needs-drop", str(self.project), "soil"])
        self.assertEqual([note["sentence"] for note in said["notes"]],
                         ["requirements.json still lists x-soil: run parts.py --requirements %s or edit the file, then build. "
                          "If the firmware imported its signal, run check_firmware.py." % self.project])
        elsewhere, _ = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual(elsewhere["notes"], [])

    def test_a_drawer_that_refuses_the_write_leaves_the_needs_file_as_it_was_so_a_retry_finishes(self):
        class FullDrawer:
            entries = staticmethod(drawer.entries)

            @staticmethod
            def apply(changes):
                raise OSError("disk full")

        result = run_operation(DropNeed(drawer_store=FullDrawer), {"project": self.project, "need": "alarm", "dry_run": False},
                               build_outside=lambda effects: None)
        self.assertEqual((result.status(), self.need_ids()), ("could-not-run", ["soil", "alarm", "input"]))
        run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((self.need_ids(), self.entry("speaker")["used_in"]), (["soil", "input"], {}))

    def test_a_hold_given_by_hand_that_no_pick_explains_stays_when_an_unrelated_need_is_dropped(self):
        run(["--drawer-set", a_file([{"entry": "probe", "used_in": {"plant-alarm": 1}}, {"entry": "speaker", "used_in": {"plant-alarm": 1}}])])
        (self.home / "drawer" / "extra.json").write_text(json.dumps({"schema": 1, "label": "Extra", "count": 2, "used_in": {"plant-alarm": 1}}))
        said, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((code, said["data"]["released"], self.entry("extra")["used_in"]), (0, [{"entry": "speaker", "was": 1, "now": 0}], {"plant-alarm": 1}))

    def test_a_pick_that_stays_keeps_its_hold_when_another_project_over_holds_the_entry(self):
        run(["--drawer-set", a_file([{"entry": "probe", "used_in": {"plant-alarm": 1, "other-gadget": 8}}])])
        before = self.entry("probe")["used_in"]
        said, code = run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual((code, said["data"]["released"], self.entry("probe")["used_in"]), (0, [{"entry": "speaker", "was": 1, "now": 0}], before))

    def test_a_need_with_only_an_id_drops_cleanly_dry_run_and_real(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "b"}]}))
        said, code = run(["--needs-drop", str(self.project), "b", "--dry-run"])
        self.assertEqual((said["status"], code, said["data"]["dropped"]), ("ok", 0, {"id": "b"}))
        said, code = run(["--needs-drop", str(self.project), "b"])
        self.assertEqual((said["status"], code, self.need_ids()), ("ok", 0, []))

    def test_a_needs_file_that_refuses_the_write_after_the_drawer_is_written_exits_2_with_a_code_and_a_retry_finishes(self):
        class FullNeeds:
            def __getattr__(self, attr):
                return getattr(needs, attr)

            @staticmethod
            def write(project, after):
                raise OSError("disk full")

        result = run_operation(DropNeed(needs_file=FullNeeds()), {"project": self.project, "need": "alarm", "dry_run": False},
                               build_outside=lambda effects: None)
        self.assertEqual((result.status(), self.need_ids(), self.entry("speaker")["used_in"]), ("could-not-run", ["soil", "alarm", "input"], {}))
        self.assertEqual(result.findings[0].code, "drop_unwritten")
        self.assertEqual(result.findings[0].fix, UNWRITTEN_FIX)
        run(["--needs-drop", str(self.project), "alarm"])
        self.assertEqual(self.need_ids(), ["soil", "input"])

    def test_the_note_reads_a_hand_written_entry_pick_as_the_record_it_is(self):
        path = self.project / ".spark" / "needs.json"
        path.write_text(json.dumps({"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "soil-moisture", "pick": [{"entry": "probe"}]}]}))
        (self.project / "requirements.json").write_text(json.dumps({"parts": ["x-soil"]}))
        said, _ = run(["--needs-drop", str(self.project), "soil"])
        self.assertEqual([note["sentence"][:36] for note in said["notes"]], ["requirements.json still lists x-soil"])

    def test_a_part_another_need_still_picks_gets_no_note(self):
        run(["--pick", str(self.project), "alarm=x-soil"])
        (self.project / "requirements.json").write_text(json.dumps({"parts": [{"part": "x-soil"}]}))
        said, _ = run(["--needs-drop", str(self.project), "soil"])
        self.assertEqual(said["notes"], [])

    def test_a_pick_after_the_drop_gives_the_other_needs_the_same_picks(self):
        run(["--needs-drop", str(self.project), "alarm"])
        before = self.picks()
        run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((self.picks(), self.picks()["soil"]), (before, [{"part": "x-soil"}]))

    def test_describe_lists_the_drop_as_a_write(self):
        said, _ = run(["--describe"])
        row = next(op for op in said["data"]["operations"] if op["op"] == "needs-drop")
        self.assertEqual((row["effects"], row["data"]), (["writes"], ["project", "need", "dropped", "released", "written"]))
# --- end MVP ---


# --- MVP ---
class TheMoveHoldTest(unittest.TestCase):
    """P1124 (#1654): `--move-hold FROM TO NEED=ID`, a core Operation (spark/idea/move_hold.py): FROM keeps its need with no
    pick, TO picks the part, and nothing is written without `--apply`. The fixture is TheNeedsDropTest's, with door-bell."""

    def setUp(self):
        self.home, parent = a_store_with_a_drawer(), Path(tempfile.mkdtemp())
        self.project, self.other = parent / "plant-alarm", parent / "door-bell"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.home / "drawer" / "buzzer.json").write_text(json.dumps({"schema": 1, "label": "a buzzer", "count": 1,
                                                                       "function": [{"does": "sound", "what": "buzzer"}]}))
        run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "sound", "what": "alarm"},
            {"id": "input", "does": "input", "what": "button"}])])
        run(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"])
        (self.other / ".spark").mkdir(parents=True)
        (self.other / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": "chime", "does": "sound", "what": "alarm"}, {"id": "moist", "does": "sense", "what": "soil-moisture"},
            {"id": "brain", "does": "compute", "what": "microcontroller"}]}))

    def move(self, given, *more):
        return run(["--move-hold", str(self.project), str(self.other), given] + list(more))

    def entry(self, key):
        return json.loads((self.home / "drawer" / (key + ".json")).read_text())

    def picks(self, folder):
        return {need["id"]: need.get("pick") for need in json.loads((folder / ".spark" / "needs.json").read_text())["needs"]}

    def digest(self):
        import hashlib
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for root in (self.home, self.project.parent) for path in sorted(root.rglob("*")) if path.is_file()}

    def text(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            parts.main(argv)
        return out.getvalue()

    def test_without_apply_it_writes_no_byte_and_no_file_and_its_next_step_asks_the_person_first(self):
        (self.other / "page.html").write_text("<p>the page</p>")
        before = self.digest()
        said, code = self.move("chime=speaker")
        self.assertEqual((said["status"], code, said["data"]["written"], self.digest()), ("ok", 0, False, before))
        step = said["next"][0]
        self.assertEqual((step["op"], step["needs_person"], step["argv"][-1], step["effects"]), ("move-hold", True, "--apply", ["writes"]))
        self.assertEqual(step["argv"], ["--move-hold", str(self.project), str(self.other), "chime=speaker", "--apply"])
        self.assertEqual((said["data"]["from_project"], said["data"]["to_project"], said["data"]["need"], said["data"]["pick"]),
                         ("plant-alarm", "door-bell", "chime", {"entry": "speaker"}))
        self.assertEqual(said["data"]["projects"][0], {"project": "plant-alarm", "needs_without_pick": ["alarm"],
                                                       "released": [{"entry": "speaker", "was": 1, "now": 0}], "out_of_date": []})
        shown = self.text(["--move-hold", str(self.project), str(self.other), "chime=speaker"])
        for line in ("move speaker from plant-alarm to door-bell: nothing written yet", "alarm keeps its need, with no pick (was speaker)",
                     "would release 1 of 1: speaker — its pick is taken off, the need stays", "chime: speaker",
                     "would list door-bell on your projects"):
            self.assertIn(line, shown)
        self.assertEqual(self.digest(), before)

    def test_with_apply_the_need_stays_with_no_pick_and_the_other_project_picks_and_holds_the_part(self):
        run(["--pick", str(self.other), "chime=buzzer"])
        self.assertEqual(self.entry("buzzer")["used_in"], {"door-bell": 1})
        said, code = self.move("chime=speaker", "--apply")
        self.assertEqual((said["status"], code, said["data"]["written"]), ("ok", 0, True))
        self.assertEqual(self.picks(self.project), {"soil": [{"part": "x-soil"}], "alarm": None, "input": None})
        self.assertNotIn("pick", json.loads((self.project / ".spark" / "needs.json").read_text())["needs"][1])
        self.assertEqual((self.entry("speaker")["used_in"], self.entry("buzzer")["used_in"]), ({"door-bell": 1}, {}))
        self.assertEqual(self.picks(self.other)["chime"], [{"entry": "speaker"}])
        self.assertEqual(said["data"]["projects"][1]["released"], [{"entry": "buzzer", "was": 1, "now": 0}])
        self.assertNotIn("move-hold", [step["op"] for step in said["next"]])

    def test_a_move_into_a_parts_now_with_open_needs_ends_with_its_pick_step(self):
        # P1141: the follow-up names the parts phase's own step after a move too (move_hold.py's written project is TO)
        said, code = self.move("chime=speaker", "--apply")
        self.assertEqual((said["status"], code), ("ok", 0))
        self.assertEqual([(step["op"], step["argv"]) for step in said["next"]],
                         [("pick", ["--pick", str(self.other.absolute()), "moist=<part>", "brain=<part>"])])

    def test_a_pick_by_its_drawer_entry_and_by_its_record_id_moves_the_one_stock(self):
        for given in ("moist=probe", "moist=x-soil"):
            with self.subTest(given=given):
                said, code = self.move(given, "--apply")
                self.assertEqual((code, said["data"]["pick"], self.entry("probe")["used_in"]), (0, {"part": "x-soil"}, {"door-bell": 1}))
                self.assertEqual((self.picks(self.project)["soil"], self.picks(self.other)["moist"]), (None, [{"part": "x-soil"}]))
                run(["--move-hold", str(self.other), str(self.project), "soil=x-soil", "--apply"])
                self.assertEqual(self.entry("probe")["used_in"], {"plant-alarm": 1})

    def test_one_pick_of_two_moves_and_the_need_keeps_the_other(self):
        run(["--pick", str(self.project), "alarm=speaker", "alarm=buzzer"])
        said, code = self.move("chime=buzzer", "--apply")
        self.assertEqual((code, self.picks(self.project)["alarm"], said["data"]["projects"][0]["needs_without_pick"]),
                         (0, [{"entry": "speaker"}], []))
        self.assertEqual((self.entry("speaker")["used_in"], self.entry("buzzer")["used_in"]), ({"plant-alarm": 1}, {"door-bell": 1}))
        run(["--move-hold", str(self.other), str(self.project), "alarm=buzzer"])
        shown = self.text(["--move-hold", str(self.other), str(self.project), "alarm=buzzer"])
        self.assertIn("chime keeps its need, with no pick (was buzzer)", shown)

    def test_a_board_picked_by_two_needs_moves_whole(self):
        (self.home / "drawer" / "xiao.json").write_text(json.dumps({"schema": 1, "label": "XIAO", "count": 1, "is": {"board": "xiao-esp32-c6"}}))
        run(["--pick", str(self.project), "input=xiao-esp32-c6", "alarm=xiao-esp32-c6"])
        said, code = self.move("brain=xiao-esp32-c6", "--apply")
        self.assertEqual((code, said["data"]["projects"][0]["needs_without_pick"], self.entry("xiao")["used_in"]),
                         (0, ["alarm", "input"], {"door-bell": 1}))
        self.assertEqual(said["data"]["released"], [{"entry": "xiao", "was": 1, "now": 0}])

    def refused(self, given, code, *, source=None, target=None):
        before = self.digest()
        said, exit_code = run(["--move-hold", str(source or self.project), str(target or self.other), given, "--apply"])
        self.assertEqual((said["status"], exit_code, said["problems"][0]["code"], said["data"]["written"], self.digest()),
                         ("problems", 1, code, False, before))
        return said

    def test_each_refusal_exits_1_with_its_code_and_writes_nothing(self):
        self.refused("chime=speaker", "move_same_project", target=self.project)
        twin = Path(tempfile.mkdtemp()) / "door-bell"
        twin.mkdir()
        said = self.refused("chime=speaker", "move_same_project", source=twin)
        self.assertIn("whose holds would go under one name, door-bell", said["problems"][0]["sentence"])
        said = self.refused("chime=x-other", "move_not_picked")
        self.assertEqual(said["problems"][0]["sentence"], "no need of plant-alarm picks x-other, so plant-alarm holds no x-other to move")
        said = self.refused("nope=speaker", None)
        self.assertIn("no need called nope", said["problems"][0]["sentence"])
        run(["--pick", str(self.project), "alarm=speaker", "input=speaker"])
        said = self.refused("chime=speaker", "move_part_of_count")
        self.assertEqual(said["problems"][0]["sentence"],
                         "plant-alarm would let go 2 of speaker and door-bell would take 1: a move of part of a count is not there yet")

    def test_a_pick_the_other_project_refuses_even_with_the_hold_let_go_is_its_own_problem(self):
        run(["--drawer-set", a_file([{"entry": "speaker", "count": 1, "used_in": {"plant-alarm": 1, "other-gadget": 1}}])])
        said = self.refused("chime=speaker", None)
        self.assertIn("held by other-gadget", said["problems"][0]["sentence"])

    def test_a_part_the_other_project_already_picks_while_this_one_holds_it_is_refused_as_already_picked(self):
        run(["--drawer-set", a_file([{"entry": "speaker", "count": 2}])])
        run(["--pick", str(self.other), "chime=speaker"])
        self.assertEqual(self.entry("speaker")["used_in"], {"plant-alarm": 1, "door-bell": 1})
        said = self.refused("chime=speaker", "move_already_picked")
        self.assertEqual(said["problems"][0]["sentence"], "door-bell already picks speaker for chime, and plant-alarm holds it too")

    def test_a_file_that_cannot_be_read_while_planning_says_nothing_was_written(self):
        for broken in (self.home / "projects.json", self.other / ".spark" / "needs.json"):
            with self.subTest(broken=broken.name):
                kept = broken.read_text() if broken.is_file() else None
                broken.write_text("{not json")
                before = self.digest()
                said, code = self.move("chime=speaker", "--apply")
                self.assertEqual((said["status"], code, said["unchecked"][0]["code"], self.digest()), ("could-not-run", 2, "move_unreadable", before))
                self.assertIn("nothing was moved: ", said["unchecked"][0]["sentence"])
                broken.unlink() if kept is None else broken.write_text(kept)

    def test_a_second_move_of_the_same_hold_is_refused(self):
        self.move("chime=speaker", "--apply")
        self.refused("chime=speaker", "move_not_picked")
        shown = self.text(["--move-hold", str(self.project), str(self.other), "chime=speaker"])
        self.assertIn("the move is refused, and nothing was written", shown)
        self.assertIn("no need of plant-alarm picks speaker, so plant-alarm holds no speaker to move", shown)

    def test_a_bad_need_and_id_exits_2_and_writes_nothing(self):
        before = self.digest()
        for given in ("chime", "=speaker", "chime="):
            with self.subTest(given=given):
                said, code = self.move(given, "--apply")
                self.assertEqual((said["status"], code, said["unchecked"][0]["code"], self.digest()), ("could-not-run", 2, "bad_argument", before))

    def test_a_pick_that_did_not_finish_stops_the_move_and_the_same_move_again_finishes_it(self):
        from spark.design.pick_parts import PickParts
        from spark.idea.move_hold import MoveHold

        class FullStore(PickParts):
            def build_answer(self, **values):
                raise OSError("disk full")

        values = {"move": [str(self.project), str(self.other), "chime=speaker"], "apply": True}
        result = run_operation(MoveHold(picker=FullStore()), values, build_outside=lambda effects: None)
        self.assertEqual((result.status(), result.findings[-1].code), ("could-not-run", "move_unwritten"))
        self.assertEqual((self.picks(self.project)["alarm"], self.entry("speaker").get("used_in")), ([{"entry": "speaker"}], {}))
        said, code = self.move("chime=speaker", "--apply")
        self.assertEqual((code, self.picks(self.project)["alarm"], self.entry("speaker")["used_in"]), (0, None, {"door-bell": 1}))

    def test_a_needs_file_that_refuses_the_last_write_is_finished_by_the_same_move_again(self):
        from spark.idea.move_hold import MoveHold

        class FullNeeds:
            def __getattr__(self, attr):
                return getattr(needs, attr)

            @staticmethod
            def write(project, after):
                raise OSError("disk full")

        values = {"move": [str(self.project), str(self.other), "chime=speaker"], "apply": True}
        result = run_operation(MoveHold(needs_file=FullNeeds()), values, build_outside=lambda effects: None)
        self.assertEqual((result.status(), result.findings[0].code), ("could-not-run", "move_unwritten"))
        self.assertEqual((self.picks(self.project)["alarm"], self.picks(self.other)["chime"], self.entry("speaker")["used_in"]),
                         ([{"entry": "speaker"}], [{"entry": "speaker"}], {"door-bell": 1}))
        said, code = self.move("chime=speaker", "--apply")
        self.assertEqual((code, said["data"]["released"], self.picks(self.project)["alarm"]), (0, [], None))

    def test_out_of_date_names_the_requirements_and_what_was_made_from_them_where_requirements_json_is(self):
        (self.project / "requirements.json").write_text(json.dumps({"parts": [{"part": "x-soil"}]}))
        said, _ = self.move("chime=speaker")
        self.assertEqual([side["out_of_date"] for side in said["data"]["projects"]], [["requirements", "build", "breadboard"], []])
        (self.other / "requirements.json").write_text(json.dumps({"parts": []}))
        said, _ = self.move("chime=speaker")
        self.assertEqual([side["out_of_date"] for side in said["data"]["projects"]], [["requirements", "build", "breadboard"]] * 2)
        self.assertIn("out of date: requirements, build, breadboard. Run parts.py --requirements %s, then build." % self.other.resolve(),
                      self.text(["--move-hold", str(self.project), str(self.other), "chime=speaker"]))

    def test_release_picks_alone_lets_go_every_pick_and_keeps_every_need(self):
        from spark.idea.move_hold import release_picks
        before = needs.read(self.project)
        release = release_picks("plant-alarm", before, drawer.entries(), lambda pick: True)
        self.assertEqual((release.after, release.released), ([{"id": "soil", "does": "sense", "what": "soil-moisture"},
                                                              {"id": "alarm", "does": "sound", "what": "alarm"},
                                                              {"id": "input", "does": "input", "what": "button"}],
                                                             [{"entry": "probe", "was": 1, "now": 0}, {"entry": "speaker", "was": 1, "now": 0}]))
        self.assertEqual((needs.read(self.project), self.entry("speaker")["used_in"]), (before, {"plant-alarm": 1}))

    def test_describe_lists_the_move_as_a_write_only_with_apply(self):
        said, _ = run(["--describe"])
        row = next(op for op in said["data"]["operations"] if op["op"] == "move-hold")
        self.assertEqual((row["effects"], row["dry_run"], row["apply"], row["data"]),
                         (["writes"], True, True, ["from_project", "to_project", "need", "pick", "released", "written", "projects"]))
# --- end MVP ---

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

    LED_LIMIT = "  part led-red-5mm: Wokwi's LED: lights on current; its forward voltage and brightness are not this part's\n"

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
        self.assertEqual((code, self.written(project)), (0, {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"],
                                                             "unserved": [{"need": "alarm", "why": "no record", "picks": ["speaker"]}]}))
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

    def test_when_the_board_serves_every_need_the_file_says_board_only(self):
        _, project = self.project([self.BOARD, ("light", [{"board": "firebeetle2-esp32s3"}])])
        said = self.text(["--requirements", str(project)])
        self.assertEqual(self.written(project), {"board": "firebeetle2-esp32s3", "parts": [], "board_only": True})
        self.assertIn("  board only: nothing to build but the board", said)
        self.assertNotIn("board_only removed", self.text(["--requirements", str(project)]))

    def test_a_part_picked_later_takes_board_only_away_and_says_so(self):
        _, project = self.project([self.BOARD, ("light", [{"board": "firebeetle2-esp32s3"}])])
        run(["--requirements", str(project)])
        self.picking(project, [self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        said = self.text(["--requirements", str(project)])
        self.assertEqual(self.written(project), {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]})
        self.assertIn("  board_only removed: the file lists parts", said)

    def test_a_need_off_the_board_leaves_board_only_to_the_person(self):
        for held, after in (({}, None), ({"board_only": True}, True)):
            with self.subTest(held=held):
                _, project = self.project([self.BOARD, ("power", [])])
                (project / "requirements.json").write_text(json.dumps(dict({"board": "firebeetle2-esp32s3", "parts": []}, **held)))
                run(["--requirements", str(project)])
                self.assertEqual(self.written(project).get("board_only"), after)

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

    def test_a_catalog_pick_whose_footprint_would_be_code_is_refused_and_never_shelved(self):
        # C-1 (TL-3's probe): a researched record carrying a crafted footprint went onto the shelf and into board.tsx
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        led = json.loads((home / "catalog" / "x-led.json").read_text())
        (home / "catalog" / "x-led.json").write_text(json.dumps(dict(led, footprint='pushbutton"} pcbX={(globalThis.x = 1, 0)} data-x="')))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, [p["subject"] for p in said["problems"]]), ("problems", 1, ["x-led"]))
        self.assertTrue(said["problems"][0]["sentence"].startswith("footprint is "), said["problems"])
        self.assertFalse((project / "requirements.json").exists() or (home / "shelf").exists())

    def test_a_catalog_pick_whose_rail_would_be_code_is_refused_and_never_shelved(self):
        # P87's attribute half, as C-1 for the footprint: the rail is written into board.tsx as `to="net.<RAIL>"`
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        led = json.loads((home / "catalog" / "x-led.json").read_text())
        led["power"][0]["rail"] = 'gnd" pcbX={(globalThis.x = 1, 0)} y="'
        (home / "catalog" / "x-led.json").write_text(json.dumps(led))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, [p["subject"] for p in said["problems"]]), ("problems", 1, ["x-led"]))
        self.assertTrue(said["problems"][0]["sentence"].startswith("power[0] rail is "), said["problems"])
        self.assertFalse((project / "requirements.json").exists() or (home / "shelf").exists())

    @slow("a real tsci build of a project whose part name is hostile, 1 test, 6 to 12 s on 2026-10-26")
    def test_a_catalog_pick_whose_name_would_end_the_board_s_comment_is_built_with_it_inert(self):
        # F11 (the review's probe; P87's emitter half): a name is not refused — product names carry inch marks — so this
        # one is shelved and built, and the board keeps it in a comment it cannot end. `tsci build` printed REVIEW-INJECTED-42
        # (the name in one comment, as the review's record had it: no host requirements to repeat it in).
        toolchain = board_engine.find_toolchain(Path(tempfile.mkdtemp()))
        if toolchain is None:
            self.skipTest("no tsci to build with: a project's own, or one on PATH")
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        led = json.loads((home / "catalog" / "x-led.json").read_text())
        (home / "catalog" / "x-led.json").write_text(json.dumps(dict(
            led, name='A soil probe */ console.log("REVIEW-INJECTED-" + 6*7) /* end', host_requirements=[])))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["shelved"]), (0, ["x-led"]))
        kept, outputs, real_run = Path(tempfile.mkdtemp()), [], subprocess.run

        def watched(*args, **kwargs):
            finished = real_run(*args, **kwargs)
            outputs.append("%s %s" % (finished.stdout, finished.stderr))
            return finished

        out = io.StringIO()
        with mock.patch.object(subprocess, "run", side_effect=watched), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(project / "requirements.json"), "--keep", str(kept), "--json"])
        stages = {stage["name"]: stage["status"] for stage in json.loads(out.getvalue())["stages"]}
        self.assertEqual(stages.get("build"), "ok", out.getvalue())
        self.assertEqual([said for said in outputs if "REVIEW-INJECTED-42" in said], [], "the build ran the name as code")
        board = (kept / "board.tsx").read_text()
        self.assertIn("REVIEW-INJECTED", board)
        self.assertNotIn("REVIEW-INJECTED", re.sub(r"/\*.*?\*/", "", board, flags=re.DOTALL), "outside every comment")

    @board_missing("physical.header")
    def test_a_board_that_stops_at_the_footprint_is_written_saying_so(self):
        # F12 (C-7): --requirements wrote the XIAO without a word, and the build then stopped; warned, never refused
        _, project = self.project([("board", [{"board": "xiao-esp32-c6"}]), ("light", [{"part": "led-red-5mm"}])])
        for extra in (["--dry-run"], []):
            with self.subTest(extra=extra):
                self.assertIn("  board xiao-esp32-c6: stops at the footprint stage (P121): its board file lacks physical.header",
                              self.text(["--requirements", str(project)] + extra).splitlines())
        self.assertEqual(self.written(project)["board"], "xiao-esp32-c6")
        _, builds = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        self.assertNotIn("stops at", self.text(["--requirements", str(builds)]))

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
        for extra, verb, names in ((["--dry-run"], "would write", "would name"), ([], "wrote", "names")):  # a real run shelves x-led
            with self.subTest(extra=extra):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    parts.main(["--requirements", str(project)] + extra)
                self.assertEqual(out.getvalue(), "  %s %s: board firebeetle2-esp32s3; parts tactile-button (OpenLid), tactile-button (Mode), x-led\n"
                                 "  part tactile-button (OpenLid): Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled\n"  # P778: each part's own limit
                                 "  part tactile-button (Mode): Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled\n"
                                 "  part x-led: Wokwi's LED: lights on current; its forward voltage and brightness are not this part's\n"
                                 "  onto the shelf, so every project builds with it: x-led\n"
                                 "  reserved, not placed — no record: speaker\n"
                                 "  not on the board: alarm — speaker has no record: fine for what is wired off the board (a speaker, "
                                 "a battery); what sits on the board needs one — link its drawer entry to a record with `is`, or "
                                 "research one\n"
                                 "  requirements.json %s your drawer entry speaker — a key made from your label, in the project's own file\n"
                                 % (verb, project / "requirements.json", names))

    def test_a_drawer_entry_s_key_the_file_names_is_said_once(self):
        # F16 (C-17's rule): `unserved` writes a key made from the person's label into requirements.json, the file most often
        # committed — said by the write that adds it, never again; two keys at once are said together
        _, project = self.project([self.BOARD, ("alarm", [{"entry": "speaker"}]), ("power", [{"entry": "lipo"}])])
        first, again = self.text(["--requirements", str(project)]), self.text(["--requirements", str(project)])
        self.assertIn("\n  requirements.json names your drawer entries lipo, speaker — a key made from your label, in the project's own "
                      "file\n", first)
        self.assertNotIn("your drawer entr", again)

    # --- a re-run keeps what the person did by hand (the PO, 2026-10-08) ---

    def test_the_dry_run_says_what_it_would_keep_and_the_board_it_would_change(self):
        _, project = self.project(self.DRIVER_AND_TWO_BUTTONS)
        (project / "requirements.json").write_text(json.dumps(dict(self.BY_HAND, board="xiao-esp32-c6")))
        before = (project / "requirements.json").read_text()
        self.assertEqual(self.text(["--requirements", str(project), "--dry-run"]),
                         "  would write %s: board firebeetle2-esp32s3; parts l9110s-module, jst-ph-2-power-inlet, "
                         "tactile-button (BtnOpen), tactile-button (BtnMode)\n"
                         '  board: "xiao-esp32-c6" → "firebeetle2-esp32s3"\n'
                         "  part l9110s-module: one channel: reads IA/IB and prints MOTOR: opening/closing/stopped; models no current, "
                         "so a stall cannot be simulated\n"  # P778: each part's own limit, the kept one's too
                         "  part jst-ph-2-power-inlet: not simulated at all: a connector is wiring, not a part to simulate; the simulator "
                         "powers the board itself\n"
                         "  part tactile-button (BtnOpen): Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled\n"
                         "  part tactile-button (BtnMode): Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled\n"
                         "  kept, not from a pick: jst-ph-2-power-inlet\n"
                         "  rail TRACTION has no supply — pick a power inlet or a supply (l9110s-module.VCC draws from it)\n"
                         "  net MOTOR6V is driven by jst-ph-2-power-inlet.VCC and nothing listed receives it — pick what it drives "
                         "(a speaker terminal, a motor, a connector)\n" % (project / "requirements.json"))
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

    def test_a_run_that_changes_nothing_says_unchanged_not_wrote(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        first, again = self.text(["--requirements", str(project)]), self.text(["--requirements", str(project)])
        # P778: the part's own limit follows the write line, on a run that writes and on one that changes nothing
        self.assertEqual((first, again), ("  wrote %s: board firebeetle2-esp32s3; parts led-red-5mm\n%s" % (project / "requirements.json", self.LED_LIMIT),
                                          "  unchanged %s: board firebeetle2-esp32s3; parts led-red-5mm\n%s" % (project / "requirements.json", self.LED_LIMIT)))

    def test_the_names_it_checks_are_the_ones_the_generator_gives(self):
        for part_id, name in (("tactile-button", None), ("led-1", None), ("led1", None), ("jst_ph_2", None), ("tactile-button", "BtnOpen")):
            with self.subTest(part_id=part_id, name=name):
                instance = {"_instance": name} if name else {}
                self.assertEqual(need_requirements._called(part_id, name), board_components.component_name(dict({"id": part_id}, **instance)))

    def test_a_re_pick_leaves_the_old_part_listed_as_kept(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        run(["--requirements", str(project)])
        self.picking(project, [self.BOARD, ("light", [{"part": "x-led"}])])
        said, _ = run(["--requirements", str(project)])
        self.assertEqual((self.written(project)["parts"], said["data"]["kept"]),
                         (["led-red-5mm", "x-led"], [{"part": "led-red-5mm", "name": None}]))
        self.assertIn("  written for a pick that is gone: led-red-5mm (need light)\n", self.text(["--requirements", str(project), "--dry-run"]))

    # --- P877: an entry spark wrote for a pick that is gone is named, and removed on the person's yes ---
    GONE_LINE = "  written for a pick that is gone: led-red-5mm (need light)\n"
    GONE = {"part": "led-red-5mm", "name": None, "need": "light", "code": "entry_pick_gone"}
    #: P1139: the gone entry's note, which comes before the record's and a reply's notes.
    GONE_NOTE = {"subject": None, "sentence": "written for a pick that is gone: led-red-5mm (need light)"}
    PREVIOUS = ".spark/previous/requirements.json.txt"
    NOTE_CHANGED = ("requirements-origin.json does not fit the parts of requirements.json as spark wrote them, "
                    "so every entry is read as yours")

    def repicked(self):
        """The walk the card comes from, up to its second run: pick, write, re-pick. Returns the project."""
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        run(["--requirements", str(project)])
        self.picking(project, [self.BOARD, ("light", [{"part": "x-led"}])])
        return project

    def named(self, project):
        """The second run of the walk, which writes both parts: its answer."""
        return run(["--requirements", str(project)])[0]

    def replying(self, project, given):
        """The agent's own replies file, with `given` ({key: value}) in it."""
        path = project.parent / "my-replies.json"
        path.write_text(json.dumps({"replies": given}))
        return path

    def digest(self, project):
        import hashlib
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(project.rglob("*")) if path.is_file()}

    def test_the_walk_a_re_pick_names_the_old_entry_and_a_yes_with_the_printed_key_removes_it(self):
        project = self.repicked()
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["status"], self.written(project)["parts"], said["data"]["unexplained"], said["data"]["previous"]),
                         (0, "ok", ["led-red-5mm", "x-led"], [self.GONE], None))
        key = said["data"]["remove_key"]
        self.assertRegex(key, r"^requirements\.remove_entries\.[0-9a-f]{8}$")
        before = (project / "requirements.json").read_text()
        replies = self.replying(project, {key: True})
        said, code = run(["--requirements", str(project), "--replies", str(replies)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["unexplained"], said["data"]["remove_key"], said["data"]["previous"]),
                         (0, ["x-led"], [], None, self.PREVIOUS))
        self.assertEqual((project / self.PREVIOUS).read_text(), before)
        self.assertEqual(json.loads(replies.read_text()), {"replies": {key: None}})

    def test_the_yes_says_what_it_removed_and_where_the_previous_version_is(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        said = self.text(["--requirements", str(project), "--replies", str(self.replying(project, {key: True}))])
        self.assertIn("  removed 1 entry (the previous version is %s)\n" % self.PREVIOUS, said)
        self.assertNotIn("written for a pick that is gone", said)

    def test_a_run_with_no_yes_writes_as_today_and_names_the_entry_its_key_and_how_to_say_yes(self):
        project = self.repicked()
        said, code = run(["--requirements", str(project)])
        key = said["data"]["remove_key"]
        self.assertEqual((code, said["data"]["kept"], [step["op"] for step in said["next"]], said["next"][0]["needs_person"]),
                         (0, [{"part": "led-red-5mm", "name": None}], ["requirements"], True))
        self.assertEqual(said["next"][0]["argv"], ["--requirements", str(project), "--replies", "<your replies file>"])
        self.assertIn(key, said["next"][0]["why"])
        text = self.text(["--requirements", str(project)])
        self.assertIn(self.GONE_LINE, text)
        self.assertNotIn("kept, not from a pick", text)
        self.assertEqual(self.named(project)["data"]["remove_key"], key)  # the key of this run fits the next one

    def test_the_yes_removes_the_entry_spark_wrote_and_keeps_the_person_s(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / "requirements.json").write_text(json.dumps({"parts": ["jst-ph-2-power-inlet"]}))
        run(["--requirements", str(project)])
        self.picking(project, [self.BOARD, ("light", [{"part": "x-led"}])])
        key = self.named(project)["data"]["remove_key"]
        said, code = run(["--requirements", str(project), "--replies", str(self.replying(project, {key: True}))])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["kept"]),
                         (0, ["jst-ph-2-power-inlet", "x-led"], [{"part": "jst-ph-2-power-inlet", "name": None}]))

    def test_a_no_keeps_the_entry_and_it_reads_as_the_person_s_after(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        replies = self.replying(project, {key: False})
        said, code = run(["--requirements", str(project), "--replies", str(replies)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["unexplained"], said["data"]["remove_key"], said["next"]),
                         (0, ["led-red-5mm", "x-led"], [], None, []))
        self.assertEqual(json.loads(replies.read_text()), {"replies": {key: None}})
        again, _ = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((again["data"]["unexplained"], again["data"]["remove_key"], again["data"]["kept"]),
                         ([], None, [{"part": "led-red-5mm", "name": None}]))
        self.assertIn("  kept, not from a pick: led-red-5mm\n", self.text(["--requirements", str(project), "--dry-run"]))

    def test_a_no_is_said_once_and_the_entries_are_not_named_again(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        text = self.text(["--requirements", str(project), "--replies", str(self.replying(project, {key: False}))])
        self.assertIn("  kept as yours: led-red-5mm (you said no)\n", text)
        self.assertNotIn("written for a pick that is gone", text)
        self.assertNotIn("answer yes", text)

    def test_only_the_json_true_is_a_yes(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        for value in ("yes", "true", 1, [True]):
            with self.subTest(value=value):
                replies = self.replying(project, {key: value})
                said, code = run(["--requirements", str(project), "--replies", str(replies)])
                self.assertEqual((code, self.written(project)["parts"], said["data"]["previous"]), (0, ["led-red-5mm", "x-led"], None))
                self.assertEqual(json.loads(replies.read_text()), {"replies": {key: value}})

    def test_a_yes_for_other_entries_or_other_bytes_removes_nothing_and_names_the_key_that_fits(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        other = "requirements.remove_entries.%s" % ("0" * 8 if not key.endswith("0" * 8) else "1" * 8)
        replies = self.replying(project, {other: True})
        said, code = run(["--requirements", str(project), "--replies", str(replies)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["previous"], json.loads(replies.read_text())),
                         (0, ["led-red-5mm", "x-led"], None, {"replies": {other: True}}))
        self.assertEqual(said["notes"], [self.GONE_NOTE, {"subject": "replies", "sentence": "the replies file holds an answer for other entries or other bytes, "
                                                          "so nothing was removed: the answer for these entries is %s" % key}])

    def test_the_dry_run_leaves_a_yes_in_the_replies_file_and_changes_no_byte(self):
        project = self.repicked()
        run(["--requirements", str(project)])
        key = run(["--requirements", str(project), "--dry-run"])[0]["data"]["remove_key"]
        replies = self.replying(project, {key: True})
        before, held = self.digest(project), replies.read_text()
        said, code = run(["--requirements", str(project), "--replies", str(replies), "--dry-run"])
        self.assertEqual((code, said["data"]["unexplained"], said["data"]["previous"], said["data"]["written"]), (0, [self.GONE], None, False))
        self.assertEqual((self.digest(project), replies.read_text()), (before, held))

    def test_a_dry_run_after_a_re_pick_writes_neither_the_file_nor_the_record(self):
        project = self.repicked()
        before = self.digest(project)
        said, code = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((code, said["data"]["written"], said["data"]["unexplained"]), (0, False, [self.GONE]))
        self.assertEqual(self.digest(project), before)

    def test_a_refused_run_reads_and_clears_no_reply_and_removes_nothing(self):
        project = self.repicked()
        self.picking(project, [self.BOARD, ("led-1", [{"part": "x-led"}]), ("led1", [{"part": "x-led"}])])
        before, junk = self.digest(project), "requirements.remove_entries.deadbeef"
        replies = self.replying(project, {junk: True})
        for given in (replies, project.parent / "no-such-replies.json"):
            with self.subTest(given=given.name):
                said, code = run(["--requirements", str(project), "--replies", str(given)])
                self.assertEqual((said["status"], code, said["data"]["unexplained"], said["data"]["remove_key"]), ("problems", 1, [], None))
        self.assertEqual((self.digest(project), json.loads(replies.read_text())), (before, {"replies": {junk: True}}))

    def test_a_file_the_person_changed_since_reads_every_entry_as_theirs_and_says_so(self):
        project = self.repicked()
        run(["--requirements", str(project)])
        held = self.written(project)
        held["parts"][0] = {"part": "led-red-5mm", "name": "Lamp"}
        (project / "requirements.json").write_text(json.dumps(held))
        said, code = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((code, said["data"]["unexplained"], said["data"]["remove_key"], said["data"]["kept"],
                          [note["sentence"] for note in said["notes"]]),
                         (0, [], None, [{"part": "led-red-5mm", "name": "Lamp"}], ["kept, not from a pick: led-red-5mm (Lamp)", self.NOTE_CHANGED]))

    def test_a_reformat_or_a_key_of_its_own_keeps_the_rows_trusted(self):
        project = self.repicked()
        run(["--requirements", str(project)])
        (project / "requirements.json").write_text(json.dumps(dict(self.written(project), signals=[]), indent=4) + "\r\n")
        said, _ = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((said["data"]["unexplained"], said["notes"]), ([self.GONE], [self.GONE_NOTE]))

    def test_an_entry_of_a_file_written_before_the_record_is_the_person_s_and_stays(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        (project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]}))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["kept"]),
                         (0, ["led-red-5mm", "x-led"], [{"part": "led-red-5mm", "name": None}]))
        self.assertIn("  kept, not from a pick: led-red-5mm\n", self.text(["--requirements", str(project), "--dry-run"]))

    # --- P1139: the kept entries are notes too, so the page can say them, and the record is written when spark wrote none ---
    KEPT = {"subject": None, "sentence": "kept, not from a pick: tactile-button, led-red-5mm"}

    def test_the_walk_entries_no_pick_explains_are_a_note_and_the_record_is_written_with_no_row(self):
        import hashlib
        _, project = self.project([self.BOARD, ("button", [{"board": "firebeetle2-esp32s3"}]), ("light", [{"board": "firebeetle2-esp32s3"}])])
        (project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button", "led-red-5mm"]}))
        record = project / ".spark" / "requirements-origin.json"
        dry, _ = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((dry["notes"], record.exists()), ([self.KEPT], False))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["status"], said["notes"]), (0, "ok", [self.KEPT]))
        parts = json.dumps(["tactile-button", "led-red-5mm"], separators=(",", ":"))
        # content_sha256 is the hash of the canonical JSON of requirements.json read back, not of the file's bytes (P1140)
        whole = json.dumps(json.loads((project / "requirements.json").read_text()), sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads(record.read_text()),
                         {"schema": 1, "parts_sha256": hashlib.sha256(parts.encode()).hexdigest(),
                          "content_sha256": hashlib.sha256(whole.encode()).hexdigest(), "written": []})
        self.assertEqual(self.text(["--requirements", str(project), "--dry-run"]).count("kept, not from a pick"), 1)

    def test_an_entry_written_for_a_pick_that_is_gone_is_a_note_said_once(self):
        project = self.repicked()
        said, _ = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual(said["notes"], [self.GONE_NOTE])
        self.assertEqual(self.text(["--requirements", str(project), "--dry-run"]).count(self.GONE_LINE), 1)

    def test_the_record_beside_the_file_holds_a_row_per_entry_spark_wrote_and_the_hash_of_the_parts(self):
        import hashlib
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        run(["--requirements", str(project)])
        parts = json.dumps(["led-red-5mm"], separators=(",", ":"))
        # content_sha256 is the hash of the canonical JSON of requirements.json read back, not of the file's bytes (P1140)
        whole = json.dumps(json.loads((project / "requirements.json").read_text()), sort_keys=True, separators=(",", ":"))
        self.assertEqual(json.loads((project / ".spark" / "requirements-origin.json").read_text()),
                         {"schema": 1, "parts_sha256": hashlib.sha256(parts.encode()).hexdigest(),
                          "content_sha256": hashlib.sha256(whole.encode()).hexdigest(),
                          "written": [{"need": "light", "entry": "led-red-5mm"}]})

    def test_a_record_that_is_no_json_reads_as_no_rows_and_is_written_again(self):
        project = self.repicked()
        record = project / ".spark" / "requirements-origin.json"
        record.write_text("{not json")
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["unexplained"], [note["sentence"] for note in said["notes"]]),
                         (0, [], ["kept, not from a pick: led-red-5mm",
                                  "requirements-origin.json cannot be read as spark writes it, so every entry is read as yours"]))
        self.assertEqual(json.loads(record.read_text())["written"], [{"need": "light", "entry": "x-led"}])

    def test_a_previous_version_that_cannot_be_staged_leaves_the_entry_and_the_row_and_the_next_run_names_it_again(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        previous = project / ".spark" / "previous"
        previous.mkdir(parents=True)
        (previous / "requirements.json.txt.new").write_text("not spark's")
        said = self.text(["--requirements", str(project), "--replies", str(self.replying(project, {key: True}))])
        self.assertIn("  left alone: led-red-5mm (.spark/previous/requirements.json.txt.new is in the way: delete it if it is not yours; "
                      "your yes is used up, write it again to try again)\n", said)
        self.assertEqual((self.written(project)["parts"], (previous / "requirements.json.txt.new").read_text(), (previous / "requirements.json.txt").exists()),
                         (["led-red-5mm", "x-led"], "not spark's", False))
        self.assertEqual(run(["--requirements", str(project), "--dry-run"])[0]["data"]["unexplained"], [self.GONE])

    def test_a_previous_folder_that_is_a_file_is_said_with_paths_from_the_project(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        (project / ".spark" / "previous").write_text("not a folder")
        said = self.text(["--requirements", str(project), "--replies", str(self.replying(project, {key: True}))])
        line = next(each for each in said.splitlines() if "left alone" in each)
        self.assertRegex(line, r"^  left alone: led-red-5mm \(the previous version could not be kept: .+ \(\.spark/previous\); "
                               r"your yes is used up, write it again to try again\)$")
        self.assertNotIn(str(project), line)
        self.assertEqual(self.written(project)["parts"], ["led-red-5mm", "x-led"])

    def test_a_record_that_cannot_be_read_as_text_does_not_stop_a_real_run(self):
        project = self.repicked()
        (project / ".spark" / "requirements-origin.json").write_bytes(b"\xff\xfe\x00")
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["status"], self.written(project)["parts"]), (0, "ok", ["led-red-5mm", "x-led"]))
        self.assertIn("requirements-origin.json could not be written, so every entry is read as yours from the next run",
                      [note["sentence"] for note in said["notes"]])

    def test_a_record_path_that_is_a_folder_does_not_stop_a_run_that_adds_an_entry(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / ".spark" / "requirements-origin.json").mkdir()
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["status"], self.written(project)["parts"]), (0, "ok", ["led-red-5mm"]))
        self.assertIn("requirements-origin.json could not be written, so every entry is read as yours from the next run",
                      [note["sentence"] for note in said["notes"]])

    def test_the_note_of_a_yes_that_fits_no_key_names_the_key_the_run_prints(self):
        project = self.repicked()
        self.named(project)
        self.picking(project, [self.BOARD, ("light", [{"part": "x-led"}]), ("inlet", [{"part": "jst-ph-2-power-inlet"}])])
        other = "requirements.remove_entries.00000000"
        said, _ = run(["--requirements", str(project), "--replies", str(self.replying(project, {other: True}))])
        self.assertEqual(self.written(project)["parts"], ["led-red-5mm", "x-led", "jst-ph-2-power-inlet"])
        self.assertEqual([note["sentence"] for note in said["notes"] if note["subject"] == "replies"],
                         ["the replies file holds an answer for other entries or other bytes, so nothing was removed: the answer for "
                          "these entries is %s" % said["data"]["remove_key"]])

    def test_a_dropped_need_s_entry_is_named_by_the_dry_run_with_a_code_and_no_byte_changes(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}]), ("alarm", [{"part": "x-led"}])])
        run(["--requirements", str(project)])
        run(["--needs-drop", str(project), "light"])
        replies = self.replying(project, {"requirements.remove_entries.00000000": True})
        before = dict(self.digest(project), replies=replies.read_bytes())
        said, code = run(["--requirements", str(project), "--replies", str(replies), "--dry-run"])
        self.assertEqual((code, said["data"]["unexplained"], said["data"]["written"]), (0, [self.GONE], False))
        self.assertIn(self.GONE_LINE, self.text(["--requirements", str(project), "--dry-run"]))
        self.assertEqual(dict(self.digest(project), replies=replies.read_bytes()), before)

    def test_a_yes_sets_back_only_the_requirements_keys(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        replies = self.replying(project, {key: True, "research.x": 5, "look.read_board.1a2b": True})
        run(["--requirements", str(project), "--replies", str(replies)])
        self.assertEqual(json.loads(replies.read_text()), {"replies": {key: None, "research.x": 5, "look.read_board.1a2b": True}})

    def test_the_entries_are_told_how_to_be_removed_by_hand_or_by_a_yes(self):
        project = self.repicked()
        self.assertIn(self.GONE_LINE + "  to remove one, delete it from requirements.json by hand, or answer yes (see next)\n",
                      self.text(["--requirements", str(project)]))

    def test_a_write_that_fails_after_the_yes_leaves_the_file_and_no_previous_version_and_no_record_change(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        record = project / ".spark" / "requirements-origin.json"
        before, held = (project / "requirements.json").read_text(), record.read_text()
        (project / "requirements.json.part").mkdir()
        said, code = run(["--requirements", str(project), "--replies", str(self.replying(project, {key: True}))])
        self.assertEqual((said["status"], code, (project / "requirements.json").read_text(), record.read_text()), ("could-not-run", 2, before, held))
        self.assertEqual(sorted(path.name for path in (project / ".spark" / "previous").glob("*")) if (project / ".spark" / "previous").exists() else [], [])

    def test_a_replies_file_that_cannot_be_written_stops_the_run_before_anything_changes(self):
        project = self.repicked()
        key = self.named(project)["data"]["remove_key"]
        replies = self.replying(project, {key: True})
        replies.chmod(0o444)
        self.addCleanup(replies.chmod, 0o644)
        before = self.digest(project)
        said, code = run(["--requirements", str(project), "--replies", str(replies)])
        self.assertEqual((said["status"], code, said["unchecked"][0]["code"], self.digest(project)), ("could-not-run", 2, "bad_argument", before))
        self.assertIn("so that spark can mark the reply as used", said["unchecked"][0]["fix"])

    def test_a_replies_file_that_cannot_be_read_says_how_to_write_one_and_not_the_research_template(self):
        project = self.repicked()
        self.named(project)
        said, code = run(["--requirements", str(project), "--replies", str(project.parent / "no-such-replies.json")])
        self.assertEqual((said["status"], code, said["unchecked"][0]["code"]), ("could-not-run", 2, "bad_argument"))
        self.assertIn('{"replies": {"<key>": true}}', said["unchecked"][0]["fix"])
        self.assertNotIn("template", said["unchecked"][0]["fix"])

    def test_a_failed_write_leaves_no_record(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / "requirements.json.part").mkdir()
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, (project / ".spark" / "requirements-origin.json").exists()), ("could-not-run", 2, False))

    def test_flow_show_reads_the_requirements_as_ok_after_the_removal(self):
        import flow

        def shown():
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                flow.main(["show", "--project", str(project), "--json"])
            return next(phase["status"] for phase in json.loads(out.getvalue())["data"]["phases"] if phase["phase"] == "requirements")
        project = self.repicked()
        said = self.named(project)
        self.assertEqual((said["data"]["unexplained"], shown()), ([self.GONE], "ok"))
        said, _ = run(["--requirements", str(project), "--replies", str(self.replying(project, {said["data"]["remove_key"]: True}))])
        self.assertEqual((said["data"]["unexplained"], shown(), self.written(project)["parts"]), ([], "ok", ["x-led"]))

    def test_the_help_and_the_idea_page_say_the_removal(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit):
            parts.main(["--requirements", "p", "--help"])
        helped = " ".join(out.getvalue().split())
        self.assertIn("names each entry that spark wrote for a pick that is gone", helped)
        self.assertIn("--replies", helped)
        idea = " ".join((ROOT / "commands" / "idea.md").read_text().split())
        self.assertIn("Write `true` only after their yes, as `{\"replies\": {\"<remove_key>\": true}}` in a file of your own", idea)

    def test_a_part_picked_for_two_needs_when_the_file_holds_one_of_it_adds_only_the_other(self):
        for held in ({"part": "tactile-button", "name": "BtnOpen"}, "tactile-button"):
            with self.subTest(held=held):
                _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
                (project / "requirements.json").write_text(json.dumps({"parts": [held]}))
                said, _ = run(["--requirements", str(project)])
                self.assertEqual((self.written(project)["parts"], said["data"]["kept"]),
                                 ([held, {"part": "tactile-button", "name": "Mode"}], []))
                self.assertEqual(board_components.duplicate_component_names(loader.parts_of(self.written(project), project)), [])

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

    # --- a pick is what it is, however it is named; a name is one name whatever its capitals (the final review) ---

    def owned(self, home, key, entry):
        """A drawer entry of the scratch store, as the person keeps it."""
        (home / "drawer").mkdir(exist_ok=True)
        (home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1}, **entry)))

    def test_a_drawer_entry_picked_by_its_key_is_placed_as_the_record_it_is_and_what_that_owes_refuses(self):
        home, project = self.project([self.BOARD, ("light", None), ("soil", None)])
        self.owned(home, "my-leds", {"label": "my LEDs", "count": 2, "is": {"part": "x-led"}})
        self.owned(home, "dfrobot-x-soil", {"label": "soil probes", "count": 2, "is": {"part": "x-soil"}})
        _, picked = run(["--pick", str(project), "light=my-leds"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((picked, code, self.written(project)["parts"], said["data"]["shelved"], said["data"]["unplaced"]),
                         (0, 0, ["x-led"], ["x-led"], []))
        _, picked = run(["--pick", str(project), "soil=dfrobot-x-soil"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((picked, said["status"], code, said["problems"], said["data"]["unplaced"]), (0, "problems", 1, [
            {"subject": "x-soil", "sentence": "owes footprint, pin_order, pin_order_proof, body_mm, simulation — fill it in its own "
                                              "home with --fact-set", "fix": None, "code": None}], []))

    def test_a_pick_written_as_the_drawer_entry_of_a_record_is_read_as_that_record(self):
        # a needs file from before a pick of an entry key became its record's, or edited by hand
        home, project = self.project([self.BOARD, ("soil", [{"entry": "dfrobot-x-soil"}])])
        self.owned(home, "dfrobot-x-soil", {"label": "soil probes", "count": 2, "is": {"part": "x-soil"}})
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, [p["subject"] for p in said["problems"]], said["data"]["unplaced"]),
                         ("problems", 1, ["x-soil"], []))

    def test_a_board_picked_by_its_drawer_entry_s_key_is_that_board(self):
        home, project = self.project([("board", None), ("light", [{"part": "led-red-5mm"}])])
        self.owned(home, "my-firebeetle", {"label": "my FireBeetle", "count": 1, "is": {"board": "firebeetle2-esp32s3"}})
        _, picked = run(["--pick", str(project), "board=my-firebeetle"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((picked, code, self.written(project)), (0, 0, {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]}))

    def test_a_board_picked_from_the_drawer_with_no_board_file_is_named_with_the_boards_spark_has(self):
        home, project = self.project([])
        library = Path(tempfile.mkdtemp())
        (library / "x-lib-board.json").write_text(json.dumps(dict(json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text()),
                                                                  id="x-lib-board")))
        (project / "boards").mkdir()
        (project / "boards" / "x-own-board.json").write_text(json.dumps({"id": "x-own-board"}))
        (project / "boards" / "active.json").write_text(json.dumps({"board": "x-own-board"}))  # the board chosen: no board itself
        self.owned(home, "beetle-c6", {"label": "Beetle ESP32 C6 Mini", "count": 3})
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"entry": "beetle-c6"}]},
            {"id": "light", "does": "indicate", "what": "led", "pick": [{"part": "led-red-5mm"}]}]}))
        with mock.patch.object(board_records, "LIBRARY", library):
            said, code = run(["--requirements", str(project)])
            text = self.text(["--requirements", str(project)])
        sentence = ("picked as the board, but a board needs a board file — a record in boards/ — before spark can build with it, "
                    "and it has none; spark has one that builds for x-lib-board; x-own-board stops at the footprint stage (P121): "
                    "its board file lacks physical.header")
        self.assertEqual((said["status"], code, said["problems"]), ("problems", 1, [
            {"subject": "beetle-c6", "sentence": sentence,
             "fix": 'pick x-lib-board, or write a board file for beetle-c6 first (docs/guide/how-it-works.md, "Your own dev board")',
             "code": None}]))  # P726: the item is a Finding's now, so `code` is a key, None where need_requirements worded it
        self.assertEqual(text, "  refused, so nothing was written: beetle-c6 — %s\n  fix for beetle-c6: %s\n"  # P124: with its fix
                         % (sentence, said["problems"][0]["fix"]))
        self.assertFalse((project / "requirements.json").exists())

    def test_each_board_that_stops_is_named_with_its_own_gaps(self):
        # P411: one sentence for "these stop" said no more than "no header geometry"; each says what its own file lacks
        home, project = self.project([])
        library = Path(tempfile.mkdtemp())
        (library / "x-lib-board.json").write_text(json.dumps(dict(json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text()),
                                                                  id="x-lib-board")))
        cut = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        del cut["physical"]["header_order"], cut["physical"]["width_mm"]
        (project / "boards").mkdir()
        (project / "boards" / "x-cut-board.json").write_text(json.dumps(dict(cut, id="x-cut-board")))
        (project / "boards" / "x-bare-board.json").write_text(json.dumps({"id": "x-bare-board"}))
        (project / "boards" / "active.json").write_text(json.dumps({"board": "x-bare-board"}))
        self.owned(home, "beetle-c6", {"label": "Beetle ESP32 C6 Mini", "count": 3})
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"entry": "beetle-c6"}]}]}))
        with mock.patch.object(board_records, "LIBRARY", library):
            said, _ = run(["--requirements", str(project)])
        self.assertEqual(said["problems"][0]["sentence"],
                         "picked as the board, but a board needs a board file — a record in boards/ — before spark can build with it, "
                         "and it has none; spark has one that builds for x-lib-board; "
                         "x-bare-board stops at the footprint stage (P121): its board file lacks physical.header; "
                         "x-cut-board stops at the footprint stage (P121): its board file lacks 2 fields (first: physical.width_mm)")

    @board_missing("physical.header")
    def test_a_board_that_stops_at_the_footprint_is_never_suggested(self):
        # C-7: the refusal suggested the XIAO, whose board file has no header geometry, beside the S3
        home, project = self.project([])
        self.owned(home, "beetle-c6", {"label": "Beetle ESP32 C6 Mini", "count": 3})
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": "board", "does": "compute", "what": "microcontroller", "pick": [{"entry": "beetle-c6"}]}]}))
        said, _ = run(["--requirements", str(project)])
        self.assertIn("spark has one that builds for firebeetle2-esp32s3; xiao-esp32-c6 stops at the footprint stage (P121): its board file lacks physical.header",
                      said["problems"][0]["sentence"])
        self.assertNotIn("xiao", said["problems"][0]["fix"])

    def test_with_no_board_picked_a_drawer_entry_of_another_need_is_no_board(self):
        _, project = self.project([("alarm", [{"entry": "speaker"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["problems"]), (1, [{"subject": "board", "sentence": "pick one board — none is picked", "fix": None, "code": None}]))

    def test_two_needs_whose_names_differ_only_in_capitals_are_refused_by_need_id(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("openlid", [{"part": "tactile-button"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, said["problems"]), ("problems", 1, [{"subject": "openlid", "fix": None, "code": None, "sentence":
            "its tactile-button would be called Openlid, and need open-lid's tactile-button is called OpenLid — the build refuses two "
            "components of one name, and capitals do not make two names; give one of them a name of your own in requirements.json, "
            '{"part": "tactile-button", "name": …}, and run this again'}]))
        self.assertFalse((project / "requirements.json").exists())

    def test_a_name_the_person_gave_in_other_capitals_is_the_need_s_own(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        (project / "requirements.json").write_text(json.dumps({"parts": [{"part": "tactile-button", "name": "MODE"}]}))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["kept"]),
                         (0, [{"part": "tactile-button", "name": "MODE"}, {"part": "tactile-button", "name": "OpenLid"}], []))

    def test_a_new_name_another_part_has_in_other_capitals_is_refused_by_need_id(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        held = json.dumps({"parts": [{"part": "jst-ph-2-power-inlet", "name": "MODE"}]})
        (project / "requirements.json").write_text(held)
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, [p["subject"] for p in said["problems"]]), (1, ["mode"]))
        self.assertIn("its tactile-button would be called Mode, and jst-ph-2-power-inlet in requirements.json is called MODE",
                      said["problems"][0]["sentence"])
        self.assertEqual((project / "requirements.json").read_text(), held)

    def test_what_a_pick_owes_is_filled_where_its_record_lives(self):
        library = Path(tempfile.mkdtemp()) / "parts"
        library.mkdir()
        (library / "x-amp.json").write_text(json.dumps({"schema": 1, "id": "x-amp", "name": "An amp", "kind": "audio-amplifier", "needs": []}))
        _, project = self.project([self.BOARD, ("alarm", [{"part": "x-amp"}]), ("soil", [{"part": "x-soil"}])])
        with mock.patch.object(record_kind, "LIBRARY", library):
            said, code = run(["--requirements", str(project)])
        owed = "owes footprint, pin_order, pin_order_proof, body_mm, simulation — "
        self.assertEqual((code, [(p["subject"], p["sentence"]) for p in said["problems"]]), (1, [
            ("x-amp", owed + "it is in spark's own library, so it is filled in spark's repository, by a commit — --fact-set does "
                             "not change the library"),
            ("x-soil", owed + "fill it in its own home with --fact-set")]))

    # --- a record that owes only its outline is written, with a warning (the PO, 2026-10-08; P165) ---

    def without(self, home, record_id, *keys):
        """A catalog record that is the library's LED but for `keys`, which it owes."""
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        (home / "catalog" / (record_id + ".json")).write_text(json.dumps(dict({k: v for k, v in led.items() if k not in keys},
                                                                             id=record_id)))

    def test_a_pick_that_owes_only_its_outline_is_written_with_a_placeholder_warning(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-dim"}])])
        self.without(home, "x-dim", "body_mm")
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, self.written(project)["parts"], said["data"]["shelved"], said["data"]["placeholder_outline"]),
                         ("ok", 0, ["x-dim"], ["x-dim"], ["x-dim"]))
        self.assertIn("  placeholder outline — x-dim owes body_mm, so the PCB step lays it out at a placeholder 16 x 12 mm: a "
                      "dimension drawing (fetched after the person's yes) or a measurement fills it — fill it in its own home "
                      "with --fact-set\n", dry)

    def test_a_pick_that_owes_its_outline_and_a_fact_the_circuit_needs_is_still_refused(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-dim"}])])
        self.without(home, "x-dim", "body_mm", "footprint")  # P996: an owed simulation stance no longer refuses
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, [(p["subject"], p["sentence"]) for p in said["problems"]]),
                         ("problems", 1, [("x-dim", "owes footprint, body_mm — fill it in its own home with --fact-set")]))
        self.assertFalse((project / "requirements.json").exists())

    def test_a_pick_that_owes_only_its_simulation_stance_is_written_with_a_warning(self):
        # P996 (the PO, 2026-11-22): "The simulation step should not stop us if we want and can deploy directly."
        home, project = self.project([self.BOARD, ("light", [{"part": "x-sim"}])])
        self.without(home, "x-sim", "simulation")
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, self.written(project)["parts"], said["data"]["placeholder_outline"],
                          said["data"]["no_simulation_stance"]), ("ok", 0, ["x-sim"], [], ["x-sim"]))
        self.assertIn("  no simulation yet — x-sim: spark cannot simulate it yet, so /spark:deploy asks your yes for firmware "
                      "that no simulation tested — fill it in its own home with --fact-set\n", dry)

    def test_a_pick_that_owes_its_outline_and_its_simulation_stance_is_written_with_both_warnings(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-dim"}])])
        self.without(home, "x-dim", "body_mm", "simulation")
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["placeholder_outline"], said["data"]["no_simulation_stance"]), (0, ["x-dim"], ["x-dim"]))

    def test_a_library_pick_that_owes_only_its_outline_says_it_is_filled_in_spark_s_repository(self):
        library = Path(tempfile.mkdtemp()) / "parts"
        library.mkdir()
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        (library / "x-dim.json").write_text(json.dumps(dict({k: v for k, v in led.items() if k != "body_mm"}, id="x-dim")))
        _, project = self.project([self.BOARD, ("light", [{"part": "x-dim"}])])
        with mock.patch.object(record_kind, "LIBRARY", library):
            text = self.text(["--requirements", str(project), "--dry-run"])
        self.assertIn("x-dim owes body_mm, so the PCB step lays it out at a placeholder 16 x 12 mm: a dimension drawing (fetched "
                      "after the person's yes) or a measurement fills it — it is in spark's own library, so it is filled in "
                      "spark's repository, by a commit — --fact-set does not change the library\n", text)

    # --- a need nothing on the board serves is said, never passed over in silence (the PO, 2026-10-08; C-2) ---

    def needing(self, project, *extra):
        """The project's needs as they are, and `extra` needs after them."""
        needs_file = project / ".spark" / "needs.json"
        written = json.loads(needs_file.read_text())
        needs_file.write_text(json.dumps(dict(written, needs=written["needs"] + list(extra))))

    def test_a_need_with_no_pick_is_named_not_on_the_board_and_the_file_is_written(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}]), ("soil", None)])
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        unserved = [{"need": "soil", "why": "no pick", "picks": []}]
        self.assertEqual((said["status"], code, said["data"]["unserved"], self.written(project)),
                         ("ok", 0, unserved, {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"], "unserved": unserved}))
        self.assertIn("  not on the board: soil — no pick; --match lists its candidates\n", dry)

    def test_a_need_marked_a_gap_is_said_as_one(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        self.needing(project, {"id": "smell", "does": "sense", "what": "gas", "mark": "gap"})
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["unserved"]), (0, [{"need": "smell", "why": "a gap", "picks": []}]))
        self.assertIn("  not on the board: smell — marked a gap: nothing like it is in the store yet; research it before it can "
                      "be built\n", self.text(["--requirements", str(project), "--dry-run"]))

    def test_a_need_picked_only_as_drawer_entries_with_no_record_is_named(self):
        _, project = self.project([self.BOARD, ("light", [{"entry": "red-leds"}]),
                                   ("alarm", [{"part": "led-red-5mm"}, {"entry": "speaker"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["unserved"], said["data"]["unplaced"]),
                         (0, [{"need": "light", "why": "no record", "picks": ["red-leds"]}], ["red-leds", "speaker"]))
        self.assertIn("  not on the board: light — red-leds has no record: fine for what is wired off the board (a speaker, a "
                      "battery); what sits on the board needs one — link its drawer entry to a record with `is`, or research "
                      "one\n", self.text(["--requirements", str(project), "--dry-run"]))

    def test_a_need_picked_as_the_drawer_entry_of_a_record_is_on_the_board(self):
        home, project = self.project([self.BOARD, ("light", [{"entry": "my-leds"}])])
        self.owned(home, "my-leds", {"label": "my LEDs", "count": 2, "is": {"part": "x-led"}})
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["unserved"]), (0, ["x-led"], []))

    def test_a_file_whose_every_need_is_served_carries_no_note_and_loses_an_old_one(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / "requirements.json").write_text(json.dumps({"parts": [], "unserved": [{"need": "light", "why": "no pick", "picks": []}]}))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["unserved"], self.written(project)),
                         (0, [], {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]}))

    # --- what the board's power would lack is said before the build (C-3; the PO, 2026-10-08) ---

    def test_a_rail_nothing_listed_supplies_is_said_and_the_file_is_written(self):
        _, project = self.project([self.BOARD, ("drive", [{"part": "l9110s-module"}])])
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, said["data"]["no_supply"], said["data"]["no_driver"], self.written(project)["parts"]),
                         ("ok", 0, [{"rail": "MOTOR6V", "drawn_by": ["l9110s-module.VCC"]}], [], ["l9110s-module"]))
        self.assertIn("  rail MOTOR6V has no supply — pick a power inlet or a supply (l9110s-module.VCC draws from it)\n", dry)

    def test_a_speaker_terminal_alone_is_told_to_pick_what_drives_its_pair_never_a_supply(self):
        # F15: told to pick a power inlet or a supply for SPEAKER_P and SPEAKER_N, a person would feed a supply into what the
        # terminal's own record calls destructive. A net only inputs naming a `polarity` are on is an amplifier's to drive.
        _, project = self.project([self.BOARD, ("alarm", [{"part": "speaker-terminal"}])])
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["no_supply"], said["data"]["no_driver"]),
                         (0, [], [{"net": "SPEAKER_N", "received_by": ["speaker-terminal.SPK_N"]},
                                  {"net": "SPEAKER_P", "received_by": ["speaker-terminal.SPK_P"]}]))
        self.assertIn("  net SPEAKER_P is one side of a driven pair and nothing listed drives it — pick what drives the pair (the "
                      "amplifier this terminal hangs off), never a supply (speaker-terminal.SPK_P is on it)\n", dry)
        self.assertNotIn("power inlet", dry)
        listed, _ = run(["--describe"])  # and the answer's keys are the ones --describe names (Operation.data_keys, P726)
        self.assertEqual(sorted(said["data"]), sorted(next(op["data"] for op in listed["data"]["operations"] if op["op"] == "requirements")))

    def test_every_terminal_on_a_side_nothing_drives_is_named(self):
        home, project = self.project([self.BOARD, ("alarm", [{"part": "speaker-terminal"}, {"part": "x-terminal"}])])
        terminal = json.loads((ROOT / "parts" / "speaker-terminal.json").read_text())
        (home / "catalog" / "x-terminal.json").write_text(json.dumps(dict(terminal, id="x-terminal")))
        self.assertIn("never a supply (speaker-terminal.SPK_P, x-terminal.SPK_P are on it)\n",
                      self.text(["--requirements", str(project), "--dry-run"]))

    def test_with_its_amplifier_the_terminal_s_pair_is_driven(self):
        _, project = self.project([self.BOARD, ("alarm", [{"part": "max98357a-dfr0954"}, {"part": "speaker-terminal"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["no_driver"], said["data"]["no_supply"], said["data"]["no_receiver"]), (0, [], [], []))

    def test_a_supply_picked_or_kept_in_the_file_answers_the_rail(self):
        _, project = self.project([self.BOARD, ("drive", [{"part": "l9110s-module"}]), ("power", [{"part": "jst-ph-2-power-inlet"}])])
        self.assertEqual(run(["--requirements", str(project)])[0]["data"]["no_supply"], [])
        _, project = self.project([self.BOARD, ("drive", [{"part": "l9110s-module"}])])
        (project / "requirements.json").write_text(json.dumps({"parts": ["jst-ph-2-power-inlet"]}))
        self.assertEqual(run(["--requirements", str(project)])[0]["data"]["no_supply"], [])

    def test_a_rail_the_file_moves_a_part_onto_is_the_rail_asked_of(self):
        _, project = self.project(self.DRIVER_AND_TWO_BUTTONS)
        (project / "requirements.json").write_text(json.dumps(self.BY_HAND))
        said, _ = run(["--requirements", str(project)])
        self.assertEqual((said["data"]["no_supply"], said["data"]["no_receiver"]),
                         ([{"rail": "TRACTION", "drawn_by": ["l9110s-module.VCC"]}],
                          [{"net": "MOTOR6V", "driven_by": "jst-ph-2-power-inlet.VCC"}]))

    def test_an_output_nothing_listed_receives_is_said_and_a_speaker_terminal_answers_it(self):
        home, project = self.project([self.BOARD, ("alarm", [{"part": "x-amp"}])])
        amplifier = json.loads((ROOT / "parts" / "max98357a-dfr0954.json").read_text())  # P864: the record without its own socket
        (home / "catalog" / "x-amp.json").write_text(json.dumps(dict({k: v for k, v in amplifier.items() if k != "own_socket"}, id="x-amp")))
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["no_receiver"]), (0, [{"net": "SPEAKER_N", "driven_by": "x-amp.SPK_N"},
                                                                  {"net": "SPEAKER_P", "driven_by": "x-amp.SPK_P"}]))
        self.assertIn("  net SPEAKER_P is driven by x-amp.SPK_P and nothing listed receives it — pick what it drives "
                      "(a speaker terminal, a motor, a connector)\n", dry)
        _, project = self.project([self.BOARD, ("alarm", [{"part": "max98357a-dfr0954"}, {"part": "speaker-terminal"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["no_receiver"], said["data"]["no_supply"]), (0, [], []))

    def test_an_output_that_ends_in_the_part_s_own_socket_is_no_gap(self):
        # P864 (#1230): P711's walk 1 printed "nothing listed receives it" for the DFR0954 and a speaker with no record, and the
        # build stopped on `speaker-terminal`; the record says the outputs end in the module's own socket.
        _, project = self.project([self.BOARD, ("alarm", [{"part": "max98357a-dfr0954"}, {"entry": "speaker"}])])
        dry = self.text(["--requirements", str(project), "--dry-run"])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, said["data"]["no_receiver"], said["data"]["no_supply"]), (0, [], []))
        self.assertNotIn("nothing listed receives it", dry)
        self.assertNotIn("speaker-terminal", self.written(project)["parts"])

    def test_a_part_in_the_file_whose_record_is_broken_is_left_to_the_build_never_a_traceback(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (home / "catalog" / "x-broken.json").write_text(json.dumps({"schema": 1, "id": "x-broken", "name": "B", "kind": "sensor",
                                                                    "needs": [], "power": ["VCC"]}))
        (project / "requirements.json").write_text(json.dumps({"parts": ["x-broken"]}))
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code, said["data"]["no_supply"], said["data"]["no_receiver"]), ("ok", 0, [], []))

    def test_the_library_s_rangefinder_is_picked_into_the_file(self):
        # C-6: its outline is read off Pololu's drawing, so the only sensor spark ships is no longer refused for owing it
        _, project = self.project([self.BOARD, ("distance", [{"part": "vl6180x-breakout"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)["parts"], said["data"]["placeholder_outline"]), (0, ["vl6180x-breakout"], []))


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
        # the body's commands — the frontmatter names each operation once, for allowed-tools (C-5), and runs nothing
        lines = (ROOT / "commands" / "idea.md").read_text().split("---", 2)[2].splitlines()
        flagged = [line for line in lines if any(op in line for op in ("--audit", "--function-set", "--fact-set", "--offer"))]
        self.assertTrue(flagged)
        for line in flagged:
            self.assertRegex(line, r"--project '?<project>'?", line)  # P1256: quoted in a block, still bare in a line of prose
        for line in lines:
            if any(op in line for op in ("--needs-set", "--match", "--pick", "--requirements", "--step", "--tally")):
                self.assertNotIn("--project", line, "--needs-set and --match take the project as their argument: " + line)

    def test_it_marks_its_steps_and_ends_with_the_tally(self):
        idea = " ".join((ROOT / "commands" / "idea.md").read_text().split())
        self.assertIn("M, C and L at their start, and S as soon as the project's folder is chosen", idea)
        self.assertIn("the questions before it are not counted", idea)
        self.assertIn("scripts/parts.py --step '<project>' S", idea)
        self.assertIn("## T — the tally", idea)
        self.assertIn("scripts/parts.py --tally '<project>'", idea)

    def test_section_l_and_the_build_page_say_what_a_later_run_keeps(self):
        idea = " ".join((ROOT / "commands" / "idea.md").read_text().split())
        build = " ".join((ROOT / "commands" / "build.md").read_text().split())
        self.assertIn("A later run changes only what the picks decide: the parts you wrote stay", idea)
        self.assertIn("and the board follows the pick", idea)
        self.assertIn("says which entries no pick explains (`kept, not from a pick`)", idea)
        self.assertIn("names each entry that spark wrote for a pick that is gone (`written for a pick that is gone`)", idea)
        self.assertIn("run again, the parts you wrote stay and the board follows the pick: it adds only the parts your picks still lack", build)


if __name__ == "__main__":
    unittest.main()
