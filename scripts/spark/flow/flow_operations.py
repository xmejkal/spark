"""
The flow Operations on the core by the `op` each prints, for the frontends (P825): `show-flow` (`flow.py show`). `page` and
`run-request` come with P827 and P829. The table is a module, because the area's `__init__` imports nothing.
"""

from spark.flow.show_flow import ShowFlow

# --- MVP ---
OPERATIONS = {ShowFlow.name: ShowFlow}
# --- end MVP ---
