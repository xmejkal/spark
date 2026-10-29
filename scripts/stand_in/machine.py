"""
spark's stand-in for MicroPython's `machine` module (P59), so a firmware imports and runs on the Mac.

It is NOT the chip. It has a `Pin`, a `PWM`, an `ADC`, an `SPI` and `SoftSPI`, an `I2C` and `SoftI2C`, and an `I2S`.
Pins remember the level written to them, and a test sets an input with `set_level(gpio, level)` and reads an output
with `level(gpio)`. A PWM keeps the last frequency and duty set on it and makes no signal (P352). The other classes
keep their arguments and return a fixed value (P421, below). It knows nothing of which GPIO exists or of interrupts
firing. A firmware that imports any other name gets an ImportError that names this file, and `hasattr` and `getattr` with a
default see an AttributeError (P443).
"""

#: GPIO number -> the level the firmware last wrote, or a test last set. Pins share it, as pins of one chip would.
_levels = {}


def set_level(gpio, level):
    """The outside world drives an input: a button pressed or released."""
    _levels[gpio] = 1 if level else 0


def level(gpio):
    """What the firmware last wrote to a GPIO (or a test set); None while nothing has."""
    return _levels.get(gpio)


# --- MVP --- (P421) The rule for ADC, SPI, I2C and I2S: each keeps its arguments and returns a fixed value. None models a
# device. No sample, frame, sound or bus traffic is made, stored or answered. The only value that depends on an input is
# a length the caller gave. A stand-in never reports a device as present.
class _StandIn:
    """What the classes below share: any arguments, kept; a deinit that is remembered; an init that turns it on again."""

    deinited = False

    def __init__(self, *args, **settings):
        _StandIn.init(self, *args, **settings)  # not self.init: a driver's subclass may give init other arguments

    def init(self, *args, **settings):
        self.args, self.settings = args, settings
        self.deinited = False

    def deinit(self):
        self.deinited = True


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

    def __call__(self, value=None):
        """`pin(1)` writes and `pin()` reads, as `pin.value` does; a driver such as the SSD1306 SPI one uses it."""
        return self.value(value)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def irq(self, handler=None, trigger=IRQ_RISING | IRQ_FALLING, **kw):
        """Remembered, never called: the stand-in has no edges."""
        self.handler = handler


class PWM(_StandIn):
    """MicroPython's PWM as calls only: each setter keeps its value, each getter returns it, None while unset."""

    def __init__(self, dest, freq=None, **settings):
        self.pin, self.settings = dest, {}
        self.init(freq, **settings)

    def init(self, freq=None, **settings):
        """As on the ESP32, the frequency can come by position. An init after a deinit turns it on again."""
        if freq is not None:
            settings["freq"] = freq
        self.settings.update(settings)
        self.deinited = False

    def _kept(self, name, value):
        if value is None:
            return self.settings.get(name)
        self.settings[name] = value

    def freq(self, value=None):
        return self._kept("freq", value)

    def duty(self, value=None):
        return self._kept("duty", value)

    def duty_u16(self, value=None):
        return self._kept("duty_u16", value)

    def duty_ns(self, value=None):
        return self._kept("duty_ns", value)


# --- MVP --- (P421) fixed value, no device
class ADC(_StandIn):
    """A pin read as a number. Every read is 0, the same "nothing sensed" as a Pin that nothing set."""

    ATTN_0DB, ATTN_2_5DB, ATTN_6DB, ATTN_11DB = 0, 1, 2, 3
    WIDTH_9BIT, WIDTH_10BIT, WIDTH_11BIT, WIDTH_12BIT, WIDTH_13BIT = 0, 1, 2, 3, 4

    def read_u16(self):
        return 0

    def read(self):
        return 0

    def read_uv(self):
        return 0

    def atten(self, x):
        pass

    def width(self, bits):
        pass


class SPI(_StandIn):
    """A clocked data bus. Nothing is sent, and a read gives zero bytes."""

    MSB, LSB = 0, 1  # as in MicroPython's extmod/machine_spi.c

    def read(self, n, *args, **settings):
        return bytes(n)

    def write(self, buf):
        pass

    def readinto(self, buf, *args, **settings):
        pass

    def write_readinto(self, write_buf, read_buf):
        pass


class SoftSPI(SPI):
    """On a board the two are separate classes. Here a software bus is the same stand-in."""


class I2C(_StandIn):
    """A two-wire bus. No device answers, so `scan()` is empty: a module-level `assert 0x3C in i2c.scan()` fails the
    import check on a Mac. Keep such a check inside a function that main.py calls."""

    def scan(self):
        return []

    def writeto(self, addr, buf, *args, **settings):
        return len(buf)

    def readfrom(self, addr, n, *args, **settings):
        return bytes(n)

    def readfrom_mem(self, addr, mem, n, **settings):
        return bytes(n)

    def writeto_mem(self, addr, mem, buf, **settings):
        pass

    def readfrom_into(self, addr, buf, *args, **settings):
        pass

    def readfrom_mem_into(self, addr, mem, buf, **settings):
        pass

    def writevto(self, addr, vector, *args, **settings):
        return sum(len(buf) for buf in vector)

    def write(self, buf):
        return len(buf)

    def readinto(self, buf, *args, **settings):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class SoftI2C(I2C):
    """On a board the two are separate classes. Here a software bus is the same stand-in."""


class I2S(_StandIn):
    """A sound data bus. A write is taken whole. A read returns len(buf) at once and leaves the buffer as it was, by
    choice: a read that waited for sound would wait for ever. The handler is never called."""

    TX, RX, MONO, STEREO = 1, 0, 0, 1
    handler = None

    def write(self, buf):
        return len(buf)

    def readinto(self, buf):
        return len(buf)

    def irq(self, handler=None, *args, **settings):
        self.handler = handler


#: The last name asked for that this module lacks, as (name, words). Python turns the AttributeError into a bare
#: ImportError for `from machine import X`, and the import child reads this to give the words back (P443).
_missed = None


def __getattr__(name):
    global _missed
    if name.startswith("__"):  # the import machinery asks for __path__ and the like
        raise AttributeError(name)
    have = sorted(n for n, value in globals().items() if isinstance(value, type) and not n.startswith("_"))
    words = ("spark's stand-in machine (scripts/stand_in/machine.py) has %s and %s only, not %s: use only these at "
             "module level, or move the rest into a function that main.py calls" % (", ".join(have[:-1]), have[-1], name))
    _missed = (name, words)
    raise AttributeError(words)
