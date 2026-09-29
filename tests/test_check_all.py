"""
Proof that the runner tells four outcomes apart.

This file exists because a review loop that ran one of seven checks looked exactly like a review
loop that ran all seven: green, fast, and reassuring. The runner's whole job is to make the
difference visible, so what is tested here is mostly its honesty rather than its findings — the
individual checks have their own suites.

The outcome that matters is the one usually missing. "I was not asked" and "I looked and found
nothing" are both silent, and only one of them is reassuring. So they are separate statuses,
they render differently, and only one of them can sink the exit code.

    python3 -m unittest discover -s tests
"""

import argparse
import json
import sys
import tempfile
import unittest
from unittest import mock
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_all  # noqa: E402
import check_footprints  # noqa: E402
import design  # noqa: E402


def written(name, payload):
    path = Path(tempfile.mkdtemp()) / name
    path.write_text(json.dumps(payload) if not isinstance(payload, str) else payload)
    return str(path)


class NothingAskedForTest(unittest.TestCase):
    def test_with_no_inputs_every_check_is_skipped_and_none_claims_to_have_looked(self):
        results = check_all.run({})
        self.assertTrue(results, "the runner knows about no checks at all")
        self.assertTrue(all(r["status"] == check_all.SKIPPED for r in results))
        self.assertTrue(all(not r.get("problems") for r in results))

    def test_skipped_says_which_input_was_missing(self):
        results = check_all.run({})
        self.assertTrue(all("not given" in r["reason"] for r in results))

    def test_asking_for_nothing_at_all_does_not_exit_zero(self):
        # This asserted EXIT_OK, on the reasoning that skipping is a choice and a choice is not a
        # failure. That holds when SOME checks were skipped and it is wrong when all of them
        # were: the exit code then answers a question nobody asked, and "everything is in step"
        # is the most expensive possible way to be wrong. The module docstring carries the
        # decision; this pins it.
        self.assertEqual(check_all.main([]), check_all.EXIT_COULD_NOT_RUN)

    def test_asking_for_some_and_getting_a_clean_answer_still_exits_zero(self):
        # The other half of the same decision, so the fix above cannot quietly grow into
        # "any skipped check fails the run", which would make the runner useless piecemeal.
        clean = [{"check": "a", "status": check_all.OK, "problems": [], "unchecked": []},
                 {"check": "b", "status": check_all.SKIPPED, "reason": "not given circuit"}]
        self.assertEqual(check_all.verdict(clean), check_all.OK)

    def test_but_the_rendering_says_so_out_loud(self):
        rendered = check_all.render(check_all.run({}))
        self.assertIn("not asked for", rendered)
        # It said "nothing found by the checks that ran" — true, useless, and read as a clean
        # bill when the number of checks that ran was zero.
        self.assertIn("nothing completed", rendered)
        self.assertIn("says nothing about the board", rendered)


def a_header_drilled_too_small():
    """A 6-pin 2.54 mm header on a 0.9 mm drill — the defect check_footprints exists for."""
    return [{"type": "source_component", "source_component_id": "J1", "name": "J1"},
            {"type": "pcb_component", "pcb_component_id": "pcb_J1", "source_component_id": "J1"}
            ] + [{"type": "pcb_plated_hole", "pcb_component_id": "pcb_J1",
                  "hole_diameter": 0.9, "outer_diameter": 1.4, "x": i * 2.54, "y": 0.0}
                 for i in range(6)]


class EveryCheckActuallyRunsThroughTheRunnerTest(unittest.TestCase):
    """
    The rung-1 rule — every check must have an input that makes it answer — applied to the RUNNER.

    The runner was exempt from it, and that is exactly where the defect was. `check_all.py` called
    `check_design.check()`, a function that has never existed, so the plugin's flagship check had
    never once run through the aggregator. The AttributeError became `could-not-run`, which reads
    as a bad environment rather than a broken plugin, and the test written to catch a check nobody
    invokes asserted that the string `load("check_design")` appeared in this file's SOURCE. It
    verified the check was named, not that it ran, and it was green for the whole life of the bug.

    So each check below is RUN, through the runner, with an input whose answer is known. The
    per-check suites prove each check bites; this proves the seam between them is connected. The
    coverage guard at the end is what stops a new check being added without one.
    """

    @classmethod
    def setUpClass(cls):
        tmp = Path(tempfile.mkdtemp())
        board_file = str(ROOT / "boards" / "firebeetle2-esp32s3.json")

        no_bom = tmp / "nobom.zip"
        zipfile.ZipFile(no_bom, "w").writestr("readme.txt", "a package with no bill of materials")

        cls.cases = {
            # check name: (inputs, the status it must come back with, why)
            "pin-capability": (
                {"design": written("adc.design.json", {
                    "board": "firebeetle2-esp32s3",
                    "parts": [{"ref": "Sense",
                               "pins": [{"signal": "SENSE", "pin": "D6", "needs": ["adc"]}]}]})},
                check_all.PROBLEMS, "an analogue input on a pin with no ADC"),
            "vendor-truth": (
                {"boards": [written("active.json", {"board": "xiao-esp32-c6"})]},
                check_all.COULD_NOT_RUN, "a selection file, which carries no vendor header"),
            "buildability": (
                {"circuit": written("bad-drill.json", a_header_drilled_too_small())},
                check_all.PROBLEMS, "a header drilled too small for its own pins"),
            "the-order": (
                {"package": str(no_bom)},
                check_all.COULD_NOT_RUN, "a fab package with no bom.csv (raises SystemExit)"),
            "physics": (
                {"circuit": written("ok.json", a_header_drilled_too_small()),
                 "rules": written("rules.json", {})},
                # Was OK, "a real netlist and no rules to break". That expectation WAS the bug:
                # an empty rules file is what `spark init` writes, so every new project got
                # `[ok  ] physics` about a board whose rails nothing had described. Three of the
                # four rules had not run.
                check_all.COULD_NOT_RUN, "a real netlist and a rules file stating no rails"),
            "rules-vs-netlist": (
                {"circuit": written("ok2.json", a_header_drilled_too_small()),
                 "rules": written("rules2.json", {})},
                check_all.OK, "a real netlist and no rules to break"),
            "firmware-vs-board": (
                {"firmware": written("config.py", "PIN_NOWHERE = 99\n"),
                 "board_file": board_file},
                check_all.PROBLEMS, "a firmware driving a pin the board does not bring out"),
        }

    def test_each_check_answers_what_it_is_given(self):
        for check in check_all.CHECKS:
            inputs, expected, why = self.cases[check.name]
            with self.subTest(check=check.name, given=why):
                result = check.run(inputs)
                self.assertEqual(
                    result["status"], expected,
                    "%s, given %s, answered %s: %s"
                    % (check.name, why, result["status"],
                       result.get("unchecked") or result.get("problems")))

    def test_no_check_is_broken_at_the_seam(self):
        # The narrow version of the defect, stated on its own so a regression names itself: a
        # check handed exactly what it asked for must never come back "I could not look" for a
        # reason that is really "this plugin does not work".
        for check in check_all.CHECKS:
            inputs, expected, why = self.cases[check.name]
            if expected == check_all.COULD_NOT_RUN:
                continue  # these cases are deliberately unanswerable; see `why`
            with self.subTest(check=check.name):
                broken = [u for u in check.run(inputs).get("unchecked", [])
                          if "Error" in u or "Exception" in u]
                self.assertEqual(broken, [], "%s raised inside the runner" % check.name)

    def test_every_check_in_the_runner_has_a_case_here(self):
        # The mechanism. Without it, adding a check silently adds an untested one — which is the
        # shape of the original bug.
        self.assertEqual(sorted(self.cases), sorted(c.name for c in check_all.CHECKS))


class OkIsUnreachableWhileAnythingWentUncheckedTest(unittest.TestCase):
    """
    Two checks folded "I could not look" into a notes field and returned `ok` anyway. Deciding the
    status in one place is what makes that impossible rather than merely discouraged.
    """

    def test_an_unchecked_entry_alone_is_not_ok(self):
        self.assertEqual(check_all.answer(unchecked=["no cached vendor header"])["status"],
                         check_all.COULD_NOT_RUN)

    def test_an_unmeasured_note_alone_is_still_ok(self):
        # The distinction that was lost: `unmeasured` is a real finding about the BOARD, and the
        # check did its job. `unchecked` is a property of the RUN. Conflating them cost a tick.
        self.assertEqual(check_all.answer(unmeasured=["GND: nobody sized the pour"])["status"],
                         check_all.OK)

    def test_nothing_at_all_is_ok(self):
        self.assertEqual(check_all.answer()["status"], check_all.OK)

    def test_a_check_that_says_could_not_run_without_saying_why_still_sinks_the_verdict(self):
        # `verdict` reads both the status and the field, because reading one trusts every call
        # site to have filled in the other — and the reason this function exists is that a call
        # site did not. No check produces this shape today; the next one written might.
        self.assertEqual(
            check_all.verdict([{"check": "a", "status": check_all.COULD_NOT_RUN,
                                "problems": [], "unchecked": []}]),
            check_all.COULD_NOT_RUN)

    def test_the_verdict_is_could_not_run_if_any_check_could_not_look(self):
        results = [{"check": "a", "status": check_all.OK, "problems": [], "unchecked": []},
                   {"check": "b", "status": check_all.COULD_NOT_RUN, "problems": [],
                    "unchecked": ["no cached header"]}]
        self.assertEqual(check_all.verdict(results), check_all.COULD_NOT_RUN)

    def test_an_empty_netlist_is_not_a_clean_board(self):
        # A build that failed part way leaves `[]`. Every check downstream then examined nothing,
        # found nothing, and said ok.
        results = check_all.run({"circuit": written("empty.json", []),
                                 "rules": written("norules.json", {})})
        looked = [r for r in results if r["status"] != check_all.SKIPPED]
        self.assertTrue(looked, "no check even tried")
        self.assertTrue(all(r["status"] == check_all.COULD_NOT_RUN for r in looked),
                        "a check reported on a board that was never built")
        self.assertEqual(check_all.verdict(results), check_all.COULD_NOT_RUN)


class OneArgumentFindsTheInputsTest(unittest.TestCase):
    """
    `--project` exists because the command a skill documented named five paths and got two wrong:
    it globbed `boards/*.json`, which matches the selection file rather than a board definition,
    and it never passed `--design` or `--firmware` — so the flagship check was permanently
    unasked while the review called itself complete.

    Discovery is only an improvement if it cannot quietly pick the wrong file, which is what the
    two rules here are about.
    """

    def _project(self, *relative_paths):
        root = Path(tempfile.mkdtemp())
        for relative in relative_paths:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]")
        return root

    def test_it_finds_what_a_usual_layout_holds(self):
        root = self._project("dist/board/circuit.json", ".spark/rules.json", "board-gerbers.zip")
        found, _, _ = check_all.discover(root)
        self.assertEqual(found["circuit"], str(root / "dist/board/circuit.json"))
        self.assertEqual(found["rules"], str(root / ".spark/rules.json"))
        self.assertEqual(found["package"], str(root / "board-gerbers.zip"))

    def test_two_candidates_are_ambiguous_rather_than_a_coin_toss(self):
        # Two fab packages in one directory is exactly when checking the wrong one costs money.
        root = self._project("old-gerbers.zip", "new-gerbers.zip")
        found, notes, _ = check_all.discover(root)
        self.assertNotIn("package", found)
        self.assertTrue(any("AMBIGUOUS" in note for note in notes), notes)

    def test_what_is_missing_says_where_it_looked(self):
        found, notes, _ = check_all.discover(self._project())
        self.assertNotIn("circuit", found)
        self.assertTrue(any("circuit" in n and "dist/board/circuit.json" in n for n in notes))

    def test_every_resolved_path_is_reported(self):
        # The one way discovery is worse than five explicit paths is by silently picking up a
        # stale artifact, so nothing may be used without being named.
        root = self._project("dist/board/circuit.json", ".spark/rules.json")
        found, notes, _ = check_all.discover(root)
        for name in found:
            with self.subTest(input=name):
                self.assertTrue(any(note.startswith(name) for note in notes))

    def test_an_explicit_flag_beats_the_convention(self):
        root = self._project("dist/board/circuit.json", ".spark/rules.json")
        chosen = written("chosen.json", [])
        args = argparse.Namespace(project=str(root), circuit=chosen, rules=None, design=None,
                                  board=None, board_file=None, firmware=None, boards=None,
                                  package=None, json=False)
        inputs, _, _ = check_all.inputs_for(args)
        self.assertEqual(inputs["circuit"], chosen, "the convention overrode an explicit path")
        self.assertEqual(inputs["rules"], str(root / ".spark/rules.json"),
                         "an input nobody named should still come from the project")

    def test_without_a_project_nothing_is_discovered(self):
        args = argparse.Namespace(project=None, circuit="given.json", json=False)
        inputs, resolved, ambiguous = check_all.inputs_for(args)
        self.assertEqual(resolved, [])
        self.assertEqual(ambiguous, {})
        self.assertEqual(inputs["circuit"], "given.json")


class PlaceholdersReachTheCheckerTest(unittest.TestCase):
    """
    Nothing about a part record survives into circuit.json, so the checker cannot learn from the
    netlist which footprints are stand-ins. `check_all` knows the project, and derives the list
    with the generator's own functions rather than re-deriving the name.
    """

    @staticmethod
    def _project(placeholder):
        root = Path(tempfile.mkdtemp())
        (root / "parts").mkdir()
        record = {"schema": 1, "id": "inlet", "name": "inlet", "kind": "connector", "needs": [],
                  # jst_ph_2 has TWO pads, and the contract checks pin_order against the
                  # footprint's pad count. The first version of this fixture named one pad and
                  # was refused — by the rule written for exactly that mistake.
                  "power": [{"pin": "VCC", "rail": "logic", "direction": "in"},
                            {"pin": "GND", "rail": "ground", "direction": "in"}],
                  "pin_order": ["VCC", "GND"], "footprint": "jst_ph_2",
                  "body_mm": {"width": 5, "height": 5, "verified": True, "source": "t"}}
        if placeholder:
            record.update(footprint_placeholder=True, footprint_note="stands in")
        (root / "parts" / "inlet.json").write_text(json.dumps(record))
        (root / "car.requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3",
             "parts": [{"part": "inlet", "name": "PackIn"}]}))
        return root

    def test_a_placeholder_in_the_project_is_found_by_its_instance_name(self):
        self.assertEqual(check_all.placeholder_components_in(self._project(True)), (("PackIn",), []))

    def test_a_real_footprint_yields_nothing(self):
        self.assertEqual(check_all.placeholder_components_in(self._project(False)), ((), []))

    def test_no_project_yields_nothing(self):
        self.assertEqual(check_all.placeholder_components_in(None), ((), []))

    def test_buildability_actually_uses_the_list(self):
        """
        The integration, not the helper. A mutation that made `Buildability.call` pass an empty
        tuple escaped every test above, because every test above exercised the derivation and
        none exercised the check that consumes it — the same way "the generator stops sizing
        traces" escaped a suite that tested the width arithmetic thoroughly.
        """
        root = self._project(True)
        # a netlist in which PackIn has a ring under the process minimum: measured, this is a
        # problem; skipped as a placeholder, it is a could-not-run.
        circuit = [{"type": "source_component", "source_component_id": "c", "name": "PackIn"},
                   {"type": "pcb_component", "pcb_component_id": "pcb_c", "source_component_id": "c"}]
        circuit += [{"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_c",
                     "hole_width": 1.6, "hole_height": 0.75, "outer_width": 2.4,
                     "outer_height": 1.2, "x": i * 2.0, "y": 0.0} for i in range(2)]
        (root / "circuit.json").write_text(json.dumps(circuit))
        check = next(c for c in check_all.CHECKS if c.name == "buildability")
        result = check.run({"circuit": str(root / "circuit.json"), "project": str(root)})
        self.assertEqual(result["status"], check_all.COULD_NOT_RUN, result)

    def test_and_without_a_project_the_same_netlist_is_measured(self):
        # The control for the test above: same geometry, no way to know it is a stand-in.
        root = self._project(True)
        circuit = [{"type": "source_component", "source_component_id": "c", "name": "PackIn"},
                   {"type": "pcb_component", "pcb_component_id": "pcb_c", "source_component_id": "c"}]
        circuit += [{"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_c",
                     "hole_width": 1.6, "hole_height": 0.75, "outer_width": 2.4,
                     "outer_height": 1.2, "x": i * 2.0, "y": 0.0} for i in range(2)]
        (root / "circuit.json").write_text(json.dumps(circuit))
        check = next(c for c in check_all.CHECKS if c.name == "buildability")
        result = check.run({"circuit": str(root / "circuit.json")})
        self.assertEqual(result["status"], check_all.PROBLEMS, result)

    def test_a_broken_requirements_file_is_reported_and_the_others_still_count(self):
        """
        The decision changed on 2026-09-29 (audit A4). Before, one unreadable file emptied the
        whole list under `except Exception` and the check measured every stand-in as if it were
        real, silently. Now each file is read on its own: the good one's placeholder is still
        known, and the broken one is a note the check reports — a stand-in the check did not
        learn about is measured as real, which the reader has to be told.
        """
        root = self._project(True)
        (root / "broken.requirements.json").write_text("{not json")
        names, notes = check_all.placeholder_components_in(root)
        self.assertEqual(names, ("PackIn",))
        self.assertEqual(len(notes), 1, notes)
        self.assertIn("broken.requirements.json", notes[0])

    def test_buildability_reports_the_file_it_could_not_read(self):
        # The integration: the note reaches the check's answer, not just the helper's return.
        root = self._project(True)
        (root / "broken.requirements.json").write_text("{not json")
        circuit = [{"type": "source_component", "source_component_id": "c", "name": "PackIn"},
                   {"type": "pcb_component", "pcb_component_id": "pcb_c", "source_component_id": "c"}]
        (root / "circuit.json").write_text(json.dumps(circuit))
        check = next(c for c in check_all.CHECKS if c.name == "buildability")
        result = check.run({"circuit": str(root / "circuit.json"), "project": str(root)})
        self.assertNotEqual(result["status"], check_all.OK, result)
        self.assertIn("broken.requirements.json", json.dumps(result))


class TwoOfSomethingIsNotNothingTest(unittest.TestCase):
    """
    A second board silently switched six of seven checks off and still reported `ok`.

    Found on a two-board project — an RC car and its remote, in one directory. The `circuit` glob
    matched twice, `discover` declined to choose (right) and then did not record the ambiguity
    (wrong), so the input was simply unset. Every check needing it reported SKIPPED — "not given
    circuit" — which the verdict reads as "not asked for", and exit was **0** with a top-level
    `"status": "ok"`.

    That is this tool's founding rule broken at the top level: a check that could not look read as
    a check nobody wanted. "There is no circuit" and "there are two and I refused to pick" are
    different sentences, and only the first is a legitimate skip.
    """

    @staticmethod
    def check():
        return check_all.Check("demo", ["circuit"], "a demo check")

    def test_an_ambiguous_input_is_could_not_run_not_skipped(self):
        result = self.check().run({}, {"circuit": ["dist/a.json", "dist/b.json"]})
        self.assertEqual(result["status"], check_all.COULD_NOT_RUN)

    def test_it_names_both_candidates_and_how_to_choose(self):
        # A could-not-run nobody can act on is only marginally better than a false pass.
        result = self.check().run({}, {"circuit": ["dist/a.json", "dist/b.json"]})
        self.assertIn("dist/a.json", result["reason"])
        self.assertIn("dist/b.json", result["reason"])
        self.assertIn("--circuit", result["reason"])

    def test_a_genuinely_absent_input_is_still_skipped(self):
        # The distinction has to cut both ways, or every project without firmware reports a
        # could-not-run it can do nothing about.
        result = self.check().run({}, {})
        self.assertEqual(result["status"], check_all.SKIPPED)

    def test_the_verdict_is_not_ok_when_something_was_ambiguous(self):
        # `verdict` answers with a STATUS, not an exit code — the exit code is mapped from it.
        results = [self.check().run({}, {"circuit": ["a", "b"]})]
        self.assertEqual(check_all.verdict(results), check_all.COULD_NOT_RUN)
        self.assertNotEqual(check_all.verdict(results), check_all.OK)

    def test_naming_one_explicitly_settles_it(self):
        # `--circuit` exists precisely to resolve this, so it must clear the ambiguity rather than
        # be overruled by it.
        root = self._project("dist/car/circuit.json", "dist/remote/circuit.json")
        args = argparse.Namespace(project=str(root), circuit="dist/car/circuit.json", rules=None,
                                  design=None, board=None, board_file=None, firmware=None,
                                  boards=None, package=None, json=False)
        _, _, ambiguous = check_all.inputs_for(args)
        self.assertNotIn("circuit", ambiguous)

    def test_two_circuits_with_no_choice_made_are_reported_ambiguous(self):
        root = self._project("dist/car/circuit.json", "dist/remote/circuit.json")
        _, _, ambiguous = check_all.discover(root)
        self.assertEqual(len(ambiguous.get("circuit", [])), 2)

    @staticmethod
    def _project(*relative):
        root = Path(tempfile.mkdtemp())
        for name in relative:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]")
        return root


class ABrokenCheckDoesNotHideTheOthers(unittest.TestCase):
    def test_an_unreadable_input_is_could_not_run_not_ok(self):
        results = check_all.run({"circuit": "/nonexistent/circuit.json",
                                 "rules": "/nonexistent/rules.json"})
        statuses = {r["check"]: r["status"] for r in results}
        self.assertIn(check_all.COULD_NOT_RUN, statuses.values())
        self.assertNotIn(check_all.OK, [statuses[name] for name in statuses
                                        if name in ("physics", "buildability")])

    def test_one_exploding_check_still_lets_the_rest_report(self):
        # This asserted only `len(results) == len(CHECKS)`, which `run()` makes true by
        # construction whatever explodes, so it could not fail — and the explosion it was written
        # for was a SystemExit, which the guard did not catch at all. What matters is that a
        # check which blew up did not stop another check from answering.
        no_bom = Path(tempfile.mkdtemp()) / "nobom.zip"
        zipfile.ZipFile(no_bom, "w").writestr("readme.txt", "no bill of materials here")
        results = {r["check"]: r for r in check_all.run({
            "package": str(no_bom),
            "design": written("exploding.design.json", {
                "board": "firebeetle2-esp32s3",
                "parts": [{"ref": "Sense",
                           "pins": [{"signal": "SENSE", "pin": "D6", "needs": ["adc"]}]}]}),
        })}
        self.assertEqual(results["the-order"]["status"], check_all.COULD_NOT_RUN)
        self.assertEqual(results["pin-capability"]["status"], check_all.PROBLEMS,
                         "a check that exploded stopped another check from answering")

    def test_could_not_run_is_not_the_same_exit_code_as_clean(self):
        self.assertNotEqual(check_all.EXIT_COULD_NOT_RUN, check_all.EXIT_OK)
        self.assertNotEqual(check_all.EXIT_COULD_NOT_RUN, check_all.EXIT_PROBLEMS)


class RealFindingsTest(unittest.TestCase):
    def test_a_board_with_a_defect_fails(self):
        circuit = written("circuit.json", [
            {"type": "pcb_via", "hole_diameter": 0.2, "outer_diameter": 0.3}])
        results = check_all.run({"circuit": circuit})
        buildability = next(r for r in results if r["check"] == "buildability")
        self.assertEqual(buildability["status"], check_all.PROBLEMS)
        self.assertEqual(check_all.main(["--circuit", circuit]), check_all.EXIT_PROBLEMS)

    def test_an_unmeasured_rail_is_reported_without_failing_the_run(self):
        circuit = written("circuit.json", [
            {"type": "source_net", "source_net_id": "GND", "name": "GND"}])
        rules = written("rules.json", {"physics": {"rails": {
            "GND": {"max_current_a": 1.5, "served_by_pour": True}}}})
        results = check_all.run({"circuit": circuit, "rules": rules})
        physics = next(r for r in results if r["check"] == "physics")
        self.assertEqual(physics["status"], check_all.OK)
        self.assertTrue(physics["unmeasured"], "an unmeasured rail must still be said out loud")
        self.assertIn("?", check_all.render(results))


class TheCheckListItselfTest(unittest.TestCase):
    """
    The runner exists so the list of checks lives beside the scripts, not in a skill's prose.
    """

    def test_every_check_has_a_name_and_says_what_it_owns(self):
        for check in check_all.CHECKS:
            self.assertTrue(check.name)
            self.assertTrue(check.what, "%s does not say what it is for" % check.name)
            self.assertTrue(check.needs, "%s claims to need no input" % check.name)

    def test_check_names_are_unique(self):
        names = [check.name for check in check_all.CHECKS]
        self.assertEqual(len(names), len(set(names)))

    def test_every_check_script_on_disk_is_wired_into_the_runner(self):
        """
        A script nobody invokes is the bug this whole file exists to prevent.

        This used to grep the runner's SOURCE for `load("check_design")`. The string was there and
        the call beneath it named a function that has never existed, so the flagship check had
        never run once and the test was green the whole time: it verified the check was NAMED,
        not that it RAN. Its own docstring even warned about an earlier version that could not
        fail.

        So it now asks the code the runner RUNS: the names each check's `call` compiles to —
        which is where the `import check_x` inside it lands — rather than the source text.
        (The previous version of this docstring claimed it "imports each script and calls what
        the runner calls" while the code beneath it grepped for `load("…")`; when the loader
        became a plain import, the grep found nothing and the test failed, which is how the
        claim was found to be untrue. Found 2026-09-29, under audit A7.) Nothing in this file may
        assert on source text.
        """
        # Scripts that are not checks OF A BUILT DESIGN, which is the only thing this runner
        # knows how to feed. Each needs a reason, because an exclusion list is also how a check
        # gets quietly switched off.
        #   check_all   — the runner itself.
        #   check_spine — takes a requirements.json and BUILDS a design; every other check reads
        #                 one that already exists. Wiring it in would make every design review
        #                 regenerate and rebuild spark's own reference board.
        NOT_A_CHECK = {"check_all", "check_spine"}
        on_disk = {path.stem for path in (ROOT / "scripts").glob("check_*.py")} - NOT_A_CHECK
        on_disk |= {"compare_design"}

        wired = set()
        for check in check_all.CHECKS:
            wired |= set(check.call.__code__.co_names)
        unwired = sorted(name for name in on_disk if name not in wired)
        self.assertEqual(
            unwired, [],
            "these check scripts exist but no check in check_all.py imports them: %s" % unwired)



class OneModulePerProcessTest(unittest.TestCase):
    """
    Audit A7. Siblings were loaded by file path, which makes a fresh module object each time and
    registers none of them: `check_all`'s `parts` was not `emit_board`'s, and their `PartError`
    classes were different objects, so an `except` for one could not catch the other.

    Proven behaviourally: a patch on the module everyone else imports is seen by the check. A
    path-loaded copy would run the unpatched original and never notice.
    """

    @staticmethod
    def _measured_circuit(root):
        circuit = [{"type": "source_component", "source_component_id": "c", "name": "PackIn"},
                   {"type": "pcb_component", "pcb_component_id": "pcb_c", "source_component_id": "c"}]
        circuit += [{"type": "pcb_plated_hole", "shape": "pill", "pcb_component_id": "pcb_c",
                     "hole_width": 1.6, "hole_height": 0.75, "outer_width": 2.4,
                     "outer_height": 1.2, "x": i * 2.0, "y": 0.0} for i in range(2)]
        (root / "circuit.json").write_text(json.dumps(circuit))
        return str(root / "circuit.json")

    def test_buildability_runs_the_check_footprints_everyone_else_imports(self):
        root = Path(tempfile.mkdtemp())
        circuit = self._measured_circuit(root)
        check = next(c for c in check_all.CHECKS if c.name == "buildability")
        # Unpatched, the rings are under the minimum: a problem.
        self.assertEqual(check.run({"circuit": circuit})["status"], check_all.PROBLEMS)
        # Patched on the shared module, the check sees no findings at all.
        with mock.patch.object(check_footprints, "run", return_value=[]):
            self.assertEqual(check.run({"circuit": circuit})["status"], check_all.OK)

    def test_the_placeholder_list_uses_the_design_module_everyone_else_imports(self):
        root = Path(tempfile.mkdtemp())
        (root / "car.requirements.json").write_text(json.dumps({"parts": []}))
        with mock.patch.object(design, "parts_of", side_effect=design.DesignError("patched")):
            names, notes = check_all.placeholder_components_in(root)
        self.assertEqual(names, ())
        self.assertEqual(len(notes), 1, notes)
        self.assertIn("patched", notes[0])

    def test_there_is_no_path_loader_left_to_reach_for(self):
        self.assertFalse(hasattr(check_all, "load"))


class OneCircuitConventionTest(unittest.TestCase):
    def test_the_runner_and_the_initialiser_look_in_the_same_places(self):
        # Two copies of the glob pair, in two files, neither knowing the other existed (audit
        # A6). G10's fix made both refuse two matches; a third path added to one would not have
        # reached the other.
        import init_project
        self.assertEqual(check_all.CONVENTIONS["circuit"], list(design.CIRCUIT_PATHS))
        self.assertIs(init_project.CIRCUIT_PATHS, design.CIRCUIT_PATHS)

if __name__ == "__main__":
    unittest.main()
