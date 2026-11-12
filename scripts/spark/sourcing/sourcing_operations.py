"""
The sourcing Operations on the core by the `op` each prints, for the frontends (P726 PR 2 and PR 3): the fifteen part
operations of `parts.py` and the four payload writes, each on `part_operation.PartOperation`. The table is a module, not the area's `__init__`, because that imports
nothing (the wave 5 cycles, P676), as design's `design_operations` is.
"""

from spark.sourcing.fetch_documents import FetchDocuments
from spark.sourcing.import_drawer import ImportDrawer
from spark.sourcing.find_kept import FindKept
from spark.sourcing.keep_file import KeepFile
from spark.sourcing.list_catalog import ListCatalog
from spark.sourcing.list_drawer import ListDrawer
from spark.sourcing.list_parts import ListParts
from spark.sourcing.list_signals import ListSignals
from spark.sourcing.list_unverified import ListUnverified
from spark.sourcing.mark_step import MarkStep
from spark.sourcing.promote_record import PromoteRecord
from spark.sourcing.read_datasheet import ReadDatasheet
from spark.sourcing.resolve_sources import ResolveSources
from spark.sourcing.set_drawer import SetDrawer
from spark.sourcing.set_facts import SetFacts
from spark.sourcing.set_function import SetFunction
from spark.sourcing.show_part import ShowPart
from spark.sourcing.validate_parts import ValidateParts
from spark.sourcing.write_skeleton import WriteSkeleton

# --- MVP ---
OPERATIONS = {operation.name: operation for operation in (
    ListParts, ShowPart, ValidateParts, ListSignals, ListUnverified, WriteSkeleton, ResolveSources, FetchDocuments, KeepFile,
    ReadDatasheet, FindKept, PromoteRecord, ListCatalog, ListDrawer, MarkStep, SetDrawer, ImportDrawer, SetFunction, SetFacts)}
# --- end MVP ---
