"""
The pins a live try must not touch (P254, #266, D14): a board record's `usb` and `flash` roles, and the reason code is
refused when it writes one of their numbers.

A library. P247 (#267) calls `RestrictedPins.from_board(record).why_refused(code)` before a live try runs anything.

    RestrictedPins    a Value with one lookup method: each restricted GPIO with its role and note, from a board record.
    whole_numbers_in  every whole number written in the code, read with Python's own parser (ast).

It refuses too much on purpose: any restricted number anywhere in the code is refused, `time.sleep(12)` and an I2C
address 0x1C too, and the sentence says so. A number computed at run time, such as `Pin(6 * 2)`, passes: the code's
text does not hold it.
"""

import ast

#: The pin roles whose numbers a live try refuses (D14). Each is one of boards.PIN_ROLES.
REFUSED_ROLES = ("usb", "flash")
#: The sentence for code that Python's parser cannot read.
DOES_NOT_PARSE = "the code does not parse as Python, so spark cannot tell which pins it names"
#: The sentence for a restricted number: the number, the GPIO, its role and the record's note with its sources.
WRITES_A_RESTRICTED_PIN = "it writes the number {gpio} (any number, not only a pin), and GPIO{gpio} is this board's {role} pin: {note}"


def whole_numbers_in(code):
    """Every whole number written in `code`, as a set of ints, or None when Python's parser cannot read it. `-12` counts
    as 12, a bool is no number, and a number inside a string is not read."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return None
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool)}


class RestrictedPins:
    """Value: each restricted GPIO of one board, with its role and note (the note cites the sources). It has one lookup
    method, `why_refused`."""

    def __init__(self, roles):
        self.roles = roles  # {gpio: (role, note)}

    @classmethod
    def from_board(cls, board):
        """The restricted pins a board record names in its `pin_roles`, under one of REFUSED_ROLES."""
        found = {}
        for role in REFUSED_ROLES:
            spec = (board.get("pin_roles") or {}).get(role) or {}
            for gpio in spec.get("gpio") or []:
                found[gpio] = (role, spec.get("note", ""))
        return cls(found)

    def has_none(self):
        """True when the record names no restricted pin, so a check against it refuses nothing."""
        return not self.roles

    def why_refused(self, code):
        """None when `code` may run, else the sentence that says why not: it does not parse, or it writes a restricted
        number (the lowest one is named)."""
        numbers = whole_numbers_in(code)
        if numbers is None:
            return DOES_NOT_PARSE
        hits = sorted(numbers & set(self.roles))
        if not hits:
            return None
        role, note = self.roles[hits[0]]
        return WRITES_A_RESTRICTED_PIN.format(gpio=hits[0], role=role, note=note)
