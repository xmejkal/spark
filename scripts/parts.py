#!/usr/bin/env python3
"""
What a part asks of the board it plugs into, and what is actually known about it.

    parts.py --list
    parts.py --show l9110s-module
    parts.py --validate
    parts.py --unverified <part> [part ...]   what nobody has checked yet about those parts

A part library is easy to get wrong in a way that is worse than not having one. The temptation is a schema covering
everything a part might have — and since a motor driver's facts (input thresholds, current) have nothing in common with
a rangefinder's (an I2C address, a calibration), that schema degenerates into `{"name": ..., "notes": ...}`: a directory
of documentation pretending to be configuration.

So this splits them.

**`needs` is a real schema**, because it IS uniform: every part asks its host for some pins, and each pin either needs a
capability or does not. That is exactly what `assign_pins.py` consumes, and it is the reason this file exists rather
than a folder of markdown.

**`facts` is deliberately open**, and every entry carries three things: a value, where it came from, and whether anyone
has actually checked. A fact with `verified: false` is not a defect — most parts arrive with several — but it must be
VISIBLE, because the unverified ones are what decide whether a design works. On the project this came from, the single
most consequential number in the whole build was an audio module's idle current, which nobody had measured and every
document quietly assumed.
"""

import argparse
import contextlib
import datetime
import hashlib
import json
import re
import shlex
import struct
import sys
import urllib.parse
from pathlib import Path


#: `--need`'s matcher (P211). A default changes only with the PO's yes.
NEED_MATCHER = "name-contains"


def audit(project=None):
    """
    Every record in every layer — the catalog included — every drawer link, and each record a link reaches in the person's
    other projects, walked once (§5.4, P89): per layer how many are current, owe facts, or are broken; which say nothing
    of what they do (spark's layers and this project only); which entries point at nothing; which boards stop the chain at
    the footprint stage, their files lacking what the footprint is drawn from (C-7, P121).
    """
    import drawer
    from spark.design import footprint_emitter
    walked = [("part", found, layer, path) for found, (layer, path) in store.records("parts", record_kind.LIBRARY,
                                                                                     project, drafts=True).items()]
    walked += [("board", found, layer, path) for found, (layer, path) in board_records.records(project).items()]
    known, mine, seen = drawer.linkable(project), store.projects(), {row[3].resolve() for row in walked}
    dangling, linked = [], []
    for entry, said in drawer.entries().items():
        if not (isinstance(said.get("is"), dict) and said["is"]):
            continue
        where, path = drawer.resolve(said["is"], known)
        if where is None:
            dangling.append(entry)
        elif where in mine and path.resolve() not in seen:
            seen.add(path.resolve())
            linked.append((next(iter(said["is"])), path.stem, where, path))
    counts, owed, broken, silent, stops = {}, [], [], [], []
    for kind, found, layer, path in walked + linked:
        row = counts.setdefault(layer, {"current": 0, "owed": 0, "broken": 0})
        record = _parse(path)
        wrong = (["does not parse as a JSON object"] if not isinstance(record, dict) else _shape_problems(
            board_records.validate, record, path, "board definition") if kind == "board"
            else broken_problems(record, path))
        owing = [] if wrong or kind == "board" else owes(record)
        row["broken" if wrong else "owed" if owing else "current"] += 1
        if wrong:
            broken.append({"id": found, "layer": layer, "problems": wrong})
        elif owing:
            owed.append({"id": found, "layer": layer, "owes": owing})
        elif kind == "board" and footprint_emitter.footprint_gaps(record):  # C-7: a board owes nothing, and may still stop the chain
            stops.append({"id": found, "layer": layer, "stops_why": footprint_emitter.why_no_footprint(record),
                          "stop_line": footprint_emitter.footprint_stop_line(record)})  # P411: the text shows the line; `--audit` drops it from the JSON
        if isinstance(record, dict) and not function_of(record, board=kind == "board") and (kind, found, layer, path) not in linked:
            silent.append(found)
    return counts, owed, broken, silent, dangling, stops


sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import AnsweringParser, BadArgument, EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN, EXIT_FOR, add_env, envelope, step as next_step  # noqa: E402, F401
from spark.records.brief import Brief  # noqa: E402
from spark.records import board_records  # noqa: E402
from spark.records import missing_facts  # noqa: E402
from spark.records import provenance  # noqa: E402
from spark.records import record_kind  # noqa: E402
from spark.records import records_codes  # noqa: E402
from spark.records.record_kind import (  # noqa: E402
    _absent, Answer, available, _cannot, CHAIN_FACTS, DEFINITION_SUFFIX, _note, owes, _parse, _problem,
    record_home, _shape_problems, _with_project, WRITE_BACK_HINT, _write_record)
from spark.sourcing import sourcing_codes  # noqa: E402
from spark.records import store  # noqa: E402
from spark.core.errors import CodedMessageError  # noqa: E402
from spark.core.text_guards import guard_lines, printable  # noqa: E402
from spark.sourcing.part_rules import conflicts_of  # noqa: E402
from spark.sourcing.part_records import (  # noqa: E402
    any_record, broken_problems, definition_path, function_of, function_problems, load, NOT_A_PLAIN_ID, PartError,
    validate)
from spark.sourcing.part_facts import (  # noqa: E402
    describe, promote, _row, _shelf_copy, shelvable, shelve, signals_for, skeleton, unverified)


#: Vendors to research in, in order, when a project's brief does not say. DFRobot first because
#: its wiki carries a pinout table and a dimension drawing for every module; Seeed next for the
#: same reason. A project overrides this in `.spark/project.json` → `prefer`.
DEFAULT_VENDOR_ORDER = ("dfrobot", "seeed")


def vendor_order(project=None):
    """The vendors to research in, from the project's brief, else the default."""
    return Brief.from_project(project).prefer or DEFAULT_VENDOR_ORDER


CATALOG_KEYS = ("schema", "id", "name", "kind")
#: What `--fetch` keeps: the sources worth having when the link rots.
KEEPABLE = (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".svg")

#: An http(s) URL inside prose: "Table 3 of https://x/ds.pdf (rev 7)" cites https://x/ds.pdf. A
#: parenthesis belongs to the URL when it is balanced — DFRobot names files "DFR (1).pdf" — and
#: to the prose when it closes one the URL never opened.
URL = re.compile(r"https?://[^\s,;\]>'\"]+")


def _url_in_prose(url):
    url = url.rstrip(".:")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1].rstrip(".:")
    return url


def catalog_records():
    """Every catalog record that parses, says what it is and keeps no seller listings, by id; the rest are named as broken."""
    records, broken = {}, []
    for path in sorted(store.place("catalog").glob("*" + DEFINITION_SUFFIX)):
        record = _parse(path)
        if not (isinstance(record, dict) and all(record.get(key) for key in CATALOG_KEYS)):
            broken.append(path.name)
        elif record.get("sourcing"):
            broken.append("%s — keeps seller listings (`sourcing`): prices and stock go stale before anyone "
                          "reads them; a catalog record keeps the part, not where to buy it (P83)" % path.name)
        else:
            records[path.stem] = record
    return records, broken


def _found(words, offers, matcher=None):
    """The offers a search by words finds (P211): the need {"does": null, "what": the words, "words": as typed}, ranked by the
    `--need` matcher."""
    from spark.sourcing import matching
    need = {"does": None, "what": " ".join(words), "words": list(words)}
    return matching.found((matcher or matching.matcher(NEED_MATCHER, "need")).rank(need, offers))


def catalog_matches(words, matcher=None):
    """The catalog records a search by words finds, the way `need` finds them — researched before, unbuilt."""
    from spark.sourcing import matching
    records = catalog_records()[0]
    offers = [matching.Offer.from_record(part_id, "part", record) for part_id, record in records.items()]
    return [dict(records[fit.offer.key], id=fit.offer.key) for fit in _found(words, offers, matcher)]


#: EXIF's pointer to the GPS block, and the size in bytes of each EXIF value type (TIFF 6.0).
GPS_BLOCK_TAG = 0x8825
EXIF_TYPE_BYTES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}


def without_location(payload):
    """
    A JPEG with its GPS block emptied, and whether it had one (P75). A phone writes where a photo
    was taken into it — all five of irrigation's did — and a person photographing a module at home
    for /spark:identify must not publish their address by committing the file. Emptied in place:
    every GPS value zeroed and the block's entry count set to 0, so nothing else in the file moves.
    """
    start = payload.find(b"Exif\x00\x00")
    if not payload.startswith(b"\xff\xd8") or start < 0:
        return payload, False
    data, tiff = bytearray(payload), start + 6
    order = "<" if data[tiff:tiff + 2] == b"II" else ">"

    def read(fmt, at):
        return struct.unpack_from(order + fmt, data, tiff + at)

    def zero(at, size):
        if tiff + at + size > len(data):
            raise struct.error("a value past the end of the file")
        data[tiff + at:tiff + at + size] = bytes(size)

    try:
        first = read("I", 4)[0]
        pointers = [read("I", first + 10 + 12 * i)[0] for i in range(read("H", first)[0])
                    if read("H", first + 2 + 12 * i)[0] == GPS_BLOCK_TAG]
        if not pointers:
            return payload, False
        block, entries = pointers[0], read("H", pointers[0])[0]
        for i in range(entries):
            _, kind, count, offset = read("HHII", block + 2 + 12 * i)
            if EXIF_TYPE_BYTES.get(kind, 1) * count > 4:
                zero(offset, EXIF_TYPE_BYTES.get(kind, 1) * count)
        zero(block, 2 + 12 * entries + 4)
    except struct.error:
        return payload, False
    return bytes(data), True


def keep_in_store(payload, name, dry_run=False):
    """
    Put a file in the store under its checksum, checked (§6.2), and return the checksum (P62a) — a photo without its
    location (P75). A dry run asks the name rule the real run enforces, so it refuses what the real run would refuse.
    """
    if name.lower().endswith((".jpg", ".jpeg")):
        payload = without_location(payload)[0]
    if not dry_run:
        return store.keep(payload, name)
    problem = store.file_name_problem(name)
    if problem:
        raise store.StoreProblem("%s", problem, code=records_codes.FILE_NAME_REFUSED)
    return hashlib.sha256(payload).hexdigest()


#: The unit a fact's name ends in, as a datasheet prints it.
UNIT_PRINTED = {"_v": r"(?<![A-Za-z])V(?![A-Za-z])", "_mv": r"mV", "_a": r"(?<![A-Za-z])A(?![A-Za-z])",
                "_ma": r"mA", "_ua": r"(µA|uA)", "_nm": r"nm", "_deg": r"(°|deg)", "_mm": r"mm",
                "_ohms": r"(Ω|ohm|k)", "_hz": r"[kM]?Hz", "_c": r"°C", "_mw": r"mW"}
#: What a datasheet calls a fact spark names its own way; the name's own words are always tried too.
DATASHEET_SAYS = {"max_continuous_current": ["dc forward current", "continuous current"],
                  "forward_voltage": ["forward voltage"], "forward_voltage_max": ["forward voltage"],
                  "peak_wavelength": ["peak wavelength", "wavelength at peak", "λpeak"], "viewing_angle": ["viewing angle"],
                  "deep_sleep_current": ["deep-sleep", "deep sleep"], "supply_voltage": ["supply voltage"]}
TABLE_ROW = re.compile(r"\S\s{3,}\S.*\S\s{3,}\S")
STANDALONE_NUMBER = re.compile(r"(?<![\w.=])\d+(\.\d+)?(?![\w.])")
#: A fact's status in a datasheet scan, as `--scan` prints it.
FOUND, LABEL_ONLY, NOT_FOUND = "FOUND", "LABEL ONLY", "NOT FOUND"
SECTION = re.compile(r"^\s*(Table\s+\d+.*|[A-Z]{2,}[A-Z0-9 /&,\-]{4,}.*|\d+(\.\d+)+\s+[A-Z].{3,60})$")


def scan_datasheet(pages, wanted, labels=None):
    """
    Each wanted fact's lines in a datasheet, read page by page and STOPPED on the page where every fact is FOUND (P80):
    a run that printed a whole datasheet paid for it on every later turn, while the facts sat on one page. FOUND is a
    table row with the label, a standalone number, and the unit on the row or in a column header above; a prose bullet
    never is — the S3 overview's "7 uA" taken for the table is the P63 misreading. LABEL ONLY shows the next two lines;
    NOT FOUND names the words tried. `pages` yields (number, text); `labels` adds words per fact.
    """
    plan = {}
    for fact in wanted:
        suffix = next((end for end in sorted(UNIT_PRINTED, key=len, reverse=True) if fact.endswith(end)), "")
        stem = fact[:-len(suffix)] if suffix else fact
        words = list(dict.fromkeys(DATASHEET_SAYS.get(stem, []) + [stem.replace("_", " ")] + list((labels or {}).get(fact, []))))
        plan[fact] = (words, re.compile(UNIT_PRINTED[suffix]) if suffix else None)
    found = {fact: {"status": NOT_FOUND, "hits": [], "tried": words} for fact, (words, _) in plan.items()}
    for number, text in pages:
        lines, section = text.splitlines(), None
        for index, line in enumerate(lines, 1):
            # A heading names a table or a section; a table row that happens to start in capitals does not.
            section = line.strip() if SECTION.match(line) and not TABLE_ROW.search(line) else section
            for fact, (words, unit) in plan.items():
                if not any(word in line.lower() for word in words):
                    continue
                above = "\n".join(lines[max(0, index - 21):index - 1])
                has_unit = unit is None or unit.search(line) or re.search(r"\(\s*" + unit.pattern + r"\s*\)", above)
                if TABLE_ROW.search(line) and STANDALONE_NUMBER.search(line) and has_unit:
                    entry = found[fact]
                    if entry["status"] != FOUND:
                        entry["status"], entry["hits"] = FOUND, []
                    entry["hits"].append((number, index, section, re.sub(r"\s{3,}", " | ", line.strip())))
                elif found[fact]["status"] == NOT_FOUND:
                    # A wrapped cell puts a row's label between its values: show the line above too.
                    above_line = [previous.strip() for previous in lines[max(0, index - 3):index - 1] if previous.strip()][-1:]
                    below = [following.strip() for following in lines[index:index + 6] if following.strip()][:2]
                    found[fact] = dict(found[fact], status=LABEL_ONLY,
                                       hits=[(number, index, section, " // ".join(above_line + [line.strip()] + below))])
        if all(entry["status"] == FOUND for entry in found.values()):
            break
    return found


def datasheet_pages(path, command):
    """(number, text) per page of a PDF, as the pdf-text tool lays it out — one page at a time, on demand."""
    import subprocess
    number = 1
    while True:
        done = subprocess.run(list(command) + ["-layout", "-f", str(number), "-l", str(number), str(path), "-"],
                              capture_output=True, text=True)
        if done.returncode != 0:
            return
        yield number, done.stdout
        number += 1


def read_datasheet(path, wanted, labels=None, project=None):
    """What `scan_datasheet` found, with the pages read, as an Answer: a fact not on a table row is a problem."""
    from spark.records import tool_finder
    try:
        reader = tool_finder.find("pdf-text", project)
    except tool_finder.ToolProblem as missing:
        return Answer(unchecked=[_cannot("--read: %s" % missing)])
    read = []
    def counted():
        for one in datasheet_pages(path, reader.command):
            read.append(one[0])
            yield one
    found = scan_datasheet(counted(), wanted, labels)
    lines = []
    for fact, entry in found.items():
        if entry["status"] == NOT_FOUND:
            lines.append("%-28s NOT FOUND — tried: %s" % (fact, ", ".join(entry["tried"])))
        for number, line, section, text in entry["hits"][:3]:
            lines.append("%-28s %-10s p%d:%d  [%s]  %s" % (fact, entry["status"], number, line, section or "no heading", text[:220]))
    missing = [fact for fact, entry in found.items() if entry["status"] != FOUND]
    lines.append("read %d of the document's pages, %s" % (len(read), "stopping where the last fact was found" if not missing
                 else "%d fact(s) not on a table row: read those pages as images" % len(missing)))
    return Answer({"facts": found, "pages_read": read}, lines,
                  problems=[_problem(fact, "not on a table row: read its pages as images") for fact in missing])


def keep_local(path, url=None, dry_run=False):
    """
    Put a file you already have into the store and return the `documents` entry that points at it
    (P62b). The WROOM-1 v1.1 datasheet exists only as a kept file — its URL now serves v1.8 — so
    fetching can never bring it in; an import can. `url` is where it came from, if anyone knows.
    """
    path = Path(path)
    return {"url": url, "sha256": keep_in_store(path.read_bytes(), path.name, dry_run), "file": path.name,
            "retrieved": datetime.date.today().isoformat(), "title": None, "version": None}


def records_with_documents(project=None):
    """(owner id, record) for every record that can point at a document: parts, catalog, boards."""
    paths = [path for _, path in store.records("parts", record_kind.LIBRARY, project, drafts=True).values()]
    paths += [path for _, path in board_records.records(project).values()]
    for path in paths:
        record = _parse(path)
        if isinstance(record, dict) and record.get("documents"):
            yield path.stem, record


def citing(record, keys, url, where=""):
    """
    (field, locator) for every object in the record that rests on this document: by one of `keys` —
    the names THIS record gives the same file — or by its URL. A record that does not hold the file
    has no key for it, and an object with no `cites` names no document, so neither can match.
    """
    found = []
    for name, value in (record.items() if isinstance(record, dict) else []):
        here = "%s.%s" % (where, name) if where else name
        if not isinstance(value, dict):
            continue
        cited = (value.get("cites") or {}).get("document")
        if cited is not None and cited in keys:
            found.append((here, value["cites"].get("at") or "no page given"))
        elif url and isinstance(value.get("source"), str) and url in value["source"]:
            found.append((here, "cites its URL"))
        else:
            found += citing(value, keys, url, here)
    return found


def find_kept(words, project=None):
    """
    Every kept document matching every word — where it is in the store, present or MISSING, and
    each fact that rests on it — read from the records alone: no network (P62b). A researcher runs
    this BEFORE fetching: one fetch in five repeated one already made (P61).
    """
    kept = store.place("sources")
    wanted = [word.lower() for word in words]
    lines = []
    for owner, record in records_with_documents(project):
        for key, entry in record["documents"].items():
            said = " ".join(str(part) for part in (owner, key, entry.get("file"), entry.get("title"),
                                                   entry.get("url"), entry.get("version"))).lower()
            if not all(word in said for word in wanted):
                continue
            path = kept / str(entry.get("sha256")) / str(entry.get("file"))
            lines.append("%s %s: %s %s" % (owner, key, entry.get("title") or entry.get("file"),
                                           entry.get("version") or "(version not read)"))
            lines.append("    %s  %s" % (path, "present" if path.is_file() else "MISSING"))
            for other, other_record in records_with_documents(project):
                same_file = {name for name, held in other_record["documents"].items()
                             if isinstance(held, dict) and held.get("sha256") == entry.get("sha256")}
                for field, locator in citing(other_record, same_file, entry.get("url")):
                    lines.append("    cited by %s %s — %s" % (other, field, locator))
    # The store itself: a file another project kept, or an interrupted run left, is still kept (P80).
    cited = {str(entry.get("sha256")) for _, record in records_with_documents(project)
             for entry in record["documents"].values() if isinstance(entry, dict)}
    for path in sorted(kept.glob("*/*")) if kept.is_dir() else []:
        if path.parent.name not in cited and all(word in path.name.lower() for word in wanted):
            lines.append("%s: kept; no record here cites it" % path.name)
            lines.append("    %s  present" % path)
    return lines


def document_key(name, taken):
    """A short, unique name for a document in a record: its file name's stem, made plain."""
    stem = re.sub(r"[^a-z0-9]+", "-", name.rsplit(".", 1)[0].lower()).strip("-") or "document"
    key, number = stem, 2
    while key in taken:
        key, number = "%s-%d" % (stem, number), number + 1
    return key


def to_fetch(record):
    """The cited datasheet and image URLs a record does not keep yet — what `--fetch` would download."""
    known = {entry.get("url") for entry in (record.get("documents") or {}).values()}
    return [url for url in cited_urls(record) if url.split("?")[0].lower().endswith(KEEPABLE) and url not in known]


def document_name(url):
    """The file name a cited URL is kept under: the last segment of its path, decoded — never its query."""
    return urllib.parse.unquote(url.split("?")[0].rsplit("/", 1)[-1]) or "document"


def fetch_plan(record):
    """
    [(url, file name)] for every document `--fetch` would keep, or a StoreProblem naming the first one the store would
    refuse by name. All or nothing (§6.4): the names come from the URLs, so every one is known before any download, and a
    refusal stops the whole fetch — not halfway, with the documents before it kept and no record pointing at them.
    `store.keep` still refuses such a name itself, as the last line of defence.
    """
    plan = [(url, document_name(url)) for url in to_fetch(record)]
    for url, name in plan:
        problem = store.file_name_problem(name)
        if problem:
            raise store.StoreProblem("%s: %s — nothing was fetched", url, problem, code=records_codes.FILE_NAME_REFUSED)
    return plan


def fetch_documents(part_id, project=None, fetch=None):
    """
    Download every cited datasheet or image into the store and point at each from the record's `documents`: its URL,
    checksum, file name and the date it was fetched — `title` and `version` stay null until someone reads them, because
    a version is what the document PRINTS, not a guess (P61). A document the store would refuse by name stops the whole
    fetch before any download (`fetch_plan`). `fetch(url) -> bytes or None` is a parameter for the tests.
    """
    home = record_home(part_id, project)
    if home is None:
        raise PartError("no record called %r to fetch for", part_id, code=sourcing_codes.NO_SUCH_PART)
    path = home / (part_id + DEFINITION_SUFFIX)
    record = json.loads(path.read_text())
    documents = dict(record.get("documents") or {})
    for url, name in fetch_plan(record):
        payload = (fetch or _download)(url)
        if payload is not None:
            documents[document_key(name, documents)] = {
                "url": url, "sha256": keep_in_store(payload, name), "file": name,
                "retrieved": datetime.date.today().isoformat(), "title": None, "version": None}
    record["documents"] = documents
    _write_record(path, record)
    return documents


def _download(url):
    """One cited document through spark's one door to the network (§6.5) — None when it does not answer, so it is not kept."""
    try:
        return store.fetch(url)
    except store.StoreProblem:
        return None


def sellers(project=None):
    """
    Where the person buys, local first, from the project's brief — or nothing, which the
    researcher reports as "no sellers named" rather than choosing a shop for them.
    """
    return Brief.from_project(project).sellers or ()


def need(words, project=None, matcher=None):
    """
    The records matching every word — in id, name, kind or an alias — so what exists is known
    before anything is researched. Backlog R11: the RC car wrote three records by hand because
    nothing looked, and "nothing looked" was the first gap its diary named (G1).
    """
    from spark.sourcing import matching
    loaded, offers = {}, []
    for part_id in available(project):
        try:
            loaded[part_id] = load(part_id, project)
        except PartError:
            # A record still being filled in — research writes a skeleton first — must not stop
            # the search for everyone: `--need` died on a researcher's draft while five ran (I3).
            # Named as a draft, matched by its id alone, never returned as usable.
            loaded[part_id] = None
        offers.append(matching.Offer.from_record(part_id, "part", loaded[part_id] or {}))
    fits = _found(words, offers, matcher)
    return ([dict(loaded[fit.offer.key], id=fit.offer.key) for fit in fits if loaded[fit.offer.key] is not None],
            [fit.offer.key for fit in fits if loaded[fit.offer.key] is None])


def cited_urls(record):
    """
    Every http(s) URL the record cites: in its `sources` — a list, or a dict of them, as four library records keep it —
    and in each fact's own source, wherever in the sentence it sits. Read only as a list of strings that START with
    http, this saw no URL at all in any of the eight library and board records (both P62 lenses, 2026-10-02).
    """
    sources = record.get("sources") or []
    texts = list(sources.values()) if isinstance(sources, dict) else list(sources)
    texts += [fact.get("source") for fact in (record.get("facts") or {}).values() if isinstance(fact, dict)]
    urls = [url for text in texts if isinstance(text, str) for url in URL.findall(text)]
    return list(dict.fromkeys(_url_in_prose(url) for url in urls))


def reachable(url):
    """Whether a URL answers at all, asked through spark's one door (§6.5). A hallucinated source is the one lie research tells easily."""
    try:
        store.fetch(url, method="HEAD")
    except store.StoreProblem:
        return False
    return True


def sources_resolve(record, fetch=reachable):
    """(url, reachable) for every cited URL. `fetch` is a parameter so a test needs no network."""
    return [(url, fetch(url)) for url in cited_urls(record)]


#: Every operation parts.py offers — the ONE table the argument parser and `--describe` are built from, so what an
#: agent reads about an operation cannot drift from what runs (§6.4.3). A row: the flag, its argparse keywords,
#: what it answers, its effects (`writes`, `network`, `deletes`), the keys of its `data`. An operation with an
#: effect takes --dry-run (§6.4.5).
OPERATIONS = (
    ("list", {"action": "store_true"}, "every record a project can build with, and where it comes from", (), ("parts",)),
    ("show", {"metavar": "PART"}, "one record, wherever it lives, and its CONFLICT lines: on verified facts a problem "
     "(exit 1), on unverified ones an assumption", (), ("record",)),
    ("validate", {"action": "store_true"}, "every record a project can build with, against the contract", (), ("checked",)),
    ("signals", {"nargs": "+", "metavar": "PART"}, "the signals these parts ask for, as assign_pins.py input", (), ("signals",)),
    ("unverified", {"nargs": "+", "metavar": "PART"}, "what nobody has checked about these parts, one assumption a fact",
     (), ("parts",)),
    ("need", {"nargs": "+", "metavar": "WORD"}, "what exists for a need, before researching: words matched in id, name, kind, alias; "
     "--matcher picks the matcher", (), ("need", "vendor_order", "found", "drafts", "catalog")),
    ("skeleton", {"metavar": "PART"}, "write a record to fill in, to the project's parts/", ("writes",), ("path", "record", "written")),
    ("sources", {"metavar": "PART"}, "ask every URL a record cites whether it answers", ("network",), ("part", "sources")),
    ("fetch", {"metavar": "PART"}, "download the datasheets and images a record cites, into your store", ("network", "writes"),
     ("documents", "would_fetch")),
    ("keep", {"metavar": "FILE"}, "put a file you already have into your store; answers its documents entry", ("writes",),
     ("document", "location_removed", "written")),
    ("read", {"metavar": "PDF"}, "read a datasheet page by page and stop where every --want fact is on a table row", (),
     ("facts", "pages_read")),
    ("kept", {"nargs": "+", "metavar": "WORD"}, "find a kept document by every word, with no network, and every fact resting on it",
     (), ("found",)),
    ("promote", {"metavar": "PART"}, "catalog → the project's parts/, or the project's parts/ → the plugin's library", ("writes",),
     ("path", "written")),
    ("catalog", {"action": "store_true"}, "every record research has kept, chosen or not", (), ("records", "broken")),
    ("drawer", {"action": "store_true"}, "what you own: label, count, the record it is, unsure, skip — 20 at a time", (),
     ("entries",)),
    ("drawer-set", {"metavar": "FILE"}, "set drawer entries from a JSON list in FILE (- for stdin): every write sets, never adds; with --project, an `is` may "
     "name a record in that project, such as one /spark:research just wrote; an entry may also say its about, description and tags",
     ("writes",), ("changes", "questions", "shelved")),
    ("drawer-import", {"nargs": 2, "metavar": ("SOURCE", "FILE")},
     "apply an importer's payload (FILE, or - for stdin) to the drawer: new entries, and counts by the re-import rule",
     ("writes",), ("changes", "questions", "shelved", "smaller")),
    ("function-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "set what a part does — a JSON [{does, what}] in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written", "shelf_copy")),
    ("fact-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "fill what a record owes — a JSON object of the facts the chain reads, or `facts` entries {value, verified, source} by name (a bench result is verified true and its source says who, when and how; a text in it has its control characters turned into a space and is cut at 1000 characters, and a key with a control character is refused), or its about, description and tags, or a board's onboard LED or button level, `pin_roles` {onboard_led|onboard_button: {active_level: {value, verified, source}}} (a board of the project's own, merged role by role), in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written", "shelf_copy")),
    ("audit", {"action": "store_true"}, "every record in every layer and every drawer link: what owes facts, what is broken",
     (), ("layers", "owed", "broken", "no_function", "dangling", "stops_at_footprint")),
    ("needs", {"metavar": "PROJECT"}, "a project's needs: what each does, its condition, its mark", (), ("needs",)),
    ("needs-set", {"nargs": 2, "metavar": ("PROJECT", "FILE")},
     "set a project's needs from a JSON list in FILE (- for stdin): every write sets, never adds", ("writes",),
     ("changes", "written")),
    ("match", {"metavar": "PROJECT"}, "each of a project's needs with the store's candidates: owned first, what each owes, "
     "each with its score and why; --matcher picks the matcher that ranks them; a board that serves a need through its own "
     "LED, button or display has `limits`, the sentences for what a passed run does not test of it", (), ("needs",)),
    ("offer", {"metavar": "KEY"}, "what one offer says of itself, for the chooser to read: a record's id or a drawer entry's "
     "key — about, description, tags, what it does, its names, power and size. --project reads the project's own records", (),
     ("offer",)),
    ("pick", {"nargs": "+", "metavar": ("PROJECT", "NEED=ID")},
     "set what each need picks (NEED=ID: a record, or a drawer entry) and reserve what you own of it — never past what another project holds; "
     "what it notes is under `notes`: a board given a need that its own part serves says what a run does not test of the part, "
     "and the other choice",
     ("writes",), ("project", "picks", "reserved", "released", "written")),
    ("needs-drop", {"nargs": 2, "metavar": ("PROJECT", "NEED")},
     "drop a need and its pick from .spark/needs.json and release only the holds of the dropped pick (every other hold stays); --dry-run "
     "says what it would do; history stays, and requirements.json is not changed: a note says when it still lists the part",
     ("writes",), ("project", "need", "dropped", "released", "written")),
    ("requirements", {"metavar": "PROJECT"},
     "the picks as the project's requirements.json: the board, and every part pick with a record — one that owes only its outline is written with a warning, one that owes more is refused; a catalog one goes onto the shelf; what the file already holds stays; board_only when the board itself serves every need",
     ("writes",), ("path", "requirements", "shelved", "unplaced", "kept", "board_was", "placeholder_outline", "unserved", "no_supply",
                   "no_driver", "no_receiver", "written")),
    ("step", {"nargs": 2, "metavar": ("PROJECT", "STEP")},
     "a spine step of a project starts now, in this Claude Code session — the cost line counts its transcript from here",
     ("writes",), ("step", "written")),
    ("tally", {"metavar": "PROJECT"},
     "the cost line: the picks, how many came from the store (known to spark before the project: its library, your store, your projects) and how many you own, and what the project's steps cost",
     (), ("picks", "from_store", "owned", "cost", "built", "line", "needs", "needs_picked")),
    ("describe", {"action": "store_true"}, "every operation, its arguments, effects and output — this list", (),
     ("operations", "options", "exits")),
)

def _not_negative(text):
    """An argparse type: a whole number from 0 up — a listing cannot start before its first item."""
    if int(text) < 0:
        raise argparse.ArgumentTypeError("%s is below 0" % text)
    return int(text)


#: The options an operation reads, in the same columns but effects.
OPTIONS = (
    ("kind", {}, "with --skeleton: the part's kind (motor-driver, sensor, regulator, …)"),
    ("vendor", {}, "with --skeleton: who makes it"),
    ("url", {}, "with --keep: where the file came from, if anyone knows"),
    ("want", {"nargs": "+", "metavar": "FACT"}, "with --read: the facts to find, named as records name them (forward_voltage_v …)"),
    ("label", {"action": "append", "metavar": "FACT=WORD|WORD"}, "with --read: extra words a datasheet uses for a fact"),
    ("passed-over", {"metavar": "FILE"}, "with --pick: the parts passed over and why, a JSON list in FILE (- for stdin) of {need, id, why, by}"),
    ("matcher", {"metavar": "NAME"}, "with --match or --need: the matcher that ranks the offers; a name that does not fit "
     "is refused with the names that do"),
    ("project", {"type": Path}, "a project whose own parts/ beats the shipped library"),
    ("from", {"type": _not_negative, "default": 0, "dest": "start", "metavar": "N"}, "with a listing: start at item N (truncated.next says where)"),
    ("dry-run", {"action": "store_true"}, "with an operation that has an effect: say what it would do, and do nothing"),
    ("json", {"action": "store_true"}, "answer in one envelope: problems, unchecked, notes, assumptions, next "
     "(docs/guide/agents/json.md, \"parts.py's envelope\")"),
)


def _parser():
    """The argument parser, built from OPERATIONS and OPTIONS so that `--describe` cannot drift from it."""
    parser = AnsweringParser(prog="parts.py", description="What a part needs, and what is known about it.")
    what = parser.add_mutually_exclusive_group(required=True)
    for name, keywords, summary, _, _ in OPERATIONS:
        what.add_argument("--" + name, help=summary, **keywords)
    for name, keywords, summary in OPTIONS:
        parser.add_argument("--" + name, help=summary, **keywords)
    return parser


def _op_list(args, project):
    listing = []
    for part_id, (layer, path) in store.records("parts", record_kind.LIBRARY, project).items():
        record = load(part_id, project)
        listing.append({"id": part_id, "kind": record["kind"], "name": record["name"], "layer": layer, "from": str(path.parent)})
    shown, truncated = store.page_with_store(listing, args.start, "list", ["--list"] + _with_project(project))
    lines = [_row(p["id"], p["kind"], "%-9s %s" % (p["layer"], p["name"])) for p in listing]
    return Answer({"parts": shown}, lines, truncated=truncated)


def _op_show(args, project):
    """The record, and each CONFLICT it holds: a problem on verified facts, an assumption on unverified ones (P124)."""
    part, problems, assumptions = any_record(args.show, project), [], []
    for conflict in conflicts_of(part):
        where = "%s.%s" % (args.show, conflict["pin"])  # the part and the pin the CONFLICT is about
        if conflict["rests_on"]:
            assumptions.append({"fact": where, "basis": "unmeasured", "rests_on": conflict["rests_on"],
                                "sentence": "CONFLICT: " + conflict["line"], "upgrade": conflict["upgrade"]})
        else:
            problems.append(_problem(where, "CONFLICT: " + conflict["line"], conflict["fix"]))
    return Answer({"record": part}, [describe(part)], problems=problems, assumptions=assumptions)


def _op_validate(args, project):
    checked = []
    for part_id in available(project):
        path = definition_path(part_id, project)
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError as bad:
            return Answer(unchecked=[_cannot("--validate: %s is not JSON: %s" % (path, bad))])
        checked.append({"part": part_id, "path": str(path), "problems": validate(record, path)})
    shown, truncated = store.page_with_store(checked, args.start, "validate", ["--validate"] + _with_project(project))
    lines = []
    for one in checked:
        lines.append("  %-28s %s" % (one["part"], "ok" if not one["problems"] else "%d problem(s)" % len(one["problems"])))
        lines += ["      - %s" % problem for problem in one["problems"]]
    return Answer({"checked": shown}, lines, truncated=truncated,
                  problems=[_problem(one["part"], problem) for one in checked for problem in one["problems"]])


def _op_signals(args, project):
    found = {"signals": signals_for(args.signals, project)}
    return Answer(found, [json.dumps(found, indent=2)])


def _op_unverified(args, project):
    questions = unverified(args.unverified, project)
    lines = ["  everything these parts claim has been checked."] if not questions else \
        ["  %d thing(s) nobody has checked:\n" % len(questions)]
    for question in questions:
        lines.append("  %s.%s = %s" % (question["part"], question["fact"], question["assumed"]))
        if question["why_it_matters"]:
            lines.append("      %s" % question["why_it_matters"])
    assumptions = [{"fact": "%s.%s" % (q["part"], q["fact"]), "basis": "unverified", "assumed": q["assumed"],
                    "sentence": q["why_it_matters"], "source": q["source"], "write": q["write"]} for q in questions]
    owners = [q["part"] for q in questions if q["write"]]  # a row with no `write` cannot go back by --fact-set
    follow = [add_env(next_step("fact-set", ["--fact-set", owners[0], "<file>"], WRITE_BACK_HINT, ["writes"]), store.read_given_env())] if owners else []
    return Answer({"parts": list(args.unverified)}, lines, assumptions=assumptions, next=follow)


def _brief(part):
    return {"id": part["id"], "kind": part["kind"], "name": part["name"]}


def _op_need(args, project):
    from spark.sourcing import matching
    try:
        chosen = matching.matcher(args.matcher or NEED_MATCHER, "need")
    except matching.UnknownMatcher as wrong:
        return Answer(unchecked=[_cannot(str(wrong))])
    found, drafts = need(args.need, project, chosen)
    known = [p for p in catalog_matches(args.need, chosen) if p["id"] not in drafts and p["id"] not in {q["id"] for q in found}]
    data = {"need": args.need, "vendor_order": list(vendor_order(project)), "found": [_brief(p) for p in found],
            "drafts": drafts, "catalog": [_brief(p) for p in known]}
    lines = [_row(p["id"], p["kind"], p["name"]) for p in found]
    lines += [_row(part_id, "(draft)", "does not yet meet the contract — being filled in") for part_id in drafts]
    lines += [_row(p["id"], p["kind"], "%s  [catalog: researched before; `--promote %s --project .` builds with it]"
                   % (p["name"], p["id"])) for p in known]
    if not lines:
        lines = ["  nothing in the library matches %r.\n  Research it: /spark:research \"%s\"  — vendors in order: %s; sellers: %s"
                 % (" ".join(args.need), " ".join(args.need), ", ".join(vendor_order(project)),
                    ", ".join(sellers(project)) or "none named in the brief")]
    return Answer(data, lines)


def _op_skeleton(args, project):
    if not project or not args.kind:
        return Answer(unchecked=[_cannot("--skeleton needs --project (the record belongs to a project's parts/) and --kind")])
    if not store.PLAIN.fullmatch(args.skeleton):  # P87: a file every reader would refuse is never written
        return Answer(problems=[_problem(args.skeleton, NOT_A_PLAIN_ID % args.skeleton)])
    target = project / "parts" / (args.skeleton + DEFINITION_SUFFIX)
    if target.exists():
        return Answer(problems=[_problem(args.skeleton, "%s exists; fill it in, do not overwrite it" % target)])
    record = skeleton(args.skeleton, args.kind, args.vendor)
    if not args.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return Answer({"path": str(target), "record": record, "written": not args.dry_run},
                  ["  %s %s — every null is a fact to record; `parts.py --validate --project .` says what is missing"
                   % ("would write" if args.dry_run else "wrote", target)])


def _op_sources(args, project):
    record = any_record(args.sources, project)
    if args.dry_run:
        urls = cited_urls(record)
        return Answer({"part": args.sources, "sources": [{"url": url, "reachable": None} for url in urls]},
                      ["  would ask %s" % url for url in urls])
    answers = sources_resolve(record)
    lines = ["  %s  %s" % ("ok  " if ok else "NO  ", url) for url, ok in answers] or \
        ["  %s cites no URL — every fact rests on prose sources a person has to find" % args.sources]
    return Answer({"part": args.sources, "sources": [{"url": url, "reachable": ok} for url, ok in answers]}, lines,
                  problems=[_problem(url, "does not answer") for url, ok in answers if not ok])


def _op_fetch(args, project):
    if args.dry_run:
        home = record_home(args.fetch, project)
        if home is None:
            raise PartError("no record called %r to fetch for", args.fetch, code=sourcing_codes.NO_SUCH_PART)
        wanted = [url for url, _ in fetch_plan(json.loads((home / (args.fetch + DEFINITION_SUFFIX)).read_text()))]
        return Answer({"documents": None, "would_fetch": wanted}, ["  would fetch %s" % url for url in wanted]
                      or ["  %s cites no datasheet or image URL to keep" % args.fetch])
    kept = fetch_documents(args.fetch, project)
    lines = ["  %s/%s  <-  %s" % (entry["sha256"][:12], entry["file"], entry["url"]) for entry in kept.values()]
    return Answer({"documents": kept, "would_fetch": []}, lines or ["  %s cites no datasheet or image URL to keep" % args.fetch])


def _op_keep(args, project):
    path = Path(args.keep)
    if not path.is_file():
        return Answer(unchecked=[_cannot("--keep: no file at %s" % path)])
    located = path.name.lower().endswith((".jpg", ".jpeg")) and without_location(path.read_bytes())[1]
    said = (["  removed the location (EXIF GPS) from %s before keeping it" % printable(path.name)]
            if located and not args.json else ())
    try:  # P423: a store that refuses the file, or cannot be written, refuses it after the line was said
        entry = keep_local(path, args.url, dry_run=args.dry_run)
    except store.StoreProblem as refused:
        return Answer(unchecked=[_cannot(str(refused))], diagnostics=said)
    except OSError as unwritable:
        return Answer(unchecked=[_cannot("--keep: %s" % unwritable)], diagnostics=said)
    return Answer({"document": entry, "location_removed": located, "written": not args.dry_run},
                  [json.dumps(entry, indent=2, ensure_ascii=False)], diagnostics=said)


def _op_read(args, project):
    labels = {}
    for given in args.label or []:
        fact, _, words = given.partition("=")
        labels[fact] = [word.strip().lower() for word in words.split("|") if word.strip()]
    return read_datasheet(args.read, args.want or [], labels, project)


def _op_kept(args, project):
    found = find_kept(args.kept, project)
    return Answer({"found": found}, found or ["nothing kept matches %s — fetch it, or --keep a file you have" % " ".join(args.kept)])


def _op_promote(args, project):
    if not project:
        return Answer(unchecked=[_cannot("--promote needs --project")])
    target = promote(args.promote, project, dry_run=args.dry_run)
    return Answer({"path": str(target), "written": not args.dry_run},
                  ["  %s %s" % ("would promote to" if args.dry_run else "promoted to", target)])


def _read_json_input(name):
    """A payload from a file, or from stdin for '-' — the way labels and names travel, never argv (§6.4.2). A refusal
    with the code `input_unreadable` when it is not readable JSON, which `main` answers as could-not-run."""
    try:
        return json.loads(sys.stdin.read() if name == "-" else Path(name).read_text())
    except (OSError, ValueError) as broken:
        raise CodedMessageError("%s is not readable JSON: %s", "stdin" if name == "-" else name, broken,
                                code=sourcing_codes.INPUT_UNREADABLE) from None


def _change_line(change, dry_run):
    """
    One set-only write's change (§5.2), the drawer's and the needs file's alike: '  new soil-probe: soil probe × 8 — is
    part sen0193-soil-moisture' for a new drawer entry (× ? when its count was left out), else '  set soil: mark null →
    "have"', every value from what it was. A new entry's key and label pass `printable` here, because a newline in them
    would start a line. A set line's values are JSON, which escapes a newline, and `_say` guards the rest.
    """
    if change["new"] and "entry" in change:
        now, linked = change["now"], change["now"].get("is")
        return printable("  %s %s: %s × %s%s" % ("would add" if dry_run else "new", change["entry"], now.get("label"), now.get("count", "?"),
                                                " — is %s %s" % next(iter(linked.items())) if linked else ""))
    return "  %s %s: %s" % ("would set" if dry_run else "set", change.get("entry") or change.get("need"), "; ".join(
        "%s %s → %s" % (key, json.dumps(change["was"].get(key), ensure_ascii=False), json.dumps(value, ensure_ascii=False))
        for key, value in change["now"].items()))


def _write_lines(changes, problems, dry_run, said=()):
    """
    What a set-only write did or would do (§5.2), said one way for the drawer and the needs file: each change — marked
    `not written:` when anything was refused, because then nothing is written — what else the write has to say, then each refusal; or
    that nothing changes.
    """
    lines = [("  not written: " + _change_line(change, False).strip()) if problems else _change_line(change, dry_run)
             for change in changes] + list(said)
    lines += ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]
    return lines or ["  nothing to change"]


def _drawer_answer(changes, questions, problems, dry_run):
    """What a drawer write did or would do (§5.2): all of it, or — when anything is refused — none of it."""
    import drawer
    if not problems and not dry_run:
        drawer.apply(changes)
    made = [change for change in changes if change["now"]]
    wanted = [change["shelve"] for change in made if change["shelve"]]
    shelved = [Path(path).stem for path, project in wanted if shelvable(path, project)]
    left = [Path(path).stem for path, project in wanted if not shelvable(path, project)]
    said = ["  ? %s" % q["sentence"] for q in questions] + [
        "  %s %s on your shelf, so every project finds it%s" % (
            "would put" if dry_run or problems else "put", Path(path).stem,
            "" if project else ". Its folder is on no list, so a later change to the record there does not reach this copy")
        for path, project in wanted if shelvable(path, project)] + [
        "  not shelved: %s — it does not meet the part contract yet, so it stays in its project and the entry still links to it"
        % stem for stem in left]
    return Answer({"changes": [{key: change[key] for key in ("entry", "new", "was", "now")} for change in made],
                   "questions": questions, "shelved": shelved, "not_shelved": left, "written": not (problems or dry_run)},
                  _write_lines(made, problems, dry_run, said), problems=problems)


def _op_drawer(args, project):
    import drawer
    entries = drawer.listing()
    shown, truncated = store.page_with_store(entries, args.start, "drawer", ["--drawer"])
    lines = ["  %-44s %6s  %-38s %s" % (str(e["label"])[:44], "?" if e["count"] is None else e["count"],
                                         "%s %s" % next(iter(e["is"].items())) if e["is"] else "—",
                                         "  ".join(filter(None, ["maybe owned — check the drawer" if e["unsure"] else ("skip: %s" % e["skip"] if e["skip"] else ""),
                                                               "held by " + ", ".join(map(printable, e["held_by"])) if e["held_by"] else ""])))
             for e in entries]
    lines.append("  %d entr%s" % (len(entries), "y" if len(entries) == 1 else "ies"))
    return Answer({"entries": shown}, lines, truncated=truncated)


def _op_drawer_set(args, project):
    import drawer
    items = _read_json_input(args.drawer_set)
    return _drawer_answer(*drawer.plan_set(items, project), args.dry_run)


def _op_drawer_import(args, project):
    import drawer
    source, name = args.drawer_import
    payload = _read_json_input(name)
    changes, questions, problems, smaller = drawer.plan_import(source, payload)
    answer = _drawer_answer(changes, questions, problems, args.dry_run)
    if not problems and not args.dry_run:
        store.write_json("drawer-import", store.slug(source), drawer.kept_payload(payload))
    return answer._replace(data=dict(answer.data, smaller=smaller), lines=list(answer.lines) + ["  %s" % s for s in smaller])


def _shelved_from(path):
    """The project a shelf copy says it was shelved from (its `based_on`, §5.5) — None for a catalog's copy, or no copy."""
    record = _parse(path) if Path(path).is_file() else None
    based_on = record.get("based_on") if isinstance(record, dict) else None
    named = based_on.get("project") if isinstance(based_on, dict) else None
    return named if isinstance(named, str) else None


def _record_path(part_id, project, kind="part"):
    """
    A part record's own file, and the project whose shelf copy follows it (§5.4, §5.5): the nearest layer that has it, the
    catalog included, else a project on the person's list — except that a shelf copy of a listed project's record is not a
    home: that project's record is. A record found in the project given names that project too, when the shelf holds a copy
    of it shelved from there: the copy follows its record, however the record was reached. `kind` is "board" for a board's record (P464).
    """
    import drawer
    path, where = next(((path, where) for found_kind, found, where, path in drawer.linkable(project) if (found_kind, found) == (kind, part_id)),
                       (None, None))
    if path is not None and path.parent == store.place("shelf"):
        named = _shelved_from(path)
        folder = store.projects().get(named) if named else None
        home = folder / "parts" / path.name if folder is not None else None
        return (home, named) if home is not None and home.is_file() else (path, None)
    named = store.find_listed_name(project) if where == "project" else None
    return path, named if named and _shelved_from(store.place("shelf") / path.name) == named else None


def _refresh_shelf_copy(path, record, project_name, dry_run):
    """
    The shelf copy of a project's record made current again (§5.5) — after a write, and when an earlier write left it behind
    (the record filled in its project while the copy stayed, so every retry said "nothing to change") — said in words:
    current, refreshed, would refresh, or not refreshed and why: a copy that would not meet the contract is not written.
    """
    copy = _shelf_copy(path, project_name, record)
    if _parse(store.place("shelf") / path.name) == copy:
        return "current"
    wrong = validate(copy, path)
    if wrong:
        return "shelf copy not refreshed: %s" % "; ".join(wrong)
    if dry_run:
        return "would refresh the shelf copy"
    shelve(path, project_name)
    return "shelf copy refreshed"


def _set_by_name(record, values):
    """`record` with `values` set, and the values it had: `facts` takes the written names over the held ones, the other names stay (P374)."""
    after, was = dict(record, **values), {key: record.get(key) for key in values}
    if isinstance(values.get("pin_roles"), dict):  # P464: role by role, so a role keeps its gpio and note
        after["pin_roles"], was["pin_roles"] = missing_facts.merged_roles(record, values)
    if isinstance(values.get("facts"), dict):
        held = record.get("facts") if isinstance(record.get("facts"), dict) else {}
        after["facts"], was["facts"] = dict(held, **values["facts"]), {name: held.get(name) for name in values["facts"]}
    return after, was


def _set_in_home(part_id, project, values, dry_run, refuse):
    """
    Set fields of a part record in its own home (§5.4) — the catalog's, a project's, or a listed project's behind a shelf
    copy — never spark's library, which is changed in spark's repository. A shelf copy that follows the record is made
    current whether or not this write changed anything (`_refresh_shelf_copy`), and the answer says what became of it.
    `refuse(record, after, path)` says what is wrong with the result, and anything it says refuses the write.
    """
    path, source = _record_path(part_id, project, "board" if "pin_roles" in values else "part")  # P464: only a level in pin_roles reaches a board
    if path is None:
        raise PartError("no record called %r — `parts.py --need` finds what exists", part_id,
                        code=sourcing_codes.NO_SUCH_PART)
    if path.parent.resolve() in (record_kind.LIBRARY.resolve(), board_records.LIBRARY.resolve()):
        return Answer(problems=[_problem(part_id, "%s is in spark's own library, which is changed in spark's repository, "
                                                  "not by parts.py" % part_id)])
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        return Answer(problems=[_problem(part_id, "%s is not a JSON object (%s) — repair the file by hand first" % (part_id, path))])
    after, was = _set_by_name(record, values)
    wrong = refuse(record, after, path)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    changes = after != record
    if changes and not dry_run:
        _write_record(path, after)
    shelf_copy = _refresh_shelf_copy(path, after, source, dry_run) if source else None
    said = ("  %s %s (%s): %s" % ("would set" if dry_run else "set", part_id, path, "; ".join(
                "%s %s → %s" % (key, json.dumps(was[key], ensure_ascii=False), json.dumps(value, ensure_ascii=False))
                for key, value in values.items()))
            if changes else "  nothing to change: %s (%s) already says this" % (part_id, path))
    return Answer({"part": part_id, "path": str(path), "was": was, "now": values, "written": not dry_run, "shelf_copy": shelf_copy},
                  [said] + (["  " + shelf_copy] if shelf_copy not in (None, "current") else []))


def _op_function_set(args, project):
    part_id, name = args.function_set
    function = _read_json_input(name)
    answer = _set_in_home(part_id, project, {"function": function}, args.dry_run, lambda record, after, path:
                          function_problems(after) if function else ["a function is a non-empty list [{does, what}]"])
    return answer._replace(data=dict(answer.data, was=answer.data["was"]["function"], now=function)) if answer.data else answer


def _op_fact_set(args, project):
    """Fill a record's chain facts, write `facts` entries by name (a bench result and its source, P374), or set what it says of itself (about, description, tags)."""
    import drawer
    part_id, name = args.fact_set
    facts = _read_json_input(name)
    if not (isinstance(facts, dict) and facts and set(facts) <= set(CHAIN_FACTS + drawer.DESCRIBING + ("facts", "pin_roles"))):
        return Answer(problems=[_problem(part_id, "a fact write is a JSON object of facts the chain reads: %s, or `facts` entries by name; or of what a "
                                                  "record says of itself: %s" % (", ".join(CHAIN_FACTS), ", ".join(drawer.DESCRIBING)))])
    facts = {key: drawer.scrub(key, value) if key in drawer.DESCRIBING + drawer.PROVENANCE_KEYS else value for key, value in facts.items()}
    wrong = [drawer.CHECKS[key][1] for key in drawer.DESCRIBING if key in facts and not drawer.CHECKS[key][0](facts[key])] + drawer.list_provenance_key_problems(facts)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    return _set_in_home(part_id, project, facts, args.dry_run, lambda record, after, path: missing_facts.board_write_problems(record, after, path, facts, project) if "pin_roles" in facts else (
        ["%s is absent — a write fills a fact, it never empties one" % key for key in facts if _absent(key, facts[key])]
        + sorted(set(provenance.list_entry_problems(facts.get("facts"), record.get("facts"))) | set(broken_problems(after, path)) - set(broken_problems(record, path)))))


def _op_catalog(args, project):
    records, broken = catalog_records()
    listing = [{"id": part_id, "kind": record["kind"], "name": record["name"]} for part_id, record in records.items()]
    shown, truncated = store.page_with_store(listing, args.start, "catalog", ["--catalog"])
    lines = [_row(r["id"], r["kind"], r["name"]) for r in listing]
    lines += [_row(name, "BROKEN", "does not parse, or names no schema/id/name/kind") for name in broken]
    lines.append("  %d record(s), %d broken" % (len(records), len(broken)))
    return Answer({"records": shown, "broken": broken}, lines, truncated=truncated,
                  problems=[_problem(name.split(" — ")[0], "a broken catalog record: %s" % name) for name in broken])


def _op_audit(args, project):
    counts, owed, broken, silent, dangling, stops = audit(project)
    shown, truncated = store.page_with_store(owed, args.start, "audit", ["--audit"] + _with_project(project))
    lines = ["  %-12s %3d current, %3d owe facts, %3d broken" % (layer, row["current"], row["owed"], row["broken"])
             for layer, row in counts.items()]
    lines += ["  BROKEN %s (%s): %s" % (b["id"], b["layer"], "; ".join(b["problems"])) for b in broken]  # each, once
    lines += ["  %s (%s) owes: %s" % (o["id"], o["layer"], ", ".join(o["owes"])) for o in owed]
    lines += ["  says nothing of what it does — set it once with --function-set <part> <file>%s: %s"
              % (" --project %s" % shlex.quote(str(project)) if project else "", ", ".join(silent))] if silent else []
    lines += ["  drawer entry %s points at a record nobody has" % entry for entry in dangling]
    lines += ["  %s (%s) %s" % (s["id"], s["layer"], s["stop_line"]) for s in stops]
    return Answer({"layers": counts, "owed": shown, "broken": broken, "no_function": silent, "dangling": dangling,
                   "stops_at_footprint": [{key: s[key] for key in ("id", "layer", "stops_why")} for s in stops]}, lines,
                  truncated=truncated, problems=[_problem(b["id"], "broken: " + "; ".join(b["problems"])) for b in broken]
                  + [_problem(entry, "points at a record nobody has") for entry in dangling])


def _op_needs(args, project):
    from spark.design import needs
    listed = needs.read(args.needs)
    return Answer({"needs": listed}, ["  %-10s %s / %s%s%s" % (n["id"], n.get("does"), n.get("what"),
                                                               "  (%s)" % n["condition"] if n.get("condition") else "",
                                                               "  [%s]" % n["mark"] if n.get("mark") else "") for n in listed]
                  or ["  no needs yet — /spark:idea writes them"])


def _op_match(args, project):
    from spark.sourcing import matching
    from spark.design import needs
    try:
        chosen = matching.matcher(args.matcher or needs.MATCHER, "match")
    except matching.UnknownMatcher as wrong:
        return Answer(unchecked=[_cannot(str(wrong))])
    matched, problems = needs.match(args.match, chosen)
    if not matched and not problems:
        return Answer(unchecked=[_cannot("%s has no needs yet — /spark:idea writes them" % args.match)])
    for need in matched:
        kept = [c for rank, c in enumerate(need["candidates"]) if matching.shown(rank, c["what_matches"], c["score"])]
        need["more"], need["candidates"] = len(need["candidates"]) - len(kept), kept
    lines = []
    for need in matched:
        lines.append("  %s — %s / %s%s%s" % (need["need"], need["does"], need["what"], "  (%s)" % need["condition"] if need["condition"] else "",
                                            "  [%s]" % need["mark"] if need["mark"] else ""))
        for c in need["candidates"]:
            lines.append("      %-10s %-46s %s" % ("owned %s" % c["owned"] if c["owned"] else "", "%s (%s)" % (c["id"] or c["entry"], c["in"]),
                                                  "  ".join(filter(None, [", ".join(c["what"]) + ("" if c["what_matches"] else " [other words]"),
                                                                          ("free %s%s" % (c["free"], ", held by " + ", ".join(map(printable, c["held_by"])) if c["held_by"] else "")) if c["owned"] else "",
                                                                          "owes " + ", ".join(c["owes"]) if c["owes"] else "",
                                                                          c.get("stop_line") or ""])))
                         + ("  maybe owned — check the drawer" if c["unsure"] else "") + ("  BROKEN" if c["broken"] else ""))
            lines += ["          " + c["about"]] if c["about"] else []
            lines += ["          " + sentence for sentence in c["limits"]]  # P397: the JSON keeps them as data
            del c["about"]  # the text shows it; the JSON gains only `score` and `why`
            c.pop("stop_line", None)  # likewise: the JSON has `stops_why`, the list
        hidden = "none with the need's words" if chosen.name == needs.MATCHER else "each scoring under %s" % matching.MIN_SHOWN
        lines += ["      … %d more, %s" % (need["more"], hidden)] if need["more"] else []
        lines += ["      nothing in the store does this — a gap"] if not need["candidates"] else []
    lines += ["  %s: %s" % (p["subject"], p["sentence"]) for p in problems]
    shown, truncated = store.page_with_store(matched, args.start, "match", ["--match", args.match] + (["--matcher", args.matcher] if args.matcher else []))
    return Answer({"needs": shown}, lines, problems=problems, truncated=truncated)


def _op_offer(args, project):
    """`--offer KEY`: the whole text of one offer, for a chooser to read (P211) — or a problem when nothing live has that key."""
    from spark.design import needs
    found = needs.offer(args.offer, project)
    if found is None:
        return Answer(problems=[_problem(args.offer, "no record and no live drawer entry called %r — `--need` and "
                                                     "`--drawer` list what exists" % args.offer)])
    return Answer({"offer": found.as_dict()}, found.describe().splitlines())  # the text once: in the lines, not again in data


def _op_needs_set(args, project):
    from spark.design import needs
    target, name = args.needs_set
    items = _read_json_input(name)
    after, changes, problems = needs.plan_set(target, items)
    written = not (problems or args.dry_run)
    if written and changes:
        needs.write(target, after)
    return Answer({"changes": changes, "written": written}, _write_lines(changes, problems, args.dry_run), problems=problems)


def _op_needs_drop(args, project):
    """The drop of a need, run on the core (P514): DropNeed through `run_operation`, its result as parts.py's Answer."""
    from spark.core import outcomes
    from spark.core.cli import run_operation
    from spark.core.events import Reporter
    from spark.core.outside import build_outside_world
    from spark.idea.drop_need import DropNeed
    target, need = args.needs_drop
    result = run_operation(DropNeed(), {"project": Path(target), "need": need, "dry_run": args.dry_run},
                           build_outside=lambda effects: build_outside_world(effects, Reporter()))
    return Answer(result.data, result.lines, notes=result.notes or (), diagnostics=result.diagnostics,
                  problems=[_problem(found.subject, found.sentence, found.fix) for found in result.findings if found.severity == outcomes.PROBLEMS],
                  unchecked=[_cannot(found.sentence, found.fix) for found in result.findings if found.severity == outcomes.COULD_NOT_RUN])


def _op_pick(args, project):
    import drawer
    from spark.design import needs
    target, given = args.pick[0], args.pick[1:]
    pairs = [tuple(one.split("=", 1)) for one in given if "=" in one]
    if not pairs or len(pairs) != len(given):
        return Answer(unchecked=[_cannot("--pick takes the project, then NEED=ID for each pick: light=led-red-5mm",
                                         "parts.py --match <project> lists each need's candidates and their ids")])
    reasons = _read_json_input(args.passed_over) if args.passed_over else []
    history = store.events()  # read whole before the first write: one that cannot be read refuses the pick, with nothing written
    listed, keys_before = store.find_listed_name(target) is not None, needs.entry_keys(needs.read(target))
    after, changes, events, notes, problems = needs.plan_pick(target, pairs, reasons)
    if not problems and not args.dry_run:
        store.add_project(target)
        drawer.apply(changes)
        for event in events:
            store.append_event(event)
        # the project's own file last: a store that refuses leaves it as it was, and the same pick, retried, finishes the rest
        needs.write(target, after)
    asked, name = dict(pairs), store.plan_listed_name(target)
    picks = [{"need": need["id"], "pick": need.get("pick") or []} for need in after if need["id"] in asked]
    said = [] if problems else ["  %s: %s" % (one["need"], ", ".join(next(iter(pick.values())) for pick in one["pick"])) for one in picks]
    released = needs.released_holds(changes, name)
    said += [] if problems else ["  %s%s: %s — no pick of this project explains it" % (
        "would release" if args.dry_run else "released", "" if hold["now"] == 0 else " %d of %d" % (hold["was"] - hold["now"], hold["was"]),
        hold["entry"]) for hold in released]
    wrote = [] if problems else _what_a_pick_wrote(name, listed, history, events, needs.entry_keys(after) - keys_before, args.dry_run)
    return Answer({"project": name, "picks": picks,
                   "reserved": [{"entry": change["entry"], "used_in": change["now"]["used_in"]} for change in changes],
                   "released": released, "written": not problems and not args.dry_run},
                  _write_lines(changes, problems, args.dry_run, said + ["  %s" % note for note in notes] + wrote), problems=problems,
                  notes=[_note(note) for note in notes])


def _what_a_pick_wrote(name, listed, history, events, new_keys, dry_run):
    """
    What a pick writes beyond the drawer, said in its answer (C-17; the PO, 2026-10-08): the project put on the person's list,
    the `reused` lines its history gains, each reason noted — or already noted, and not changed, since the history keeps a
    need's first reason for a part — and a drawer entry's key that the project's own needs.json names from now on, said once.
    """
    seen, new = list(history), []
    for event in events:
        if not store.recorded(event, seen):
            new.append(event)
            seen.append(event)
    reused = sum(1 for event in new if event["event"] == "reused")
    lines = [] if listed else ["  %s %s on your projects" % ("would list" if dry_run else "listed", name)]
    lines += ["  %s to your history: %d reused" % ("would write" if dry_run else "wrote", reused)] if reused else []
    for event in (event for event in events if event["event"] == "passed_over"):
        passed = "%s (%s)" % (next(event[kind] for kind in ("part", "board", "entry") if kind in event), event["need"])
        lines.append("  %s why you passed over %s" % ("would note" if dry_run else "noted", passed) if event in new else
                     "  already noted, not changed: why you passed over %s — your history keeps the first reason" % passed)
    return lines + _names_your_entries("needs.json", new_keys, dry_run)


def _names_your_entries(file_name, new_keys, dry_run):
    """
    What a write says once when a project file starts naming drawer entries by their keys — each a key made from the person's
    label (C-17; F16): needs.json for --pick, requirements.json for --requirements, worded alike. Nothing when no key is new.
    """
    return ["  %s %s your drawer entr%s %s — a key made from your label, in the project's own file" % (file_name, "would name" if dry_run else
        "names", "y" if len(new_keys) == 1 else "ies", ", ".join(sorted(new_keys)))] if new_keys else []


def _gap_lines(problems, no_supply, no_receiver, no_driver):
    """What `--requirements` says of a rail with no supply, a net with no receiver or no driver: none on a refusal."""
    said = []
    said += ["  rail %s has no supply — pick a power inlet or a supply (%s draw%s from it)"
             % (gap["rail"], ", ".join(gap["drawn_by"]), "s" if len(gap["drawn_by"]) == 1 else "") for gap in ([] if problems else no_supply)]
    said += ["  net %s is driven by %s and nothing listed receives it — pick what it drives (a speaker terminal, a motor, a connector)"
             % (gap["net"], gap["driven_by"]) for gap in ([] if problems else no_receiver)]
    said += ["  net %s is one side of a driven pair and nothing listed drives it — pick what drives the pair (the amplifier this "
             "terminal hangs off), never a supply (%s %s on it)" % (gap["net"], ", ".join(gap["received_by"]),
                                                                    "is" if len(gap["received_by"]) == 1 else "are")
             for gap in ([] if problems else no_driver)]
    return said


def _op_requirements(args, project):
    from spark.design import footprint_emitter, needs
    content, shelving, unplaced, kept, board_was, problems, placeholder, unserved, no_supply, no_receiver, no_driver = needs.requirements(
        args.requirements)
    path, changed = Path(args.requirements) / needs.REQUIREMENTS, False
    # F16: the drawer keys the file names before this write — needs.requirements has read it as JSON already
    held = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    named = needs.unserved_keys(held)
    if not problems and not args.dry_run:
        for record, source in shelving:
            shelve(record, source)
        changed = store.write_file(path, json.dumps(content, indent=2, ensure_ascii=False) + "\n")
    said = [] if problems else ["  %s %s: board %s; parts %s" % (
        "would write" if args.dry_run else "wrote" if changed else "unchanged", path, content["board"],
        ", ".join(needs.entry_label(entry) for entry in content["parts"]) or "none")]
    said += ["  board: %s → %s" % (json.dumps(board_was), json.dumps(content["board"]))] if board_was not in (None, content["board"]) and not problems else []
    # --- MVP --- P387: board_only is said both ways, never silently written or dropped
    said += ["  board only: nothing to build but the board; the build skips the parts, schematic and footprint"
             ] if content.get(needs.BOARD_ONLY) is True and not problems else []
    said += ["  board_only removed: the file lists parts"] if isinstance(held, dict) and needs.BOARD_ONLY in held and content["parts"] and not problems else []
    stop = "" if problems else footprint_emitter.footprint_stop(content["board"], Path(args.requirements))
    said += ["  board %s: %s" % (content["board"], stop)] if stop else []  # F12 (C-7): said, never refused
    said += ["  onto the shelf, so every project builds with it: %s" % ", ".join(Path(r).stem for r, _ in shelving)] if shelving and not problems else []
    said += ["  placeholder outline — %s owes body_mm, so the PCB step lays it out at a placeholder %g x %g mm: a dimension drawing "
             "(fetched after the person's yes) or a measurement fills it — %s" % ((part_id,) + needs.board_emitter.DEFAULT_BODY_MM + (how,))
             for part_id, how in ([] if problems else placeholder)]
    said += ["  reserved, not placed — no record: %s" % ", ".join(unplaced)] if unplaced and not problems else []
    said += ["  kept, not from a pick: %s" % ", ".join(needs.entry_label(entry) for entry in kept)] if kept and not problems else []
    said += _gap_lines(problems, no_supply, no_receiver, no_driver)
    said += ["  not on the board: %s — %s" % (item["need"], needs.NOT_ON_THE_BOARD[item["why"]].format(picks=", ".join(item["picks"])))
             for item in ([] if problems else unserved)]
    said += [] if problems else _names_your_entries(needs.REQUIREMENTS, needs.unserved_keys(content) - named, args.dry_run)
    return Answer({"path": str(path), "requirements": content, "shelved": [Path(r).stem for r, _ in shelving],
                   "unplaced": unplaced, "kept": kept, "board_was": board_was, "placeholder_outline": [part_id for part_id, _ in placeholder],
                   "unserved": unserved, "no_supply": no_supply, "no_driver": no_driver,
                   "no_receiver": no_receiver, "written": not problems and not args.dry_run},
                  _write_lines([], problems, args.dry_run, said), problems=problems)


def _op_step(args, project):
    from spark.sourcing import run_cost
    target, step = args.step
    if step not in run_cost.STEPS:
        return Answer(unchecked=[_cannot("a step is one of %s (the spine, §2 of the store design)"
                                         % ", ".join(run_cost.STEPS))])
    listed = store.find_listed_name(target) is not None
    event = run_cost.step_event(store.plan_listed_name(target) if args.dry_run else store.add_project(target), step)
    if not args.dry_run:
        store.append_event(event)
    # C-17: what a step writes is said — a line in the person's history, with the session's id, and the project on their list
    return Answer({"step": event, "written": not args.dry_run},
                  ["  %s step %s of %s — a line in your history%s" % (
                      "would start" if args.dry_run else "started", step, event["project"],
                      ", with this Claude Code session's id" if event["session"] else run_cost.session_note())]
                  + ([] if listed else ["  %s %s on your projects" % ("would list" if args.dry_run else "listed", event["project"])]))


def _op_tally(args, project):
    from spark.sourcing import run_cost
    import drawer
    from spark.design import needs
    name = store.find_listed_name(args.tally)
    if name is None:
        return Answer(unchecked=[_cannot("%s is not on your list of projects, so no step of it was marked" % args.tally,
                                         "mark a step with parts.py --step <project> <step> in a Claude Code session: that puts it on the list")])
    history, entries, listed = store.events(), drawer.entries(), needs.read(args.tally)
    picks = [(need["id"], pick) for need in listed for pick in need.get("pick") or []]
    unpicked = [need["id"] for need in listed if not need.get("pick")]  # C-2: the picks are counted against the needs they serve
    reused = [event for event in history if event.get("event") == "reused" and event.get("project") == name]
    from_store = sum(1 for need_id, pick in picks if dict({"event": "reused", "project": name, "need": need_id}, **pick) in reused)
    owned = sum(1 for _, pick in picks if needs.owned(pick, entries))
    try:
        counted, unchecked = run_cost.cost([event for event in history if event.get("event") == "step"], name), []
    except run_cost.NoTranscript as missing:
        counted, unchecked = None, [_cannot(str(missing), "mark each step with parts.py --step <project> <step> in a Claude Code session")]
    said, unreadable = run_cost.line(len(picks), from_store, owned, counted), run_cost.unreadable_note(counted)
    built = any(event.get("event") == "built" and event.get("project") == name for event in history)
    needs_said = "%d of %d needs picked%s" % (len(listed) - len(unpicked), len(listed),
                                              " — not picked: %s" % ", ".join(unpicked) if unpicked else "")
    return Answer({"picks": len(picks), "from_store": from_store, "owned": owned, "cost": counted, "built": built, "line": said,
                   "needs": len(listed), "needs_picked": len(listed) - len(unpicked)},
                  ["  " + said, "  " + needs_said] + ["  " + glossed for glossed in run_cost.gloss(counted)]
                  + ["  " + item["sentence"] for item in unchecked] + (["  " + unreadable] if unreadable else [])
                  + ([] if built else ["  not built yet — check_spine records it when the chain runs end to end, and a board-only build records none"]),
                  unchecked=unchecked)


def _op_describe(args, project):
    operations = [{"op": name, "flag": "--" + name, "summary": summary, "effects": list(effects), "dry_run": bool(effects),
                   "arguments": {key: (list(value) if isinstance(value, tuple) else value)
                                 for key, value in keywords.items() if key in ("nargs", "metavar")},
                   "data": list(keys)} for name, keywords, summary, effects, keys in OPERATIONS]
    options = [{"flag": "--" + name, "summary": summary} for name, _, summary in OPTIONS]
    exits = {str(code): status for status, code in EXIT_FOR.items()}
    lines = ["  %-18s %s%s" % (op["flag"], op["summary"], "  [%s]" % ", ".join(op["effects"]) if op["effects"] else "")
             for op in operations]
    return Answer({"operations": operations, "options": options, "exits": exits}, lines)


def _text_of(answer):
    """
    The person's lines, then what the answer carries that they do not say yet: each problem and could-not-run item
    with its fix, each note and assumption, and the next steps (P124, #58). A line already said is not said again, so a
    handler that prints an item its own way keeps its wording; one that forgets an item no longer drops it.
    """
    lines = list(answer.lines)
    said = lambda words: bool(words) and any(words in line for line in answer.lines)  # noqa: E731 — the handler's own
    for heading, items in (("", answer.problems), ("could not check: ", answer.unchecked)):
        for item in items:
            if not (said(item["sentence"]) or said(item.get("subject"))):  # a handler may word an item its own way
                lines.append("  %s%s%s" % (heading, "%s: " % item["subject"] if item.get("subject") else "", item["sentence"]))
            if item.get("fix") and not said(item["fix"]):
                lines.append("  fix%s: %s" % (" for %s" % item["subject"] if item.get("subject") else "", item["fix"]))
    for note in answer.notes:
        shown = "%s: %s" % (note["subject"], note["sentence"]) if note.get("subject") else note["sentence"]
        if not said(shown):
            lines.append("  " + shown)
    for assumption in answer.assumptions:
        if not (said(assumption["fact"]) or said(assumption.get("sentence"))):
            lines.append("  ? %s%s%s" % (assumption["fact"], " = %s" % assumption["assumed"] if "assumed" in assumption else "",
                                         " — " + assumption["sentence"] if assumption.get("sentence") else ""))
        if assumption.get("upgrade") and not said(assumption["upgrade"]):
            lines.append("    to settle it: %s" % assumption["upgrade"])
    lines += ["  next: parts.py %s — %s" % (" ".join(step["argv"]), step["why"]) for step in answer.next]
    return lines


def _say(op, answer, as_json):
    """
    Print one answer and return its exit code (§6.4.1): with --json the envelope, compact, on stdout; without, the
    person's lines and whatever the answer carries that they leave out (`_text_of`). An answer with no lines says its
    problems and could-not-run items on stderr, as before.
    """
    said = envelope("parts", op, answer.data, answer.problems, answer.unchecked, answer.next, answer.truncated,
                    notes=answer.notes, assumptions=answer.assumptions)
    if answer.diagnostics:
        print(guard_lines("\n".join(answer.diagnostics)), file=sys.stderr)
    if as_json:
        print(json.dumps(said, ensure_ascii=False, separators=(",", ":")).encode("utf-8", "backslashreplace").decode("utf-8"))  # P445: a lone surrogate is written as a JSON escape
    else:
        if not answer.lines:
            for item in list(answer.problems) + list(answer.unchecked):
                said_here = "parts.py: %s%s" % (item["sentence"], " — " + item["fix"] if item.get("fix") else "")
                print(guard_lines(said_here), file=sys.stderr)
            answer = answer._replace(problems=(), unchecked=())
        for line in _text_of(answer):
            # P403, P423: every field, once, at the edge: a control or a right-to-left character shows as `?`. A line's own
            # newlines stay. A name that can hold a newline (a holder, a used_in key) is guarded where it is put in.
            print(guard_lines(line))  # --json stays raw, as data
    return EXIT_FOR[said["status"]]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    asked = next((name for name, *_ in OPERATIONS if "--" + name in argv), None)
    try:
        args = _parser().parse_args(argv)
    except BadArgument as bad:
        return _say(asked, Answer(unchecked=[_cannot(str(bad), "parts.py --describe --json lists every operation and its arguments")]),
                    "--json" in argv)
    op = next(name for name, *_ in OPERATIONS if getattr(args, name.replace("-", "_")) not in (None, False))
    project = args.project.resolve() if args.project else None
    writes = "writes" in next(effects for name, _, _, effects, _ in OPERATIONS if name == op)
    try:
        with store.locked() if writes else contextlib.nullcontext():
            answer = globals()["_op_" + op.replace("-", "_")](args, project)
    except (OSError, json.JSONDecodeError) as unreadable:
        answer = Answer(unchecked=[_cannot("--%s: %s" % (op, unreadable))])
    except PartError as broken:
        value = getattr(args, op.replace("-", "_"))
        answer = Answer(problems=[_problem(" ".join(value) if isinstance(value, list) else
                                           (value if isinstance(value, str) else None), str(broken))])
    except CodedMessageError as broken:  # a store's refusal, an unreadable input: could-not-run, never a traceback
        answer = Answer(unchecked=[_cannot(str(broken))])
    return _say(op, answer, args.json)


if __name__ == "__main__":
    sys.exit(main())
