# P158 part 2 — plan critic: are the cards well defined, separated and ordered, and do they carry validated learning?

**What this is.** The critic of `docs/2026-10-10-p158-plan.md` ("the plan") against its one question, the PO's words:
the final issues *"well defined, separated and ordered in the best way"*, with *"technical design and validated
learning"* (D the PO 2026-10-10, quoted at plan:17-22). Each card is checked eight ways, each iteration three ways, and
an order is proposed where it differs. Nothing here is decided: every fix is a proposal, and *What the PO must decide*
(end of *Proposed order*) lists his calls. Written on the night of 2026-10-10 to 11 (the brief's date is 2026-10-10;
the machine's clock read 2026-10-11), against spark 0.8.1 at main `5acbe42` (E `git log -1` → `5acbe42 2026-10-10
22:26:37 +0200 Merge pull request #129`; E `.claude-plugin/plugin.json:3` → `"version": "0.8.1"`).

**Read.** The plan whole (2,288 lines) and the design `docs/2026-10-10-p158-architecture-design.md` whole (2,426
lines). Part 1 (`proposal.md`): the header (`:1-107`), §3's rule (`:511-590`), every CH block's *kind / size / card* and
*depends on* lines (extracted by a script into `<scratch>/ch-extract.txt`, then read), CH-18, CH-26, CH-27 and CH-63
whole, *How the list becomes cards*, §4 and §5 (`:2509-2655`). `design/refuter-round-1.md` §1.1, §3–§7, read so that
this file builds on it: where the refuter found a defect first, a row cites "refuter §x" and adds only what is new.
spark at `5acbe42`: `scripts/boards.py:60-70`; `scripts/needs.py:118-130`; `scripts/drawer.py:54`;
`scripts/parts.py:899-903`; `scripts/outcomes.py:19-43`; `scripts/check_spine.py:94-135`, `:366-380`, `:582-583`;
`scripts/sim_project.py:167-176`; `scripts/flash_image.py:81-85`; `tests/test_check_bom.py:138-146`;
`tests/test_check_physics.py:382-397`; `tests/test_check_vendor_pins.py:158-191`; `tests/test_boards.py:310-318`;
`scrum/README.md:1-30`, `:90-125`, `:236-250`; `scrum/WORKING_AGREEMENTS.md` W14, W16, W19, W20;
`.github/ISSUE_TEMPLATE/item.yml`. The siblings, read only: the bin's `Makefile` spark lines and the keys of its
`.spark/rules.json`; irrigation's `.spark/rules.json` keys, `sim/` listing and `sim/scenarios/wet-and-dry.scenario.yaml:1-35`;
plant-alarm's listing; the `parts/` of rc-car and spark-quickstart and two of their records. Read-only `gh` on
2026-10-11: `issue list --state open --limit 200`; `issue view` #13, #20, #23, #48, #69, #71, #97.

**Ran.** No spark command against the PO's store; nothing written but this file and `<scratch>`.
- `cp -R ~/.local/share/spark <scratch>/store`, then read-only listings and `python3` reads of the copy.
- One spark command, on copies only: in `<scratch>/plant-alarm` (a `cp -R` of `~/Development/plant-alarm`),
  `SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp python3 ~/Development/spark/scripts/check_spine.py requirements.json`
  → `[ok  ] board  Seeed XIAO ESP32-C6` · `[ok  ] schematic  11 trace(s) written` · `[!!  ] schematic-notes  note: DFRobot
  DFR0954 MAX98357A I2S amplifier.SPK_N drives net.SPEAKER_N and nothing on this board receives it …` (and the same for
  `SPK_P`) · `[????] footprint  no footprint could be generated for xiao-esp32-c6` · `the chain is broken` · `exit=1`.
  This reproduces the refuter's R1 (W9: a claim is a hypothesis until reproduced).
- Read-only `python3` passes: the kinds of the 77 cards in the plan (→ above the cut: 24 bugs, 21 stories, 8 chores);
  a field compare of `~/Development/rc-car/parts/tactile-button.json` and `~/Development/spark-quickstart/parts/led-red-5mm.json`
  with the library's records; the keys of the three projects' rules files.
- Greps, each cited in its row.

**Tags.** **E** a pointer or a command and its output · **H** a claim, with its source · **D** a decision, who and
when · **—** unknown. `plan:N`, `design:N` and `proposal:N` are lines of the three documents at `5acbe42`. Sizes are
estimates on part 1's scale (S under an hour, M a day, L more), labelled.

**The eight checks** (columns of *Per card*): **T** the title is the fault, then the change · **1** one concern ·
**B** buildable alone once its hard edges are Done, and its edges are the true ones · **V** *Value proven by* names a
measurement and a pass line that can fail · **M** it names the test it adds and the failure sentence it prints · **S**
its size is honest against part 1 and the design's §12.2 · **R** it reuses an existing card where one exists · **P** it
sits in the right iteration and position (dependency, then part 1's priority rule, then the smallest unblocker).

## The ten defects that move the plan most

Ranked by what goes wrong if they stay. Each points at its row.

1. **Questions asked after the cards they gate** — Q42 and Q43 (the keys that order the fix lane from I0) in batch 3;
   Q36 (C3, in the first slice) in batch 2; Q8 (C42's Design in the first slice, C45 in I2) in batch 4; DP13 (scope) in
   batch 6; DP9 (the item shape C5 asserts in I0) in batch 2. *Proposed order*, A.
2. **C39's pass line cannot be met at its Done**: "13 subTests green" (plan:1344), while three of the thirteen bases are
   produced by later cards (C41/C43, C51); and C39 and C41 both claim the `unserved` conversion. C39 row.
3. **C36 removes plant-alarm's only `problems`** (`check_spine.py:374-375`): after it, plant-alarm answers
   could-not-run, exit 2, unless C36 keeps "a net with one member" a problem — and its card says "plant-alarm's stop
   unchanged" (plan:1289). Reproduced. C36 row.
4. **C3's measurement cannot tell C3's value from the choice of mutant**: today's tests compare `main()`'s return with
   the module's own constant (`tests/test_check_bom.py:138-145`), so the mutants must be written before the run and C3
   must assert the literal 0/1/2 the bin's `make` reads. C3 row.
5. **21 stories above the cut, and Design scheduled for one** (C42). The plan does not say whether the accepted
   architecture design is each story's approved spec (`scrum/README.md:110-111`: a story with no approved spec goes
   through Design), its forecast counts no Design council, and the kinds send the layer's core (C23, C31 as bugs; C30 as
   a chore) straight to Ready. *Defects common to many cards*, G1.
6. **The commitment boundary contradicts the schedule**: R10 commits "Ready through I2" (plan:180), while the first slice
   puts C42 (I3) in Design (plan:244) and R7 runs C30 (I3) beside I2. I2 row.
7. **C37 (rank 15, tier 1) waits for C30 (I3) with no edge in part 1**; placed first as F→A, it lands about twenty
   positions earlier and removes the window in which C30 turns the bin's Gerber recipe red (refuter R3). C37 row; move M7.
8. **Value lines dropped or contradicted on the way to filing**: C26 closes #69 while #69's second half "stays on it"
   (plan:1028-1029); C24 cites Q6 (a) and implements Q6 (b) (plan:988, :993); C23 leaves `assign_pins`' `assumptions`
   empty from I1 to I4 while `data.unverified` holds the facts. Their rows.
9. **Two hypotheses cannot fail as measured**: H1 is about an agent, and I1 runs no agent (plan:349-361; the first agent
   runs in C53, I5); Hf0's pass line excuses any diff a card names, while the diffs I0 makes can be listed now. I0, I1
   rows.
10. **Edges missing or spurious**: C9 needs C8's sentence (plan:685); C68's test is C58's check; C65 → C1 and C66 → C39
    have no reason; C13 must read YAML with no reader in the standard library. Their rows.

## Per card

### Defects common to many cards

- **G1 · kinds and the Design stage.** `scrum/README.md:110-111`: a story the PO chose with no approved spec enters
  Design before Ready (its own council, the PO's yes); chores and bugs enter Ready directly. Above the cut the plan has
  21 stories (C6, C13, C14, C21, C22, C24, C27, C28, C34, C36, C39, C40, C41, C42, C43, C45, C46, C48, C50, C51, C52;
  E my pass over the plan's *kind* lines), and schedules Design for C42 only (plan:244). The forecast (plan:255-258, :272) counts
  no Design stage, as it counts no council (it says so of the latter). Meanwhile C31 (a new module with an interface, U2) is a *bug*, C23 (seven `main`s
  onto a new contract) a *bug*, and C30 (two tables, a generator, a page) a *chore*, which routes the layer's core around
  Design. **Fix:** a ruling the PO strikes or keeps — "the accepted design (§4, §5, §6) is the approved spec for C14,
  C21, C23, C28, C30, C31, C36, C39, C41, C43, C46, C48, C50, C51, C52, C53; part 1's CH block is the spec for C6, C13,
  C22, C24, C27, C40, C45; C42 alone enters Design" — and the kinds follow what each card is (C31 and C30 stories).
- **G2 · where a card's fields live once filed.** The issue form has *Needed by*, *Value proven by* and *Archive*
  (E `.github/ISSUE_TEMPLATE/item.yml`); each card block has eleven fields. Nothing says where *depends on*, *tests*,
  *prints*, *removes* and *must not break* go, and the board has no dependency field (*Waiting on* is for the PO,
  `scrum/README.md:242-243`). A hard edge that lives only in this plan is lost at filing. **Fix:** one sentence in R10:
  the block below *Value proven by* in the body, and each hard edge also as a GitHub "blocked by" link if the PO wants it
  machine-read (—: whether `tools/board.py` reads one).
- **G3 · the global numbers are a schedule, not an order.** C1–C77 are "numbered in the proposed global order"
  (plan:66), which is the interleave `<scratch>/sim4.py` forecast (plan:56); C30 is numbered before C31 although
  DP2 (a) puts I2 first on one slot (plan:193), because R7 lends the fix lane's slot. A changed size renumbers the
  cards, and Ready's order is the PO's (W11). **Fix:** two ordered lists, one per lane (L1…, F1…), the interleave rule
  (R7) stated once, and the forecast as a separate table.

### Card by card

| card | fails | what is wrong | fix |
| --- | --- | --- | --- |
| C1 | S | Two sizes for one card: S "plus machine time" here (plan:504, part 1's), M in the design (E design:1614 `I0a CH-2 (M)`). The forecast spends 0.1 day on the card every I1 card waits on. Part 1's CH-2 is "refuse; then sweep before and after the epic" (proposal:1299): the sweep *before* rides in C7, the sweep *after* is on no card (E `grep -n sweep` on the plan → lines 320, 333, 639, 643 only), though the design names "dated sweeps before I1 and after I4" as the guard against re-anchoring hiding a dead mutant (E design:2110). | One size with its reason. The after-sweep as a named task at I4's close (move M12), and the coverage row of CH-2 says where each half went. |
| C2 | 1 | Two concerns in two places: a board's stand-in silicon (`boards.validate`, the chip table) and an interpreter image's chip (`check_spine`'s simulation stage reading `--firmware`'s image, E `check_spine.py:582-583`; `flash_image.py`, which has no `--chip` today, E `flash_image.py:81-85`). Different fixtures, scripts and users (the bin's `boards-valid`; irrigation's image). Also refuter §3.3. | C2a the board half (fix lane first, D8); C2b the image half after it, reading the same table. |
| C3 | V, B, P | (a) "change the exit code each gives the bin" (plan:317) is unspecified, and the choice decides the result: `tests/test_check_bom.py:138-145` asserts `check_bom.main([…]) == check_bom.EXIT_PROBLEMS`, so a mutant that sets `EXIT_PROBLEMS = 0` leaves it green while the bin's `make` (`Makefile:186`) sees 0; `tests/test_check_vendor_pins.py:158-161` only asserts the three constants differ. (b) C3's own cases would repeat that blind spot if they compare with constants. (c) The bin's live call `check_vendor_pins.py $(BOARD_FILES)` (E the bin's `Makefile:223`) is not pinned and not said. (d) Its needed-by is Q36 (a) (plan:555), asked in batch 2 (plan:213) after C3 is in Ready (plan:245). | Write the three mutants on the card before the run (a constant in `check_bom`, the needs-measurement mapping in `check_physics`, `EXIT_MISMATCH` in `check_vendor_pins`); C3's cases assert the literal integers 0, 1, 2. Say that `:223` is network and is measured in I2 (f). Q36 in batch 1 or 2 before C3's Build. |
| C4 | B | (a) "removes `needs._words` as a private copy reached from `parts`" (plan:577): nothing in `parts.py` reaches it (E `grep -nE '_words' scripts/parts.py` → nothing); part 1 named that import as the alternative it refused (proposal:676-679). A second, different `_words` exists: `drawer._words`, a predicate used as a validator (E `drawer.py:54`; `needs.py:30-31`). (b) "one `words()` at layer 1 beside `store.PLAIN`" (plan:576) is part 1's layer number; in the design's table `store` is layer 2 (design §4.3), which C5's test enforces. | *Removes*: "`needs._words` (`needs.py:122-123`), moved down as `words()`", and say whether `drawer._words` stays. Name the module, not a layer number. |
| C5 | 1, B | Two tests of two kinds, with two expected lists: the outcome invariant (16 `main`s' behaviour; E `grep -l '^def main' scripts/*.py` → 16) and the import direction (structure; it needs DP1's layer list). The invariant asserts "one item with a `where` and a `sentence`" (plan:599), which is DP9's vocabulary, asked in batch 2 (plan:212) after C5 builds in I0. | C5a the invariant, C5b the layer test (S). DP9 before C5a's Build, or C5a asserts exit 2 and no `Traceback` until C14. |
| C6 | V, P | (a) The pass line's example names `host_parts, simulation` (plan:630, from part 1); rc-car's copy differs from the library's in three keys `SHELF_DROPS` keeps: `host_parts`, `host_requirements`, `simulation` (E my field compare; `SHELF_DROPS` at `parts.py:899`). "Nothing else named" holds for spark-quickstart's `led-red-5mm` (E equal to the library's, my compare), a fact the card does not state. (b) "Rewritten on its next write" migrates the PO's own shelf (five files in his store, E the copy's listing) the first time he writes — not announced. (c) It changes `--audit`'s output in I0 before the baseline (refuter §3.1.2). | Pass line written with the three fields and the quickstart prediction. *Must not break*: announce the shelf's rewrite. After C7a (move M1). |
| C7 | 1, V, P | Three concerns: journeys in the suite, a measurement tool (`tools/snapshot.py`, plan:642), and a dated full mutation sweep (machine time, CH-2's). Its pass line holds by construction (refuter §3.4). Journeys that need `tsci` are skipped in the suite (design §10.1), so A3's run 2 (a chain run) proves nothing there; its baseline exists only in the snapshot. In Ready slot 5 behind three output-changing cards (refuter §3.1.2). | C7a: the snapshot and the baseline (A3's runs 1 and 2, STORE-9 and round 0's fixtures as they answer today, the three projects with plant-alarm's measured stop) — first (move M1). C7b: the journeys, whose value line is a seeded change to one journey's script that turns it red naming the step (a mutation row). The sweep a task of C7a. |
| C8 | — | none found. Merged with C9 below. | — |
| C9 | B, 1 | It prints "C8's two-names sentence" (plan:685) and tests the same reader, a hard edge on C8 that *depends on* omits (plan:686). Part 1 sizes CH-6 as one S change for #118 and #119 (proposal:893); constraint 2 (one card, one pull request) makes it two pull requests and two councils for one S. | One card reusing #118, #119 closed into it (move M5); or `depends on C8`. |
| C10 | — | none found. | — |
| C11 | — | none found. | — |
| C12 | V, P | (a) *Must not break*: "whether the bin's or irrigation's `rules.json` states a fabrication override is —" (plan:740-741). It is known: the bin's keys are `['//', '//physics', 'i2c_buses', 'must_not_float', 'physics']`, irrigation's `fabrication` is `{}`, plant-alarm has no rules file (E my reads). No sibling number moves; the bin's `check_physics` trace line gains words. (b) Its placement cites "(R5)" (plan:728), the merges ruling; no ruling places it. | Write both facts on the card, and list the bin's changed line among I0 (d)'s expected diffs. Name the key that places it: part 1's (c)(1), a circuit judged on the wrong copper. |
| C13 | B, S | The stage must read `expect-pin` steps from a `.scenario.yaml` (E irrigation's `wet-and-dry.scenario.yaml:19-21`); spark has no YAML reader (E `grep -rli yaml scripts/` → nothing) and constraint 7 allows no dependency (plan:113-115). The card says neither how it reads the file nor what it refuses that it cannot read. S may not hold. | The card names its reader: a line reader for the `expect-pin` blocks only, refusing anything else as could-not-run naming the line — or a dependency the PO allows. Size it after that choice. |
| C14 | 1, B | Frame and first adopter in one M–L card (refuter §3.3). New here: *changes* (plan:774-786) omits the pages that read the fields it moves — `--unverified`'s `data.questions` is read by `docs/guide/agents.md:263`, `commands/research.md:97`, `commands/identify.md:52`, `skills/spark-review/SKILL.md:72`, `skills/spark-design/SKILL.md:96`, `agents/datasheet-reader.md:53`; `--show --json`'s CONFLICT advice at `agents.md:265-266` (E grep). W16 and the design's I1 risk ("each page is edited in the same commit", design §15) put them in this commit. | List the pages in *changes*, and a test that fails when a page names a field the envelope no longer has (the page-sequence test, or a grep test). Split as refuter §3.3 (a)/(b) if the PO wants the frame proven on a small `main` first. |
| C15 | — | none found. | — |
| C16 | — | none found. | — |
| C17 | — | none found. | — |
| C18 | — | none found. | — |
| C19 | — | none found. | — |
| C20 | 1 | Two concerns merged by R5 (refuter §3.3), pulling CH-58 (rank 66, tier 4) into a rank-24 slot. The design gates CH-64 on Q19 (E design:1848 `24 · CH-64 \| — \| Q19`); the card names no Q19 and part 1 none either. | Say which document is right on Q19 and why; keep R5 as the PO's to strike. |
| C21 | B | *Changes* omits the agent guide's documentation of the shape it removes: `results[].unmeasured`, the `?` lines and "read `unmeasured`" (E `docs/guide/agents.md:176`, `:195`, `:224`, `:232`, `:237`, `:367`, `:384`) and `skills/spark-review/SKILL.md:43`. W1's amendment inside a product card (refuter §3.3). | List the pages; W1's amendment in its own commit, with the PO's DP9 answer quoted. |
| C22 | — | none found. | — |
| C23 | V, S | From C23 (I1) to C39 (I4) `assign_pins --json` speaks envelope 2 with its open facts in `data.unverified` and nothing in `assumptions`: the plan moved that removal from I1 (E design:599, §4.4) to C39 (plan:1349) without listing it among R4's departures. An agent reading the new field sees an answer resting on nothing — the silence criterion (d) forbids. Seven `main`s at M (refuter §3.3). | Either C23 maps `assign_pins`' `unverified` to `assumptions` (the design's I1), or its envelope says the field is not fed yet, naming C39 — a placeholder named, not an empty list. Re-size at re-plan point 1 (plan:333). |
| C24 | 1, V | (a) It cites Q6 (a), "before the code" (plan:988; proposal Q6), and makes the data pass its *last* task (plan:993), which is Q6 (b). (b) Its pass line ("before, 2 candidates; after, 6", plan:990-991) measures the data pass, not the code (RISKS-2: 2 → 6 with no code changed, proposal:582-583), so the code card cannot close until the PO has given his time. (c) Code and a write to the real store in one card (refuter §3.3). | C24a: the data pass, a chore with the PO, after Q6 in batch 2, its line RISKS-2's. C24b: the count and `--audit`, its line "the silent entries counted and named, on a copy of his store". Move M6. |
| C25 | — | none found. | — |
| C26 | R, P | (a) C26 *is* #69 and its pull request closes it, yet #69's "words that fit any project" half "stays on it" (plan:1028-1029). #69's value line holds both: "… prints the dev board's stand-in under 'what it cannot show' … and no generated file or library record names a lid, a bin or another project's hardware" (E `gh issue view 69`). That half reaches no card, and PQ3 (plan:207-210) does not list #69. (b) Placed at 26 (rank 36) ahead of C27 (rank 29) and C29 (rank 35) "to sit before C39" (R4), which is in I4; part 1 moves a prerequisite up only for D8's first fix (proposal:550-556). | File C26 new and keep #69 re-scoped to its words half, or move that half to C46 and add #69 to PQ3. Place C26 after C27 (move M9). |
| C27 | — | none found. | — |
| C28 | 1, R | Six `main`s, `--describe` for sixteen and `boards.py`'s exit in one M (refuter §3.3). New: CH-45's `init` half changes what `init` answers when there is nothing to do; #71 P137 changes what `init` says it did (E `gh issue view 71`). Not placed. `test_the_bin_s_value_calls_print_the_same_bytes` (plan:1081) is a suite test and cannot read C7's snapshot (design §15); its fixture is synthetic, and the comparison with the snapshot is a separate run. | Name #71 and its order relative to C28. Say the test is synthetic and the snapshot comparison is the iteration's measurement (f). |
| C29 | M | Its test is named; the failure it prints is not (which key or stance is missing). | Name the assertion's sentence. |
| C30 | B, 1, V, S | (a) Removes `footprint_module` while `REQUIRED_FOR_FAB = ("footprint_module", "footprint_export")` (E `boards.py:67`) requires it until C37 (refuter R3; confirmed). (b) It generates `envelope.schema.json`, which is I1's artefact (E design:904 "from `outcomes` (I1)"). (c) Its value is "H3 as I3 states it" (plan:1113), whose (b) is C2's line and (e) is C37's. (d) Q16 decides part of its *changes* (plan:1120) and is asked in batch 4, "before I2 and I3 close" (plan:220), after C30 can enter Build beside I2. (e) M for two tables, a generator, a page, a reader test and five removals: M–L (my estimate). | (a) Move M7. (b) The envelope schema in C14 or C23. (c) C30's own lines: I3 (a), (c), (d), (f) and #61's. (d) Q16 before C30's Build. (e) M–L. |
| C31 | B, 1, S, P | Hard edges part 1 removed (refuter §3.1.5); many concerns at M (refuter §3.3); kind *bug* routes a new module around Design (G1). It is the largest priority inversion in the plan: CH-1 is rank 8, tier 1 (proposal:837), at position 31. | The PO's call (move M15): CH-1's refusal as part 1 sized it, early in the fix lane, then `where` in I2 replaces it (W16); or as planned, said as a choice. |
| C32 | B, P | Rank 6 (proposal:778) waits for C28 at position 32, though part 1's edges are soft (CH-18, CH-5). Its search and show half lives in `parts.py`, which C14 already moves onto `cli`; its `--validate` half reads the selection inside `boards.py`'s loop (`boards.py:476`, plan:1188), which needs no `cli`. | After C14 in I1's fix lane, with C28 soft (move M10). |
| C33 | — | none beyond refuter §3.1.5 and the plan's own note on #84's value line. | — |
| C34 | — | none beyond refuter §3.1.5. | — |
| C35 | 1, B | Three changes, the third conditional on an unknown: "`agents/datasheet-reader.md` loses `Write` and `Edit` once `--fact-set` is shown to set every field it fills (—, part 1)" (plan:1257-1258). The catalog writer's name — an interface agents call — is "set in the card's task plan" (plan:1256), after Ready. | The tool-list change to its own card after a read settles the —. The operation's name decided before Ready. |
| C36 | V, B | It removes "any stderr line of the generator is PROBLEMS" (E `check_spine.py:374-375`). That rule is plant-alarm's only `problems` today: my run gives `[!!  ] schematic-notes` for `SPK_N` and `SPK_P` and `[????] footprint`, exit 1; `status_of` returns problems when any, else could-not-run (E `outcomes.py:43`). If C36 makes those notes non-problems, plant-alarm goes 1 → 2 while its amplifier still drives nothing. The card says "plant-alarm's stop unchanged" (plan:1289). Part 1's "the four circuit-gap notes stay problems" is on no card (refuter §2.2, §5). | C36 names which generator notes stay problems (a net with one member: kind `design`), with a test on the `SPK_N` case, and announces plant-alarm's exit either way. |
| C37 | P, B | Rank 15, tier 1 (proposal:1058), part 1 *depends on* `—`, placed at position 37 behind C30 (I3). Its change can check `physical.header` presence directly and judge the selection, as `emit_footprint._missing` already checks geometry today; C30 then makes it a row (the F→A pattern the plan uses for C2 and C11). Landed first, it retires `REQUIRED_FOR_FAB`'s key-presence check, so C30's removal of `footprint_module` breaks nothing. | Move M7. |
| C38 | P | Placed after C35 (rank 53, tier 3) although C38 is rank 17, tier 1, and is a hard prerequisite of C41 (plan:1410); C35 unblocks nothing. The plan's own rule: priority, then the smallest unblocker (plan:82-86). | Move M8. |
| C39 | V, B, 1, S | (a) "13 subTests green" (plan:1344) cannot pass at C39's Done: C39 names ten producers (plan:1348-1352); `generic-board` is C51's (its tests list "`tests/test_ledger_channels.py`'s `generic-board` subTest", plan:1621-1622), and `edited-after` and `unknown-origin` come from `state` (design §4.2's producer table, "new: `state` (§6.3)"), C41 and C43. (b) `unserved` is claimed twice: C39 lists `emit_board` as its producer (plan:1349), C41 removes `check_spine.left_off`'s channel "which becomes the basis `unserved`" (plan:1401), and the design gives it to `state` (E design:449). (c) "Whether C13's coverage line becomes an entry or stays a note is settled here" (plan:1352): an open design question inside a build card. (d) Ten producers in eight modules, `ledger.py`, the board-facts producer and the firmware levels at M: M–L (my estimate; refuter §3.3). Refuter R2: `regulator_3v3_a` already reaches `unmeasured` through physics, so a board-facts producer lists it twice unless the card says which wins. | (a) "10 subTests green; 3 listed as expected, each naming C41, C43 or C51", and those cards move them out. (b) `unserved` to C41 alone. (c) A question in batch 5 with a recommendation. (d) M–L, and the double listing decided on the card. |
| C40 | P | Q24 decides it (plan:1372, :1382) and is asked in batch 4, "before I2 and I3 close" (plan:220); an ask must precede the card's Build, not its iteration's close. | Q24 before C40's Build. |
| C41 | 1 | The page-order check (CH-41's half; plan:1406, `tests/test_journeys.py::test_each_page_s_sequence_is_a_path_through_the_stage_table`) inside the state card (refuter §3.3); `unserved` (C39 row). | The page-order check to C7b's journeys or its own card. |
| C42 | B, S, P | (a) Q8 decides where the command lives (plan:1426, "a `parts.py` row or a `boards.py` verb: Q8") and is asked in batch 4 (plan:220), while C42's Design opens in the first slice (plan:244): the spec cannot close. (b) Part 1 sizes CH-24 L (E proposal:1429); the plan's two halves are M–L and S (1.6 card-days on its mapping against L's 2.5), while the skeleton half carries the bulk — a per-chip facts table citing `soc_caps.h`, the variant from `boards.txt`, pins through `parse_pins`, documents kept with their digests. (c) Its pass line rests on a document the PO's store does not hold: no DFR1075 document under the copy's `sources/` (E my search); round 0 read a vector PDF from the wiki and parsed it geometrically (E P100 `diary-round-0-board.md:24`, `:28`) — a network fetch and an agent's parse, n = 1, said nowhere on the card. | (a) Q8 in batch 2; Design opens after it (move M4). (b) L, or the per-chip facts table as its own card, which C2's table and C51's role column also read. (c) Say n = 1 and the network step on the card. |
| C43 | V | Its value is "H4 and its pass lines (a)–(f)" (plan:1448): (b)'s corpus, irrigation's `sim/WHAT-THIS-CANNOT-SHOW.md`, is absent (E `ls ~/Development/irrigation/sim` lists none; refuter R4), and (f) has no pass line. | (b) regenerates `sim/` on the copy first and lists the expected sentences before the run. |
| C44 | — | none found. | — |
| C45 | B, P | "From the library or the store" (plan:1479): boards have no store place until CH-27, which the plan defers to P178 (plan's deferred table; proposal:1522-1538). The store half is unbuildable and untested — both tests copy from the library (plan:1488-1489). Q8 decides the verb's home (plan:1485) and is asked in batch 4, after C45 in I2 can enter Build. | Scope "library → project"; the store half with CH-27 in P178. Q8 in batch 2. |
| C46 | — | none found (it is where #69's words half could land: C26 row). | — |
| C47 | — | none found. | — |
| C48 | V | "Every stage reads only the record keys it declares" depends on HB, the key-level audit being buildable (design §14 HB, §17.3). If it is not, the card cannot close, and the design's fallback (keys declared and reviewed by hand) is not on the card. | Add the refutation branch: what the card closes on if HB fails. |
| C49 | P, V | Its place above the cut (R4: "what I5's plant-alarm measurement needs") and its pass line ("plant-alarm's schematic `ok`") rest on plant-alarm stopping at the schematic on `power.io_volts`. It does not: `[ok  ] schematic  11 trace(s) written`, then `[????] footprint` (E my run; refuter R1). The `io_volts` datum moves plant-alarm nowhere. | Back to rank 41 after C47, or below the cut (move M11). Pass line: the XIAO's listing names each stop once; plant-alarm's footprint stop as Q21 decides. |
| C50 | — | none found. | — |
| C51 | V | "The simulation reached" already holds with the S3 (refuter §3.4); only the entry is new. | Pass line: `board.choice` is the first entry, and a requirements file naming no board gets none. |
| C52 | 1 | Two concerns with different prerequisites: the generic header for target `simulate` (needs C50) and the silkscreen mark on every placeholder footprint, part placeholders included, which needs neither targets nor the ledger (`footprint_placeholder: true` exists today, design §5.3) and rests on HE, unknown (design §14 HE). | C52a the header (I5). C52b the mark, after a one-hour check of HE, placeable as soon as it holds (move M13). |
| C53 | V | A judgement pass line (refuter §3.4). | Refuter's fix. |
| C54 | — | none found. | — |
| C55 | — | none found. | — |
| C56 | — | none found. | — |
| C57 | — | none found (its bench step needs the PO's hands, and says so). | — |
| C58 | — | none found. | — |
| C59 | R | It removes "run `init` again with `--force`" everywhere (plan:1779-1783); #48 P114 is a bug in that flow ("init --force lists only what is still unanswered", E `gh issue view 48`) and #71 P137 another ("init says only what it did"). Neither is placed; the card names #48 as "related" only. | Say whether #48 closes as superseded by C59 or lands first, and place #71. |
| C60 | — | none found. | — |
| C61 | — | none found. | — |
| C62 | — | none found. | — |
| C63 | 1 | Four changes behind three different questions (Q29, Q33, Q45; plan:1855): the card closes only when all three are answered. | Split by question; the download cap, gated by none, ships alone. |
| C64 | P | "Its form is P151's design" (plan:1869): no spec, so it enters Design, not Ready. | Say so on the card. |
| C65 | B | "Depends on C1" (plan:1897); part 1's edge from CH-2 is "for the held check" (proposal CH-67 *depends on*), which this card excludes. | Depends on —. |
| C66 | B, P | Hard on C3 and C39 (plan:1912); part 1 has soft CH-68 only (proposal CH-44 *depends on*). A figure's key and source are in the record; nothing of the ledger is needed. | Soft C3; drop C39; earliest I0. |
| C67 | 1 | L with part 1's three pieces, "S + M + M" (proposal CH-40 *kind*): the recorder tracked, the binding with JSON twins, the version check in `check_commit.py`. | Three cards. |
| C68 | B, V | Its tests use "C58's retired-sentence check" (plan:1948); *depends on* lists C31, C22, C4, C27 (plan:1950). Its pass line is the council's reading. | Add C58; name the gate assertion that holds the section. |
| C69 | — | none found. | — |
| C70 | — | none found. | — |
| C71 | — | none found. | — |
| C72 | — | none found. | — |
| C73 | — | none found. | — |
| C74 | — | none found. | — |
| C75 | V | Pass line is the council's reading. | The gate's name check, named. |
| C76 | — | none found. | — |
| C77 | — | none found. | — |

## Per iteration

Each iteration checked three ways: **W** it ends in a whole that runs for the bin, irrigation and plant-alarm · **H**
it states a hypothesis that can fail · **L** it says what changes if it does.

### I0 — the net and the baseline (plan:297-335)

- **W — partly.** The bin and irrigation: yes. Plant-alarm: the baseline's prediction "the schematic, on
  `power.io_volts`" (plan:310-311) is wrong (E my run: schematic `ok`, footprint could-not-run, exit 1 from two
  schematic notes). The baseline must record the measured stop. The baseline is also taken after C2, C4 and C6 have
  changed outputs (refuter §3.1.2; move M1).
- **H — Hf0 cannot fail.** Its pass line (d) excuses "lines a fix card names on purpose" (plan:324), named after the run.
  The diffs I0 makes are known now: C4's `--need` miss sentence (none of the three runs `--need`); C6's `--audit` lines and
  the shelf's rewrite; C12's words on the bin's `check_physics` trace line, with no number moved (E no fabrication
  override in the three projects); C13's coverage line in irrigation's simulation stage. **Fix:** (d)'s pass line is
  exactly these four, written before the run.
- **H — (a) depends on the mutant chosen** (C3 row). **Fix:** the three mutants on the card; a control that turns red
  replaces its mutant with one the existing tests miss, so the run measures C3.
- **L — present for (a)–(d);** (a)'s control branch changes nothing (refuter §3.4).
- **Constraint 10 cannot hold here**: "every placeholder named in the output" (plan:121-122) needs the ledger (I4). **Fix:**
  restate it for I0–I3 as "no channel of today's ten loses a line, against C7a's channel lines", which is testable now.

### I1 — one answer (plan:336-366)

- **W — yes** as stated, with refuter §5's two additions (the bin's stderr on every `make`; crash paths 1 → 2).
- **H — H1 cannot fail in I1.** H1 is about an agent acting from the JSON alone (plan:349); measurements (a)–(g) are
  properties of the output (plan:351-361); the first agent runs in C53, in I5, and the plan's own refutation of H1 is
  scheduled "later, from C53's cold run" (plan:365-366). **Fix:** restate H1 as what (a)–(g) measure, and add one cold
  agent run on the journeys at I1's close (n = 1, said; its tokens under DP11, which then moves to batch 2). That run is
  where "the envelope lacks a field" can fire while the envelope is still cheap to change.
- **L — present for (a), (c), (f) and the rows moved; none for (b), (d), (e), (g)** (refuter §3.6.3). (e) "reported, not
  promised" has no line.
- **Asks out of time**: Q42 and Q43 "which order the fix lane inside its tiers" are asked "during I1" (plan:216-217) —
  the fix lane has run since I0. C23's empty `assumptions` (C23 row).

### I2 — where, the guard and the lock (plan:368-395)

- **W — yes.**
- **H — H2 and Hf2 can fail** through (b), (e), (g), (i), each with a consequence; (a), (c), (d), (f), (h) have none
  (refuter §3.6.3).
- **L — re-plan point 2 contradicts the schedule.** R10 commits "Ready through I2" and re-plans at I2's close
  (plan:180, :394), but the first slice puts C42 (I3) in Design (plan:244) and R7 runs C30 (I3) beside I2 (plan:171-172).
  Either I3's first cards are committed with I2, or they wait for re-plan point 2 and R7 does not lend the slot to them.
  **Fix:** the PO commits I0–I2 plus C30, C37 and C42's Design by name, or holds them; R10 says which.
- **Order**: C38 after C35 (move M8). Q8 (C45, C32's sentence) in batch 4 (move A).

### I3 — the board contract, and boards as records (plan:397-423)

- **W — no, twice.** The bin's `boards.py --validate --for-fab` is red between C30 and C37 (E `boards.py:67`; the bin's
  `Makefile:182`; refuter R3) — move M7 removes it. Plant-alarm: "after C49's datum, its chain stops at the footprint,
  not the schematic" (plan:405-406) — it stops at the footprint today (E my run), so the iteration predicts a change that
  will not happen.
- **H — H3 can fail;** H3b's (g) can fail, n = 1, through a network fetch and an agent's parse of a vector PDF (C42 row).
- **L — present** for (b), (d), (e), (g). Q16 and Q24 are asked "before I2 and I3 close" (plan:220), after C30 and C40
  can enter Build.

### I4 — the stage table, the run record and the ledger (plan:425-450)

- **W — not as stated.** Plant-alarm "the same status" (plan:434) contradicts C36 (C36 row: exit 1 → 2 unless one-member
  nets stay problems). The bin's `make` writes `.spark/state/` on every run of `boards.py --resolve` (E the bin's
  `Makefile:96`), ignored by itself under DP7 (a) — said on C41, fine.
- **H — (b) has no corpus** (C43 row); C39's 13 subTests cannot pass (C39 row); (f) has no pass line, which is right for
  a measurement that feeds re-plan point 3.
- **L — present** for (b), (e), (f), (g). Missing: the after-sweep, the one measure of whether I1–I4's re-anchoring hid a
  dead mutant (C1 row; move M12).

### I5 — fidelity as a working loop (plan:452-475)

- **W — plant-alarm's table starts from a wrong "before".** I5 (a) compares each stale list with design §7.6's tables;
  plant-alarm's row predicts a schematic stop that does not exist (E my run). **Fix:** rewrite plant-alarm's §7.6 row
  from the measured stop, dated, before I5 runs (pass lines are set before the run, constraint 10).
- **H — (b) is n = 1 and partly a judgement** (refuter §3.4); the rest can fail.
- **L — present for each line**, and re-plan point 4 decides C76.

### I6, I7 — on their triggers (plan:477-492)

- **W, H, L — met.** Each trigger is measurable (I5 (a)'s extra stages; P178's shared store or a named client), each
  pass line can fail, and the three projects are unchanged by default.

## Proposed order

### A. The asks, re-batched by the first card each gates

`scrum/README.md:238-241`: one batch open at a time, at most six questions. The plan's batches keyed to iteration
closes; these are keyed to the first card's Build (or Design).

| batch | asks | why there |
| --- | --- | --- |
| 1 — before filing | DP1 · DP2 with **Q42, Q43** as its keys and PQ5 · DP15 with **DP13** · PQ1 · PQ2 · PQ3 with DP12 and **#69's words half** | Q42 and Q43 order the fix lane from its first card (plan:216-217 put them in batch 3); DP13 is scope, which the cut line already assumes (plan:229 asks it in batch 6). Still six items. |
| 2 — before the first card enters Build | **DP3 with Q5** (round A on today's spark, before any fix: the design's own reason, design DP3) · **Q36** (C3) · **DP9** (C5a's item shape) · **Q8** (C42's Design, C45, C32's sentence) · **Q6** (the data pass, C24a) · G1's ruling (which stories have their spec) | Each gates a card in the first slice or the first I2 cards. |
| 3 — before C14 | Q14 · Q25 · Q41 · Q1 with Q34 and Q38 · Q44 · Q2 | As the plan's batches 2–3, less what moved up. |
| 4 — before C30 and C40 enter Build | Q16 · Q24 · Q11 · Q21 · Q7 · DP11 (if I1's cold run is taken) | Keyed to the card, not to "before I2 and I3 close". |
| 5, 6 | as the plan's (plan:224-229), less DP13 | — |

### B. The moves

Each move: what, from → to, and the reason. M1–M14 are this critic's proposals; M15 is the PO's call with both costs.

| move | what | from → to | reason |
| --- | --- | --- | --- |
| M1 | C7 split; C7a (snapshot and baseline) | Ready slot 5 (plan:245) → first card of the layer lane, before any output-changing fix enters Build; C7b (journeys) after C5a | Every iteration's "whole" diffs against it; C2, C4, C6, C12 and C13 change outputs (their rows); refuter §3.1.2 found the order, the split lets the baseline land without waiting for the journeys. |
| M2 | DP3/Q5 | batch 2 "before C14" (plan:212) → batch 2 "before the first card's Build" | "A baseline taken after I1 would measure the change, not the start" (design DP3) applies to I0's fixes. |
| M3 | The asks of A | as the table | Each gates a card that runs before its old batch. |
| M4 | C42's Design | first slice (plan:244) → after Q8 is answered | A Design whose interface (the verb's home) is undecided cannot close; until then the Design slot holds the first story's spec under G1, or nothing. |
| M5 | C8 + C9 | two cards → one, reusing #118, #119 closed into it | One S change in part 1 (proposal:893), one shared sentence and reader; constraint 2 would spend two councils on it. |
| M6 | C24 split | one card in I1 → C24a, the data pass with the PO, after batch 2 (Q6 (a)); C24b, the count, after C14 | The card cites Q6 (a); part 1's "before rank 1 — decisions and data, no code" (proposal:576-583); each half closes on its own line. |
| M7 | C37 | position 37, after C30 (I3) → fix lane after C27, as F→A; C30 then makes it a row | Rank 15, tier 1, no edge in part 1; retiring `REQUIRED_FOR_FAB`'s key check first removes the window in which C30 turns the bin's Gerber recipe red (E `boards.py:67`). |
| M8 | C38 | after C35 → right after C34 | Rank 17, tier 1, a hard prerequisite of C41; C35 is rank 53 and unblocks nothing (plan:82-86, the plan's own rule). |
| M9 | C26 | before C27 → after C27 and C29 | Ranks 36 against 29 and 35; C26 is needed by C39 only, in I4. |
| M10 | C32 | after C28 (I2) → after C14, in I1's fix lane; C28 soft | Rank 6 (proposal:778); "search … the boards for sure" (D the PO 2026-10-10); part 1's edges are soft. |
| M11 | C49 | above the cut (R4) → rank 41 after C47, or below the cut | Its reason and its pass line rest on a stop plant-alarm does not have (E my run). |
| M12 | The after-sweep | no card → a task at I4's close | Design §15's guard against re-anchoring hiding a dead mutant (E design:2110). |
| M13 | Splits | C2 → C2a/C2b; C5 → C5a/C5b; C7 → C7a/C7b; C52 → C52a/C52b; C63 by question; C67 into three | One concern each (their rows). C14, C23, C28, C31 and C39 as refuter §3.3 proposes, re-sized at re-plan point 1 with the rows each moves. |
| M14 | Numbering | C1–C77 global → L1…, F1… per lane, forecast apart | G3. |
| M15 | CH-1 and CH-11 | C31 and C34 (I2, after C21, C23, C28) → **the PO's call**: early in the fix lane as part 1 sized them, or as planned | The plan's largest priority inversion (rank 8 at position 31, rank 13 at 34) on an incident class (#101). Cost of moving: each `main` that reads the store maps the refusal itself until `cli` carries it, then that code goes (W16), and C31 shrinks to `where`. Cost of staying: the refusal waits about thirty cards. |

### C. The resulting start, and each lane above the cut

If M1–M14 are taken (M15 not):

- **Build (2):** C7a (layer lane) · C1 (the fix lane's slot, lent by R7, because every fix card changes an output the
  baseline must record first).
- **Design:** none until Q8 and G1's ruling; then C42.
- **Ready (5):** C2a · C3 · C5a · C4 · C11. C6 next.
- **In flight:** #6, C7a, C1 — three; C24a joins when the PO takes Q6 (a).
- **Layer lane:** C7a · C1 · C3 · C5a · C5b · C7b · C14 · C21 · C23 · C28 · C31 · C33 · C30 · C36 · C39 · C41 · C43 ·
  C46 · C48 · C50 · C51 · C52a · C53.
- **Fix lane:** C2a · C4 · C6 · C8+C9 · C10 · C11 · C12 · C13 · C2b · C15 · C16 · C17 · C18 · C19 · C20 · C24a · C22 ·
  C24b · C32 · C25 · C27 · C26 · C29 · C37 · C34 · C38 · C35 · C45 · C40 · C42 · C44 · C47 · C52b (when HE holds).
  C49 below the cut.

### What the PO must decide

- G1: which stories have their approved spec in the accepted design or in part 1, and which enter Design.
- M15: CH-1 and CH-11 early as part 1 sized them, or in I2 as planned.
- R10 with I2's row: commit I0–I2 plus C30, C37 and C42's Design by name, or hold them.
- C36: which generator notes stay problems; plant-alarm's exit after it.
- C26: whether #69's words half moves to C46 or stays on #69 with C26 filed new.
- C23: `assign_pins`' open facts into `assumptions` in I1, or a named "not fed yet" until C39.
- I1: one cold agent run at I1's close (its tokens), or H1 restated to what I1 measures.
- C13: a line reader for `expect-pin` blocks, or a YAML dependency.
- C20: whether CH-64 waits on Q19 (the design) or not (part 1, the plan).

## Searches

None. No web or MCP search was made. The `gh` commands listed under *Read* are read-only views of the board.

## Found on the way

- E · `status_of` returns `problems` when any item is a problem, so a stage that could not look is hidden behind a
  finding in the same answer (`scripts/outcomes.py:43`): plant-alarm's footprint could not run, and the answer reads
  `problems`, exit 1 (my run). W1 holds (it never reads as a pass), but an agent reading only the status learns nothing of
  the stage that could not look; neither the design's `verdict` rule (design §5.1) nor the plan says how a mixed answer
  names both.
- E · Existing tests pin exit codes against the module's own constants (`tests/test_check_bom.py:138-145`;
  `tests/test_check_vendor_pins.py:158-161` asserts only that three constants differ), so a mutation of a constant is
  invisible to them — a QA pattern for #103 / #97 beyond C3.
- E · spark has no YAML reader (`grep -rli yaml scripts/` → nothing) while Wokwi scenarios are YAML (irrigation's
  `sim/scenarios/wet-and-dry.scenario.yaml`): any scenario-aware check meets "standard library only" (`docs/guide/agents.md:70`).
- E · Two functions named `_words` mean different things: `needs._words` returns a set of words (`scripts/needs.py:122`),
  `drawer._words` is a truthiness validator (`scripts/drawer.py:54`, used by `scripts/needs.py:30-31`).
- E · The PO's `projects.json` (read from the scratch copy) lists five projects — irrigation, smartbin-local, rc-car,
  spark-quickstart, plant-alarm — while the plan and the design measure "the three"; rc-car's copy is C6's own pass line,
  and spark-quickstart holds a project copy of `led-red-5mm` that `--audit` (C6) will read.
- E · Part 1's K13 example for rc-car's `tactile-button` names two differing fields (`proposal.md`, CH-26 *prints*); the
  copy differs in three, `host_requirements` included (my field compare against `parts/tactile-button.json`).
- E · `design/refuter-round-1.md` (01:41) was written after the plan (01:16, both 2026-10-11 by `ls -la`); its §3 and
  this file overlap on the order, and its §7's alternative iteration 0 and this file's moves M1, M15 answer the same
  question two ways — the re-plan reads both.
