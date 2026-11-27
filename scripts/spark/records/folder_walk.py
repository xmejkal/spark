"""
One walk of the files under a folder (P1273): every file, except those under `__pycache__`, sorted by path. The firmware
image (`image_builder.files_under`), the files newer than an image (`ProjectImage.find_newer_files`) and a check record
(P1209) read the same files. `MISSING` is what a missing file adds to a hash, beside it.
"""

from pathlib import Path

# --- MVP ---
#: What a missing file adds to a hash: not the bytes of an empty one, so a file that appears empty still changes the hash.
MISSING = b"\x00missing"


def files_under(folder):
    """Every file under FOLDER as a Path, sorted, leaving out what is under a `__pycache__` folder."""
    return [path for path in sorted(Path(folder).rglob("*")) if path.is_file() and "__pycache__" not in path.parts]
# --- end MVP ---
