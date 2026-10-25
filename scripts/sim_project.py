"""
The simulation project a design implies (backlog P31, ordered by the PO 2026-09-29).

Each part record says how it is simulated — `simulation.wokwi` names a Wokwi part standing in or
a custom chip kept beside the record, `simulation.skip` gives the reason a part is absent. This
turns a design into what the converter and the simulator need: a mapping per component name,
the chips staged and compiled to WebAssembly, and the `wokwi.toml` that names them. The chain's
simulation stage calls it; nothing here knows about tscircuit.
"""

import json
import shutil
import subprocess
from pathlib import Path

import boards
import emit_board
import parts as parts_library
import tools

def find_wokwi_cli(project=None):
    """wokwi-cli, wherever the tools list says to look (PATH, ~/.local/bin, spark's downloads), else None."""
    try:
        return tools.find("simulator", project).command[0]
    except tools.ToolProblem:
        return None


def simulator_problem(project=None):
    """Why there is no wokwi-cli, in the tools list's own words with its install line — or None when it is here."""
    try:
        tools.find("simulator", project)
    except tools.ToolProblem as missing:
        return str(missing)
    return None


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
            values = ((host_part.get("top_ohms"), host_part.get("bottom_ohms")) if host_part["kind"] == "divider"
                      else (emit_board.series_ohms(part, host_part, design.board)[0],) if host_part["kind"] == "series"
                      else (host_part.get("ohms"),))
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
             "Generated beside the diagram by spark. Every line comes from a part record's own words, or from",
             "the board's Wokwi definition: the JSON file of the Wokwi part type that spark keeps in its store,",
             "or says what spark did not check.",
             "A scenario passing over any of these proves what the FIRMWARE did, and nothing about",
             "the hardware the stand-in replaced or the board's part that Wokwi lacks.", ""]
    for component, sentence in limits:
        lines.append("- **%s** — %s" % (component, sentence))
    return "\n".join(lines) + "\n"


# --- MVP ---
#: The component of a limit about the board's own GPIOs as a whole, and the two reasons they were not compared.
ONBOARD_GPIOS = "onboard GPIOs"
NO_DEFINITION_NAMED = "not checked: the board record names no Wokwi definition"
DEFINITION_NOT_KEPT = ("not checked: spark's store lacks the Wokwi definition that the board record names, its sha256 "
                       "differs, or it does not parse")


def onboard_limits(board):
    """
    The board's own LED and button that its Wokwi definition gives no pin, as (component, sentence) limits (P396).
    Spark knows no way for a scenario to reach them, so a passed run does not test them. A board with no onboard LED
    or button gives []. A record that cannot be compared says "not checked", in the list and never as a failure: it is
    what the build did not look at, as a stand-in's sentence is what the simulation cannot show (P37).
    """
    roles = [(spec, entry) for _, spec, entry in boards.onboard_entries(board) if spec.scenario_verb]
    if not roles:
        return []
    documents = board.get("documents") if isinstance(board.get("documents"), dict) else {}
    if boards.WOKWI_DEFINITION not in documents:
        return [(ONBOARD_GPIOS, NO_DEFINITION_NAMED)]
    part = boards.read_simulated_part(board)
    if part is None:
        return [(ONBOARD_GPIOS, DEFINITION_NOT_KEPT)]
    said = []
    for spec, entry in roles:
        gpios = entry.get("gpio") if isinstance(entry.get("gpio"), list) else []
        for gpio in (gpio for gpio in gpios if isinstance(gpio, int) and not isinstance(gpio, bool)):
            why = part.why_not_simulated(gpio)
            if why:
                said.append(("%s (GPIO%d)" % (spec.constant, gpio),
                             "%s, so spark knows no way for a scenario to %s it. Test it on the board."
                             % (why, spec.scenario_verb)))
    return said
# --- end MVP ---


def write_limits(sim_dir, design, board):
    """
    Put the note beside the diagram and hand back what it said, or [] when there is nothing. The design's records and the
    board's own GPIOs both count (P396), and a board-only build passes no design. `board` has no default: no test reaches
    the full build's simulation stage (`check_spine.simulation_detail`), so a call that drops it fails at once.
    """
    limits = (limits_of(design) if design is not None else []) + onboard_limits(board)
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
                problems.append("chip %s has no compiled binary — %s; `chip compile` runs locally and needs no account"
                                % (chip, simulator_problem() or "wokwi-cli was not found"))
                continue
            made = subprocess.run([cli, "chip", "compile", chip + ".chip.c", "-o", chip + ".chip.wasm"],
                                  cwd=str(target), capture_output=True, text=True)
            if made.returncode != 0 or not (target / binary.name).is_file():
                problems.append("chip %s did not compile:\n%s" % (chip, (made.stderr or made.stdout)[-600:]))
                continue
            shutil.copy2(target / binary.name, binary)
            staged[chip] = "compiled"
    return staged, problems


#: How a wokwi.toml line names the flash image: `wokwi_toml` writes it, and `firmware_in` reads it.
FIRMWARE_LINE = "firmware = "


def firmware_in(toml):
    """
    The flash image a kept wokwi.toml names, or None (P196's refuter): a rebuild with no --firmware keeps running it,
    where it used to rewrite the line commented out. `wokwi_toml` writes the value as a JSON string, so it reads back so.
    """
    try:
        lines = Path(toml).read_text().splitlines()
        named = [line[len(FIRMWARE_LINE):] for line in lines if line.startswith(FIRMWARE_LINE)]
        return json.loads(named[0]) if named else None
    except (OSError, ValueError):
        return None


#: The line wokwi_toml writes when no image is named yet. wokwi-cli refuses such a file, so run_scenario.py names one here.
UNNAMED_FIRMWARE = '# firmware = "flash-with-firmware.bin"  # no image named yet: MicroPython plus the project\'s files'


def firmware_lines(firmware):
    """The two lines that name the flash image. Each value is a JSON string, which TOML reads as its basic string: a quote
    or a line break in the person's own --firmware stays inside its value, and the file keeps the structure written here."""
    return [FIRMWARE_LINE + json.dumps(firmware), "elf = %s" % json.dumps(firmware)]


def wokwi_toml(chips, firmware=None):
    """The simulator's project file: the firmware image, and every chip by name and binary."""
    lines = ["# Written by spark from the part records. The chips stand in for parts Wokwi has no model of.",
             "[wokwi]", "version = 1"]
    lines += firmware_lines(firmware) if firmware else [UNNAMED_FIRMWARE]
    for chip in chips:
        lines += ["", "[[chip]]", "name = %s" % json.dumps(chip), "binary = %s" % json.dumps("chips/%s.chip.wasm" % chip)]
    return "\n".join(lines) + "\n"
