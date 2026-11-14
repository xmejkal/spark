"""
The mutation ledger (P787): one line per mutation row a run tried (a refused row too), so a sweep knows which rows were
caught or refused, when, and at which content of their file. `mutate.py` writes it after every run that plants rows,
and reads it to put each row in its tier (`tier_of`, `Tiers`), so a sweep runs a few hundred rows and not all 3000, and
to list the retired rows (`is_retired`) and the same-line groups (`same_line_groups`, `group_verdict`) for a deleting PR.

    tests/mutations/ledger.jsonl
    {"key": "4a1f0c9e2b7d", "file": "tools/mutate.py", "blob": "<40 hex>", "date": "2026-11-12T18:04:11+01:00",
     "status": "caught", "by": "test_mutate", "caught": 1, "refused": 0, "s": 7}

`key` is the row's identity (`row_key`); `blob` is git's hash of the file the row was planted in, as the run read it;
`date` is the run's end, with its zone, the moment the facts are known; `status` is the run's word for the row (`caught`,
`escaped`, `refused`); `by` is the test module that caught it, `suite` when no red line named one, `escape` when none did,
and null when the row was refused and nothing ran; `caught` counts the catches at this `blob` and `refused` the refusals
there (a changed file starts both counts again); `s` is the row's seconds. The file is in git and rewritten whole,
sorted by key: two branches that ran different keys merge line by line in git; two that ran the same key conflict on
that line, and a person resolves it by hand. `merged` is this tool's rule for one tree (the newer date wins), never
git's. An empty ledger is empty: nothing seeds it.

THE TIERS (the plan's words, each a fact a tool reads): *critical*, the row carries `"tier": "critical"` (a fifth key,
hand-written); *retired*, a `refused` line at the file's current blob with `refused` 2 or more (`is_retired`: refused in
two sweeps, so a sweep plants it no more and `--retire` lists it for a deleting PR); *new*, no line for the row's key at
its file's current blob (never run, or the file changed since), or a line whose status is `escaped` (a missing test: it
runs again, never retires) or `refused` once; *proving*, a `caught` line at the current blob with `caught` 1; *proven*,
a `caught` line at the current blob with `caught` 2 or more. `status` and the counts are read together: a refused line
keeps its `caught` from the same blob (`merged` adds 0), so a count alone never makes a row proving, proven or retired.
The blob rule alone decides staleness: no git history is read, and a row with no line is new, never proven. The order a
sweep runs them: critical, new in the tables' given order (the caller names the oldest table first: no table carries
a date), proving, proven oldest date first; a retired row runs in no tier.

A SAME-LINE GROUP (PR 6) is two or more rows on one `file` and one `find` with different replaces: two mutants of one
line, each its own row and key (a *duplicate* is PR 0's kind, the same replace too, one key). `same_line_groups` finds
them (the line is `same_line_key` of the find: its lines stripped of indentation, the trailing line break dropped) and
`group_verdict` reads the ledger for each: *merge candidate* when every row of the group has a line at the file's current
blob, caught, by the same test module (`by`): a candidate to read, not a proof, because two functions of one module may
tell the mutants apart, so the deleting PR opens the module and checks that one test fails for every mutant of the line
before it drops a row; *distinct* when a status is not a catch, a `by` differs or a `by` is `suite` (no module named),
decided as soon as the known lines say so; *not yet run* when nothing disagrees and a row has no line at the current
blob. The tool reports (`mutate.py --duplicates`) and deletes nothing: a merge candidate is dropped in a PR with its
reason (W3: dropping a mutation is dropping the test), the others stay.

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
#: `by` when a catch named no test module (a crash before any test), and when no test caught the row.
SUITE, ESCAPE = "suite", "escape"
#: The five tier words (P787): the four a sweep runs, in its order, and `retired`, which it runs no more (PR 5).
CRITICAL, NEW, PROVING, PROVEN, RETIRED = "critical", "new", "proving", "proven", "retired"
TIERS = (CRITICAL, NEW, PROVING, PROVEN)
TIER_WORDS = TIERS + (RETIRED,)
#: The row's fifth key, hand-written, that makes it critical.
TIER_KEY = "tier"
#: Two catches at one blob, as the plan says.
PROVEN_AT = 2
#: Two refusals at one blob, as the plan says: "refused by --anchors in two sweeps".
RETIRED_AT = 2
#: The three verdicts of a same-line group (PR 6), as `--duplicates` prints them.
MERGE_CANDIDATE, DISTINCT, NOT_YET_RUN = "merge candidate", "distinct", "not yet run"
VERDICTS = (MERGE_CANDIDATE, DISTINCT, NOT_YET_RUN)


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
    """One ledger line for `row`, in the file's order; `caught` and `refused` are 1 or 0 for this run, `merged` adds the past."""
    return {"key": row_key(row), "file": row["file"], "blob": blob, "date": date, "status": status, "by": by,
            "caught": 1 if status == CAUGHT else 0, "refused": 1 if status == REFUSED else 0, "s": seconds}


def merged(kept, fresh):
    """
    The lines of `kept` with those of `fresh` over them, by key: the newer `date` wins, and on the same date the fresh one.
    When the fresh line wins and sits on the same `blob` as the kept one, its `caught` and `refused` add the kept counts:
    "caught twice at the current blob" and "refused in two sweeps" are counts across runs. A changed blob starts both
    counts at the fresh line's own.
    """
    result = {entry["key"]: entry for entry in kept}
    for entry in fresh:
        old = result.get(entry["key"])
        if old is not None and _when(old["date"]) > _when(entry["date"]):
            continue
        if old is not None and old["blob"] == entry["blob"]:
            # An eight-field line (written before PR 5) has no `refused`: read as 0, never a crash.
            entry = dict(entry, caught=old["caught"] + entry["caught"], refused=old.get("refused", 0) + entry["refused"])
        result[entry["key"]] = entry
    return [result[key] for key in sorted(result)]


def _when(date):
    return datetime.fromisoformat(date)


def is_retired(entry, blob):
    """
    Whether a row whose ledger line is `entry` (None when it has none) is retired at its file's current blob `blob`: the
    line sits at this blob, its last word is `refused`, and it was refused `RETIRED_AT` times or more there (two sweeps).
    An escaped line never retires, whatever it counts: an escape is a missing test. A gone file hashes to None in the
    line and now, so a row on it retires too: the deleting PR deletes or retargets it. An eight-field line (before PR 5)
    counts no refusal.
    """
    return entry is not None and entry["blob"] == blob and entry["status"] == REFUSED and entry.get("refused", 0) >= RETIRED_AT


def tier_of(row, entry, blob):
    """
    The tier of `row`, whose ledger line is `entry` (None when it has none) and whose file's current blob is `blob`:
    critical when the row says so (a critical row refused twice stays critical and runs every sweep; `--retire` lists it
    all the same); retired when `is_retired`, so it is not new again and a sweep plants it no more; new when the file is
    gone (`blob` None), when no line sits at this blob, or when the line there is not a catch (escaped, or refused once);
    proving when caught once there; proven when caught `PROVEN_AT` times or more.
    """
    if row.get(TIER_KEY) == CRITICAL:
        return CRITICAL
    if is_retired(entry, blob):
        return RETIRED
    if blob is None or entry is None or entry["blob"] != blob or entry["status"] != CAUGHT:
        return NEW
    return PROVEN if entry["caught"] >= PROVEN_AT else PROVING


class Tiers:
    """
    Value: the rows of a run's tables under their tiers (`TIER_WORDS`), each tier's rows in the order a sweep runs them
    (`TIERS`): the critical rows, the new ones and the proving ones in the tables' given order, the proven ones oldest
    date first; the retired rows in the tables' order, run by no sweep. `counts` says how many rows each of the five
    tiers holds; `selected` gives the rows of the named tiers, in the sweep's order, and never a retired row.
    """

    def __init__(self, rows_by_tier):
        self.rows = {tier: list(rows_by_tier.get(tier, ())) for tier in TIER_WORDS}

    def counts(self):
        """How many rows each tier holds, in the tiers' order, the retired ones last."""
        return {tier: len(self.rows[tier]) for tier in TIER_WORDS}

    def selected(self, tiers):
        """The rows of the tiers named in `tiers`, in the sweep's order; a tier not named gives none; `retired` is never run."""
        return [row for tier in TIERS if tier in tiers for row in self.rows[tier]]


def tiers_of(root, mutations, lines):
    """
    The `Tiers` of `mutations` under `root`, read against the ledger's `lines`: each row's file is hashed as it is now
    (a missing file hashes to None, so its rows are new and the run refuses them, or retired once refused twice there),
    and each row meets its line by key.
    """
    by_key = {entry["key"]: entry for entry in lines}
    blobs = blobs_now(root, mutations)
    found = {tier: [] for tier in TIER_WORDS}
    for row in mutations:
        entry = by_key.get(row_key(row))
        found[tier_of(row, entry, blobs[row["file"]])].append((entry, row))
    found[PROVEN].sort(key=lambda pair: _when(pair[0]["date"]))  # a stable sort: the same date keeps the tables' order
    return Tiers({tier: [row for _, row in pairs] for tier, pairs in found.items()})


def same_line_key(find):
    """
    The line a `find` anchors on, for `same_line_groups`: its lines with their indentation stripped and the trailing line
    break dropped (the review of PR 6: 15 pairs of rows mutated one line with finds that differed only so). Two finds on
    one file with one key sit on one place, because each occurs exactly once and one contains the other's text.
    """
    return tuple(line.strip() for line in find.strip().splitlines())


def same_line_groups(rows):
    """
    The same-line groups of `rows`, in the rows' order: each is the rows on one `file` and one line (`same_line_key` of
    their `find`) whose replaces are not all the same, two rows or more. A row alone on its line is in no group, and rows
    with one replace too are one row twice (PR 0 dropped those), so they make no group on their own. A row keeps whatever
    keys the caller gave it.
    """
    found = {}
    for row in rows:
        found.setdefault((row["file"], same_line_key(row["find"])), []).append(row)
    return [group for group in found.values() if len({row["replace"] for row in group}) > 1]


def lines_now(entries, blob):
    """The ledger lines `entries` (None for a row with none) that sit at the file's current blob `blob`; None for one that does not."""
    return [entry if entry is not None and entry["blob"] == blob else None for entry in entries]


def group_verdict(current):
    """
    A same-line group's verdict from `current`, its rows' ledger lines at the file's current blob (`lines_now`; None for a
    row with none there). `DISTINCT` when the lines there disagree already, whatever is still to run: a status is not a
    catch, a `by` differs, or a `by` is `suite` (no red line named a test module, so nothing says
    one module sees both mutants); `NOT_YET_RUN` when no line disagrees and a row has none at this blob (never run, or
    the file changed since); `MERGE_CANDIDATE` when every row has a line there, caught, by one and the same test module.
    A candidate to read, not a proof: `by` is the module, and two mutants of one line may be told apart by two functions
    in it; the deleting PR opens the module before it drops a row.
    """
    known = [entry for entry in current if entry is not None]
    if any(entry["status"] != CAUGHT or entry["by"] == SUITE for entry in known) or len({entry["by"] for entry in known}) > 1:
        return DISTINCT
    if len(known) < len(current):
        return NOT_YET_RUN
    return MERGE_CANDIDATE


def blobs_now(root, mutations):
    """The current blob of each file the rows of `mutations` name, by file, read once each; a missing file is None."""
    blobs = {}
    for file in {row["file"] for row in mutations}:
        path = Path(root) / file
        blobs[file] = blob_of(path.read_bytes()) if path.is_file() else None
    return blobs


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
