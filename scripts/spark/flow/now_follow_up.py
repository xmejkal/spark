"""
The flow's follow-up (P1035, piece 3 of P793): after an ok run that wrote to a project, the core adds the steps that
`flow.py show` names now, after the Operation's own, with one line each. `parts.py --pick` and `check_spine.py --keep` hand
it to the core first. A step can hold a placeholder that Claude fills before the line runs: `<name>` of a scenario run,
`<answers.json>` of the brief step, `<part>` of the parts step (P1141). PR 2 (the PO's D16): after a run that wrote to a project with a page.html, at any
status but a crash (P1069), and after `deploy.py` too (`PageFollowUp`), it writes the page again on disk
(`write_flow_page.write_page`). It never publishes it and makes no GitHub call (D23): Claude republishes the page at the
next /spark:page.
"""

import os
import stat
from pathlib import Path

from spark.core.follow_up import FollowUp
from spark.flow.flow_page import FlowHtmlPage
from spark.flow.show_flow import NEEDS_YOU, flow_and_guide, needs_you, now_steps
from spark.flow.write_flow_page import write_page

# --- MVP ---
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
    and for each the base's line (`follow_up.step_line`, P1256), with NEEDS_YOU after the command for a step that needs
    the person or their yes (`show_flow.needs_you`). Its refresh writes page.html again (PR 2). `renderer` and `store` are what a test
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

    def after_command(self, step):
        return NEEDS_YOU if needs_you(step) else ""


class PageFollowUp(FollowUp):
    """Strategy: the follow-up of a run that adds no flow step, `deploy.py` (P1069): its refresh is FlowFollowUp's, which
    writes page.html again, and its steps are the base's, none. `renderer` and `store` are what a test swaps."""

    refreshes = FlowHtmlPage.FILE_NAME

    def __init__(self, renderer=None, store=None):
        self.flow = FlowFollowUp(renderer, store)

    def refresh(self, project, result):
        return self.flow.refresh(project, result)
# --- end MVP ---
