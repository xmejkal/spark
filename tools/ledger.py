"""
The mutation ledger (P787): one line per mutation row that a run planted, so a sweep knows which rows were caught, when,
and at which content of their file. `mutate.py` writes it after every run that plants rows; the tiers (PR 2) read it.

    tests/mutations/ledger.jsonl
    {"key": "4a1f0c9e2b7d", "file": "tools/mutate.py", "blob": "<40 hex>", "date": "2026-11-12T18:04:11+01:00",
     "status": "caught", "by": "test_mutate", "caught": 1, "s": 7}

`key` is the row's identity (`row_key`); `blob` is git's hash of the file the row was planted in, as the run read it;
`date` is the run's start, with its zone; `status` is the run's word for the row (`caught`, `escaped`, `refused`); `by`
is the test module that caught it, `suite` when the whole suite did, `escape` when none did, and null when the row was
refused and nothing ran; `caught` counts the catches at this `blob` (a changed file starts the count again); `s` is the
row's seconds. The file is in git and rewritten whole, sorted by key, so two branches merge line by line and the newer
date wins (`merged`). An empty ledger is empty: nothing seeds it.

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
