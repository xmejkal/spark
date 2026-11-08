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
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from spark.bench import board_envelope  # noqa: E402
from spark.breadboard import tabbed_page  # noqa: E402
from spark.build import board_engine  # noqa: E402
from spark.build import build_codes  # noqa: E402
from spark.build.board_engine import modules_for  # noqa: E402
from spark.build.build_service import run, verdict, vouches_for_a_build  # noqa: E402
from spark.build.kept_files import (REQUIREMENTS_STAGE, _kept, _kept_pins, design_handed_to, drop_an_older_build,  # noqa: E402
                                    keep_breadboard, keep_simulation, keep_tabbed_page, left_off, simulation_dir)
from spark.build.stages import Stage  # noqa: E402
from spark.design import loader  # noqa: E402
import parts  # noqa: E402
from spark.firmware import sim_project  # noqa: E402
from spark.records import store  # noqa: E402

from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN, NOT_CHECKED, OK, PROBLEMS, COULD_NOT_RUN, SKIPPED, STATUS_FOR  # noqa: E402
from spark.core.text_guards import guard_lines  # noqa: E402

#: The design the chain is proven against when nobody names one. A motor driver, a sensor on a
#: bus, and the power inlet that supplies the rail the modules only consume — the smallest set
#: that exercises pin assignment, a bus, a rail with an external source, and two footprint kinds.
REFERENCE = {"board": "firebeetle2-esp32s3",
             "parts": ["l9110s-module", "vl6180x-breakout", "jst-ph-2-power-inlet"]}


def render(stages, code, unserved=()):
    mark = {OK: "ok  ", PROBLEMS: "!!  ", COULD_NOT_RUN: "????", SKIPPED: "--  "}
    lines = ["", "  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation", ""]
    for stage in stages:
        lines.append("  [%s] %-16s %s" % (mark[stage.status], stage.name, stage.detail))
    lines.append("")
    lines.append({
        EXIT_OK: "  the chain runs end to end" + (" for the board alone: nothing to wire, so no board was built"
                                                  if any(stage.status == SKIPPED for stage in stages) else ""),
        EXIT_PROBLEMS: "  the chain is broken",
        EXIT_COULD_NOT_RUN: "  the chain was NOT exercised — this is not a pass",
    }[code] + (" — but not every need is on the board: %s" % ", ".join(unserved) if unserved and code == EXIT_OK else ""))
    return "\n".join(lines) + "\n"


#: How much of a late command's own output the sentence keeps, as the other last-words sites cap theirs.
LAST_WORDS_CAP = 800


def timed_out_sentence(late):
    """What a command that ran past its limit said (P659): the command by its file names (two words, three when the
    second is `run`, as a converter run as `<runtime> run cli.ts`), the limit it had, and its last three lines of stderr, or of stdout when stderr is empty, capped."""
    words = shlex.split(late.cmd) if isinstance(late.cmd, str) else list(late.cmd)
    names = [Path(str(word)).name for word in words]
    cmd = names[:3] if names[1:2] == ["run"] else names[:2]
    out = late.stderr or late.stdout or ""
    said = out.decode(errors="replace") if isinstance(out, bytes) else out
    last = " | ".join(said.strip()[-LAST_WORDS_CAP:].splitlines()[-3:])
    return "`%s` did not finish in %ss%s" % (" ".join(cmd), late.timeout, "; its last words: " + last if last else "")


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

    # The input is read before anything runs, and read AS input: a malformed file is a stage that could not run, not a
    # traceback with exit 1 (which says "the chain is broken"). The project is the file's, up from its own directory, so a
    # design belongs to its parts wherever it is typed; a file in no project is built from the plugin's library.
    source = Path(args.requirements).resolve() if args.requirements else None
    try:
        requirements = loader.read(source) if source else dict(REFERENCE)
    except loader.DesignError as broken:
        return report([Stage(REQUIREMENTS_STAGE, COULD_NOT_RUN, str(broken), broken.code)], args)
    # A file in no project is built from the plugin's library, and the board stage says so.
    project = loader.project_for(source) if source else None
    from_library = bool(source) and loader.is_library(project)

    workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))
    (workdir / "requirements.json").write_text(json.dumps(requirements))
    # tsci needs its toolchain reachable from the build directory.
    toolchain = board_engine.find_toolchain(source.parent if source else Path.cwd())
    modules = modules_for(toolchain) if toolchain is not None else None
    if modules is not None and not (workdir / "node_modules").exists():
        os.symlink(modules, workdir / "node_modules")

    # What `built` will name is loaded now, once, before anything can change under it.
    handed = design_handed_to(workdir, project) if source and not from_library else None

    # A rebuild runs the flash image the kept wokwi.toml already names, unless --firmware names another.
    simulation = simulation_dir(args)
    if simulation and (simulation / "diagram.json").is_file():  # P482: run() merges into a copy, never the person's file
        shutil.copy(simulation / "diagram.json", workdir / sim_project.KEPT_DIAGRAM)
    firmware, kept = args.firmware, None
    if not firmware and simulation:
        kept = sim_project.firmware_in(simulation / "wokwi.toml")
        firmware = kept.name
    try:
        stages = run(requirements, workdir, toolchain, project, from_library, firmware=firmware)
    except subprocess.TimeoutExpired as late:
        stages = [Stage("build", COULD_NOT_RUN, timed_out_sentence(late), build_codes.STAGE_TIMED_OUT)]
    except Exception as exc:  # noqa: BLE001
        # Anything unforeseen is could-not-run, never problems. An exception says this tool
        # failed, which is not the same as the chain failing, and reporting one as the other
        # sends somebody to debug a design that was never examined.
        stages = [Stage("check_spine", COULD_NOT_RUN,
                        "%s: %s" % (type(exc).__name__, exc), build_codes.STAGE_CRASHED)]

    # P429: a line this could not read goes with the file the build writes again, so that is said, but only when it did.
    if kept is not None and kept.state == NOT_CHECKED and (workdir / "sim" / "wokwi.toml").is_file():
        print(guard_lines("  sim/wokwi.toml %s The rebuild wrote it again with no image named, and a scenario run then names "
                          "the default one." % kept.why), file=sys.stderr)

    # The history says a build ran end to end (§5.7) — written here, by the chain itself, never on anyone's say-so.
    # A history that cannot be kept is said, and the verdict stands: the chain ran, whatever the store thinks of it.
    if handed is not None and vouches_for_a_build(stages):
        try:
            parts.note_built(handed)
        except (store.StoreProblem, OSError) as unrecorded:
            print(guard_lines("  the build was not recorded in your history: %s" % unrecorded), file=sys.stderr)

    return report(stages, args, workdir, requirements, tabbed_page.TscircuitExport(toolchain))


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
