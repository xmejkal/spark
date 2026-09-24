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

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_all  # noqa: E402


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

    def test_nothing_asked_for_exits_zero_because_you_chose_not_to_ask(self):
        self.assertEqual(check_all.main([]), check_all.EXIT_OK)

    def test_but_the_rendering_says_so_out_loud(self):
        rendered = check_all.render(check_all.run({}))
        self.assertIn("not asked for", rendered)
        self.assertIn("nothing found by the checks that ran", rendered)


class ABrokenCheckDoesNotHideTheOthers(unittest.TestCase):
    def test_an_unreadable_input_is_could_not_run_not_ok(self):
        results = check_all.run({"circuit": "/nonexistent/circuit.json",
                                 "rules": "/nonexistent/rules.json"})
        statuses = {r["check"]: r["status"] for r in results}
        self.assertIn(check_all.COULD_NOT_RUN, statuses.values())
        self.assertNotIn(check_all.OK, [statuses[name] for name in statuses
                                        if name in ("physics", "buildability")])

    def test_one_exploding_check_still_lets_the_rest_report(self):
        # Every check runs; a failure in one is caught and reported as its own status.
        results = check_all.run({"circuit": written("circuit.json", "not json at all"),
                                 "rules": written("rules.json", {})})
        self.assertEqual(len(results), len(check_all.CHECKS))

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
        A script nobody invokes is the bug this whole file exists to prevent: for a while the
        review loop ran one check out of seven, and looked exactly like one that ran all seven.

        Asserted against the runner's own SOURCE, because that is the thing that would be
        forgotten. A first version of this test subtracted the very scripts it was looking for
        and could not fail — which is its own lesson about tests that agree with themselves.
        """
        NOT_A_CHECK = {"check_all"}
        on_disk = {path.stem for path in (ROOT / "scripts").glob("check_*.py")} - NOT_A_CHECK
        on_disk |= {"compare_design"}

        source = (ROOT / "scripts" / "check_all.py").read_text()
        unwired = sorted(name for name in on_disk if 'load("%s")' % name not in source)
        self.assertEqual(
            unwired, [],
            "these check scripts exist but check_all.py never loads them: %s" % unwired)


if __name__ == "__main__":
    unittest.main()
