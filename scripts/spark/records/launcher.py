"""
The launcher (P920, #1302): the file in spark's store that a tool outside spark runs to reach `bench.py`, so it needs only
the store's path and any `python3`. `bench.py register` writes it again at every run, which is also its repair.

The launcher starts spark's `scripts/bench.py` with the Python that ran `register` (the system `python3` may have no
mpremote), passes the arguments on and returns the exit code. Its child's SPARK_HOME is the store the launcher lives in,
found from the launcher's own place at run time, so a caller whose environment names another store still reaches this one. When that Python or that script is gone, it prints one JSON
line in the envelope's shape, with the code `launcher_stale`, and exits 2. No path to spark's code stays valid after a
plugin update or a removed worktree, so a person registers from a checkout that stays.
"""

import sys
from pathlib import Path

from spark.core import outcomes
from spark.records import store

# --- MVP ---
PLACE = "launcher"
#: The script the launcher runs: spark's bench.py, by its whole path.
BENCH_SCRIPT = Path(__file__).resolve().parents[2] / "bench.py"
#: The code of the launcher's own line: the code it runs is gone.
LAUNCHER_STALE = "launcher_stale"
STALE_SENTENCE = "the Python or the bench.py that spark's launcher runs is gone, so nothing ran"
STALE_FIX = ("run bench.py register <name> --origin <origin> --tool <tool> again from a spark checkout that stays: it writes "
             "the launcher again")
#: The launcher's text: Python 3.9 and later, the standard library only. %(...)r are the Python, the script and the line.
TEXT = '''#!/usr/bin/env python3
"""spark's launcher for bench.py, written by bench.py register (P920). Run it with any python3: it starts spark's bench.py
with the Python that registered, on the store this file lives in, passes the arguments on and returns the exit code. When
that Python or that bench.py is gone, it prints one JSON line and exits 2. Do not edit it: bench.py register writes it again."""
import json
import os
import subprocess
import sys

PYTHON, SCRIPT = %(python)r, %(script)r
STORE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not (os.access(PYTHON, os.X_OK) and os.path.isfile(SCRIPT)):
    print(json.dumps(%(stale)r, separators=(",", ":")))
    sys.exit(%(exit)d)
sys.exit(subprocess.call([PYTHON, SCRIPT] + sys.argv[1:], env=dict(os.environ, SPARK_HOME=STORE)))
'''


def stale_line():
    """The envelope the launcher prints when the code it runs is gone: bench's, with no op and one unchecked item."""
    return outcomes.envelope("bench", None, None, [], [{"code": LAUNCHER_STALE, "sentence": STALE_SENTENCE, "fix": STALE_FIX}])


def write_launcher(python=sys.executable, script=BENCH_SCRIPT):
    """Write the launcher into the store, private, for `python` and `script` (default: this Python and this bench.py), and
    return its path. store.StoreError when the store refuses the write."""
    store.write_place(PLACE, TEXT % {"python": str(python), "script": str(script), "stale": stale_line(),
                                    "exit": outcomes.EXIT_COULD_NOT_RUN})
    return store.place(PLACE)
# --- end MVP ---
