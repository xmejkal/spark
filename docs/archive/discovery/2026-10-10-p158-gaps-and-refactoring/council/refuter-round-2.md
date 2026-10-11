# P158 part 1: refuter, round 2, on `proposal.md` (second version)

Written 2026-10-10 by the adversarial refuter, round 2. I did not write the proposal. Spark is read at main `4a18333`.
That is 0.8.1 with PR #125 merged (E `git log -1 4a18333` → `2026-10-10 19:32:07 +0200 Merge pull request #125 from
xmejkal/p179-vendor-cache`). The proposal cites `a8aa34d`. The two differ in 9 files: 493 lines added, 32 removed
(E `git diff --stat a8aa34d 4a18333`).

What I read:
- the proposal's "Changes since round 1" in full, and the sections it names: §1, §2, all of §3 (with every rank's
  `depends on` and `unblocks` line), §4, §5, §6 and §7's dependency list;
- `council/refuter-round-1.md` and `council/completeness-critic.md` in full;
- the catalogue's severity and "observed by" columns;
- the verifiers' "missed root causes" ids.

I opened the code at every line quoted below.

Tags: **E** a pointer (file:line in spark at `4a18333` unless another repository is named; a command and its output; a
card); **H** a claim with its source; **D** a decision (who, when); **—** unknown. Nothing here decides anything for the PO.

**How I ran things.**
- **The store.** The PO's real store was copied with `cp -R` to `<scratch>/p158/refuter-r2/store` and read with
  `python3 -I`. Beyond that I only listed the real store's top folder (`ls -la`). Nothing was written under it.
- **Spark.** No spark command was run against any store. One `python3 -I` imported `scripts/parts.py` to list
  `OPERATIONS`, without the three-assignment prefix. That breaks the letter of the brief, and I say so here. The import
  reads no store: `store.py:40-52` runs `home()` only when called, and `parts.py` reads no home at import (E
  `grep -n -E '^[A-Z_]+ *= *.*store\.(place|home)' scripts/*.py` → `tools.py:47-48` only).
- **Scripts of my own.** Two parsers of the proposal's dependency lines, kept under `<scratch>/p158/refuter-r2/scripts`.
- **`gh`.** Read-only calls only, listed under Searches.
- **Writes.** Nothing was written anywhere but this file and my scratch folder.

## Verdicts

One row per root-cause statement or change in the changed sections, and for each of the top ten. "Line read" quotes
what I opened. For **partly** and **refuted**, the last column gives the sentence to change and why.

### The preamble, §1 and §2 as changed

| target | verdict | line read (verbatim) | the sentence to change, and why |
| --- | --- | --- | --- |
| Preamble (1): the stray header was moved by P179's work, sha256 unchanged | holds | #124 comment 2026-10-10T15:20:33Z: "its sha256 `beb1db11…c055f` was the same before and after the move" | — |
| Preamble (2), CH-62 (rank 7), Q32, §2.2's removed row, §6 split 20, the first slice's "Q32 (merge PR #125)": "still open and unmerged" | **refuted** | `gh pr view 125 --json state,mergedAt,mergedBy` → `"mergedAt":"2026-10-10T17:32:08Z"`, `"login":"xmejkal"`, `"state":"MERGED"`; `gh issue view 124` → `CLOSED 2026-10-10T17:32:09Z`; #124 comment 17:36:24Z "Done — reproduced on main after the merge of #125 (4a18333), 2026-10-10". The proposal was last written at `2026-10-10T19:58:19+0200` (E `stat`), 26 min after the merge. | → "PR #125 was merged by the PO on 2026-10-10T17:32Z (D), and #124 is closed." **Edits that follow:** (1) take CH-62 off the ranks; (2) record Q32 as answered; (3) mark CH-24's and CH-47's dependency on it as met; (4) mark the §2.2 row "done by #125"; (5) re-point every cited line that moved. **Lines that moved:** `agents.md:126` is now `:131`; `how-it-works.md:145` → `:146`, `:155-156` → `:156-157`, `:175` → `:177`; `check_vendor_pins.py:111-112`/`:137-138` are gone. |
| §1 and CH-1: "Set but empty, it quietly reads your real store" | partly | `store.py:48-51` `if os.environ.get("SPARK_HOME"):` … `if os.environ.get("XDG_DATA_HOME"):` / `return Path(os.environ["XDG_DATA_HOME"]) / "spark"` | → "an empty `SPARK_HOME` reads the fallback: `XDG_DATA_HOME/spark` when that is set, else the real store". CH-1's printed fix "unset it to use ~/.local/share/spark" is wrong whenever `XDG_DATA_HOME` is set. It should print the path `home()` would fall back to. |
| §1: the promote rule is documented in three places | holds | `docs/guide/agents.md:131` "**`--promote` copies a project's record into the plugin's own library: never run it unasked.**" (it was `:126` before #125) | Re-point only. |
| §1 and CH-23: `check_spine` reports the errors "only after the island, and then by type only" | partly | `check_spine.py:433-437` `if islands:` / `return stages + [Stage("build", PROBLEMS, …`, then `:438-439` `if errors:` / `kinds = sorted({element["type"] for element in errors})` | → "when there is an island it never reports the build's errors (the island returns first); when there is none, it reports their types only". "Only after" says they come later. When there is an island they never come. |
| §1, R8 and CH-45: "two mappings in two scripts", init's "nothing to do" → 1 named as a fault | partly | `outcomes.py:9-11` "the middle word varied with the script — IMPOSSIBLE, INVALID, MISMATCH, ESCAPED, NOTHING_TO_DO — which is fine as a local name for "ran, and the answer is no""; `init_project.py:43` `from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_NOTHING_TO_DO` | `outcomes.py` names `NOTHING_TO_DO` as one of the sanctioned aliases. So init's mapping is the written design, as `boards.py`'s `EXIT_INVALID` alias is. → "one mapping adds a meaning (`boards.py:537-539`, 'no selection'); init's is a design the PO may change (Q25)". Take init out of §1's implementation faults and out of R8's "go" list. |
| §1: three writers go around the door | holds | `tools.py:47` `PERSONAL = store.place("tools")`; `tools.py:445` `where.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")`; `sim_project.py:162` `shutil.copy2(target / binary.name, binary)`; `git ls-files 'parts/*/chip/*.wasm'` → `parts/l9110s-module/chip/l9110s.chip.wasm`, `parts/vl6180x-breakout/chip/vl6180x.chip.wasm` | — |
| §1 data: "0 groups" of drawer entries sharing a part number | holds | my copy: 103 of 110 entries carry `part_number`; 0 groups by (part number, `from`), 0 by part number alone, 0 by `is` | — |
| §1 data: 91 of 110 entries say nothing of what they do | holds | my copy: 110 drawer files; 91 with neither `is` nor `function`; 12 with `is`, 12 with `function` | — |
| §2.1 R1 and CH-1: "`home()` refuses … on every call"; "the refusal would otherwise be a traceback at import" | partly | `tools.py:59` `class ToolProblem(Exception):`; `store.py:119` `class StoreProblem(Exception):` (unrelated classes); `tools.py:78` `paths = [DEFAULTS, Path(personal) if personal else PERSONAL]`; `init_project.py:411-413` `tools.merged(project)` … `except tools.ToolProblem as broken:`; `tools.py:532` `where = PERSONAL if (args.personal or not project) else …` (outside the `try` that ends `:587` `except ToolProblem`) | CH-1 moves the import-time read to call time. That moves the traceback: it does not remove it. `tools.merged` and `tools.find` read `PERSONAL`, so after CH-1 `home()`'s `StoreProblem` passes through every `except ToolProblem`. It ends in a traceback and exit 1 ("problems") in `init_project.py` and `tools.py`. Those two I traced; for `flash_image.py:76`, `sim_project.py:22-24` and `check_spine.py:100-103`: —. → add "`tools` re-raises a `StoreProblem` from `home()` as a `ToolProblem` naming `SPARK_HOME`, or every `main` that reaches `home()` maps `StoreProblem` to could-not-run". Test: "every script's `main` under an empty `SPARK_HOME` exits 2 with the sentence and no traceback" (§2.4's invariant, here for the store's own error). Without it CH-1 hard-depends on CH-5 (rank 41). |
| §2.1 R2, §2.5 seam 3, CH-4: "a run-time test lists what a suite run wrote under the plugin tree … and fails on anything else" | partly | `tools/check_commit.py:131-133` `suite = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],` / `cwd=str(tree), …`; INDEX.md:294 N25 "A folder inside spark's tree with no marker of its own sends a new board's header into spark's cache"; :295 N26 "A symlinked board file or `boards/` folder writes into spark's tracked cache"; :283 N14 "one owner for "where is spark" and "which project owns this path", and writes that refuse spark's folder unless asked" | The map sees only what the suite writes. R2 also allows "a shipped board's vendor header" as an artefact. Two of the post-#125 writes into spark's tracked cache that P179's own refuter found therefore land on an allowed path: N25 (an unmarked folder in spark's tree) and N26 (a symlinked board). The map cannot name them. P179's council sent N14 and N28 to P158 as a design input: a run-time write helper that refuses spark's folder unless asked. → R2 states why that refusal is not taken, or takes it. See Missing 1. |
| §2.3: holds released through the path a pick already runs | holds | `needs.py:327-328` `used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}` / `used_in.update({name: mine[entry_id]} if mine[entry_id] else {})` | — |

### The rule and the order (§3) as changed

| target | verdict | line read (verbatim) | the sentence to change, and why |
| --- | --- | --- | --- |
| "Silent, defined so it can be checked … a line naming the problem is a sign" | holds as a definition | `proposal.md:426-430` | It is applied inconsistently (the next rows and The order). |
| CH-58 moved "Up into tier 1 … silent by the rule's own test"; its block says "prints —" and "a silent undercount" | **refuted** | `cost.py:274-275` `return "%d line%s of the transcripts could not be read and %s left out of the count" % (`; `parts.py:2154` `… + (["  " + unreadable] if unreadable else [])`; `cost.py:105-106` "Left out and counted, so the cost line never rests on a line it silently dropped." | A line cut at U+2028 becomes two halves that fail `json.loads`. They are counted, and `--tally` prints the count. `--json` carries `cost.unreadable_lines` (`cost.py:245`). By §3's own definition that is a sign. → CH-58 goes to tier 4: "the tally says N lines could not be read; it should count them, and say why when it cannot". Its "prints" becomes that sentence with its cause. The catalogue's K62 grade ("undercounts with no sign") is wrong for the same reason. |
| CH-57 moved "Up into tier 1"; "readable private files and an unlocked write, both with no sign" | partly | `store.py:96` `PRIVATE = ("drawer", "drawer-import", "shelf", "projects", "history")`; `store.py:211` `if private and inside_git(target):`; `ls -la ~/.local/share/spark` → `drwx------ … .`, `drwxr-xr-x … catalog`, `… downloads`, `… sources` | No answer reports anything false. A file's mode is never reported, and "wrote" is true. So the rule's own test does not put CH-57 in tier 1. The home is `0700`, so no other user can reach the `0755` folders on his Mac. The harm that is real: `sources` is not in `PRIVATE`, so `_make_ready` does not refuse it inside a git work tree, and kept vendor documents can land in a repository where one `git add .` publishes them. → tier 3 (spec against code). Its "why" becomes that sentence. |
| "All ordering keys are stated" | partly | CH-49 "key (c) puts the simulation class first"; CH-36 "circuit class, behind CH-49 by key (d)"; CH-20 "layout class, behind CH-36 by key (d) — reasoned only"; CH-11 "key (d) puts it first of the data class among those" | Key (c) names "a circuit, a simulation or the person's data wrong" as one class. The ranks 17–23 use an unstated order inside it: simulation, then circuit, then layout, then data. That is the same defect round 1 found. By the stated keys, (d) puts CH-11 (recorded harm, #101) before CH-36 (an agent's run) and CH-20 ("reasoned only"). |
| "Enabling work is not a key" | partly | CH-1's why: "every later proof — of these changes and of P100's rounds — could otherwise run on the wrong store and look right" | That is the enabling argument the rule forbids. Either drop the clause (CH-1 is first by count anyway) or state enabling work as a key. |
| "Each block carries an unblocks line, and §7 lists the dependencies the counts are read from" | holds, with two findings | my parser over the 71 blocks: the stated count equals the reverse-dependency count for all 71. CH-31 leaves out CH-24 ("only for its simulation stage") and CH-5 leaves out CH-6 ("rather than waiting for CH-5"), both by the blocks' own words. | **(1) Hard and soft weigh the same.** CH-1's 7 is 1 hard (CH-42) and 6 soft, and the soft ones are mostly "the message names the store". Hard only: CH-16 5, CH-22 5, CH-13 4, CH-26/CH-18/CH-21 3, CH-1 1, CH-12 0. **(2) Concepts outside the epic are counted.** Edges into P178 concepts count too, though "the P178 concepts go to #123's discovery, not to this epic" (§3, cards). Counting only in-epic hard edges: CH-9 0, CH-10 0, CH-26 2, CH-21 2. → state both choices, or count hard in-epic edges only. |
| "CH-3 stays above CH-11 by key (a)" (§6 split 18) | partly | CH-25 "depends on CH-3, CH-16; soft CH-1; Q1"; CH-8 "depends on CH-3" (no reason in either block, nor in §7's list); `parts.py:2198-2200` `writes = "writes" in next(effects …)` / `with store.locked() if writes else contextlib.nullcontext():` | A `--release` or `--forget-project` row with `("writes",)` is serialised by today's lock, for one `TMPDIR`, exactly as `--pick` is. Neither edge says what CH-3 adds that the release or CH-8 needs. Without the two edges CH-3 unblocks 0, and split 18's refusal falls back to key (d), which favours CH-11. → give each edge its reason, or apply the swap. |
| "R1's strongest-case top five is answered by the first slice … inside the stage limits" | **refuted** | `scrum/README.md:7` "The limits: 2 per working stage, Ready 5, at most 4 cards in flight across both boards."; `gh project item-list 2` (2026-10-10) → Discovery: P100, P158; Review: P180, P181; `gh project item-list 1` → Ready 3, nothing in a working stage | Four cards are in flight today. The slice adds Design 2 (CH-24, CH-26) and Build 2 (CH-1, CH-13). Even after P158, P180 and P181 leave, P100 + 4 = 5 > 4. → "the first slice is three working-stage cards once P158, P180 and P181 are done, or P100 waits". It cannot be four. |
| "Every root cause now opens with a 'because …' sentence" | holds | my parse of each block's `root cause` field: 71 of 71 begin "because" | — |
| Q35, §6 split 17: "CH-24 … with its Design starting in the first slice" | partly | CH-24 "depends on CH-13, CH-14, CH-21, CH-22, CH-23, CH-62"; CH-22 is rank 28, CH-23 rank 43 | Design can start, but Build waits for rank 43. Two hard prerequisites rank below the change they block: CH-24 (29) ← CH-23 (43), and CH-28 (34) ← CH-37 (49). → Q35 says "Build after CH-23, rank 43", or CH-23 moves up beside CH-22 (The order). |

### The changes, as changed, and the top ten

| target | verdict | line read (verbatim) | the sentence to change, and why |
| --- | --- | --- | --- |
| CH-1 (rank 1) | partly | `store.py:48`; `tools.py:59`, `store.py:119`, `init_project.py:411-413`, `tools.py:532` (above); `docs/guide/agents.md:85-86` "`SPARK_HOME` overrides it. When you check someone else's project, use a scratch `SPARK_HOME`." | **(1) Tracebacks.** Map the store's error (R1 row above), or CH-1 trades a silent wrong store for tracebacks in `init` and `tools`. **(2) Printed fix.** It names `~/.local/share/spark` where `XDG_DATA_HOME` may answer. **(3) The page.** `agents.md:85-86` tells agents to "use a scratch `SPARK_HOME`", and after CH-1 a scratch home that does not exist is refused. Add "make the folder first" to the page. **(4) Its why** uses the enabling argument. **(5) Its count** is 1 hard edge, not 7. |
| CH-13 (rank 2) | partly | `boards/firebeetle2-esp32s3.json` `"chip"` → `esp32s3`; `boards/xiao-esp32-c6.json` → `esp32c6` (my read); STORE-10 (E): wokwi-boards `esp32-s3-devkitc-1` → `"mcu": "esp32-s3"` | Spark spells chips `esp32s3`, while wokwi-boards spells its `mcu` field `esp32-s3`, and its folders drop the `board-` prefix. Compare them directly and both shipped boards are refused, and the bin's `boards-valid` (`Makefile:230-233`) and irrigation's chain fail with them. `test_the_shipped_boards_stand_in_on_their_own_silicon` would catch that. → add "one chip-name map in one place, read by CH-13, CH-24's per-chip table and CH-33; a part type the table lacks answers could-not-look, naming the table". The prints line mixes both spellings. |
| CH-16 (rank 3) | holds (root cause) | `parts.py:2182-2184` `if not answer.lines:` / `for item in list(answer.problems) + list(answer.unchecked):`; `:2024` `said + ["  %s" % note for note in notes] + wrote` (notes in lines, not in `data`) | Mechanism: see that section. |
| CH-26 (rank 4) | partly | `parts.py:899-901` "not its outline (`body_mm`) or its simulation stand-in: a digest of these vouches for a record until one of them changes." / `BUILD_FACTS = ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts")`; `:940` `copy["based_on"] = {"project": project_name, "digest": digest(record)}`; `:910-915` `def digest(record, facts=BUILD_FACTS)` | **What it promises.** Its prints promise "`(host_parts, simulation differ)`" and "with another `pin_order`". **What the data supports.** `based_on.digest` is one hash of six facts, `simulation` not among them. So it cannot see a stand-in change (half of K13's own example), and it cannot say which fact changed. One digest also cannot tell "the source moved" from "the copy was edited here", so "behind" can be the wrong word. → "`based_on.digest` covers the whole record less `SHELF_DROPS` (or the copy keeps the source's fields); `--audit` compares copy and source field by field and prints `differs: <fields>`, and `behind` only when the copy still matches its `based_on` digest". §4's "do not widen `BUILD_FACTS` before something reads a digest": CH-26 is that reader, so state the condition as met or not. |
| CH-18 (rank 5) | holds | `parts.py:1326-1329` `return all(word.lower() in haystack for word in words)`; `needs.py:122-123` `return {word for word in re.split(r"[^a-z0-9]+", str(text or "").lower()) if word}`; `tests/test_parts.py:794-795` `parts.need(["motor-driver"])` still matches when split | Note: it imports a private `needs._words` into `parts.py`, a crossing §2.5 lists (layer 2 importing layer 5), which seam 4 would flag. Put the splitter at layer 0–1. |
| CH-21 (rank 6) | partly | `boards.py:476` `marker = "active" if board_id == active_id(project) else "     "`; `:537-539` `except BoardError as broken:` … `return EXIT_INVALID`; CH-21: "a missing selection where one is needed exits 2 (CH-45's mapping)" | Root cause holds. But CH-21 performs CH-45's `boards.py` half at rank 6, while CH-45 is rank 51 and depends (softly) on CH-68's bin pins. → "CH-21 carries CH-45's `boards.py` mapping and its test `test_no_board_selection_is_could_not_run`", and CH-45 keeps init's question and `mismatch`. |
| CH-62 (rank 7) | **refuted** | see Preamble (2) | Done. Off the list. |
| CH-3 (rank 8) | partly | `store.py:186-187` `named = hashlib.sha256(str(home().resolve()).encode()).hexdigest()[:16]` / `lock_file = Path(tempfile.gettempdir()) / ("spark-%s.lock" % named)`; `parts.py:2198-2200` (the lock is taken for every "writes" op, `--dry-run` included) | Root cause holds. But with `<home>/.lock` "the default home made first if absent", every dry run of a writing operation creates the default home and a file inside the store. That includes an agent's unscoped dry run against the PO's real store, and it contradicts CH-1's "made on first write". → "a dry run takes no lock" (it writes nothing to protect), or say that a dry run touches `.lock`. The CH-8 and CH-25 edges also need reasons (order rows). |
| CH-17 (rank 9) | partly | `needs.py:34` `isinstance(p, dict) and len(p) == 1 and next(iter(p)) in PICKS`; `needs.py:68-70` `extra = sorted(set(need) - set(NEED_FIELDS) - {"id"})` … "not a need's field"; `needs.py:53-54` refuses stray top-level keys | A `fit` "on each pick" is a change to the needs file's schema. Today's reader refuses a pick with two keys, and a need with a field it does not know. Six sites assume one key per pick (`needs.py:225`, `:236`, `:283`, `:297`; `parts.py:2011`; the check at `:34`). → name the shape (a `fits` list beside `pick`, or schema 2) and the reader change. Add a test that a file holding a fit is read, and one that a file from before it still is. Size S–M is low for that. |
| CH-19 (rank 10) | holds | my copy: 91 of 110 (above); `parts.py:1955` cut at eight (R1) | — |
| CH-6 (rank 11) | partly | `design.py:96-97` `if not path.is_file():` / `raise DesignError("no requirements at %s" % path)`; `needs.py:609` `held = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {}`; `design.py:99` `wanted = json.loads(path.read_text())` | The first `--requirements` has no file, and `design.read` refuses a missing file. → "reads through `design.read` when the file exists". `design.read` decodes with the locale, not UTF-8. The suite tests a C locale with coercion off (`tests/test_drawer.py:652`), where a non-ASCII requirements file would read as "is not JSON". Fix that in the same change, or wait for CH-5's one reader. |
| CH-14 (rank 13) | partly | CH-14 prints "start it with <the board skeleton command>` (named once CH-24 lands; until then "copy the closest board with the board copy verb (CH-63) …")" | When CH-14 lands at rank 13, neither CH-24 (29) nor CH-63 (33) exists. The fix it prints would name a verb that does not exist. → until either lands, it names today's route: `boards/README.md` and `how-it-works.md`'s steps, with CH-13's "set its chip and stand-in". |
| CH-9, CH-10, CH-12 | holds | `drawer.py:90-92` (R1); `store.py:247-250` `if where.resolve() == folder`; `boards.py:344-349` `pads \|= set(labels)` | Rank: see The order (CH-9 and CH-10 rest on a P178-concept edge). |
| CH-2 (rank 16) | partly | `tools/mutate.py:201-202` `caught_near = bool(near) and not suite_is_green(root, tests, only=near, failfast=True)` / `green = False if caught_near else suite_is_green(root, tests, failfast=True)`; `:59-60` "Which run caught a mutation (P98): the tests near the mutated file, or the whole suite." / `NEAR, FULL = "near", "full"` | **The ≈12.2 h.** It assumes every mutant runs the whole suite. The tool runs the near tests first and stops at the first failure, so ≈12.2 h is an upper bound, reached only by escapes. Say "at most". **`--near <file>`.** It reuses "near", which already names P98's near tests and prints as `caught near` (`:226`). Call it `--rows-in <file>`. **Its one dependent.** CH-67's held check exists only if Q22 is "yes". |
| CH-4 (rank 17) | partly | as R2 above | Promote half holds. The write map cannot see N25/N26, and it is a test-time guard where P179 asked P158 for a run-time one. |
| CH-49, CH-36, CH-20, CH-11, CH-15, CH-54, CH-55, CH-64 | holds | CH-36: XIAO `physical` keys `footprint_export, footprint_module, height_mm, width_mm, wokwi_size_px` (my read); `tests/test_boards.py:378-382` accepts `(0, 1)`. CH-20: `parts.py:658-660`. CH-15: `parts.py:1260` `if payload is not None:`, `:1203` `for path in sorted(kept.glob("*/*"))`. CH-64: `docs/observations/INDEX.md:210` (E16b, "verified"). | CH-36's scope test is the only guard of the bin's Gerber recipe, because P41's test accepts exit 1. CH-11's place: The order. |
| CH-22 (rank 28) | holds | `grep -rln 'flush_edge\|corner_radius_mm' scripts tools/circuit-to-wokwi/lib` → nothing; `thickness_mm`/`pad_mm` appear only as `fab.process("…_thickness_mm")`/`min_via_pad_mm` keys | Rank: see The order. |
| CH-23 (rank 43) | holds | `check_spine.py:438-440` as above | Rank: see The order. |
| CH-24 (rank 29) | partly | its `depends on` line (above) | Its #125 edge is met. Its Build waits behind rank 43 (Q35 row). |
| CH-32 (rank 38) | partly | `boards/firebeetle2-esp32s3.json:115` `"wokwi_is_stand_in": true,`; the XIAO has no such key (my read: `None`); the bin's `Makefile:230-233` `boards-valid:` … `boards.py --validate` | "makes it required (true or false)" refuses the library XIAO, which the bin's `make check` validates. Every person's own board file without the flag would also be refused after an update. → "the XIAO gains `false` in the same commit (a test that the shipped boards pass); a person's file without it is refused with the sentence, said in the release note". Alternatively, absent reads as false, with a note. |
| CH-45 (rank 51) | partly | `boards.py:495` `what.add_argument("--id", action="store_true", help="the active board's id")`; CH-45 prints "select one, or pass --id" | `--id` is a mode that prints the active id. It selects nothing. The printed fix sends a person or an agent to an option that does not exist. → "select one: write `boards/active.json` as `{"schema": 1, "board": "<id>"}`". `boards.py` has no option that selects a board for one call: its modes are one mutually exclusive group (`boards.py:493`), and only `--for-fab` and `--project` sit beside them (`:504`, `:506`). Plus the init row above. |
| CH-5, CH-7, CH-8, CH-37, CH-39, CH-41, CH-44, CH-48, CH-66 | holds | `store.py:293-294` "line %d is not a history event — fix it by hand"; `parts.py:2081-2083` "wrote" with the path; `init_project.py:485` "build, then re-run with --force"; `check_physics.py:305-309`; `grep -rn '\.local/share' agents commands skills \| wc -l` → 6; `needs.py:511` and `parts.py:1920` the two spellings of the stop | — |
| CH-29, CH-63, CH-65, CH-67, CH-69, CH-70, CH-71 | not re-opened by me | — | Round 1's verdicts, or their absence, are the only reading. I make no claim. |

## The order

**1. The list is not topologically consistent.** Four hard prerequisites rank below the change they block:

| change | rank | blocked by | its rank |
| --- | --- | --- | --- |
| CH-24 | 29 | CH-23 | 43 |
| CH-28 | 34 | CH-37 | 49 |
| CH-54 | 24 | soft CH-22 | 28 |
| CH-55 | 25 | soft CH-7 | 42 |

Four tier-1 changes lean softly on CH-5 at rank 41: CH-26 (4), CH-21 (6), CH-9 (14) and CH-15 (22). By my CH-1 row,
CH-1 needs CH-5's mapping for the store's error in hard form. A priority list a team pulls from the top must never put a
change above its own hard prerequisite.
→ Rule: "after the keys, a change moves up to sit right after its last hard prerequisite, or its prerequisite moves up
to it".

**2. Changes in the wrong tier, by §3's own definition:**
- **CH-58 → tier 4.** It is signed: `cost.py:274-275` and `parts.py:2154` print the unreadable count.
- **CH-57 → tier 3.** No answer reports anything false. Its real harm is `sources` outside the git refusal.
- **CH-62 → off the list.** Merged 2026-10-10T17:32Z.
- **CH-25's listing half → arguably tier 1, by the same reasoning that lifted CH-49.** `--drawer` prints "1 owned" for
  the S3 with no word that the bin holds it (`parts.py:1772-1775` prints label, count, `is`, unsure/skip; `used_in` is
  not printed). That is `ok` over an incomplete answer. The "incomplete" clause makes the tier-1 boundary depend on which
  omissions one counts. → either narrow "incomplete" to "omits what the answer claims to cover", or lift CH-25's
  `held by` column into tier 1. It is a column, S.

**3. Pairs that should swap.**
- **CH-11 ↔ CH-20, and CH-11 above CH-36.** Key (d): CH-11's harm is recorded (#101; twelve scratch projects in his
  `projects.json`). CH-20 is "reasoned only" (catalogue K54, K63: "nobody — reasoned only"). CH-36 was met by an agent.
  The sub-order simulation > circuit > layout > data is not a stated key.
- **CH-9 and CH-10 → below CH-11, CH-15 and CH-4.** Their only dependent is CH-29, a P178 concept the proposal sends
  out of this epic. Counted in-epic, they unblock 0. CH-9's block says "Its reach today is nil". K9 and K4's spelling
  half are "nobody — reasoned only".
- **CH-3 ↔ CH-11.** This holds unless the CH-25 and CH-8 edges get their reasons (Verdicts).
- **CH-23 up to sit with CH-22.** CH-23 is S–M, a hard prerequisite of D8's first fix (CH-24), and the proposal's
  own G3 row says README's Build "works" is false until it lands.
- **CH-5's mapping for `StoreProblem` with CH-1 at rank 1** (Verdicts, CH-1). The rest of CH-5 can stay in tier 2.

**4. Key (e) is out-weighed by tier placement.** D8 (2026-10-09): *"we want to start by the boards"*. On 2026-10-10:
*"the boards for sure"*. Yet the board contract (CH-22) sits at rank 28. It is M, it unblocks 5 hard (the most hard
edges in the list, tied with CH-16), and it is removal-first (key (b)). It sits behind 27 tier-1 changes. Eleven of
those unblock nothing. Four have nil or near-nil reach on his machine today: CH-9 ("reach today is nil"), CH-57 ("no
data is lost on his Mac today"), CH-58 (signed) and CH-55 ("misleads only a reader of `boards.py --id`"). The tier
rule is the brief's. The brief's (a) "unblocks the most" is applied only inside tiers, so a prerequisite of the PO's
named first fix waits behind changes nobody has met.

**The strongest case for a different top five.**

The inputs:
- The only person blocked today is the PO, at round A, by K3 + K29 + K36 together (RISKS-1, E).
- His order is boards first (D8).
- #125 is done.
- His design criteria (D 2026-10-10) are testability, diagnosability, and removal before addition.

The top five:
1. **CH-1 with the store's error mapped in every `main`** (S–M). Every answer names its store, and a wrong store is
   refused with a sentence, not a traceback. Recorded harm (#101; P100's refuter's dry run).
2. **CH-13** (S + S). Wrong silicon refused, with one chip-name map. It hard-unblocks 4 (CH-24, CH-30, CH-31, CH-34).
3. **CH-22** (M). The board contract written where it is enforced, and unread keys removed. It hard-unblocks 5
   (CH-24, CH-28, CH-31, CH-33, CH-66). Removal first. Boards first.
4. **CH-16** (S–M). It hard-unblocks 5. The agent's JSON stops dropping what the text says.
5. **CH-14 + CH-21 + CH-23, as one "boards are found, refused as parts, and build with their aliases" pull request**
   (S, S–M, S–M). These are the last hard prerequisites of CH-24, so D8's first fix can enter Build in the first month,
   not after rank 43.

Q1, Q5 and Q6 go to the PO in week one, as the proposal says. CH-25 follows Q1, and CH-18 (S; I1 is the most frequent
recorded wrong turn) is next.

Against it: it delays CH-26 (silent drift) and CH-18. If the PO weighs I1 above the agent's JSON, CH-18 swaps with
CH-16. It also moves CH-3 later; CH-3's harm is reasoned only (K5, "nobody — reasoned only").

## Mechanism or symptom

- **CH-1.** Mechanism for the home. As written it moves the failure from silent to traceback in `init` and `tools`
  (Verdicts). The named tests do not catch that. `test_changing_spark_home_after_import_moves_the_tools_list` runs no
  `main`. Add a test per script `main` under an empty `SPARK_HOME`, expecting exit 2. **Simpler:** the call-time
  `PERSONAL()`/`DOWNLOADS()` that CH-1 adds turns `StoreProblem` into `ToolProblem`. That is one `try` in one place,
  and every existing `except ToolProblem` then says it. **The bin, irrigation, plant-alarm:** none sets
  `SPARK_HOME` (E `grep -rIl SPARK_HOME` in all three, excluding `node_modules`, `.git`, `dist` → nothing). For kind
  `boards`, `store.layers` adds no store row (`store.py:78`), and `boards.validate`'s `parts` calls
  (`document_problems`, `SELECTOR_SAFE`) read no home. Nothing breaks, E.
- **CH-2.** Mechanism for the scoring. The named tests would catch a non-importing mutant. The size of the harm is two
  rows ever (K53, R1). The machine-time figure overstates.
- **CH-3.** Mechanism (the lock follows the data). **Regression risk:** a dry run touching the store (Verdicts).
  `test_two_processes_with_two_tmpdirs_cannot_hold_one_store_at_once` would not catch it. Add a test that a dry run
  leaves the home's listing unchanged.
- **CH-4 / R2.** Test-time symptom guard. It sees only the suite's writes, and its allow-list hides N25/N26. The
  mechanism P179's council named: one owner for "where is spark", and a write helper that refuses spark's folder
  unless asked. That would refuse a real run's write, not only a test's. **Simpler, and in-process:**
  `store._make_ready` refuses a target under `PLUGIN`. That catches every door write. The three non-door writers
  (`promote`'s `copy2`, `check_vendor_pins`' `write_text`, `sim_project`'s `copy2`) go through one helper with an
  explicit "spark's own artefact" flag.
- **CH-6.** Mechanism (one loader, one name). As written it breaks the first `--requirements` unless the missing-file
  case stays `{}`. The suite's existing first-run tests would catch it, so it is a spec gap, not a hidden break.
- **CH-13.** Mechanism for the record, symptom guard for the image (stated). **Regression:** the chip spelling. Its
  named test catches it.
- **CH-16. Symptom.** Root cause as stated: two printers that each leave something out. The change adds four fields
  and nine named tests. A fifth note appended to `lines` tomorrow is dropped again, and no test sees it. **Mechanism,
  and as small:** `Answer` gains one field per class of line (`notes`, `conflicts`), which both printers read. Then a
  note cannot reach the text without reaching the envelope, by construction. The guard is one test per field: text and
  envelope are both rendered from it. That replaces nine tests of today's omissions with two of the construction.
- **CH-17.** Mechanism (a recorded fit). Its schema change is unnamed, and the reader refuses it today (Verdicts). As
  written, the first pick that records a fit makes `needs.read` refuse the file on the next command:
  "`pick` is a list of {"part"|"board"|"entry": id}". Plant-alarm's `needs.json` is read by every `--match`. Its
  old picks read fine. Its next pick would write a file the current reader refuses.
- **CH-18.** Mechanism for the quoting, symptom-free. `test_need_keeps_prefix_finds` catches R1's regression.
- **CH-26.** Mechanism (a reader of digests), but the digest is the wrong one for the drift it names. A test with a
  changed `simulation` stand-in would pass `test_audit_names_a_copy_behind_its_source` only if the fixture changes a
  `BUILD_FACTS` field. Name the fixture's field `simulation` and the test fails as specified.
- **CH-32.** It breaks the bin's `boards-valid` through the library XIAO unless the XIAO gains the flag (Verdicts).
  The "bin" line says only "the library S3 gains the sentence".
- **CH-36.** Mechanism. P41's contract test cannot see the bin's recipe turn red (it accepts 1). The new scope test is
  the only guard, as the block says.
- **CH-45.** Its message names a non-existent option, so it fails the PO's diagnosability criterion (Verdicts).
- **CH-58.** Already signed. The change turns a signed undercount into a count. Its message should still say *why* a
  line is unreadable, which today it does not ("could not be read").
- **For the bin, irrigation and plant-alarm:**
  - CH-13 without a chip map turns the bin's `boards-valid` and irrigation's chain red. Both read the library S3
    (irrigation's `boards/` holds only `active.json`, E `ls`).
  - CH-32 turns the bin's `boards-valid` red through the XIAO.
  - CH-17 can make plant-alarm's `needs.json` unreadable after its first new pick.
  - CH-3 makes every unscoped dry run touch the real store.
  - No other changed block breaks the three that I could trace. The bin's `make check` against any change is still
    run by nobody (critic, Modalities).

## Missing

1. **P179's council rows addressed to P158.** None is cited: `grep -c` of N12, N13, N14, N24, N25, N26, N27 and N28 in
   the proposal → 0 each. `docs/observations/2026-10-10-p179-council.md` appears only as a file name in #125's list
   (`proposal.md:2327`). They are on main (E `docs/observations/INDEX.md:281-297`):
   - N13 (U-4, TL-7): an agent reads the header file in two shapes, `source` offline and `wrote` live, and no field
     says whose copy answered. "raised for the one envelope (P43's shape, P158's plan)". CH-16 and R6 should carry it.
   - N14 and N28 (PA-6, TL-6, Q3, Q5): "one owner for 'where is spark' and 'which project owns this path', and writes
     that refuse spark's folder unless asked". "an input to P158's design". The proposal folds TECH-LEAD-4's seven
     spellings into §2.3 "since no K row needs it", but this row exists.
   - N24–N27: a stray `.spark/` owns a board file; **an unmarked folder inside spark's tree, and a symlinked board,
     write into spark's tracked cache**; two spark copies. N25 and N26 are K14's silent-plugin-write shape after #125,
     so tier 1 by the rule. Each needs a rank or a §4 line.
2. **Cards created at 17:37–17:42Z on 2026-10-10 that overlap ranked changes.** 0 mentions each. Existing-first:
   reuse or merge them.
   - **P181 (#127, in Review)** edits `how-it-works.md` and `agents.md`. CH-22, CH-24, CH-47 and CH-48 cite and change
     those pages. Its F4 is a fact CH-16 and CH-48 need: "agents.md's JSON row says every entry has `source`; a
     could-not-run entry has only `board`, `status` and `reason`".
   - **P182 (#128, in Idea)** rewrites README's first screen. CH-23's Build row, CH-42, CH-43 and CH-61 change the
     same file.
3. **The PO's documentation brief of 2026-10-10** (D, quoted in #128's *Needed by*: "before every PR, I want you to
   have a documentation expert check the documentation and make sure its up to date, well understandable, well
   readable, exciting for humans…"). It applies to every card of this epic. The "Done, for every change" rule names a
   glossary entry, the K-id trail and the bin line, not this.
4. **No home for chip names.** CH-13, CH-24's per-chip table and CH-33's `board.json` `mcu` each need `esp32s3` ↔
   `esp32-s3` ↔ `board-esp32-s3-devkitc-1`. No change owns the map. That is R5's "one table per fact" shape, unranked.
5. **The needs-file schema change under CH-17** (Verdicts), and its version rule: what an older spark does with a
   newer `needs.json`.
6. **The store's error through `tools`** (Verdicts, CH-1). No change covers it before CH-5 at rank 41.
7. **A file at the store root that no place names:** `b12-kept-from-the-bin.jsonl`, 6,575 bytes, mode `0644`,
   2026-10-04 (E `ls -la ~/.local/share/spark`). `PLACES` names no such file (`store.py:61-63`), no script writes it
   (`grep -rn kept-from-the-bin scripts` → nothing), and nothing in the P158 folder mentions it (`grep -c` → 0 in
   every file). It bears on CH-57 (privacy) and CH-70/CH-29 (what a sync or a shared layer carries). Low.
8. **The verifiers' missed causes.** BR-M2, BR-M8, BR-M9, DR-M3, DR-M7 and SL-M5 are cited 0 times by id. Each is
   covered in substance:
   - BR-M2 → CH-30's amended sentences;
   - BR-M8 → CH-12's phantom port;
   - BR-M9 → CH-56's second case at `test_json_contracts.py:142`;
   - DR-M3 → §2.6's two classes;
   - DR-M7 → CH-41;
   - SL-M5 → §4's severity row.

   Nothing missed.

## Numbers

- **"1,268 mutations × the suite's 34.6 s ≈ 12.2 h" (CH-2).**
  - Population: at `a8aa34d`. At `4a18333` the tables hold 1,281 rows in 116 files: 1,241 `.py`, 24 `.md`, 13
    `.json`, 2 `.ts`, 1 `.js` (E my count).
  - The 34.6 s is a full run of 1,699 tests on an earlier day. #124 records 1,713 tests on #125's branch.
  - The product is an upper bound under an assumption `mutate.py:201-202` contradicts (near tests first, `failfast`).
    State "at most".
- **"The unblocks counts, top to bottom: 7, 5, 5, 4, 4, 3, then four with 2, six with 1, eleven with 0".** The
  arithmetic holds (my parse). The composition is unstated: hard + soft, and edges into P178 concepts outside the
  epic. Hard only: CH-1 1, CH-16 5, CH-13 4, CH-26/CH-18/CH-21 3.
- **"17 in Done on the spark board since 2026-10-05".** 18 at 2026-10-10 evening (E `gh project item-list 2`: Done 18).
  The 18th is P179.
- **"Nine files, 493 lines added, 32 removed" (CH-62).** It holds (E `git diff --stat a8aa34d 4a18333`). It describes
  a merged change.
- **"42 direct store writes" (CH-3).** It holds for the named pattern at `4a18333`: `tests/test_store.py` 41,
  `tests/test_drawer.py` 1 (E my `grep -c -E`).
- **"12" writing operations (CH-3).** It holds (E `OPERATIONS` rows with `writes`: skeleton, fetch, keep, promote,
  drawer-set, drawer-import, function-set, fact-set, needs-set, pick, requirements, step).
- **CH-1's prints "drawer 110 entries, shelf 5, catalog 18, projects 5".** It holds on my copy (E). It is the PO's
  data as of the copy, 2026-10-10. Printed by a test, it must come from a fixture.
- **"Tests that point SPARK_HOME at a folder they expect the first write to make each gain a mkdir (how many: —)".**
  Answerable without guessing: run the suite once on a branch with the refusal in `home()`. Left —.
- **"60 s", "2 s" (CH-3).** H, a proposal. Fine as tagged.
- **"how many cards close in a week is —".** Fine. But the slice's "inside the limits" rests on a stage count that is
  not read. It is 4 in flight now (Order).
- **The "four of his six ESP SKUs" counts (CH-24),** "398 transcript files … 25 lines" (CH-58), "137 files,
  319,145 bytes" (§2.3): each carries its source and date. No change needed.

## Searches

No web searches. Read-only `gh`, 2026-10-10:
- `gh pr view 125 --json state,mergedAt,mergedBy,title`;
- `gh issue view 124 --json state,closedAt` and its comments;
- `gh issue list --state all --limit 12`;
- `gh pr list --state all --limit 6`;
- `gh issue view 127` and `gh issue view 128` (bodies);
- `gh project item-list 1` and `gh project item-list 2`.

Local, read-only:
- spark at `4a18333` and `git diff a8aa34d 4a18333`;
- `docs/observations/2026-10-10-p179-council.md` and `INDEX.md`;
- the bin's `Makefile`;
- irrigation's `boards/` and `.spark/` listings;
- plant-alarm's listing;
- the store copy at `<scratch>/p158/refuter-r2/store`;
- `ls -la` of the real store's top folder.
