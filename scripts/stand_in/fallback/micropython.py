"""
spark's stand-in for MicroPython's `micropython` module (P421), so a display driver's `from micropython import const`
imports on the Mac. It is NOT the interpreter: `const` gives back its argument, and the decorators give back the
function they were given, uncompiled.
"""


# --- MVP --- (P421)
def const(x):
    return x


def native(function):
    return function


def viper(function):
    return function


def bytecode(function):
    return function


def __getattr__(name):
    if name.startswith("__"):  # the import machinery asks for __path__ and the like
        raise AttributeError(name)
    have = sorted(n for n in globals() if not n.startswith("_"))
    raise ImportError("spark's stand-in micropython (scripts/stand_in/fallback/micropython.py) has %s and %s only, "
                      "not %s: use only these at module level, or move the rest into a function that main.py calls"
                      % (", ".join(have[:-1]), have[-1], name))
