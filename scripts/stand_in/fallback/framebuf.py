"""
spark's stand-in for MicroPython's `framebuf` module (P421), so a display driver that subclasses `FrameBuffer`
imports on the Mac. It is NOT a picture: nothing is drawn or stored, and a pixel reads 0.
"""

# --- MVP --- (P421) The format names are MicroPython's; the numbers are distinct small integers that nothing reads.
MONO_VLSB, MONO_HLSB, MONO_HMSB, RGB565, GS2_HMSB, GS4_HMSB, GS8 = range(7)


def _nothing(self, *args, **settings):
    """A drawing call: it keeps nothing and draws nothing."""


class FrameBuffer:
    """MicroPython's FrameBuffer as calls only. A driver's subclass draws into the buffer it gave, and here the buffer
    is left as it is."""

    def __init__(self, buffer, width, height, format, stride=None):
        """Keeps nothing, as the C class keeps nothing on the Python object: a driver's subclass may define `width`
        as a property."""

    fill = hline = vline = line = rect = fill_rect = text = scroll = blit = ellipse = poly = _nothing

    def pixel(self, x, y, c=None):
        """No colour reads the pixel, which is 0; a colour sets it, and nothing is kept."""
        return 0 if c is None else None


#: The last name asked for that this module lacks, as (name, words), for the import child to give back (P443).
_missed = None


def __getattr__(name):
    global _missed
    if name.startswith("__"):  # the import machinery asks for __path__ and the like
        _missed = None  # a dunder miss is not the name an earlier probe left
        raise AttributeError(name)
    have = sorted(n for n in globals() if not n.startswith("_"))
    words = ("spark's stand-in framebuf (scripts/stand_in/fallback/framebuf.py) has %s and %s only, not %s: use only "
             "these at module level, or move the rest into a function that main.py calls"
             % (", ".join(have[:-1]), have[-1], name))
    _missed = (name, words)
    raise AttributeError(words)
