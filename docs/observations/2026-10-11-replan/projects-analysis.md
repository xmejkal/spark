# Projects, spark and the safety net (2026-10-11; spark origin/main b5a19bb)

## 1. Entwined today
- **In spark:** `tests/data/` (5 snapshot fixtures, 2 breadboard projects), `docs/observations/2026-10-11-baseline.json`, 48 dated output blocks in `docs/guide/` (journey 35).
- **`tools/check_docs.py:20-22`** demands a date note on each output and bans "smartbin-local"; it never re-checks recorded counts.
- **Tests:** `test_boards.py:316` pins the bin's Makefile calls (on a temp project); `test_orphans.py:32` reads sibling Makefiles; `test_emit_footprint.py:38` reads `../smartbin-local` (skipped elsewhere).
- **`tools/snapshot.py:68-97`** hardcodes `~/Development/{smartbin-local,irrigation,plant-alarm}`; by hand, not in the gate.
- **Push gate** (`check_commit.py`): suite, anchors, then `check_backlog`, which reads the bin's board by `gh`. No project files.
- **Install ships everything:** `"source": "./"`; archive 9.8 MB, ~1.3 MB runtime (scripts, parts, skills, commands, boards, agents, data, converter), ~8.5 MB dev (docs 5.3, tests 2.1, tools 0.9, scrum 0.3). The cached 0.4.0 equals its commit's tree; `installed_plugins.json` says 0.4.0.
- **Bin:** Makefile calls six spark scripts via `SPARK ?= $(HOME)/Development/spark`; CI skips them (private repo). It carries 30 converter files, diverged from spark's (P32b, bin #6). P188 (#137) pins four calls. The PO's SessionStart hook runs `spark/tools/board.py status`.

## 2. Cost since 2026-09-27 (estimates)
Spark: 590 commits, ~154,000 changed lines: docs/scrum 44%, tools 18%, tests+mutation tables 16%, product code 12%, guides 2.6%, fixtures+baseline 2.6%.
Project-tied: `docs/guide` 61 commits, snapshot/fixtures/baseline 13: ~74 (~13%), ~9,000 lines (~6%); an upper bound. The bin: 25 commits, none after 10-09.
Mainly project work: P104 (#40), P97's journey fixes (#98), P184 (#133: 31 council findings), P191 (#143), P190 (#142, from B31). Open: P77 (#13), P130 (#64), P102f (#30).

## 3. The safety net
- **Per push:** suite 1,803 tests, 39.4 s here today, plus anchors (1,348 mutations, 120 tables, 0.16 s). No mutation runs.
- **Pushes:** at least 146 since 09-27 (remote-tracking reflogs; deleted branches' logs are gone), so at least ~97 min of suite. The PO's note: ~17 of ~60 gate minutes wasted (10-09).
- **Mutations:** DoD 2 asks one table per change; all tables once per epic (`scrum/README.md:304`). One table, 17 mutations, took 145 s (~8.5 s each); a full sweep is ~3 h (estimate); no timing is recorded.
- **TDD:** of 271 commits touching code or tests, 226 (83%) carry both, 26 tests only, 19 code without a test file. Of 8 merged PRs sampled (#147, 146, 141, 117, 115, 109, 120, 125), 1 was test-first (#115, the only "(red)" commits: 3 of 590) and 7 committed test and code together. What is enforced is mutation-after, not red-first.

## 4. Options
| | moves | saves | costs / risk |
|---|---|---|---|
| a. Rule | projects and recorded runs change only after an epic, on the PO's yes | most of the ~13% | guides stale between epics; low |
| b. Fixtures | snapshot and baseline read `tests/data` only; outside projects optional | no sibling reads; reproducible | less real coverage; medium |
| c. Repos | the three projects to `spark-demos` (P102f), pinning a spark tag | gate, tests, hook stop reading siblings | repos, history audit, pin bumps; medium-high |
| d. Slim payload | plugin into `plugin/` or a git-subdir source | ~8.5 of 9.8 MB per install | no exclude field exists; every script path changes; high |

Subdir sources exist (official list here: 53 relative, 98 git-subdir, of 315).

## 5. Recommendation
Do (a) now with (b) as the chore; (c) with P102f and P32b; (d) after v1, ideally with the v2 core.

**Chore:** *P194 — Demo projects and recorded runs take ~13% of spark's commits while validation reads three outside folders → projects change only after an epic on the PO's yes, and spark validates on fixtures it carries.*
Needed by: the PO, 2026-10-11, verbatim: *"the demo project updates or recreatino can be dne after a bigger epic or something by asking the PO … howver, if its for the validation part, for testing purposes, it's different"*.
Value proven by: `python3 tools/snapshot.py --out <dir>` exits 0 with the three folders absent; `grep -rn "Development/" tests tools scripts` finds no sibling path; `docs/guide` plus `tests/data` stay under 13% of the next 100 commits.
Placement: Idea, after v1, beside P158 (#94, the v2 candidate); links P102f, P173, P188, P77.
