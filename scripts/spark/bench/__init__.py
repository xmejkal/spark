"""
The bench area: the Operations on a board on USB, and the outside they reach. `look` is the first on the core (P442,
W3-3); the other bench CLIs follow in S7. `OPERATIONS` maps each printed `op` to its class, for the frontends.
"""

import tools
from spark.bench.look_at_board import LookAtBoard
from spark.core.outside import build_outside_world

# --- MVP ---
OPERATIONS = {LookAtBoard.name: LookAtBoard}


def build_project_outside_world(project, effects, reporter):
    """Core's OutsideWorld for an Operation on `project`: `find_tool` finds a role or a tool as the project's tools list says,
    and as the shared lists alone say with `project=None`; `report` is the given Reporter's (P507)."""
    return build_outside_world(effects, reporter, find_tool=lambda name, project=project: tools.find(name, project))
# --- end MVP ---
