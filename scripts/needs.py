"""
What a goal needs, and what the store offers for each (P96; docs/2026-10-04-store-design.md §5.3, §6.2, §8 S and M).

A need is a verb and a few words — `{"id": "soil", "does": "sense", "what": "soil-moisture"}` — with a condition only when
it decides a part, and later a mark: have, have-unknown, know or gap. The file is `<project>/.spark/needs.json`. It holds
no part numbers, no owned counts, no places and no reasons: it belongs to a project, which may be public (§5.8). Why a
need is marked as it is, is said to the person, and 1c's history keeps it. Every write sets, never adds.
"""

import collections
import json
import re
from pathlib import Path

import boards
import drawer
import parts
import store

#: How a need stands against the store (§3).
MARKS = ("have", "have-unknown", "know", "gap")
#: What a pick names (§5.3): a part or a board record, or the drawer entry of an owned thing with no record.
PICKS = ("part", "board", "entry")
#: Each field of a need besides its `id` (§5.3): its test, and what is said when a value fails it — read and write alike.
#: A pick is set only by --pick, which reserves what the person owns (§8 C).
CHECKS = {"does": (lambda v: v in parts.VERBS, "`does` is one of %s" % ", ".join(parts.VERBS)),
          "what": (drawer._words, "`what` is a few words: soil-moisture, alarm, microcontroller"),
          "condition": (lambda v: v is None or drawer._words(v), "`condition` is words, or null"),
          "mark": (lambda v: v is None or v in MARKS, "`mark` is one of %s, or null" % ", ".join(MARKS)),
          "pick": (lambda v: v is None or (isinstance(v, list) and all(
              isinstance(p, dict) and len(p) == 1 and next(iter(p)) in PICKS and isinstance(next(iter(p.values())), str)
              and store.PLAIN.fullmatch(next(iter(p.values()))) for p in v)), '`pick` is a list of {"part"|"board"|"entry": id}, set with --pick')}
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
        if "pick" in item:
            problems.append(parts._problem(need_id, "a pick is set with --pick, which reserves what you own"))
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
    store.write_file(path, json.dumps({"schema": 1, "needs": needs}, indent=2, ensure_ascii=False) + "\n")


#: Where a candidate lives, nearest first (§5.5); anything else is one of the person's other projects, after these.
LAYERS = ("drawer", "project", "shelf", "library", "catalog")


def _words(text):
    return {word for word in re.split(r"[^a-z0-9]+", str(text or "").lower()) if word}


def _what_matches(need, functions, names):
    """Every word of the need's `what` in a function with the need's verb, or in the record's name or an alias (§6.2)."""
    wanted = _words(need["what"])
    return bool(wanted) and (any(wanted <= _words(f.get("what")) for f in functions if f.get("does") == need["does"])
                             or wanted <= set().union(*(_words(name) for name in names)))


def _counts(holding, mine=None):
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


def _candidate(need, functions, names, holding, said, mine=None):
    """One candidate (§6.2): `said` names it and where it lives; the rest is what its verb's functions say, and its counts."""
    owned, free, unsure = _counts(holding, mine)
    return dict({"id": None, "kind": None, "entry": None, "owes": [], "broken": False, "proof": []}, **said,
                what=sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                what_matches=_what_matches(need, functions, names), owned=owned, free=free, unsure=unsure)


def candidates(need, known, entries, mine=None):
    """
    The store's candidates for one need (§6.2's code half): every record and every record-less drawer entry whose function
    has the need's verb, owned first, then those whose `what` is the need's, nearest first. Similar enough is the agent's call.
    What `mine`, the asking project, holds is free to it.
    """
    pointing = _pointing(entries)
    found, known_keys = [], set()
    for kind, record_id, where, path in known:
        record = parts._parse(path)
        holding = [entry for _, entry in pointing.get((kind, record_id), [])]
        if not isinstance(record, dict):
            continue
        known_keys.add((kind, record_id))
        functions = parts.function_of(record, board=kind == "board") + [f for e in holding for f in e.get("function") or []]
        if not any(f.get("does") == need["does"] for f in functions):
            continue
        names = [record.get("name")] + parts.aliases(record)
        found.append(_candidate(need, functions, names, holding,
                                {"id": record_id, "kind": kind, "in": where, "label": record.get("name"),
                                 "owes": [] if kind == "board" else parts.owes(record),
                                 "broken": bool(parts._shape_problems(boards.validate, record, path, "board definition")) if kind == "board"
                                 else bool(parts.broken_problems(record, path))}, mine))
    for entry_id, entry in entries.items():
        functions = entry.get("function") or []
        points_at_a_record = isinstance(entry.get("is"), dict) and bool(entry["is"]) and next(iter(entry["is"].items())) in known_keys
        if points_at_a_record or entry.get("skip") or entry.get("count") == 0 or not any(f.get("does") == need["does"] for f in functions):
            continue
        found.append(_candidate(need, functions, [entry.get("label")], [entry],
                                {"entry": entry_id, "in": "drawer", "label": entry.get("label")}, mine))
    return sorted(found, key=lambda c: (c["owned"] == 0, not c["what_matches"],
                                        LAYERS.index(c["in"]) if c["in"] in LAYERS else len(LAYERS), c["id"] or c["entry"]))


def match(project):
    """Each need with its candidates (§6.2), and a problem for each need with no verb — it cannot be matched."""
    known, entries, matched, problems, mine = drawer.linkable(project), drawer.entries(), [], [], store.project_name(project)
    for need in read(project):
        if need.get("does") not in parts.VERBS:
            problems.append(parts._problem(need.get("id"), "a need with no `does` cannot be matched — set it with --needs-set"))
            continue
        if not need.get("what"):
            problems.append(parts._problem(need["id"], "a need with no `what` cannot be matched — set it with --needs-set"))
            continue
        matched.append(dict({key: need.get(key) for key in NEED_FIELDS}, need=need["id"],
                            candidates=candidates(need, known, entries, mine)))
    return matched, problems


def _pointing(entries):
    """{(kind, id): [(entry key, entry)]} for every live drawer entry that says what it is — one said to be dead holds nothing."""
    pointing = {}
    for entry_id, entry in entries.items():
        if not entry.get("skip") and isinstance(entry.get("is"), dict) and entry["is"]:
            pointing.setdefault(next(iter(entry["is"].items())), []).append((entry_id, entry))
    return pointing


def _held(pick, entries, pointing):
    """The live drawer entries that hold one pick (§8 C), as (key, entry): those that say they are its record, or the entry it names."""
    kind, key = next(iter(pick.items()))
    if kind == "entry":
        return [(key, entries[key])] if key in entries and not entries[key].get("skip") else []
    return pointing.get((kind, key), [])


def _resolve(pick_id, known, entries):
    """A pick by its id (§5.3): the record of that id — a part's, then a board's — else the drawer entry of that key, else None."""
    kind = next((kind for kind in ("part", "board") if (kind, pick_id) in known), "entry" if pick_id in entries else None)
    return {kind: pick_id} if kind else None


def plan_pick(project, given, passed_over=()):
    """
    What a `--pick` would do (§8 C): (the needs after, drawer changes, history events, notes, problems). `given` is
    [(need id, id)], and each need it names gets exactly those picks. Then the project's reservations are worked out again
    from every need's picks — one piece per pick — on the entries that hold them, never past what is owned or what another
    project holds (C2; a record and its drawer entry are one stock, however it is picked), so a re-pick frees what it no
    longer picks. A pick no entry holds is to get, not reserved. Nothing is written here.
    """
    name, current, entries = store.add_project(project, dry_run=True), read(project), drawer.entries()
    known, ids, problems, picked = {row[:2] for row in drawer.linkable(project)}, {need["id"] for need in current}, [], {}
    for need_id, pick_id in given:
        pick = _resolve(pick_id, known, entries)
        if need_id not in ids:
            problems.append(parts._problem(need_id, "no need called %s — --needs lists them" % need_id))
        elif pick is None:
            problems.append(parts._problem(need_id, "no record or drawer entry called %s — --match lists the candidates" % pick_id))
        elif not store.PLAIN.fullmatch(pick_id):
            raise store.StoreProblem("%r is not a plain key — lower-case letters, digits and '-' — so a pick cannot name it: "
                                     "rename the drawer entry, or the record's file, then pick it" % pick_id)
        elif pick not in picked.setdefault(need_id, []):
            picked[need_id].append(pick)
    after = [dict(need, pick=picked[need["id"]]) if need["id"] in picked else need for need in current]
    wanted = collections.Counter(next(iter(pick.items())) for need in after for pick in need.get("pick") or [])
    pointing, mine, notes = _pointing(entries), collections.Counter(), []
    # a pick of one drawer entry has nowhere else to go: it takes its piece before a pick of a record, which may take another entry
    for (kind, key), pieces in sorted(wanted.items(), key=lambda asked: (asked[0][0] != "entry", asked[0])):
        held = _held({kind: key}, entries, pointing)
        owned, _, unsure = _counts([entry for _, entry in held], name)
        if owned == 0:
            notes.append("%s: to get — known, not owned" % key)
            continue
        for entry_id, entry in held:
            # what an earlier pick of the same stock — its record, or its drawer entry by key — took is not there to take again
            room = pieces if not isinstance(entry.get("count"), int) else entry["count"] - sum(
                n for who, n in (entry.get("used_in") or {}).items() if who != name) - mine[entry_id]
            taken = max(min(room, pieces), 0)
            mine[entry_id] += taken
            pieces -= taken
        holders = sorted({who for _, entry in held for who in entry.get("used_in") or {} if who != name})
        if pieces:
            problems.append(parts._problem(key, "%s owned%s — %d picked here" % (owned, ", held by " + ", ".join(holders) if holders else "",
                                                                                 pieces + sum(mine[entry_id] for entry_id, _ in held)),
                                           "free it — --drawer-set %s with `used_in` leaving out %s, after a dry run — or pick another"
                                           % (", ".join(entry_id for entry_id, _ in held), ", ".join(holders) or "nobody")))
        notes += ["%s: maybe owned — check the drawer first" % key] if unsure else []
        notes += ["%s: count unknown — check the drawer" % key] if owned == "unknown" else []
    changes = []
    for entry_id, entry in sorted(entries.items()):
        used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}
        used_in.update({name: mine[entry_id]} if mine[entry_id] else {})
        if used_in != (entry.get("used_in") or {}):
            changes.append(drawer.settle(entry_id, entry, {"used_in": used_in}, [])[0])
    events = [dict({"event": "reused", "project": name, "need": need_id}, **pick) for need_id in picked for pick in picked[need_id]]
    for number, item in enumerate(passed_over if isinstance(passed_over, (list, tuple)) else [None], 1):
        pick = _resolve(item.get("id"), known, entries) if isinstance(item, dict) and isinstance(item.get("id"), str) else None
        if not (pick and item.get("need") in ids and drawer._words(item.get("why")) and item.get("by", "person") in ("person", "agent")):
            problems.append(parts._problem("passed over %d" % number, 'a part passed over is {"need", "id", "why", "by": '
                                           '"person" or "agent"}: a need and an id spark has, and the reason in words'))
            continue
        events.append(dict({"event": "passed_over", "project": name, "need": item["need"]}, **pick,
                           why=drawer.clean(item["why"]), by=item.get("by", "person")))
    return after, changes, events, notes, problems


REQUIREMENTS = "requirements.json"

#: What `requirements` works out (§5.3, §8 L): the file as it would be, the records to shelve, the picks with no record to place,
#: the entries already in the file that no pick explains, the board the file named before, and what refuses it.
Requirements = collections.namedtuple("Requirements", "content shelving unplaced kept board_was problems")


def _part_of(entry):
    """The part an entry of a requirements file's `parts` names — a bare id, or {part, name} — or None when it names none."""
    named = entry.get("part") if isinstance(entry, dict) else entry
    return named if isinstance(named, str) else None


def _name_of(entry):
    """The name an entry of `parts` gives its instance, or None."""
    name = entry.get("name") if isinstance(entry, dict) else None
    return name if isinstance(name, str) and name else None


def entry_label(entry):
    """An entry of `parts` in a sentence: tactile-button (BtnOpen), l9110s-module, or an entry that names no part."""
    return "%s%s" % (_part_of(entry) or "an entry that names no part", " (%s)" % _name_of(entry) if _name_of(entry) else "")


def _name_after(need_id):
    """A need's id as the name of its instance: open-lid is OpenLid."""
    return "".join(word.capitalize() for word in need_id.split("-"))


def _called(part_id, name):
    """What the generator calls an instance (`emit_board.component_name`): the name it is given, else its part id in capitals."""
    return name or "".join(word.capitalize() for word in part_id.replace("_", "-").split("-"))


def _serve_picks(existing, picked_by):
    """
    (the entries a pick explains, as indexes into `existing`; the picks no entry serves, as (position, need id, part id)).
    `picked_by` is {part id: [(position, need id)]}. An entry named after a need is that need's; the entries of a part that
    are left pair off with its other picks in order — so what a pick leaves unserved is added, and what no pick serves is
    the entry nobody asked for.
    """
    explained, unserved = set(), []
    for part_id, picks in picked_by.items():
        free, unnamed = [number for number, entry in enumerate(existing) if _part_of(entry) == part_id], []
        for position, need_id in picks:
            own = next((number for number in free if _name_of(existing[number]) == _name_after(need_id)), None)
            if own is None:
                unnamed.append((position, need_id))
            else:
                free.remove(own)
                explained.add(own)
        paired = min(len(unnamed), len(free))
        explained.update(free[:paired])
        unserved += [(position, need_id, part_id) for position, need_id in unnamed[paired:]]
    return explained, unserved


def _merge_parts(existing, wanted):
    """
    (the parts after, the entries no pick explains, problems): the file's `parts` with its picks read into them (the PO,
    2026-10-08). What is there stays, unchanged and in its order — a name, `rails` and any other key are the person's — and an
    entry is added at the end for each pick it lacks. `wanted` is [(need id, part id)], one per pick, in pick order; a part
    picked n times needs n entries (`_serve_picks` says which are there). What no pick explains — added by hand, or left by a
    pick since changed — is kept, and said. An entry added for a part with two or more instances is named after its need, and
    refused by need id when the file already has that name: the build refuses two components of one name.
    """
    picked_by = collections.defaultdict(list)
    for position, (need_id, part_id) in enumerate(wanted):
        picked_by[part_id].append((position, need_id))
    explained, unserved = _serve_picks(existing, picked_by)
    held_by = {}
    for entry in existing:
        if _part_of(entry):
            held_by.setdefault(_called(_part_of(entry), _name_of(entry)), "%s in requirements.json" % entry_label(entry))
    added, problems = [], []
    for _, need_id, part_id in sorted(unserved):
        name = _name_after(need_id) if len(picked_by[part_id]) >= 2 else None
        called = _called(part_id, name)
        if called in held_by:
            problems.append(parts._problem(need_id, 'its %s would be called %s, which %s has too — the build refuses two components '
                                           'of one name; give one of them a name of your own in requirements.json, '
                                           '{"part": "%s", "name": …}, and run this again' % (part_id, called, held_by[called], part_id)))
            continue
        held_by[called] = "need %s's %s" % (need_id, part_id)
        added.append(part_id if name is None else {"part": part_id, "name": name})
    kept = [{"part": _part_of(entry), "name": _name_of(entry)} for number, entry in enumerate(existing) if number not in explained]
    return list(existing) + added, kept, problems


def requirements(project):
    """
    The picks read into the project's requirements file (§5.3, §8 L): a `Requirements` of (the file as it would be, the records
    to shelve, the picks not placed, the entries it keeps that no pick explains, the board it named before, the problems). The
    board pick, and every part pick whose record owes nothing — one in the catalog or in another project goes onto the shelf,
    so the build finds it; a pick with no record is reserved, not placed. The file's own `parts` stay as they are and gain an
    entry for each pick they lack (`_merge_parts`); the keys the person added to the file (signals) stay.
    """
    known = {row[:2]: row for row in drawer.linkable(project)}
    picks = [(need["id"], next(iter(pick.items()))) for need in read(project) for pick in need.get("pick") or []]
    board_picks = sorted({key for _, (kind, key) in picks if kind == "board"})
    problems = [] if len(board_picks) == 1 else [parts._problem("board", "pick one board — %s" % (
        "picked: " + ", ".join(board_picks) if board_picks else "none is picked"))]
    shelve, wanted = [], []
    for need_id, (kind, key) in picks:
        if kind != "part":
            continue
        _, _, where, path = known.get(("part", key), (None, None, None, None))
        record = parts._parse(path) if path else None
        wrong = (["no record called %s any more" % key] if path is None else
                 ["its record at %s does not parse as a JSON object — repair the file by hand" % path] if not isinstance(record, dict) else
                 ["owes %s — fill it in its own home with --fact-set" % ", ".join(parts.owes(record))] if parts.owes(record)
                 else parts.broken_problems(record, path))
        problems += [parts._problem(key, sentence) for sentence in wrong]
        shelve += [(path, None if where == "catalog" else where)] if not wrong and where not in ("project", "shelf", "library") else []
        wanted.append((need_id, key))
    file = Path(project) / REQUIREMENTS
    try:
        held = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {}
    except ValueError as broken:
        raise store.StoreProblem("%s is not JSON (%s) — fix it by hand" % (file, broken))
    held = held if isinstance(held, dict) else {}
    existing = held.get("parts") or []
    if not isinstance(existing, list):
        raise store.StoreProblem("%s: `parts` is not a list — fix it by hand" % file)
    after, kept, naming = _merge_parts(existing, wanted)
    content = dict(held, board=board_picks[0] if board_picks else None, parts=after)
    problems += naming
    problems = [problem for number, problem in enumerate(problems) if problem not in problems[:number]]  # a part picked twice is refused once
    return Requirements(content, list(dict.fromkeys(shelve)), list(dict.fromkeys(key for _, (kind, key) in picks if kind == "entry")),
                        kept, held.get("board"), problems)


def owned(pick, entries):
    """Whether the drawer holds a pick (§6.7's "owned"): a live entry with a count above 0, many, or a count nobody gave."""
    held = _held(pick, entries, _pointing(entries))
    return bool(held) and _counts([entry for _, entry in held])[0] != 0
