#!/usr/bin/env python3
"""
Say where a project stands, write it as the project's page.html, or run the step the page asked for (P825, P827, P829).

Its `--help` sentence is the summary of the verb's Operation, ShowFlow's, WriteFlowPage's or RunRequest's (P937), and
EPILOG is the CLI's own text.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.cli import HelpText, run_cli
from spark.core.outside import build_bare_outside_world
from spark.flow.run_request import RunRequest
from spark.flow.show_flow import ShowFlow
from spark.flow.write_flow_page import WriteFlowPage

#: The verbs, each the Operation it runs. With no verb word, flow.py shows.
VERBS = {"show": ShowFlow, "page": WriteFlowPage, "run-request": RunRequest}
DEFAULT_VERB = "show"

EPILOG = """Each verb's own --help says what it does: flow.py show --help, flow.py page --help and flow.py run-request --help.
The rest of this text is the CLI's own, for every verb.

The guide (P977) starts the text: NOW, the phase to act on now, its sentence and the key of its offer, or next: and the
op of the step of a now phase that holds no offer, with needs you for a step the person takes (P1034), then DONE and
LATER (with nothing open, the line that says so stands in place of NOW). One line per phase comes after it; the parts
line says the count, and one line per need follows it: its pick with a tick, its lines, then its pick keys, each with
its have (P1135). With --json,
next holds the step of that offer, raw (P1030), or the step of the simulate or the deploy (P1034), and an empty next
means: read data.guide.now. When Wokwi has no model of the board, the build ends its simulation stage skipped with the
code board_not_in_wokwi and exits 0 (P1207). The guide counts that build as done and says there is no simulation. An
older record of such a build, with the stage could-not-run, is counted as done too and keeps exit 2 until the next build.

The deploy phase reads the newest board log in sim/runs/board/: its time, image, verdict and cause, never its port or
console text (P1043). Only ready seen on the image the project holds now is ok. Ready unknown is partial, and ready not
seen is problems. Firmware newer than that image, an image that differs from the last deploy's, or no image makes it
stale, and stale wins over problems. The says line keeps the verdict. With the deploy ok, guide.now is null and
guide.no_open_phase says why. data.deploy holds the logged deploy: at, image, verdict, cause, fact and read_back.
From the On the board station on, guide.gate_a (P1220) is gate A's one free condition: shut_by lists run-failed while a run
failed on the current image, and the line TESTED BEFORE THE BOARD says it. An empty shut_by never means that gate A is open.
It reads sim/runs/ and runs nothing, so it costs no Wokwi minutes.

With --json, flow.py page prints its own keys, not show's nine: data.file, data.did, data.stands_at, data.phases (each
phase and its status only), data.fingerprint, data.guide and data.artifact. --artifact ID keeps the id of the Artifact
the page is published as in .spark/page.json, the id only, and every later page answers it as data.artifact (null when
none is kept). An id that is no UUID in lower case is a bad argument, and nothing is written. Show, run-request and the
page show each value of the project's secrets files (firmware/*secret*.py, values only) as ***
(P1060); a secrets file that cannot be read or parsed keeps the page from being written, and show notes the mask is off.

flow.py run-request runs the step the page asked for: flow.py run-request --help says the request's shape and its
refusals.

The fingerprint is the sha256 of the current offers and of .spark/needs.json, requirements.json and .spark/build.json. It
changes when an offer or one of these files changes. No other file of the project changes it, except through an offer.

The build phase reads .spark/build.json, which check_spine.py --keep writes when its folder is a project. It is stale when
requirements.json changed after that build. The needs phase is stale when the goal or the must lines of the brief changed
after parts.py --needs-set wrote the needs (.spark/needs-basis.json). Spark changes neither. The requirements phase reads
.spark/requirements-origin.json, which parts.py --requirements writes (P1140): when requirements.json differs from what
the picks give and is not as spark last wrote it, the phase and NOW say it was changed by hand. With no record, or one
spark cannot read, they name no cause. A need dropped after the
must lines were last gone through makes the idea phase out of date, and its next step is init_project.py --answers, on the
person's yes. After an ok run that writes to a project, the command ends its next with the step flow.py show names now (P1035):
parts.py --pick and check_spine.py --keep. At any status but a crash, they and deploy.py (not --dry-run, P1069) also write
page.html again when the project has one (the build with --keep writes its own), and never publish it.

With --json it prints one envelope: data.phases, data.stands_at, data.fingerprint, data.guide, data.deploy, then
data.name (the project folder's), data.title (the page's), data.stamp (newest: the page's data-written) and
data.artifact (the id kept in .spark/page.json, else null) (docs/guide/agents/flow.md).

Exit codes: 0 no phase holds problems or could not run, 1 a phase holds problems (a need that cannot be matched,
requirements the picks cannot give, a build that failed, a firmware line in sim/wokwi.toml that spark cannot use), 2 a
phase could not be read or its last build could not run, or an argument is wrong. Problems win: with both, the status is
problems and the exit 1, and the phase that could not run is listed under unchecked. Every phase answers either way.
For page, 0 means the page was written and 2 that it could not be written or an argument is wrong. A phase's own
problems do not change them. For run-request, 0 means the step ran ok, 1 that it ran with problems, and 2 that nothing
ran, the step could not run or an argument is wrong."""


def operation_for(argv):
    """(the Operation class `argv` asks for, argv without its verb word): the first word when it is a verb in VERBS, else
    `show` with argv as it is, so a word that is no verb fails in argparse."""
    return (VERBS[argv[0]], argv[1:]) if argv and argv[0] in VERBS else (VERBS[DEFAULT_VERB], argv)


def main(argv=None, outside=None):
    """Run the verb `argv` names and print its lines, or with --json its envelope. `outside` is the OutsideWorld a test
    gives. Returns the exit code."""
    operation, argv = operation_for(sys.argv[1:] if argv is None else list(argv))
    return run_cli(HelpText("flow.py", epilog=EPILOG, tool="flow"), operation(), argv,
                   outside_builder=build_bare_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
