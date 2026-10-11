# Council — the user's journey, for an AI agent at the keyboard (P158 part 1)

Written 2026-10-10 by the user's-journey lens for an AI agent, against spark 0.8.1 (main `a8aa34d`, E: `git log -1`,
`.claude-plugin/plugin.json`). "The agent" here is Claude in a Claude Code session following a command page, or an agent
anywhere else following `docs/guide/agents.md` — which tells it to *"Act on what the scripts answer, the JSON and the exit
code, not on what their source seems to say"* (agents.md:8). Every finding below asks one question: where does a script's
output let that reader conclude something false, and what shape would have stopped it.

**How the runs were made.** The PO's store was copied once (`cp -R ~/.local/share/spark <scratch>/store`, 33 MB by `du
-sh`); every spark command ran as `SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp python3 -B …` —
three assignments as three words, verified once with `env | grep` (E: the three variables printed, pointing into
`<scratch>`), `-B` so no bytecode landed under `~/Development/spark`. One scratch project `proj-a` with three needs (board ·
compute/microcontroller; soil · sense/soil-moisture; radio · communicate/wifi), one real pick on the copy (the soil probe),
every other write a `--dry-run`. The real store was never run against: `stat` of its `history.jsonl` (Oct 8 12:33:35) and
`projects.json` (Oct 8 14:26:17) read the same before and after (E). `git status --short` in spark showed the same three
untracked paths before and after (E). The scripts of the walk and their outputs are kept under `<scratch>` (`walk.sh`,
`walk.out`, `walk2.sh`, `walk2.out`). Nothing under the bin, irrigation or plant-alarm was touched. Tags: **E** a pointer or
a run and what it printed, **H** a claim with its source, **D** a decision (who, when), **—** unknown.

I read first: the catalogue; the six diagnoses and their verifications; then `scripts/outcomes.py`, `parts.py` (the
`OPERATIONS` table, `_op_pick`, `_op_requirements`, `_op_match`, `_op_need`, `_say`, `main`), `store.py` (`home`, the
lock, `add_project`), `check_spine.py` (the classifier, `run`, `render`, `report`), `check_all.py`, `boards.py`'s and
`check_vendor_pins.py`'s cache path, every page under `commands/` and `agents/`, `skills/spark-design/SKILL.md`,
`docs/guide/agents.md`, `commands.md`, `how-it-works.md`, `AGENTS.md`, `tests/test_json_contracts.py`, the store design,
the store discovery and the refactoring notes; the P100 folder's accounts (the round-0 runner, the refuter, the user, the
PO assistant, the tech lead, the brief, items, verification, risks, the round-0 diary); irrigation's `DIARY.md`; and the
cards #94 (with its comments), #101, #58, #23, #17, #123, #99, #102, #59 by `gh issue view` (read-only).

## 1. Findings

Each: id · claim · tag · pointer · supports only.

- **USER-AI-AGENT-1 · The `--pick` envelope drops every note the text prints — including "a board needs a board file".**
  `--pick <proj> board=dfrobot-dfr1075 --dry-run --json` → `status ok`, `problems []`, `unchecked []`, `data` keys
  `picks, project, released, reserved, written`; the words "board file" occur nowhere in the envelope. The same command
  without `--json` prints `dfrobot-dfr1075: a board needs a board file — a record in boards/ — before spark can build with
  it`, `would list proj-a on your projects`, `would write to your history: 1 reused` and `needs.json would name your drawer
  entry dfrobot-dfr1075 …`. Code: `parts.py:2020` hands `notes` and the "what a pick wrote" lines to `_write_lines` (the
  text) only; the `Answer`'s `data` (`:2017-2019`) has no key for them; `--describe` declares exactly `project, picks,
  reserved, released, written` for `pick` (my J1), so the self-description is honest and the information is absent. An
  agent acting on the JSON reserves a board it cannot build with, writes a `reused` line for it, and learns at
  `--requirements` (K29). · E (my runs R2b, J10, J1, 2026-10-10, on the copy; `parts.py:1988-2020`) · supports only:
  0.8.1's `--pick`. The same shape for `--requirements`' footprint-stop note (`parts.py:2086-2087`, `said` only, `data`
  has no key for it) is a code read, not a run — the XIAO is held, so no pick of it is accepted on the copy.
- **USER-AI-AGENT-2 · Neither channel is whole; an agent needs both to get one answer.** The JSON lacks what the text
  says: `--show l9110s-module --json` → `status ok`, "CONFLICT" absent from the envelope, `data` = `{record}`, while the
  text prints two `CONFLICT:` lines (AIA, AIB); `--unverified l9110s-module --json` → `status ok`, `problems 0`,
  `unchecked 0`, `data.questions 1`. The text lacks what the JSON says: the refusal of the held S3 prints `refused, so
  nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here` and nothing more, while the
  envelope's `problems[0].fix` holds `free it — a file holding [{"entry": "dfrobot-dfr0975", "used_in": …}] without
  smartbin-local, given to --drawer-set <file> after a dry run — or pick another`; `_say` prints `fix` only when an answer
  has no lines (`parts.py:2182-2184`). · E (my J4, J5, R2c; the code; the catalogue's K55, K56) · supports only: the four
  operations run; K55/K56 as catalogued.
- **USER-AI-AGENT-3 · `next`, the design's machine-readable remedy, is filled by nothing.** §6.4.2 of the store design
  specifies `next` items `{op, argv, why, effects, needs_yes}` (`docs/2026-10-04-store-design.md:320-322`). `grep -n
  'next_steps\|\.next\b\|next=' scripts/parts.py` → `:1547` (the `--from` help text) and `:2176` (passing `answer.next`
  through); `Answer`'s default is `()` (`:233`); agents.md:255 says *"It is empty today: no operation fills it"*. Every
  envelope in my runs carried `next: []` (describe, match ×2, pick ×3, drawer, show ×2, need, step, requirements, tally),
  and two refusals carried `fix: null` (`--show no-such-part`; `--requirements` → `pick one board — none is picked`). So
  an agent's next command is always inferred from prose, and sometimes from a sentence with no remedy at all. · E (the
  grep, 2026-10-10; J1–J3, R2b, R2c, R6, R9, R14, J11) · supports only: `parts.py` 0.8.1; `check_spine` and `check_all`
  have no such field in their shapes at all (`tests/test_json_contracts.py:127-131`, `:152-157`).
- **USER-AI-AGENT-4 · "Nothing" and "the wrong store" print the same `ok`, and the answer never says where it looked.**
  With `SPARK_HOME` naming a folder that does not exist: `--drawer --json` → `status ok`, `entries []`, exit 0; `--match
  proj-a --json` → `status ok`, `firebeetle2-esp32s3 (library) owned 0 free 0`, the shelf's `sen0193-soil-moisture`
  absent, `radio → []`; the text's owned column is blank; the folder was not created (`ls` → No such file). On the copy,
  the same `--match` → `firebeetle2-esp32s3 owned 1 free 0`, `sen0193-soil-moisture (shelf) owned 8 free 7`. No field in
  any envelope names the store, the layers searched or the drawer's size (`outcomes.py:73-74` lists the envelope's
  fields; `grep -n 'home()' scripts/parts.py` prints nothing — store diag RC-2). `--need temperature --json` → `status
  ok`, `found []`, `catalog []`. By §6.4.1 a gap *is* `ok` (D the PO, 2026-10-04: "a gap is an answer") — the status
  word is right; what lets the agent conclude "not owned" is the envelope's silence about where it looked. And
  `SPARK_HOME=` (set, empty) resolves to `<HOME>/.local/share/spark` because `store.py:48` tests truthiness (my R4; the
  store verify's M1). · E (my R3, J3, J2, J9, R4; `store.py:46-49`; `outcomes.py:65-74`) · supports only: the agent's
  reading of 0.8.1; K1/K2/F5 stand as catalogued.
- **USER-AI-AGENT-5 · The chain's JSON names no cause kind; the agent is told to classify by string.** `check_spine
  --json` is `{check, stages[{name, status, detail}], status[, unserved]}` (`check_spine.py:675-678`;
  `tests/test_json_contracts.py:152-157`), `detail` a sentence. The one tool-limit classifier is a substring,
  `CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"` (`check_spine.py:216-221`); agents.md:316-317 tells the agent
  *"A stage detail that starts `Traceback (most recent call last):` is a crash"*; agents.md:292-328 ("Not yet true
  everywhere") lists five exception classes to its own exit-code table — a crash exits 1, `check_vendor_pins --json` is a
  bare list that may say `mismatch`, `init_project.py`'s three exits, a bad command line, an unknown id exits 1. Round 0's
  `"14" is not a pin of board-esp32-c6-devkitc-1` was `[!!] simulation` — "the chain is broken" — over a design that had
  built (round-0-runner.md:5, :21; the firmware diagnosis RC-1, its refuter M8: "the classifier's mechanism is substring
  matching over free text"). · E (code, tests, agents.md, round 0's account) · supports only: that cause classes live in
  prose and substrings on 0.8.1; how often an agent misreads one is —.
- **USER-AI-AGENT-6 · `--keep`'s two sentences go to stderr after the verdict, and the JSON has no `kept` key.**
  `report()` prints `left alone: board.tsx (delete it to have it regenerated)` and `wrote dist — this is what every check
  reads` with `file=sys.stderr` after the verdict (`check_spine.py:683-684`); the `--json` dict (`:675-678`) carries
  `check, status, stages[, unserved]`. An agent parsing stdout JSON has no sign that `dist/` is the regenerated board while
  `board.tsx` is the person's (K20; the chain diagnosis RC-3, E: irrigation's 13-line diff). · E (code; the chain diag's
  run) · supports only: the channel; K20 is the catalogue's.
- **USER-AI-AGENT-7 · `--need` answers differ by how the agent quotes, and the miss message cannot show it.** On the
  copy: `--need "soil sensor"` (one argument) → `nothing in the library matches 'soil sensor'. Research it: …`, exit 0;
  `--need soil sensor` (two arguments) → `sen0193-soil-moisture … Gravity: Analog Capacitive Soil Moisture Sensor …`;
  `--need 12 V inlet` → the two catalog screw terminals, not `jst-ph-2-power-inlet` (I1 holds: `all(word in haystack)`,
  `parts.py:1327-1329`). The miss line prints `" ".join(args.need)` (`parts.py:1634`), so both forms of "soil sensor" would
  print the same `'soil sensor'`: the output cannot tell an agent how its words were split or which word missed. · E (my
  J9; the code) · supports only: these phrases on the copy. **H:** the needs diagnosis's reproduction line *"`--need soil
  sensor` → nothing"* (RC-1, repeated by its refuter) was the one-argument form — a correction to that line, not to the
  mechanism, which stands on `12 V inlet`. The store discovery recorded the same trap for `--need "time of flight"` on
  2026-10-04 (`docs/2026-10-04-store-discovery.md:37`, S6).
- **USER-AI-AGENT-8 · The agent guide and the command pages give two instructions one pick cannot both meet.**
  agents.md:8: act on the JSON and the exit code. `commands/idea.md:99-103`: say "a board needs a board file" and "board …
  stops at the footprint stage" *"to the person as they are"*; `:143`: *"Say each to the person as it is printed"*. Those
  sentences exist only in the text (USER-AI-AGENT-1). An agent in Claude Code reads the text (the page says so); an agent
  elsewhere reads the JSON (the guide says so); the two learn different things from one command. · E (the two pages; J10)
  · supports only: the documents and this operation.
- **USER-AI-AGENT-9 · Four exit codes an agent acts on say the wrong kind of wrong.** `--show no-such-part` → exit 1,
  `status problems`, `fix null` — a typo reads as a finding about a part (by design: §6.4.1 "problems = a named id that
  does not exist", D the PO 2026-10-04; agents.md:328 documents it). `boards.py --validate` from a folder with no project
  → exit 1, `boards.py: no board selection at <plugin>/boards/active.json` — it looked for a selection in the plugin and
  answered "problems" (K52; the chain verify's MC-8: `EXIT_PROBLEMS as EXIT_INVALID`). `tools.py --status --project
  <proj>` → exit 2, `2 to install: wokwi-cli tscircuit` (agents.md:53: it exits 2 *"while any tool is missing, even one
  the current step does not need"*). `check_all.py --project <empty> --json` → exit 0, `status ok`, 4 of 5 checks
  `skipped`, and `resolved` as padded display strings (`'circuit      not found (looked for dist/board/circuit.json,
  dist/*/circuit.json)'`) the agent must parse — agents.md:213 warns that `resolved` "can name a file that was not
  checked". · E (my R6, R11, R12, J6) · supports only: these four commands on 0.8.1.
- **USER-AI-AGENT-10 · `--describe`, the agent's contract, is wrong for one row I compared and right for seven.**
  `drawer-set` declares `data` = `changes, questions, shelved` (J1); `_drawer_answer` returns also `not_shelved` and
  `written` (`parts.py:1763-1764`). For `pick`, `requirements`, `step`, `tally`, `match`, `need`, `audit` the declared
  keys match what my runs returned (J1 against R2b, R14, R9, J11, J2, J9, J7). · E · supports only: the rows compared;
  K57's `--tally` effect and `tools.py`'s missing `--json` are the catalogue's.
- **USER-AI-AGENT-11 · `--step` lists a folder that does not exist, and the page puts that step first.** `--step
  <scratch>/ghost-project S --dry-run` → `would start step S of ghost-project … would list ghost-project on your
  projects`, `status ok`, exit 0; the folder was never there (K63). `commands/idea.md:13-18` puts `--step <project> S`
  before the `--needs-set` that makes the folder (the chain verify, RC-7). An agent following the page literally lists a
  phantom in whichever store its prefix reached — the #101 shape. · E (my R9; idea.md:13-18; `parts.py:2112-2126` via the
  chain diag) · supports only: the dry run; the real write is the same code path.
- **USER-AI-AGENT-12 · A tool writes outside every store and the agent's only sign is `git status` in a folder it was
  told not to touch.** `check_vendor_pins.py:102-112` returns the plugin's cache path whenever the project has none,
  `:137-138` writes there, and the file has no `import store`; round 0's header is still untracked on 2026-10-10 (`??
  .spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h`, my R18 and J12), and `--offline` then reads it saying `cache
  (<name>)` with no folder (store diag RC-2, E). · E · supports only: K14, from the agent's seat.
- **USER-AI-AGENT-13 · The agent's whole defence is prose it must hold, and two agents on record did not hold it.**
  agents.md is 481 lines (`wc -l`, 2026-10-10); its exception list is :292-328. The P100 facilitator — an agent — ran
  with `SPARK_HOME` as one unsplit string and read an empty store as "not owned" (`council/refuter.md:57-62`); the #101
  incident was an agent's `export` not surviving to the next tool call (#101 body). Both are the behaviour the guide
  warns against, by readers who had the guide. · E (wc; agents.md; refuter.md; #101) · supports only: that the guard is
  prose; n = 2 recorded incidents, no count of unrecorded ones (—).
- **USER-AI-AGENT-14 · What an agent can already act on (kept, so the changes below build on it).** A refusal carries
  `subject`, `sentence` and, in JSON, `fix`; a bad argument is an envelope, `could-not-run`, exit 2 (`parts.py:2190-2195`;
  §6.4.1); `--tally` on an unmarked project → `status could-not-run`, exit 2, `data.line` = `1 pick: 1 from the store (1
  owned) — its cost was not counted`, `unchecked[0]` naming `--step` (J11); `--requirements --dry-run --json` carries
  `data.requirements.unserved` with a `why` per need (R14); `--describe --json` marks the two network operations
  (`sources`, `fetch`; J1); `check_all`'s three-plus-one outcome words are decided in one place (`outcomes.py:32-43`,
  `check_all.py:429-441`). · E · supports only: these.

## 2. The proposed changes, judged from this lens

The question for each: would an agent reading the output after the change conclude the truth, and could a test prove
it? Verdict words: **keep** · **change** (how) · **drop** (why). Sizes are the diagnoses' (H). The catalogue's K ids and
the diagnoses' C ids are theirs; the counts of changes are mine (`§3` headings: store 13, board 12, needs 9, chain 9,
firmware 6, docs 7 — 56).

### Store (`diagnosis/store-levels-and-holds.md`)

| change | verdict | from the agent's seat |
| --- | --- | --- |
| C1 a `SPARK_HOME` that names nothing is refused; every answer names its store | **keep, change** | add the set-but-empty case (`SPARK_HOME=` → the default home, my R4; the verify's M1): the #101 shape is an unset or empty variable, not a wrong one. Put the `store` field in `check_spine`'s and `check_all`'s JSON too — `check_spine` writes the store's history (`note_built`), `check_all` reads its boards. Order it with the git refusal as the verify says (two tests). This is the one change that makes an agent's own log self-checking: `"store": "<scratch>/store"` beside every answer |
| C2 the real store is written only on purpose (#101) | **keep** | the temp-root rule catches an agent's scratch project (the twelve `p1`–`p12`); the copy-under-home case (the refuter's `irr`) needs the flag — the PO's call. Either way the refusal must *name* the rule and the store (C1's field); an agent that is refused with a sentence stops, one that writes silently does not |
| C3 one lock beside the data; a writer with no lock refuses | **keep** | every agent brief sets `TMPDIR`, and councils run agents in parallel on one store copy: the two-`TMPDIR` race is the normal case here, and it has no output at all (store diag RC-3, E: both inside for 1.5 s). The verify's costs (33 direct writes in the suite; `mkdir` of the home before `open`) are real; S becomes M |
| C4 an operation's writes land all or none | **change** | take the verify's form: keep the ordered sequence, record each step, and on a stop say `written before the stop: …; the same command, retried, finishes it`; move `add_project` after `drawer.apply`. The agent's harm is the answer lying about what landed (K8's Python-list traceback, exit 2); a sentence naming what landed fixes that at a tenth of the size |
| C5 a project is its folder, not its spelling | **keep (the spelling half now; the id with the shared store)** | the verify's move case: do not strand a moved project's holds until the id exists |
| C6 holds are listed and released by an operation | **keep, change** | put the release command in the problem's `sentence` (or in `next`, USER-AI-AGENT-3), not only in `fix` — the text drops `fix` (K56), so USER-3's walk would still end at a grep of the store. Decide the verify's M2 (derive holds on read, or keep `used_in` as a decision) first; under (i) `--release` has no target |
| C7 reads refuse what writes refuse | **keep** | the agent's `--match` counts owned 16 of 8 after a sync client's copy (K9) with no sign; the refusal names the file. Small |
| C8 one reader for a store file; no store problem is a traceback | **keep, change** | catch `UnicodeDecodeError` and `StoreProblem` by name, not every `ValueError` (the verify): for an agent a traceback *is* "where"; a swallowed one is a could-not-run with no location. Add `store.py:145` (the write side reads too) |
| C9 `--fetch` names what it could not keep, status `problems` | **keep** | the research agents run `--fetch` and check nothing (verify); the record then cites a document the store never kept. Say in `agents/parts-researcher.md` what exit 1 means here |
| C10 one layer, one count | **keep** | S; two true counts read as one wrong one (K18, my J7/J8: `catalog 0 current, 17 owe` beside `18 record(s)`) |
| C11 a record has one home that is the store | **keep (promote → shelf; the cache in the store); change the shelving half** | shelving every project record on `--requirements` puts four placeholder footprints on every project's shelf (the verify's E); "proven" needs the `built` reader first (M3). The datasheet-reader losing `Write/Edit` presumes `--fact-set` sets every field it fills — not checked (—); if it cannot, the agent is stuck mid-task |
| C12 spec and code agree on privacy | **keep as the verify re-states it** | add `sources` to `PRIVATE`, do not shrink the spec; not agent-facing |
| C13 the `built` line vouches for what the chain reads | **change** | the verify's M3: no reader compares a digest, so a wider digest changes no answer. Keep the half that prints a sentence — `the build was not recorded in your history: <project> is not on your projects list` — which an agent can act on; drop the digest half until `--audit` or `--tally` reads it |

The existing-mechanism paragraph (SQLite, git, content-addressed files): from this lens nothing in it changes what the
agent reads; the four invariants (identity by thing, one lock beside the data, a unit of work, one reader) are what make
the *answers* true, whatever holds the bytes. H, as the diagnosis tags it.

### Board records (`diagnosis/board-records.md`)

| change | verdict | from the agent's seat |
| --- | --- | --- |
| C1 a bare-number `header_order` label is refused | **keep** | the one silent class round 0 met (G0.3); add the verify's M6 (the `pins` key side) and both tscircuit regexes. The refusal names row, index and the colliding pad — the shape every refusal should have |
| C2 `pad_aliases` reaches the footprint | **keep, change** | fix the self-contradictory validator rule (`A4` is a `pins` key — the verify); and do the verify's **M1 first**: `check_spine.py:430-441` returns the island before it looks at `errors`, so the agent reads `Led08SeriesA.pin1 (a terminal connected to nothing)` while `circuit.json` holds `Could not find port for selector ".Mcu > .MISO"` — the cause, dropped. Printing the errors first is a reorder; C2's "diagnosable" clause rebuilds the same sentence by parsing two files |
| C3 the `physical` schema written where it is enforced; an unread key refused | **keep** | round 0 learnt the schema from refusals one at a time (G0.2, G0.5); the refusals were the only good documentation an agent had. Correct the *Known* list (the verify's M3) or the test contradicts the example |
| C4 `emit_footprint.py --json` prints JSON on every path | **keep the could-not-run variant** | an agent asked for JSON and got 51 lines of TSX, exit 0 (my R10; K28); `--json needs --out` is a removal of a path, and `tests/test_json_contracts.py:142-146` gains the case it never had |
| C5 the drill sentence | **keep** | S |
| C6 one comment-key rule | **keep** | the `//jtag` refusal said "not a role any script reads" of a comment — a wrong cause (G0.5) |
| C7 the vendor-header cache lives in the store; the line says `cached at <path>` | **keep** | USER-AI-AGENT-12: today the only sign is `git status` in the plugin. Say which writer (`store`'s, with the git refusal) and the fallback order for the bin's `--offline` |
| C8 a board record from a drawer entry (`--board-skeleton`) | **keep (the decided item, D8)** | from this lens the two clauses that matter: every owed field named *with the document to read it from*, and the pick printing the command instead of a page name. The pick-side change (no `reused` for a board with no file) is the PO's — the catalogue files "warned, accepted, refused later" as by design, disputed |
| C9 every stop from one rule; `--for-fab` requires geometry | **keep** | change both spellings of the stop sentence (the verify's M5) or `--list` and `_board_problems` disagree the day a board has two stops; the XIAO's data step is `footprint_source`, not a through-hole header (the verify) |
| C10 a board's `function`, validated | **keep** | a malformed `function` on a board is accepted by `--validate` and dropped by `--match` without a word (the verify's run) — the silent-drop class; decide record vs drawer (M4) |
| C11 `pins` against the stand-in's list | **keep in the verify's wider form** | "every `pins` key, mapped the way `mapping.ts:96,108` maps it, is a pin of `wokwi_part_type`"; read the registry from a copy under `data/` with its version — a Python validator that shells to node for a note is a new could-not-run for an agent without node |
| C12 remove `footprint_module` | **keep** | a removal; with C9 |

### Needs, matching, vocabulary (`diagnosis/needs-matching-vocabulary.md`)

| change | verdict | from the agent's seat |
| --- | --- | --- |
| C1 one matcher; hits, not AND; says which words missed | **change: the sentences first, the ranking later** | the agent's commonest wrong turn is "nothing matches → research" over a store it did not search (I1, USER-1, USER-9, my J9). Two sentences close the misdirection at a tenth of the change: `looked for: soil, sensor — every word must match; missed: …` and `the drawer (110 entries) and function words are not searched here — --match <project> does`. Tokens, not substrings (the verify's M5), and print the tokens — that is what makes the quoting trap (USER-AI-AGENT-7) visible. The ranking change rewrites a documented behaviour and two recorded outputs; a later card |
| C2 the pick says what the match knew | **keep the note; drop the pair rule** | add the verb case (the verify's M1: a motor driver for `sense / temperature` is taken with the same silence); put the note in `data.notes` as well as the text (USER-AI-AGENT-1). The mark/pick pair rule refuses plant-alarm's file on read (the verify, E) and the documented gap → research → pick path — drop it |
| C3 drop a need, clear a pick, set-only | **keep** | the only exit from a wrong pick today is a hand edit of a file the tool validates on read; say the history keeps the old need id |
| C4 every answer over the drawer says how many entries it could not look at | **keep** | `91 of 110 drawer entries say nothing of what they do, so no need reaches them` is the sentence that stops an agent calling an owned SCD41 a gap; add the drawer.md step (M8) or the count has no path to zero |
| C5 the skeleton carries every chain fact; research ends with `--audit` | **keep, correct the claim** | the verify's M3 is the agent's trap: `--validate ok` is research.md's done-signal, and it is silent on `simulation: null`, `function: null` and a null proof beside an empty `pin_order`; only `--audit` says "owes". An agent ends research with a record the matcher cannot see and the chain refuses. Say in research.md *why* `--audit`, not `--validate` |
| C6 the cut lists its words and ids | **keep** | cap ids per word (the verify); `more` has no reader to break |
| C7 a need says how many the design uses | **PO decision; the verify's M7 first** | one need per instance already yields irrigation's `Valve1…Valve4`; a sentence in idea.md before a schema change |
| C8 refuse when a differently named requirements file sits in the project | **keep; M6 first** | one `git mv` in irrigation ends K40 there; the check protects the next agent; cover "both exist and differ" |
| C9 the store's words shown where a need is written | **keep** | add M2's case (`distance sensor` vs `distance` — one word more); the vocabulary list alone would not explain the commonest `[other words]` |

### Chain and checks (`diagnosis/chain-and-checks.md`)

| change | verdict | from the agent's seat |
| --- | --- | --- |
| C1 the chain re-seeds `rules.json` after a kept build (C1a) / the derived half leaves the file (C1b) | **change to the verify's MC-6** | seed at `parts.py --requirements`, already a writer with the picks and records in hand; a check that writes another check's input gives a wrong rule two authors. Carry MC-1's decision (zero derived rules → `ok, checked: 0` with the reason, or could-not-run for ever on a sensor-only board). For the agent the present message is a wrong cause: *"which is what `/spark:init` writes and where they have stayed"* is false when init ran before the parts existed, and its fix sends the agent to type entries `--force` derives |
| C2 a declared signal is reported, not refused; a non-note stderr line is could-not-run | **keep** | "the chain is broken" regains a meaning on a project with a bare signal; use a shared `NOTE_PREFIX` constant (the verify), not a string contract between two files; say that a dangling pin now records `built` |
| C3 a record says an input defines its own level | **change to the wider vocabulary** | the verify's MC-5: the library's own amplifier record (`SD` held high by a module-side resistor; I²S lines driven from reset) is not a current load; name the key by what the check does with it |
| C4 one table says what each owed fact does to the chain | **keep; decide MC-3 first** | today the agent reads `--promote … builds with it` (`--need`), `owes pin_order_proof, simulation` (`--audit`) and `does not meet the part contract` (the chain's parts stage) of one record — three verdicts from one module. The consequence per fact belongs in the envelope (`owes: [{fact, stage, consequence}]`), so an agent can do what #102 asks: go on, marked |
| C5 one reader, one namer | **keep** | the sentences already exist and move to where the agent is; fold `_name_after` (the verify) |
| C6 the board changes in one place | **keep the first variant now** | `boards.py --id` answers the old board with no sign (K49); `boards/README.md:21` still says "THE one place" |
| C7 five small contract fixes | **keep** | K52 also as could-not-run (MC-8); K63 the refuse variant and reorder idea.md:13-15 so `--step S` follows `--needs-set` (USER-AI-AGENT-11) |
| C8 `--keep` builds the kept `board.tsx` | **keep with MC-4 (build in place)** | and, whatever the PO decides on #44, put `kept: [{file, left_alone|wrote}]` into the chain's JSON (USER-AI-AGENT-6) — today the two sentences are stderr after the verdict |
| C9 the unserved note on its own line in every outcome | **keep** | S; text and JSON then agree |

### Firmware and bench (`diagnosis/firmware-and-bench.md`)

| change | verdict | from the agent's seat |
| --- | --- | --- |
| C1 the stand-in's pins as a board fact read first | **change per the verify** | for both library boards the "missing pins" are name mismatches (0 of 24 GPIOs absent on the S3's stand-in, E the verify); fix the emitter's name choice (M1), give `wokwi_power_pins` its real name, document and validate it; a "spend last" role only for a GPIO with no name at all. (d) — a second pinned substring in `check_spine` — becomes a `kind` on the stage instead (USER-AI-AGENT-5) |
| C2 `flash_image.py` refuses an interpreter built for another chip | **keep the 16-byte read** | the verify's placement (the chain's simulation stage, where the resolved board and `--firmware` meet) and "could not check the chip" when no board resolves — irrigation has no `.spark/board.json`; the chip-id 13 stays H until read from a newer esptool |
| C3 the step from the image to the board | **the PO's choice** | from this lens the script's value is its could-not-run sentences (no tool, no board on a port, a chip mismatch); the page variant leaves all three to the person. A minimum esptool version (M5: 3.3 cannot flash a C6) |
| C4 a sixth check: the firmware against the pin map | **keep as a use-against-map check** | name the cut (M2: `check_firmware.py` was removed on 2026-09-29, D the PO), say what kind of check it is (M3: with `import pins` there are no literals to compare); fix `tools/mutate.py`'s import over-count (K53) before its proof leans on it; "has" = `pins` ∪ `pin_roles[*].gpio` or the XIAO's LED is refused |
| C5 a scenario measured against the pin map before it spends a minute | **keep as a note** | `asserts 1 of 12 pin-map constants … a pass proves those pins nothing` is the sentence that stops "the scenario passed" being read as "the firmware is right" (K67) |
| C6 the documents follow the code | **change** | amend the true sentences (the superset claim is true of GPIOs), do not delete them; the retired-phrase check is the bin's, not spark's — propose it as a new S check |

### Documents and recorded outputs (`diagnosis/docs-and-recorded-outputs.md`)

| change | verdict | from the agent's seat |
| --- | --- | --- |
| Change 1 the gate counts recorded outputs behind the version | **keep as a report line** | as a failing check it raises 44 false alarms on a patch that changes no output (the verify); the version is provenance, a diff is currency |
| Change 2 the README block ends where a shell can finish it; the gate runs it | **keep** | keep the file in the project; show the tally's refusal as a recorded block (the verify's M8) — the one place a stranger sees the honest exit 2 |
| Change 3 one recorder at each release; drift fails a check | **keep the mechanism; change the plan** | promote or delete the recorder that already exists under `.superpowers/` (the verify's M1); classify the 42 blocks (8 have no command above them, M2; several are not functions of plugin+store+project, M3); "the release gate" does not exist (M4) — hook `--check` into `check_commit.py` on a version change or it is prose again |
| Change 4 the own-board route recorded; three facts written where the steps are | **keep** | cut the half already on the page (`how-it-works.md:172`); `--fetch <board>` → the truthful refusal through the argument path, exit 2 |
| Change 5 the gate reads the pages agents follow | **keep** | the one docs change that protects the agent directly: a wrong flag on a command page reaches Claude at the keyboard first (C-36). Fix `path.name` → relative (M7) or three `SKILL.md`s are one name; exclude the sibling Makefiles `routes()` appends |
| Change 6 density and long lines | **change** | a rule that fails, or nothing; README's long lines are 8 table rows of 10 (the verify) — a non-finding |
| Change 7 one sentence on what spark has built | **keep** | say it per store (`parts.py --list` adds what the person's store holds) |

### Missing — changes nobody proposed

- **M-A · A named cause on every stage, problem and unchecked item.** A closed `kind` — `design`, `input`, `tool`,
  `limit`, `crash`, `store` — on `check_spine`'s `stages[]`, `check_all`'s `results[]` and `parts.py`'s `problems[]` /
  `unchecked[]`. It replaces the three string classifiers (`CONVERTER_HAS_NO_PART`, the `Traceback` prefix agents.md:317
  teaches, the firmware C1(d) proposal) and makes agents.md:292-328's exception list deletable. Testable: a
  characterisation test like `test_json_contracts.py` asserting every emitted item's `kind` is in the set, and the
  classifier's tests re-targeted at `kind`. Diagnosable: `[????] simulation (limit) the stand-in has no pin for GPIO43 …`
  — the agent branches on one word instead of a sentence. Simplicity: removes two substring matches and ~35 lines of
  exceptions prose. P43 (#11) is its card.
- **M-B · The envelope carries everything the text says, and the text carries the fix — as one tested property.**
  `data.notes` on `pick` and `requirements`; `conflicts` on `show`; `questions` promoted out of `data` into `unchecked`
  (or `status problems`) on `unverified`; `kept` on `check_spine`; and `_say` printing `fix` under every refusal (K56). The
  test: run each `OPERATIONS` row's documented example in text and JSON and assert every text line's content is reachable
  from the envelope (a property test over the table, in the style of `tests/test_routes.py`). Closes K55, K56,
  USER-AI-AGENT-1, -2, -6, -8 with one rule instead of five fixes.
- **M-C · Every search says where it looked.** `data.searched` on `--need`, `--match`, `--audit`: `{"store": "<home>",
  "layers": {"drawer": 110, "shelf": 5, "library": 10, "catalog": 18}, "looked_for": ["soil", "sensor"]}` — the numbers
  the store copy answers today (my J7, J8; the drawer's 110 from the needs diagnosis's count). It is store C1's `store`
  field plus the counts that make an empty or wrong store visible from the answer (USER-AI-AGENT-4), and the tokens that
  make USER-AI-AGENT-7 visible. One test: a missing-store `--match` carries `drawer: 0`.
- **M-D · Fill `next`, or remove it.** A promised field that is always `[]` trains the agent to ignore it
  (USER-AI-AGENT-3). The first fillers already know their command: the hold's release (`--release …` once C6 exists; today
  the `--drawer-set` template), an unknown id (`--match <project>`), an unmarked project (`--step …`), a board with no file
  (`--board-skeleton …` once board C8 exists). The test: a refusal with a `fix` has a `next` whose `argv` the parser
  accepts.
- **M-E · `--json` on the four scripts an agent runs blind.** `tools.py --status` (P92 #23 asks), `boards.py`,
  `init_project.py`, `emit_board.py` (agents.md:263-266). Until then an agent parses `[????]` rows and `wrote active.json`
  prose for its decisions; `tools.py --status`'s exit 2 cannot say *which* step is blocked (USER-AI-AGENT-9).
- **M-F · A documented exception is a bug with a number, not a paragraph.** Each row of agents.md:292-328 names its card
  (P43, P131, P119, P107, P114); the docs gate (Change 5) can fail when agents.md still names an exception whose card is
  closed. The page then shrinks as the exits become uniform instead of growing as a curated list.

### The ten that matter most for an agent, in order

1. **Store C1 with M1 and M-C's `store` field** — a `SPARK_HOME` naming nothing or empty is refused; every answer names the
   store it read. One wrong or absent variable makes every other answer false with the right shape, and two agents on
   record met it (USER-AI-AGENT-4, -13). Two lines, one field, two tests.
2. **Store C2 (#101)** — the real store is written only on purpose. The agent's prefix discipline is the only guard
   today, and spark's own pages tell agents to run the writes (idea.md's `allowed-tools` lists `--pick`, `--step`,
   `--drawer-set`). The temp-root rule now; the flag is the PO's.
3. **M-A, named causes** — one `kind` word per stage and item. It is the P43 shape the agent guide has been apologising
   for since 2026-09-30 (`docs/2026-09-30-refactoring-architecture.md:139-146`); without it the agent's reliability rests
   on string prefixes and a 37-line exception list (agents.md:292-328).
4. **M-B, JSON ⊇ text and text carries the fix** (K55, K56, USER-AI-AGENT-1, -2, -6, -8) — one tested property over
   `OPERATIONS` instead of five fixes. Until it holds, "designed for agents first" (§6.4) is true of the envelope's
   shape and false of its content.
5. **Chain C4 with MC-3** — one table for what each owed fact does to the chain, and a decision on `pin_order_proof`. The
   agent today reads three verdicts of one record (`builds with it` / `owes` / `does not meet the part contract`); the
   per-fact consequence in the envelope is what lets it do what #102 asks.
6. **Store C3** — one lock beside the data. Parallel agents with their own `TMPDIR` are this project's normal working
   mode; the race has no output and the suite does not pin it for 3 of 4 rows tested (store diag K6).
7. **Needs C1 (the two sentences and tokens first), C4 and C9** — the matcher says what it looked for, where, what missed,
   and how much of the drawer it could not reach. "Nothing matches → research" is the agent's most frequent wrong turn on
   record (I1, USER-1, USER-9, the P162 council).
8. **Board C1 and the board verify's M1** — the silent short class refused at `--validate`, and tscircuit's own error
   printed before the island sentence (`check_spine.py:430-441`), so the agent reads the cause, not a component two hops
   away.
9. **Chain C8 with MC-4, and `kept` in the chain's JSON** — the verdict and the `built` record describe a board the
   person does not have (K20); an agent reading stdout JSON has no sign (USER-AI-AGENT-6).
10. **Needs C2 (with the verb case) and C3; board C8's pick-side line** — the pick is the agent's decision point, and
    today it accepts an other-verb pick, a record-less board and a loose fit with the same `status ok`; the note at pick
    time, in both channels, and a way to undo.

Next after these, from this lens: chain C1 as MC-6 (seed at `--requirements`, carry MC-1), firmware C1 as the verify
reshapes it, docs Change 5 with M7, and M-E's `--json` on `tools.py --status`.

**On the PO's relayed question** (an existing library or format for the store): from the agent's seat the "library" that
would make it reliable is a declared contract, not a sync mechanism — a JSON Schema per operation generated from
`OPERATIONS` (so `--describe` becomes machine-checkable and every envelope validates against it in the suite), and the
`kind`/`next` fields above; an MCP face (part 2's option) serves the same list unchanged (§6.4.7 already says so). H,
mine; no search run.

## 3. What I could not check, and why

- **The chain itself** (`check_spine.py`): not run by me. agents.md:118-120 says a run "may also compile a chip beside its
  record, which for a library part is inside the plugin", and writing under `~/Development/spark` is forbidden here. The
  verdict shapes (`stages[].detail`, `unserved`, the stderr `kept` lines) are read from `check_spine.py:675-684` and
  `tests/test_json_contracts.py:152-157`; the runs are the diagnoses' and the refuter's (E in their files).
- **`--requirements` with a board that stops at the footprint** (the stop note's absence from the JSON): a code read
  (`parts.py:2086-2087`), not a run — the XIAO is held by plant-alarm on the copy and a pick of it is refused.
- **`drawer-set`'s undeclared `data` keys**: `parts.py:1763-1764` read, not run (a `--drawer-set` writes the drawer; a
  dry run would have shown the keys, and I did not make one).
- **The real store**: never run against; its two files' times read the same before and after (E).
- **Whether the needs diagnosis ran `--need soil sensor` quoted**: H (USER-AI-AGENT-7); its text shows the unquoted form
  and the result of the quoted one.
- **A human typing**: n = 0, as every P100 lens says (★C9); every output above was read by an agent.
- **Claude Code's own matching of `allowed-tools` patterns** against a command line: not run; `tests/test_routes.py`
  models it as a stated assumption (the store design §6.4.5).
- **How often an agent misreads a cause kind** (USER-AI-AGENT-5): two incidents on record (the facilitator's empty store;
  #101); no count of unrecorded ones.
- **Wokwi, hardware, the install path, the research agents**: not run — paid minutes, no board here, no `/plugin` outside
  Claude Code's own command, no web.
- **The suite**: not run (it writes `__pycache__` under spark); the tests cited were read.

## 4. Questions for the decider

| question | what it decides |
| --- | --- |
| Is `problems`, exit 1 the right word for an id that does not exist (`--show no-such-part`)? §6.4.1 decided yes on 2026-10-04; for an agent a typo then reads as a finding about a part | whether the three words gain a `kind` (M-A) or the agents.md exception stays |
| Should every answer carry `store` (store C1) and `searched` counts (M-C), and the chain's and `check_all`'s JSON too? | the shape of C1; whether an empty or wrong store is visible from any answer |
| `next`: fill it (M-D) or remove it from the envelope? | whether remedies are machine-readable or prose; an always-empty promised field is a trap |
| A `kind` per stage and item (M-A): a closed set of six words, or keep classifying by sentence? | whether agents.md:292-328's exception list is retired or maintained; P43's shape |
| Should `--pick` refuse, or warn and not record `reused`, for a board with no board file (board C8's pick side)? Today it reserves and records (K29), by design, disputed | the pick's contract at the agent's decision point |
| May an agent working on project B run `--release`/`--forget-project` (store C6) against a hold of project A? One person, one Mac today; a shared store (P178) later | the permission model of holds before the operation exists |
| Is a scratch-store run "as a hobbyist would" for P100's rounds, and is `SPARK_STORE=real` the guard you want (#101)? | whether the agent's walks count as the product's test; the shape of store C2 |
| Should the matcher's ranking change (needs C1's hits-desc) now, or only the two sentences first? It rewrites a documented behaviour and two recorded outputs | the size of the first card for K33 |

## 5. Searches

none — every claim rests on the files named in the header, the runs under `<scratch>` (`walk.out`, `walk2.out`,
2026-10-10) and `gh issue view` of #94 (with comments), #101, #58, #23, #17, #123, #99, #102, #59 (read-only). No web
search and no documentation-server query.
