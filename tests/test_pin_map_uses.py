"""
The pin names a project's firmware uses, read against its pin map (P882, #1250): `spark.firmware.pin_map_uses.PinMapUses`.

    python3 -m unittest tests.test_pin_map_uses

Each test makes a small project in the suite's temp folder from literal sources. The Value reads with `ast` and runs nothing.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.firmware.pin_map_uses import PinMapUses  # noqa: E402

MAIN = "import pins\nfrom machine import Pin\nPin(pins.JOY_SW)\n"


def a_project(files, pins="LED = 2\n"):
    """A project whose firmware/ holds FILES ({"main.py": source}, a path may have a folder) and `pins.py` with source PINS
    (None leaves it out; `files` None leaves firmware/ out). Returns the project."""
    project = Path(tempfile.mkdtemp()) / "project"
    project.mkdir()
    if files is None:
        return project
    for name, source in dict(files, **({} if pins is None else {"pins.py": pins})).items():
        (project / "firmware" / name).parent.mkdir(parents=True, exist_ok=True)
        (project / "firmware" / name).write_text(source)
    (project / "firmware").mkdir(exist_ok=True)
    return project


def read(files, **keywords):
    return PinMapUses.read(a_project(files, **keywords))


def missing_of(uses):
    return [(each.name, each.file, each.line) for each in uses.missing]


def places_of(uses):
    return [(each.file, each.line) for each in uses.places]


class WhatAUseIsTest(unittest.TestCase):
    def test_a_name_the_map_lacks_is_missing_with_its_file_and_line(self):
        uses = read({"main.py": MAIN})
        self.assertEqual((uses.state, uses.used, missing_of(uses)), ("recorded", 1, [("JOY_SW", "firmware/main.py", 3)]))

    def test_names_that_all_exist_give_nothing(self):
        uses = read({"main.py": MAIN}, pins="JOY_SW = 4\n")
        self.assertEqual((uses.state, uses.used, uses.missing, uses.places), ("recorded", 1, (), ()))

    def test_used_counts_uses_not_names(self):
        uses = read({"main.py": "import pins\nx = (pins.LED, pins.LED)\ny = pins.LED\n"})
        self.assertEqual(uses.used, 2)

    def test_a_name_in_a_module_function_is_compared(self):
        uses = read({"ui.py": "import pins\n\ndef run():\n    return pins.JOY_SW\n"})
        self.assertEqual(missing_of(uses), [("JOY_SW", "firmware/ui.py", 4)])

    def test_the_alias_of_import_as_is_the_name_that_is_read(self):
        uses = read({"main.py": "import pins as p\nx = p.JOY_SW\ny = pins.OTHER\n"})
        self.assertEqual(missing_of(uses), [("JOY_SW", "firmware/main.py", 2)])

    def test_from_import_compares_each_name_at_the_import_line(self):
        uses = read({"main.py": "from pins import LED, JOY_SW as J\n"})
        self.assertEqual((uses.used, missing_of(uses)), (2, [("JOY_SW", "firmware/main.py", 1)]))
        self.assertTrue(uses.missing[0].imported)

    def test_a_from_import_is_compared_when_the_file_binds_the_name_again(self):
        uses = read({"main.py": "from pins import LED\nLED = Pin(LED, Pin.OUT)\n"}, pins="LED = 2\n")
        self.assertEqual((uses.used, uses.missing, uses.places), (1, (), ()))
        uses = read({"main.py": "from pins import JOY\nJOY = Pin(JOY, Pin.OUT)\n"})
        self.assertEqual(missing_of(uses), [("JOY", "firmware/main.py", 1)])

    def test_a_dunder_is_no_pin_name(self):
        uses = read({"main.py": "import pins\nprint(pins.__name__)\n"})
        self.assertEqual((uses.used, uses.places), (0, ()))

    def test_a_file_in_a_folder_is_named_with_the_folder(self):
        uses = read({"app/ui.py": "import pins\nx = pins.NOPE\n"})
        self.assertEqual(missing_of(uses), [("NOPE", "firmware/app/ui.py", 2)])

    def test_a_firmware_that_uses_no_pin_name_is_recorded_with_none(self):
        uses = read({"main.py": "print('ready')\n"})
        self.assertEqual((uses.state, uses.used, uses.missing, uses.places), ("recorded", 0, (), ()))


class WhatTheCheckDoesNotCompareTest(unittest.TestCase):
    """A use the check cannot compare is a place, and it says so."""

    def test_from_import_star_is_a_place(self):
        uses = read({"main.py": "from pins import *\n"})
        self.assertEqual((places_of(uses), uses.used), ([("firmware/main.py", 1)], 0))
        self.assertEqual(uses.assumptions(),
                         ["not checked: firmware/main.py:1 takes every name of pins.py with *, so the names it uses are not compared"])

    def test_the_module_alias_used_as_a_value_is_a_place(self):
        for source in ("p = pins\n", 'x = getattr(pins, "X")\n', "f(pins)\n", "pins.X = 1\n", "del pins.X\n", 'hasattr(pins, "X")\n'):
            with self.subTest(source=source):
                uses = read({"main.py": "import pins\n" + source})
                self.assertEqual((places_of(uses), uses.used), ([("firmware/main.py", 2)], 0))
                self.assertIn("uses the pin map as a value, so the names it reaches are not compared", uses.assumptions()[0])

    def test_a_module_alias_that_the_file_binds_another_way_is_one_place_at_the_import(self):
        uses = read({"main.py": "import pins\n\ndef run(pins):\n    return pins.NOPE\n"})
        self.assertEqual((places_of(uses), uses.used, uses.missing), ([("firmware/main.py", 1)], 0, ()))
        self.assertEqual(uses.assumptions(), ["not checked: firmware/main.py:1 also uses the name pins for something else "
                                              "(line 3), so its pin names are not compared"])

    def test_only_the_alias_that_is_rebound_loses_its_names(self):
        uses = read({"main.py": "import pins\nimport pins as p\np = 3\nx = pins.NOPE\n"})
        self.assertEqual(missing_of(uses), [("NOPE", "firmware/main.py", 4)])
        self.assertEqual(places_of(uses), [("firmware/main.py", 2)])

    def test_a_place_is_counted_once_per_line_and_form(self):
        uses = read({"main.py": "import pins\nf(pins, pins)\n"})
        self.assertEqual(places_of(uses), [("firmware/main.py", 2)])

    def test_a_name_the_file_guards_with_hasattr_or_getattr_is_a_place_not_a_missing_use(self):
        for guard in ('hasattr(pins, "X")', 'getattr(pins, "X", None)'):
            with self.subTest(guard=guard):
                uses = read({"main.py": "import pins\nif %s:\n    y = pins.X\n" % guard})
                self.assertEqual((uses.missing, places_of(uses)), ((), [("firmware/main.py", 2)]))

    def test_forms_the_check_does_not_see_give_nothing(self):
        for source in ("import pins.x\nx = pins.NOPE\n", "from .pins import NOPE\n", 'm = __import__("pins")\nm.NOPE\n'):
            with self.subTest(source=source):
                uses = read({"main.py": source})
                self.assertEqual((uses.state, uses.used, uses.missing, uses.places), ("recorded", 0, (), ()))


class TheMapTest(unittest.TestCase):
    def test_a_name_bound_in_an_if_at_module_level_counts(self):
        uses = read({"main.py": "import pins\nx = pins.A\ny = pins.B\n"}, pins="import sys\nif sys.platform:\n    A = 1\nelse:\n    (B, C) = 1, 2\n")
        self.assertEqual((uses.used, uses.missing), (2, ()))

    def test_a_name_bound_in_a_def_of_the_map_does_not_count(self):
        uses = read({"main.py": "import pins\nx = pins.INNER\n"}, pins="def f():\n    INNER = 1\n    return INNER\n")
        self.assertEqual(missing_of(uses), [("INNER", "firmware/main.py", 2)])

    def test_a_def_a_class_and_an_import_at_module_level_count(self):
        uses = read({"main.py": "import pins\nx = (pins.f, pins.C, pins.sqrt, pins.m)\n"},
                    pins="def f():\n    pass\nclass C:\n    pass\nfrom math import sqrt\nimport math as m\n")
        self.assertEqual((uses.used, uses.missing), (4, ()))

    def test_the_names_of_the_map_are_a_field_for_the_next_card(self):
        uses = read({"main.py": "print('x')\n"}, pins="LED = 2\nJOY = 3\n")
        self.assertEqual(uses.names, ("JOY", "LED"))

    def test_an_open_map_is_not_checked(self):
        for source in ("from x import *\n", "def __getattr__(name):\n    return 1\n"):
            with self.subTest(source=source):
                uses = read({"main.py": MAIN}, pins=source)
                self.assertEqual(uses.state, "not-checked")
                self.assertIn("firmware/pins.py", uses.why)
                self.assertEqual(uses.where, "firmware/pins.py")

    def test_a_map_that_does_not_parse_is_not_checked_and_names_the_line(self):
        uses = read({"main.py": MAIN}, pins="LED = 2\nJOY = (\n")
        self.assertEqual(uses.state, "not-checked")
        self.assertIn("firmware/pins.py", uses.why)
        self.assertIn("line 2", uses.why)

    def test_no_pin_map_while_a_file_uses_pins_makes_each_use_missing(self):
        uses = read({"main.py": MAIN + "x = pins.LED\n"}, pins=None)
        self.assertEqual((uses.state, uses.has_map, uses.used, len(uses.missing)), ("recorded", False, 2, 2))

    def test_no_pin_map_and_no_use_is_recorded_with_none(self):
        uses = read({"main.py": "print('x')\n"}, pins=None)
        self.assertEqual((uses.state, uses.used, uses.missing), ("recorded", 0, ()))


class TheFilesTest(unittest.TestCase):
    def test_a_file_that_does_not_parse_is_not_checked_and_names_the_file_and_line(self):
        uses = read({"main.py": MAIN, "ui.py": "x = 1\ndef (:\n"})
        self.assertEqual(uses.state, "not-checked")
        self.assertEqual(uses.where, "firmware/ui.py")
        self.assertIn("firmware/ui.py", uses.why)
        self.assertIn("line 2", uses.why)

    def test_lib_and_the_secrets_files_are_left_out(self):
        uses = read({"lib/drv.py": "import pins\nx = pins.NOPE\n", "wifi_secrets.py": "import pins\nx = pins.NOPE\n",
                     "lib/bad.py": "def (:\n"})
        self.assertEqual((uses.state, uses.used, uses.places), ("recorded", 0, ()))

    def test_a_secrets_file_in_a_folder_is_read_as_the_rule_says(self):
        # is_secret_path names only the files directly in firmware/
        uses = read({"app/my_secret.py": "import pins\nx = pins.NOPE\n"})
        self.assertEqual(missing_of(uses), [("NOPE", "firmware/app/my_secret.py", 2)])

    def test_it_runs_nothing(self):
        marker = Path(tempfile.mkdtemp()) / "ran"
        project = a_project({"main.py": "raise SystemExit(3)\nimport pins\nx = pins.NOPE\n"},
                            pins="open(%r, 'w').write('x')\nLED = 2\n" % str(marker))
        uses = PinMapUses.read(project)
        self.assertEqual(missing_of(uses), [("NOPE", "firmware/main.py", 3)])
        self.assertFalse(marker.exists())

    def test_no_firmware_folder_is_not_checked(self):
        uses = read(None)
        self.assertEqual(uses.state, "not-checked")
        self.assertIn("firmware/", uses.why)


class TheDataAndTheLineTest(unittest.TestCase):
    def test_the_data_holds_the_uses_and_the_places(self):
        uses = read({"main.py": "import pins\nx = pins.JOY\nf(pins)\n"})
        self.assertEqual(uses.to_data(), {"state": "recorded", "used": 1,
                                          "missing": [{"name": "JOY", "file": "firmware/main.py", "line": 2}],
                                          "not_compared": [{"file": "firmware/main.py", "line": 3,
                                                            "form": "uses the pin map as a value, so the names it reaches are not compared"}],
                                          "names": ["LED"]})

    def test_the_data_of_a_map_that_was_not_read_holds_only_why(self):
        uses = read(None)
        self.assertEqual(uses.to_data(), {"state": "not-checked", "why": uses.why})

    def test_the_line_says_what_was_found_and_what_was_not(self):
        data = {"state": "recorded", "used": 5, "missing": [{"name": "JOY_SW", "file": "firmware/main.py", "line": 12}], "not_compared": []}
        self.assertEqual(PinMapUses.line_from(data),
                         "pin map: 4 of 5 uses found in firmware/pins.py, not found: JOY_SW (firmware/main.py:12)")
        data["missing"].append({"name": "B", "file": "firmware/ui.py", "line": 3})
        self.assertEqual(PinMapUses.line_from(data),
                         "pin map: 3 of 5 uses found in firmware/pins.py, not found: JOY_SW (firmware/main.py:12), B (firmware/ui.py:3)")

    def test_all_found_gives_the_found_part_alone(self):
        data = {"state": "recorded", "used": 2, "missing": [], "not_compared": []}
        self.assertEqual(PinMapUses.line_from(data), "pin map: 2 of 2 uses found in firmware/pins.py")

    def test_nothing_compared_is_none_compared_never_0_of_0(self):
        place = {"file": "firmware/main.py", "line": 1, "form": "x"}
        data = {"state": "recorded", "used": 0, "missing": [], "not_compared": [place]}
        self.assertEqual(PinMapUses.line_from(data), "pin map: none compared, not compared in 1 place, first firmware/main.py:1")

    def test_places_are_counted_and_the_first_is_named(self):
        places = [{"file": "firmware/main.py", "line": 1, "form": "x"}, {"file": "firmware/ui.py", "line": 9, "form": "y"}]
        data = {"state": "recorded", "used": 1, "missing": [], "not_compared": places}
        self.assertEqual(PinMapUses.line_from(data),
                         "pin map: 1 of 1 uses found in firmware/pins.py, not compared in 2 places, first firmware/main.py:1")

    def test_with_no_pin_map_the_line_says_it_is_not_there(self):
        uses = read({"main.py": MAIN + "x = pins.LED\n"}, pins=None)
        self.assertEqual(uses.to_data()["has_map"], False)
        self.assertEqual(PinMapUses.line_from(uses.to_data()),
                         "pin map: firmware/pins.py is not there, and 2 uses need it, first firmware/main.py:3")
        one = read({"main.py": MAIN}, pins=None).to_data()
        self.assertEqual(PinMapUses.line_from(one), "pin map: firmware/pins.py is not there, and 1 use needs it, first firmware/main.py:3")
        self.assertEqual(PinMapUses.line_from(one, missing_only=True), PinMapUses.line_from(one))

    def test_a_map_that_is_there_keeps_the_data_as_it_was(self):
        self.assertNotIn("has_map", read({"main.py": MAIN}).to_data())

    def test_a_firmware_with_no_use_and_no_place_has_no_line(self):
        self.assertIsNone(PinMapUses.line_from({"state": "recorded", "used": 0, "missing": [], "not_compared": []}))

    def test_a_map_that_was_not_read_says_why(self):
        self.assertEqual(PinMapUses.line_from({"state": "not-checked", "why": "firmware/ui.py does not parse (line 2)"}),
                         "pin map: not checked (firmware/ui.py does not parse (line 2))")

    def test_a_file_name_with_a_newline_prints_on_one_line(self):
        data = {"state": "recorded", "used": 1, "missing": [{"name": "A", "file": "firmware/a\nb.py", "line": 1}], "not_compared": []}
        self.assertNotIn("\n", PinMapUses.line_from(data))

    def test_missing_only_gives_a_line_only_when_a_name_is_missing(self):
        found = {"state": "recorded", "used": 2, "missing": [], "not_compared": []}
        lacks = dict(found, missing=[{"name": "A", "file": "firmware/a.py", "line": 1}])
        self.assertIsNone(PinMapUses.line_from(found, missing_only=True))
        self.assertIsNone(PinMapUses.line_from({"state": "not-checked", "why": "x"}, missing_only=True))
        self.assertEqual(PinMapUses.line_from(lacks, missing_only=True), PinMapUses.line_from(lacks))

    def test_any_other_shape_gives_none_and_never_raises(self):
        good = {"state": "recorded", "used": 1, "missing": [{"name": "A", "file": "firmware/a.py", "line": 1}], "not_compared": []}
        odd = [None, [], "x", 3, {}, {"state": "recorded"}, {"state": "other"}, {"state": "not-checked"}, {"state": "not-checked", "why": 3},
               dict(good, used="1"), dict(good, used=True), dict(good, used=-1), dict(good, used=0), dict(good, missing="A"), dict(good, missing=[1]),
               dict(good, missing=[{"name": "A"}]), dict(good, missing=[{"name": "A", "file": "f", "line": "1"}]),
               dict(good, missing=[{"name": 1, "file": "f", "line": 1}]), dict(good, not_compared="x"), dict(good, not_compared=[None]),
               dict(good, not_compared=[{"file": "f", "line": 1}]), {k: v for k, v in good.items() if k != "not_compared"}]
        for data in odd:
            for only in (False, True):
                with self.subTest(data=data, only=only):
                    self.assertIsNone(PinMapUses.line_from(data, missing_only=only))
        self.assertIsNotNone(PinMapUses.line_from(good))


class TheNamesSinceTest(unittest.TestCase):
    """changed_since: the names of the map now against the names an earlier record kept (P1270)."""

    @staticmethod
    def now(*names):
        return read({"main.py": "x = 1\n"}, pins="".join("%s = 2\n" % each for each in names))

    def test_a_gained_name_is_gained(self):
        self.assertEqual(self.now("LED", "JOY_SW").changed_since({"names": ["LED"]}), (("JOY_SW",), ()))

    def test_a_lost_name_is_lost(self):
        self.assertEqual(self.now("LED").changed_since({"names": ["LED", "LED2"]}), ((), ("LED2",)))

    def test_the_same_names_give_no_change(self):
        self.assertEqual(self.now("LED", "B").changed_since({"names": ["B", "LED"]}), ((), ()))

    def test_kept_data_with_no_list_of_names_gives_none(self):
        uses = self.now("LED")
        for kept in (None, {}, {"names": [1]}, {"names": "LED"}, {"state": "recorded", "used": 1}):
            self.assertIsNone(uses.changed_since(kept), kept)

    def test_a_value_with_no_map_gives_none(self):
        self.assertIsNone(read(None).changed_since({"names": ["LED"]}))
        self.assertIsNone(PinMapUses.read(a_project({"main.py": "x = 1\n"}, pins=None)).changed_since({"names": ["LED"]}))

    def test_the_answer_is_sorted(self):
        self.assertEqual(self.now("Z", "A", "M").changed_since({"names": ["Q", "B"]}), (("A", "M", "Z"), ("B", "Q")))


class TheFindingsSentencesTest(unittest.TestCase):
    def test_the_sentence_of_each_missing_use(self):
        uses = read({"main.py": "import pins\nfrom pins import GONE\nx = pins.JOY_SW\n"})
        self.assertEqual([each.sentence() for each in uses.missing],
                         ["firmware/main.py:2 imports GONE from pins, and firmware/pins.py has no GONE",
                          "firmware/main.py:3 uses pins.JOY_SW, and firmware/pins.py has no JOY_SW"])


if __name__ == "__main__":
    unittest.main()
