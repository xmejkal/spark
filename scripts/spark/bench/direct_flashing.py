"""
Disallow direct flashing as an Operation on the core (P1029): keep the file grants/direct_flashing_disallowed in the store.
While it is there, no deploy grant answers a deploy.py --no-simulation deploy, and grant.py --no-simulation gives no grant.
grant.py --disallow-direct-flashing is its CLI. It only narrows what a grant answers, so it asks no yes and writes at once.
To allow direct flashing again, the person deletes the file in their own hands: no Claude session writes, changes or
deletes a file in the grants folder.
"""

import shlex

from spark.bench import bench_privacy
from spark.bench import board_codes
from spark.bench import board_grant
from spark.records import store
from spark.core import outcomes
from spark.core.operation import WRITES, Argument, Operation
from spark.core.privacy import PastedLine
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines, printable

# --- MVP ---
SCRIPT = "grant.py"
#: The flag that picks this mode: grant.operation_for reads it.
DISALLOW_FLAG = "--disallow-direct-flashing"
#: The line after the write: what it does, and the line that allows direct flashing again, for the person's own hands.
DISALLOWED_LINE = ("  direct flashing disallowed: no deploy grant answers a deploy.py --no-simulation deploy while the file "
                   "is there. To allow it again, delete it yourself: rm %s")


class DisallowDirectFlashing(Operation):
    """
    Operation: keep the file that disallows direct flashing, through GrantService.disallow_direct_flashing, with who
    wrote it and when (the outside's clock). A store that refuses the write, or a folder in the file's place, is one unchecked item. It has no `--json`.
    """

    name = "disallow-direct-flashing"
    summary = ("Disallow direct flashing: no deploy grant answers a deploy.py --no-simulation deploy while the file this "
               "writes is in your store (P1029).")
    arguments = (Argument((DISALLOW_FLAG,), "disallow_direct_flashing", bool,
                          "keep the file grants/direct_flashing_disallowed in your store, at once and with no question"),)
    effects = (WRITES,)
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def run(self, *, outside, disallow_direct_flashing=True):
        try:
            path = board_grant.GrantService(now=outside.clock.now).disallow_direct_flashing()
        except (store.StoreError, OSError) as refused:  # OSError: a folder in the file's place (P1029 review)
            return OperationResult(None, [Finding(outcomes.COULD_NOT_RUN, None, board_codes.STORE_PROBLEM, str(refused), "")],
                                   diagnostics=[guard_lines("%s: %s" % (SCRIPT, refused))])
        return OperationResult({"direct_flashing_allowed": False},
                               lines=[PastedLine(DISALLOWED_LINE % shlex.quote(printable(str(path))))])  # P677: its rm line runs
# --- end MVP ---
