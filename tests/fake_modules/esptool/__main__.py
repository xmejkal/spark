"""Fake esptool for the bench goldens (P380, P383): `flash-id` prints the canned output that FAKE_ESPTOOL_FLASH_ID_FILE names.
`erase-flash` prints one line on stdout and exits 2, the code on which deploy retries the erase, so a golden holds the
flash tool's own output and the retry line (P508). With FAKE_BOARD set (the board mpremote's fake keeps), `erase-flash` and
`write-flash` print one line and exit 0, so a deploy goes through to the board's start.

A child runs `python -m esptool`, so this package, first on PYTHONPATH, stands in for the real one.
"""

import os
import sys

if "flash-id" in sys.argv:
    sys.stdout.write(open(os.environ["FAKE_ESPTOOL_FLASH_ID_FILE"]).read())
    sys.exit(0)
if os.environ.get("FAKE_BOARD") and ("erase-flash" in sys.argv or "write-flash" in sys.argv):
    sys.stdout.write("fake esptool: %s done\n" % ("erase-flash" if "erase-flash" in sys.argv else "write-flash"))
    sys.exit(0)
if "erase-flash" in sys.argv:
    sys.stdout.write("fake esptool: erase-flash failed\n")
    sys.exit(2)
sys.stderr.write("fake esptool: no canned answer for %s\n" % " ".join(sys.argv[1:]))
sys.exit(2)
