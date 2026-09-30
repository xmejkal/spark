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

FakeDesign = namedtuple("FakeDesign", "parts project")


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


if __name__ == "__main__":
    unittest.main()
