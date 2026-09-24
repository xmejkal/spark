#!/usr/bin/env python3
"""
The findings store: what is wrong with a design, in a form that survives being wrong.

    findings.py anchors                     what a finding may refer to
    findings.py append <file.json>          add findings, deduped and validated
    findings.py list [--status open]        what is on the board
    findings.py status <key> <status> --reason "..."
    findings.py measure <id> --value <n> --unit mA --source measured --instrument "..."
    findings.py validate                    mark findings whose anchors no longer resolve
    findings.py next                        the one thing to do now

Three ideas do all the work here.

**Identity is structural.** A finding does not own a name; it owns the design elements it is
about. The key is a hash of its dimension and its sorted anchors, so the same defect described
in different words on two different runs collapses to one entry. A reviewer therefore never
needs to see the existing list, which is what keeps it able to rediscover things independently.

**An anchor that does not resolve rejects the finding.** Anchors are checked against the
generated circuit.json, which is the authoritative namespace. A finding about a net that does
not exist never enters the file — a free filter on the most common kind of hallucination.

**`rejected` is a terminal state that stays in the corpus.** A reviewer that is confidently
wrong is the normal case, not the exception. Without somewhere to retire a wrong finding, every
run raises it again and the tool becomes noise on the third run.
"""

import fcntl
import hashlib
import json
import os
import sys
from contextlib import contextmanager
from datetime import date
from pathlib import Path

EXIT_OK = 0
EXIT_PROBLEMS = 1
#: Distinct from 1 on purpose. A caller must be able to tell "I looked and there is nothing" from
#: "I never got to look" — conflating them once made a broken eval look like a broken reviewer.
EXIT_COULD_NOT_RUN = 2

SCHEMA = 1
SPARK_DIR = ".spark"
STORE_NAME = "findings.json"
DEFAULT_CIRCUIT = "dist/board/circuit.json"

#: Open states invite work; terminal states are answers. `regressed` is terminal on purpose — a
#: finding that comes back after being resolved means something undid the fix, and that is a
#: person's problem, never an automatic re-fix.
OPEN, WORKING, BLOCKED = "open", "working", "blocked"
RESOLVED, ACCEPTED, REJECTED, REGRESSED, STALE = (
    "resolved", "accepted", "rejected", "regressed", "stale")
LIVE = (OPEN, WORKING, BLOCKED, REGRESSED)
TERMINAL = (RESOLVED, ACCEPTED, REJECTED, STALE)

SEVERITIES = ("problem", "caveat")

#: What a reviewer is allowed to say. Everything else in a finding — its status, its decision,
#: when it was first seen — is written by this tool, never by the thing that found it.
REVIEWER_FIELDS = ("dimension", "anchors", "what", "consequence", "severity", "rests_on",
                   "confidence")

#: What `next` works on first. Blocked findings come top because clearing one is usually minutes
#: of someone's time and unblocks everything behind it.
PRIORITY = {BLOCKED: 0, REGRESSED: 1, OPEN: 2, WORKING: 3}


# ----------------------------------------------------------------- the anchor namespace

def anchor_namespace(circuit):
    """
    Every anchor a finding is allowed to cite, read out of the built design.

    `comp:` and `net:` come straight from the netlist; `port:` is qualified by its component so
    that two parts may both have a pin called VCC without colliding.
    """
    components = {
        element["source_component_id"]: element["name"]
        for element in circuit if element["type"] == "source_component"
    }
    names = {"comp:%s" % name for name in components.values()}
    names |= {
        "net:%s" % element["name"]
        for element in circuit
        if element["type"] == "source_net" and element.get("name")
    }
    for element in circuit:
        if element["type"] != "source_port":
            continue
        owner = components.get(element.get("source_component_id"))
        if owner and element.get("name"):
            names.add("port:%s.%s" % (owner, element["name"]))
    return names


def unresolved(anchors, namespace):
    """
    Anchors the design does not contain.

    `req:` and `file:` are not in the netlist and are checked elsewhere or not at all — they are
    how a finding refers to a requirement or a source file rather than a circuit element.
    """
    return [
        anchor for anchor in anchors
        if not anchor.startswith(("req:", "file:")) and anchor not in namespace
    ]


def key_for(dimension, anchors):
    """
    A finding's identity: its dimension and the set of things it is about.

    Deliberately not its wording. "The MP3 module is always powered" and "the DFR0534 can never
    be switched off" are the same finding, and both must cite `port:Mp3Player.VCC` and `net:VBAT`.
    """
    material = json.dumps([dimension, sorted(set(anchors))], sort_keys=True)
    return hashlib.sha1(material.encode()).hexdigest()[:12]


# ----------------------------------------------------------------- the store

def project_root(start=None):
    """
    The directory holding `.spark/`, found by walking up from here.

    Without this the store is whatever `.spark/findings.json` resolves to in the current working
    directory — so running from a subdirectory silently creates a second, invisible store and
    reports "nothing open" about a project full of findings. The caller does not control its own
    cwd; an agent may have changed it.
    """
    here = Path(start or Path.cwd()).resolve()
    for directory in [here, *here.parents]:
        if (directory / SPARK_DIR).is_dir():
            return directory
    raise SystemExit(
        "no %s/ directory here or above %s. Run `/spark:init`, or the script behind it, so there "
        "is one store rather than one per directory you happen to be standing in. (This used to "
        "say `spark init`, which existed nowhere but in this sentence.)" % (SPARK_DIR, here))


class Store:
    """
    Where findings live, and the only thing that knows they are a JSON file.

    Everything above this is rules — identity, dedupe, status — and none of it touches a disk.
    That separation is what lets the memory move somewhere else later (a database, a service, a
    shared store) by writing another one of these rather than rewriting the rules.
    """

    def __init__(self, root=None, circuit=None):
        self.root = Path(root) if root else project_root()
        self.path = self.root / SPARK_DIR / STORE_NAME
        self.circuit_path = Path(circuit) if circuit else self.root / DEFAULT_CIRCUIT

    @contextmanager
    def locked(self):
        """
        Hold the store for a whole read-modify-write.

        Every command reads the file, changes it and writes it back. Two of those overlapping —
        an agent appending while a person records a measurement — loses one of them completely
        and silently. A comment in a skill file saying "one writer" is a convention; this is the
        property.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock = self.path.with_suffix(".lock")
        with open(lock, "w") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def load(self):
        if not self.path.exists():
            return {"schema": SCHEMA, "findings": [], "measurements": {}}
        try:
            store = json.loads(self.path.read_text())
        except ValueError as broken:
            raise SystemExit("%s is not valid JSON: %s" % (self.path, broken))
        if store.get("schema") != SCHEMA:
            raise SystemExit(
                "%s is schema %s; this tool speaks %s" % (self.path, store.get("schema"), SCHEMA))
        store.setdefault("findings", [])
        store.setdefault("measurements", {})
        return store

    def save(self, store):
        """
        Write completely or not at all.

        `write_text` truncates before it writes, so an interruption leaves an empty or half
        finished file — and this is the only record of which findings a person already rejected,
        which is the one thing in here that cannot be regenerated by running the reviewers again.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".json.tmp")
        with open(temporary, "w") as handle:
            handle.write(json.dumps(store, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, self.path)

    def circuit(self):
        if not self.circuit_path.exists():
            raise SystemExit(
                "no %s — build the design first (`make`, or `tsci build`)" % self.circuit_path)
        return json.loads(self.circuit_path.read_text())


def merge(store, incoming, namespace, found_against=None, today=None):
    """
    Add findings, refusing what cannot be true and collapsing what is already known.

    Returns (added, refused, duplicates, regressions) so the caller can say what happened rather
    than silently absorbing a run's worth of work.
    """
    today = today or date.today().isoformat()
    existing = {finding["key"]: finding for finding in store["findings"]}
    added, refused, duplicates, regressions = [], [], [], []

    for candidate in incoming:
        problems = _malformed(candidate)
        if problems:
            refused.append((candidate.get("what", "<no description>"), "; ".join(problems)))
            continue

        missing = unresolved(candidate["anchors"], namespace)
        if missing:
            refused.append((candidate["what"],
                            "cites %s, which the design does not contain" % ", ".join(missing)))
            continue

        # Only these fields come from a reviewer. Copying the whole object would let it write
        # `resolution: {"reason": "signed off by Petr"}` into the store — and the entire value of
        # `accepted` and `rejected` is that they mean a person decided.
        finding = {field: candidate[field] for field in REVIEWER_FIELDS if field in candidate}
        finding["anchors"] = sorted(set(finding["anchors"]))
        finding["key"] = key_for(finding["dimension"], finding["anchors"])
        finding.setdefault("rests_on", [])

        previous = existing.get(finding["key"])
        if previous is None:
            waiting = [n for n in finding["rests_on"] if n not in store.get("measurements", {})]
            finding.update(status=BLOCKED if waiting else OPEN,
                           first_seen=today, found_against=found_against)
            store["findings"].append(finding)
            existing[finding["key"]] = finding
            added.append(finding)
        elif previous["status"] == RESOLVED:
            # It was fixed and it is back. Never re-fix this automatically.
            previous.update(status=REGRESSED, regressed_on=today)
            regressions.append(previous)
        else:
            duplicates.append(previous)

    return added, refused, duplicates, regressions


def _malformed(finding):
    problems = []
    for field in ("dimension", "anchors", "what", "consequence", "severity"):
        if not finding.get(field):
            problems.append("no %s" % field)
    if finding.get("severity") and finding["severity"] not in SEVERITIES:
        problems.append("severity must be one of %s" % ", ".join(SEVERITIES))
    anchors = finding.get("anchors")
    if anchors and not isinstance(anchors, list):
        problems.append("anchors must be a list")
    elif anchors and not all(isinstance(a, str) and a for a in anchors):
        problems.append("every anchor must be a non-empty string")
    return problems


def rank(findings):
    """
    What to do next: a sort, not a judgement.

    Blocked first because clearing one is usually minutes and unblocks everything behind it;
    then regressions, because something undid a fix; then problems before caveats.
    """
    def order(finding):
        return (PRIORITY.get(finding["status"], 9),
                0 if finding["severity"] == "problem" else 1,
                finding.get("first_seen", ""))
    return sorted([f for f in findings if f["status"] in LIVE], key=order)


# ----------------------------------------------------------------- measurements

#: How a number got here. Only `measured` means somebody put an instrument on the actual part.
#:
#: `simulated` exists so the loop can be demonstrated and tested without a bench, and it is a
#: separate source rather than a convincing `measured` on purpose. A fabricated value once walked
#: out of this project's own documentation into a live store and sat there looking exactly like a
#: reading; a simulator that produced indistinguishable numbers would be that mistake with a
#: feature request attached.
SOURCES = ("measured", "datasheet", "estimate", "simulated")

#: Sources that may not settle a decision that costs money. A simulated number is for showing the
#: machinery works, never for choosing a part.
NOT_EVIDENCE = ("estimate", "simulated")


def record_measurement(store, name, value, unit, source, instrument=None,
                       today=None, supersede=False):
    """
    Supply a number somebody was guessing, and reopen whatever was resting on it.

    Every number says where it came from, and that is not paperwork. This function once took any
    string and stored it, and the example value out of the documentation walked into a real
    project's store and sat there looking exactly like a reading — indistinguishable from a
    number somebody had actually taken off a meter. The measurements registry is the one place
    where a wrong value costs money, so it is the one place that must not accept a guess quietly.

    A second reading that disagrees with the first is information, not a correction, so replacing
    a value keeps the old one rather than overwriting it.
    """
    today = today or date.today().isoformat()
    if source not in SOURCES:
        raise ValueError("source must be one of %s, not %r" % (", ".join(SOURCES), source))
    if source == "measured" and not instrument:
        raise ValueError("a measured value needs --instrument: a reading with no instrument "
                         "is not reproducible")
    if not value:
        raise ValueError("a measurement needs a value")

    registry = store.setdefault("measurements", {})
    previous = registry.get(name)
    if previous and not supersede:
        raise ValueError(
            "%s already reads %s %s (%s). Pass --supersede to replace it; the old value is kept."
            % (name, previous["value"], previous.get("unit", ""), previous.get("source", "?")))

    entry = {"value": value, "unit": unit, "source": source, "date": today}
    if instrument:
        entry["instrument"] = instrument
    if previous:
        entry["superseded"] = previous.get("superseded", []) + [
            {k: v for k, v in previous.items() if k != "superseded"}]
    registry[name] = entry
    reopened = []
    for finding in store["findings"]:
        if name not in finding.get("rests_on", []):
            continue
        if finding["status"] == BLOCKED and not unfilled(finding, store):
            # Only when nothing else it rests on is still missing, or `next` would offer it as
            # work and print "waiting on a number nobody has taken" in the same breath.
            finding["status"] = OPEN
            reopened.append(finding)
        elif finding["status"] == RESOLVED:
            # It was fixed on the strength of a number that has now moved. Somebody has to look.
            finding["status"] = REGRESSED
            reopened.append(finding)
    return reopened


def unfilled(finding, store):
    """Measurements this finding rests on that nobody has taken yet."""
    taken = store.get("measurements", {})
    return [name for name in finding.get("rests_on", []) if name not in taken]


# ----------------------------------------------------------------- command line

def _circuit():
    if not CIRCUIT.exists():
        raise SystemExit("no %s — run `make` (or `tsci build`) first" % CIRCUIT)
    return json.loads(CIRCUIT.read_text())


def _show(finding):
    line = "  [%s] %-9s %-8s %s" % (
        finding["key"], finding["status"], finding["severity"], finding["what"])
    if finding.get("rests_on"):
        line += "\n       rests on: %s" % ", ".join(finding["rests_on"])
    return line


def _measurement(name, entry):
    text = "%s = %s %s (%s" % (name, entry["value"], entry.get("unit", ""), entry["source"])
    if entry.get("instrument"):
        text += ", %s" % entry["instrument"]
    return text + ")"


def _show(finding):
    line = "  [%s] %-9s %-8s %s" % (
        finding["key"], finding["status"], finding["severity"], finding["what"])
    if finding.get("rests_on"):
        line += "\n       rests on: %s" % ", ".join(finding["rests_on"])
    return line


def _measurement(name, entry):
    text = "%s = %s %s (%s" % (name, entry["value"], entry.get("unit") or "", entry["source"])
    if entry.get("instrument"):
        text += ", %s" % entry["instrument"]
    text += ")"
    if entry["source"] in NOT_EVIDENCE:
        text += "  <- NOT A READING"
    return text


def answer(status, rendered, **data):
    """
    One result, two audiences.

    The human line and the machine object are built from the same call, so they cannot drift —
    which is the failure this whole plugin exists to catch, and it would be embarrassing to
    reproduce it in the output of the tool that catches it.
    """
    return dict({"tool": "findings", "status": status, "rendered": rendered}, **data)


def _parser():
    """
    One place that knows the command line, so a missing flag is a message rather than a traceback.

    Hand-rolled argv indexing gave `IndexError` for a missing value, silently recorded a
    measurement called "--value" when the id was omitted, and accepted any string as a status —
    which made a typo'd status permanently invisible, because nothing lists it and `next` skips it.
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="findings.py", description="What is wrong with a design, and what was decided about it.")
    parser.add_argument("--store", help="project root holding .spark/ (default: found by walking up)")
    parser.add_argument("--circuit", help="the built design (default: dist/board/circuit.json)")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="the result as data, for a caller that is not a person")
    parser.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True, parser_class=lambda **kw:
                                argparse.ArgumentParser(parents=[common], **kw))

    sub.add_parser("anchors", help="what a finding may refer to")
    sub.add_parser("next", help="the one thing to do now")
    sub.add_parser("measurements", help="every number and where it came from")

    appended = sub.add_parser("append", help="add findings, deduped and validated")
    appended.add_argument("file", help="JSON: a list of findings, or {\"findings\": [...]}")

    listed = sub.add_parser("list", help="what is on the board")
    listed.add_argument("--status", choices=sorted(LIVE + TERMINAL))

    status = sub.add_parser("status", help="record a decision about a finding")
    status.add_argument("key")
    status.add_argument("status", choices=sorted(LIVE + TERMINAL))
    status.add_argument("--reason")

    measure = sub.add_parser("measure", help="record a number somebody obtained")
    measure.add_argument("name")
    measure.add_argument("--value", required=True)
    measure.add_argument("--unit", required=True)
    measure.add_argument("--source", required=True, choices=SOURCES)
    measure.add_argument("--instrument")
    measure.add_argument("--supersede", action="store_true")

    checked = sub.add_parser("validate", help="find findings whose anchors no longer resolve")
    checked.add_argument("--apply", action="store_true",
                         help="actually mark them stale (default: say what would change)")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        result = _run(args)
    except SystemExit as refusal:
        # A refusal is an answer, not a crash — an autonomous caller has to act on it.
        result = answer("could-not-run", str(refusal), reason=str(refusal))

    if getattr(args, "json", False):
        print(json.dumps(result, indent=2))
    elif result["rendered"]:
        print(result["rendered"])

    return {"ok": EXIT_OK, "problems": EXIT_PROBLEMS,
            "could-not-run": EXIT_COULD_NOT_RUN}[result["status"]]


def _run(args):
    store_io = Store(root=args.store, circuit=args.circuit)

    if args.command == "anchors":
        names = sorted(anchor_namespace(store_io.circuit()))
        return answer("ok", "\n".join(names), anchors=names)

    with store_io.locked():
        store = store_io.load()

        if args.command == "append":
            raw = json.loads(Path(args.file).read_text())
            if isinstance(raw, dict):
                raw = raw.get("findings", [raw])
            if not isinstance(raw, list) or not all(isinstance(f, dict) for f in raw):
                raise SystemExit("%s must hold a list of findings" % args.file)

            added, refused, duplicates, regressions = merge(
                store, raw, anchor_namespace(store_io.circuit()))
            store_io.save(store)
            lines = ["%d new, %d already known, %d refused, %d regressed"
                     % (len(added), len(duplicates), len(refused), len(regressions))]
            lines += [_show(f) for f in added]
            lines += ["  refused: %s\n       %s" % (w, y) for w, y in refused]
            lines += ["  REGRESSED: %s" % f["what"] for f in regressions]
            # A refusal is not a success: a caller needs to know the run was partly rejected.
            return answer("problems" if refused else "ok", "\n".join(lines),
                          added=[f["key"] for f in added],
                          duplicates=[f["key"] for f in duplicates],
                          regressed=[f["key"] for f in regressions],
                          refused=[{"what": w, "why": y} for w, y in refused])

        if args.command == "list":
            shown = [f for f in store["findings"]
                     if args.status is None or f["status"] == args.status]
            return answer("ok", "\n".join(_show(f) for f in shown), findings=shown)

        if args.command == "measurements":
            taken = store.get("measurements", {})
            return answer("ok", "\n".join("  " + _measurement(n, e)
                                          for n, e in sorted(taken.items())),
                          measurements=taken)

        if args.command == "status":
            if args.status in (ACCEPTED, REJECTED) and not args.reason:
                raise SystemExit("%s needs --reason: it is a decision, and decisions are recorded"
                                 % args.status)
            for finding in store["findings"]:
                if finding["key"] == args.key:
                    finding["status"] = args.status
                    finding.setdefault("decisions", []).append(
                        {"status": args.status, "reason": args.reason,
                         "date": date.today().isoformat()})
                    store_io.save(store)
                    return answer("ok", _show(finding), finding=finding)
            raise SystemExit("no finding %s" % args.key)

        if args.command == "measure":
            waiting = {name for finding in store["findings"]
                       for name in finding.get("rests_on", [])}
            if args.name not in waiting:
                raise SystemExit(
                    "nothing rests on %r, so recording it changes nothing.\n  waiting on: %s"
                    % (args.name, ", ".join(sorted(waiting)) or "nothing"))
            try:
                reopened = record_measurement(
                    store, args.name, args.value, args.unit, args.source,
                    args.instrument, supersede=args.supersede)
            except ValueError as refusal:
                raise SystemExit(str(refusal))
            store_io.save(store)
            entry = store["measurements"][args.name]
            lines = ["recorded " + _measurement(args.name, entry)]
            lines += ["  %s: %s" % ("regressed" if f["status"] == REGRESSED else "unblocked",
                                    f["what"]) for f in reopened]
            return answer("ok", "\n".join(lines), measurement=entry,
                          reopened=[f["key"] for f in reopened])

        if args.command == "validate":
            namespace = anchor_namespace(store_io.circuit())
            stale = [f for f in store["findings"]
                     if f["status"] in LIVE and unresolved(f["anchors"], namespace)]
            shown = ["  %s\n       anchors gone: %s"
                     % (_show(f), ", ".join(unresolved(f["anchors"], namespace))) for f in stale]
            keys = [f["key"] for f in stale]
            if not args.apply:
                # Run against a half-built or wrong-branch design, this would retire every live
                # finding with no way back. It says what it would do unless told to do it.
                return answer("problems" if stale else "ok",
                              "\n".join(shown) + "\n\n%d would go stale. Re-run with --apply."
                              % len(stale), would_go_stale=keys, applied=False)
            for finding in stale:
                finding["status"] = STALE
                finding["stale_anchors"] = unresolved(finding["anchors"], namespace)
            store_io.save(store)
            return answer("ok", "%d marked stale." % len(stale), went_stale=keys, applied=True)

        if args.command == "next":
            ordered = rank(store["findings"])
            if not ordered:
                return answer("ok", "nothing live.", next=None, live=0)
            chosen = ordered[0]
            waiting = unfilled(chosen, store)
            lines = ["%d live; the one to do now:\n" % len(ordered), _show(chosen)]
            if waiting:
                lines.append("\n   waiting on a number nobody has taken yet: %s"
                             % ", ".join(waiting))
            return answer("ok", "\n".join(lines), next=chosen, live=len(ordered),
                          waiting_on=waiting)

    raise SystemExit("unknown command %r" % args.command)


if __name__ == "__main__":
    sys.exit(main())
