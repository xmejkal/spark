"""
The flow's follow-up (P1035, piece 3 of P793): after an ok run that wrote to a project, the core adds the steps that
`flow.py show` names now, after the Operation's own, with one line each. `parts.py --pick` and `check_spine.py --keep` hand
it to the core first. A step can hold a placeholder that Claude fills before the line runs: `<name>` of a scenario run,
`<answers.json>` of the brief step. PR 2 (the PO's D16): after an ok run that wrote to a project with a page.html, it
writes the page again on disk (`write_flow_page.write_page`). It never publishes it and makes no GitHub call (D23): Claude
republishes the page at the next /spark:page.
"""

import os
import stat
from pathlib import Path

from spark.core.follow_up import STEP_LINE, FollowUp
from spark.core.text_guards import printable
from spark.flow.flow_page import FlowHtmlPage
from spark.flow.show_flow import NEEDS_YOU, flow_and_guide, needs_you, now_steps
from spark.flow.write_flow_page import write_page
from spark.records import store

# --- MVP ---
#: The script of a step whose op is not its script's name; every other op runs `<op>.py`, as `board_envelope.next_text`
#: and flow.md name it (`look`, `run_scenario`, `init_project`). Which script runs an op is the frontend's fact, which the
#: Operation catalogue does not hold (P1077); P1081 #1585 moves it to one place.
STEP_SCRIPTS = {"pick": "parts.py", "requirements": "parts.py", "needs-drop": "parts.py", "build-board": "check_spine.py"}
#: The folder of the scripts a step runs.
SCRIPTS = Path(__file__).resolve().parents[2]
#: The sentence of the page written again (P1035 PR 2): a line of the text, and a note under --json.
REFRESHED = "wrote %s again: /spark:page publishes it" % FlowHtmlPage.FILE_NAME


class PageNotRegularError(OSError):
    """Error: the project's page.html is a folder, a FIFO or a link, so the refresh writes no page through it (P1035 PR 2)."""


def kept_its_page(result):
    """Whether the run took charge of page.html itself: a kept entry of its data names it. The build with --keep writes the
    page with the pictures it just drew (`write_kept_page`), or removes it, or says why it could not write it."""
    kept = result.data.get("kept") if isinstance(result.data, dict) else None
    return any(isinstance(entry, dict) and Path(str(entry.get("file"))).name == FlowHtmlPage.FILE_NAME for entry in kept or [])


class FlowFollowUp(FollowUp):
    """Strategy: the follow-up of a run that wrote to a project: the now steps of `flow.py show` (`show_flow.now_steps`),
    and for each the line a person runs, with NEEDS_YOU after the command for a step that needs the person or their yes
    (`show_flow.needs_you`), then why. Its refresh writes page.html again (PR 2). `renderer` and `store` are what a test
    swaps (None: the real ones)."""

    refreshes = FlowHtmlPage.FILE_NAME

    def __init__(self, renderer=None, store=None):
        self.renderer, self.store = renderer, store

    def refresh(self, project, result):
        """REFRESHED once page.html is written again, or None: the project has no page.html (decision G), or the run kept
        its own (amendment A). A page.html that is no regular file raises PageNotRegularError before any write; a link is
        not followed. What the write raises is the core's to report."""
        page = Path(project) / self.refreshes
        if kept_its_page(result) or not os.path.lexists(page):
            return None
        if not stat.S_ISREG(page.lstat().st_mode):
            raise PageNotRegularError("%s is no regular file" % self.refreshes)
        write_page(project, renderer=self.renderer, store=self.store)
        return REFRESHED

    def steps(self, project):
        phases, guide = flow_and_guide(project)
        return now_steps(project, phases, guide)

    def line(self, step):
        script = SCRIPTS / STEP_SCRIPTS.get(step.op, "%s.py" % step.op)
        mark = NEEDS_YOU if needs_you(step) else ""
        return printable(STEP_LINE % (store.format_rerun_line(script, step.argv) + mark, step.why))
# --- end MVP ---
