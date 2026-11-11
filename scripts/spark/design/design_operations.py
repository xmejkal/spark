"""
The design Operations on the core by the `op` each prints, for the frontends (P707, N19; P726): `list-boards` (`boards.py
--list`), `audit` (`parts.py --audit`) and the six goal Operations of `parts.py` (`need`, `needs`, `match`, `offer`,
`requirements`, `tally`). The table is a module, not the area's `__init__`, because that imports nothing (the wave 5
cycles, P676); an area whose `__init__` imports nothing holds its table in `<area>_operations.py`.
"""

from spark.design.audit_records import AuditRecords
from spark.design.find_offers import FindOffers
from spark.design.list_boards import ListBoards
from spark.design.list_needs import ListNeeds
from spark.design.match_needs import MatchNeeds
from spark.design.show_offer import ShowOffer
from spark.design.tally_cost import TallyCost
from spark.design.write_requirements import WriteRequirements

# --- MVP ---
OPERATIONS = {operation.name: operation for operation in (ListBoards, AuditRecords, FindOffers, ListNeeds, MatchNeeds, ShowOffer,
                                                          WriteRequirements, TallyCost)}
# --- end MVP ---
