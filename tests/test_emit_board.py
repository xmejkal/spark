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

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
import copper  # noqa: E402
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

    def test_the_microcontroller_is_wired_to_ground_and_its_logic_rail(self):
        # The board file says which of its pads are power; every one of them must appear. A
        # processor connected to no ground builds, routes, and reports no error.
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        for pad in (board.get("power_pads") or {}):
            with self.subTest(pad=pad):
                self.assertIn('<trace from=".Mcu > .%s" to="net.' % pad, self.tsx)

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
                "pin_order": ["VCC", "GND"], "footprint": "pinrow2",
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
                "pin_order": ["A", "B"], "footprint": "pushbutton",
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
        self.assertEqual(emit_board.signal_name(left, left["needs"][0]), "BTNLEFT_BUTTON")
        self.assertEqual(emit_board.signal_name(right, right["needs"][0]), "BTNRIGHT_BUTTON")

    def test_an_unnamed_part_keeps_its_bare_signal_name(self):
        plain = self.button()
        self.assertEqual(emit_board.signal_name(plain, plain["needs"][0]), "BUTTON")

    def test_a_bare_string_and_an_object_are_both_valid_entries(self):
        self.assertEqual(
            emit_board.requested_parts({"parts": ["l9110s-module",
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
                "needs": [], "power": power, "pin_order": [s["pin"] for s in power],
                "footprint": "pinrow%d" % len(power)}

    def test_a_rail_nobody_thought_of_becomes_a_net(self):
        self.assertEqual(emit_board.net_name_for_rail("servo"), "SERVO")
        self.assertEqual(emit_board.net_name_for_rail("traction"), "TRACTION")

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
        module_grounds = [line for line in tsx.splitlines()
                          if 'to="net.GND"' in line and '.Mcu >' not in line]
        self.assertEqual(len(module_grounds), 2)

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


if __name__ == "__main__":
    unittest.main()
