"""
What is known about a part, said and kept (W6-S3b, P721): the signals it asks for (`signals_for`), what nobody has
checked (`unverified`, `open_questions_of`), the names it prints (`printed_names`), the shelf copy and its digest
(`digest`, `shelve`, `note_built`), a record promoted or written to fill in (`promote`, `skeleton`), and one record
described (`describe`, `_row`). Moved whole from `parts.py`. It imports the records area, `part_rules` and
`part_records` below it, never `parts.py`.
"""

import hashlib
import json
from pathlib import Path

from spark.records import provenance, record_kind, store
from spark.records.record_kind import DEFINITION_SUFFIX, PIN_LISTS, record_home
from spark.sourcing import sourcing_codes
from spark.sourcing.part_records import any_record, load, PartError, validate
from spark.sourcing.part_rules import conflicts_of


def printed_names(part):
    """`{wiring name: silkscreen text}` for every pin whose silkscreen differs from its name."""
    out = {}
    for group in PIN_LISTS:
        for entry in part.get(group) or []:
            pin, printed = entry.get("pin"), entry.get("printed")
            if pin and printed and printed != pin:
                out[pin] = printed
    return out


def has_placeholder_footprint(part):
    """Whether this part's footprint is a stand-in for one nobody has drawn yet."""
    return bool(part.get("footprint_placeholder"))


def signals_for(part_ids, project: Path = None) -> list:
    """
    Every signal these parts ask the host for, ready for `assign_pins.py`.

    Optional signals are included: a part that CAN wake the host usually should be able to, and
    a caller that does not want it can drop it. Silently omitting them would hide a requirement.
    """
    signals = []
    for part_id in part_ids:
        part = load(part_id, project)
        for need in part.get("needs") or []:
            entry = {"name": need["signal"], "needs": need.get("needs", [])}
            if need.get("bus"):
                # A bus signal means dedicated hardware: the board's pin for that line of that
                # bus, found by `assign_pins.bus_line`. `line` is the part's own name for the
                # line — SDA, or a vendor's DIN — and it has to survive the instance rename that
                # `loader.signals_of` gives `name`, or the assigner cannot find the pin (P21).
                entry["bus"] = need["bus"]
                entry["line"] = need["signal"]
            entry["from"] = part_id
            signals.append(entry)
    return signals


def open_questions_of(part, part_id=None):
    """Every fact in one record nobody has checked — its pin order and its outline among them (P81, P373)."""
    return [{"part": part_id or part.get("id"), **row} for row in provenance.list_unverified_facts(part)]


def unverified(part_ids, project: Path = None) -> list:
    """Every fact nobody has checked, across these parts — the design's real open questions."""
    return [question for part_id in part_ids for question in open_questions_of(any_record(part_id, project), part_id)]


#: What a record leaves behind when it goes onto the shelf (§5.5): who owns one, their photos, where to buy it,
#: the options one project weighed. The shelf keeps the part, not one project's story of it.
SHELF_DROPS = ("owned", "photo", "photos", "sourcing", "alternatives")

#: Some of the facts a build reads from a part record (§5.7) — not its outline (`body_mm`) or its simulation stand-in: a
#: digest of these vouches for a record until one of them changes.
BUILD_FACTS = ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts")
#: Some of the facts a build reads from a board (§5.7) — not its pin roles or GPIO capabilities (`pin_roles`, `adc_gpio`,
#: `wake_capable_gpio`, which assign_pins reads).
BOARD_FACTS = ("pins", "power_pads", "physical")


def digest(record, facts=BUILD_FACTS):
    """
    The sha256 of some of the facts a build reads (BUILD_FACTS / BOARD_FACTS: not a part's outline or simulation stand-in,
    nor a board's pin roles) — a part's by default, a board's with BOARD_FACTS (§5.7).
    """
    shown = {key: record[key] for key in facts if key in record}
    return hashlib.sha256(json.dumps(shown, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def note_built(design):
    """
    A `built` line in the history when a listed project's board runs end to end (§5.7, §8 T): the board's and each part's
    digest, so a proof of an old pin order never vouches for a corrected one. A project not on the list keeps no history.
    """
    name = store.find_listed_name(design.project)
    if name is None:
        return False
    with store.locked():
        return store.append_event({"event": "built", "project": name,
                                   "board": {"id": design.board["id"], "digest": digest(design.board, BOARD_FACTS)},
                                   "parts": [{"id": part["id"], "digest": digest(part)} for part in design.parts]})


def _shelf_copy(path, project_name=None, record=None):
    """
    What the shelf would hold of a record: filtered — and when it came from a project, which one and its digest (§5.5).
    `record` is the record as it would be written, when that is not yet what its file says (a dry run).
    """
    record = json.loads(Path(path).read_text()) if record is None else record
    copy = {key: value for key, value in record.items() if key not in SHELF_DROPS}
    if project_name:
        copy["based_on"] = {"project": project_name, "digest": digest(record)}
    return copy


def shelvable(path, project_name=None):
    """Whether a record may go onto the shelf: only one whose shelf copy meets the contract, or `--list` breaks in every project."""
    return not validate(_shelf_copy(path, project_name), Path(path))


def shelve(path, project_name=None):
    """
    Put a record onto the person's shelf, so every project finds it (§5.5): a filtered copy — that says which project
    it came from and that record's digest, when it came from one; a catalog record names none, since nothing reads it.
    Its folder (a simulation chip) travels with it. Returns whether the shelf changed — or None when the record does
    not meet the contract (a draft stays where it is).
    """
    path = Path(path)
    copy = _shelf_copy(path, project_name)
    if validate(copy, path):
        return None
    changed = store.write_json("shelf", path.stem, copy)
    if (path.parent / path.stem).is_dir():
        store.copy_folder("shelf", path.parent / path.stem, path.stem)
    return changed


def promote(part_id, project, to=None, dry_run=False):
    """
    Move a record one step along its life: catalog -> the project's parts/ (to build with; it must
    then pass the contract), or the project's parts/ -> the plugin's library (for every later
    project). Its folder (a simulation chip) travels with it; its documents are
    pointers into the store and need nothing moved. Nothing is ever overwritten. Returns the path.
    """
    import shutil
    home = record_home(part_id, project)
    if home is None:
        raise PartError("no record called %r to promote", part_id, code=sourcing_codes.NO_SUCH_PART)
    to = Path(to) if to else (Path(project) / "parts" if home in (store.place("catalog"), store.place("shelf"))
                              else record_kind.LIBRARY)
    target = to / (part_id + DEFINITION_SUFFIX)
    if target.exists():
        raise PartError("%s exists; a promotion never overwrites", target,
                        code=sourcing_codes.PROMOTION_WOULD_OVERWRITE)
    if dry_run:
        return target
    to.mkdir(parents=True, exist_ok=True)
    shutil.copy2(home / (part_id + DEFINITION_SUFFIX), target)
    if (home / part_id).is_dir():
        shutil.copytree(home / part_id, to / part_id, dirs_exist_ok=True)
    return target


def skeleton(part_id, kind, vendor=None, sku=None):
    """
    A record with every field present and nothing guessed: what research fills in. `sku` is the maker's exact part
    number when the person knows it (P737: the DFRobot wiki source finds the page by it).

    Nulls are facts nobody has recorded, and `validate` refuses the file until they are — the
    same rule `init` applies to the rules file. A fact is `verified: true` only when its value
    is the vendor's own text at the cited URL; read off an image, scaled, inferred or computed,
    it is `verified: false` with `why_it_matters` (the rule `commands/research.md` states). No `sourcing`: the
    rules keep no seller listing and no price (W21, P740).
    """
    return {
        "schema": 1, "id": part_id, "name": None, "kind": kind,
        "//": ("Written by /spark:research. A null is a fact nobody has recorded. verified: true = the "
               "vendor's own text at the cited URL; read off an image, inferred or computed = false. A pin is a wiring "
               "name of letters, digits and _; what the silkscreen prints goes in printed (\"pin\": \"VCC\", \"printed\": \"+5V\")."),
        "vendor": vendor, "sku": sku, "sources": [],
        "needs": [], "power": [], "unused_pins": [], "pin_order": [], "footprint": None,
        "body_mm": {"width": None, "height": None, "verified": False, "source": None,
                    "why_it_matters": "every placement is arranged around it"},
        "facts": {}, "host_requirements": [],
    }


def _physical_lines(part):
    """The `physical` block and its proof, as `--show` prints them (P737): each size, the mark, the source, the keys not published."""
    physical, proof = part.get("physical"), part.get("physical_proof")
    if not isinstance(proof, dict):
        return []
    lines = ["\n  physical: %s (%s)" % ("verified" if proof.get("verified") else "UNVERIFIED", proof.get("source", ""))]
    lines += ["    %-28s %s" % (key, json.dumps(value)) for key, value in (physical.items() if isinstance(physical, dict) else ())]
    if proof.get("not_published"):
        lines.append("    not published: %s" % ", ".join(map(str, proof["not_published"])))
    if not proof.get("verified") and proof.get("why_it_matters"):
        lines.append("      %s" % proof["why_it_matters"])
    return lines


def describe(part):
    lines = ["%s — %s" % (part["name"], part["kind"]), ""]
    lines.append("  asks the host for:")
    for need in part.get("needs") or []:
        wants = (" [%s]" % ", ".join(need["needs"])) if need.get("needs") else ""
        optional = " (optional)" if need.get("optional") else ""
        lines.append("    %-12s -> module pin %s%s%s" % (need["signal"], need["pin"], wants, optional))

    facts = part.get("facts") or {}
    if facts:
        lines.append("\n  known:")
        for name, fact in facts.items():
            mark = "verified" if fact.get("verified") else "UNVERIFIED"
            lines.append("    %-28s %-10s %s" % (name, str(fact.get("value")), mark))
            if not fact.get("verified") and fact.get("why_it_matters"):
                lines.append("      %s" % fact["why_it_matters"])

    lines += _physical_lines(part)
    for pin, leg in (part.get("legs") or {}).items() if isinstance(part.get("legs"), dict) else ():
        lines.append("  leg %s: %s" % (pin, leg))  # P741: what --fact-set wrote, read back
    for requirement in part.get("host_requirements") or []:
        lines.append("\n  the board must: %s" % requirement)
    for conflict in conflicts_of(part):
        if conflict["rests_on"]:  # the PO's `?` line: it holds only if facts nobody has verified hold
            lines.append("\n  ? CONFLICT: %s\n    it rests on facts nobody has verified — %s" % (conflict["line"], conflict["upgrade"]))
        else:
            lines.append("\n  CONFLICT: %s" % conflict["line"])
    return "\n".join(lines)


def _row(part_id, kind, rest):
    return "  %-28s %-14s %s" % (part_id, kind, rest)
