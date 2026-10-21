"""Fake mpremote for the bench goldens (P380).

`devs` prints the canned list that FAKE_MPREMOTE_DEVS_FILE names. `exec` of reach's one line prints `reached`.
Any other command fails, so a golden never records an answer this fake made up.
"""

import os
import sys

args = sys.argv[1:]
if args[:1] == ["connect"]:
    args = args[2:]
if args == ["devs"]:
    sys.stdout.write(open(os.environ["FAKE_MPREMOTE_DEVS_FILE"]).read())
    sys.exit(0)
if args == ["exec", 'print("reached")']:
    print("reached")
    sys.exit(0)
sys.stderr.write("fake mpremote: no canned answer for %s\n" % " ".join(sys.argv[1:]))
sys.exit(1)
