"""
Remove a run's old scratch folders from a temp folder (P435).

Standard library only: `tests/suite_temp.py` imports it, and it must not pull in the product.
"""

import os
import shutil
import stat

#: A folder untouched for this long belongs to a run that is over: a live run is younger than a day.
OLD_AFTER_SECONDS = 24 * 3600


def remove_old_folders(parent, prefix, now, owner=None):
    """
    Remove the folders in `parent` that are ours and old; the names removed, sorted.

    Ours, proved in this order: the name starts with `prefix`; `os.lstat` (never follows a link) says a plain directory;
    its owner is `owner` (default: this user); its mtime is older than OLD_AFTER_SECONDS before `now`. Anything that
    fails a step stays. A racing sweep is harmless: the removal ignores errors.
    """
    owner = getattr(os, "getuid", lambda: None)() if owner is None else owner
    removed = []
    try:
        names = sorted(os.listdir(parent))
    except OSError:
        return removed
    for name in names:
        if not name.startswith(prefix):
            continue
        full = os.path.join(parent, name)
        try:
            found = os.lstat(full)
        except OSError:
            continue
        if not stat.S_ISDIR(found.st_mode) or (owner is not None and found.st_uid != owner):
            continue
        if found.st_mtime < now - OLD_AFTER_SECONDS:
            shutil.rmtree(full, ignore_errors=True)
            removed.append(name)
    return removed
