# Store 1c — picks to a building list, tallied — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The plant alarm's picks become a board that builds — the bin's FireBeetle S3 refused as already held, owed facts
filled once in each record's own home, `check_spine` ending `[ok]` with no placeholder outline — and one line saying what
the run cost and what came from the store (backlog P97, spark#18).

**Architecture:** Two refactors and the P96 review's carry-overs come first: one candidate builder, one way to say a
write, aliases read safely, a broken board marked, a project's own reservation free to it, a count left out read as
"owned, count unknown", and one writer at a time with every write whole. Then the store gains its history
(`history.jsonl`, §5.7), `needs.json` gains `pick`, and `parts.py --pick` reserves what the person owns — refusing past
what another project holds. spark's one door to the network and the document store's checked keep go into `store.py`
(§6.2, §6.5). `parts.py --fact-set` fills an owed fact in its record's own home, and `--requirements` turns the picks
into `requirements.json`, shelving a catalog pick on the way. `check_spine` records `built`. A new `scripts/cost.py`
reads each step's session transcripts for `parts.py --tally`'s cost line, replacing `tools/research_cost.py`.

**Tech Stack:** Python 3 standard library (`scripts/`), `unittest`, `tools/mutate.py`; tscircuit borrowed from the bin's
`node_modules` for the two runs that build (Tasks 11 and 12), never in the suite.

**Spec:** `docs/2026-10-04-store-design.md` v2 — §4 "Store 1c" (C1, C2, L1, T1 and its foundations), §5.2, §5.3, §5.4,
§5.5, §5.7, §6.2 (the document store, the cost counter, the fetcher), §6.4, §6.5, §6.7, §8 C, L and T, §9 step 3. The
card: spark#18 and the PO's three decisions of 2026-10-06 in its comment. Builds on P95 and P96 (merged): `store.py`,
`drawer.py`, `needs.py`, the envelope. The carry-overs come from the P96 fix plan
(`docs/2026-10-05-store-1b-fixes-plan.md`, Task F and its deferred list), recorded on P97's archive entry.

## Global Constraints

- **Branch `p97-store-1c`**, cut from `origin/main` 51841d5; this plan is its first commit. The work reaches `main` by
  one pull request that says `Closes #18` (W8, W19); the PO merges. Nothing of another item rides on it.
- **The suite never touches the person's store or the person's transcripts.** A test that needs a store sets
  `SPARK_HOME` with `mock.patch.dict(os.environ, …)` (or `in_store(home)` in `tests/test_parts.py`); a test that
  reads transcripts also sets `HOME` to a scratch folder, so `~/.claude` is never read. Fixtures are synthetic. Never
  mutate the suite guard in `scripts/store.py` (`if "unittest" in sys.modules:`) or the `SPARK_HOME` branch of
  `store.home()`. The real store and `~/.claude` are read and written in Task 12 only, with the PO.
- **No network on the default path.** The suite opens no URL: the fetcher's tests use `file://` URLs of temp files, and
  a test that would reach further patches `store.fetch`. After Task 7 only `store.fetch` opens a URL (§6.5);
  `tools.py`'s installs stay with `/spark:setup`.
- **W2 — a test runs the thing and writes its values as literals.** No expected value built from the module under test;
  a module constant a test reads needs a `MAY_READ` entry in `tests/test_self_confirmation.py` (this plan needs none —
  never read `cost.NETWORK_TOOLS`, `needs.PICKS`, `store.EVENT_KEYS` or the like in a test). The one source scan this
  plan adds (only `store.py` opens a URL) follows the store's existing architecture pin
  (`test_only_the_store_says_where_the_store_is`).
- **W14 — pull, never push.** Only §4 store 1c's stories and the carry-overs. Not here: G and the researcher seam,
  `simulated` and `ran`, proof and "passed over elsewhere" in `--match`, the 18 `//why_not` notes as history lines, the
  drawer's own cost line, P90's restore and manifest, the other ways in.
- **W16 — a replacement deletes what it replaces, in the same commit.** `tools/research_cost.py` goes with
  `scripts/cost.py`, and so do the two guide lines naming it. `_download`'s and `reachable`'s own `urlopen` and
  `parts.py`'s `import urllib.request` go with `store.fetch`. `keep_in_store`'s direct write goes with `store.keep`. The
  hand-written write-and-rename in `store.write_json` and `needs.write` goes with `store.write_file`. The drawer's and
  the needs file's own write lines go with `_write_lines`.
- **W21 — keep a datum only if a decision rests on it.** The history keeps ids, project names, the person's reasons and
  counts — never a URL, a query, a path, a price or an order number (§5.7). A catalog record promoted onto the shelf
  carries no `based_on`: nothing reads it.
- **W13 — numbers only after output.** A count or a verdict enters a commit message, an issue comment or the Done line
  only in a later call than the run that printed it. A proof asserts the verdict string
  (`grep -q "the chain runs end to end"`), never the presence of output. A number not yet run says *estimate* (W20).
- **The envelope (§6.4).** Every new operation is a row of `OPERATIONS` (so `--describe` lists it), answers in the one
  envelope, takes `--dry-run`, refuses all or nothing, and holds ids only on its command line — a reason travels in a
  file. `commands/idea.md` keeps the text-is-data paragraph word for word.
- **Size (W15b, P99).** There is no cap: since P99 `tests/test_orphans.py` holds no budget, and the pre-push gate
  prints `scripts/: N code lines (+M since origin/main)`. `scripts/` is **5,529 code lines** on `origin/main` 51841d5
  (measured 2026-10-06 with `tools/check_commit.py`'s `size_line`). §9 estimated about 180 for 1c; this plan estimates
  about +275 (the size table below says why). The Done line says the measured growth and why.
- **Mutations (W3).** Each code task ships `tests/mutations/p97-<name>.json`, every mutation caught:
  `python3 tools/mutate.py tests/mutations/p97-<name>.json`, in the foreground, with a 600000 ms timeout. Before every
  commit, `python3 tools/mutate.py --anchors tests/mutations/*.json` is clean; re-point every row it names in the same
  commit and run each table you touched. The rows this plan already knows will move are listed in each task. After a
  killed run, `git diff --stat` before going on: a killed run can leave a file mutated.
- **Commands**, from the root of a checkout of `p97-store-1c` (on 2026-10-06: `~/Development/spark-p146`):
  - one test: `python3 -m unittest discover -s tests -t tests -p '<file>' -k <name>` (`-k` is case-sensitive and
    matches part of a test's name; give it several times for several);
  - the suite: `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3`.
- **Commits** end with the `Co-Authored-By` trailer your environment gives (on 2026-10-06:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). Shell: `/usr/bin/grep` for any count or scan whose result
  is reported; never a zsh loop variable named `path`; an unquoted `$var` does not word-split in zsh.

## Review Focus

1. **One `--pick` naming several needs where one pick is refused** (the person picks everything at once, and the bin
   holds the board) — expected: nothing is written at all, no pick, no reservation, no history line. Test in Task 6
   (`test_a_refused_pick_writes_nothing_at_all`).
2. **A need picked again with another part** (the person changes their mind) — expected: the old part's reservation is
   freed in the same write, and nothing is held twice. Test in Task 6 (`test_a_re_pick_frees_what_it_no_longer_picks`).
3. **The same part picked for two needs** (two buttons, open and mode) — expected: the requirements file names each
   instance after its need, so the build does not refuse two components of one name. Test in Task 9
   (`test_a_part_picked_for_two_needs_is_named_after_each`).
4. **A `requirements.json` the person extended by hand** (`signals`, `rails`, as `/spark:build`'s page documents) —
   expected: `--requirements` sets `board` and `parts` and keeps every other key. Test in Task 9
   (`test_what_the_person_added_to_the_file_stays`).
5. **A tally with no transcript** (spark run outside Claude Code, or the harness has cleaned old transcripts away) —
   expected: could-not-run, and the line says the cost was not counted — never "0 requests". Test in Task 10
   (`test_no_transcript_is_could_not_run_never_zero`).

## Rulings this plan makes, for the PO

1. **The DFR0954's footprint is filled in spark's repository**, by a commit on this branch in Task 12. Its record lives
   in spark's library, which `--function-set` already refuses (P96 fix B, your ruling of 2026-10-05); `--fact-set`
   refuses it the same way. The drawing comes in through `parts.py --fetch` — the one counted request — into your
   store; the record keeps only the pointer (B12: no vendor file in spark's history).
2. **A step's end is derived, not stored** (§3, §5.7 and §6.7 amended in Task 10). `parts.py --step <project> <step>`
   writes one line when a step starts; the step ends where the next step of its session starts, or at the session's
   last transcript line. An append-only history cannot fill in an end later, and a second line per step would repeat
   its key.
3. **Promotion into the shelf happens when the requirements file is written**, for a pick whose record owes nothing.
   The catalog copy stays (store slice 1 deletes nothing, §6.4.5); the shelf copy is nearer, so it is what every
   project reads and what a later `--fact-set` writes.
4. **`--fact-set` sets only the facts the chain reads** (`footprint`, `pin_order`, `pin_order_proof`, `body_mm`,
   `simulation`), never empties one, and refuses a value that breaks the record. `--function-set` keeps its name and
   its answer, through the same helper.
5. **A new drawer entry needs only a label** — your decision of 2026-10-06: no `count` means owned, count unknown, and
   a pick says so. §5.2's "Required: `label`, `count`" is amended with it (Task 3). Measured 2026-10-06: none of the 110
   entries in your drawer lacks a count, your own-words ones included. The decision changes no entry today; it decides
   what a count left out means from now on.
6. **"From the store" is a `reused` line written when a part is picked** — every pick in 1c, since nothing is
   researched yet. G's item will leave out what its own research found.
7. **`built` is written by `check_spine` itself**, when the chain runs end to end for a project on your list — never by
   an agent's say-so (W1).
8. **P90 (#21) and P89 (#20) stay their own items.** The fetcher here is one door and one checked keep; restoring
   documents on a new machine, same/DIFFERS, a manifest, and `tools.py` sharing the door are P90's. Only SEN0193's
   `pin_order_proof` is filled here, by `--fact-set` from its `//pin_order` note, because the plant alarm builds with
   it; the 18-record migration stays P89's.
9. **Not in 1c, because §4 does not run them:** proof and passed-over-elsewhere in `--match` (P96's ruling 3 waited for
   the history, which lands here; the first project to read them is the second one, P100); the drawer import's cost
   line.

## Open questions for the PO — answered 2026-10-07 (recorded on spark#18)

- **Execution:** subagent-driven, the PO's choice.
- **1 — not the default.** The S3 and the LiPo stay held by the bin. The alarm's real run (Task 12) takes another
  ESP32 from his drawer, which he picks on the spot (Beetle ESP32 C6 Mini ×3 and Beetle ESP32 ×2 beside the S3; a
  board without a record cannot build, so the run may end at the refusal and the pick, with `check_spine [ok]`
  proven by Task 11). The refusal itself still proves "already held". His wider answer — offer every owned module
  with the same function and recommend the minimal one that fits — is P157 (spark#93), designed with him later.
- **2 — the default:** the potentiometer stand-in.
- **3 — the default:** report what is actually counted.

The questions as they were asked, each with the default the plan followed before the answer:

1. **The board for the plant alarm after the refusal.** The S3 is the only board that builds today (the XIAO C6 stops
   at the footprint stage, P121), and the bin holds both the S3 and the LiPo. **Default:** in the real run (Task 12)
   you free both from the bin for the alarm, as §8 C's example says, and the bin reserves them again when its bench
   bring-up (B14) starts. The other road: they stay with the bin; the real run then ends at the refusal, and
   `check_spine [ok]` is proven by Task 11's scratch run only.
2. **SEN0193's `simulation`** (§8 L: "a stand-in or a skip, decided in 1c"). **Default:** a stand-in, Wokwi's
   potentiometer on the signal pin, saying it gives a level a scenario sets and does not model soil, the probe's
   1.2–3.0 V range or its drift. If the converter refuses it in Task 12, a skip with that reason.
3. **"1 request".** The drawing's URL is recorded nowhere: the record names its file
   (`DFR0954_max98357a-i2s_dimension_1.0.pdf`) and the wiki page (checked 2026-10-06). Reading the wiki page to find
   the URL is a second counted request, and the line then says "2 requests". **Default:** count what happens and report
   it (W13, W20). The other road: you paste the drawing's URL from your browser, and spark's one fetch is the one
   request.

## The carry-overs from P96's review, checked against the code (2026-10-06, `origin/main` 51841d5)

None is done; all eight are still present.

| carry-over | where it is today | task |
| --- | --- | --- |
| one candidate builder (P96 fix plan F1) | `scripts/needs.py:148-152` and `:159-162` build the same candidate dict twice | 1 |
| shared write lines (F2) | `scripts/parts.py:1603-1610` (`_drawer_answer`) and `:1754-1757` (`_op_needs_set`) each compose their own lines | 1 |
| `drawer.numbers` and an alias that is no list | `scripts/drawer.py:129` raises TypeError on an integer; worse, a string alias becomes its single characters as exact part numbers (reproduced: `"DFR0954"` gives `{'0','4','5','r','f','d','9'}`); `parts._matches` reads it unguarded too (`scripts/parts.py:1204`) | 2 |
| `--match` marking a broken board | `scripts/needs.py:152`: `"broken": kind == "part" and …` never marks a board | 2 |
| a project's own reservations free to it | `scripts/needs.py:122` subtracts every project's `used_in`, the asking project's own included | 2 |
| the PO's question: a drawer entry with no `count` | answered 2026-10-06 (owned, count unknown); today a missing count reads as 0 owned (`scripts/needs.py:121`) and a new entry needs a count (`scripts/drawer.py:207-208`) | 3 |
| the lock and atomic writes | no lock anywhere in `scripts/`; `parts.main` runs each write unguarded (`scripts/parts.py:1801`); `_write_record`'s project write (`:1656`), `fetch_documents`' (`:1143`) and `keep_in_store`'s (`:930`) write in place | 4, 7 |
| `--function-set` on a shelf copy, through `based_on` | `scripts/parts.py:1645-1648` resolves to the shelf copy and `:1651-1656` writes it; `based_on` is written (`:841`) and read nowhere | 8 |

## Size, estimated (W20: estimates until measured)

| task | code lines in `scripts/` |
| --- | --- |
| 1 refactors | about 0 |
| 2 what a candidate says | about +9 |
| 3 a count left out | about +3 |
| 4 one writer, whole writes | about +12 |
| 5 the history | about +20 |
| 6 picks and reservations | about +70 |
| 7 the fetcher and the checked keep | about +8 |
| 8 `--fact-set` | about +18 |
| 9 the requirements file, the shelf, `built` | about +38 |
| 10 the cost counter and the line | about +100 |
| **total** | **about +275** |

Why above §9's 180: the carry-overs (about +25) were not known then; the history needs its own reader and its keys,
and the steps their windows (about +30); and the counter keeps what `tools/research_cost.py` measured — tokens, runs by
agent type, one transcript on its own — so its deletion loses nothing (about +25).

---

## File structure

| file | what changes |
| --- | --- |
| `scripts/store.py` | `project_name` (T2); `write_file`, `locked` (T4); the history: `events`, `append_event` (T5); `add_project(dry_run)` (T6); `fetch`, `keep` (T7); the suite's session (T10) |
| `scripts/needs.py` | `_candidate` (T1); `mine`, aliases, a broken board (T2); a count left out (T3); `write` through the store (T4); `pick`: `PICKS`, a `CHECKS` row, `_pointing`, `_held`, `_resolve`, `plan_pick` (T6); `requirements` (T9); `owned` (T10) |
| `scripts/drawer.py` | `numbers` through `parts.aliases` (T2); a new entry needs only a label (T3) |
| `scripts/parts.py` | `_change_line`, `_write_lines` (T1); `aliases` (T2); the drawer's "?" (T3); the lock in `main`, `_write_record`, `fetch_documents` (T4); `--pick`, `--passed-over` (T6); `_download`, `reachable`, `keep_in_store` (T7); `_record_path`, `_set_in_home`, `--fact-set` (T8); `shelve(…, project_name=None)`, `digest(…, facts)`, `BOARD_FACTS`, `note_built`, `--requirements` (T9); `--step`, `--tally` (T10) |
| `scripts/cost.py` (create) | the counter and the cost line (T10) |
| `scripts/check_spine.py` | `built` when the chain runs end to end (T9) |
| `tools/research_cost.py` (delete) | T10 |
| `commands/idea.md` | C (T6); L's fact write and the shelf sentence (T8); L (T9); the steps and T (T10) |
| `commands/drawer.md`, `commands/build.md` | a count left out (T3); `built` (T9) |
| `README.md`, `AGENTS.md`, `docs/guide/journey.md`, `docs/guide/commands.md` | P76 → P97 for the requirements file (T9, the PO's decision 2); `research_cost.py` (T10) |
| `docs/guide/agents.md` | the list of writes (T6, T8, T9, T10) |
| `docs/guide/developing.md` | `research_cost.py` → `cost.py` (T10) |
| `docs/2026-10-04-store-design.md` | §5.2 (T3); §4 L1 (T9); §3, §5.7, §6.7 (T10) |
| `parts/max98357a-dfr0954.json` | `sources`, `documents`, `footprint` (T12) |
| `tests/test_needs.py`, `test_parts.py`, `test_drawer.py`, `test_store.py`, `test_check_spine.py`; `tests/test_cost.py` (create) | as each task says |
| `tests/mutations/p97-*.json` (create) | one per code task |

---

### Task 0: The branch, measured

- [ ] **Step 1:** `git status --short && git log --oneline -1` — expected: nothing listed; the head is this plan's commit
  on `p97-store-1c`.
- [ ] **Step 2:** the suite — expected: `Ran 1171 tests` and `OK (skipped=1)` (measured 2026-10-06 on 51841d5; the
  plan adds no test).
- [ ] **Step 3:** `python3 tools/mutate.py --anchors tests/mutations/*.json | tail -1` — expected:
  `596 mutation(s) in 95 table(s): every anchor present, once`.
- [ ] **Step 4:** move card #18 to the working stage the flow in `scrum/README.md` names, as that page says.

---

### Task 1: The two refactors only P97 needs — one candidate builder, one way to say a write

**Files:** Modify `scripts/needs.py` (`candidates`, new `_candidate`), `scripts/parts.py` (`_change_line`, new
`_write_lines`, `_drawer_answer`, `_op_needs_set`). Test `tests/test_needs.py` (`TheNeedsFileTest`). Create
`tests/mutations/p97-refactors.json`. Re-point two rows (Step 5).

**Interfaces:**
- Produces: `needs._candidate(need, functions, names, holding, said) -> dict`, the one candidate shape
  `{"id", "kind", "entry", "in", "label", "what", "what_matches", "owned", "free", "unsure", "owes", "broken", "proof"}`.
- Produces: `parts._change_line(change, dry_run) -> str` for a drawer change (`change["entry"]`) and a needs change
  (`change["need"]`) alike; `parts._write_lines(changes, problems, dry_run, said=()) -> [str]`: each change (marked
  `refused, not written:` when anything was refused), then `said`, then each refusal — or `["  nothing to change"]`.
- One output changes: a needs write now says what each value was — `would set soil: mark null → "have"`.

- [ ] **Step 1: The failing test.** In `tests/test_needs.py`, class `TheNeedsFileTest`, after
  `test_a_new_need_with_no_what_is_refused`:

```python
    def test_a_needs_write_says_what_each_value_was(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}]), "--dry-run"])
        self.assertEqual(out.getvalue(), '  would set soil: mark null → "have"\n')
```

- [ ] **Step 2: Run it.** `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k says_what_each_value_was`
  — expected: FAIL, the line reads `  would set soil: mark → "have"`.

- [ ] **Step 3: The code.** In `scripts/needs.py`, below `_counts`, add:

```python
def _candidate(need, functions, names, holding, said):
    """One candidate (§6.2): `said` names it and where it lives; the rest is what its verb's functions say, and its counts."""
    owned, free, unsure = _counts(holding)
    return dict({"id": None, "kind": None, "entry": None, "owes": [], "broken": False, "proof": []}, **said,
                what=sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                what_matches=_what_matches(need, functions, names), owned=owned, free=free, unsure=unsure)
```

In `candidates`, replace the record loop's last lines

```python
        owned, free, unsure = _counts(holding)
        found.append({"id": record_id, "kind": kind, "entry": None, "in": where, "label": record.get("name"),
                      "what": sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                      "what_matches": _what_matches(need, functions, names),
                      "owned": owned, "free": free, "unsure": unsure, "owes": [] if kind == "board" else parts.owes(record),
                      "broken": kind == "part" and bool(parts.broken_problems(record, path)), "proof": []})
```

with

```python
        found.append(_candidate(need, functions, names, holding,
                                {"id": record_id, "kind": kind, "in": where, "label": record.get("name"),
                                 "owes": [] if kind == "board" else parts.owes(record),
                                 "broken": kind == "part" and bool(parts.broken_problems(record, path))}))
```

and the drawer loop's last lines

```python
        owned, free, unsure = _counts([entry])
        found.append({"id": None, "kind": None, "entry": entry_id, "in": "drawer", "label": entry.get("label"),
                      "what": sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                      "what_matches": _what_matches(need, functions, [entry.get("label")]),
                      "owned": owned, "free": free, "unsure": unsure, "owes": [], "broken": False, "proof": []})
```

with

```python
        found.append(_candidate(need, functions, [entry.get("label")], [entry],
                                {"entry": entry_id, "in": "drawer", "label": entry.get("label")}))
```

In `scripts/parts.py`, replace `_change_line` with:

```python
def _change_line(change, dry_run):
    """
    One set-only write's change (§5.2), the drawer's and the needs file's alike: '  new soil-probe: soil probe × 8 — is
    part sen0193-soil-moisture' for a new drawer entry, else '  set soil: mark null → "have"', every value from what it was.
    """
    if change["new"] and "entry" in change:
        now, linked = change["now"], change["now"].get("is")
        return "  %s %s: %s × %s%s" % ("would add" if dry_run else "new", change["entry"], now.get("label"), now.get("count"),
                                         " — is %s %s" % next(iter(linked.items())) if linked else "")
    return "  %s %s: %s" % ("would set" if dry_run else "set", change.get("entry") or change.get("need"), "; ".join(
        "%s %s → %s" % (key, json.dumps(change["was"].get(key), ensure_ascii=False), json.dumps(value, ensure_ascii=False))
        for key, value in change["now"].items()))


def _write_lines(changes, problems, dry_run, said=()):
    """
    What a set-only write did or would do (§5.2), said one way for every write: each change — marked when anything was
    refused, because then nothing is written — what else the write has to say, then each refusal; or that nothing changes.
    """
    lines = [("  refused, not written: " + _change_line(change, dry_run).strip()) if problems else _change_line(change, dry_run)
             for change in changes] + list(said)
    lines += ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]
    return lines or ["  nothing to change"]
```

Replace `_drawer_answer`'s lines and return (from `lines = [(("  refused, not written: "` to its end) with:

```python
    said = ["  ? %s" % q["sentence"] for q in questions] + [
        "  not shelved: %s — it does not meet the part contract yet, so it stays in its project and the entry still links to it"
        % stem for stem in left]
    return Answer({"changes": [{key: change[key] for key in ("entry", "new", "was", "now")} for change in made],
                   "questions": questions, "shelved": shelved, "not_shelved": left, "written": not (problems or dry_run)},
                  _write_lines(made, problems, dry_run, said), problems=problems)
```

In `_op_needs_set`, keep `written = …` and the `if written and changes:` write, and replace the `lines` lines and the
return with:

```python
    return Answer({"changes": changes, "written": written}, _write_lines(changes, problems, args.dry_run), problems=problems)
```

- [ ] **Step 4: Run** Step 2's command, then `-p 'test_drawer.py'`, then the suite. Expected: PASS; the suite `OK`.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-refactors.json`:

```json
[
 {"file": "scripts/needs.py", "name": "a candidate's words never match",
  "find": "what_matches=_what_matches(need, functions, names), owned=owned", "replace": "what_matches=False, owned=owned"},
 {"file": "scripts/needs.py", "name": "a candidate's counts are lost",
  "find": "owned=owned, free=free, unsure=unsure)", "replace": "owned=0, free=0, unsure=unsure)"},
 {"file": "scripts/parts.py", "name": "a needs write hides what each value was",
  "find": "\"%s %s → %s\" % (key, json.dumps(change[\"was\"].get(key), ensure_ascii=False), json.dumps(value, ensure_ascii=False))",
  "replace": "\"%s → %s\" % (key, json.dumps(value, ensure_ascii=False))"},
 {"file": "scripts/parts.py", "name": "a needs change is named as a drawer entry",
  "find": "change.get(\"entry\") or change.get(\"need\")", "replace": "change.get(\"entry\")"}
]
```

Re-point, in the same commit:
- `sprint-10-p96-final.json`, "text mode hides a refused needs-set": find
  `    lines += ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]\n    return lines or ["  nothing to change"]`,
  replace `    return lines or ["  nothing to change"]`.
- `sprint-10-p96-fix-d.json`, "a refusal also says nothing to change": find `    return lines or ["  nothing to change"]\n`,
  replace `    return lines + ["  nothing to change"]\n`.

Run the anchors check, re-point anything else it names, then run `p97-refactors.json` and both re-pointed tables.
Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 1 (P96 fix plan F): one candidate builder; one way to say a set-only write — a needs write now says what each value was`

---

### Task 2: What a candidate says — an alias that is no list, a broken board, the project's own reservation

**Files:** Modify `scripts/parts.py` (new `aliases`, `_matches`), `scripts/drawer.py` (`numbers`), `scripts/needs.py`
(`_counts`, `_candidate`, `candidates`, `match`, `import boards`), `scripts/store.py` (new `project_name`). Test
`tests/test_drawer.py`, `tests/test_needs.py` (`TheMatcherTest`). Create `tests/mutations/p97-candidates.json`.
Re-point one row.

**Interfaces:**
- Consumes: `needs._candidate` (Task 1).
- Produces: `parts.aliases(record) -> [str]` — `also_known_as`'s strings when it is a list, else `[]`.
- Produces: `store.project_name(folder) -> str | None` — the name a project folder has on the person's list.
- Produces: `needs._counts(holding, mine=None)`, `needs._candidate(need, functions, names, holding, said, mine=None)`,
  `needs.candidates(need, known, entries, mine=None)`: what `mine` (a project's name) holds is free to it.

- [ ] **Step 1: Failing tests.** In `tests/test_drawer.py`, class `TheDrawerTest`, after `test_a_word_is_not_a_part_number`:

```python
    def test_an_alias_that_is_no_list_names_nothing(self):
        self.assertEqual(drawer.numbers({"sku": "X1", "also_known_as": "DFR0954"}, "x-part"), ({"x1"}, set()))
        self.assertEqual(drawer.numbers({"sku": "X1", "also_known_as": 7}, "x-part"), ({"x1"}, set()))
        (self.home / "catalog" / "x-odd.json").write_text(json.dumps(
            {"schema": 1, "id": "x-odd", "name": "Odd", "kind": "sensor", "also_known_as": 7}))
        said, code = run(["--drawer-set", a_file([{"label": "probe", "count": 1, "part_number": {"number": "SEN0193"}}])])
        self.assertEqual((code, self.entry("probe")["is"]), (0, {"part": "sen0193-soil-moisture"}),
                         "one odd record in the catalog takes no drawer write down")
```

In `tests/test_needs.py`, class `TheMatcherTest`, after `test_a_board_owes_nothing_and_is_never_broken_here`:

```python
    def test_a_broken_board_is_marked_broken(self):
        (self.project / "boards").mkdir(parents=True)
        (self.project / "boards" / "half-board.json").write_text(json.dumps({"schema": 1, "id": "half-board", "name": "Half a board"}))
        found = [c["broken"] for c in self.alone({"id": "mcu", "does": "compute", "what": "microcontroller"})["candidates"]
                 if c["id"] == "half-board"]
        self.assertEqual(found, [True])

    def test_a_project_s_own_reservation_is_free_to_it(self):
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        (self.home / "drawer" / "probe.json").write_text(json.dumps({"schema": 1, "label": "soil probe", "count": 8, "is": {"part": "x-soil"},
                                                                    "used_in": {"plant-alarm": 1, "smartbin-local": 2}}))
        soil = [c for c in self.alone({"id": "soil", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "x-soil"][0]
        self.assertEqual((soil["owned"], soil["free"]), (8, 6), "what plant-alarm holds is free to it; what the bin holds is not")
```

- [ ] **Step 2: Run them.**
  `python3 -m unittest discover -s tests -t tests -p 'test_drawer.py' -k alias_that_is_no_list` and
  `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k broken_board -k own_reservation`.
  Expected: the alias test fails on the string (single characters) and errors on 7 (TypeError); the board is `False`;
  free is 5, not 6.

- [ ] **Step 3: The code.** In `scripts/parts.py`, below `function_problems`:

```python
def aliases(record):
    """A record's other names (`also_known_as`) — only those that are words; a value that is no list names nothing (§5.5)."""
    said = record.get("also_known_as")
    return [alias for alias in said if isinstance(alias, str)] if isinstance(said, list) else []
```

and in `_matches`, replace `" ".join(record.get("also_known_as") or [])` with `" ".join(aliases(record))`.

In `scripts/drawer.py` `numbers`, replace
`    aliases = [alias for alias in record.get("also_known_as") or [] if isinstance(alias, str)]` with
`    aliases = parts.aliases(record)`.

In `scripts/store.py`, below `projects`:

```python
def project_name(folder):
    """The name a project's folder has on the person's list (§5.5), or None when it is not on it."""
    folder = Path(folder).resolve()
    return next((name for name, where in projects().items() if where.resolve() == folder), None)
```

In `scripts/needs.py`, add `import boards` above `import drawer`. Replace `_counts` and `_candidate` with:

```python
def _counts(holding, mine=None):
    """
    (owned, free, unsure) over the live drawer entries (callers pass none said to be dead) — `many` stays many, and what
    `mine`, the asking project, holds is free to it: only other projects' reservations are not free.
    """
    unsure = any(entry.get("unsure") for entry in holding)
    if any(entry.get("count") == "many" for entry in holding):
        return "many", "many", unsure
    owned = sum(entry.get("count", 0) for entry in holding)
    held = sum(n for entry in holding for who, n in (entry.get("used_in") or {}).items() if who != mine)
    return owned, max(owned - held, 0), unsure


def _candidate(need, functions, names, holding, said, mine=None):
    """One candidate (§6.2): `said` names it and where it lives; the rest is what its verb's functions say, and its counts."""
    owned, free, unsure = _counts(holding, mine)
    return dict({"id": None, "kind": None, "entry": None, "owes": [], "broken": False, "proof": []}, **said,
                what=sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                what_matches=_what_matches(need, functions, names), owned=owned, free=free, unsure=unsure)
```

Replace `candidates` and `match` with:

```python
def candidates(need, known, entries, mine=None):
    """
    The store's candidates for one need (§6.2's code half): every record and every record-less drawer entry whose function
    has the need's verb, owned first, then those whose `what` is the need's, nearest first. Similar enough is the agent's call.
    What `mine`, the asking project, holds is free to it.
    """
    pointing = {}
    for entry in entries.values():
        if not entry.get("skip") and isinstance(entry.get("is"), dict) and entry["is"]:
            pointing.setdefault(next(iter(entry["is"].items())), []).append(entry)
    found, known_keys = [], set()
    for kind, record_id, where, path in known:
        record = parts._parse(path)
        holding = pointing.get((kind, record_id), [])
        if not isinstance(record, dict):
            continue
        known_keys.add((kind, record_id))
        functions = parts.function_of(record, board=kind == "board") + [f for e in holding for f in e.get("function") or []]
        if not any(f.get("does") == need["does"] for f in functions):
            continue
        names = [record.get("name")] + parts.aliases(record)
        found.append(_candidate(need, functions, names, holding,
                                {"id": record_id, "kind": kind, "in": where, "label": record.get("name"),
                                 "owes": [] if kind == "board" else parts.owes(record),
                                 "broken": bool(parts._shape_problems(boards.validate, record, path, "board definition")) if kind == "board"
                                 else bool(parts.broken_problems(record, path))}, mine))
    for entry_id, entry in entries.items():
        functions = entry.get("function") or []
        points_at_a_record = isinstance(entry.get("is"), dict) and bool(entry["is"]) and next(iter(entry["is"].items())) in known_keys
        if points_at_a_record or entry.get("skip") or entry.get("count") == 0 or not any(f.get("does") == need["does"] for f in functions):
            continue
        found.append(_candidate(need, functions, [entry.get("label")], [entry],
                                {"entry": entry_id, "in": "drawer", "label": entry.get("label")}, mine))
    return sorted(found, key=lambda c: (c["owned"] == 0, not c["what_matches"],
                                        LAYERS.index(c["in"]) if c["in"] in LAYERS else len(LAYERS), c["id"] or c["entry"]))


def match(project):
    """Each need with its candidates (§6.2), and a problem for each need with no verb — it cannot be matched."""
    known, entries, matched, problems, mine = drawer.linkable(project), drawer.entries(), [], [], store.project_name(project)
    for need in read(project):
        if need.get("does") not in parts.VERBS:
            problems.append(parts._problem(need.get("id"), "a need with no `does` cannot be matched — set it with --needs-set"))
            continue
        if not need.get("what"):
            problems.append(parts._problem(need["id"], "a need with no `what` cannot be matched — set it with --needs-set"))
            continue
        matched.append(dict({key: need.get(key) for key in NEED_FIELDS}, need=need["id"],
                            candidates=candidates(need, known, entries, mine)))
    return matched, problems
```

- [ ] **Step 4: Run** Step 2's commands, then the suite. Expected: PASS; the suite `OK`.
  `test_a_board_owes_nothing_and_is_never_broken_here` still passes: the library's FireBeetle validates.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-candidates.json`:

```json
[
 {"file": "scripts/parts.py", "name": "an alias that is no list is iterated",
  "find": "[alias for alias in said if isinstance(alias, str)] if isinstance(said, list) else []",
  "replace": "[alias for alias in said or [] if isinstance(alias, str)]"},
 {"file": "scripts/needs.py", "name": "a broken board is never marked",
  "find": "bool(parts._shape_problems(boards.validate, record, path, \"board definition\")) if kind == \"board\"",
  "replace": "False if kind == \"board\""},
 {"file": "scripts/needs.py", "name": "a project's own reservation is not free to it", "find": " if who != mine)", "replace": ")"},
 {"file": "scripts/needs.py", "name": "the match does not know whose project it is",
  "find": "drawer.linkable(project), drawer.entries(), [], [], store.project_name(project)",
  "replace": "drawer.linkable(project), drawer.entries(), [], [], None"}
]
```

Re-point `sprint-10-p96-fix-a.json`, "aliases are trusted": file `scripts/parts.py`, find
`[alias for alias in said if isinstance(alias, str)] if isinstance(said, list) else []`, replace `list(said or [])`.
Run the anchors check, re-point anything else it names, run both tables. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 2: an alias that is no list names nothing (it took drawer writes down and made one-letter part numbers); --match marks a broken board; a project's own reservation is free to it`

---

### Task 3: A count left out — owned, count unknown (the PO's decision of 2026-10-06)

**Files:** Modify `scripts/needs.py` (`_counts`), `scripts/drawer.py` (`settle`), `scripts/parts.py` (`_op_drawer`),
`commands/drawer.md`, `docs/2026-10-04-store-design.md` (§5.2). Test `tests/test_drawer.py`, `tests/test_needs.py`.
Create `tests/mutations/p97-count-unknown.json`.

**Interfaces:**
- Produces: `needs._counts(…)` answers `("unknown", "unknown", unsure)` when a live entry has no `count` (after `many`,
  which still wins). A new drawer entry needs only a `label`. `--drawer` shows `?` for a count left out.

- [ ] **Step 1: Failing tests.** In `tests/test_drawer.py`, class `TheDrawerTest`, after `test_an_entry_needs_only_a_label_and_a_count`:

```python
    def test_an_entry_with_no_count_is_owned_count_unknown(self):
        said, code = run(["--drawer-set", a_file([{"label": "some resistors"}])])
        self.assertEqual((code, self.entry("some-resistors")), (0, {"schema": 1, "label": "some resistors"}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--drawer"])
        self.assertEqual(next(line for line in out.getvalue().splitlines() if "some resistors" in line).split()[2], "?")
```

In `tests/test_needs.py`, class `TheMatcherTest`:

```python
    def test_a_count_nobody_gave_is_owned_count_unknown(self):
        self.catalog({"id": "y-probe", "name": "Probe Y", "function": [{"does": "sense", "what": "soil-moisture"}]})
        (self.home / "drawer" / "y.json").write_text(json.dumps({"schema": 1, "label": "some probes", "is": {"part": "y-probe"}}))
        found = [c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "y-probe"][0]
        self.assertEqual((found["owned"], found["free"]), ("unknown", "unknown"))
```

- [ ] **Step 2: Run them** (`-k no_count_is_owned` in `test_drawer.py`, `-k count_nobody_gave` in `test_needs.py`).
  Expected: the entry is refused ("a new entry needs a label and a count"); owned reads 0.

- [ ] **Step 3: The code.** In `scripts/needs.py` `_counts`, after the `many` line pair, add:

```python
    if any("count" not in entry for entry in holding):
        return "unknown", "unknown", unsure
```

and make the sum `owned = sum(entry["count"] for entry in holding)`. In its docstring, after "`many` stays many,", add
"an entry with no count is owned, count unknown (the PO, 2026-10-06),".

In `scripts/drawer.py` `settle`, replace

```python
    if before is None and not {"label", "count"} <= set(values):
        problems.append(parts._problem(entry_id, "a new entry needs a label and a count"))
```

with

```python
    if before is None and "label" not in values:
        problems.append(parts._problem(entry_id, "a new entry needs a label — with no count it is owned, count unknown"))
```

In `scripts/parts.py` `_op_drawer`, the first statement becomes:

```python
    lines = ["  %-44s %6s  %-38s %s" % (str(e["label"])[:44], "?" if e["count"] is None else e["count"],
                                         "%s %s" % next(iter(e["is"].items())) if e["is"] else "—",
                                         "maybe owned — check the drawer" if e["unsure"] else ("skip: %s" % e["skip"] if e["skip"] else ""))
             for e in entries]
```

`commands/drawer.md`: in the opening paragraph, "An entry needs only a label and a count" becomes "An entry needs only
a label; with no count it is owned, count unknown". In step 1 of "Say what else you own", after
`` `"many"` is a count)`` add: "— leave `count` out when the person does not know how many: the entry is owned, count
unknown, and a pick of it says so".

`docs/2026-10-04-store-design.md` §5.2: "- Required: `label`, `count`. `count` is an integer ≥ 0 or `"many"`, in
**pieces** (a 10-pack counts 10; the label keeps "pack of 10") — the PO." becomes "- Required: `label`. `count` is an
integer ≥ 0 or `"many"`, in **pieces** (a 10-pack counts 10; the label keeps "pack of 10") — the PO; an entry with no
`count` is owned, count unknown, and a pick of it says so (the PO, 2026-10-06)."

- [ ] **Step 4: Run** Step 2's commands, then the suite. Expected: PASS; the suite `OK`
  (`test_a_count_is_whole_pieces_or_many` still refuses `"count": null` — a null is not a count left out).

- [ ] **Step 5: Mutations.** `tests/mutations/p97-count-unknown.json`:

```json
[
 {"file": "scripts/needs.py", "name": "a count nobody gave is counted",
  "find": "    if any(\"count\" not in entry for entry in holding):\n", "replace": "    if False:\n"},
 {"file": "scripts/drawer.py", "name": "a new entry needs a count again",
  "find": "    if before is None and \"label\" not in values:", "replace": "    if before is None and not {\"label\", \"count\"} <= set(values):"},
 {"file": "scripts/parts.py", "name": "the drawer prints no count as None",
  "find": "\"?\" if e[\"count\"] is None else e[\"count\"]", "replace": "e[\"count\"]"}
]
```

Anchors check; run the table. Expected: every mutation caught (the first by a KeyError, which counts).

- [ ] **Step 6: Commit.** `P97 task 3 (the PO, 2026-10-06): a drawer entry with no count is owned, count unknown — a new entry needs only a label`

---

### Task 4: One writer at a time, and every write whole

**Files:** Modify `scripts/store.py` (imports, new `write_file`, `write_json`, new `locked`), `scripts/parts.py`
(`import contextlib`, `main`, `_write_record`, `fetch_documents`), `scripts/needs.py` (`write`). Test
`tests/test_store.py`, `tests/test_parts.py`, `tests/test_needs.py`. Create `tests/mutations/p97-one-writer.json`.
Re-point four rows.

**Interfaces:**
- Produces: `store.write_file(path, text, private=False) -> bool` — to `.part`, then renamed; only when the bytes
  differ; 0600 when private. `store.locked()` — a context manager: one writer at a time, through a lock file in the
  system's temp folder named after the store's home.
- Produces: `parts.main` holds `store.locked()` around every operation whose effects include `writes`. Ruled 2026-10-07 at Task 4's review, replacing the plan's "nothing else may take the lock": `store.locked()` is re-entrant for the thread that holds it — an inner acquisition passes through and only the outermost releases — so a store function may take the lock inside a locked operation. (The verbatim `write_file` and `locked` code below is the pre-review text; the branch's `scripts/store.py` at 6228278 is the implementation.)

- [ ] **Step 1: Failing tests.** In `tests/test_store.py`, add `import time` beside `import tempfile`, and before
  `class TheProjectsListTest`:

```python
class OneWriterAtATimeTest(unittest.TestCase):
    """P97 (§6.1): a write is whole or not at all, and a second writer waits for the first."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_write_that_fails_halfway_leaves_the_old_file_whole(self):
        target = Path(tempfile.mkdtemp()) / "record.json"
        target.write_text("old\n")
        with mock.patch.object(Path, "replace", side_effect=OSError("the disk is full")), self.assertRaises(OSError):
            store.write_file(target, "new\n")
        self.assertEqual(target.read_text(), "old\n")

    def test_a_write_waits_while_another_holds_the_store(self):
        given = Path(tempfile.mkdtemp()) / "entries.json"
        given.write_text(json.dumps([{"label": "a probe", "count": 1}]))
        with store.locked():
            writer = subprocess.Popen([sys.executable, str(SCRIPTS / "parts.py"), "--drawer-set", str(given)],
                                      env=dict(os.environ), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
            self.assertFalse((self.home / "drawer" / "a-probe.json").exists(), "it wrote while another held the store")
        self.assertEqual(writer.wait(timeout=60), 0)
        self.assertTrue((self.home / "drawer" / "a-probe.json").exists())
```

In `tests/test_parts.py`, class `WhatAPartDoesTest`, after `test_function_set_with_the_project_writes_the_copy_match_reads`:

```python
    def test_a_project_s_record_is_never_left_half_written(self):
        home, given = self.a_probe_in_the_catalog()
        project = Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        record = {"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}
        (project / "parts" / "x-soil.json").write_text(json.dumps(record))
        with in_store(home), mock.patch.object(Path, "replace", side_effect=OSError("the disk is full")):
            said, code = run_json(["--function-set", "x-soil", str(given), "--project", str(project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual(json.loads((project / "parts" / "x-soil.json").read_text()), record)
```

In `tests/test_needs.py`, class `TheNeedsFileTest`:

```python
    def test_a_needs_write_that_fails_halfway_leaves_the_file_whole(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        before = self.saved()
        with mock.patch.object(Path, "replace", side_effect=OSError("the disk is full")):
            _, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}])])
        self.assertEqual((code, self.saved()), (2, before))
```

- [ ] **Step 2: Run them** (`-k OneWriterAtATime` in `test_store.py`, `-k half_written` in `test_parts.py`,
  `-k fails_halfway` in `test_needs.py`). Expected: ERROR (no `write_file`, no `locked`); the project's record is
  overwritten in place.

- [ ] **Step 3: The code.** In `scripts/store.py`, imports become:

```python
import contextlib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

try:
    import fcntl
except ImportError:  # spark installs on macOS and Linux (README); where there is no fcntl, a write takes no lock
    fcntl = None
```

Replace `write_json` with:

```python
def write_file(path, text, private=False):
    """
    A whole file (§6.1): written to `.part` and renamed, so a write that fails halfway leaves the old file whole — and only
    when the bytes differ, so a retried write changes nothing. A private file is 0600. Returns whether it changed.
    """
    path = Path(path)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        if private:
            os.chmod(path, 0o600)
        return False
    part = path.with_name(path.name + ".part")
    part.write_text(text, encoding="utf-8")
    if private:
        os.chmod(part, 0o600)
    part.replace(path)
    return True


def write_json(name, key, data):
    """
    Put one JSON file into a place (§5.1) and say whether it changed. `key` names the file inside the place (None for a
    place that is itself a file). A private place is written 0600 in 0700 folders, never inside a git work tree.
    """
    target = _target(name, key)
    _make_ready(name, target)
    return write_file(target, json.dumps(data, indent=2, ensure_ascii=False) + "\n", name in PRIVATE)


@contextlib.contextmanager
def locked():
    """
    One writer at a time (§6.1): the store held from a write's plan to its last byte, so two agents writing at once cannot
    each write what the other never read — a part reserved twice, a count lost. The lock is a file in the system's temp
    folder named after this home, never in the store, so it is never a stray file in a repository; the operating system
    lets go of it when its holder exits.
    """
    named = hashlib.sha256(str(home().resolve()).encode()).hexdigest()[:16]
    with open(Path(tempfile.gettempdir()) / ("spark-%s.lock" % named), "a") as held:
        if fcntl:
            fcntl.flock(held, fcntl.LOCK_EX)
        yield
```

In `scripts/parts.py`, add `import contextlib` below `import argparse`. In `main`, replace

```python
    try:
        answer = globals()["_op_" + op.replace("-", "_")](args, project)
```

with

```python
    writes = "writes" in next(effects for name, _, _, effects, _ in OPERATIONS if name == op)
    try:
        with store.locked() if writes else contextlib.nullcontext():
            answer = globals()["_op_" + op.replace("-", "_")](args, project)
```

`_write_record` becomes:

```python
def _write_record(path, record):
    """A record back to its own home, whole (§6.1): through the store when it lives there (contained, private), else to its file."""
    for name in ("shelf", "catalog"):
        if path.parent == store.place(name):
            return store.write_json(name, path.stem, record)
    return store.write_file(path, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
```

In `fetch_documents`, replace `    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")` with
`    _write_record(path, record)`.

In `scripts/needs.py`, `write` becomes:

```python
def write(project, needs):
    """The needs file, whole (`.part`, then renamed) — the project's folder made when it is new (§8 S rule 5)."""
    path = Path(project) / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    store.write_file(path, json.dumps({"schema": 1, "needs": needs}, indent=2, ensure_ascii=False) + "\n")
```

- [ ] **Step 4: Run** Step 2's commands, then the suite. Expected: PASS; the suite `OK`.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-one-writer.json`:

```json
[
 {"file": "scripts/store.py", "name": "a write is made in place", "find": "    part.replace(path)\n    return True",
  "replace": "    path.write_text(text, encoding=\"utf-8\")\n    return True"},
 {"file": "scripts/store.py", "name": "the store is never locked", "find": "            fcntl.flock(held, fcntl.LOCK_EX)",
  "replace": "            pass"},
 {"file": "scripts/parts.py", "name": "a write takes no lock",
  "find": "        with store.locked() if writes else contextlib.nullcontext():", "replace": "        with contextlib.nullcontext():"},
 {"file": "scripts/parts.py", "name": "a project's record is written in place",
  "find": "    return store.write_file(path, json.dumps(record, indent=2, ensure_ascii=False) + \"\\n\")",
  "replace": "    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + \"\\n\")"},
 {"file": "scripts/needs.py", "name": "the needs file is written in place",
  "find": "    store.write_file(path, json.dumps({\"schema\": 1, \"needs\": needs}", "replace": "    path.write_text(json.dumps({\"schema\": 1, \"needs\": needs}"}
]
```

Re-point, in the same commit:
- `sprint-10-p95-4.json`, "a write is made even when nothing changed": find
  `    if path.is_file() and path.read_text(encoding="utf-8") == text:`, replace `    if False:`.
- `sprint-10-p95-4.json`, "an unchanged private file is left as loose as it was": find
  `        if private:\n            os.chmod(path, 0o600)\n        return False`, replace `        return False`.
- `sprint-5-catalog.json`, "a rewrite turns the record's text into escapes": file `scripts/store.py`, find
  `    return write_file(target, json.dumps(data, indent=2, ensure_ascii=False) + "\n", name in PRIVATE)`, replace
  `    return write_file(target, json.dumps(data, indent=2) + "\n", name in PRIVATE)` (a catalog record's rewrite goes
  through `write_json` now; `test_fetch_keeps_the_text_as_written_and_decodes_the_saved_name` still catches it).
- `sprint-10-p95-4.json`, "a private file is left readable by others": `        os.chmod(part, 0o600)` still occurs
  once — no change, but the anchors check confirms it.

Anchors check; run `p97-one-writer.json`, `sprint-10-p95-4.json` and `sprint-5-catalog.json`. Expected: every mutation
caught. Never mutate the suite guard.

- [ ] **Step 6: Commit.** `P97 task 4 (P96 review): one writer at a time — a lock around every parts.py write — and every write whole, a project's record and the needs file included`

---

### Task 5: The history (§5.7)

**Files:** Modify `scripts/store.py` (`PLACES`, `PRIVATE`, new `EVENT_KEYS`, `events`, `append_event`). Test
`tests/test_store.py`. Create `tests/mutations/p97-history.json`.

**Interfaces:**
- Produces: the place `history` (`history.jsonl`), private (0600, never inside a git work tree).
- Produces: `store.events() -> [dict]` — every line, in order; a line that is not an event is a `StoreProblem` naming
  the file and the line. `store.append_event(event) -> bool` — appended unless an event with the same key is there:
  `step` by (project, step, session, start); `reused` and `passed_over` by (project, need, and the pick's
  part/board/entry); `built` by (project, board, parts). Callers hold the lock (`parts.main` does).

- [ ] **Step 1: Failing tests.** In `tests/test_store.py`, before `class TheProjectsListTest`:

```python
class TheHistoryTest(unittest.TestCase):
    """P97 (§5.7): one event per line, appended, a repeat of a key not written, private."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_an_event_is_written_once(self):
        reused = {"event": "reused", "project": "plant-alarm", "need": "soil", "part": "sen0193-soil-moisture"}
        self.assertEqual((store.append_event(reused), store.append_event(dict(reused))), (True, False))
        self.assertEqual([json.loads(line) for line in (self.home / "history.jsonl").read_text().splitlines()], [reused])

    def test_a_reason_given_again_is_the_same_event(self):
        first = {"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x", "why": "too big", "by": "person"}
        store.append_event(first)
        self.assertFalse(store.append_event(dict(first, why="too dear")), "keyed by project, need and part")

    def test_a_step_started_again_is_another_event(self):
        step = {"event": "step", "project": "plant-alarm", "step": "C", "session": "s1", "start": "2026-10-06T10:00:00+00:00"}
        store.append_event(step)
        self.assertTrue(store.append_event(dict(step, start="2026-10-06T11:00:00+00:00")))
        self.assertEqual(len(store.events()), 2)

    def test_the_history_is_private_and_never_inside_git(self):
        store.append_event({"event": "reused", "project": "p", "need": "n", "part": "x"})
        self.assertEqual(stat.S_IMODE((self.home / "history.jsonl").stat().st_mode), 0o600)
        repo = Path(tempfile.mkdtemp())
        (repo / ".git").mkdir()
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(repo / "store")}), self.assertRaises(store.StoreProblem):
            store.append_event({"event": "reused", "project": "p", "need": "n", "part": "x"})
        self.assertFalse((repo / "store" / "history.jsonl").exists())

    def test_a_line_that_is_not_an_event_is_named(self):
        (self.home / "history.jsonl").write_text('{"event":"reused"}\nnot json\n')
        with self.assertRaises(store.StoreProblem) as broken:
            store.events()
        self.assertIn("line 2", str(broken.exception))
```

- [ ] **Step 2: Run them** (`-k TheHistoryTest`). Expected: ERROR (no `append_event`).

- [ ] **Step 3: The code.** In `scripts/store.py`, `PLACES` and `PRIVATE` become:

```python
PLACES = {"sources": "sources", "catalog": "catalog", "downloads": "downloads", "tools": "tools.json",
          "drawer": "drawer", "drawer-import": "drawer-import", "shelf": "shelf", "projects": "projects.json",
          "history": "history.jsonl"}
```

```python
PRIVATE = ("drawer", "drawer-import", "shelf", "projects", "history")
```

Below `add_project`:

```python
#: What makes two history lines one event (§5.7): a line whose key fields equal an earlier one's is not written again.
EVENT_KEYS = {"step": ("project", "step", "session", "start"), "reused": ("project", "need", "part", "board", "entry"),
              "passed_over": ("project", "need", "part", "board", "entry"), "built": ("project", "board", "parts")}


def events():
    """The history (§5.7), every line in order — [] before the first. A line that is not an event is named, never skipped."""
    path = place("history")
    said = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines() if path.is_file() else [], 1):
        try:
            event = json.loads(line)
        except ValueError:
            event = None
        if not (isinstance(event, dict) and isinstance(event.get("event"), str)):
            raise StoreProblem("%s line %d is not a history event — fix it by hand" % (path, number))
        said.append(event)
    return said


def append_event(event):
    """One event onto the history (§5.7) — not written when an event with the same key is there. Returns whether it was."""
    keys = EVENT_KEYS[event["event"]]
    if any(other.get("event") == event["event"] and all(other.get(key) == event.get(key) for key in keys) for other in events()):
        return False
    target = place("history")
    _make_ready("history", target)
    with open(target, "a", encoding="utf-8") as history:
        history.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.chmod(target, 0o600)
    return True
```

- [ ] **Step 4: Run** them, then the suite. Expected: PASS; the suite `OK`.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-history.json`:

```json
[
 {"file": "scripts/store.py", "name": "a repeat is written", "find": "        return False\n    target = place(\"history\")",
  "replace": "        pass\n    target = place(\"history\")"},
 {"file": "scripts/store.py", "name": "the history is left readable by others", "find": "    os.chmod(target, 0o600)\n    return True",
  "replace": "    return True"},
 {"file": "scripts/store.py", "name": "a line that is not an event is skipped",
  "find": "        if not (isinstance(event, dict) and isinstance(event.get(\"event\"), str)):\n            raise",
  "replace": "        if False:\n            raise"},
 {"file": "scripts/store.py", "name": "the history may be written inside git",
  "find": "\"shelf\", \"projects\", \"history\")", "replace": "\"shelf\", \"projects\")"}
]
```

Anchors check; run the table. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 5 (§5.7): the store's history — one event per line, a repeat of its key never written, private`

---

### Task 6: Picks and reservations (C1, C2)

**Files:** Modify `scripts/needs.py` (`import collections`, `PICKS`, a `CHECKS` row, `plan_set`, `candidates`'
pointing, new `_pointing`, `_held`, `_resolve`, `plan_pick`), `scripts/store.py` (`add_project`), `scripts/parts.py`
(an `OPERATIONS` row, an `OPTIONS` row, new `_op_pick`), `commands/idea.md`, `docs/guide/agents.md`. Test
`tests/test_needs.py` (new `ThePicksTest`, `TheIdeaCommandTest`), `tests/test_parts.py` (the envelope list). Create
`tests/mutations/p97-picks.json`.

**Interfaces:**
- Consumes: `_write_lines` (Task 1); `needs._counts(holding, mine)` (Tasks 2–3); `store.append_event` (Task 5);
  `store.locked` held by `main` (Task 4); `drawer.entries`, `drawer.linkable`, `drawer.settle`, `drawer.apply`,
  `drawer.clean`, `drawer._words`.
- Produces: a need's `pick` — `[{"part"|"board"|"entry": id}]`, checked on read and refused in `--needs-set`.
- Produces: `needs._pointing(entries) -> {(kind, id): [(entry key, entry)]}`; `needs._held(pick, entries, pointing)
  -> [(entry key, entry)]`; `needs._resolve(id, known, entries) -> {kind: id} | None`;
  `needs.plan_pick(project, given, passed_over=()) -> (needs after, drawer changes, events, notes, problems)`, `given`
  being `[(need id, id)]`.
- Produces: `store.add_project(folder, dry_run=False) -> name` (a dry run only says the name).
- Produces: operation `--pick PROJECT NEED=ID…` with option `--passed-over FILE` (`[{"need", "id", "why", "by"}]`);
  `data` `{"project", "picks": [{"need", "pick"}], "reserved": [{"entry", "used_in"}], "written"}`. A refusal's
  sentence is `"<owned> owned, held by <projects> — <n> picked here"` and its fix names the entry key(s) to free.
  Events: `reused` per pick of each need named, `passed_over` per reason.

- [ ] **Step 1: Failing tests.** In `tests/test_needs.py`, before `class TheIdeaCommandTest`:

```python
class ThePicksTest(unittest.TestCase):
    """P97, §8 C: a pick per need; what you own is reserved, never past what another project holds; a reason is kept."""

    def setUp(self):
        self.home, self.project = a_store_with_a_drawer(), Path(tempfile.mkdtemp()) / "plant-alarm"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        run(["--needs-set", str(self.project), a_file([
            {"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "sound", "what": "alarm"},
            {"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "input", "does": "input", "what": "button"}])])

    def entry(self, key):
        return json.loads((self.home / "drawer" / (key + ".json")).read_text())

    def picks(self):
        return {need["id"]: need.get("pick") for need in json.loads((self.project / ".spark" / "needs.json").read_text())["needs"]}

    def history(self):
        path = self.home / "history.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []

    def text(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            parts.main(argv)
        return out.getvalue()

    def test_the_bin_s_only_board_is_refused_naming_who_holds_it(self):
        said, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("1 owned, held by smartbin-local", said["problems"][0]["sentence"])
        self.assertIn("--drawer-set board", said["problems"][0]["fix"])
        self.assertEqual((self.picks()["board"], self.entry("board")["used_in"]), (None, {"smartbin-local": 1}))

    def test_a_pick_reserves_one_piece_and_the_history_says_it_was_reused(self):
        _, code = run(["--pick", str(self.project), "soil=x-soil", "alarm=speaker"])
        self.assertEqual(code, 0)
        self.assertEqual((self.picks()["soil"], self.picks()["alarm"]), ([{"part": "x-soil"}], [{"entry": "speaker"}]))
        self.assertEqual((self.entry("probe")["used_in"], self.entry("speaker")["used_in"]), ({"plant-alarm": 1}, {"plant-alarm": 1}))
        self.assertEqual(self.history(), [{"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x-soil"},
                                          {"event": "reused", "project": "plant-alarm", "need": "alarm", "entry": "speaker"}])

    def test_freed_by_the_person_the_board_is_reserved_for_this_project(self):
        run(["--drawer-set", a_file([{"entry": "board", "used_in": {}}])])
        _, code = run(["--pick", str(self.project), "board=firebeetle2-esp32s3"])
        self.assertEqual((code, self.entry("board")["used_in"]), (0, {"plant-alarm": 1}))

    def test_a_refused_pick_writes_nothing_at_all(self):
        _, code = run(["--pick", str(self.project), "soil=x-soil", "board=firebeetle2-esp32s3"])
        self.assertEqual(code, 1)
        self.assertEqual((self.picks()["soil"], self.entry("probe").get("used_in"), self.history()), (None, None, []))

    def test_a_re_pick_frees_what_it_no_longer_picks(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        _, code = run(["--pick", str(self.project), "soil=x-other"])
        self.assertEqual((code, self.picks()["soil"], self.entry("probe")["used_in"]), (0, [{"part": "x-other"}], {}))

    def test_a_pick_nobody_owns_is_to_get_and_reserves_nothing(self):
        self.assertIn("x-other: to get — known, not owned", self.text(["--pick", str(self.project), "soil=x-other"]))

    def test_an_unsure_pick_says_check_the_drawer_first(self):
        self.assertIn("mp3: maybe owned — check the drawer first", self.text(["--pick", str(self.project), "alarm=mp3"]))

    def test_a_count_nobody_gave_is_reserved_and_said(self):
        (self.home / "drawer" / "probes.json").write_text(json.dumps({"schema": 1, "label": "some probes"}))
        self.assertIn("probes: count unknown — check the drawer", self.text(["--pick", str(self.project), "soil=probes"]))
        self.assertEqual(self.entry("probes")["used_in"], {"plant-alarm": 1})

    def test_many_is_reserved_one_piece_at_a_time(self):
        run(["--pick", str(self.project), "input=tactile-button"])
        self.assertEqual(self.entry("buttons")["used_in"], {"plant-alarm": 1})

    def test_a_part_passed_over_keeps_its_reason_once(self):
        reasons = a_file([{"need": "soil", "id": "x-other", "why": "a gas sensor does not sense soil", "by": "person"}])
        for _ in range(2):
            run(["--pick", str(self.project), "soil=x-soil", "--passed-over", reasons])
        self.assertEqual([event for event in self.history() if event["event"] == "passed_over"],
                         [{"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x-other",
                           "why": "a gas sensor does not sense soil", "by": "person"}])

    def test_a_retried_pick_changes_nothing(self):
        run(["--pick", str(self.project), "soil=x-soil"])
        said, code = run(["--pick", str(self.project), "soil=x-soil"])
        self.assertEqual((code, said["data"]["reserved"], self.entry("probe")["used_in"]), (0, [], {"plant-alarm": 1}))

    def test_a_need_or_an_id_spark_does_not_have_is_named(self):
        said, code = run(["--pick", str(self.project), "smell=x-soil", "soil=no-such-thing"])
        self.assertEqual((code, [p["subject"] for p in said["problems"]]), (1, ["smell", "soil"]))

    def test_a_pick_names_ids_only(self):
        said, code = run(["--pick", str(self.project), "soil"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))

    def test_a_hand_edited_pick_of_the_wrong_shape_is_named(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps(
            {"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "x", "pick": [{"part": 7}]}]}))
        said, code = run(["--needs", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("needs.json", said["unchecked"][0]["sentence"])
```

In `TheIdeaCommandTest.test_it_names_the_project_where_a_command_takes_it_and_only_there`, replace
`if "--needs-set" in line or "--match" in line:` with
`if any(op in line for op in ("--needs-set", "--match", "--pick")):`.

In `tests/test_parts.py` `test_every_operation_answers_in_one_envelope_whose_status_is_its_exit`, add
`["--pick", str(project), "soil=x-part"],` to the list.

- [ ] **Step 2: Run them** (`-p 'test_needs.py' -k ThePicksTest`). Expected: ERROR (unknown `--pick`).

- [ ] **Step 3: The code.** In `scripts/needs.py`, add `import collections` above `import json`. Above `CHECKS`:

```python
#: What a pick names (§5.3): a part or a board record, or the drawer entry of an owned thing with no record.
PICKS = ("part", "board", "entry")
```

Change the comment above `CHECKS` to end "A pick is set only by --pick, which reserves what the person owns (§8 C).",
and add a last row to `CHECKS`:

```python
          "pick": (lambda v: v is None or (isinstance(v, list) and all(
              isinstance(p, dict) and len(p) == 1 and next(iter(p)) in PICKS and isinstance(next(iter(p.values())), str)
              and store.PLAIN.fullmatch(next(iter(p.values()))) for p in v)), '`pick` is a list of {"part"|"board"|"entry": id}, set with --pick'),
```

(`isinstance(…, str)` first: `{"part": 7}` would pass `store.PLAIN` as the string "7".)

In `plan_set`, after the `id` check's `continue`:

```python
        if "pick" in item:
            problems.append(parts._problem(need_id, "a pick is set with --pick, which reserves what you own"))
            continue
```

In `candidates`, replace the four `pointing` lines with `    pointing = _pointing(entries)` and the `holding` line with
`        holding = [entry for _, entry in pointing.get((kind, record_id), [])]`. Below `match`:

```python
def _pointing(entries):
    """{(kind, id): [(entry key, entry)]} for every live drawer entry that says what it is — one said to be dead holds nothing."""
    pointing = {}
    for entry_id, entry in entries.items():
        if not entry.get("skip") and isinstance(entry.get("is"), dict) and entry["is"]:
            pointing.setdefault(next(iter(entry["is"].items())), []).append((entry_id, entry))
    return pointing


def _held(pick, entries, pointing):
    """The live drawer entries that hold one pick (§8 C), as (key, entry): those that say they are its record, or the entry it names."""
    kind, key = next(iter(pick.items()))
    if kind == "entry":
        return [(key, entries[key])] if key in entries and not entries[key].get("skip") else []
    return pointing.get((kind, key), [])


def _resolve(pick_id, known, entries):
    """A pick by its id (§5.3): the record of that id — a part's, then a board's — else the drawer entry of that key, else None."""
    kind = next((kind for kind in ("part", "board") if (kind, pick_id) in known), "entry" if pick_id in entries else None)
    return {kind: pick_id} if kind else None


def plan_pick(project, given, passed_over=()):
    """
    What a `--pick` would do (§8 C): (the needs after, drawer changes, history events, notes, problems). `given` is
    [(need id, id)], and each need it names gets exactly those picks. Then the project's reservations are worked out again
    from every need's picks — one piece per pick — on the entries that hold them, never past what another project holds
    (C2), so a re-pick frees what it no longer picks. A pick no entry holds is to get, not reserved. Nothing is written here.
    """
    name, current, entries = store.add_project(project, dry_run=True), read(project), drawer.entries()
    known, ids, problems, picked = {row[:2] for row in drawer.linkable(project)}, {need["id"] for need in current}, [], {}
    for need_id, pick_id in given:
        pick = _resolve(pick_id, known, entries)
        if need_id not in ids:
            problems.append(parts._problem(need_id, "no need called %s — --needs lists them" % need_id))
        elif pick is None:
            problems.append(parts._problem(need_id, "no record or drawer entry called %s — --match lists the candidates" % pick_id))
        elif pick not in picked.setdefault(need_id, []):
            picked[need_id].append(pick)
    after = [dict(need, pick=picked[need["id"]]) if need["id"] in picked else need for need in current]
    wanted = collections.Counter(next(iter(pick.items())) for need in after for pick in need.get("pick") or [])
    pointing, mine, notes = _pointing(entries), collections.Counter(), []
    for (kind, key), pieces in sorted(wanted.items()):
        held = _held({kind: key}, entries, pointing)
        owned, _, unsure = _counts([entry for _, entry in held], name)
        if owned == 0:
            notes.append("%s: to get — known, not owned" % key)
            continue
        for entry_id, entry in held:
            room = pieces if not isinstance(entry.get("count"), int) else entry["count"] - sum(
                n for who, n in (entry.get("used_in") or {}).items() if who != name)
            taken = max(min(room, pieces), 0)
            mine[entry_id] += taken
            pieces -= taken
        holders = sorted({who for _, entry in held for who in entry.get("used_in") or {} if who != name})
        if pieces:
            problems.append(parts._problem(key, "%s owned%s — %d picked here" % (owned, ", held by " + ", ".join(holders) if holders else "",
                                                                                 wanted[(kind, key)]),
                                           "free it — --drawer-set %s with `used_in` leaving out %s, after a dry run — or pick another"
                                           % (", ".join(entry_id for entry_id, _ in held), ", ".join(holders) or "nobody")))
        notes += ["%s: maybe owned — check the drawer first" % key] if unsure else []
        notes += ["%s: count unknown — check the drawer" % key] if owned == "unknown" else []
    changes = []
    for entry_id, entry in sorted(entries.items()):
        used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}
        used_in.update({name: mine[entry_id]} if mine[entry_id] else {})
        if used_in != (entry.get("used_in") or {}):
            changes.append(drawer.settle(entry_id, entry, {"used_in": used_in}, [])[0])
    events = [dict({"event": "reused", "project": name, "need": need_id}, **pick) for need_id in picked for pick in picked[need_id]]
    for number, item in enumerate(passed_over if isinstance(passed_over, list) else [None], 1):
        pick = _resolve(item.get("id"), known, entries) if isinstance(item, dict) and isinstance(item.get("id"), str) else None
        if not (pick and item.get("need") in ids and drawer._words(item.get("why")) and item.get("by", "person") in ("person", "agent")):
            problems.append(parts._problem("passed over %d" % number, 'a part passed over is {"need", "id", "why", "by": '
                                           '"person" or "agent"}: a need and an id spark has, and the reason in words'))
            continue
        events.append(dict({"event": "passed_over", "project": name, "need": item["need"]}, **pick,
                           why=drawer.clean(item["why"]), by=item.get("by", "person")))
    return after, changes, events, notes, problems
```

In `scripts/store.py` `add_project`, the signature becomes `def add_project(folder, dry_run=False):`, its docstring
ends "Returns the name; a dry run only says it.", and its write becomes:

```python
    if not dry_run:
        write_json("projects", None, listed)
```

In `scripts/parts.py`, an `OPERATIONS` row before `("describe", …)`:

```python
    ("pick", {"nargs": "+", "metavar": ("PROJECT", "NEED=ID")},
     "set what each need picks (NEED=ID: a record, or a drawer entry) and reserve what you own of it — never past what another project holds",
     ("writes",), ("project", "picks", "reserved", "written")),
```

an `OPTIONS` row before `("project", …)`:

```python
    ("passed-over", {"metavar": "FILE"}, "with --pick: the parts passed over and why, a JSON list in FILE (- for stdin) of {need, id, why, by}"),
```

and, below `_op_needs_set`:

```python
def _op_pick(args, project):
    import drawer
    import needs
    target, given = args.pick[0], args.pick[1:]
    pairs = [tuple(one.split("=", 1)) for one in given if "=" in one]
    if not pairs or len(pairs) != len(given):
        return Answer(unchecked=[_cannot("--pick takes the project, then NEED=ID for each pick: soil=sen0193-soil-moisture",
                                         "parts.py --match <project> lists each need's candidates and their ids")])
    reasons, unreadable = _read_json_input(args.passed_over) if args.passed_over else ([], None)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    after, changes, events, notes, problems = needs.plan_pick(target, pairs, reasons)
    if not problems and not args.dry_run:
        store.add_project(target)
        needs.write(target, after)
        drawer.apply(changes)
        for event in events:
            store.append_event(event)
    asked = dict(pairs)
    picks = [{"need": need["id"], "pick": need.get("pick") or []} for need in after if need["id"] in asked]
    said = [] if problems else ["  %s: %s" % (one["need"], ", ".join(next(iter(pick.values())) for pick in one["pick"])) for one in picks]
    return Answer({"project": store.add_project(target, dry_run=True), "picks": picks,
                   "reserved": [{"entry": change["entry"], "used_in": change["now"]["used_in"]} for change in changes],
                   "written": not problems and not args.dry_run},
                  _write_lines(changes, problems, args.dry_run, said + ["  %s" % note for note in notes]), problems=problems)
```

(Spell `written` this way, not `not (problems or args.dry_run)`: that spelling is the anchor of
`sprint-10-p96-3.json`'s "a refused needs write is written" and must stay unique.)

`commands/idea.md`: replace the section `## Not yet` and its paragraph with:

````markdown
## C — a part per need

Pick with the person, need by need, from what `--match` offered: a record's id, or the drawer entry's key of an owned
thing with no record (a speaker, a battery). Then:

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --pick <project> soil=sen0193-soil-moisture alarm=max98357a-dfr0954 alarm=dfrobot-fit0502 --dry-run
```

and without `--dry-run`. Each need it names gets exactly those picks, and what the person owns of each is reserved for
the project, one piece per pick. A pick another project holds is **refused, naming the holder** ("1 owned, held by
…"): say so; the person frees it — `--drawer-set` of that entry's `used_in` without the holder, after a dry run — or
picks another. Say "to get" (known, not owned), "maybe owned — check the drawer first" and "count unknown" to the
person as they are. For each candidate the person passed over, write their reason **in their words** to a JSON file
with the Write tool — `[{"need": "soil", "id": "<the part>", "why": "…", "by": "person"}]` — and add
`--passed-over <file>`: the reason goes to the history in your store, never to the project.

Building from the picks is store 1c's next steps; say so, and stop at the picks.
````

`docs/guide/agents.md`: in the list of `parts.py` writes, `--drawer-set`, `--needs-set`, `--function-set`, becomes
`--drawer-set`, `--needs-set`, `--pick`, `--function-set`,.

- [ ] **Step 4: Run** Step 2's command, then `-p 'test_parts.py' -k one_envelope`, `-p 'test_docs.py'`, then the
  suite. Expected: PASS; the suite `OK`.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-picks.json`:

```json
[
 {"file": "scripts/needs.py", "name": "a reservation takes what another project holds",
  "find": "                n for who, n in (entry.get(\"used_in\") or {}).items() if who != name)",
  "replace": "                0 for who, n in (entry.get(\"used_in\") or {}).items() if who != name)"},
 {"file": "scripts/needs.py", "name": "a pick past what is free is not refused", "find": "        if pieces:\n", "replace": "        if False:\n"},
 {"file": "scripts/needs.py", "name": "a re-pick keeps what it no longer picks",
  "find": "        used_in = {who: n for who, n in (entry.get(\"used_in\") or {}).items() if who != name}",
  "replace": "        used_in = dict(entry.get(\"used_in\") or {})"},
 {"file": "scripts/needs.py", "name": "nothing is said to be reused", "find": "    events = [dict({\"event\": \"reused\"",
  "replace": "    events = [] and [dict({\"event\": \"reused\""},
 {"file": "scripts/needs.py", "name": "a reason is not kept", "find": "        events.append(dict({\"event\": \"passed_over\"",
  "replace": "        (dict({\"event\": \"passed_over\""},
 {"file": "scripts/needs.py", "name": "an unsure pick is not said",
  "find": "notes += [\"%s: maybe owned — check the drawer first\" % key] if unsure else []", "replace": "notes += []"},
 {"file": "scripts/needs.py", "name": "a count nobody gave is not said",
  "find": "notes += [\"%s: count unknown — check the drawer\" % key] if owned == \"unknown\" else []", "replace": "notes += []"},
 {"file": "scripts/needs.py", "name": "a pick may be set through --needs-set", "find": "        if \"pick\" in item:\n",
  "replace": "        if False:\n"},
 {"file": "scripts/parts.py", "name": "a refused pick is written",
  "find": "    if not problems and not args.dry_run:\n        store.add_project(target)",
  "replace": "    if not args.dry_run:\n        store.add_project(target)"}
]
```

Anchors check (if `" or entry.get(\"skip\")"`, `"if who != mine)"` or a `CHECKS` row now occurs twice, re-point the
older row to a longer `find`); run the table. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 6 (C1, C2): --pick — a part per need, what you own reserved and never past what another project holds, the refusal naming the holder; passed-over reasons and reused parts in the history`

---

### Task 7: spark's one door to the network, and the checked keep (§6.2, §6.5)

**Files:** Modify `scripts/store.py` (new `fetch`, `keep`), `scripts/parts.py` (`import urllib.request` removed;
`_download`, `reachable`, `keep_in_store`). Test `tests/test_store.py`. Create `tests/mutations/p97-fetcher.json`.
Re-point two rows.

**Interfaces:**
- Produces: `store.fetch(url, method="GET") -> bytes` — the one door; `method="HEAD"` asks only whether it answers;
  a URL that does not answer is a `StoreProblem`.
- Produces: `store.keep(payload, name) -> sha256` — `sources/<sha256>/<name>`, through `.part`, read back and checked
  before it takes its name; a `name` that is not a plain file name is refused.
- Keeps: `parts._download(url) -> bytes | None` (the test seam `fetch_documents(fetch=…)` and the dry-run test still
  use it) and `parts.reachable(url) -> bool`, both through `store.fetch`.

- [ ] **Step 1: Failing tests.** In `tests/test_store.py`, before `class TheProjectsListTest`:

```python
class TheOneDoorTest(unittest.TestCase):
    """P97 (§6.2, §6.5): spark reaches the network through one door, and a kept document is checked before it takes its name."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def a_file(self, payload):
        path = Path(tempfile.mkdtemp()) / "drawing.pdf"
        path.write_bytes(payload)
        return path

    def test_the_door_brings_back_what_the_url_serves(self):
        self.assertEqual(store.fetch(self.a_file(b"%PDF drawing").as_uri()), b"%PDF drawing")

    def test_a_url_that_does_not_answer_is_a_store_problem_never_empty_bytes(self):
        with self.assertRaises(store.StoreProblem) as missing:
            store.fetch((Path(tempfile.mkdtemp()) / "gone.pdf").as_uri())
        self.assertIn("does not answer", str(missing.exception))

    def test_parts_asks_through_the_door(self):
        import parts
        asked = []
        with mock.patch.object(store, "fetch", lambda url, method="GET": asked.append((url, method)) or b"x"):
            self.assertEqual((parts.reachable("https://v.example/a.pdf"), parts._download("https://v.example/b.pdf")), (True, b"x"))
        self.assertEqual(asked, [("https://v.example/a.pdf", "HEAD"), ("https://v.example/b.pdf", "GET")])

    def test_only_the_store_opens_a_url(self):
        opening = [path.name for path in sorted(SCRIPTS.glob("*.py")) if "urlopen" in path.read_text() and path.name != "store.py"]
        self.assertEqual(opening, [], "spark's code reaches the network through store.fetch alone (§6.5)")

    def test_a_kept_file_lands_under_its_checksum(self):
        digest = store.keep(b"%PDF drawing", "drawing.pdf")
        self.assertEqual(digest, "8158f0d8a471f168c2daf1361a3919c034b7e43a62f5f2ac08c048ee9e58168e")
        self.assertEqual((self.home / "sources" / digest / "drawing.pdf").read_bytes(), b"%PDF drawing")

    def test_a_kept_file_is_checked_before_it_takes_its_name(self):
        real = Path.write_bytes
        with mock.patch.object(Path, "write_bytes", lambda self, data: real(self, data[:3])), self.assertRaises(store.StoreProblem):
            store.keep(b"%PDF drawing", "drawing.pdf")
        self.assertEqual([found.name for found in (self.home / "sources").rglob("*") if found.is_file()], [])

    def test_a_name_that_would_leave_the_sources_is_refused(self):
        for name in ("../x.pdf", "a/b.pdf", "..", ""):
            with self.subTest(name=name), self.assertRaises(store.StoreProblem):
                store.keep(b"x", name)
```

- [ ] **Step 2: Run them** (`-k TheOneDoorTest`). Expected: ERROR (no `fetch`, no `keep`); the source scan names
  `parts.py`.

- [ ] **Step 3: The code.** In `scripts/store.py`, below `append_event`:

```python
def fetch(url, method="GET"):
    """
    spark's one door to the network (§6.5): one download — or, with HEAD, only whether the URL answers. Nothing else in
    spark's code opens a URL, and each call is counted from the session's transcript (§6.7). A URL that does not answer is
    a StoreProblem, never empty bytes.
    """
    import urllib.request
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method=method, headers={"User-Agent": "spark"}), timeout=30) as answer:
            return answer.read()
    except Exception as unreachable:  # noqa: BLE001 — every way of not answering is the same answer here
        raise StoreProblem("%s does not answer (%s)" % (url, unreachable))


def keep(payload, name):
    """
    The document store's checked keep (§6.2): a file under its checksum, written to `.part`, read back and checked, then
    renamed — what does not match what was fetched is deleted and named, never kept. Returns the checksum. A name that is
    not a plain file name would leave the store's sources, and is refused.
    """
    if Path(name).name != name or name in ("", ".", ".."):
        raise StoreProblem("%r is not a file name, so it could leave the store's sources" % name)
    digest = hashlib.sha256(payload).hexdigest()
    folder = place("sources") / digest
    folder.mkdir(parents=True, exist_ok=True)
    part = folder / (name + ".part")
    part.write_bytes(payload)
    if hashlib.sha256(part.read_bytes()).hexdigest() != digest:
        part.unlink()
        raise StoreProblem("%s was not kept: what was written is not what was fetched" % name)
    part.replace(folder / name)
    return digest
```

In `scripts/parts.py`, delete `import urllib.request`. `keep_in_store` becomes:

```python
def keep_in_store(payload, name, dry_run=False):
    """Put a file in the store under its checksum, checked (§6.2), and return the checksum (P62a) — a photo without its location (P75)."""
    if name.lower().endswith((".jpg", ".jpeg")):
        payload = without_location(payload)[0]
    return hashlib.sha256(payload).hexdigest() if dry_run else store.keep(payload, name)
```

`_download` becomes:

```python
def _download(url):
    """One cited document through spark's one door to the network (§6.5) — None when it does not answer, so it is not kept."""
    try:
        return store.fetch(url)
    except store.StoreProblem:
        return None
```

and `reachable`:

```python
def reachable(url):
    """Whether a URL answers at all, asked through spark's one door (§6.5). A hallucinated source is the one lie research tells easily."""
    try:
        store.fetch(url, method="HEAD")
    except store.StoreProblem:
        return False
    return True
```

- [ ] **Step 4: Run** them, then `-p 'test_parts.py' -k fetch -k kept -k network`, then the suite. Expected: PASS;
  the suite `OK`.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-fetcher.json`:

```json
[
 {"file": "scripts/store.py", "name": "a URL that does not answer is empty bytes",
  "find": "        raise StoreProblem(\"%s does not answer (%s)\" % (url, unreachable))", "replace": "        return b\"\""},
 {"file": "scripts/store.py", "name": "a kept file is not checked",
  "find": "    if hashlib.sha256(part.read_bytes()).hexdigest() != digest:\n", "replace": "    if False:\n"},
 {"file": "scripts/store.py", "name": "a name may leave the sources",
  "find": "    if Path(name).name != name or name in (\"\", \".\", \"..\"):\n", "replace": "    if False:\n"},
 {"file": "scripts/parts.py", "name": "asking whether a URL answers downloads it",
  "find": "        store.fetch(url, method=\"HEAD\")", "replace": "        store.fetch(url)"}
]
```

Re-point, in the same commit:
- `sprint-10-p95-1.json`, "a kept document goes beside the catalog, not into sources": file `scripts/store.py`, find
  `    folder = place("sources") / digest\n`, replace `    folder = place("sources").parent / digest\n`.
- `sprint-9-p62a.json`, "a file is kept under its name, not its checksum": file `scripts/store.py`, find
  `    folder = place("sources") / digest\n`, replace `    folder = place("sources")\n`.

Anchors check; run the three tables. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 7 (§6.2, §6.5): spark's one door to the network, store.fetch — parts.py's two doors go behind it — and the document store's checked keep`

---

### Task 8: Owed facts filled once, in the record's own home (§5.4)

**Files:** Modify `scripts/parts.py` (`_record_path`, new `_set_in_home`, `_op_function_set`, new `_op_fact_set`, an
`OPERATIONS` row), `commands/idea.md`, `docs/guide/agents.md`. Test `tests/test_parts.py` (new
`OwedFactsFilledInTheirHomeTest`; the envelope list), `tests/test_needs.py` (`TheIdeaCommandTest`). Create
`tests/mutations/p97-fact-set.json`. Re-point two rows.

**Interfaces:**
- Consumes: `_write_record` (Task 4); `owes`, `broken_problems`, `_absent`, `CHAIN_FACTS`, `function_problems`, `shelve`.
- Produces: `parts._record_path(part_id, project) -> (path | None, project name to re-shelve from | None)`: a shelf copy
  of a listed project's record resolves to that project's record (the P96 review's carry-over).
- Produces: `parts._set_in_home(part_id, project, values, dry_run, refuse) -> Answer` with `data`
  `{"part", "path", "was": {key: value}, "now": values, "written"}`; `refuse(record, after, path) -> [sentence]`.
- Produces: operation `--fact-set PART FILE [--project P] [--dry-run]` — FILE a JSON object of `CHAIN_FACTS` keys.
  `--function-set` keeps its `data` shape (`was` and `now` are the functions).

- [ ] **Step 1: Failing tests.** In `tests/test_parts.py`, after class `WhatAPartDoesTest`:

```python
class OwedFactsFilledInTheirHomeTest(unittest.TestCase):
    """P97 (§5.4): what a record owes is filled once, in its own home, through parts.py — never in spark's library."""

    def a_probe(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps(
            {"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor", "pin_order": ["GND", "VCC", "SIG"],
             "needs": [{"signal": "SOIL", "pin": "SIG", "direction": "out"}],
             "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}]}))
        return home

    def facts(self, given):
        path = Path(tempfile.mkdtemp()) / "facts.json"
        path.write_text(json.dumps(given))
        return str(path)

    def test_a_fact_is_filled_in_the_catalog_after_a_dry_run(self):
        home = self.a_probe()
        given = self.facts({"footprint": "jst_ph_3", "simulation": {"skip": "no soil in a simulator"}})
        with in_store(home):
            dry, code = run_json(["--fact-set", "x-soil", given, "--dry-run"])
            self.assertEqual((code, dry["data"]["written"]), (0, False))
            self.assertNotIn("footprint", json.loads((home / "catalog" / "x-soil.json").read_text()))
            _, code = run_json(["--fact-set", "x-soil", given])
        record = json.loads((home / "catalog" / "x-soil.json").read_text())
        self.assertEqual((code, record["footprint"], parts.owes(record)), (0, "jst_ph_3", ["pin_order_proof", "body_mm"]))

    def test_spark_s_library_is_refused(self):
        library = Path(tempfile.mkdtemp()) / "parts"
        library.mkdir()
        record = {"schema": 1, "id": "x-amp", "name": "An amp", "kind": "audio-amplifier", "needs": []}
        (library / "x-amp.json").write_text(json.dumps(record))
        with in_store(Path(tempfile.mkdtemp())), mock.patch.object(parts, "LIBRARY", library):
            said, code = run_json(["--fact-set", "x-amp", self.facts({"footprint": "pinrow12"})])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("spark's own library", said["problems"][0]["sentence"])
        self.assertEqual(json.loads((library / "x-amp.json").read_text()), record)

    def test_only_a_fact_the_chain_reads_and_never_an_empty_one(self):
        home = self.a_probe()
        with in_store(home):
            for given in ({"price_czk": 89}, {"footprint": None}, {}, ["jst_ph_3"]):
                with self.subTest(given=given):
                    self.assertEqual(run_json(["--fact-set", "x-soil", self.facts(given)])[1], 1)

    def test_a_fact_that_breaks_the_record_is_refused(self):
        home = self.a_probe()
        with in_store(home):
            said, code = run_json(["--fact-set", "x-soil", self.facts({"footprint": "pinrow5"})])
        self.assertEqual(code, 1)
        self.assertIn("5 pads", said["problems"][0]["sentence"])

    def test_a_shelf_copy_of_a_listed_project_s_record_is_filled_in_that_project_and_shelved_again(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "irrigation"
        (other / "parts").mkdir(parents=True)
        record = {"schema": 1, "id": "x-valve", "name": "A valve driver", "kind": "mosfet-driver", "needs": []}
        (other / "parts" / "x-valve.json").write_text(json.dumps(record))
        (home / "shelf").mkdir()
        (home / "shelf" / "x-valve.json").write_text(json.dumps(dict(record, based_on={"project": "irrigation", "digest": "0" * 64})))
        (home / "projects.json").write_text(json.dumps({"irrigation": str(other)}))
        with in_store(home):
            said, code = run_json(["--fact-set", "x-valve", self.facts({"footprint": "pinrow2"})])
        self.assertEqual((code, Path(said["data"]["path"]).resolve()), (0, (other / "parts" / "x-valve.json").resolve()))
        self.assertEqual(json.loads((other / "parts" / "x-valve.json").read_text())["footprint"], "pinrow2")
        self.assertEqual(json.loads((home / "shelf" / "x-valve.json").read_text())["footprint"], "pinrow2", "the shelf copy follows")
```

In `test_every_operation_answers_in_one_envelope_whose_status_is_its_exit`, add
`["--fact-set", "x-part", str(project / "absent.json")],`. In `tests/test_needs.py`
`TheIdeaCommandTest.test_it_names_the_project_where_a_command_takes_it_and_only_there`, the flagged lines become
`[line for line in lines if any(op in line for op in ("--audit", "--function-set", "--fact-set"))]`.

- [ ] **Step 2: Run them** (`-p 'test_parts.py' -k OwedFacts`). Expected: ERROR (unknown `--fact-set`).

- [ ] **Step 3: The code.** In `scripts/parts.py`, replace `_record_path` and `_op_function_set` with:

```python
def _record_path(part_id, project):
    """
    A part record's own file, and the project to shelve it again from (§5.4, §5.5): the nearest layer that has it, the
    catalog included, else a project on the person's list — except that a shelf copy of a listed project's record is not a
    home: that project's record is, and the copy follows it.
    """
    import drawer
    path = next((path for kind, found, _, path in drawer.linkable(project) if (kind, found) == ("part", part_id)), None)
    record = _parse(path) if path is not None and path.parent == store.place("shelf") else None
    named = record.get("based_on", {}).get("project") if isinstance(record, dict) and isinstance(record.get("based_on"), dict) else None
    folder = store.projects().get(named) if isinstance(named, str) else None
    home = folder / "parts" / path.name if folder is not None else None
    return (home, named) if home is not None and home.is_file() else (path, None)


def _set_in_home(part_id, project, values, dry_run, refuse):
    """
    Set fields of a part record in its own home (§5.4) — the catalog's, a project's, or a listed project's behind a shelf
    copy, which is then shelved again — never spark's library, which is changed in spark's repository. `refuse(record,
    after, path)` says what is wrong with the result, and anything it says refuses the write.
    """
    path, source = _record_path(part_id, project)
    if path is None:
        raise PartError("no part record called %r — `parts.py --need` finds what exists" % part_id)
    if path.parent.resolve() == LIBRARY.resolve():
        return Answer(problems=[_problem(part_id, "is in spark's own library, which is changed in spark's repository, "
                                                  "not by parts.py")])
    record = json.loads(path.read_text(encoding="utf-8"))
    after = dict(record, **values)
    wrong = refuse(record, after, path)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    was, changes = {key: record.get(key) for key in values}, after != record
    if changes and not dry_run:
        _write_record(path, after)
        if source:
            shelve(path, source)
    said = ("  %s %s (%s): %s" % ("would set" if dry_run else "set", part_id, path, "; ".join(
                "%s %s → %s" % (key, json.dumps(was[key], ensure_ascii=False), json.dumps(value, ensure_ascii=False))
                for key, value in values.items()))
            if changes else "  nothing to change: %s (%s) already says this" % (part_id, path))
    return Answer({"part": part_id, "path": str(path), "was": was, "now": values, "written": not dry_run}, [said])


def _op_function_set(args, project):
    part_id, name = args.function_set
    function, unreadable = _read_json_input(name)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    answer = _set_in_home(part_id, project, {"function": function}, args.dry_run, lambda record, after, path:
                          function_problems(after) if function else ["a function is a non-empty list [{does, what}]"])
    return answer._replace(data=dict(answer.data, was=answer.data["was"]["function"], now=function)) if answer.data else answer


def _op_fact_set(args, project):
    part_id, name = args.fact_set
    facts, unreadable = _read_json_input(name)
    if unreadable:
        return Answer(unchecked=[_cannot(unreadable)])
    if not (isinstance(facts, dict) and facts and set(facts) <= set(CHAIN_FACTS)):
        return Answer(problems=[_problem(part_id, "a fact write is a JSON object of facts the chain reads: %s" % ", ".join(CHAIN_FACTS))])
    return _set_in_home(part_id, project, facts, args.dry_run, lambda record, after, path: (
        ["%s is absent — a write fills a fact, it never empties one" % key for key in facts if _absent(key, facts[key])]
        + sorted(set(broken_problems(after, path)) - set(broken_problems(record, path)))))
```

An `OPERATIONS` row after `function-set`'s:

```python
    ("fact-set", {"nargs": 2, "metavar": ("PART", "FILE")},
     "fill what a record owes — a JSON object of the facts the chain reads, in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
     ("writes",), ("part", "path", "was", "now", "written")),
```

`commands/idea.md`, in the M section: "A file in the store's `shelf/` is a copy: a later re-shelve from its project
overwrites it, so say so." becomes "A record on the shelf that came from one of the person's projects is written in that
project, and its shelf copy follows." Before the section `## C — a part per need`'s last line, add:

````markdown
A part pick whose record owes facts cannot be built from. Fill each owed fact once, in the record's own home, from its
source: a JSON object of the facts (`footprint`, `pin_order`, `pin_order_proof`, `body_mm`, `simulation`) in a file
written with the Write tool, then

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --fact-set <part> <file> --project <project> --dry-run
```

and without `--dry-run`. A record in spark's own library is changed in spark's repository, not from here: say so. A
source not kept yet is fetched only after the person's yes — it reaches the network.
````

`docs/guide/agents.md`: `--pick`, `--function-set`, becomes `--pick`, `--function-set`, `--fact-set`,.

- [ ] **Step 4: Run** Step 2's command, `-p 'test_parts.py' -k function_set -k one_envelope`, `-p 'test_needs.py'
  -k TheIdeaCommandTest`, then the suite. Expected: PASS; the suite `OK` (every `--function-set` test unchanged).

- [ ] **Step 5: Mutations.** `tests/mutations/p97-fact-set.json`:

```json
[
 {"file": "scripts/parts.py", "name": "a shelf copy is its own home",
  "find": "    return (home, named) if home is not None and home.is_file() else (path, None)", "replace": "    return (path, None)"},
 {"file": "scripts/parts.py", "name": "the shelf copy does not follow its record",
  "find": "        if source:\n            shelve(path, source)", "replace": "        if False:\n            shelve(path, source)"},
 {"file": "scripts/parts.py", "name": "an empty fact is a fact",
  "find": "[\"%s is absent — a write fills a fact, it never empties one\" % key for key in facts if _absent(key, facts[key])]",
  "replace": "[]"},
 {"file": "scripts/parts.py", "name": "a fact may break the record",
  "find": "+ sorted(set(broken_problems(after, path)) - set(broken_problems(record, path)))", "replace": "+ []"},
 {"file": "scripts/parts.py", "name": "any key is a fact", "find": "set(facts) <= set(CHAIN_FACTS)", "replace": "True"}
]
```

Re-point, in the same commit:
- `sprint-10-p96-1.json`, "a dry run of --function-set writes": find
  `    if changes and not dry_run:\n        _write_record(path, after)`, replace `    if changes:\n        _write_record(path, after)`.
- `sprint-10-p96-fix-b.json`, "function-set: written means bytes changed": find
  `"now": values, "written": not dry_run}`, replace `"now": values, "written": changes and not dry_run}`.

`sprint-10-p96-fix-b.json`'s "the library is written", "the answer hides the file" and "a retry says it set something",
and `sprint-10-p96-final.json`'s "--function-set accepts null", keep their `find` (the helper keeps those spellings);
the anchors check confirms it. Run the four tables. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 8 (§5.4, P96 review): --fact-set fills an owed fact once in the record's own home — a listed project's behind a shelf copy, which follows — never spark's library`

---

### Task 9: The picks become a requirements file — promoted onto the shelf, `built` recorded (L1)

**Files:** Modify `scripts/needs.py` (new `REQUIREMENTS`, `requirements`), `scripts/parts.py` (`_shelf_copy`,
`shelvable`, `shelve`, new `BOARD_FACTS`, `digest`, new `note_built`, new `_op_requirements`, an `OPERATIONS` row),
`scripts/check_spine.py` (`import parts`, `main`), `commands/idea.md`, `commands/build.md`, `README.md`, `AGENTS.md`,
`docs/guide/journey.md`, `docs/guide/commands.md`, `docs/guide/agents.md`, `docs/2026-10-04-store-design.md` (§4 L1).
Test `tests/test_needs.py` (new `TheRequirementsFileTest`, `TheIdeaCommandTest`), `tests/test_check_spine.py`,
`tests/test_parts.py` (the envelope list). Create `tests/mutations/p97-requirements.json`.

**Interfaces:**
- Consumes: a need's `pick` (Task 6); `owes`, `broken_problems` (P96); `store.append_event`, `store.locked`,
  `store.project_name` (Tasks 2, 4, 5); `store.write_file` (Task 4).
- Produces: `needs.REQUIREMENTS = "requirements.json"`; `needs.requirements(project) -> (content, [(record path,
  project name | None)] to shelve, [entry keys not placed], problems)`.
- Produces: `parts.shelve(path, project_name=None)` — no `based_on` when it comes from the catalog;
  `parts.BOARD_FACTS = ("pins", "power_pads", "physical")`; `parts.digest(record, facts=BUILD_FACTS)`;
  `parts.note_built(design) -> bool` — a `built` line for a listed project, under the lock.
- Produces: operation `--requirements PROJECT [--dry-run]`, `data` `{"path", "requirements", "shelved", "unplaced", "written"}`.

- [ ] **Step 1: Failing tests.** In `tests/test_needs.py`, before `class TheIdeaCommandTest`:

```python
def a_project_with_picks(picks):
    """A scratch store holding a catalog record that owes nothing (the library's LED, as x-led) and one that owes facts,
    and a project whose needs pick `picks` — [(need id, [pick])]."""
    home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
    (home / "catalog").mkdir()
    led = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
    (home / "catalog" / "x-led.json").write_text(json.dumps(dict(led, id="x-led")))
    (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor", "needs": []}))
    (project / ".spark").mkdir(parents=True)
    (project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
        {"id": need_id, "does": "sense", "what": "x", "pick": pick} for need_id, pick in picks]}))
    return home, project


class TheRequirementsFileTest(unittest.TestCase):
    """P97, §8 L: the picks become a requirements file — the board and each part pick with a record that owes nothing."""

    BOARD = ("board", [{"board": "firebeetle2-esp32s3"}])

    def project(self, picks):
        home, project = a_project_with_picks(picks)
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        return home, project

    def written(self, project):
        return json.loads((project / "requirements.json").read_text())

    def test_the_picks_become_the_board_and_the_parts_with_records(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}]), ("alarm", [{"entry": "speaker"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((code, self.written(project)), (0, {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"]}))
        self.assertEqual(said["data"]["unplaced"], ["speaker"])

    def test_a_pick_that_owes_facts_is_named_and_nothing_is_written(self):
        _, project = self.project([self.BOARD, ("soil", [{"part": "x-soil"}])])
        said, code = run(["--requirements", str(project)])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("owes footprint", said["problems"][0]["sentence"])
        self.assertFalse((project / "requirements.json").exists())

    def test_a_catalog_pick_that_owes_nothing_goes_onto_the_shelf(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        run(["--requirements", str(project)])
        shelved = json.loads((home / "shelf" / "x-led.json").read_text())
        self.assertEqual((shelved["id"], "based_on" in shelved, self.written(project)["parts"]), ("x-led", False, ["x-led"]))

    def test_one_board_is_picked(self):
        for picks in ([("light", [{"part": "led-red-5mm"}])], [self.BOARD, ("other", [{"board": "xiao-esp32-c6"}])]):
            with self.subTest(picks=picks):
                _, project = self.project(picks)
                said, code = run(["--requirements", str(project)])
                self.assertEqual((code, said["problems"][0]["subject"]), (1, "board"))

    def test_a_part_picked_for_two_needs_is_named_after_each(self):
        _, project = self.project([self.BOARD, ("open-lid", [{"part": "tactile-button"}]), ("mode", [{"part": "tactile-button"}])])
        run(["--requirements", str(project)])
        self.assertEqual(self.written(project)["parts"], [{"part": "tactile-button", "name": "OpenLid"},
                                                          {"part": "tactile-button", "name": "Mode"}])

    def test_what_the_person_added_to_the_file_stays(self):
        _, project = self.project([self.BOARD, ("light", [{"part": "led-red-5mm"}])])
        (project / "requirements.json").write_text(json.dumps({"board": "x", "parts": [], "signals": [{"name": "LED_STATUS", "needs": []}]}))
        run(["--requirements", str(project)])
        self.assertEqual(self.written(project), {"board": "firebeetle2-esp32s3", "parts": ["led-red-5mm"],
                                                 "signals": [{"name": "LED_STATUS", "needs": []}]})

    def test_a_dry_run_writes_nothing(self):
        home, project = self.project([self.BOARD, ("light", [{"part": "x-led"}])])
        said, code = run(["--requirements", str(project), "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse((project / "requirements.json").exists() or (home / "shelf").exists())
```

In `TheIdeaCommandTest`, the second tuple becomes `("--needs-set", "--match", "--pick", "--requirements")`.

In `tests/test_check_spine.py`, at its end before `if __name__`:

```python
class ABuildThatRunsEndToEndIsRecordedTest(unittest.TestCase):
    """P97 (§5.7, §8 T): when the chain runs end to end for a project on the person's list, the history says it was built."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        (self.project / "requirements.json").write_text(json.dumps({"board": "firebeetle2-esp32s3", "parts": ["tactile-button"]}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def spine(self, last):
        stages = [stage(name, check_spine.OK) for name in ("board", "schematic", "footprint", "build")] + [stage("simulation", last)]
        with mock.patch.object(check_spine, "run", return_value=stages), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            check_spine.main([str(self.project / "requirements.json")])
        path = self.home / "history.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.is_file() else []

    def test_a_chain_that_runs_end_to_end_is_recorded_once_with_each_digest(self):
        self.spine(check_spine.OK)
        built = self.spine(check_spine.OK)
        self.assertEqual([(e["event"], e["project"], e["board"]["id"], [p["id"] for p in e["parts"]]) for e in built],
                         [("built", "plant-alarm", "firebeetle2-esp32s3", ["tactile-button"])])
        self.assertEqual((len(built[0]["board"]["digest"]), len(built[0]["parts"][0]["digest"])), (64, 64))

    def test_a_chain_that_did_not_run_end_to_end_records_nothing(self):
        self.assertEqual(self.spine(check_spine.COULD_NOT_RUN), [])
```

In `tests/test_parts.py`'s envelope list, add `["--requirements", str(project)],`.

- [ ] **Step 2: Run them** (`-p 'test_needs.py' -k TheRequirementsFileTest`, `-p 'test_check_spine.py'
  -k RecordedTest`). Expected: ERROR (unknown `--requirements`); no history line.

- [ ] **Step 3: The code.** In `scripts/needs.py`, below `plan_pick`:

```python
REQUIREMENTS = "requirements.json"


def requirements(project):
    """
    The picks as a requirements file (§5.3, §8 L): (its content, records to shelve, picks not placed, problems). The board
    pick, and every part pick whose record owes nothing — one in the catalog or in another project goes onto the shelf, so
    the build finds it; a pick with no record is reserved, not placed. A part picked for two needs is named after each.
    The keys the person added to the file (signals, rails) stay.
    """
    known = {row[:2]: row for row in drawer.linkable(project)}
    picks = [(need["id"], next(iter(pick.items()))) for need in read(project) for pick in need.get("pick") or []]
    board_picks = sorted({key for _, (kind, key) in picks if kind == "board"})
    problems = [] if len(board_picks) == 1 else [parts._problem("board", "pick one board — %s" % (
        "picked: " + ", ".join(board_picks) if board_picks else "none is picked"))]
    part_ids = [key for _, (kind, key) in picks if kind == "part"]
    placed, shelve = [], []
    for need_id, (kind, key) in picks:
        if kind != "part":
            continue
        _, _, where, path = known.get(("part", key), (None, None, None, None))
        record = parts._parse(path) if path else None
        wrong = (["no record called %s any more" % key] if not isinstance(record, dict) else
                 ["owes %s — fill it in its own home with --fact-set" % ", ".join(parts.owes(record))] if parts.owes(record)
                 else parts.broken_problems(record, path))
        problems += [parts._problem(key, sentence) for sentence in wrong]
        shelve += [(path, None if where == "catalog" else where)] if not wrong and where not in ("project", "shelf", "library") else []
        placed.append(key if part_ids.count(key) == 1 else {"part": key, "name": "".join(word.capitalize() for word in need_id.split("-"))})
    path = Path(project) / REQUIREMENTS
    kept = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    content = dict(kept if isinstance(kept, dict) else {}, board=board_picks[0] if board_picks else None, parts=placed)
    return content, list(dict.fromkeys(shelve)), [key for _, (kind, key) in picks if kind == "entry"], problems
```

In `scripts/parts.py`, `_shelf_copy`, `shelvable` and `shelve` take `project_name=None`, and `_shelf_copy` writes
`based_on` only for a project:

```python
def _shelf_copy(path, project_name=None):
    """What the shelf would hold of a record: filtered — and when it came from a project, which one and its digest (§5.5)."""
    record = json.loads(Path(path).read_text())
    copy = {key: value for key, value in record.items() if key not in SHELF_DROPS}
    if project_name:
        copy["based_on"] = {"project": project_name, "digest": digest(record)}
    return copy
```

(`shelvable(path, project_name=None)` and `shelve(path, project_name=None)` pass it on unchanged.) Replace
`BUILD_FACTS`' comment and `digest` with:

```python
#: The facts a build reads from a part record (§5.7): a digest of these vouches for a record until one changes.
BUILD_FACTS = ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts")
#: The facts a build reads from a board (§5.7).
BOARD_FACTS = ("pins", "power_pads", "physical")


def digest(record, facts=BUILD_FACTS):
    """The sha256 of the facts a build reads from a record — a part's by default, a board's with BOARD_FACTS (§5.7)."""
    shown = {key: record[key] for key in facts if key in record}
    return hashlib.sha256(json.dumps(shown, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def note_built(design):
    """
    A `built` line in the history when a listed project's board runs end to end (§5.7, §8 T): the board's and each part's
    digest, so a proof of an old pin order never vouches for a corrected one. A project not on the list keeps no history.
    """
    name = store.project_name(design.project)
    if name is None:
        return False
    with store.locked():
        return store.append_event({"event": "built", "project": name,
                                   "board": {"id": design.board["id"], "digest": digest(design.board, BOARD_FACTS)},
                                   "parts": [{"id": part["id"], "digest": digest(part)} for part in design.parts]})
```

An `OPERATIONS` row after `match`'s:

```python
    ("requirements", {"metavar": "PROJECT"},
     "the picks as the project's requirements.json: the board, and every part pick with a record that owes nothing — a catalog one goes onto the shelf",
     ("writes",), ("path", "requirements", "shelved", "unplaced", "written")),
```

and below `_op_pick`:

```python
def _op_requirements(args, project):
    import needs
    content, shelving, unplaced, problems = needs.requirements(args.requirements)
    path = Path(args.requirements) / needs.REQUIREMENTS
    if not problems and not args.dry_run:
        for record, source in shelving:
            shelve(record, source)
        store.write_file(path, json.dumps(content, indent=2, ensure_ascii=False) + "\n")
    said = [] if problems else ["  %s %s: board %s; parts %s" % (
        "would write" if args.dry_run else "wrote", path, content["board"],
        ", ".join(p if isinstance(p, str) else "%s (%s)" % (p["part"], p["name"]) for p in content["parts"]) or "none")]
    said += ["  onto the shelf, so every project builds with it: %s" % ", ".join(Path(r).stem for r, _ in shelving)] if shelving and not problems else []
    said += ["  reserved, not placed — no record: %s" % ", ".join(unplaced)] if unplaced and not problems else []
    return Answer({"path": str(path), "requirements": content, "shelved": [Path(r).stem for r, _ in shelving],
                   "unplaced": unplaced, "written": not problems and not args.dry_run},
                  _write_lines([], problems, args.dry_run, said), problems=problems)
```

In `scripts/check_spine.py`, add `import parts  # noqa: E402` below `import netlist  # noqa: E402`, and in `main`,
right after the `try … except` around `stages = run(…)`:

```python
    if source and not from_library and verdict(stages) == EXIT_OK:
        parts.note_built(design.load(source, project))
```

`commands/idea.md`: replace the `## C` section's last line ("Building from the picks is store 1c's next steps; say so,
and stop at the picks.") with:

````markdown
## L — the building list

Run `/spark:init --board <the board pick>` in the project first. Then fill what the part picks owe (above), and:

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --requirements <project> --dry-run
```

and without `--dry-run`. It writes `requirements.json`: the board and every part pick with a record. A pick with no
record (the speaker, the battery) is reserved, not placed. A pick from the catalog goes onto the shelf, so every project
builds with it. `/spark:build` takes it from there.
````

`commands/build.md`: after the paragraph that begins "`--keep .` writes the board into the project", add: "When the
chain runs end to end for a project on your list, your store's history records `built`, with a digest of the board
and of each part, so a later project sees what has been built and with which facts."

The PO's decision 2 — the requirements file is P97's, and P76's output is `needs.json` — in the same commit:
- `README.md`: "Its placement is a first draft, which you lay out before ordering. Today
  [the chain](GLOSSARY.md#the-spine-or-the-chain--scriptscheck_spinepy) starts from that requirements file; nothing yet
  writes one from a vague idea with no parts named ([P76](https://github.com/xmejkal/spark/issues/5))." becomes "Its
  placement is a first draft, which you lay out before ordering.
  [The chain](GLOSSARY.md#the-spine-or-the-chain--scriptscheck_spinepy) starts from that requirements file, which you
  write, or which `parts.py --requirements` writes from the parts you picked for your needs
  ([P97](https://github.com/xmejkal/spark/issues/18))."
- `README.md`, the Idea row's middle cell becomes: "**partly**: a goal becomes needs, matched against what you own and
  what spark knows; a part is picked per need, what you own is reserved, and the picks become a requirements file
  ([P97](https://github.com/xmejkal/spark/issues/18)). The conversation, the picking and the requirements file were not
  run here".
- `AGENTS.md`: "Nothing yet writes the requirements file from a vague idea with no parts named
  ([P76](https://github.com/xmejkal/spark/issues/5)), and no simulation runs unless you run one." becomes
  "`parts.py --requirements` writes the requirements file from the parts picked for a goal's needs
  ([P97](https://github.com/xmejkal/spark/issues/18)), and no simulation runs unless you run one."
- `docs/guide/journey.md`, its opening: "Today the chain starts from a
  [requirements file](../../GLOSSARY.md#the-requirements-file); nothing yet writes one from a vague idea with no parts
  named ([P76](https://github.com/xmejkal/spark/issues/5))." becomes "The chain starts from a
  [requirements file](../../GLOSSARY.md#the-requirements-file): yours, or the one `parts.py --requirements` writes from
  your picks ([P97](https://github.com/xmejkal/spark/issues/18))."
- `docs/guide/journey.md`, the Idea section: "It stops once each need is marked: have, have-unknown, know or gap. Not
  built yet:" and the two bullets under it become "Then a part is picked per need (`parts.py --pick`), what you own is
  reserved, and the picks become a requirements file (`parts.py --requirements`)
  ([P97](https://github.com/xmejkal/spark/issues/18)); those steps were not run for this page."
- `docs/guide/commands.md`, the `/spark:idea` section: "It stops after matching each need. Not built yet:" and its two
  bullets become "Then it picks a part per need and reserves what you own of it, and the picks become a requirements
  file ([P97](https://github.com/xmejkal/spark/issues/18)); one line at the end says what the run cost and what came
  from your store."
- `docs/guide/agents.md`: `--fact-set`, becomes `--fact-set`, `--requirements`,.
- `docs/2026-10-04-store-design.md` §4, L1's check: after "`check_spine` ends `[ok] … the chain runs end to end`" add
  "and `emit_board.py` without `--assume-missing-sizes` exits 0 — no placeholder outline (the PO, 2026-10-06)".

- [ ] **Step 4: Run** Step 2's commands, `-p 'test_docs.py'`, `-p 'test_parts.py' -k one_envelope`, then the suite.
  Expected: PASS; the suite `OK`. `test_docs.py` runs `check_docs` on the real docs: a flag shown after `parts.py` must
  be one its `--help` lists, and no line may name a personal path.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-requirements.json`:

```json
[
 {"file": "scripts/needs.py", "name": "a pick that owes facts is placed",
  "find": "[\"owes %s — fill it in its own home with --fact-set\" % \", \".join(parts.owes(record))] if parts.owes(record)",
  "replace": "[] if False"},
 {"file": "scripts/needs.py", "name": "two boards are fine", "find": "problems = [] if len(board_picks) == 1 else",
  "replace": "problems = [] if board_picks else"},
 {"file": "scripts/needs.py", "name": "a part picked twice is not named",
  "find": "placed.append(key if part_ids.count(key) == 1 else", "replace": "placed.append(key if True else"},
 {"file": "scripts/needs.py", "name": "what the person added to the file is dropped",
  "find": "content = dict(kept if isinstance(kept, dict) else {},", "replace": "content = dict({},"},
 {"file": "scripts/needs.py", "name": "a catalog pick is not shelved",
  "find": "if not wrong and where not in (\"project\", \"shelf\", \"library\") else []", "replace": "if False else []"},
 {"file": "scripts/parts.py", "name": "a catalog copy on the shelf claims a project", "find": "    if project_name:\n        copy[\"based_on\"]",
  "replace": "    if True:\n        copy[\"based_on\"]"},
 {"file": "scripts/check_spine.py", "name": "a chain that did not run end to end is recorded as built",
  "find": "    if source and not from_library and verdict(stages) == EXIT_OK:", "replace": "    if source and not from_library:"},
 {"file": "scripts/parts.py", "name": "a refused requirements file is written",
  "find": "    if not problems and not args.dry_run:\n        for record, source in shelving:",
  "replace": "    if not args.dry_run:\n        for record, source in shelving:"}
]
```

Anchors check; run the table. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 9 (L1, the PO's decision 2): --requirements turns the picks into requirements.json — a catalog pick goes onto the shelf, a part picked twice is named after each need — and check_spine records built`

---

### Task 10: The cost counter and the cost line (T1)

**Files:** Create `scripts/cost.py`, `tests/test_cost.py`, `tests/mutations/p97-cost.json`. Modify `scripts/store.py`
(the suite guard gains the session), `scripts/needs.py` (new `owned`), `scripts/parts.py` (`OPERATIONS` rows,
`_op_step`, `_op_tally`), `commands/idea.md`, `docs/guide/agents.md`, `docs/guide/commands.md`,
`docs/guide/developing.md`, `docs/2026-10-04-store-design.md` (§3, §5.7, §6.7). Delete `tools/research_cost.py`.
Test `tests/test_store.py`, `tests/test_parts.py` (the envelope list), `tests/test_needs.py` (`TheIdeaCommandTest`).

**Interfaces:**
- Consumes: `store.events`, `store.append_event`, `store.add_project`, `store.project_name`; a need's `pick`;
  `needs._held`, `needs._pointing`, `needs._counts`.
- Produces: `cost.STEPS`; `cost.step_event(project, step) -> dict`; `cost.transcripts(session, root=None) -> [Path]`;
  `cost.count(entries) -> {"requests", "by_tool", "runs", "documents", "tokens"}`; `cost.windows(steps, project)`;
  `cost.cost(steps, project, root=None) -> count + {"minutes"}` or `cost.NoTranscript`; `cost.line(picks, from_store,
  owned, counted) -> str`; `cost.main([transcript])`.
- Produces: `needs.owned(pick, entries) -> bool`.
- Produces: operation `--step PROJECT STEP [--dry-run]` (`data` `{"step", "written"}`) and `--tally PROJECT`
  (`data` `{"picks", "from_store", "owned", "cost", "built", "line"}`; could-not-run when the cost is not known).
- Produces: under `unittest`, `CLAUDE_CODE_SESSION_ID` is `spark-suite`, so a test's steps never name the person's
  session.

- [ ] **Step 1: Failing tests.** `tests/test_cost.py`:

```python
"""P97: what a project's run cost, from its session transcripts (docs/2026-10-04-store-design.md §6.7, §8 T)."""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import cost  # noqa: E402
import parts  # noqa: E402


def assistant(when, *tools, usage=None, message_id=None):
    """One assistant turn of a transcript, as the harness writes it: its time, its tool calls, its usage."""
    return {"type": "assistant", "timestamp": when,
            "message": {"id": message_id or when, "usage": usage or {},
                        "content": [{"type": "tool_use", "name": name, "input": given} for name, given in tools]}}


def run(argv):
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
        code = parts.main(argv + ["--json"])
    return json.loads(out.getvalue()), code


class WhatATranscriptSaysTest(unittest.TestCase):
    """§6.7's counts, from transcript entries: names and counts, never arguments."""

    def test_what_reached_the_network_what_ran_and_what_was_read(self):
        counted = cost.count([assistant(
            "2026-10-06T10:01:00Z", ("WebSearch", {"query": "q"}), ("WebFetch", {"url": "https://v.example/"}),
            ("mcp__plugin_spark_jlcpcb__component_search", {"query": "jst"}),
            ("Bash", {"command": "curl -sO https://v.example/a.pdf"}), ("Bash", {"command": "python3 scripts/parts.py --sources x-part"}),
            ("Bash", {"command": "ls -la"}), ("Read", {"file_path": "/s/a.PDF"}), ("Read", {"file_path": "/s/a.PDF"}),
            ("Read", {"file_path": "/s/notes.md"}), ("Bash", {"command": "python3 scripts/parts.py --read /s/b.pdf --want x"}),
            ("Agent", {"subagent_type": "spark:part-finder"}))])
        self.assertEqual((counted["requests"], counted["documents"], counted["runs"]), (5, 2, {"spark:part-finder": 1}))
        self.assertEqual(counted["by_tool"], {"WebSearch": 1, "WebFetch": 1, "mcp__plugin_spark_jlcpcb__component_search": 1, "Bash": 2})

    def test_new_tokens_leave_out_cache_reads_and_a_turn_is_counted_once(self):
        usage = {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 5000, "output_tokens": 7}
        self.assertEqual(cost.count([assistant("2026-10-06T10:01:00Z", usage=usage, message_id="m1"),
                                     assistant("2026-10-06T10:01:01Z", usage=usage, message_id="m1")])["tokens"], 117)

    def test_one_transcript_is_answered_on_its_own(self):
        path = Path(tempfile.mkdtemp()) / "agent-x.jsonl"
        path.write_text("".join(json.dumps(entry) + "\n" for entry in (
            assistant("2026-10-06T10:00:00Z", ("WebFetch", {"url": "u"})), assistant("2026-10-06T10:06:00Z", ("Read", {"file_path": "/d.pdf"})))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cost.main([str(path)]), 0)
        self.assertIn("requests  1", out.getvalue())
        self.assertIn("minutes   6", out.getvalue())


class TheCostLineTest(unittest.TestCase):
    """§6.7, §8 T: each step of the project, its session's transcripts inside the step's window, one line at the end."""

    PICKS = {"soil": [{"part": "x-soil"}], "alarm": [{"part": "x-amp"}, {"entry": "speaker"}],
             "board": [{"board": "firebeetle2-esp32s3"}], "battery": [{"entry": "lipo"}]}

    def setUp(self):
        self.home, self.claude = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        self.project = Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home), "HOME": str(self.claude)})
        patcher.start()
        self.addCleanup(patcher.stop)
        (self.home / "drawer").mkdir()
        for key, entry in {"probe": {"label": "soil probe", "count": 8, "is": {"part": "x-soil"}},
                           "amp": {"label": "an I2S amp", "count": 2, "is": {"part": "x-amp"}},
                           "speaker": {"label": "3 W speaker", "count": 2},
                           "board": {"label": "FireBeetle", "count": 1, "is": {"board": "firebeetle2-esp32s3"}},
                           "lipo": {"label": "1S LiPo", "count": 1}}.items():
            (self.home / "drawer" / (key + ".json")).write_text(json.dumps(dict({"schema": 1}, **entry)))
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [
            {"id": need, "does": "sense", "what": "x", "pick": pick} for need, pick in self.PICKS.items()]}))
        (self.home / "projects.json").write_text(json.dumps({"plant-alarm": str(self.project.resolve())}))
        self.history([dict({"event": "reused", "project": "plant-alarm", "need": need}, **pick)
                      for need, chosen in self.PICKS.items() for pick in chosen])

    def history(self, events):
        with (self.home / "history.jsonl").open("a") as history:
            history.writelines(json.dumps(event) + "\n" for event in events)

    def step(self, session, start, project="plant-alarm"):
        self.history([{"event": "step", "project": project, "step": "C", "session": session, "start": start}])

    def transcript(self, session, *entries):
        folder = self.claude / ".claude" / "projects" / "-Users-someone-plant-alarm"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (session + ".jsonl")).write_text("".join(json.dumps(entry) + "\n" for entry in entries))

    def test_the_line_counts_a_step_s_requests_documents_and_minutes(self):
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T09:59:00Z", ("WebFetch", {"url": "https://before.example/"})),
                        assistant("2026-10-06T10:01:00Z", ("Bash", {"command": "python3 scripts/parts.py --fetch max98357a-dfr0954"})),
                        assistant("2026-10-06T10:02:00Z", ("Read", {"file_path": "/store/sources/ab/drawing.pdf"})),
                        assistant("2026-10-06T10:14:00Z", ("Bash", {"command": "python3 scripts/parts.py --tally ."})))
        said, code = run(["--tally", str(self.project)])
        self.assertEqual((code, said["data"]["line"]), (0, "5 picks: 5 from the store (5 owned) — 1 request, 1 document, 14 min"))

    def test_a_subagent_s_work_inside_the_window_counts(self):
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T10:10:00Z", ("Bash", {"command": "ls"})))
        folder = self.claude / ".claude" / "projects" / "-Users-someone-plant-alarm" / "s1" / "subagents"
        folder.mkdir(parents=True)
        (folder / "agent-a1.jsonl").write_text(json.dumps(assistant("2026-10-06T10:05:00Z", ("WebSearch", {"query": "q"}))) + "\n")
        self.assertEqual(run(["--tally", str(self.project)])[0]["data"]["cost"]["requests"], 1)

    def test_a_step_ends_where_the_next_step_of_its_session_starts(self):
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.step("s1", "2026-10-06T10:05:00+00:00", project="rc-car")
        self.transcript("s1", assistant("2026-10-06T10:01:00Z", ("WebFetch", {"url": "u"})),
                        assistant("2026-10-06T10:06:00Z", ("WebFetch", {"url": "v"})))
        counted = run(["--tally", str(self.project)])[0]["data"]["cost"]
        self.assertEqual((counted["requests"], counted["minutes"]), (1, 5))

    def test_no_transcript_is_could_not_run_never_zero(self):
        self.step("gone", "2026-10-06T10:00:00+00:00")
        said, code = run(["--tally", str(self.project)])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertEqual(said["data"]["line"], "5 picks: 5 from the store (5 owned) — its cost was not counted")

    def test_a_pick_the_drawer_does_not_hold_is_not_owned(self):
        (self.home / "drawer" / "lipo.json").unlink()
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T10:01:00Z"))
        self.assertTrue(run(["--tally", str(self.project)])[0]["data"]["line"].startswith("5 picks: 5 from the store (4 owned)"))

    def test_a_pick_with_no_reused_line_is_not_from_the_store(self):
        lines = (self.home / "history.jsonl").read_text().splitlines()
        (self.home / "history.jsonl").write_text("".join(line + "\n" for line in lines if '"lipo"' not in line))
        self.step("s1", "2026-10-06T10:00:00+00:00")
        self.transcript("s1", assistant("2026-10-06T10:01:00Z"))
        self.assertTrue(run(["--tally", str(self.project)])[0]["data"]["line"].startswith("5 picks: 4 from the store (5 owned)"))


class TheStepTest(unittest.TestCase):
    """§5.7, §6.7: a step is one line when it starts — its project, its letter, its session, its start."""

    def setUp(self):
        self.home, self.project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "plant-alarm"
        (self.project / ".spark").mkdir(parents=True)
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_step_says_its_session_and_when_it_started(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "s9"}):
            _, code = run(["--step", str(self.project), "C"])
        event = json.loads((self.home / "history.jsonl").read_text().splitlines()[-1])
        self.assertEqual((code, event["event"], event["project"], event["step"], event["session"]), (0, "step", "plant-alarm", "C", "s9"))

    def test_a_step_outside_claude_code_says_its_cost_cannot_be_counted(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ), contextlib.redirect_stdout(out):
            os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            parts.main(["--step", str(self.project), "C"])
        self.assertIn("no Claude Code session here", out.getvalue())

    def test_a_step_is_one_of_the_spine_s_letters(self):
        said, code = run(["--step", str(self.project), "X"])
        self.assertEqual((said["status"], code), ("could-not-run", 2))
        self.assertFalse((self.home / "history.jsonl").exists())

    def test_a_dry_run_of_a_step_writes_nothing(self):
        said, code = run(["--step", str(self.project), "C", "--dry-run"])
        self.assertEqual((code, said["data"]["written"]), (0, False))
        self.assertFalse((self.home / "history.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
```

In `tests/test_store.py`, class `TheSuiteStaysOutOfThePersonsStoreTest`:

```python
    def test_the_suite_s_steps_never_name_the_person_s_session(self):
        self.assertEqual(os.environ.get("CLAUDE_CODE_SESSION_ID"), "spark-suite")
```

In `tests/test_parts.py`'s envelope list, add `["--step", str(project), "C"], ["--tally", str(project / "untallied")],`
(a folder no step names, so no transcript is looked for). In `TheIdeaCommandTest`, the second tuple becomes
`("--needs-set", "--match", "--pick", "--requirements", "--step", "--tally")`.

- [ ] **Step 2: Run them.** `python3 -m unittest discover -s tests -t tests -p 'test_cost.py'` — expected: ERROR
  (`No module named 'cost'`).

- [ ] **Step 3: The code.** `scripts/cost.py`:

```python
#!/usr/bin/env python3
"""
What a project's run cost, read from the session transcripts (P97; docs/2026-10-04-store-design.md §6.7).

Each spine step of a project is a `step` line in the store's history: the session it ran in and when it started. A step
lasts until the next step of the same session starts — of any project — or to that session's last line. The counter
reads the main and the subagent transcripts of each step's session inside its window, and counts what reached the
network (a table of tool names and shell patterns), the runs of each agent type, the documents read, the new tokens
apart from cache reads, and the minutes. It keeps tool names and counts, never arguments. No transcript is
could-not-run, never 0: the harness keeps transcripts for a while, not for ever. The transcript is the harness's format,
not spark's, and may change. This replaced tools/research_cost.py (W16), and still answers for one transcript:

    cost.py <transcript.jsonl>      what one run cost — a research agent's, for instance
"""

import collections
import datetime
import json
import os
import re
import sys
from pathlib import Path

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN

#: What reaches the network (§6.7): these tools, every MCP server's tools, and a shell command that names one of these.
NETWORK_TOOLS = ("WebSearch", "WebFetch")
NETWORK_SHELL = re.compile(r"\b(curl|wget)\b|\bgh api\b|--(fetch|sources)\b")
#: What reading a document is: the Read tool, or `parts.py --read`, on one of these.
DOCUMENTS = (".pdf", ".png", ".jpg", ".jpeg", ".webp", ".svg")
#: A project's spine steps (§2): shape, match, choose, research the gap, the part list, the tally; ideas, fit, revive.
STEPS = ("S", "M", "C", "G", "L", "T", "I", "F", "R")
#: Earlier than any transcript: the lower bound for a window that has none.
EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


class NoTranscript(Exception):
    """A step whose cost is not known: no step, no session, or no transcript of it here. Could-not-run, never 0."""


def _when(stamp):
    return datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))


def step_event(project, step):
    """The history line a step starts with (§5.7): which project and step, the Claude Code session it runs in, and when."""
    return {"event": "step", "project": project, "step": step, "session": os.environ.get("CLAUDE_CODE_SESSION_ID"),
            "start": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}


def transcripts(session, root=None):
    """The main and the subagent transcripts of one session, wherever the harness filed them."""
    root = Path(root) if root else Path.home() / ".claude" / "projects"
    return sorted(root.glob("*/%s.jsonl" % session)) + sorted(root.glob("*/%s/subagents/*.jsonl" % session))


def _lines(paths):
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if isinstance(entry, dict):
                yield entry


def _inside(entry, start, end):
    try:
        when = _when(entry.get("timestamp"))
    except ValueError:
        return False
    return start <= when and (end is None or when < end)


def count(entries):
    """What a run of transcript entries did (§6.7): {requests, by_tool, runs, documents, tokens} — names and counts only."""
    by_tool, runs, documents, seen, tokens = collections.Counter(), collections.Counter(), set(), set(), 0
    for entry in entries:
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        if message.get("id") is None or message["id"] not in seen:
            seen.add(message.get("id"))
            usage = message.get("usage") or {}
            tokens += sum(usage.get(key) or 0 for key in ("input_tokens", "cache_creation_input_tokens", "output_tokens"))
        for block in message.get("content") or []:
            if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                continue
            name, given = str(block.get("name")), block.get("input") if isinstance(block.get("input"), dict) else {}
            command = str(given.get("command") or "") if name.lower() == "bash" else ""
            if name in NETWORK_TOOLS or name.startswith("mcp__") or NETWORK_SHELL.search(command):
                by_tool[name] += 1
            if name in ("Agent", "Task"):
                runs[str(given.get("subagent_type") or "general-purpose")] += 1
            reading = re.search(r"--read\s+(\S+)", command)
            read = given.get("file_path") if name == "Read" else (reading.group(1) if reading else None)
            if isinstance(read, str) and read.lower().endswith(DOCUMENTS):
                documents.add(read)
    return {"requests": sum(by_tool.values()), "by_tool": dict(by_tool), "runs": dict(runs), "documents": len(documents),
            "tokens": tokens}


def windows(steps, project):
    """(session, start, end or None) of each of a project's steps (§6.7): a step ends where the next step of its session starts."""
    said = []
    for step in steps:
        if step.get("project") == project:
            start = _when(step["start"])
            later = [_when(other["start"]) for other in steps
                     if other.get("session") == step.get("session") and _when(other["start"]) > start]
            said.append((step.get("session"), start, min(later) if later else None))
    return said


def cost(steps, project, root=None):
    """
    What a project's steps cost (§6.7): `count` over every step's window, and the minutes the windows span. NoTranscript —
    never a 0 — when no step was recorded, a step has no session, or its session's transcript is not here.
    """
    found = windows(steps, project)
    if not found:
        raise NoTranscript("no step of %s is in the history — `parts.py --step <project> <step>` marks each" % project)
    inside, minutes = [], 0.0
    for session, start, end in found:
        paths = transcripts(session, root) if session else []
        if not paths:
            raise NoTranscript("no transcript of session %s here, so the cost of its steps is not known" % session)
        here = [entry for entry in _lines(paths) if _inside(entry, start, end)]
        inside += here
        minutes += ((end or max([_when(entry["timestamp"]) for entry in here], default=start)) - start).total_seconds() / 60
    return dict(count(inside), minutes=round(minutes))


def line(picks, from_store, owned, counted):
    """The cost line (§6.7): "5 picks: 5 from the store (5 owned) — 1 request, 1 document, 14 min"."""
    said = "%d pick%s: %d from the store (%d owned)" % (picks, "" if picks == 1 else "s", from_store, owned)
    if counted is None:
        return said + " — its cost was not counted"
    return said + " — %d request%s, %d document%s, %d min" % (
        counted["requests"], "" if counted["requests"] == 1 else "s", counted["documents"],
        "" if counted["documents"] == 1 else "s", counted["minutes"])


def main(argv=None):
    given = sys.argv[1:] if argv is None else list(argv)
    if len(given) != 1 or not Path(given[0]).is_file():
        print("usage: cost.py <transcript.jsonl> — what one run cost, from its transcript", file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    entries = list(_lines([Path(given[0])]))
    counted = count(entries)
    stamps = sorted(_when(entry["timestamp"]) for entry in entries if _inside(entry, EPOCH, None))
    counted["minutes"] = round((stamps[-1] - stamps[0]).total_seconds() / 60) if stamps else 0
    for key in ("requests", "by_tool", "runs", "documents", "tokens", "minutes"):
        print("%-9s %s" % (key, counted[key]))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

In `scripts/store.py`'s suite guard, below the `SPARK_HOME` line, add:

```python
    os.environ["CLAUDE_CODE_SESSION_ID"] = "spark-suite"  # P97: a test's steps never name the person's own session
```

In `scripts/needs.py`, below `requirements`:

```python
def owned(pick, entries):
    """Whether the drawer holds a pick (§6.7's "owned"): a live entry with a count above 0, many, or a count nobody gave."""
    held = _held(pick, entries, _pointing(entries))
    return bool(held) and _counts([entry for _, entry in held])[0] != 0
```

In `scripts/parts.py`, two `OPERATIONS` rows after `requirements`':

```python
    ("step", {"nargs": 2, "metavar": ("PROJECT", "STEP")},
     "a spine step of a project starts now, in this Claude Code session — the cost line counts its transcript from here",
     ("writes",), ("step", "written")),
    ("tally", {"metavar": "PROJECT"},
     "the cost line: the picks, how many came from your store and how many you own, and what the project's steps cost",
     (), ("picks", "from_store", "owned", "cost", "built", "line")),
```

and below `_op_requirements`:

```python
def _op_step(args, project):
    import cost
    target, step = args.step
    if step not in cost.STEPS:
        return Answer(unchecked=[_cannot("a step is one of %s (the spine, §2 of the store design)" % ", ".join(cost.STEPS))])
    event = cost.step_event(store.add_project(target, dry_run=args.dry_run), step)
    if not args.dry_run:
        store.append_event(event)
    return Answer({"step": event, "written": not args.dry_run},
                  ["  %s step %s of %s%s" % ("would start" if args.dry_run else "started", step, event["project"],
                                             "" if event["session"] else " — no Claude Code session here, so its cost cannot be counted")])


def _op_tally(args, project):
    import cost
    import drawer
    import needs
    name, history, entries = store.project_name(args.tally), store.events(), drawer.entries()
    picks = [(need["id"], pick) for need in needs.read(args.tally) for pick in need.get("pick") or []]
    reused = [event for event in history if event.get("event") == "reused" and event.get("project") == name]
    from_store = sum(1 for need_id, pick in picks if dict({"event": "reused", "project": name, "need": need_id}, **pick) in reused)
    owned = sum(1 for _, pick in picks if needs.owned(pick, entries))
    try:
        counted, unchecked = cost.cost([event for event in history if event.get("event") == "step"], name), []
    except cost.NoTranscript as missing:
        counted, unchecked = None, [_cannot(str(missing), "mark each step with parts.py --step <project> <step> in a Claude Code session")]
    said = cost.line(len(picks), from_store, owned, counted)
    built = any(event.get("event") == "built" and event.get("project") == name for event in history)
    return Answer({"picks": len(picks), "from_store": from_store, "owned": owned, "cost": counted, "built": built, "line": said},
                  ["  " + said] + ([] if built else ["  not built yet — check_spine records it when the chain runs end to end"]),
                  unchecked=unchecked)
```

Delete `tools/research_cost.py` (W16). In `docs/guide/developing.md`, its line becomes
"- [`scripts/cost.py`](../../scripts/cost.py): the cost of one research run, read from its transcript; `parts.py --tally`
  says a whole project's." In `docs/guide/commands.md`, "Measured from their transcripts on 2026-10-03 with
`tools/research_cost.py`" becomes "Measured from their transcripts on 2026-10-03 (`scripts/cost.py <transcript>`
measures one run the same way today)". `docs/guide/agents.md`: `--requirements`, becomes `--requirements`, `--step`,.

`commands/idea.md`: below the opening paragraph (before `## S`), add:

````markdown
At the start of each step below — S, M, C and L — mark it, so the cost line can count what it took:

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --step <project> S
```
````

and after the `## L` section:

````markdown
## T — the tally

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --tally <project>
```

ends the run with one line — "5 picks: 5 from the store (5 owned) — 1 request, 1 document, 14 min" — counted from the
steps' transcripts. Say it as it is; "its cost was not counted" is an answer too.
````

`docs/2026-10-04-store-design.md`, ruling 2:
- §3: "A **step** — one spine step of one project, with a start and an end." becomes "A **step** — one spine step of
  one project, with a start; it ends where the next step of its session starts (P97)."
- §5.7's first example line drops `,"end":"…"`.
- §6.7: "Each spine step writes a `step` event with its session id, start and end." becomes "Each spine step writes a
  `step` event with its session id and start; a step ends where the next step of the same session starts, or at the
  session's last line (P97: an append-only history cannot fill in an end)."

- [ ] **Step 4: Run** `-p 'test_cost.py'`, `-p 'test_store.py'`, `-p 'test_docs.py'`, `-p 'test_orphans.py'`,
  `-p 'test_self_confirmation.py'`, then the suite. Expected: PASS; the suite `OK`. `test_orphans` finds `cost.py`
  imported by `parts.py`; `test_self_confirmation` needs `scripts/cost.py` named by a mutation table — Step 5's.

- [ ] **Step 5: Mutations.** `tests/mutations/p97-cost.json`:

```json
[
 {"file": "scripts/cost.py", "name": "a cache read counts as a new token",
  "find": "(\"input_tokens\", \"cache_creation_input_tokens\", \"output_tokens\")",
  "replace": "(\"input_tokens\", \"cache_creation_input_tokens\", \"cache_read_input_tokens\", \"output_tokens\")"},
 {"file": "scripts/cost.py", "name": "a shell command never reaches the network", "find": " or NETWORK_SHELL.search(command):", "replace": ":"},
 {"file": "scripts/cost.py", "name": "an MCP call is not a request", "find": " or name.startswith(\"mcp__\")", "replace": ""},
 {"file": "scripts/cost.py", "name": "anything read is a document",
  "find": "if isinstance(read, str) and read.lower().endswith(DOCUMENTS):", "replace": "if isinstance(read, str):"},
 {"file": "scripts/cost.py", "name": "a step never ends", "find": "min(later) if later else None", "replace": "None"},
 {"file": "scripts/cost.py", "name": "no transcript is a cost of nothing",
  "find": "            raise NoTranscript(\"no transcript of session", "replace": "            continue\n            raise NoTranscript(\"no transcript of session"},
 {"file": "scripts/cost.py", "name": "a step forgets its session", "find": "\"session\": os.environ.get(\"CLAUDE_CODE_SESSION_ID\")",
  "replace": "\"session\": None"},
 {"file": "scripts/needs.py", "name": "every pick is owned",
  "find": "    return bool(held) and _counts([entry for _, entry in held])[0] != 0", "replace": "    return True"},
 {"file": "scripts/parts.py", "name": "every pick is from the store",
  "find": "if dict({\"event\": \"reused\", \"project\": name, \"need\": need_id}, **pick) in reused)", "replace": "if True)"},
 {"file": "scripts/parts.py", "name": "a dry run of a step writes",
  "find": "    if not args.dry_run:\n        store.append_event(event)", "replace": "    if True:\n        store.append_event(event)"}
]
```

Never mutate the suite guard, its new line included. Anchors check; run the table. Expected: every mutation caught.

- [ ] **Step 6: Commit.** `P97 task 10 (T1, §6.7): the cost counter reads each step's session transcripts — parts.py --step marks a step, --tally says the line — and replaces tools/research_cost.py (W16)`

---

### Task 11: The scratch proof — the whole of 1c on a scratch store, offline

No repository change. It runs the chain the way the plant alarm will, on a synthetic probe and the library's LED,
so it needs no network and no person. The board engine is the bin's own tscircuit, on `PATH`, as the bin's `CLAUDE.md`
does it (checked 2026-10-06: the reference design ran end to end that way in about 11 s).

- [ ] **Step 1: Run it**, as one script, from the root of the `p97-store-1c` checkout:

```bash
set -euo pipefail
export SPARK_HOME="$(mktemp -d)/store"
WORK="$(mktemp -d)"; P="$WORK/plant-alarm"; S=scripts/parts.py
export PATH="$HOME/Development/smartbin-local/node_modules/.bin:$PATH"
mkdir -p "$SPARK_HOME/catalog"
cat > "$SPARK_HOME/catalog/x-soil-probe.json" <<'EOF'
{"schema": 1, "id": "x-soil-probe", "name": "A capacitive soil probe on a JST PH 3-pin cable", "kind": "sensor",
 "function": [{"does": "sense", "what": "soil-moisture"}],
 "needs": [{"signal": "SOIL_MOISTURE", "pin": "Signal", "direction": "out", "needs": ["adc"]}],
 "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}],
 "unused_pins": [], "pin_order": ["GND", "VCC", "Signal"],
 "body_mm": {"width": 10, "height": 6, "verified": false, "source": "the proof's stand-in", "why_it_matters": "where the socket sits"}}
EOF
cat > "$WORK/drawer.json" <<'EOF'
[{"entry": "soil-probes", "label": "soil probes", "count": 8, "is": {"part": "x-soil-probe"}},
 {"entry": "red-leds", "label": "red LEDs, pack of 10", "count": 10, "is": {"part": "led-red-5mm"}},
 {"entry": "speaker", "label": "a 3 W speaker", "count": 2, "function": [{"does": "sound", "what": "speaker"}]},
 {"entry": "firebeetle", "label": "the FireBeetle 2 ESP32-S3", "count": 1, "is": {"board": "firebeetle2-esp32s3"}, "used_in": {"smartbin-local": 1}},
 {"entry": "lipo", "label": "a 1S LiPo", "count": 1, "function": [{"does": "power", "what": "battery"}], "used_in": {"smartbin-local": 1}}]
EOF
python3 $S --drawer-set "$WORK/drawer.json" > /dev/null
cat > "$WORK/needs.json" <<'EOF'
[{"id": "soil", "does": "sense", "what": "soil-moisture"}, {"id": "alarm", "does": "indicate", "what": "alarm"},
 {"id": "board", "does": "compute", "what": "microcontroller"}, {"id": "battery", "does": "power", "what": "battery"}]
EOF
python3 $S --needs-set "$P" "$WORK/needs.json" > /dev/null
python3 $S --step "$P" C > /dev/null
python3 $S --pick "$P" board=firebeetle2-esp32s3 > "$WORK/refused.txt" || true
grep -q "1 owned, held by smartbin-local" "$WORK/refused.txt"
cat > "$WORK/free.json" <<'EOF'
[{"entry": "firebeetle", "used_in": {}}, {"entry": "lipo", "used_in": {}}]
EOF
python3 $S --drawer-set "$WORK/free.json" > /dev/null
cat > "$WORK/passed.json" <<'EOF'
[{"need": "soil", "id": "vl6180x-breakout", "why": "it senses distance, not moisture", "by": "person"}]
EOF
python3 $S --pick "$P" soil=x-soil-probe alarm=led-red-5mm alarm=speaker board=firebeetle2-esp32s3 battery=lipo --passed-over "$WORK/passed.json"
python3 $S --step "$P" L > /dev/null
python3 $S --requirements "$P" > "$WORK/owed.txt" || true
grep -q "x-soil-probe — owes footprint, pin_order_proof, simulation" "$WORK/owed.txt"
cat > "$WORK/facts.json" <<'EOF'
{"footprint": "jst_ph_3",
 "pin_order_proof": {"verified": false, "source": "the proof's stand-in: the cable's order, GND VCC Signal"},
 "simulation": {"skip": "no Wokwi part for a soil probe; the proof does not simulate soil"}}
EOF
python3 $S --fact-set x-soil-probe "$WORK/facts.json"
python3 scripts/init_project.py --project "$P" --board firebeetle2-esp32s3 > /dev/null
python3 $S --requirements "$P"
python3 scripts/check_spine.py "$P/requirements.json" --keep "$P" | tee "$WORK/spine.txt"
grep -q "the chain runs end to end" "$WORK/spine.txt"
python3 scripts/emit_board.py "$P/requirements.json" --project "$P" > /dev/null
python3 $S --tally "$P" | tee "$WORK/tally.txt" || true
grep -q "^  5 picks: 5 from the store (5 owned) — " "$WORK/tally.txt"
/usr/bin/grep -c '"event":"built"' "$SPARK_HOME/history.jsonl"
echo "the scratch proof holds"
```

Expected: it ends `the scratch proof holds`, after printing `1` for the built line. Each `grep -q` is a gate: the
refusal names smartbin-local; the requirements file is refused while the probe owes three facts; the chain runs end
to end; `emit_board.py` without `--assume-missing-sizes` exits 0, so no part was placed on a placeholder outline; the
line begins with the picks' part. The cost part depends on where it runs: inside Claude Code it counts the session's
lines between the steps; outside it says the cost was not counted. Neither is asserted here — Task 12's line is.

- [ ] **Step 2:** if any gate fails, stop and debug (superpowers:systematic-debugging). A `jst_ph_3` footprint
  tscircuit does not know is a finding for Task 12 too: SEN0193 takes the same string.
- [ ] **Step 3:** keep the run's output for the pull request. No commit.

---

### Task 12: The real run — the plant alarm, on the PO's store, with the PO

The value proof. It writes the PO's real store and one spark commit, so it runs with the PO, in one Claude Code
session (the cost line reads that session's transcript), from the `p97-store-1c` checkout. **Inside the C and L
windows do no GitHub, web or board work, and read no screenshots:** the counter would count them. Run each command
below on its own, read its output, then go on.

- [ ] **Step 1: The state, read only.** `scripts/parts.py --audit` (note each layer's counts) and
  `scripts/parts.py --kept dfr0954` (expected: nothing kept — so checked on 2026-10-06).
- [ ] **Step 2: C starts.** `scripts/parts.py --step ~/Development/plant-alarm C`, then
  `scripts/parts.py --match ~/Development/plant-alarm` — note the speaker's and the LiPo's entry keys.
- [ ] **Step 3: The refusal — value proof 1.**
  `scripts/parts.py --pick ~/Development/plant-alarm board=firebeetle2-esp32s3 --dry-run` — expected: exit 1 and
  `firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here`. Show the PO.
- [ ] **Step 4: The PO's choice (open question 1, answered 2026-10-07).** The S3 and the LiPo stay with the bin. The
  PO names another ESP32 from his drawer for the alarm; if it has no record, the run ends after the refusal and the
  other picks, and `check_spine [ok]` stands on Task 11. Do not free the bin's entries.
- [ ] **Step 5: The picks.** Ask the PO for his reasons for what he passed over in M (the DFPlayer Pro, the XIAO, the
  piezo as the simpler road), written in his words to a JSON file with the Write tool; then
  `scripts/parts.py --pick ~/Development/plant-alarm soil=sen0193-soil-moisture alarm=max98357a-dfr0954 alarm=<the speaker's key> board=firebeetle2-esp32s3 battery=<the LiPo's key> --passed-over <file> --dry-run`,
  then without `--dry-run`. Expected: five reservations and no refusal.
- [ ] **Step 6: L starts.** `scripts/parts.py --step ~/Development/plant-alarm L`.
- [ ] **Step 7: SEN0193's owed facts, in its home (your catalog).** Write to a file: `footprint` `"jst_ph_3"`;
  `pin_order_proof` from its `//pin_order` note — `{"verified": false, "source": "J1 'CON/SIP3' on the V1.0 schematic:
  1 GND, 2 VCC, 3 Signal — read off the drawing", "cites": {"document": "sen0193-capacitive-soil-moisture-sensor-schematics-1-0", "at": "J1"}}`
  — and `simulation` by open question 2 (default: `{"wokwi": {"part": "wokwi-potentiometer", "pins": {"GND": "GND", "VCC": "VCC", "Signal": "SIG"}, "stand_in": "Wokwi's potentiometer: its SIG is a level a scenario sets; it does not model soil, the probe's 1.2-3.0 V range or its drift"}}`).
  `scripts/parts.py --fact-set sen0193-soil-moisture <file> --dry-run`, then without. Expected: `--audit` no longer
  lists it as owing those three.
- [ ] **Step 8: The DFR0954's footprint, in its home (spark's repository) — ruling 1, open question 3.** Find the
  dimension drawing's URL (by default from DFRobot's wiki page, a counted request), add it to
  `parts/max98357a-dfr0954.json` as `"sources": ["<url>"]`, then — with the PO's yes, it reaches the network —
  `scripts/parts.py --fetch max98357a-dfr0954` (expected: one document kept under its sha256, `documents` written into
  the record). Read the kept drawing; write `footprint` (a footprinter string whose pad count is the record's 12 pads,
  or the drawing's own) and a `//footprint` note citing the drawing's page. `scripts/parts.py --validate` → ok;
  `scripts/parts.py --audit` → the library's DFR0954 owes nothing. Commit on the branch:
  `P97 real run: the DFR0954's footprint from DFRobot's dimension drawing — fetched once, kept in the store, cited by its sha256`.
- [ ] **Step 9: The building list.** `scripts/init_project.py --project ~/Development/plant-alarm --board firebeetle2-esp32s3`,
  then `scripts/parts.py --requirements ~/Development/plant-alarm --dry-run` and without. Expected: board
  `firebeetle2-esp32s3`; parts `sen0193-soil-moisture`, `max98357a-dfr0954`; SEN0193 onto the shelf; the speaker and
  the LiPo reserved, not placed.
- [ ] **Step 10: The build — value proof 3, and no placeholder outline.**
  `PATH="$HOME/Development/smartbin-local/node_modules/.bin:$PATH" scripts/check_spine.py ~/Development/plant-alarm/requirements.json --keep ~/Development/plant-alarm`
  — expected: ends `the chain runs end to end`. Then
  `scripts/emit_board.py ~/Development/plant-alarm/requirements.json --project ~/Development/plant-alarm > /dev/null; echo $?`
  — expected: `0`. If the potentiometer stand-in stops the simulation stage, open question 2's fallback is a skip: set
  it with `--fact-set`, then `--requirements` and `check_spine` again.
- [ ] **Step 11: The line — value proof 4.** `scripts/parts.py --tally ~/Development/plant-alarm`. Expected (an
  estimate until read, W20): `5 picks: 5 from the store (5 owned) — 1 request, 1 document, N min` — 2 requests if the
  URL took a read of the wiki page. Show the PO; copy the line exactly as printed.
- [ ] **Step 12: Value proof 2, from the record.** `git show --stat HEAD` (the DFR0954 commit) and `scripts/parts.py
  --show max98357a-dfr0954` — the footprint filled in its own home, its drawing kept and cited.

---

### Task 13: Close P97

- [ ] `python3 tools/mutate.py --anchors tests/mutations/*.json` clean; the suite `OK`; `tools/check_commit.py HEAD`
  prints the size line — read it, then write the growth on the Done line (W13, W15b).
- [ ] One fresh reviewer, on the most capable model, reads the branch from the plan's commit to HEAD against this plan
  and the spec. Critical and Important findings get one fix pass, each with its test and mutation.
- [ ] Spark's story map, slice 10's row: `1c **P97** (#18) (picks to a building list — with **P90** (#21))` becomes
  `1c P97 (done <date> — picks to a building list, tallied); **P90** (#21) and **P89** (#20) stay their own items`
  (`tests/test_orphans.py` passes).
- [ ] Push (`git push`); then check GitHub's head, not the local tracking ref:
  `gh api repos/xmejkal/spark/branches/p97-store-1c --jq .commit.sha` equals `git rev-parse HEAD`.
- [ ] Open the pull request `P97: store 1c — picks to a building list, tallied`, its body saying `Closes #18`, the
  four value proofs as Task 12 printed them, the scratch proof's gates, the size line with why, and the PO's answers to
  the three open questions. Comment the Done line on #18 and move the card as `scrum/README.md`'s flow says. The merge
  is the PO's.

---

## Self-review (2026-10-06)

**Spec coverage, store 1c (§4).** C1 — Task 6 (`--pick <project> <need>=<id> --json`; `passed_over` lines with the
reason and who gave it). C2 — Task 6 (refused past what another project holds, naming the holder; the person frees it
with `--drawer-set` or picks another). L1 — Tasks 8–9 and 12 (owed facts filled in the record's own home; `/spark:init
--board <pick>` after C; the requirements file; `check_spine [ok]`; no placeholder outline — the PO's decision 3, by
the requirements file refusing a pick that owes `body_mm` and by Task 11's and 12's `emit_board` gate). T1 — Tasks
9–10 (`reused` at pick time, `built` from `check_spine`, `passed_over` per reason; the one cost line). Foundations:
the fetcher and the checked keep (Task 7), the history (Task 5), the cost counter (Task 10), reservations (Task 6),
promotion into the shelf (Task 9). §6.5: parts.py's two doors behind the fetcher (Task 7). §6.7: `tools/research_cost.py`
goes (Task 10). §8 C (1)–(3), L (1)–(3), T (1)–(2): Tasks 6, 8, 9, 10. The PO's decisions of 2026-10-06: 1 (Task 3),
2 (Task 9's doc edits), 3 (Tasks 9, 11, 12). The eight carry-overs: Tasks 1, 2, 3, 4, 7, 8.

**Placeholders.** None in code. Task 12's `<the speaker's key>`, `<the LiPo's key>`, `<file>` and `<url>` are values
that run reads from its own earlier output, said where each comes from.

**Type consistency.** `_candidate(need, functions, names, holding, said, mine=None)`, `_counts(holding, mine=None)`,
`candidates(need, known, entries, mine=None)` (Tasks 1–3); `_pointing(entries) -> {(kind, id): [(key, entry)]}` and
`_held(pick, entries, pointing)` used by `plan_pick` (Task 6) and `owned` (Task 10); `plan_pick(...)` returns five
values, `_op_pick` unpacks five; `requirements(...)` returns four, `_op_requirements` unpacks four;
`store.add_project(folder, dry_run=False)` (Task 6) used by Tasks 6 and 10; `store.project_name` (Task 2) used by Tasks
2, 9, 10; `_record_path` returns `(path, source)` everywhere after Task 8 (its one caller is `_set_in_home`);
`shelve(path, project_name=None)` (Task 9) keeps `drawer.apply`'s two-argument call; `digest(record, facts=BUILD_FACTS)`
keeps `_shelf_copy`'s one-argument call.

**Review Focus.** Five lines, each with its test in its owning task: 1 and 2 in Task 6, 3 and 4 in Task 9, 5 in Task 10.
