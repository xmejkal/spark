"""
The offers of the store (P211, P743): what a need, or a search by words, can be matched to. `build(known, entries)` makes
one `matching.Offer` per readable record (a part or a board, of any layer) with the live drawer entries that say they are
it, then one per live record-less entry; `from_store(project)` builds them for everything the person's store and spark's
library hold. `pointing_at` and `counts` are the drawer arithmetic both `--match` (`spark.design.needs`) and `--need`
(`spark.sourcing.datasheets`) share, and `row` and `rank_key` the keys of a Fit's row and its order that both say the same
way (P783). It reads records through `record_kind._parse` and the drawer through `drawer`, and
imports nothing of the design layer. Moved here from `needs.py` by P743, so that `--need` could use it.
"""

from spark.records.record_kind import _parse
from spark.sourcing import drawer, matching

# --- MVP ---
#: The `in` of an offer that is a drawer entry with no record, and of a Fit's context for it.
DRAWER = "drawer"


def counts(holding, mine=None):
    """
    (owned, free, unsure) over the live drawer entries (callers pass none said to be dead) — `many` stays many, an entry
    with no count is owned, count unknown (the PO, 2026-10-06), and what `mine`, the asking project, holds is free to it:
    only other projects' reservations are not free.
    """
    unsure = any(entry.get("unsure") for entry in holding)
    if any(entry.get("count") == "many" for entry in holding):
        return "many", "many", unsure
    if any("count" not in entry for entry in holding):
        return "unknown", "unknown", unsure
    owned = sum(entry["count"] for entry in holding)
    held = sum(n for entry in holding for who, n in (entry.get("used_in") or {}).items() if who != mine)
    return owned, max(owned - held, 0), unsure


def row(fit, context, said, mine=None):
    """
    One row of a Fit for `--match`'s candidates and `--need`'s rows: `id` (a record's) or `entry` (a drawer entry with no
    record), then what the caller `said`, then `in` (the layer), `owned` (the drawer count: a number, "many" or "unknown"),
    `score` and `why`. `context` is `build`'s for the Fit's offer; `mine` is `counts`'.
    """
    record_less = context["record"] is None
    return {"id": None if record_less else fit.offer.key, "entry": fit.offer.key if record_less else None, **said,
            "in": context["in"], "owned": counts(context["holding"], mine)[0], "score": fit.score, "why": fit.why}


def rank_key(row):
    """The order of rows: what is owned first, then the best score. A caller adds its own tie-breaks after it."""
    return (row["owned"] == 0, -row["score"])


def pointing_at(entries):
    """{(kind, id): [(entry key, entry)]} for every live drawer entry that says what it is — one said to be dead holds nothing."""
    pointing = {}
    for entry_id, entry in entries.items():
        if not entry.get("skip") and isinstance(entry.get("is"), dict) and entry["is"]:
            pointing.setdefault(next(iter(entry["is"].items())), []).append((entry_id, entry))
    return pointing


def build(known, entries):
    """
    Every offer in the store (P211) as [(Offer, context)]: each readable record with the live drawer entries that say they
    are it, then each live record-less entry that holds any. Context is {"record", "in", "path", "holding"}. Nothing costly
    runs here: what a record owes is asked only of an offer a matcher admits.
    """
    pointing, built, known_keys = pointing_at(entries), [], set()
    for kind, record_id, where, path in known:
        record = _parse(path)
        if not isinstance(record, dict):
            continue
        known_keys.add((kind, record_id))
        holding = [entry for _, entry in pointing.get((kind, record_id), [])]
        built.append((matching.Offer.from_record(record_id, kind, record, holding),
                      {"record": record, "in": where, "path": path, "holding": holding}))
    for entry_id, entry in entries.items():
        points_at_a_record = isinstance(entry.get("is"), dict) and bool(entry["is"]) and next(iter(entry["is"].items())) in known_keys
        if not (points_at_a_record or entry.get("skip") or entry.get("count") == 0):
            built.append((matching.Offer.from_entry(entry_id, entry), {"record": None, "in": DRAWER, "path": None, "holding": [entry]}))
    return built


def from_store(project=None):
    """The offers of everything the store holds for `project`: its records, the shelf, the library, the catalog, the other
    projects' records (`drawer.linkable`), and the drawer's entries."""
    return build(drawer.linkable(project), drawer.entries())
