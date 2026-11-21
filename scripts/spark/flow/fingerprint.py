"""
The fingerprint of a project's flow (P829): the sha256 of its current offers and of the three files a click changes, so a
page that was read before the project changed can be told apart from the project now. The offers count, because one
reads the drawer: "You have none" becomes "Uses 1 of your 3" with no file of the project changed. The page carries its first
SHORT hex digits. The person never sees it.
"""

import hashlib
import json
from pathlib import Path

from spark.build.build_record import BUILD_RECORD_FILE
from spark.design import needs
from spark.flow.phase_readers import REQUIREMENTS_FILE

# --- MVP ---
#: The project's files the fingerprint reads, from the project's folder: the needs, the parts list and the last build.
FILES = (needs.FILE, Path(REQUIREMENTS_FILE), BUILD_RECORD_FILE)
#: What a missing file adds: not the bytes of an empty one, so a file that appears empty still changes the fingerprint.
MISSING = b"\x00missing"
#: How many hex digits the page and a request carry.
SHORT = 12


def fingerprint_of(project, phases):
    """The sha256, in hex, of the offers of `phases` (each Phase's key, effect and makes_stale, as canonical JSON) and of
    each of FILES in `project`, in that order."""
    offers = [{"key": offer.key, "effect": offer.effect, "makes_stale": list(offer.makes_stale)}
              for phase in phases for offer in phase.offers]
    digest = hashlib.sha256()
    digest.update(json.dumps(offers, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for name in FILES:
        path = Path(project) / name
        digest.update(hashlib.sha256(path.read_bytes() if path.is_file()
                                     else MISSING).digest())
    return digest.hexdigest()
# --- end MVP ---
