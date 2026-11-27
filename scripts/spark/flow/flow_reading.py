"""
The facts of one read of a project's flow (P1060, #1558): the Value `FlowReading`, which `show_flow.reading_of` makes
once. `flow.py show --json` prints it as its data, and `write_flow_page.compose_page` draws the page from it, so the
page and `show` never read the project by two routes (D22 of the P1038 design).
"""

from collections import namedtuple

from spark.breadboard.tabbed_page import page_title
from spark.flow.guide import stands_at_of


# --- MVP ---
class FlowReading(namedtuple("FlowReading", "name phases guide fingerprint deploy stamp artifact steps", defaults=((),))):
    """Value: every fact of one read of a project's flow. `name` is the project folder's name, `phases` its Phases in
    order, `guide` its guide (`guide_of`, P977, with the line to type of `show_flow.with_command`, P1286), `fingerprint`
    its sha256 (`fingerprint_of`, P829), `deploy` the newest board log (`deploy_reading.deploy_data`, P1043), `stamp`
    `{"newest": time or None}`, the newest change of the fingerprint's files, `artifact` the id of the Artifact the page is
    published as, or None (P829), and `steps` the NextSteps of its now (`show_flow.now_steps`), whose argv hold whole paths:
    `show` puts them in `next`, so `to_dict` leaves them out."""

    __slots__ = ()

    @property
    def stands_at(self):
        """Where the project stands: the guide's now phase (`guide.stands_at_of`, the one rule, P1030)."""
        return stands_at_of(self.guide)

    @property
    def title(self):
        """The page's title, from the folder's name (`page_title`): Claude names the published Artifact with it (P1060)."""
        return page_title(self.name)

    def to_dict(self):
        """`data` of `flow.py show`: the keys from before P1060 first, then the name, the title, the stamp and the Artifact."""
        return {"phases": [phase.to_dict() for phase in self.phases], "stands_at": self.stands_at, "fingerprint": self.fingerprint,
                "guide": self.guide, "deploy": self.deploy, "name": self.name, "title": self.title, "stamp": self.stamp,
                "artifact": self.artifact}
# --- end MVP ---
