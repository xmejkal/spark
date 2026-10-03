"""
P31: the simulation project a design implies, from the records — what stands in, which chips
to compile, what the simulator's project file says. No simulator and no compiler are run here:
the compiler is a script that writes a file, the way `fake_tsci` stands in for tscircuit.
"""

import json
import os
import stat
import sys
import tempfile
import unittest
from unittest import mock
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sim_project  # noqa: E402

FakeDesign = namedtuple("FakeDesign", "parts project board", defaults=(None,))


def a_project():
    """A project with one record that has a chip beside it, so definition_path resolves."""
    root = Path(tempfile.mkdtemp())
    (root / ".spark").mkdir()
    chip = root / "parts" / "probe-x" / "chip"
    chip.mkdir(parents=True)
    (root / "parts" / "probe-x.json").write_text(json.dumps({"schema": 1, "id": "probe-x", "name": "P", "kind": "sensor"}))
    (chip / "probe.chip.c").write_text("// c\n")
    (chip / "probe.chip.json").write_text('{"name": "probe", "pins": ["SIG"]}\n')
    return root, chip


def fake_compiler(root, succeeds=True):
    script = root / "fake-wokwi-cli"
    script.write_text("#!/bin/sh\n" + ('[ "$1" = chip ] && [ "$2" = compile ] && { echo wasm > "$5"; exit 0; }\n' if succeeds else "") + "echo 'no' >&2; exit 1\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return str(script)


class WhatStandsInTest(unittest.TestCase):
    def test_each_record_becomes_an_entry_by_the_generators_component_name(self):
        root, chip = a_project()
        parts = [
            {"id": "valve-x", "_instance": "Valve1", "simulation": {"wokwi": {"part": "wokwi-led", "pins": {"SIGNAL": "A", "GND": "C"}, "attrs": {"color": "red"}, "stand_in": "s"}}},
            {"id": "jack-x", "simulation": {"skip": "wiring"}},
            {"id": "probe-x", "_instance": "Soil1", "simulation": {"wokwi": {"chip": "probe", "pins": {"SIG": "SIG"}}}},
            {"id": "probe-x", "_instance": "Soil2", "simulation": {"wokwi": {"chip": "probe", "pins": {"SIG": "SIG"}}}},
        ]
        mapping, chips, unmapped = sim_project.mapping_for(FakeDesign(parts, root))
        self.assertEqual(mapping["Valve1"], {"wokwiType": "wokwi-led", "pins": {"SIGNAL": "A", "GND": "C"}, "attrs": {"color": "red"}})
        self.assertEqual(mapping["JackX"], {"skip": "wiring"})
        self.assertEqual(mapping["Soil1"]["wokwiType"], "chip-probe")
        self.assertEqual(chips, [(chip, "probe")], "one chip to stage, however many instances use it")
        self.assertEqual(unmapped, [])

    def test_the_passives_spark_placed_for_a_part_are_resistors_in_the_diagram(self):
        part = {"id": "l9110s-module", "simulation": {"skip": "x"},
                "host_parts": [{"kind": "pulldown", "pin": "AIA", "ohms": 10000, "why": "w"},
                               {"kind": "divider", "pin": "AIB", "top_ohms": 10000, "bottom_ohms": 18000, "why": "w"}]}
        mapping, _, unmapped = sim_project.mapping_for(FakeDesign([part], None))
        self.assertEqual(unmapped, [])
        self.assertEqual(mapping["L9110sModulePulldownAIA"], {"wokwiType": "wokwi-resistor", "attrs": {"value": "10000"},
                                                               "pins": {"anode": "1", "cathode": "2", "pin1": "1", "pin2": "2"}},
                         "tscircuit names a resistor's ports anode and cathode; the diagram must not inherit the module's mapping")
        self.assertEqual(mapping["L9110sModuleDividerAIBBottom"]["attrs"], {"value": "18000"})

    def test_a_series_resistor_computed_for_a_current_has_that_value_in_the_diagram(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        part = {"id": "led-x", "simulation": {"skip": "x"}, "facts": {"forward_voltage_v": {"value": 2.0}},
                "host_parts": [{"kind": "series", "pin": "A", "for_current_ma": 5, "why": "w"}]}
        mapping, _, _ = sim_project.mapping_for(FakeDesign([part], None, board))
        self.assertEqual(mapping["LedXSeriesA"]["attrs"], {"value": "270"})

    def test_a_record_that_says_nothing_is_named_with_its_id(self):
        mapping, chips, unmapped = sim_project.mapping_for(FakeDesign([{"id": "mystery-x", "_instance": "M1"}], None))
        self.assertEqual((mapping, chips, unmapped), ({}, [], [("M1", "mystery-x")]))
        said = sim_project.unmapped_detail(unmapped)
        self.assertIn("M1 (mystery-x)", said)
        self.assertIn("simulation.skip", said)


class ChipsAreStagedAndCompiledTest(unittest.TestCase):
    def test_a_fresh_binary_beside_the_record_is_reused_without_a_compiler(self):
        root, chip = a_project()
        (chip / "probe.chip.wasm").write_bytes(b"\\0asm")
        os.utime(chip / "probe.chip.c", (1, 1))  # older than the binary
        sim_dir = root / "sim"
        staged, problems = sim_project.stage_chips([(chip, "probe")], sim_dir, compiler="/nonexistent")
        self.assertEqual((staged, problems), ({"probe": "reused"}, []), "a fresh binary is reused, and said to be")
        self.assertEqual((sim_dir / "chips" / "probe.chip.wasm").read_bytes(), b"\\0asm")
        self.assertTrue((sim_dir / "chips" / "probe.chip.json").is_file())

    def test_a_missing_or_stale_binary_is_compiled_and_kept_beside_the_record(self):
        root, chip = a_project()
        staged, problems = sim_project.stage_chips([(chip, "probe")], root / "sim", compiler=fake_compiler(root))
        self.assertEqual((staged, problems), ({"probe": "compiled"}, []))
        self.assertTrue((chip / "probe.chip.wasm").is_file(), "the compiled binary travels with the record")
        # stale: the binary is older than the source it was compiled from
        (chip / "probe.chip.wasm").write_bytes(b"old")
        os.utime(chip / "probe.chip.wasm", (1, 1))
        staged, problems = sim_project.stage_chips([(chip, "probe")], root / "sim2", compiler=fake_compiler(root))
        self.assertEqual((staged, problems), ({"probe": "compiled"}, []))
        self.assertNotEqual((root / "sim2" / "chips" / "probe.chip.wasm").read_bytes(), b"old", "a stale binary is recompiled")

    def test_no_compiler_is_could_not_run_with_the_install_hint(self):
        root, chip = a_project()
        with mock.patch.object(sim_project, "find_wokwi_cli", return_value=None):
            staged, problems = sim_project.stage_chips([(chip, "probe")], root / "sim")
        self.assertEqual(staged, {})
        self.assertIn("wokwi-cli was not found", problems[0])

    def test_a_compile_failure_is_a_problem_naming_the_chip(self):
        root, chip = a_project()
        staged, problems = sim_project.stage_chips([(chip, "probe")], root / "sim", compiler=fake_compiler(root, succeeds=False))
        self.assertEqual(staged, {})
        self.assertIn("probe did not compile", problems[0])


class TheProjectFileTest(unittest.TestCase):
    def test_names_every_chip_and_the_firmware(self):
        toml = sim_project.wokwi_toml(["probe", "flow-meter"], firmware="flash-with-firmware.bin")
        self.assertIn('firmware = "flash-with-firmware.bin"', toml)
        self.assertIn('name = "probe"', toml)
        self.assertIn('binary = "chips/flow-meter.chip.wasm"', toml)

    def test_without_a_firmware_it_says_none_was_named(self):
        toml = sim_project.wokwi_toml([])
        self.assertIn("no image named yet", toml)
        self.assertNotIn("[[chip]]", toml)


class WhatTheSimulationCannotShowTest(unittest.TestCase):
    """
    P37. Every stand-in record is REQUIRED to carry this sentence — `parts.py` refuses a built-in
    stand-in without one — and no command printed a single one. The irrigation controller's valve
    driver says it plainly: *"an LED on the gate drive... No opto, no MOSFET, no 12 V load and no
    flyback."* A green scenario over that read exactly like a bench result.
    """

    class FakeDesign:
        def __init__(self, parts):
            self.parts = parts

    @staticmethod
    def part(name, **simulation):
        return {"id": name.lower(), "name": name, "simulation": simulation}

    def test_a_stand_ins_sentence_is_collected(self):
        design = self.FakeDesign([self.part("Valve", wokwi={"part": "wokwi-led", "stand_in": "an LED"})])
        self.assertEqual(sim_project.limits_of(design), [("Valve", "an LED")])

    def test_a_custom_chips_note_counts_too(self):
        # A chip is closer to the part than a stand-in is, and still not the part.
        design = self.FakeDesign([self.part("Tof", wokwi={"chip": "vl6180x", "note": "no optics"})])
        self.assertEqual(sim_project.limits_of(design), [("Tof", "no optics")])

    def test_a_part_nobody_simulates_says_so_with_its_reason(self):
        design = self.FakeDesign([self.part("Jack", skip="a connector is wiring")])
        self.assertEqual(sim_project.limits_of(design),
                         [("Jack", "not simulated at all: a connector is wiring")])

    def test_a_part_that_is_really_simulated_says_nothing(self):
        design = self.FakeDesign([self.part("Btn", wokwi={"part": "wokwi-pushbutton"})])
        self.assertEqual(sim_project.limits_of(design), [])

    def test_identical_sentences_are_grouped(self):
        # Three identical soil probes printed three identical paragraphs, and a finding that long
        # is one that gets scrolled past — which is how this one stayed invisible.
        same = {"part": "wokwi-led", "stand_in": "an LED"}
        design = self.FakeDesign([self.part("Soil1", wokwi=dict(same)),
                                  self.part("Soil3", wokwi=dict(same)),
                                  self.part("Soil2", wokwi=dict(same))])
        self.assertEqual(sim_project.limits_of(design), [("Soil1, Soil2, Soil3", "an LED")])

    def test_the_file_is_actually_written_beside_the_diagram(self):
        import tempfile
        work = Path(tempfile.mkdtemp())
        design = self.FakeDesign([self.part("Valve", wokwi={"part": "wokwi-led", "stand_in": "an LED"})])
        said = sim_project.write_limits(work, design)
        self.assertEqual(said, [("Valve", "an LED")])
        self.assertIn("an LED", (work / "WHAT-THIS-CANNOT-SHOW.md").read_text())

    def test_nothing_is_written_when_nothing_stands_in(self):
        import tempfile
        work = Path(tempfile.mkdtemp())
        design = self.FakeDesign([self.part("Btn", wokwi={"part": "wokwi-pushbutton"})])
        self.assertEqual(sim_project.write_limits(work, design), [])
        self.assertFalse((work / "WHAT-THIS-CANNOT-SHOW.md").exists())

    def test_the_stage_says_it_too_for_the_person_watching_the_run(self):
        import check_spine
        detail = check_spine.simulation_detail(34, {"l9110s": "reused"}, 0,
                                               [("Valve1, Valve2", "no MOSFET")])
        self.assertIn("34 wire(s)", detail)
        self.assertIn("what it cannot show", detail)
        self.assertIn("Valve1, Valve2: no MOSFET", detail)

    def test_a_simulation_with_nothing_to_admit_says_only_what_it_did(self):
        import check_spine
        self.assertEqual(check_spine.simulation_detail(5, {}, 0, []), "5 wire(s) in the diagram")

    def test_the_note_beside_the_diagram_carries_every_line(self):
        # The terminal gets closed; the sim directory is what somebody opens a week later.
        note = sim_project.limits_note([("Valve1, Valve2", "no MOSFET"), ("Jack", "not simulated")])
        self.assertIn("no MOSFET", note)
        self.assertIn("Valve1, Valve2", note)
        self.assertIn("Jack", note)
        self.assertIn("cannot show", note.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
