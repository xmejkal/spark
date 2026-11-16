"""
The checks' Operations on the core by the `op` each prints, for the frontends (P804): `check-design` (`check_all.py`). The
table is a module, because the area's `__init__` imports nothing.
"""

from spark.checks.check_design import CheckDesign

# --- MVP ---
OPERATIONS = {CheckDesign.name: CheckDesign}
# --- end MVP ---
