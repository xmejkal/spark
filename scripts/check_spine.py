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
process (P706). The Operation `spark/build/build_board.BuildBoard` runs it, keeps what --keep asks for and removes the
work folder (P804); this CLI hands the arguments to the core, which parses them and prints.
"""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from spark.build.build_board import BuildBoard  # noqa: E402
from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN  # noqa: E402
from spark.core.outcomes import OK as OK, PROBLEMS as PROBLEMS, COULD_NOT_RUN as COULD_NOT_RUN, SKIPPED as SKIPPED  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402


def main(argv=None, outside=None):
    """Build the requirements file and print the verdict, or with --json its one line. `outside` is the OutsideWorld a
    test gives. Returns the exit code."""
    return run_cli(HelpText("check_spine.py", __doc__.strip().splitlines()[0], None), BuildBoard(), argv,
                   outside_builder=build_bare_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
