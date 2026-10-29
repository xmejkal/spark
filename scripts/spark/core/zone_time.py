"""
Times as spark stores and says them (P291, P315, P401): in the machine's zone, with the zone. A module with no spark
imports, so that the store's readers and the grant both use it without importing each other.
"""

import datetime


def stamp(moment):
    """A time as the store keeps it: ISO 8601 to the second, in the machine's zone, with the zone."""
    return moment.astimezone().isoformat(timespec="seconds")


def say_in_local_zone(iso):
    """A stored time with its zone, said in the machine's zone (P315): a grant kept in UTC before P291 too."""
    return stamp(datetime.datetime.fromisoformat(iso))
