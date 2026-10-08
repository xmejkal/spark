"""
Proof that a module list becomes a board file, and that the file admits what it is.

The output of this script is the one artifact in the plugin most likely to be over-trusted: it
looks like a finished design. So what is tested here is as much about what it SAYS as what it
emits.

The connections are derived and defensible — every trace comes from a pin assignment checked
against the board's own constraints. The placement is not: it is a column, chosen because it
does not overlap. The file has to say so, or someone will order it.

    python3 -m unittest discover -s tests
"""

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
import copper  # noqa: E402
import design  # noqa: E402
import emit_board  # noqa: E402
import parts  # noqa: E402

PARTS = ["l9110s-module", "vl6180x-breakout", "dfr0534-module"]


def generated():
    board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
    part_list = [parts.load(part_id) for part_id in PARTS]
    signals = parts.signals_for(PARTS)
    assignments, _ = assign_pins.assign(board, signals)
    placements, width, height = emit_board.place(board, part_list)
    return emit_board.emit(board, part_list, assignments, placements, width, height)


class WhatItEmitsTest(unittest.TestCase):
    def setUp(self):
        self.tsx = generated()

    def test_it_imports_the_boards_footprint(self):
        self.assertIn('import { FireBeetle2Esp32S3 }', self.tsx)

    def test_every_part_becomes_a_component(self):
        for part_id in PARTS:
            with self.subTest(part=part_id):
                self.assertIn(emit_board.component_name(parts.load(part_id)), self.tsx)

    def test_every_signal_a_part_asked_for_becomes_a_trace(self):
        """
        One trace per signal, no more and no less. A dropped signal is a module that does not
        work; a duplicated one is a short.

        Counted as traces from the MCU to a PART, not as every trace from the MCU. It used to be
        the latter, which silently assumed the microcontroller had no supply connections of its
        own — and for a long time that was true, which is exactly the defect: a generated board
        whose processor shared a net with none of its 32 pins.
        """
        signal_traces = [line for line in self.tsx.splitlines()
                         if '<trace from=".Mcu' in line and 'to="net.' not in line]
        self.assertEqual(len(signal_traces), len(parts.signals_for(PARTS)))

    def test_every_pad_the_board_file_calls_power_is_wired_or_says_why_not(self):
        # The board file says which of its pads are power; every one of them must appear. A
        # processor connected to no ground builds, routes, and reports no error.
        #
        # Since P29 a pad the module RECEIVES on is conditional — this design has no 5 V source,
        # so Mcu.VCC is not wired — but conditional is not silent, and that is the whole value:
        # a trace that was reasoned about and one that was forgotten must not read the same.
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        for pad, supply in (board.get("power_pads") or {}).items():
            with self.subTest(pad=pad):
                wired = '<trace from=".Mcu > .%s" to="net.' % pad in self.tsx
                self.assertTrue(wired or ("Mcu.%s receives net." % pad) in self.tsx,
                                "%s is neither wired nor accounted for" % pad)
                if supply.get("direction", "in") == "out":
                    self.assertTrue(wired, "a pad the module DRIVES is never conditional")

    def test_each_module_pin_appears_on_the_trace_that_reaches_it(self):
        for part_id in PARTS:
            part = parts.load(part_id)
            for need in part["needs"]:
                with self.subTest(part=part_id, pin=need["pin"]):
                    self.assertIn('.%s > .%s"' % (emit_board.component_name(part), need["pin"]),
                                  self.tsx)

    def test_each_trace_carries_the_reason_the_pin_was_chosen(self):
        # A board file that says why is one a person can argue with.
        self.assertIn("dedicated hardware, not a choice", self.tsx)
        self.assertIn("needs wake", self.tsx)

    def test_power_pins_are_wired_to_named_rails(self):
        self.assertIn('to="net.GND"', self.tsx)
        self.assertIn('to="net.V33"', self.tsx)
        self.assertIn('to="net.MOTOR6V"', self.tsx)

    def test_it_sets_the_fabrication_defaults_rather_than_inheriting_them(self):
        # A tool's floor is what you get when nothing is stated, and on a real board that was
        # 0.2 mm vias with a 0.05 mm annular ring — below every cheap process's minimum.
        self.assertIn('minViaHoleDiameter="0.3mm"', self.tsx)
        self.assertIn('minViaPadDiameter="0.6mm"', self.tsx)
        self.assertIn('thickness="1.6mm"', self.tsx)


class WhatItAdmitsTest(unittest.TestCase):
    def setUp(self):
        self.tsx = generated()

    def test_it_says_the_placement_is_a_draft(self):
        self.assertIn("first draft", self.tsx)

    def test_it_lists_what_it_has_not_decided(self):
        for undecided in ("mounting holes", "connector keying", "trace widths"):
            with self.subTest(undecided=undecided):
                self.assertIn(undecided, self.tsx)

    def test_it_carries_each_parts_requirements_of_its_host(self):
        # These are the things a generated board cannot do for you, and they live in the part
        # files where they can be verified once. Leaving them in a library nobody opens is how
        # a hardware pulldown gets forgotten.
        self.assertIn("Pull both inputs down in HARDWARE", self.tsx)

    def test_it_names_a_rail_that_nothing_sources(self):
        # A module list is a list of CONSUMERS. Nobody lists the battery connector among their
        # parts, so the motor rail has one member and cannot route — and saying so is more
        # useful than emitting a file that fails to build.
        self.assertIn("NOTHING ON THIS BOARD SOURCES net.MOTOR6V", self.tsx)


class TheSilkscreenSurvivesTest(unittest.TestCase):
    """
    A part's `pin` is what a selector can parse; `printed` is what is on the module. The emitted
    file has to show both where they differ, or a person wiring the board reads VIN in the file
    and IN+ on the part and has no record that they are one pad.
    """

    @staticmethod
    def buck():
        return {"schema": 1, "id": "buck", "name": "buck", "kind": "regulator", "needs": [],
                "power": [{"pin": "VIN", "printed": "IN+", "rail": "traction", "direction": "in"},
                          {"pin": "GNDIN", "printed": "IN-", "rail": "ground", "direction": "in"}],
                "pin_order": ["VIN", "GNDIN"], "pin_order_proof": {"verified": False, "source": "a test fixture"}, "footprint": "pinrow2",
                "body_mm": {"width": 5, "height": 5, "verified": True, "source": "test"}}

    def _emit(self, part):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        placements, width, height = emit_board.place(board, [part])
        return emit_board.emit(board, [part], [], placements, width, height, {})

    def test_the_wiring_name_is_what_reaches_the_selector(self):
        tsx = self._emit(self.buck())
        self.assertIn('pin1: "VIN"', tsx)
        self.assertNotIn('pin1: "IN+"', tsx)

    def test_the_silkscreen_is_recorded_beside_the_chip(self):
        tsx = self._emit(self.buck())
        self.assertIn("VIN is printed IN+", tsx)
        self.assertIn("GNDIN is printed IN-", tsx)

    def test_a_part_whose_names_match_its_silkscreen_gets_no_note(self):
        plain = self.buck()
        for entry in plain["power"]:
            entry.pop("printed")
        self.assertNotIn("silkscreen:", self._emit(plain))


#: A record's text with a comment's end in it: the review's probe (F11), whose `console.log` `tsci build` ran.
INJECTED = 'A soil probe */ console.log("REVIEW-INJECTED-" + 6*7) /* end'


def outside_comments(tsx):
    """The emitted file as JavaScript runs it: every `/* … */` taken out, each ending at its first `*/`."""
    return re.sub(r"/\*.*?\*/", "", tsx, flags=re.DOTALL)


class ARecordsTextStaysInsideItsCommentTest(unittest.TestCase):
    """
    F11 (P87's emitter half): the board keeps a record's words in `{/* … */}` comments and in its header's doc
    comment — a name, a signal, a passive's why, a power pin's note, a footprint note, a host requirement — and a
    `*/` in any of them ended the comment, so `tsci build` ran what followed. They are kept, with `*/` written `* /`.
    """

    #: Where the probe goes, and how: one place at a time, in a copy of the library LED.
    PLACES = {
        "the name": lambda led, board: led.update(name=INJECTED),
        "the name of a part nobody measured": lambda led, board: (led.update(name=INJECTED), led.pop("body_mm")),
        "a signal": lambda led, board: led["needs"][0].update(signal=INJECTED),
        "the silkscreen": lambda led, board: led["needs"][0].update(printed=INJECTED),
        "a passive's why": lambda led, board: led["host_parts"][0].update(why=INJECTED),
        "a power pin's note": lambda led, board: led["power"][0].update(note=INJECTED),
        "a footprint note": lambda led, board: led.update(footprint_placeholder=True, footprint_note=INJECTED),
        "a host requirement": lambda led, board: led["host_requirements"].append(INJECTED),
        "the board's name": lambda led, board: board.update(name=INJECTED),
    }

    @staticmethod
    def emitted(place):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        led = parts.load("led-red-5mm")
        place(led, board)
        signals = [{"name": need["signal"], "needs": need.get("needs", []), "from": led["id"]} for need in led["needs"]]
        assignments, _ = assign_pins.assign(board, signals)
        placements, width, height = emit_board.place(board, [led])
        return emit_board.emit(board, [led], assignments, placements, width, height, {})

    def test_text_with_a_comment_s_end_in_it_never_reaches_code(self):
        for where, place in self.PLACES.items():
            with self.subTest(where=where):
                tsx = self.emitted(place)
                self.assertEqual([line.strip() for line in outside_comments(tsx).splitlines() if "REVIEW-INJECTED" in line], [],
                                 "what JavaScript would run")
                self.assertTrue('A soil probe * / console.log("REVIEW-INJECTED-" + 6*7) /* end' in tsx, "kept, and inert")

    def test_a_comment_s_end_is_the_only_text_changed(self):
        # a `"` is only text inside a comment, and product names carry inch marks: nothing but `*/` is touched
        self.assertEqual(emit_board.inert('a 1/4" jack */ and **/ twice'), 'a 1/4" jack * / and ** / twice')
        self.assertEqual(emit_board.inert(5), "5")


class PlaceholderFootprintsAreNamedTest(unittest.TestCase):
    """
    The generator is where a placeholder gets the name the netlist will carry, so it is where the
    list of them is made — a second derivation of the name in `check_all` would be one more copy
    of a rule to drift.
    """

    @staticmethod
    def part(part_id, placeholder=False, instance=None):
        record = {"schema": 1, "id": part_id, "name": part_id, "kind": "test", "needs": [],
                  "power": [{"pin": "GND", "rail": "ground", "direction": "in"}],
                  "pin_order": ["GND"], "pin_order_proof": {"verified": False, "source": "a test fixture"}, "footprint": "pinrow1",
                  "body_mm": {"width": 5, "height": 5, "verified": True, "source": "test"}}
        if placeholder:
            record.update(footprint_placeholder=True, footprint_note="stands in")
        if instance:
            record["_instance"] = instance
        return record

    def test_a_placeholder_is_named_as_the_netlist_will_see_it(self):
        self.assertEqual(emit_board.placeholder_components(
            [self.part("xt30-inlet", placeholder=True)]), ["Xt30Inlet"])

    def test_a_named_instance_is_named_by_its_instance(self):
        # Otherwise the checker looks for a name that is not in the netlist and skips nothing.
        self.assertEqual(emit_board.placeholder_components(
            [self.part("inlet", placeholder=True, instance="PackIn")]), ["PackIn"])

    def test_a_real_footprint_is_not_listed(self):
        self.assertEqual(emit_board.placeholder_components([self.part("real")]), [])

    def test_the_emitted_file_says_which_footprints_are_stand_ins(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        parts_list = [self.part("xt30-inlet", placeholder=True)]
        placements, width, height = emit_board.place(board, parts_list)
        tsx = emit_board.emit(board, parts_list, [], placements, width, height, {})
        self.assertIn("PLACEHOLDERS", tsx)
        self.assertIn("Xt30Inlet drawn as pinrow1", tsx)


class PowerTracesAreSizedTest(unittest.TestCase):
    """
    Every generated trace was the router's 0.15 mm default, good for about 0.6 A.

    On an RC car whose traction rail carries 2.9 A that is a burnt board, and the generator had
    never asked what a rail carries even though the answer was in a file the same project holds.
    `check_physics` caught all three rails, which is the system working — but the generator
    producing something its own checker rejects is not a design, it is a first draft.

    The width comes from `copper`, the same module the checker judges by, so the two cannot
    disagree.
    """

    RULES = {"physics": {"rails": {"TRACTION": {"max_current_a": 2.9},
                                   "SERVO": {"max_current_a": 1.2},
                                   "V33": {"max_current_a": None}}}}

    @staticmethod
    def part(part_id, rail):
        return {"schema": 1, "id": part_id, "name": part_id, "kind": "test", "needs": [],
                "power": [{"pin": "VCC", "rail": rail, "direction": "in"},
                          {"pin": "GND", "rail": "ground", "direction": "in"}],
                "pin_order": ["VCC", "GND"], "pin_order_proof": {"verified": False, "source": "a test fixture"}, "footprint": "pinrow2",
                "body_mm": {"width": 5, "height": 5, "verified": True, "source": "test"}}

    def _emit(self, rules):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        parts_list = [self.part("load", "traction")]
        placements, width, height = emit_board.place(board, parts_list)
        return emit_board.emit(board, parts_list, [], placements, width, height, rules)

    def test_a_heavy_rail_gets_a_stated_thickness(self):
        self.assertIn('to="net.TRACTION" thickness=', self._emit(self.RULES))

    def test_the_thickness_carries_the_current_the_rules_state(self):
        # Not just "a number is present" — the number has to be the right one.
        tsx = self._emit(self.RULES)
        stated = float(re.search(r'to="net\.TRACTION" thickness="([0-9.]+)mm"', tsx).group(1))
        self.assertGreaterEqual(copper.current_capacity_a(stated, copper.DEFAULT_RISE_C), 2.9)

    def test_a_rail_with_no_stated_current_gets_no_invented_one(self):
        # Matched on the TRACE, not on the string: `<board thickness="1.6mm">` is the board's
        # own, and a bare `assertNotIn("thickness=")` fails on it. Mine did.
        tsx = self._emit({"physics": {"rails": {"TRACTION": {"max_current_a": None}}}})
        self.assertNotRegex(tsx, r'<trace[^>]*thickness=')

    def test_and_says_plainly_that_those_widths_are_unjustified(self):
        # Silence there would be the router's default wearing the clothes of a decision.
        tsx = self._emit({"physics": {"rails": {}}})
        self.assertIn("UNJUSTIFIED", tsx)

    def test_with_no_rules_file_at_all_it_still_emits_a_board(self):
        # A project that has not run `init` yet must still get something, just an unjustified one.
        tsx = self._emit({})
        self.assertIn('to="net.TRACTION"', tsx)
        self.assertIn("UNJUSTIFIED", tsx)


class ManyOfOnePartTest(unittest.TestCase):
    """
    Five identical buttons became one component with five GPIOs shorted to its single port.

    Found by building a remote control. The requirements file listed the same part five times,
    which is the obvious way to say "five of these". `component_name` derived the name from the
    part id, so all five were `TactileButton`; `tsci build` kept ONE; and the five distinct pins
    `assign_pins` had carefully allocated were all wired to the survivor. Exit 0, no warning.

    Fourth instance of one defect class — after signals with no part record, the processor on no
    ground, and rails outside the vocabulary. Every time the generator emitted less than it was
    asked for and said nothing, and three of the four were found by building something new rather
    than by any test.
    """

    @staticmethod
    def button(instance=None):
        part = {"schema": 1, "id": "tactile-button", "name": "button", "kind": "button",
                "needs": [{"signal": "BUTTON", "pin": "A", "direction": "in"}],
                "power": [{"pin": "B", "rail": "ground", "direction": "in"}],
                "pin_order": ["A", "B"], "pin_order_proof": {"verified": False, "source": "a test fixture"}, "footprint": "pushbutton",
                "body_mm": {"width": 6, "height": 6, "verified": True, "source": "6x6"}}
        if instance:
            part["_instance"] = instance
        return part

    def test_an_instance_name_wins_over_the_part_id(self):
        self.assertEqual(emit_board.component_name(self.button("BtnForward")), "BtnForward")

    def test_without_one_the_part_id_is_still_used(self):
        self.assertEqual(emit_board.component_name(self.button()), "TactileButton")

    def test_two_unnamed_instances_are_caught_before_anything_is_emitted(self):
        # The safety net, independent of how a design arrives at two of the same name.
        repeated = emit_board.duplicate_component_names([self.button(), self.button()])
        self.assertEqual(repeated, ["TactileButton"])

    def test_named_instances_do_not_collide(self):
        self.assertEqual(emit_board.duplicate_component_names(
            [self.button("BtnLeft"), self.button("BtnRight")]), [])

    def test_two_instances_given_the_SAME_name_are_still_caught(self):
        # Naming is not a cure by itself; a copy-pasted requirements entry hits the same wall.
        self.assertEqual(emit_board.duplicate_component_names(
            [self.button("BtnLeft"), self.button("BtnLeft")]), ["BtnLeft"])

    def test_each_instance_asks_for_its_own_signal(self):
        # Five buttons asking for `BUTTON` produced five signals of one name, which every lookup
        # keyed by name then collapsed to whichever came last.
        left = self.button("BtnLeft")
        right = self.button("BtnRight")
        self.assertEqual(design.signal_name(left, left["needs"][0]), "BTNLEFT_BUTTON")
        self.assertEqual(design.signal_name(right, right["needs"][0]), "BTNRIGHT_BUTTON")

    def test_an_unnamed_part_keeps_its_bare_signal_name(self):
        plain = self.button()
        self.assertEqual(design.signal_name(plain, plain["needs"][0]), "BUTTON")

    def test_a_bare_string_and_an_object_are_both_valid_entries(self):
        self.assertEqual(
            design.requested_parts({"parts": ["l9110s-module",
                                                  {"part": "tactile-button", "name": "BtnLeft"}]}),
            [("l9110s-module", None), ("tactile-button", "BtnLeft")])


class AnyRailCanBeNamedTest(unittest.TestCase):
    """
    The rail vocabulary was four names, closed, and a rail outside it was silently dropped.

    Found by building something that was not the smart bin. An RC car has a 5 V servo rail and a
    7.4 V traction pack; neither name was in the dictionary, `net_for` returned None, and the
    power loop's `if not net: continue` turned three declared connections into nothing. The
    emitted schematic had a servo with a ground and no supply, and a 5 V regulator joined to the
    board by its two ground pins alone. Exit 0.

    Third instance of one defect: the generator emitting less than it was asked for in silence.
    The first two were signals with no part record, and the microcontroller on no ground.
    """

    @staticmethod
    def part(part_id, power):
        return {"schema": 1, "id": part_id, "name": part_id, "kind": "test",
                "needs": [], "power": power, "pin_order": [s["pin"] for s in power], "pin_order_proof": {"verified": False, "source": "a test fixture"},
                "footprint": "pinrow%d" % len(power)}

    def test_a_rail_nobody_thought_of_becomes_a_net(self):
        self.assertEqual(emit_board.net_name_for_rail("servo"), "SERVO")
        self.assertEqual(emit_board.net_name_for_rail("traction"), "TRACTION")

    def test_a_rail_named_by_its_voltage_gets_a_net_name_the_builder_accepts(self):
        # tscircuit: 'Net name "12V" cannot start with a number' — the irrigation build's first stop (I7)
        self.assertEqual(emit_board.net_name_for_rail("12v"), "V12V")
        self.assertEqual(emit_board.net_name_for_rail("5v"), "V5V")

    def test_the_established_names_are_unchanged(self):
        # Existing designs reference these nets by name; renaming them would be a silent rewire.
        self.assertEqual(emit_board.net_name_for_rail("logic"), "V33")
        self.assertEqual(emit_board.net_name_for_rail("ground"), "GND")
        self.assertEqual(emit_board.net_name_for_rail("motor"), "MOTOR6V")
        self.assertEqual(emit_board.net_name_for_rail("speaker"), "SPEAKER")

    def test_no_rail_at_all_is_still_None(self):
        # Absent is different from unrecognised. A power pin naming no rail is a record that never
        # said where the pin goes, and inventing a default for it would be the original defect
        # wearing a different hat.
        self.assertIsNone(emit_board.net_name_for_rail(None))
        self.assertIsNone(emit_board.net_name_for_rail(""))

    def test_an_invented_rail_is_reported_with_the_pins_on_it(self):
        # Open vocabulary means a typo creates a net. Reported rather than refused, because
        # refusing is what dropped the connections.
        servo = self.part("servo", [{"pin": "VCC", "rail": "servo", "direction": "in"},
                                    {"pin": "GND", "rail": "ground", "direction": "in"}])
        invented = emit_board.rails_not_established([servo])
        self.assertEqual(invented, {"SERVO": ["servo.VCC"]})

    def test_a_design_using_only_established_rails_invents_nothing(self):
        motor = self.part("m", [{"pin": "VCC", "rail": "motor", "direction": "in"},
                                {"pin": "GND", "rail": "ground", "direction": "in"}])
        self.assertEqual(emit_board.rails_not_established([motor]), {})

    def test_a_power_pin_naming_no_rail_is_reported(self):
        broken = self.part("x", [{"pin": "VCC", "direction": "in"}])
        self.assertEqual(emit_board.power_pins_with_no_rail([broken]), ["x.VCC"])

    def test_every_declared_power_pin_reaches_a_net(self):
        """
        The regression, stated as the thing that was actually wrong.

        Eight power pins were declared across three parts and five were emitted. Nothing said so.
        """
        servo = self.part("servo", [{"pin": "VCC", "rail": "servo", "direction": "in"},
                                    {"pin": "GND", "rail": "ground", "direction": "in"}])
        buck = self.part("buck", [{"pin": "IN+", "rail": "traction", "direction": "in"},
                                  {"pin": "IN-", "rail": "ground", "direction": "in"},
                                  {"pin": "OUT+", "rail": "servo", "direction": "out"},
                                  {"pin": "OUT-", "rail": "ground", "direction": "out"}])
        for part in (servo, buck):
            for supply in part["power"]:
                with self.subTest(part=part["id"], pin=supply["pin"]):
                    self.assertIsNotNone(emit_board.net_for(supply),
                                         "declared and unplaceable, which is how it vanished")


class TwoOutputsNeverShareANetTest(unittest.TestCase):
    """
    The generator emitted a board that would destroy a part.

    `RAIL_NETS` mapped a rail name to exactly one net, and both halves of a bridged class-D
    amplifier declared `"rail": "speaker"` — so both landed on `net.SPEAKER`, shorting the
    amplifier to itself, with the part file's own warning ("never ground either side") printed on
    the trace that did it. Under a banner reading "Nothing here is guessed."

    A rail is shared BY DEFINITION and an output must never be. Several GND pins on one net is
    how ground works; two outputs on one net is a short. Direction is the whole difference, and
    the schema did not carry it.
    """

    def _emit(self, part_ids):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        part_list = [parts.load(part_id) for part_id in part_ids]
        assignments, _ = assign_pins.assign(board, parts.signals_for(part_ids))
        placements, width, height = emit_board.place(board, part_list)
        return emit_board.emit(board, part_list, assignments, placements, width, height)

    def test_a_bridged_output_pair_lands_on_two_nets(self):
        tsx = self._emit(["dfr0534-module"])
        self.assertIn('.SPKP" to="net.SPEAKER_P"', tsx)
        self.assertIn('.SPKN" to="net.SPEAKER_N"', tsx)

    def test_no_two_outputs_of_one_part_ever_share_a_net(self):
        # The general property, so this cannot be fixed for the speaker and left broken for the
        # next differential output somebody adds.
        for part_id in parts.available():
            part = parts.load(part_id)
            nets = [emit_board.net_for(supply) for supply in part.get("power") or []
                    if supply.get("direction") == "out"]
            with self.subTest(part=part_id):
                self.assertEqual(len(nets), len(set(nets)),
                                 "%s drives two outputs onto one net" % part_id)

    def test_inputs_still_share_the_rail_they_name(self):
        """
        The other half: if outputs getting their own net turned into every pin getting its own
        net, nothing would connect to anything.

        Counts the MODULES' ground connections specifically. It counted every `net.GND` in the
        file until the microcontroller started contributing its own three ground pads — the
        number was right only while the processor was ungrounded.
        """
        tsx = self._emit(["dfr0534-module", "l9110s-module"])
        modules = tuple('.%s >' % emit_board.component_name(parts.load(p)) for p in ("dfr0534-module", "l9110s-module"))
        module_grounds = [line for line in tsx.splitlines()
                          if 'to="net.GND"' in line and any(line.startswith('    <trace from="%s' % m) for m in modules)]
        self.assertEqual(len(module_grounds), 2, "two modules, one ground pin each; the pulldowns the L9110S demands have their own")

    def test_the_contract_refuses_two_outputs_that_cannot_be_told_apart(self):
        broken = json.loads((ROOT / "parts" / "dfr0534-module.json").read_text())
        for supply in broken["power"]:
            supply.pop("polarity", None)
        problems = parts.validate(broken, ROOT / "parts" / "dfr0534-module.json")
        self.assertTrue(any("short into each other" in p for p in problems), problems)


class PadOneIsAFactAboutTheModuleTest(unittest.TestCase):
    """
    `pinLabels` were numbered from the order the pins happened to appear in the JSON file.

    That is not a fact about anything. The L9110S's header reads BIA BIB GND VCC AIA AIB on its
    own silkscreen, and the generator emitted `pin1: "AIA"` — so every trace to the module landed
    on the wrong pad. The board would build, the render would look right, and nothing would work.
    The physical order simply was not written down, so the generator could not have been correct.
    """

    def test_pads_are_numbered_from_the_module_not_from_the_file(self):
        part = parts.load("l9110s-module")
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        assignments, _ = assign_pins.assign(board, parts.signals_for(["l9110s-module"]))
        placements, width, height = emit_board.place(board, [part])
        tsx = emit_board.emit(board, [part], assignments, placements, width, height)
        # Off the silkscreen, confirmed four independent ways.
        self.assertIn('pin1: "BIA", pin2: "BIB", pin3: "GND", pin4: "VCC", pin5: "AIA", '
                      'pin6: "AIB"', tsx)

    def test_a_pad_the_part_does_not_wire_is_left_empty_not_renumbered(self):
        # The audio module has ten pads and wires five. Closing the gaps would put SPKN on pad 4.
        part = parts.load("dfr0534-module")
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        assignments, _ = assign_pins.assign(board, parts.signals_for(["dfr0534-module"]))
        placements, width, height = emit_board.place(board, [part])
        tsx = emit_board.emit(board, [part], assignments, placements, width, height)
        self.assertIn('pin9: "SPKN", pin10: "SPKP"', tsx)
        self.assertNotIn('pin4: "SPKN"', tsx)

    def test_a_part_with_no_recorded_pinout_is_refused(self):
        # Asserted against a part built for the purpose. This used to name the rangefinder,
        # because that was the library's unpinned part on the day it was written — so the test
        # broke the moment somebody found a schematic and recorded its pinout, which is the
        # library getting better. A test should fail when the behaviour breaks, not when the data
        # improves.
        unpinned = {"id": "x", "name": "A part nobody has opened", "kind": "test", "needs": []}
        self.assertEqual(emit_board.parts_without_a_pinout([unpinned]),
                         ["A part nobody has opened"])

    def test_every_part_in_the_library_either_has_a_pinout_or_says_why_not(self):
        # The library's own state, kept honest separately: a part may carry no pin_order, but
        # then the file has to say what would make one possible.
        for part_id in parts.available():
            part = parts.load(part_id)
            with self.subTest(part=part_id):
                self.assertTrue(part.get("pin_order") or part.get("//pin_order"),
                                "%s has neither a pinout nor a reason it lacks one" % part_id)

    def test_every_pin_the_part_uses_has_a_pad(self):
        # The contract's half of it: a pin with no pad would silently connect to nothing.
        for part_id in parts.available():
            part = parts.load(part_id)
            if not part.get("pin_order"):
                continue
            used = {need["pin"] for need in part.get("needs") or []}
            used |= {supply["pin"] for supply in part.get("power") or []}
            with self.subTest(part=part_id):
                self.assertEqual(used - set(part["pin_order"]), set())


class EveryUnroutableNetIsPredictedTest(unittest.TestCase):
    """
    A generated board has nets with one member, and that is not a bug — a battery, a speaker and
    a motor are not modules, so nobody lists them and nothing on the board is at the other end.
    What matters is that the file SAYS SO, in both directions, before anyone builds it.

    Built against the real engine while this was written: 415 elements, 3 errors, and the three
    nets the build refused to route were exactly the three the generator had named.
    """

    def test_a_rail_nothing_supplies_is_named(self):
        self.assertIn("MOTOR6V", emit_board.rails_without_a_source([parts.load("l9110s-module")]))

    def test_an_output_nothing_receives_is_named_too(self):
        # The half that was missing. Excluding outputs from the rail check was right — the part
        # IS the source — but it left two unroutable nets unmentioned.
        driven = emit_board.outputs_with_nothing_on_them([parts.load("dfr0534-module")])
        self.assertEqual({net for net, _, _ in driven}, {"SPEAKER_P", "SPEAKER_N"})

    def test_both_kinds_reach_the_generated_file(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        ids = ["l9110s-module", "dfr0534-module"]
        part_list = [parts.load(part_id) for part_id in ids]
        assignments, _ = assign_pins.assign(board, parts.signals_for(ids))
        placements, width, height = emit_board.place(board, part_list)
        tsx = emit_board.emit(board, part_list, assignments, placements, width, height)
        self.assertIn("NOTHING ON THIS BOARD SOURCES net.MOTOR6V", tsx)
        self.assertIn("NOTHING ON THIS BOARD RECEIVES IT", tsx)

    def test_a_rail_the_module_supplies_is_not_reported_either_way(self):
        part_list = [parts.load("vl6180x-breakout")]
        self.assertNotIn("V33", emit_board.rails_without_a_source(part_list))
        self.assertEqual(emit_board.outputs_with_nothing_on_them(part_list), [])


class EverySignalTheAssignerPlacedIsAccountedForTest(unittest.TestCase):
    """
    The emitted file said "Signals, each on the pin assign_pins.py chose" over half a board.

    The loop ran over PARTS and their needs, so a signal placed for something with no part record
    — a button, an LED, a limit switch, a connector — was never looked up. On a twelve-signal
    design six vanished, silently, exit 0. `parts/` holds four parts and all four are modules, so
    every discrete component on a real board falls in this hole.

    The assignments are the authority on what has to be connected. The parts only say where.
    """

    def _emit_with_extra_signals(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        part_list = [parts.load("l9110s-module")]
        signals = parts.signals_for(["l9110s-module"]) + [
            {"name": "BTN_OPEN", "needs": ["wake"]}, {"name": "LED_RED", "needs": []}]
        assignments, _ = assign_pins.assign(board, signals)
        placements, width, height = emit_board.place(board, part_list)
        return assignments, emit_board.emit(
            board, part_list, assignments, placements, width, height)

    def test_a_signal_no_part_claims_is_named_rather_than_dropped(self):
        _, tsx = self._emit_with_extra_signals()
        self.assertIn("ASSIGNED, AND CONNECTED TO NOTHING", tsx)
        for signal in ("BTN_OPEN", "LED_RED"):
            with self.subTest(signal=signal):
                self.assertIn(signal, tsx)

    def test_it_carries_the_pin_and_the_reason_so_it_can_be_wired_by_hand(self):
        _, tsx = self._emit_with_extra_signals()
        self.assertIn("needs wake", tsx)
        self.assertRegex(tsx, r"BTN_OPEN on \w+ \(GPIO\d+\)")

    def test_every_assigned_signal_appears_somewhere_in_the_file(self):
        # The general property: a placed signal is either traced or declared unclaimed. Never
        # absent, which is the state that reads as finished.
        assignments, tsx = self._emit_with_extra_signals()
        for entry in assignments:
            with self.subTest(signal=entry["signal"]):
                self.assertIn(entry["signal"], tsx)

    def test_a_signal_a_part_does_claim_is_traced_not_listed(self):
        _, tsx = self._emit_with_extra_signals()
        self.assertIn('<trace from=".Mcu > .', tsx)
        unclaimed = tsx.split("ASSIGNED, AND CONNECTED TO NOTHING")[1]
        self.assertNotIn("MOTOR_IA", unclaimed)


class RailsWithoutASourceTest(unittest.TestCase):
    def test_a_rail_the_module_supplies_is_not_reported(self):
        # The microcontroller module provides 3V3 and ground, so consuming those is fine.
        part_list = [parts.load("vl6180x-breakout")]
        self.assertNotIn("V33", emit_board.rails_without_a_source(part_list))
        self.assertNotIn("GND", emit_board.rails_without_a_source(part_list))

    def test_a_rail_only_consumed_is_reported(self):
        part_list = [parts.load("l9110s-module")]
        self.assertIn("MOTOR6V", emit_board.rails_without_a_source(part_list))


class ASpeakerTerminalEndsTheAmplifiersNetsTest(unittest.TestCase):
    """
    C-3 (the council on PR #98): an amplifier's two outputs each drove a net with one member, so every amplifier ended
    "the chain is broken" — a speaker is not a module and nobody lists one. The terminal its wires go to is a record now, and
    its two pins receive the pair: an input that names a side of a pair (`polarity`) joins that side's net.
    """

    def test_an_input_naming_a_side_of_a_pair_joins_that_side_s_net(self):
        for polarity, net in (("+", "SPEAKER_P"), ("-", "SPEAKER_N")):
            with self.subTest(polarity=polarity):
                self.assertEqual(emit_board.net_for({"pin": "X", "rail": "speaker", "direction": "in", "polarity": polarity}), net)
        self.assertEqual(emit_board.net_for({"pin": "X", "rail": "speaker", "direction": "in"}), "SPEAKER")

    def test_the_terminal_receives_both_outputs_and_nothing_is_left_unrouted(self):
        part_list = [parts.load("max98357a-dfr0954"), parts.load("speaker-terminal")]
        self.assertEqual([emit_board.net_for(supply) for supply in part_list[1]["power"]], ["SPEAKER_P", "SPEAKER_N"])
        self.assertEqual((emit_board.outputs_with_nothing_on_them(part_list), emit_board.rails_without_a_source(part_list)), ([], []))

    def test_the_terminal_alone_is_a_rail_nothing_drives(self):
        self.assertEqual(emit_board.rails_without_a_source([parts.load("speaker-terminal")]), ["SPEAKER_N", "SPEAKER_P"])

    def test_the_terminal_alone_is_told_to_add_what_drives_the_pair_never_a_supply(self):
        # F15's follow-up: --requirements said "never a supply", while the board's comment and emit_board's own note still
        # said to add "whatever supplies this rail (a connector, a regulator, a battery)" — into a bridged amplifier output
        said = "\n".join(emit_board.power_note_lines([parts.load("speaker-terminal")]))
        self.assertIn("    {/* NOTHING ON THIS BOARD DRIVES net.SPEAKER_P, one side of a driven pair. Add what\n"
                      "        drives the pair (the amplifier this terminal hangs off), never a supply,\n"
                      "        or the net has one member and will not route. */}", said)
        self.assertNotIn("supplies this rail", said)
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["speaker-terminal"]}))
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = emit_board.main([str(root / "requirements.json")])
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertIn("note: nothing drives net.SPEAKER_P, one side of a driven pair — add what drives the pair (the amplifier "
                      "this terminal hangs off), never a supply, or that net has one member and the board will not route\n",
                      err.getvalue())
        self.assertNotIn("add whatever supplies it", err.getvalue())

    def test_a_load_across_a_pair_is_named_so_the_island_check_asks_it_no_ground(self):
        part_list = [parts.load("max98357a-dfr0954"), parts.load("speaker-terminal"), parts.load("l9110s-module"),
                     parts.load("jst-ph-2-power-inlet")]
        self.assertEqual(emit_board.loads_across_a_pair(part_list), ["SpeakerTerminal"])


class PlacementTest(unittest.TestCase):
    def test_nothing_is_placed_on_top_of_anything_else(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        part_list = [parts.load(part_id) for part_id in PARTS]
        placements, _, _ = emit_board.place(board, part_list)

        boxes = []
        for part in part_list:
            x, y = placements[emit_board.component_name(part)]
            w, h = emit_board.body_of(part)
            boxes.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
        for index, first in enumerate(boxes):
            for second in boxes[index + 1:]:
                overlaps = (min(first[2], second[2]) > max(first[0], second[0])
                            and min(first[3], second[3]) > max(first[1], second[1]))
                self.assertFalse(overlaps, "two module bodies occupy the same space")

    def test_the_board_is_big_enough_for_what_is_on_it(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        part_list = [parts.load(part_id) for part_id in PARTS]
        _, width, height = emit_board.place(board, part_list)
        self.assertGreater(height, board["physical"]["height_mm"])
        self.assertGreater(width, board["physical"]["width_mm"])



class TheDocumentedInvocationTest(unittest.TestCase):
    """
    `main()`, run the way the docstring says to run it: inside the project, no `--project`.

    Nothing called `main()` before 2026-09-29. Every sizing test handed `emit()` a rules dict,
    and `main()` looked the rules up by the raw flag — None without it — so the documented
    invocation emitted every power trace unsized, exit 0, and said the widths were unjustified
    while `.spark/rules.json` two directories down stated them. The mutation table could not
    reach it. This is the test the sprint audit said would fail, and it did.
    """

    RULES = {"physics": {"rails": {"MOTOR6V": {"max_current_a": 2.0}}}}

    def _project(self, rules=RULES):
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        if rules is not None:
            (root / ".spark" / "rules.json").write_text(json.dumps(rules))
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        return root

    @staticmethod
    def _main(argv, cwd):
        out, err = io.StringIO(), io.StringIO()
        was = os.getcwd()
        os.chdir(cwd)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = emit_board.main(argv)
        finally:
            os.chdir(was)
        return code, out.getvalue(), err.getvalue()

    SIZED = r'to="net\.MOTOR6V" thickness="[0-9.]+mm"'

    def test_inside_the_project_without_the_flag_the_traces_are_sized(self):
        code, tsx, _ = self._main(["requirements.json"], self._project())
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertRegex(tsx, self.SIZED)

    def test_from_elsewhere_by_absolute_path_the_same(self):
        root = self._project()
        code, tsx, _ = self._main([str(root / "requirements.json")], tempfile.mkdtemp())
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertRegex(tsx, self.SIZED)

    def test_the_flag_still_wins(self):
        # Pointed at a project with no rules, the same file comes out unsized: the control that
        # the two tests above are reading the project's rules and not something else.
        root, bare = self._project(), self._project(rules=None)
        code, tsx, _ = self._main([str(root / "requirements.json"), "--project", str(bare)], root)
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertNotRegex(tsx, self.SIZED)
        self.assertIn("UNJUSTIFIED", tsx)

    def test_malformed_requirements_are_could_not_run_not_a_traceback(self):
        root = self._project()
        (root / "bad.json").write_text("{not json")
        code, tsx, err = self._main(["bad.json"], root)
        self.assertEqual(code, emit_board.EXIT_COULD_NOT_RUN)
        self.assertEqual(tsx, "")
        self.assertIn("not JSON", err)

    def test_a_rail_named_in_the_requirements_reaches_the_netlist(self):
        # R9: no copied record — the design says which rail the driver sits on, and the file
        # carries that net. The rail is not in the established vocabulary, so it is also listed
        # as invented, which is the reader's cue to check the name.
        root = self._project()
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3",
             "parts": [{"part": "l9110s-module", "rails": {"VCC": "traction"}}]}))
        code, tsx, _ = self._main(["requirements.json"], root)
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertIn('to="net.TRACTION"', tsx)
        self.assertNotIn('to="net.MOTOR6V"', tsx)
        self.assertIn("Rails this design INVENTED", tsx)

    def test_the_signals_the_loader_derives_are_the_ones_traced(self):
        # P20: the signals come from `design.load`, the same list `assign_pins.py` prints. A main
        # that traced anything else — or nothing — would still emit a file that builds.
        code, tsx, _ = self._main(["requirements.json"], self._project())
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertIn('to=".L9110sModule > .AIA" />  {/* MOTOR_IA:', tsx)

    def test_a_malformed_part_record_is_could_not_run_not_a_traceback(self):
        # B10: `parts.load` read the file outside any try; through here it was a JSONDecodeError.
        root = self._project()
        (root / "parts").mkdir()
        (root / "parts" / "l9110s-module.json").write_text("{half a record")
        code, tsx, err = self._main(["requirements.json"], root)
        self.assertEqual(code, emit_board.EXIT_COULD_NOT_RUN)
        self.assertIn("l9110s-module", err)
        self.assertIn("not JSON", err)

    def test_a_named_i2c_part_is_traced_to_the_boards_own_bus_pins(self):
        # Audit B2: named, the rangefinder landed on D3/D12 "needs nothing special".
        root = self._project()
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3",
             "parts": [{"part": "vl6180x-breakout", "name": "Rangefinder"}, "jst-ph-2-power-inlet"]}))
        code, tsx, _ = self._main(["requirements.json", "--assume-missing-sizes"], root)
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertIn('<trace from=".Mcu > .SDA" to=".Rangefinder > .SDA" />', tsx)
        self.assertIn('<trace from=".Mcu > .SCL" to=".Rangefinder > .SCL" />', tsx)

    def test_two_parts_on_one_bus_are_both_traced_to_it(self):
        root = self._project()
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3",
             "parts": [{"part": "vl6180x-breakout", "name": "Near"},
                       {"part": "vl6180x-breakout", "name": "Far"}, "jst-ph-2-power-inlet"]}))
        code, tsx, _ = self._main(["requirements.json", "--assume-missing-sizes"], root)
        self.assertEqual(code, emit_board.EXIT_OK)
        for name in ("Near", "Far"):
            self.assertIn('<trace from=".Mcu > .SDA" to=".%s > .SDA" />' % name, tsx)
            self.assertIn('<trace from=".Mcu > .SCL" to=".%s > .SCL" />' % name, tsx)

    def test_a_project_that_does_not_exist_is_could_not_run_not_an_unsized_board(self):
        # Close audit C5: with the flag pointing at a typo, the board came out unsized, exit 0.
        root = self._project()
        code, tsx, err = self._main(["requirements.json", "--project", "typo"], root)
        self.assertEqual(code, emit_board.EXIT_COULD_NOT_RUN)
        self.assertEqual(tsx, "")
        self.assertIn("typo", err)

    def test_an_entry_without_a_part_is_could_not_run(self):
        root = self._project()
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": [{"name": "X"}]}))
        code, _, err = self._main(["requirements.json"], root)
        self.assertEqual(code, emit_board.EXIT_COULD_NOT_RUN)
        self.assertIn("parts[0]", err)

    def test_a_resistor_the_board_gives_no_voltage_for_is_could_not_run_naming_the_fact(self):
        # F9: series_ohms' refusal was a traceback and exit 1, which check_spine read as a defect in the design
        root = self._project()
        (root / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": ["led-red-5mm"]}))
        code, tsx, err = self._main(["requirements.json"], root)
        self.assertEqual((code, tsx), (emit_board.EXIT_COULD_NOT_RUN, ""))
        self.assertIn("cannot emit a board: led-red-5mm asks for 5 mA through a series resistor, but the board states no "
                      "power.io_volts — nothing to compute it from", err)

    def test_an_led_the_pin_cannot_light_is_could_not_run_too(self):
        # F9: the input asks the impossible, which is could-not-run like every refusal of the input here — not "problems"
        root = self._project()
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        led["facts"]["forward_voltage_v"]["value"] = 3.4
        (root / "parts").mkdir()
        (root / "parts" / "led-red-5mm.json").write_text(json.dumps(led))
        (root / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]}))
        code, tsx, err = self._main(["requirements.json"], root)
        self.assertEqual((code, tsx), (emit_board.EXIT_COULD_NOT_RUN, ""))
        self.assertIn("cannot emit a board: led-red-5mm needs 3.4 V forward, and a 3.3 V pin cannot push current through it", err)


class EachSectionStandsAloneTest(unittest.TestCase):
    """
    `emit()` was one 186-line function with ten sections and 39 branches (sprint audit A5), where
    a rule fixed in one section stayed wrong in the next. Each section is now a function that can
    be driven alone. The composed file is covered by the classes above; these are the sections'.
    """

    BOARD = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_the_file_is_the_sections_in_order_and_nothing_else(self):
        # Every section must be NON-EMPTY here, or the order cannot be seen: the first fixture
        # had no placeholder, and swapping the stand-in and host-requirement sections left the
        # output identical — a mutation the tool reported escaped. So one part is a stand-in.
        board = self.BOARD
        part_list = [parts.load(part_id) for part_id in PARTS]
        part_list[1] = dict(part_list[1], footprint_placeholder=True, footprint_note="stand-in")
        assignments, _ = assign_pins.assign(board, parts.signals_for(PARTS))
        placements, width, height = emit_board.place(board, part_list)
        self.assertTrue(emit_board.stand_in_lines(part_list), "the fixture must have a stand-in")
        self.assertTrue(emit_board.host_requirement_lines(part_list),
                        "the fixture must have a part with host requirements")
        sections = (emit_board.header_lines(board, part_list, placements, width, height)
                    + emit_board.component_lines(part_list, placements)
                    + emit_board.host_part_lines(part_list, placements)
                    + emit_board.signal_lines(part_list, assignments)
                    + emit_board.power_lines(board, part_list, {})
                    + emit_board.stand_in_lines(part_list)
                    + emit_board.host_requirement_lines(part_list)
                    + ["  </board>", ")"])
        self.assertEqual(emit_board.emit(board, part_list, assignments, placements, width, height),
                         "\n".join(sections) + "\n")

    def test_a_pad_naming_no_rail_is_said_not_skipped(self):
        # Was `continue`: the silent drop G2 removed for module pins, kept for the MCU's own.
        board = dict(self.BOARD, power_pads={"GND1": {"rail": "ground"}, "3V3": {}})
        text = "\n".join(emit_board.mcu_power_lines(board, [], {}, set()))
        self.assertIn("Mcu.3V3 NAMES NO RAIL", text)
        self.assertIn('from=".Mcu > .GND1" to="net.GND"', text)

    def test_a_board_with_no_power_pads_at_all_is_said(self):
        board = {key: value for key, value in self.BOARD.items() if key != "power_pads"}
        self.assertIn("DOES NOT SAY WHICH OF ITS PADS ARE POWER",
                      "\n".join(emit_board.mcu_power_lines(board, [], {}, set())))

    def test_the_unjustified_note_names_every_net_nobody_sized(self):
        self.assertEqual(emit_board.unjustified_lines(set()), [])
        self.assertIn("net.GND, net.V33", emit_board.unjustified_lines({"V33", "GND"})[0])

    def test_stand_ins_are_listed_only_when_there_are_any(self):
        real = parts.load("l9110s-module")
        fake = dict(real, id="x", name="x", footprint_placeholder=True, footprint_note="stands in")
        self.assertEqual(emit_board.stand_in_lines([real]), [])
        self.assertIn("X drawn as %s — stands in" % real["footprint"],
                      "\n".join(emit_board.stand_in_lines([fake])))

    def test_host_requirements_are_carried_per_part(self):
        part = dict(parts.load("l9110s-module"), host_requirements=["pull both inputs down"])
        self.assertIn("- %s: pull both inputs down" % part["name"],
                      "\n".join(emit_board.host_requirement_lines([part])))
        self.assertEqual(emit_board.host_requirement_lines([dict(part, host_requirements=[])]), [])


class OnePowerWalkTest(unittest.TestCase):
    """
    The power lists were walked four times, each with its own `net_for` and `continue` (audit
    A6). One generator now; an entry with no rail is not yielded and is reported by the one rule
    that says so.
    """

    PART = {"id": "p", "name": "p", "power": [
        {"pin": "VCC", "rail": "logic", "direction": "in"},
        {"pin": "OUT", "rail": "speaker", "direction": "out", "polarity": "+"},
        {"pin": "NC"}]}

    def test_every_entry_with_a_rail_is_yielded_with_its_net(self):
        got = [(part["name"], supply["pin"], net)
               for part, supply, net in emit_board.power_connections([self.PART])]
        self.assertEqual(got, [("p", "VCC", "V33"), ("p", "OUT", "SPEAKER_P")])

    def test_an_entry_with_no_rail_is_not_yielded_and_is_reported_by_the_one_rule(self):
        self.assertNotIn("NC", [s["pin"] for _, s, _ in emit_board.power_connections([self.PART])])
        self.assertEqual(emit_board.power_pins_with_no_rail([self.PART]), ["p.NC"])

    def test_the_placeholder_filter_is_the_one_the_names_come_from(self):
        real = parts.load("l9110s-module")
        fake = dict(real, id="x", name="x", footprint_placeholder=True, footprint_note="n")
        self.assertEqual(emit_board.placeholders([fake, real]), [fake])
        self.assertEqual(emit_board.placeholder_components([fake, real]), ["X"])


class WhatAPartMustRecordTest(unittest.TestCase):
    # Three helpers the audit found untested (A15); each refusal in `main` rests on one.

    def test_a_part_with_no_footprint_is_named(self):
        part = {k: v for k, v in parts.load("l9110s-module").items() if k != "footprint"}
        self.assertEqual(emit_board.parts_without_a_footprint([part]), [part["name"]])
        self.assertEqual(emit_board.parts_without_a_footprint([parts.load("l9110s-module")]), [])

    def test_a_part_with_no_outline_is_named_and_one_with_is_not(self):
        with_outline = parts.load("l9110s-module")
        without = {k: v for k, v in with_outline.items() if k != "body_mm"}
        self.assertTrue(emit_board.has_an_outline(with_outline))
        self.assertFalse(emit_board.has_an_outline(without))
        self.assertEqual(emit_board.parts_without_an_outline([without]), [with_outline["name"]])
        self.assertEqual(emit_board.parts_without_an_outline([with_outline]), [])


class TwoSuppliesOnOneRailTest(unittest.TestCase):
    """
    Audit B9: a regulator's VOUT on `logic` was traced to net.V33 beside the microcontroller's
    own 3V3 — exit 0, no note. `parts.validate` looks inside one part; this looks across the
    design and at the rails the module itself supplies.
    """

    @staticmethod
    def regulator(name, rail):
        return {"schema": 1, "id": name.lower(), "name": name, "kind": "regulator", "needs": [],
                "power": [{"pin": "VIN", "rail": "traction", "direction": "in"},
                          {"pin": "VOUT", "rail": rail, "direction": "out"},
                          {"pin": "GND", "rail": "ground", "direction": "in"}],
                "pin_order": ["VIN", "VOUT", "GND"], "pin_order_proof": {"verified": False, "source": "a test fixture"}, "footprint": "pinrow3",
                "body_mm": {"width": 10, "height": 10, "verified": True, "source": "test"}}

    def test_a_supply_onto_the_modules_own_rail_is_named(self):
        contended = emit_board.outputs_in_contention([self.regulator("Buck", "logic")])
        self.assertEqual([net for net, _ in contended], ["V33"])
        self.assertIn("Buck.VOUT", contended[0][1])
        self.assertTrue(any("microcontroller" in who for who in contended[0][1]))

    def test_two_supplies_onto_one_rail_are_named(self):
        contended = emit_board.outputs_in_contention(
            [self.regulator("BuckA", "servo"), self.regulator("BuckB", "servo")])
        self.assertEqual(contended, [("SERVO", ["BuckA.VOUT", "BuckB.VOUT"])])

    def test_a_ground_return_from_a_connector_is_not_a_contended_supply(self):
        # The inlet's GND is `out` — where the pack's return meets board ground. The first
        # version of the rule called that a second supply on GND, on every design with an inlet.
        self.assertEqual(emit_board.outputs_in_contention([parts.load("jst-ph-2-power-inlet")]), [])

    def test_one_supply_on_its_own_rail_is_not(self):
        self.assertEqual(emit_board.outputs_in_contention([self.regulator("Buck", "servo")]), [])
        self.assertEqual(emit_board.outputs_in_contention(
            [parts.load(part_id) for part_id in PARTS] + [parts.load("jst-ph-2-power-inlet")]), [])

    def test_the_file_and_the_notes_both_say_it(self):
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / "parts").mkdir()
        (root / "parts" / "buck.json").write_text(json.dumps(self.regulator("Buck", "logic")))
        (root / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["buck"]}))
        code, tsx, err = TheDocumentedInvocationTest._main(["requirements.json"], root)
        self.assertEqual(code, emit_board.EXIT_OK)
        self.assertIn("net.V33 IS DRIVEN BY MORE THAN ONE SUPPLY", tsx)
        self.assertIn("note: net.V33 is driven by more than one supply", err)


class ThePowerHelpersEachHaveANameTest(unittest.TestCase):
    """Audit B16: reached only through `emit`; each has a claim of its own to hold it to."""

    RULES = {"physics": {"rails": {"TRACTION": {"max_current_a": 2.9}}}}

    def test_trace_width_mm_is_none_unless_a_positive_current_is_stated(self):
        self.assertIsNone(emit_board.trace_width_mm("V33", self.RULES))
        self.assertGreater(emit_board.trace_width_mm("TRACTION", self.RULES), copper.MIN_TRACE_WIDTH_MM)
        for bad in (0, -1, "2.9", None):
            rules = {"physics": {"rails": {"X": {"max_current_a": bad}}}}
            self.assertIsNone(emit_board.trace_width_mm("X", rules), bad)

    def test_power_trace_sizes_a_stated_rail_and_records_an_unstated_one(self):
        unjustified = set()
        sized = emit_board.power_trace("Drive", "VCC", "TRACTION", self.RULES, "", unjustified)
        self.assertIn('from=".Drive > .VCC" to="net.TRACTION" thickness="', sized)
        self.assertEqual(unjustified, set())
        bare = emit_board.power_trace("Drive", "GND", "GND", self.RULES, "return", unjustified)
        self.assertNotIn("thickness=", bare)
        self.assertIn("{/* return */}", bare)
        self.assertEqual(unjustified, {"GND"})

    def test_power_note_lines_reports_a_pin_naming_no_rail(self):
        part = {"id": "x", "name": "X", "power": [{"pin": "VCC"}]}
        self.assertIn("X.VCC NAMES NO RAIL", "\n".join(emit_board.power_note_lines([part])))
        self.assertEqual(emit_board.power_note_lines([]), [])

    def test_module_power_lines_traces_every_power_pin_that_names_a_rail(self):
        lines = emit_board.module_power_lines([parts.load("l9110s-module")], self.RULES, set())
        self.assertEqual(len(lines), 2)
        self.assertTrue(any('from=".L9110sModule > .VCC" to="net.MOTOR6V"' in line for line in lines))
        self.assertTrue(any('from=".L9110sModule > .GND" to="net.GND"' in line for line in lines))


class WhatThePartsDemandIsDoneTest(unittest.TestCase):
    """
    P6: a record's `host_parts` become components and traces. The file printed "10 k pulldowns
    on both inputs" under a board whose inputs floated, on the reference design and the car.
    """

    def _emit(self, part, signals=()):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        assignments, _ = assign_pins.assign(board, list(signals))
        placements, width, height = emit_board.place(board, [part])
        return emit_board.emit(board, [part], assignments, placements, width, height, {}), placements

    def _part(self, **extra):
        part = parts.load("l9110s-module")
        part.update(extra)
        return part

    def test_a_pulldown_is_a_resistor_from_the_pad_to_ground(self):
        tsx, _ = self._emit(self._part())  # the shipped record demands 10 k on AIA and AIB
        self.assertIn('<resistor name="L9110sModulePulldownAIA" resistance="10k" footprint="0603"', tsx)
        self.assertIn('<trace from=".L9110sModulePulldownAIA > .pin1" to=".L9110sModule > .AIA" />', tsx)
        self.assertIn('<trace from=".L9110sModulePulldownAIA > .pin2" to="net.GND" />', tsx)
        self.assertIn("Beyond the 2 passive(s) placed above", tsx, "the prose block says what was done")

    def test_a_pullup_goes_to_the_parts_own_rail(self):
        part = self._part(host_parts=[{"kind": "pullup", "pin": "AIA", "ohms": 4700, "why": "test"}])
        tsx, _ = self._emit(part)
        self.assertIn('resistance="4.7k"', tsx)
        self.assertIn('<trace from=".L9110sModulePullupAIA > .pin2" to="net.MOTOR6V" />', tsx,
                      "the L9110S record's VCC sits on the motor rail, so its pull-up does too")

    def test_a_divider_puts_the_hosts_pin_on_the_midpoint(self):
        part = self._part(host_parts=[{"kind": "divider", "pin": "AIA", "top_ohms": 10000, "bottom_ohms": 18000, "why": "5 V pulse"}])
        signals = parts.signals_for(["l9110s-module"])
        tsx, _ = self._emit(part, signals)
        self.assertIn('<trace from=".L9110sModule > .AIA" to=".L9110sModuleDividerAIATop > .pin1" />', tsx)
        self.assertIn('<trace from=".L9110sModuleDividerAIATop > .pin2" to=".L9110sModuleDividerAIABottom > .pin1" />', tsx)
        self.assertIn('<trace from=".L9110sModuleDividerAIABottom > .pin2" to="net.GND" />', tsx)
        self.assertRegex(tsx, r'<trace from="\.Mcu > \.\w+" to="\.L9110sModuleDividerAIATop > \.pin2" />  \{/\* MOTOR_IA',
                         "the host's own trace ends at the midpoint, not at the module's pad")
        self.assertNotRegex(tsx, r'<trace from="\.Mcu > \.\w+" to="\.L9110sModule > \.AIA"')

    def test_a_series_resistor_sits_between_the_hosts_pin_and_the_pad(self):
        # P78: an LED's current-limiting resistor is in the signal's path, not to a rail.
        part = self._part(host_parts=[{"kind": "series", "pin": "AIA", "ohms": 1000, "why": "limits the current"}])
        tsx, _ = self._emit(part, parts.signals_for(["l9110s-module"]))
        self.assertIn('<resistor name="L9110sModuleSeriesAIA" resistance="1k" footprint="0603"', tsx)
        self.assertIn('<trace from=".L9110sModuleSeriesAIA > .pin2" to=".L9110sModule > .AIA" />', tsx)
        self.assertRegex(tsx, r'<trace from="\.Mcu > \.\w+" to="\.L9110sModuleSeriesAIA > \.pin1" />  \{/\* MOTOR_IA',
                         "the host's own trace ends at the resistor")
        self.assertNotRegex(tsx, r'<trace from="\.Mcu > \.\w+" to="\.L9110sModule > \.AIA"')

    def test_a_series_resistor_for_a_current_is_computed_and_the_arithmetic_printed(self):
        # The PO, building the quickstart: "it can find the parts and calculate, right?"
        part = self._part(host_parts=[{"kind": "series", "pin": "AIA", "for_current_ma": 5, "why": "an indicator"}])
        part["facts"] = dict(part.get("facts") or {}, forward_voltage_v={"value": 2.0, "verified": True, "source": "s"})
        tsx, _ = self._emit(part, parts.signals_for(["l9110s-module"]))
        self.assertIn('<resistor name="L9110sModuleSeriesAIA" resistance="270"', tsx,
                      "(3.3 - 2.0) V / 5 mA = 260, rounded UP to E12 so the current never exceeds what was asked")
        self.assertIn("(3.3 V - 2 V) / 5 mA = 260 ohm; next E12 value up: 270 ohm, about 4.8 mA", tsx)

    def test_an_led_the_pin_cannot_light_is_refused_not_given_a_negative_resistor(self):
        part = self._part(host_parts=[{"kind": "series", "pin": "AIA", "for_current_ma": 5, "why": "w"}])
        part["facts"] = dict(part.get("facts") or {}, forward_voltage_v={"value": 3.4, "verified": True, "source": "s"})
        with self.assertRaises(ValueError) as refused:
            self._emit(part, parts.signals_for(["l9110s-module"]))
        self.assertIn("3.4 V", str(refused.exception))

    def test_a_current_without_the_numbers_to_compute_it_is_refused_by_name(self):
        part = self._part(host_parts=[{"kind": "series", "pin": "AIA", "for_current_ma": 5, "why": "w"}])
        with self.assertRaises(ValueError) as refused:
            self._emit(part, parts.signals_for(["l9110s-module"]))
        self.assertIn("forward_voltage_v", str(refused.exception))

    def test_a_pulldown_the_modules_own_pullup_defeats_is_named_in_the_board_file(self):
        # B11 / P81: the shipped L9110S states 10 k pull-ups to VCC and demands 10 k pull-downs.
        tsx, _ = self._emit(self._part())
        self.assertIn("CONFLICT", tsx)
        self.assertIn("idles HIGH, not low, on any supply above 5 V", tsx)

    def test_a_shipped_button_gets_the_pull_up_its_record_asks_for(self):
        # G7 / B13: the record said "give it an external pull" in prose only; the board had none.
        button = parts.load("tactile-button")
        tsx, _ = self._emit(button, parts.signals_for(["tactile-button"]))
        self.assertIn('<resistor name="TactileButtonPullupA" resistance="10k"', tsx)
        self.assertIn('<trace from=".TactileButtonPullupA > .pin2" to="net.V33" />', tsx)

    def test_the_passives_sit_beside_the_modules_not_on_them(self):
        _, placements = self._emit(self._part())
        positions = list(placements.values())
        self.assertEqual(len(positions), len(set(positions)), "no two components share a position")
        module_x = placements["L9110sModule"][0]
        for name in ("L9110sModulePulldownAIA", "L9110sModulePulldownAIB"):
            self.assertGreater(placements[name][0], module_x + emit_board.body_of(self._part())[0] / 2,
                               "%s sits to the right of the module's body" % name)


class WhatARailCarries(unittest.TestCase):
    """
    P52: a rail's load is summed from the facts its members' power pins name, never guessed.

    The figures were already in the records — a servo's 700 mA stall, a buck's 3 A — and nothing
    linked a pin to the fact that states its current, so nothing summed them.
    """

    @staticmethod
    def part(part_id, power, facts=None, instance=None):
        made = {"schema": 1, "id": part_id, "name": part_id, "kind": "test", "needs": [],
                "power": power, "facts": facts or {}}
        if instance:
            made["_instance"] = instance
        return made

    @staticmethod
    def fact(value, verified=True):
        return {"value": value, "verified": verified, "source": "test"}

    def servo(self, stall=700, verified=False):
        return self.part("sg90-servo", [{"pin": "VCC", "rail": "servo", "direction": "in",
                                         "draws": "stall_current_ma"},
                                        {"pin": "GND", "rail": "ground", "direction": "in"}],
                         {"stall_current_ma": self.fact(stall, verified),
                          "idle_current_ma": self.fact(10)})

    def buck(self, rating=3.0, out_rail="servo"):
        return self.part("buck", [{"pin": "VIN", "rail": "traction", "direction": "in",
                                   "feeds": "VOUT"},
                                  {"pin": "VOUT", "rail": out_rail, "direction": "out",
                                   "can_supply": "output_current_a"}],
                         {"output_current_a": self.fact(rating)})

    def test_a_load_is_read_from_the_fact_its_pin_names_in_that_facts_unit(self):
        rail = emit_board.rail_loads([self.servo(), self.buck()])["SERVO"]
        self.assertAlmostEqual(rail["amps"], 0.7, msg="stall_current_ma, not idle_current_ma")
        self.assertTrue(rail["complete"])

    def test_microamps_and_amps_are_scaled_too(self):
        rtc = self.part("rtc", [{"pin": "VCC", "rail": "servo", "direction": "in",
                                 "draws": "active_supply_current_ua.active_max"}],
                        {"active_supply_current_ua": self.fact({"active_max": 200, "standby_max": 110})})
        motor = self.part("motor", [{"pin": "VCC", "rail": "servo", "direction": "in",
                                     "draws": "run_current_a"}], {"run_current_a": self.fact(1.5)})
        rail = emit_board.rail_loads([rtc, motor, self.buck()])["SERVO"]
        self.assertAlmostEqual(rail["amps"], 1.5002, msg="a dotted pointer reads one key of the value")

    def test_a_load_whose_figure_is_null_is_named_not_summed_as_zero(self):
        probe = self.part("probe", [{"pin": "VCC", "rail": "servo", "direction": "in",
                                     "draws": "operating_current_ma"}],
                          {"operating_current_ma": self.fact(None, verified=False)}, instance="Soil1")
        rail = emit_board.rail_loads([probe, self.servo(), self.buck()])["SERVO"]
        self.assertFalse(rail["complete"])
        self.assertAlmostEqual(rail["amps"], 0.7, msg="what IS stated is still summed")
        self.assertEqual(len(rail["missing"]), 1)
        self.assertIn("Soil1.VCC", rail["missing"][0])
        self.assertIn("operating_current_ma", rail["missing"][0])

    def test_an_input_that_names_no_fact_is_named_as_missing(self):
        mute = self.part("mute", [{"pin": "VCC", "rail": "servo", "direction": "in"}])
        rail = emit_board.rail_loads([mute, self.buck()])["SERVO"]
        self.assertFalse(rail["complete"])
        self.assertIn("Mute.VCC", rail["missing"][0])

    def test_a_pointer_to_a_fact_with_no_current_unit_is_refused_not_read_as_amps(self):
        odd = self.part("odd", [{"pin": "VCC", "rail": "servo", "direction": "in",
                                 "draws": "stall_current"}], {"stall_current": self.fact(700)})
        rail = emit_board.rail_loads([odd, self.buck()])["SERVO"]
        self.assertFalse(rail["complete"], "700 of what — amps, milliamps? Not a guess to make")

    def test_the_supply_and_its_rating_come_from_the_output_pin(self):
        supply = emit_board.rail_loads([self.servo(), self.buck(rating=3.0)])["SERVO"]["supply"]
        self.assertEqual(supply["who"], "Buck.VOUT")
        self.assertAlmostEqual(supply["amps"], 3.0)

    def test_a_converter_input_draws_what_its_output_carries(self):
        rails = emit_board.rail_loads([self.servo(stall=700), self.buck()])
        self.assertAlmostEqual(rails["TRACTION"]["amps"], 0.7,
                               msg="a step-down converter draws at most what it delivers")
        self.assertTrue(rails["TRACTION"]["complete"])

    def test_a_converter_whose_output_is_not_fully_stated_leaves_its_input_open(self):
        mute = self.part("mute", [{"pin": "VCC", "rail": "servo", "direction": "in"}])
        rails = emit_board.rail_loads([mute, self.buck()])
        self.assertFalse(rails["TRACTION"]["complete"])
        self.assertIn("Buck.VIN", rails["TRACTION"]["missing"][0])

    def test_unverified_figures_are_carried_so_a_sum_can_say_what_it_rests_on(self):
        rail = emit_board.rail_loads([self.servo(verified=False), self.buck()])["SERVO"]
        self.assertIn("Sg90Servo.VCC", " ".join(rail["unverified"]))

    def test_ground_is_not_a_rail_with_a_load(self):
        self.assertNotIn("GND", emit_board.rail_loads([self.servo(), self.buck()]))

    def test_the_module_feeds_its_own_logic_rail_and_takes_its_own_share_of_it(self):
        board = {"power_pads": {"VCC": {"rail": "servo", "direction": "in", "feeds": "3V3"},
                                "3V3": {"rail": "logic", "direction": "out",
                                        "can_supply": "regulator_3v3_a",
                                        "own_draw": "module_peak_a"},
                                "GND1": {"rail": "ground", "direction": "out"}},
                 "power": {"regulator_3v3_a": self.fact(1.5), "module_peak_a": self.fact(0.355)}}
        rails = emit_board.rail_loads([self.servo(stall=700), self.buck()], board)
        self.assertAlmostEqual(rails["V33"]["amps"], 0.355)
        self.assertAlmostEqual(rails["V33"]["supply"]["amps"], 1.5)
        self.assertAlmostEqual(rails["SERVO"]["amps"], 1.055,
                               msg="the servo's stall plus everything the module draws through VCC")

    def test_the_generator_sizes_a_rail_the_rules_leave_null_from_its_records(self):
        """
        P52's second half: the trace was emitted at the router's default with a note calling it
        unjustified, while the records held the servo's stall the whole time — and the checker,
        reading the same records, would then judge the default against it.
        """
        lines = "\n".join(emit_board.power_lines({}, [self.servo(stall=1500), self.buck()], {}))
        self.assertRegex(lines, r'from="\.Sg90Servo > \.VCC" to="net\.SERVO" thickness="[\d.]+mm"')
        unjustified = [line for line in lines.splitlines() if "IS UNJUSTIFIED" in line]
        self.assertNotIn("net.SERVO", " ".join(unjustified))

    def test_a_stated_current_still_beats_the_records(self):
        rules = {"physics": {"rails": {"SERVO": {"max_current_a": 0.05}}}}
        filled = emit_board.rules_with_record_currents(rules, {"SERVO": {"amps": 1.5, "complete": True}})
        self.assertEqual(filled["physics"]["rails"]["SERVO"]["max_current_a"], 0.05)

    def test_an_open_rail_is_not_filled_from_a_partial_sum(self):
        filled = emit_board.rules_with_record_currents({}, {"SERVO": {"amps": 0.7, "complete": False}})
        self.assertNotIn("SERVO", filled["physics"]["rails"], "a partial sum would size it too thin")

if __name__ == "__main__":
    unittest.main()
