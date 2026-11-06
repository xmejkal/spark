"""
The idea area: the Operations on a project's needs and what they hold, the stage /spark:idea works in. `needs-drop` is the
first on the core (P514); `--needs-set`, `--pick` and `--requirements` can move here later. `OPERATIONS` maps each printed
`op` to its class, for the frontends.
"""

from spark.idea.drop_need import DropNeed

# --- MVP ---
OPERATIONS = {DropNeed.name: DropNeed}
# --- end MVP ---
