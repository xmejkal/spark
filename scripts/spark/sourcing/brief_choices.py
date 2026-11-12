"""
What a project's brief chooses for the sourcing (P726 PR 3; the functions were `part_handlers`' since W6-S3b): the vendors
to research in, in order (`vendor_order`), and where the person buys (`sellers`). `Brief` (records) holds the words; the
default vendor order is spark's.
"""

from spark.records.brief import Brief


# --- MVP ---
#: Vendors to research in, in order, when a project's brief does not say. DFRobot first because
#: its wiki carries a pinout table and a dimension drawing for every module; Seeed next for the
#: same reason. A project overrides this in `.spark/project.json` → `prefer`.
DEFAULT_VENDOR_ORDER = ("dfrobot", "seeed")


def vendor_order(project=None):
    """The vendors to research in, from the project's brief, else the default."""
    return Brief.from_project(project).prefer or DEFAULT_VENDOR_ORDER


def sellers(project=None):
    """
    Where the person buys, local first, from the project's brief — or nothing, which the
    researcher reports as "no sellers named" rather than choosing a shop for them.
    """
    return Brief.from_project(project).sellers or ()
# --- end MVP ---
