"""
What a goal needs, and what the store offers for each (P96; docs/2026-10-04-store-design.md §5.3, §6.2, §8 S and M).

A need is a verb and a few words — `{"id": "soil", "does": "sense", "what": "soil-moisture"}` — with a condition only when
it decides a part, and later a mark: have, have-unknown, know or gap. The file is `<project>/.spark/needs.json`. It holds
no part numbers, no owned counts, no places and no reasons: it belongs to a project, which may be public (§5.8). Why a
need is marked as it is, is said to the person, and 1c's history keeps it. Every write sets, never adds.
"""

import json
import re
from pathlib import Path

import drawer
import parts
import store

#: How a need stands against the store (§3).
MARKS = ("have", "have-unknown", "know", "gap")
#: Each field of a need besides its `id` (§5.3): its test, and what is said when a value fails it — read and write alike.
#: A pick is 1c's, and will be one more row.
CHECKS = {"does": (lambda v: v in parts.VERBS, "`does` is one of %s" % ", ".join(parts.VERBS)),
          "what": (drawer._words, "`what` is a few words: soil-moisture, alarm, microcontroller"),
          "condition": (lambda v: v is None or drawer._words(v), "`condition` is words, or null"),
          "mark": (lambda v: v is None or v in MARKS, "`mark` is one of %s, or null" % ", ".join(MARKS))}
NEED_FIELDS = tuple(CHECKS)
FILE = Path(".spark") / "needs.json"


def read(project):
    """The project's needs, in order — [] when it has none yet; a file not in the needs shape is a StoreProblem."""
    path = Path(project) / FILE
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as broken:
        raise store.StoreProblem("%s is not JSON (%s)" % (path, broken))
    if not (isinstance(data, dict) and isinstance(data.get("needs"), list)
            and all(isinstance(need, dict) and isinstance(need.get("id"), str) for need in data["needs"])):
        raise store.StoreProblem('%s is not {"schema": 1, "needs": [{"id", "does", "what", …}]} — fix it by hand' % path)
    stray = sorted(set(data) - {"schema", "needs"})
    if stray:
        raise store.StoreProblem("%s holds %s, which a needs file does not — fix it by hand" % (path, ", ".join(stray)))
    if data.get("schema", 1) != 1:
        raise store.StoreProblem("%s is schema %r — this spark reads schema 1" % (path, data["schema"]))
    ids = [need["id"] for need in data["needs"]]
    for need in data["needs"]:
        said = ((["`id` is not lower-case letters, digits and '-'"] if not store.PLAIN.fullmatch(need["id"]) else [])
                + (["is there more than once"] if ids.count(need["id"]) > 1 else []) + faults(need, held_only=True))
        if said:
            raise store.StoreProblem("%s: need %r: %s — fix it by hand" % (path, need["id"], said[0]))
    return data["needs"]


def faults(need, held_only=False):
    """What is wrong with one need's fields (§5.3) — on read only the values the file holds: an absent one is --needs-set's to fill."""
    extra = sorted(set(need) - set(NEED_FIELDS) - {"id"})
    return (["%s: not a need's field — a need holds %s, and no part number, count, place or reason (§5.3)"
             % (", ".join(extra), ", ".join(NEED_FIELDS))] if extra else []) + [
        sentence for key, (test, sentence) in CHECKS.items() if (key in need or not held_only) and not test(need.get(key))]


def plan_set(project, items):
    """
    What a `--needs-set` would do (§8 S rule 5, M2): (the needs after, changes, problems). Each item sets fields on one
    need, by `id`; a new need needs `does` and `what`. A later item sees what an earlier one set. Nothing is written here.
    """
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return None, [], [parts._problem("the file", "a needs write is a JSON list of needs, each an object with an `id`")]
    current = {need["id"]: dict(need) for need in read(project)}
    order, changes, problems = list(current), [], []
    for number, item in enumerate(items, 1):
        need_id = item.get("id")
        if not (isinstance(need_id, str) and store.PLAIN.fullmatch(need_id)):
            problems.append(parts._problem("item %d" % number, "a need's `id` is lower-case letters, digits and '-', not %s"
                                           % json.dumps(need_id, ensure_ascii=False)))
            continue
        before = current.get(need_id)
        after = dict(before or {}, **{key: (drawer.clean(value) if isinstance(value, str) else value) for key, value in item.items()})
        problems += [parts._problem(need_id, sentence) for sentence in faults(after)]
        changed = [key for key in NEED_FIELDS if after.get(key) != (before or {}).get(key)]
        if changed:
            changes.append({"need": need_id, "new": before is None,
                            "was": {key: before.get(key) for key in changed} if before else {},
                            "now": {key: after.get(key) for key in changed}})
        order += [] if need_id in current else [need_id]
        current[need_id] = after
    return [current[need_id] for need_id in order], changes, problems


def write(project, needs):
    """The needs file, whole (`.part`, then renamed) — the project's folder made when it is new (§8 S rule 5)."""
    path = Path(project) / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    part.write_text(json.dumps({"schema": 1, "needs": needs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    part.replace(path)


#: Where a candidate lives, nearest first (§5.5); anything else is one of the person's other projects, after these.
LAYERS = ("drawer", "project", "shelf", "library", "catalog")


def _words(text):
    return {word for word in re.split(r"[^a-z0-9]+", str(text or "").lower()) if word}


def _what_matches(need, functions, names):
    """Every word of the need's `what` in a function with the need's verb, or in the record's name or an alias (§6.2)."""
    wanted = _words(need["what"])
    return bool(wanted) and (any(wanted <= _words(f.get("what")) for f in functions if f.get("does") == need["does"])
                             or wanted <= set().union(*(_words(name) for name in names)))


def _counts(holding):
    """(owned, free, unsure) over the live drawer entries (callers pass none said to be dead) — `many` stays many."""
    unsure = any(entry.get("unsure") for entry in holding)
    if any(entry.get("count") == "many" for entry in holding):
        return "many", "many", unsure
    owned = sum(entry.get("count", 0) for entry in holding)
    held = sum(sum((entry.get("used_in") or {}).values()) for entry in holding)
    return owned, max(owned - held, 0), unsure


def candidates(need, known, entries):
    """
    The store's candidates for one need (§6.2's code half): every record and every record-less drawer entry whose function
    has the need's verb, owned first, then those whose `what` is the need's, nearest first. Similar enough is the agent's call.
    """
    pointing = {}
    for entry in entries.values():
        if not entry.get("skip") and isinstance(entry.get("is"), dict) and entry["is"]:
            pointing.setdefault(next(iter(entry["is"].items())), []).append(entry)
    found, known_keys = [], set()
    for kind, record_id, where, path in known:
        record = parts._parse(path)
        holding = pointing.get((kind, record_id), [])
        if not isinstance(record, dict):
            continue
        known_keys.add((kind, record_id))
        functions = parts.function_of(record, board=kind == "board") + [f for e in holding for f in e.get("function") or []]
        if not any(f.get("does") == need["does"] for f in functions):
            continue
        aliases = record.get("also_known_as")
        names = [record.get("name")] + ([a for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else [])
        owned, free, unsure = _counts(holding)
        found.append({"id": record_id, "kind": kind, "entry": None, "in": where, "label": record.get("name"),
                      "what": sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                      "what_matches": _what_matches(need, functions, names),
                      "owned": owned, "free": free, "unsure": unsure, "owes": [] if kind == "board" else parts.owes(record),
                      "broken": kind == "part" and bool(parts.broken_problems(record, path)), "proof": []})
    for entry_id, entry in entries.items():
        functions = entry.get("function") or []
        points_at_a_record = isinstance(entry.get("is"), dict) and bool(entry["is"]) and next(iter(entry["is"].items())) in known_keys
        if points_at_a_record or entry.get("skip") or entry.get("count") == 0 or not any(f.get("does") == need["does"] for f in functions):
            continue
        owned, free, unsure = _counts([entry])
        found.append({"id": None, "kind": None, "entry": entry_id, "in": "drawer", "label": entry.get("label"),
                      "what": sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                      "what_matches": _what_matches(need, functions, [entry.get("label")]),
                      "owned": owned, "free": free, "unsure": unsure, "owes": [], "broken": False, "proof": []})
    return sorted(found, key=lambda c: (c["owned"] == 0, not c["what_matches"],
                                        LAYERS.index(c["in"]) if c["in"] in LAYERS else len(LAYERS), c["id"] or c["entry"]))


def match(project):
    """Each need with its candidates (§6.2), and a problem for each need with no verb — it cannot be matched."""
    known, entries, matched, problems = drawer.linkable(project), drawer.entries(), [], []
    for need in read(project):
        if need.get("does") not in parts.VERBS:
            problems.append(parts._problem(need.get("id"), "a need with no `does` cannot be matched — set it with --needs-set"))
            continue
        if not need.get("what"):
            problems.append(parts._problem(need["id"], "a need with no `what` cannot be matched — set it with --needs-set"))
            continue
        matched.append(dict({key: need.get(key) for key in NEED_FIELDS}, need=need["id"],
                            candidates=candidates(need, known, entries)))
    return matched, problems
