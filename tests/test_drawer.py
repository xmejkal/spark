"""P95: the drawer — what the person owns, written by setting, linked by exact part number (docs/2026-10-04-store-design.md §5.2, §5.5, §8 D)."""

import contextlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import drawer  # noqa: E402
import parts  # noqa: E402


def a_store():
    """A scratch store: one catalog record (SEN0193) and one project on the list, holding one record (DFR0457)."""
    home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "irrigation"
    (home / "catalog").mkdir()
    (home / "catalog" / "sen0193-soil-moisture.json").write_text(json.dumps(
        {"schema": 1, "id": "sen0193-soil-moisture", "name": "Capacitive soil moisture sensor", "kind": "sensor",
         "vendor": "dfrobot", "sku": "SEN0193", "also_known_as": ["Capacitive Soil Moisture Sensor SKU SEN0193"]}))
    record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
    record.update(id="dfr0457-mosfet", vendor="dfrobot", sku="DFR0457", owned=True, sourcing=[{"seller": "a shop"}])
    (project / "parts").mkdir(parents=True)
    (project / "parts" / "dfr0457-mosfet.json").write_text(json.dumps(record))
    (home / "projects.json").write_text(json.dumps({"irrigation": str(project)}))
    return home, project


def run(argv):
    """parts.py with --json: (the envelope, the exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


def a_file(items):
    """Entries as the agent writes them: a JSON file outside any repository, never a command line."""
    path = Path(tempfile.mkdtemp()) / "entries.json"
    path.write_text(json.dumps(items))
    return str(path)


class TheDrawerTest(unittest.TestCase):
    def setUp(self):
        self.home, self.project = a_store()
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def entry(self, key):
        return json.loads((self.home / "drawer" / (key + ".json")).read_text())

    def test_an_entry_needs_only_a_label_and_a_count(self):
        said, code = run(["--drawer-set", a_file([{"label": "a CJMCU-111", "count": 1}])])
        self.assertEqual((code, said["status"]), (0, "ok"))
        self.assertEqual(self.entry("a-cjmcu-111"), {"schema": 1, "label": "a CJMCU-111", "count": 1})

    def test_a_dry_run_says_what_would_change_and_changes_nothing(self):
        run(["--drawer-set", a_file([{"entry": "dfrobot-dfr0954", "label": "I2S amplifier", "count": 2}])])
        said, code = run(["--drawer-set", a_file([{"entry": "dfrobot-dfr0954", "count": 4}]), "--dry-run"])
        self.assertEqual(said["data"]["changes"], [{"entry": "dfrobot-dfr0954", "new": False, "was": {"count": 2}, "now": {"count": 4}}])
        self.assertEqual((code, self.entry("dfrobot-dfr0954")["count"]), (0, 2))

    def test_every_write_sets_never_adds_and_a_retried_one_changes_nothing(self):
        run(["--drawer-set", a_file([{"entry": "dfrobot-dfr0954", "label": "I2S amplifier", "count": 2}])])
        again = a_file([{"entry": "dfrobot-dfr0954", "count": 4}])
        run(["--drawer-set", again])
        said, _ = run(["--drawer-set", again])
        self.assertEqual((self.entry("dfrobot-dfr0954")["count"], said["data"]["changes"]), (4, []))

    def test_a_count_is_whole_pieces_or_many(self):
        self.assertEqual(run(["--drawer-set", a_file([{"label": "buttons", "count": "many"}])])[1], 0)
        for count in (-1, 2.5, True, "lots", None):
            with self.subTest(count=count):
                said, code = run(["--drawer-set", a_file([{"label": "x", "count": count}])])
                self.assertEqual((said["status"], code), ("problems", 1))

    def test_a_write_with_any_wrong_value_writes_nothing(self):
        said, code = run(["--drawer-set", a_file([{"label": "fine", "count": 1}, {"label": "wrong", "count": -1}])])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertFalse((self.home / "drawer").exists())

    def test_an_unknown_field_is_refused_by_name(self):
        said, _ = run(["--drawer-set", a_file([{"label": "x", "count": 1, "price": 3}])])
        self.assertIn("price", said["problems"][0]["sentence"])

    def test_a_label_is_cleaned_never_obeyed(self):
        run(["--drawer-set", a_file([{"entry": "x", "label": "\x1b[31mred\x1b[0m " + "y" * 300, "count": 1}])])
        label = self.entry("x")["label"]
        self.assertNotIn("\x1b", label)
        self.assertEqual(len(label), 160)

    def test_an_exact_part_number_links_the_record_in_the_catalog(self):
        run(["--drawer-set", a_file([{"label": "soil probe", "count": 8, "part_number": {"maker": "dfrobot", "number": "sen0193"}}])])
        self.assertEqual(self.entry("soil-probe")["is"], {"part": "sen0193-soil-moisture"})

    def test_a_whole_token_of_an_id_or_alias_links_the_library_record(self):
        run(["--drawer-set", a_file([{"label": "amp", "count": 2, "part_number": {"number": "DFR0954"}}])])
        self.assertEqual(self.entry("amp")["is"], {"part": "max98357a-dfr0954"})

    def test_a_board_links_by_its_sku_list(self):
        run(["--drawer-set", a_file([{"label": "FireBeetle", "count": 1, "part_number": {"number": "DFR0975"}}])])
        self.assertEqual(self.entry("firebeetle")["is"], {"board": "firebeetle2-esp32s3"})

    def test_a_suffix_difference_is_a_question_never_a_link(self):
        said, _ = run(["--drawer-set", a_file([{"label": "probe v2", "count": 1, "part_number": {"number": "SEN0193-V2"}}])])
        self.assertNotIn("is", self.entry("probe-v2"))
        self.assertIn("sen0193-soil-moisture", said["data"]["questions"][0]["sentence"])

    def test_a_name_alone_never_links(self):
        said, _ = run(["--drawer-set", a_file([{"label": "Capacitive soil moisture sensor", "count": 1}])])
        self.assertNotIn("is", self.entry("capacitive-soil-moisture-sensor"))
        self.assertEqual(said["data"]["questions"], [])

    def test_two_matches_are_a_question(self):
        (self.home / "catalog" / "sen0193-copy.json").write_text(json.dumps(
            {"schema": 1, "id": "sen0193-copy", "name": "Another", "kind": "sensor", "sku": "SEN0193"}))
        said, _ = run(["--drawer-set", a_file([{"label": "probe", "count": 1, "part_number": {"number": "SEN0193"}}])])
        self.assertNotIn("is", self.entry("probe"))
        self.assertIn("sen0193-copy", said["data"]["questions"][0]["sentence"])

    def test_a_record_in_another_project_goes_onto_the_shelf_filtered(self):
        said, _ = run(["--drawer-set", a_file([{"label": "MOSFET", "count": 8, "part_number": {"number": "DFR0457"}}])])
        self.assertEqual((self.entry("mosfet")["is"], said["data"]["shelved"]), ({"part": "dfr0457-mosfet"}, ["dfr0457-mosfet"]))
        shelved = json.loads((self.home / "shelf" / "dfr0457-mosfet.json").read_text())
        self.assertEqual((shelved.get("owned"), shelved.get("sourcing"), shelved["based_on"]["project"]), (None, None, "irrigation"))
        self.assertIn("dfr0457-mosfet", parts.available(), "every project finds it now")

    def test_a_dry_run_shelves_nothing(self):
        run(["--drawer-set", a_file([{"label": "MOSFET", "count": 8, "part_number": {"number": "DFR0457"}}]), "--dry-run"])
        self.assertFalse((self.home / "shelf").exists())

    def test_an_is_the_write_names_must_exist(self):
        said, code = run(["--drawer-set", a_file([{"label": "x", "count": 1, "is": {"part": "no-such-part"}}])])
        self.assertEqual((said["status"], code), ("problems", 1))

    def test_an_is_the_write_names_in_another_project_is_shelved(self):
        run(["--drawer-set", a_file([{"label": "the MOSFET board", "count": 1, "is": {"part": "dfr0457-mosfet"}}])])
        self.assertTrue((self.home / "shelf" / "dfr0457-mosfet.json").is_file())

    def test_the_drawer_lists_label_count_is_unsure_skip(self):
        run(["--drawer-set", a_file([{"label": "A4988 HW-134", "count": 1, "skip": "I think it's dead"},
                                    {"label": "MP3 mini module", "count": 1, "unsure": True}])])
        said, code = run(["--drawer"])
        self.assertEqual(code, 0)
        self.assertEqual(said["data"]["entries"][0], {"entry": "a4988-hw-134", "label": "A4988 HW-134", "count": 1, "is": None,
                                                      "in": None, "unsure": False, "skip": "I think it's dead"})
        self.assertTrue(said["data"]["entries"][1]["unsure"])

    def test_ninety_nine_entries_answer_in_at_most_4_kb_20_at_a_time(self):
        names = ['Gravity: "Analog" $%d Capacitive Soil Moisture Sensor - Corrosion Resistant, pack of 10 pcs %s' % (n, "x" * 20)
                 for n in range(99)]
        run(["--drawer-set", a_file([{"entry": "dfrobot-x%02d" % n, "label": name, "count": 1} for n, name in enumerate(names)])])
        seen, argv = [], ["--drawer"]
        while argv:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                parts.main(argv + ["--json"])
            self.assertLessEqual(len(out.getvalue().encode("utf-8")), 4096)
            said = json.loads(out.getvalue())
            self.assertLessEqual(len(said["data"]["entries"]), 20)
            seen += [e["entry"] for e in said["data"]["entries"]]
            argv = said["truncated"]["next"]["argv"] if said["truncated"] and said["truncated"]["next"] else None
        self.assertEqual(sorted(seen), ["dfrobot-x%02d" % n for n in range(99)])

    def test_the_drawer_is_private(self):
        run(["--drawer-set", a_file([{"label": "x", "count": 1}])])
        self.assertEqual(stat.S_IMODE((self.home / "drawer" / "x.json").stat().st_mode), 0o600)

    def test_the_drawer_is_never_written_inside_git(self):
        repo = Path(tempfile.mkdtemp())
        (repo / ".git").mkdir()
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(repo / "spark")}):
            said, code = run(["--drawer-set", a_file([{"label": "x", "count": 1}])])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("git work tree", said["unchecked"][0]["sentence"])
        self.assertFalse((repo / "spark" / "drawer").exists())

    def test_a_drawer_file_that_is_not_json_is_named(self):
        (self.home / "drawer").mkdir()
        (self.home / "drawer" / "broken.json").write_text("{")
        said, code = run(["--drawer"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("broken.json", said["unchecked"][0]["sentence"])

    def test_a_project_whose_folder_is_gone_is_passed_over(self):
        (self.home / "projects.json").write_text(json.dumps({"gone": str(self.project.parent / "no-such-folder")}))
        said, code = run(["--drawer-set", a_file([{"label": "probe", "count": 1, "part_number": {"number": "SEN0193"}}])])
        self.assertEqual((code, self.entry("probe")["is"]), (0, {"part": "sen0193-soil-moisture"}))
        self.assertEqual(run(["--drawer"])[1], 0)

    def test_a_write_that_is_not_a_json_list_could_not_run_or_is_refused(self):
        broken = Path(tempfile.mkdtemp()) / "entries.json"
        broken.write_text("[{")
        self.assertEqual(run(["--drawer-set", str(broken)])[1], 2)
        self.assertEqual(run(["--drawer-set", a_file({"label": "x", "count": 1})])[1], 1)

    def test_labels_without_ascii_get_their_own_entries_and_a_retry_changes_nothing(self):
        write = a_file([{"label": "电阻", "count": 100}, {"label": "电容", "count": 50}])
        run(["--drawer-set", write])
        said, _ = run(["--drawer-set", write])
        self.assertEqual(sorted((e["label"], e["count"]) for e in run(["--drawer"])[0]["data"]["entries"]), [("电容", 50), ("电阻", 100)])
        self.assertEqual(said["data"]["changes"], [])

    def test_labels_equal_in_their_first_60_slug_characters_get_their_own_entries(self):
        run(["--drawer-set", a_file([{"label": "a" * 70 + "1", "count": 1}, {"label": "a" * 70 + "2", "count": 2}])])
        self.assertEqual(len(run(["--drawer"])[0]["data"]["entries"]), 2)

    def test_a_suffixed_record_is_a_question_even_through_an_id_token(self):
        (self.home / "catalog" / "sen0161-v2-ph-meter.json").write_text(json.dumps(
            {"schema": 1, "id": "sen0161-v2-ph-meter", "name": "pH meter", "kind": "sensor", "sku": "SEN0161-V2"}))
        said, _ = run(["--drawer-set", a_file([{"label": "ph", "count": 1, "part_number": {"number": "SEN0161"}}])])
        self.assertNotIn("is", self.entry("ph"))
        self.assertIn("sen0161-v2-ph-meter", said["data"]["questions"][0]["sentence"])

    def test_a_link_can_be_removed_and_stays_removed(self):
        run(["--drawer-set", a_file([{"label": "probe", "count": 8, "part_number": {"number": "SEN0193"}}])])
        said, _ = run(["--drawer-set", a_file([{"entry": "probe", "is": None}])])
        self.assertEqual(said["data"]["changes"], [{"entry": "probe", "new": False, "was": {"is": {"part": "sen0193-soil-moisture"}}, "now": {"is": None}}])
        run(["--drawer-set", a_file([{"entry": "probe", "count": 2}])])
        self.assertIsNone(self.entry("probe")["is"])

    def test_a_new_part_number_that_nothing_knows_drops_the_old_link(self):
        run(["--drawer-set", a_file([{"label": "probe", "count": 8, "part_number": {"number": "SEN0193"}}])])
        run(["--drawer-set", a_file([{"entry": "probe", "part_number": {"number": "ZZ999"}}])])
        self.assertNotIn("is", self.entry("probe"))

    def test_a_word_is_not_a_part_number(self):
        said, _ = run(["--drawer-set", a_file([{"label": "b", "count": 1, "part_number": {"number": "button"}}])])
        self.assertNotIn("is", self.entry("b"))
        self.assertEqual(said["data"]["questions"], [])

    def test_a_different_maker_makes_an_exact_number_a_question(self):
        said, _ = run(["--drawer-set", a_file([{"label": "p", "count": 1, "part_number": {"maker": "adafruit", "number": "SEN0193"}}])])
        self.assertNotIn("is", self.entry("p"))
        self.assertIn("sen0193-soil-moisture", said["data"]["questions"][0]["sentence"])

    def test_a_drawer_file_that_is_not_an_object_is_named(self):
        (self.home / "drawer").mkdir()
        (self.home / "drawer" / "x.json").write_text("[]")
        said, code = run(["--drawer"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("x.json", said["unchecked"][0]["sentence"])


if __name__ == "__main__":
    unittest.main()
