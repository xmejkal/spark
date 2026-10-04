"""
What the person owns: the drawer (P93, P95; docs/2026-10-04-store-design.md §5.2, §5.5, §8 D).

An entry is light — a label and a count are enough, and owning never triggers research. It points at a record
when one exists (`is`), found by an exact part number only: a near number, two matches or a name alone is a
question for the person, never a link. Every write SETS values the agent worked out and the dry run showed
("count 2 → 4"), so a retried write changes nothing, and nothing is deleted — gone is count 0. When an entry
links a part that lives only in another project, the record goes onto the shelf, so every project finds it.
"""

import json
import re
from collections import namedtuple

import boards
import parts
import store

#: What a part does (§5.6) — one list, in parts.py.
VERBS = parts.VERBS

#: An entry's fields, in the order its file shows them (§5.2). No price, no date, no condition grade (W21).
FIELDS = ("label", "count", "part_number", "revision", "is", "function", "place", "used_in", "from", "bought",
          "unsure", "skip", "photos")

#: A label is shown and matched, never obeyed (§6.4.6): control and bidi characters go, and it stops at 160 characters.
LABEL_MAX = 160
CONTROL = re.compile("[\x00-\x1f\x7f-\x9f\u200e\u200f\u202a-\u202e\u2066-\u2069]+")

#: The layers spark keeps itself. A record found anywhere else lives in one project, and is shelved when linked.
SPARKS_OWN = ("shelf", "library", "catalog")

#: What a part number links to: the `is` it sets, where that record lives and its file — or the question to ask instead.
Link = namedtuple("Link", "target where path question")


def clean(text):
    """Words from a shop or a person, made safe to show: control and bidi characters become a space; at most 160 characters."""
    return CONTROL.sub(" ", str(text)).strip()[:LABEL_MAX]


def _scrubbed(value):
    """A value with every string in it cleaned — but not the fixed words (`does`, a photo's sha256) nor the ids an `is` names."""
    if isinstance(value, str):
        return clean(value)
    if isinstance(value, list):
        return [_scrubbed(item) for item in value]
    if isinstance(value, dict):
        return {key: item if key in ("sha256", "does") else _scrubbed(item) for key, item in value.items()}
    return value


def _words(value):
    return isinstance(value, str) and bool(value.strip())


def _whole(value, least=0):
    return isinstance(value, int) and not isinstance(value, bool) and value >= least


#: Each field's test, and the sentence said when a value fails it (§5.2).
CHECKS = {
    "label": (_words, "a label is the words you would say for it"),
    "count": (lambda v: v == "many" or _whole(v), 'a count is whole pieces, 0 or more, or "many" — a 10-pack is 10'),
    "part_number": (lambda v: v is None or (isinstance(v, dict) and _words(v.get("number")) and set(v) <= {"maker", "number"}),
                    'a part number is {"maker", "number"}, or null'),
    "revision": (lambda v: v is None or _words(v), "a revision is words, or null"),
    "is": (lambda v: v is None or (isinstance(v, dict) and len(v) == 1 and set(v) <= {"part", "board"}
                                   and _words(next(iter(v.values())))), '`is` is {"part": id} or {"board": id}, or null'),
    "function": (lambda v: isinstance(v, list) and all(isinstance(f, dict) and f.get("does") in VERBS and _words(f.get("what"))
                                                       for f in v),
                 'a function is [{"does": one of %s, "what": words}]' % ", ".join(VERBS)),
    "place": (lambda v: v is None or _words(v), "a place is words, or null"),
    "used_in": (lambda v: isinstance(v, dict) and all(_whole(n, 1) for n in v.values()), "`used_in` is {project: how many}"),
    "from": (lambda v: v is None or (isinstance(v, dict) and _words(v.get("seller")) and set(v) <= {"seller", "product"}),
             '`from` is {"seller", "product"} — a shop\'s product code, never an order number'),
    "bought": (lambda v: isinstance(v, dict) and all(_whole(n) for n in v.values()), "`bought` is {source: the total last seen}"),
    "unsure": (lambda v: isinstance(v, bool), "`unsure` is true or false"),
    "skip": (lambda v: v is None or _words(v), "`skip` is the person's words, or null"),
    "photos": (lambda v: isinstance(v, list) and all(isinstance(p, dict) and re.fullmatch(r"[0-9a-f]{64}", str(p.get("sha256")))
                                                     and _words(p.get("file")) for p in v),
               '`photos` are [{"sha256", "file"}], each kept with `parts.py --keep`'),
}


def entries():
    """{entry key: entry} — the whole drawer. A file that is not JSON is named, never skipped: a drawer read in part lies."""
    found, folder = {}, store.place("drawer")
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        try:
            found[path.stem] = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(found[path.stem], dict):
                raise ValueError("an entry is a JSON object")
        except ValueError as broken:
            raise store.StoreProblem("%s is not JSON (%s) — fix it by hand; the drawer is read whole or not at all" % (path, broken))
        for key, value in found[path.stem].items():
            if key != "schema" and (key not in FIELDS or not CHECKS[key][0](value)):
                raise store.StoreProblem("%s: %s — fix it by hand; the drawer is read whole or not at all"
                                         % (path, "`%s` is not a drawer field" % key if key not in FIELDS else "`%s`: %s" % (key, CHECKS[key][1])))
    return found


def linkable():
    """
    Every record an entry may point at, nearest first, as (kind, id, where, path): spark's own layers (the shelf, the
    library, the catalog), then each project on the person's list, by its name (§5.5). The first of an id wins. A
    project whose folder is gone has nothing to offer and is passed over.
    """
    found = [("part", part_id, layer, path) for part_id, (layer, path) in store.records("parts", parts.LIBRARY, drafts=True).items()]
    found += [("board", board_id, layer, path) for board_id, (layer, path) in boards.records().items()]
    for name, folder in store.projects().items():
        found += [("part", path.stem, name, path) for path in sorted((folder / "parts").glob("*.json"))]
        found += [("board", path.stem, name, path) for path in sorted((folder / "boards").glob("*.json"))
                  if path.name not in boards.NOT_A_BOARD]
    unique = {}
    for row in found:
        unique.setdefault(row[:2], row)
    return list(unique.values())


def numbers(record, record_id):
    """
    A record's exact part numbers, lower case (§5.5): (stated, tokens). Stated are its `sku` (a board keeps a list)
    and each whole alias; tokens are the whole tokens of its id and aliases that hold a letter and a digit, so a
    word like "button" is never a number.
    """
    sku = record.get("sku")
    aliases = [alias for alias in record.get("also_known_as") or [] if isinstance(alias, str)]
    stated = {s.lower() for s in (sku if isinstance(sku, list) else [sku]) + aliases if isinstance(s, str)}
    words = (token for word in [record_id] + aliases for token in re.split(r"[^a-z0-9]+", word.lower()))
    return stated, {w for w in words if re.search(r"[a-z]", w) and re.search(r"\d", w)}


def _differs_by_a_suffix(number, other):
    """Whether two part numbers differ only by a suffix after a separator — SEN0161-V2 and SEN0161: a question, never a link."""
    longer, shorter = (number, other) if len(number) > len(other) else (other, number)
    return (len(longer) > len(shorter) and longer.startswith(shorter) and not longer[len(shorter)].isalnum()
            and any(c.isdigit() for c in shorter) and any(c.isalpha() for c in shorter))


def _match(wanted, record, record_id):
    """'exact', 'near' or None: a stated number outranks an id token, and a stated near miss outranks a token hit."""
    stated, tokens = numbers(record, record_id)
    for these in (stated, tokens):
        if wanted in these:
            return "exact"
        if any(_differs_by_a_suffix(wanted, other) for other in these):
            return "near"
    return None


def _named(rows):
    return ", ".join("%s %s (%s)" % (kind, record_id, where) for kind, record_id, where, _ in rows)


def link(number, known=None, maker=None):
    """
    What a part number links to (§5.5): exactly one exact match, ignoring case, is a link; two, or numbers that
    differ only by a suffix, or a maker that is not the record's vendor, are a question; a number nothing knows is
    neither — owned, with no record.
    """
    wanted, exact, near = number.lower(), [], []
    for kind, record_id, where, path in (linkable() if known is None else known):
        record = parts._parse(path)
        if not isinstance(record, dict):
            continue
        found = _match(wanted, record, record_id)
        vendor = record.get("vendor")
        if found == "exact" and isinstance(maker, str) and isinstance(vendor, str) and maker.lower() != vendor.lower():
            found = "near"
        if found:
            (exact if found == "exact" else near).append((kind, record_id, where, path))
    if len(exact) == 1:
        kind, record_id, where, path = exact[0]
        return Link({kind: record_id}, where, path, None)
    if exact:
        return Link(None, None, None, "%s matches %s — which one is it?" % (number, _named(exact)))
    if near:
        return Link(None, None, None, "%s is close to %s — the same part?" % (number, _named(near)))
    return Link(None, None, None, None)


def resolve(target, known):
    """Where an `is` points — resolved on read, no layer kept (§5.2): (where, path), or (None, None) when nothing has that id."""
    kind, record_id = next(iter(target.items()))
    return next(((where, path) for found_kind, found_id, where, path in known if (found_kind, found_id) == (kind, record_id)),
                (None, None))


def _shelve_from(target, where, path):
    """What shelving a link needs — (path, project) — when the record is a part living only in one project."""
    return (path, where) if where is not None and where not in SPARKS_OWN and "part" in target else None


def settle(entry_id, before, values, known):
    """
    One entry after a write sets `values` on it (§5.2): (change or None, questions, problems). Every value is checked;
    an `is` the write names must exist and is set as given (null too). Otherwise a new or changed part number links, and
    drops a stale `is` when nothing matches; an entry with a number and no `is` key is linked once. A change is
    {"entry", "new", "was", "now", "after", "shelve"}. Nothing is written here.
    """
    values = {key: (value if key == "is" else _scrubbed(value)) for key, value in values.items()}
    problems = [parts._problem(entry_id, "%s is not a drawer field — the fields are %s" % (key, ", ".join(FIELDS)))
                for key in values if key not in FIELDS]
    problems += [parts._problem(entry_id, CHECKS[key][1]) for key, value in values.items() if key in CHECKS and not CHECKS[key][0](value)]
    if before is None and not {"label", "count"} <= set(values):
        problems.append(parts._problem(entry_id, "a new entry needs a label and a count"))
    if problems:
        return None, [], problems
    after, questions, shelve = dict(before or {"schema": 1}, **values), [], None
    if values.get("is"):
        where, path = resolve(values["is"], known)
        if where is None:
            return None, [], [parts._problem(entry_id, "no record called %s — `parts.py --need` finds what exists"
                                             % json.dumps(values["is"]))]
        shelve = _shelve_from(values["is"], where, path)
    elif "is" not in values and _words((after.get("part_number") or {}).get("number")) and (
            "is" not in after or before is None or after["part_number"] != before.get("part_number")):
        number = after["part_number"]
        found = link(number["number"], known, number.get("maker"))
        after.pop("is", None)
        if found.target:
            after["is"], shelve = found.target, _shelve_from(found.target, found.where, found.path)
        elif found.question:
            questions.append({"entry": entry_id, "sentence": found.question})
    after = {key: after[key] for key in ("schema",) + FIELDS if key in after}
    changed = [key for key in FIELDS if after.get(key) != (before or {}).get(key)]  # a removed key is a change to null
    return ({"entry": entry_id, "new": before is None, "was": {key: before.get(key) for key in changed} if before else {},
             "now": {key: after.get(key) for key in changed}, "after": after, "shelve": shelve if changed else None},
            questions, [])


def _free_key(label, current):
    """The key a new label is filed under: its slug, or the next `<slug>-2`, `-3` … whose entry has another label."""
    base, key, n = store.slug(label), store.slug(label), 1
    while key in current and current[key].get("label") != label:
        n += 1
        key = "%s-%d" % (base, n)
    return key


def plan_set(items):
    """
    What a `--drawer-set` would do: (changes, questions, problems). Each item sets fields on one entry — `entry`
    names it; a new one's key is made from its label. A later item sees what an earlier one set.
    """
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return [], [], [parts._problem(None, "a drawer write is a JSON list of entries, each an object")]
    current, known, changes, questions, problems = entries(), linkable(), [], [], []
    for item in items:
        values = {key: value for key, value in item.items() if key != "entry"}
        entry_id = item.get("entry") or (_free_key(clean(values["label"]), current) if _words(values.get("label")) else None)
        if not (isinstance(entry_id, str) and store.PLAIN.fullmatch(entry_id)):
            problems.append(parts._problem(None, "an entry needs a label, or an `entry` key of lower-case letters, digits and '-'"))
            continue
        change, asked, refused = settle(entry_id, current.get(entry_id), values, known)
        questions += asked
        problems += refused
        if change:
            changes.append(change)
            current[entry_id] = change["after"]
    return changes, questions, problems


def apply(changes):
    """Shelve what a new link brought in, then write every entry that changed."""
    for change in changes:
        if change["shelve"]:
            parts.shelve(*change["shelve"])
        if change["now"]:
            store.write_json("drawer", change["entry"], change["after"])


def listing():
    """Every entry as the drawer shows it (§8 D4): its key, label, count, what it is and where that lives, unsure, skip."""
    known, shown = linkable(), []
    for entry_id, entry in sorted(entries().items(), key=lambda pair: (str(pair[1].get("label", "")).lower(), pair[0])):
        target = entry.get("is") if isinstance(entry.get("is"), dict) and entry.get("is") else None
        shown.append({"entry": entry_id, "label": entry.get("label"), "count": entry.get("count"), "is": target,
                      "in": resolve(target, known)[0] if target else None, "unsure": bool(entry.get("unsure")),
                      "skip": entry.get("skip")})
    return shown


#: An importer's SKU, by source (§6.6): capitals, digits, and the suffixes the shop really prints (DFR0675-EN,
#: FIT0654-1, SEN0161-V2, MYST01-Raspberry Pi). Importers are a set keyed by source, and this is that set.
SKU_SHAPES = {"dfrobot": re.compile(r"[A-Z]{2,6}\d{2,5}(?:-[A-Za-z0-9][A-Za-z0-9 ]{0,30})?")}


def payload_problems(source, payload):
    """Why an importer's payload cannot be applied (§6.6): its shape, a SKU that is not one, lines read ≠ lines stated."""
    if source not in SKU_SHAPES:
        return ["no importer called %r — there is: %s" % (source, ", ".join(sorted(SKU_SHAPES)))]
    if not isinstance(payload, dict) or payload.get("source") != source or not isinstance(payload.get("items"), list):
        return ['a %s payload is {"source": "%s", "lines", "stated", "items": [{"sku", "name", "count"}]}' % (source, source)]
    problems = []
    if payload.get("lines") == 0 == payload.get("stated"):
        problems.append("read no order lines — logged out, or the pages changed; nothing imported")
    if not _whole(payload.get("lines")) or payload.get("lines") != payload.get("stated"):
        problems.append("read %s line(s) where the order pages state %s — a line the extractor could not parse is a part left "
                        "out (a `$` in a name did it once): fix the extractor and read again"
                        % (payload.get("lines"), payload.get("stated")))
    for index, item in enumerate(payload["items"]):
        sku = item.get("sku") if isinstance(item, dict) else None
        if not (isinstance(sku, str) and SKU_SHAPES[source].fullmatch(sku)):
            problems.append("items[%d]: %s is not a %s SKU" % (index, json.dumps(sku, ensure_ascii=False)[:40], source))
        elif not _whole(item.get("count"), 1):
            problems.append("items[%d] %s: a count is a whole number, 1 or more" % (index, sku))
        elif not _words(item.get("name")):
            problems.append("items[%d] %s: it has no name" % (index, sku))
    return problems


def kept_payload(payload):
    """What the store keeps of an import (§5.1): SKU, name and count per line, and the two line counts — nothing else."""
    return {"source": payload["source"], "lines": payload["lines"], "stated": payload["stated"],
            "items": [{"sku": item["sku"], "name": clean(item["name"]), "count": item["count"]} for item in payload["items"]]}


def plan_import(source, payload):
    """
    What applying an importer's payload would do (§5.2): (changes, questions, problems, smaller). A SKU the drawer
    has not seen becomes an entry, counted as owned — the person corrects. One seen before follows the re-import rule:
    when its total T grew, `count += T − bought` and `bought` becomes T — but a count the person corrected away from
    `bought` is a question, not arithmetic (a pack of 10 is not one more piece); an `unsure` entry it
    confirms takes T and is sure; a smaller T changes nothing and is said. A new SKU whose record an entry said in
    words already is, is a question — not written until the person answers.
    """
    refused = payload_problems(source, payload)
    if refused:
        return [], [], [parts._problem(source, sentence) for sentence in refused], []
    current, known = entries(), linkable()
    by_product = {(entry.get("from") or {}).get("product"): entry_id for entry_id, entry in current.items()
                  if (entry.get("from") or {}).get("seller") == source}
    others = {entry_id: entry for entry_id, entry in current.items() if (entry.get("from") or {}).get("seller") != source}
    totals = {}
    for item in payload["items"]:  # a SKU on several lines is one product: its lines add up, the first name stays
        first = totals.setdefault(item["sku"], dict(item, count=0))
        first["count"] += item["count"]
    changes, questions, problems, smaller = [], [], [], []
    for item in totals.values():
        sku, total = item["sku"], item["count"]
        entry_id = by_product.get(sku) or store.slug("%s-%s" % (source, sku))
        before = current.get(entry_id)
        if before is None:
            target = link(sku, known, maker=source).target
            said = next((other for other, entry in others.items() if (target and entry.get("is") == target)
                         or str((entry.get("part_number") or {}).get("number")).lower() == sku.lower()), None)
            if said:
                questions.append({"entry": said, "sentence":
                                  "%s from %s is what entry %s already says it is — the same item, or another? The same: set this "
                                  "entry's `from` to %s. Another: write the entry %s with --drawer-set. Either way the next import "
                                  "finds it and asks no more." % (sku, source, said, json.dumps({"seller": source, "product": sku}),
                                                                  entry_id)})
                continue
            values = {"label": item["name"], "count": total, "part_number": {"maker": source, "number": sku},
                      "from": {"seller": source, "product": sku}, "bought": {source: total}, "unsure": False}
        else:
            seen = (before.get("bought") or {}).get(source)
            if seen is not None and total < seen:
                smaller.append("%s: %s now says %d, %d were seen before — the entry keeps what it says" % (entry_id, source, total, seen))
            if seen is not None and total <= seen:
                continue
            values = {"bought": dict(before.get("bought") or {}, **{source: total})}
            if before.get("unsure"):
                values.update(count=total, unsure=False)
            elif _whole(before.get("count")) and seen is not None and before["count"] != seen:
                questions.append({"entry": entry_id, "sentence":
                                  "%s: %d more bought from %s since; this entry's count was corrected (%d for %d) — how many pieces "
                                  "now? Set it with --drawer-set, with `bought` %s." % (entry_id, total - seen, source, before["count"], seen,
                                                                                      json.dumps({source: total}))})
                continue
            elif before.get("count") != "many" and seen is not None:  # no total seen yet: the count is the person's own
                values["count"] = before.get("count", 0) + total - seen
        change, asked, refused = settle(entry_id, before, values, known)
        questions += asked
        problems += refused
        if change:
            changes.append(change)
            current[entry_id], by_product[sku] = change["after"], entry_id
    return changes, questions, problems, smaller
