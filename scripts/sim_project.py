"""
The simulation project a design implies (backlog P31, ordered by the PO 2026-09-29).

Each part record says how it is simulated — `simulation.wokwi` names a Wokwi part standing in or
a custom chip kept beside the record, `simulation.skip` gives the reason a part is absent. This
turns a design into what the converter and the simulator need: a mapping per component name,
the chips staged and compiled to WebAssembly, and the `wokwi.toml` that names them. The chain's
simulation stage calls it; nothing here knows about tscircuit.
"""

import shutil
import subprocess
from pathlib import Path

import emit_board
import parts as parts_library

#: Where wokwi-cli is looked for beyond PATH: where its releases page says to put it.
WOKWI_CLI_HOME = Path.home() / ".local" / "bin" / "wokwi-cli"
INSTALL_HINT = ("install wokwi-cli from github.com/wokwi/wokwi-cli/releases into ~/.local/bin; "
                "`chip compile` runs locally and needs no account")


def find_wokwi_cli():
    """wokwi-cli on PATH or in ~/.local/bin, else None."""
    found = shutil.which("wokwi-cli")
    if found:
        return found
    return str(WOKWI_CLI_HOME) if WOKWI_CLI_HOME.is_file() else None


def mapping_for(design):
    """
    What the converter needs, from the records: (mapping by component name, chips to stage as
    (source folder, chip name), components whose record says nothing as (name, part id)).
    """
    mapping, chips, unmapped = {}, [], []
    for part in design.parts:
        name = emit_board.component_name(part)
        # The passives spark itself placed for this part (P6): a resistor is a resistor, whatever
        # the record says about the module — its own skip must not skip them.
        for host_part in part.get("host_parts") or []:
            values = (host_part.get("top_ohms"), host_part.get("bottom_ohms")) if host_part["kind"] == "divider" else (host_part.get("ohms"),)
            for resistor, ohms in zip(emit_board.host_part_names(part, host_part), values):
                mapping[resistor] = {"wokwiType": "wokwi-resistor", "attrs": {"value": str(ohms)},
                                     "pins": {"anode": "1", "cathode": "2", "pin1": "1", "pin2": "2"}}
        simulation = part.get("simulation")
        if not isinstance(simulation, dict):
            unmapped.append((name, part["id"]))
            continue
        if simulation.get("skip"):
            mapping[name] = {"skip": simulation["skip"]}
            continue
        wokwi = simulation.get("wokwi") or {}
        entry = {"pins": wokwi.get("pins") or {}}
        if wokwi.get("attrs"):
            entry["attrs"] = wokwi["attrs"]
        if wokwi.get("chip"):
            entry["wokwiType"] = "chip-" + wokwi["chip"]
            record = parts_library.definition_path(part["id"], design.project)
            chips.append((parts_library.chip_folder(part, record), wokwi["chip"]))
        else:
            entry["wokwiType"] = wokwi.get("part")
        mapping[name] = entry
    return mapping, list(dict.fromkeys(chips)), unmapped


def limits_of(design):
    """
    What this simulation cannot show, as (component, sentence) — from the records, in their words.

    Every stand-in record is REQUIRED to carry one of these (`parts.py` refuses a built-in
    stand-in without it), and until P37 no command printed a single one. So a green scenario read
    exactly like a bench result. The irrigation controller's valve driver says it plainly: *"an
    LED on the gate drive: lit means the valve is commanded open. No opto, no MOSFET, no 12 V load
    and no flyback."* A passing run over that proves the firmware commanded the valve, and nothing
    whatever about the thing that switches 12 V.

    A custom chip's `note` counts too: a chip is closer to the part than a stand-in is, and still
    not the part.
    """
    said = []
    for part in design.parts:
        wokwi = ((part.get("simulation") or {}).get("wokwi") or {})
        sentence = wokwi.get("stand_in") or wokwi.get("note")
        if sentence:
            said.append((emit_board.component_name(part), sentence))
        skip = (part.get("simulation") or {}).get("skip")
        if skip:
            said.append((emit_board.component_name(part), "not simulated at all: %s" % skip))
    # Grouped by the sentence, because three identical soil probes printed three identical
    # paragraphs and a finding that long gets scrolled past — which is how this one was invisible
    # in the first place.
    together = {}
    for component, sentence in said:
        together.setdefault(sentence, []).append(component)
    return sorted((", ".join(sorted(names)), sentence) for sentence, names in together.items())


def limits_note(limits):
    """The same, as the file a person finds beside the diagram rather than in a terminal they closed."""
    lines = ["# What this simulation cannot show", "",
             "Generated beside the diagram by spark. Every line is a part record's own words.",
             "A scenario passing over any of these proves what the FIRMWARE did, and nothing about",
             "the hardware the stand-in replaced.", ""]
    for component, sentence in limits:
        lines.append("- **%s** — %s" % (component, sentence))
    return "\n".join(lines) + "\n"


def write_limits(sim_dir, design):
    """Put the note beside the diagram and hand back what it said, or () when there is nothing."""
    limits = limits_of(design)
    if limits:
        (Path(sim_dir) / "WHAT-THIS-CANNOT-SHOW.md").write_text(limits_note(limits))
    return limits


def unmapped_detail(unmapped):
    """The could-not-run message: which records to finish, and what to write."""
    return ("no simulation in the record for %s — add `simulation.wokwi` (a stand-in part or a "
            "chip beside the record) or `simulation.skip` with a reason; the design built"
            % ", ".join("%s (%s)" % pair for pair in unmapped))


def stage_chips(chips, sim_dir, compiler=None):
    """
    Copy each chip's sources into `sim_dir/chips/` and see that a binary exists there: a
    binary beside the record no older than its source is reused, anything else is compiled
    with wokwi-cli and the result kept beside the record too. Returns (staged, problems), where
    staged maps each chip to "compiled" or "reused" — the spine printed "2 chip(s) compiled"
    over two binaries from a week before (audit D5), the shape W1 forbids.
    """
    target = sim_dir / "chips"
    staged, problems = {}, []
    for folder, chip in chips:
        target.mkdir(parents=True, exist_ok=True)
        source, binary = folder / (chip + ".chip.c"), folder / (chip + ".chip.wasm")
        for suffix in parts_library.CHIP_SOURCE_SUFFIXES:
            shutil.copy2(folder / (chip + suffix), target / (chip + suffix))
        if binary.is_file() and binary.stat().st_mtime >= source.stat().st_mtime:
            shutil.copy2(binary, target / binary.name)
            staged[chip] = "reused"
        else:
            cli = compiler or find_wokwi_cli()
            if cli is None:
                problems.append("chip %s has no compiled binary and wokwi-cli was not found — %s" % (chip, INSTALL_HINT))
                continue
            made = subprocess.run([cli, "chip", "compile", chip + ".chip.c", "-o", chip + ".chip.wasm"],
                                  cwd=str(target), capture_output=True, text=True)
            if made.returncode != 0 or not (target / binary.name).is_file():
                problems.append("chip %s did not compile:\n%s" % (chip, (made.stderr or made.stdout)[-600:]))
                continue
            shutil.copy2(target / binary.name, binary)
            staged[chip] = "compiled"
    return staged, problems


def wokwi_toml(chips, firmware=None):
    """The simulator's project file: the firmware image, and every chip by name and binary."""
    lines = ["# Written by spark from the part records. The chips stand in for parts Wokwi has no model of.",
             "[wokwi]", "version = 1"]
    if firmware:
        lines += ['firmware = "%s"' % firmware, 'elf = "%s"' % firmware]
    else:
        lines += ['# firmware = "flash-with-firmware.bin"  # no image named yet: MicroPython plus the project\'s files']
    for chip in chips:
        lines += ["", "[[chip]]", 'name = "%s"' % chip, 'binary = "chips/%s.chip.wasm"' % chip]
    return "\n".join(lines) + "\n"
