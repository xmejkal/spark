"""P505 (#694): no tracked file holds a real board's full MAC address. A full address is either masked (its last three
bytes `xx`) or made up for a test (`8c:bf:ea:00:00:0N`, `aa:bb:cc:...`, `11:22:33:...`, `de:ad:be:ef:...`)."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
MAC = re.compile(r"[0-9a-fA-F]{2}([:-])[0-9a-fA-F]{2}(?:\1[0-9a-fA-F]{2}){4}")
MADE_UP = re.compile(r"(?:8c:bf:ea:00:00:0\d|aa:bb:cc:.*|11:22:33:.*|de:ad:be:ef:.*|.*:xx:xx:xx)")


def real_addresses():
    """(file, line number) of each full address that is neither masked nor made up, in the tracked text files."""
    found = subprocess.run(["git", "grep", "-nIE", r"[0-9a-fA-F]{2}([:-][0-9a-fA-F]{2}){5}"], cwd=ROOT,
                           capture_output=True, text=True).stdout.splitlines()
    return [line.split(":", 2)[:2] for line in found
            if any(not MADE_UP.fullmatch(m.group(0).lower().replace("-", ":")) for m in MAC.finditer(line.split(":", 2)[2]))]


class NoRealBoardAddressTest(unittest.TestCase):
    def test_no_tracked_file_holds_a_real_full_mac(self):
        self.assertEqual(real_addresses(), [], "mask it as 8c:bf:ea:xx:xx:xx, or use a made-up address in a test")


if __name__ == "__main__":
    unittest.main()
