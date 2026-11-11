"""
The design Operations on the core by the `op` each prints, for the frontends (P707, N19): `list-boards` (`boards.py --list`)
and `audit` (`parts.py --audit`). The table is a module, not the area's `__init__`, because that imports nothing (the
wave 5 cycles, P676); an area whose `__init__` imports nothing holds its table in `<area>_operations.py`.
"""

from spark.design.audit_records import AuditRecords
from spark.design.list_boards import ListBoards

# --- MVP ---
OPERATIONS = {operation.name: operation for operation in (ListBoards, AuditRecords)}
# --- end MVP ---
