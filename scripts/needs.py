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
import design
import drawer
import emit_board
import emit_footprint
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


def entry_keys(listed):
    """The drawer entry keys a needs file names (§5.8, C-17): what a pick of an owned thing with no record writes into the
    project's own file — a key made from the person's label."""
    return {pick["entry"] for need in listed for pick in need.get("pick") or [] if "entry" in pick}


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


def stops_at_footprint(board):
    """Whether a board stops the chain at the footprint stage (C-7, P121): its file has no header geometry to draw the footprint
    from (`emit_footprint.footprint_gaps`) — or it is no board file at all. A board owes nothing; this is what it lacks."""
    return not isinstance(board, dict) or bool(emit_footprint.footprint_gaps(board))


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
        said = {"id": record_id, "kind": kind, "in": where, "label": record.get("name"),
                "owes": [] if kind == "board" else parts.owes(record),
                "broken": bool(parts._shape_problems(boards.validate, record, path, "board definition")) if kind == "board"
                else bool(parts.broken_problems(record, path))}
        if kind == "board":  # C-7: a board owes nothing, and its file may still stop the chain at the footprint stage (P121)
            said["stops_at"] = "footprint" if stops_at_footprint(record) else None
        found.append(_candidate(need, functions, names, holding, said, mine))
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


def _as_record(pick, known, entries):
    """
    A pick as what it is (§5.3): the drawer entry of a record spark knows is a pick of that record — one stock, however it is
    named — so the building list places the record and checks what it owes. Any other pick stays as it is.
    """
    kind, key = next(iter(pick.items()))
    said = (entries.get(key) or {}).get("is") if kind == "entry" else None
    return dict(said) if said and next(iter(said.items())) in known else pick


def _resolve(pick_id, known, entries):
    """
    A pick by its id (§5.3): the record of that id — a part's, then a board's — else the drawer entry of that key, as the
    record it says it is when spark knows that record (`_as_record`); None when nothing has that id.
    """
    kind = next((kind for kind in ("part", "board") if (kind, pick_id) in known), "entry" if pick_id in entries else None)
    return _as_record({kind: pick_id}, known, entries) if kind else None


def _how_to_free(entry_keys, holders):
    """The fix for a reservation past what is free (§8 C): what other projects hold is freed — and when none holds any, the
    shortage is the person's own count: fewer are picked, or a count that was low is set. `--drawer-set` takes a file."""
    if holders:
        return ("free it — a file holding [%s] without %s, given to --drawer-set <file> after a dry run — or pick another"
                % (", ".join('{"entry": "%s", "used_in": …}' % key for key in entry_keys), ", ".join(holders)))
    return ("pick fewer, or another — or, if you own more, a file holding [%s], given to --drawer-set <file> after a dry run"
            % ", ".join('{"entry": "%s", "count": …}' % key for key in entry_keys))


def _unfiled_boards(needs, known, entries):
    """The drawer entries picked for a need that computes — the board (`/spark:idea`, S) — that are no board spark has a file
    for: the person owns it, and spark cannot build with it until a board file says its pins (§5.3)."""
    return sorted({key for need in needs if need.get("does") == "compute" for pick in need.get("pick") or []
                   for kind, key in [next(iter(_as_record(pick, known, entries).items()))] if kind == "entry"})


def plan_pick(project, given, passed_over=()):
    """
    What a `--pick` would do (§8 C): (the needs after, drawer changes, history events, notes, problems). `given` is
    [(need id, id)], and each need it names gets exactly those picks. Then the project's reservations are worked out again
    from every need's picks — one piece per pick — on the entries that hold them, never past what is owned or what another
    project holds (C2; a record and its drawer entry are one stock, however it is picked), so a re-pick frees what it no
    longer picks. A pick no entry holds is to get, not reserved. A drawer entry of a record spark knows, picked by its key, is
    a pick of that record, and says so. A `reused` event is written for each pick except a record the project keeps in its
    own parts/ or boards/: that was not there before the project. A reason a part was passed over is kept in the person's
    words, without any URL or price in them (`kept_reason`), and said when one was taken out. Nothing is written here.
    """
    name, current, entries = store.add_project(project, dry_run=True), read(project), drawer.entries()
    known, ids, problems, picked = {row[:2]: row[2] for row in drawer.linkable(project)}, {need["id"] for need in current}, [], {}
    notes = []
    for need_id, pick_id in given:
        pick = _resolve(pick_id, known, entries)
        named = next(iter(pick.values())) if pick else None
        if need_id not in ids:
            problems.append(parts._problem(need_id, "no need called %s — --needs lists them" % need_id))
        elif pick is None:
            problems.append(parts._problem(need_id, "no record or drawer entry called %s — --match lists the candidates" % pick_id))
        elif not (store.PLAIN.fullmatch(pick_id) and store.PLAIN.fullmatch(named)):  # the key given, and the id written
            raise store.StoreProblem("%r is not a plain key — lower-case letters, digits and '-' — so a pick cannot name it: "
                                     "rename the drawer entry, or the record's file, then pick it"
                                     % (named if store.PLAIN.fullmatch(pick_id) else pick_id))
        elif pick not in picked.setdefault(need_id, []):
            picked[need_id].append(pick)
            renamed = "%s: the drawer entry of %s — picked as that record" % (pick_id, named)
            notes += [renamed] if named != pick_id and renamed not in notes else []
    after = [dict(need, pick=picked[need["id"]]) if need["id"] in picked else need for need in current]
    wanted = collections.Counter(next(iter(pick.items())) for need in after for pick in need.get("pick") or [])
    pointing, mine = _pointing(entries), collections.Counter()
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
                                           _how_to_free([entry_id for entry_id, _ in held], holders)))
        notes += ["%s: maybe owned — check the drawer first" % key] if unsure else []
        notes += ["%s: count unknown — check the drawer" % key] if owned == "unknown" else []
    notes += ["%s: a board needs a board file — a record in boards/ — before spark can build with it" % key
              for key in _unfiled_boards(after, known, entries)]
    # F12 (C-7): a board this pick picks that stops the chain at the footprint stage is said, never refused
    for key in sorted({key for need_id in picked for pick in picked[need_id] for kind, key in pick.items() if kind == "board"}):
        stop = boards.footprint_stop(key, project)
        notes += ["board %s %s" % (key, stop)] if stop else []
    changes = []
    for entry_id, entry in sorted(entries.items()):
        used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}
        used_in.update({name: mine[entry_id]} if mine[entry_id] else {})
        if used_in != (entry.get("used_in") or {}):
            changes.append(drawer.settle(entry_id, entry, {"used_in": used_in}, [])[0])
    events = [dict({"event": "reused", "project": name, "need": need_id}, **pick) for need_id in picked for pick in picked[need_id]]
    # a record the project keeps in its own parts/ or boards/ was not there before the project: it is no reuse of the store (§6.7)
    events = [event for event in events if not any(known.get((kind, event.get(kind))) == "project" for kind in ("part", "board"))]
    for number, item in enumerate(passed_over if isinstance(passed_over, (list, tuple)) else [None], 1):
        pick = _resolve(item.get("id"), known, entries) if isinstance(item, dict) and isinstance(item.get("id"), str) else None
        why, cut = kept_reason(item["why"]) if pick and isinstance(item.get("why"), str) else ("", False)
        why = why if re.search(r"[^\W\d_]", why) else ""  # F14: what is left with no letter in it is no reason either
        if not (pick and item.get("need") in ids and drawer._words(why) and item.get("by", "person") in ("person", "agent")):
            problems.append(parts._problem("passed over %d" % number, 'a part passed over is {"need", "id", "why", "by": '
                                           '"person" or "agent"}: a need and an id spark has, and the reason in words — a URL or '
                                           'a price is not kept, so a reason that is only those is none'))
            continue
        events.append(dict({"event": "passed_over", "project": name, "need": item["need"]}, **pick, why=why, by=item.get("by", "person")))
        notes += ["%s: the reason is kept without the URL or price in it — your history keeps words, never a URL or a price"
                  % item["id"]] if cut else []
    return after, changes, events, notes, problems


#: What a passed-over reason never keeps (§5.7, W21: "never a URL … a price"): a web address — any scheme, `www.`, or a bare
#: host with a path whose last label is a common top-level domain (TLDS), so `3.3/5V`, `v1.1/v1.2` and `pinout.png/page 2`
#: stay — with a bracket around it; and an amount of money — a currency symbol before a number, glued or spaced, a code
#: before it only spaced (`EUR 12`; `EUR12` and `KC868` are part numbers), a symbol or a code after it, glued or spaced,
#: thousands spaced with a space or a no-break space, a Czech `,-` with or without its crowns (F14).
TLDS = "com|org|net|io|cz|sk|de|eu|co|uk|pl|at|ch|fr|it|es|nl|info|shop|dev|app"
#: A URL's own characters: none a space or a bracket, but a bracketed run inside it (`…/wiki/Foo_(bar)`) is its own too.
URL_CHAR = r"(?:[^\s<>()\[\]]|\([^\s<>()\[\]]*\))"
#: A bracket around a URL goes with it only when the URL is opened by it (the re-check: `(see aliexpress.com/x)` lost its
#: `)` to the URL and kept its `(`), so the text's own brackets stay as balanced as they were.
URL_IN_WORDS = re.compile(r"(?:(<)|(\()|(\[))?"
                          r"(?:(?:[a-z][a-z0-9+.-]*://|www\.)%s+|\b[\w-]+(?:\.[\w-]+)*\.(?:%s)(?::\d+)?/%s*)"
                          r"(?(1)>?)(?(2)\)?)(?(3)\]?)" % (URL_CHAR, TLDS, URL_CHAR), re.IGNORECASE)
CODES = r"(?:eur|euros?|usd|dollars?|czk|kč|kc|gbp|chf|pln|zł|cny|rmb|yuan|jpy|yen)"
AMOUNT = r"\d{1,3}(?:[ \u00a0]\d{3})+(?:[.,]\d+)?|\d[\d.,]*"
PRICE_IN_WORDS = re.compile(r"(?:[$€£¥]\s?|\b%s\s)(?:%s)|(?:%s)(?:,-)?\s?(?:[$€£¥]|%s\b)|\b\d[\d. ]*,-(?!\w)" % (CODES, AMOUNT, AMOUNT, CODES),
                            re.IGNORECASE)


def kept_reason(text):
    """
    A passed-over reason as the history keeps it (§5.7, W21; C-17): cleaned as a label is, and with every URL and every price
    taken out — (the reason, whether anything was taken out). The person's words stay; what the history never keeps does not.
    """
    said = drawer.clean(text)
    kept = PRICE_IN_WORDS.sub("", URL_IN_WORDS.sub("", said))
    if kept == said:
        return said, False
    return re.sub(r"\s+([,;:.)\]>])", r"\1", re.sub(r"\s{2,}", " ", kept)).strip(" ,;:.-—"), True


REQUIREMENTS = "requirements.json"

#: What `requirements` works out (§5.3, §8 L): the file as it would be, the records to shelve, the picks with no record to place,
#: the entries already in the file that no pick explains, the board the file named before, what refuses it, the picks laid out
#: at a placeholder outline, the needs nothing on the board serves, and what the board's power would lack (`_power_gaps`).
Requirements = collections.namedtuple("Requirements", "content shelving unplaced kept board_was problems placeholder unserved "
                                                      "no_supply no_receiver no_driver")

#: The note a requirements file keeps of the needs it leaves off the board (C-2): `check_spine` reads it into its verdict.
UNSERVED = "unserved"


def unserved_keys(content):
    """
    The drawer entry keys a requirements file names (F16): the picks of each `unserved` note "no record" — keys made from the
    person's labels, which `--requirements` says once, as `--pick` does of needs.json's. A note that is no such note names none.
    """
    notes = content.get(UNSERVED) if isinstance(content, dict) else None
    return {key for note in (notes if isinstance(notes, list) else []) if isinstance(note, dict) and note.get("why") == "no record"
            for key in (note.get("picks") if isinstance(note.get("picks"), list) else []) if isinstance(key, str)}

#: The facts that place a part, not wire it (the PO, 2026-10-08; P165): a pick that owes only these is written, and the PCB step
#: lays it out at a placeholder size, said; one that owes a fact the circuit needs — a footprint, a pin order and its proof, a
#: simulation stance — is refused, as before.
LAYOUT_FACTS = ("body_mm",)


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


#: A name as the build tells names apart — `design.one_name`, the one definition (P163, W16); this was a second copy of it.
_one_name = design.one_name


def _serve_picks(existing, picked_by):
    """
    (the entries a pick explains, as indexes into `existing`; the picks no entry serves, as (position, need id, part id)).
    `picked_by` is {part id: [(position, need id)]}. An entry named after a need — whatever its capitals — is that need's; the
    entries of a part that are left pair off with its other picks in order — so what a pick leaves unserved is added, and
    what no pick serves is the entry nobody asked for.
    """
    explained, unserved = set(), []
    for part_id, picks in picked_by.items():
        free, unnamed = [number for number, entry in enumerate(existing) if _part_of(entry) == part_id], []
        for position, need_id in picks:
            its_own = _one_name(_name_after(need_id))
            own = next((number for number in free if _one_name(_name_of(existing[number]) or "") == its_own), None)
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
    refused by need id when the file already has that name, in any capitals (`_one_name`): the build refuses two components
    of one name.
    """
    picked_by = collections.defaultdict(list)
    for position, (need_id, part_id) in enumerate(wanted):
        picked_by[part_id].append((position, need_id))
    explained, unserved = _serve_picks(existing, picked_by)
    held_by = {}  # {one name: (who has it, what it is called there)}
    for entry in existing:
        if _part_of(entry):
            called = _called(_part_of(entry), _name_of(entry))
            held_by.setdefault(_one_name(called), ("%s in requirements.json" % _part_of(entry), called))
    added, problems = [], []
    for _, need_id, part_id in sorted(unserved):
        name = _name_after(need_id) if len(picked_by[part_id]) >= 2 else None
        called = _called(part_id, name)
        if _one_name(called) in held_by:
            holder, its_name = held_by[_one_name(called)]
            problems.append(parts._problem(need_id, 'its %s would be called %s, and %s is called %s — %s; give one of them a name of '
                                           'your own in requirements.json, {"part": "%s", "name": …}, and run this again'
                                           % (part_id, called, holder, its_name, design.ONE_NAME_RULE, part_id)))
            continue
        held_by[_one_name(called)] = ("need %s's %s" % (need_id, part_id), called)
        added.append(part_id if name is None else {"part": part_id, "name": name})
    kept = [{"part": _part_of(entry), "name": _name_of(entry)} for number, entry in enumerate(existing) if number not in explained]
    return list(existing) + added, kept, problems


def _board_problems(board_picks, unfiled, project):
    """
    What refuses the board (§8 L): it is one, picked as its record. A board picked from the drawer that spark has no board
    file for is named, with the boards spark has a file for — the library's and the project's — that build, and those that stop
    at the footprint stage, which are never suggested (C-7); no board, or two, is said so.
    """
    if len(board_picks) == 1:
        return []
    if unfiled and not board_picks:
        filed = boards.records(project)
        stopping = [board_id for board_id, (_, path) in filed.items() if stops_at_footprint(parts._parse(path))]
        builds = [board_id for board_id in filed if board_id not in stopping]  # C-7: a board that stops is never suggested
        said = ("spark has one that builds for %s" % ", ".join(builds) if builds else "spark has no board file that builds") + (
            "; %s stop%s at the footprint stage (P121) — no header geometry in %s board file" % (
                ", ".join(stopping), "s" if len(stopping) == 1 else "", "its" if len(stopping) == 1 else "their") if stopping else "")
        return [parts._problem(key, "picked as the board, but a board needs a board file — a record in boards/ — before spark can "
                                    "build with it, and it has none; %s" % said,
                               '%swrite a board file for %s first (docs/guide/how-it-works.md, "Your own dev board")'
                               % ("pick %s, or " % " or ".join(builds) if builds else "", key)) for key in unfiled]
    return [parts._problem("board", "pick one board — %s" % (
        "picked: " + ", ".join(board_picks) if board_picks else "none is picked"))]


def _unserved(needs, known, entries):
    """
    The needs nothing on the board serves (the PO, 2026-10-08; C-2), as {"need", "why", "picks"}: one with no pick — "no pick",
    or "a gap" when it is marked one — and one whose every pick is a drawer entry with no record ("no record"), which the
    building list reserves and does not place. A record-less pick beside a placed one (the speaker beside its amplifier) leaves
    its need served. Said, never refused: whether a thing belongs on the board is the person's to say.
    """
    said = []
    for need in needs:
        picks = [_as_record(pick, known, entries) for pick in need.get("pick") or []]
        if not picks:
            said.append({"need": need["id"], "why": "a gap" if need.get("mark") == "gap" else "no pick", "picks": []})
        elif all("entry" in pick for pick in picks):
            said.append({"need": need["id"], "why": "no record", "picks": [pick["entry"] for pick in picks]})
    return said


def _power_gaps(listed, known):
    """
    What the board's power would lack (C-3; the PO, 2026-10-08), from the records of every part the file lists, on the rails the
    file gives them: each rail a part draws from and nothing listed supplies — `emit_board.rails_without_a_source`, the rule the
    schematic stage stops on — as {"rail", "drawn_by"}; each net a part drives that nothing listed receives
    (`emit_board.outputs_with_nothing_on_them`) as {"net", "driven_by"}; and, split out of the first, each side of a driven pair
    nothing listed drives (`emit_board.pair_sides_without_a_driver`: an amplifier's, never a supply's; F15) as {"net",
    "received_by"}. A part whose record is not found or is broken is left to the build to name. Said before the build, never
    refused: the inlet, the supply, the amplifier or the terminal is the person's pick.
    """
    part_list = []
    for entry in listed:
        part_id = _part_of(entry)
        path = known.get(("part", part_id), (None,) * 4)[3] if part_id else None
        record = parts._parse(path) if path else None
        if not isinstance(record, dict) or parts.broken_problems(record, path):
            continue
        rails = entry.get("rails") if isinstance(entry, dict) and isinstance(entry.get("rails"), dict) else None
        try:
            # named by its id here, so what is said names what was picked rather than the record's long name
            part_list.append(dict(design.on_rails(record, rails) if rails else record, name=part_id))
        except (design.DesignError, TypeError, AttributeError):
            continue  # a rail given to a pin the part does not have: the build names it
    no_supply = [{"rail": net, "drawn_by": sorted({"%s.%s" % (part["name"], supply["pin"])
                                                   for part, supply, on in emit_board.power_connections(part_list)
                                                   if on == net and supply.get("direction") != "out"})}
                 for net in emit_board.rails_without_a_source(part_list)]
    no_receiver = [{"net": net, "driven_by": "%s.%s" % (name, pin)} for net, name, pin in emit_board.outputs_with_nothing_on_them(part_list)]
    pair_sides = set(emit_board.pair_sides_without_a_driver(part_list))
    no_driver = [{"net": gap["rail"], "received_by": gap["drawn_by"]} for gap in no_supply if gap["rail"] in pair_sides]
    return [gap for gap in no_supply if gap["rail"] not in pair_sides], no_receiver, no_driver


def _how_to_fill(path):
    """Where what a record owes is filled (§5.4): a record in spark's own library in spark's repository; any other with --fact-set."""
    if Path(path).parent.resolve() == parts.LIBRARY.resolve():
        return "it is in spark's own library, so it is filled in spark's repository, by a commit — --fact-set does not change the library"
    return "fill it in its own home with --fact-set"


def requirements(project):
    """
    The picks read into the project's requirements file (§5.3, §8 L): a `Requirements` of (the file as it would be, the records
    to shelve, the picks not placed, the entries it keeps that no pick explains, the board it named before, the problems, the
    picks laid out at a placeholder outline with where theirs is filled). The board pick, and every part pick whose record owes
    nothing the circuit needs — one owing only its outline (`LAYOUT_FACTS`) is placed and said — and one in the catalog or in
    another project goes onto the shelf, so the build finds it; a pick with no record is reserved, not placed. A pick of a drawer
    entry is read as the record that entry is, when spark knows it (`_as_record`). The file's own `parts` stay as they are and
    gain an entry for each pick they lack (`_merge_parts`); the keys the person added to the file (signals) stay.
    """
    known, entries, needs = {row[:2]: row for row in drawer.linkable(project)}, drawer.entries(), read(project)
    picks = [(need["id"], next(iter(_as_record(pick, known, entries).items()))) for need in needs for pick in need.get("pick") or []]
    board_picks = sorted({key for _, (kind, key) in picks if kind == "board"})
    problems = _board_problems(board_picks, _unfiled_boards(needs, known, entries), project)
    shelve, wanted, placeholder = [], [], []
    for need_id, (kind, key) in picks:
        if kind != "part":
            continue
        _, _, where, path = known.get(("part", key), (None, None, None, None))
        record = parts._parse(path) if path else None
        owed = parts.owes(record) if isinstance(record, dict) else []
        wrong = (["no record called %s any more" % key] if path is None else
                 ["its record at %s does not parse as a JSON object — repair the file by hand" % path] if not isinstance(record, dict) else
                 ["owes %s — %s" % (", ".join(owed), _how_to_fill(path))] if set(owed) - set(LAYOUT_FACTS)
                 else parts.broken_problems(record, path))
        problems += [parts._problem(key, sentence) for sentence in wrong]
        shelve += [(path, None if where == "catalog" else where)] if not wrong and where not in ("project", "shelf", "library") else []
        placeholder += [(key, _how_to_fill(path))] if owed and not wrong else []
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
    unserved = _unserved(needs, known, entries)
    if unserved:
        content[UNSERVED] = unserved
    else:
        content.pop(UNSERVED, None)  # an old note goes once every need is on the board
    problems += naming
    problems = [problem for number, problem in enumerate(problems) if problem not in problems[:number]]  # a part picked twice is refused once
    return Requirements(content, list(dict.fromkeys(shelve)), list(dict.fromkeys(key for _, (kind, key) in picks if kind == "entry")),
                        kept, held.get("board"), problems, list(dict.fromkeys(placeholder)), unserved, *_power_gaps(after, known))


def owned(pick, entries):
    """Whether the drawer holds a pick (§6.7's "owned"): a live entry with a count above 0, many, or a count nobody gave."""
    held = _held(pick, entries, _pointing(entries))
    return bool(held) and _counts([entry for _, entry in held])[0] != 0
