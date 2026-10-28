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
        self.buffer, self.width, self.height, self.format = buffer, width, height, format

    fill = hline = vline = line = rect = fill_rect = text = scroll = blit = ellipse = poly = _nothing

    def pixel(self, x, y, c=None):
        """No colour reads the pixel, which is 0; a colour sets it, and nothing is kept."""
        return 0 if c is None else None


def __getattr__(name):
    if name.startswith("__"):  # the import machinery asks for __path__ and the like
        raise AttributeError(name)
    raise ImportError("spark's stand-in framebuf (scripts/stand_in/framebuf.py) has FrameBuffer and the format "
                      "constants only, not %s" % name)
