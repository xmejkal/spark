"""
The handlers of the parts records, their facts, the datasheets, the drawer and a run's steps (W6-S3b, P721): one
`_op_<flag>` per operation of `parts.py`, each taking the parsed arguments and the project and answering an `Answer`.
The vendors to research in and the sellers (`vendor_order`, `sellers`) read the project's `Brief`, and a write that
sets a record in its own home (`_set_in_home`) is here too. Moved whole from `parts.py`, whose `main` dispatches to them.
The handlers that read a JSON payload stay in the CLI: reading stdin is the interface's job (P721 row 6). It imports
the records area and the sourcing modules below it, never `parts.py`. The sourcing Operations on `run_cli` come with
their card.
"""

import json
from pathlib import Path

from spark.core.outcomes import add_env, step
from spark.core.text_guards import printable
from spark.records import board_records, missing_facts, record_kind, store
from spark.records.brief import Brief
from spark.records.fact_needs import FactNeeds
from spark.records.record_kind import (
    Answer, available, _cannot, DEFINITION_SUFFIX, _parse, _problem, record_home, _with_project, WRITE_BACK_HINT,
    _write_record)
from spark.sourcing import drawer, run_cost, sourcing_codes
from spark.sourcing.datasheets import (
    catalog_records, cited_urls, fetch_documents, fetch_plan, find_kept, keep_local, read_datasheet, sources_resolve,
    without_location)
from spark.sourcing.part_facts import (
    describe, promote, _row, _shelf_copy, shelvable, shelve, signals_for, skeleton, unverified)
from spark.sourcing.part_records import any_record, definition_path, load, NOT_A_PLAIN_ID, PartError, validate
from spark.sourcing.part_rules import conflicts_of


#: Vendors to research in, in order, when a project's brief does not say. DFRobot first because
#: its wiki carries a pinout table and a dimension drawing for every module; Seeed next for the
#: same reason. A project overrides this in `.spark/project.json` → `prefer`.
DEFAULT_VENDOR_ORDER = ("dfrobot", "seeed")


def vendor_order(project=None):
    """The vendors to research in, from the project's brief, else the default."""
    return Brief.from_project(project).prefer or DEFAULT_VENDOR_ORDER


def sellers(project=None):
    """
    Where the person buys, local first, from the project's brief — or nothing, which the
    researcher reports as "no sellers named" rather than choosing a shop for them.
    """
    return Brief.from_project(project).sellers or ()


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


def _reader_line(need):
    """One reader of an open fact: who, and whether it reads the fact today or which card makes it read (P738)."""
    return "      read by %s (%s)" % (need.consumer, need.status if need.reads else "%s, %s" % (need.status, need.card))


def _op_unverified(args, project):
    questions = unverified(args.unverified, project)
    needs = FactNeeds.from_file()  # P738: who reads each open fact, joined on its `write` key, never on English
    lines = ["  everything these parts claim has been checked."] if not questions else \
        ["  %d thing(s) nobody has checked:\n" % len(questions)]
    assumptions = []
    for q in questions:
        lines.append("  %s.%s = %s" % (q["part"], q["fact"], q["assumed"]))
        if q["why_it_matters"]:
            lines.append("      %s" % q["why_it_matters"])
        entry = {"fact": "%s.%s" % (q["part"], q["fact"]), "basis": "unverified", "assumed": q["assumed"],
                 "sentence": q["why_it_matters"], "source": q["source"], "write": q["write"]}
        read_by = needs.of_fact(q["write"] or "")
        lines.extend(_reader_line(need) for need in read_by)
        if read_by:
            entry["read_by"] = [need.to_dict() for need in read_by]
        assumptions.append(entry)
    owners = [q["part"] for q in questions if q["write"]]  # a row with no `write` cannot go back by --fact-set
    follow = [add_env(step("fact-set", ["--fact-set", owners[0], "<file>"], WRITE_BACK_HINT, ["writes"]), store.read_given_env())] if owners else []
    return Answer({"parts": list(args.unverified)}, lines, assumptions=assumptions, next=follow)


def _part_summary(part):
    return {"id": part["id"], "kind": part["kind"], "name": part["name"]}


#: The layers `--promote` copies a record out of, into the project (`part_facts.promote`).
PROMOTABLE = ("shelf", "catalog")
#: What to do instead of a skeleton, by the layer that holds the record (P740).
SKELETON_FIXES = {"project": "fill it in, do not overwrite it",
                  "shelf": "`--promote %(id)s --project .` copies it into the project",
                  "catalog": "`--promote %(id)s --project .` copies the draft into the project",
                  "library": "spark ships it; name it in the requirements as it is"}


def _op_skeleton(args, project):
    if not project or not args.kind:
        return Answer(unchecked=[_cannot("--skeleton needs --project (the record belongs to a project's parts/) and --kind")])
    if not store.PLAIN.fullmatch(args.skeleton):  # P87: a file every reader would refuse is never written
        return Answer(problems=[_problem(args.skeleton, NOT_A_PLAIN_ID % args.skeleton)])
    held = store.records("parts", record_kind.LIBRARY, project, drafts=True).get(args.skeleton)
    if held:  # P740: the project layer wins over every other, so a skeleton here would hide the record that exists
        layer, path = held
        would = "overwrite" if layer == "project" else "hide"
        return Answer(problems=[_problem(args.skeleton, "%s already holds %s; a skeleton here would %s it" % (layer, path, would),
                                         SKELETON_FIXES[layer] % {"id": args.skeleton})],
                      next=[add_env(step("promote", ["--promote", args.skeleton] + _with_project(project),
                                         "copy the %s record into the project" % layer, ["writes"]), store.read_given_env())]
                      if layer in PROMOTABLE else ())
    target = project / "parts" / (args.skeleton + DEFINITION_SUFFIX)
    record = skeleton(args.skeleton, args.kind, args.vendor, args.sku)
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
    except store.StoreError as refused:
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
    entries = drawer.listing()
    shown, truncated = store.page_with_store(entries, args.start, "drawer", ["--drawer"])
    lines = ["  %-44s %6s  %-38s %s" % (str(e["label"])[:44], "?" if e["count"] is None else e["count"],
                                         "%s %s" % next(iter(e["is"].items())) if e["is"] else "—",
                                         "  ".join(filter(None, ["maybe owned — check the drawer" if e["unsure"] else ("skip: %s" % e["skip"] if e["skip"] else ""),
                                                               "held by " + ", ".join(map(printable, e["held_by"])) if e["held_by"] else ""])))
             for e in entries]
    lines.append("  %d entr%s" % (len(entries), "y" if len(entries) == 1 else "ies"))
    return Answer({"entries": shown}, lines, truncated=truncated)


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
    """`record` with `values` set, and the values it had: `facts` takes the written names over the held ones, the other names stay
    (P374); `legs` the same, leg by leg (P741)."""
    after, was = dict(record, **values), {key: record.get(key) for key in values}
    if isinstance(values.get("legs"), dict):
        held = record.get("legs") if isinstance(record.get("legs"), dict) else {}
        after["legs"], was["legs"] = dict(held, **values["legs"]), {pin: held.get(pin) for pin in values["legs"]}
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


def _op_catalog(args, project):
    records, broken = catalog_records()
    listing = [{"id": part_id, "kind": record["kind"], "name": record["name"]} for part_id, record in records.items()]
    shown, truncated = store.page_with_store(listing, args.start, "catalog", ["--catalog"])
    lines = [_row(r["id"], r["kind"], r["name"]) for r in listing]
    lines += [_row(name, "BROKEN", "does not parse, or names no schema/id/name/kind") for name in broken]
    lines.append("  %d record(s), %d broken" % (len(records), len(broken)))
    return Answer({"records": shown, "broken": broken}, lines, truncated=truncated,
                  problems=[_problem(name.split(" — ")[0], "a broken catalog record: %s" % name) for name in broken])


def _op_step(args, project):
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
