"""
The computer's clock (P475 made it the one clock of the bench; P605 moved it into the core, where `run_operation`
times a run with it).
"""

import datetime
import time


# --- MVP ---
class SystemClock:
    """Adapter: the computer's own clock. `now` is the time in the machine's zone, with the zone (P291): the zone a person
    reads, and a stored time carries it."""

    monotonic, sleep = staticmethod(time.monotonic), staticmethod(time.sleep)

    @staticmethod
    def now():
        return datetime.datetime.now().astimezone()
# --- end MVP ---
