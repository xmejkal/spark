"""
spark's stand-in for MicroPython's `machine` module (P59), so a firmware imports and runs on the Mac.

It is NOT the chip. It has a `Pin` and nothing else: pins remember the level written to them, and a test sets an input
with `set_level(gpio, level)` and reads an output with `level(gpio)`. It knows nothing of which GPIO exists, of
interrupts firing, of PWM, I2C or SPI. A firmware that imports those gets an ImportError that names this file.
"""

#: GPIO number -> the level the firmware last wrote, or a test last set. Pins share it, as pins of one chip would.
_levels = {}


def set_level(gpio, level):
    """The outside world drives an input: a button pressed or released."""
    _levels[gpio] = 1 if level else 0


def level(gpio):
    """What the firmware last wrote to a GPIO (or a test set); None while nothing has."""
    return _levels.get(gpio)


class Pin:
    IN, OUT, PULL_UP, PULL_DOWN, IRQ_RISING, IRQ_FALLING = 1, 3, 2, 1, 1, 2

    def __init__(self, id, mode=-1, pull=-1, *, value=None):
        self.id, self.handler = id, None
        self.init(mode, pull, value=value)

    def init(self, mode=-1, pull=-1, *, value=None):
        self.mode, self.pull = mode, pull
        if value is not None:
            self.value(value)

    def value(self, x=None):
        """No argument reads the level; an input nothing set reads 1 with a pull-up, else 0."""
        if x is None:
            return _levels.get(self.id, 1 if self.pull == self.PULL_UP else 0)
        _levels[self.id] = 1 if x else 0

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def irq(self, handler=None, trigger=IRQ_RISING | IRQ_FALLING, **kw):
        """Remembered, never called: the stand-in has no edges."""
        self.handler = handler


def __getattr__(name):
    if name.startswith("__"):  # the import machinery asks for __path__ and the like
        raise AttributeError(name)
    raise ImportError("spark's stand-in machine (scripts/stand_in/machine.py) has Pin only, not %s" % name)
