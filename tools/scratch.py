"""
Remove a run's old scratch folders from a temp folder (P435).

Standard library only: `tests/suite_temp.py` imports it, and it must not pull in the product.
"""

import os
import shutil
import stat

#: A folder untouched for this long belongs to a run that is over: a live run is younger than a day.
OLD_AFTER_SECONDS = 24 * 3600


# --- MVP ---
def remove_tree(folder):
    """
    Remove `folder` with all it holds, also a read-only folder inside it (P435); True when it is gone. A first plain
    removal ignores errors. If something stays, every folder under it gets u+rwx (never following a link), and the
    removal runs again.
    """
    if os.path.islink(folder):  # a link is never opened up or followed: its target is not ours
        return False
    shutil.rmtree(folder, ignore_errors=True)
    if os.path.lexists(folder):
        stack = [folder]
        while stack:
            here = stack.pop()
            try:
                os.chmod(here, stat.S_IRWXU)
                stack += [entry.path for entry in os.scandir(here) if entry.is_dir(follow_symlinks=False)]
            except OSError:
                continue
        shutil.rmtree(folder, ignore_errors=True)
    return not os.path.lexists(folder)


# --- MVP ---
def remove_old_folders(parent, prefix, now, owner=None):
    """
    Remove the folders in `parent` that are ours and old; the names removed, sorted.

    Ours, proved in this order: the name starts with `prefix`; `os.lstat` (never follows a link) says a plain directory;
    its owner is `owner` (default: this user); the folder's own mtime (nothing inside is looked at) is older than
    OLD_AFTER_SECONDS before `now`. Anything that fails a step stays, and a name is listed only if the folder is gone.
    A racing sweep is harmless: the removal ignores errors.
    """
    owner = os.getuid() if owner is None else owner
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
        if not stat.S_ISDIR(found.st_mode) or found.st_uid != owner:
            continue
        if found.st_mtime < now - OLD_AFTER_SECONDS and remove_tree(full):
            removed.append(name)
    return removed
