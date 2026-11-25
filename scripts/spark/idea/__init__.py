"""
The idea area: the Operations on a project's needs and what they hold, the stage /spark:idea works in. `needs-drop` is the
first on the core (P514), and `move-hold` moves a held part to another project (P1124); `--needs-set`, `--pick` and `--requirements` can move here later. `OPERATIONS` maps each printed
`op` to its class, for the frontends.
"""

from spark.idea.drop_need import DropNeed
from spark.idea.move_hold import MoveHold

# --- MVP ---
OPERATIONS = {DropNeed.name: DropNeed, MoveHold.name: MoveHold}
# --- end MVP ---
