"""
What a fact in a record must carry: a module with no spark imports, so that a part record and a board record check
their facts by one rule. A fact is {value, verified, source}, and an unverified value says why it matters.
`parts.validate` and `boards.validate` call it.
"""


# --- MVP ---
#: Each fact must answer all three, or it is an opinion with a number attached.
REQUIRED_FACT_KEYS = ("value", "verified", "source")


def read_value(record, *path):
    """
    The one reader of a fact's value. It walks `path` through the dicts of `record` and returns the `value` of the
    fact it reaches. A bare value where a fact belongs (a number, not {value, verified, source}) is read as the value.
    A missing key, a path through no dict, or no record gives None. It never raises.
    """
    for key in path:
        record = record.get(key) if isinstance(record, dict) else None
    return record.get("value") if isinstance(record, dict) else record


def fact_problems(where, fact):
    """
    Every way `fact` breaks the rule, as sentences that start with `where` (the caller's name for it). A fact that is
    no object gives one problem. Empty means it holds. It reads the fact only and never raises.
    """
    if not isinstance(fact, dict):
        return ["%s is %r, but it is an object" % (where, fact)]
    problems = []
    for key in REQUIRED_FACT_KEYS:
        if key not in fact:
            problems.append("%s has no %r — a number with no provenance is an opinion" % (where, key))
    if fact.get("verified") and fact.get("value") is None:
        problems.append("%s is marked verified but has no value" % where)
    if fact.get("verified") is False and fact.get("value") is not None and not fact.get("why_it_matters"):
        # An unverified guess that nobody explains is how an assumption becomes a fact.
        problems.append("%s is an unverified value with no why_it_matters; say what depends on it or do not "
                        "carry the number" % where)
    return problems
# --- end MVP ---
