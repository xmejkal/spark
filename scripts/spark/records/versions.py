"""
Version numbers compared: a pin against the release installed (P214), and an installed release against the oldest one
spark runs (P471, #642).

Reads only the metadata of an installed module. In the floor compare (`release_tuple`) a pre-release counts as its release; `release` keeps it.
"""

import importlib.metadata


def installed_release(entry):
    """A Python tool's module version as installed for this interpreter, or None without metadata."""
    try:
        return importlib.metadata.version(entry["module"])
    except importlib.metadata.PackageNotFoundError:
        return None


def too_old(entry):
    """The installed release of a Python tool that is older than its `oldest_version`, else None."""
    here = installed_release(entry) if entry.get("kind") == "python" else None
    return here if is_older(here, entry.get("oldest_version")) else None


def release(version):
    """A version without its trailing zero parts, so a pin of 5.5 is the 5.5.0 installed, as pip counts it."""
    parts = str(version).split(".")
    while len(parts) > 1 and parts[-1] == "0":
        parts.pop()
    return ".".join(parts)


def release_tuple(version):
    """A version as a tuple to compare: the leading digits of each dotted part, up to the first part that is not all
    digits, and no trailing zeros. So 5.0, 5.0.0, 5.0.0b1, 5.0.dev0 and 5.0.post1 are all (5,). None for no digits."""
    parts = []
    for part in str(version).split("."):
        digits = part[:len(part) - len(part.lstrip("0123456789"))]
        if not digits:
            break
        parts.append(int(digits))
        if digits != part:
            break
    while parts and parts[-1] == 0:
        parts.pop()
    return tuple(parts) or None


def is_older(here, oldest):
    """True when `here` is below `oldest`. False when either is missing or has no digits: that refuses nothing."""
    if not here or not oldest:
        return False
    return None not in (release_tuple(here), release_tuple(oldest)) and release_tuple(here) < release_tuple(oldest)
