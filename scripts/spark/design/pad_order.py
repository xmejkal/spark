"""
The order in which `pin_assigner.assign` offers the free pads to a signal, and why a signal takes a bus pad (P1010).

The PO's order of 2026-11-22, "Plain pads before bus pads", which reverses P780's of 2026-11-13: first the pads that no
other rule keeps, the plain ones before the SPI pads and those before the I2C pads; then the kept pads, by cost. A pad
is kept when it would waste an ADC1 reading or when something else is wired to it (the console, a button, an LED, a
display, the battery sense). An I2C sensor needs both I2C pads, and a write-only SPI part leaves MISO unused, so I2C
goes last.

No single bus penalty gave this order. Measured on the FireBeetle 2 ESP32-C6, 2026-11-22: for a plain signal, SDA, SCL
and MISO cost 13 (pwm and the bus penalty 5), and D11 costs 16 (pwm and wake), so the walk P934's EPD_RST and EPD_BUSY
took SDA and SCL while D11 was free. A penalty above 8 fixes the C6, but on the FireBeetle 2 ESP32-S3 an SPI penalty
above 6 sends a plain signal onto an ADC1 pin (MOSI costs 22, an ADC1 pin 24): the regression of 2026-09-29. So the
bus is a tier of the sort key, after the kept tier, and the penalty still orders the kept pads.
"""

#: The bus roles, in the order a signal that is no bus line takes their pads: an I2C sensor needs both I2C pads, and a
#: write-only SPI part leaves MISO unused.
BUS_ORDER = ("spi", "i2c")

#: The why of a signal on a bus pad: its needs, why no pad with no bus role served, and the bus.
BUS_PAD_WHY = "needs %s; %s, so this %s pad is spent here"

#: When pads with no bus role are free: each is kept, and the words name them by their reason.
KEPT_PADS = "the free pins with no bus role are kept for another job (%s)"

#: When no pad with no bus role that could serve is free.
NO_PAD_LEFT = "every pin with no bus role that could serve is taken"

#: The why of a plain signal on a pad with no bus role while a free bus pad costs less.
NO_BUS_ROLE_WHY = "needs nothing special; the cheapest pin left with no bus role could still %s, which is spent here"


class PadOrder:
    """
    Strategy: the sort key of the free pads for one signal, and the why of a pad the key chose for a bus pad. `cost` is
    the assigner's `_cost(pin, needs)` and `conflicting` its CONFLICTING_ROLES, given as arguments so this module
    imports nothing of the assigner. A pin is the assigner's dict: `gpio`, `can` and `roles`.
    """

    def __init__(self, cost, conflicting, buses=BUS_ORDER):
        self.cost = cost
        self.conflicting = tuple(conflicting)
        self.buses = tuple(buses)

    def reasons(self, pin, needs):
        """Why the pad is kept for another job: "adc" when the signal would waste it, then its conflicting roles."""
        return (["adc"] if "adc" in pin["can"] - set(needs) else []) + [role for role in pin["roles"] if role in self.conflicting]

    def bus(self, pin):
        """The first bus of the order that the pad carries, or None."""
        return next((bus for bus in self.buses if bus in pin["roles"]), None)

    def rank(self, pin, needs):
        """The sort key: kept last, then the bus tier (0 for no bus or a kept pad), the cost and the GPIO."""
        kept = bool(self.reasons(pin, needs))
        bus = self.bus(pin)
        tier = 0 if kept or bus is None else 1 + self.buses.index(bus)
        return (kept, tier, self.cost(pin, needs), pin["gpio"])

    def why(self, needs, pin, free):
        """
        The why of a pad, or None for the assigner's own words. `free` is the free pads that could serve, by label, the
        chosen one too. A pad with another job wired to it keeps the assigner's words, which say so.
        """
        if any(role in self.conflicting for role in pin["roles"]):
            return None
        bus = self.bus(pin)
        if bus:
            spare = sorted(pin["can"] - set(needs))
            said = BUS_PAD_WHY % (", ".join(sorted(needs)) or "nothing special", self.kept_words(needs, pin, free),
                                  bus.upper())
            return said + (", though it could still %s" % " and ".join(spare) if spare else "")
        cheaper = any(self.bus(other) and self.cost(other, needs) < self.cost(pin, needs) for other in free.values())
        if not needs and pin["can"] and cheaper:
            return NO_BUS_ROLE_WHY % " and ".join(sorted(pin["can"]))
        return None

    def kept_words(self, needs, pin, free):
        """The kept free pads with no bus role, grouped by their reason in the pads' order, or NO_PAD_LEFT."""
        groups = {}
        for label, other in free.items():
            if other["gpio"] != pin["gpio"] and not self.bus(other):
                groups.setdefault(" and ".join(self.reasons(other, needs)), []).append(label)
        if not groups:
            return NO_PAD_LEFT
        return KEPT_PADS % "; ".join("%s: %s" % (reason, _listed(labels)) for reason, labels in groups.items())


def _listed(labels):
    """"A", "A and B", "A, B and C"."""
    return labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
