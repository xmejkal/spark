"""
Proof that a part says what it needs, and admits what nobody has checked.

A part library is easy to build in a way that is worse than not having one. The temptation is one
schema for everything a part might have — and since a motor driver's facts have nothing in common
with a rangefinder's, that schema collapses into `{name, notes}`: documentation pretending to be
configuration. So the split is the design, and both halves are tested here.

`needs` is a real schema because it is genuinely uniform: every part asks its host for pins. It
is what makes this data rather than prose, and what `assign_pins.py` consumes.

`facts` is open, but every entry must carry a value, a source, and whether anyone actually
checked. The contract's sharpest rule is about the unverified ones: a number nobody has confirmed
must say what depends on it, or not be carried at all. That is how an assumption becomes a fact
without anyone deciding to promote it.

    python3 -m unittest discover -s tests
"""

import contextlib
import hashlib
import io
import json
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from board_library import board_missing  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.design import pin_assigner  # noqa: E402
from spark.records import missing_facts  # noqa: E402
from spark.core import outcomes  # noqa: E402
import parts  # noqa: E402
from spark.records import record_kind  # noqa: E402
from spark.sourcing import brief_choices, datasheets, list_unverified, part_facts, part_records, record_home  # noqa: E402
from spark.sourcing.set_drawer import SetDrawer  # noqa: E402
from spark.core import cli  # noqa: E402
from spark.core.errors import CodedMessageError  # noqa: E402
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402
from spark.records.answer_operation import AnswerOperation  # noqa: E402
from spark.sourcing import part_rules  # noqa: E402
from spark.records import store  # noqa: E402
from flat_message import NASTY, assert_flat  # noqa: E402


def in_store(home):
    """Point the store at a scratch folder for one block (P88): SPARK_HOME, read on every call."""
    return mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})


def part(part_id="thing", **overrides):
    definition = dict({
        "schema": 1, "id": part_id, "name": "A Thing", "kind": "test",
        "needs": [{"signal": "SIG", "pin": "P", "direction": "in"}],
    }, **overrides)
    if definition.get("pin_order") and "pin_order_proof" not in definition:
        definition["pin_order_proof"] = {"verified": False, "source": "a test fixture"}  # P81
    return definition


def written(definition):
    path = Path(tempfile.mkdtemp()) / (definition["id"] + ".json")
    path.write_text(json.dumps(definition))
    return path


class TheContractTest(unittest.TestCase):
    def _problems(self, **overrides):
        definition = part(**overrides)
        return part_records.validate(definition, written(definition))

    def test_a_good_definition_passes(self):
        self.assertEqual(self._problems(), [])

    def test_a_need_with_no_pin_is_caught(self):
        problems = self._problems(needs=[{"signal": "SIG"}])
        self.assertTrue(any("has no pin" in p for p in problems))

    def test_a_need_with_no_pin_is_caught_even_when_the_part_has_a_pin_order(self):
        """
        The validator crashed on exactly the malformation it exists to catch.

        `needs[0] has no pin` was appended, and three lines later the pin_order block read
        `need["pin"]` on that same entry and raised KeyError. Every real part has a pin_order, so
        any part broken this way took the whole run down instead of being reported — and the run
        it took down was `--validate`, whose entire job is surviving bad records long enough to
        describe them.
        """
        problems = self._problems(needs=[{"signal": "SIG"}], pin_order=["A", "B"])
        self.assertTrue(any("has no pin" in p for p in problems), problems)

    def test_a_power_entry_with_no_pin_is_caught_rather_than_crashing(self):
        # The SECOND instance of the same crash, found by writing the test for the first. Only
        # `needs` entries were checked for a pin, and `power` was then read with `["pin"]` in
        # four places — a rule written at the use site instead of in the contract.
        problems = self._problems(power=[{"rail": "logic", "direction": "in"}], pin_order=["P"])
        self.assertTrue(any("power[0] has no pin" in p for p in problems), problems)

    def test_an_unused_pin_entry_with_no_pin_is_caught_too(self):
        problems = self._problems(unused_pins=[{"note": "left floating"}])
        self.assertTrue(any("unused_pins[0] has no pin" in p for p in problems), problems)

    def test_a_well_formed_power_entry_is_not_reported(self):
        # The rule was widened, not made noisy.
        self.assertEqual(self._problems(
            power=[{"pin": "VCC", "rail": "logic", "direction": "in"}],
            pin_order=["P", "VCC"]), [])

    def test_a_capability_no_pin_can_offer_is_caught_where_it_is_written(self):
        """
        Two halves of the plugin disagreed, and the honest record was the one punished.

        A servo declaring `needs: ["pwm"]` — which is true, a servo is a pulse-width device —
        validated as a good record here, and then made `assign_pins` refuse the ENTIRE design,
        because that file kept its own vocabulary of `("wake", "adc")`. The only way to get a
        board out was to delete a true fact about the part.

        There is now one `CAPABILITIES`, owned by this file because a capability is a claim a
        PART makes, and `assign_pins` imports it.
        """
        problems = self._problems(
            needs=[{"signal": "S", "pin": "P", "direction": "in", "needs": ["telepathy"]}])
        self.assertTrue(any("telepathy" in p for p in problems), problems)

    def test_pwm_is_a_thing_a_part_may_ask_for(self):
        self.assertEqual(self._problems(
            needs=[{"signal": "S", "pin": "P", "direction": "in", "needs": ["pwm"]}]), [])

    def test_the_assigner_reads_the_same_vocabulary_this_file_validates(self):
        # The disagreement is gone structurally, not by keeping two lists in step.
        from spark.design import pin_assigner
        self.assertIs(pin_assigner.CAPABILITIES, part_rules.CAPABILITIES)

    def test_a_placeholder_footprint_must_say_what_the_real_one_is(self):
        """
        The most expensive field to get wrong was the one field with no way to say "not yet".

        `facts` and `body_mm` carry `verified`; the footprint carried nothing. An XT30 drawn as a
        JST PH — wrong pitch, wrong hole, stated as a stand-in in a comment nothing reads — looked
        identical to a footprint generated from a vendor drawing, and `check_footprints` measured
        the JST's annular rings and reported a defect about a part that is not on the board.
        """
        problems = self._problems(footprint="jst_ph_2", footprint_placeholder=True)
        self.assertTrue(any("footprint_note" in p for p in problems), problems)

    def test_a_placeholder_WITH_a_note_is_a_valid_record(self):
        self.assertEqual(self._problems(
            footprint="jst_ph_2", footprint_placeholder=True,
            footprint_note="stands in for an XT30-PW nobody has drawn"), [])

    def test_a_footprint_is_the_name_of_one_and_a_number_or_a_list_is_not(self):
        for given, said in ((5, "footprint is 5"), (True, "footprint is True"), (3.5, "footprint is 3.5"),
                            (["pinrow2"], "footprint is ['pinrow2']"), ({"name": "pinrow2"}, "footprint is {'name': 'pinrow2'}")):
            with self.subTest(footprint=given):
                problems = self._problems(footprint=given)
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith(said), problems)
        for given in ("pinrow2", "jlcpcb:C2040", None, "", [], {}):
            with self.subTest(footprint=given):
                self.assertEqual(self._problems(footprint=given), [], "a name is a footprint, and an absent one is owed, not wrong")

    def test_a_real_footprint_needs_no_note(self):
        # Opt-in, so the five shipped records and every honest footprint are untouched.
        self.assertEqual(self._problems(footprint="pinrow5"), [])
        self.assertFalse(part_facts.has_placeholder_footprint(part(footprint="pinrow5")))

    def test_a_footprint_that_is_no_footprinter_name_is_refused(self):
        """
        C-1 (the council on PR #98): the generated board is written with the footprint as an attribute's text, unescaped
        (P87, #19), and `--fact-set` took any string, `--audit` called such a record current, and `--requirements` shelved
        it "so every project builds with it" — code from a web page, one command from `board.tsx`. A footprint is a
        footprinter's name or a JLCPCB part, and nothing else.
        """
        for given in ('pinrow4" onClick={alert(1)} data-x="', 'pushbutton"} pcbX={(globalThis.x = 1, 0)} data-x="',
                      "pinrow 4", "PINROW4", "jst_ph_2>", "jlcpcb:C12a", "kicad:R_0603", "pinrow4\n"):
            with self.subTest(footprint=given):
                problems = self._problems(footprint=given)
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith("footprint is %r" % given), problems)
                self.assertIn("jlcpcb:C<number>", problems[0])
        for given in ("pinrow5", "jst_ph_3", "dip12_w15.24mm", "0603", "sot23_3", "pushbutton", "jlcpcb:C2040"):
            with self.subTest(footprint=given):
                self.assertEqual(self._problems(footprint=given), [], "a footprinter's name, or a JLCPCB part")

    def test_an_id_that_is_no_plain_key_is_refused(self):
        # P87's attribute half: a record's id is its file's name, and emit_board names the part after it, `<chip name="…">`
        for part_id in ('x"y', "Lone_Sensor", "X-LED", "x*y"):
            with self.subTest(id=part_id):
                self.assertEqual(self._problems(part_id=part_id), [
                    "id is %r, but an id is a plain key — lower-case letters, digits and - (led-red-5mm): files are named by "
                    "it, and the board names the part after it in code" % part_id])

    def test_a_rail_or_a_signal_that_is_no_name_is_refused(self):
        """
        P87's attribute half (after F11): a rail becomes the net the board is written with — `to="net.<RAIL>"`, upper-cased —
        so a crafted one was code in board.tsx past --validate, --audit and --requirements. A rail and a signal are names:
        letters, digits and _, as a pin is; every rail and signal the library ships is one.
        """
        for rail in ('gnd" pcbX={(globalThis.x = 1, 0)} y="', "motor 6v", "5v-rail", "gnd\n", 5):
            with self.subTest(rail=rail):
                problems = self._problems(power=[{"pin": "GND", "rail": rail, "direction": "in"}])
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith("power[0] rail is %r, but a rail is a name" % (rail,)), problems)
                self.assertIn("the board is written with it as code", problems[0])
        for signal in ('SIG" x="', "IN+", "A */ x", "MOTOR IA"):
            with self.subTest(signal=signal):
                problems = self._problems(needs=[{"signal": signal, "pin": "P", "direction": "in"}])
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith("needs[0] signal is %r, but a signal is a name" % signal), problems)
        for rail in ("ground", "logic", "motor", "speaker", "5v", "TRACTION"):
            with self.subTest(rail=rail):
                self.assertEqual(self._problems(power=[{"pin": "GND", "rail": rail, "direction": "in"}]), [])
        for signal in ("MOTOR_IA", "STATUS_LED", "TOF_INT", "SDA"):
            with self.subTest(signal=signal):
                self.assertEqual(self._problems(needs=[{"signal": signal, "pin": "P", "direction": "in"}]), [])

    def test_a_silkscreen_that_would_end_the_comment_the_board_keeps_it_in_is_refused(self):
        """C-1: the generated board keeps `printed` in a `{/* … */}` comment, which `*/` ends — what follows would be code —
        and a `"` would end a string; every other silkscreen stays the person's to write."""
        for printed in ("IN+ */} <chip name=\"X\" /> {/*", 'VIN"', "*/"):
            with self.subTest(printed=printed):
                problems = self._problems(needs=[{"signal": "S", "pin": "VIN", "printed": printed, "direction": "in"}])
                self.assertEqual(len(problems), 1, problems)
                self.assertTrue(problems[0].startswith("needs[0] printed %r" % printed), problems)
        for printed in ("IN+", "OUT-", "GPIO0/CE", "SPK+", "~RESET", "3V3 (out)"):
            with self.subTest(printed=printed):
                self.assertEqual(self._problems(needs=[{"signal": "S", "pin": "VIN", "printed": printed, "direction": "in"}]), [])

    def test_a_pin_name_a_selector_cannot_parse_is_caught_where_it_is_written(self):
        """
        Measured on a probe board: `IN+`, `OUT-` and `A.B` do not resolve as tscircuit selectors;
        `V_IN`, `GND2` and `3V3` do. An MP1584's pads are silkscreened IN+ IN- OUT+ OUT-, a record
        using those names produced four "could not find port" errors, and the rename that fixed
        it LOST the silkscreen — the exact failure `pad_aliases` prevents on the board side.
        """
        for bad in ("IN+", "OUT-", "A.B", "V IN", "A\n"):  # the re-check: `A⏎` passed and broke the build, a string unterminated
            with self.subTest(pin=bad):
                problems = self._problems(needs=[{"signal": "S", "pin": bad, "direction": "in"}])
                self.assertTrue(any("cannot be a selector" in p for p in problems), problems)

    def test_the_names_that_DO_resolve_are_not_refused(self):
        for good in ("VIN", "GND2", "3V3", "V_IN", "a"):
            with self.subTest(pin=good):
                self.assertEqual(self._problems(
                    needs=[{"signal": "S", "pin": good, "direction": "in"}]), [])

    def test_the_silkscreen_may_say_anything(self):
        # `printed` is what is on the part. It never reaches a selector, so nothing constrains it but the two marks that
        # would end the comment the board keeps it in (C-1, below).
        self.assertEqual(self._problems(
            needs=[{"signal": "S", "pin": "VIN", "printed": "IN+", "direction": "in"}]), [])

    def test_printed_names_are_collected_only_where_they_differ(self):
        record = part(needs=[{"signal": "S", "pin": "VIN", "printed": "IN+", "direction": "in"}],
                      power=[{"pin": "GND", "printed": "GND", "rail": "ground", "direction": "in"}])
        self.assertEqual(part_facts.printed_names(record), {"VIN": "IN+"})

    def test_a_nonsense_direction_is_caught(self):
        problems = self._problems(needs=[{"signal": "S", "pin": "P", "direction": "sideways"}])
        self.assertTrue(any("direction" in p for p in problems))

    def test_a_fact_without_provenance_is_caught(self):
        # A number with no source is an opinion, and this library's whole value is telling the
        # two apart.
        problems = self._problems(facts={"current_ma": {"value": 20, "verified": True}})
        self.assertTrue(any("source" in p for p in problems))

    def test_a_fact_that_is_no_object_is_caught(self):
        self.assertEqual(self._problems(facts={"x": "s"}), ["facts.x is 's', but it is an object"])

    def test_a_fact_claiming_to_be_verified_with_no_value_is_caught(self):
        problems = self._problems(
            facts={"x": {"value": None, "verified": True, "source": "somewhere"}})
        self.assertTrue(any("verified but has no value" in p for p in problems))

    def test_an_unverified_number_must_say_what_depends_on_it(self):
        # The sharpest rule in the contract. An unexplained guess with a number attached is how
        # an assumption gets treated as a fact — nobody promotes it, it just stops being
        # questioned.
        problems = self._problems(
            facts={"idle_ma": {"value": 20, "verified": False, "source": "a guess"}})
        self.assertTrue(any("why_it_matters" in p for p in problems))

    def test_an_unverified_number_WITH_a_reason_is_fine(self):
        self.assertEqual(self._problems(facts={"idle_ma": {
            "value": 20, "verified": False, "source": "a guess",
            "why_it_matters": "decides whether the battery lasts a day or a month"}}), [])

    def test_an_unknown_with_no_value_needs_no_justification(self):
        # "Nobody knows" is an honest state and must not be made tedious to record.
        self.assertEqual(self._problems(facts={"idle_ma": {
            "value": None, "verified": False, "source": "not measured"}}), [])

    #: A document the record keeps, so a citation of it has nothing to be refused for but its own form (P785).
    KEPT_P1 = {"url": "https://v.example/p1.pdf", "sha256": "a" * 64, "file": "p1.pdf", "retrieved": "2026-11-12",
               "title": "P1", "version": None}

    def test_a_cites_that_is_a_string_is_one_problem_that_states_the_form(self):
        # P785 (P737 row 74): `cites: "p1"` passed every rule, because only an object was read as a citation
        problems = self._problems(documents={"p1": self.KEPT_P1},
                                  facts={"io_volts": {"value": 3.3, "verified": True, "source": "the datasheet", "cites": "p1"}})
        self.assertEqual(problems, ['facts.io_volts cites \'p1\', but a citation is an object {"document": "<key in documents>", '
                                    '"at": "<page or table>"}'])

    def test_a_cites_that_is_a_list_and_a_cites_inside_a_list_item_are_named_by_their_path(self):
        problems = self._problems(documents={"p1": self.KEPT_P1},
                                  body_mm={"width": 10, "height": 5, "verified": True, "source": "the drawing", "cites": ["p1"]},
                                  power=[{"pin": "VCC", "rail": "logic", "direction": "in", "cites": "p1"}])
        self.assertEqual([p.split(" cites ")[0] for p in problems if "a citation is an object" in p], ["body_mm", "power[0]"])

    def test_a_cites_that_is_null_or_an_object_naming_a_kept_document_is_no_problem(self):
        for cites in (None, {"document": "p1", "at": "page 3"}):
            with self.subTest(cites=cites):
                self.assertEqual(self._problems(documents={"p1": self.KEPT_P1},
                                                facts={"io_volts": {"value": 3.3, "verified": True, "source": "the datasheet", "cites": cites}}), [])


class WhatAPartAsksForTest(unittest.TestCase):
    def test_signals_come_out_ready_for_the_assigner(self):
        signals = part_facts.signals_for(["l9110s-module"])
        self.assertEqual([s["name"] for s in signals], ["MOTOR_IA", "MOTOR_IB"])
        self.assertTrue(all(s["from"] == "l9110s-module" for s in signals))

    def test_a_capability_a_part_needs_survives_into_the_signal(self):
        signals = part_facts.signals_for(["vl6180x-breakout"])
        interrupt = next(s for s in signals if s["name"] == "TOF_INT")
        self.assertIn("wake", interrupt["needs"])

    def test_a_bus_signal_is_marked_as_one(self):
        signals = part_facts.signals_for(["vl6180x-breakout"])
        self.assertEqual({s["name"] for s in signals if s.get("bus") == "i2c"}, {"SDA", "SCL"})

    def test_an_optional_signal_is_still_offered(self):
        # Dropping it silently would hide a requirement. A caller that does not want the sensor
        # to wake the host can remove it; it must not vanish on its own.
        self.assertIn("TOF_INT", [s["name"] for s in part_facts.signals_for(["vl6180x-breakout"])])


class WhatNobodyHasCheckedTest(unittest.TestCase):
    def test_unverified_facts_are_collected_across_parts(self):
        questions = part_facts.unverified(["dfr0534-module", "vl6180x-breakout"])
        self.assertTrue(questions)
        self.assertTrue(all("why_it_matters" in q for q in questions))

    def test_a_verified_fact_is_not_reported_as_open(self):
        names = {q["fact"] for q in part_facts.unverified(["l9110s-module"])}
        self.assertNotIn("input_high_threshold_v", names)

    def test_the_audio_module_declares_its_unmeasured_idle_current(self):
        # The single most consequential unknown on the project this came from. If the library
        # cannot surface that, it is not doing its job.
        questions = part_facts.unverified(["dfr0534-module"])
        self.assertIn("idle_current_ma", {q["fact"] for q in questions})

    def test_a_joystick_lists_ten_rows_and_the_guessed_outline_row_says_where_it_goes_back(self):
        # P373: the outline is a fact nobody checked, so it is listed beside the eight facts and the pin order.
        home = Path(tempfile.mkdtemp()); (home / "catalog").mkdir()
        facts = {"fact_%d" % n: {"value": n, "verified": False, "source": "the maker's page", "why_it_matters": "it matters"}
                 for n in range(8)}
        record = part("x-joy", pin_order=["GND", "VCC", "X"], facts=facts, body_mm={
            "width": 34, "height": 26, "verified": False, "source": "a guess from the photo", "why_it_matters": "the fit"})
        (home / "catalog" / "x-joy.json").write_text(json.dumps(record))
        with in_store(home):
            said, code = run_json(["--unverified", "x-joy"])
        self.assertEqual((code, len(said["assumptions"])), (0, 10))
        self.assertEqual(said["assumptions"][-1], {"fact": "x-joy.body_mm", "basis": "unverified", "assumed": {"width": 34, "height": 26},
                                                   "sentence": "the fit", "source": "a guess from the photo", "write": "body_mm",
                                                   "read_by": [{"consumer": "spark.design.board_components", "status": "reads", "card": None},
                                                               {"consumer": "spark.design.need_requirements", "status": "reads", "card": None}]})
        self.assertNotIn("read_by", said["assumptions"][7], "a fact nothing reads names no reader (P738)")
        self.assertEqual([row["write"] for row in said["assumptions"][7:]], ["facts.fact_7", "pin_order_proof", "body_mm"])
        self.assertEqual([(step["op"], step["argv"], step["effects"]) for step in said["next"]],
                         [("fact-set", ["--fact-set", "x-joy", "<file>"], ["writes"])])
        self.assertEqual(said["next"][0]["env"], {"SPARK_HOME": str(home.resolve())})  # the run's store rides the step (P473)
        with in_store(home), contextlib.redirect_stdout(io.StringIO()) as out:
            parts.main(["--unverified", "x-joy"])
        self.assertTrue(out.getvalue().rstrip().splitlines()[-1].startswith("  next: parts.py --fact-set x-joy <file> — "), out.getvalue())
        self.assertIn("      read by spark.design.board_components (reads)\n", out.getvalue())

    def test_a_reader_that_will_read_a_fact_prints_its_card(self):
        # P738: no record reaches a `will read` row today (a block's write key is the block), so the line is proved here.
        from spark.records.fact_needs import FactNeed, READS, WILL_READ
        self.assertEqual(list_unverified._reader_line(FactNeed("module", "body_mm", "spark.x.Y", WILL_READ, "P734")),
                         "      read by spark.x.Y (will read, P734)")
        self.assertEqual(list_unverified._reader_line(FactNeed("module", "body_mm", "spark.x.Y", READS)),
                         "      read by spark.x.Y (reads)")

    def test_the_next_step_names_the_first_part_with_a_row_that_can_go_back_and_none_when_no_row_can(self):
        # P373: a record whose facts is no object has one row with `write` null, and `--fact-set` would refuse it.
        home = Path(tempfile.mkdtemp()); (home / "catalog").mkdir()
        (home / "catalog" / "x-bad.json").write_text(json.dumps(part("x-bad", facts=[])))
        (home / "catalog" / "x-good.json").write_text(json.dumps(part("x-good", facts={
            "f": {"value": 1, "verified": False, "source": "the maker's page", "why_it_matters": "it matters"}})))
        with in_store(home):
            both, _ = run_json(["--unverified", "x-bad", "x-good"])
            alone, _ = run_json(["--unverified", "x-bad"])
            with contextlib.redirect_stdout(io.StringIO()) as out:
                parts.main(["--unverified", "x-bad"])
        self.assertEqual([step["argv"] for step in both["next"]], [["--fact-set", "x-good", "<file>"]])
        self.assertEqual(([row["write"] for row in alone["assumptions"]], alone["next"]), ([None], []))
        self.assertNotIn("next:", out.getvalue())
        self.assertIn("repair the file by hand", out.getvalue())


class FromPartsToAPinMapTest(unittest.TestCase):
    """The whole point: a list of modules in, a defensible pin map out."""

    def setUp(self):
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.signals = part_facts.signals_for(
            ["l9110s-module", "vl6180x-breakout", "dfr0534-module"])

    def test_every_signal_the_parts_ask_for_is_placed(self):
        assignments, _ = pin_assigner.assign(self.board, self.signals)
        self.assertEqual({a["signal"] for a in assignments},
                         {s["name"] for s in self.signals})

    def test_i2c_lands_on_the_boards_own_i2c_pins(self):
        # It went to two arbitrary GPIOs once, while the pin actually labelled SDA was given to
        # an analogue input. That is wrong twice: the bus loses its hardware peripheral, and the
        # silkscreen now lies about what is connected to it.
        assignments, _ = pin_assigner.assign(self.board, self.signals)
        placed = {a["signal"]: a["pin"] for a in assignments}
        self.assertEqual(placed["SDA"], "SDA")
        self.assertEqual(placed["SCL"], "SCL")

    def test_the_sensor_interrupt_lands_somewhere_that_can_wake_the_chip(self):
        assignments, _ = pin_assigner.assign(self.board, self.signals)
        interrupt = next(a for a in assignments if a["signal"] == "TOF_INT")
        self.assertIn(interrupt["gpio"], self.board["wake_capable_gpio"])

    def test_nothing_lands_on_a_strapping_pin(self):
        assignments, _ = pin_assigner.assign(self.board, self.signals)
        strapping = set(self.board["pin_roles"]["strapping"]["gpio"])
        self.assertEqual([a for a in assignments if a["gpio"] in strapping], [])


class APwmPinTest(unittest.TestCase):
    """A steering servo is the part that made `pwm` necessary."""

    def setUp(self):
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())

    def test_a_pwm_signal_is_placed_on_this_board(self):
        placed, _ = pin_assigner.assign(self.board, [{"name": "STEER", "needs": ["pwm"]}])
        self.assertEqual(len(placed), 1)

    def test_every_pin_offers_pwm_when_the_board_does_not_say_otherwise(self):
        # Deliberate: an ESP32 routes LEDC through a GPIO matrix, so any output pin can do it.
        # The default is a statement about the chips this tool targets, not an omission.
        self.assertIn("pwm", pin_assigner.capability_of(self.board, self.board["pins"]["D3"]))

    def test_a_board_that_LISTS_its_pwm_pins_is_believed_instead(self):
        # Most STM32 parts have a fixed timer map, and a servo must not land off it.
        limited = dict(self.board, pwm_gpio=[self.board["pins"]["D3"]])
        self.assertIn("pwm", pin_assigner.capability_of(limited, limited["pins"]["D3"]))
        self.assertNotIn("pwm", pin_assigner.capability_of(limited, limited["pins"]["D5"]))


class ABusPinComesAfterThePlainPinsTest(unittest.TestCase):
    """
    Nothing marked SCK, MI and MO as a bus, so the assigner spent all three on two LEDs and a
    button — the cheapest pins left, by its lights — and a later SPI part had nowhere to go.
    Found by a cold rebuild of the bin and left open as backlog P3 until 2026-09-29.

    A bus signal still lands on its own named pin: that path runs first and ignores penalties.
    This is only about PLAIN signals: among pins that waste the same abilities a bus pin comes last,
    and a pin that wastes one more (wake, ADC1) costs more than a bus pin. The order is the design's
    (P3); P780 made the docs say it.
    """

    def setUp(self):
        self.board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.spi = set(self.board["pin_roles"]["spi"]["gpio"])
        self.i2c = set(self.board["pin_roles"]["i2c"]["gpio"])

    def test_the_board_records_which_pins_are_a_bus(self):
        # The data, since the assigner can only avoid what the board file names.
        self.assertEqual(self.spi, {self.board["pins"][k] for k in ("MOSI", "MISO", "SCK", "SS")})
        self.assertEqual(self.i2c, {self.board["pins"]["SDA"], self.board["pins"]["SCL"]})

    def test_six_plain_signals_fill_every_plain_pin_before_touching_the_spi_bus(self):
        """
        Six, because the FireBeetle has exactly six pins that are neither scarce nor a bus —
        D3, A5, D10, D11, D12, D6 — and the bus pins MOSI/MISO/SCK are ADC2 pins exactly like
        D6. Without the penalty the six-way tie is broken by GPIO number, which spends MOSI (15)
        and MISO (16) before D6 (18): that is the whole defect, measured. My first version placed
        three LEDs, never reached the tie, and passed with the penalty at zero.
        """
        signals = [{"name": "S%d" % i, "needs": []} for i in range(6)]
        placed, _ = pin_assigner.assign(self.board, signals)
        landed = {a["gpio"] for a in placed}
        self.assertEqual(len(placed), 6)
        self.assertEqual(landed & self.spi, set(), "a plain signal took a bus pin: %s" % placed)
        self.assertEqual(landed & self.i2c, set())

    def test_a_plain_signal_takes_an_unlabelled_adc1_pin_before_the_i2c_pair(self):
        """
        On this board SDA and SCL are ADC1 pins (GPIO 1 and 2), equal in every ability to A0-A3
        and lower-numbered, so the tie-break alone would spend them first. Ten plain signals:
        nine fill every pin cheaper than an ADC1 pin (six plain, then the three SPI pins — a bus
        is cheaper than a scarce pin, by design), and the tenth must choose among the ADC1 pins.
        """
        ten = [{"name": "S%d" % i, "needs": []} for i in range(10)]
        placed, _ = pin_assigner.assign(self.board, ten)
        landed = {a["gpio"] for a in placed}
        self.assertEqual(len(placed), 10)
        self.assertTrue(landed & set(self.board["adc_gpio"]),
                        "ten signals never reached an ADC1 pin; the pin count this test assumes is wrong")
        self.assertEqual(landed & self.i2c, set(), "the I2C pair was spent: %s" % placed)

    def test_the_bus_penalty_is_a_tie_breaker_smaller_than_one_ability(self):
        # 0 < penalty < CAPABILITY_COST: it orders pins that waste the same abilities and can
        # never make a plain signal waste an ability to avoid a bus. 15 broke this — two plain
        # signals sent onto ADC1 — and the ordering test below caught it; this pins the reason.
        for bus in ("spi", "i2c"):
            self.assertGreater(pin_assigner.ROLE_PENALTY[bus], 0, bus)
            self.assertLess(pin_assigner.ROLE_PENALTY[bus], pin_assigner.CAPABILITY_COST, bus)

    def test_a_bus_signal_still_lands_on_its_own_pin(self):
        # The penalty must not push a real SPI signal off the pin it exists for.
        placed, _ = pin_assigner.assign(self.board, [{"name": "SCK", "bus": "spi", "needs": []}])
        self.assertEqual(placed[0]["pin"], "SCK")

    def test_a_bus_pin_is_still_available_when_nothing_else_is(self):
        # Worse, not forbidden. A design with no SPI and many signals may use the bus; refusing
        # would fail boards that are perfectly buildable. Twenty signals: more than the pins
        # that are NOT a bus, so the bus must be drawn on, and fewer than the board has, so the
        # request is satisfiable. (My first version asked for 24 of a 23-pin board and blamed
        # the penalty for the refusal.)
        many = [{"name": "S%d" % i, "needs": []} for i in range(20)]
        placed, _ = pin_assigner.assign(self.board, many)
        self.assertEqual(len(placed), 20)
        self.assertTrue({a["gpio"] for a in placed} & (self.spi | self.i2c),
                        "twenty plain signals were placed without touching a bus pin, which "
                        "means there are more non-bus pins than this test assumes")

    def test_for_a_plain_signal_a_bus_pin_costs_more_than_a_plain_pin_and_less_than_a_scarce_one(self):
        """
        The ordering, through `_cost` on real pins — not the penalty number, which is an
        implementation detail that the cost constant could move under.

        plain pin < bus pin < ADC1 pin. My first penalty was 15, which put the bus ABOVE the ADC1
        pins and sent three LEDs onto the board's scarcest inputs; a test pinning the number
        against other roles passed throughout. This one would not have.
        """
        pins = pin_assigner.candidates(self.board)
        plain, bus, scarce = pins["D3"], pins["SCK"], pins["A1"]
        def cost(pin):
            return pin_assigner._cost(pin, frozenset())

        self.assertLess(cost(plain), cost(bus))
        self.assertLess(cost(bus), cost(scarce))

    def test_the_bin_still_spends_no_adc1_pin_on_a_plain_signal(self):
        """
        The regression the wrong penalty caused, stated beside the ordering that prevents it:
        the bin's LEDs and buttons must not be pushed onto ADC1 by the bus being expensive.

        A plain signal has no `bus` and no `needs`. SDA and SCL are excluded on purpose: on this
        board the I2C pins ARE GPIO 1 and 2, which are ADC1 — a bus signal goes where its bus is,
        and the first version of this test counted them and failed for the right placement.
        """
        signals = part_facts.signals_for(["l9110s-module", "vl6180x-breakout"]) + [
            {"name": "LED_%d" % i, "needs": []} for i in range(3)]
        placed, _ = pin_assigner.assign(self.board, signals)
        adc1 = set(self.board["adc_gpio"])
        plain = {s["name"] for s in signals if not s.get("bus") and not s.get("needs")}
        self.assertEqual({"MOTOR_IA", "MOTOR_IB", "LED_0", "LED_1", "LED_2"}, plain)
        on_adc1 = [a["signal"] for a in placed if a["gpio"] in adc1 and a["signal"] in plain]
        self.assertEqual(on_adc1, [], "plain signals landed on ADC1 pins: %s" % on_adc1)


class WhichPadIsPinOneTest(unittest.TestCase):
    """
    The generator numbered pads from the order the pins happened to appear in the file, which is
    not a fact about any module. `pin_order` is that fact; these are the ways it can be wrong and
    still look fine.
    """

    def _problems(self, **overrides):
        definition = part(**overrides)
        return part_records.validate(definition, written(definition))

    def test_a_pad_naming_something_the_part_never_mentions_is_caught(self):
        # It would silently wire nothing — the worst shape of wrong, because the file looks
        # complete and the board builds.
        problems = self._problems(pin_order=["P", "TYPO"])
        self.assertTrue(any("never mentions" in p for p in problems), problems)

    def test_a_pin_with_no_pad_is_caught(self):
        problems = self._problems(pin_order=[None, None])
        self.assertTrue(any("does not say where" in p for p in problems), problems)

    def test_a_signal_on_two_pads_is_caught(self):
        # Two pads carrying one signal is two pads shorted together.
        problems = self._problems(pin_order=["P", "P"])
        self.assertTrue(any("more than one pad" in p for p in problems), problems)

    def test_a_supply_on_two_pads_is_allowed(self):
        """
        Real modules bring VCC and GND out on both rows so either side can be fed — the DFR0954
        I2S amplifier does exactly that with all twelve of its pads. Refusing it would have made
        the contract reject a part the library needs to describe.
        """
        self.assertEqual(self._problems(
            pin_order=["VCC", "P", "GND", "VCC", "GND"],
            power=[{"pin": "VCC", "rail": "logic", "direction": "in"},
                   {"pin": "GND", "rail": "ground", "direction": "in"}]), [])

    def test_an_unwired_pad_is_allowed_to_be_empty(self):
        # A module with ten pads of which you use five is the normal case; the gaps must stay
        # gaps, or everything after one shifts by a pad.
        self.assertEqual(self._problems(pin_order=[None, "P", None]), [])

    def test_a_part_that_records_no_pinout_at_all_still_validates(self):
        # Absent is honest — four different VL6180X breakouts exist with different pinouts. The
        # generator refuses such a part; the contract does not force a guess into the file.
        self.assertEqual(self._problems(), [])


class AProjectCanExtendTheLibraryTest(unittest.TestCase):
    """
    Every function here took `project`, the docstring promised "a project's own wins", and
    `main()` never passed one. So the override was unreachable from every entry point and the
    library was closed at whatever ships with the plugin — a stranger's first part could not be
    added, which makes the library a private data file with a read-only API.
    """

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        (self.project / "parts").mkdir()
        self.own = part("ssd1306-oled", name="SSD1306 OLED", kind="display")
        (self.project / "parts" / "ssd1306-oled.json").write_text(json.dumps(self.own))

    def test_a_projects_own_part_is_listed(self):
        self.assertIn("ssd1306-oled", record_kind.available(self.project))
        self.assertNotIn("ssd1306-oled", record_kind.available())

    def test_a_projects_own_part_can_be_loaded_and_asked_for_signals(self):
        self.assertEqual(part_records.load("ssd1306-oled", self.project)["name"], "SSD1306 OLED")
        self.assertTrue(part_facts.signals_for(["ssd1306-oled"], self.project))

    def test_a_project_definition_beats_the_shipped_one_of_the_same_name(self):
        # The reason the override exists: what you verified yourself must not be replaced by a
        # plugin update.
        shadowed = part("l9110s-module", name="My own measured L9110S")
        (self.project / "parts" / "l9110s-module.json").write_text(json.dumps(shadowed))
        self.assertEqual(part_records.load("l9110s-module", self.project)["name"],
                         "My own measured L9110S")

    def test_the_cli_reaches_it(self):
        # The defect was exactly here: the library functions worked and no flag could get to them.
        self.assertEqual(parts.main(["--show", "ssd1306-oled", "--project", str(self.project)]),
                         parts.EXIT_OK)

    def test_the_cli_without_a_project_still_cannot_see_it(self):
        self.assertEqual(parts.main(["--show", "ssd1306-oled"]), parts.EXIT_INVALID)


class TheFootprintAndThePinoutDescribeOnePartTest(unittest.TestCase):
    """
    Two fields, one physical object, and nothing compared them.

    `vl6180x-breakout` shipped saying `pinrow5` while its `pin_order` named seven pads — five of
    the seven carry a signal and two are unwired, so somebody counted the pins instead of the
    pads. The file's own prose note said seven all along, which is the recurring shape here: the
    truth written for a human, the contradiction written for the program.

    What it cost: the generator labelled a pad that did not exist, that port was given no
    position, and tscircuit's autorouter died reading its `x`. That failure is silent — the board
    comes back with zero traces rather than an error naming the part.
    """

    def _problems(self, **overrides):
        definition = part(**overrides)
        return part_records.validate(definition, written(definition))

    def test_a_footprint_with_fewer_pads_than_the_pinout_is_caught(self):
        problems = self._problems(footprint="pinrow5", pin_order=[None, "P", None, None, None,
                                                                 None, None])
        self.assertTrue(any("7" in p and "5" in p for p in problems), problems)

    def test_a_footprint_with_more_pads_than_the_pinout_is_caught(self):
        # The other direction is just as wrong and reads as "finished" just as easily.
        problems = self._problems(footprint="pinrow8", pin_order=["P", None])
        self.assertTrue(any("8" in p for p in problems), problems)

    def test_they_agree_and_nothing_is_reported(self):
        self.assertEqual(self._problems(footprint="pinrow2", pin_order=["P", None]), [])

    def test_a_footprint_whose_pad_count_cannot_be_read_asserts_nothing(self):
        # Most footprints do not encode a count. Guessing one would report every honest part
        # file as a disagreement, and a checker that cries wolf gets switched off.
        self.assertEqual(self._problems(footprint="jlcpcb:C2040", pin_order=["P", None]), [])


class CountingPadsFromAFootprintNameTest(unittest.TestCase):
    def test_a_pin_row_says_how_many(self):
        self.assertEqual(part_rules.footprint_pad_count("pinrow7"), 7)

    def test_a_module_header_says_how_many(self):
        self.assertEqual(part_rules.footprint_pad_count("headermodule6"), 6)

    def test_a_package_named_after_its_body_is_not_a_pad_count(self):
        # The trap that makes this a whitelist. `sot23` is three pads, `0603` is a size in
        # hundredths of an inch, `sod123` is neither — and the obvious implementation, "take the
        # first integer", reads them as 23, 603 and 123.
        for footprint in ("sot23", "0603", "0805", "sod123", "sot23_3"):
            with self.subTest(footprint=footprint):
                self.assertIsNone(part_rules.footprint_pad_count(footprint))

    def test_a_footprint_from_a_supplier_or_a_file_says_nothing(self):
        self.assertIsNone(part_rules.footprint_pad_count("jlcpcb:C12345"))
        self.assertIsNone(part_rules.footprint_pad_count(None))


class TheWalksBoardTest(unittest.TestCase):
    """P780, the T-Display walk's row 27: with a button and an LED, the LED took GPIO21 (I2C) while GPIO13, 25 and 32
    were free. That is the order the PO kept on 2026-11-13: IO21 wastes no wake or ADC ability, IO13, 25 and 32 waste
    more, and the bus penalty only breaks ties among equals."""

    def test_the_led_takes_the_i2c_pin_and_leaves_the_wake_and_adc_pins_free(self):
        board = json.loads((ROOT / "tests" / "data" / "boards" / "lilygo-t-display.json").read_text())
        placed, _ = pin_assigner.assign(board, [{"name": "BUTTON", "needs": []}, {"name": "STATUS_LED", "needs": []}])
        self.assertEqual({a["signal"]: a["pin"] for a in placed}, {"BUTTON": "IO17", "STATUS_LED": "IO21"})
        self.assertFalse({a["gpio"] for a in placed} & {13, 25, 32})


class TheShippedLibraryTest(unittest.TestCase):
    def test_every_part_shipped_satisfies_the_contract(self):
        for part_id in record_kind.available():
            with self.subTest(part=part_id):
                path = part_records.definition_path(part_id)
                problems = part_records.validate(json.loads(path.read_text()), path)
                self.assertEqual(problems, [], "%s: %s" % (part_id, problems))

    def test_every_shipped_part_does_something_for_the_board(self):
        """
        This asserted that every part produces SIGNALS, which was true only for as long as the
        library held nothing but modules with GPIO.

        A power inlet asks the host for no pin at all — that is the entire point of it, and it is
        the part that stops a generated board having a rail with one member. Requiring a signal
        would have made the contract reject the category the library most needed.

        The real rule underneath is that a part must do SOMETHING: ask for a pin, or carry a
        rail. One that does neither is inert, and would be emitted as a component nothing can
        ever connect to.
        """
        for part_id in record_kind.available():
            with self.subTest(part=part_id):
                definition = part_records.load(part_id)
                self.assertTrue(
                    part_facts.signals_for([part_id]) or definition.get("power"),
                    "%s asks the host for no pin and carries no rail, so placing it on a board "
                    "does nothing at all" % part_id)

    def test_the_speaker_terminal_owes_nothing_and_says_what_it_does(self):
        # C-3 (the council on PR #98): the record an amplifier's two outputs needed, so a sound need builds end to end
        record = part_records.load("speaker-terminal")
        self.assertEqual((record_kind.owes(record), record["footprint"], [s["pin"] for s in record["power"]],
                          part_records.function_of(record)),
                         ([], "jst_ph_2", ["SPK_P", "SPK_N"],
                          [{"does": "sound", "what": "speaker-terminal"}, {"does": "connect", "what": "speaker"}]))

    def test_the_rangefinder_s_outline_is_read_off_pololu_s_drawing(self):
        # C-6 (the council on PR #98): the only sensor spark ships owed body_mm, and --requirements refused it for that
        record = part_records.load("vl6180x-breakout")
        self.assertEqual(record_kind.owes(record), [])
        self.assertEqual((record["body_mm"]["width"], record["body_mm"]["height"], record["body_mm"]["verified"],
                          record["body_mm"]["cites"]["document"]), (12.7, 17.8, True, "pololu-2489-dimensions"))



class AMissingPinIsReportedOnceTest(unittest.TestCase):
    """
    `3b5f38f` moved the missing-pin rule to the contract and left the older use-site copy in
    the `power` walk, so one malformation produced two problems — the patch-not-audit pattern
    inside the commit that named it. Found by the sprint audit (A3), reproduced, copy removed.
    """

    def test_a_power_entry_without_a_pin_is_one_problem_not_two(self):
        path = ROOT / "parts" / "l9110s-module.json"
        record = json.loads(path.read_text())
        record["power"] = [{"rail": "v33", "direction": "in"}]
        problems = [p for p in part_records.validate(record, path) if "no pin" in p]
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("power[0]", problems[0])


class ABusIsCheckedWhereTheRecordIsWrittenTest(unittest.TestCase):
    """The contract refuses an unknown bus or a line the bus lacks, so the chain never has to."""

    def _problems(self, **need):
        path = ROOT / "parts" / "vl6180x-breakout.json"
        record = json.loads(path.read_text())
        record["needs"] = [dict(record["needs"][0], **need)]
        return [p for p in part_records.validate(record, path) if "bus" in p]

    def test_an_unknown_bus_is_refused_by_name(self):
        problems = self._problems(signal="X", bus="can")
        self.assertTrue(problems and "not a bus this knows" in problems[0], problems)

    def test_a_line_the_bus_does_not_have_is_refused_naming_the_lines(self):
        problems = self._problems(signal="XYZ", bus="spi")
        self.assertTrue(problems and "not one of its lines" in problems[0] and "SCK" in problems[0], problems)

    def test_a_bus_prefixed_signal_names_its_line(self):
        self.assertEqual(part_rules.bus_line_of("i2s", "I2S_BCLK"), "BCLK")
        self.assertEqual(part_rules.bus_line_of("spi", "CS"), "SS")
        self.assertIsNone(part_rules.bus_line_of("spi", "XYZ"))
        self.assertEqual(self._problems(signal="I2S_LRC", bus="i2s"), [])

    def test_every_shipped_record_is_still_within_the_vocabulary(self):
        for path in sorted((ROOT / "parts").glob("*.json")):
            record = json.loads(path.read_text())
            self.assertEqual([p for p in part_records.validate(record, path) if "bus" in p], [], path.name)


class AnI2cBusIsPulledUpBySomebodyTest(unittest.TestCase):
    """
    P55. I2C only ever pulls down, and the FireBeetle V1.2+ has no pull-ups of its own, so every
    record on the bus must say where its pull-ups come from: the module (a fact) or the host
    (`host_parts`). The fact sat in four catalog records that no test read, and flipping it, or
    setting a 1 MOhm pull-up, passed a green suite — while the RTC the PO owns said the same thing
    under a second name the catalog does not use.
    """

    I2C = [{"signal": "SDA", "pin": "SDA", "bus": "i2c"}, {"signal": "SCL", "pin": "SCL", "bus": "i2c"}]

    def _problems(self, facts=None, host_parts=None):
        definition = part(needs=self.I2C, facts=facts or {})
        if host_parts is not None:
            definition["host_parts"] = host_parts
        return [p for p in part_records.validate(definition, written(definition)) if "pull" in p]

    @staticmethod
    def fact(value):
        return {"value": value, "verified": True, "source": "test"}

    def test_a_module_that_carries_its_pull_ups_says_so_and_passes(self):
        self.assertEqual(self._problems({"module_has_i2c_pullups": self.fact(True)}), [])

    def test_a_host_that_adds_them_passes(self):
        pullups = [{"kind": "pullup", "pin": line, "ohms": 2200, "why": "the bus"} for line in ("SDA", "SCL")]
        self.assertEqual(self._problems(host_parts=pullups), [])

    def test_a_host_pull_up_on_one_line_does_not_cover_the_other(self):
        half = [{"kind": "pullup", "pin": "SDA", "ohms": 2200, "why": "the data line"}]
        self.assertEqual(len(self._problems(host_parts=half)), 1, "SCL still floats")

    def test_a_bus_nobody_pulls_up_is_refused(self):
        refused = self._problems({"module_has_i2c_pullups": self.fact(False)})
        self.assertEqual(len(refused), 1, refused)
        self.assertIn("module_has_i2c_pullups", refused[0])

    def test_silence_is_refused_too(self):
        self.assertEqual(len(self._problems()), 1, "saying nothing is how a bus floats")

    def test_a_module_pull_up_that_cannot_hold_a_bus_is_refused(self):
        refused = self._problems({"module_has_i2c_pullups": self.fact(True),
                                  "i2c_pullup_ohms": self.fact(1_000_000)})
        self.assertTrue(any("i2c_pullup_ohms" in p for p in refused), refused)

    def test_every_shipped_record_holds_the_contract(self):
        # The real files — not a temporary directory standing in for them. The catalog was walked
        # here too until P83 moved it into the person's store, where `--promote` demands the
        # contract of a record before anything builds with it.
        paths = sorted((ROOT / "parts").glob("*.json"))
        self.assertGreaterEqual(len(paths), 7)
        for path in paths:
            with self.subTest(record=path.name):
                self.assertEqual(part_records.validate(json.loads(path.read_text()), path), [])


class ResearchStartsFromWhatExistsTest(unittest.TestCase):
    """
    Backlog R11, pulled by the PO for the third cold test: research parts vendor by vendor and
    keep what was found. The deterministic half lives here — what exists, a skeleton to fill, the
    vendor order, and sources that must answer. The reading is the agent's.
    """

    def setUp(self):
        """A scratch store (P743): the library's parts and boards, a drawer entry that is the l9110s (8 owned, drives a load-switch)
        and a record-less entry. The PO's own store never enters a test."""
        self.home = Path(tempfile.mkdtemp())
        (self.home / "drawer").mkdir()
        self.entry("dfrobot-dfr0457", {"label": "Gravity: MOSFET Power Controller", "count": 8, "is": {"part": "l9110s-module"},
                                       "function": [{"does": "drive", "what": "load-switch"}]})
        self.entry("a-bag-of-reed-switches", {"label": "Reed switch, a bag", "count": "many", "function": [{"does": "sense", "what": "magnet"}]})
        patcher = in_store(self.home)
        patcher.start()
        self.addCleanup(patcher.stop)

    def entry(self, key, fields):
        (self.home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1}, **fields)))

    def test_need_matches_what_a_record_or_an_entry_does_and_puts_what_is_owned_first(self):
        rows, drafts, more = datasheets.need(["load", "switch"])
        self.assertEqual([(r["id"], r["is"], r["kind"], r["in"], r["owned"], r["score"], r["why"]) for r in rows][:1],
                         [("l9110s-module", "part", "motor-driver", "library", 8, 1.0, ["load: in functions", "switch: in functions"])])
        self.assertEqual((drafts, more), ([], 0))
        reed = [r for r in datasheets.need(["reed", "switch"])[0] if r["entry"]]
        self.assertEqual([(r["id"], r["entry"], r["is"], r["kind"], r["name"], r["in"], r["owned"]) for r in reed],
                         [(None, "a-bag-of-reed-switches", "entry", None, "Reed switch, a bag", "drawer", "many")])

    def test_need_finds_a_board_by_its_name(self):
        rows = datasheets.need(["ESP32-C6"])[0]
        self.assertEqual([(r["id"], r["is"], r["in"], r["owned"]) for r in rows if r["id"] == "xiao-esp32-c6"], [("xiao-esp32-c6", "board", "library", 0)])

    def test_need_matches_name_kind_and_alias_and_ranks_the_best_first(self):
        self.assertEqual(datasheets.need(["motor"])[0][0]["id"], "l9110s-module")
        self.assertIn("vl6180x-breakout", [p["id"] for p in datasheets.need(["rangefinder"])[0]])
        self.assertEqual(datasheets.need(["unobtainium"]), ([], [], 0))
        self.assertEqual(datasheets.need(["motor", "driver"])[0][0]["id"], "l9110s-module")
        self.assertIn("l9110s-module", [p["id"] for p in datasheets.need(["motor-driver"])[0]],
                      "the kind's words count for a search: the name says 'motor driver' without the hyphen")
        self.assertIn("l9110s-module", [p["id"] for p in datasheets.need(["hg7881"])[0]],
                      "an alias alone matches — HG7881 appears nowhere but also_known_as")

    def test_fits_past_the_first_eight_with_half_the_words_are_counted_not_shown(self):
        for n in range(10):
            self.entry("widget-%d" % n, {"label": "Widget %d" % n, "count": 1})
        rows, drafts, more = datasheets.need(["widget", "sprocket"])
        self.assertEqual((len(rows), more, rows[0]["score"]), (8, 2, 0.3))
        said, code = run_json(["--need", "widget", "sprocket"])
        self.assertEqual((code, said["data"]["more"], said["data"]["matcher"]), (0, 2, "word-overlap"))

    def test_need_takes_a_matcher_and_refuses_one_that_does_not_serve_it(self):
        said, code = run_json(["--need", "motor", "--matcher", "same-words"])
        self.assertEqual(code, 2)
        self.assertIn("name-contains, word-overlap", said["unchecked"][0]["sentence"])
        said, code = run_json(["--need", "motor", "--matcher", "name-contains"])
        self.assertEqual(([p["id"] for p in said["data"]["found"]], said["data"]["matcher"]), (["l9110s-module"], "name-contains"))

    def test_a_draft_still_being_filled_in_is_named_and_does_not_stop_the_search(self):
        # I3: `--need` died on a researcher's skeleton while five researchers were running.
        import tempfile
        root = Path(tempfile.mkdtemp())
        parts.main(["--skeleton", "dfr0457-mosfet-driver", "--kind", "mosfet-driver", "--project", str(root)])
        found, drafts, _ = datasheets.need(["mosfet"], root)
        self.assertEqual(found, [])
        self.assertEqual(drafts, ["dfr0457-mosfet-driver"])
        self.assertIn("l9110s-module", [p["id"] for p in datasheets.need(["motor"], root)[0]],
                      "the library is still searched past the draft")

    def test_no_match_names_the_research_command_and_the_vendor_order(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--need", "unobtainium"])
        self.assertIn("/spark:research", out.getvalue())
        self.assertIn("dfrobot, seeed", out.getvalue())

    def test_the_vendor_order_is_the_briefs_when_it_says_and_the_default_when_not(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        self.assertEqual(brief_choices.vendor_order(root), brief_choices.DEFAULT_VENDOR_ORDER)
        (root / ".spark").mkdir()
        (root / ".spark" / "project.json").write_text(json.dumps({"prefer": ["Seeed", "adafruit"]}))
        self.assertEqual(brief_choices.vendor_order(root), ("seeed", "adafruit"))
        (root / ".spark" / "project.json").write_text(json.dumps({"prefer": None}))
        self.assertEqual(brief_choices.vendor_order(root), brief_choices.DEFAULT_VENDOR_ORDER)

    def test_sellers_come_from_the_brief_or_are_none_named(self):
        # Local first is the person's rule, so it lives in their brief; the tool never picks a shop.
        import tempfile
        root = Path(tempfile.mkdtemp())
        self.assertEqual(brief_choices.sellers(root), ())
        (root / ".spark").mkdir()
        (root / ".spark" / "project.json").write_text(json.dumps({"sellers": ["LaskaKit", "gme"]}))
        self.assertEqual(brief_choices.sellers(root), ("laskakit", "gme"))

    def test_a_skeleton_whose_id_is_no_plain_key_is_refused_and_nothing_is_written(self):
        # P87's follow-through: every reader refuses a record named so, so nobody is handed a file they cannot use
        root = Path(tempfile.mkdtemp())
        for part_id in ("my_sensor", 'x"y', "X-LED"):
            for flags in ([], ["--dry-run"]):
                with self.subTest(id=part_id, flags=flags):
                    said, code = run_json(["--skeleton", part_id, "--kind", "sensor", "--project", str(root)] + flags)
                    self.assertEqual((said["status"], code), ("problems", 1))
                    self.assertEqual(said["problems"][0]["sentence"], "id is %r, but an id is a plain key — lower-case letters, "
                                     "digits and - (led-red-5mm): files are named by it, and the board names the part after it "
                                     "in code" % part_id)
        self.assertFalse((root / "parts").exists())

    def test_a_skeleton_has_every_field_and_no_guess_and_the_contract_refuses_it_until_filled(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        code = parts.main(["--skeleton", "sg90-servo", "--kind", "actuator", "--vendor", "dfrobot", "--sku", "SER0006",
                           "--project", str(root)])
        self.assertEqual(code, parts.EXIT_OK)
        written = json.loads((root / "parts" / "sg90-servo.json").read_text())
        self.assertEqual((written["id"], written["vendor"], written["sku"]), ("sg90-servo", "dfrobot", "SER0006"))
        self.assertIsNone(written["name"])
        self.assertIsNone(written["footprint"])
        self.assertFalse(written["body_mm"]["verified"])
        self.assertIn('A pin is a wiring name of letters, digits and _; what the silkscreen prints goes in printed ("pin": "VCC", '
                      '"printed": "+5V").', written["//"], "the way out of a refused +5V, where the author looks (P785)")
        self.assertNotIn("sourcing", written, "the rules keep no seller listing and no price (W21, P740)")
        problems = part_records.validate(written, root / "parts" / "sg90-servo.json")
        self.assertTrue(problems, "a skeleton full of nulls must not pass the contract")
        self.assertEqual(parts.main(["--skeleton", "sg90-servo", "--kind", "actuator", "--project", str(root)]),
                         parts.EXIT_INVALID, "an existing record is never overwritten")

    def test_a_skeleton_is_refused_when_a_layer_holds_the_id_and_names_that_record(self):
        # P740 (TL-13): the project layer wins over the shelf, the library and the catalog, so an empty skeleton
        # would hide a researched record. The refusal names the layer and, where --promote applies, is the step.
        import tempfile
        root, home = Path(tempfile.mkdtemp()).resolve(), Path(tempfile.mkdtemp())  # resolved: `main` resolves --project
        for place in ("shelf", "catalog"):
            (home / place).mkdir()
            (home / place / ("x-%s.json" % place)).write_text(json.dumps({"schema": 1, "id": "x-%s" % place, "kind": "sensor"}))
        (root / "parts").mkdir()
        (root / "parts" / "x-project.json").write_text(json.dumps({"schema": 1, "id": "x-project", "kind": "sensor"}))
        fixes = {"project": "fill it in, do not overwrite it",
                 "shelf": "`--promote <id> --project .` copies it into the project",
                 "catalog": "`--promote <id> --project .` copies the draft into the project",
                 "library": "spark ships it; name it in the requirements as it is"}
        with in_store(home):
            for layer, part_id in (("project", "x-project"), ("shelf", "x-shelf"), ("catalog", "x-catalog"),
                                   ("library", "led-red-5mm")):
                for flags in ([], ["--dry-run"]):
                    with self.subTest(layer=layer, flags=flags):
                        said, code = run_json(["--skeleton", part_id, "--kind", "sensor", "--project", str(root)] + flags)
                        self.assertEqual((said["status"], code), ("problems", parts.EXIT_INVALID))
                        problem = said["problems"][0]
                        self.assertTrue(problem["sentence"].startswith("%s already holds " % layer), problem["sentence"])
                        self.assertTrue(problem["sentence"].endswith("would %s it" % ("overwrite" if layer == "project" else "hide")))
                        self.assertIn(part_id + ".json", problem["sentence"])
                        self.assertEqual(problem["fix"], fixes[layer].replace("<id>", part_id))
                        if layer in ("project", "library"):
                            self.assertEqual(said["next"], [])
                        else:
                            self.assertEqual(said["next"][0]["argv"], ["--promote", part_id, "--project", str(root)])
                            self.assertEqual(said["next"][0]["env"], {"SPARK_HOME": str(home.resolve())})
        self.assertEqual([p.name for p in (root / "parts").iterdir()], ["x-project.json"], "a refused skeleton writes nothing")

    def test_sources_are_fetched_and_a_dead_one_is_named(self):
        record = {"sources": ["https://wiki.example/a", "not a url"],
                  "facts": {"x": {"value": 1, "verified": True, "source": "https://wiki.example/b"},
                            "y": {"value": 2, "verified": False, "source": "the datasheet, page 3"}}}
        self.assertEqual(datasheets.cited_urls(record), ["https://wiki.example/a", "https://wiki.example/b"])
        answers = datasheets.sources_resolve(record, fetch=lambda url: url.endswith("/a"))
        self.assertEqual(answers, [("https://wiki.example/a", True), ("https://wiki.example/b", False)])


class EachPartRefusalHasItsCodeTest(unittest.TestCase):
    """P717: each PartError names its sourcing code, so an agent decides on the code and never on the sentence."""

    def test_a_part_no_record_holds_and_a_record_that_breaks_the_contract(self):
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "broken-part.json").write_text(json.dumps({"schema": 1, "id": "broken-part"}))
        asked = {"definition_path": (lambda: part_records.definition_path("no-such-part", project), "no_such_part"),
                 "fetch_documents": (lambda: datasheets.fetch_documents("no-such-part", project), "no_such_part"),
                 "promote": (lambda: part_facts.promote("no-such-part", project), "no_such_part"),
                 "set_fields": (lambda: record_home.set_fields("no-such-part", project, {}, True, None),
                                "no_such_part"),
                 "load": (lambda: part_records.load("broken-part", project), "part_contract_broken"),
                 "load_payloads": (lambda: cli.load_payloads(SetDrawer(), {"items": str(project / "parts")}, io.StringIO()), "input_unreadable")}
        with in_store(home):
            for name, (refusing, code) in asked.items():
                with self.subTest(name=name):
                    with self.assertRaises(CodedMessageError) as refused:
                        refusing()
                    self.assertEqual(refused.exception.code, code, str(refused.exception))

    def test_validate_s_items_carry_the_contract_s_code(self):
        # P785 (P366 row 13): the item had `code: null`, so an agent could decide on the sentence alone
        project = Path(tempfile.mkdtemp()); (project / "parts").mkdir()
        (project / "parts" / "plus5v.json").write_text(json.dumps(part("plus5v", power=[{"pin": "+5V", "rail": "logic", "direction": "in"}])))
        said, code = run_json(["--validate", "--project", str(project)])
        self.assertEqual((code, said["status"], said["problems"][0]["code"], said["problems"][0]["fix"]), (1, "problems", "part_contract_broken", None))
        self.assertIn("power[0] pin '+5V' cannot be a selector", said["problems"][0]["sentence"])


class EverythingFoundIsKeptTest(unittest.TestCase):
    """The catalog: what research has read, chosen or not, with its datasheets kept beside it."""

    def _catalog_record(self, catalog, part_id, **extra):
        record = dict(schema=1, id=part_id, name="A candidate", kind="sensor", sources=[], facts={})
        record.update(extra)
        (catalog / (part_id + ".json")).write_text(json.dumps(record))
        return record

    def test_the_catalog_is_searched_like_the_library_and_a_broken_record_is_named(self):
        home = self._home(); catalog = home / "catalog"
        self._catalog_record(catalog, "sen0193-soil-moisture", name="Gravity capacitive soil moisture sensor")
        self._catalog_record(catalog, "dfr0831-buck-5v", name="Buck converter", kind="power")
        (catalog / "broken.json").write_text("{not json")
        (catalog / "nameless.json").write_text(json.dumps({"schema": 1, "id": "nameless", "kind": "sensor"}))
        with in_store(home):
            rows = datasheets.need(["Soil", "moisture"])[0]
            records, broken = datasheets.catalog_records()
        self.assertEqual([(p["id"], p["in"]) for p in rows if p["in"] == "catalog"], [("sen0193-soil-moisture", "catalog")])
        self.assertEqual((sorted(records), broken), (["dfr0831-buck-5v", "sen0193-soil-moisture"], ["broken.json", "nameless.json"]),
                         "a record that parses but does not say what it is, is broken too")

    @staticmethod
    def _home():
        """A scratch store for one test (P88): its catalog folder made, its sources folder not yet."""
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        return home

    def test_fetch_keeps_datasheets_and_images_in_the_store_under_their_checksum(self):
        """P62a: a published plugin cannot carry vendor files, so nothing lands beside the record."""
        import datetime
        import hashlib
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf?v=2", "https://v.example/page.html"],
                             facts={"w": {"value": 1, "verified": True, "source": "https://v.example/photo.jpg"}})
        fetched = []
        def fetch(url):
            fetched.append(url)
            return b"payload" if ".pdf" in url or url.endswith(".jpg") else None
        with in_store(home):
            kept = datasheets.fetch_documents("x-part", fetch=fetch)
        self.assertEqual(sorted(fetched), ["https://v.example/photo.jpg", "https://v.example/x.pdf?v=2"],
                         "only datasheets and images are fetched; a page is not")
        digest = hashlib.sha256(b"payload").hexdigest()
        self.assertEqual(kept["x"], {"url": "https://v.example/x.pdf?v=2", "sha256": digest, "file": "x.pdf",
                                     "retrieved": datetime.date.today().isoformat(), "title": None, "version": None})
        self.assertEqual(kept["photo"]["file"], "photo.jpg")
        self.assertEqual((store / digest / "x.pdf").read_bytes(), b"payload")
        self.assertFalse((catalog / "x-part").exists(), "nothing is kept beside the record any more")
        written = json.loads((catalog / "x-part.json").read_text())
        self.assertEqual((written["documents"], "attachments" in written), (kept, False))

    def test_a_document_already_kept_is_not_fetched_again(self):
        home = self._home(); catalog = home / "catalog"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf"])
        with in_store(home):
            datasheets.fetch_documents("x-part", fetch=lambda url: b"pdf")
            again = []
            datasheets.fetch_documents("x-part", fetch=lambda url: again.append(url))
        self.assertEqual(again, [])

    def test_a_catalog_draft_answers_sources_show_and_unverified_like_any_record(self):
        from unittest import mock
        home = self._home(); catalog = home / "catalog"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf"],
                             facts={"pitch_mm": {"value": 2.0, "verified": False, "why_it_matters": "the socket", "source": "the maker's page"}})
        answered = lambda record: [(url, True) for url in datasheets.cited_urls(record)]  # noqa: E731 — no network
        with in_store(home), mock.patch.object(datasheets, "sources_resolve", answered):
            self.assertEqual(part_records.any_record("x-part")["id"], "x-part")
            self.assertEqual([q["fact"] for q in part_facts.unverified(["x-part"])], ["pitch_mm"])
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = parts.main(["--sources", "x-part"])
        self.assertEqual((code, "ok" in out.getvalue()), (0, True), out.getvalue())

    def test_fetch_keeps_the_text_as_written_and_decodes_the_saved_name(self):
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/DFR%20(1).pdf"],
                             **{"//": "98 Kč — 帝江"})
        with in_store(home):
            kept = datasheets.fetch_documents("x-part", fetch=lambda url: b"pdf")
        (key, entry), = kept.items()
        self.assertEqual(entry["file"], "DFR (1).pdf")
        self.assertTrue((store / entry["sha256"] / "DFR (1).pdf").is_file())
        self.assertIn("98 Kč — 帝江", (catalog / "x-part.json").read_text(), "a rewrite must not turn text into escapes")

    def test_a_fetch_that_fails_halfway_leaves_the_record_whole(self):
        home = self._home(); catalog = home / "catalog"
        self._catalog_record(catalog, "x-part", sources=["https://v.example/x.pdf"])
        before = (catalog / "x-part.json").read_text()
        real_replace = Path.replace

        def the_disk_fills_at_the_record(part, target):
            # Only the record's own rename fails: the document is kept first (its rename runs for real), so the failure
            # cannot be the keep's — a patch on every rename would raise there and never reach the record at all.
            if Path(target).name == "x-part.json":
                raise OSError("the disk is full")
            return real_replace(part, target)

        with in_store(home), mock.patch.object(Path, "replace", autospec=True, side_effect=the_disk_fills_at_the_record):
            with self.assertRaises(OSError):
                datasheets.fetch_documents("x-part", fetch=lambda url: b"pdf")
        self.assertEqual((catalog / "x-part.json").read_text(), before)
        self.assertEqual([found.name for found in (home / "sources").rglob("*") if found.is_file()], ["x.pdf"])

    # --- all or nothing (§6.4): a name the store would refuse stops the whole fetch before it starts ---

    #: Documents whose names the store refuses, each cited second in a record that also cites a fine one: its URL, and the
    #: name it would be kept under as a refusal shows it. The first would leave the sources; the second holds a NUL byte; the
    #: third is 251 bytes, which no file can be named once `.part` is added (the shown name is cut at 40 characters).
    REFUSED = {"a path out of the sources": ("https://v.example/..%2fevil.pdf", "'../evil.pdf'"),
               "a NUL byte": ("https://v.example/a%00.pdf", r"'a\x00.pdf'"),
               "a name too long to keep": ("https://v.example/" + "a" * 247 + ".pdf", "'" + "a" * 40 + "…'")}

    def _a_record_citing_a_fine_source_and_then(self, second):
        home = self._home()
        self._catalog_record(home / "catalog", "x-part", sources=["https://v.example/ok.pdf", second])
        return home, (home / "catalog" / "x-part.json").read_text()

    def test_a_name_the_store_would_refuse_stops_the_whole_fetch_before_anything_is_downloaded_or_kept(self):
        for what, (cited, shown) in self.REFUSED.items():
            with self.subTest(what=what):
                home, before = self._a_record_citing_a_fine_source_and_then(cited)
                asked = []
                with in_store(home):
                    with self.assertRaises(store.StoreError) as refused:
                        datasheets.fetch_documents("x-part", fetch=lambda url: asked.append(url) or b"pdf")
                self.assertEqual(asked, [], "the first document, which is fine, is not downloaded either: all or nothing")
                self.assertIn(cited, str(refused.exception), "the refusal names the document")
                self.assertIn(shown, str(refused.exception), "and the name the store would not keep it under")
                self.assertEqual(refused.exception.code, "file_name_refused")
                self.assertFalse((home / "sources").exists(), "nothing was kept")
                self.assertEqual((home / "catalog" / "x-part.json").read_text(), before)

    def test_the_fetch_operation_and_its_dry_run_refuse_such_a_name_the_same_way(self):
        for what, (cited, shown) in self.REFUSED.items():
            home, before = self._a_record_citing_a_fine_source_and_then(cited)
            asked = []
            for argv in (["--fetch", "x-part"], ["--fetch", "x-part", "--dry-run"]):
                with self.subTest(what=what, argv=argv):
                    with in_store(home), mock.patch.object(store, "fetch", lambda url, method="GET": asked.append(url) or b"pdf"):
                        said, code = run_json(argv)  # an answer in the envelope, never a traceback
                    self.assertEqual((said["status"], code), ("could-not-run", 2))
                    self.assertIn(cited, said["unchecked"][0]["sentence"])
                    self.assertIn(shown, said["unchecked"][0]["sentence"])
            with self.subTest(what=what):
                self.assertEqual(asked, [], "the door was not asked once")
                self.assertFalse((home / "sources").exists(), "nothing was kept")
                self.assertEqual((home / "catalog" / "x-part.json").read_text(), before)

    def test_a_dry_run_of_a_fetch_says_what_it_would_fetch_and_reaches_nothing(self):
        home = self._home()
        self._catalog_record(home / "catalog", "x-part", sources=["https://v.example/ok.pdf", "https://v.example/page.html"])
        asked = []
        with in_store(home), mock.patch.object(store, "fetch", lambda url, method="GET": asked.append(url) or b"pdf"):
            said, code = run_json(["--fetch", "x-part", "--dry-run"])
        self.assertEqual((said["status"], code, said["data"]["would_fetch"]), ("ok", 0, ["https://v.example/ok.pdf"]))
        self.assertEqual(asked, [])
        self.assertFalse((home / "sources").exists())

    def test_two_sources_with_one_basename_are_both_kept(self):
        home = self._home(); catalog, store = home / "catalog", home / "sources"
        self._catalog_record(catalog, "x-part", sources=["https://a.example/DS3231.pdf", "https://b.example/DS3231.pdf"])
        with in_store(home):
            kept = datasheets.fetch_documents("x-part", fetch=lambda url: url.encode())
        self.assertEqual(sorted(entry["url"] for entry in kept.values()),
                         ["https://a.example/DS3231.pdf", "https://b.example/DS3231.pdf"])
        self.assertEqual(len({entry["sha256"] for entry in kept.values()}), 2, "two documents, two checksums")
        for entry in kept.values():
            self.assertEqual((store / entry["sha256"] / "DS3231.pdf").read_bytes(), entry["url"].encode())

    def test_promote_moves_a_record_with_its_documents_and_its_folder_and_never_overwrites(self):
        import tempfile
        home = self._home(); catalog = home / "catalog"; project, library = (Path(tempfile.mkdtemp()) for _ in range(2))
        (project / ".spark").mkdir()
        documents = {"x": {"url": "https://v.example/x.pdf", "sha256": "a" * 64, "file": "x.pdf",
                           "retrieved": "2026-10-02", "title": None, "version": None}}
        self._catalog_record(catalog, "x-part", documents=documents)
        (catalog / "x-part" / "chip").mkdir(parents=True)
        (catalog / "x-part" / "chip" / "x.chip.json").write_text("{}")
        with in_store(home):
            self.assertEqual(part_facts.promote("x-part", project), project / "parts" / "x-part.json")
            self.assertEqual(json.loads((project / "parts" / "x-part.json").read_text())["documents"], documents)
            self.assertTrue((project / "parts" / "x-part" / "chip" / "x.chip.json").is_file(), "a chip travels with it")
            with self.assertRaises(part_records.PartError) as refused:
                part_facts.promote("x-part", project, to=project / "parts")
            self.assertEqual(refused.exception.code, "promotion_would_overwrite")  # P717
            self.assertEqual(part_facts.promote("x-part", project, to=library), library / "x-part.json")
            self.assertTrue((library / "x-part" / "chip" / "x.chip.json").is_file())

    def test_a_newline_in_the_target_gives_one_line_in_a_promotion_that_never_overwrites(self):
        home = self._home(); catalog = home / "catalog"; project = Path(tempfile.mkdtemp()) / NASTY
        (project / ".spark").mkdir(parents=True)
        self._catalog_record(catalog, "x-part")
        (project / "parts").mkdir()
        (project / "parts" / "x-part.json").write_text("{}")
        with in_store(home):
            with self.assertRaises(part_records.PartError) as caught:
                part_facts.promote("x-part", project, to=project / "parts")
        assert_flat(self, caught.exception, project / "parts" / "x-part.json")

    def test_a_newline_in_the_name_of_a_document_gives_one_line_in_a_fetch_that_the_store_would_refuse(self):
        url = "https://x.example/a%0AGRANTED:%20board%20ok.pdf"
        with self.assertRaises(store.StoreError) as caught:
            datasheets.fetch_plan({"sources": [url]})
        assert_flat(self, caught.exception, url)
        self.assertEqual(caught.exception.code, "file_name_refused")

    def test_cited_urls_reads_a_dict_of_sources_and_a_url_inside_prose(self):
        # Both P62 lenses: four library records keep `sources` as a dict, and `--sources` saw none.
        record = {"sources": {"pins": "the vendor header, https://a.example/pins.h, read 09-24",
                              "wiki": "https://b.example/wiki"},
                  "facts": {"w": {"source": "Table 3 of https://c.example/ds.pdf (rev 7)"},
                            "v": {"source": "the drawing (see https://d.example/dim.pdf)."},
                            "u": {"source": "https://e.example/DFR%20(1).pdf"}}}
        self.assertEqual(sorted(datasheets.cited_urls(record)),
                         ["https://a.example/pins.h", "https://b.example/wiki", "https://c.example/ds.pdf",
                          "https://d.example/dim.pdf", "https://e.example/DFR%20(1).pdf"],
                         "a parenthesis the URL opened is its own; one it never opened is the prose's")

    def test_a_record_still_carrying_attachments_is_refused(self):
        definition = part(attachments={"https://v.example/x.pdf": "thing/x.pdf"})
        self.assertTrue(any("attachments" in p for p in part_records.validate(definition, written(definition))))

    # --- P62b: a source is found before it is fetched again ---

    def test_keep_puts_a_local_file_in_the_store_and_says_what_to_record(self):
        import datetime
        import hashlib
        import tempfile
        home = self._home(); store = home / "sources"
        local = Path(tempfile.mkdtemp()) / "ds_v1.1.pdf"
        local.write_bytes(b"the v1.1 pdf")
        with in_store(home):
            entry = datasheets.keep_local(local, url="https://v.example/ds.pdf")
        digest = hashlib.sha256(b"the v1.1 pdf").hexdigest()
        self.assertEqual(entry, {"url": "https://v.example/ds.pdf", "sha256": digest, "file": "ds_v1.1.pdf",
                                 "retrieved": datetime.date.today().isoformat(), "title": None, "version": None})
        self.assertEqual((store / digest / "ds_v1.1.pdf").read_bytes(), b"the v1.1 pdf")

    def test_a_dry_run_of_keep_refuses_the_name_the_real_run_refuses_and_keeps_nothing(self):
        home = self._home()
        for what, name in (("a line break in the name", "a\nb.pdf"), ("a name too long to keep", "a" * 247 + ".pdf")):
            local = Path(tempfile.mkdtemp()) / name
            local.write_bytes(b"%PDF drawing")
            for flags in (["--dry-run"], []):
                with self.subTest(what=what, flags=flags):
                    with in_store(home):
                        said, code = run_json(["--keep", str(local)] + flags)
                    self.assertEqual((said["status"], code, said["unchecked"][0]["code"]), ("could-not-run", 2, "file_name_refused"))  # P726 PR 2: the store's own code
        self.assertFalse((home / "sources").exists(), "nothing was kept")

    def test_a_dry_run_of_keep_says_what_the_real_run_would_record_and_keeps_nothing(self):
        home = self._home()
        local = Path(tempfile.mkdtemp()) / "ds.pdf"
        local.write_bytes(b"%PDF drawing")
        with in_store(home):
            said, code = run_json(["--keep", str(local), "--dry-run"])
        self.assertEqual((said["status"], code, said["data"]["written"]), ("ok", 0, False))
        self.assertEqual(said["data"]["document"]["sha256"], "8158f0d8a471f168c2daf1361a3919c034b7e43a62f5f2ac08c048ee9e58168e")
        self.assertFalse((home / "sources").exists(), "nothing was kept")

    def test_a_document_with_no_url_is_allowed_a_photo_of_your_own_module_has_none(self):
        definition = part(documents={"photo": {"url": None, "sha256": "a" * 64, "file": "top.jpg",
                                               "retrieved": "2026-10-03", "title": None, "version": None}})
        self.assertEqual([p for p in part_records.validate(definition, written(definition)) if "documents" in p], [])

    def test_a_document_not_kept_needs_a_url_and_no_sha256_and_nothing_cites_it(self):
        # P737 step 5: a file the wiki lists that the store cannot keep (a zip) is in `documents` as a pointer with `kept: false`
        definition = part(documents={"cad": {"url": "https://v.example/cad.zip", "kept": False, "title": "CAD"}})
        self.assertEqual([p for p in part_records.validate(definition, written(definition)) if "documents" in p or "cad" in p], [])
        for odd in ({"kept": False, "title": "CAD"}, {"url": "", "kept": False}, {"url": "https://v.example/cad.zip", "kept": False, "sha256": "a" * 64}):
            with self.subTest(odd=odd):
                problems = part_records.validate(part(documents={"cad": odd}), written(definition))
                self.assertEqual(len([p for p in problems if p.startswith("documents.cad")]), 1, problems)
        cited = dict(definition, facts={"rating_a": {"value": 2, "verified": True, "source": "the CAD", "cites": {"document": "cad", "at": "page 1"}}})
        self.assertEqual([p for p in part_records.validate(cited, written(definition)) if "cad" in p],
                         ["facts.rating_a cites 'cad', which is not kept, so nobody can read it there"])

    def _kept_world(self, stored=True, cites=None):
        """A catalog record and a project board that both point at one datasheet, the board citing a page; `cites` goes on
        the catalog record's one fact as written."""
        import tempfile
        home = self._home(); catalog, project, store = home / "catalog", Path(tempfile.mkdtemp()), home / "sources"
        (project / ".spark").mkdir()
        digest = "b" * 64
        document = {"url": "https://v.example/wroom.pdf", "sha256": digest, "file": "wroom_v1.1.pdf",
                    "retrieved": "2026-09-24", "title": "ESP32-S3-WROOM-1 Datasheet", "version": "v1.1"}
        self._catalog_record(catalog, "x-rtc", documents={"wroom": document, "cad": {"url": "https://v.example/rtc_cad.zip", "kept": False, "title": "CAD files"}},
                             facts={"idle_ua": dict({"value": 8, "verified": True, "source": "https://v.example/wroom.pdf"},
                                                    **({"cites": cites} if cites else {}))})
        # A record with a document of its own and nothing resting on the WROOM: it must not be named.
        self._catalog_record(catalog, "x-jack", body_mm={"value": [9, 14], "verified": True, "source": "drawing"},
                             documents={"drawing": dict(document, url="https://v.example/jack.pdf",
                                                        sha256="c" * 64, file="jack.pdf", title="Jack")},
                             facts={"rating_a": {"value": 2, "verified": True, "source": "the drawing",
                                                 "cites": {"document": "drawing", "at": "page 2"}}})
        (project / "boards").mkdir()
        (project / "boards" / "x-board.json").write_text(json.dumps({
            "id": "x-board", "documents": {"wroom": document},
            "power": {"deep_sleep_ua": {"value": None, "verified": False, "source": "Table 12",
                                        "cites": {"document": "wroom", "at": "Table 12, page 15"}}}}))
        if stored:
            (store / digest).mkdir(parents=True)
            (store / digest / "wroom_v1.1.pdf").write_bytes(b"pdf")
        return home, project, store

    def _kept(self, words, stored=True, cites=None):
        from unittest import mock
        home, project, store = self._kept_world(stored, cites)
        def no_network(url):
            raise AssertionError("--kept must never reach the network, asked for %s" % url)
        from spark.records import board_records
        with in_store(home), \
                mock.patch.object(board_records, "LIBRARY", home / "no-library"), \
                mock.patch.object(datasheets, "_download", no_network), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--kept"] + words + ["--project", str(project)])
        return code, out.getvalue(), store

    def test_kept_finds_a_document_by_every_word_and_says_where_it_is(self):
        code, said, store = self._kept(["wroom", "v1.1"])
        self.assertEqual(code, 0, said)
        self.assertIn(str(store / ("b" * 64) / "wroom_v1.1.pdf"), said)
        self.assertIn("present", said)

    def test_kept_names_every_fact_that_rests_on_it_with_its_page_and_nothing_else(self):
        _, said, _ = self._kept(["wroom"])
        cited = sorted(set(line.strip() for line in said.splitlines() if "cited by" in line))
        self.assertEqual(cited, ["cited by x-board power.deep_sleep_ua — Table 12, page 15",
                                 "cited by x-rtc facts.idle_ua — cites its URL"])

    def test_kept_reads_a_cites_that_is_no_object_as_no_citation_and_the_fact_still_cites_its_url(self):
        # P785: `--kept` crashed with an AttributeError on `cites: "wroom"`; the record is read raw, so the guard is here too
        code, said, _ = self._kept(["wroom"], cites="wroom")
        self.assertEqual(code, 0, said)
        self.assertIn("cited by x-rtc facts.idle_ua — cites its URL", said)

    def test_kept_says_missing_when_the_store_does_not_hold_it(self):
        _, said, _ = self._kept(["wroom"], stored=False)
        self.assertIn("MISSING", said)

    def test_kept_says_not_kept_for_a_listed_file_the_store_cannot_keep(self):
        # P737 step 5: a zip the wiki lists is in `documents` with `kept: false` and no sha256, so there is no file to find
        code, said, _ = self._kept(["cad"])
        self.assertEqual(code, 0, said)
        self.assertIn("x-rtc cad: CAD files (version not read)", said)
        self.assertIn("    not kept (https://v.example/rtc_cad.zip)", said)
        self.assertNotIn("MISSING", said)

    def test_kept_finds_a_stored_file_no_record_here_cites(self):
        """P80: the L-7113ID kept by the quickstart was invisible to every other project, so the next
        one would have fetched it again."""
        home, project, store = self._kept_world()
        (store / ("d" * 64)).mkdir(parents=True)
        (store / ("d" * 64) / "L-7113ID(Ver.29A).pdf").write_bytes(b"pdf")
        with in_store(home), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--kept", "l-7113id"])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn(str(store / ("d" * 64) / "L-7113ID(Ver.29A).pdf"), out.getvalue())
        self.assertIn("no record here cites it", out.getvalue())

    def test_kept_needs_every_word(self):
        code, said, _ = self._kept(["wroom", "nothing-like-this"])
        self.assertNotIn("present", said)
        self.assertIn("nothing kept matches", said)
        self.assertEqual(code, 0, "finding nothing is an answer, said in words (§6.4.1: a gap is an answer)")

    # --- P784: --keep --part lists the kept file in its record, so --kept finds it by its URL and its record ---

    #: The URL the joystick's record cites, as the photo walk's ky023 did (P366's rows 8 and 9).
    MANUAL = "https://v.example/joystick/manual.pdf"

    def _keep_for_a_part(self, documents=None):
        """A scratch store (SPARK_HOME set for this test alone and put back after it) and a project whose ky023 record cites
        the joystick's manual by URL and lists `documents`; (home, project, the manual to keep)."""
        home, project = self._home(), Path(tempfile.mkdtemp())
        before = os.environ.get("SPARK_HOME")
        os.environ["SPARK_HOME"] = str(home)
        self.addCleanup(lambda: os.environ.pop("SPARK_HOME") if before is None else os.environ.__setitem__("SPARK_HOME", before))
        (project / ".spark").mkdir()
        (project / "parts").mkdir()
        (project / "parts" / "ky023.json").write_text(json.dumps(part("ky023", sources=[self.MANUAL], **({"documents": documents} if documents else {}))))
        local = Path(tempfile.mkdtemp()) / "manual.pdf"
        local.write_bytes(b"%PDF joystick")
        return home, project, local

    @staticmethod
    def _said(argv):
        """parts.py in text: (exit code, stdout, stderr)."""
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = parts.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_keep_for_a_part_lists_the_file_in_its_record_and_kept_finds_it_by_its_url_and_its_record(self):
        home, project, local = self._keep_for_a_part()
        said, code = run_json(["--keep", str(local), "--url", self.MANUAL, "--part", "ky023", "--project", str(project)])
        self.assertEqual((said["status"], code, said["data"]["record"], said["data"]["key"]), ("ok", 0, "ky023", "manual"))
        documents = json.loads((project / "parts" / "ky023.json").read_text())["documents"]
        self.assertEqual(documents, {"manual": said["data"]["document"]})
        self.assertEqual((documents["manual"]["url"], documents["manual"]["sha256"]), (self.MANUAL, hashlib.sha256(b"%PDF joystick").hexdigest()))
        code, out, _ = self._said(["--kept", "joystick", "--project", str(project)])  # row 8: found by its URL
        self.assertEqual(code, 0, out)
        self.assertIn("ky023 manual: manual.pdf", out)
        self.assertIn(str(home / "sources" / documents["manual"]["sha256"] / "manual.pdf") + "  present", out)
        _, out, _ = self._said(["--kept", "ky023", "--project", str(project)])  # row 9: its record cites it
        self.assertIn("ky023 manual: manual.pdf", out)
        self.assertNotIn("cites it", out)

    def test_keep_for_a_part_with_no_record_is_a_problem_on_its_id_and_keeps_nothing(self):
        home, project, local = self._keep_for_a_part()
        for part_id, code_word in (("nobody", "no_such_part"), ("dfr0534-module", None)):  # a part nobody has; spark's own library
            with self.subTest(part=part_id):
                said, code = run_json(["--keep", str(local), "--part", part_id, "--project", str(project)])
                self.assertEqual((said["status"], code, [(item["subject"], item.get("code")) for item in said["problems"]]),
                                 ("problems", 1, [(part_id, code_word)]))
        self.assertFalse((home / "sources").exists(), "nothing was kept")

    def test_keep_for_a_part_whose_documents_is_no_object_is_refused_and_keeps_nothing(self):
        home, project, local = self._keep_for_a_part(documents=["manual.pdf"])
        said, code = run_json(["--keep", str(local), "--part", "ky023", "--project", str(project)])
        self.assertEqual((said["status"], code, said["problems"][0]["subject"]), ("problems", 1, "ky023"))
        self.assertIn("documents is not an object", said["problems"][0]["sentence"])
        self.assertFalse((home / "sources").exists(), "nothing was kept")

    def test_the_same_bytes_kept_twice_for_a_part_are_listed_once_and_the_line_names_the_entry(self):
        _, project, local = self._keep_for_a_part()
        first, code = run_json(["--keep", str(local), "--url", self.MANUAL, "--part", "ky023", "--project", str(project)])
        self.assertEqual((code, first["data"]["key"], first["data"]["document"]["url"]), (0, "manual", self.MANUAL))
        again = local.with_name("joystick-manual.pdf")
        again.write_bytes(local.read_bytes())
        code, _, err = self._said(["--keep", str(again), "--part", "ky023", "--project", str(project)])
        self.assertEqual(code, 0, err)
        self.assertEqual(list(json.loads((project / "parts" / "ky023.json").read_text())["documents"]), ["manual"])
        self.assertIn("already listed in ky023 as manual (manual.pdf, from %s)" % self.MANUAL, err)

    def test_keep_for_a_part_replaces_the_not_kept_entry_of_its_url_under_its_key_and_title(self):
        # the PR refuter: research writes {url, kept: false, title} for a file the store could not fetch (research_source.py),
        # exactly the file a person then downloads and keeps; listed beside it, the URL would be there twice
        home, project, local = self._keep_for_a_part(documents={"joystick-manual": {"url": self.MANUAL, "kept": False, "title": "Joystick manual"}})
        code, out, err = self._said(["--keep", str(local), "--url", self.MANUAL, "--part", "ky023", "--project", str(project)])
        self.assertEqual(code, 0, err)
        entry = json.loads(out)
        record = json.loads((project / "parts" / "ky023.json").read_text())
        self.assertEqual(record["documents"], {"joystick-manual": dict(entry, title="Joystick manual")}, "the shape a fetched entry has")
        self.assertEqual([p for p in part_records.validate(record, project / "parts" / "ky023.json") if "documents" in p], [])
        self.assertIn("listed in ky023 as joystick-manual (it was not kept before)", err)
        _, found, _ = self._said(["--kept", "joystick", "--project", str(project)])
        self.assertIn(str(home / "sources" / entry["sha256"] / "manual.pdf") + "  present", found)

    def test_keep_for_a_part_with_no_record_names_project_only_when_none_was_given(self):
        # the PR review: inside a project folder without --project, the walk's row 9a again
        _, project, local = self._keep_for_a_part()
        for flags, hinted in (([], True), (["--project", str(project)], False)):
            with self.subTest(flags=flags):
                said, code = run_json(["--keep", str(local), "--part", "nobody"] + flags)
                self.assertEqual((code, said["problems"][0]["code"]), (1, "no_such_part"))
                self.assertEqual(said["problems"][0]["sentence"].endswith("(a project's records need --project)"), hinted, said)

    def test_keep_for_a_part_whose_record_is_not_json_is_a_problem_naming_the_record(self):
        home, project, local = self._keep_for_a_part()
        (project / "parts" / "ky023.json").write_text("{not json")
        said, code = run_json(["--keep", str(local), "--part", "ky023", "--project", str(project)])
        self.assertEqual((said["status"], code, said["problems"][0]["subject"], said["problems"][0]["code"]),
                         ("problems", 1, "ky023", "part_contract_broken"))
        self.assertIn(str(project / "parts" / "ky023.json"), said["problems"][0]["sentence"])
        self.assertFalse((home / "sources").exists(), "nothing was kept")

    def test_keep_for_a_part_keeps_the_documents_the_record_already_lists(self):
        held = {name: {"url": "https://v.example/%s.pdf" % name, "sha256": letter * 64, "file": name + ".pdf",
                       "retrieved": "2026-11-01", "title": None, "version": None} for name, letter in (("pinout", "a"), ("drawing", "c"))}
        _, project, local = self._keep_for_a_part(documents=held)
        said, code = run_json(["--keep", str(local), "--part", "ky023", "--project", str(project)])
        self.assertEqual(code, 0, said)
        self.assertEqual(json.loads((project / "parts" / "ky023.json").read_text())["documents"],
                         dict(held, manual=said["data"]["document"]))

    def test_a_dry_run_of_keep_for_a_part_says_the_key_and_changes_nothing(self):
        home, project, local = self._keep_for_a_part()
        before = (project / "parts" / "ky023.json").read_bytes()
        code, out, err = self._said(["--keep", str(local), "--part", "ky023", "--project", str(project), "--dry-run"])
        self.assertEqual(code, 0, err)
        self.assertIn('would list it in ky023 as manual: cite it as {"document": "manual", "at": "p<N>"}', err)
        self.assertEqual(json.loads(out)["file"], "manual.pdf", "the text stays the entry's JSON")
        self.assertEqual((project / "parts" / "ky023.json").read_bytes(), before)
        self.assertFalse((home / "sources").exists(), "nothing was kept")

    def test_keep_without_a_part_says_no_record_lists_it(self):
        _, _, local = self._keep_for_a_part()
        said, code = run_json(["--keep", str(local)])
        self.assertEqual((code, said["data"]["record"], said["data"]["key"]), (0, None, None))
        _, _, err = self._said(["--keep", str(local)])
        self.assertIn("kept, but listed in no record: add --part <id> --project . to list it", err)

    def test_kept_names_project_only_when_none_was_given(self):
        home, project, _ = self._keep_for_a_part()
        (home / "sources" / ("d" * 64)).mkdir(parents=True)
        (home / "sources" / ("d" * 64) / "joystick-pinout.pdf").write_bytes(b"pdf")
        for flags, hinted in (([], True), (["--project", str(project)], False)):
            with self.subTest(flags=flags):
                _, found, _ = self._said(["--kept", "pinout"] + flags)
                self.assertIn("joystick-pinout.pdf: kept; no record here cites it", found)
                self.assertEqual("(a project's records need --project)" in found, hinted, found)
                _, nothing, _ = self._said(["--kept", "nothing-like-this"] + flags)
                self.assertEqual(", or name the project with --project" in nothing, hinted, nothing)

    def test_a_fact_citing_a_document_the_record_does_not_hold_is_refused(self):
        definition = part(facts={"idle_ua": {"value": 8, "verified": True, "source": "the datasheet",
                                             "cites": {"document": "ds", "at": "page 3"}}})
        self.assertTrue(any("facts.idle_ua" in p and "'ds'" in p for p in part_records.validate(definition,
                                                                                                written(definition))))

    @staticmethod
    def _photo_with_location():
        """A minimal JPEG whose EXIF carries a GPS block: latitude N 50° 5' 12.34" — as a phone writes it."""
        import struct
        latitude = struct.pack("<6I", 50, 1, 5, 1, 1234, 100)
        tiff = (b"II*\x00" + struct.pack("<I", 8)
                + struct.pack("<H", 1) + struct.pack("<HHII", 0x8825, 4, 1, 26) + struct.pack("<I", 0)
                + struct.pack("<H", 2) + struct.pack("<HHI4s", 1, 2, 2, b"N\x00\x00\x00")
                + struct.pack("<HHII", 2, 5, 3, 56) + struct.pack("<I", 0) + latitude)
        exif = b"Exif\x00\x00" + tiff
        return b"\xff\xd8\xff\xe1" + struct.pack(">H", len(exif) + 2) + exif + b"\xff\xd9", latitude

    def _keep_photo(self, payload, name="module.jpg"):
        import tempfile
        home = self._home(); store, local = home / "sources", Path(tempfile.mkdtemp()) / name
        local.write_bytes(payload)
        with in_store(home), contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()) as err:
            parts.main(["--keep", str(local)])
        json.loads(out.getvalue())  # what is pasted into a record stays JSON
        kept = next(store.rglob(name)).read_bytes()
        return kept, err.getvalue()

    def test_a_kept_photo_does_not_say_where_it_was_taken(self):
        """P75: all five of irrigation's phone photos carried latitude, longitude and altitude."""
        import struct
        photo, latitude = self._photo_with_location()
        kept, said = self._keep_photo(photo)
        self.assertNotIn(latitude, kept, "the coordinates are still in the file")
        self.assertNotIn(b"N\x00\x00\x00", kept[kept.index(b"Exif"):], "the hemisphere is still in the file")
        gps_entries = struct.unpack_from("<H", kept, kept.index(b"II*\x00") + 26)[0]
        self.assertEqual(gps_entries, 0, "the GPS block still lists entries")
        self.assertEqual(len(kept), len(photo), "nothing else in the file may move")
        self.assertIn("location", said.lower())

    def test_the_photo_s_name_with_an_override_shows_as_a_question_mark_in_the_line_that_says_the_location_went(self):
        # P423: the name is the person's own; the store refuses it after the line was printed
        import tempfile
        photo, _ = self._photo_with_location()
        local = Path(tempfile.mkdtemp()) / "mod\u202eule.jpg"
        local.write_bytes(photo)
        with in_store(self._home()), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            parts.main(["--keep", str(local)])
        self.assertIn("  removed the location (EXIF GPS) from mod?ule.jpg before keeping it\n", err.getvalue())

    def test_a_store_that_cannot_be_written_refuses_the_photo_after_the_line_that_says_the_location_went(self):
        # P717 (the refuter): keep_local's OSError is answered by --keep itself, so its line is not lost
        import tempfile
        photo, _ = self._photo_with_location()
        local = Path(tempfile.mkdtemp()) / "module.jpg"
        local.write_bytes(photo)
        home = self._home()
        home.chmod(0o500)  # read-only: no sources folder can be made
        self.addCleanup(home.chmod, 0o700)
        err = io.StringIO()
        with in_store(home), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = parts.main(["--keep", str(local)])
        said = err.getvalue()
        self.assertEqual(code, 2, said)
        location_went = "  removed the location (EXIF GPS) from module.jpg before keeping it\n"
        self.assertTrue(said.startswith(location_went + "parts.py: --keep: "), said)

    def test_a_photo_with_no_location_and_any_other_file_are_kept_unchanged(self):
        photo, _ = self._photo_with_location()
        plain = photo.replace(b"\x25\x88", b"\x0f\x01", 1)  # the GPS pointer becomes the camera maker's tag
        for payload, name in ((plain, "plain.jpg"), (b"%PDF-1.4 whatever", "ds.pdf")):
            kept, said = self._keep_photo(payload, name)
            self.assertEqual(kept, payload, name)
            self.assertNotIn("location", said.lower(), name)

    def test_a_document_whose_checksum_is_not_one_is_refused(self):
        definition = part(documents={"x": {"url": "https://v.example/x.pdf", "sha256": "abc", "file": "x.pdf",
                                           "retrieved": "2026-10-02", "title": None, "version": None}})
        self.assertTrue(any("sha256" in p for p in part_records.validate(definition, written(definition))))


class WhatAPartsSimulationCannotShowTest(unittest.TestCase):
    """P778: `limits_of_part` says, in the record's own words, what a simulation cannot show of one part; the build, the
    pick and the look read the one function, so they say one thing."""

    def test_a_skipped_part_is_not_simulated_at_all_with_its_reason(self):
        self.assertEqual(part_records.limits_of_part({"simulation": {"skip": "a connector is wiring"}}, "Jack"),
                         [("Jack", "not simulated at all: a connector is wiring")])

    def test_a_stand_in_s_sentence_and_a_chip_s_note_are_the_limit(self):
        self.assertEqual(part_records.limits_of_part({"simulation": {"wokwi": {"part": "wokwi-led", "stand_in": "an LED"}}}, "Valve"),
                         [("Valve", "an LED")])
        self.assertEqual(part_records.limits_of_part({"simulation": {"wokwi": {"chip": "vl6180x", "note": "no optics"}}}, "Tof"),
                         [("Tof", "no optics")])

    def test_a_real_wokwi_part_and_a_record_with_no_simulation_table_say_nothing(self):
        self.assertEqual(part_records.limits_of_part({"simulation": {"wokwi": {"part": "wokwi-pushbutton", "pins": {}}}}, "Btn"), [])
        self.assertEqual(part_records.limits_of_part({"id": "x-part"}, "X"), [])
        self.assertEqual(part_records.limits_of_part({"simulation": "yes"}, "X"), [])
        self.assertEqual(part_records.limits_of_part({"simulation": {"wokwi": "led"}}, "X"), [])


class ASimulationIsDeclaredTest(unittest.TestCase):
    """P31: a record says how it is simulated, and the contract refuses a half-said one."""

    def _record(self, **extra):
        record = {"schema": 1, "id": "x-part", "name": "X", "kind": "sensor",
                  "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}],
                  "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}],
                  "unused_pins": [{"pin": "NC", "note": "no connection"}]}
        record.update(extra)
        return record

    def _problems(self, simulation, root=None):
        import tempfile
        root = root or Path(tempfile.mkdtemp())
        path = root / "x-part.json"
        return part_rules.simulation_problems(self._record(simulation=simulation), path), root

    def test_a_skip_needs_its_reason_and_nothing_else(self):
        self.assertEqual(self._problems({"skip": "wiring, not a part"})[0], [])
        self.assertTrue(self._problems({"skip": ""})[0])
        self.assertTrue(self._problems({"skip": "x", "wokwi": {}})[0])

    def test_a_stand_in_names_its_part_its_pins_and_what_differs(self):
        good = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None}, "stand_in": "an LED shows the level"}}
        self.assertEqual(self._problems(good)[0], [])
        no_note = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None}}}
        self.assertTrue(any("stand_in" in p for p in self._problems(no_note)[0]))
        both = {"wokwi": {"part": "wokwi-led", "chip": "x", "pins": {"OUT": "A", "GND": "C", "VCC": None}, "stand_in": "s"}}
        self.assertTrue(any("exactly one" in p for p in self._problems(both)[0]))

    def test_every_wired_pad_is_placed_and_no_unknown_pad_is_named(self):
        missing = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A"}, "stand_in": "s"}}
        said = " ".join(self._problems(missing)[0])
        self.assertIn("'GND'", said); self.assertIn("'VCC'", said)
        unknown = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None, "BOGUS": "B"}, "stand_in": "s"}}
        self.assertTrue(any("never mentions" in p for p in self._problems(unknown)[0]))
        unused_may_be_absent = {"wokwi": {"part": "wokwi-led", "pins": {"OUT": "A", "GND": "C", "VCC": None}, "stand_in": "s"}}
        self.assertEqual(self._problems(unused_may_be_absent)[0], [], "NC is unused and need not be placed")

    def test_a_control_id_is_what_a_scenario_can_name(self):
        # wokwi-cli's own check: /controls/0/id must match ^[a-zA-Z][a-zA-Z0-9]*$ — `flow_lpm` was refused.
        import tempfile
        root = Path(tempfile.mkdtemp())
        folder = root / "x-part" / "chip"; folder.mkdir(parents=True)
        (folder / "probe.chip.c").write_text("// c")
        (folder / "probe.chip.json").write_text(json.dumps({"pins": ["SIG", "GND", "VCC"], "controls": [{"id": "flow_lpm"}, {"id": "flowLpm"}]}))
        chip = {"wokwi": {"chip": "probe", "pins": {"OUT": "SIG", "GND": "GND", "VCC": "VCC"}}}
        problems = self._problems(chip, root)[0]
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("'flow_lpm'", problems[0])

    def test_a_chip_pin_map_names_only_pins_the_chip_has(self):
        # Audit D18: `AIA: "NOPE"` validated clean and was refused only by the converter.
        import tempfile
        root = Path(tempfile.mkdtemp())
        folder = root / "x-part" / "chip"; folder.mkdir(parents=True)
        (folder / "probe.chip.c").write_text("// c")
        (folder / "probe.chip.json").write_text(json.dumps({"pins": ["SIG", "GND", "VCC"]}))
        good = {"wokwi": {"chip": "probe", "pins": {"OUT": "SIG", "GND": "GND", "VCC": None}}}
        self.assertEqual(self._problems(good, root)[0], [])
        bad = {"wokwi": {"chip": "probe", "pins": {"OUT": "NOPE", "GND": "GND", "VCC": "VCC"}}}
        self.assertTrue(any("does not have" in p and "'NOPE'" in p for p in self._problems(bad, root)[0]))

    def test_a_chip_whose_name_is_no_name_is_refused_before_its_files_are_looked_for(self):
        # the re-check's probes: `../escape` named files outside the record's chip folder, which stage_chips then copied,
        # and `x"⏎[[chip]]` wrote a TOML table of its own into wokwi.toml
        for name in ("../escape", 'x"\n[[chip]]\nname = "evil', "flow meter"):
            with self.subTest(chip=name):
                chip = {"wokwi": {"chip": name, "pins": {"OUT": "SIG", "GND": "GND", "VCC": "VCC"}}}
                self.assertEqual(self._problems(chip)[0], [
                    "simulation.wokwi.chip is %r, but a chip's name is a name — letters, digits and _ (vl6180x, l9110s): its "
                    "files beside the record are named by it, and wokwi.toml is written with it" % name])

    def test_a_chip_must_exist_beside_the_record(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        chip = {"wokwi": {"chip": "probe", "pins": {"OUT": "SIG", "GND": "GND", "VCC": "VCC"}}}
        self.assertTrue(any("needs" in p and "probe.chip.c" in p for p in self._problems(chip, root)[0]))
        folder = root / "x-part" / "chip"; folder.mkdir(parents=True)
        (folder / "probe.chip.c").write_text("// c"); (folder / "probe.chip.json").write_text("{}")
        self.assertEqual(self._problems(chip, root)[0], [])

    def test_the_validator_refuses_a_record_whose_simulation_is_half_said(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        record = self._record(simulation={"skip": ""}, pin_order=["OUT", "VCC", "GND", "NC"], footprint="pinrow4",
                              body_mm={"width": 10, "height": 10, "verified": True, "source": "x"})
        self.assertTrue(any("simulation.skip" in p for p in part_records.validate(record, root / "x-part.json")),
                        "validate must carry the simulation problems, or --validate passes a record the converter cannot use")

    def test_every_shipped_record_says_how_it_is_simulated(self):
        for part_id in record_kind.available():
            record = part_records.load(part_id)
            self.assertIn("simulation", record, "%s: the converter has nothing to read" % part_id)


class WhatAPartDemandsOfItsHostTest(unittest.TestCase):
    """P6: `host_parts` is a component list the generator can act on, so it is checked like one."""

    def _problems(self, host_parts):
        part = {"schema": 1, "id": "x", "name": "X", "kind": "sensor",
                "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}],
                "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}]}
        part["host_parts"] = host_parts
        return part_rules.host_part_problems(part)

    def test_a_well_said_pulldown_passes_and_each_omission_is_named(self):
        self.assertEqual(self._problems([{"kind": "pulldown", "pin": "OUT", "ohms": 10000, "why": "floats at reset"}]), [])
        self.assertTrue(any("not one the generator can place" in p for p in self._problems([{"kind": "flyback", "pin": "OUT", "ohms": 1, "why": "w"}])))
        self.assertTrue(any("not a signal pad" in p for p in self._problems([{"kind": "pulldown", "pin": "VCC", "ohms": 10000, "why": "w"}])))
        self.assertTrue(any("positive ohms" in p for p in self._problems([{"kind": "pulldown", "pin": "OUT", "ohms": 0, "why": "w"}])))
        self.assertTrue(any("no why" in p for p in self._problems([{"kind": "pulldown", "pin": "OUT", "ohms": 10000}])))

    def test_internal_will_do_is_true_and_only_on_a_pull_up(self):
        # P204: the code reads it as truthy, so the string "false" would leave the resistor to the firmware.
        pullup = {"kind": "pullup", "pin": "OUT", "ohms": 10000, "why": "w"}
        self.assertEqual(self._problems([dict(pullup, internal_will_do=True)]), [])
        for wrong in (dict(pullup, internal_will_do="false"), dict(pullup, kind="pulldown", internal_will_do=True)):
            with self.subTest(wrong=wrong):
                self.assertTrue(any("internal_will_do" in p for p in self._problems([wrong])))

    def test_a_series_resistor_states_its_ohms_or_the_current_it_is_for(self):
        self.assertEqual(self._problems([{"kind": "series", "pin": "OUT", "ohms": 1000, "why": "limits the LED"}]), [])
        self.assertEqual(self._problems([{"kind": "series", "pin": "OUT", "for_current_ma": 5, "why": "an indicator"}]), [])
        said = " ".join(self._problems([{"kind": "series", "pin": "OUT", "why": "w"}]))
        self.assertIn("for_current_ma", said, "neither a value nor a current: nothing to place")

    def test_the_validator_carries_the_host_parts_problems(self):
        import tempfile
        record = {"schema": 1, "id": "x-part", "name": "X", "kind": "sensor",
                  "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}], "power": [{"pin": "GND", "rail": "ground", "direction": "in"}],
                  "pin_order": ["OUT", "GND"], "footprint": "pinrow2", "body_mm": {"width": 5, "height": 5, "verified": True, "source": "x"},
                  "host_parts": [{"kind": "pulldown", "pin": "GND", "ohms": 100, "why": "w"}]}
        self.assertTrue(any("not a signal pad" in p
                            for p in part_records.validate(record, Path(tempfile.mkdtemp()) / "x-part.json")))

    def test_a_divider_needs_both_values(self):
        said = " ".join(self._problems([{"kind": "divider", "pin": "OUT", "top_ohms": 10000, "why": "w"}]))
        self.assertIn("bottom_ohms", said)
        self.assertEqual(self._problems([{"kind": "divider", "pin": "OUT", "top_ohms": 10000, "bottom_ohms": 18000, "why": "w"}]), [])

class APinOrderSaysHowItWasReadTest(unittest.TestCase):
    """
    P81. Every fact must say where it came from, except the one where a mistake reverses a supply:
    `pin_order` carried its proof only in a prose note nothing checked — and the irrigation DS3231's
    note described the 4-pad edge while its typed order was the 6-pin header, SCL against 32K.
    """

    def record(self, **extra):
        definition = {"schema": 1, "id": "x-part", "name": "X", "kind": "sensor",
                      "needs": [{"signal": "OUT", "pin": "OUT", "needs": []}],
                      "power": [{"pin": "GND", "rail": "ground", "direction": "in"}],
                      "pin_order": ["OUT", "GND"], "footprint": "pinrow2",
                      "body_mm": {"width": 5, "height": 5, "verified": True, "source": "x"}}
        definition.update(extra)
        return definition

    def problems(self, definition):
        import tempfile
        return [p for p in part_records.validate(definition, Path(tempfile.mkdtemp()) / "x-part.json")
                if "pin_order" in p]

    def test_a_pin_order_without_proof_is_refused(self):
        self.assertTrue(any("pin_order_proof" in p for p in self.problems(self.record())))

    def test_a_proof_says_whether_it_was_verified_and_where_it_was_read(self):
        good = self.record(pin_order_proof={"verified": False, "source": "read off the module's silkscreen in a photo"})
        self.assertEqual(self.problems(good), [])
        self.assertTrue(self.problems(self.record(pin_order_proof={"verified": False, "source": ""})))
        self.assertTrue(self.problems(self.record(pin_order_proof={"verified": "yes", "source": "x"})))

    def test_an_unverified_pin_order_is_listed_with_the_unverified_facts(self):
        definition = self.record(pin_order_proof={"verified": False, "source": "read off a photo"})
        listed = [q for q in part_facts.open_questions_of(definition) if q["fact"] == "pin_order"]
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["source"], "read off a photo")

class FactSetWritesTheSheetKeysTest(unittest.TestCase):
    """P741 (#1017): `--fact-set` writes `legs` (leg by leg, each pin one of pin_order) and `host_requirements` (the list as a whole),
    the two keys the breadboard sheet reads as text, so no hand edit is needed for them."""

    LEGS = {"A": "the anode, the longer leg", "K": "the cathode, by the flat of the rim"}
    LINE = "A series resistor between the GPIO and the anode, always."

    def a_store(self, **extra):
        home = Path(tempfile.mkdtemp()); (home / "catalog").mkdir()
        record = part("x-led", pin_order=["A", "K"], footprint="led5mm", body_mm={"width": 5, "height": 5}, **extra)
        (home / "catalog" / "x-led.json").write_text(json.dumps(record))
        return home

    def write(self, home, values):
        given = home / "write.json"
        given.write_text(json.dumps(values))
        with in_store(home):
            said, code = run_json(["--fact-set", "x-led", str(given)])
        return said, code, json.loads((home / "catalog" / "x-led.json").read_text())

    def test_legs_are_written_and_a_second_write_merges_leg_by_leg(self):
        home = self.a_store()
        said, code, after = self.write(home, {"legs": self.LEGS})
        self.assertEqual((code, after["legs"], said["data"]["was"]["legs"]), (0, self.LEGS, {"A": None, "K": None}))
        said, code, after = self.write(home, {"legs": {"K": "the shorter leg"}})
        self.assertEqual((code, after["legs"], said["data"]["was"]["legs"]), (0, dict(self.LEGS, K="the shorter leg"), {"K": self.LEGS["K"]}))

    def test_host_requirements_are_written_as_a_whole_and_a_rerun_changes_nothing(self):
        home = self.a_store(host_requirements=["an old line"])
        said, code, after = self.write(home, {"host_requirements": [self.LINE]})
        self.assertEqual((code, after["host_requirements"], said["data"]["was"]["host_requirements"]), (0, [self.LINE], ["an old line"]))
        said, code, after = self.write(home, {"host_requirements": [self.LINE]})
        self.assertEqual((code, said["data"]["was"]["host_requirements"], after["host_requirements"]), (0, [self.LINE], [self.LINE]))

    def test_a_leg_for_a_pin_the_record_does_not_name_an_empty_leg_and_an_empty_line_are_refused(self):
        home = self.a_store()
        said, code, after = self.write(home, {"legs": {"B": "a third leg", "K": ""}, "host_requirements": [self.LINE, " "]})
        self.assertEqual((code, "legs" in after, "host_requirements" in after), (1, False, False))
        self.assertEqual([p["sentence"] for p in said["problems"]],
                         ["legs is {pin of pin_order (A, K): words that tell the leg apart}; B is not",
                          "legs is {pin of pin_order (A, K): words that tell the leg apart}; K is not",
                          "host_requirements is a list of lines that are not empty; item 1 is not"])

    def test_an_empty_legs_a_string_for_the_lines_and_a_control_character_in_a_leg_key_are_refused(self):
        home = self.a_store()
        said, code, after = self.write(home, {"legs": {}})
        self.assertEqual((code, said["problems"][0]["sentence"]), (1, "legs is absent — a write fills a fact, it never empties one"))
        said, code, after = self.write(home, {"host_requirements": "one line"})
        self.assertEqual((code, said["problems"][0]["sentence"]), (1, "host_requirements is a list of lines that are not empty; item the value is not"))
        said, code, after = self.write(home, {"legs": {"A\x07": "a leg"}})
        self.assertEqual((code, len(said["problems"]), "legs" in after), (1, 2, False))

    def test_show_reads_a_written_leg_back(self):
        home = self.a_store()
        self.write(home, {"legs": self.LEGS})
        with in_store(home):
            printed, code = run_text(["--show", "x-led"])
        self.assertEqual((code, [line for line in printed.splitlines() if line.startswith("  leg ")]), (0, ["  leg A: the anode, the longer leg", "  leg K: the cathode, by the flat of the rim"]))

    def test_a_text_in_a_leg_or_a_line_is_cleaned_and_cut_at_the_provenance_cap(self):
        home = self.a_store()
        said, code, after = self.write(home, {"legs": {"A": "the\x1banode"}, "host_requirements": ["x" * 1200]})
        self.assertEqual((code, after["legs"]["A"], len(after["host_requirements"][0])), (0, "the anode", 1000))


class AModulesPhysicalSaysHowItWasReadTest(unittest.TestCase):
    """
    P737 step 3. `physical` holds what `body_mm` does not (the thickness, the holes, the header) as bare values under the
    board record's key names, and one `physical_proof` beside it says where they were read. A key the vendor did not
    publish is left out and named in the proof's `not_published`, never null and never an empty list.
    """

    PHYSICAL = {"thickness_mm": 1.6,
                "mounting_holes": [{"x_mm": 2.0, "y_mm": 2.0, "drill_mm": 2.2}, {"x_mm": 14.0, "y_mm": 2.0, "drill_mm": 2.2}],
                "header": {"pitch_mm": 2.54, "row_spacing_mm": 7.62, "pins": [4, 4], "rows": 2, "first_pad_from_edge_mm": 1.27}}
    PROOF = {"verified": True, "source": "the vendor's dimension drawing",
             "cites": {"document": "sen0526-dimensions", "at": "page 1"}, "not_published": []}

    DOCUMENTS = {"sen0526-dimensions": {"url": "https://example.test/sen0526.pdf", "file": "sen0526.pdf", "sha256": "a" * 64}}

    def record(self, **extra):
        definition = part("x-mic", physical=dict(self.PHYSICAL), physical_proof=dict(self.PROOF), documents=self.DOCUMENTS)
        definition.update(extra)
        return definition

    def problems(self, **extra):
        return [p for p in part_records.validate(self.record(**extra), written(self.record(**extra))) if "physical" in p]

    def test_a_block_with_its_proof_passes_and_a_record_with_neither_is_not_asked(self):
        self.assertEqual(self.problems(), [])
        self.assertEqual(self.problems(physical=None, physical_proof=None), [])

    def test_a_block_without_its_proof_is_refused_with_why_it_matters(self):
        said = self.problems(physical_proof=None)
        self.assertEqual(len(said), 1)
        self.assertIn("physical states no physical_proof", said[0])
        self.assertIn("pins miss the breadboard", said[0])

    def test_a_block_that_is_no_object_or_is_empty_is_one_problem(self):
        self.assertEqual(self.problems(physical=[1.6]), ["physical is [1.6], but it is an object of thickness_mm, mounting_holes, header"])
        self.assertEqual(self.problems(physical={}), ["physical is empty; leave the block out, and name what was not "
                                                       "published in physical_proof.not_published"])

    def test_a_null_or_an_empty_key_is_refused_and_sent_to_not_published(self):
        for value in (None, []):
            with self.subTest(value=value):
                said = self.problems(physical=dict(self.PHYSICAL, mounting_holes=value))
                self.assertEqual(said, ["physical.mounting_holes is %r; leave the key out and name it in "
                                        "physical_proof.not_published" % (value,)])

    def test_every_size_is_a_finite_number_above_zero(self):
        for bad in (0, -1.6, float("nan"), float("inf"), "1.6", True):
            with self.subTest(bad=bad):
                self.assertEqual(self.problems(physical=dict(self.PHYSICAL, thickness_mm=bad)),
                                 ["physical.thickness_mm is %r, but it is a number above 0" % (bad,)])
        header = dict(self.PHYSICAL["header"], pitch_mm=0)
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header=header)),
                         ["physical.header.pitch_mm is 0, but it is a number above 0"])

    def test_each_hole_has_its_two_coordinates_and_its_drill(self):
        holes = [{"x_mm": 2.0, "y_mm": 2.0, "drill_mm": 2.2}, {"x_mm": 14.0, "y_mm": 2.0}, 7]
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, mounting_holes=holes)),
                         ["physical.mounting_holes[1] has no drill_mm above 0"] +
                         ["physical.mounting_holes[2] has no %s above 0" % key for key in ("x_mm", "y_mm", "drill_mm")])
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, mounting_holes={"count": 4})),
                         ["physical.mounting_holes is {'count': 4}, but it is a list of {x_mm, y_mm, drill_mm}"])

    def test_a_header_counts_its_pins_per_row(self):
        header = dict(self.PHYSICAL["header"], pins=[8])
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header=header)),
                         ["physical.header.pins counts 1 row(s), but rows says 2"])
        for pins in ([4, 0], [True], 8):
            with self.subTest(pins=pins):
                said = self.problems(physical=dict(self.PHYSICAL, header=dict(self.PHYSICAL["header"], pins=pins)))
                self.assertEqual(said, ["physical.header.pins is %r, but it is a list of whole pin counts above 0, one per row" % (pins,)])
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header=2.54)), ["physical.header is 2.54, but it is an object"])

    def test_counts_are_whole_numbers_and_a_header_key_is_never_null_or_empty(self):
        header = dict(self.PHYSICAL["header"], rows=2.0)
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header=header)),
                         ["physical.header.rows is 2.0, but it is a whole number above 0"])
        header = dict(self.PHYSICAL["header"], pins=[8.5, 4])
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header=header)),
                         ["physical.header.pins is [8.5, 4], but it is a list of whole pin counts above 0, one per row"])
        for value in (None, [], {}):
            with self.subTest(value=value):
                header = dict(self.PHYSICAL["header"], pins=value)
                self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header=header)),
                                 ["physical.header.pins is %r; leave the key out and name it in physical_proof.not_published" % (value,)])
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, header={})),
                         ["physical.header is {}; leave the key out and name it in physical_proof.not_published"])

    def test_a_huge_integer_is_a_size_and_never_a_traceback(self):
        huge = 10 ** 400  # valid JSON; math.isfinite raises OverflowError on it (P434)
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, thickness_mm=huge)), [])
        holes = [{"x_mm": huge, "y_mm": 2.0, "drill_mm": 2.2}]
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, mounting_holes=holes)), [])

    def test_the_block_holds_the_three_keys_and_notes_under_double_slash(self):
        self.assertEqual(self.problems(physical=dict(self.PHYSICAL, **{"width_mm": 16, "//header": "two rows"})),
                         ["physical.width_mm is not one of thickness_mm, mounting_holes, header: a size the sheet reads goes under "
                          "the board record's key name, and a note under a key that starts with //"])

    def test_fact_set_writes_the_block_with_its_proof_and_refuses_a_wrong_one(self):
        home = Path(tempfile.mkdtemp()); (home / "catalog").mkdir()
        (home / "catalog" / "x-mic.json").write_text(json.dumps(self.record(physical=None, physical_proof=None)))
        given = home / "write.json"
        given.write_text(json.dumps({"physical": self.PHYSICAL, "physical_proof": self.PROOF}))
        with in_store(home):
            said, code = run_json(["--fact-set", "x-mic", str(given)])
            after = json.loads((home / "catalog" / "x-mic.json").read_text())
            given.write_text(json.dumps({"physical": {"thickness_mm": 0}, "physical_proof": self.PROOF}))
            refused, bad = run_json(["--fact-set", "x-mic", str(given)])
        self.assertEqual((code, after["physical"], after["physical_proof"]), (0, self.PHYSICAL, self.PROOF))
        self.assertEqual((bad, [p["sentence"] for p in refused["problems"]]),
                         (1, ["physical.thickness_mm is 0, but it is a number above 0"]))

    def test_the_proof_carries_verified_and_source_and_an_unverified_one_its_why(self):
        self.assertEqual(len(self.problems(physical_proof={})), 2)
        self.assertEqual(self.problems(physical_proof={"verified": False, "source": "a photo"}),
                         ["physical_proof is unverified with no why_it_matters; say what depends on it — here, where "
                          "the module's holes and pins land"])
        self.assertEqual(self.problems(physical_proof={"verified": False, "source": "a photo", "why_it_matters": "the fit"}), [])
        self.assertTrue(self.problems(physical_proof={"verified": "yes", "source": ""}))

    def test_not_published_names_only_keys_the_block_leaves_out(self):
        self.assertEqual(self.problems(physical_proof=dict(self.PROOF, not_published=["thickness_mm"])),
                         ["physical_proof.not_published names thickness_mm, but physical holds it: one of the two is wrong"])
        without = {key: value for key, value in self.PHYSICAL.items() if key != "thickness_mm"}
        self.assertEqual(self.problems(physical=without, physical_proof=dict(self.PROOF, not_published=["thickness_mm"])), [])
        self.assertEqual(self.problems(physical_proof=dict(self.PROOF, not_published="thickness_mm")),
                         ["physical_proof.not_published is 'thickness_mm', but it is a list of the keys the vendor did not publish"])

    def test_a_proof_that_is_no_object_and_a_null_size_are_each_one_sentence(self):
        self.assertEqual(self.problems(physical_proof=["the wiki"]),
                         ["physical_proof is ['the wiki'], but it is an object {verified, source, cites, not_published}"])
        self.assertEqual(self.problems(physical=None, physical_proof="the wiki"),
                         ["physical_proof is 'the wiki', but it is an object {verified, source, cites, not_published}"])
        self.assertEqual(len(self.problems(physical=dict(self.PHYSICAL, thickness_mm=[]))), 1)
        self.assertEqual(len(self.problems(physical=dict(self.PHYSICAL, header=None))), 1)

    def test_not_published_names_only_the_three_keys(self):
        self.assertEqual(self.problems(physical_proof=dict(self.PROOF, not_published=["colour"])),
                         ["physical_proof.not_published names colour, which is not one of thickness_mm, mounting_holes, header"])

    def test_a_proof_with_no_block_holds_only_when_it_names_what_was_not_published(self):
        self.assertEqual(self.problems(physical=None, physical_proof=dict(self.PROOF, not_published=["thickness_mm", "mounting_holes", "header"])), [])
        self.assertEqual(self.problems(physical=None),
                         ["physical_proof vouches for no physical and names nothing in not_published: leave both out, "
                          "or say what was not published"])

    def test_an_unverified_block_is_listed_with_its_own_why_and_goes_back_under_physical_proof(self):
        proof = {"verified": False, "source": "read off the wiki's drawing", "why_it_matters": "where the holes land"}
        listed = [q for q in part_facts.open_questions_of(self.record(physical_proof=proof)) if q["fact"] == "physical"]
        self.assertEqual(listed, [{"part": "x-mic", "fact": "physical", "assumed": self.PHYSICAL, "write": "physical_proof",
                                   "source": "read off the wiki's drawing", "why_it_matters": "where the holes land"}])
        self.assertEqual(part_facts.open_questions_of(self.record()), [], "a verified block is not an open question")

    def test_show_prints_the_block_its_proof_and_what_was_not_published(self):
        home = Path(tempfile.mkdtemp()); (home / "catalog").mkdir()
        without = {key: value for key, value in self.PHYSICAL.items() if key != "thickness_mm"}
        proof = {"verified": False, "source": "the wiki table", "why_it_matters": "where the holes land", "not_published": ["thickness_mm"]}
        (home / "catalog" / "x-mic.json").write_text(json.dumps(self.record(physical=without, physical_proof=proof)))
        with in_store(home):
            said, code = run_json(["--show", "x-mic"])
            with contextlib.redirect_stdout(io.StringIO()) as out:
                parts.main(["--show", "x-mic"])
        self.assertEqual((code, said["data"]["record"]["physical"]), (0, without))
        text = out.getvalue()
        self.assertIn("  physical: UNVERIFIED (the wiki table)\n", text)
        self.assertIn("    mounting_holes               [{\"x_mm\": 2.0, \"y_mm\": 2.0, \"drill_mm\": 2.2}, ", text)
        self.assertIn("    header                       {\"pitch_mm\": 2.54, ", text)
        self.assertIn("    not published: thickness_mm\n      where the holes land\n", text)
        self.assertNotIn("thickness_mm ", text.split("not published")[0])

    def test_validate_passes_a_project_record_with_the_block(self):
        project = Path(tempfile.mkdtemp()); (project / "parts").mkdir()
        (project / "parts" / "x-mic.json").write_text(json.dumps(self.record()))
        said, code = run_json(["--validate", "--project", str(project)])
        self.assertEqual((code, [one["problems"] for one in said["data"]["checked"] if one["part"] == "x-mic"]), (0, [[]]))


class APullTheBoardAddsAgainstTheModulesOwnIsShownWithItsArithmeticTest(unittest.TestCase):
    """
    P81 increment 2, B11. The L9110S record states, verified, 10 k pull-ups to VCC on its inputs, and
    demands 10 k pull-downs of the board "so both are held low" — together a divider at half the
    supply, above the 2.5 V input threshold on the 6 V pack. The record's own note said so; no
    output did. A pull the board adds against the module's own is now shown, with the arithmetic.
    """

    def record(self, pulldown_ohms=10000):
        return part(facts={"onboard_input_pullups_ohms": {"value": 10000, "verified": True, "source": "schematic"},
                           "input_high_threshold_v": {"value": 2.5, "verified": True, "source": "datasheet"},
                           "supply_range_v": {"value": [2.5, 12.0], "verified": True, "source": "datasheet"}},
                    needs=[{"signal": "MOTOR_IA", "pin": "AIA"}],
                    host_parts=[{"kind": "pulldown", "pin": "AIA", "ohms": pulldown_ohms, "why": "held low"}])

    def test_the_divider_and_where_it_crosses_the_threshold_are_said(self):
        said = " ".join(part_rules.pull_conflicts(self.record()))
        self.assertIn("AIA", said)
        self.assertIn("0.5 of the supply", said)
        self.assertIn("5 V", said, "2.5 V x (10k + 10k) / 10k: the supply above which the pin idles HIGH")
        self.assertIn("input-low threshold is not recorded", said, "what is missing to decide, named")

    def test_a_pulldown_strong_enough_for_the_whole_supply_range_is_quiet(self):
        # 1 k against 10 k: at 12 V the pin idles at 1.09 V, under the 2.5 V threshold everywhere.
        self.assertEqual(part_rules.pull_conflicts(self.record(pulldown_ohms=1000)), [])

    def test_show_prints_it_where_a_person_reads_the_part(self):
        self.assertIn("5 V", part_facts.describe(self.record()))

class ReadingADatasheetStopsWhenItHasWhatItNeedsTest(unittest.TestCase):
    """
    P80. A research run printed a whole datasheet early and paid for it on every later turn; the
    facts a record needs sit on one or two pages (13 % of the LED's text, 2 % of the WROOM's). So
    `--read` streams page by page and stops on the page where every wanted fact has a table row.
    The fixture is written in a datasheet's shape; no vendor's text is copied.
    """

    PAGE_1 = """
    FEATURES
      * Low forward voltage, typically 1.9 V
      * Viewing angle 30 deg
    """
    PAGE_2 = """
    ELECTRICAL / OPTICAL CHARACTERISTICS at TA=25 C
      Parameter              Symbol      Typ.      Max.      Unit      Test Condition
      Forward Voltage        VF          1.9       2.3       V         IF=10mA
      Peak Wavelength        lambda      627                 nm        IF=10mA
    ABSOLUTE MAXIMUM RATINGS
      DC Forward Current     IF                    30        mA
    Viewing angle (2 theta)
      Lamp
           30
    """

    def pages(self, *texts):
        for number, text in enumerate(texts, 1):
            yield number, text
        raise AssertionError("read past the last page the facts are on")

    def test_a_fact_on_a_table_row_is_found_and_the_reading_stops_there(self):
        found = datasheets.scan_datasheet(self.pages(self.PAGE_1, self.PAGE_2),
                                          ["forward_voltage_v", "max_continuous_current_ma"])
        self.assertEqual(found["forward_voltage_v"]["status"], "FOUND")
        self.assertEqual(found["forward_voltage_v"]["hits"][0][:2], (2, 4), "page 2, line 4")
        self.assertIn("1.9", found["forward_voltage_v"]["hits"][0][3])
        self.assertEqual(found["max_continuous_current_ma"]["status"], "FOUND")

    def test_a_prose_bullet_is_never_taken_for_the_table(self):
        # The S3 overview's "7 uA" bullet was taken before the table — the P63 misreading in miniature.
        found = datasheets.scan_datasheet(iter([(1, self.PAGE_1)]), ["forward_voltage_v"])
        self.assertNotEqual(found["forward_voltage_v"]["status"], "FOUND")

    def test_a_unit_stated_in_a_column_header_counts(self):
        page = """
        Table 12: Current Consumption
          Work mode                 Description                     Current (uA)
          Deep-sleep                RTC memory and peripherals on   8
        """
        found = datasheets.scan_datasheet(iter([(1, page)]), ["deep_sleep_current_ua"])
        self.assertEqual(found["deep_sleep_current_ua"]["status"], "FOUND")
        self.assertIn("Table 12", found["deep_sleep_current_ua"]["hits"][0][2], "the locator a citation needs")

    def test_a_label_whose_value_sits_below_shows_the_next_lines(self):
        found = datasheets.scan_datasheet(iter([(1, self.PAGE_2)]), ["viewing_angle_deg"])
        self.assertEqual(found["viewing_angle_deg"]["status"], "LABEL ONLY")
        self.assertIn("30", found["viewing_angle_deg"]["hits"][0][3])

    def test_a_fact_nowhere_says_so_and_names_the_words_tried(self):
        found = datasheets.scan_datasheet(iter([(1, self.PAGE_2)]), ["reverse_current_ua"],
                                          labels={"reverse_current_ua": ["leakage"]})
        self.assertEqual(found["reverse_current_ua"]["status"], "NOT FOUND")
        self.assertIn("leakage", found["reverse_current_ua"]["tried"])

    def test_a_value_on_the_line_above_its_label_is_shown(self):
        # The WROOM-1's Table 12: "Deep-sleep" sits between its two rows, 8 uA above and 7 uA below
        # — showing only what follows the label is how 8 uA could be missed again (P63).
        page = """
        Table 12: Current Consumption Depending on Work Modes
          Work mode      Description                                       Typ      Unit
                         RTC memory and RTC peripherals are powered on.    8        uA
          Deep-sleep
                         RTC memory is powered on. RTC peripherals off.    7        uA
        """
        hit = datasheets.scan_datasheet(iter([(1, page)]),
                                        ["deep_sleep_current_ua"])["deep_sleep_current_ua"]["hits"][0][3]
        self.assertIn("8", hit)
        self.assertIn("7", hit)

    def test_a_table_row_is_never_taken_for_the_heading_it_sits_under(self):
        page = """
        Table 9: Recommended Operating Conditions
          VDD33        Power supply voltage        3.0     3.3     3.6     V
        """
        hit = datasheets.scan_datasheet(iter([(1, page)]), ["supply_voltage_v"])["supply_voltage_v"]["hits"][0]
        self.assertEqual(hit[2], "Table 9: Recommended Operating Conditions")

    def test_a_stray_capital_letter_is_not_a_heading(self):
        # The L-7113ID's ratings table has a line reading "K      Symbol" under its real heading.
        page = """
        ABSOLUTE MAXIMUM RATINGS
        K                           Symbol
          DC Forward Current        IF        30        mA
        """
        hit = datasheets.scan_datasheet(iter([(1, page)]),
                                        ["max_continuous_current_ma"])["max_continuous_current_ma"]["hits"][0]
        self.assertEqual(hit[2], "ABSOLUTE MAXIMUM RATINGS")

    def test_a_maker_naming_the_fact_its_own_way_is_still_read(self):
        page = """
          Parameter                           Symbol     Typ.     Unit
          Wavelength at Peak Emission         lpeak      627      nm
        """
        found = datasheets.scan_datasheet(iter([(1, page)]), ["peak_wavelength_nm"])["peak_wavelength_nm"]
        self.assertEqual(found["status"], "FOUND")
        self.assertEqual(len(found["tried"]), len(set(found["tried"])), "each word tried once")

    def test_the_command_reads_a_real_pdf_and_exits_by_what_it_found(self):
        import shutil
        import tempfile
        if not shutil.which("pdftotext"):
            self.skipTest("pdftotext is not installed")
        pdf = Path(tempfile.mkdtemp()) / "ds.pdf"
        pdf.write_bytes(_tiny_pdf([["FEATURES", "Small and bright"],
                                   ["Parameter      Symbol      Max.      Unit", "DC Forward Current      IF      30      mA"],
                                   ["this page must not be read"]]))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--read", str(pdf), "--want", "max_continuous_current_ma"])
        self.assertEqual(code, parts.EXIT_OK, out.getvalue())
        self.assertIn("p2:", out.getvalue())
        self.assertIn("read 2 of", out.getvalue(), "it stopped at the page with the fact")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = parts.main(["--read", str(pdf), "--want", "peak_wavelength_nm"])
        self.assertNotEqual(code, parts.EXIT_OK, "a fact not found is not a pass")


def _tiny_pdf(pages):
    """A PDF with one text line per entry, columns kept by spaces — enough for pdftotext -layout."""
    objects, kids = [], []
    font = "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"
    objects.append(font)
    for lines in pages:
        stream = "BT /F1 10 Tf 40 760 Td 12 TL " + " ".join("(%s) '" % line for line in lines) + " ET"
        objects.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        kids.append(len(objects) + 1)
        objects.append("<< /Type /Page /Parent PAGESREF /MediaBox [0 0 612 792] /Contents %d 0 R "
                       "/Resources << /Font << /F1 1 0 R >> >> >>" % len(objects))
    pages_index = len(objects) + 1
    objects.append("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % k for k in kids), len(kids)))
    objects.append("<< /Type /Catalog /Pages %d 0 R >>" % pages_index)
    out, offsets = "%PDF-1.4\n", []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += "%d 0 obj\n%s\nendobj\n" % (number, body.replace("PAGESREF", "%d 0 R" % pages_index))
    xref = len(out)
    out += "xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1) + "".join("%010d 00000 n \n" % o for o in offsets)
    out += "trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, len(objects), xref)
    return out.encode("latin-1")



class TheCatalogIsThePersonSTest(unittest.TestCase):
    """P83: candidates nobody chose live in the person's store, keep their part facts, and no seller listings."""

    def test_the_catalog_lives_in_the_person_s_store_not_the_plugin(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "rtc-a.json").write_text(json.dumps({"schema": 1, "id": "rtc-a", "name": "An RTC", "kind": "rtc"}))
        with in_store(home):
            self.assertEqual(sorted(datasheets.catalog_records()[0]), ["rtc-a"], "read from the store's catalog")
        self.assertEqual(sorted((ROOT / "catalog").glob("*.json")), [], "the plugin ships no catalog records")

    def test_a_catalog_record_with_seller_listings_is_refused_by_name(self):
        import tempfile
        home = Path(tempfile.mkdtemp()); catalog = home / "catalog"; catalog.mkdir()
        record = {"schema": 1, "id": "rtc-a", "name": "An RTC", "kind": "rtc",
                  "pin_order": ["VCC", "GND", "SCL", "SDA"],
                  "sourcing": [{"seller": "a shop", "url": "https://example.org", "price_czk": 99}]}
        (catalog / "rtc-a.json").write_text(json.dumps(record))
        kept = dict(record, id="rtc-b"); kept.pop("sourcing")
        (catalog / "rtc-b.json").write_text(json.dumps(kept))
        with in_store(home):
            records, broken = datasheets.catalog_records()
        self.assertEqual(sorted(records), ["rtc-b"], "a candidate keeps its part facts — its pinout too")
        self.assertEqual(records["rtc-b"]["pin_order"], ["VCC", "GND", "SCL", "SDA"])
        self.assertEqual(len(broken), 1)
        self.assertIn("rtc-a.json", broken[0])
        self.assertIn("seller listings", broken[0])


#: `notes` and `assumptions` joined in P124 (#58): what the text said and the envelope left out.
ENVELOPE_KEYS = ["assumptions", "data", "envelope", "next", "notes", "op", "problems", "status", "tool", "truncated",
                 "unchecked"]


class SaidAnswer(AnswerOperation):
    """A parts.py Operation that answers a given Answer: the text printer's rules are `Answer.to_result`'s and `run_cli`'s since P726."""

    name = "show"
    arguments = (COMMON_ARGUMENTS[JSON_DEST],)

    def __init__(self, answer):
        self.answer = answer

    def build_answer(self):
        return self.answer


def say_through_the_core(answer, as_json):
    """(stdout, stderr) of `answer` printed as parts.py prints it, with --json or without."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        cli.run_cli(parts.HELP, SaidAnswer(answer), ["--json"] if as_json else [], outside_builder=build_bare_outside_world)
    return out.getvalue(), err.getvalue()


def run_json(argv):
    """parts.py with --json: (the one envelope it printed, its exit code). Anything else on stdout fails to parse."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


class EveryAnswerIsOneEnvelopeTest(unittest.TestCase):
    """P95, §6.4.1–6.4.5: an agent reads one shape from every parts.py --json run, errors and bad arguments included."""

    def test_every_operation_answers_in_one_envelope_whose_status_is_its_exit(self):
        project = Path(tempfile.mkdtemp())
        for argv in (["--list"], ["--show", "no-such-part"], ["--validate"], ["--signals", "tactile-button"],
                     ["--unverified", "tactile-button"], ["--need", "unobtainium"], ["--skeleton", "x-part"],
                     ["--kept", "nothing-like-this"], ["--catalog"], ["--describe"], ["--promote", "x-part"],
                     ["--keep", str(project / "absent.pdf")], ["--function-set", "x-part", str(project / "absent.json")],
                     ["--fact-set", "x-part", str(project / "absent.json")],
                     ["--audit"], ["--needs", str(project)], ["--needs-set", str(project), str(project / "absent.json")],
                     ["--needs-drop", str(project), "light"],
                     ["--match", str(project)], ["--pick", str(project), "soil=x-part"], ["--bogus"], [],
                     ["--requirements", str(project)], ["--step", str(project), "C"], ["--tally", str(project / "untallied")],
                     ["--list", "--show", "x"]):
            with self.subTest(argv=argv):
                said, code = run_json(argv)
                self.assertEqual(sorted(said), ENVELOPE_KEYS)
                self.assertEqual((said["envelope"], said["tool"]), (1, "parts"))
                self.assertEqual(code, outcomes.EXIT_FOR[said["status"]])

    def test_a_named_id_that_does_not_exist_is_problems(self):
        said, code = run_json(["--show", "no-such-part"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual(said["problems"][0]["subject"], "no-such-part")

    def test_a_bad_argument_is_could_not_run_and_says_where_the_operations_are(self):
        said, code = run_json(["--bogus"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("--describe", said["unchecked"][0]["fix"])

    def test_an_operation_missing_its_project_is_could_not_run(self):
        said, code = run_json(["--skeleton", "x-part", "--kind", "sensor"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))

    def test_finding_nothing_is_an_answer(self):
        said, code = run_json(["--need", "unobtainium"])
        self.assertEqual((said["status"], code, said["data"]["found"]), ("ok", 0, []))

    def test_describe_lists_exactly_what_the_parser_accepts(self):
        said, _ = run_json(["--describe"])
        described = {entry["flag"] for entry in said["data"]["operations"] + said["data"]["options"]}
        accepted = {flag for operation in parts.OPERATIONS.values() for argument in operation.arguments for flag in argument.flags}
        self.assertEqual(described, accepted)
        self.assertEqual(said["data"]["exits"], {"0": "ok", "1": "problems", "2": "could-not-run"})
        self.assertEqual([op["op"] for op in said["data"]["operations"] if op["effects"] and not op["dry_run"]], [],
                         "every operation with an effect takes --dry-run")

    def test_a_dry_run_writes_nothing(self):
        project = Path(tempfile.mkdtemp())
        said, code = run_json(["--skeleton", "x-part", "--kind", "sensor", "--project", str(project), "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse((project / "parts").exists())

    def test_a_dry_run_of_a_network_operation_reaches_nothing(self):
        # `sources_resolve` binds `reachable` as a default argument, so it is the function patched here.
        def no_network(*_):
            raise AssertionError("a dry run asked the network")
        with mock.patch.object(datasheets, "sources_resolve", no_network), \
                mock.patch.object(datasheets, "_download", no_network):
            said, code = run_json(["--sources", "l9110s-module", "--dry-run"])
        self.assertEqual((code, bool(said["data"]["sources"])), (0, True))

    def test_a_record_that_is_not_json_is_could_not_run_not_a_traceback(self):
        project = Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "broken.json").write_text("{")
        said, code = run_json(["--validate", "--project", str(project)])
        self.assertEqual(sorted(said), ENVELOPE_KEYS)
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertIn("broken.json", said["unchecked"][0]["sentence"])

    def test_an_unreadable_store_is_could_not_run_not_a_traceback(self):
        with mock.patch.object(store, "records", side_effect=PermissionError("the store is unreadable")):
            said, code = run_json(["--list"])
        self.assertEqual((sorted(said), said["status"], code), (ENVELOPE_KEYS, "could-not-run", 2))
        self.assertIn("the store is unreadable", said["unchecked"][0]["sentence"])

    def test_a_listing_is_paged_and_says_how_to_get_the_rest(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        for number in range(30):
            (home / "catalog" / ("x-%02d.json" % number)).write_text(json.dumps(
                {"schema": 1, "id": "x-%02d" % number, "name": "A candidate", "kind": "sensor"}))
        with in_store(home):
            first, _ = run_json(["--catalog"])
            rest, _ = run_json(first["truncated"]["next"]["argv"])
        self.assertEqual((first["truncated"]["shown"], first["truncated"]["total"]), (20, 30))
        self.assertEqual([r["id"] for r in first["data"]["records"] + rest["data"]["records"]],
                         ["x-%02d" % number for number in range(30)])
        self.assertIsNone(rest["truncated"]["next"])
        self.assertEqual(first["truncated"]["next"]["env"], {"SPARK_HOME": str(home.resolve())})  # the page's store (P473)


def run_text(argv):
    """parts.py without --json: (what it printed on stdout, its exit code)."""
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv)
    return out.getvalue(), code


class EveryFieldReachesBothPrintersTest(unittest.TestCase):
    """
    P124 (#58), part 1's CH-16: the text and the envelope are printed from one answer, and each printer left something
    out. A CONFLICT was text only, so `--show --json` answered a clean ok; `--unverified`'s open facts sat in a `data`
    field no page named; a fix reached the text only when an answer had no lines. Each field now reaches both.
    """

    #: One item per field of an answer that both printers must carry. A field added to `Answer` fails the first test
    #: until it has an item here, and so until the core prints it (`Answer.to_result`, `run_cli`).
    SAMPLES = {
        "problems": record_kind._problem("thing", "is wrong in a way the lines never said", "do this to mend it"),
        "unchecked": record_kind._cannot("could not read the thing's file", "re-save it"),
        "notes": {"subject": "thing", "sentence": "is said and does not fail"},
        "assumptions": {"fact": "thing.pitch_mm", "basis": "unverified", "assumed": 2.0, "sentence": "the socket rests on it",
                        "upgrade": "measure the pitch with calipers"},
        "next": outcomes.step("show", ["--show", "thing"], "to read the thing"),
    }

    def say(self, answer, as_json):
        out, err = say_through_the_core(answer, as_json)
        return out + err

    def test_each_answer_field_reaches_both_the_text_and_the_envelope(self):
        for field in set(record_kind.Answer._fields) - {"data", "lines", "truncated", "diagnostics"}:
            item = self.SAMPLES[field]
            with self.subTest(field=field):
                answer = record_kind.Answer({"x": 1}, ["  a line of the answer"], **{field: [item]})
                said = json.loads(self.say(answer, True))
                self.assertEqual([{k: v for k, v in one.items() if not (k == "code" and v is None)} for one in said[field]], [item])  # P726: items carry `code`
                text = self.say(answer, False)
                for words in filter(None, (item.get("sentence"), item.get("fix"), item.get("why"), item.get("fact"),
                                           item.get("upgrade"))):
                    self.assertIn(words, text)
        self.assertIn("could not check: could not read",
                      self.say(record_kind.Answer({}, ["  a line"], unchecked=[self.SAMPLES["unchecked"]]), False))

    def test_the_diagnostics_go_to_stderr_with_json_or_without_and_never_into_the_envelope(self):
        # P717 (X2): a handler returns its stderr lines and `run_cli` prints them, so no handler prints
        for as_json in (True, False):
            with self.subTest(as_json=as_json):
                out, err = say_through_the_core(record_kind.Answer({"x": 1}, ["  a line"], diagnostics=["a crash's line", "its traceback"]), as_json)
                self.assertEqual(err, "a crash's line\nits traceback\n")
                self.assertNotIn("traceback", out)

    def test_an_answer_with_no_lines_says_its_problems_and_fixes_on_stderr(self):
        out, err = say_through_the_core(record_kind.Answer(problems=[self.SAMPLES["problems"]]), False)
        self.assertEqual(err, "parts.py: is wrong in a way the lines never said — do this to mend it\n")
        self.assertEqual(out, "", "said once, on stderr")

    def test_an_item_with_no_sentence_is_still_said(self):
        bare = {"fact": "thing.colour", "basis": "unverified", "assumed": "red", "sentence": ""}
        self.assertIn("thing.colour = red", self.say(record_kind.Answer({}, ["  a line"], assumptions=[bare]), False))

    def test_two_notes_that_share_a_sentence_are_both_said(self):
        notes = [{"subject": "a", "sentence": "maybe owned"}, {"subject": "b", "sentence": "maybe owned"}]
        text = self.say(record_kind.Answer({}, ["  a: maybe owned"], notes=notes), False)
        self.assertEqual((text.count("a: maybe owned"), text.count("b: maybe owned")), (1, 1), text)

    def test_a_problem_the_lines_say_in_their_own_words_is_not_said_again(self):
        record = written(part("cited", sources=["https://unreachable.example/a.pdf"]))
        asked = []  # the stub answers as the network would, so only its calls show the patch is the one looked up
        unreachable = lambda record: asked.append(1) or [("https://unreachable.example/a.pdf", False)]  # noqa: E731
        project = Path(tempfile.mkdtemp()); (project / "parts").mkdir()
        (project / "parts" / "cited.json").write_text(record.read_text())
        with mock.patch.object(datasheets, "sources_resolve", unreachable):
            text, code = run_text(["--sources", "cited", "--project", str(project)])
        self.assertEqual((code, text.count("unreachable.example"), asked), (1, 1, [1]), text)
        home = Path(tempfile.mkdtemp()); (home / "catalog").mkdir()
        (home / "catalog" / "half-written.json").write_text("{")
        with in_store(home):
            text, _ = run_text(["--catalog"])
        self.assertEqual(text.count("half-written.json"), 1, text)

    def test_a_line_the_answer_already_says_is_not_said_again(self):
        note = {"subject": "thing", "sentence": "is said and does not fail"}
        text = self.say(record_kind.Answer({"x": 1}, ["  thing: is said and does not fail"], notes=[note]), False)
        self.assertEqual(text.count("is said and does not fail"), 1, text)

    def project_with(self, verified, unverified=(), missing=(), low=None):
        project = Path(tempfile.mkdtemp()); (project / "parts").mkdir()
        fact = lambda name, value: dict(  # noqa: E731
            {"value": value, "verified": verified and name not in unverified, "source": "a test fixture"},
            **({} if verified and name not in unverified else {"why_it_matters": "the pull-down's arithmetic rests on it"}))
        values = {"onboard_input_pullups_ohms": 10000, "input_high_threshold_v": 2.5, "supply_range_v": [2.5, 12.0],
                  **({"input_low_threshold_v": low} if low is not None else {})}
        record = part("pulled", facts={name: fact(name, value) for name, value in values.items() if name not in missing},
                      host_parts=[{"kind": "pulldown", "pin": "P", "ohms": 10000, "why": "held low"}])
        (project / "parts" / "pulled.json").write_text(json.dumps(record))
        return project

    def test_a_conflict_on_verified_facts_is_a_problem_in_both(self):
        project = self.project_with(verified=True)
        said, code = run_json(["--show", "pulled", "--project", str(project)])
        text, text_code = run_text(["--show", "pulled", "--project", str(project)])
        self.assertEqual((said["status"], code, text_code), ("problems", 1, 1))
        self.assertEqual(said["problems"][0]["subject"], "pulled.P")
        self.assertIn("CONFLICT: P:", said["problems"][0]["sentence"])
        self.assertEqual(said["problems"][0]["fix"], "record the module's input_low_threshold_v, the level it reads as "
                         "low, then run --show again: held only under the input-high threshold, the level is undefined")
        self.assertEqual(text.count("CONFLICT: P:"), 1, text)
        self.assertEqual(text.count(said["problems"][0]["fix"]), 1, text)
        self.assertNotIn("? CONFLICT", text)

    def test_a_conflict_on_unverified_facts_is_an_assumption_and_the_answer_stays_ok(self):
        project = self.project_with(verified=False)
        said, code = run_json(["--show", "pulled", "--project", str(project)])
        self.assertEqual((said["status"], code, said["problems"]), ("ok", 0, []))
        self.assertEqual([(a["fact"], a["basis"]) for a in said["assumptions"]], [("pulled.P", "unmeasured")])
        self.assertEqual(said["assumptions"][0]["rests_on"],
                         ["pulled.input_high_threshold_v", "pulled.onboard_input_pullups_ohms", "pulled.supply_range_v"])
        self.assertIn("CONFLICT: P:", said["assumptions"][0]["sentence"])
        text = run_text(["--show", "pulled", "--project", str(project)])[0]
        self.assertEqual(text.count("CONFLICT: P:"), 1, text)
        self.assertIn("? CONFLICT: P:", text, "the PO's ? line: a CONFLICT on unverified facts reads as one")
        self.assertEqual(text.count(said["assumptions"][0]["upgrade"]), 1, text)

    def test_a_conflict_s_fix_holds_the_pin_under_the_input_low_threshold(self):
        # The refuter, RF-2: sized against the input-high threshold, the pin sat in the band where the level is undefined.
        said, _ = run_json(["--show", "pulled", "--project", str(self.project_with(verified=True, low=0.8))])
        self.assertEqual(said["problems"][0]["fix"], "a pull-down under 714 ohm holds it under its 0.8 V input-low threshold "
                         "up to 12 V, so it reads low; it then draws up to 1.1 mA from the supply at rest")

    def test_a_conflict_on_a_fact_not_recorded_is_an_assumption(self):
        # The refuter, RF-3: a missing threshold or supply range is no more verified than an unverified one.
        for missing in ("input_high_threshold_v", "supply_range_v"):
            with self.subTest(missing=missing):
                said, code = run_json(["--show", "pulled", "--project",
                                       str(self.project_with(verified=True, missing=(missing,)))])
                self.assertEqual((said["status"], code, said["problems"]), ("ok", 0, []))
                self.assertEqual(said["assumptions"][0]["rests_on"], ["pulled." + missing])

    def test_a_conflict_on_one_unverified_fact_names_only_that_one(self):
        said, code = run_json(["--show", "pulled", "--project",
                               str(self.project_with(verified=True, unverified=("input_high_threshold_v",)))])
        self.assertEqual((said["status"], code, said["problems"]), ("ok", 0, []))
        self.assertEqual(said["assumptions"][0]["rests_on"], ["pulled.input_high_threshold_v"])

    def test_unverified_facts_are_assumptions_and_the_answer_stays_ok(self):
        project = self.project_with(verified=False)
        said, code = run_json(["--unverified", "pulled", "--project", str(project)])
        self.assertEqual((said["status"], code), ("ok", 0))
        self.assertEqual(sorted(a["fact"] for a in said["assumptions"]),
                         ["pulled.input_high_threshold_v", "pulled.onboard_input_pullups_ohms", "pulled.supply_range_v"])
        self.assertEqual({a["basis"] for a in said["assumptions"]}, {"unverified"})
        self.assertEqual({a["source"] for a in said["assumptions"]}, {"a test fixture"})
        self.assertNotIn("questions", said["data"])
        text, _ = run_text(["--unverified", "pulled", "--project", str(project)])
        for fact in ("pulled.input_high_threshold_v = 2.5", "pulled.onboard_input_pullups_ohms = 10000"):
            self.assertEqual(text.count(fact), 1, text)

    def test_the_documented_example_answers_in_json_as_its_text_says(self):
        # #58's proof, on the shipped records the journey uses (PA-1): the L9110S's two CONFLICTs, its open facts.
        said, code = run_json(["--show", "l9110s-module"])
        self.assertEqual((said["status"], code, [p["subject"] for p in said["problems"]]),
                         ("problems", 1, ["l9110s-module.AIA", "l9110s-module.AIB"]))
        self.assertTrue(all(p["fix"] for p in said["problems"]))
        text, _ = run_text(["--show", "l9110s-module"])
        self.assertEqual([text.count("fix for l9110s-module.%s: " % pin) for pin in ("AIA", "AIB")], [1, 1], text)
        said, code = run_json(["--unverified", "l9110s-module", "jst-ph-2-power-inlet", "tactile-button"])
        self.assertEqual((said["status"], code, "questions" in said["data"]), ("ok", 0, False))
        self.assertEqual(len(said["assumptions"]),
                         len(part_facts.unverified(["l9110s-module", "jst-ph-2-power-inlet", "tactile-button"])))


class TheShelfIsALayerTest(unittest.TestCase):
    """P91, §5.5: a record on the shelf is found from every project — no project needed — and says where it is."""

    def test_a_record_on_the_shelf_is_listed_and_loaded_without_a_project(self):
        home = Path(tempfile.mkdtemp())
        record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        record["id"] = "x-shelved"
        (home / "shelf").mkdir()
        (home / "shelf" / "x-shelved.json").write_text(json.dumps(record))
        with in_store(home):
            self.assertIn("x-shelved", record_kind.available())
            self.assertEqual(part_records.load("x-shelved")["id"], "x-shelved")
            said, _ = run_json(["--list"])
        self.assertIn({"id": "x-shelved", "layer": "shelf"},
                      [{"id": p["id"], "layer": p["layer"]} for p in said["data"]["parts"]])


class TheShelfTest(unittest.TestCase):
    """P91, §5.5, §5.7: a record from one project goes onto the shelf as the part, not as that project's story of it."""

    def test_a_digest_moves_only_with_the_facts_a_build_reads(self):
        record = {"id": "x", "name": "X", "needs": [{"signal": "SIG"}], "pin_order": ["SIG", "GND"]}
        self.assertEqual(part_facts.digest(record),
                         hashlib.sha256(b'{"needs":[{"signal":"SIG"}],"pin_order":["SIG","GND"]}').hexdigest())
        self.assertEqual(part_facts.digest(dict(record, name="renamed", sources=["https://x.example"])),
                         part_facts.digest(record))
        self.assertNotEqual(part_facts.digest(dict(record, pin_order=["GND", "SIG"])), part_facts.digest(record))

    def test_a_shelved_record_leaves_the_project_s_story_behind_and_says_where_it_came_from(self):
        home, source = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "x-module.json"
        record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        record.update(id="x-module", owned=True, photo="photos/x.jpg", photos=["photos/x.jpg"],
                      sourcing=[{"seller": "a shop"}], alternatives=["y-module"])
        source.write_text(json.dumps(record))
        (source.parent / "x-module" / "chip").mkdir(parents=True)
        (source.parent / "x-module" / "chip" / "x.chip.json").write_text("{}")
        with in_store(home):
            self.assertTrue(part_facts.shelve(source, "irrigation"))
            self.assertFalse(part_facts.shelve(source, "irrigation"), "a retried shelving changes nothing")
            shelved = json.loads((home / "shelf" / "x-module.json").read_text())
            self.assertEqual(part_records.load("x-module")["id"], "x-module", "the shelf copy still meets the contract")
        self.assertEqual(sorted(set(record) - set(shelved)), ["alternatives", "owned", "photo", "photos", "sourcing"])
        self.assertEqual(shelved["based_on"]["project"], "irrigation")
        self.assertEqual(len(shelved["based_on"]["digest"]), 64)
        self.assertTrue((home / "shelf" / "x-module" / "chip" / "x.chip.json").is_file(), "its folder travels with it")

    def test_a_shelved_folder_is_private_though_its_source_was_not(self):
        home, source = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "y-module.json"
        record = json.loads((ROOT / "parts" / "tactile-button.json").read_text())
        record["id"] = "y-module"
        source.write_text(json.dumps(record))
        chip = source.parent / "y-module" / "chip"
        chip.mkdir(parents=True)
        (chip / "y.chip.json").write_text("{}")
        os.chmod(chip / "y.chip.json", 0o644)
        os.chmod(chip, 0o755)
        with in_store(home):
            part_facts.shelve(source, "irrigation")
        shelved = home / "shelf" / "y-module" / "chip"
        self.assertEqual(stat.S_IMODE((shelved / "y.chip.json").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(shelved.stat().st_mode), 0o700)


class OwningIsTheDrawersTest(unittest.TestCase):
    """P95 (W16): a record no longer says the person owns one — the drawer does."""

    def test_owned_photo_and_an_owned_seller_are_refused_naming_where_they_go(self):
        for extra, where in (({"owned": True}, "drawer"), ({"photo": "photos/x.jpg"}, "photos"),
                             ({"sourcing": [{"seller": "owned"}]}, "drawer")):
            with self.subTest(extra=extra):
                definition = part(**extra)
                said = [problem for problem in part_records.validate(definition, written(definition))
                        if "retired" in problem]
                self.assertEqual(len(said), 1, said)
                self.assertIn(where, said[0])


class WhatAPartDoesTest(unittest.TestCase):
    """P96, §5.6: a record says what it does, or its kind says it; a sensor's is written once, through parts.py."""

    def test_a_kind_that_says_it_and_a_function_that_says_it(self):
        self.assertEqual(part_records.function_of({"kind": "rtc"}), [{"does": "keep-time", "what": "rtc"}])
        self.assertEqual(part_records.function_of({"kind": "rtc", "function": [{"does": "store", "what": "eeprom"}]}),
                         [{"does": "store", "what": "eeprom"}], "a record's own function wins")
        self.assertEqual(part_records.function_of({"kind": "sensor"}), [], "a sensor says nothing until it is written")
        self.assertEqual(part_records.function_of({"pins": {}}, board=True), [{"does": "compute",
                                                                               "what": "microcontroller"}])

    LED = {"does": "indicate", "what": "onboard LED light", "role": "onboard_led"}
    BUTTON = {"does": "input", "what": "onboard button", "role": "onboard_button"}
    SCREEN = {"does": "indicate", "what": "onboard display screen", "role": "onboard_display"}
    COMPUTE = {"does": "compute", "what": "microcontroller"}

    def test_a_board_also_does_what_its_own_parts_do_in_table_order(self):
        roles = {"onboard_display": {"gpio": [4, 5], "labels": {"BL": 4}, "note": "x"}, "onboard_button": {"gpio": [0], "note": "x"},
                 "onboard_led": {"gpio": [2], "note": "x"}, "strapping": {"gpio": [0], "note": "x"}}
        self.assertEqual(part_records.function_of({"pin_roles": roles}, board=True), [self.COMPUTE, self.LED,
                                                                                      self.BUTTON, self.SCREEN])

    def test_a_board_with_a_function_of_its_own_still_does_what_its_own_parts_do(self):
        own = [{"does": "store", "what": "eeprom"}]
        record = {"function": own, "pin_roles": {"onboard_led": {"gpio": [2], "note": "x"}}}
        self.assertEqual(part_records.function_of(record, board=True), own + [self.LED])
        self.assertEqual(own, [{"does": "store", "what": "eeprom"}], "the record's own list is not changed")

    def test_a_part_that_is_no_board_does_not_gain_the_board_s_parts(self):
        record = {"kind": "rtc", "pin_roles": {"onboard_led": {"gpio": [2], "note": "x"}}}
        self.assertEqual(part_records.function_of(record), [{"does": "keep-time", "what": "rtc"}])

    def test_a_function_the_record_already_says_is_not_added_twice(self):
        record = {"function": [{"does": "indicate", "what": "onboard LED light"}], "pin_roles": {"onboard_led": {"gpio": [2], "note": "x"}}}
        self.assertEqual(part_records.function_of(record, board=True), [self.LED])

    def test_the_boards_own_dict_with_its_role_wins_a_function_the_record_says_without_one(self):
        # P397: a record may name "input / onboard button" itself. The pick reads the role, so the role-less copy must not shadow it.
        own = {"does": "input", "what": "onboard button"}
        record = {"function": [own, {"does": "store", "what": "eeprom"}], "pin_roles": {"onboard_button": {"gpio": [9], "note": "x"}}}
        self.assertEqual(part_records.function_of(record, board=True), [self.BUTTON, {"does": "store",
                                                                                      "what": "eeprom"}])
        self.assertEqual(own, {"does": "input", "what": "onboard button"}, "the record's own function is not changed")

    def test_pin_roles_of_the_wrong_shape_name_no_part(self):
        for pin_roles in (["onboard_led"], "onboard_led", None, {"onboard_led": "x"}, {"onboard_led": ["gpio"]}):
            with self.subTest(pin_roles=pin_roles):
                self.assertEqual(part_records.function_of({"pin_roles": pin_roles}, board=True), [self.COMPUTE])

    def test_a_part_is_offered_only_when_pins_py_has_a_name_for_its_pins(self):
        # the walk record's buttons: two GPIOs and no labels get no name in pins.py, so they are not offered
        for entry, offered in (({"gpio": [], "note": "x"}, False), ({"gpio": [0, 35], "note": "x"}, False),
                               ({"gpio": [0, 35], "labels": {}, "note": "x"}, False), ({"gpio": 7, "note": "x"}, False),
                               ({"gpio": [7], "note": "x"}, True), ({"gpio": [0, 35], "labels": {"S1": 0}, "note": "x"}, True),
                               ({"gpio": [], "labels": {"S1": 0}, "note": "x"}, True), ({"labels": {"S1": 0}, "note": "x"}, False)):
            with self.subTest(entry=entry):
                said = part_records.function_of({"pin_roles": {"onboard_led": entry}}, board=True)
                self.assertEqual(said, [self.COMPUTE, self.LED] if offered else [self.COMPUTE])

    def test_a_board_does_what_its_power_facts_say_after_what_its_pin_roles_say(self):
        fact = {"value": "TP4054", "verified": True, "source": "s"}
        record = {"power": {"battery_input": fact, "charger": fact}, "pin_roles": {"onboard_led": {"gpio": [2], "note": "x"}}}
        self.assertEqual(part_records.function_of(record, board=True),
                         [self.COMPUTE, self.LED, {"does": "power", "what": "onboard charger"},
                          {"does": "connect", "what": "onboard battery input"}])
        self.assertEqual(part_records.function_of(record), [],
                         "a part that is no board does not gain the board's power parts")

    def test_a_function_outside_the_thirteen_verbs_is_refused(self):
        definition = part(function=[{"does": "measure", "what": "soil-moisture"}])
        self.assertTrue(any("function" in p and "keep-time" in p for p in part_records.validate(definition,
                                                                                                written(definition))))
        definition = part(function=[{"does": "sense", "what": "soil-moisture"}])
        self.assertEqual([p for p in part_records.validate(definition, written(definition)) if "function" in p], [])

    def test_function_set_writes_into_the_record_s_own_home_after_a_dry_run(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        with in_store(home):
            dry, code = run_json(["--function-set", "x-soil", str(given), "--dry-run"])
            self.assertEqual((code, dry["data"]["written"]), (0, False))
            self.assertNotIn("function", json.loads((home / "catalog" / "x-soil.json").read_text()))
            done, code = run_json(["--function-set", "x-soil", str(given)])
        self.assertEqual((code, done["data"]["now"]), (0, [{"does": "sense", "what": "soil-moisture"}]))
        self.assertEqual(json.loads((home / "catalog" / "x-soil.json").read_text())["function"],
                         [{"does": "sense", "what": "soil-moisture"}])

    def a_probe_in_the_catalog(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        return home, given

    def test_function_set_refuses_spark_s_own_library_and_writes_nothing(self):
        library = Path(tempfile.mkdtemp()) / "parts"
        library.mkdir()
        record = {"schema": 1, "id": "x-inlet", "name": "An inlet", "kind": "connector"}
        (library / "x-inlet.json").write_text(json.dumps(record))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "connect", "what": "power-inlet"}]))
        with in_store(Path(tempfile.mkdtemp())), mock.patch.object(record_kind, "LIBRARY", library):
            said, code = run_json(["--function-set", "x-inlet", str(given)])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("spark's own library", said["problems"][0]["sentence"])
        self.assertIn("x-inlet is in spark's own library", said["problems"][0]["sentence"])  # F10: text mode prints the sentence alone
        self.assertEqual(json.loads((library / "x-inlet.json").read_text()), record)

    def test_function_set_says_which_file_it_changes(self):
        home, given = self.a_probe_in_the_catalog()
        out = io.StringIO()
        with in_store(home):
            said, _ = run_json(["--function-set", "x-soil", str(given), "--dry-run"])
            with contextlib.redirect_stdout(out):
                parts.main(["--function-set", "x-soil", str(given), "--dry-run"])
        self.assertEqual(Path(said["data"]["path"]).resolve(), (home / "catalog" / "x-soil.json").resolve())
        self.assertIn("x-soil.json", out.getvalue())

    def test_a_retried_function_set_is_carried_out_with_nothing_to_change(self):
        home, given = self.a_probe_in_the_catalog()
        out = io.StringIO()
        with in_store(home):
            run_json(["--function-set", "x-soil", str(given)])
            said, code = run_json(["--function-set", "x-soil", str(given)])
            with contextlib.redirect_stdout(out):
                parts.main(["--function-set", "x-soil", str(given)])
        self.assertEqual((code, said["data"]["written"]), (0, True))
        self.assertIn("nothing to change", out.getvalue())

    def test_function_set_with_the_project_writes_the_copy_match_reads(self):
        home, given = self.a_probe_in_the_catalog()
        project = Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        with in_store(home):
            _, code = run_json(["--function-set", "x-soil", str(given), "--project", str(project)])
        self.assertEqual(code, 0)
        self.assertIn("function", json.loads((project / "parts" / "x-soil.json").read_text()))
        self.assertNotIn("function", json.loads((home / "catalog" / "x-soil.json").read_text()))

    def test_a_project_s_record_is_never_left_half_written(self):
        home, given = self.a_probe_in_the_catalog()
        project = Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        record = {"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}
        (project / "parts" / "x-soil.json").write_text(json.dumps(record))
        with in_store(home), mock.patch.object(Path, "replace", side_effect=OSError("the disk is full")):
            said, code = run_json(["--function-set", "x-soil", str(given), "--project", str(project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual(json.loads((project / "parts" / "x-soil.json").read_text()), record)

    def test_function_set_on_a_shelf_copy_says_it_writes_the_shelf(self):
        home, given = self.a_probe_in_the_catalog()
        (home / "shelf").mkdir()
        (home / "shelf" / "x-shelved.json").write_text(json.dumps({"schema": 1, "id": "x-shelved", "name": "A probe", "kind": "sensor",
                                                                     "needs": [], "based_on": {"project": "other", "digest": "0"}}))
        with in_store(home):
            said, code = run_json(["--function-set", "x-shelved", str(given), "--dry-run"])
            shelf = store.place("shelf").resolve()
        self.assertEqual((code, Path(said["data"]["path"]).parent.resolve()), (0, shelf))

    def test_every_record_in_spark_s_library_says_what_it_does(self):
        with in_store(Path(tempfile.mkdtemp())):
            library = {part_id: path for part_id, (layer, path) in store.records("parts", record_kind.LIBRARY).items()
                       if layer == "library"}
        self.assertTrue(library)
        self.assertEqual([part_id for part_id, path in sorted(library.items())
                          if not part_records.function_of(record_kind._parse(path))], [])

    def test_function_set_refuses_a_wrong_function_and_a_part_nobody_has(self):
        home, given = self.a_probe_in_the_catalog()
        given.write_text(json.dumps([{"does": "measure", "what": "x"}]))
        with in_store(home):
            self.assertEqual(run_json(["--function-set", "x-soil", str(given), "--dry-run"])[1], 1)
            given.write_text(json.dumps([{"does": "sense", "what": "x"}]))
            self.assertEqual(run_json(["--function-set", "no-such-part", str(given), "--dry-run"])[1], 1)

    def test_function_set_refuses_null_and_an_empty_list_and_writes_nothing(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        record = {"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}
        (home / "catalog" / "x-soil.json").write_text(json.dumps(record))
        given = Path(tempfile.mkdtemp()) / "function.json"
        for text in ("null", "[]"):
            given.write_text(text)
            with self.subTest(text=text), in_store(home):
                said, code = run_json(["--function-set", "x-soil", str(given)])
                self.assertEqual((said["status"], code), ("problems", 1))
                self.assertIn("non-empty list", said["problems"][0]["sentence"])
            self.assertEqual(json.loads((home / "catalog" / "x-soil.json").read_text()), record)


class ALevelIsWrittenToABoardTest(unittest.TestCase):
    """P464 (#632): `--fact-set` writes the active level of a board's onboard LED or button, as a fact, to the project's own board."""

    BENCH = {"value": 0, "verified": True, "source": "the PO's bench, 2026-11-01"}

    def a_project(self):
        """(the scratch store, a project whose own board lacks both levels)."""
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "project"
        (project / "boards").mkdir(parents=True)
        board = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
        for role in ("onboard_led", "onboard_button"):
            del board["pin_roles"][role]["active_level"]
        (project / "boards" / "xiao-esp32-c6.json").write_text(json.dumps(board, indent=2))
        return home, project, board

    def given(self, values):
        path = Path(tempfile.mkdtemp()) / "levels.json"
        path.write_text(json.dumps(values))
        return str(path)

    def write(self, home, project, values, *more, part_id="xiao-esp32-c6", flag="--fact-set"):
        with in_store(home):
            return run_json([flag, part_id, self.given(values), "--project", str(project)] + list(more))

    def stored(self, project):
        return json.loads((project / "boards" / "xiao-esp32-c6.json").read_text())

    def test_the_write_merges_role_by_role_and_keeps_gpio_and_note(self):
        home, project, board = self.a_project()
        said, code = self.write(home, project, {"pin_roles": {"onboard_led": {"active_level": self.BENCH}}})
        self.assertEqual((code, said["data"]["written"]), (0, True))
        roles = self.stored(project)["pin_roles"]
        self.assertEqual(roles["onboard_led"], dict(board["pin_roles"]["onboard_led"], active_level=self.BENCH))
        self.assertEqual(roles["onboard_button"], board["pin_roles"]["onboard_button"])
        self.assertEqual(said["data"]["was"]["pin_roles"], {"onboard_led": {"active_level": None}})

    def test_a_dry_run_writes_nothing(self):
        home, project, board = self.a_project()
        said, code = self.write(home, project, {"pin_roles": {"onboard_led": {"active_level": self.BENCH}}}, "--dry-run")
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertEqual(self.stored(project), board)

    def test_what_is_not_a_fact_for_a_known_role_is_refused_and_nothing_is_written(self):
        home, project, board = self.a_project()
        for values in ({"pin_roles": {"onboard_led": {"active_level": 0}}},
                       {"pin_roles": {"onboard_led": {"active_level": dict(self.BENCH, value=2)}}},
                       {"pin_roles": {"onboard_led": {"active_level": self.BENCH, "note": "mine"}}},
                       {"pin_roles": {"onboard_display": {"active_level": self.BENCH}}},
                       {"pin_roles": {"onboard_led": {"active_level": self.BENCH}}, "about": "x"}):
            with self.subTest(values=values):
                self.assertEqual(self.write(home, project, values)[1], 1)
                self.assertEqual(self.stored(project), board)

    def test_a_board_of_spark_s_library_is_refused(self):
        # a dry run, so that a guard that failed would show as "would set" and not write into the library
        said, code = self.write(Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()), {"pin_roles": {"onboard_led": {"active_level": self.BENCH}}}, "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("spark's own library", said["problems"][0]["sentence"])

    def test_a_board_of_another_listed_project_or_of_no_project_is_refused(self):
        # P464: a board is written from its own project only
        home, project, board = self.a_project()
        (project / "boards" / "xiao-esp32-c6.json").rename(project / "boards" / "only-in-b.json")
        board = self.stored_as(project, "only-in-b")
        here = Path(tempfile.mkdtemp()) / "here"
        here.mkdir()
        (home / "projects.json").write_text(json.dumps({"proj-b": str(project)}))
        values = {"pin_roles": {"onboard_led": {"active_level": self.BENCH}}}
        said, code = self.write(home, here, values, part_id="only-in-b")
        self.assertEqual(code, 1)
        self.assertIn("not a board of this project", said["problems"][0]["sentence"])
        self.assertIn("pass --project <the folder", said["problems"][0]["sentence"])
        with in_store(home):
            self.assertEqual(run_json(["--fact-set", "only-in-b", self.given(values)])[1], 1)
        with in_store(home):
            said = run_json(["--fact-set", "only-in-b", self.given(values)])[0]
        self.assertIn("a project (no --project was given)", said["problems"][0]["sentence"])
        self.assertNotIn("None", said["problems"][0]["sentence"])
        self.assertEqual(self.stored_as(project, "only-in-b"), board)
        self.assertEqual(self.write(home, project, values, part_id="only-in-b")[1], 0)

    def test_the_fix_command_run_as_written_from_the_project_folder_writes_the_level(self):
        # P464: the fix names --project ., so a person in the project's folder gets no refusal
        home, project, board = self.a_project()
        (project / "boards" / "xiao-esp32-c6.json").rename(project / "boards" / "only-in-b.json")
        board = dict(self.stored_as(project, "only-in-b"), id="only-in-b")
        (project / "boards" / "only-in-b.json").write_text(json.dumps(board))
        fix = missing_facts.list_missing_facts(board)[0].fix
        command = re.search(r"`parts\.py ([^`]+)`", fix).group(1).replace("FILE", self.given({"pin_roles": {"onboard_led": {"active_level": self.BENCH}}}))
        here = os.getcwd()
        os.chdir(project)
        try:
            with in_store(home):
                said, code = run_json(command.split())
        finally:
            os.chdir(here)
        self.assertEqual((code, said["data"]["written"]), (0, True))
        self.assertEqual(self.stored_as(project, "only-in-b")["pin_roles"]["onboard_led"]["active_level"], self.BENCH)

    def stored_as(self, project, name):
        return json.loads((project / "boards" / (name + ".json")).read_text())

    def test_the_text_of_a_level_is_cleaned_and_cut_and_a_key_with_a_control_character_is_refused(self):
        home, project, board = self.a_project()
        dirty = dict(self.BENCH, source="bench\x07\x1b[31m\nX" + "y" * 5000)
        said, code = self.write(home, project, {"pin_roles": {"onboard_led": {"active_level": dirty}}})
        self.assertEqual(code, 0)
        source = self.stored(project)["pin_roles"]["onboard_led"]["active_level"]["source"]
        self.assertEqual((len(source) <= 1000, any(ord(each) < 32 for each in source)), (True, False))
        home, project, board = self.a_project()
        said, code = self.write(home, project, {"pin_roles": {"onboard_led": {"active_level": dict(self.BENCH, **{"\u0000k": 1})}}})
        self.assertEqual(code, 1)
        self.assertEqual(self.stored(project), board)

    def test_a_write_never_empties_a_level(self):
        home, project, board = self.a_project()
        self.write(home, project, {"pin_roles": {"onboard_led": {"active_level": self.BENCH}}})
        held = self.stored(project)
        said, code = self.write(home, project, {"pin_roles": {"onboard_led": {"active_level": {"value": None, "verified": False, "source": "x"}}}})
        self.assertEqual(code, 1)
        self.assertIn("never empties", said["problems"][0]["sentence"])
        self.assertEqual(self.stored(project), held)

    def test_function_set_never_reaches_a_board(self):
        home, project, board = self.a_project()
        said, code = self.write(home, project, [{"does": "indicate", "what": "led"}], flag="--function-set")
        self.assertEqual(code, 1)
        self.assertIn("no record called 'xiao-esp32-c6'", said["problems"][0]["sentence"] if said["problems"] else said["unchecked"][0]["sentence"])
        self.assertEqual(self.stored(project), board)


class OwedFactsFilledInTheirHomeTest(unittest.TestCase):
    """P97 (§5.4): what a record owes is filled once, in its own home, through parts.py — never in spark's library."""

    def a_probe(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps(
            {"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor", "pin_order": ["GND", "VCC", "SIG"],
             "needs": [{"signal": "SOIL", "pin": "SIG", "direction": "out"}],
             "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}]}))
        return home

    def facts(self, given):
        path = Path(tempfile.mkdtemp()) / "facts.json"
        path.write_text(json.dumps(given))
        return str(path)

    def test_a_fact_is_filled_in_the_catalog_after_a_dry_run(self):
        home = self.a_probe()
        given = self.facts({"footprint": "jst_ph_3", "simulation": {"skip": "no soil in a simulator"}})
        with in_store(home):
            dry, code = run_json(["--fact-set", "x-soil", given, "--dry-run"])
            self.assertEqual((code, dry["data"]["written"]), (0, False))
            self.assertNotIn("footprint", json.loads((home / "catalog" / "x-soil.json").read_text()))
            _, code = run_json(["--fact-set", "x-soil", given])
        record = json.loads((home / "catalog" / "x-soil.json").read_text())
        self.assertEqual((code, record["footprint"], record_kind.owes(record)), (0, "jst_ph_3", ["pin_order_proof",
                                                                                                 "body_mm"]))

    def test_spark_s_library_is_refused(self):
        library = Path(tempfile.mkdtemp()) / "parts"
        library.mkdir()
        record = {"schema": 1, "id": "x-amp", "name": "An amp", "kind": "audio-amplifier", "needs": []}
        (library / "x-amp.json").write_text(json.dumps(record))
        with in_store(Path(tempfile.mkdtemp())), mock.patch.object(record_kind, "LIBRARY", library):
            said, code = run_json(["--fact-set", "x-amp", self.facts({"footprint": "pinrow12"})])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("spark's own library", said["problems"][0]["sentence"])
        self.assertIn("x-amp is in spark's own library", said["problems"][0]["sentence"])  # F10: text mode prints the sentence alone
        self.assertEqual(json.loads((library / "x-amp.json").read_text()), record)

    def test_only_a_fact_the_chain_reads_and_never_an_empty_one(self):
        home = self.a_probe()
        with in_store(home):
            for given in ({"price_czk": 89}, {"footprint": None}, {}, ["jst_ph_3"]):
                with self.subTest(given=given):
                    self.assertEqual(run_json(["--fact-set", "x-soil", self.facts(given)])[1], 1)

    def test_a_record_gets_its_about_and_tags_cleaned(self):
        home = self.a_probe()
        with in_store(home):
            _, code = run_json(["--fact-set", "x-soil", self.facts({"about": "Tells how wet\x00 the soil is.", "tags": ["Plant"]})])
        record = json.loads((home / "catalog" / "x-soil.json").read_text())
        self.assertEqual((code, record["about"], record["tags"]), (0, "Tells how wet  the soil is.", ["plant"]))

    def test_an_unknown_key_is_still_refused(self):
        home = self.a_probe()
        with in_store(home):
            said, code = run_json(["--fact-set", "x-soil", self.facts({"price": 3})])
        self.assertEqual(code, 1)
        self.assertIn("about, description, tags", said["problems"][0]["sentence"])

    def test_a_fact_that_breaks_the_record_is_refused(self):
        home = self.a_probe()
        with in_store(home):
            said, code = run_json(["--fact-set", "x-soil", self.facts({"footprint": "pinrow5"})])
        self.assertEqual(code, 1)
        self.assertIn("5 pads", said["problems"][0]["sentence"])

    def test_a_footprint_that_is_no_name_is_refused_and_nothing_is_written(self):
        home = self.a_probe()
        before = (home / "catalog" / "x-soil.json").read_text()
        with in_store(home):
            for given in (5, True, 3.5, ["jst_ph_3"], {"name": "jst_ph_3"}, 'jst_ph_3" onClick={alert(1)} data-x="'):
                for flags in ([], ["--dry-run"]):
                    with self.subTest(footprint=given, flags=flags):
                        said, code = run_json(["--fact-set", "x-soil", self.facts({"footprint": given})] + flags)
                        self.assertEqual((said["status"], code), ("problems", 1))
                        self.assertTrue(said["problems"][0]["sentence"].startswith("footprint is "), said["problems"])
        self.assertEqual((home / "catalog" / "x-soil.json").read_text(), before)

    def test_a_record_that_is_no_object_is_refused_with_a_sentence_never_a_traceback(self):
        home = self.a_probe()
        function = Path(tempfile.mkdtemp()) / "function.json"
        function.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        for text in ("[]", "5", "null", '"a probe"'):
            (home / "catalog" / "x-soil.json").write_text(text)
            for argv in (["--fact-set", "x-soil", self.facts({"footprint": "jst_ph_3"})], ["--function-set", "x-soil", str(function)]):
                with self.subTest(text=text, op=argv[0]), in_store(home):
                    said, code = run_json(argv)
                    self.assertEqual((said["status"], code), ("problems", 1))
                    self.assertIn("is not a JSON object", said["problems"][0]["sentence"])
                    self.assertIn("x-soil is not a JSON object", said["problems"][0]["sentence"])  # F10: the path names it too
            self.assertEqual((home / "catalog" / "x-soil.json").read_text(), text)

    def test_a_shelf_copy_of_a_listed_project_s_record_is_filled_in_that_project_and_shelved_again(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "irrigation"
        (other / "parts").mkdir(parents=True)
        record = {"schema": 1, "id": "x-valve", "name": "A valve driver", "kind": "mosfet-driver", "needs": []}
        (other / "parts" / "x-valve.json").write_text(json.dumps(record))
        (home / "shelf").mkdir()
        (home / "shelf" / "x-valve.json").write_text(json.dumps(dict(record, based_on={"project": "irrigation", "digest": "0" * 64})))
        (home / "projects.json").write_text(json.dumps({"irrigation": str(other)}))
        with in_store(home):
            said, code = run_json(["--fact-set", "x-valve", self.facts({"footprint": "pinrow2"})])
        self.assertEqual((code, Path(said["data"]["path"]).resolve()), (0, (other / "parts" / "x-valve.json").resolve()))
        self.assertEqual(json.loads((other / "parts" / "x-valve.json").read_text())["footprint"], "pinrow2")
        self.assertEqual(json.loads((home / "shelf" / "x-valve.json").read_text())["footprint"], "pinrow2", "the shelf copy follows")

    def test_a_shelf_copy_whose_project_has_lost_the_record_is_filled_where_it_is(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "irrigation"
        (other / "parts").mkdir(parents=True)
        record = {"schema": 1, "id": "x-valve", "name": "A valve driver", "kind": "mosfet-driver", "needs": []}
        (home / "shelf").mkdir()
        (home / "shelf" / "x-valve.json").write_text(json.dumps(dict(record, based_on={"project": "irrigation", "digest": "0" * 64})))
        (home / "projects.json").write_text(json.dumps({"irrigation": str(other)}))
        with in_store(home):
            said, code = run_json(["--fact-set", "x-valve", self.facts({"footprint": "pinrow2"})])
        self.assertEqual((code, Path(said["data"]["path"]).resolve()), (0, (home / "shelf" / "x-valve.json").resolve()))
        self.assertEqual(json.loads((home / "shelf" / "x-valve.json").read_text())["footprint"], "pinrow2")
        self.assertFalse((other / "parts" / "x-valve.json").exists(), "the project's record is not made up")

    # --- a shelf copy follows its record however the record is reached (the final review) ---

    #: An outline as a record keeps one: the size, and where it came from.
    OUTLINE = {"width": 20, "height": 10, "verified": True, "source": "measured with calipers"}

    def a_valve_in_irrigation(self, **record):
        """irrigation's own x-valve record, owing its footprint, and the shelf copy of it every project reads — stale on
        purpose (a digest nobody computed); the store's list names irrigation."""
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "irrigation"
        (other / "parts").mkdir(parents=True)
        record = dict({"schema": 1, "id": "x-valve", "name": "A valve driver", "kind": "mosfet-driver", "needs": []}, **record)
        (other / "parts" / "x-valve.json").write_text(json.dumps(record))
        (home / "shelf").mkdir()
        (home / "shelf" / "x-valve.json").write_text(json.dumps(dict(record, based_on={"project": "irrigation", "digest": "0" * 64})))
        (home / "projects.json").write_text(json.dumps({"irrigation": str(other)}))
        return home, other

    def text(self, argv):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            parts.main(argv)
        return out.getvalue()

    def shelved(self, home):
        return json.loads((home / "shelf" / "x-valve.json").read_text())

    def test_a_fact_filled_in_its_project_refreshes_the_shelf_copy_that_follows_it(self):
        home, other = self.a_valve_in_irrigation()
        record = (other / "parts" / "x-valve.json").resolve()
        footprint = self.facts({"footprint": "pinrow2"})
        with in_store(home):
            outline = self.text(["--fact-set", "x-valve", self.facts({"body_mm": self.OUTLINE}), "--project", str(other)])
            dry = self.text(["--fact-set", "x-valve", footprint, "--project", str(other), "--dry-run"])
            self.assertNotIn("footprint", self.shelved(home), "a dry run writes nothing")
            said, code = run_json(["--fact-set", "x-valve", footprint, "--project", str(other)])
            again = self.text(["--fact-set", "x-valve", footprint, "--project", str(other)])
        self.assertEqual((outline.splitlines()[1:], dry.splitlines()[1:]), (["  shelf copy refreshed"], ["  would refresh the shelf copy"]))
        self.assertEqual((code, said["data"]["shelf_copy"], self.shelved(home)["footprint"], self.shelved(home)["body_mm"]),
                         (0, "shelf copy refreshed", "pinrow2", self.OUTLINE))
        self.assertEqual((self.shelved(home)["based_on"]["project"], self.shelved(home)["based_on"]["digest"] == "0" * 64), ("irrigation", False))
        self.assertEqual(again, "  nothing to change: x-valve (%s) already says this\n" % record, "a copy that follows says nothing more")

    def test_a_retry_with_nothing_to_change_still_refreshes_a_stale_shelf_copy(self):
        # filled in its project while the copy stayed behind: every retry said "nothing to change", and --requirements refused on
        for through in ("its project", "the shelf copy"):
            home, other = self.a_valve_in_irrigation(footprint="pinrow2")
            with self.subTest(through=through), in_store(home):
                said = self.text(["--fact-set", "x-valve", self.facts({"footprint": "pinrow2"})]
                                 + (["--project", str(other)] if through == "its project" else []))
                self.assertEqual((said.splitlines()[0].startswith("  nothing to change: x-valve ("), said.splitlines()[1:]),
                                 (True, ["  shelf copy refreshed"]))
                self.assertEqual(self.shelved(home)["footprint"], "pinrow2")

    def test_a_shelf_copy_that_would_break_the_contract_is_not_refreshed_and_says_why(self):
        home, other = self.a_valve_in_irrigation(needs=[{"signal": "VALVE", "pin": "GATE", "direction": "sideways"}])
        before = (home / "shelf" / "x-valve.json").read_text()
        with in_store(home):
            said, code = run_json(["--fact-set", "x-valve", self.facts({"footprint": "pinrow2"}), "--project", str(other)])
        self.assertEqual((code, said["data"]["shelf_copy"], (home / "shelf" / "x-valve.json").read_text()),
                         (0, "shelf copy not refreshed: needs[0] direction is 'sideways'; expected in, out or bidirectional", before))

    def test_a_shelf_copy_from_another_project_does_not_follow_this_project_s_record(self):
        home, other = self.a_valve_in_irrigation()
        alarm = Path(tempfile.mkdtemp()) / "plant-alarm"
        (alarm / "parts").mkdir(parents=True)
        (alarm / "parts" / "x-valve.json").write_text(json.dumps(
            {"schema": 1, "id": "x-valve", "name": "Our own valve driver", "kind": "mosfet-driver", "needs": []}))
        (home / "projects.json").write_text(json.dumps({"irrigation": str(other), "plant-alarm": str(alarm)}))
        before = (home / "shelf" / "x-valve.json").read_text()
        with in_store(home):
            said, code = run_json(["--fact-set", "x-valve", self.facts({"footprint": "pinrow2"}), "--project", str(alarm)])
        self.assertEqual((code, said["data"]["shelf_copy"], (home / "shelf" / "x-valve.json").read_text()), (0, None, before))

    def test_the_answer_says_what_each_fact_was_and_what_it_is_now(self):
        home = self.a_probe()
        with in_store(home):
            said, _ = run_json(["--fact-set", "x-soil", self.facts({"footprint": "jst_ph_3"}), "--dry-run"])
        self.assertEqual((said["data"]["part"], said["data"]["was"], said["data"]["now"]),
                         ("x-soil", {"footprint": None}, {"footprint": "jst_ph_3"}))


class ABenchResultGoesBackWithItsSourceTest(unittest.TestCase):
    """P374 (#479): `--fact-set` takes `facts` entries {value, verified, source}, `body_mm` and `pin_order_proof`; P373 lists what is left."""

    BENCH = "bench, 2026-10-29, meter on the owned board, Petr Smejkal"

    def entry(self, **change):
        return dict({"value": True, "verified": True, "source": self.BENCH}, **change)

    def a_joystick(self, **change):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        record = {"schema": 1, "id": "x-joy", "name": "A joystick", "kind": "input", "footprint": "pinrow3",
                  "pin_order": ["GND", "VCC", "X"], "pin_order_proof": {"verified": False, "source": "a photo"},
                  "needs": [{"signal": "X", "pin": "X", "direction": "out"}],
                  "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}],
                  "body_mm": {"width": 34, "height": 26, "verified": False, "source": "a guess", "why_it_matters": "the fit"},
                  "facts": {"runs_at_3v3": {"value": True, "verified": False, "source": "the maker", "why_it_matters": "the rail"},
                            "supply_range_v": {"value": [3, 5], "verified": False, "source": "none", "why_it_matters": "the rail"},
                            "kept": {"value": 1, "verified": True, "source": "page 2"}}}
        (home / "catalog" / "x-joy.json").write_text(json.dumps(dict(record, **change)))
        return home

    def given(self, content):
        path = Path(tempfile.mkdtemp()) / "facts.json"
        path.write_text(json.dumps(content))
        return str(path)

    def record(self, home):
        return json.loads((home / "catalog" / "x-joy.json").read_text())

    def test_a_bench_result_is_written_beside_the_other_entries_and_its_row_goes(self):
        home = self.a_joystick()
        held = self.record(home)["facts"]["runs_at_3v3"]
        with in_store(home):
            said, code = run_json(["--fact-set", "x-joy", self.given({"facts": {"runs_at_3v3": self.entry()}})])
            left = [row["write"] for row in run_json(["--unverified", "x-joy"])[0]["assumptions"]]
        record = self.record(home)
        self.assertEqual((code, record["facts"]["runs_at_3v3"], sorted(record["facts"])), (0, self.entry(), ["kept", "runs_at_3v3", "supply_range_v"]))
        self.assertEqual(record["facts"]["supply_range_v"]["verified"], False)
        self.assertEqual(part_records.broken_problems(record, home / "catalog" / "x-joy.json"), [])
        self.assertEqual((said["data"]["was"], said["data"]["now"]), ({"facts": {"runs_at_3v3": held}}, {"facts": {"runs_at_3v3": self.entry()}}))
        self.assertEqual(left, ["facts.supply_range_v", "pin_order_proof", "body_mm"])

    def test_a_bench_outline_and_pin_order_proof_end_with_nothing_left_unverified(self):
        home = self.a_joystick()
        write = {"facts": {"runs_at_3v3": self.entry(), "supply_range_v": self.entry(value=[3, 5])},
                 "body_mm": {"width": 33.5, "height": 25.8, "verified": True, "source": self.BENCH},
                 "pin_order_proof": {"verified": True, "source": self.BENCH}}
        with in_store(home):
            _, code = run_json(["--fact-set", "x-joy", self.given(write)])
            left = run_json(["--unverified", "x-joy"])[0]["assumptions"]
        self.assertEqual((code, left), (0, []))
        self.assertEqual(self.record(home)["body_mm"]["width"], 33.5)

    def test_a_dry_run_leaves_the_bytes_and_the_same_entry_again_changes_nothing(self):
        home = self.a_joystick()
        path, written = home / "catalog" / "x-joy.json", self.given({"facts": {"runs_at_3v3": self.entry()}})
        before = path.read_bytes()
        with in_store(home):
            said, code = run_json(["--fact-set", "x-joy", written, "--dry-run"])
            self.assertEqual((code, said["data"]["written"], path.read_bytes()), (0, False, before))
            self.assertEqual(said["data"]["now"], {"facts": {"runs_at_3v3": self.entry()}})
            run_json(["--fact-set", "x-joy", written])
            once = path.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()) as out:
                parts.main(["--fact-set", "x-joy", written])
        self.assertNotEqual(once, before)
        self.assertEqual(path.read_bytes(), once)
        self.assertIn("nothing to change", out.getvalue())

    def test_a_mixed_write_sets_the_footprint_and_the_facts_together(self):
        home = self.a_joystick(footprint=None)
        with in_store(home):
            _, code = run_json(["--fact-set", "x-joy", self.given({"footprint": "pinrow3", "facts": {"runs_at_3v3": self.entry()}})])
        record = self.record(home)
        self.assertEqual((code, record["footprint"], record["facts"]["runs_at_3v3"]), (0, "pinrow3", self.entry()))

    def test_the_text_a_bench_result_writes_is_cleaned_and_kept_up_to_a_thousand_characters(self):
        dirty = "bench\u202e, 2026-10-29\x00, meter"
        clean = "bench , 2026-10-29 , meter"
        cases = {"a facts entry": ({"facts": {"runs_at_3v3": self.entry(source=dirty)}}, lambda r: r["facts"]["runs_at_3v3"]["source"]),
                 "an entry named does": ({"facts": {"does": self.entry(source=dirty)}}, lambda r: r["facts"]["does"]["source"]),
                 "a bench body_mm": ({"body_mm": {"width": 34, "height": 26, "verified": True, "source": dirty}},
                                     lambda r: r["body_mm"]["source"]),
                 "a bench pin_order_proof": ({"pin_order_proof": {"verified": True, "source": dirty}},
                                             lambda r: r["pin_order_proof"]["source"])}
        for what, (content, source_of) in cases.items():
            with self.subTest(what), in_store(home := self.a_joystick()):
                said, code = run_json(["--fact-set", "x-joy", self.given(content)])
                self.assertEqual((code, source_of(self.record(home)), source_of(said["data"]["now"])), (0, clean, clean), said)
        with in_store(home := self.a_joystick()):
            run_json(["--fact-set", "x-joy", self.given({"facts": {"runs_at_3v3": self.entry(source="s" * 700)}})])
        self.assertEqual(len(self.record(home)["facts"]["runs_at_3v3"]["source"]), 700)
        from spark.sourcing import drawer
        self.assertEqual(len(drawer.scrub("place", "p" * 700)), 160)

    def test_each_refusal_says_its_own_sentence_and_writes_nothing(self):
        bad_outline = {"width": 34, "height": 26, "verified": True, "source": ""}
        lacks = {"value": 1, "verified": False, "why_it_matters": "the rail"}
        cases = [
            ("an entry whose verified is no bool", {}, {"facts": {"good": self.entry(), "bad": self.entry(verified="yes")}},
             "facts.bad has verified 'yes', but it must be true or false"),
            ("entries that are a list", {}, {"facts": [self.entry()]}, "facts is [{'value': True"),
            ("a name outside the pattern", {}, {"facts": {"good": self.entry(), "Bad Name": self.entry()}},
             "'Bad Name' is no fact name: use lowercase letters, digits and underscores"),
            ("a record whose own facts is a list", {"facts": ["x"]}, {"facts": {"good": self.entry()}},
             "the record's own facts is ['x'], but it is an object — repair the file by hand first"),
            ("a rewrite that lacks a source like the held one", {"facts": {"old": lacks}}, {"facts": {"good": self.entry(), "old": lacks}},
             "facts.old has no 'source' — a number with no provenance is an opinion"),
            ("a bench outline with no words for a source", {}, {"body_mm": bad_outline},
             "body_mm has source '', but it must be words that say where the value came from"),
            ("a key with a bidi character in an entry", {}, {"facts": {"x": dict(self.entry(), **{"no\u202ete": 1})}},
             "facts['x']['no\\u202ete'] is a key that is no string or holds a control or bidi character"),
            ("a key with a control character in a value", {}, {"facts": {"x": self.entry(value={"k": [{"a\x1b": 1}]})}},
             "facts['x']['value']['k'][0]['a\\x1b'] is a key"),
            ("a key with a bidi character in a bench outline", {}, {"body_mm": {
                "width": 34, "height": 26, "verified": True, "source": self.BENCH, "no\u202ete": 1}},
             "body_mm['no\\u202ete'] is a key"),
            ("a key with a control character in a bench pin order proof", {}, {"pin_order_proof": {
                "verified": True, "source": self.BENCH, "no\x00te": 1}}, "pin_order_proof['no\\x00te'] is a key"),
        ]
        for what, held, content, sentence in cases:
            home = self.a_joystick(**held)
            path = home / "catalog" / "x-joy.json"
            before = path.read_bytes()
            with self.subTest(what), in_store(home):
                for flags in ([], ["--dry-run"]):
                    said, code = run_json(["--fact-set", "x-joy", self.given(content)] + flags)
                    self.assertEqual((said["status"], code), ("problems", 1), said)
                    self.assertEqual([sentence in p["sentence"] for p in said["problems"]], [True], said["problems"])  # one fault, one sentence
                self.assertEqual(path.read_bytes(), before)


class OwedIsNotBrokenTest(unittest.TestCase):
    """§5.4: an absent fact is owed — the record waits for it; a present, wrong value is broken."""

    def test_a_record_missing_what_the_chain_reads_owes_it_and_is_not_broken(self):
        definition = part(body_mm={"width": None, "height": None, "verified": False, "source": None})
        self.assertEqual(sorted(record_kind.owes(definition)), ["body_mm", "footprint", "pin_order", "pin_order_proof",
                                                                "simulation"])
        self.assertEqual(part_records.broken_problems(definition, written(definition)), [])

    def test_a_present_wrong_value_is_broken(self):
        definition = part(needs=[{"signal": "SIG", "pin": "S", "direction": "sideways"}])
        self.assertTrue(any("sideways" in p for p in part_records.broken_problems(definition, written(definition))))

    def test_a_footprint_of_the_wrong_type_is_broken_and_an_absent_one_is_only_owed(self):
        wrong = part(footprint=5)
        self.assertNotIn("footprint", record_kind.owes(wrong))
        self.assertEqual([p[:14] for p in part_records.broken_problems(wrong, written(wrong))], ["footprint is 5"])
        absent = part(footprint=None)
        self.assertIn("footprint", record_kind.owes(absent))
        self.assertEqual(part_records.broken_problems(absent, written(absent)), [])

    def test_a_problem_that_merely_names_an_owed_key_is_still_broken(self):
        placeholder = part(footprint=None, footprint_placeholder=True)
        self.assertIn("footprint", record_kind.owes(placeholder))
        self.assertTrue(any(p.startswith("footprint_placeholder is set")
                            for p in part_records.broken_problems(placeholder, written(placeholder))))
        no_needs = part(simulation={"wokwi": "x"})
        del no_needs["needs"]
        self.assertIn("needs", record_kind.owes(no_needs))
        self.assertTrue(any(p.startswith("simulation needs wokwi")
                            for p in part_records.broken_problems(no_needs, written(no_needs))))

    def test_a_malformed_board_is_named_broken_never_a_traceback(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "other7"
        (other / "boards").mkdir(parents=True)
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        (other / "boards" / "bad-board.json").write_text(json.dumps(dict(board, id="bad-board", pins=1)))
        (home / "drawer").mkdir()
        (home / "drawer" / "bad.json").write_text(json.dumps({"schema": 1, "label": "a board", "count": 1, "is": {"board": "bad-board"}}))
        (home / "projects.json").write_text(json.dumps({"other7": str(other)}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((said["envelope"], code), (1, 1))
        self.assertEqual([(b["id"], b["layer"]) for b in said["data"]["broken"]], [("bad-board", "other7")])
        self.assertIn("board definition", said["data"]["broken"][0]["problems"][0])

    def test_audit_walks_a_record_the_drawer_links_to_in_another_project(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "other7"
        (other / "parts").mkdir(parents=True)
        (other / "parts" / "y-soil.json").write_text(json.dumps({"schema": 1, "id": "y-soil", "name": "Soil probe Y", "kind": "sensor",
                                                                  "needs": [], "function": [{"does": "sense", "what": "soil-moisture"}],
                                                                  "facts": {"range": {"value": 3}}}))
        (other / "parts" / "z-silent.json").write_text(json.dumps({"schema": 1, "id": "z-silent", "name": "Mystery Z", "kind": "sensor", "needs": []}))
        (home / "drawer").mkdir()
        for entry, record_id in (("soil-probe-y", "y-soil"), ("mystery-z", "z-silent")):
            (home / "drawer" / (entry + ".json")).write_text(json.dumps({"schema": 1, "label": entry, "count": 3, "is": {"part": record_id}}))
        (home / "projects.json").write_text(json.dumps({"other7": str(other)}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual(code, 1)
        self.assertEqual([(b["id"], b["layer"]) for b in said["data"]["broken"]], [("y-soil", "other7")])
        self.assertNotIn("z-silent", said["data"]["no_function"], "another project's silent record is that project's to set")

    def test_a_pin_order_with_no_proof_owes_the_proof_and_is_not_broken(self):
        unproven = part(pin_order=["P"])
        del unproven["pin_order_proof"]
        self.assertIn("pin_order_proof", record_kind.owes(unproven))
        self.assertEqual(part_records.broken_problems(unproven, written(unproven)), [])

    def test_validate_does_not_run_the_checks_of_an_owed_key(self):
        empty = part(pin_order=["P"], pin_order_proof={}, simulation={}, body_mm={"height": 3, "verified": True, "source": "x"})
        path = written(empty)
        owed = ("pin_order_proof", "simulation", "body_mm")
        self.assertTrue(all(any(p.startswith(key) for p in part_records.validate(empty, path)) for key in owed))
        self.assertEqual(part_records.validate(empty, path, owed=owed), [])
        self.assertEqual(part_records.broken_problems(empty, path), [])
        blank = part(pin_order="")
        self.assertIn("pin_order", record_kind.owes(blank))
        self.assertEqual(part_records.broken_problems(blank, written(blank)), [], "an owed key is not type-checked")
        unordered = part(pin_order=[])
        self.assertTrue(part_records.validate(unordered, written(unordered))[0].startswith("pin_order must be"))
        self.assertEqual(part_records.validate(unordered, written(unordered), owed=("pin_order",)), [])

    def test_validate_does_not_check_an_owed_required_key(self):
        nameless = part(schema=2)
        del nameless["kind"]
        problems = part_records.validate(nameless, written(nameless))
        self.assertEqual([p[:9] for p in problems], ["schema is", "missing r"])
        self.assertEqual(part_records.validate(nameless, written(nameless), owed=("schema", "kind")), [])
        anonymous = part()
        path = written(anonymous)
        del anonymous["id"]
        self.assertTrue(any(p.startswith("id is None") for p in part_records.validate(anonymous, path)))
        self.assertEqual(part_records.broken_problems(anonymous, path), [])

    def test_a_problem_inside_a_present_list_is_broken_even_when_other_keys_are_owed(self):
        unsignalled = part(needs=[{"pin": "P", "direction": "in"}])
        self.assertIn("simulation", record_kind.owes(unsignalled))
        self.assertEqual(part_records.broken_problems(unsignalled, written(unsignalled)), ["needs[0] has no signal"])

    def test_a_pin_order_that_is_no_list_is_named_not_a_shape_line(self):
        for wrong in (5, "AB"):
            unlisted = part(pin_order=wrong, pin_order_proof={"verified": False, "source": "x"})
            self.assertEqual(part_records.broken_problems(unlisted, written(unlisted)),
                             ["pin_order is %r, but it is a list" % (wrong,)])

    def test_a_chip_record_with_no_plain_id_is_named_not_a_shape_line(self):
        anonymous = part(simulation={"wokwi": {"chip": "x", "pins": {}}})
        path = written(anonymous)
        del anonymous["id"]
        self.assertIn("missing required key 'id'", part_records.validate(anonymous, path))
        self.assertFalse(any(p.startswith("does not meet") for p in part_records.broken_problems(anonymous, path)))
        numbered = part(id=5, simulation={"wokwi": {"chip": "x", "pins": {}}})
        self.assertTrue(any(p.startswith("id is 5 but the file is named") for p in part_records.validate(numbered,
                                                                                                         path)))
        self.assertFalse(any(p.startswith("does not meet") for p in part_records.broken_problems(numbered, path)))

    def test_a_value_of_the_wrong_type_is_named_not_a_shape_line(self):
        cited = {"value": 1, "verified": True, "source": "s", "cites": {"document": ["x"]}}
        wrong = [({"needs": ["a"]}, "needs[0] is 'a'"), ({"power": ["a"]}, "power[0] is 'a'"),
                 ({"unused_pins": ["a"]}, "unused_pins[0] is 'a'"), ({"needs": 5}, "needs is 5"),
                 ({"power": {"a": 1}}, "power is {'a': 1}"), ({"documents": ["a"]}, "documents is ['a']"),
                 ({"pin_order": [["a"]]}, "pin_order[0] is ['a']"), ({"facts": 5}, "facts is 5"),
                 ({"facts": {"module_has_i2c_pullups": "x"}}, "facts.module_has_i2c_pullups is 'x'"),
                 ({"host_parts": 5}, "host_parts is 5"), ({"host_parts": ["a"]}, "host_parts[0] is 'a'"),
                 ({"sourcing": 5}, "sourcing is 5"),
                 ({"needs": [{"signal": "S", "pin": ["a"], "direction": "in"}]}, "needs[0].pin is ['a']"),
                 ({"needs": [{"signal": "S", "pin": "P", "bus": ["i2c"]}]}, "needs[0].bus is ['i2c']"),
                 ({"needs": [{"signal": "S", "pin": "P", "needs": 5}]}, "needs[0].needs is 5"),
                 ({"facts": {"x": cited}}, "facts.x cites ['x']"),
                 ({"power": [{"rail": "m", "direction": "out"}, {"rail": "m", "direction": "out"}]}, "power[0] has no pin"),
                 ({"power": [{"pin": "V", "rail": ["m"], "direction": "out"}]}, "power[0] rail is ['m']"),
                 ({"needs": [None]}, "needs[0] is None, but it is an object"), ({"power": [None]}, "power[0] is None"),
                 ({"unused_pins": [None]}, "unused_pins[0] is None"), ({"host_parts": [None]}, "host_parts[0] is None"),
                 ({"needs": [{"signal": "S", "bus": "i2c"}]}, "needs[0] has no pin"),
                 ({"needs": [{"signal": "S", "pin": "P", "needs": [None]}]}, "needs[0].needs[0] is None, but it is a string")]
        for overrides, named in wrong:
            with self.subTest(named):
                record = part(**overrides)
                problems = part_records.broken_problems(record, written(record))
                self.assertTrue(any(p.startswith(named) for p in problems), problems)
                self.assertFalse(any(p.startswith("does not meet") for p in problems), problems)

    def test_a_wrong_pin_order_is_named_when_its_proof_is_owed(self):
        unlisted = part(pin_order=5)
        del unlisted["pin_order_proof"]
        self.assertIn("pin_order_proof", record_kind.owes(unlisted))
        self.assertEqual(part_records.broken_problems(unlisted, written(unlisted)),
                         ["pin_order is 5, but it is a list"])

    def test_audit_walks_every_layer_names_what_says_nothing_and_exits_1_only_on_broken(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-draft.json").write_text(json.dumps({"schema": 1, "id": "x-draft", "name": "A probe", "kind": "sensor"}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((said["status"], code), ("ok", 0), "a draft that owes facts is not a problem")
        self.assertEqual(said["data"]["layers"]["catalog"], {"current": 0, "owed": 1, "broken": 0})
        self.assertIn("x-draft", said["data"]["no_function"])
        (home / "catalog" / "x-bad.json").write_text(json.dumps({"schema": 2, "id": "x-bad", "name": "B", "kind": "rtc"}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertEqual([b["id"] for b in said["data"]["broken"]], ["x-bad"])

    def test_audit_says_every_problem_of_a_broken_record_once(self):
        # The refuter, RF-1: its line kept three problems, and the printer took the record's id for all of them.
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "x-many.json").write_text(json.dumps({"schema": 1, "id": "x-many", "name": "M", "kind": "sensor",
                                                                  "needs": [{"signal": s} for s in "ABCD"]}))
        with in_store(home):
            text, code = run_text(["--audit", "--project", str(project)])
        self.assertEqual((code, text.count("needs[3] has no pin")), (1, 1), text)

    def test_audit_s_hint_names_the_project_it_walked(self):
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "x-local.json").write_text(json.dumps({"schema": 1, "id": "x-local", "name": "A probe", "kind": "sensor"}))
        out = io.StringIO()
        with in_store(home), contextlib.redirect_stdout(out):
            parts.main(["--audit", "--project", str(project)])
        self.assertIn("--function-set <part> <file> --project %s: x-local" % project.resolve(), out.getvalue())

    def test_audit_calls_a_record_whose_id_is_no_plain_key_broken(self):
        # P87's attribute half: a record whose file is named with a quote is found by every walk of the store
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        (home / "catalog" / 'x"y.json').write_text(json.dumps(dict(led, id='x"y')))
        with in_store(home):
            said, _ = run_json(["--audit"])
        broken = {row["id"]: row["problems"] for row in said["data"]["broken"]}
        self.assertTrue(broken.get('x"y', [""])[0].startswith("id is 'x\"y', but an id is a plain key"), said["data"]["broken"])

    @board_missing("physical.header")
    def test_audit_says_a_board_whose_file_has_no_header_geometry_stops_at_the_footprint(self):
        # C-7 (the council on PR #98): the XIAO was counted current, and the chain stops at its footprint stage all the same
        out = io.StringIO()
        with in_store(Path(tempfile.mkdtemp())):
            said, code = run_json(["--audit"])
            with contextlib.redirect_stdout(out):
                parts.main(["--audit"])
        self.assertEqual((code, said["data"]["stops_at_footprint"]), (0, [{
            "id": "xiao-esp32-c6", "layer": "library",
            "stops_why": "xiao-esp32-c6 cannot have a footprint generated — these are not recorded, and none of them can be derived "
                         "from the rest:\n  physical.header (no header geometry at all)"}]))
        self.assertIn("  xiao-esp32-c6 (library) stops at the footprint stage (P121): its board file lacks physical.header\n",
                      out.getvalue())

    def test_audit_names_a_drawer_link_to_a_record_nobody_has(self):
        home = Path(tempfile.mkdtemp())
        (home / "drawer").mkdir()
        (home / "drawer" / "x.json").write_text(json.dumps({"schema": 1, "label": "x", "count": 1, "is": {"part": "gone-part"}}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((code, said["data"]["dangling"]), (1, ["x"]))


class TheGoalOperationsRunOnTheCoreTest(unittest.TestCase):
    """P707 (N19) and P726: `parts.py --audit` and the six goal flags run design Operations through `run_cli`, with parts.py's
    envelope: eleven keys on every path, `tool` parts, paging with --from, a store it cannot read as could-not-run, never a
    traceback, and the flags picked as argparse picks them (an exact flag first, then a prefix that fits one flag)."""

    def test_an_abbreviation_runs_the_audit_and_the_envelope_is_parts_py_s(self):
        with in_store(Path(tempfile.mkdtemp())):
            said, code = run_json(["--aud"])
        self.assertEqual((code, sorted(said), said["tool"], said["op"]), (0, ENVELOPE_KEYS, "parts", "audit"))

    def test_a_negative_from_is_a_bad_argument_with_every_key(self):
        with in_store(Path(tempfile.mkdtemp())):
            said, code = run_json(["--audit", "--from", "-1"])
        self.assertEqual((code, sorted(said), said["unchecked"][0]["code"]), (2, ENVELOPE_KEYS, "bad_argument"))

    def test_the_owed_rows_page_from_the_item_asked_for(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        for n in range(25):
            (home / "catalog" / ("x-%02d.json" % n)).write_text(json.dumps({"schema": 1, "id": "x-%02d" % n, "name": "A probe %d" % n, "kind": "sensor"}))
        with in_store(home):
            said, _ = run_json(["--audit"])
            later, _ = run_json(["--audit", "--from", "20"])
        self.assertEqual((len(said["data"]["owed"]), said["truncated"]["total"], said["truncated"]["next"]["argv"][:3]), (20, 25, ["--audit", "--from", "20"]))
        self.assertEqual(([o["id"] for o in later["data"]["owed"]][:1], later["truncated"]["next"]), (["x-20"], None))

    def test_a_drawer_file_that_is_not_json_is_could_not_run_with_the_store_s_code(self):
        home = Path(tempfile.mkdtemp())
        (home / "drawer").mkdir()
        (home / "drawer" / "bad.json").write_text("{not json")
        err = io.StringIO()
        with in_store(home):
            said, code = run_json(["--audit"])
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(err):
                text_code = parts.main(["--audit"])
        self.assertEqual((code, said["status"], said["unchecked"][0]["code"], said["problems"]), (2, "could-not-run", "record_file_broken", []))
        self.assertEqual((text_code, out.getvalue()), (2, ""))
        self.assertTrue(err.getvalue().startswith("parts.py: %s is not JSON" % (home / "drawer" / "bad.json")), err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_a_control_character_in_a_record_s_name_does_not_reach_the_terminal(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x\x1b[31mred.json").write_text(json.dumps({"schema": 1, "id": "x\x1b[31mred", "name": "R", "kind": "sensor"}))
        with in_store(home):
            text, _ = run_text(["--audit"])
        self.assertIn("BROKEN x?[31mred", text)
        self.assertNotIn("\x1b", text)

    def test_a_broken_record_and_a_dangling_entry_are_problems_with_codes(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-bad.json").write_text(json.dumps({"schema": 2, "id": "x-bad", "name": "B", "kind": "rtc"}))
        (home / "drawer").mkdir()
        (home / "drawer" / "x.json").write_text(json.dumps({"schema": 1, "label": "x", "count": 1, "is": {"part": "gone-part"}}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual((code, [(p["subject"], p["code"]) for p in said["problems"]]), (1, [("x-bad", "record_file_broken"), ("x", "drawer_entry_dangling")]))

    def test_audit_s_help_lists_its_own_arguments_alone(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(err):
            parts.main(["--audit", "--help"])
        self.assertIn("--from START", err.getvalue())
        self.assertNotIn("--list", err.getvalue())

    def test_each_describe_row_and_its_operation_agree(self):
        # P726 PR 3: --describe reflects over the registry, so a row cannot drift from its class; every entry has a summary
        from spark.core.describe_operations import effect_words_of, summary_of
        said, code = run_json(["--describe"])
        rows = {row["op"]: row for row in said["data"]["operations"]}
        self.assertEqual((code, list(rows)), (0, list(parts.OPERATIONS)))
        for op, operation in parts.OPERATIONS.items():
            with self.subTest(op=op):
                self.assertIsNotNone(summary_of(operation))
                self.assertEqual((rows[op]["flag"], rows[op]["summary"], rows[op]["effects"]), ("--" + op, summary_of(operation), effect_words_of(operation)))
                self.assertEqual(sorted(rows[op]["arguments"]), sorted(a.dest for a in operation.arguments if a.dest != "json" and not (a.kind is bool and "--" + op in a.flags)))
                self.assertEqual(rows[op]["data"], list(operation.data_keys))
        self.assertEqual(rows["fetch"]["effects"], ["network", "writes"])
        from spark.design import design_operations
        from spark.sourcing import sourcing_operations
        self.assertEqual(set(parts.OPERATIONS), (set(design_operations.OPERATIONS) | set(sourcing_operations.OPERATIONS) | {"needs-drop", "describe"}) - {"list-boards"})
        self.assertEqual(rows["fact-set"]["arguments"]["part_and_facts"]["prefixItems"][1], {"type": ["object", "array"]})

    def test_each_part_operation_s_help_lists_its_own_arguments_alone(self):
        # P726 PR 2: `parts.py --list --help` is ListParts' parser, not the whole CLI's
        out = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(out):
            parts.main(["--list", "--help"])
        self.assertIn("--from N", out.getvalue())
        self.assertIn("--project PROJECT", out.getvalue())
        self.assertNotIn("--kind", out.getvalue())
        out = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(out):
            parts.main(["--step", "p", "S", "--help"])
        self.assertIn("--step PROJECT STEP", out.getvalue())
        said, code = run_json(["--list", "--dry-run"])
        self.assertEqual((code, said["op"], said["unchecked"][0]["code"]), (2, "list", "bad_argument"))

    def test_a_cited_url_that_does_not_answer_is_a_problem_on_the_url_and_nothing_is_kept(self):
        # P722: a failed download said "cites no URL" with exit 0; now the URL is named, with url_unreachable, exit 1
        home = Path(tempfile.mkdtemp()); project = Path(tempfile.mkdtemp()); (project / "parts").mkdir()
        (project / "parts" / "x-led.json").write_text(json.dumps(part("x-led", sources=["http://127.0.0.1:9/ds.pdf"], documents={})))
        with in_store(home):
            said, code = run_json(["--fetch", "x-led", "--project", str(project)])
        self.assertEqual((code, said["data"]["failed"], said["problems"][0]["subject"], said["problems"][0]["code"]),
                         (1, ["http://127.0.0.1:9/ds.pdf"], "http://127.0.0.1:9/ds.pdf", "url_unreachable"))
        self.assertEqual(said["data"]["documents"], {})

    def test_a_part_refusal_on_a_payload_flag_names_the_part_alone(self):
        # P726 PR 3: the loaded payload is a token of the flag's value too, and never enters the subject
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text('[{"does": "indicate", "what": "a lamp"}]')
        said, code = run_json(["--function-set", "led-red-5mm", str(given)])
        self.assertEqual((code, said["problems"][0]["subject"]), (1, "led-red-5mm"))

    def test_a_part_nobody_has_is_a_problem_on_every_id_the_flag_named(self):
        # P726 PR 2: PartOperation.answer_refusal keeps parts._part_problem's rule
        said, code = run_json(["--signals", "led-red-5mm", "nosuch"])
        self.assertEqual((code, said["problems"][0]["subject"], said["problems"][0]["code"]), (1, "led-red-5mm nosuch", "no_such_part"))

    def test_a_listing_on_the_core_refuses_a_negative_start_and_takes_zero(self):
        with in_store(Path(tempfile.mkdtemp())):
            refused, code = run_json(["--catalog", "--from", "-1"])
            taken, taken_code = run_json(["--catalog", "--from", "0"])
        self.assertEqual((code, refused["unchecked"][0]["code"], refused["unchecked"][0]["fix"]),
                         (2, "bad_argument", "--from takes a whole number from 0 up"))
        self.assertEqual((taken_code, taken["status"]), (0, "ok"))

    def test_the_refusals_the_part_operations_word_carry_a_code(self):
        project = Path(tempfile.mkdtemp())
        with in_store(Path(tempfile.mkdtemp())):
            for argv, word in ((["--promote", "x"], "bad_argument"), (["--step", str(project), "nap"], "bad_argument"),
                               (["--skeleton", "x", "--project", str(project)], "bad_argument"),
                               (["--keep", str(project / "missing.pdf")], "file_refused")):
                with self.subTest(argv=argv):
                    said, code = run_json(argv)
                    self.assertEqual((code, said["unchecked"][0]["code"]), (2, word))

    def test_every_write_operation_narrows_its_effects_on_a_dry_run(self):
        from spark.core.operation import READS, WRITES
        from spark.design import design_operations
        from spark.sourcing import sourcing_operations
        writers = [op for op, cls in {**design_operations.OPERATIONS, **sourcing_operations.OPERATIONS}.items() if WRITES in cls.effects]
        self.assertEqual(sorted(writers), ["drawer-import", "drawer-set", "fact-set", "fetch", "function-set", "keep", "needs-set", "pick", "promote",
                                           "requirements", "skeleton", "step"])
        for op in writers:
            with self.subTest(op=op):
                operation = sourcing_operations.OPERATIONS.get(op, design_operations.OPERATIONS.get(op))()
                self.assertEqual(operation.effects_of({"dry_run": True}), (READS,))
                self.assertEqual(operation.effects_of({"dry_run": False}), operation.effects)

    def test_two_labels_both_reach_the_datasheet_reader(self):
        # P726 PR 2: Argument.repeats; nargs="+" would keep the last --label alone
        from spark.core.cli import HelpText, parser_for
        from spark.sourcing import read_datasheet
        parsed = vars(parser_for(HelpText("parts.py", "", ""), read_datasheet.ReadDatasheet()).parse_args(
            ["--read", "x.pdf", "--want", "a", "b", "--label", "a=x| Y", "--label", "b=z"]))
        self.assertEqual((parsed["datasheet"], parsed["wanted"], parsed["labels"]), ("x.pdf", ["a", "b"], ["a=x| Y", "b=z"]))
        self.assertEqual(read_datasheet.words_by_fact(parsed["labels"]), {"a": ["x", "y"], "b": ["z"]})
        self.assertEqual(read_datasheet.words_by_fact(None), {})

    def test_an_exact_flag_wins_over_the_flags_it_is_a_prefix_of(self):
        project = Path(tempfile.mkdtemp())
        with in_store(Path(tempfile.mkdtemp())):
            need, _ = run_json(["--need", "unobtainium"])
            needs, _ = run_json(["--needs", str(project)])
            equals, _ = run_json(["--match=" + str(project)])
            ambiguous, code = run_json(["--ne", str(project)])
        self.assertEqual((need["op"], needs["op"], equals["op"]), ("need", "needs", "match"))
        self.assertEqual((code, ambiguous["status"], ambiguous["unchecked"][0]["sentence"][:22]), (2, "could-not-run", "unrecognized arguments"))  # P726 PR 3
        with in_store(Path(tempfile.mkdtemp())):  # P726 PR 2: the fifteen join the rule
            show, show_code = run_json(["--sh", "nosuch"])
            promote_or_project, code = run_json(["--pro", "x"])
        self.assertEqual((show["op"], show_code, code, promote_or_project["unchecked"][0]["sentence"][:16]), ("show", 1, 2, "ambiguous option"))  # PromoteRecord's own parser

    def test_a_unique_prefix_picks_its_operation_as_argparse_did(self):
        project = Path(tempfile.mkdtemp())
        with in_store(Path(tempfile.mkdtemp())):
            said, _ = run_json(["--req", str(project)])
            tally, _ = run_json(["--tal", str(project)])
        self.assertEqual((said["op"], tally["op"]), ("requirements", "tally"))

    def test_a_flag_the_operation_does_not_take_is_a_bad_argument_with_every_key(self):
        project = Path(tempfile.mkdtemp())
        with in_store(Path(tempfile.mkdtemp())):
            said, code = run_json(["--needs", str(project), "--project", str(project)])
            start, start_code = run_json(["--match", str(project), "--from", "-1"])
        self.assertEqual((code, sorted(said), said["unchecked"][0]["code"]), (2, ENVELOPE_KEYS, "bad_argument"))
        self.assertEqual((start_code, start["unchecked"][0]["code"], start["unchecked"][0]["fix"]), (2, "bad_argument", "--from takes a whole number from 0 up"))

    def test_the_refusals_the_goal_operations_word_carry_their_codes(self):
        project = Path(tempfile.mkdtemp())
        with in_store(Path(tempfile.mkdtemp())):
            matcher, _ = run_json(["--need", "x", "--matcher", "nosuch"])
            tally, _ = run_json(["--tally", str(project)])
            offer, offer_code = run_json(["--offer", "nothing-like-this"])
            match, _ = run_json(["--match", str(project)])
        self.assertEqual(matcher["unchecked"][0]["code"], "unknown_matcher")
        self.assertEqual(tally["unchecked"][0]["code"], "project_not_listed")
        self.assertEqual((offer_code, offer["problems"][0]["code"], offer["problems"][0]["subject"]), (1, "offer_unknown", "nothing-like-this"))
        self.assertEqual(match["unchecked"][0]["code"], "no_needs_yet")

    def test_a_needs_file_that_is_not_json_is_could_not_run_with_the_store_s_code(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / ".spark" / "needs.json").write_text("{not json")
        err = io.StringIO()
        with in_store(Path(tempfile.mkdtemp())):
            said, code = run_json(["--needs", str(project)])
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(err):
                text_code = parts.main(["--needs", str(project)])
        self.assertEqual((code, said["status"], said["unchecked"][0]["code"]), (2, "could-not-run", "record_file_broken"))
        self.assertEqual((text_code, out.getvalue()), (2, ""))
        self.assertTrue(err.getvalue().startswith("parts.py: %s is not JSON" % (project / ".spark" / "needs.json")), err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_a_needs_drop_problem_carries_the_operation_s_code(self):
        # P726: `Answer.from_result` keeps a Finding's code, so --needs-drop's items gain `code` as the six's do
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "light", "does": "indicate", "what": "status"}]}))
        with in_store(Path(tempfile.mkdtemp())):
            said, code = run_json(["--needs-drop", str(project), "nosuch"])
        self.assertEqual((code, said["problems"][0]["code"], said["problems"][0]["subject"]), (1, "need_unknown", "nosuch"))

    def test_a_goal_operation_s_help_lists_its_own_arguments_with_their_words(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(out):
            parts.main(["--match", "x", "--help"])
        self.assertIn("--match PROJECT", out.getvalue())
        self.assertIn("--from N", out.getvalue())
        self.assertNotIn("--list", out.getvalue())


if __name__ == "__main__":
    unittest.main()
