"""
The bench area: the Operations on a board on USB, and the outside they reach. `look` is the first on the core (P442,
W3-3), `deploy` the second (P655, W4-2), `issue_grant`, `check_grant`, `live` and `reach` the rest (P657). `OPERATIONS` maps each printed `op` to its class, for the frontends.
"""

import deploy_gate
import tools
from spark.bench.deploy_image import DeployImage
from spark.bench.check_grant import CheckGrant
from spark.bench.issue_grant import IssueGrant
from spark.bench.look_at_board import LookAtBoard
from spark.bench.reach_board import ReachBoard
from spark.bench.run_live_code import RunLiveCode
from spark.core.clock import SystemClock
from spark.core.outside import build_outside_world

# --- MVP ---
OPERATIONS = {operation.name: operation for operation in (LookAtBoard, DeployImage, IssueGrant, CheckGrant, RunLiveCode, ReachBoard)}


def build_project_outside_world(project, effects, reporter):
    """Core's OutsideWorld for an Operation on `project`: `find_tool` finds a role or a tool as the project's tools list says,
    and as the shared lists alone say with `project=None`; `report` is the given Reporter's (P507); `clock` the computer's;
    `make_consent` asks in the terminal, on the Reporter's stream (P655)."""
    return build_outside_world(effects, reporter, find_tool=lambda name, project=project: tools.find(name, project),
                               clock=SystemClock(),
                               make_consent=lambda line: deploy_gate.TerminalConsentStrategy(line, stdout=reporter.stream))
# --- end MVP ---
