"""
The flow's follow-up (P1035, piece 3 of P793): after an ok run that wrote to a project, the core adds the steps that
`flow.py show` names now, after the Operation's own, with one line each. `parts.py --pick` and `check_spine.py --keep` hand
it to the core first. A step can hold a placeholder that Claude fills before the line runs: `<name>` of a scenario run,
`<answers.json>` of the brief step.
"""

from pathlib import Path

from spark.core.follow_up import STEP_LINE, FollowUp
from spark.core.text_guards import printable
from spark.flow.show_flow import NEEDS_YOU, flow_and_guide, needs_you, now_steps
from spark.records import store

# --- MVP ---
#: The script of a step whose op is not its script's name; every other op runs `<op>.py`, as `board_envelope.next_text`
#: and flow.md name it (`look`, `run_scenario`, `init_project`). Piece 4's catalogue replaces this map.
STEP_SCRIPTS = {"pick": "parts.py", "requirements": "parts.py", "needs-drop": "parts.py", "build-board": "check_spine.py"}
#: The folder of the scripts a step runs.
SCRIPTS = Path(__file__).resolve().parents[2]


class FlowFollowUp(FollowUp):
    """Strategy: the follow-up of a run that wrote to a project: the now steps of `flow.py show` (`show_flow.now_steps`),
    and for each the line a person runs, with NEEDS_YOU after the command for a step that needs the person or their yes
    (`show_flow.needs_you`), then why."""

    def steps(self, project):
        phases, guide = flow_and_guide(project)
        return now_steps(project, phases, guide)

    def line(self, step):
        script = SCRIPTS / STEP_SCRIPTS.get(step.op, "%s.py" % step.op)
        mark = NEEDS_YOU if needs_you(step) else ""
        return printable(STEP_LINE % (store.format_rerun_line(script, step.argv) + mark, step.why))
# --- end MVP ---
