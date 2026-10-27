"""P211: the matching library — offers, fits and the three matchers (docs/2026-10-12-p211-matching-design.md)."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import matching  # noqa: E402

SENSE = {"does": "sense", "what": "range"}


def an_offer(**said):
    return matching.Offer(said.pop("key", "x"), said.pop("kind", "entry"), **said)


class TheWordsTest(unittest.TestCase):
    def test_digits_are_word_characters(self):
        self.assertEqual(matching.words("VL6180X 3V3"), ["vl6180x", "3v3"])

    def test_the_plural_fold(self):
        self.assertEqual([matching.fold(w) for w in ("sensors", "gps", "bus", "glass", "status", "leds")],
                         ["sensor", "gps", "bus", "glass", "status", "led"])

    def test_filler_words_go_and_each_word_counts_once(self):
        self.assertEqual(matching.need_words("The sensors for a range, range"), ["sensor", "range"])


class TheOfferTest(unittest.TestCase):
    def test_a_tag_is_cleaned_of_control_and_bidi_characters_and_capped(self):
        offer = an_offer(tags=["Knob\u202eDial\x00", "x" * 200])
        self.assertEqual(offer.tags, ["knob dial", "x" * 160])

    def test_a_board_does_what_its_kind_says(self):
        offer = matching.Offer.from_record("fb", "board", {"name": "FireBeetle"})
        self.assertEqual(offer.functions, [{"does": "compute", "what": "microcontroller"}])

    def test_a_board_offers_what_its_own_parts_do(self):
        record = {"name": "XIAO", "pin_roles": {"onboard_led": {"gpio": [15], "note": "x"}, "onboard_button": {"gpio": [9], "note": "x"}}}
        offer = matching.Offer.from_record("xiao", "board", record)
        self.assertEqual(offer.functions, [{"does": "compute", "what": "microcontroller"},
                                           {"does": "indicate", "what": "onboard LED light", "role": "onboard_led"},
                                           {"does": "input", "what": "onboard button", "role": "onboard_button"}])
        self.assertNotIn("role", json.dumps(offer.as_dict()), "the role is for the pick (P397), never for a chooser or a JSON")
        self.assertNotIn("role", offer.describe())
        for what in ("light", "led", "onboard LED light"):
            with self.subTest(what=what):
                self.assertTrue(matching.same_words({"does": "indicate", "what": what}, offer))
        self.assertFalse(matching.same_words({"does": "sense", "what": "light"}, offer), "the verb must be the need's")

    def test_a_board_offers_its_power_parts_for_the_words_of_each_and_for_no_others(self):
        fact = {"value": "x", "verified": True, "source": "s"}
        record = {"name": "T-Display", "power": {"charger": fact, "regulator": fact, "battery_input": fact},
                  "pin_roles": {"onboard_battery_sense": {"gpio": [34], "note": "x"}}}
        offer = matching.Offer.from_record("t", "board", record)
        for does, what in (("power", "charger"), ("power", "voltage regulator"), ("connect", "battery input"),
                           ("sense", "battery level"), ("sense", "battery"), ("power", "onboard charger")):
            with self.subTest(need=(does, what)):
                self.assertTrue(matching.same_words({"does": does, "what": what}, offer))
        for does, what in (("power", "battery"), ("power", "battery charger"), ("sense", "voltage"), ("connect", "charger")):
            with self.subTest(need=(does, what)):
                self.assertFalse(matching.same_words({"does": does, "what": what}, offer))

    def test_a_part_record_with_pin_roles_offers_nothing_of_a_board(self):
        offer = matching.Offer.from_record("x", "part", {"kind": "rtc", "pin_roles": {"onboard_led": {"gpio": [2], "note": "x"}}})
        self.assertEqual(offer.functions, [{"does": "keep-time", "what": "rtc"}])

    def test_entries_pointing_at_a_record_join_it_and_the_record_s_own_text_wins(self):
        record = {"name": "VL6180X", "kind": "rangefinder", "about": "Ranges.", "power": {"v": 3.3}}
        holding = [{"function": [{"does": "sense", "what": "range"}], "about": "Mine.", "tags": ["tof"]}]
        offer = matching.Offer.from_record("vl", "part", record, holding)
        self.assertEqual((offer.about, offer.tags, offer.facts),
                         ("Ranges.", ["tof"], {"kind": "rangefinder", "power": {"v": 3.3}}))
        self.assertIn({"does": "sense", "what": "range"}, offer.functions)

    def test_a_draft_is_its_id_alone(self):
        offer = matching.Offer.from_record("vl6180x", "part", {})
        self.assertEqual((offer.functions, offer.names, offer.about), ([], [], None))

    def test_an_entry_s_label_is_its_name(self):
        offer = matching.Offer.from_entry("k", {"label": "a knob"})
        self.assertEqual(offer.names, ["a knob"])
        self.assertTrue(matching.same_words({"does": "input", "what": "knob"}, offer), "a name counts whatever the verb")

    def test_a_malformed_text_is_ignored(self):
        offer = matching.Offer.from_entry("k", {"label": "a knob", "about": 5, "tags": "knob", "description": ["x"]})
        self.assertEqual((offer.about, offer.description, offer.tags), (None, None, []))

    def test_the_texts_are_capped(self):
        offer = an_offer(about="a" * 300, description="d" * 1500, tags=["t%d" % n for n in range(20)])
        self.assertEqual((len(offer.about), len(offer.description), len(offer.tags)), (200, 1000, 12))

    def test_describe_cleans_what_a_record_says_and_leaves_out_what_it_lacks(self):
        offer = matching.Offer.from_record("vl", "part", {"name": "VL", "about": "Ranges\u202e far.", "body_mm": {"width": 20, "height": 15},
                                                          "power": {"note": "3V3\u202e only"}})
        text = offer.describe()
        self.assertIn("about: Ranges  far.", text)
        self.assertIn('body_mm: {"width": 20, "height": 15}', text)
        self.assertNotIn("description", text)
        self.assertNotIn("\u202e", text)


class TheOfferJsonTest(unittest.TestCase):
    def test_as_dict_gives_the_cleaned_capped_text_that_describe_prints(self):
        note = "3V3\u202e only " + "x" * 5000
        offer = matching.Offer.from_record("fb", "board", {"name": "FB", "kind": "board", "power": {"note": note}, "body_mm": {"width": 20}})
        facts = offer.as_dict()["facts"]
        self.assertEqual((len(facts["power"]), facts["body_mm"], facts["kind"]), (1000, '{"width": 20}', "board"))
        self.assertIn("power: " + facts["power"], offer.describe(), "one text, built once, for the lines and for the JSON")
        self.assertLess(len(json.dumps(offer.as_dict())), 3400)
        self.assertNotIn("\u202e", json.dumps(offer.as_dict(), ensure_ascii=False))

    def test_as_dict_cleans_what_it_does_and_keeps_the_shape(self):
        offer = an_offer(functions=[{"does": "sense", "what": "ran\u202ege"}])
        self.assertEqual(offer.as_dict()["functions"], [{"does": "sense", "what": "ran ge"}])
        self.assertIn("does: sense ran ge", offer.describe())


class TheMatchersTest(unittest.TestCase):
    #: The score of named pairs: a change of weights shows here (the spec, "How WordOverlap scores", step 5).
    SCORES = (
        ("range", dict(functions=[{"does": "sense", "what": "range"}]), 1.0),
        ("range", dict(functions=[{"does": "sense", "what": "x"}], tags=["range"]), 0.8),
        ("range", dict(functions=[{"does": "sense", "what": "x"}], names=["Range finder"]), 0.6),
        ("range", dict(key="range-x", functions=[{"does": "sense", "what": "x"}]), 0.6),
        ("range", dict(functions=[{"does": "sense", "what": "x"}], about="It finds the range."), 0.4),
        ("laser range", dict(functions=[{"does": "sense", "what": "distance"}], tags=["laser"]), 0.4),
        ("the sensors", dict(functions=[{"does": "sense", "what": "x"}], tags=["sensor"]), 0.8),
        ("range", dict(functions=[{"does": "sense", "what": "x"}, {"does": "input", "what": "range"}]), 0.0),
        ("sensor", dict(functions=[{"does": "sense", "what": "x"}], tags=["sensors"]), 0.8),  # the offer's plural folds too
        ("leds", dict(functions=[{"does": "sense", "what": "x"}], names=["LEDs"]), 0.6),
        ("range", dict(functions=[{"does": "sense", "what": "x"}], description="It finds the range."), 0.4),
    )

    def test_word_overlap_scores_the_named_pairs(self):
        for what, said, score in self.SCORES:
            with self.subTest(what=what, said=said):
                fit = matching.WordOverlap().score({"does": "sense", "what": what}, an_offer(**said))
                self.assertEqual(fit.score, score)

    def test_a_need_of_only_filler_scores_zero(self):
        offer = an_offer(functions=[{"does": "sense", "what": "the"}])
        for what in ("of the", "--", ""):
            with self.subTest(what=what):
                need = {"does": "sense", "what": what}
                self.assertEqual((matching.WordOverlap().score(need, offer).score, matching.same_words(need, offer)), (0.0, False))

    def test_word_overlap_says_why(self):
        fit = matching.WordOverlap().score({"does": "sense", "what": "laser range"},
                                           an_offer(functions=[{"does": "sense", "what": "range"}], tags=["laser"]))
        self.assertEqual(fit.why, ["laser: in tags", "range: in functions"])

    def test_same_words_is_the_old_rule(self):
        offer = an_offer(functions=[{"does": "sense", "what": "soil-moisture"}], names=["A probe"])
        self.assertTrue(matching.same_words({"does": "sense", "what": "soil moisture"}, offer))
        self.assertFalse(matching.same_words({"does": "sense", "what": "moisture probe"}, offer))
        self.assertFalse(matching.same_words({"does": "input", "what": "soil-moisture"}, offer))
        self.assertTrue(matching.same_words({"does": "input", "what": "probe"}, offer), "a name counts whatever the verb")

    def test_exact_is_same_words_whatever_matcher_runs(self):
        offer = an_offer(functions=[{"does": "sense", "what": "range"}])
        self.assertTrue(matching.WordOverlap().score(SENSE, offer).exact)

    def test_the_default_admits_only_the_need_s_verb_unless_the_need_has_none(self):
        offer = an_offer(functions=[{"does": "input", "what": "range"}])
        self.assertEqual(matching.SameWords().rank(SENSE, [offer]), [])
        self.assertEqual(len(matching.SameWords().rank({"does": None, "what": "range"}, [offer])), 1)

    def test_name_contains_finds_a_part_of_a_word_and_admits_every_offer(self):
        offer = matching.Offer.from_record("vl6180x-breakout", "part", {"name": "VL6180X", "kind": "rangefinder"})
        need = {"does": None, "what": "vl6180 rangefinder"}
        self.assertEqual(matching.NameContains().score(need, offer).score, 1.0)
        self.assertEqual(matching.NameContains().score({"does": None, "what": "lidar"}, offer).score, 0.0)
        self.assertTrue(matching.NameContains().admits({"does": "input", "what": "x"}, offer), "a search word has no verb")

    def test_name_contains_needs_every_typed_word(self):
        offer = matching.Offer.from_record("vl6180x-breakout", "part", {"name": "VL6180X", "kind": "rangefinder"})
        self.assertEqual(matching.NameContains().score({"does": None, "what": "vl6180 lidar"}, offer).score, 0.0)

    def test_name_contains_searches_the_id_name_kind_and_aliases_in_that_order(self):
        # `--need "amplifier audio-amplifier"` found the DFR0954 before P211: the name ends where the kind begins
        offer = matching.Offer.from_record("max98357a-dfr0954", "part", {"name": "DFR0954 I2S amplifier", "kind": "audio-amplifier",
                                                                       "also_known_as": ["MAX98357A board"]})
        for typed, score in (("amplifier audio-amplifier", 1.0), ("audio-amplifier max98357a", 1.0), ("max98357a audio-amplifier", 0.0),
                             ("audio-amplifier dfr0954", 0.0)):
            with self.subTest(typed=typed):
                need = {"does": None, "what": typed, "words": [typed]}
                self.assertEqual(matching.NameContains().score(need, offer).score, score)

    def test_name_contains_keeps_an_argument_with_a_space_as_one_substring(self):
        offer = an_offer(names=["soil probe, moisture"])
        need = {"does": None, "what": "soil moisture"}
        self.assertEqual(matching.NameContains().score(need, offer).score, 1.0)
        self.assertEqual(matching.NameContains().score(dict(need, words=["soil moisture"]), offer).score, 0.0)

    def test_a_search_finds_only_what_scores(self):
        a, b = an_offer(key="a"), an_offer(key="b")
        fits = [matching.Fit(a, 0.0, False, []), matching.Fit(b, 1.0, True, [])]
        self.assertEqual([fit.offer.key for fit in matching.found(fits)], ["b"])

    def test_rank_puts_the_best_first_and_keeps_the_order_of_equals(self):
        a, b, c = (an_offer(key=k, functions=[{"does": "sense", "what": w}]) for k, w in (("a", "x"), ("b", "range"), ("c", "y")))
        self.assertEqual([fit.offer.key for fit in matching.WordOverlap().rank(SENSE, [a, b, c])], ["b", "a", "c"])

    def test_a_matcher_is_found_by_name_for_a_caller_it_serves(self):
        self.assertIsInstance(matching.matcher("word-overlap", "match"), matching.WordOverlap)
        with self.assertRaises(matching.UnknownMatcher) as refused:
            matching.matcher("name-contains", "match")
        self.assertIn("same-words, word-overlap", str(refused.exception))

    def test_what_match_shows(self):
        self.assertEqual([matching.shown(r, e, s) for r, e, s in ((7, False, 0.0), (8, False, 0.0), (8, True, 0.0), (8, False, 0.5))],
                         [True, False, True, True])
