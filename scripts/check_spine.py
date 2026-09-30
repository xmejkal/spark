#!/usr/bin/env python3
"""
The one thing that has to work: a module list in, a board that builds out.

    check_spine.py                       # the reference design that ships with spark
    check_spine.py my-requirements.json  # your own
    check_spine.py --json

WHY THIS EXISTS

spark is a chain — parts, pin assignment, schematic, footprint, build — and every link had its
own tests, all green, while the chain itself had never once been run end to end. It produced a
board with zero traces for weeks under a docstring that said it "BUILDS", and four independent
defects were sitting in it, each alone enough to cause that:

  * a part file whose footprint said five pads and whose pinout named seven,
  * a missing footprint quietly defaulting to a four-pad one,
  * a rule named `rails_without_a_source` that never looked for a source,
  * and its mirror, warning that a correctly-supplied rail went nowhere.

None of them was findable from a unit test, because each component did exactly what its own
tests asked. They were only visible by running the whole thing and counting what came out.

WHAT IT MEANS TO PASS

Not "no exception was raised". A board is only built if copper reached it:

    the build succeeds, AND at least one pcb_trace exists, AND no *_error element is present

The trace count is the load-bearing clause. tscircuit's autorouter can fail on a single
unroutable net and skip routing entirely, which does not raise — it returns a circuit with every
component placed, every port present, and no copper at all. That artefact passes every structural
check that does not think to count traces, and it is exactly what this tool shipped.

WHAT IT REFUSES TO CALL A PASS

If `tsci` is not installed, the build stage is `could-not-run` and the exit code says so. A chain
that could not be exercised has not been proven; it has been skipped, and the difference is the
whole point of this file.

If it IS installed and cannot build a trivial board from the working directory, the same. A tool
that fails on a resistor is not reporting on the design, and "the chain is broken" for a broken
tool sends somebody to debug a design nobody examined — the mirror image of a false pass, and as
misleading. Every build verdict names the tsci that produced it, because "exit 0" once depended
on which one PATH found first, and nothing said so.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
import design  # noqa: E402
import emit_board  # noqa: E402
import sim_project  # noqa: E402
import emit_footprint  # noqa: E402

from outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN  # noqa: E402

from outcomes import OK, PROBLEMS, COULD_NOT_RUN  # noqa: E402

#: The design the chain is proven against when nobody names one. A motor driver, a sensor on a
#: bus, and the power inlet that supplies the rail the modules only consume — the smallest set
#: that exercises pin assignment, a bus, a rail with an external source, and two footprint kinds.
REFERENCE = {"board": "firebeetle2-esp32s3",
             "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}

BUILD_TIMEOUT_S = 300


class Stage:
    """One link, and what became of it."""

    def __init__(self, name, status, detail=""):
        self.name, self.status, self.detail = name, status, detail

    def __repr__(self):
        return "Stage(%r, %r)" % (self.name, self.status)


def find_toolchain(start):
    """
    `tsci`, or None.

    Looked for beside the requirements file, then upward, then on PATH — the same places a person
    would look, and in that order because a project's own pinned version beats whatever is
    installed globally.
    """
    for directory in boards.walk_up(start):
        candidate = directory / "node_modules" / ".bin" / "tsci"
        if candidate.is_file():
            return candidate
    found = shutil.which("tsci")
    return Path(found) if found else None


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
                            capture_output=True, text=True, timeout=BUILD_TIMEOUT_S)
    return (probe / "dist" / "board" / "circuit.json").is_file(), result.stderr.strip()[-400:]


def tsci_version(toolchain):
    """What `tsci --version` says, or "unknown version" — never an exception, never nothing."""
    try:
        said = subprocess.run([str(toolchain), "--version"], capture_output=True, text=True,
                              timeout=60).stdout.strip().splitlines()
        return said[-1].strip() if said else "unknown version"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown version"


#: Where the circuit.json -> Wokwi diagram.json converter might be. It is not part of this
#: plugin yet: it lives in the project that proved it, and moving ~1800 lines of TypeScript into
#: a Python plugin is a structural decision nobody has made. Until then this stage is honest
#: about not having run rather than absent, because "the spine reaches simulation" is the whole
#: product goal and a chain that quietly stops at `build` misrepresents it.
CONVERTER_PATHS = (
    "tools/circuit-to-wokwi/cli.ts",
    "../smartbin-local/tools/circuit-to-wokwi/cli.ts",
)


def find_converter(start):
    """The circuit-to-Wokwi converter, or None."""
    for directory in boards.walk_up(start):
        for relative in CONVERTER_PATHS:
            candidate = (directory / relative).resolve()
            if candidate.is_file():
                return candidate
    return None


#: What the converter says when it has no Wokwi part for a component. That is a limit of the
#: converter's mapping table, not a defect in the design — the board built — and reporting it as
#: "the chain is broken" sent a reader to debug a design that was fine (audit B11, A9's shape at
#: the last stage). Matched on the converter's own words, which its tests pin.
CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"


def simulation_could_not_look(said):
    """Whether the converter's output describes its own limit rather than the design's."""
    return CONVERTER_HAS_NO_PART in (said or "")


def wires_in(diagram):
    """How many connections the emitted diagram makes."""
    return len(diagram.get("connections") or [])


def count_in(circuit):
    """Traces and errors, which is what 'did it build' actually means."""
    traces = sum(1 for element in circuit if element.get("type") == "pcb_trace")
    errors = [element for element in circuit if "error" in (element.get("type") or "")]
    return traces, errors


#: Nets that are a ground: the generator's list, so this rule and its supply rule agree.
GROUND_NETS = emit_board.GROUND_NETS
#: tscircuit's types for the two-terminal parts a generated board places between a pin and a rail.
PASSIVE_FTYPES = ("simple_resistor", "simple_capacitor", "simple_inductor", "simple_diode")


def components_not_on_ground(circuit):
    """
    Every component that reaches no ground net, by name.

    A component can be perfectly placed, carry every pad, route its signals and still share no
    return path with anything. Nothing in a build flags it: tscircuit checks that each trace you
    asked for is satisfiable, never that you asked for the ones a circuit needs.

    Connection is counted through the source netlist rather than through copper, because a pin on
    a poured net has no trace of its own and is connected all the same.
    """
    names, grounded, present, traced = {}, set(), set(), set()
    ground_ids = {element["source_net_id"] for element in circuit
                  if element.get("type") == "source_net"
                  and (element.get("name") or "").upper() in GROUND_NETS}
    passives = set()
    for element in circuit:
        if element.get("type") == "source_component":
            names[element["source_component_id"]] = element.get("name") or "?"
            if element.get("ftype") in PASSIVE_FTYPES:
                passives.add(element["source_component_id"])
    ports = {element["source_port_id"]: element for element in circuit
             if element.get("type") == "source_port"}
    for element in circuit:
        if element.get("type") != "source_trace":
            continue
        on_ground = bool(set(element.get("connected_source_net_ids") or []) & ground_ids)
        port_ids = [port_id for port_id in element.get("connected_source_port_ids") or [] if port_id in ports]
        traced.update(port_ids)
        owners = {ports[port_id].get("source_component_id") for port_id in port_ids}
        present |= owners
        if on_ground:
            grounded |= owners
    # A component with no trace at all is a separate complaint, already covered by the parts that
    # refuse to emit. Report only those that are wired to something and to no ground — for a
    # chip. A two-terminal passive is asked a different question: a pull-up, or the top of a
    # divider, sits between a pin and a rail and reaches no ground BY DESIGN, and was reported
    # here as an island the evening P6 placed the first ones. What must hold for it is that
    # neither end dangles.
    findings = [names.get(owner, "?") for owner in present - grounded if owner not in passives]
    findings += ["%s.%s (a terminal connected to nothing)" % (names.get(port.get("source_component_id"), "?"), port.get("name") or port_id)
                 for port_id, port in ports.items() if port.get("source_component_id") in present & passives and port_id not in traced]
    return sorted(findings)


def run(requirements, workdir, toolchain=None, project=None, from_library=False, firmware=None):
    """
    Every stage, in order, stopping at the first that cannot produce input for the next.

    `project` is where the design's parts and rules live, resolved by `main` from the
    requirements FILE — never from the current directory. Resolved from `cwd`, a run from
    anywhere but inside the project said `no part called 'sg90-servo'` about a part sitting
    beside the file. None means the plugin's own library, which is what the reference design is
    built from and must not require a surrounding project for.
    """
    stages = []
    project = project or SCRIPTS.parent

    # --- parts and pin assignment, via the generator that owns them ---
    try:
        board = boards.load(project, requirements.get("board"))
    except Exception as exc:  # noqa: BLE001
        return stages + [Stage("board", COULD_NOT_RUN, str(exc))]
    stages.append(Stage("board", OK, board["name"] + (
        " — from the plugin's library; no project up from the requirements file, so no rules"
        if from_library else "")))

    # Nothing to build is not a pass. An empty parts list came out `ok` end to end — two traces
    # (the processor's own ground and 3.3 V) and two wires — which proves nothing about the chain
    # and reads as though it did. Intake row M3 had it as `problems` on 09-25; both were wrong.
    if not requirements.get("parts"):
        return stages + [Stage("parts", COULD_NOT_RUN,
                               "the requirements name no parts, so there is nothing to build; a "
                               "board holding only the microcontroller proves nothing")]

    board_file = workdir / "board.tsx"
    emitted = subprocess.run(
        [sys.executable, str(SCRIPTS / "emit_board.py"), str(workdir / "requirements.json"),
         "--project", str(project), "--assume-missing-sizes"],
        capture_output=True, text=True)
    if emitted.returncode != 0:
        # emit_board distinguishes the two, and so must this. "It refused because a part has no
        # measured outline" and "it produced a broken design" send a person to different places.
        refused = emitted.returncode == emit_board.EXIT_COULD_NOT_RUN
        return stages + [Stage("schematic", COULD_NOT_RUN if refused else PROBLEMS,
                               emitted.stderr.strip())]
    board_file.write_text(emitted.stdout)
    traces_asked = emitted.stdout.count("<trace ")
    stages.append(Stage("schematic", OK, "%d trace(s) written" % traces_asked))
    if emitted.stderr.strip():
        stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip()))

    # --- the footprint the schematic imports ---
    export = (board.get("physical") or {}).get("footprint_export")
    footprint = emit_footprint.main(
        ["--board", board["id"], "--project", str(project),
         "-o", str(workdir / ("%s.tsx" % export))])
    if footprint != emit_footprint.EXIT_OK:
        return stages + [Stage("footprint", COULD_NOT_RUN,
                               "no footprint could be generated for %s" % board["id"])]
    stages.append(Stage("footprint", OK, "%s.tsx" % export))

    # --- the build, which is the only stage that can prove any of the above ---
    toolchain = toolchain or find_toolchain(workdir)
    if toolchain is None:
        return stages + [Stage("build", COULD_NOT_RUN,
                               "tsci is not installed, so the chain was not exercised. "
                               "npm i -g @tscircuit/cli, or run from a project that has it")]

    built = subprocess.run([str(toolchain), "build", "board.tsx"],
                           cwd=str(workdir), capture_output=True, text=True,
                           timeout=BUILD_TIMEOUT_S)
    version = tsci_version(toolchain)
    circuit_path = workdir / "dist" / "board" / "circuit.json"
    if not circuit_path.is_file():
        # Nothing came out. Before blaming the design, ask the same tool for a resistor on a
        # board: a tool that cannot build that is not reporting on the design at all.
        can, last_words = toolchain_can_build(toolchain, workdir)
        if not can:
            return stages + [Stage("build", COULD_NOT_RUN,
                                   "%s (%s) cannot build even a trivial board from here, so this "
                                   "is the toolchain, not the design. Use the project's own tsci "
                                   "(npm i @tscircuit/cli in the project) or one that builds on "
                                   "its own.\n%s" % (toolchain, version, last_words))]
        return stages + [Stage("build", PROBLEMS,
                               "no circuit.json was produced by %s (%s), which does build a "
                               "trivial board\n%s" % (toolchain, version,
                                                      built.stderr.strip()[-800:]))]

    traces, errors = count_in(json.loads(circuit_path.read_text()))
    # NOT a trace count. Comparing connections asked for against `pcb_trace`s is wrong twice
    # over, and was tried here first: a net with N members needs N-1 traces, and a pin on a
    # poured net (V33 and GND are poured, 53 pours on this board) is connected by copper with no
    # trace at all. That rule failed a correct board, which is the mirror of the defect it was
    # chasing.
    #
    # The real invariant is grounding. The defect that prompted this was a microcontroller
    # sharing a net with NONE of its 32 pins — no ground, no 3.3 V — on a board that built,
    # routed and reported zero errors, while every module around it was correctly wired to a
    # ground the processor was not on.
    ungrounded = components_not_on_ground(json.loads(circuit_path.read_text()))
    if ungrounded:
        return stages + [Stage("build", PROBLEMS,
                               "%s no ground. A board builds, routes and reports no error with "
                               "a component grounded to nothing — the parts around it are wired "
                               "to a net it is simply not on"
                               % (("%s reaches" % ungrounded[0]) if len(ungrounded) == 1
                                  else ("%s reach" % ", ".join(ungrounded))))]
    if errors:
        kinds = sorted({element["type"] for element in errors})
        return stages + [Stage("build", PROBLEMS, "%d error(s): %s" % (len(errors),
                                                                      ", ".join(kinds)))]
    if traces == 0:
        # The failure this file was written for. Everything is placed, nothing is connected, and
        # no exception was raised anywhere.
        return stages + [Stage("build", PROBLEMS,
                               "built with 0 pcb_traces — every component is placed and no "
                               "copper joins any of them. tscircuit skips routing entirely when "
                               "one net is unroutable, and that does not raise")]
    stages.append(Stage("build", OK, "%d trace(s), 0 errors, tsci %s" % (traces, version)))

    # --- simulation: the last step of the product goal -------------------------
    # From the project, not from `cwd`: the same defect the project resolution had, one stage
    # later — run from /tmp the converter beside the project was "not found".
    converter = find_converter(project)
    if converter is None:
        return stages + [Stage("simulation", COULD_NOT_RUN,
                               "no circuit-to-wokwi converter found. It is not shipped with this "
                               "plugin yet — it lives in the project that proved it. Looked for: "
                               + ", ".join(CONVERTER_PATHS))]
    if shutil.which("bun") is None:
        return stages + [Stage("simulation", COULD_NOT_RUN,
                               "the converter is TypeScript and bun is not installed")]

    # What stands in for each part comes from the records (P31), not from a table in the
    # converter's repo: a record that says nothing stops here, naming itself.
    loaded = design.load(workdir / "requirements.json", None if from_library else project)
    mapping, chips, unmapped = sim_project.mapping_for(loaded)
    if unmapped:
        return stages + [Stage("simulation", COULD_NOT_RUN, sim_project.unmapped_detail(unmapped))]
    sim_dir = workdir / "sim"
    sim_dir.mkdir(exist_ok=True)
    (sim_dir / "wokwi-mapping.json").write_text(json.dumps(mapping, indent=2) + "\n")
    (sim_dir / "board.json").write_text(json.dumps(board, indent=2) + "\n")
    staged, chip_problems = sim_project.stage_chips(chips, sim_dir)
    if chip_problems:
        return stages + [Stage("simulation", COULD_NOT_RUN, "\n".join(chip_problems))]
    (sim_dir / "wokwi.toml").write_text(sim_project.wokwi_toml(staged, firmware))

    diagram_path = sim_dir / "diagram.json"
    made = subprocess.run(
        ["bun", "run", str(converter), "--circuit", str(circuit_path), "--out", str(diagram_path),
         "--mapping", str(sim_dir / "wokwi-mapping.json"), "--chips", str(sim_dir / "chips")],
        cwd=str(converter.parent), capture_output=True, text=True, timeout=BUILD_TIMEOUT_S,
        env=dict(os.environ, SPARK_BOARD_JSON=str(sim_dir / "board.json")))
    if not diagram_path.is_file():
        said = (made.stderr or made.stdout)[-800:]
        if simulation_could_not_look(said):
            return stages + [Stage("simulation", COULD_NOT_RUN,
                                   "the converter has no Wokwi part for a component on this board "
                                   "— a mapping to add to its lib/mapping.ts, not a defect in the "
                                   "design, which built\n" + said)]
        return stages + [Stage("simulation", PROBLEMS, "no diagram was produced\n" + said)]

    wires = wires_in(json.loads(diagram_path.read_text()))
    if wires == 0:
        # The same failure shape as a board with no copper: every part placed, nothing joined.
        return stages + [Stage("simulation", PROBLEMS,
                               "a diagram with 0 connections. Every part is placed and none is "
                               "wired, which is what an unmapped component looks like once the "
                               "converter has given up on it")]
    compiled = sum(1 for how in staged.values() if how == "compiled")
    return stages + [Stage("simulation", OK, "%d wire(s) in the diagram%s" % (
        wires, ", %d chip(s): %d compiled, %d reused" % (len(staged), compiled, len(staged) - compiled) if staged else ""))]


def verdict(stages):
    if any(stage.status == PROBLEMS for stage in stages):
        return EXIT_PROBLEMS
    if any(stage.status == COULD_NOT_RUN for stage in stages):
        return EXIT_COULD_NOT_RUN
    return EXIT_OK


def render(stages, code):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????"}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation", ""]
    for stage in stages:
        lines.append("  [%s] %-16s %s" % (mark[stage.status], stage.name, stage.detail))
    lines.append("")
    lines.append({
        EXIT_OK: "  the chain runs end to end",
        EXIT_PROBLEMS: "  the chain is broken",
        EXIT_COULD_NOT_RUN: "  the chain was NOT exercised — this is not a pass",
    }[code])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("requirements", nargs="?",
                        help="a requirements.json; omit for the reference design")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep", action="store_true", help="leave the working directory behind")
    parser.add_argument("--sim-dir", type=Path, metavar="DIR",
                        help="keep the simulation project here: diagram.json, wokwi.toml, the chips")
    parser.add_argument("--firmware", metavar="IMAGE",
                        help="the flash image wokwi.toml names, relative to the sim dir (flash_image.py writes one)")
    args = parser.parse_args(argv)

    # The input is read before anything runs, and read AS input: a malformed file is a stage
    # that could not run, not a traceback with exit 1 — which is "the chain is broken" to anyone
    # reading the code. The project is the file's, up from its own directory, so a design
    # belongs to its parts wherever the command is typed; a file inside no project at all is
    # built from the plugin's library, like the reference design.
    source = Path(args.requirements).resolve() if args.requirements else None
    try:
        requirements = design.read(source) if source else dict(REFERENCE)
    except design.DesignError as broken:
        return report([Stage("requirements", COULD_NOT_RUN, str(broken))], args)
    # A file in no project is built from the plugin's library, and the board stage says so.
    project = design.project_for(source) if source else None
    from_library = bool(source) and design.is_library(project)

    workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))
    (workdir / "requirements.json").write_text(json.dumps(requirements))
    # tsci needs its toolchain reachable from the build directory.
    toolchain = find_toolchain(source.parent if source else Path.cwd())
    modules = modules_for(toolchain) if toolchain is not None else None
    if modules is not None and not (workdir / "node_modules").exists():
        os.symlink(modules, workdir / "node_modules")

    try:
        stages = run(requirements, workdir, toolchain, project, from_library, firmware=args.firmware)
    except subprocess.TimeoutExpired:
        stages = [Stage("build", COULD_NOT_RUN,
                        "the build did not finish in %ds" % BUILD_TIMEOUT_S)]
    except Exception as exc:  # noqa: BLE001
        # Anything unforeseen is could-not-run, never problems. An exception says this tool
        # failed, which is not the same as the chain failing, and reporting one as the other
        # sends somebody to debug a design that was never examined.
        stages = [Stage("check_spine", COULD_NOT_RUN,
                        "%s: %s" % (type(exc).__name__, exc))]

    if args.sim_dir and (workdir / "sim").is_dir():
        shutil.copytree(workdir / "sim", args.sim_dir, dirs_exist_ok=True)
        print("simulation project kept in %s" % args.sim_dir, file=sys.stderr)
    return report(stages, args, workdir)


def report(stages, args, workdir=None):
    """The verdict, rendered the way it was asked for; the working directory kept or removed."""
    code = verdict(stages)
    if args.json:
        print(json.dumps({"check": "spine", "status": {EXIT_OK: OK, EXIT_PROBLEMS: PROBLEMS,
                                                       EXIT_COULD_NOT_RUN: COULD_NOT_RUN}[code],
                          "stages": [{"name": s.name, "status": s.status, "detail": s.detail}
                                     for s in stages]}))
    else:
        sys.stdout.write(render(stages, code))
    if workdir is None:
        return code
    if args.keep:
        print("  working directory: %s" % workdir, file=sys.stderr)
    elif workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
