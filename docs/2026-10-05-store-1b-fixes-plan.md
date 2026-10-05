# Store 1b — the council's fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** PR #2 (P96, store 1b) merges with every Important finding of the council of 2026-10-05 fixed. The matcher
judges by the need's verb and words. `/spark:idea` works on the copy `--match` reads. Nothing writes into spark's
library. One bad record never takes the walk down. The write commands answer the way the drawer's do. Refactoring comes
last, and only what this PR needs.

**Architecture:** No new module. The fixes land where the findings point: `scripts/needs.py` (the matcher and the needs
file), `scripts/parts.py` (`function_of`, `broken_problems`, `audit`, and the `--function-set`, `--match` and
`--needs-set` handlers), `scripts/drawer.py` (`linkable`), `commands/idea.md`, one library record, and four lines of
the design doc. The needs file's checks become one table in the same edit that makes read and write agree.

**Tech Stack:** Python 3 standard library (`scripts/`), `unittest`, `tools/mutate.py`.

**Spec:** `docs/2026-10-04-store-design.md` v2: §4 store 1b, §5.3, §5.4, §5.6, §6.2, §8 S and M. The P96 plan
`docs/2026-10-04-store-1b-plan.md` and its rulings stand. The findings come from the council of 2026-10-05 (four
lenses: bugs, agent contract, tests, design), consolidated below. This plan was reviewed by a three-lens plan council
on the same day: tests and correctness (it ran Tasks A–D in a clone), scope, and contract. Its edits are in.

## The findings, in the order they are fixed

The PO's order (2026-10-05): **functionality first, refactoring last.** Among the functional fixes, the rank is what a
person gets if the finding ships. The four reports label 13 findings Important. Three of them are the same finding seen
twice, so 10 are distinct. The plan also fixes a design Refactor finding (read and write disagree), because it changes
an answer. It fixes two findings its lenses graded lower (bugs 9, contract 5), at about three lines each. Contract 7's
last point is left: `--match` on an unknown folder exits 2, while `--needs` exits 0.

| rank | finding (lens) | what the person gets if it ships | task |
| --- | --- | --- | --- |
| 1 | `what_matches` compares across every verb and never splits words; the text never shows what a candidate does (bugs 5, contract 1, tests 1) | an agent marks a soil sensor `have` for a distance need; SEN0193 ranks last for "soil moisture" | A |
| 1 | a used-up drawer entry (count 0) is still offered (bugs 6) | a part he no longer has is offered first | A |
| 1 | a candidate with the need's words is cut by the 8-row cap (bugs 5) | with a full drawer, the record that fits is never shown | A |
| 2 | `idea.md` runs `--audit` and `--function-set` without `--project`, and so does the audit's hint (bugs 1) | a part he has reads as a gap after a write that said "set" | B |
| 2 | `--function-set` writes spark's read-only library and does not say which file it changed; the shipped inlet record says nothing (bugs 2, contract 3) | a silent edit outside his project, lost on the next update | B |
| 2 | `idea.md` asks for "what each would cost" (contract 2); the spec says reasons go into `needs.json` (contract 8) | the agent invents a price; the spec contradicts the code | B |
| 3 | one malformed record crashes `--audit` and `--match` (bugs 3) | a traceback instead of the store's answer | C |
| 3 | `--audit` never walks a record the drawer links to in another project (bugs 4) | a broken record he owns passes the walk | C |
| 4 | read and write check a need differently: `"does": "fly"` passes the read (design 1) | `--match` says a need has no verb when it has a wrong one | D |
| 4 | `written` means "bytes changed" in the two new commands and "carried out" everywhere else (design 3) | an agent's harmless retry reads as a failure | B, D |
| 4 | a refused item is named `None`, and a refusal also says "nothing to change" (contract 4, 5) | the agent cannot tell which item to fix | D |
| 4 | an unknown top-level key in `needs.json` is dropped on the next write (bugs 9) | a line he wrote by hand vanishes without a word | D |
| 5 | `_known` and `_record_path` resolve records differently from `drawer.linkable`; a project's own boards are never candidates (design 2) | `--match` and `--function-set` can see different records | E |
| last | one candidate builder; shared write lines (design 4, 3) | about 7 fewer code lines (design lens); only P97 needs them | F, **the PO's call** |

**Deferred, with the reason.** Each goes on P97's entry in the backlog in Task G.
- **The lock and the atomic writes** (bugs 7, design 5): a lock around plan-and-write, and one atomic `store.write_file`
  that also makes `_write_record`'s project write atomic. P97's reservations write `needs.json` and the drawer together
  and need that lock, so it is built there, once.
- **A project's own reservations counting as not free** (bugs 8): no reservation exists until P97.
- **`--function-set` on a shelf copy** (tests lens): in this PR it says the file it writes, and `idea.md` warns that a
  re-shelve overwrites it. P97 resolves the source through `based_on`.
- **Removing or renaming a need** (contract 6): one sentence in `idea.md` says how to fix one by hand (Task B).
- **`validate` returning (key, sentence) pairs** instead of `_about` reading its English (design, Later): about 75
  sites, so it is its own item.
- **A used-up entry that points at a record** still lends that record its `function` (tests lens, a hypothesis). The
  record is then offered with owned 0, as a `know`. That is not wrong, so it is noted only.

## Global Constraints

- **Branch `p96-store-1b`, PR #2** (W8); the PO merges. Nothing of P100 goes on this branch (the PO, 2026-10-05: a new
  PR for every bigger feature).
- **The order is the PO's:** Tasks A–E are functional, by rank. F is the refactors only P97 needs, and runs only if
  the PO says so. G closes.
- **Everything in the P96 plan's Global Constraints still holds:**
  - the 13 verbs, in `parts.VERBS`;
  - the four marks;
  - owed vs broken;
  - the needs file holds no owned count, place or reason;
  - store first, owned first. The spec, line 420: *"Owned first, the simpler option shown beside it, with what it
    would cost (the PO)"*;
  - the envelope, dry runs, pages of 4 KB / 20.
- **The suite never touches the person's store** (`SPARK_HOME` via `mock.patch.dict` / `in_store`), **nor spark's own
  library**. A test of the library refusal patches `parts.LIBRARY` to a scratch folder, so a RED run cannot write
  `parts/`. Tests use literal expected values. macOS resolves `/var` to `/private/var`: compare paths with `.resolve()`.
- **Each code task (A–E):**
  - its mutation table, `tests/mutations/sprint-10-p96-fix-<task>.json`, with the rows given, every mutation caught;
  - **before committing,** run `python3 tools/mutate.py --anchors tests/mutations/*.json`, re-point every row it names
    in the same commit, and re-run each table you touched;
  - the full suite green;
  - never mutate the suite guard in `store.py`.
- **`tools/mutate.py` runs take 60–165 s:** run them with a 600000 ms timeout, in the foreground. After any run that was
  killed, `git diff --stat` before going on, because a killed run can leave a file mutated.
- **Size** (W15b): Task G's Done line says the fix round's code-line growth and why; the gate prints it.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Numbers in them come from output
  already shown (W13). Shell: `/usr/bin/grep`; never a zsh loop variable named `path`.
- **Commands.** `-k` is case-sensitive and matches part of a test's name:
  - one test: `python3 -m unittest discover -s tests -t tests -p '<file>' -k <name>`
  - the suite: `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3`

## Review Focus

1. **The PO's real store** (110 drawer entries, 18 catalog drafts, his projects on the list). `--audit` and
   `--match ~/Development/plant-alarm` run without a traceback. Plant-alarm's four needs keep SEN0193, the DFR0954, the
   FireBeetle and the LiPo where P96's Done line put them. Proven in Task G by a read-only run.
2. **A need's `what` in capitals or with a trailing space** ("Soil Moisture "): it matches like "soil-moisture". Test
   in Task A.
3. **A record in both the project and the catalog:** `--function-set … --project` writes the project's copy, the one
   `--match` reads. Test in Task B.
4. **A hand-written needs file with `"does": null`:** could-not-run, naming the file, as with `"fly"`. Test in Task D.
5. **An agent retrying a write unchanged:** running `--needs-set` or `--function-set` twice with the same file reads as
   done (`written: true`, "nothing to change"), not as a failure. Tests in Tasks B and D.

## Rulings this plan makes, for the PO

1. **Owned first stays** (the PO's words in the spec). A candidate whose words match the need is never cut by the
   8-row cap. Owned candidates that do not match still come before records nobody owns.
2. **`[other words]`** marks, in text mode, a candidate that has the need's verb but other words. JSON says the same in
   `what_matches`. Whether it is similar enough stays the agent's call, said to the person (§6.2).
3. **`--function-set` refuses spark's library.** The shipped `jst-ph-2-power-inlet` gets
   `[{"does": "connect", "what": "power-inlet"}]` in this PR (W16). A test keeps every library record saying what it
   does, so the refusal is never the person's problem.
4. **`written` means carried out**: not refused and not a dry run. `--drawer-set`, `--skeleton`, `--keep` and
   `--promote` already use this meaning. A retry with nothing to change says "nothing to change".
5. **`--audit` follows the drawer's links into other projects for owed and broken only** (§5.4: "every layer and the
   drawer's links"). A linked record there that says nothing of what it does belongs to that project. It is not listed,
   so `/spark:idea` never sends `--function-set` into another project's repository.
6. **"Cost" keeps the PO's word**, and `idea.md` says what it is in 1b: what a candidate still owes before it can build.
   spark knows no prices.
7. **Read and write agree through one check table, built in Task D.** The fix and the design lens's refactor are the
   same edit, so it is done once, as a fix.
8. **One resolver (Task E) is functional.** `--match`, `--function-set` and `--audit` see the same records, and a
   project's own boards become candidates.
9. **`/spark:idea` asks for the Write tool the way `/spark:drawer` does**, without adding it to `allowed-tools`. The
   person gets the same prompt the drawer gives.

---

## File structure

| file | what changes |
| --- | --- |
| `scripts/needs.py` | A: `_what_matches(need, …)`, count 0, aliases; D: `CHECKS`/`faults` replace `_file_fault` and `_problems`, `read` refuses stray keys, `plan_set` names items; E: `_known` deleted |
| `scripts/parts.py` | A: the cap and the text row; B: `--function-set` (library refusal, `path`, `written`, nothing to change), the audit hint, the OPERATIONS row; C: `function_of`, `broken_problems`, `audit`; D: `_op_needs_set`; E: `_record_path` |
| `scripts/drawer.py` | E: `linkable(project=None)` |
| `commands/idea.md` | B: `--project`, `[other words]`, cost, ids, when to audit, the Write tool, paging, the shelf |
| `parts/jst-ph-2-power-inlet.json` | B: a `function` |
| `docs/2026-10-04-store-design.md`, `README.md` | B: M1, M2, §5.6's matching sentence and the matcher row; the `/spark:idea` row |
| `tests/test_needs.py`, `tests/test_parts.py`, `tests/test_self_confirmation.py` | as each task says |
| `scrum/PRODUCT_BACKLOG.md`, `scrum/STORY_MAP.md` | Task 0 and Task G: P96's entry and place; P97's deferred list |

---

### Task 0: The plan, recorded

- [ ] `scrum/PRODUCT_BACKLOG.md`, P96's heading: replace `— DONE 2026-10-04` with `— in PR #2: the council's fix round, 2026-10-05`.
  Append to its entry:

  ```
  **Council review, 2026-10-05 (PR #2):** four lenses labelled 13 findings Important, 10 of them distinct; none
  Critical. They are fixed before merge by `docs/2026-10-05-store-1b-fixes-plan.md`, functionality first and refactoring
  last (the PO's order). A plan council reviewed that plan the same day.
  ```
- [ ] `scrum/STORY_MAP.md`, slice 10: `1b P96 (done 2026-10-04 — a goal matched — with **P89**)` becomes
  `1b **P96** (in PR #2, the council's fix round — a goal matched — with **P89**)`. An open item must sit on the map
  (`tests/test_orphans.py`); Task G sets it back to done.
- [ ] `python3 -m unittest discover -s tests -t tests -p 'test_orphans.py'`. Expected: `OK`.
- [ ] Commit the plan, the entry and the map (trailer).

---

### Task A: The matcher judges by the need's verb and words, and shows it (rank 1)

**Files:** Modify `scripts/needs.py` (`_what_matches`, `candidates`) and `scripts/parts.py` (`_op_match`). Test
`tests/test_needs.py` (`TheMatcherTest`). Create `tests/mutations/sprint-10-p96-fix-a.json`. Re-point
`sprint-10-p96-4.json`'s "an owned part without a record is never offered".

**Interfaces:**
- Produces: `needs._what_matches(need, functions, names) -> bool`. It takes the whole need (`does` and `what`), no
  longer `need["what"]`.
- Produces: `TheMatcherTest.catalog(*records)` and `TheMatcherTest.alone(need)`, test helpers that Tasks C and E use.
- Produces: `--match` keeps every candidate whose words match, even past the 8-row cap. The text row shows `what`, and
  `[other words]` when `what_matches` is false.

- [ ] **Step 1: Failing tests.** In `TheMatcherTest`, after `smell`:

```python
    def catalog(self, *records):
        for record in records:
            (self.home / "catalog" / (record["id"] + ".json")).write_text(json.dumps(dict({"schema": 1, "kind": "sensor"}, **record)))

    def alone(self, need):
        """One need, matched alone (a full page holds few needs): the need's answer, with its candidates and `more`."""
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [need]}))
        said, _ = run(["--match", str(self.project)])
        return said["data"]["needs"][0]

    def test_what_matches_only_through_a_function_with_the_need_s_verb(self):
        self.catalog({"id": "a-combo", "name": "A combo board", "function": [{"does": "sense", "what": "temperature"},
                                                                            {"does": "indicate", "what": "light"}]},
                     {"id": "b-light", "name": "B ambient sensor", "function": [{"does": "sense", "what": "light"}]})
        found = {c["id"]: c for c in self.alone({"id": "lux", "does": "sense", "what": "light"})["candidates"] if c["id"]}
        self.assertEqual((found["a-combo"]["what_matches"], found["b-light"]["what_matches"]), (False, True))

    def test_the_need_s_words_match_a_function_however_they_are_written(self):
        self.catalog({"id": "y-probe", "name": "SEN0193", "function": [{"does": "sense", "what": "soil-moisture"}]})
        for what in ("soil moisture", "Soil Moisture ", "soil-moisture"):
            with self.subTest(what=what):
                found = {c["id"]: c for c in self.alone({"id": "wet", "does": "sense", "what": what})["candidates"] if c["id"]}
                self.assertTrue(found["y-probe"]["what_matches"])

    def test_an_alias_matches_other_words_do_not_and_an_alias_that_is_no_list_is_ignored(self):
        self.catalog({"id": "z-dist", "name": "VL53L0X", "also_known_as": ["time of flight distance sensor"],
                      "function": [{"does": "sense", "what": "tof"}]},
                     {"id": "z-seven", "name": "Z", "also_known_as": 7, "function": [{"does": "sense", "what": "distance"}]})
        found = {c["id"]: c for c in self.alone({"id": "far", "does": "sense", "what": "distance"})["candidates"] if c["id"]}
        self.assertTrue(found["z-dist"]["what_matches"])
        self.assertTrue(found["z-seven"]["what_matches"], "matched by its function; the stray alias is passed over")
        self.assertFalse(found["x-other"]["what_matches"], "a gas sensor is not a distance sensor")

    def test_a_used_up_part_without_a_record_is_not_offered(self):
        (self.home / "drawer" / "used-up.json").write_text(json.dumps({"schema": 1, "label": "an old buzzer", "count": 0,
                                                                       "function": [{"does": "sound", "what": "buzzer"}]}))
        self.assertNotIn("used-up", [c["entry"] for c in self.alone({"id": "alarm", "does": "sound", "what": "alarm"})["candidates"]])

    def test_a_candidate_with_the_need_s_words_is_never_cut_by_the_cap(self):
        for number in range(9):
            (self.home / "drawer" / ("t%d.json" % number)).write_text(json.dumps(
                {"schema": 1, "label": "thermometer %d" % number, "count": 1, "function": [{"does": "sense", "what": "temperature"}]}))
        self.catalog({"id": "y-probe", "name": "SEN0193", "function": [{"does": "sense", "what": "soil-moisture"}]})
        self.assertIn("y-probe", [c["id"] for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"]],
                      "ten owned thermometers and probes come first; the unowned record that fits still shows")

    def test_text_mode_shows_what_each_candidate_does(self):
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [{"id": "soil", "does": "sense", "what": "soil-moisture"}]}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--match", str(self.project)])
        lines = out.getvalue().splitlines()
        self.assertIn("soil-moisture", next(line for line in lines if "x-soil (catalog)" in line))
        self.assertIn("gas [other words]", next(line for line in lines if "x-other (catalog)" in line))

    def test_a_board_owes_nothing_and_is_never_broken_here(self):
        board = [c for c in self.needs["board"]["candidates"] if c["id"] == "firebeetle2-esp32s3"][0]
        self.assertEqual((board["owes"], board["broken"]), ([], False))

    def test_a_project_s_own_record_shadows_the_same_id_elsewhere(self):
        (self.project / "parts").mkdir(parents=True)
        (self.project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "Our probe", "kind": "sensor",
                                                                         "function": [{"does": "sense", "what": "soil-moisture"}]}))
        found = [c["in"] for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"] == "x-soil"]
        self.assertEqual(found, ["project"])
```

- [ ] **Step 2: Run them.**
  `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k what_matches -k words -k alias -k used_up -k cap -k shows_what -k owes_nothing -k shadows`.
  Expected FAILs and ERRORs:
  - `a-combo` matches (True);
  - "soil moisture" does not match;
  - `z-seven` raises a TypeError;
  - `used-up` is offered;
  - `y-probe` is cut;
  - no `[other words]` in the text.

  The board test and the shadow test pass already: they pin decisions for Task E.

- [ ] **Step 3: Implement.** In `scripts/needs.py`, replace `_what_matches`:

```python
def _what_matches(need, functions, names):
    """Every word of the need's `what` in a function with the need's verb, or in the record's name or an alias (§6.2)."""
    wanted = _words(need["what"])
    return bool(wanted) and (any(wanted <= _words(f.get("what")) for f in functions if f.get("does") == need["does"])
                             or wanted <= set().union(*(_words(name) for name in names)))
```

  In `candidates`'s record loop, after the verb check, take aliases only from a list of strings:

```python
        aliases = record.get("also_known_as")
        names = [record.get("name")] + ([a for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else [])
```

  The record's candidate uses `_what_matches(need, functions, names)`. The drawer's candidate uses
  `_what_matches(need, functions, [entry.get("label")])`, and the drawer loop passes over a used-up entry:

```python
        if points_at_a_record or entry.get("skip") or entry.get("count") == 0 or not any(f.get("does") == need["does"] for f in functions):
            continue
```

  In `scripts/parts.py` `_op_match`, the cap keeps every candidate whose words match:

```python
    for need in matched:
        kept = [c for rank, c in enumerate(need["candidates"]) if rank < 8 or c["what_matches"]]
        need["more"], need["candidates"] = len(need["candidates"]) - len(kept), kept
```

  The candidate row says what the candidate does, and the "more" line says what was left out:

```python
        lines += ["      %-10s %-46s %s" % ("owned %s" % c["owned"] if c["owned"] else "", "%s (%s)" % (c["id"] or c["entry"], c["in"]),
                                        "  ".join(filter(None, [", ".join(c["what"]) + ("" if c["what_matches"] else " [other words]"),
                                                                "free %s" % c["free"] if c["owned"] else "",
                                                                "owes " + ", ".join(c["owes"]) if c["owes"] else ""])))
                  + ("  maybe owned — check the drawer" if c["unsure"] else "") + ("  BROKEN" if c["broken"] else "")
                  for c in need["candidates"]]
        lines += ["      … %d more, none with the need's words" % need["more"]] if need["more"] else []
```

- [ ] **Step 4: Run** the same command, then the suite. Expected: PASS; the suite `OK`.
- [ ] **Step 5: Mutation table.** `tests/mutations/sprint-10-p96-fix-a.json`:

```json
[
 {"file": "scripts/needs.py", "name": "what matches through a function of any verb",
  "find": "any(wanted <= _words(f.get(\"what\")) for f in functions if f.get(\"does\") == need[\"does\"])",
  "replace": "any(wanted <= _words(f.get(\"what\")) for f in functions)"},
 {"file": "scripts/needs.py", "name": "what matches only when written exactly alike",
  "find": "any(wanted <= _words(f.get(\"what\")) for f in functions",
  "replace": "any(str(f.get(\"what\")) == need[\"what\"] for f in functions"},
 {"file": "scripts/needs.py", "name": "aliases are trusted",
  "find": "([a for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else [])", "replace": "list(aliases or [])"},
 {"file": "scripts/needs.py", "name": "a used-up entry is offered", "find": " or entry.get(\"count\") == 0", "replace": ""},
 {"file": "scripts/needs.py", "name": "many is summed",
  "find": "    if any(entry.get(\"count\") == \"many\" for entry in live):\n", "replace": "    if False:\n"},
 {"file": "scripts/needs.py", "name": "a board owes facts",
  "find": "\"owes\": [] if kind == \"board\" else parts.owes(record)", "replace": "\"owes\": parts.owes(record)"},
 {"file": "scripts/needs.py", "name": "a record is offered twice", "find": "        if row[:2] not in seen:\n", "replace": "        if True:\n"},
 {"file": "scripts/parts.py", "name": "the cap cuts a candidate that fits",
  "find": "if rank < 8 or c[\"what_matches\"]", "replace": "if rank < 8"},
 {"file": "scripts/parts.py", "name": "the text hides other words",
  "find": "(\"\" if c[\"what_matches\"] else \" [other words]\")", "replace": "\"\""}
]
```

  Run the anchors check and re-point what it names; you will need to re-point at least `sprint-10-p96-4.json`'s "an
  owned part without a record is never offered", to
  `if points_at_a_record or entry.get("skip") or entry.get("count") == 0 or not any(f.get("does") == need["does"] for f in functions`.
  Then run `python3 tools/mutate.py tests/mutations/sprint-10-p96-fix-a.json` and every table you re-pointed.
  Expected: every mutation caught. The "many" row is caught by an error, which counts.
- [ ] **Step 6: Commit.** Message: `P96 fix A: the matcher judges by the need's verb and words, never offers a used-up part, never cuts one that fits, and says what each does` (trailer).

---

### Task B: `--function-set` and `/spark:idea` work on the project's copy, and spark's library is never written (rank 2)

**Files:**
- Modify:
  - `scripts/parts.py`: `_op_function_set`, `_op_audit`'s hint, `OPERATIONS`' `function-set` row, `import shlex`;
  - `commands/idea.md`;
  - `parts/jst-ph-2-power-inlet.json`;
  - `docs/2026-10-04-store-design.md:87`, `:88`, `:222`, `:272`;
  - `README.md:52`;
  - `tests/test_self_confirmation.py:62`.
- Test: `tests/test_parts.py` (`WhatAPartDoesTest`, `OwedIsNotBrokenTest`), `tests/test_needs.py`.
- Create: `tests/mutations/sprint-10-p96-fix-b.json`.

**Interfaces:**
- Produces: `--function-set` data `{"part", "path", "was", "now", "written"}`. `path` is the file it changes, as a
  string. `written` is `not dry_run`, because a refusal has already returned.
- Produces: a refusal (exit 1) for a record in `parts.LIBRARY`, and "nothing to change" when the record already says
  this.
- Produces: `--audit`'s hint `set it once with --function-set <part> <file> --project <project>: …` when a project is
  given.

- [ ] **Step 1: Failing tests.** In `tests/test_parts.py` `WhatAPartDoesTest` (add `import store` at the top if it is
  not there):

```python
    def a_probe_in_the_catalog(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        return home, given

    def test_function_set_refuses_spark_s_own_library_and_writes_nothing(self):
        library = Path(tempfile.mkdtemp()) / "parts"
        library.mkdir()
        record = {"schema": 1, "id": "x-inlet", "name": "An inlet", "kind": "connector"}
        (library / "x-inlet.json").write_text(json.dumps(record))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "connect", "what": "power-inlet"}]))
        with in_store(Path(tempfile.mkdtemp())), mock.patch.object(parts, "LIBRARY", library):
            said, code = run_json(["--function-set", "x-inlet", str(given)])
        self.assertEqual((said["status"], code), ("problems", 1))
        self.assertIn("spark's own library", said["problems"][0]["sentence"])
        self.assertEqual(json.loads((library / "x-inlet.json").read_text()), record)

    def test_function_set_says_which_file_it_changes(self):
        home, given = self.a_probe_in_the_catalog()
        out = io.StringIO()
        with in_store(home):
            said, _ = run_json(["--function-set", "x-soil", str(given), "--dry-run"])
            with contextlib.redirect_stdout(out):
                parts.main(["--function-set", "x-soil", str(given), "--dry-run"])
        self.assertEqual(Path(said["data"]["path"]).resolve(), (home / "catalog" / "x-soil.json").resolve())
        self.assertIn("x-soil.json", out.getvalue())

    def test_a_retried_function_set_is_carried_out_with_nothing_to_change(self):
        home, given = self.a_probe_in_the_catalog()
        out = io.StringIO()
        with in_store(home):
            run_json(["--function-set", "x-soil", str(given)])
            said, code = run_json(["--function-set", "x-soil", str(given)])
            with contextlib.redirect_stdout(out):
                parts.main(["--function-set", "x-soil", str(given)])
        self.assertEqual((code, said["data"]["written"]), (0, True))
        self.assertIn("nothing to change", out.getvalue())

    def test_function_set_with_the_project_writes_the_copy_match_reads(self):
        home, given = self.a_probe_in_the_catalog()
        project = Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        with in_store(home):
            _, code = run_json(["--function-set", "x-soil", str(given), "--project", str(project)])
        self.assertEqual(code, 0)
        self.assertIn("function", json.loads((project / "parts" / "x-soil.json").read_text()))
        self.assertNotIn("function", json.loads((home / "catalog" / "x-soil.json").read_text()))

    def test_function_set_on_a_shelf_copy_says_it_writes_the_shelf(self):
        home, given = self.a_probe_in_the_catalog()
        (home / "shelf").mkdir()
        (home / "shelf" / "x-shelved.json").write_text(json.dumps({"schema": 1, "id": "x-shelved", "name": "A probe", "kind": "sensor",
                                                                     "needs": [], "based_on": {"project": "other", "digest": "0"}}))
        with in_store(home):
            said, code = run_json(["--function-set", "x-shelved", str(given), "--dry-run"])
            shelf = store.place("shelf").resolve()
        self.assertEqual((code, Path(said["data"]["path"]).parent.resolve()), (0, shelf))

    def test_every_record_in_spark_s_library_says_what_it_does(self):
        with in_store(Path(tempfile.mkdtemp())):
            library = {part_id: path for part_id, (layer, path) in store.records("parts", parts.LIBRARY).items() if layer == "library"}
        self.assertTrue(library)
        self.assertEqual([part_id for part_id, path in sorted(library.items()) if not parts.function_of(parts._parse(path))], [])
```

  Rewrite `test_function_set_refuses_a_wrong_function_and_a_part_nobody_has` so that the wrong function is refused on a
  catalog record. The library's `tactile-button` would now be refused for another reason, so this keeps the test's
  intent; it does not fix a failure:

```python
    def test_function_set_refuses_a_wrong_function_and_a_part_nobody_has(self):
        home, given = self.a_probe_in_the_catalog()
        given.write_text(json.dumps([{"does": "measure", "what": "x"}]))
        with in_store(home):
            self.assertEqual(run_json(["--function-set", "x-soil", str(given), "--dry-run"])[1], 1)
            given.write_text(json.dumps([{"does": "sense", "what": "x"}]))
            self.assertEqual(run_json(["--function-set", "no-such-part", str(given), "--dry-run"])[1], 1)
```

  In `OwedIsNotBrokenTest`:

```python
    def test_audit_s_hint_names_the_project_it_walked(self):
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        (project / "parts").mkdir()
        (project / "parts" / "x-local.json").write_text(json.dumps({"schema": 1, "id": "x-local", "name": "A probe", "kind": "sensor"}))
        out = io.StringIO()
        with in_store(home), contextlib.redirect_stdout(out):
            parts.main(["--audit", "--project", str(project)])
        self.assertIn("--function-set <part> <file> --project %s: x-local" % project.resolve(), out.getvalue())
```

  In `tests/test_needs.py`, add a new class before `if __name__`:

```python
class TheIdeaCommandTest(unittest.TestCase):
    """commands/idea.md is followed as written (R4.2): the project is named where a command takes it as a flag, and only there."""

    def test_it_names_the_project_where_a_command_takes_it_and_only_there(self):
        lines = (ROOT / "commands" / "idea.md").read_text().splitlines()
        flagged = [line for line in lines if "--audit" in line or "--function-set" in line]
        self.assertTrue(flagged)
        for line in flagged:
            self.assertIn("--project <project>", line, line)
        for line in lines:
            if "--needs-set" in line or "--match" in line:
                self.assertNotIn("--project", line, "--needs-set and --match take the project as their argument: " + line)
```

- [ ] **Step 2: Run them.**
  - `python3 -m unittest discover -s tests -t tests -p 'test_parts.py' -k function_set -k library -k hint`
  - `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k TheIdeaCommandTest`

  Expected FAILs and ERRORs:
  - the library is not refused;
  - there is no `path`;
  - a retry says `written: false`;
  - `jst-ph-2-power-inlet` says nothing;
  - there is no `--project` in the hint or in `idea.md` (its line "`parts.py --audit` lists").

  These pass already and pin behaviour: the project-copy test (Review Focus 3), the shelf test, and the rewritten
  wrong-function test.

- [ ] **Step 3: Implement.** In `scripts/parts.py`, add `import shlex` beside `import json`. In `_op_function_set`,
  after the `path is None` check and before the function check:

```python
    if path.parent.resolve() == LIBRARY.resolve():
        return Answer(problems=[_problem(part_id, "is in spark's own library, which is changed in spark's repository, "
                                                  "not by --function-set")])
```

  and its answer, from `was, changes = …` on:

```python
    was, changes = record.get("function"), record.get("function") != function
    if changes and not args.dry_run:
        record["function"] = function
        _write_record(path, record)
    said = ("  %s %s (%s): function %s → %s" % ("would set" if args.dry_run else "set", part_id, path,
                                                json.dumps(was, ensure_ascii=False), json.dumps(function, ensure_ascii=False))
            if changes else "  nothing to change: %s (%s) already says this" % (part_id, path))
    return Answer({"part": part_id, "path": str(path), "was": was, "now": function, "written": not args.dry_run}, [said])
```

  `OPERATIONS`' `function-set` row:
  - summary: `"set what a part does — a JSON [{does, what}] in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library"`
  - data keys: `("part", "path", "was", "now", "written")`

  `_op_audit`'s hint (a project path with a space stays one word):

```python
    lines += ["  says nothing of what it does — set it once with --function-set <part> <file>%s: %s"
              % (" --project %s" % shlex.quote(str(project)) if project else "", ", ".join(silent))] if silent else []
```

  `parts/jst-ph-2-power-inlet.json`: after `"kind": "connector",`, add
  `"function": [{"does": "connect", "what": "power-inlet"}],`.

  `tests/test_self_confirmation.py:62`: add `"parts.LIBRARY": STRUCTURE,` beside `"boards.LIBRARY": STRUCTURE,`. The
  library test reads `parts.LIBRARY` as where the library is, not as a value under test.

  `commands/idea.md`:
  - **S step 1**, after "Each need has an `id` (…)", add: *"An `id` stays: there is no removing or renaming a need yet,
    so a wrong one is fixed by hand in `<project>/.spark/needs.json`, then checked with `parts.py --needs <project>`."*
  - **S step 3** reads: "write the needs as a JSON list to a file outside any repository **with the Write tool** — a word
    the person said never goes on a command line — and:".
  - **The M section** after the `--match` block becomes:

  ````
  Owned candidates come first, each with how many are owned and **free** (a part another project holds is not free),
  "maybe owned" when the person was not sure, what it does, and what it **owes** before it can build. `[other words]`
  means the candidate has the need's verb in other words: whether it is similar enough is your call, said to the person.
  With `--json`, `truncated.next` is the command for the rest of a long answer. Show the person, for each need, the
  owned option and the simpler one beside it, with what each would cost — in 1b, what it still owes before it can
  build; spark knows no prices. Then mark each need — `have` (owned, with a record), `have-unknown` (owned, no record),
  `know` (a record, not owned) or `gap` (nothing similar) — and **say why in the conversation**: the reason is not
  written to the project. Write the marks with `--needs-set` (`{"id", "mark"}`).

  When a need shows no candidate, or fewer than you expect, a record may say nothing of what it does — such a record
  is never offered. Look:

  ```
  ${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --audit --project <project>
  ```

  Only its `no_function` list is yours here; a BROKEN row, or exit 1, is for the person to know — say it, do not fix
  it. For a record that plausibly fits, write its function as a JSON list `[{"does": …, "what": …}]` to a file outside
  any repository with the Write tool, then:

  ```
  ${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --function-set <part> <file> --project <project> --dry-run
  ```

  Show the person the file it prints, then run it without `--dry-run`. A file in the store's `shelf/` is a copy: a
  later re-shelve from its project overwrites it, so say so. spark's own library is not changed from here.
  ````

  `docs/2026-10-04-store-design.md`:
  - **`:87`, M1's last cell:** replace `lists candidates by \`does\`/\`what\` (exact or alias)` with
    `lists candidates by \`does\`, and says whether every word of the need's \`what\` is in a same-verb function, the name or an alias (\`what_matches\`)`.
  - **`:88`, M2's last cell:**
    `the marks are written into \`needs.json\` through \`parts.py --needs-set\`; the reason is said to the person, not stored (amended 2026-10-05: a project file holds no reasons, §5.3; 1c keeps only a passed-over part's, §5.7)`.
  - **`:222`:** replace `Matching: the code lists candidates by \`does\` and \`what\` (exact or alias)` with
    `Matching: the code lists candidates by \`does\`, and marks those whose function, name or alias holds every word of the need's \`what\``.
  - **`:272`:** replace `the mark and its reason (agent)` with `the mark (agent; its reason is said to the person, §5.3)`.

  `README.md:52`, the `/spark:idea` row's last sentence becomes:
  `Nothing is researched until a need is a real gap; for now it stops at the marks.`

- [ ] **Step 4: Run** the Step 2 commands, then the suite. Expected: PASS; the suite `OK`.
- [ ] **Step 5: Mutation table.** `tests/mutations/sprint-10-p96-fix-b.json`:

```json
[
 {"file": "scripts/parts.py", "name": "the library is written",
  "find": "    if path.parent.resolve() == LIBRARY.resolve():\n", "replace": "    if False:\n"},
 {"file": "scripts/parts.py", "name": "the answer hides the file",
  "find": "{\"part\": part_id, \"path\": str(path), \"was\"", "replace": "{\"part\": part_id, \"path\": None, \"was\""},
 {"file": "scripts/parts.py", "name": "function-set: written means bytes changed",
  "find": "\"now\": function, \"written\": not args.dry_run}", "replace": "\"now\": function, \"written\": changes and not args.dry_run}"},
 {"file": "scripts/parts.py", "name": "a retry says it set something",
  "find": "            if changes else \"  nothing to change", "replace": "            if True else \"  nothing to change"},
 {"file": "scripts/parts.py", "name": "the audit's hint drops the project",
  "find": "(\" --project %s\" % shlex.quote(str(project)) if project else \"\", \", \".join(silent))",
  "replace": "(\"\", \", \".join(silent))"}
]
```

  Run the anchors check, re-point what it names, then run this table and any table you re-pointed. Expected: every
  mutation caught.
- [ ] **Step 6: Commit.** Message: `P96 fix B: --function-set says the file, refuses spark's library and says when nothing changes; /spark:idea names the project and says when to audit; the inlet says what it does; the spec says how matching works and that reasons are not stored` (trailer).

---

### Task C: One bad record never takes the walk down; the walk follows the drawer into other projects (rank 3)

**Files:** Modify `scripts/parts.py` (`function_of`, `broken_problems`, `audit`). Test `tests/test_needs.py` and
`tests/test_parts.py` (`OwedIsNotBrokenTest`). Create `tests/mutations/sprint-10-p96-fix-c.json`. Re-point
`sprint-10-p96-2.json`'s "every validate problem counts as broken" and "a drawer link to nothing is not named".

**Interfaces:**
- Produces: `parts.broken_problems(record, path)` never raises on a malformed record. It returns
  `["does not meet the part record's shape (…)"]`.
- Produces: `parts.audit(project)` also walks each record a drawer entry links to in one of the person's projects
  (its layer is the project's name), for owed and broken only. Such a record is never in `no_function`.

- [ ] **Step 1: Failing tests.** In `tests/test_needs.py` `TheMatcherTest` (uses Task A's `catalog` and `alone`):

```python
    def test_a_malformed_record_is_named_broken_never_a_traceback(self):
        soil = [{"does": "sense", "what": "soil-moisture"}]
        self.catalog({"id": "m-kind", "name": "m", "kind": ["sensor", "rtc"]},
                     {"id": "m-needs", "name": "m", "needs": ["SIG"], "function": soil},
                     {"id": "m-facts", "name": "m", "facts": [1, 2], "function": soil})
        found = {c["id"]: c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"]}
        self.assertEqual((found["m-needs"]["broken"], found["m-facts"]["broken"]), (True, True))
        said, code = run(["--audit"])
        self.assertEqual(code, 1)
        self.assertLessEqual({"m-needs", "m-facts"}, {b["id"] for b in said["data"]["broken"]})
        self.assertIn("m-kind", said["data"]["no_function"], "a kind that is a list says nothing, and crashes nothing")
```

  In `test_a_record_whose_function_is_malformed_is_matched_by_its_kind`, after `self.assertEqual(code, 0)`, add:

```python
        soil = [c["id"] for c in next(n for n in said["data"]["needs"] if n["need"] == "soil")["candidates"]]
        self.assertNotIn("x-nowhat", soil, "a sensor's kind says nothing, and a function with no `what` is not one")
```

  In `tests/test_parts.py` `OwedIsNotBrokenTest`:

```python
    def test_audit_walks_a_record_the_drawer_links_to_in_another_project(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "other7"
        (other / "parts").mkdir(parents=True)
        (other / "parts" / "y-soil.json").write_text(json.dumps({"schema": 1, "id": "y-soil", "name": "Soil probe Y", "kind": "sensor",
                                                                  "needs": [], "function": [{"does": "sense", "what": "soil-moisture"}],
                                                                  "facts": {"range": {"value": 3}}}))
        (other / "parts" / "z-silent.json").write_text(json.dumps({"schema": 1, "id": "z-silent", "name": "Mystery Z", "kind": "sensor", "needs": []}))
        (home / "drawer").mkdir()
        for entry, record_id in (("soil-probe-y", "y-soil"), ("mystery-z", "z-silent")):
            (home / "drawer" / (entry + ".json")).write_text(json.dumps({"schema": 1, "label": entry, "count": 3, "is": {"part": record_id}}))
        (home / "projects.json").write_text(json.dumps({"other7": str(other)}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual(code, 1)
        self.assertEqual([(b["id"], b["layer"]) for b in said["data"]["broken"]], [("y-soil", "other7")])
        self.assertNotIn("z-silent", said["data"]["no_function"], "another project's silent record is that project's to set")
```

- [ ] **Step 2: Run them.**
  - `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k malformed`
  - `python3 -m unittest discover -s tests -t tests -p 'test_parts.py' -k links_to_in_another`

  Expected:
  - the malformed-record test ERRORs with a TypeError/AttributeError traceback;
  - the malformed-function test FAILs (`x-nowhat` is offered);
  - the other-project test FAILs (`broken` is `[]`, exit 0).

- [ ] **Step 3: Implement.** In `scripts/parts.py`:

```python
def function_of(record, board=False):
    """What a record does (§5.6): its own `function`, else what its kind says, else nothing."""
    if record.get("function") and not function_problems(record):
        return record["function"]
    kind = "board" if board else record.get("kind")
    said = KIND_FUNCTION.get(kind) if isinstance(kind, str) else None
    return [{"does": said[0], "what": said[1]}] if said else []


def broken_problems(record, path):
    """What is wrong with a part record beyond what it owes (§5.4): `validate`'s problems that name no owed key."""
    owed = owes(record)
    try:
        said = validate(record, path)
    except (AttributeError, TypeError, KeyError, ValueError) as wrong:
        return ["does not meet the part record's shape (%s)" % wrong]
    return [problem for problem in said if not any(_about(problem, key) for key in owed)]
```

  `audit`: the links are resolved before the walk. A linked record in one of the person's projects is walked for owed
  and broken, and never listed as saying nothing:

```python
def audit(project=None):
    """
    Every record in every layer — the catalog included — every drawer link, and each record a link reaches in the person's
    other projects, walked once (§5.4, P89): per layer how many are current, owe facts, or are broken; which say nothing
    of what they do (spark's layers and this project only); which entries point at nothing.
    """
    import boards
    import drawer
    walked = [("part", found, layer, path) for found, (layer, path) in store.records("parts", LIBRARY, project, drafts=True).items()]
    walked += [("board", found, layer, path) for found, (layer, path) in boards.records(project).items()]
    known, mine, seen = drawer.linkable(), store.projects(), {row[3].resolve() for row in walked}
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
    counts, owed, broken, silent = {}, [], [], []
    for kind, found, layer, path in walked + linked:
        # … the loop body as it is today, except its last two lines:
        if isinstance(record, dict) and not function_of(record, board=kind == "board") and (kind, found, layer, path) not in linked:
            silent.append(found)
    return counts, owed, broken, silent, dangling
```

- [ ] **Step 4: Run** the Step 2 commands, then the suite. Expected: PASS; the suite `OK`.
- [ ] **Step 5: Mutation table.** `tests/mutations/sprint-10-p96-fix-c.json`:

```json
[
 {"file": "scripts/parts.py", "name": "a kind that is a list is looked up",
  "find": "KIND_FUNCTION.get(kind) if isinstance(kind, str) else None", "replace": "KIND_FUNCTION.get(kind)"},
 {"file": "scripts/parts.py", "name": "a malformed record raises",
  "find": "except (AttributeError, TypeError, KeyError, ValueError) as wrong:", "replace": "except ZeroDivisionError as wrong:"},
 {"file": "scripts/parts.py", "name": "a malformed function is trusted",
  "find": "    if record.get(\"function\") and not function_problems(record):\n", "replace": "    if record.get(\"function\"):\n"},
 {"file": "scripts/parts.py", "name": "the walk stops at spark's layers",
  "find": "    for kind, found, layer, path in walked + linked:\n", "replace": "    for kind, found, layer, path in walked:\n"},
 {"file": "scripts/parts.py", "name": "another project's silent record is listed",
  "find": " and (kind, found, layer, path) not in linked:", "replace": ":"}
]
```

  Run the anchors check and re-point what it names. That includes `sprint-10-p96-2.json`:
  - "every validate problem counts as broken" →
    `return [problem for problem in said if not any(_about(problem, key) for key in owed)]`
  - "a drawer link to nothing is not named" → `if where is None:\n            dangling.append(entry)`

  Then run this table and each re-pointed one. Expected: every mutation caught.
- [ ] **Step 6: Commit.** Message: `P96 fix C: a malformed record is named broken, never a traceback; --audit walks the records the drawer links to in the person's other projects` (trailer).

---

### Task D: The needs file is read and written by one table, and `--needs-set` answers the way the drawer does (rank 4)

**Files:** Modify `scripts/needs.py` (`CHECKS` and `faults` replace `NEED_FIELDS`'s tuple, `_file_fault` and
`_problems`; `read`; `plan_set`; `match`'s echo) and `scripts/parts.py` (`_op_needs_set`). Test `tests/test_needs.py`
(`TheNeedsFileTest`). Create `tests/mutations/sprint-10-p96-fix-d.json`. Re-point every row of `sprint-10-p96-3.json` and
`sprint-10-p96-final.json` that anchored in `_file_fault`, `_problems` or `_op_needs_set` (the design lens counted 8,
plus "a refused needs write is written").

**Interfaces:**
- Produces: `needs.CHECKS` ({field: (test, sentence)}), `needs.NEED_FIELDS = tuple(CHECKS)`, and
  `needs.faults(need, held_only=False) -> [sentence]`. P97's `pick` becomes one row.
- Produces: `written` = `not (problems or dry_run)` for `--needs-set`. A refused item's subject is `"item <n>"`
  (1-based) or `"the file"`. A refusal never also says "nothing to change".
- Produces: `needs.read` raises `StoreProblem`, naming the file, for:
  - a top-level key other than `schema`/`needs`;
  - a field value that the write would refuse.

- [ ] **Step 1: Failing tests.** In `TheNeedsFileTest`:

```python
    def test_a_retried_needs_set_is_carried_out_with_nothing_to_change(self):
        given = a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])
        run(["--needs-set", str(self.project), given])
        said, code = run(["--needs-set", str(self.project), given])
        self.assertEqual((code, said["data"]["written"], said["data"]["changes"]), (0, True, []))

    def test_the_file_is_refused_on_read_for_what_a_write_refuses(self):
        (self.project / ".spark").mkdir(parents=True)
        for need in ({"id": "soil", "does": "fly", "what": "x"}, {"id": "soil", "does": None, "what": "x"},
                     {"id": "soil", "does": "sense", "what": "x", "condition": ""}):
            with self.subTest(need=need):
                (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [need]}))
                said, code = run(["--needs", str(self.project)])
                self.assertEqual(code, 2)
                self.assertIn("needs.json", said["unchecked"][0]["sentence"])

    def test_a_key_the_needs_file_does_not_hold_is_refused_not_dropped(self):
        (self.project / ".spark").mkdir(parents=True)
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [], "goal": "a thirsty plant"}))
        said, code = run(["--needs", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("goal", said["unchecked"][0]["sentence"])

    def test_a_refused_item_is_named_by_its_place_and_its_value(self):
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "x"},
                                                                    {"id": "Soil2", "does": "sense", "what": "x"}])])
        self.assertEqual((code, said["problems"][0]["subject"]), (1, "item 2"))
        self.assertIn('"Soil2"', said["problems"][0]["sentence"])

    def test_a_refused_write_does_not_also_say_nothing_to_change(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "Soil2"}])])
        self.assertNotIn("nothing to change", out.getvalue())

    def test_a_later_item_sees_what_an_earlier_one_set(self):
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"},
                                                                    {"id": "soil", "mark": "have"}])])
        self.assertEqual(code, 0)
        self.assertEqual(self.saved()["needs"], [{"id": "soil", "does": "sense", "what": "soil-moisture", "mark": "have"}])

    def test_a_new_need_with_no_what_is_refused(self):
        self.assertEqual(run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense"}])])[1], 1)
```

- [ ] **Step 2: Run them.**
  `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k retried -k refused_on_read -k does_not_hold -k place_and -k nothing_to_change -k later_item -k no_what`.
  Expected FAILs:
  - `written` is False on a retry;
  - `fly`, `null` and `""` read as ok;
  - `goal` is accepted;
  - the subject is `None`;
  - "nothing to change" is printed with a refusal.

  The last two tests pass already: they pin `plan_set` for the table.

- [ ] **Step 3: Implement.** In `scripts/needs.py`, replace `NEED_FIELDS`, `_file_fault` and `_problems` with:

```python
#: Each field of a need besides its `id` (§5.3): its test, and what is said when a value fails it — read and write alike.
#: A pick is 1c's, and will be one more row.
CHECKS = {"does": (lambda v: v in parts.VERBS, "`does` is one of %s" % ", ".join(parts.VERBS)),
          "what": (drawer._words, "`what` is a few words: soil-moisture, alarm, microcontroller"),
          "condition": (lambda v: v is None or drawer._words(v), "`condition` is words, or null"),
          "mark": (lambda v: v is None or v in MARKS, "`mark` is one of %s, or null" % ", ".join(MARKS))}
NEED_FIELDS = tuple(CHECKS)


def faults(need, held_only=False):
    """What is wrong with one need's fields (§5.3) — on read only the values the file holds: an absent one is --needs-set's to fill."""
    extra = sorted(set(need) - set(NEED_FIELDS) - {"id"})
    return (["%s: not a need's field — a need holds %s, and no part number, count, place or reason (§5.3)"
             % (", ".join(extra), ", ".join(NEED_FIELDS))] if extra else []) + [
        sentence for key, (test, sentence) in CHECKS.items() if (key in need or not held_only) and not test(need.get(key))]
```

  `read`, after the shape check and before the schema check:

```python
    stray = sorted(set(data) - {"schema", "needs"})
    if stray:
        raise store.StoreProblem("%s holds %s, which a needs file does not — fix it by hand" % (path, ", ".join(stray)))
```

  and its loop over the needs:

```python
    ids = [need["id"] for need in data["needs"]]
    for need in data["needs"]:
        said = ((["`id` is not lower-case letters, digits and '-'"] if not store.PLAIN.fullmatch(need["id"]) else [])
                + (["is there more than once"] if ids.count(need["id"]) > 1 else []) + faults(need, held_only=True))
        if said:
            raise store.StoreProblem("%s: need %r: %s — fix it by hand" % (path, need["id"], said[0]))
    return data["needs"]
```

  `plan_set`:

```python
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return None, [], [parts._problem("the file", "a needs write is a JSON list of needs, each an object with an `id`")]
    current = {need["id"]: dict(need) for need in read(project)}
    order, changes, problems = list(current), [], []
    for number, item in enumerate(items, 1):
        need_id = item.get("id")
        if not (isinstance(need_id, str) and store.PLAIN.fullmatch(need_id)):
            problems.append(parts._problem("item %d" % number, "a need's `id` is lower-case letters, digits and '-', not %s"
                                           % json.dumps(need_id, ensure_ascii=False)))
            continue
        before = current.get(need_id)
        after = dict(before or {}, **{key: (drawer.clean(value) if isinstance(value, str) else value) for key, value in item.items()})
        problems += [parts._problem(need_id, sentence) for sentence in faults(after)]
        # … `changed`, `changes`, `order` and `current[need_id] = after` as they are today …
```

  `match`'s echo: `{key: need.get(key) for key in NEED_FIELDS}`.

  In `scripts/parts.py` `_op_needs_set`:

```python
    written = not (problems or args.dry_run)
    if written and changes:
        needs.write(target, after)
    lines = ["  %s%s %s: %s" % ("refused, not written: " if problems else "", "would set" if args.dry_run else "set",
                                c["need"], ", ".join("%s → %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in c["now"].items()))
             for c in changes] or ([] if problems else ["  nothing to change"])
```

- [ ] **Step 4: Run** the same command, then the suite. Expected: PASS; the suite `OK`.
  `test_text_mode_says_why_a_needs_set_was_refused` still reads `soil — why: not a need's field`.
- [ ] **Step 5: Mutation table.** `tests/mutations/sprint-10-p96-fix-d.json`:

```json
[
 {"file": "scripts/parts.py", "name": "needs-set: written means bytes changed",
  "find": "    written = not (problems or args.dry_run)\n    if written and changes:\n        needs.write",
  "replace": "    written = bool(changes) and not (problems or args.dry_run)\n    if written and changes:\n        needs.write"},
 {"file": "scripts/parts.py", "name": "a refusal also says nothing to change",
  "find": "or ([] if problems else [\"  nothing to change\"])", "replace": "or [\"  nothing to change\"]"},
 {"file": "scripts/needs.py", "name": "any verb is one", "find": "\"does\": (lambda v: v in parts.VERBS,", "replace": "\"does\": (lambda v: True,"},
 {"file": "scripts/needs.py", "name": "an empty condition is words",
  "find": "\"condition\": (lambda v: v is None or drawer._words(v),", "replace": "\"condition\": (lambda v: v is None or isinstance(v, str),"},
 {"file": "scripts/needs.py", "name": "a write checks only what it was given",
  "find": "if (key in need or not held_only) and not test", "replace": "if key in need and not test"},
 {"file": "scripts/needs.py", "name": "a stray key is dropped", "find": "    if stray:\n", "replace": "    if False:\n"},
 {"file": "scripts/needs.py", "name": "a refused item is named None",
  "find": "parts._problem(\"item %d\" % number,", "replace": "parts._problem(None,"},
 {"file": "scripts/needs.py", "name": "a later item forgets an earlier one", "find": "        current[need_id] = after\n", "replace": "        pass\n"}
]
```

  Run the anchors check and re-point every row it names in `sprint-10-p96-3.json` and `sprint-10-p96-final.json`
  (`_file_fault` and `_problems` are gone: point each row at the `CHECKS` row or the `read` line that now holds its
  rule; "a refused needs write is written" points at `written = not (problems or args.dry_run)`, replaced by
  `written = not args.dry_run`). Then run this table and each re-pointed one. Expected: every mutation caught.
- [ ] **Step 6: Commit.** Message: `P96 fix D: one table checks a need on read and on write; written means carried out; the needs file keeps nothing it does not hold; a refused item is named` (trailer).

---

### Task E: One resolver — `drawer.linkable(project)` (rank 5)

**Files:** Modify `scripts/drawer.py` (`linkable`), `scripts/needs.py` (delete `_known`), and `scripts/parts.py`
(`_record_path`, `audit`). Test `tests/test_needs.py` (`TheMatcherTest`). Re-point Task A's "a record is offered twice".

**Interfaces:**
- Produces: `drawer.linkable(project=None)`: the project's own records (layer `"project"`) first, then spark's layers,
  then the person's projects. `--match`, `--function-set` and `--audit` all resolve through it.

- [ ] **Step 1: Failing test.** In `TheMatcherTest`:

```python
    def test_a_project_s_own_board_is_a_candidate(self):
        (self.project / "boards").mkdir(parents=True)
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        (self.project / "boards" / "my-own-board.json").write_text(json.dumps(dict(board, id="my-own-board")))
        found = [c["in"] for c in self.alone({"id": "mcu", "does": "compute", "what": "microcontroller"})["candidates"] if c["id"] == "my-own-board"]
        self.assertEqual(found, ["project"])
```

- [ ] **Step 2: Run** `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k own_board`. Expected: FAIL (`[]`).
- [ ] **Step 3: Implement.**
  - `drawer.linkable(project=None)` passes `project` on:
    `store.records("parts", parts.LIBRARY, project, drafts=True)` and `boards.records(project)`.
  - Delete `needs._known`. `match` calls `drawer.linkable(project)`.
  - `parts._record_path` becomes:

    ```python
    def _record_path(part_id, project):
        """A part record's own file: the nearest layer that has it, the catalog included, else a project on the person's list."""
        import drawer
        return next((path for kind, found, _, path in drawer.linkable(project) if (kind, found) == ("part", part_id)), None)
    ```

  - `audit` uses `known = drawer.linkable(project)`.
- [ ] **Step 4: Run** it, then the suite. Expected: PASS; the suite `OK`. Task A's shadow test and Task B's project-copy
  test still pass: they are this task's net.
- [ ] **Step 5: Mutations.** In `sprint-10-p96-fix-a.json`, re-point "a record is offered twice" at `linkable`:
  - find: `        unique.setdefault(row[:2], row)\n`
  - replace: `        unique[row[:2]] = row\n`

  Run the anchors check and that table. Expected: every mutation caught.
- [ ] **Step 6: Commit.** Message: `P96 fix E: one resolver, drawer.linkable(project) — --match, --function-set and --audit see the same records, a project's own boards included` (trailer).

---

### Task F: The two refactors only P97 needs — **only if the PO says now**; otherwise P97's first task

The plan council (scope lens) recommends moving both to P97, which will touch the same lines for `pick` and `proof`
(W14: pull, never push). If the PO says now, each is one commit, run with the anchors rule:

- **F1, one candidate builder** (`scripts/needs.py`). The design lens measured −5 lines and 3 anchors.

  ```python
  def _candidate(need, functions, names, holding, said):
      """One candidate (§6.2): `said` names it and where it lives; the rest is what its verb's functions say, and its counts."""
      owned, free, unsure = _counts(holding)
      return dict({"id": None, "kind": None, "entry": None, "owes": [], "broken": False, "proof": []}, **said,
                  what=sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                  what_matches=_what_matches(need, functions, names), owned=owned, free=free, unsure=unsure)
  ```

  Both loops in `candidates` append through it and keep their conditions.
- **F2, the write lines, shared** (`scripts/parts.py`). The design lens measured about −2 lines and 3 anchors.
  `_write_lines(changes, problems, dry_run, said=())` serves `_drawer_answer` and `_op_needs_set`, and `_change_line`
  names `change.get("entry") or change.get("need")`. It changes one output: the needs dry-run line becomes
  `would set soil: mark null → "have"`. Pin that first with a test that is RED before.

---

### Task G: Close — measured, checked on the real store, reviewed

- [ ] `python3 tools/mutate.py --anchors tests/mutations/*.json` is clean; the suite is `OK`; `tools/check_commit.py`
  prints the size line.
- [ ] **The real store, read only** (Review Focus 1): run `scripts/parts.py --audit` and
  `scripts/parts.py --match ~/Development/plant-alarm`. Expected:
  - no traceback;
  - plant-alarm's four needs as P96's Done line says.

  Whatever the walk now finds in his other projects goes to the PO as found. It is not fixed here.
- [ ] Update the backlog and the map, then commit and push the branch:
  - `scrum/PRODUCT_BACKLOG.md`, P96's entry: the fix round's size line (W15b), and its heading `— DONE <date>` (the
    last fix commit's date, R7);
  - `scrum/STORY_MAP.md`: `**P96**` gets its `done <date>` back;
  - P97's entry: the deferred list from the top of this plan, plus Task F if the PO deferred it;
  - `test_orphans.py` is `OK`.
- [ ] One fresh reviewer, on the most capable model, reads this plan's range once: Task 0's commit to HEAD. Critical
  and Important findings get one fix pass. Then the PO merges PR #2.
