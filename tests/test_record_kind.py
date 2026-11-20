"""P724: RecordKind, the Strategy each kind of record is validated by: the shared checks, its rules in order, stop_after and owed."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core import outcomes  # noqa: E402
from spark.records.record_kind import (Answer, RecordKind, Validation, _cannot, _problem, feature_problems,  # noqa: E402
                                      picture_problems, type_problems)

PATH = Path("/nowhere/x.json")


def first_problems(record, validation):
    return ["first"]


def second_problems(record, validation):
    return ["second"]


def quiet_problems(record, validation):
    return []


def seen_problems(record, validation):
    """The validation a rule is given, as one problem, so a test reads it."""
    return [validation]


class RecordKindTest(unittest.TestCase):
    def kind(self, rules, stop_after=()):
        return RecordKind("thing", 1, ("schema", "id"), rules, stop_after)

    def test_a_record_that_holds_has_no_problem(self):
        self.assertEqual(self.kind([quiet_problems]).validate({"schema": 1, "id": "x"}, PATH), [])

    def test_the_shared_checks_come_first_then_each_rule_in_order(self):
        self.assertEqual(self.kind([second_problems, first_problems]).validate({"schema": 2}, PATH),
                         ["schema is 2, but this code understands only 1", "missing required key 'id'",
                          "second", "first"])

    def test_a_rule_in_stop_after_that_finds_a_problem_is_the_last_to_run(self):
        self.assertEqual(self.kind([first_problems, second_problems], stop_after=(first_problems,))
                         .validate({"schema": 1, "id": "x"}, PATH), ["first"])

    def test_a_rule_in_stop_after_that_finds_nothing_lets_the_next_run(self):
        self.assertEqual(self.kind([quiet_problems, second_problems], stop_after=(quiet_problems,))
                         .validate({"schema": 1, "id": "x"}, PATH), ["second"])

    def test_an_owed_key_skips_its_shared_check(self):
        kind = self.kind([])
        self.assertEqual(kind.validate({}, PATH, owed=("schema", "id")), [])
        self.assertEqual(kind.validate({}, PATH, owed=("schema",)), ["missing required key 'id'"])
        self.assertEqual(kind.validate({"schema": 2}, PATH, owed=("id",)), ["schema is 2, but this code understands only 1"])

    def test_each_rule_is_given_the_path_the_owed_keys_and_for_fab(self):
        found = self.kind([seen_problems]).validate({"schema": 1, "id": "x"}, PATH, owed=("id",), for_fab=True)
        self.assertEqual(found, [Validation(PATH, ("id",), True)])


class AnAnswerBecomesAResultTest(unittest.TestCase):
    """P726: `Answer.to_result` carries a handler's answer onto the core with parts.py's text rules, and `from_result` is
    the way back for a handler that runs an Operation on the core (`--needs-drop`)."""

    def test_each_item_is_a_finding_with_its_code_and_a_step_round_trips(self):
        step = outcomes.step("show", ["--show", "thing"], "to read the thing")
        answer = Answer({"x": 1}, ["  a line"], problems=[_problem("thing", "is wrong", "mend it")],
                        unchecked=[_cannot("could not read", code="file_refused")], next=[step])
        result = answer.to_result()
        self.assertEqual([(f.severity, f.subject, f.code, f.sentence, f.fix) for f in result.findings],
                         [("problems", "thing", None, "is wrong", "mend it"), ("could-not-run", None, "file_refused", "could not read", None)])
        self.assertEqual(result.to_envelope("parts", "show")["next"], [step])
        self.assertEqual(result.lines, ["  a line", "  thing: is wrong", "  fix for thing: mend it", "  could not check: could not read",
                                        "  next: parts.py --show thing — to read the thing"])
        back = Answer.from_result(result)
        self.assertEqual((back.problems, back.unchecked, back.next, back.data), (answer.problems, answer.unchecked, answer.next, answer.data))

    def test_an_answer_with_no_lines_says_its_refusals_on_stderr_with_the_fix_only_when_there_is_one(self):
        result = Answer(unchecked=[_cannot("nosuch is no matcher"), _cannot("a store refused", "fix the store")]).to_result()
        self.assertEqual((result.lines, result.diagnostics), ([], ["parts.py: nosuch is no matcher", "parts.py: a store refused — fix the store"]))
        self.assertEqual(result.status(), "could-not-run")

    def test_a_control_character_in_a_line_is_guarded_and_the_envelope_keeps_it_raw(self):
        result = Answer({"name": "x\x1b[31m"}, ["  x\x1b[31m"]).to_result()
        self.assertEqual((result.lines, result.data["name"]), (["  x?[31m"], "x\x1b[31m"))

    def test_a_code_is_in_an_item_only_when_given(self):
        self.assertEqual(_problem("s", "t"), {"subject": "s", "sentence": "t", "fix": None})
        self.assertEqual(_cannot("t", code="c"), {"sentence": "t", "fix": None, "code": "c"})


SHA = "a" * 64


def pictured(**block):
    """A part with one kept document and a breadboard-top picture of it, `block` changing the picture's fields."""
    picture = dict({"document": "photo", "made_by": "photo", "likeness": "near", "credit": "the PO's photo", "verified": False},
                   **block)
    return {"body_mm": {"width": 85, "height": 44, "verified": False}, "documents": {
        "photo": {"url": None, "file": "photo.svg", "sha256": SHA}, "page": {"url": "https://example.org/a", "kept": False}},
        "pictures": {"breadboard-top": picture}}


class APartsPicturesTest(unittest.TestCase):
    """P946: a part record's `pictures`, one block per view, each pointing at a kept document."""

    def test_pictures_is_an_object_of_objects(self):
        self.assertEqual(type_problems({"pictures": {"breadboard-top": "x.svg"}}),
                         ["pictures.breadboard-top is 'x.svg', but it is an object"])
        self.assertEqual(type_problems({"pictures": ["x.svg"]}), ["pictures is ['x.svg'], but it is an object"])
        self.assertEqual(type_problems(pictured()), [])

    def test_a_picture_that_holds_has_no_problem(self):
        self.assertEqual(picture_problems(pictured()), [])
        self.assertEqual(picture_problems({}), [])
        verified = pictured(verified=True)
        verified["body_mm"]["verified"] = True
        self.assertEqual(picture_problems(verified), [])

    def test_each_picture_problem(self):
        cases = {
            "an unknown view": ({"pictures": {"breadboard-back": pictured()["pictures"]["breadboard-top"]}},
                                "pictures.breadboard-back is no view spark draws (breadboard-top)"),
            "a document not listed": ({"document": "other"}, "pictures.breadboard-top.document is 'other', which documents does not hold"),
            "a document not kept": ({"document": "page"}, "pictures.breadboard-top.document is 'page', which is not kept in the store"),
            "a likeness not in the list": ({"likeness": "perfect"}, "pictures.breadboard-top.likeness is 'perfect', but it is one of exact, near, rough"),
            "an empty credit": ({"credit": ""}, "pictures.breadboard-top.credit is '', but it says who made the picture"),
            "a made_by that is no string": ({"made_by": 3}, "pictures.breadboard-top.made_by is 3, but it names the maker"),
            "verified that is no bool": ({"verified": "no"}, "pictures.breadboard-top.verified is 'no', but it is true or false"),
            "verified over a size not verified": ({"verified": True}, "pictures.breadboard-top.verified is true, but body_mm is not verified"),
        }
        for name, (change, problem) in cases.items():
            with self.subTest(name):
                part = dict(pictured(), **change) if "pictures" in change else pictured(**change)
                self.assertEqual(picture_problems(part), [problem])

    def test_two_broken_views_are_both_named(self):
        part = pictured()
        part["pictures"]["side"] = part["pictures"]["breadboard-top"]
        part["pictures"]["back"] = part["pictures"]["breadboard-top"]
        self.assertEqual(len(picture_problems(part)), 2)


def _feature(**changed):
    """A good measured feature (P956) with `changed` set."""
    return dict({"name": "MCU", "kind": "chip", "x": 1.0, "y": 2.0, "w": 3.0, "h": 4.0, "colour": "#838383",
                 "verified": False, "source": "measured by the suite"}, **changed)


def _problems(*features, colour=None):
    physical = dict({"features": list(features)}, **({"colour": colour} if colour is not None else {}))
    return feature_problems({"physical": physical})


class FeatureProblemsTest(unittest.TestCase):
    """P956: a record's measured features and its colour hold their shape, each problem naming the feature."""

    def test_each_broken_field_is_named_with_the_feature(self):
        label = _feature(name="WORD", kind="label", text="SPARK")
        no_text = {key: value for key, value in label.items() if key != "text"}
        kinds = "chip, usb, button, led, jst, fpc, connector, crystal, inductor, passives, hole, label"
        for case, found, wanted in (
                ("a good chip and a label", _problems(_feature(), label), []),
                ("a kind outside the list", _problems(_feature(kind="robot")),
                 ["physical.features[0] (MCU) is of kind 'robot', which is none of %s" % kinds]),
                ("a colour that is no hex", _problems(_feature(colour="grey")),
                 ["physical.features[0] (MCU) has colour 'grey', but it is #rrggbb in lower case"]),
                ("an upper-case hex", _problems(_feature(colour="#83838A")),
                 ["physical.features[0] (MCU) has colour '#83838A', but it is #rrggbb in lower case"]),
                ("two features of one name", _problems(_feature(), _feature()),
                 ["physical.features[1] (MCU) has the name of a feature before it: each name is one feature's"]),
                ("a label with no text", _problems(no_text),
                 ["physical.features[0] (WORD) has text None, but a label holds a text of 1 to 24 characters"]),
                ("a label over 24 characters", _problems(dict(label, text="X" * 25)),
                 ["physical.features[0] (WORD) has text '%s', but a label holds a text of 1 to 24 characters" % ("X" * 25)]),
                ("a size of nothing", _problems(_feature(w=0)), ["physical.features[0] (MCU) has w 0, but it is above 0"]),
                ("a size that is text", _problems(_feature(x="1")), ["physical.features[0] (MCU) has x '1', but it is a number of mm"]),
                ("a size that is a bool", _problems(_feature(h=True)), ["physical.features[0] (MCU) has h True, but it is a number of mm"]),
                ("no source", _problems(_feature(source=" ")), ["physical.features[0] (MCU) has no source: it says who measured it, on what"]),
                ("verified as text", _problems(_feature(verified="no")),
                 ["physical.features[0] (MCU) has verified 'no', but it is true or false"]),
                ("leads of a sort no chip has", _problems(_feature(leads="six")),
                 ["physical.features[0] (MCU) has leads 'six', but they are one of four, top-bottom, left-right, none"]),
                ("a count on a chip", _problems(_feature(count=2)),
                 ["physical.features[0] (MCU) holds count, which only a passives or fpc or jst holds"]),
                ("a count of nothing", _problems(_feature(kind="jst", count=0)),
                 ["physical.features[0] (MCU) has count 0, but it is a whole number above 0"]),
                ("a field no feature has", _problems(_feature(url="x")), ["physical.features[0] (MCU) holds url, which is no field of a feature"]),
                ("features that are no list", feature_problems({"physical": {"features": {}}}), ["physical.features is {}, but it is a list of features"]),
                ("a feature that is no object", _problems("chip"), ["physical.features[0] is 'chip', but a feature is an object"]),
                ("a board colour with no source", _problems(colour={"value": "#040404", "verified": False}),
                 ["physical.colour is {'value': '#040404', 'verified': False}, but it is {value: #rrggbb in lower case, verified, source}"]),
                ("no physical block", feature_problems({}), [])):
            with self.subTest(case):
                self.assertEqual(found, wanted)

    def test_board_and_part_rules_both_run_feature_problems(self):
        """The board's rules run it (P956); a module's record holds no features in this version, so its rules refuse the key."""
        import json
        from spark.records import board_records
        from spark.sourcing import part_records
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        board["physical"]["features"] = [_feature(kind="robot")]
        self.assertIn("physical.features[0] (MCU) is of kind 'robot', which is none of chip, usb, button, led, jst, fpc, "
                      "connector, crystal, inductor, passives, hole, label", board_records.validate(board, ROOT / "boards" / "x.json"))
        part = json.loads((ROOT / "tests" / "data" / "breadboard" / "epaper" / "parts" / "epaper-2in9-bwr-mh-et-live.json").read_text())
        part["physical"]["features"] = [_feature()]
        self.assertTrue([problem for problem in part_records.validate(part, ROOT / "parts" / "x.json") if "features" in problem])


if __name__ == "__main__":
    unittest.main()
