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

from spark.design import footprint_emitter
from spark.sourcing import drawer, matching, offers
from spark.sourcing.part_records import broken_problems, limits_of_part
from spark.records import board_records, onboard_parts, records_codes, store
from spark.records.record_kind import _problem, _shape_problems, owes, VERBS
from spark.core.text_guards import clean, kept_reason, printable

#: How a need stands against the store (§3).
MARKS = ("have", "have-unknown", "know", "gap")
#: What a pick names (§5.3): a part or a board record, or the drawer entry of an owned thing with no record.
PICKS = ("part", "board", "entry")
#: Each field of a need besides its `id` (§5.3): its test, and what is said when a value fails it — read and write alike.
#: A pick is set only by --pick, which reserves what the person owns (§8 C).
CHECKS = {"does": (lambda v: v in VERBS, "`does` is one of %s" % ", ".join(VERBS)),
          "what": (drawer._words, "`what` is a few words: soil-moisture, alarm, microcontroller"),
          "condition": (lambda v: v is None or drawer._words(v), "`condition` is words, or null"),
          "mark": (lambda v: v is None or v in MARKS, "`mark` is one of %s, or null" % ", ".join(MARKS)),
          "pick": (lambda v: v is None or (isinstance(v, list) and all(
              isinstance(p, dict) and len(p) == 1 and next(iter(p)) in PICKS and isinstance(next(iter(p.values())), str)
              and store.PLAIN.fullmatch(next(iter(p.values()))) for p in v)), '`pick` is a list of {"part"|"board"|"entry": id}, set with --pick')}
NEED_FIELDS = tuple(CHECKS)
FILE = Path(".spark") / "needs.json"


def read(project):
    """The project's needs, in order — [] when it has none yet; a file not in the needs shape is a StoreError."""
    path = Path(project) / FILE
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as broken:
        raise store.StoreError("%s is not JSON (%s)", path, broken, code=records_codes.RECORD_FILE_BROKEN)
    if not (isinstance(data, dict) and isinstance(data.get("needs"), list)
            and all(isinstance(need, dict) and isinstance(need.get("id"), str) for need in data["needs"])):
        raise store.StoreError('%s is not {"schema": 1, "needs": [{"id", "does", "what", …}]} — fix it by hand', path, code=records_codes.RECORD_FILE_BROKEN)
    stray = sorted(set(data) - {"schema", "needs"})
    if stray:
        raise store.StoreError("%s holds %s, which a needs file does not — fix it by hand", path, ", ".join(stray), code=records_codes.RECORD_FILE_BROKEN)
    if data.get("schema", 1) != 1:
        raise store.StoreError("%s is schema %r — this spark reads schema 1", path, data["schema"], code=records_codes.RECORD_FILE_BROKEN)
    ids = [need["id"] for need in data["needs"]]
    for need in data["needs"]:
        said = ((["`id` is not lower-case letters, digits and '-'"] if not store.PLAIN.fullmatch(need["id"]) else [])
                + (["is there more than once"] if ids.count(need["id"]) > 1 else []) + faults(need, held_only=True))
        if said:
            raise store.StoreError("%s: need %r: %s — fix it by hand", path, need["id"], said[0], code=records_codes.RECORD_FILE_BROKEN)
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
        return None, [], [_problem("the file", "a needs write is a JSON list of needs, each an object with an `id`")]
    current = {need["id"]: dict(need) for need in read(project)}
    order, changes, problems = list(current), [], []
    for number, item in enumerate(items, 1):
        need_id = item.get("id")
        if not (isinstance(need_id, str) and store.PLAIN.fullmatch(need_id)):
            problems.append(_problem("item %d" % number, "a need's `id` is lower-case letters, digits and '-', not %s"
                                     % json.dumps(need_id, ensure_ascii=False)))
            continue
        if "pick" in item:
            problems.append(_problem(need_id, "a pick is set with --pick, which reserves what you own"))
            continue
        before = current.get(need_id)
        after = dict(before or {}, **{key: (clean(value) if isinstance(value, str) else value) for key, value in item.items()})
        problems += [_problem(need_id, sentence) for sentence in faults(after)]
        changed = [key for key in NEED_FIELDS if after.get(key) != (before or {}).get(key)]
        if changed:
            changes.append({"need": need_id, "new": before is None, "was": {key: before.get(key) for key in changed}
                            if before else {}, "now": {key: after.get(key) for key in changed}})
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
LAYERS = (offers.DRAWER, "project", "shelf", "library", "catalog")

#: `--match`'s matcher (P211). A default changes only with the PO's yes, after he reads the matchers' numbers on his needs.
MATCHER = "same-words"


def offer(key, project=None):
    """The offer called `key` (P211): a record's id, a part's before a board's, or a drawer entry's key — the record it
    says it is, when spark knows that record. None when nothing live has that key."""
    rows, entries = drawer.linkable(project), drawer.entries()
    pick = _resolve(key, {row[:2]: row[2] for row in rows}, entries)  # _resolve takes {(kind, id): where}, as plan_pick builds it
    if pick is None:
        return None
    wanted = next(iter(pick.items()))
    return next((found for found, _ in offers.build(rows, entries) if (found.kind, found.key) == wanted), None)


# --- MVP ---
#: What the pick's note says after the limits of a board (P397): the part to wire to a header pad, or why none is named.
OTHER_CHOICE = "The other choice: %s on a header pad, which has a Wokwi model."
ALL_HELD = "Every other part with a Wokwi model for %s is held by another project."

Limits = collections.namedtuple("Limits", "sentences no_pin")
Limits.__doc__ = "What a passed run does not test of a board's parts that serve one need: plain sentences, and whether one says a pin is missing."


def serving_roles(need, functions):
    """
    The `role` of each of a board's `functions` (`onboard_functions`) that serves the need, as WordOverlap admits a
    board: the need's verb and any word of `matching.need_words` that the function's `what` shares, so `press button`,
    `input button`, `boot button` and `status led` meet the board's own button and LED. A function with no role is a
    power fact, which no limit is about.
    """
    wanted = set(matching.need_words(need.get("what")))
    return [function["role"] for function in functions if function.get("role") and function.get("does") == need.get("does")
            and wanted & set(matching.need_words(function.get("what")))]


def board_limits(need, record, functions, definitions=None, key=None):
    """
    The Limits of the board `record` for the need (P397): the sentences of `role_limits` for the roles that serve it
    (`onboard_limits` returns (component, sentence) pairs; the `limits` key and this keep the sentences). A sentence about a definition spark did not
    compare says "not checked" and then the bench, which the build's own text leaves to the reader. `no_pin` is true when a
    part a scenario could reach has no pin in the definition, or only a stand-in's bare header pin: the only limit that a part on a header pad would lift.
    `definitions` and `key` are `role_limits`'s: the caller's memo, and the offer's key that names the board in it. A stand-in
    board's wired sentence is the board-only build's truth; the full build wires nothing until P792 #1100 (P778).
    """
    said = onboard_parts.limits_of_board(record, serving_roles(need, functions), None, definitions, key)
    pairs = [pair for each in said.values() for pair in each]
    sentences = [("%s. %s" % (sentence, board_records.BENCH)) if component == board_records.ONBOARD_GPIOS else sentence
                 for component, sentence in pairs]
    no_pin = any(board_records.ONBOARD_ROLES[role].scenario_verb and each and each[0][0] != board_records.ONBOARD_GPIOS
                 for role, each in said.items())
    return Limits(list(dict.fromkeys(sentences)), no_pin)


# --- end MVP ---


def _candidate(need, fit, context, mine=None):
    """One candidate (§6.2): where it lives and what it owes, what its verb's functions say, its counts and its fit. The
    keys `--need` says too (`id` or `entry`, `in`, `owned`, `score`, `why`) are `offers.row`'s."""
    offer, record = fit.offer, context["record"]
    _, free, unsure = offers.counts(context["holding"], mine)
    if record is None:
        said = {"label": context["holding"][0].get("label")}
    else:
        said = {"kind": offer.kind, "label": record.get("name"),
                "owes": [] if offer.kind == "board" else owes(record),
                "broken": bool(_shape_problems(board_records.validate, record, context["path"],
                "board definition")) if offer.kind == "board" else bool(broken_problems(record, context["path"]))}
        if offer.kind == "board":  # C-7: a board owes nothing, and its file may still stop the chain at the footprint stage (P121)
            said["stops_at"] = "footprint" if footprint_emitter.footprint_gaps(record) else None
            if said["stops_at"]:  # P411: a board that builds gains no key
                said["stops_why"] = footprint_emitter.why_no_footprint(record)  # the list, for Claude
                said["stop_line"] = footprint_emitter.footprint_stop_line(record)  # the text shows it; `--match` drops it from the JSON
    said = dict({"kind": None, "owes": [], "broken": False, "proof": [], "limits": []}, **said,
                what=sorted({f["what"] for f in offer.functions if f.get("does") == need["does"]}),
                what_matches=fit.exact, about=offer.about, held_by=drawer.holders_of(context["holding"], mine))
    return dict(offers.row(fit, context, said, mine), free=free, unsure=unsure)


def _rank(need, built, mine=None, matcher=None):
    """The candidates for one need from the offers `built`, ranked: owned first, then the best score, then nearest. No limits yet."""
    context = {(offer.kind, offer.key): said for offer, said in built}
    ranked = (matcher or matching.matcher(MATCHER, "match")).rank(need, [offer for offer, _ in built])
    found = [_candidate(need, fit, context[(fit.offer.kind, fit.offer.key)], mine) for fit in ranked]
    return sorted(found, key=lambda c: offers.rank_key(c) + (LAYERS.index(c["in"]) if c["in"] in LAYERS else len(LAYERS),
                                                             c["id"] or c["entry"]))


def candidates(need, known, entries, mine=None, matcher=None, definitions=None):
    """
    The store's candidates for one need (§6.2's code half): every offer the matcher admits, owned first, then the best
    score, then nearest. The matcher is MATCHER's unless one is given (P211). Similar enough is the chooser's call. What
    `mine`, the asking project, holds is free to it. A board candidate gets its `limits` (P397), and a part candidate those of its
    record (`limits_of_part`: a stand-in, a chip's note, a skip; P778); `definitions` is the dict that
    `role_limits` fills, so a caller that matches several needs reads each board's Wokwi definition once.
    """
    built = offers.build(known, entries)
    found = _rank(need, built, mine, matcher)
    seen = {(offer.kind, offer.key): (offer, said["record"]) for offer, said in built}
    for one in found:
        if one["kind"] == "board":
            offer, record = seen[("board", one["id"])]
            one["limits"] = board_limits(need, record, offer.functions, definitions, offer.key).sentences
        elif one["kind"] == "part":
            one["limits"] = [sentence for _, sentence in limits_of_part(seen[("part", one["id"])][1], one["id"])]
    return found


def match(project, matcher=None):
    """Each need with its candidates (§6.2), and a problem for each need with no verb — it cannot be matched. `matcher` is
    MATCHER's unless one is given (P211)."""
    # the name a pick holds under, as plan_pick takes it: an unlisted project still holds as its folder (P403 refuter)
    known, entries, matched, problems, mine = (drawer.linkable(project), drawer.entries(), [], [], store.plan_listed_name(project))
    definitions = {}  # P397: each board's Wokwi definition, read once for every need
    for need in read(project):
        if need.get("does") not in VERBS:
            problems.append(_problem(need.get("id"), "a need with no `does` cannot be matched — set it with --needs-set"))
            continue
        if not need.get("what"):
            problems.append(_problem(need["id"], "a need with no `what` cannot be matched — set it with --needs-set"))
            continue
        matched.append(dict({key: need.get(key) for key in NEED_FIELDS}, need=need["id"],
                            candidates=candidates(need, known, entries, mine, matcher, definitions)))
    return matched, problems


def _held(pick, entries, pointing):
    """The live drawer entries that hold one pick (§8 C), as (key, entry): those that say they are its record, or the entry it names."""
    kind, key = next(iter(pick.items()))
    if kind == "entry":
        return [(key, entries[key])] if key in entries and not entries[key].get("skip") else []
    return pointing.get((kind, key), [])


def as_record(pick, known, entries):
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
    record it says it is when spark knows that record (`as_record`); None when nothing has that id.
    """
    kind = next((kind for kind in ("part", "board") if (kind, pick_id) in known), "entry" if pick_id in entries else None)
    return as_record({kind: pick_id}, known, entries) if kind else None


def _how_to_free(entry_keys, holders):
    """The fix for a reservation past what is free (§8 C): what other projects hold is freed — and when none holds any, the
    shortage is the person's own count: fewer are picked, or a count that was low is set. `--drawer-set` takes a file."""
    if holders:
        return ("free it — a file holding [%s] without %s, given to --drawer-set <file> after a dry run — or pick another"
                % (", ".join('{"entry": "%s", "used_in": …}' % key for key in entry_keys), ", ".join(printable(who) for who in holders)))
    return ("pick fewer, or another — or, if you own more, a file holding [%s], given to --drawer-set <file> after a dry run"
            % ", ".join('{"entry": "%s", "count": …}' % key for key in entry_keys))


def unfiled_boards(needs, known, entries):
    """The drawer entries picked for a need that computes — the board (`/spark:idea`, S) — that are no board spark has a file
    for: the person owns it, and spark cannot build with it until a board file says its pins (§5.3)."""
    return sorted({key for need in needs if need.get("does") == "compute" for pick in need.get("pick") or []
                   for kind, key in [next(iter(as_record(pick, known, entries).items()))] if kind == "entry"})


# --- MVP ---
def _holds_wokwi(record):
    """Whether a record has a Wokwi model for the part (`simulation.wokwi`, a table): all spark checks, not that a scenario can drive it."""
    return isinstance(record, dict) and isinstance(record.get("simulation"), dict) and isinstance(record["simulation"].get("wokwi"), dict)


def _other_choice(need, built, mine):
    """
    The sentence that closes a board's limits when a part on a header pad would lift them (P397). It looks only at the
    parts the person owns whose words match the need (score from `matching.MIN_SHOWN`) and whose record has a Wokwi model:
    spark looks in what the person owns first, so a part to get is never named, and a part that matches no word is never
    named. It names the first with free stock. When each of them is held by another project, it says so. With none, it says
    nothing of a choice.
    """
    records = {(offer.kind, offer.key): said["record"] for offer, said in built}
    nameable = [c for c in _rank(need, built, mine) if c["kind"] == "part" and c["score"] >= matching.MIN_SHOWN
                and c["owned"] != 0 and _holds_wokwi(records[("part", c["id"])])]
    free = next((c for c in nameable if c["free"] != 0), None)
    if free:
        return OTHER_CHOICE % free["id"]
    return ALL_HELD % need["id"] if nameable else ""


def _limits_notes(after, picked, rows, entries, mine):
    """
    One note for each board this pick gives to a need that the board's own parts serve, when the board has limits (P397):
    `board <key> for <need>: <the limits>`, the sentences of the build's own text, then the other choice when a missing pin
    is the limit; and one for each part picked whose record has limits (`limits_of_part`, P778): `part <key> for <need>: <the
    limits>`. They sit after the F12 note. The Wokwi definition is read once per board.
    """
    asked = sorted(((kind, key, need) for need in after if need["id"] in picked for pick in picked[need["id"]]
                    for kind, key in pick.items() if kind in ("board", "part")), key=lambda asked: (asked[0], asked[1], asked[2]["id"]))
    if not asked:
        return []
    built, definitions, notes = offers.build(rows, entries), {}, []
    records = {(offer.kind, offer.key): (offer, said["record"]) for offer, said in built}
    for kind, key, need in asked:
        if (kind, key) not in records:
            continue
        offer, record = records[(kind, key)]
        if kind == "part":
            sentences, other = [sentence for _, sentence in limits_of_part(record, key)], ""
        else:
            limits = board_limits(need, record, offer.functions, definitions, key)
            sentences, other = limits.sentences, _other_choice(need, built, mine) if limits.no_pin else ""
        if sentences:
            notes.append("%s %s for %s: %s" % (kind, key, need["id"], " ".join(sentences + ([other] if other else []))))
    return notes


# --- end MVP ---


def plan_holds(name, after, entries):
    """
    The drawer changes that bring project `name`'s holds in line with its needs `after` (§8 C), with the notes and problems
    working them out gives: (changes, notes, problems). One piece per pick, one board however many needs pick it, on the
    entries that hold it, never past what is owned or what another project holds. Nothing is written here.
    """
    notes, problems = [], []
    wanted = collections.Counter(next(iter(pick.items())) for need in after for pick in need.get("pick") or [])
    # --- MVP --- P387: a project has one board, however many needs its own LED or button serves
    wanted = collections.Counter({asked: 1 if asked[0] == "board" else pieces for asked, pieces in wanted.items()})
    pointing, mine = offers.pointing_at(entries), collections.Counter()
    # a pick of one drawer entry has nowhere else to go: it takes its piece before a pick of a record, which may take another entry
    for (kind, key), pieces in sorted(wanted.items(), key=lambda asked: (asked[0][0] != "entry", asked[0])):
        held = _held({kind: key}, entries, pointing)
        owned, _, unsure = offers.counts([entry for _, entry in held], name)
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
        holders = drawer.holders_of([entry for _, entry in held], name)
        if pieces:
            problems.append(_problem(key, "%s owned%s — %d picked here" % (owned, ", held by " + ", ".join(printable(who) for who in holders) if holders else "",
                                                                           pieces + sum(mine[entry_id] for entry_id, _ in held)),
                                     _how_to_free([entry_id for entry_id, _ in held], holders)))
        notes += ["%s: maybe owned — check the drawer first" % key] if unsure else []
        notes += ["%s: count unknown — check the drawer" % key] if owned == "unknown" else []
    changes = []
    for entry_id, entry in sorted(entries.items()):
        used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}
        used_in.update({name: mine[entry_id]} if mine[entry_id] else {})
        if used_in != (entry.get("used_in") or {}):
            changes.append(drawer.settle(entry_id, entry, {"used_in": used_in}, [])[0])
    return changes, notes, problems


def released_holds(changes, name):
    """
    The holds of project `name` a pick lets go (C-4): each drawer entry whose reservation for it goes down, because no pick of
    the project explains it any more — a re-pick, or a hold given by hand — as {"entry", "was", "now"}. A pick rebuilds the
    project's holds from its picks (§8 C), and what it drops is said, never left to a bare `used_in … → {}`.
    """
    return [{"entry": change["entry"], "was": was, "now": now} for change in changes
            for was, now in [((change["was"].get("used_in") or {}).get(name, 0), change["now"]["used_in"].get(name, 0))] if now < was]


def dropped_holds(name, current, after, entries):
    """
    What dropping a need lets go (P514): (drawer changes, released) for project `name`. Only an entry whose planned hold falls
    between the needs `current` and the needs `after` is touched, and by that fall alone, taken off the hold the entry has now.
    A hold no pick explains, and a hold another project's over-holding keeps from the plan, stay as they are.
    """
    def planned(needs):
        return {change["entry"]: change["now"]["used_in"].get(name, 0) for change in plan_holds(name, needs, entries)[0]}
    before, later, changes, released = planned(current), planned(after), [], []
    for entry_id, entry in sorted(entries.items()):
        has = (entry.get("used_in") or {}).get(name, 0)
        fall = before.get(entry_id, has) - later.get(entry_id, has)
        if fall > 0 and has > 0:
            used_in = {who: n for who, n in entry["used_in"].items() if who != name}
            used_in.update({name: has - fall} if has > fall else {})
            changes.append(drawer.settle(entry_id, entry, {"used_in": used_in}, [])[0])
            released.append({"entry": entry_id, "was": has, "now": used_in.get(name, 0)})
    return changes, released


def _picks_given(given, known, entries, ids):
    """(each need's picks, notes, problems) of the [(need id, id)] a `--pick` gives, for `plan_pick`; a key that is not plain raises."""
    picked, notes, problems = {}, [], []
    for need_id, pick_id in given:
        pick = _resolve(pick_id, known, entries)
        named = next(iter(pick.values())) if pick else None
        if need_id not in ids:
            problems.append(_problem(need_id, "no need called %s — --needs lists them" % need_id))
        elif pick is None:
            problems.append(_problem(need_id, "no record or drawer entry called %s — --match lists the candidates" % pick_id))
        elif not (store.PLAIN.fullmatch(pick_id) and store.PLAIN.fullmatch(named)):  # the key given, and the id written
            raise store.StoreError("%r is not a plain key — lower-case letters, digits and '-' — so a pick cannot name it: "
                                     "rename the drawer entry, or the record's file, then pick it",
                                     named if store.PLAIN.fullmatch(pick_id) else pick_id, code=records_codes.KEY_NOT_PLAIN)
        elif pick not in picked.setdefault(need_id, []):
            picked[need_id].append(pick)
            renamed = "%s: the drawer entry of %s — picked as that record" % (pick_id, named)
            notes += [renamed] if named != pick_id and renamed not in notes else []
    return picked, notes, problems


def plan_pick(project, given, passed_over=()):
    """
    What a `--pick` would do (§8 C): (the needs after, drawer changes, history events, notes, problems). `given` is
    [(need id, id)], and each need it names gets exactly those picks. Then the project's reservations are worked out again
    from every need's picks — one piece per pick, one board however many needs pick it — on the entries that hold them,
    never past what is owned or what another project holds (C2; a record and its drawer entry are one stock, however it is picked), so a re-pick frees what it no
    longer picks. A pick no entry holds is to get, not reserved. A drawer entry of a record spark knows, picked by its key, is
    a pick of that record, and says so. A `reused` event is written for each pick except a record the project keeps in its
    own parts/ or boards/: that was not there before the project. A reason a part was passed over is kept in the person's
    words, without any URL or price in them (`kept_reason`), and said when one was taken out. Nothing is written here.
    """
    name, current, entries = store.plan_listed_name(project), read(project), drawer.entries()
    rows = drawer.linkable(project)
    known, ids = {row[:2]: row[2] for row in rows}, {need["id"] for need in current}
    picked, notes, problems = _picks_given(given, known, entries, ids)
    after = [dict(need, pick=picked[need["id"]]) if need["id"] in picked else need for need in current]
    changes, hold_notes, hold_problems = plan_holds(name, after, entries)
    notes += hold_notes
    problems += hold_problems
    notes += ["%s: a board needs a board file — a record in boards/ — before spark can build with it" % key
              for key in unfiled_boards(after, known, entries)]
    # F12 (C-7): a board this pick picks that stops the chain at the footprint stage is said, never refused
    for key in sorted({key for need_id in picked for pick in picked[need_id] for kind, key in pick.items() if kind == "board"}):
        stop = footprint_emitter.footprint_stop(key, project)
        notes += ["board %s: %s" % (key, stop)] if stop else []
    notes += _limits_notes(after, picked, rows, entries, name)
    events = [dict({"event": "reused", "project": name, "need": need_id}, **pick) for need_id in picked for pick in picked[need_id]]
    # a record the project keeps in its own parts/ or boards/ was not there before the project: it is no reuse of the store (§6.7)
    events = [event for event in events if not any(known.get((kind, event.get(kind))) == "project" for kind in ("part", "board"))]
    told, said, refused = _passed_over(passed_over, name, known, entries, ids)
    return after, changes, events + told, notes + said, problems + refused


def _passed_over(passed_over, name, known, entries, ids):
    """(events, notes, problems) of each part `--pick` was told was passed over, for `plan_pick`: a `passed_over` event, a
    note when its reason lost a URL or a price, or a problem."""
    events, notes, problems = [], [], []
    for number, item in enumerate(passed_over if isinstance(passed_over, (list, tuple)) else [None], 1):
        pick = _resolve(item.get("id"), known, entries) if isinstance(item, dict) and isinstance(item.get("id"), str) else None
        why, cut = kept_reason(item["why"]) if pick and isinstance(item.get("why"), str) else ("", False)
        why = why if re.search(r"[^\W\d_]", why) else ""  # F14: what is left with no letter in it is no reason either
        if not (pick and item.get("need") in ids and drawer._words(why) and item.get("by", "person") in ("person", "agent")):
            problems.append(_problem("passed over %d" % number, 'a part passed over is {"need", "id", "why", "by": '
                                     '"person" or "agent"}: a need and an id spark has, and the reason in words — a URL or '
                                     'a price is not kept, so a reason that is only those is none'))
            continue
        events.append(dict({"event": "passed_over", "project": name, "need": item["need"]}, **pick, why=why, by=item.get("by", "person")))
        notes += ["%s: the reason is kept without the URL or price in it — your history keeps words, never a URL or a price"
                  % item["id"]] if cut else []
    return events, notes, problems


def owned(pick, entries):
    """Whether the drawer holds a pick (§6.7's "owned"): a live entry with a count above 0, many, or a count nobody gave."""
    held = _held(pick, entries, offers.pointing_at(entries))
    return bool(held) and offers.counts([entry for _, entry in held])[0] != 0
