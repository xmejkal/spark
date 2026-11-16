"""
The build's Operations on the core by the `op` each prints, for the frontends (P804): `build-board` (`check_spine.py`). The
table is a module, because the area's `__init__` imports nothing.
"""

from spark.build.build_board import BuildBoard

# --- MVP ---
OPERATIONS = {BuildBoard.name: BuildBoard}
# --- end MVP ---
