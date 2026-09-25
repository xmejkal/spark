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
import emit_board  # noqa: E402
import emit_footprint  # noqa: E402

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

OK, PROBLEMS, COULD_NOT_RUN = "ok", "problems", "could-not-run"

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
    for directory in [start, *start.parents]:
        candidate = directory / "node_modules" / ".bin" / "tsci"
        if candidate.is_file():
            return candidate
    found = shutil.which("tsci")
    return Path(found) if found else None


def count_in(circuit):
    """Traces and errors, which is what 'did it build' actually means."""
    traces = sum(1 for element in circuit if element.get("type") == "pcb_trace")
    errors = [element for element in circuit if "error" in (element.get("type") or "")]
    return traces, errors


#: Nets that are a ground. Named rather than guessed, because "the one called GND" stops being
#: true the moment a design has an analogue ground or an isolated return.
GROUND_NETS = ("GND", "AGND", "DGND", "GROUND")


def components_not_on_ground(circuit):
    """
    Every component that reaches no ground net, by name.

    A component can be perfectly placed, carry every pad, route its signals and still share no
    return path with anything. Nothing in a build flags it: tscircuit checks that each trace you
    asked for is satisfiable, never that you asked for the ones a circuit needs.

    Connection is counted through the source netlist rather than through copper, because a pin on
    a poured net has no trace of its own and is connected all the same.
    """
    names, grounded, present = {}, set(), set()
    ground_ids = {element["source_net_id"] for element in circuit
                  if element.get("type") == "source_net"
                  and (element.get("name") or "").upper() in GROUND_NETS}
    for element in circuit:
        if element.get("type") == "source_component":
            names[element["source_component_id"]] = element.get("name") or "?"
    ports = {element["source_port_id"]: element for element in circuit
             if element.get("type") == "source_port"}
    for element in circuit:
        if element.get("type") != "source_trace":
            continue
        on_ground = bool(set(element.get("connected_source_net_ids") or []) & ground_ids)
        owners = {ports[port_id].get("source_component_id")
                  for port_id in element.get("connected_source_port_ids") or []
                  if port_id in ports}
        present |= owners
        if on_ground:
            grounded |= owners
    # A component with no trace at all is a separate complaint, already covered by the parts that
    # refuse to emit. Report only those that are wired to something and to no ground.
    return sorted(names.get(owner, "?") for owner in present - grounded)


def run(requirements, workdir, toolchain=None):
    """Every stage, in order, stopping at the first that cannot produce input for the next."""
    stages = []
    # The reference design is built from the plugin's OWN library, so it must not require a
    # surrounding project. It did: `project_root()` raises outside one, the exception escaped
    # `main`, and the traceback exited 1 — which reads as "the chain is broken" when the truth
    # is "the chain was never started". A crash must not be able to impersonate a verdict.
    try:
        project = boards.project_root()
    except Exception:  # noqa: BLE001
        project = SCRIPTS.parent

    # --- parts and pin assignment, via the generator that owns them ---
    try:
        board = boards.load(project, requirements.get("board"))
    except Exception as exc:  # noqa: BLE001
        return stages + [Stage("board", COULD_NOT_RUN, str(exc))]
    stages.append(Stage("board", OK, board["name"]))

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
    circuit_path = workdir / "dist" / "board" / "circuit.json"
    if not circuit_path.is_file():
        return stages + [Stage("build", PROBLEMS,
                               "no circuit.json was produced\n" + built.stderr.strip()[-800:])]

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
    return stages + [Stage("build", OK, "%d trace(s), 0 errors" % traces)]


def verdict(stages):
    if any(stage.status == PROBLEMS for stage in stages):
        return EXIT_PROBLEMS
    if any(stage.status == COULD_NOT_RUN for stage in stages):
        return EXIT_COULD_NOT_RUN
    return EXIT_OK


def render(stages, code):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????"}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build", ""]
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
    args = parser.parse_args(argv)

    requirements = (json.loads(Path(args.requirements).read_text())
                    if args.requirements else dict(REFERENCE))

    workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))
    (workdir / "requirements.json").write_text(json.dumps(requirements))
    # tsci needs its toolchain reachable from the build directory.
    source = Path(args.requirements).resolve().parent if args.requirements else Path.cwd()
    toolchain = find_toolchain(source)
    if toolchain is not None:
        modules = toolchain.parent.parent
        if not (workdir / "node_modules").exists():
            os.symlink(modules, workdir / "node_modules")

    try:
        stages = run(requirements, workdir, toolchain)
    except subprocess.TimeoutExpired:
        stages = [Stage("build", COULD_NOT_RUN,
                        "the build did not finish in %ds" % BUILD_TIMEOUT_S)]
    except Exception as exc:  # noqa: BLE001
        # Anything unforeseen is could-not-run, never problems. An exception says this tool
        # failed, which is not the same as the chain failing, and reporting one as the other
        # sends somebody to debug a design that was never examined.
        stages = [Stage("check_spine", COULD_NOT_RUN,
                        "%s: %s" % (type(exc).__name__, exc))]

    code = verdict(stages)
    if args.json:
        print(json.dumps({"check": "spine", "status": {EXIT_OK: OK, EXIT_PROBLEMS: PROBLEMS,
                                                       EXIT_COULD_NOT_RUN: COULD_NOT_RUN}[code],
                          "stages": [{"name": s.name, "status": s.status, "detail": s.detail}
                                     for s in stages]}))
    else:
        sys.stdout.write(render(stages, code))
    if args.keep:
        print("  working directory: %s" % workdir, file=sys.stderr)
    elif workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
