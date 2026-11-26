"""
The step of each flow offer (P1030, #1510): the core's NextStep that runs it, so the CLI's `next`, the page's request and
later an MCP tool name the same step. A NextStep holds plain values only, so an event can carry it later (P793). Each op
is written here as text: importing build_board makes a cycle (build_board imports write_flow_page, which imports
show_flow, which imports phase_readers). tests/test_flow.py pins each op, argv and effects against its Operation.
"""

from pathlib import Path

from spark.core.operation import READS, RUNS, WRITES
from spark.core.result import NextStep
from spark.flow import flow_codes
from spark.records import store

# --- MVP ---
#: The project's requirements file, as every stage names it. phase_readers takes it from here.
REQUIREMENTS_FILE = "requirements.json"


def whole(project):
    """The project as a whole path: a project whose name starts with `-` never reads as a flag."""
    return Path(project).absolute()


def picks_step(project, pairs, why):
    """The step of a pick of each `NEED=ID` in `pairs`, the one shape of a pick's step (P1141): the offer's pick and the
    parts phase's own step build through it. A pick is the person's choice, so the step needs the person."""
    return NextStep("pick", ["--pick", str(whole(project))] + list(pairs), why, (READS, WRITES), False, True, store.read_given_env())


def pick_step(project, need, pick_id, name):
    """The step of the offer to pick `pick_id` (the part `name`) for `need`: `why` names the part and the need."""
    return picks_step(project, ["%s=%s" % (need, pick_id)], flow_codes.PICK_WHY % (name, need))


def requirements_step(project):
    """The step of the offer to write the parts list from the picks."""
    return NextStep("requirements", ["--requirements", str(whole(project))], flow_codes.REQUIREMENTS_LABEL, (READS, WRITES),
                    False, None, store.read_given_env())


def build_step(project):
    """The step of the offer to build the board from the project's requirements.json, kept in the project."""
    return NextStep("build-board", [str(whole(project) / REQUIREMENTS_FILE), "--keep", str(whole(project))], flow_codes.BUILD_LABEL,
                    (READS, RUNS, WRITES), False, None, store.read_given_env())


def drop_step(project, need):
    """The step of the offer to drop `need` (parts.py --needs-drop). It is asked in the chat, never from the page."""
    return NextStep("needs-drop", ["--needs-drop", str(whole(project)), need], flow_codes.DROP_LABEL % need, (READS, WRITES),
                    False, None, store.read_given_env())
# --- end MVP ---
