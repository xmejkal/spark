"""
The datasheets and the catalog (W6-S3b, P721): what exists for a need before research (`need`, `catalog_records`), a document kept in the store with no location in it (`keep_in_store`, `keep_local`,
`without_location`), a datasheet read page by page (`read_datasheet`, `scan_datasheet`), a kept document found by its
words (`find_kept`), the documents a record cites fetched (`fetch_plan`, `fetch_documents`), and every cited URL asked
whether it answers (`cited_urls`, `sources_resolve`). Moved whole from `parts.py`. It imports the records area,
`matching` and `part_records` below it, never `parts.py`. `DatasheetService` comes with its card.
"""

import datetime
import hashlib
import json
import re
import struct
import urllib.parse
from pathlib import Path

from spark.records import board_records, record_kind, records_codes, store, tool_finder
from spark.records.record_kind import (
    Answer, available, _cannot, DEFINITION_SUFFIX, _parse, _problem, record_home, _write_record)
from spark.sourcing import matching, offers, sourcing_codes
from spark.sourcing.part_records import load, PartError


#: `--need`'s matcher (P211). A default changes only with the PO's yes: word-overlap since P743 (D15, 2026-11-10).
NEED_MATCHER = "word-overlap"
#: The layers `load` resolves a part id over, so a part row there that `load` refuses is a draft (P743); a catalog row,
#: another project's row, a board or an entry is never one.
LOADABLE = ("project", "shelf", "library")


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


def _found(words, built, matcher=None):
    """The offers a search by words finds (P211): the need {"does": null, "what": the words, "words": as typed}, ranked by the
    `--need` matcher."""
    need = {"does": None, "what": " ".join(words), "words": list(words)}
    return matching.found((matcher or matching.matcher(NEED_MATCHER, "need")).rank(need, built))


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
        raise store.StoreError("%s", problem, code=records_codes.FILE_NAME_REFUSED)
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
    try:
        reader = tool_finder.find("pdf-text", project)
    except tool_finder.ToolError as missing:
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
            lines.append("%s %s: %s %s" % (owner, key, entry.get("title") or entry.get("file") or entry.get("url"),
                                           entry.get("version") or "(version not read)"))
            if not entry.get("sha256"):  # P737: a document the page listed but the store cannot keep (a zip, a STEP)
                lines.append("    not kept (%s)" % entry.get("url"))
                continue
            path = kept / str(entry.get("sha256")) / str(entry.get("file"))
            lines.append("    %s  %s" % (path, "present" if path.is_file() else "MISSING"))
            for other, other_record in records_with_documents(project):
                same_file = {name for name, held in other_record["documents"].items()
                             if isinstance(held, dict) and held.get("sha256") and held.get("sha256") == entry.get("sha256")}
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


def keepable_url(url):
    """Whether the store keeps what this URL names, by its ending (`KEEPABLE`), the query left aside."""
    return url.split("?")[0].lower().endswith(KEEPABLE)


def to_fetch(record):
    """The cited datasheet and image URLs a record does not keep yet — what `--fetch` would download."""
    known = {entry.get("url") for entry in (record.get("documents") or {}).values()}
    return [url for url in cited_urls(record) if keepable_url(url) and url not in known]


def document_name(url):
    """The file name a cited URL is kept under: the last segment of its path, decoded — never its query."""
    return urllib.parse.unquote(url.split("?")[0].rsplit("/", 1)[-1]) or "document"


def document_entry(url, sha256, name, retrieved, title=None):
    """A record's `documents` entry for a kept file: its URL, checksum, file name and the date it was fetched. `title`
    is what the page that listed it calls it, else null, and `version` stays null until someone reads what the document
    PRINTS (P61). `--fetch` and the research sources write every entry through this one function."""
    return {"url": url, "sha256": sha256, "file": name, "retrieved": retrieved, "title": title, "version": None}


def fetch_plan(record):
    """
    [(url, file name)] for every document `--fetch` would keep, or a StoreError naming the first one the store would
    refuse by name. All or nothing (§6.4): the names come from the URLs, so every one is known before any download, and a
    refusal stops the whole fetch — not halfway, with the documents before it kept and no record pointing at them.
    `store.keep` still refuses such a name itself, as the last line of defence.
    """
    plan = [(url, document_name(url)) for url in to_fetch(record)]
    for url, name in plan:
        problem = store.file_name_problem(name)
        if problem:
            raise store.StoreError("%s: %s — nothing was fetched", url, problem, code=records_codes.FILE_NAME_REFUSED)
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
            documents[document_key(name, documents)] = document_entry(url, keep_in_store(payload, name), name, datetime.date.today().isoformat())
    record["documents"] = documents
    _write_record(path, record)
    return documents


def _download(url):
    """One cited document through spark's one door to the network (§6.5) — None when it does not answer, so it is not kept."""
    try:
        return store.fetch(url)
    except store.StoreError:
        return None


def need(words, project=None, matcher=None):
    """
    What the store holds for a search by words (P743, D15), so what exists is known before anything is researched: the rows
    the matcher finds and `matching.shown` keeps, owned first, then the best score; the drafts among them; and how many fits
    the cutoff dropped. An offer is a part or a board record of any layer with the drawer entries that say they are it, or a
    record-less entry (`offers.from_store`). Backlog R11: the RC car wrote three records by hand because nothing looked, and
    "nothing looked" was the first gap its diary named (G1).
    """
    built = offers.from_store(project)
    context = {(offer.kind, offer.key): said for offer, said in built}
    fits = _found(words, [offer for offer, _ in built], matcher)
    ranked = sorted(((fit, _need_row(fit, context[(fit.offer.kind, fit.offer.key)])) for fit in fits),
                    key=lambda pair: (pair[1]["owned"] == 0, -pair[0].score))
    kept = [row for rank, (fit, row) in enumerate(ranked) if matching.shown(rank, fit.exact, fit.score)]
    drafts = [row["id"] for row in kept if _is_draft(row, project)]
    return [row for row in kept if row["id"] not in drafts], drafts, len(ranked) - len(kept)


def _need_row(fit, context):
    """One `--need` row (P743), its keys the words `--match`'s candidates use: `id` or `entry`, `is` (part, board or entry), the
    record's own `kind`, `name`, `in` (the layer), `owned` (the drawer count: a number, "many" or "unknown"), `score`, `why`."""
    offer, record, holding = fit.offer, context["record"], context["holding"]
    return {"id": None if record is None else offer.key, "entry": offer.key if record is None else None,
            "is": "entry" if record is None else offer.kind, "kind": None if record is None else record.get("kind"),
            "name": holding[0].get("label") if record is None else record.get("name"), "in": context["in"],
            "owned": offers.counts(holding)[0], "score": fit.score, "why": fit.why}


def _is_draft(row, project):
    """Whether a row is a record still being filled in: a part of a layer `load` resolves over that the contract refuses. Research
    writes a skeleton first, and `--need` died on a researcher's draft while five ran (I3): named as a draft, never usable."""
    if row["is"] != "part" or row["in"] not in LOADABLE:
        return False
    try:
        load(row["id"], project)
    except PartError:
        return True
    return False


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
    except store.StoreError:
        return False
    return True


def sources_resolve(record, fetch=reachable):
    """(url, reachable) for every cited URL. `fetch` is a parameter so a test needs no network."""
    return [(url, fetch(url)) for url in cited_urls(record)]
