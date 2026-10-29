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


#: A top-level block that vouches for a fact of the record (`pin_order_proof` for `pin_order`): the fact it vouches for,
#: and the sentence that says what depends on it. Its row comes right after the facts.
PROOF_BLOCKS = {"pin_order_proof": ("pin_order", "a pin order read wrong reverses a supply or swaps a signal")}

#: What a top-level block carries besides the value it vouches for. The rest of the block is its `assumed`.
BLOCK_NOTES = ("verified", "source", "why_it_matters", "cites")


def _unverified_row(fact, assumed, block, write, why=None):
    """One row of `list_unverified_facts`: `write` is the key a result goes back to, a constant and never English."""
    return {"fact": fact, "assumed": assumed, "why_it_matters": why or block.get("why_it_matters") or "",
            "source": block.get("source", ""), "write": write}


def list_unverified_facts(record):
    """
    Every fact in a part record whose `verified` is not true, as rows {fact, assumed, why_it_matters, source, write}.
    First each entry of `facts` (an entry that is no object counts as unchecked), then the `PROOF_BLOCKS`, then each other
    top-level object with a `verified` key, such as `body_mm`, in record order. `write` names where the result goes back:
    `facts.<name>`, `pin_order_proof` or `body_mm`. A `facts` that is no object gives one row with `write` None. It never raises.
    """
    facts = record.get("facts") or {}
    if not isinstance(facts, dict):
        return [{"fact": "facts", "assumed": facts, "write": None, "source": "",
                 "why_it_matters": "facts is not an object, so nothing in it can be read — repair the file by hand"}]
    rows = [_unverified_row(name, fact.get("value") if isinstance(fact, dict) else fact,
                            fact if isinstance(fact, dict) else {}, "facts." + name)
            for name, fact in facts.items() if not (isinstance(fact, dict) and fact.get("verified") is True)]
    for key, (proves, why) in PROOF_BLOCKS.items():
        proof = record.get(key)
        if isinstance(proof, dict) and proof.get("verified") is not True:
            rows.append(_unverified_row(proves, record.get(proves), proof, key, why))
    for key, block in record.items():
        if key not in PROOF_BLOCKS and key != "facts" and isinstance(block, dict) and "verified" in block \
                and block["verified"] is not True:
            rows.append(_unverified_row(key, {k: v for k, v in block.items() if k not in BLOCK_NOTES}, block, key))
    return rows
# --- end MVP ---
