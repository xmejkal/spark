# Store 1b — the council's fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** PR #2 (P96, store 1b) merges with every Important finding of the council of 2026-10-05 fixed: the matcher judges by
the need's verb and words, `/spark:idea` works on the copy `--match` reads, nothing writes into spark's library, one bad
record never takes the walk down, and the write commands answer the way the drawer's do. The refactors come last.

**Architecture:** No new module. The fixes land where the findings point: `scripts/needs.py` (the matcher and the needs
file), `scripts/parts.py` (`function_of`, `broken_problems`, `audit`, the `--function-set`, `--match` and `--needs-set`
handlers), `commands/idea.md`, one library record, and two lines of the design doc. The refactors then fold the needs
checks into one table, give `drawer.linkable` the project, build candidates in one place and share the write lines.

**Tech Stack:** Python 3 standard library (`scripts/`), `unittest`, `tools/mutate.py`.

**Spec:** `docs/2026-10-04-store-design.md` v2 — §4 store 1b, §5.3, §5.4, §5.6, §6.2, §8 S and M. The P96 plan
`docs/2026-10-04-store-1b-plan.md` and its rulings stand; this plan adds to them. Findings: the council of 2026-10-05
(four lenses: bugs, agent contract, tests, design), consolidated in the table below.

## The findings, in the order they are fixed

The PO's order (2026-10-05): **functionality first, refactoring last.** Inside the functional fixes, the rank is what a
person gets if the finding ships.

| rank | finding (lens) | what the person gets if it ships | task |
| --- | --- | --- | --- |
| 1 | `what_matches` compares across every verb, never splits words; the text never shows what a candidate does (bugs 5, contract 1, tests 1) | an agent marks a soil sensor `have` for a distance need; SEN0193 ranks last for "soil moisture" | A |
| 1 | a used-up drawer entry (count 0) is still offered (bugs 6) | a part he no longer has is offered first | A |
| 1 | a candidate with the need's words is cut by the 8-row cap (bugs 5) | with a full drawer, the record that fits is never shown | A |
| 2 | `idea.md` runs `--audit` and `--function-set` without `--project`; the audit's hint too (bugs 1) | a part he has reads as a gap after a write that said "set" | B |
| 2 | `--function-set` writes spark's read-only library; the shipped inlet record says nothing (bugs 2, contract 3) | a silent edit outside his project, lost on the next update | B |
| 2 | `idea.md` asks for "what each would cost" (contract 2); the spec says reasons go into `needs.json` (contract 8) | the agent invents a price; the spec contradicts the code | B |
| 3 | one malformed record crashes `--audit` and `--match` (bugs 3) | a traceback instead of the store's answer | C |
| 3 | `--audit` never walks a record the drawer links to in another project (bugs 4) | a broken record he owns passes the walk | C |
| 4 | `written` means "bytes changed" in the two new commands, "carried out" everywhere else (design 3) | an agent's harmless retry reads as a failure | D |
| 4 | read and write check a need differently: `"does": "fly"` passes the read (design 1) | `--match` says a need has no verb when it has a wrong one | D |
| 4 | a refused item is named `None`; a refusal also says "nothing to change" (contract 4, 5) | the agent cannot tell which item to fix | D |
| 4 | an unknown top-level key in `needs.json` is dropped on the next write (bugs 9) | a line he wrote by hand vanishes without a word | D |
| — | tests that pin decisions no test pins yet (tests lens) | the refactors would have no net | E |
| last | one check table for needs; `linkable(project)`; one candidate builder; shared write lines (design 1, 2, 4, 3) | about 40 fewer code lines (the design lens's measure); P97's `pick` and `proof` become one-place edits | F |

**Deferred, with the reason** (each goes on P97's entry in the backlog in Task G):
- a lock around plan-and-write, and one atomic `store.write_file` (bugs 7, design 5): P97's reservations write
  `needs.json` and the drawer together and need exactly that lock, so it is built there, once;
- a project's own reservations counting as not free (bugs 8): no reservation exists until P97;
- `--function-set` on a shelf copy (tests lens): P97 resolves the source through `based_on`;
- removing or renaming a need (contract 6): one sentence in `idea.md` says how to fix one by hand (Task B);
- `validate` returning (key, sentence) pairs instead of `_about` reading its English (design, Later): about 75 sites, its own item.

## Global Constraints

- **Branch `p96-store-1b`, PR #2** (W8); the PO merges. Nothing of P100 goes on this branch (the PO, 2026-10-05: a new PR
  for every bigger feature).
- **The order is the PO's:** Tasks A–D (functional, by rank), E (the test net), F (refactors), G (close).
- **Everything the P96 plan's Global Constraints say still holds:** the 13 verbs in `parts.VERBS`; the four marks; owed
  vs broken; the needs file holds no owned count, place or reason; store first, owned first (the spec, line 420: *"Owned
  first, the simpler option shown beside it, with what it would cost (the PO)"*); the envelope, dry runs, pages of 4 KB / 20.
- **The suite never touches the person's store** (`SPARK_HOME` via `mock.patch.dict` / `in_store`), **nor spark's own
  library**: a test of a library refusal patches `parts.LIBRARY` to a scratch folder, so a RED run cannot write `parts/`.
  Tests use literal expected values.
- **Each code task (A–F):** its mutation table `tests/mutations/sprint-10-p96-fix-<task>.json` (rows as given), every
  mutation caught (`python3 tools/mutate.py <table>`, in the foreground); `python3 tools/mutate.py --anchors
  tests/mutations/*.json` clean before every commit; the full suite green. A refactor that breaks an anchor re-points it
  in the same commit and re-runs that table. Never mutate the suite guard in `store.py`.
- **Size** (W15b): Task G's Done line says the fix round's code-line growth and why; the gate prints it.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; numbers in them come from output
  already shown (W13). Shell: `/usr/bin/grep`; never a zsh loop variable named `path`.
- **Commands:** one test — `python3 -m unittest discover -s tests -t tests -p '<file>' -k <name>`; the suite —
  `python3 -m unittest discover -s tests -t tests 2>&1 | tail -3`.

## Review Focus

1. **The PO's real store** (110 drawer entries, 18 catalog drafts, his projects on the list) — `--audit` and
   `--match ~/Development/plant-alarm` run without a traceback, and plant-alarm's four needs keep SEN0193, the DFR0954,
   the FireBeetle and the LiPo where P96's Done line put them. Proven in Task G by a read-only run.
2. **A need's `what` in capitals or with a trailing space** ("Soil Moisture ") — matches like "soil-moisture". Test in Task A.
3. **A record in both the project and the catalog** — `--function-set … --project` writes the project's copy, the one
   `--match` reads. Test in Task B.
4. **A hand-written needs file with `"does": null`** — could-not-run naming the file, like `"fly"`. Test in Task D.
5. **An agent retrying a write unchanged** — `--needs-set` or `--function-set` twice with the same file — reads as done
   (`written: true`, no changes), not as a failure. Tests in Task D.

## Rulings this plan makes, for the PO

1. **Owned first stays** (the PO's words in the spec). A candidate whose words match the need is never cut by the 8-row
   cap; owned ones that do not match still come before records nobody owns.
2. **`[other words]`** marks a candidate with the need's verb but other words, in text mode; whether it is similar
   enough stays the agent's call, said to the person (§6.2).
3. **`--function-set` refuses spark's library**, and the shipped `jst-ph-2-power-inlet` gets
   `[{"does": "connect", "what": "power-inlet"}]` in this PR (W16); a test keeps every library record saying what it does,
   so the refusal is never the person's problem.
4. **`written` means carried out** — not refused, not a dry run — the meaning `--drawer-set`, `--skeleton`, `--keep` and
   `--promote` already use.
5. **`--audit` walks the drawer's links into other projects, not every record of every project** (§5.4: "every layer
   and the drawer's links").
6. **"Cost" keeps the PO's word** and says what it is in 1b: what a candidate still owes before it can build. spark
   knows no prices.
7. **Read checks the same rules as write in Task D with two lines**, which refactor F1 then replaces by one table.
   That is a small double edit, accepted to keep the PO's order (functionality before refactoring).

---

## File structure

| file | what changes |
| --- | --- |
| `scripts/needs.py` | A: `_what_matches(need, …)`, count 0, aliases; C: alias filter; D: `read` refuses stray keys and bad verbs, `plan_set` names items; F: `CHECKS`/`faults`, `_candidate`, `_known` deleted |
| `scripts/parts.py` | A: the cap and the text row; B: library refusal, `path`, the audit hint; C: `function_of`, `broken_problems`, `audit`; D: `written`, "nothing to change"; F: `_record_path`, `_write_lines` |
| `scripts/drawer.py` | F: `linkable(project=None)` |
| `commands/idea.md` | B: `--project`, `[other words]`, cost, ids, the Write tool |
| `parts/jst-ph-2-power-inlet.json` | B: a `function` |
| `docs/2026-10-04-store-design.md`, `README.md` | B: M2 and the matcher row amended; the `/spark:idea` row |
| `tests/test_needs.py`, `tests/test_parts.py` | as each task says |
| `scrum/PRODUCT_BACKLOG.md` | Task 0 and G: P96's entry; P97's deferred list |

---

### Task 0: The plan, recorded

- [ ] In `scrum/PRODUCT_BACKLOG.md`, P96's heading: replace `— DONE 2026-10-04` with `— in PR #2: the council's fix round, 2026-10-05`,
  and append to its entry:

  ```
  **Council review, 2026-10-05 (PR #2):** four lenses found 11 Important findings (none Critical); fixed before merge by
  `docs/2026-10-05-store-1b-fixes-plan.md`, functionality first and the refactors last (the PO's order).
  ```
- [ ] `scrum/STORY_MAP.md`, slice 10: `1b P96 (done 2026-10-04 — a goal matched — with **P89**)` becomes
  `1b **P96** (in PR #2, the council's fix round — a goal matched — with **P89**)` — an open item must sit on the map
  (`tests/test_orphans.py`); Task G sets it back to done.
- [ ] `python3 -m unittest discover -s tests -t tests -p 'test_orphans.py'` — expected: `OK`.
- [ ] Commit the plan, the entry and the map: `git add docs/2026-10-05-store-1b-fixes-plan.md scrum/PRODUCT_BACKLOG.md scrum/STORY_MAP.md && git commit -m "P96: the council's fix plan — functionality first, refactors last …"` (trailer).

---

### Task A: The matcher judges by the need's verb and words, and shows it (rank 1)

**Files:** Modify `scripts/needs.py` (`_what_matches`, `candidates`), `scripts/parts.py` (`_op_match`); Test `tests/test_needs.py` (`TheMatcherTest`); Create `tests/mutations/sprint-10-p96-fix-a.json`.

**Interfaces:**
- Produces: `needs._what_matches(need, functions, names) -> bool` — takes the whole need (`does` and `what`), no longer `need["what"]`.
- Produces: `--match` keeps every candidate whose words match past the 8-row cap; the text row shows `what`, and `[other words]` when `what_matches` is false.

- [ ] **Step 1: Failing tests** — in `TheMatcherTest`, after `smell`:

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

    def test_an_alias_matches_and_other_words_do_not(self):
        self.catalog({"id": "z-dist", "name": "VL53L0X", "also_known_as": ["time of flight distance sensor"],
                      "function": [{"does": "sense", "what": "tof"}]})
        found = {c["id"]: c for c in self.alone({"id": "far", "does": "sense", "what": "distance"})["candidates"] if c["id"]}
        self.assertTrue(found["z-dist"]["what_matches"])
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
```

- [ ] **Step 2: Run them** — `python3 -m unittest discover -s tests -t tests -p 'test_needs.py' -k what_matches -k words -k used_up -k cap -k shows_what`.
  Expected: FAIL — `a-combo` matches (True), `soil moisture` does not, `used-up` is offered, `y-probe` is cut, no `[other words]`.
  `test_an_alias_matches_and_other_words_do_not` passes already: it pins the alias rule (§6.2) for the refactors.

- [ ] **Step 3: Implement** — in `scripts/needs.py`, replace `_what_matches`:

```python
def _what_matches(need, functions, names):
    """Every word of the need's `what` in a function with the need's verb, or in the record's name or an alias (§6.2: exact or alias)."""
    wanted = _words(need["what"])
    return bool(wanted) and (any(wanted <= _words(f.get("what")) for f in functions if f.get("does") == need["does"])
                             or wanted <= set().union(*(_words(name) for name in names)))
```

  In `candidates`, both calls pass the need: `_what_matches(need, functions, [record.get("name")] + list(record.get("also_known_as") or []))`
  and `_what_matches(need, functions, [entry.get("label")])`. In the drawer loop, a used-up entry is passed over:

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

  and the candidate row says what it does:

```python
        lines += ["      %-10s %-46s %s" % ("owned %s" % c["owned"] if c["owned"] else "", "%s (%s)" % (c["id"] or c["entry"], c["in"]),
                                        "  ".join(filter(None, [", ".join(c["what"]) + ("" if c["what_matches"] else " [other words]"),
                                                                "free %s" % c["free"] if c["owned"] else "",
                                                                "owes " + ", ".join(c["owes"]) if c["owes"] else ""])))
                  + ("  maybe owned — check the drawer" if c["unsure"] else "") + ("  BROKEN" if c["broken"] else "")
                  for c in need["candidates"]]
```

- [ ] **Step 4: Run** the same command, then the suite. Expected: PASS; suite `OK`.
- [ ] **Step 5: Mutation table** `tests/mutations/sprint-10-p96-fix-a.json`:

```json
[
 {"file": "scripts/needs.py", "name": "what matches through a function of any verb",
  "find": "any(wanted <= _words(f.get(\"what\")) for f in functions if f.get(\"does\") == need[\"does\"])",
  "replace": "any(wanted <= _words(f.get(\"what\")) for f in functions)"},
 {"file": "scripts/needs.py", "name": "what matches only when written exactly alike",
  "find": "any(wanted <= _words(f.get(\"what\")) for f in functions",
  "replace": "any(str(f.get(\"what\")) == need[\"what\"] for f in functions"},
 {"file": "scripts/needs.py", "name": "a used-up entry is offered",
  "find": " or entry.get(\"count\") == 0", "replace": ""},
 {"file": "scripts/parts.py", "name": "the cap cuts a candidate that fits",
  "find": "if rank < 8 or c[\"what_matches\"]", "replace": "if rank < 8"},
 {"file": "scripts/parts.py", "name": "the text hides other words",
  "find": "(\"\" if c[\"what_matches\"] else \" [other words]\")", "replace": "\"\""}
]
```

  Run `python3 tools/mutate.py tests/mutations/sprint-10-p96-fix-a.json` — expected: every mutation caught.
- [ ] **Step 6: Commit** — `tests/test_needs.py scripts/needs.py scripts/parts.py tests/mutations/sprint-10-p96-fix-a.json`, message
  `P96 fix A: the matcher judges by the need's verb and words, never offers a used-up part, never cuts one that fits, and says what each does` (trailer).

---

### Task B: `/spark:idea` works on the project's copy, and spark's library is never written (rank 2)

**Files:** Modify `scripts/parts.py` (`_op_function_set`, `_op_audit`, `OPERATIONS`' `function-set` row), `commands/idea.md`, `parts/jst-ph-2-power-inlet.json`, `docs/2026-10-04-store-design.md:88` and `:272`, `README.md:52`; Test `tests/test_parts.py` (`WhatAPartDoesTest`, `OwedIsNotBrokenTest`), `tests/test_needs.py`; Create `tests/mutations/sprint-10-p96-fix-b.json`.

**Interfaces:**
- Produces: `--function-set` data `{"part", "path", "was", "now", "written"}` (`path` is the file it changes, a string); a refusal (exit 1) for a record in `parts.LIBRARY`.
- Produces: `--audit`'s hint `set it once with --function-set <part> <file> --project <project>: …` when a project is given.

- [ ] **Step 1: Failing tests** — in `tests/test_parts.py` `WhatAPartDoesTest` (add `import store` at the top if it is not there):

```python
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
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        out = io.StringIO()
        with in_store(home):
            said, _ = run_json(["--function-set", "x-soil", str(given), "--dry-run"])
            with contextlib.redirect_stdout(out):
                parts.main(["--function-set", "x-soil", str(given), "--dry-run"])
        self.assertEqual(Path(said["data"]["path"]).resolve(), (home / "catalog" / "x-soil.json").resolve())
        self.assertIn("x-soil.json", out.getvalue())

    def test_function_set_with_the_project_writes_the_copy_match_reads(self):
        home, project = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (project / "parts").mkdir()
        for folder in (home / "catalog", project / "parts"):
            (folder / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        with in_store(home):
            _, code = run_json(["--function-set", "x-soil", str(given), "--project", str(project)])
        self.assertEqual(code, 0)
        self.assertIn("function", json.loads((project / "parts" / "x-soil.json").read_text()))
        self.assertNotIn("function", json.loads((home / "catalog" / "x-soil.json").read_text()))

    def test_every_record_in_spark_s_library_says_what_it_does(self):
        with in_store(Path(tempfile.mkdtemp())):
            library = {part_id: path for part_id, (layer, path) in store.records("parts", parts.LIBRARY).items() if layer == "library"}
        self.assertTrue(library)
        self.assertEqual([part_id for part_id, path in sorted(library.items()) if not parts.function_of(parts._parse(path))], [])
```

  Rewrite `test_function_set_refuses_a_wrong_function_and_a_part_nobody_has` so its wrong function is refused on a catalog
  record, not on the library's `tactile-button` (which Task B refuses for another reason):

```python
    def test_function_set_refuses_a_wrong_function_and_a_part_nobody_has(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
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
        self.assertIn("--function-set <part> <file> --project %s: x-local" % project, out.getvalue())
```

  In `tests/test_needs.py`, a new class before `if __name__`:

```python
class TheIdeaCommandTest(unittest.TestCase):
    """commands/idea.md is followed as written (R4.2): every command it gives that reads or writes a record names the project."""

    def test_every_audit_and_function_set_it_gives_names_the_project(self):
        lines = [line for line in (ROOT / "commands" / "idea.md").read_text().splitlines() if "--audit" in line or "--function-set" in line]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn("--project <project>", line, line)
```

- [ ] **Step 2: Run** — `python3 -m unittest discover -s tests -t tests -p 'test_parts.py' -k function_set -k library -k hint` and
  `… -p 'test_needs.py' -k idea`. Expected: FAIL — the library is not refused, no `path`, `jst-ph-2-power-inlet` says
  nothing, no `--project` in the hint or in `idea.md`. `…_writes_the_copy_match_reads` passes already (Review Focus 3, pinned).

- [ ] **Step 3: Implement** — `scripts/parts.py` `_op_function_set`, after the `path is None` check and before the function check:

```python
    if path.parent.resolve() == LIBRARY.resolve():
        return Answer(problems=[_problem(part_id, "is in spark's own library, which is changed in spark's repository, "
                                                  "not by --function-set")])
```

  and its answer carries the file:

```python
    return Answer({"part": part_id, "path": str(path), "was": was, "now": function, "written": changes and not args.dry_run},
                  ["  %s %s (%s): function %s → %s" % ("would set" if args.dry_run else "set", part_id, path,
                                                        json.dumps(was, ensure_ascii=False), json.dumps(function, ensure_ascii=False))])
```

  (`written` changes meaning in Task D, not here.) `OPERATIONS`' `function-set` row: data keys `("part", "path", "was", "now", "written")`.
  `_op_audit`'s hint:

```python
    lines += ["  says nothing of what it does — set it once with --function-set <part> <file>%s: %s"
              % (" --project %s" % project if project else "", ", ".join(silent))] if silent else []
```

  `parts/jst-ph-2-power-inlet.json`: after `"kind": "connector",` add `"function": [{"does": "connect", "what": "power-inlet"}],`.

  `commands/idea.md` — S step 1, after "Each need has an `id` (…)": *"An `id` stays: there is no removing or renaming a
  need yet, so a wrong one is fixed by hand in `<project>/.spark/needs.json`."* S step 3: "write the needs as a JSON list
  to a file outside any repository **with the Write tool, never a heredoc**, and:". The M section after the `--match`
  block becomes:

  ````
  Owned candidates come first, each with how many are owned and **free** (a part another project holds is not free),
  "maybe owned" when the person was not sure, what it does, and what it **owes** before it can build. `[other words]`
  means the candidate has the need's verb in other words: whether it is similar enough is your call, said to the person.
  Show the person, for each need, the owned option and the simpler one beside it, with what each would cost — in 1b,
  what it still owes before it can build; spark knows no prices. Then mark each need — `have` (owned, with a record),
  `have-unknown` (owned, no record), `know` (a record, not owned) or `gap` (nothing similar) — and **say why in the
  conversation**: the reason is not written to the project. Write the marks with `--needs-set` (`{"id", "mark"}`).

  A record whose kind says nothing (a sensor) is not offered until its function is written once, into the copy
  `--match` reads. The file is a JSON list `[{"does": …, "what": …}]`:

  ```
  ${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --audit --project <project>
  ${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --function-set <part> <file> --project <project> --dry-run
  ```

  then without `--dry-run`. It prints the file it changes: tell the person. spark's own library is not changed from here.
  ````

  `docs/2026-10-04-store-design.md:88` (M2's last cell): `the marks are written into \`needs.json\` through \`parts.py --needs-set\`;
  the reason is said to the person and kept by 1c's history (amended 2026-10-05: a project file holds no reasons, §5.3, §5.8)`.
  `:272`: `the mark and its reason (agent)` → `the mark (agent; its reason is said to the person, §5.8)`.
  `README.md:52`, the `/spark:idea` row's last sentence: `Nothing is researched until a need is a real gap; for now it stops at the marks.`

- [ ] **Step 4: Run** the Step 2 commands, then the suite. Expected: PASS; suite `OK` (a test asserting the old hint text,
  if any, is updated to the new one in this commit).
- [ ] **Step 5: Mutation table** `tests/mutations/sprint-10-p96-fix-b.json`:

```json
[
 {"file": "scripts/parts.py", "name": "the library is written",
  "find": "    if path.parent.resolve() == LIBRARY.resolve():\n", "replace": "    if False:\n"},
 {"file": "scripts/parts.py", "name": "the answer hides the file",
  "find": "{\"part\": part_id, \"path\": str(path),", "replace": "{\"part\": part_id, \"path\": None,"},
 {"file": "scripts/parts.py", "name": "the audit's hint drops the project",
  "find": "(\" --project %s\" % project if project else \"\", \", \".join(silent))", "replace": "(\"\", \", \".join(silent))"}
]
```

  Run it — expected: every mutation caught.
- [ ] **Step 6: Commit** — message `P96 fix B: /spark:idea works on the copy --match reads, --function-set says the file and refuses spark's library; the inlet says what it does; the spec's M2 says reasons are not stored` (trailer).

---

### Task C: One bad record never takes the walk down; the walk follows the drawer into other projects (rank 3)

**Files:** Modify `scripts/parts.py` (`function_of`, `broken_problems`, `audit`), `scripts/needs.py` (`candidates`); Test `tests/test_needs.py`, `tests/test_parts.py` (`OwedIsNotBrokenTest`); Create `tests/mutations/sprint-10-p96-fix-c.json`.

**Interfaces:**
- Produces: `parts.broken_problems(record, path)` never raises on a malformed record: it returns `["does not meet the part record's shape (…)"]`.
- Produces: `parts.audit(project)` also walks each record a drawer entry links to in one of the person's projects (layer = the project's name).

- [ ] **Step 1: Failing tests** — `tests/test_needs.py` `TheMatcherTest` (uses Task A's `catalog` and `alone`):

```python
    def test_a_malformed_record_is_named_broken_never_a_traceback(self):
        soil = [{"does": "sense", "what": "soil-moisture"}]
        self.catalog({"id": "m-kind", "name": "m", "kind": ["sensor", "rtc"]},
                     {"id": "m-alias", "name": "m", "also_known_as": 7, "function": soil},
                     {"id": "m-needs", "name": "m", "needs": ["SIG"], "function": soil},
                     {"id": "m-facts", "name": "m", "facts": [1, 2], "function": soil})
        found = {c["id"]: c for c in self.alone({"id": "wet", "does": "sense", "what": "soil-moisture"})["candidates"] if c["id"]}
        self.assertEqual((found["m-needs"]["broken"], found["m-facts"]["broken"]), (True, True))
        said, code = run(["--audit"])
        self.assertEqual(code, 1)
        self.assertLessEqual({"m-needs", "m-facts"}, {b["id"] for b in said["data"]["broken"]})
        self.assertIn("m-kind", said["data"]["no_function"], "a kind that is a list says nothing — and crashes nothing")
```

  `tests/test_parts.py` `OwedIsNotBrokenTest`:

```python
    def test_audit_walks_a_record_the_drawer_links_to_in_another_project(self):
        home, other = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp()) / "other7"
        (other / "parts").mkdir(parents=True)
        (other / "parts" / "y-soil.json").write_text(json.dumps({"schema": 1, "id": "y-soil", "name": "Soil probe Y", "kind": "sensor",
                                                                  "needs": [], "function": [{"does": "sense", "what": "soil-moisture"}],
                                                                  "facts": {"range": {"value": 3}}}))
        (home / "drawer").mkdir()
        (home / "drawer" / "soil-probe-y.json").write_text(json.dumps({"schema": 1, "label": "soil probe Y", "count": 3, "is": {"part": "y-soil"}}))
        (home / "projects.json").write_text(json.dumps({"other7": str(other)}))
        with in_store(home):
            said, code = run_json(["--audit"])
        self.assertEqual(code, 1)
        self.assertEqual([(b["id"], b["layer"]) for b in said["data"]["broken"]], [("y-soil", "other7")])
```

- [ ] **Step 2: Run** — `… -p 'test_needs.py' -k malformed_record_is_named` and `… -p 'test_parts.py' -k links_to_in_another`.
  Expected: the first ERRORs with a TypeError/AttributeError traceback; the second FAILs (`broken` is `[]`, exit 0).

- [ ] **Step 3: Implement** — `scripts/parts.py`:

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

  `audit` — the links are resolved before the walk, and a linked record in one of the person's projects is walked too:

```python
def audit(project=None):
    """
    Every record in every layer — the catalog included — every drawer link, and each record a link reaches in the person's
    other projects, walked once (§5.4, P89): per layer how many are current, owe facts, or are broken; which say nothing
    of what they do; which entries point at nothing.
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
    walked += linked
    counts, owed, broken, silent = {}, [], [], []
    for kind, found, layer, path in walked:
        # … the loop body as it is today, unchanged …
    return counts, owed, broken, silent, dangling
```

  `scripts/needs.py` `candidates`, after the verb check — aliases are the strings of a list, nothing else:

```python
        aliases = record.get("also_known_as")
        names = [record.get("name")] + ([a for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else [])
```

  and the record's `what_matches` uses `_what_matches(need, functions, names)`.
- [ ] **Step 4: Run** the Step 2 commands, then the suite. Expected: PASS; suite `OK`.
- [ ] **Step 5: Mutation table** `tests/mutations/sprint-10-p96-fix-c.json`:

```json
[
 {"file": "scripts/parts.py", "name": "a kind that is a list is looked up",
  "find": "KIND_FUNCTION.get(kind) if isinstance(kind, str) else None", "replace": "KIND_FUNCTION.get(kind)"},
 {"file": "scripts/parts.py", "name": "a malformed record raises",
  "find": "except (AttributeError, TypeError, KeyError, ValueError) as wrong:", "replace": "except ZeroDivisionError as wrong:"},
 {"file": "scripts/needs.py", "name": "aliases are trusted",
  "find": "([a for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else [])", "replace": "list(aliases or [])"},
 {"file": "scripts/parts.py", "name": "the walk stops at spark's layers", "find": "    walked += linked\n", "replace": "    walked += []\n"}
]
```

  Run it — expected: every mutation caught.
- [ ] **Step 6: Commit** — message `P96 fix C: a malformed record is named broken, never a traceback; --audit walks the records the drawer links to in the person's other projects` (trailer).

---

### Task D: The needs file and the write commands answer the way the drawer's do (rank 4)

**Files:** Modify `scripts/needs.py` (`read`, `_file_fault`, `plan_set`), `scripts/parts.py` (`_op_needs_set`, `_op_function_set`); Test `tests/test_needs.py` (`TheNeedsFileTest`), `tests/test_parts.py` (`WhatAPartDoesTest`); Create `tests/mutations/sprint-10-p96-fix-d.json`.

**Interfaces:**
- Produces: `written` = `not (problems or dry_run)` for `--needs-set` and `--function-set`; a refused item's subject is `"item <n>"` (1-based) or `"the file"`.
- Produces: `needs.read` raises `StoreProblem` for a top-level key other than `schema`/`needs`, a `does` that is not a verb, and a `condition` that is not words.

- [ ] **Step 1: Failing tests** — `tests/test_needs.py` `TheNeedsFileTest`:

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
                self.assertEqual(run(["--needs", str(self.project)])[1], 2)

    def test_a_key_the_needs_file_does_not_hold_is_refused_not_dropped(self):
        (self.project / ".spark").mkdir(parents=True)
        (self.project / ".spark" / "needs.json").write_text(json.dumps({"schema": 1, "needs": [], "goal": "a thirsty plant"}))
        said, code = run(["--needs", str(self.project)])
        self.assertEqual(code, 2)
        self.assertIn("goal", json.dumps(said["unchecked"]))

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
```

  `tests/test_parts.py` `WhatAPartDoesTest`:

```python
    def test_a_retried_function_set_is_carried_out_with_nothing_to_change(self):
        home = Path(tempfile.mkdtemp())
        (home / "catalog").mkdir()
        (home / "catalog" / "x-soil.json").write_text(json.dumps({"schema": 1, "id": "x-soil", "name": "A probe", "kind": "sensor"}))
        given = Path(tempfile.mkdtemp()) / "function.json"
        given.write_text(json.dumps([{"does": "sense", "what": "soil-moisture"}]))
        with in_store(home):
            run_json(["--function-set", "x-soil", str(given)])
            said, code = run_json(["--function-set", "x-soil", str(given)])
        self.assertEqual((code, said["data"]["written"]), (0, True))
```

- [ ] **Step 2: Run** — `… -p 'test_needs.py' -k retried -k refused_on_read -k does_not_hold -k place_and -k nothing_to_change` and
  `… -p 'test_parts.py' -k retried_function_set`. Expected: FAIL — `written` False on a retry, `fly`/`null`/`""` read as
  ok, `goal` accepted, subject `None`, "nothing to change" printed with a refusal.

- [ ] **Step 3: Implement** — `scripts/needs.py` `read`, right after the shape check:

```python
    stray = sorted(set(data) - {"schema", "needs"})
    if stray:
        raise store.StoreProblem("%s holds %s, which a needs file does not — fix it by hand" % (path, ", ".join(stray)))
```

  `_file_fault`, before the `what` line, and its `condition` line made the write's rule:

```python
    if "does" in need and need["does"] not in parts.VERBS:
        return "has a `does` that is not one of %s" % ", ".join(parts.VERBS)
    …
    if need.get("condition") is not None and not (isinstance(need["condition"], str) and need["condition"].strip()):
        return "has a `condition` that is not words"
```

  `plan_set` names what it refuses:

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
```

  `scripts/parts.py` `_op_needs_set`:

```python
    written = not (problems or args.dry_run)
    if written and changes:
        needs.write(target, after)
    lines = ["  %s%s %s: %s" % ("refused, not written: " if problems else "", "would set" if args.dry_run else "set",
                                c["need"], ", ".join("%s → %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in c["now"].items()))
             for c in changes] or ([] if problems else ["  nothing to change"])
```

  `_op_function_set`'s answer: `"written": not args.dry_run` (a refusal has already returned).
- [ ] **Step 4: Run** the Step 2 commands, then the suite. Expected: PASS; suite `OK`.
- [ ] **Step 5: Mutation table** `tests/mutations/sprint-10-p96-fix-d.json`:

```json
[
 {"file": "scripts/parts.py", "name": "needs-set: written means bytes changed",
  "find": "    written = not (problems or args.dry_run)\n    if written and changes:\n        needs.write",
  "replace": "    written = bool(changes) and not (problems or args.dry_run)\n    if written and changes:\n        needs.write"},
 {"file": "scripts/parts.py", "name": "function-set: written means bytes changed",
  "find": "\"written\": not args.dry_run},", "replace": "\"written\": changes and not args.dry_run},"},
 {"file": "scripts/needs.py", "name": "the read trusts a verb that is not one",
  "find": "    if \"does\" in need and need[\"does\"] not in parts.VERBS:\n", "replace": "    if False:\n"},
 {"file": "scripts/needs.py", "name": "the read trusts an empty condition",
  "find": "not (isinstance(need[\"condition\"], str) and need[\"condition\"].strip()):\n        return \"has a",
  "replace": "not isinstance(need[\"condition\"], str):\n        return \"has a"},
 {"file": "scripts/needs.py", "name": "a stray key is dropped", "find": "    if stray:\n", "replace": "    if False:\n"},
 {"file": "scripts/needs.py", "name": "a refused item is named None",
  "find": "parts._problem(\"item %d\" % number,", "replace": "parts._problem(None,"},
 {"file": "scripts/parts.py", "name": "a refusal also says nothing to change",
  "find": "or ([] if problems else [\"  nothing to change\"])", "replace": "or [\"  nothing to change\"]"}
]
```

  Run it — expected: every mutation caught.
- [ ] **Step 6: Commit** — message `P96 fix D: written means carried out; the needs file is read by the write's rules and keeps nothing it does not hold; a refused item is named` (trailer).

---

### Task E: The net before the refactors — tests for decisions no test pins

**Files:** Test `tests/test_needs.py`; Create `tests/mutations/sprint-10-p96-fix-e.json`. No production code changes; each test below
passes on arrival — its mutation row is what proves it bites.

- [ ] **Step 1: Tests** — `TheNeedsFileTest`:

```python
    def test_a_later_item_sees_what_an_earlier_one_set(self):
        said, code = run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"},
                                                                    {"id": "soil", "mark": "have"}])])
        self.assertEqual(code, 0)
        self.assertEqual(self.saved()["needs"], [{"id": "soil", "does": "sense", "what": "soil-moisture", "mark": "have"}])

    def test_a_new_need_with_no_what_is_refused(self):
        self.assertEqual(run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense"}])])[1], 1)
```

  `TheMatcherTest`:

```python
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

  And in `test_a_record_whose_function_is_malformed_is_matched_by_its_kind`, after `self.assertEqual(code, 0)`:

```python
        soil = [c["id"] for c in next(n for n in said["data"]["needs"] if n["need"] == "soil")["candidates"]]
        self.assertNotIn("x-nowhat", soil, "a sensor's kind says nothing, and a function with no `what` is not one")
```

- [ ] **Step 2: Run** `… -p 'test_needs.py'` — expected: PASS.
- [ ] **Step 3: Mutation table** `tests/mutations/sprint-10-p96-fix-e.json`:

```json
[
 {"file": "scripts/needs.py", "name": "many is summed", "find": "    if any(entry.get(\"count\") == \"many\" for entry in live):\n", "replace": "    if False:\n"},
 {"file": "scripts/needs.py", "name": "a later item forgets an earlier one", "find": "        current[need_id] = after\n", "replace": "        pass\n"},
 {"file": "scripts/needs.py", "name": "a new need needs no what",
  "find": "    if not (isinstance(need.get(\"what\"), str) and need[\"what\"].strip()):\n        said.append", "replace": "    if False:\n        said.append"},
 {"file": "scripts/needs.py", "name": "a board owes facts", "find": "\"owes\": [] if kind == \"board\" else parts.owes(record)", "replace": "\"owes\": parts.owes(record)"},
 {"file": "scripts/needs.py", "name": "a record is offered twice", "find": "        if row[:2] not in seen:\n", "replace": "        if True:\n"},
 {"file": "scripts/parts.py", "name": "a malformed function is trusted",
  "find": "    if record.get(\"function\") and not function_problems(record):\n", "replace": "    if record.get(\"function\"):\n"}
]
```

  Run it — expected: every mutation caught (the "many" one by an error, which counts).
- [ ] **Step 4: Commit** — message `P96 fix E: the net before the refactors — six decisions pinned by a test and a mutation each` (trailer).

---

### Task F: The refactors, last — one place for each rule

Four commits, each with the suite green and the anchors it breaks re-pointed in the same commit
(`python3 tools/mutate.py --anchors tests/mutations/*.json` names them; re-run each table it names).

**F1 — one check table for needs** (`scripts/needs.py`). Replace `NEED_FIELDS`, `_file_fault` and `_problems` with:

```python
#: Each field of a need besides its `id` (§5.3): its test, and what is said when a value fails it. A pick is 1c's.
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

  `read`'s loop: `said = ((["\`id\` is not lower-case letters, digits and '-'"] if not store.PLAIN.fullmatch(need["id"]) else []) + (["is there more than once"] if ids.count(need["id"]) > 1 else []) + faults(need, held_only=True))`, raising `"%s: need %r: %s — fix it by hand" % (path, need["id"], said[0])`.
  `plan_set`: drop the inline extra-field block; `after = dict(before or {}, **{key: (drawer.clean(value) if isinstance(value, str) else value) for key, value in item.items()})`; `problems += [parts._problem(need_id, sentence) for sentence in faults(after)]`.
  `match`'s echo: `{key: need.get(key) for key in NEED_FIELDS}`. Re-point the anchors in `sprint-10-p96-3.json`, `sprint-10-p96-final.json`,
  `sprint-10-p96-fix-d.json` and `-fix-e.json` at `faults`/`CHECKS`. Commit `P96 refactor F1: one check table for a need, read and write`.

**F2 — `drawer.linkable(project)`** (`scripts/drawer.py`, `scripts/needs.py`, `scripts/parts.py`). `linkable(project=None)` passes
`project` to `store.records("parts", parts.LIBRARY, project, drafts=True)` and `boards.records(project)`; delete `needs._known`
and call `drawer.linkable(project)` in `match`; `_record_path` becomes
`return next((path for kind, found, _, path in drawer.linkable(project) if (kind, found) == ("part", part_id)), None)`;
`audit` uses `drawer.linkable(project)`. This also lists a project's own boards — pin it first, in `TheMatcherTest`:

```python
    def test_a_project_s_own_board_is_a_candidate(self):
        (self.project / "boards").mkdir(parents=True)
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        (self.project / "boards" / "my-own-board.json").write_text(json.dumps(dict(board, id="my-own-board")))
        found = [c["in"] for c in self.alone({"id": "mcu", "does": "compute", "what": "microcontroller"})["candidates"] if c["id"] == "my-own-board"]
        self.assertEqual(found, ["project"])
```

  RED before F2, GREEN after. Re-point `fix-e`'s "a record is offered twice" at `linkable`'s `unique.setdefault(row[:2], row)` →
  `unique[row[:2]] = row`. Commit `P96 refactor F2: one resolver, drawer.linkable(project) — a project's own boards are candidates`.

**F3 — one candidate builder** (`scripts/needs.py`):

```python
def _candidate(need, functions, names, holding, said):
    """One candidate (§6.2): `said` names it and where it lives; the rest is what its verb's functions say, and its counts."""
    owned, free, unsure = _counts(holding)
    return dict({"id": None, "kind": None, "entry": None, "owes": [], "broken": False, "proof": []}, **said,
                what=sorted({f["what"] for f in functions if f.get("does") == need["does"]}),
                what_matches=_what_matches(need, functions, names), owned=owned, free=free, unsure=unsure)
```

  The record loop appends `_candidate(need, functions, names, holding, {"id": record_id, "kind": kind, "in": where, "label": record.get("name"), "owes": [] if kind == "board" else parts.owes(record), "broken": kind == "part" and bool(parts.broken_problems(record, path))})`;
  the drawer loop appends `_candidate(need, functions, [entry.get("label")], [entry], {"entry": entry_id, "in": "drawer", "label": entry.get("label")})`,
  keeping its conditions (skip, count 0, points at a known record). Commit `P96 refactor F3: one candidate builder`.

**F4 — the write lines, shared** (`scripts/parts.py`). `_change_line` names `change.get("entry") or change.get("need")` and treats
`change["new"] and "entry" in change` as a new drawer entry; a new function

```python
def _write_lines(changes, problems, dry_run, said=()):
    """What a set-only write did or would do, line by line: all of it, or — when anything is refused — none of it."""
    lines = [("  refused, not written: " + _change_line(c, dry_run).strip()) if problems else _change_line(c, dry_run) for c in changes]
    lines += list(said) + ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]
    return lines or ["  nothing to change"]
```

  serves `_drawer_answer` (questions and not-shelved lines as `said`) and `_op_needs_set`. Pin it first, in `TheNeedsFileTest`:

```python
    def test_a_needs_set_line_says_what_was_and_what_will_be(self):
        run(["--needs-set", str(self.project), a_file([{"id": "soil", "does": "sense", "what": "soil-moisture"}])])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            parts.main(["--needs-set", str(self.project), a_file([{"id": "soil", "mark": "have"}]), "--dry-run"])
        self.assertIn('  would set soil: mark null → "have"', out.getvalue())
```

  RED before F4. Re-point `fix-d`'s "nothing to change" row at `_write_lines`' `return lines or ["  nothing to change"]`. Commit
  `P96 refactor F4: one way to say what a write did — a needs line says was → now, as §5.2 asks`.

- [ ] After F4: the suite `OK`; every table under `tests/mutations/sprint-10-p96*` run, every mutation caught.

---

### Task G: Close — measured, checked on the real store, reviewed

- [ ] `python3 tools/mutate.py --anchors tests/mutations/*.json` clean; the suite `OK`; `tools/check_commit.py` prints the size line.
- [ ] **The real store, read only** (Review Focus 1): `scripts/parts.py --audit` and `scripts/parts.py --match ~/Development/plant-alarm`.
  Expected: no traceback; plant-alarm's four needs as P96's Done line says; whatever the walk now finds in his other
  projects is reported to the PO as found, not fixed here.
- [ ] `scrum/PRODUCT_BACKLOG.md`: P96's entry gets the fix round's size line (W15b) and its heading `— DONE <date>` (the last
  fix commit's date, R7), the story map's `**P96**` its `done <date>` back; P97's entry gets the deferred list from the
  top of this plan. `test_orphans.py` `OK`. Commit, push the branch.
- [ ] One fresh reviewer (the most capable model) reads the range from Task 0's commit to HEAD against this plan; Critical and
  Important findings get one fix pass; then the PO merges PR #2.
