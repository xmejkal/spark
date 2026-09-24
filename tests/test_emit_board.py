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
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import assign_pins  # noqa: E402
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
        # One trace per signal, no more and no less. A dropped signal is a module that does not
        # work; a duplicated one is a short.
        self.assertEqual(self.tsx.count('<trace from=".Mcu'), len(parts.signals_for(PARTS)))

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
        # The other half: if outputs getting their own net turned into every pin getting its own
        # net, nothing would connect to anything.
        tsx = self._emit(["dfr0534-module", "l9110s-module"])
        self.assertEqual(tsx.count('to="net.GND"'), 2)

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
        # The rangefinder deliberately has none: four different VL6180X breakouts exist and they
        # do not share a pinout, so any order would be invented.
        unpinned = parts.load("vl6180x-breakout")
        self.assertIn(unpinned["name"], emit_board.parts_without_a_pinout([unpinned]))

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
