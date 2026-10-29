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
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Optional

import boards
import emit_board
from spark.core import outcomes
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


# --- MVP ---
#: The note's file name, in the simulation project's folder: `write_limits` writes it, run_scenario.py copies it into a log and
#: `check_spine.keep_simulation` removes an older one.
LIMITS_NOTE = "WHAT-THIS-CANNOT-SHOW.md"
#: How a limit line of the note begins, how its component is marked and what comes between the component and the sentence:
#: `limits_note` writes `- **component** — sentence`, and `limits_in` reads it back.
LIMIT_PREFIX, LIMIT_MARK, LIMIT_DASH = "- ", "**", " — "


class Limit(NamedTuple):
    """Value: one limit of the note, what the simulation cannot show of a `component`. The component is "" when a line has no shape of `limits_note`'s."""

    component: str
    sentence: str


def limits_in(note_text):
    """
    The Limits a note's text holds, in order, as `limits_note` wrote them; it never raises. The lines before the first limit line
    are skipped. A limit line that does not continue the shape `- **component** — sentence` gives the component "" and the text
    after the prefix. A line without the prefix after the first limit joins the limit above it with a space, since
    `limits_note` writes a sentence with a line break as it is. A blank line ends the limit above it, so a closing paragraph that
    a person adds is no part of it. A limit whose sentence is empty is dropped.
    """
    found, open_limit = [], False
    for line in note_text.splitlines():
        if line.startswith(LIMIT_PREFIX):
            found.append(_limit_of(line[len(LIMIT_PREFIX):]))
            open_limit = True
        elif not line.strip():
            open_limit = False
        elif open_limit:
            found[-1] = Limit(found[-1].component, ("%s %s" % (found[-1].sentence, line.strip())).strip())
    return [limit for limit in found if limit.sentence]


def _limit_of(text):
    """The Limit of one limit line, after its prefix."""
    end = text.find(LIMIT_MARK, len(LIMIT_MARK))
    if text.startswith(LIMIT_MARK) and end > 0 and text[end + len(LIMIT_MARK):].startswith(LIMIT_DASH):
        return Limit(text[len(LIMIT_MARK):end], text[end + len(LIMIT_MARK) + len(LIMIT_DASH):].strip())
    return Limit("", text.strip())
# --- end MVP ---


def _one_paragraph(sentence):
    """The sentence with its blank and whitespace-only lines removed and the rest joined by one space, so the reader never meets a blank line inside a limit."""
    return " ".join(line for line in sentence.splitlines() if line.strip())


def limits_note(limits):
    """The same, as the file a person finds beside the diagram rather than in a terminal they closed."""
    lines = ["# What this simulation cannot show", "",
             "Generated beside the diagram by spark. Most lines come from a part record's own words, or from",
             "the board's Wokwi definition: the JSON file of the Wokwi part type that spark keeps in its store.",
             "The rest say what spark did not check or leaves out of the diagram.",
             "A scenario passing over any of these proves what the FIRMWARE did, and nothing about",
             "the hardware the stand-in replaced or the board's part that Wokwi lacks.", ""]
    for component, sentence in limits:
        lines.append(LIMIT_PREFIX + LIMIT_MARK + component + LIMIT_MARK + LIMIT_DASH + _one_paragraph(sentence))
    return "\n".join(lines) + "\n"


def write_limits(sim_dir, design, board):
    """
    Put the note beside the diagram and hand back what it said, or [] when there is nothing. The design's records and the
    board's own GPIOs both count (P396), and a board-only build passes no design. `board` has no default: no test reaches
    the full build's simulation stage (`check_spine.simulation_detail`), so a call that drops it fails at once.
    """
    limits = (limits_of(design) if design is not None else []) + boards.onboard_limits(board)
    if limits:
        (Path(sim_dir) / LIMITS_NOTE).write_text(limits_note(limits))
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


#: How `why` begins when the file itself cannot be read, and not one of its lines.
CANNOT_READ = "cannot be read: "

#: How a wokwi.toml line names the flash image: `wokwi_toml` writes it, and `firmware_in` reads it.
FIRMWARE_LINE = "firmware = "


# --- MVP ---
@dataclass(frozen=True)
class FirmwareLine:
    """
    Value: what a wokwi.toml says of its flash image (P429). `state` is one of the three words of `outcomes` (the reader
    rule, OC4): `name` holds the file name only when it is RECORDED, and `why` says what stopped the reader only when it
    is NOT_CHECKED, as a sentence without the file's name (a caller puts that first). `name` is whatever non-empty string the
    file holds: where it may point is `why_outside_sim`'s rule, which the run and the project's image apply, not the reader.
    """

    state: str
    name: Optional[str] = None
    why: Optional[str] = None

    def fix(self):
        """What to add after `why` when a person can rewrite the line: the form to write, or "" when the file cannot be read."""
        return "" if self.why is None or self.why.startswith(CANNOT_READ) else ' To fix it, write it as firmware = "name.bin".'


def firmware_in(toml):
    """
    The flash image a kept wokwi.toml names, as a FirmwareLine; never raises (P196's refuter, P429). A rebuild with no
    --firmware keeps running it, where it used to rewrite the line commented out. `wokwi_toml` writes the value as a JSON
    string after `firmware = ` at the start of the line, and only that form is read. No file, or no line that starts with
    `firmware`: NONE_RECORDED. A file that cannot be read, or a first such line in any other form (indented, no spaces
    around the `=`, a value that is no JSON string, or an empty one): NOT_CHECKED, because wokwi-cli reads full TOML and
    would take an image that this does not.
    """
    try:
        lines = Path(toml).read_text().splitlines()
    except FileNotFoundError:
        return FirmwareLine(outcomes.NONE_RECORDED)
    except (OSError, ValueError) as cannot:  # ValueError: bytes that are no text
        reason = getattr(cannot, "strerror", None) or "it is not text in UTF-8"
        return FirmwareLine(outcomes.NOT_CHECKED, why=CANNOT_READ + reason + ".")
    for number, line in enumerate(lines, 1):
        if not line.strip().startswith("firmware"):
            continue
        try:
            name = json.loads(line[len(FIRMWARE_LINE):]) if line.startswith(FIRMWARE_LINE) else None
        except (ValueError, RecursionError):
            name = None
        if isinstance(name, str) and name:
            return FirmwareLine(outcomes.RECORDED, name)
        if name == "":
            return FirmwareLine(outcomes.NOT_CHECKED, why="line %d names no file." % number)
        return FirmwareLine(outcomes.NOT_CHECKED, why="line %d names the firmware in a form spark cannot read." % number)
    return FirmwareLine(outcomes.NONE_RECORDED)
# --- end MVP ---


def why_outside_sim(sim, image):
    """The sentence that refuses an image outside the sim folder, or None when it is inside. A run writes its image, so it
    only writes inside sim/, and the look and the deploy refuse the same image: they would flash a file no run made."""
    try:
        outside = Path(sim).resolve() not in Path(image).resolve().parents
    except (OSError, ValueError, RuntimeError):  # a null byte in the name, a link loop
        outside = True
    return "wokwi.toml names %s, outside sim/, and a run writes its image only inside sim/" % image if outside else None


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
