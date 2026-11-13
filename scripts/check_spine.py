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

The run is `spark/build/requirements_build.RequirementsBuildService`: it reads the file, makes the work folder and runs
`build_service.BuildService` over `board_engine.TscircuitEngine` and `spark/design/board_emitter.BoardEmitter`, all in
process (P706); this CLI parses, runs it and reports.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from spark.bench import board_envelope  # noqa: E402
from spark.breadboard import tabbed_page  # noqa: E402
from spark.build.build_service import verdict  # noqa: E402
from spark.build.kept_files import (_kept, _kept_pins, drop_an_older_build, keep_breadboard, keep_simulation,  # noqa: E402
                                    keep_tabbed_page, left_off, simulation_dir)
from spark.build.requirements_build import RequirementsBuildService  # noqa: E402
from spark.build.stages import skipped_the_build  # noqa: E402

from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, OK, PROBLEMS, COULD_NOT_RUN, SKIPPED, STATUS_FOR  # noqa: E402
from spark.core.text_guards import guard_lines  # noqa: E402

#: What the closing line adds when a full build's simulation stage is skipped: every part's record skips the simulation (P778).
EVERY_PART_SKIPPED_LINE = "; every part is skipped from the simulation, so the diagram holds the board alone"


def render(stages, code, unserved=()):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????", SKIPPED: "--  "}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation", ""]
    for stage in stages:
        lines.append("  [%s] %-16s %s" % (mark[stage.status], stage.name, stage.detail))
    lines.append("")
    lines.append({
        EXIT_OK: "  the chain runs end to end" + (" for the board alone: nothing to wire, so no board was built" if skipped_the_build(stages)
                                                  else EVERY_PART_SKIPPED_LINE if any(stage.status == SKIPPED for stage in stages) else ""),
        EXIT_PROBLEMS: "  the chain is broken",
        EXIT_COULD_NOT_RUN: "  the chain was NOT exercised — this is not a pass",
    }[code] + (" — but not every need is on the board: %s" % ", ".join(unserved) if unserved and code == EXIT_OK else ""))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("requirements", nargs="?",
                        help="a requirements.json; omit for the reference design. \"board_only\": true with no parts builds the board alone")
    parser.add_argument("--json", action="store_true",
                        help="the verdict as one JSON object: check, status, stages, next (the firmware step, when ok in a project), and kept with --keep or --sim-dir")
    parser.add_argument("--keep", metavar="DIR", type=Path,
                        help="write the built board into DIR: board.tsx, its footprint and "
                             "dist/, where every check already looks. Existing .tsx files are "
                             "left alone and named; with --json, each file is listed under kept. With a requirements "
                             "file it also writes breadboard.md, the parts and how to wire them on a breadboard, "
                             "breadboard.json, the same wiring drawn on a Wokwi breadboard (the XIAO ESP32-C6 today; a part "
                             "you moved in it, a resistor or a jumper too, stays where you put it, or the build names it as "
                             "`move not kept`; an end the drawing joins differently from the points is a `drawing differs` entry), "
                             "breadboard.svg, that drawing as a picture, "
                             "a rebuild also lists what to change on the bench (one `changed` entry for each line), page.html, the breadboard, schematic and PCB "
                             "in three tabs to open in a browser or to publish as an Artifact, and "
                             "firmware/pins.py, the pins the firmware imports, with one `missing_facts` item for each fact the board record lacks. The simulation project goes to DIR/sim")
    parser.add_argument("--sim-dir", type=Path, metavar="DIR",
                        help="keep the simulation project here instead of DIR/sim: diagram.json, wokwi.toml, the chips")
    parser.add_argument("--firmware", metavar="IMAGE",
                        help="the flash image wokwi.toml names, relative to the sim dir (flash_image.py writes one); "
                             "without it, the image a kept wokwi.toml names is kept")
    args = parser.parse_args(argv)

    run = RequirementsBuildService().build(args.requirements, args.firmware, simulation_dir(args))
    for line in run.diagnostics:
        print(guard_lines(line), file=sys.stderr)
    return report(run.stages, args, run.workdir, run.requirements, tabbed_page.TscircuitExport(run.toolchain))


def report(stages, args, workdir=None, requirements=None, exporter=None):
    """
    The verdict, rendered the way it was asked for — with the needs the requirements file leaves off the board, when it says
    any (`left_off`; with --json its own note, under `unserved`), and the facts the board record lacks (`missing_facts`, P464) — and the working directory kept or removed. What
    --keep wrote and left alone is said on stderr and, with --json, carried under `kept` (P124). With no workdir, a
    requirements file that is there but refused still removes what an earlier build left (P280); a missing one, which
    may be a typo, removes nothing.
    """
    code = verdict(stages)
    requirements_file = getattr(args, "requirements", None)
    following = board_envelope.firmware_next_steps(code == EXIT_OK, requirements_file)  # P517: write the firmware next
    keeps = args.keep and (workdir is not None or bool(requirements_file) and Path(requirements_file).is_file())
    kept = (_kept(workdir, args.keep) if workdir is not None else []) if keeps else None
    if kept is not None and requirements_file:
        kept += keep_breadboard(Path(args.requirements), Path(args.keep), stages) + drop_an_older_build(Path(args.keep), stages)
        kept.append(_kept_pins(Path(args.requirements), Path(args.keep)))
        kept.append(keep_tabbed_page(Path(args.keep), stages, kept, exporter or tabbed_page.TscircuitExport(None)))
    simulation = keep_simulation(workdir, simulation_dir(args), stages) if workdir is not None and simulation_dir(args) else None
    kept = (kept or []) + [simulation] if simulation is not None else kept
    if args.json:
        said = {"check": "spine", "status": STATUS_FOR[code], "stages": [{"name": s.name, "status": s.status, "detail": s.detail} for s in stages],
                **({"unserved": requirements["unserved"]} if left_off(requirements) else {}), **({"next": following} if following else {}),
                **({"missing_facts": held} if (held := [item for entry in kept or [] for item in entry.get("missing_facts", [])]) else {})}
        if kept is not None:
            said["kept"] = [{key: value for key, value in entry.items() if key != "line"} for entry in kept]
        print(json.dumps(said))
    else:
        sys.stdout.write(guard_lines(render(stages, code, left_off(requirements)) + board_envelope.next_text(following)))
    for entry in kept or []:
        print(guard_lines("  %s" % entry["line"]), file=sys.stderr)
    if workdir is not None:
        shutil.rmtree(workdir, ignore_errors=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
