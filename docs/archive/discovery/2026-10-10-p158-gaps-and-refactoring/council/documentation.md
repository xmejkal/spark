# Council — the documentation lens (P158 part 1)

Written 2026-10-10 by the documentation expert, against spark 0.8.1 (main `a8aa34d`, `git log -1`). The questions asked of
this lens: which findings are documentation faults and which are documentation that was right while the tool was wrong;
how the recorded outputs are kept current today and what would make them checkable; for each proposed change, what the
documents must say and where; and what a stranger — a person or an AI — reads first, and whether it tells them where a
mistake would show. The one user line the harness relayed (the PO, 2026-10-10, verbatim: *"maybe some new file formats
or synch libraries or techinques could be used from an existing library that does somwthing that would make the whole
store synch and global and loval and project store sync and rules and editor?"*) is answered where it touches this lens,
in §2 under "On the PO's question".

**How this was read and run.** I read `../catalogue.md`, the six diagnoses and their six verifications, the P100 folder
(`brief.md`, `items.md`, `risks-and-tests.md`, `verification.md`, `diary-round-0-board.md`, every council report),
`council/user-human.md` of this folder, irrigation's `DIARY.md` at the lines they cite, the store design
(`docs/2026-10-04-store-design.md`), the architecture notes (`docs/archive/2026-09-30-refactoring-architecture.md`), the README
design (`docs/2026-10-05-readme-design.md`), `scrum/README.md`'s Definition of Done, `docs/observations/INDEX.md` at the
rows the catalogue cites, and the pages themselves whole: `README.md`, `AGENTS.md`, the five guides, the seven command
pages, the three skills, the four agents, `boards/README.md`, `tools/check_docs.py`, `tests/test_docs.py`,
`tests/mutations/p104-docs.json`. Runs: a `git archive HEAD` of spark unpacked at `<scratch>/spark`, a copy of the PO's
store at `<scratch>/store`, and every spark command with `SPARK_HOME`, `HOME` and `TMPDIR` as three separate words
(`env | grep SPARK_HOME` under that prefix printed the scratch path once, first); `tools/check_docs.py` and the gate's
five per-page functions ran there, nothing else of spark did. The real store was neither run against nor written;
nothing was written under spark but this file. `gh` read-only: one `issue list --state all`, `issue view` of #11, #23,
#61, #94. One web search (§5). Tags: **E** a pointer or a run and what it printed; **H** a claim with its source; **D** a
decision (who, when); **—** unknown. Line numbers are spark's at `a8aa34d`. The PO's criteria (D, 2026-10-10): testable ·
diagnosable (where and why, to a person and to an agent) · simple (remove before add).

## 1. Findings

### DOCUMENTATION-1 · The 74 rows, sorted by what the documents did

claim: of the catalogue's 74 rows, 19 are documentation faults (the page is wrong, missing, stale or contradicts another
page), 16 are documentation that was right while the tool was wrong (the page says the fault, usually with its card), 12
are both halves, and 27 have no documentation dimension · tag: my reading, 2026-10-10, each row by the pointer below (E
for the pointers; the sorting is a judgement) · supports only: which rows a documentation change can close alone, which
it cannot, and where a page already carries the load a tool does not.

| class | rows | the pointer that decides the class, one per row |
| --- | --- | --- |
| **a documentation fault** (19) | K24 K25 K26 K32 K69 K71 K72 K73 K58 K46 K15 K68 K74 K57 K23 K31 K47 K48 K37 | K24 `docs/guide/how-it-works.md:145` says `boards/README.md` "has the schema"; `boards/README.md:55-58` holds the name rule only · K25/K26 no page names `PIN_ROLES` or the three pad forms (`council/round-0-runner.md:66`, `:71`) · K32 `boards/README.md:97` "costs only the silkscreen labels" · K69 `README.md:121-123` explains its own block's exit 2 · K71 the menu is in `scrum/PRODUCT_BACKLOG.md:1569`, no persona page · K72/K73 `how-it-works.md:160-173` names no listing and no `documents` entry · K58 six literal `~/.local/share/spark` paths in `agents/` and `commands/` (DOCUMENTATION-11) · K46 three pages, two orders for `init` (DOCUMENTATION-10) · K15 `docs/2026-10-04-store-design.md:120` "all private" against `store.py:96` · K68 44 version markers, none 0.8.x (DOCUMENTATION-2) · K74 `tools/check_docs.py:30-33` · K57 `--describe` wrong in three places, the document agents are told to read first (`docs/guide/agents.md:103-104`; `scripts/parts.py:1764` vs `:1496-1499`, `:1521-1523` — the chain diagnosis's E, not re-run here) · K23 `pad_aliases` is documented in no spark page (grep `pad_aliases docs commands boards/README.md` → nothing, 2026-10-10); the bin's CLAUDE.md calls it the bridge · K31 no page says a board record may state `function`; `commands/drawer.md:28` documents the entry's · K47 `scripts/parts.py:97` "no build can place it" is true of two facts of five (chain diagnosis RC-4) · K48 `parts.py:1631` promises "builds with it" · K37 `agents/parts-researcher.md:76-104` and `skills/spark-design/references/part-data.md` name no `function` or `simulation`; `commands/research.md:83-85` ends at `--validate` |
| **the documentation was right, the tool wrong** (16) | K20 K21 K45 K35 K55 K30 K14 K3 K19 K65 K66 K42 K70 K56 K43 K67 | K20 `commands/build.md:72-74`, `docs/guide/journey.md:706-709`, `agents.md:413-416` all say `dist/` is the regenerated board, with P110 (#44) · K21 `README.md:123`, `journey.md:379-382`, `commands.md:121-123` say the tally exits 2 and why · K45 `how-it-works.md:37` "It counts as a problem, so the run exits 1 even when the board builds" · K35 `commands/idea.md:24-25` "there is no removing or renaming a need yet" · K55 `agents.md:258-261` say `--show --json` carries the record alone and `data.questions`, with P124 · K30 `how-it-works.md:175-178` names the XIAO's missing geometry and that `--for-fab` answers ok, with P121 · K14 `agents.md:123` names "the header cache" as a write (its place unsaid) · K3 `idea.md:96-98` documents the hand route; `drawer.md:43` names `entry` · K19 `how-it-works.md:194-196`, `build.md:76-78` say the digest covers "some of the facts" (F30, `5670ac9`) · K65 `research.md:13-15` defines `verified: true` as "the maker's own text at a cited page"; `--show` is looser (#17) · K66 `journey.md:911-914` "Not yet. No command does this yet"; `README.md:77` · K42 `idea.md:63-65` sends a gap to research and says nothing stands in for G · K70 the admissions are true by the convention's own definition (`README.md:62-64` "runs made for these docs") · K56 `README.md:182-188` promises the terminal persona; the design says agents first (store design §6.4, D the PO 2026-10-04) — the page states both truthfully · K43 the store design's §2 table documents seven ways in and `scrum/STORY_MAP.md` marks them not designed · K67 `README.md:75` "Not built yet: checking the firmware on a Mac against it (P59, P74)" |
| **both** (12) | K1 K2 K29 K33 K34 K36 K40 K22 K53 K64 K63 K49 | K1/K2 `agents.md:86` tells an agent to use a scratch `SPARK_HOME`; no page says a missing or empty value is a silent empty store (the shape of #101 and F5) · K29 `scripts/needs.py:513-516` sends the person to a five-step page round 0 ran with ten gaps · K33 `research.md:24` "a match is the answer"; `parts.py:1334`'s docstring says every word; the output says "Research it" · K34 `idea.md:50-51` "your call" with no rule for an all-`[other words]` list; the pick records nothing · K36 `idea.md:67-74` warns of a *record* with no function, never an *entry*; 91 of 110 entries are such · K40 every page names `requirements.json` (`build.md:48`, `:64`; `README.md:148`; `idea.md:134`); irrigation's older name; the writer does not look · K22 `boards/README.md:55-58` and `how-it-works.md:165-168` state the name rule for keys only; the labels' rule is neither stated nor enforced · K53 `developing.md:52-54` "must report every one caught"; `tools/mutate.py` scores a non-importing file as caught · K64 the design's §6.1 "refactor first" (D the PO, 2026-10-04) against `parts.py`'s 2,214 lines · K63 `idea.md:13-15` puts `--step S` before the folder exists, read literally (chain verifier RC-7) · K49 `boards/README.md:21` "THE one place it is chosen" against `idea.md:132-133` "the board follows the pick" (chain verifier RC-6) |
| **no documentation dimension** (27) | K4–K13, K16–K18, K27, K28, K38, K39, K41, K44, K50–K52, K54, K59–K62 | store internals, locks, encodings, the cap, a `?` in a generated file — nothing a page says or should have said |

What the sorting carries: a documentation change alone closes the 19; for the 16 the page is already doing the tool's
job and the sentence must leave when the card closes (DOCUMENTATION-6 says nothing watches that); for the 12 the page and
the code change together or the page stays wrong a second time.

### DOCUMENTATION-2 · Recorded outputs are kept current by a hand paste that did not happen at three releases; the gate proves provenance and never currency

claim: every one of the 42 recorded output blocks carries the note the gate demands and none is on the shipped version;
nothing re-records, and the release step is a two-line edit · tag: E · pointers: `grep -c '^```text'` per page → agents 2,
commands 1, developing 5, journey 34, README 0, AGENTS 0 (42), and `grep -c '<!-- output: run'` → the same four counts
(42 of 42 noted; my runs, 2026-10-10); `grep -o 'spark 0\.[0-9]\.[0-9]' docs/guide/*.md README.md | sort | uniq -c` →
0.6.0: agents 2, commands 1, developing 1, journey 12; 0.7.0: developing 4, journey 24; 0.8.x: 0 (my run);
`tools/check_docs.py:20` (`OUTPUT_NOTE`), `:142-145` (the only test on a note is its shape), `:148-167`
(`failed_examples` compares an exit code, never output, for blocks marked `runs:` — three exist: `agents.md:45`, `:336`,
`journey.md:636`, all listings), `:170-173` (the version test is `"v0.8.1" in readme`); `python3 tools/check_docs.py` on
the archive copy → `docs: 7 file(s), nothing named that is not there`, exit 0, 5.5 s wall (my run); the three release
commits — `87daf54` (0.7.0: `plugin.json`, `README.md`, 2 lines), `36d6998` (0.8.0: those two and `scrum/README.md`),
`1fc0909` (0.8.1: 2 files, 2 lines) — `git show --stat`, my run; `tools/check_commit.py` holds no line matching
`version|plugin.json|check_docs|release` (my grep → nothing); `scrum/README.md:232-234` (DoD 8: "Nothing mechanical
checks it"), `:236-242` (DoD 10, prose); `journey.md:195` "These commands ran from a recording script" · supports only:
that the pages' currency has no mechanism; not that any block is wrong — where compared (five blocks by the docs
diagnostician, three by the P100 user lens, the 17-line build block by the user-human lens; all theirs, E), the lines match
0.8.1 in form. I compared none myself (§3).

### DOCUMENTATION-3 · The recorder exists, untracked, bound to a worktree that is gone, and it never wrote a page

claim: the "recording script" `journey.md:195` names is on disk under `.superpowers/` (gitignored), 300 lines in three
files, with its plugin path and scratch folder hard-coded, and nothing in it writes into a page — the paste was manual ·
tag: E · pointers: `git ls-files .superpowers | wc -l` → 0; `wc -l` → `record.sh` 102, `journey/record-journey.sh` 176,
`journey/blocks.py` 22 (my runs, read-only); `record.sh:4-7` and `record-journey.sh:8-12` set a session's scratchpad
path, `~/Development/spark-p97/scripts` (a worktree that no longer exists) and the bin's `node_modules/.bin`; no `sed` or
`write_text` in either script (the docs verifier's M1; the hard-coded paths re-read by me) · supports only: what the docs
diagnosis's Change 3 should start from — promote or delete what exists before writing a third recorder.

### DOCUMENTATION-4 · The output convention is a fence tag, and it misreads in both directions

claim: the gate takes every ```` ```text ```` block as a recorded output and sees no output in any other fence, so a folder
tree is "an undated output" and a pasted chain run in a bare fence is invisible · tag: E · pointers: the five per-page
functions over `boards/README.md` → `README.md: the output at line 15 has no <!-- output: run DATE, spark VERSION -->
above it` (the folder tree at `boards/README.md:15-24`) and `README.md: config.py names no script` (my run on the
archive copy); `commands/build.md:80-90` — the chain's stage lines (`[ok  ] build  19 trace(s), 0 errors, tsci 0.0.2600`)
in a bare ```` ``` ```` fence with no note, which no widening of `doc_files` would catch (`check_docs.py:131-138`,
`_fenced(text, "text")`); the convention is stated nowhere — `developing.md:165` says "paste an output without the date
and version" and names no fence tag; `GLOSSARY.md` has no entry for it (`grep -n -i 'output: run|recorded output'` →
nothing, my run) · supports only: that the convention needs a sentence and a second trigger (the note, not the tag), and
that `build.md:80-90` is a second copy of `journey.md:683-702` with an older `tsci` and no date.

### DOCUMENTATION-5 · The gate names a page by its file name, so widening it makes three `SKILL.md`s and two `README.md`s one name

claim: `problems()` prefixes every sentence with `path.name`, which already reads `README.md:` for `boards/README.md` ·
tag: E · pointers: `tools/check_docs.py:187` (`"%s: %s" % (path.name, sentence)`); my run above printed `README.md: config.py
names no script` for `boards/README.md` · supports only: that Change 5 must change the prefix to `path.relative_to(root)`
in the same commit, or a failure stops naming where (the docs verifier's M7, now my E).

### DOCUMENTATION-6 · 84 links to 37 cards, no check that a named card is still open; one page cites a closed card as the plan for a gap the code still has

claim: the pages name spark's issues 84 times (37 distinct cards); 5 of those cards are closed; 4 are cited as history
(P97 #18, P167 #105, P168 #106, P172 #112 — the item that built the thing) and 1 as the plan for an open gap:
`docs/guide/agents.md:248` and `:295` name P43 (#11) for `check_vendor_pins.py --json`'s bare list, its `mismatch`
status and the differing `--json` shapes; P43 closed 2026-10-06 — "merged into P118 (#52) … the status words and shapes
… stay parked" — and `scripts/check_vendor_pins.py:147` still prints `mismatch` · tag: E · pointers: my join of
`gh issue list --state all --limit 400` (102 issues: 82 open, 20 closed) against `xmejkal/spark/issues/(\d+)` in README,
AGENTS, the guides, commands, skills, agents and `boards/README.md` (2026-10-10, read-only); `gh issue view 11 --comments`
(the closing comment, read-only); `check_vendor_pins.py:147`, `:181-184` · supports only: today's links; an agent reading
`agents.md:295` is told the shape difference is a card's work when it is parked under none, and no mechanism would have
said so — the pre-push gate already reads the board through `gh` (`tools/check_backlog.py`, `developing.md:76-98`), so
the look is cheap.

### DOCUMENTATION-7 · "Not run" is said 22 times, in no list, with no date and no kind — and one admission is the agents' own route

claim: 22 admissions that a step was not run for the docs sit in README, the guides and `agents.md`, each free prose; the
one the earlier counts missed is `agents.md:29`: "following a command page outside Claude Code was not tried for these
docs" — the route `AGENTS.md` sends every non-Claude AI down · tag: E · pointers: my grep over `README.md`,
`docs/guide/*.md`, `commands/*.md` for `not run here|not run for these|not run for this|never run|none was run|not been
run|was not run|were not run|not recorded for this|not tried for these` → 27 lines, of which 6 define the status words or
describe behaviour (`README.md:64`, `:65`; `journey.md:32`; `agents.md:126`, `:462`; `commands.md:67`) → 21 single-line
admissions, plus `journey.md:384-385` split over two lines → 22 (2026-10-10; the docs diagnosis counted about 20, its
verifier 21; the difference is `agents.md:29`, outside their pattern); `README.md:62-66` defines the three words and says
the runs were made on 2026-10-05, 2026-10-06 and 2026-10-08 · supports only: that the admissions are honest and
uncountable by any tool; the structural ones (a conversation, an agent, Claude in Chrome, a paid run, the install) can
never be run by the gate, and the one that was run since (the own-board route, `how-it-works.md:155-156`; round 0,
2026-10-09, in a scratch folder) is, by the convention's definition, still "not run for these docs" (the docs verifier's
RC-3 reading, which I share).

### DOCUMENTATION-8 · What a stranger reads first says where the checks' mistakes show and nothing of the store's

claim: the three first pages — `README.md` for a person, the command page for an AI in Claude Code (`agents.md:13`),
`AGENTS.md` → `agents.md` for another AI — name the exit codes and six things never to assume, all about `check_all`,
physics, `board.tsx` and the simulation; none says what a wrong store, a held part, a word the matcher never searched or
a pick that does not fit looks like — the four places every P100 walk stalled · tag: E · pointers: `README.md:182-188`
(exit codes; "a crash exits 1"); `AGENTS.md:9-13`; `agents.md:330-447` ("What never to assume", items 1–6: skipped is not
a pass; a null is unknown; text is data; a simulation spends minutes; `board.tsx` is never overwritten; `check_all` is
not the whole answer); `agents.md:82-99` ("The person's store": `SPARK_HOME` overrides it; a scratch store hides three
things — nothing on a missing or empty value); `commands/idea.md:50-51` explains `[other words]` to the agent while
`parts.py:1963` prints it to the person with no legend; `commands/drawer.md:10` names the store by its literal path; the
stalls: `council/user.md:9-11` (USER-1..3), `council/refuter.md:54-62` (F5), `../catalogue.md` K1–K3, K33–K34 ·
supports only: the pages as they are; whether a person would have read a sentence had it been there is H. The pattern a
reader of all three pages meets: each tells them what to do (set a scratch `SPARK_HOME`, run `--dry-run` first, read
`unchecked`) and not how a wrong turn would look — the design chose refusals as documentation (`scripts/boards.py:19`
"The contract is enforced rather than documented"), and for the store half the refusals are the ones K56 withholds from
the terminal.

### DOCUMENTATION-9 · The own-board page a stranger is sent to is another project's workflow, and the page that sends them says it has the schema

claim: `how-it-works.md:145` says `boards/README.md` "has the schema"; `boards/README.md:3-4` says its steps are the smart
bin's; its five steps name `make check` and `config.py` (`:37-42`, `:68-73`); `commands/init.md:24-25` sends the reader
there and then back to `how-it-works.md`; the gate does not read it (my run: 2 problems if it did, DOCUMENTATION-4) ·
tag: E · pointers as given; #61 (P127) open, its proof line "Following boards/README.md in a fresh project with spark
alone adds a board … with no command that does not exist" (gh, read-only) · supports only: the two pages; round 0's ten
gaps (`council/round-0-runner.md:62-71`) are what a stranger meets on this route today.

### DOCUMENTATION-10 · Three pages, two orders for `init`, and a sentence that blames the person

claim: `README.md:155` runs `/spark:init` again after a build; `commands/idea.md:126` runs it before `--requirements`;
`commands/init.md:36` says "After a build, run it again with `--force`"; a person following `idea.md` gets two
could-not-run checks and the sentence "which is what `/spark:init` writes and where they have stayed"
(`scripts/compare_design.py:254-259`), one following README gets one · tag: E · pointers as given; chain diagnosis RC-1
and its verifier (holds; MC-6: the derived half needs no build) · supports only: the documented sequences; a documentation
fix (one order on three pages) is possible today, and MC-6 would remove the step the three pages describe.

### DOCUMENTATION-11 · Six literal store paths in the pages agents follow, against the card that forbids them

claim: `agents/parts-researcher.md:53`, `:58`; `commands/setup.md:11`, `:51`; `commands/drawer.md:10`;
`commands/research.md:105` spell `~/.local/share/spark/…`; #23 (P92)'s proof is "`grep '\.local/share' agents commands`
prints nothing" · tag: E · pointers: my grep (2026-10-10); `gh issue view 23` (open, read-only) · supports only: the six
hits; `README.md:197` and `how-it-works.md:182-183` name the path too, as the person-facing statement the agent pages
could point at — a store that moves (P178) changes four pages and six sentences today.

### DOCUMENTATION-12 · The owed-facts list is restated in prose in five places, and the restatements disagree with the code at one row

claim: `journey.md:401-402` and `:450`, `idea.md:47-50` and `:107-110`, `build.md:140-145` each restate which owed facts
stop what; `parts.py:1631` says a catalog record "builds with it"; the chain's parts stage refuses a record owing
`pin_order_proof` as a contract failure (chain verifier RC-4, `<scratch>/proj-proof`, E theirs) · tag: E · supports only:
that the pages copy a table that does not exist (chain diagnosis C4) and will drift again when it changes; the docs
verifier's point that `journey.md:450` is right for `--requirements` and wrong for "nothing stops" stands.

### DOCUMENTATION-13 · Two true-in-part sentences the changes propose to delete

claim: `boards/README.md:96-97` ("a stand-in costs only the silkscreen labels") and `boards/firebeetle2-esp32s3.json:104`
("a superset of every pin this board brings out … names its pins by raw GPIO number") are true of GPIOs (24 of 24 on the
devkit) and false of two names (`TX`, `RX`); the firmware diagnosis's C1 and C6 remove them · tag: E (the firmware
verifier's registry read, `@wokwi/diagram-lint` 0.1.1; M9) · supports only: amend, not delete; and one more: the S3
record's own `//pad_aliases` comment (`:97`) states K23's fault exactly ("they do not connect — silently") — a comment is
documentation that no writer read (board-records verifier RC-1).

### DOCUMENTATION-14 · README has no recorded output, against its own design

claim: `README.md` holds 0 ```` ```text ```` blocks (my grep); its design asked for "Install and a first run: three
commands, with output from a real run" (`docs/2026-10-05-readme-design.md:49`); the one typed block (`README.md:125-132`)
is outside the gate (no `runs:` mark; `check_docs.py:152-154`) and ends in an exit 2 the page predicts (`:121-123`) · tag:
E · supports only: the page against its spec; the docs verifier reproduced lines 1–5 exit 0, line 6 exit 2 (E theirs).

### DOCUMENTATION-15 · The 2026-10-05 recordings show the real store's path, so their state cannot be rebuilt

claim: `journey.md:50` says the scratch store is shown as `<store>` "(as `~/.local/share/spark` in the 2026-10-05 runs)",
and the recorded `tools.py --status` block (`journey.md:599`) prints `personal: ~/.local/share/spark/tools.json` — the
2026-10-05 blocks (16 of 42, the 0.6.0 ones) ran against the PO's own store · tag: E (the page's own words) · supports
only: that a re-recording of those blocks is a re-recording against a store that has changed since; a recorder must say
per block which state it needs (DOCUMENTATION-2), and for these the honest note is "recorded-only".

### DOCUMENTATION-16 · The agent pages pass the gate's functions today, so the guard costs nothing

claim: the five per-page functions (`missing_names`, `missing_flags`, `undated_outputs`, `broken_links`,
`personal_paths`) over the 14 pages in `commands/`, `skills/*/SKILL.md` and `agents/` report 0 problems · tag: E (my run
on the archive copy, 2026-10-10: `agent pages: 14, problems: 0`) · supports only: that widening `doc_files` is a pure
guard; its value is the day a command page shows a flag `--help` lacks.

### DOCUMENTATION-17 · The recorder's pairing rule fails on a fifth of the blocks

claim: 10 of the 42 recorded blocks do not sit directly under a ```` ```sh ```` block (prose or a second output between):
`agents.md:147`; `developing.md:103`, `:121`, `:126`, `:140`, `:151`; `journey.md:439`, `:466`, `:495`, `:507` · tag: E (my
walk over the pages, 2026-10-10; the docs verifier's looser rule counted 8 — mine counts prose between a command and its
output as unpaired, which is what a recorder that pairs by adjacency would meet) · supports only: that re-recording needs
an explicit per-block binding, not adjacency; `developing.md:100` already calls its block "a dated record, not today's
output", and `developing.md:120-153` reads the live GitHub boards (never equal twice).

### DOCUMENTATION-18 · Process jargon in the persona pages is small and one instance is on the page every `/spark:idea` run reads

claim: `scrum/` or `§<n>` appears in `README.md` once, `commands.md` once, `developing.md` 3 times, `journey.md` twice,
`commands/idea.md` once — `idea.md:11`: "(docs/2026-10-04-store-design.md §8 S and M)" · tag: E (my grep, 2026-10-10) ·
supports only: that the style half of K74 is a short pass; `developing.md`'s three are its subject.

### DOCUMENTATION-19 · The machine-readable documentation agents are told to trust first is wrong in three places

claim: `agents.md:103-104` says "read `parts.py --describe --json` before calling `parts.py`"; its effects column omits
`not_shelved`/`written` for `--drawer-set`/`--drawer-import`, declares no effect for `--tally` though it reads
transcripts, and `tools.py` has no `--json` (K57) · tag: E (the catalogue's pointers `scripts/parts.py:1764` vs
`:1496-1499`, `:1521-1523`; `grep -n -- --json scripts/tools.py` → nothing; not re-run here) · supports only: that the
self-description (§6.4.3 "a test fails if they differ") is tested for its arguments and not its effects.

### DOCUMENTATION-20 · On the PO's question, for the documents: two existing tools do the re-record-and-check job, and both leave the hard parts to spark

claim: `mdsh` (a Rust crate) runs `$ command` lines in Markdown, writes the output under them and fails with `--frozen`
when the output would change; `cog` (Python, MIT) rewrites marked regions in place and fails with `--check` — the docs
diagnosis's option A · tag: E for mdsh's `--frozen` (its documentation page, read 2026-10-10, §5); H for cog (the docs
diagnosis's reading of its pages; not opened here) · supports only: that the diff-and-check wrapper is available ready
made; what neither supplies is spark's: the state each block needs (a drawer, two projects, the 2026-10-08 store), the
redaction `journey.md:49-51` specifies (`~/`, `<temp>`, `<store>`, session ids, the `tsci` line), and the class of each
block (re-recordable, or dated history — DOCUMENTATION-15, -17). Adopting mdsh also rewrites the convention on every block
(`$ cmd` lines instead of ```` ```sh ```` + ```` ```text ````); cog keeps it and adds three comment lines per block, which
an agent reading the raw page sees.

## 2. The proposed changes, judged from this lens

For each change in the six diagnoses, by title: keep · change (how) · drop (why), and — the question asked — what the
documents must say and where. The verifiers' corrections are taken where they change the shape (named). Sizes are the
diagnoses' (H, theirs).

### docs-and-recorded-outputs

- **Change 1 · The gate counts, and names, every recorded output behind the shipped version** — keep as a report line,
  never a failing check (the verifier: a patch that changes no output would raise 44 false alarms; `developing.md:103` is
  history by its own words). Docs must say, in `developing.md` "The docs name only what is there": that the gate reports
  how many outputs predate the shipped version and that the number is provenance, not a verdict.
- **Change 2 · The README's typed block ends where a shell can finish it, and the gate runs it** — keep, with the
  verifier's M8 (a recorded ```` ```text ```` output under it, with its note, and the tally's honest exit 2 shown as a
  second recorded block beside `README.md:121-123`'s sentence). Docs: `README.md:117-123` loses "The block leaves them
  out, so its last line exits 2" and gains the output; `README.md:119-120`'s "outside any repository, here
  `../button-needs.json`" changes with the heredoc (the verifier's (a)). This is also DOCUMENTATION-14's fix.
- **Change 3 · Recorded outputs are re-recorded by one tool at each release, and drift fails a check** — keep the
  direction; change the shape: (i) promote or delete the untracked recorder first (DOCUMENTATION-3; remove before add);
  (ii) bind each block to its command and its state explicitly, in the note or a marker (DOCUMENTATION-17: 10 blocks are
  not adjacent to a command); (iii) classify every block re-recordable or recorded-only (DOCUMENTATION-15: the 2026-10-05
  blocks ran on the real store; `developing.md:120-153` reads live boards); (iv) run the `--check` in
  `tools/check_commit.py` when the commit changes `plugin.json`'s version — "the release gate" names nothing that exists
  (my grep; the verifier's M4). Docs: `developing.md` gains the recorder's command, the two block classes and the note's
  grammar; `journey.md:36-51` "How these runs were made" becomes the recorder's specification and loses `:195`'s
  "recording script" sentence once the script is tracked; `scrum/README.md` DoD 10 gains "a release re-records and
  `--check` passes". Tool choice (DOCUMENTATION-20) is the PO's (§4).
- **Change 4 · The own-board route is recorded on 0.8.1, and the three facts the scripts hold are written where the
  steps are** — keep; cut the half already on the page (`how-it-works.md:172` names `vendor.arduino_variant`); the variant
  listing (`gh api … | grep -i <vendor>`), `--keep <file> --url <url>` for a board's documents and `--kept <word>` are the
  three sentences round 0 lacked (G0.1, G0.9). Docs: `how-it-works.md:153-178` "Your own dev board" carries the sentences
  and two recorded blocks (the `--validate` refusal on an unedited copy, exit 1; then ok), both offline and fit for
  `runs:`; the `check_vendor_pins.py` step stays recorded-only (network, `gh` login, and the live write — board-records
  C7). The "not run" sentence at `:155-156` goes only with the recorded blocks beside it (the convention retires it, not a
  date). `boards/README.md:35-73` is P127's (#61): rewrite its steps as spark's, or make it the schema page (BR-C3) and
  send every step to `how-it-works.md`.
- **Change 5 · The gate reads the pages agents follow** — keep; S; add DOCUMENTATION-5 (name a page by its path) in the
  same commit, and share one list with `tests/test_orphans.py::routes()` minus its sibling-project Makefiles
  (`test_orphans.py:32-35`, which must not enter `doc_files`). Docs: `developing.md:157` and
  `docs/2026-10-05-readme-design.md:92` say the new scope; `developing.md`'s summary line reads `docs: 21 file(s)`.
  `boards/README.md` joins when P127 lands (2 problems today, one a false positive — DOCUMENTATION-4).
- **Change 6 · Density and long lines: one measured rule, or none** — the PO's call; from this lens README's long lines
  are table rows (the verifier), the real figure is 231 lines against a design of about 120 (`readme-design.md:39`), and
  the cut that also closes K69 is to make "Two roads to a board" (`README.md:111-158`) point at the journey instead of
  retelling it — against the design's §3 item 3, which wants typed commands with output in README. One shape for that
  section, decided once, serves Changes 2 and 6 together (the verifier's point).
- **Change 7 · One sentence says what spark has built, and where the rest of the library is listed** — keep, with the
  per-store fact (the library holds 8 records; `parts.py --list` adds the person's shelf — 13 on the PO's copy). Docs:
  `README.md:37-51` "What it shows on the example".

### store-levels-and-holds

- **C1 · A `SPARK_HOME` that names nothing is refused, and every answer names its store** — keep, plus the verifier's M1
  (an empty value). Docs must say, in `agents.md:82-99` "The person's store": the refusal's sentence, that an empty or
  missing value is refused rather than becoming a store, and that every write prints `in store <path>`; in
  `commands/drawer.md:10`, replace the literal path with "your store ([how it works](../../../../discovery/2026-10-10-p158-gaps-and-refactoring/council/…#your-store))" (DOCUMENTATION-11).
- **C2 · The real store is written only on purpose (P164)** — keep as the PO's decision; whichever mechanism, the
  refusal's text is the document a stranger reads, so it names the rule and both ways out. Docs: `agents.md` "The
  person's store" and `how-it-works.md` "Your store" say the rule; if `SPARK_STORE=real` is chosen, `README.md:182-188`
  "Without Claude Code" says it before the first typed command.
- **C3 · One lock beside the data** — keep; docs: `agents.md:88-89` says the lock is held "from its plan to its last
  byte" — add where the lock file lives (the store) and that a writer with no lock refuses; `how-it-works.md` "Your store"
  lists `.lock`.
- **C4 · An operation's writes land all or none** — change to the verifier's smaller form (record what landed; say it on
  a stop). Docs: the sentence `written before the stop: …; the same command, retried, finishes it` belongs in
  `agents.md`'s envelope section as a named `unchecked` shape, so an agent knows a retry is safe.
- **C5 · A project is its folder** — keep the spelling half; docs: `how-it-works.md` "Your store" says a project is listed
  by its folder (and, with the id, by `.spark/project.json`'s id); `agents.md:117` (`init_project.py` writes "the store's
  projects list") names what identifies a project.
- **C6 · Holds are seen in the listing and released by an operation** — keep; decide the verifier's M2 first. Docs:
  `commands/idea.md:96-98` and `GLOSSARY.md`'s "Pick, and reserve" replace the hand-written-file procedure with
  `--release`; `commands/drawer.md:15-21` "See it" says the listing prints the key and `held by …`; `commands.md:84-103`
  follows. Under M2 (i) — derived holds — the pages say instead that a hold is the other project's pick and is freed by
  changing that pick.
- **C7 · Reads refuse what writes refuse** — keep; docs: the conflict-copy sentence names the file and the fix; one line
  in `how-it-works.md` "Your store": a sync client's conflict copy is refused by name, not counted.
- **C8 · One reader for a store file; no store problem is a traceback** — keep with the verifier's caution; docs:
  `agents.md:292-328` "Not yet true everywhere" item 2 ("a crash exits 1") shrinks by the inputs this closes — the list
  there is the one place that documents the crash class, so it is edited in the same change or it misleads again.
- **C9 · `--fetch` names every URL it could not keep** — keep; docs: `commands/research.md:44-53` and
  `agents/parts-researcher.md:52-55` say what exit 1 means after `--fetch` (a URL not kept, named) — neither asserts exit
  0 today (the verifier), so the sentence is an addition, not a correction.
- **C10 · One layer, one count** — keep; no page states either count; nothing to change.
- **C11 · A record has one home that is the store** — keep the direction, slow the shelving half (the verifier: four
  placeholder-footprint records would reach the shelf). Docs: `commands/research.md:99-100` ("`--promote` copies a verified
  record into the plugin's library, and the next project finds it") and `README.md:108-109`, `journey.md:552-553`,
  `agents.md:126` (the `--promote` warning) all describe the plugin-folder target — five sentences change together; the
  `--promote` dry run's own line says "the plugin's own library, which the next update replaces" until the branch goes;
  `agents/datasheet-reader.md:5` loses `Write, Edit` and its "Finish" section (`:49-54`) says it writes through
  `--fact-set`; the six literal paths (DOCUMENTATION-11) go in the same PR with #23's grep as a test.
- **C12 · The spec and the code say the same about privacy** — keep as a chore; take the verifier's correction (do not
  shrink §5.1; `sources` are document bytes the spec promises twice not to publish). Docs: `agents.md:89-92` lists the
  private places — it must match `PRIVATE` after the change; a test that reads the page's list against the tuple is the
  suite's own style (`test_docs.py`).
- **C13 · The `built` line vouches for what the chain reads** — keep only the sentence half (`note_built` returns a
  sentence; `check_spine` prints it); the digest half waits for a reader (the verifier's M3). Docs: `how-it-works.md:194-196`
  and `build.md:76-78` already say "some of the facts" — they change only when the digest does.

### board-records

- **C1 · A `header_order` label tscircuit would read as a pin number is refused** — keep, with M6 (keys too). Docs: the
  one sentence proposed for `boards/README.md`'s schema ("a pad label is what is printed; it may not be a bare number …")
  and the same under `how-it-works.md:164-168`'s name rule, which today covers keys only (K22's doc half).
- **C2 · `pad_aliases` reaches the footprint** — keep with the verifier's rule (an alias target that is also a key maps to
  the same GPIO). Docs: `pad_aliases` is documented in no spark page (DOCUMENTATION-1, K23) — the schema page (C3) gets
  its one paragraph: what it bridges (the vendor's key, the printed label), who reads it after the change (the footprint,
  the validator, the firmware comment, the converter). The record's `//pad_aliases` comment (`:97`) is rewritten to say the
  footprint now carries both names.
- **C3 · The `physical` schema is written where it is enforced, and a key nobody reads is refused** — keep; it is the
  documentation change of this council: a `## The board file, key by key` section generated or checked from `PHYSICAL_KEYS`
  and `PIN_ROLES` (with their one-line meanings, `boards.py:95-107`), so the list in prose cannot drift from the list in
  code (the mechanism DOCUMENTATION-12 and -19 lack). Docs: `boards/README.md` (the schema page), `how-it-works.md:145`
  ("has the schema" becomes true), `commands/init.md:24-25` (the pointer); take M3 (five unread keys) and the bin's `make
  check` dependency on the library file.
- **C4 · `emit_footprint.py --json` prints JSON on every path** — keep the simpler variant; docs: `agents.md:249`'s row
  for `emit_footprint.py` stays true either way; `agents.md:263-265` lists it among the scripts that take `--json` — add
  "with `-o`" if the could-not-run variant is chosen.
- **C5 · The footprint's header says what the drawing states** — keep; no page quotes the header.
- **C6 · One comment-key rule for every walker** — keep; docs: the schema page states the `//` convention (beside a keyed
  table, or inside a dict read by field — the verifier's reading of the shipped file).
- **C7 · The vendor-header cache lives in the store** — keep; docs: `agents.md:123` ("`check_vendor_pins.py` without
  `--offline`: the header cache") names where; `how-it-works.md:79-83` (vendor-truth "reads the plugin's cached copy")
  and "Your store" list `cache/`; the bin's `Makefile:220` `--offline` run must still find a header — say the fallback
  order on the page.
- **C8 · A board record from a drawer entry** — keep as the PO's first fix (D8). Docs: it replaces the five-step hand route
  (`how-it-works.md:160-173`) with one command and a list of owed fields naming the document to read each from — the route
  then has a recorded block; `commands/research.md` gains the board flow (#99's "no flow for a BOARD"); `commands/idea.md:
  99-101`'s "a board needs a board file" sentence names the command.
- **C9 · A board says every stop it stops at** — keep; change both spellings (the verifier's M5). Docs: `README.md:25-29`,
  `journey.md:181-183`, `how-it-works.md:175-178`, `commands/init.md:20-22`, `idea.md:146-147` all carry "stops at the
  footprint stage (P121)" — six prose copies of one code sentence; when the sentence becomes a list, the pages quote the
  command's output once (the journey) and point, rather than restate.
- **C10 · A board's `function` is a documented, validated key** — keep with M4 (the drawer slot exists). Docs: the schema
  page says a board record may state what it gives for free, in the 13 verbs, and `commands/drawer.md:28` says the entry's
  `function` is the owned piece's — two slots, one sentence each on which fact goes where.
- **C11 · `pins` are checked against the stand-in's pin list** — change per the firmware verifier (the library boards'
  "absent" pins are names). Docs: DOCUMENTATION-13 — amend `boards/README.md:93-97` and the S3 record's
  `//wokwi_part_type` note, do not delete them; document `wokwi_power_pins` (or its new name) as the override it already is
  (`mapping.ts:109`), in the schema page.
- **C12 · Remove `footprint_module`** — keep; docs: `agents.md:456` ("`physical.footprint_module` and `footprint_export`")
  and `boards/README.md:71` change in the same commit (the verifier's touch points).

### needs-matching-vocabulary

- **C1 · One matcher: `--need` reads `function.what` and the drawer, matches by words hit, and says which words
  missed** — keep, with tokens not substrings (M5) and the user-human lens's quoting point. Docs: `commands/research.md:24`
  ("a match is the answer") says what a ranked answer means; `parts.py:1334`'s docstring and `tests/test_parts.py:791-797`
  change; `journey.md:524` and `:533` are re-recorded (two 0.7.0 blocks); the five pages that send agents to `--need`
  (`research.md:20`, `build.md:145`, `identify.md:31`, `agents/parts-researcher.md:12`, `skills/spark-design/SKILL.md:21`)
  need no change if the command's name and shape hold. The verifier's cheaper alternative (keep the AND, add the two
  sentences) is a documentation-sized change that still leaves the quoting trap.
- **C2 · The pick says what the match knew, and the needs listing shows the pick** — keep the note (verb first, M1); drop
  the mark/pick pair rule (it refuses plant-alarm's real file and the documented gap → research → pick path). Docs:
  `commands/idea.md:50-51` gains the rule for an all-`[other words]` list (mark `gap` and pick nothing, or pick and say
  why); `journey.md:179-180` says the pick prints the note.
- **C3 · A need can be dropped, and a pick cleared** — keep; docs: `commands/idea.md:24-25` loses "there is no removing or
  renaming a need yet, so a wrong one is fixed by hand" — the one hand edit the pages prescribe; `journey.md:149-152`
  (what `--needs-set` prints) gains the drop line; say that history lines keep the old id (the verifier).
- **C4 · Every answer that runs over the drawer says how many entries it could not look at** — keep; incomplete without
  M8: a step in `commands/drawer.md:47-80` after the import where the agent proposes `function` from the label and the
  person says yes — the only path to zero for the 91. Docs: that step; `commands/idea.md:67-74` extends its warning from
  records to entries; `commands.md:84-103` follows.
- **C5 · The research skeleton carries every chain fact, and research ends with `--audit`** — keep; correct the
  diagnosability line (the verifier's M3: `--validate` accepts the nulls; `--audit` names them). Docs:
  `commands/research.md:80-90` "Check what came back" adds `--audit --project .` with its two sentences quoted;
  `agents/parts-researcher.md:76-104` and `skills/spark-design/references/part-data.md` name `function`, `pin_order_proof`
  and `simulation`; `agents/datasheet-reader.md:49-54` "Finish" ends in `--audit` too.
- **C6 · The cut lists its words and ids** — keep (cap ids per word). Docs: `journey.md:170-186` "How to read the
  matches" gains the `… N more under other words` line's meaning.
- **C7 · A need says how many the design uses** — the PO's decision; M7 (one need per instance already yields
  `Valve1…Valve4`) is one sentence in `commands/idea.md` and nothing else — the remove-before-add path; if `count` is
  made, `idea.md:37` ("A need holds no reason, count or place") and the store design §5.3 change together.
- **C8 · `--requirements` refuses when a differently named requirements file sits in the project** — keep after M6
  (irrigation's `git mv`). Docs: none — every page already names `requirements.json` (DOCUMENTATION-1, K40).
- **C9 · The store's words are shown where a need is written and matched** — keep; docs: `commands/idea.md:22-24` (S:
  "write `what` in the store's words where one fits — `--match` shows them"); the 13 verbs are listed in prose twice
  (`idea.md:22-23`, `drawer.md:28-29`) — a test that each list equals `parts.VERBS` is grep-shaped and cheap (see
  Missing, M-D7).

### chain-and-checks

- **C1 · The chain re-seeds the derived half of `rules.json`** — change to the verifier's MC-6 (seed at
  `parts.py --requirements`, already a writer, no check becomes a writer). Docs: the three pages of DOCUMENTATION-10 lose
  the manual step (`init.md:36-42`, `README.md:155`, `journey.md:717-722`) and say one order; `compare_design.py:254-259`'s
  sentence stops blaming the person. Until the code lands, a documentation-only fix is available today: make the three
  pages agree on one order.
- **C2 · A signal the file declares is reported, not refused** — keep; docs: `how-it-works.md:37` loses "It counts as a
  problem, so the run exits 1 even when the board builds"; `build.md:41-43` ("the spine flags that") says it is reported
  on the schematic line; irrigation's `DIARY.md:134-135` becomes history, not a current statement.
- **C3 · A record can say that an input defines its own level** — keep, widened (MC-5); docs:
  `agents/parts-researcher.md:79-81` (`needs`) names the new key and when a record states it; `compare_design.py`'s remedy
  text names it; MC-2 (the `//` note that claims derivation over a person's entries) is a documentation-of-provenance fault
  inside a generated file — the template text must state the rule, never the origin.
- **C4 · One table says what each owed fact does to the chain, and every mouth reads it** — keep; it is DOCUMENTATION-12's
  fix: the five prose restatements become one quoted output (the journey) and pointers; `commands/idea.md:47-50`,
  `:107-110`, `build.md:140-145`, `journey.md:401-402`, `:450` change together; decide MC-3 (`pin_order_proof`) first or
  the pages are rewritten twice.
- **C5 · The requirements writer reads the file through `design.read`** — keep; docs: none beyond the sentences that
  already exist moving to `--requirements`.
- **C6 · The board changes in one place** — keep the recommended variant; docs: `boards/README.md:21` ("THE one place it is
  chosen") and `idea.md:132-133` ("the board follows the pick") are the documented contradiction (K49) — one sentence on
  each page says the other file follows.
- **C7 · Five small contract fixes** — keep all five; for K63 the refuse variant and `idea.md:13-15` reordered so
  `--step S` follows `--needs-set` (a documentation fix in the same change).
- **C8 · `--keep` builds the kept `board.tsx`** — keep (D the PO, 2026-10-05), in place (MC-4). Docs: the three pages that
  were right while the tool was wrong (`build.md:72-74`, `journey.md:706-709`, `agents.md:413-424` rule 5) change
  together, and `journey.md:937-942` "From draft to order" step 4 loses "Until P110 lands"; this is the model case for
  DOCUMENTATION-6 — three sentences naming #44 that must leave when it closes.
- **C9 · ★C7 — keep; one wording option** — keep; docs: `build.md:94-98` already says the suffix; add that it prints in
  every outcome.

### firmware-and-bench

- **C1 · The stand-in's pins are a board fact the chain reads first** — change per the verifier (fix the emitter's name
  choice; document and validate the override; the converter's sentence carries the remedy; `check_spine` classifies it
  could-not-run). Docs: DOCUMENTATION-13 (amend, not delete); `how-it-works.md:40` (the simulation stage's row) says a
  stand-in's missing pad is a limit, not a defect; `build.md:100-105`'s three-outcomes paragraph stays true only once the
  classification changes.
- **C2 · `flash_image.py` refuses an interpreter built for another chip** — keep in the verifier's form; docs:
  `build.md:186-189` ("for another chip, `--micropython <its .bin from micropython.org>`") gains the refusal's sentence;
  `journey.md:901-902`.
- **C3 · The step from the image to the board** — keep; the PO chooses script or page. Docs either way: `journey.md:
  911-925` "Bench" stops saying "Not yet. No command does this yet"; `README.md:77`'s row and the flowchart's last node
  change; `how-it-works.md:216-229`'s tools table gains `flasher` and `device-files`; the page carries the two commands
  and, once run, the first line the board printed as a recorded block — the first recorded output in the journey that is
  not a build or a check (`journey.md:924-925` says every green result is one today). Carry M5 (esptool 3.3 on the PO's
  machine cannot flash a C6; a minimum version) onto the page.
- **C4 · A sixth check: the firmware against the pin map it imports** — keep, named as what it is (M2: the check was cut
  on 2026-09-29 by the PO; M3: a use-against-map check, not the triangle). Docs: `README.md:75` ("Not built yet: checking
  the firmware on a Mac against it (P59, P74)") and `journey.md:887-888` are the two sentences that go; `how-it-works.md:
  75-102` "The checks" gains the sixth; `agents.md:108` (the read-only list) and `skills/spark-review/SKILL.md:30-36` (the
  table of what each check owns) gain a row — the skill's "Do not ask a reviewer to look at anything in that table"
  makes the row load-bearing for the firmware-hardware reviewer.
- **C5 · A scenario is measured against the pin map before it spends a minute** — keep as a note; docs: `build.md:
  189-193` (the scenario paragraph) says the count.
- **C6 · The documents follow the code** — keep; the verifier's correction stands: spark has no retired-phrase check (the
  bin has `tools/check-current-docs.py`); if one is wanted it is a new function in `check_docs.py` with a list of retired
  phrases and the pages they may still appear in deliberately — the bin's shape, S.

### On the PO's question (the relayed line), from this lens

For the documents: the technique exists — a Markdown pre-processor that runs the commands and fails when the recorded text
would change (`mdsh --frozen`; `cog --check`) — and either tool supplies the diff and the check; spark still owns each
block's state, redaction and class (DOCUMENTATION-20). For the store: whatever format or sync P178 chooses, today's pages
describe the store's layout in three places (`how-it-works.md:180-202` "Your store", the design's §5.1, `drawer.md:10`),
spell its path in six agent sentences (DOCUMENTATION-11), and document the kept-document shape (`documents`, `cites`,
`member`, `private_only`) only in the S3 record's `//documents` comment (K73). A redesign that moves the store moves at
least four pages; the documentation debt to pay first is to make the agent pages point at one sentence, so that a sync
redesign changes one. An "editor" (P160 #96) is a documentation question too: a page that can be edited in place and a
page the gate re-records are the same page, and the convention (DOCUMENTATION-4) must survive both.

### Missing — changes nobody proposed, from this lens

- **M-D1 · A card named by a page is checked against its state.** `tools/check_commit.py`'s board half already reads
  `gh`; one more look: every `xmejkal/spark/issues/<n>` in the pages whose card is CLOSED is named —
  `agents.md:248 names P43 (#11), closed 2026-10-06 — say what replaced it, or drop the link` — as could-not-run when `gh`
  is absent (the gate's own rule for its board part, `developing.md:84`). Testable on the suite's recorded listing
  (`tests/data/p102a-items.json` exists for the backlog test). Closes DOCUMENTATION-6 and gives the 16 "docs right, tool
  wrong" rows their retirement signal. S.
- **M-D2 · The output convention is stated and keyed on the note.** `developing.md` says what a recorded output is (a
  fenced block under `<!-- output: run DATE, spark VERSION -->`), the gate flags a `<!-- output -->` note with no block
  under it and a block of stage lines (`[ok  ]`, `[????]`, `refused, so nothing was written`) with no note above it
  whatever its fence, and `commands/build.md:80-90`'s duplicate pasted run is deleted for a link to `journey.md:683-702`
  (remove before add). Closes DOCUMENTATION-4; `boards/README.md:15`'s folder tree stops being a false positive. S.
- **M-D3 · "Where a mistake would show" for the store half, before any code.** `agents.md:330-447` "What never to assume"
  gains the four store items in the shape the page already uses (symptom → cause → what to do): a missing or empty
  `SPARK_HOME` answers from an empty store with the same words (today); a held part is refused in the plain text with no
  key and no command — read the `--json` `fix` (today); `--need` matches every argument as a substring and never the drawer
  or `function` — try fewer words, then `--match` (today); a pick is taken whatever its verb and words — read `--match`
  again beside it (today). Each item names its card. The command pages (`idea.md`, `drawer.md`, `research.md`) carry the
  same one-liners where the step is. This is the documentation half of SL-C1, SL-C6, NM-C1, NM-C2, and it lands in a day;
  when the code lands, M-D1 retires each sentence. Answers DOCUMENTATION-8. S.
- **M-D4 · The "not run" admissions get one home.** A table in `journey.md:36-51` "How these runs were made": step ·
  what was not run · kind (a conversation, an agent, Claude in Chrome, a paid run, the install — structural; or runnable
  and unrun) · since (date) · the card or the recording that would retire it; and a grep-shaped test (the suite's own style,
  `test_docs.py`) that every admission phrase in the pages sits in a row. Retiring one is deleting the row and the sentence
  with a recorded block beside it — the convention, now counted and dated. Closes DOCUMENTATION-7. S.
- **M-D5 · Lists in prose equal lists in code.** `parts.VERBS` (13, in prose at `idea.md:22-23` and `drawer.md:28-29`),
  `PIN_ROLES`, `PHYSICAL_KEYS` (BR-C3), `CHAIN_FACTS`' table (CC-C4), the `OPERATIONS` effects (`--describe`,
  DOCUMENTATION-19), `PRIVATE` (`agents.md:89-92`): one `test_docs.py` function per list that reads the page's words and the
  code's tuple and names the odd one out — or the recorder renders the list into the page (cog's job). The pattern
  already exists for the version (`check_docs.py:170-173`) and for roles (`tests/test_boards.py:286-294`). S each.
- **M-D6 · README's "What works today" rows carry their proof.** Each row links a journey section; nothing ties the word
  (**works**, **partly**, **not yet**) to a recorded block. A rule the gate can hold: a row marked **works** links a section
  that holds at least one `<!-- output: run … -->` block, and the newest such note's version is reported beside the row's
  word (never failed; DoD 8 says the council reads currency). S; the PO decides whether DoD 8's "nothing mechanical checks
  it" should stay true (§4).
- **M-D7 · A rule in `developing.md`: a sentence that documents a fault names its card, and the card's close deletes the
  sentence.** The 16 rows in DOCUMENTATION-1's second class are this pattern working; M-D1 is its check. One paragraph.

### The ten that matter most, in this lens's order

1. **DC Change 3, reshaped (promote the recorder, bind and classify every block, `--check` on a version change in
   `check_commit.py`).** Reason: "a pasted output is real" is the rule every page rests on (`readme-design.md:80-82`), and
   the only mechanism behind it is a hand paste that did not happen at three releases (DOCUMENTATION-2, -3); nothing else
   in the documents can be trusted further than this is.
2. **DC Change 5 + DOCUMENTATION-5 + M-D2.** Reason: the first page an AI agent reads in Claude Code is a command page,
   and it is outside the gate; the guard costs nothing today (0 problems over 14 pages) and the gate's own sentences must
   name a page by its path or they stop saying where.
3. **M-D3 — "where a mistake would show" for the store half.** Reason: the stranger question's answer; every P100 stall
   was in that half and the pages say nothing of its shape; it needs no code and M-D1 retires it when the code lands.
4. **CC-C4 + MC-3 as the single source for the owed-facts sentences, rendered or checked (M-D5).** Reason: five prose
   copies disagree with the code at one row today (DOCUMENTATION-12); a table in code is the documentation that cannot
   drift, and it is also the fix for "builds with it" (K48).
5. **BR-C3 — the `physical` schema, `PIN_ROLES` and the pad forms written where enforced, generated or checked from
   code.** Reason: round 0 learned the schema from refusals one at a time (G0.2, G0.5, G0.10); the page that claims to have
   it (`how-it-works.md:145`) does not; with #61 it also retires the other project's steps from `boards/README.md`.
6. **DC Change 4 — the own-board route recorded on 0.8.1, with the variant listing and `--keep`/`--kept` for a board's
   documents.** Reason: it is the route D8 makes the first fix, the one route the docs admit was not run that a script
   can run, and two of its three sentences are facts the scripts already hold.
7. **M-D1 — closed cards named by pages.** Reason: 84 links are dated promises; one already misleads (P43); the 16 rows
   where the page carries the tool's fault need this signal to ever be cleaned.
8. **DOCUMENTATION-10's fix: one order for `init` on three pages today, then CC-C1 as MC-6.** Reason: a person
   following one page gets a different `check_all` than one following another, and the sentence blames them; the
   documentation half is a day's work and the code half removes the step.
9. **DC Change 2 + M8 — the README's typed block exits 0 and shows its output.** Reason: README holds zero recorded
   outputs against its own design's §3 item 3; a stranger's first typed block is the one place the convention is not
   kept.
10. **K58 — six literal store paths out of the agent pages, `datasheet-reader` without `Write`/`Edit`, #23's grep as a
    test (SL-C11's documentation half).** Reason: the store cannot move while six agent sentences spell its path, and
    P178 is the next epic.

Just below the ten: M-D4 (the admissions in one table, S), M-D5's remaining lists (the verbs, `PRIVATE`), DC Change 7,
FB-C6 as an amendment (DOCUMENTATION-13), and K57 (`--describe`'s effects tested, DOCUMENTATION-19).

## 3. What I could not check, and why

- Whether any of the 42 recorded blocks is wrong on 0.8.1: I compared none myself; the five, three and one compared by
  the docs diagnostician, the P100 user lens and the user-human lens are their E. The `--match`/`--pick`/`--audit`
  blocks need the 2026-10-08 scratch store (a drawer, `plant-alarm`, `button-light`), which nobody rebuilt; the
  2026-10-05 blocks ran on the real store (DOCUMENTATION-15) and cannot be reproduced at all.
- The install path (`/plugin marketplace add`, `/plugin install`): Claude Code's own command; no script runs it. Its
  admission (`README.md:102-103`) stands.
- The conversations (`/spark:drawer`'s words to entries, `/spark:idea`'s questions, the research agents, the reviewers,
  Claude in Chrome) and Wokwi: not runnable here; their admissions are structural.
- `cog`'s markers and `--check`: the docs diagnosis's reading (H here); `mdsh` beyond its documentation page (one search,
  §5; not installed, not tried): H for everything but `--frozen`'s existence.
- The P97 council's own report (`docs/observations/2026-10-08-p97-store-1c-council.md`) and #94's 26-item checklist: I
  read `docs/observations/INDEX.md`'s rows and the catalogue's rendering, not the report or the comments.
- The suite was not run (it writes bytecode and temp folders; the archive copy would have allowed it, but the gate's one
  run was the question); `tools/check_docs.py` ran once on the copy (5.5 s, exit 0).
- `--describe`'s three wrong declarations (DOCUMENTATION-19) and `parts.py:1631`'s promise: the catalogue's and the chain
  diagnosis's E, not re-run here.
- How many of the 84 card links are read by anyone: —. Whether a hobbyist reads `agents.md` at all: — (the user lens's
  Q11, unanswered).
- The real store: never read by a command nor written, by rule; the copy at `<scratch>/store` was not read by any command
  of mine either — `check_docs.py` runs each `runs:` block in a store of its own.

## 4. Questions for the decider

| question | what it decides |
| --- | --- |
| Is "a pasted output is real" a promise re-kept at every release (the recorder runs in the release step; drift fails), or dated history that may lag (the gate reports the count; nothing fails)? | DC Change 1 versus Change 3; whether DoD 10 gains a step |
| The recorder: the untracked `record.sh` promoted and tracked, `cog` (pip, Python, three comment lines per block), or `mdsh` (a Rust binary, every block rewritten to `$ cmd` lines)? | Change 3's shape; a maintainer-side dependency or none; whether the raw pages agents read gain markers |
| May the pages keep naming cards (84 links today), with a check that a named card is open (M-D1), or should a page name no card and one "known gaps" list carry them? | M-D1 versus a rewrite of 84 links; how the 16 "docs right, tool wrong" rows are retired |
| Does DoD 8's "nothing mechanical checks whether a status is current" stay true, or does a **works** row have to link a section with a recorded block (M-D6)? | whether README's three words get a rule the gate holds |
| Which pages are "the docs" for the gate: README, AGENTS, the guides — plus `commands/`, `skills/`, `agents/` now, and `boards/README.md` after P127? | Change 5's list; whether a wrong flag on a command page can reach a stranger again |
| Is a person typing spark's scripts without Claude Code a persona the documents serve (`README.md:182-188`), or only a way to check what an agent did (the design's §6.4)? | whether M-D3's sentences go into the command pages and the terminal's output, or only into `agents.md`; the user-human lens's first question |
| Should the "not run" admissions carry a date and a kind in one table (M-D4), so that "what was never run" is a count the council reads rather than a grep? | M-D4; how P100's next rounds know what to run first |
| For the owed-facts sentences: is `pin_order_proof` absent an owed fact or a contract failure (MC-3)? | whether the five prose restatements are rewritten once or twice (CC-C4; DOCUMENTATION-12) |
| Should a board's schema be written by hand on `boards/README.md` or generated from `PHYSICAL_KEYS`/`PIN_ROLES` and checked by `test_docs.py` (BR-C3, M-D5)? | whether the page can drift from the validator again |

## 5. Searches

- Web, once: `tool run shell code blocks in markdown insert command output check frozen mdsh` · decision served: whether
  an existing Markdown-native tool runs the documented commands and fails when their recorded output would change — the
  shape of DC Change 3 and the PO's "existing library" question for the documents · used (DOCUMENTATION-20; §2 "On the
  PO's question"): mdsh's page says it runs inline `$` commands into fenced blocks and that `--frozen` "will fail if the
  output is different from the input", for CI — [mdsh on docs.rs](https://docs.rs/crate/mdsh/latest), read 2026-10-10.
  cog was not searched; the docs diagnosis's reading stands as H.
- `gh issue list --repo xmejkal/spark --state all --limit 400 --json number,state,title` (read-only, 2026-10-10) ·
  decision: whether any card a page names is closed (DOCUMENTATION-6, M-D1) · used — 102 issues, 5 closed among the 37
  named.
- `gh issue view 11 --comments`, `gh issue view 23`, `61`, `94` (read-only) · decisions: why P43 closed and what its
  page sentence should say; #23's proof line (DOCUMENTATION-11); #61's proof line (DOCUMENTATION-9); #94's two parts ·
  used.

```text
how the runs were made (sanitised; every spark command on the archive copy, with the three words as separate words)
SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp env | grep SPARK_HOME     → the scratch path
<scratch>/spark$ … python3 tools/check_docs.py                                                 → docs: 7 file(s), nothing named that is not there; exit 0; 5.5 s
<scratch>/spark$ … python3 <scratch>/gate_over_agent_pages.py <scratch>/spark                → agent pages: 14, problems: 0; boards/README.md problems: 2 (named "README.md: …"); text blocks not under an sh block: agents 1, developing 5, journey 4
~/Development/spark$ grep/wc over the pages (read-only): version markers, fences, notes, admissions, literal paths, jargon, the recorder's wc and hard-coded lines, git show --stat of three release commits, git ls-files .superpowers
gh (read-only): issue list --state all; issue view 11 --comments, 23, 61, 94
```
