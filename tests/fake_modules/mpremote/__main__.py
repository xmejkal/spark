"""Fake mpremote for the bench goldens (P380, P383).

`devs` prints the canned list that FAKE_MPREMOTE_DEVS_FILE names. `exec` of reach's one line prints `reached`, and `reset`
exits 0. With FAKE_BOARD (a folder) it is also a board that was just flashed: `fs cp` keeps a file in the folder and `fs cat`
reads it back, `exec` of the hash script (ready_check.HASH_FILES) hashes `<cwd>/firmware/<path>`, which is what the image
holds, and `exec import main` prints `ready`. Any other command fails, so a golden never records an answer this fake made up.
"""

import ast
import hashlib
import os
import shutil
import sys
from pathlib import Path

args = sys.argv[1:]
if args[:1] == ["connect"]:
    args = args[2:]
board = os.environ.get("FAKE_BOARD")
if args == ["devs"]:
    sys.stdout.write(open(os.environ["FAKE_MPREMOTE_DEVS_FILE"]).read())
    sys.exit(0)
if args == ["exec", 'print("reached")']:
    print("reached")
    sys.exit(0)
if args == ["reset"]:
    sys.exit(0)
if board and args[:2] == ["fs", "cp"] and len(args) == 4:
    shutil.copy(args[2], Path(board) / args[3].lstrip(":"))
    sys.exit(0)
if board and args[:2] == ["fs", "cat"] and len(args) == 3:
    sys.stdout.write((Path(board) / args[2].lstrip(":")).read_text())
    sys.exit(0)
if board and args[:1] == ["exec"] and len(args) == 2 and args[1].startswith("import hashlib, binascii"):
    for path in ast.literal_eval(args[1].split("for p in ", 1)[1].split(":\n", 1)[0]):
        print("file", hashlib.sha256((Path.cwd() / "firmware" / path.lstrip("/")).read_bytes()).hexdigest(), path)
    sys.exit(0)
if board and args == ["exec", "import main"]:
    print("ready")
    sys.exit(0)
sys.stderr.write("fake mpremote: no canned answer for %s\n" % " ".join(sys.argv[1:]))
sys.exit(1)
