"""
Version numbers compared: a pin against the release installed (P214), and an installed release against the oldest one
spark runs (P471, #642).

A pure helper, no I/O. A pre-release counts as its release, as `tools.py` counts a pin.
"""


def release(version):
    """A version without its trailing zero parts, so a pin of 5.5 is the 5.5.0 installed, as pip counts it."""
    parts = str(version).split(".")
    while len(parts) > 1 and parts[-1] == "0":
        parts.pop()
    return ".".join(parts)


def key(version):
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
    return None not in (key(here), key(oldest)) and key(here) < key(oldest)
