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

EPILOG = """flow.py show reads the project's files and the store, and writes nothing. It says each phase in order: idea,
needs, parts, requirements, build, breadboard, firmware, simulate and deploy. Each phase has a status (ok, problems,
could-not-run, not-started, partial or stale, or none), who does it (you, claude or your terminal), what it says and its
offers. The idea has no status. A hand-written project (requirements.json and no needs) has none for its needs and
parts, and so has a project whose last need was dropped, which says so. Written firmware and a simulated image have none, because what their sentences say is for you to judge. An offer
is a key, such as pick:soil:x-led, with a label (the words of its button, such as Build the board), its effect (plain
sentences that name every write it makes) and makes_stale (the phases it can make out of date, only those that hold
something now). flow.py show runs no offer. The guide (P977) ends the text: NOW, the phase to act on now, its sentence
and the key of its offer, or next: and the op of the step of a now phase that holds no offer, with needs you for a
step the person takes (P1034), then DONE and LATER. With --json, next holds the step of that offer, raw (P1030), or
the step of the simulate or the deploy (P1034), and an empty next means: read data.guide.now. A build that stopped
only because Wokwi has no model of its board (board_not_in_wokwi) is counted as done there, and the guide says there
is no simulation.

The deploy phase reads the newest board log in sim/runs/board/: its time, image, verdict and cause, never its port or
console text (P1043). Only ready seen on the image the project holds now is ok. Ready unknown is partial, and ready not
seen is problems. Firmware newer than that image, an image that differs from the last deploy's, or no image makes it
stale, and stale wins over problems. The says line keeps the verdict. With the deploy ok, guide.now is null and
guide.no_open_phase says why. data.deploy holds the logged deploy: at, image, verdict, cause, fact and read_back.

flow.py page writes page.html in the project from the one reading that flow.py show prints (P1060): the station line
(each phase's place from data.guide.stations, a ring on now, a note's words under its name, then Perfboard, PCB and
Case greyed, P1119; DONE and LATER stand only in the developer fold), the phases, each with its status word and a mark, the wiring of a built project (the lines before power, then the steps, one at a time
or all at once) and the pictures the project holds: the breadboard, and the schematic and the PCB that the build with
--keep kept as files. The page adds no tick of its own: a
phase that is not ok never shows one. Only the build with --keep draws the schematic and the PCB. The page reads the
project's files and its board logs, and cannot see your wiring or what the board shows now. Each offer shows its label and its effect. The page's <body> carries
data-fingerprint (the first 12 hex digits of the fingerprint) and data-written (the newest change time of the three files
below). With --json, flow.py page prints its own keys, not show's nine: data.file, data.did, data.stands_at,
data.phases (each phase and its status only), data.fingerprint, data.guide and data.artifact. --artifact ID keeps the id of the Artifact the page is published as
in .spark/page.json, the id only, and every later page answers it as data.artifact (null when none is kept). An id that
is no UUID in lower case is a bad argument, and nothing is written. Only /spark:page publishes the page. Show,
run-request and the page show each value of the project's secrets files (firmware/*secret*.py, values only) as ***
(P1060); a secrets file that cannot be read or parsed keeps the page from being written, and show notes the mask is off.

flow.py run-request reads .spark/page-request.json, the page's request {id, key, seen, at}, and deletes it at once. It
runs the step only when seen is the first 12 hex digits of the fingerprint now, the key is an offer now, its kind
is pick, requirements or build, and its step names an Operation spark runs from the page. The values come from spark's
offer's step, never from the request. Else it runs nothing:
request_malformed (no regular file, no JSON object, an id that is no UUID, a key that is no text, a seen that is not 12
hex digits, or a file it cannot delete), request_in_chat (a need's drop, or a chat offer: a job only Claude does, such as
write-firmware), request_stale (the project changed after the page was read), request_not_offered (not an offer now,
or a kind the page never runs) or request_secrets_unreadable (a secrets file in firmware/ that cannot be read or
parsed). With --json it prints
data.for, data.key, data.label, data.ran, data.status, data.mark, data.line and data.fingerprint, the one after the
run, a refusal too; key and label only of an offer. After a run, write the page again with flow.py page.

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
