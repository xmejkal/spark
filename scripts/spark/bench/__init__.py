"""
The bench area: the Operations on a board on USB, and the outside they reach. `look` is the first on the core (P442,
W3-3), `deploy` the second (P655, W4-2), the grant, live and reach Operations (`issue-grant`, `check-grant`, `live`, `reach`) the next (P657), `show-bench`,
the bench's show (P919), and `register-project` and `record-deploy`, which let a project that is not spark's record its
deploys (P920), and `disallow-direct-flashing`, grant.py's third mode (P1029). `OPERATIONS` maps each printed `op` to its class, for the frontends.
"""

from spark.bench import deploy_gate
from spark.records.tool_finder import build_tool_outside_world
from spark.bench.deploy_image import DeployImage
from spark.bench.check_grant import CheckGrant
from spark.bench.direct_flashing import DisallowDirectFlashing
from spark.bench.issue_grant import IssueGrant
from spark.bench.look_at_board import LookAtBoard
from spark.bench.reach_board import ReachBoard
from spark.bench.record_deploy import RecordDeploy
from spark.bench.register_project import RegisterProject
from spark.bench.run_live_code import RunLiveCode
from spark.bench.show_bench import ShowBench
from spark.core.operation import JSON_DEST
from spark.core.replies import Terminal, reply_strategy_for

# --- MVP ---
OPERATIONS = {operation.name: operation for operation in (LookAtBoard, DeployImage, IssueGrant, CheckGrant, RunLiveCode, ReachBoard,
                                                            ShowBench, RegisterProject, RecordDeploy, DisallowDirectFlashing)}


def build_project_outside_world(project, effects, reporter, values=None):
    """Core's OutsideWorld for an Operation on `project`, `tool_finder.build_tool_outside_world`'s (P1078): `find_tool` is
    `ToolFinder(project).find`, which finds a role or a tool as the project's tools list says (P725); `report` is the given
    Reporter's (P507); `clock` the computer's;
    `make_consent` asks in the terminal, on the Reporter's stream (P655), the question masked as the Reporter masks (P677).
    `replies` answers the look's Question (P865), for an Operation that takes `--replies`: from that file in `values`, the
    parsed arguments `run_cli` hands every builder, then live in the terminal, with no terminal under `--json`, as research's
    builder does. A replies file that cannot be read is `RepliesStore.load`'s SparkError: `run_operation` answers it as one Finding."""
    values = values or {}
    replies = reply_strategy_for(values["replies"], None if values.get(JSON_DEST) else Terminal(stdout=reporter.stream, mask=reporter.mask)) \
        if "replies" in values else None
    return build_tool_outside_world(project, effects, reporter, values,
                                    make_consent=lambda line: deploy_gate.TerminalConsentStrategy(line, stdout=reporter.stream, mask=reporter.mask),
                                    replies=replies)
# --- end MVP ---
