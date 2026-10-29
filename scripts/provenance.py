"""
What a fact in a record must carry: a module with no spark imports, so that a part record and a board record check
their facts by one rule. A fact is {value, verified, source}, and an unverified value says why it matters.
`parts.validate` and `boards.validate` call it.
"""

import re


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


#: A fact is written under a name of lowercase letters, digits and underscores; a name is a key that no scrub cleans.
FACT_NAME = re.compile(r"[a-z0-9_]+")


def list_type_problems(where, block):
    """
    The kinds that `verified` and `source` of a `block` must be, when they are there: `verified` true or false, and `source`
    words (not blank). A key that is missing is the caller's own sentence (`fact_problems` says "has no 'x'"). It never raises.
    """
    problems = []
    if "verified" in block and not isinstance(block["verified"], bool):
        problems.append("%s has verified %r, but it must be true or false" % (where, block["verified"]))
    if "source" in block and not (isinstance(block["source"], str) and block["source"].strip()):
        problems.append("%s has source %r, but it must be words that say where the value came from" % (where, block["source"]))
    return problems


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
    problems.extend(list_type_problems(where, fact))
    if fact.get("verified") and fact.get("value") is None:
        problems.append("%s is marked verified but has no value" % where)
    if fact.get("verified") is False and fact.get("value") is not None and not fact.get("why_it_matters"):
        # An unverified guess that nobody explains is how an assumption becomes a fact.
        problems.append("%s is an unverified value with no why_it_matters; say what depends on it or do not "
                        "carry the number" % where)
    return problems


def list_fact_problems(facts):
    """`fact_problems` of each entry of a `facts` object, spelled `facts.<name>`. A `facts` that is no object gives one problem; it never raises."""
    if not isinstance(facts, dict):
        return ["facts is %r, but it is an object of facts" % (facts,)]
    return [problem for name, fact in facts.items() for problem in fact_problems("facts.%s" % name, fact)]


def list_entry_problems(entries, held):
    """
    Why `entries`, facts to write into a record whose own `facts` is `held`, cannot be written (P374). Each name is
    lowercase letters, digits and underscores, and each entry holds under `list_fact_problems`. A `held` that is neither absent nor
    an object is one problem: repair the file by hand first, it is never read as empty. Nothing, `{}` and `[]` give no
    problem, because `parts._absent` refuses them already.
    """
    if entries is None or entries == {} or entries == []:
        return []
    problems = [] if held is None or isinstance(held, dict) else [
        "the record's own facts is %r, but it is an object — repair the file by hand first" % (held,)]
    if isinstance(entries, dict):
        problems += ["%r is no fact name: use lowercase letters, digits and underscores" % name
                     for name in entries if not FACT_NAME.fullmatch(name)]
    return problems + list_fact_problems(entries)


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
