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


#: The twelve month words (P1062): the one list for a day said in words, here, in `wired_board.day_of` and in the page
#: script's words block.
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def day_and_time(iso):
    """A stored time said as "23 Nov 2026, 14:18" in the machine's zone (P1062); a time that does not parse, as written."""
    try:
        moment = datetime.datetime.fromisoformat(iso).astimezone()
    except (TypeError, ValueError):
        return iso
    return "%d %s %d, %02d:%02d" % (moment.day, MONTHS[moment.month - 1], moment.year, moment.hour, moment.minute)
