"""
Proof that setting a project up guesses nothing.

`findings.py` told people to "Run `spark init`", and that command existed nowhere but inside the
error message. So the first thing a second project hit was a remedy that did not exist, and two
of the deterministic checks plus every reviewer depend on files nothing created.

What is tested here is mostly what it REFUSES to write. An init that inferred a rail's current
from a part name would poison the one check that does arithmetic, in a tool whose whole thesis is
that an unchecked thing must not look like a checked one. So every value is null, and the list of
nulls is the output rather than a shortfall.

    python3 -m unittest discover -s tests -t tests
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_physics  # noqa: E402
import init_project  # noqa: E402
import store  # noqa: E402


def a_project(nets=("V33", "GND", "MOTOR6V", "SDA", "SCL")):
    root = Path(tempfile.mkdtemp())
    circuit = root / "dist" / "board" / "circuit.json"
    circuit.parent.mkdir(parents=True)
    circuit.write_text(json.dumps(
        [{"type": "source_net", "source_net_id": net, "name": net} for net in nets]))
    return root


class WhatItWritesTest(unittest.TestCase):
    def test_a_project_s_own_pin_reaches_the_package_file(self):
        # The spec's "change a version": one line in the project's tools file, and the next init uses it.
        import json, tempfile
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / ".spark" / "tools.json").write_text(json.dumps({"tscircuit": {"version": "0.1.2200", "core": "0.0.2700"}}))
        dependencies = init_project.package_file(root)["dependencies"]
        self.assertEqual(dependencies, {"@tscircuit/cli": "0.1.2200", "tscircuit": "0.0.2700"})

    def test_the_pins_are_the_tools_list_s(self):
        import tools
        entry = tools.merged()["tools"]["tscircuit"]
        self.assertEqual((init_project.PINNED_TSCI, init_project.PINNED_CORE), (entry["version"], entry["core"]))

    def setUp(self):
        self.root = a_project()
        init_project.main(["--project", str(self.root)])
        self.rules = json.loads((self.root / ".spark" / "rules.json").read_text())

    def test_the_rails_are_named_from_the_design_that_exists(self):
        # Typing them again is a chance to get one wrong, and a rule keyed on a net name that is
        # not in the design never fires — which looks exactly like a rule that passes.
        self.assertEqual(set(self.rules["physics"]["rails"]), {"V33", "GND", "MOTOR6V"})

    def test_a_bus_is_not_also_listed_as_a_rail(self):
        self.assertEqual(set(self.rules["i2c_buses"]), {"SDA", "SCL"})
        self.assertNotIn("SDA", self.rules["physics"]["rails"])

    def test_the_brief_is_written_too(self):
        # No script reads it; every reviewer does, and it is what consequence is judged against.
        brief = json.loads((self.root / ".spark" / "project.json").read_text())
        self.assertIn("must", brief)

    def test_the_toolchain_is_pinned_to_a_version_of_the_package_it_names(self):
        # THIS TEST HELD THE WRONG PAIR, and that is why P33 shipped a project nobody could
        # install. It asserted that the `@tscircuit/cli` pin equals the version printed in
        # build.md's example output — but `tsci --version` prints the `tscircuit` CORE the CLI
        # bundles, not the CLI. Making them equal is the conflation itself: it forced the pin to
        # be a core number, and `npm install` then failed with `No matching version found for
        # @tscircuit/cli@0.0.2600` for everyone without a global CLI already on PATH (P51).
        import re
        pinned = json.loads((self.root / "package.json").read_text())["dependencies"]["@tscircuit/cli"]
        self.assertRegex(pinned, r"^\d+\.\d+\.\d+$", "an exact version, not a range: %r" % pinned)
        self.assertEqual(pinned, init_project.PINNED_TSCI)
        documented = re.search(r"tsci (\d+\.\d+\.\d+)", (ROOT / "commands" / "build.md").read_text())
        self.assertIsNotNone(documented, "build.md's example output names the core it was run with")
        self.assertEqual(documented.group(1), init_project.PINNED_CORE,
                         "the documents show core %s and the pinned CLI carries %s"
                         % (documented.group(1), init_project.PINNED_CORE))

    def test_the_two_version_numbers_are_not_the_same_kind_of_thing(self):
        # The guard against re-conflating them. `@tscircuit/cli` numbers its releases 0.1.2xxx and
        # its 0.0.x line stopped at 0.0.394; `tscircuit` is on 0.0.2xxx. A pin that looks like a
        # core version is the defect P51 fixed, and it is invisible without a network call.
        self.assertNotEqual(init_project.PINNED_TSCI, init_project.PINNED_CORE)
        self.assertTrue(init_project.PINNED_TSCI.startswith("0.1."),
                        "the CLI's own line is 0.1.x; %r looks like a core version"
                        % init_project.PINNED_TSCI)
        self.assertTrue(init_project.PINNED_CORE.startswith("0.0."),
                        "the core's line is 0.0.2xxx; %r looks like a CLI version"
                        % init_project.PINNED_CORE)

    def test_the_core_is_pinned_too_because_the_cli_takes_it_as_a_wildcard_peer(self):
        # THE DEFECT P51 FIXED. `@tscircuit/cli` declares `tscircuit: "*"` as a peerDependency, so
        # npm installs whatever core is newest and the CLI's own pin constrains nothing. Proved in
        # clean projects on 2026-09-30: `@tscircuit/cli@0.1.2113` installed fresh reported core
        # 0.0.2687, the same CLI version installed here weeks ago reports 0.0.2600. `tscircuit` was
        # never in the package file at all, so every project spark ever made took the newest core.
        deps = json.loads((self.root / "package.json").read_text())["dependencies"]
        self.assertEqual(deps.get("tscircuit"), init_project.PINNED_CORE,
                         "the core is unpinned, so a new project gets whatever npm has newest")
        self.assertRegex(deps["tscircuit"], r"^\d+\.\d+\.\d+$", "an exact version, not a range")

    def test_a_core_the_documents_were_not_measured_on_is_said_not_swallowed(self):
        # W1's shape, for the toolchain: a build on a different core is not failed — a newer core
        # may be perfectly good — but it is never passed in silence either.
        import check_spine
        self.assertEqual(check_spine.core_note(init_project.PINNED_CORE), "")
        self.assertIn(init_project.PINNED_CORE, check_spine.core_note("0.0.9999"))
        self.assertEqual(check_spine.core_note("unknown version"), "",
                         "a version nobody could read is not a drift claim")

    def test_a_package_file_is_written_so_tscircuit_stops_its_walk_at_the_project(self):
        # I9: with no package file, `npx tsci build` climbed to the home folder and died on a
        # protected directory; the car had one from its first evening, the irrigation box did not.
        package = json.loads((self.root / "package.json").read_text())
        self.assertEqual((package["name"], package["private"], "@tscircuit/cli" in package["dependencies"]),
                         (self.root.name, True, True))
        (self.root / "package.json").write_text('{"name": "mine", "dependencies": {"tscircuit": "*"}}')
        init_project.main(["--project", str(self.root), "--force"])
        self.assertEqual(json.loads((self.root / "package.json").read_text())["name"], "mine",
                         "a package file a person may have added to is never rewritten, even by --force")

    def test_an_existing_file_is_not_overwritten(self):
        (self.root / ".spark" / "rules.json").write_text('{"mine": true}')
        init_project.main(["--project", str(self.root)])
        self.assertEqual(json.loads((self.root / ".spark" / "rules.json").read_text()),
                         {"mine": True})


class TheThreeFunctionsTheAuditFoundUnnamedTest(unittest.TestCase):
    """Audit C9: `nets_in`, `rules_for` and `has_answers` were named by no test."""

    def test_nets_in_reads_the_nets_that_exist_and_nothing_from_nowhere(self):
        root = a_project(nets=("GND", "V33", "SDA"))
        self.assertEqual(init_project.nets_in(root / "dist" / "board" / "circuit.json"), ["GND", "SDA", "V33"])
        self.assertEqual(init_project.nets_in(root / "nowhere.json"), [])
        self.assertEqual(init_project.nets_in(None), [])

    def test_rules_for_puts_rails_and_buses_where_they_belong_with_nothing_measured(self):
        rules = init_project.rules_for(["GND", "V33", "SDA", "SCL"])
        self.assertEqual(set(rules["physics"]["rails"]), {"GND", "V33"})
        self.assertEqual(set(rules["i2c_buses"]), {"SDA", "SCL"})
        self.assertTrue(all(rail.get("max_current_a") is None for rail in rules["physics"]["rails"].values()),
                        "a current nobody measured is null, not a guess")

    def test_has_answers_tells_a_filled_brief_from_the_template(self):
        root = Path(tempfile.mkdtemp())
        blank, filled, broken = root / "blank.json", root / "filled.json", root / "broken.json"
        blank.write_text(json.dumps(init_project.PROJECT_TEMPLATE))
        filled.write_text(json.dumps(dict(init_project.PROJECT_TEMPLATE, goal="water the beds")))
        broken.write_text("{not json")
        self.assertFalse(init_project.has_answers(blank, init_project.PROJECT_TEMPLATE))
        self.assertTrue(init_project.has_answers(filled, init_project.PROJECT_TEMPLATE))
        self.assertTrue(init_project.has_answers(broken, init_project.PROJECT_TEMPLATE), "whatever is in it, it is not ours to replace")


class WhatItRefusesToGuessTest(unittest.TestCase):
    """The design. Everything here is about values NOT being invented."""

    def setUp(self):
        self.root = a_project()
        init_project.main(["--project", str(self.root)])
        self.rules = json.loads((self.root / ".spark" / "rules.json").read_text())

    def test_every_rail_current_is_null(self):
        for name, rail in self.rules["physics"]["rails"].items():
            with self.subTest(rail=name):
                self.assertIsNone(rail["max_current_a"])
                self.assertIsNone(rail["nominal_volts"])

    def test_a_null_rail_makes_physics_report_it_rather_than_pass_it(self):
        # The reason nulls are safe, asserted rather than assumed. If a null ever became a pass,
        # this whole design would be worse than writing a plausible number.
        circuit = json.loads((self.root / "dist" / "board" / "circuit.json").read_text())
        findings = check_physics.run(circuit, self.rules)
        self.assertTrue(findings, "a design with no stated currents was reported as fine")
        self.assertTrue(all(f.severity != "problem" for f in findings))

    def test_it_lists_every_field_nobody_answered(self):
        unanswered = init_project.nulls_in(self.rules)
        self.assertIn("physics.rails.V33.max_current_a", unanswered)
        self.assertIn("physics.i2c_hz", unanswered)

    def test_the_one_value_it_does_set_is_a_decision_not_a_measurement(self):
        # A temperature rise is a choice about how hot you will let a trace get. It is the only
        # number here that can be defaulted honestly, and the file says it is a decision.
        self.assertEqual(self.rules["physics"]["trace_temperature_rise_c"], 10)
        self.assertIn("DECISION", self.rules["physics"]["//trace_temperature_rise_c"])


class WithoutABuiltDesignTest(unittest.TestCase):
    def test_it_still_writes_the_files_and_says_the_rails_are_empty(self):
        root = Path(tempfile.mkdtemp())
        self.assertEqual(init_project.main(["--project", str(root)]), init_project.EXIT_OK)
        rules = json.loads((root / ".spark" / "rules.json").read_text())
        self.assertEqual(rules["physics"]["rails"], {})

    def test_a_directory_that_does_not_exist_is_refused(self):
        self.assertEqual(init_project.main(["--project", "/nonexistent/project"]),
                         init_project.EXIT_COULD_NOT_RUN)

    def test_a_board_that_does_not_exist_is_refused_rather_than_written(self):
        root = a_project()
        self.assertEqual(init_project.main(["--project", str(root), "--board", "no-such-board"]),
                         init_project.EXIT_COULD_NOT_RUN)
        self.assertFalse((root / "boards" / "active.json").exists())


class ForceMustNotEatWhatSomebodyMeasuredTest(unittest.TestCase):
    """
    P53. `--force` REPLACED the rules file, and the documents tell people to use it: *"no built
    design found, so the rails are empty — build, then re-run with --force"*. So the one workflow
    this tool prescribes destroyed the answers it had just asked somebody to go and measure.
    Reproduced on a copy of the RC car: `i2c_hz` set to 400000 came back `null`, a rail current of
    0.5 A came back nulls. The brief was protected by `has_answers`; the rules file — the one
    holding numbers you need a meter for — was not.
    """

    def test_a_stated_value_beats_a_derived_null(self):
        self.assertEqual(init_project.merged({"i2c_hz": 400000}, {"i2c_hz": None}),
                         {"i2c_hz": 400000})

    def test_a_missing_key_is_filled_in(self):
        self.assertEqual(init_project.merged({}, {"i2c_hz": None}), {"i2c_hz": None})

    def test_a_null_somebody_left_is_filled_in(self):
        self.assertEqual(init_project.merged({"rails": None}, {"rails": {"V33": {}}}),
                         {"rails": {"V33": {}}})

    def test_nested_answers_merge_rather_than_being_replaced(self):
        was = {"physics": {"i2c_hz": 400000, "rails": {"V33": {"max_current_a": 0.5}}}}
        now = {"physics": {"i2c_hz": None, "rails": {"GND": {"max_current_a": None}}}}
        after = init_project.merged(was, now)
        self.assertEqual(after["physics"]["i2c_hz"], 400000)
        self.assertEqual(after["physics"]["rails"]["V33"]["max_current_a"], 0.5)
        self.assertIn("GND", after["physics"]["rails"], "a new rail was not added")

    def test_an_empty_list_is_seeded(self):
        # Exactly where P45's lists stayed: empty and indistinguishable from "nobody looked".
        self.assertEqual(init_project.merged({"must_not_float": []},
                                             {"must_not_float": [["U1", "IN"]]}),
                         {"must_not_float": [["U1", "IN"]]})

    def test_a_list_somebody_filled_in_is_theirs(self):
        # A rule they deleted stays deleted.
        self.assertEqual(init_project.merged({"must_not_float": [["U1", "IN"]]},
                                             {"must_not_float": [["U2", "IN"]]}),
                         {"must_not_float": [["U1", "IN"]]})

    def test_a_key_this_tool_knows_nothing_about_is_kept(self):
        self.assertEqual(init_project.merged({"mine": 1}, {})["mine"], 1)

    def test_the_notes_take_the_derived_text_because_they_are_ours(self):
        self.assertEqual(init_project.merged({"//x": "old"}, {"//x": "new"}), {"//x": "new"})

    def test_what_the_records_add_to_a_filled_list_is_named(self):
        said = init_project.not_yet_stated(
            {"must_not_float": [["Valve1", "SIGNAL"]]},
            {"must_not_float": [["Valve1", "SIGNAL"], ["BtnMode", "A"]]})
        self.assertEqual(len(said), 1)
        self.assertIn("BtnMode.A", said[0])

    def test_an_empty_list_says_nothing_because_the_merge_filled_it(self):
        self.assertEqual(init_project.not_yet_stated({"must_not_float": []},
                                                     {"must_not_float": [["U1", "IN"]]}), [])

    def test_force_through_the_command_line_keeps_the_answers(self):
        # The helper above is not the product; this is. R2.2's shape, named twice already.
        root = Path(tempfile.mkdtemp())
        (root / ".spark").mkdir()
        (root / ".spark" / "rules.json").write_text(json.dumps(
            {"i2c_buses": [], "must_not_float": [],
             "physics": {"i2c_hz": 400000, "rails": {"V33": {"max_current_a": 0.5}}}}))
        (root / "a.requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        init_project.main(["--project", str(root), "--force"])
        after = json.loads((root / ".spark" / "rules.json").read_text())
        self.assertEqual(after["physics"]["i2c_hz"], 400000, "--force ate a measured value")
        self.assertEqual(after["physics"]["rails"]["V33"]["max_current_a"], 0.5)
        self.assertEqual(after["must_not_float"], [["L9110sModule", "AIA"], ["L9110sModule", "AIB"]])


class TwoBuiltDesignsTest(unittest.TestCase):
    """
    Two halves of one tool disagreed about whether choosing is allowed.

    `check_all` calls two matching circuits ambiguous and refuses. `init_project` took
    `matches[0]` — whichever sorted first — seeded the rules from it, and reported "named N
    rail(s) from circuit.json" while naming no path. On the RC-car project that made one board's
    rails the rules for both, silently.
    """

    @staticmethod
    def _with(*circuits):
        root = Path(tempfile.mkdtemp())
        for name in circuits:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(
                [{"type": "source_net", "source_net_id": "n1", "name": "V33"}]))
        return root

    def test_the_rails_of_one_board_never_become_the_rules_for_both(self):
        # The invariant, unchanged: choosing between them silently is the defect.
        root = self._with("dist/car/circuit.json", "dist/remote/circuit.json")
        init_project.main(["--project", str(root)])
        written = json.loads((root / ".spark" / "rules.json").read_text())
        self.assertEqual(written["physics"]["rails"], {},
                         "it seeded the rails from one of two designs")

    def test_it_still_answers_could_not_run(self):
        root = self._with("dist/car/circuit.json", "dist/remote/circuit.json")
        self.assertEqual(init_project.main(["--project", str(root)]),
                         init_project.EXIT_COULD_NOT_RUN)

    def test_but_what_the_part_records_give_is_still_written(self):
        # THE CONTRACT CHANGED WITH P53. This used to refuse and write nothing, so a two-board
        # project could never get its floating-input rules — and the RC car, which carries the
        # canonical example in its L9110S, had `must_not_float: []` for two sprints. A record
        # says the same thing whichever board was built, so the ambiguity does not reach it.
        root = self._with("dist/car/circuit.json", "dist/remote/circuit.json")
        (root / "a.requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        init_project.main(["--project", str(root)])
        written = json.loads((root / ".spark" / "rules.json").read_text())
        self.assertEqual(written["must_not_float"],
                         [["L9110sModule", "AIA"], ["L9110sModule", "AIB"]])

    def test_and_it_says_which_designs_it_could_not_choose_between(self):
        import contextlib, io
        root = self._with("dist/car/circuit.json", "dist/remote/circuit.json")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            init_project.main(["--project", str(root)])
        said = out.getvalue()
        self.assertIn("dist/car/circuit.json", said)
        self.assertIn("dist/remote/circuit.json", said)

    def test_naming_one_settles_it(self):
        root = self._with("dist/car/circuit.json", "dist/remote/circuit.json")
        self.assertEqual(
            init_project.main(["--project", str(root), "--circuit", "dist/car/circuit.json"]),
            init_project.EXIT_OK)

    def test_one_built_design_is_still_used_without_being_named(self):
        # The refusal must not cost the ordinary case its convenience.
        root = self._with("dist/board/circuit.json")
        self.assertEqual(init_project.main(["--project", str(root)]), init_project.EXIT_OK)
        rules = json.loads((root / ".spark" / "rules.json").read_text())
        self.assertIn("V33", rules["physics"]["rails"])


class ABriefIsYoursTest(unittest.TestCase):
    """
    `init --force` was the only way to re-seed the rails after a build, and it replaced the
    hand-written `project.json` with the blank template on the way (intake R13, 09-25;
    reproduced in the code 09-29). The rules file is derived and may be rewritten; a brief with
    answers in it is a person's, and no flag touches it.
    """

    def _init(self, root, *extra):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return init_project.main(["--project", str(root), *extra])

    def test_force_reseeds_the_rules_and_keeps_an_answered_brief(self):
        root = Path(tempfile.mkdtemp())
        self._init(root)
        brief = root / ".spark" / "project.json"
        answered = json.loads(brief.read_text())
        answered["goal"] = "a bin that opens when waved at"
        brief.write_text(json.dumps(answered))
        rules = root / ".spark" / "rules.json"
        rules.write_text("{}")
        self._init(root, "--force")
        self.assertEqual(json.loads(brief.read_text())["goal"], "a bin that opens when waved at")
        self.assertNotEqual(rules.read_text(), "{}", "the derived rules were not re-seeded")

    def test_an_unanswered_brief_is_still_rewritten_by_force(self):
        # The control: the template itself has no answers, so --force may replace it.
        root = Path(tempfile.mkdtemp())
        self._init(root)
        brief = root / ".spark" / "project.json"
        brief.write_text(json.dumps(json.loads(brief.read_text())) + "\n\n")
        self._init(root, "--force")
        self.assertFalse(brief.read_text().endswith("\n\n"))

    def test_a_brief_that_cannot_be_read_is_not_replaced_either(self):
        root = Path(tempfile.mkdtemp())
        self._init(root)
        brief = root / ".spark" / "project.json"
        brief.write_text("{half-written")
        self._init(root, "--force")
        self.assertEqual(brief.read_text(), "{half-written")

class TheRulesAreSeededFromTheDesignTest(unittest.TestCase):
    """
    P45. `must_not_float: []` and `i2c_buses: []` on every project this tool has ever set up.

    An empty list and "nobody filled it in" were the same thing on disk, so `compare_design`
    had no rule to apply and said it compared nothing — on the RC car, on the irrigation
    controller, on the reference design.
    """

    L9110S = {"id": "l9110s-module", "name": "L9110S dual motor driver module",
              "needs": [{"signal": "MOTOR_IA", "pin": "AIA", "direction": "in"},
                        {"signal": "MOTOR_IB", "pin": "AIB", "direction": "in"}],
              "host_parts": [{"kind": "pulldown", "pin": "AIA", "ohms": 10000, "why": "x"},
                             {"kind": "pulldown", "pin": "AIB", "ohms": 10000, "why": "x"}]}
    #: A breakout with no pull-ups of its own: the host has to supply them.
    NEEDY = {"id": "vl6180x-breakout", "name": "VL6180X breakout",
             "needs": [{"signal": "SDA", "pin": "SDA", "direction": "bidirectional", "bus": "i2c"},
                       {"signal": "SCL", "pin": "SCL", "direction": "bidirectional", "bus": "i2c"}],
             "host_parts": [{"kind": "pullup", "pin": "SDA", "ohms": 4700, "why": "x"},
                            {"kind": "pullup", "pin": "SCL", "ohms": 4700, "why": "x"}]}
    #: A module that brings its own 4.7 k, like the irrigation controller's DS3231.
    SELF_PULLED = {"id": "ds3231", "name": "DS3231 RTC module",
                   "needs": [{"signal": "SDA", "pin": "SDA", "direction": "bidirectional", "bus": "i2c"},
                             {"signal": "SCL", "pin": "SCL", "direction": "in", "bus": "i2c"}]}

    def test_every_declared_input_becomes_a_rule(self):
        self.assertEqual(init_project.declared_inputs([self.L9110S]),
                         [["L9110sModule", "AIA"], ["L9110sModule", "AIB"]])

    def test_the_rules_file_actually_carries_them(self):
        # The helper was tested and the file it writes was not — the shape R2.2 was written for,
        # and a mutation setting `must_not_float` back to `[]` escaped a green suite because of
        # it. The defect being guarded against is the FILE coming out empty, not the function
        # returning nothing.
        self.assertEqual(init_project.rules_for([], [self.L9110S])["must_not_float"],
                         [["L9110sModule", "AIA"], ["L9110sModule", "AIB"]])

    def test_and_the_written_file_does_too(self):
        work = Path(tempfile.mkdtemp())
        (work / "a.requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["l9110s-module"]}))
        init_project.main(["--project", str(work)])
        written = json.loads((work / ".spark" / "rules.json").read_text())
        self.assertEqual(written["must_not_float"],
                         [["L9110sModule", "AIA"], ["L9110sModule", "AIB"]])

    def test_a_pin_that_is_not_an_input_is_not_one(self):
        # A bidirectional bus line and an interrupt output are not floating-input rules; naming
        # every pin is how a check becomes noise.
        self.assertEqual(init_project.declared_inputs([self.NEEDY]), [])

    def test_a_bus_the_host_must_pull_up_is_seeded(self):
        self.assertEqual(init_project.i2c_lines([self.NEEDY])[0],
                         ["Vl6180xBreakout.SCL", "Vl6180xBreakout.SDA"])

    def test_only_a_pull_up_makes_the_bus_the_hosts(self):
        # The record schema allows any `kind` on any pin, and what makes a line THIS board's to
        # pull up is specifically a pull-up. A pull-down on a bus line is a mistake in the
        # record; counting it here would hide that mistake behind a rule that passes.
        wrong = dict(self.SELF_PULLED,
                     host_parts=[{"kind": "pulldown", "pin": "SDA", "ohms": 10000, "why": "x"}])
        host, carried = init_project.i2c_lines([wrong])
        self.assertEqual(host, [])
        self.assertIn("Ds3231.SDA", carried)

    def test_a_module_that_carries_its_own_pullups_is_not(self):
        # The false alarm this avoids, reproduced from a real record: the irrigation DS3231's
        # own text is "Add NO pull-ups: the module carries 4.7 k on SDA and SCL". Seeding its
        # lines would report a bus nothing pulls up, on a bus that is pulled up.
        host, carried = init_project.i2c_lines([self.SELF_PULLED])
        self.assertEqual(host, [])
        self.assertEqual(carried, ["Ds3231.SCL", "Ds3231.SDA"])

    def test_an_empty_list_says_why_it_is_empty(self):
        rules = init_project.rules_for([], [self.SELF_PULLED])
        self.assertEqual(rules["i2c_buses"], [])
        self.assertIn("carries its own pull-ups", rules["//i2c_buses"])
        # the note names the MODULE, not every line of it
        self.assertIn("(Ds3231)", rules["//i2c_buses"])

    def test_a_bus_is_named_by_a_pin_because_no_generated_net_is_called_sda(self):
        # spark's generator wires every signal pin-to-pin. A rule naming the net SDA could only
        # ever report "no net of that name" on a board this tool produced.
        self.assertTrue(all("." in line for line in init_project.i2c_lines([self.NEEDY])[0]))

    def test_a_net_actually_called_sda_is_still_a_bus(self):
        # A hand-written board.tsx has one. The smart bin's does.
        self.assertEqual(init_project.rules_for(["SDA", "SCL", "V33"], [])["i2c_buses"],
                         ["SCL", "SDA"])

    def test_a_requirements_file_that_will_not_read_is_a_note_not_a_silence(self):
        work = Path(tempfile.mkdtemp())
        (work / "broken.requirements.json").write_text("{ not json")
        part_list, notes = init_project.design_in(work)
        self.assertEqual(part_list, [])
        self.assertEqual(len(notes), 1)
        self.assertIn("no rule was seeded from it", notes[0])



class TheMeasuredPinsAreSparkSTest(unittest.TestCase):
    def test_a_person_s_pin_does_not_become_what_the_documents_were_measured_on(self):
        # The final review: PINNED_* read the merged list, so a personal pin leaked into "measured on"
        # and into the suite. The documents were measured on spark's own defaults.
        import importlib
        import tools
        personal = Path(tempfile.mkdtemp()) / "tools.json"
        personal.write_text(json.dumps({"tscircuit": {"version": "9.9.9", "core": "8.8.8"}}))
        defaults = json.loads((ROOT / "data" / "tools.json").read_text())["tscircuit"]
        try:
            with mock.patch.object(tools, "PERSONAL", personal):
                importlib.reload(init_project)
                self.assertEqual((init_project.PINNED_TSCI, init_project.PINNED_CORE), (defaults["version"], defaults["core"]))
        finally:
            importlib.reload(init_project)

class TheProjectsListTest(unittest.TestCase):
    """P95 (§5.5): /spark:init puts the project on the person's projects list, so spark finds its records."""

    def test_the_brief_no_longer_asks_what_you_own(self):
        """P95 (W16): what you own is the drawer's to say — /spark:drawer — not each project's."""
        self.assertNotIn("parts_on_hand", json.dumps(init_project.PROJECT_TEMPLATE))

    def test_init_puts_the_project_on_the_list(self):
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(home)}), contextlib.redirect_stdout(io.StringIO()) as out:
            init_project.main(["--project", str(project)])
            listed = store.projects()
        self.assertEqual(listed, {project.name: project.resolve()})
        self.assertIn("on your projects list as %r" % project.name, out.getvalue())


if __name__ == "__main__":
    unittest.main()
