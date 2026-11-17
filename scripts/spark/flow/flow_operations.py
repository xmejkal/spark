"""
The flow Operations on the core by the `op` each prints, for the frontends (P825): `show-flow` (`flow.py show`) and `write-flow-page`
(`flow.py page`, P827). `run-request` comes with P829. The table is a module, because the area's `__init__` imports nothing.
"""

from spark.flow.show_flow import ShowFlow
from spark.flow.write_flow_page import WriteFlowPage

# --- MVP ---
OPERATIONS = {ShowFlow.name: ShowFlow, WriteFlowPage.name: WriteFlowPage}
# --- end MVP ---
