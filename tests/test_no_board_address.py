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
#: A full address with ':' or '-' between its bytes (mixed separators too), not part of a longer run of hex pairs.
MAC = re.compile(r"(?<![0-9a-fA-F:-])[0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5}(?![0-9a-fA-F:-])")
#: An Espressif address written with no separators (a USB serial), the spelling the first pattern cannot see.
BARE = re.compile(r"(?<![0-9a-fA-F])8cbfea[0-9a-f]{6}", re.IGNORECASE)
MADE_UP = re.compile(r"(?:8c:bf:ea:00:00:0\d|aa:bb:cc:.*|11:22:33:.*|de:ad:be:ef:.*)")


def real_addresses():
    """(file, line number) of each full address that is neither masked nor made up, in the tracked text files."""
    found = subprocess.run(["git", "grep", "-nIiE", r"[0-9a-f]{2}([:-][0-9a-f]{2}){5}|8cbfea[0-9a-f]{6}"], cwd=ROOT,
                           capture_output=True, text=True).stdout.splitlines()
    return [line.split(":", 2)[:2] for line in found if _real(line.split(":", 2)[2])]


def _real(text):
    """True when the text holds a full address that is neither masked nor made up."""
    spaced = [m.group(0).lower().replace("-", ":") for m in MAC.finditer(text)]
    bare = [m.group(0).lower() for m in BARE.finditer(text)]
    return any(not MADE_UP.fullmatch(each) for each in spaced) or any(not each.startswith("8cbfea00000") for each in bare)


class NoRealBoardAddressTest(unittest.TestCase):
    def test_no_tracked_file_holds_a_real_full_mac(self):
        self.assertEqual(real_addresses(), [], "mask it as 8c:bf:ea:xx:xx:xx, or use a made-up address in a test")


if __name__ == "__main__":
    unittest.main()
