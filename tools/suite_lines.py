"""
The lines of unittest's verdict that say what went red (P787, P797): `tools/mutate.py` names a red pre-check's tests with
them, and `tools/check_commit.py` prints a red push's.

Standard library only: both tools import it, and it must not pull in the product.
"""

import re

#: A line of unittest's verdict that names a red test or sums the red run.
RED_LINE = re.compile(r"^(?:(?:FAIL|ERROR): .*|FAILED \(.*|Ran \d+ tests? in .*|[\w.]+Error: .*)$", re.M)
#: The sums among them: the gate's verdict line already says these.
SUMS = ("Ran ", "FAILED")
#: The start of the line that names one red test; its error lines follow it.
TEST_NAMED = ("FAIL: ", "ERROR: ")


# --- MVP ---
def red_tests(said):
    """The lines of `said`, a run's output, that name a red test or its error: each `FAIL:`, `ERROR:` and `...Error:` line."""
    return [line for line in RED_LINE.findall(said) if not line.startswith(SUMS)]
