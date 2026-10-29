"""
spark's stand-in for MicroPython's `micropython` module (P421), so a display driver's `from micropython import const`
imports on the Mac. It is NOT the interpreter: `const` gives back its argument, the decorators give back the
function they were given, uncompiled, and `alloc_emergency_exception_buf` does nothing (P443).
"""


# --- MVP --- (P421)
def alloc_emergency_exception_buf(size):
    """Keeps no buffer, as there is no interpreter to give one to."""


def const(x):
    return x


def native(function):
    return function


def viper(function):
    return function


def bytecode(function):
    return function


#: The last name asked for that this module lacks, as (name, words), for the import child to give back (P443).
_missed = None


def __getattr__(name):
    global _missed
    if name.startswith("__"):  # the import machinery asks for __path__ and the like
        raise AttributeError(name)
    have = sorted(n for n in globals() if not n.startswith("_"))
    words = ("spark's stand-in micropython (scripts/stand_in/fallback/micropython.py) has %s and %s only, not %s: use "
             "only these at module level, or move the rest into a function that main.py calls"
             % (", ".join(have[:-1]), have[-1], name))
    _missed = (name, words)
    raise AttributeError(words)
