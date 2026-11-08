"""
The build's two tools (P705): the board engine, tscircuit's `tsci`, found where the tools list says, asked its version
and whether it builds a trivial board; and the diagram converter, found and run. `build_service.run` and
`check_spine.main` read `find_toolchain` through this module, so one patch reaches both.
"""

import json
import os
import subprocess
from pathlib import Path

from spark.records import board_records
from spark.build import build_codes
from spark.build.stages import Stage
from spark.firmware import sim_project
import tools

from spark.core.outcomes import COULD_NOT_RUN, PROBLEMS

#: The probe and the converter are small jobs with their own limit, beside the build's (P659).
PROBE_TIMEOUT_S = 120
CONVERTER_TIMEOUT_S = 120


def find_toolchain(start):
    """
    `tsci`, or None — the board-engine from the tools list (P82): the project's own node_modules,
    upward from `start`, then the PATH — the same places a person would look, and in that order
    because a project's own pinned version beats whatever is installed globally.
    """
    try:
        return Path(tools.find("board-engine", start).command[0])
    except tools.ToolProblem:
        return None


def modules_for(toolchain):
    """
    The `node_modules` a project-local tsci lives in, or None for a global one.

    tsci resolves the emitted board's imports upward from the build directory, so a project's
    own `node_modules` has to be reachable from the working directory; `main` links it in. A
    GLOBAL tsci resolves them from its own install and needs nothing linked — and linking
    `toolchain.parent.parent` for it, which is the Node prefix and not a `node_modules`, put a
    directory with no `react` in it first on the path and broke a toolchain that built the same
    board on its own. That was the "toolchain fault" of audit A9: the spine's fault, not the
    tool's. Measured 2026-09-29: nvm's global 0.0.2600 builds with no link, and fails with the
    prefix linked.
    """
    modules = toolchain.parent.parent
    if toolchain.parent.name == ".bin" and modules.name == "node_modules":
        return modules
    return None


#: The smallest board that should build anywhere: what the preflight asks of a toolchain that
#: produced nothing, to tell "the design is broken" from "the tool is".
TRIVIAL_BOARD = """export default () => (
  <board width="10mm" height="10mm">
    <resistor name="R1" resistance="1k" footprint="0402" />
  </board>
)
"""


def toolchain_can_build(toolchain, workdir):
    """
    Whether this tsci builds a trivial board from this working directory at all.

    Run only after a build produced no circuit.json, so the happy path pays nothing. Returns
    (built, the tool's last words) — the words matter, because "Cannot find package 'react'"
    names a broken install where "no circuit.json" names nothing.
    """
    probe = workdir / "spark-probe"
    probe.mkdir(exist_ok=True)
    (probe / "board.tsx").write_text(TRIVIAL_BOARD)
    result = subprocess.run([str(toolchain), "build", "board.tsx"], cwd=str(probe),
                            capture_output=True, text=True, timeout=PROBE_TIMEOUT_S)
    return (probe / "dist" / "board" / "circuit.json").is_file(), result.stderr.strip()[-400:]


def tsci_version(toolchain):
    """What `tsci --version` says, or "unknown version" — never an exception, never nothing."""
    try:
        said = subprocess.run([str(toolchain), "--version"], capture_output=True, text=True,
                              timeout=60).stdout.strip().splitlines()
        return said[-1].strip() if said else tools.UNKNOWN_VERSION
    except (OSError, subprocess.TimeoutExpired):
        return tools.UNKNOWN_VERSION


#: Where a project may carry its own converter, for its developer; otherwise the tools list's diagram-converter, the
#: plugin's bundle, runs (B10, P82). Searched up from the project, never from the current folder (backlog P32a).
CONVERTER_PATHS = ("tools/circuit-to-wokwi/cli.ts",)


def find_converter(start):
    """A project's own TypeScript converter, for its developer — or None, and the tools list's converter runs.

    Never the plugin's own source: a requirements file in no project resolves to the plugin, and its
    cli.ts needs node_modules an installed plugin does not have (the final review of P82). What the
    plugin ships is the bundle, which the tools list names as the diagram-converter (B10).
    """
    for directory in board_records.walk_up(start):
        for relative in CONVERTER_PATHS:
            candidate = (directory / relative).resolve()
            # A spark checkout's own source — this plugin, or another found walking up — is never a project's.
            if candidate.is_file() and not (directory / "scripts" / "check_spine.py").is_file():
                return candidate
    return None


def converter_command(project, own):
    """The command that converts: a project's own cli.ts under the ts-runtime; else the tools list's
    diagram-converter — the bundle under the js-runtime, or a swapped converter as it is."""
    if own is not None:
        return tools.find("ts-runtime", project).command + ["run", str(own)]
    converter = tools.find("diagram-converter", project)
    if converter.entry.get("kind") == "bundled":
        return tools.find("js-runtime", project).command + converter.command
    return converter.command


def converter_stage_problem(project, own=None):
    """None when the converter and what runs it are here; else the could-not-run Stage saying which and how to install it."""
    try:
        converter_command(project, own)
    except tools.ToolProblem as missing:
        return Stage("simulation", COULD_NOT_RUN, str(missing), build_codes.TOOL_MISSING)
    return None


#: What the converter says when it has no Wokwi part for a component. That is a limit of the
#: converter's mapping table, not a defect in the design — the board built — and reporting it as
#: "the chain is broken" sent a reader to debug a design that was fine (audit B11, A9's shape at
#: the last stage). Matched on the converter's own words, which its tests pin.
CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"


def simulation_could_not_look(said):
    """Whether the converter's output describes its own limit rather than the design's."""
    return CONVERTER_HAS_NO_PART in (said or "")


def convert(project, own, source, sim_dir, workdir):
    """
    The converter run on `source` (["--circuit", path] or ["--netlist", path]) and what `sim_dir` holds, merging into the
    person's kept diagram (P482): (the diagram, None, the merge notes), or (None, the Stage that stopped it, "").
    """
    diagram_path = sim_dir / "diagram.json"
    bad_kept = sim_project.copy_kept_diagram(workdir / sim_project.KEPT_DIAGRAM, sim_dir)
    made = subprocess.run(converter_command(project, own) + source + ["--out", str(diagram_path), "--mapping", str(sim_dir / sim_project.MAPPING_FILE),
                                                                      "--chips", str(sim_dir / "chips")], cwd=str(own.parent if own else sim_dir),
                          capture_output=True, text=True, timeout=CONVERTER_TIMEOUT_S, env=dict(os.environ, SPARK_BOARD_JSON=str(sim_dir / "board.json")))
    if made.returncode or not diagram_path.is_file():
        said = (made.stderr or made.stdout)[-800:]
        if simulation_could_not_look(said):
            return None, Stage("simulation", COULD_NOT_RUN, "the converter has no Wokwi part for a component on this board — a mapping "
                               "to add to its lib/mapping.ts, not a defect in the design, which built\n" + said, build_codes.CONVERTER_LACKS_PART), ""
        return None, Stage("simulation", PROBLEMS, "no diagram was produced\n" + said, build_codes.NO_DIAGRAM), ""
    notes = "".join("\n           " + note for note in (bad_kept, sim_project.kept_note(made.stdout), *sim_project.converter_warnings(made.stdout)) if note)
    return json.loads(diagram_path.read_text()), None, notes
