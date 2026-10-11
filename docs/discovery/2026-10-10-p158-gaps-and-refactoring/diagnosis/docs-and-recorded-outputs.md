# Diagnosis — docs-and-recorded-outputs (P158 part 1, rows K68–K74)

Written 2026-10-10 against spark 0.8.1 (main `a8aa34d`) for the P158 council, from the code and from runs on copies,
not from the reports alone. Setup: a `git archive HEAD` of spark unpacked at `<scratch>/spark`, so no `--help` or
build could write into the checkout; a copy of the PO's store at `<scratch>/store` and an empty one at
`<scratch>/store-empty`; every spark command with `SPARK_HOME`, `HOME` and `TMPDIR` as three separate words (checked
once with `env | grep SPARK_HOME`); `CLAUDE_PLUGIN_ROOT` at the copy; `PATH` led by the bin's `node_modules/.bin` for
`tsci` 0.0.2621; `gh` read-only, once with the PO's config named by `GH_CONFIG_DIR` so a 404 could be told from "not
logged in". Nothing ran against `~/.local/share/spark`; nothing was written under spark but this file. Tags: E a
pointer, H a claim with its source, D a decision (who, when), — unknown. Line numbers are spark's at `a8aa34d`.

**What the area is.** For a stranger, the documents are spark: `README.md` (231 lines), `AGENTS.md` (16), five guides
in `docs/guide` (2,216 lines together: journey 1,037, agents 481, commands 261, how-it-works 243, developing 194),
seven command pages, three skills, four agent pages and `boards/README.md` (101) — E `wc -l`, 2026-10-10. Two
conventions carry the evidence: a pasted output sits in a ```` ```text ```` block under
`<!-- output: run DATE, spark VERSION -->`, and a ```` ```sh ```` block marked `<!-- runs: exit N -->` is executed by
the gate. The gate is `tools/check_docs.py`, run by `tests/test_docs.py` in the suite and so at every push; its scope
is `doc_files()` (`tools/check_docs.py:30-33`).

## 1. Root causes

### RC-docs-and-recorded-outputs-1 — the gate proves that an output carries a provenance note, never that the provenance is current, and nothing re-records

- **where** · `tools/check_docs.py:20` (`OUTPUT_NOTE`), `:142-145` (`undated_outputs`, the only test on a note:
  `if not OUTPUT_NOTE.match(above)`), `:170-173` (`version_mismatch`: the plugin's version is tied to README's footer
  alone), `:148-167` (`failed_examples`: compares an exit code, never an output, and only for blocks marked `runs:` —
  E `grep -rn 'runs: exit'` → three: `docs/guide/journey.md:636`, `docs/guide/agents.md:45`, `:336`, all listings or
  `check_all` on an empty project); `docs/guide/journey.md:195` ("These commands ran from a recording script") — the
  script is in no commit (E `git ls-files .superpowers | wc -l` → 0; `grep -rn "recording script"` over the tree →
  that line only; 2026-10-10); `scrum/README.md:236-241` (DoD 10: a release changes `.claude-plugin/plugin.json` and
  the footer); E `git show --stat 1fc0909` (v0.8.1) → 2 files, 2 lines; `36d6998` (v0.8.0) → plugin.json, README,
  scrum/README; `87daf54` (0.7.0) → 2 files; PR #122's body: "Two files".
- **why** · The README design chose provenance over currency: §5 item 6 makes "a pasted output block has no `output:`
  comment with a date and a version" the failure (`docs/2026-10-05-readme-design.md:90-101`), and DoD 8 hands the
  rest to the council: "Nothing mechanical checks it: `tools/check_docs.py` cannot tell whether a status is still
  current" (`scrum/README.md:232-234`). Re-recording was a one-off script that was never committed, and the release
  step was defined as a two-line edit. So every release moves the footer and leaves every note where it was. Three
  bumps in two days (0.7.0 on 2026-10-08, 0.8.0 and 0.8.1 on 2026-10-09 — E `git log -- .claude-plugin/plugin.json`)
  against recordings of 2026-10-05, 10-06 and 10-08 (journey.md:38-40) give 16 × "spark 0.6.0", 28 × "spark 0.7.0",
  0 × 0.8.x — E `grep -o 'spark 0\.[0-9]\.[0-9]' docs/guide/*.md README.md | sort | uniq -c`, 2026-10-10, the
  catalogue's count; 42 of the 44 are notes over the 42 ```` ```text ```` blocks (journey 34, developing 5, agents 2,
  commands 1 — E `grep -c '^```text'`) and 2 are prose at journey.md:39-40. Verified on the copy: `undated_outputs`
  accepts `spark 0.1.0`, `0.7.0` and `9.9.9` alike, and `python3 tools/check_docs.py` on the 0.8.1 tree prints
  `docs: 7 file(s), nothing named that is not there`, exit 0 (my runs, 2026-10-10).
- **kind** · design.
- **explains** · K68 wholly; it is also the condition under which K69's and K70's stale sentences stood through two
  releases.
- **how a person or an AI agent would have known** · Only by reading a note and the footer side by side, as USER-11 did
  (`council/user.md:19`). The gate's summary says the opposite of "stale", and an agent reading journey.md has no
  signal whether "spark 0.7.0" still holds on 0.8.1. Where I compared, it does: five blocks re-run on 0.8.1 in an
  empty store — `--needs-set`, `--requirements`, `check_spine` (the first 13 of its 17 lines), `parts.py --list` (8
  rows) and `check_all.py --project . --json` on an empty project (the 12 lines the page shows) — were identical in
  form to the 2026-10-08 and 2026-10-05 recordings, down to `tsci 0.0.2621; the documents were measured on core
  0.0.2600` (E my runs, 2026-10-10). The `--match`/`--pick`/`--audit` blocks depend on a drawer I did not rebuild, so
  they were not compared. "Behind" is therefore measured; "wrong" is not shown anywhere.

### RC-docs-and-recorded-outputs-2 — the README's one typed block is outside the gate and ends in a step that only Claude Code can finish

- **where** · `README.md:125-132` (the block: six commands, no `<!-- runs: exit N -->` above it, so `failed_examples`
  skips it — `tools/check_docs.py:152-154`, `if not mark: continue`); `README.md:121-123` ("It also marks each step as
  it begins, with `parts.py --step <project> S` … The block leaves them out, so its last line exits 2: no step is in
  the history"); `commands/idea.md:13-18` (the marks are required) and `:161-169` (T, the tally: "Say it as it is;
  'its cost was not counted' is an answer too"); `scripts/cost.py:225` ("no step of %s is in the history —
  `parts.py --step <project> <step>` marks each") and `:232` ("no transcript of session %s here, so the cost of its
  steps is not known"); `docs/guide/journey.md:195-197` (the recorded run set `CLAUDE_CODE_SESSION_ID=demo-session` by
  hand so `--step` had a session to record).
- **why** · The block was written as "the scripts a person types" (README:117-119) but copies the whole of
  `/spark:idea`, whose last step reads Claude Code transcripts. Outside a session the tally exits 2 whatever the person
  does. Verified in an empty store on 0.8.1: lines 1–5 exit 0, 0, 0, 0, 0 (`--pick` answers `to get — known, not
  owned` for all three and writes 3 `reused` lines; `check_spine` built in 6 s wall time with `tsci` on the PATH);
  line 6 exits 2 with the history message. After the four `--step` marks it still exits 2, now with the transcript
  message (`no transcript of session <session> here, so the cost of its steps is not known`) — the same words as the
  journey's recording (journey.md:372-376). The `--step` lines were left out of the block because they need a session
  id, so the author explained the exit 2 instead of removing the step that causes it. No test runs the block: the
  three `runs:` blocks are all listings on an empty project.
- **kind** · design (of the block); the symptom is documentation.
- **explains** · K69. The tally half of K21 is the same mechanism; its exit 2 is honest and named, so K21 stays in its
  own area.
- **how one would have known** · README:123 says it in advance, and the tally's two messages name the cause exactly
  (`cost.py:225`, `:232`) — this part of the design is right. What nobody had: a test that the five lines above the
  tally still run. They do today (my run); a renamed flag or a changed pick refusal would reach a stranger first.

### RC-docs-and-recorded-outputs-3 — "not run" is prose, in about twenty places, with no list, no date and no way to retire one

- **where** · `README.md:62-66` (the three status words) and the admissions at `:70`, `:71`, `:72`, `:74`, `:76`,
  `:80`, `:103`, `:117`, `:151`, `:173`; `docs/guide/journey.md:75`, `:109`, `:135`, `:192`, `:553`, `:860`, `:907`,
  `:940`; `docs/guide/commands.md:238`; `docs/guide/how-it-works.md:155-156` ("Another board needs its own
  definition, a JSON file in the project's `boards/`; this was not run for these docs"). E `grep -c -i -E 'not run
  here|not run for these|not run for this|never run|none was run|not been run|was not run|were not run|not recorded
  for this'` over README and the guides → 26 matching lines, of which 6 define the words or describe behaviour
  (README:64-65, journey:32, agents.md:126, :462, commands.md:67), leaving about 20 admissions (my reading,
  2026-10-10). `scrum/README.md:232-234` (DoD 8). `council/round-0-runner.md:1-8`, `:28-29` (the own-board route run
  on 2026-10-09 in a scratch folder; "What stands" names files under `R/project`); E `find docs/discovery -name
  '*c6*'` → nothing: the round-0 board file is not in the repository.
- **why** · Two different things share one sentence. Some admissions are structural: a conversation (`/spark:drawer`'s
  words to entries, `/spark:idea`'s questions), an agent (`/spark:research`, the reviewers), a paid run (Wokwi) or the
  Claude Code install cannot be run by a Python gate, and the README's status words were designed to say so
  (`docs/2026-10-05-readme-design.md:45-48`). One is not: the own-board route is five scripts, four of them offline,
  and round 0 ran them in 14 minutes (round-0-runner.md:8). Because every admission is free prose with no date and no
  mark, nothing can list them, count them, or tell the structural ones from the one that was run on 2026-10-09 outside
  the docs. The sentence at how-it-works.md:155-156 is still literally true ("not run for these docs") and still
  misleads: a run exists, with its numbers (round-0-runner.md:31-59), and the page does not know. PO-15
  (`council/po-assistant.md:26`) is the same gap from the other side: the PO's store (110 drawer entries, 18 catalog
  records) starts past exactly these steps, so the admissions are also the steps no run here has covered.
- **kind** · documentation, on a design limit that is honest (DoD 8).
- **explains** · K70.
- **how one would have known** · The sentences themselves — they are the right thing to say — but no count, no date,
  no list. An agent planning P100's rounds read "not run" as "unproven" and made it the first act (D7/D8,
  `brief.md:83-84`); the refuter read the same sentence as the frame's weakness (`council/refuter.md:20-25`). Both
  were reading one undated sentence.

### RC-docs-and-recorded-outputs-4 — the own-board pages are the smart bin's workflow, and omit three facts the scripts already hold

- **where** · `boards/README.md:3-4` (the banner: "The steps are the smart bin's: they name a Makefile, `make check`
  and `config.py`"), `:37-42`, `:68-73` (those steps), `:59-62` ("`espressif/arduino-esp32` →
  `variants/<board>/pins_arduino.h` … record both under `sources`"); `docs/guide/how-it-works.md:145` ("boards/README.md
  has the schema") and `:160-173` (the five steps with spark's scripts — no word on how to find `<board>`, none on
  keeping documents); `scripts/check_vendor_pins.py:117` (`vendor.arduino_variant` is the field read), `:55-64`
  (`fetch_variant_header`: on any `gh` failure, `could not fetch %s from %s: %s` with `gh`'s stderr);
  `scripts/parts.py:1144-1152` (`records_with_documents` yields boards too), `:1176-1208` (`find_kept`), `:966-969`
  (`record_home` looks in the parts layers only), `:1670-1680` (`--fetch` → `no record called %r to fetch for`),
  `:1683-1692` (`--keep FILE --url URL` prints the entry to paste); `boards/firebeetle2-esp32s3.json`, keys
  `//documents` and `documents` (the P62b shape: `url`, `sha256`, `file`, `retrieved`, `title`, `version`, `member` for
  a zip member, `private_only`); `commands/research.md:21-27`, `:44-52` (`--kept`, `--keep`, `--fetch`, written for
  parts).
- **why** · (a) The variant folder: the page gives the path pattern and the record gives the field, but neither says
  how a person finds the folder's name among 409 (E `gh api repos/espressif/arduino-esp32/contents/variants --jq
  '.[].name' | wc -l` → 409, of which 11 match `dfrobot|firebeetle`, 2026-10-10). Round 0 guessed it from the S3's
  (round-0-runner.md:12). A wrong name is refused with the path and `gh`'s text — `mystery-board could not run: could
  not fetch variants/dfrobot_no_such_variant/pins_arduino.h from espressif/arduino-esp32: gh: Not Found (HTTP 404)`,
  exit 2 (my run, authenticated) — not with the field's name or the listing that would fix it; unauthenticated, the
  same line ends in `gh auth login`, so two causes look alike. (b) Board documents: the store already keeps them and
  `--kept` already finds them — on the store copy `parts.py --kept wroom` printed the S3's WROOM-1 v1.1 datasheet,
  `present`, with the three facts citing it (`power.module_peak_a — Table 11, page 15`, `power.deep_sleep_ua — Table
  12, page 15`, `power.io_volts — Table 9, page 14`), and `--kept dfr0975` the two schematic PDFs (my runs,
  2026-10-10) — but no page in the own-board route says that a board file has `documents` or how an entry gets there,
  so round 0 wrote provenance per number and kept nothing (round-0-runner.md:31-59, :70). The one route that writes an
  entry for you, `--fetch`, refuses a board id with a reason that is false for the person — `parts.py: no record
  called 'firebeetle2-esp32s3' to fetch for`, exit 1 (my dry run on the copy), while `boards.py --list` prints that id
  as a library record — because `record_home` never looks in `boards/`; and exit 1 is the code for "problems", not
  "could not run".
- **kind** · documentation; one implementation defect (the `--fetch` refusal's reason and exit code).
- **explains** · K72, K73. The pages' smart-bin steps themselves are K24/P127 (#61, board-records area).
- **how one would have known** · The S3 file's `//documents` comment is the only description of the shape, visible to
  someone who opens the file; `--kept` tells only someone who asks with the right word; the 404 names the path, which
  is enough for a reader who already knows the field. An AI agent reading the pages concludes, as round 0 did, that
  documents are not kept for boards.

### RC-docs-and-recorded-outputs-5 — the gate's scope is a list of three places, and style has no rule at all

- **where** · `tools/check_docs.py:30-33` (`doc_files`: README.md, AGENTS.md, docs/guide/*.md), `:182-194`
  (`problems`: every check is a function of a page's text, so the scope is only that list), `:201-202` (the summary
  prints the count: `docs: 7 file(s)`); `docs/2026-10-05-readme-design.md:90-92` ("It reads `README.md`, `AGENTS.md`
  and `docs/guide/*.md`"), `:39` ("`README.md` — about 120 lines, value first"); `docs/guide/developing.md:157`;
  `tests/test_orphans.py:27-36` (the one test that does read commands, skills and agents — for orphan scripts only);
  `docs/observations/INDEX.md:230-231` (E36a, E36b); #94's comment of 2026-10-08 (C-36: "widen `doc_files`").
- **why** · The scope was set when the agent pages were out of the design's frame; the functions are page-agnostic, so
  widening is a list edit — and today it would pass: five of the gate's functions (names, flags, output notes, links,
  personal paths) run over the 14 agent pages (7 commands, 3 skills, 4 agents) report 0 problems; over
  `boards/README.md` 2 — `config.py names no script` (the smart bin's file, P127) and `the output at line 15 has no
  <!-- output … -->` (the folder tree at `boards/README.md:15-24` is a ```` ```text ```` block, which the gate's
  convention reads as a pasted output: a false positive the convention invites) (my run on the copy, 2026-10-10). So
  the guard C-36 asked for is cheap and currently silent; its value is the day a command page shows a flag `--help`
  lacks, which today reaches Claude at the keyboard and the person pays. Density and line length have no rule anywhere
  (none in test_docs.py): README is 231 lines against the design's ~120; lines over 120 columns are README 10 (longest
  586), how-it-works 16, journey 32, agents 13, commands 11, idea.md 23 (longest 653), build.md 23 (longest 691) —
  table rows and list items mostly (E `awk 'length($0) > 120'` per page, 2026-10-10). The jargon lines C-36 named are
  still there: `commands/idea.md:11` ("docs/2026-10-04-store-design.md §8 S and M"), `:14` ("S's item 3"),
  `commands/research.md:99`.
- **kind** · design (the scope); documentation (the style).
- **explains** · K74.
- **how one would have known** · `docs: 7 file(s)` is the only hint that 14 pages are outside; nothing measures
  length.

### RC-docs-and-recorded-outputs-6 — the "menu" is a planning artefact, and the README's answer to "what can I build" is three sentences apart

- **where** · `scrum/SPRINT.md:611-622` (R2.5: "(a) a battery sensor node", "(b) a USB MIDI foot controller", "(c) a
  garden irrigation controller" — "the PO's answer can be one letter"), `scrum/PRODUCT_BACKLOG.md:1568-1569`;
  `README.md:25-29` (two boards, 8 parts, one builds, with the two `--list` commands), `:39` (the example: an S3, an
  L9110S, a power inlet, two buttons), `:142-146` (the recorded run's file: a button and an LED);
  `docs/guide/journey.md:636-650` (`parts.py --list` recorded, and run by the gate).
- **why** · The menu was never for the persona; it chose test domains. What a hobbyist can build today is a function
  of a small library, and the README states the library's size and the two shapes that were built — in three places,
  none framed as the answer to that question. USER-13 read these pages and reported no list (`council/user.md:21`).
- **kind** · documentation.
- **explains** · K71.
- **how one would have known** · Nothing says "this is all". `parts.py --list` on 0.8.1 prints the same 8 rows as the
  recording (my run).

## 2. What the design gets right and must be kept

- The note convention and its enforcement: `<!-- output: run DATE, spark VERSION -->` above every ```` ```text ````
  block, failed otherwise (`tools/check_docs.py:20`, `:142-145`; `tests/test_docs.py:74-77`; the mutation "an undated
  output passes" in `tests/mutations/p104-docs.json`). It is why K68 could be counted at all with one grep. Any
  re-recording must emit this note, not replace it.
- `<!-- runs: exit N -->`: a block executed in a fresh project with a store of its own and a 60 s bound
  (`tools/check_docs.py:148-167`; `tests/test_docs.py:79-91`; the mutations "a failing example passes", "an example
  runs in the person's store", "a hanging example stops the check"). It is the mechanism K69's fix needs, unchanged in
  kind.
- Each check is a pure function of (text, root), so the suite feeds literal Markdown (`tests/test_docs.py:26-103`) and
  `problems()` composes them (`tools/check_docs.py:182-194`). Widening the scope (RC-5) and adding a currency check
  (RC-1) are a list edit and one more function, not a new tool.
- README's footer tied to plugin.json (`tools/check_docs.py:170-173`; DoD 10): the one currency rule that exists works.
  Extend it to the notes; do not replace it.
- The honesty of the admissions and of the three status words (README:62-66; DoD 8 says what is not mechanical). The
  fix is to date, list and retire them, never to drop them.
- The tally's refusals name where and why, exit 2 (`scripts/cost.py:225-240`), and the journey explains them
  (journey.md:379-382). A README block that ends in that exit is wrong; the exit itself is right.
- "How these runs were made" (journey.md:36-51): when, where, how, and the path redactions (`~/`, `<temp>`,
  `<store>`) — the specification any recorder must honour.
- `--kept` reads boards' documents already (`scripts/parts.py:1144-1152`), and the S3 file's `documents` carries
  checksums and page citations: the shape exists and is right (P62b). It needs a page, not a schema.
- `tests/test_orphans.py:27-36` already reads commands, skills and agents for routing; the two tests should share one
  list of "pages a user is routed by".

## 3. Changes

### Change 1 — The gate counts, and names, every recorded output behind the shipped version

- **kind** · story · **size** · S · **fixes** · K68 (the diagnosability half; Change 3 is the mechanism).
- **adds** · one function in `tools/check_docs.py`, `stale_outputs(text, root)`: parse the version in each
  `OUTPUT_NOTE`, compare it with `.claude-plugin/plugin.json`'s, return one sentence per block; `problems()` collects
  them and the summary line prints the count. Until Change 3 lands it reports and does not fail (44 today); after it,
  it fails. Optional, the PO's call: a note may carry `checked 0.8.1` after a person compared the lines, as USER-11
  did, so a re-run is not the only way to retire a stale mark. **removes** · nothing.
- **testable** · `tests/test_docs.py::test_an_output_recorded_on_an_older_version_is_named` on literal Markdown
  (`spark 0.6.0` against a plugin.json of `9.9.9`); a row in `tests/mutations/p104-docs.json`, "a stale output passes"
  (`if recorded != current` → `if False`).
- **diagnosable** · `journey.md: the output at line 81 was recorded on spark 0.7.0; the plugin is 0.8.1 — re-record it,
  or mark it checked`, and the summary `docs: 7 file(s), 44 output(s) recorded on an older version`.
- **proof** · `python3 tools/check_docs.py` on main prints that count (44, by the grep above); after Change 3's first
  re-recording it prints 0.

### Change 2 — The README's typed block ends where a shell can finish it, and the gate runs it

- **kind** · bug (documentation) · **size** · S · **fixes** · K69.
- **removes** · the `--tally` line from README:125-132 and the sentence at README:121-123 that explains its exit 2.
  **adds** · the block writes its needs file itself (a heredoc of the three needs at journey.md:214-220, into the
  project), keeps `--needs-set`, `--match`, `--pick`, `--requirements`, and is marked `<!-- runs: exit 0 -->`; one
  sentence after it: `/spark:build` runs the chain and `/spark:idea` marks the steps and ends with the tally, both
  shown in the recorded run (journey.md:188-377); typed in a shell, the tally says why it cannot count. The build
  stays out of the gate-run block: it needs `tsci` on the PATH and took 6 s here, and the suite should not depend on a
  toolchain. One line in `tools/check_docs.py:157`: the temp project becomes a child of the gate's scratch folder, so
  a block's `../file` lands inside what is removed and P172's leak count stays 0 — or the block keeps the file in the
  project.
- **testable** · the gate itself: `TheDocsTest.test_the_docs_name_only_what_is_there` runs the block at every suite
  run; the existing mutation "a failing example passes" covers the comparison. Verified by hand that the four lines
  exit 0 in an empty store on 0.8.1.
- **diagnosable** · today's sentence names the block and the codes (`the example `python3 … --needs-set …` exits 1,
  not 0`); add the last three lines of the block's output to it (`failed_examples` has `done.stdout` and `stderr` at
  `:160` and discards them), so the sentence also names why.
- **proof** · `python3 tools/check_docs.py` exits 0 with the README block marked; a reader typing the block gets exit 0
  at every line.

### Change 3 — Recorded outputs are re-recorded by one tool at each release, and drift fails a check

- **kind** · story · **size** · L (M for README and the journey's recorded run alone) · **fixes** · K68 (the
  mechanism); enables Change 4's recording; retires the "recording script" nobody has (journey.md:195).
- **adds** · one recorder. Two ways, the PO's choice. **(A) cog** (`pip install cogapp`; H: MIT, pure Python): `cog -r`
  rewrites the generated text in place, `cog --check` fails when a file would change, `--diff` shows the change (E the
  tool's pages, read 2026-10-10 — section 5). Each recorded block is wrapped `<!-- [[[cog record("parts.py --list")
  ]]] -->` … `<!-- [[[end]]] -->` (H: cog lets the markers sit inside any comment), three lines a reader of the rendered
  page does not see; `record()` lives in a small `tools/record.py` that gives each page one scratch project and store,
  runs the page's commands in order, redacts paths as journey.md:49-51 specifies and writes the
  `<!-- output: run DATE, spark VERSION -->` note from today's date and plugin.json. **(B) own**:
  `tools/record_docs.py` reusing `check_docs._fenced`, running each ```` ```sh ```` block in page order and replacing
  the ```` ```text ```` block under it; `--check` diffs. A gets the check and the diff for free and is the established
  tool for exactly this job — the technique the PO asked about on 2026-10-10, an existing library rather than own
  code; it adds a maintainer-side dependency and 3 lines per block (44 blocks). B adds about a hundred lines of own
  code with its own tests and mutation rows. Both need the same two pieces of work: the page's state (the 2026-10-08
  store with the drawer, `plant-alarm` and `button-light` — rebuilt from the `--drawer-set` files the Drawer section
  shows) and the redaction. The structural "not run" steps stay as prose by design. DoD 10 gains one line: a release
  re-records and `--check` passes. **removes** · the hand-pasting of 44 blocks at each release, which is the step that
  did not happen.
- **testable** · `cog --check docs/guide/*.md README.md` (or `record_docs.py --check`) in the release gate, not the
  suite (a build needs `tsci`, and the journey has several); a unit test on the redaction (`<temp>`, `<store>`, `~/`,
  the session id).
- **diagnosable** · `Checking docs/guide/journey.md ... (changed)` with the unified diff of the block — where and what;
  the note's date and version say when.
- **proof** · after a release bump, `grep -o 'spark 0\.[0-9]\.[0-9]' docs/guide/*.md | sort | uniq -c` shows one
  version, the shipped one, and `--check` exits 0.

### Change 4 — The own-board route is recorded on 0.8.1, and the three facts the scripts hold are written where the steps are

- **kind** · chore (docs) plus two small bugs · **size** · M · **fixes** · K70 (its runnable part), K72, K73; touches
  K24/P127 (#61).
- **adds**, on how-it-works.md "Your own dev board" (or on boards/README.md once P127 rewrites its steps): (1) how to
  find the variant — `gh api repos/espressif/arduino-esp32/contents/variants --jq '.[].name' | grep -i <vendor>` (409
  folders on 2026-10-10) — and that `vendor.arduino_variant` is the field `check_vendor_pins.py` reads; (2) how a
  board's documents are kept: `parts.py --keep <file> --url <url>` prints the entry, which goes under the board file's
  `documents` (the S3 file's shape; `member` for a zip member), and `parts.py --kept <word>` finds it from then on;
  (3) a recorded run of steps 1–4 on a copy of the S3 file under a new id: `boards.py --validate --project .` refusing
  the unedited copy (`id is 'firebeetle2-esp32s3' but the file is named …`, round-0-runner.md:18), then ok,
  `emit_footprint.py`, `check_vendor_pins.py` — and the sentence "this was not run for these docs"
  (how-it-works.md:155-156) deleted. The round-0 C6 file is not in the repository; its provenance table
  (round-0-runner.md:31-59) is enough to make it again, and the recording can use the S3 copy instead. Code:
  `scripts/check_vendor_pins.py:61-63` — when `gh` answers 404, say `vendor.arduino_variant names no folder under
  variants/ of espressif/arduino-esp32; list them with gh api …` (about 3 lines); `parts.py --fetch <board>` — either
  `record_home` also looks in `boards/` (so `--fetch firebeetle2-esp32s3` fetches the board's cited documents) or the
  refusal tells the truth: `firebeetle2-esp32s3 is a board; --fetch takes a part — keep a board's document with --keep
  <file> --url <url>`, exit 2. The second is the remove-before-add choice. **removes** · the "not run" sentence; the
  smart-bin steps once P127 lands.
- **testable** · a `<!-- runs: exit 1 -->` block for the validate refusal and a `<!-- runs: exit 0 -->` one after the
  id is fixed (both offline, no toolchain; not timed here); a unit test of `fetch_variant_header` with a fake `gh`
  returning 404 (the message names the field); a unit test that `--fetch` of a board id names it a board.
  `undated_outputs` covers the recorded outputs as today.
- **diagnosable** · the two refusals name the field and the next command; the recorded blocks carry their date and
  version.
- **proof** · items.md:50's: a second person makes a validated board file from the page alone without meeting G0.1 and
  G0.9; `parts.py --kept <a word of the board>` lists the kept document.

### Change 5 — The gate reads the pages agents follow

- **kind** · chore · **size** · S · **fixes** · K74 (the scope half); C-36's code half (#94, 2026-10-08).
- **adds** · `commands/*.md`, `skills/*/SKILL.md`, `agents/*.md` to `doc_files` (`tools/check_docs.py:30-33`) — 0
  problems today, so a pure guard; `tests/test_orphans.py:27-36` and `check_docs.doc_files` share one list.
  `boards/README.md` joins when P127 rewrites it (today it would fail twice: `config.py names no script`, and the
  folder tree at `:15` would need a bare ```` ``` ```` fence, since the gate reads every ```` ```text ```` block as an
  output). **removes** · the scope sentences at `docs/guide/developing.md:157` and
  `docs/2026-10-05-readme-design.md:92` are updated, not kept wrong.
- **testable** · `tests/test_docs.py::test_the_pages_agents_follow_are_read`: a temp root with `commands/x.md` naming
  `/spark:nothing` is reported; a mutation row "an agent page is not read" (`glob("*.md")` on commands → an empty
  list).
- **diagnosable** · the existing sentences already name page and cause (`idea.md: parts.py shows --frob, which its
  --help does not list`); the summary becomes `docs: 21 file(s), …`.
- **proof** · `python3 tools/check_docs.py` → `docs: 21 file(s), nothing named that is not there` (7 + 7 + 3 + 4).

### Change 6 — Density and long lines: one measured rule, or none

- **kind** · chore · **size** · S for the measure, M for the edits · **fixes** · K74 (the style half: E36b — DOC-39,
  DOC-47, DOC-48, DOC-51).
- **adds**, if the PO wants "about 120 lines" (`docs/2026-10-05-readme-design.md:39`) to be a rule and not a wish: the
  gate reports README's line count and, per page, the lines over 120 columns outside tables and code (README 10,
  idea.md 23, build.md 23 today), as a report line, not a failure; the jargon lines (idea.md:11, :14; research.md:99)
  are a documentation pass. **removes** · the README's retelling of the journey — "Two roads to a board"
  (README:111-158) retells what journey.md records; cutting to ~120 lines means pointing, not rewriting. The PO
  decides whether the rule exists; without it, this change is only the edits.
- **testable** · the measure, with a literal-Markdown test; the edits are not testable and should not pretend to be.
- **diagnosable** · `README.md: 231 lines (the design says about 120); 10 lines over 120 columns, the first at line
  70`.
- **proof** · the summary line's numbers before and after.

### Change 7 — One sentence says what spark has built, and where the rest of the library is listed

- **kind** · chore (docs) · **size** · S · **fixes** · K71.
- **adds** · one sentence in README's "What it shows on the example": two gadgets have been built from the library as
  documented — the example (an S3, an L9110S, a power inlet, two buttons) and the recorded run (a button and an LED);
  `parts.py --list` and `boards.py --list` print what else it holds, and one board builds. **removes** · nothing. A
  true menu is a function of the library (P157 #93: a function pass over 90 drawer entries) and belongs there, not in
  a page.
- **testable** · `missing_names` and `broken_links` as today; no new mechanism, by design.
- **diagnosable** · not applicable — a sentence.
- **proof** · USER-13's question answered from README alone.

## 4. What I could not check, and why

- The install path (`/plugin marketplace add`, `/plugin install`): needs Claude Code's own command; no script can run
  it. Its admission (README:102-103) stands until a person runs it once and dates the sentence.
- The conversations (`/spark:drawer`'s words to entries, `/spark:idea`'s questions, the research agents, the
  reviewers) and Wokwi: not runnable here; their admissions are structural (RC-3).
- Whether all 44 recorded blocks still match 0.8.1: I compared 5 (RC-1); the `--match`, `--pick` and `--audit` blocks
  need the 2026-10-08 drawer state, which I did not rebuild. Where the journey shows `~/.local/share/spark` for the
  2026-10-05 runs (journey.md:50) I did not check which store those ran in.
- Whether `cog`'s comment markers render acceptably on GitHub and in Claude Code's page reader (H: HTML comments are
  hidden in rendered Markdown; a raw reader sees three extra lines per block) — not tried.
- The time a full re-recording takes: one build was 6 s here; the journey holds several builds and a
  `tools.py --status` that depends on the machine — not measured.
- The PO's real store: never touched; every `--kept` output above is from the copy at `<scratch>/store`. One artefact
  of mine: `--match` in my scratch project listed `mystery-board (project)` because my K72 experiment left a board file
  there — not spark's output on a clean project.

## 5. Searches

- Web, once: `cog cogapp "--check" option Ned Batchelder inline code generation` · decision served: whether an existing
  tool re-records generated text in Markdown and checks drift (Change 3, option A) · used — confirmed `--check`
  ("check that the files would not change if run again … useful in continuous integration") and `--diff`:
  [cog.readthedocs.io — Running cog](https://cog.readthedocs.io/en/stable/running.html) and
  [nedbatchelder.com/code/cog](https://nedbatchelder.com/code/cog/index.html), read 2026-10-10.
- `gh api repos/espressif/arduino-esp32/contents/variants --jq '.[].name'` (a fetch, read-only, 2026-10-10) · decision:
  whether the variant folders are listable in one command (Change 4) · used — 409 names, 11 matching
  `dfrobot|firebeetle`.
- Read-only `gh issue view 94 --comments` (C-36 and its 2026-10-08 correction) and `gh pr view 122` (the release's two
  files) · used.
