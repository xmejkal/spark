#!/usr/bin/env python3
"""
The findings store: what is wrong with a design, in a form that survives being wrong.

    findings.py anchors                     what a finding may refer to
    findings.py append <file.json>          add findings, deduped and validated
    findings.py list [--status open]        what is on the board
    findings.py status <key> <status> --reason "..."
    findings.py measure <id> --value 18.4 --unit mA --instrument "DMM in series"
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

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

SCHEMA = 1
STORE = Path(".spark/findings.json")
BRIEF = Path(".spark/project.json")
CIRCUIT = Path("dist/board/circuit.json")

#: Open states invite work; terminal states are answers. `regressed` is terminal on purpose — a
#: finding that comes back after being resolved means something undid the fix, and that is a
#: person's problem, never an automatic re-fix.
OPEN, WORKING, BLOCKED = "open", "working", "blocked"
RESOLVED, ACCEPTED, REJECTED, REGRESSED, STALE = (
    "resolved", "accepted", "rejected", "regressed", "stale")
LIVE = (OPEN, WORKING, BLOCKED, REGRESSED)
TERMINAL = (RESOLVED, ACCEPTED, REJECTED, STALE)

SEVERITIES = ("problem", "caveat")

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
    material = "%s|%s" % (dimension, "|".join(sorted(anchors)))
    return hashlib.sha1(material.encode()).hexdigest()[:12]


# ----------------------------------------------------------------- the store

def load(path=STORE):
    if not Path(path).exists():
        return {"schema": SCHEMA, "findings": []}
    store = json.loads(Path(path).read_text())
    if store.get("schema") != SCHEMA:
        raise SystemExit(
            "%s is schema %s; this tool speaks %s" % (path, store.get("schema"), SCHEMA))
    return store


def save(store, path=STORE):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(store, indent=2) + "\n")


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

        finding = dict(candidate)
        finding["key"] = key_for(finding["dimension"], finding["anchors"])
        finding.setdefault("rests_on", [])
        finding["anchors"] = sorted(finding["anchors"])

        previous = existing.get(finding["key"])
        if previous is None:
            finding.update(status=OPEN, first_seen=today, found_against=found_against)
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
    if finding.get("anchors") and not isinstance(finding["anchors"], list):
        problems.append("anchors must be a list")
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

def record_measurement(store, name, value, unit, instrument, today=None):
    """
    Supply a number somebody was guessing, and reopen whatever was resting on it.

    This is what makes an assumption safe to work with: it is not a risk buried in prose, it is
    a named thing that findings point at, and filling it in tells you exactly what changed.
    """
    today = today or date.today().isoformat()
    store.setdefault("measurements", {})[name] = {
        "value": value, "unit": unit, "instrument": instrument, "date": today,
    }
    reopened = []
    for finding in store["findings"]:
        if name in finding.get("rests_on", []) and finding["status"] == BLOCKED:
            finding["status"] = OPEN
            reopened.append(finding)
    return reopened


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


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__.split("\n\n")[1].strip())
    command = argv[1]

    if command == "anchors":
        for anchor in sorted(anchor_namespace(_circuit())):
            print(anchor)
        return 0

    store = load()

    if command == "append":
        incoming = json.loads(Path(argv[2]).read_text())
        incoming = incoming.get("findings", incoming)
        added, refused, duplicates, regressions = merge(
            store, incoming, anchor_namespace(_circuit()))
        save(store)
        print("%d new, %d already known, %d refused, %d regressed"
              % (len(added), len(duplicates), len(refused), len(regressions)))
        for finding in added:
            print(_show(finding))
        for what, why in refused:
            print("  refused: %s\n       %s" % (what, why))
        for finding in regressions:
            print("  REGRESSED: %s" % finding["what"])
        return 0

    if command == "list":
        wanted = argv[3] if len(argv) > 3 and argv[2] == "--status" else None
        for finding in store["findings"]:
            if wanted is None or finding["status"] == wanted:
                print(_show(finding))
        return 0

    if command == "status":
        key, new_status = argv[2], argv[3]
        reason = argv[argv.index("--reason") + 1] if "--reason" in argv else None
        if new_status in (ACCEPTED, REJECTED) and not reason:
            raise SystemExit("%s needs --reason: it is a decision, and decisions are recorded"
                             % new_status)
        for finding in store["findings"]:
            if finding["key"] == key:
                finding["status"] = new_status
                finding["resolution"] = {"reason": reason, "date": date.today().isoformat()}
                save(store)
                print(_show(finding))
                return 0
        raise SystemExit("no finding %s" % key)

    if command == "measure":
        name = argv[2]
        def flag(which):
            return argv[argv.index(which) + 1] if which in argv else None
        reopened = record_measurement(
            store, name, flag("--value"), flag("--unit"), flag("--instrument"))
        save(store)
        print("recorded %s = %s %s" % (name, flag("--value"), flag("--unit") or ""))
        for finding in reopened:
            print("  unblocked: %s" % finding["what"])
        return 0

    if command == "validate":
        namespace = anchor_namespace(_circuit())
        stale = []
        for finding in store["findings"]:
            if finding["status"] in LIVE and unresolved(finding["anchors"], namespace):
                finding["status"] = STALE
                stale.append(finding)
        save(store)
        print("%d finding(s) went stale" % len(stale))
        for finding in stale:
            print(_show(finding))
        return 0

    if command == "next":
        ordered = rank(store["findings"])
        if not ordered:
            print("nothing open.")
            return 0
        print("%d open; the one to do now:\n" % len(ordered))
        print(_show(ordered[0]))
        return 0

    raise SystemExit("unknown command %r" % command)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
