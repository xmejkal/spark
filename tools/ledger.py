"""
The mutation ledger (P787): one line per mutation row a run tried (a refused row too), so a sweep knows which rows were
caught, when, and at which content of their file. `mutate.py` writes it after every run that plants rows, and reads
it to put each row in its tier (`tier_of`, `Tiers`), so a sweep runs a few hundred rows and not all 3000.

    tests/mutations/ledger.jsonl
    {"key": "4a1f0c9e2b7d", "file": "tools/mutate.py", "blob": "<40 hex>", "date": "2026-11-12T18:04:11+01:00",
     "status": "caught", "by": "test_mutate", "caught": 1, "s": 7}

`key` is the row's identity (`row_key`); `blob` is git's hash of the file the row was planted in, as the run read it;
`date` is the run's end, with its zone, the moment the facts are known; `status` is the run's word for the row (`caught`,
`escaped`, `refused`); `by` is the test module that caught it, `suite` when the whole suite did, `escape` when none did,
and null when the row was refused and nothing ran; `caught` counts the catches at this `blob` (a changed file starts the
count again); `s` is the row's seconds. The file is in git and rewritten whole, sorted by key: two branches that ran
different keys merge line by line in git; two that ran the same key conflict on that line, and a person resolves it by
hand. `merged` is this tool's rule for one tree (the newer date wins), never git's. An empty ledger is empty: nothing
seeds it.

THE TIERS (the plan's words, each a fact a tool reads): *critical*, the row carries `"tier": "critical"` (a fifth key,
hand-written); *new*, no line for the row's key at its file's current blob (never run, or the file changed since), or
a line whose status is `escaped` (a missing test: it runs again) or `refused` (`--anchors`' business until PR 5
retires it); *proving*, a `caught` line at the current blob with `caught` 1; *proven*, a `caught` line at the current
blob with `caught` 2 or more. `status` and `caught` are read together: a refused line keeps its count from the same
blob (`merged` adds 0), so the count alone never makes a row proving or proven. *Retired* (PR 5) is not decided here.
The blob rule alone decides staleness: no git history is read, and a row with no line is new, never proven. The order a
sweep runs them: critical, new in the tables' given order (the caller names the oldest table first: no table carries
a date), proving, proven oldest date first.

Standard library only, as `scratch.py`: `mutate.py` imports it by path.
"""

import collections
import hashlib
import json
from datetime import datetime
from pathlib import Path

#: The ledger's name under tests/mutations/; `.jsonl` so the tables' `*.json` glob never reads it as a table.
LEDGER_NAME = "ledger.jsonl"
#: How many hex digits of the sha1 make a key: 12, as the plan says (48 bits over about 3200 rows).
KEY_LENGTH = 12
#: Between the parts of a key: without it `ab` + `c` and `a` + `bc` would hash alike.
SEPARATOR = "\0"
#: The run's words for a row, as `mutate.py` reports them; the ledger adds none.
CAUGHT, ESCAPED, REFUSED = "caught", "escaped", "refused"
#: `by` when the whole suite caught the row, and when no test did.
SUITE, ESCAPE = "suite", "escape"
#: The tiers a row can be in, in the order a sweep runs them (P787 PR 2); `retired` is PR 5's.
CRITICAL, NEW, PROVING, PROVEN = "critical", "new", "proving", "proven"
TIERS = (CRITICAL, NEW, PROVING, PROVEN)
#: The row's fifth key, hand-written, that makes it critical.
TIER_KEY = "tier"
#: Two catches at one blob, as the plan says.
PROVEN_AT = 2


def row_key(row):
    """
    The identity of a mutation row: sha1 of its file, find and replace, the first 12 hex digits (P787). The file is in
    it (PR 0, row 2): one `find` and `replace` on two files are two defects. It survives a change of the row's `name`,
    and a retarget changes it, as it should: the row then guards another file.
    """
    return hashlib.sha1(SEPARATOR.join((row["file"], row["find"], row["replace"])).encode()).hexdigest()[:KEY_LENGTH]


def blob_of(content):
    """
    git's blob hash of `content` (bytes): sha1 over `blob <length>\\0` and the bytes, what `git hash-object` prints, so a
    `--copy` tree without `.git` hashes as the real tree does.
    """
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


def line(row, blob, date, status, by, seconds):
    """One ledger line for `row`, in the order the file keeps; `caught` is 1 or 0 for this run, `merged` adds the past."""
    return {"key": row_key(row), "file": row["file"], "blob": blob, "date": date, "status": status, "by": by,
            "caught": 1 if status == CAUGHT else 0, "s": seconds}


def merged(kept, fresh):
    """
    The lines of `kept` with those of `fresh` over them, by key: the newer `date` wins, and on the same date the fresh one.
    When the fresh line wins and sits on the same `blob` as the kept one, its `caught` adds the kept count: "caught twice
    at the current blob" is a count across runs. A changed blob starts the count at the fresh line's own.
    """
    result = {entry["key"]: entry for entry in kept}
    for entry in fresh:
        old = result.get(entry["key"])
        if old is not None and _when(old["date"]) > _when(entry["date"]):
            continue
        if old is not None and old["blob"] == entry["blob"]:
            entry = dict(entry, caught=old["caught"] + entry["caught"])
        result[entry["key"]] = entry
    return [result[key] for key in sorted(result)]


def _when(date):
    return datetime.fromisoformat(date)


def tier_of(row, entry, blob):
    """
    The tier of `row`, whose ledger line is `entry` (None when it has none) and whose file's current blob is `blob`:
    critical when the row says so; new when the file is gone (`blob` None), when no line sits at this blob, or when the
    line there is not a catch (escaped or refused); proving when caught once there; proven when caught `PROVEN_AT`
    times or more.
    """
    if row.get(TIER_KEY) == CRITICAL:
        return CRITICAL
    if blob is None or entry is None or entry["blob"] != blob or entry["status"] != CAUGHT:
        return NEW
    return PROVEN if entry["caught"] >= PROVEN_AT else PROVING


class Tiers:
    """
    Value: the rows of a run's tables under their tiers, each tier's rows in the order a sweep runs them (`TIERS`):
    the critical rows, the new ones and the proving ones in the tables' given order, the proven ones oldest date first.
    `counts` says how many rows each tier holds; `selected` gives the rows of the named tiers, in that order.
    """

    def __init__(self, rows_by_tier):
        self.rows = {tier: list(rows_by_tier.get(tier, ())) for tier in TIERS}

    def counts(self):
        """How many rows each tier holds, in the tiers' order."""
        return {tier: len(self.rows[tier]) for tier in TIERS}

    def selected(self, tiers):
        """The rows of the tiers named in `tiers`, in the sweep's order; a tier not named gives none."""
        return [row for tier in TIERS if tier in tiers for row in self.rows[tier]]


def tiers_of(root, mutations, lines):
    """
    The `Tiers` of `mutations` under `root`, read against the ledger's `lines`: each row's file is hashed as it is now
    (a missing file hashes to None, so its rows are new and the run refuses them), and each row meets its line by key.
    """
    by_key = {entry["key"]: entry for entry in lines}
    blobs = {}
    found = {tier: [] for tier in TIERS}
    for row in mutations:
        file = row["file"]
        if file not in blobs:
            path = Path(root) / file
            blobs[file] = blob_of(path.read_bytes()) if path.is_file() else None
        entry = by_key.get(row_key(row))
        found[tier_of(row, entry, blobs[file])].append((entry, row))
    found[PROVEN].sort(key=lambda pair: _when(pair[0]["date"]))  # a stable sort: the same date keeps the tables' order
    return Tiers({tier: [row for _, row in pairs] for tier, pairs in found.items()})


class LedgerStore:
    """
    Store: reads and writes the ledger file whole, one JSON line per key, sorted by key. A missing file reads as no
    lines. `record` puts a run's lines over the file's (`merged`) and writes the result; `counts` says how many lines
    hold each status.
    """

    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        """The lines, in the file's order; none when the file does not exist."""
        if not self.path.is_file():
            return []
        return [json.loads(text) for text in self.path.read_text().splitlines() if text.strip()]

    def write(self, lines):
        """The whole file, sorted by key, one line each."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("".join(json.dumps(entry) + "\n" for entry in sorted(lines, key=lambda entry: entry["key"])))

    def record(self, lines):
        """Merge a run's lines into the file and write it; the lines written."""
        kept = merged(self.read(), lines)
        self.write(kept)
        return kept

    def counts(self):
        """How many lines hold each status, by status word, sorted."""
        return dict(sorted(collections.Counter(entry["status"] for entry in self.read()).items()))
