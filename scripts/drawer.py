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

#: What a part does (§5.6): the PO's 13 verbs. `drive` is the driver (an L9110S), `move` the thing driven (a motor).
VERBS = ("sense", "input", "indicate", "sound", "move", "drive", "power", "keep-time", "store", "compute",
         "communicate", "connect", "mount")

#: An entry's fields, in the order its file shows them (§5.2). No price, no date, no condition grade (W21).
FIELDS = ("label", "count", "part_number", "revision", "is", "function", "place", "used_in", "from", "bought",
          "unsure", "skip", "photos")

#: A label is shown and matched, never obeyed (§6.4.6): control characters go, and it stops at 160 characters.
LABEL_MAX = 160
CONTROL = re.compile(r"[\x00-\x1f\x7f]+")

#: The layers spark keeps itself. A record found anywhere else lives in one project, and is shelved when linked.
SPARKS_OWN = ("shelf", "library", "catalog")

#: What a part number links to: the `is` it sets, where that record lives and its file — or the question to ask instead.
Link = namedtuple("Link", "target where path question")


def clean(text):
    """Words from a shop or a person, made safe to show: control characters become a space; at most 160 characters."""
    return CONTROL.sub(" ", str(text)).strip()[:LABEL_MAX]


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
            found[path.stem] = json.loads(path.read_text())
            if not isinstance(found[path.stem], dict):
                raise ValueError("an entry is a JSON object")
        except ValueError as broken:
            raise store.StoreProblem("%s is not JSON (%s) — fix it by hand; the drawer is read whole or not at all" % (path, broken))
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
    an `is` the write names must exist; an entry with a part number and no `is` is linked by that number. A change is
    {"entry", "new", "was", "now", "after", "shelve"}. Nothing is written here.
    """
    values = {key: (clean(value) if key == "label" and isinstance(value, str) else value) for key, value in values.items()}
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
    changed = [key for key in FIELDS if key in after and after[key] != (before or {}).get(key)]
    return ({"entry": entry_id, "new": before is None, "was": {key: before.get(key) for key in changed} if before else {},
             "now": {key: after[key] for key in changed}, "after": after, "shelve": shelve if changed else None},
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
            problems.append(parts._problem(None, "an entry needs a label, or an `entry` key of letters, digits and '-'"))
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
