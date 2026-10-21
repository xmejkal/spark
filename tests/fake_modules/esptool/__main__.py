"""Fake esptool for the bench goldens (P380): `flash_id` prints the canned output that FAKE_ESPTOOL_FLASH_ID_FILE names.

A child runs `python -m esptool`, so this package, first on PYTHONPATH, stands in for the real one.
"""

import os
import sys

if "flash_id" in sys.argv:
    sys.stdout.write(open(os.environ["FAKE_ESPTOOL_FLASH_ID_FILE"]).read())
    sys.exit(0)
sys.stderr.write("fake esptool: no canned answer for %s\n" % " ".join(sys.argv[1:]))
sys.exit(2)
