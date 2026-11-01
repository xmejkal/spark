# P480 UX lens: what the person and Claude saw at each stall of walk 3

> Every stall S1 to S7 (walk 3's seven waits) was a missing sentence at the point of action, not a missing feature.
> Three one-line fixes carry most of the value: name the project that a command used (C3), say each store write before it happens (C4), and split "board read" from "token given" (C5).
> Each proposal below is one message in one file, so each fits one PR.

## Findings

Evidence: `walk3-diary.md` (Stalls, Gaps) and the code in this worktree at `53c1cbb8`. "Person" is Petr, "Claude" is the agent.

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| U1 | S1: the person saw nothing about USB at init, and Claude saw no command that reads USB before a `requirements.json` exists. Both had to ask each other. | G1, G4, `commands/init.md` step 1 lists boards only, `board_look.py:474` stops with "requirements.json names no board" | C5 (which board is on USB) | Init and idea pages gain a step 0: run `look.py --board-only`. Wording in P-C5a below. | high |
| U2 | The look's wrong cause: the file is missing, the line says it names no board. `fix` and `next` are empty, so nothing tells either reader what to do. | G3, `board_look.py:474` has one reason for two cases | C5 | Split the code in two: `NO_REQUIREMENTS` and `NO_BOARD_NAMED`, each with a `next`. Wording in P-C5b. | high |
| U3 | S3 and the "walk3-2" folder: init printed the name "walk3", the pages write `<project>`, and the command takes a folder. Claude read the name as a name. | G9, `init_project.py:430`, `parts.py:2243` calls `store.add_project(target)` with a path | C3 (project by name or folder) | The first line of every project command says which project it used and how. Wording in P-C3. | high |
| U4 | The dry run that showed the mistake ("would list walk3-2") was skipped, because the idea page shows `--step` with no dry run. The safe path was invisible. | G17, `commands/idea.md:17`, `parts.py:2253` | C3 and C4 | Idea page shows the dry run first, once, for the first `--step`. No new code. | high |
| U5 | S2, S3, S5: the person stopped three times to approve writes that nobody listed in advance. Claude told the person that init does not change the store, and that was wrong. | G5, G8, G25, S2, S3, S5, `init_project.py:430` writes `projects.json` | C4 (every store write said) | Every page gets one "Writes to your store" line, and every writing script gets one `--help` line with the same words. Wording in P-C4. | high |
| U6 | The build says it records `built`, but a board-only build records nothing. Claude asked for a yes to a write that did not happen. | G27, `check_spine.py` `board_alone` returns before `parts.note_built` | C4 | The verdict names the store line it wrote, or says "no store line: board-only build". A check reads the verdict, never the page. | medium |
| U7 | The look gave `could-not-run` and exit 2 both when it read nothing and when it read every field and had no token yet. The person could not tell "the board is wrong" from "build first". | G18, `board_look.py:416`, `look.py:47` | C5 | Add one summary line on top of the look, plus a `board_read` flag in the JSON. Wording in P-C5c. | high |
| U8 | S4 and S6: the bootloader buttons came twice, and the second time the sentence did not explain why. After the look, the board waits in the bootloader and the `next` is empty. | G19, G34 | C5 | The doctor says what it saw, what it cannot tell, and the one step. Wording in P-C5d. | medium |
| U9 | The doctor read the USB serial, which holds the MAC, and the store had a record for that MAC. Nothing joined the two. The person could not learn "this is the board I flashed at 06:23". | G15, G16, O2 | C5 | One line after the MAC: `known board: <id>, last deploy <time> by <project> (store record, not read from the board)`. Reuse the sentence that O16 shows already exists. | medium |
| U10 | S7: auto mode refused the run, and neither page nor script said what the person does next. Claude built the line by hand from the look's `next`. | G35, G36 | none yet (C6 does not cover it) | Deploy page gets one paragraph: "If your tool refuses this run, copy the line the look printed under `next` into your own terminal." Look prints `next` as a full line with no `--port` when one board is on USB. | medium |
| U11 | `--match` shows `xiao-esp32-c6-fresh` with no word, and `--offer` repeats words. The person reads noise at the pick. | G11, G12 | outside C1 to C8 | Not a message gap. Leave to product lens. | low |
| U12 | Two readers need two forms. The person reads one sentence. Claude needs a code and a field to branch on. Today the look has codes (`board_codes.py`) but the human line is the only place that says "no token yet". | `board_codes.py:58-69`, `look.py:43` | C5 | Rule for all proposals: one sentence for the person, one code and one boolean for Claude, never English text compared by Claude (the "no magic strings" rule). | medium |

## The exact lines

**P-C3. A project named by name or by folder.** Where: `scripts/parts.py` (every operation that takes `<project>`), with the helper in `store.py`. One resolver, used by all operations.

- Rule: a word with no slash that is on the projects list is a name. A path that exists is a folder. Anything else stops, and nothing is made.
- First output line, every run: `project walk3 = folder /Users/.../walk3 (listed name, used as a name)`.
- Stop line: `stop: "walk3" is not a folder here and not on your projects list. Nothing was made. Listed names: walk3, smartbin-local. To start a new project, run /spark:init in its folder.`
- The `--help` line: `<project> is a listed name (see --projects) or an existing folder. A folder that does not exist is refused, never made.`
- JSON: `data.project = {"name": "walk3", "folder": "...", "by": "name"}` and the code `project_not_found`.
- Removal: `parts.py --unlist <name>` with `--dry-run`. Its line: `removes walk3-2 from your projects list and 1 line from your history. The folder is not touched.`

**P-C4. Every store write said, with a dry run.** Where: one sentence on each page that has a writing step, the same sentence in `--help`, and a `--dry-run` on every writer. Writers found in this walk: `init_project.py` (projects list), `parts.py --step`, `check_spine.py` (`built`), `--pick`, `--drawer-set`, `deploy.py`.

- The line, the same on the page, in `--help` and in the output:
  `Writes to your store: <file> (<what>). Add --dry-run to see it first.`
  Example: `Writes to your store: projects.json (lists walk3) and history.jsonl (one step line). Add --dry-run to see it first.`
- After a real write, the output ends with `wrote: projects.json, history.jsonl` and the JSON carries `data.store_writes: ["projects.json", "history.jsonl"]`. An empty list means no write. Claude reads the list, not the sentence.
- The list of writers lives in the idea page's first lines once, as `Store writes in this command: --step (history), --pick (drawer, history), --needs-set (project file)`. The person approves the whole list in one yes. This removes S2, S3 and S5.
- Init: change the claim. `init_project.py` prints `wrote projects.json: listed walk3` as its own line, and the init page lists it.
- `check_spine.py`: `--dry-run` runs the chain and prints `dry run: built is not recorded` or `built recorded: board firebeetle2-esp32s3, 0 parts`. A board-only build prints `no store line for a board-only build` until C4 also fixes G27, which is a code change.

**P-C5a. Which board is on USB, before init.** Where: `scripts/look.py --board-only` (no project needed), called from `commands/init.md` and `commands/idea.md` as step 0. Same board reader as today, so no new code path.

- Output: `on USB: ESP32-S3, 16 MB flash, MAC 34:85:18:42:xx:xx. Known: FireBeetle 2 ESP32-S3 (library board firebeetle2-esp32s3, drawer entry dfrobot-dfr0975, store record 34-85-18-42-xx-xx, last deploy 06:23 by "bench", store record, not read from the board). Name it in init with --board firebeetle2-esp32s3.`
- Not known: `on USB: ESP32-S3, MAC aa:bb:... Spark has no record of this MAC. Pick a board from boards.py --list.`
- Not read: `on USB: not read. A board is on port /dev/cu.usbmodem1101, but the chip did not answer. Hold BOOT, press RESET, release BOOT, run it again.`
- Page text for init and idea: `If the person says "the connected board" and names none, run look.py --board-only first. Never ask them to name it.`

**P-C5b. The look with no requirements file.** Where: `board_look.py:474` and `board_codes.py:58`.

- Now: `requirements.json names no board`. Change to two codes. `NO_REQUIREMENTS`: `no requirements.json here, so the look has no board to compare with. Run look.py --board-only to see what is on USB, then /spark:init --board <id>.` `NO_BOARD_NAMED` keeps its sentence and gains `next: /spark:init --board <id> --force`.

**P-C5c. "Read, no token yet" against "not read".** Where: the first line of the look's output, `board_look.py:416`, and the JSON.

- Read, no token: `board read: yes, every field matches. Token: none yet, because nothing is built. Build first (/spark:build), then look again.` Exit stays 2.
- Not read: `board read: NO. The chip did not answer. See the steps below.` Exit stays 2.
- JSON: `data.board_read: true|false` and `data.token: null` with `no_token_reason` code `NOT_BUILT` or `NO_MAC`. Claude branches on `board_read`, never on the sentence.
- Exit codes do not change (a rule in `look.py:43`), so only a field and a line are added.

**P-C5d. The doctor's hand step.** Where: `board_doctor` output, the sentence after the silent console.

- `The console was silent for 2 s. This means the firmware prints nothing or the board does not answer. spark cannot tell which. Hold BOOT, press and release RESET, release BOOT. After the look, press RESET once: the board stays in the bootloader until you do.`
- The reason esptool cannot reset this FireBeetle (G34) is not known in the code. The line says "spark does not know why this board needs the buttons". It never guesses. A board-record fact `needs_manual_bootloader` is a later card, once the PO tests it.

## C1 to C8

- C1 (spike: best use of Wokwi and an own emulator): keep. No UX content. Drop only the wish that it starts "after the MVP" from the UX side: it does not touch a stall.
- C2 (a board's own part is a real part): keep. UX effect: the person sees the LED on GPIO21 in the sheet. One message gap remains: until C2 lands, the board-only verdict must say `onboard LED and button: not drawn, no scenario can reach them` in the first line, not only in the limits (G28). Add that as a one-line change inside C2's first PR.
- C3 (project by name or folder): keep, rewrite. The change: one resolver in `store.py` used by every `parts.py` operation. It says which project it used (P-C3), refuses a folder that does not exist, and has `--unlist`. Done when: the walk 3 mistake (`--step walk3` from inside `walk3`) prints the project line and the stop line, makes no folder, and `--unlist` with `--dry-run` removes a listed name.
- C4 (every store write said): keep, rewrite and split. Part 1: the "Writes to your store" sentence on pages and `--help`, plus `store_writes` in the JSON, plus dry runs on init and `check_spine.py`. Part 2: board-only build records `built` (G27), a code change. Done when: each writer in the list above prints the same sentence on its page, in `--help` and in its output, and a test finds a writer with no `--dry-run`.
- C5 (board on USB before init, status words): keep, split in two. C5-1: `look.py --board-only`, `NO_REQUIREMENTS`, the `board_read` field, the summary line (P-C5a to P-C5c). C5-2: the doctor's MAC-to-record line and the bootloader sentence (P-C5d, U9). Done when: with no `requirements.json`, the look prints what is on USB and the next command, and a look that read every field but has no token says `board read: yes`.
- C6 (bench result place, verdict names what it tested): keep, no UX rewrite. UX wish: the verdict's first line says `passed: the firmware starts. Tested: no must line.` (G32). That line is one change and does not need the bench-result record.
- C7 (hand edits kept or named): keep, low priority. UX: each generated file header says `spark owns: ... / yours: ...`. Start with one page, no merge code.
- C8 (free firmware tests on the Mac): keep, no UX content. Not a stall.

## New cards

- P? - the project's `next` after a refusal is empty -> every refusal and every `could-not-run` carries a `next` line and a code. Need: G3, G19 and U10 each left both readers with no step. Done when: a test runs every stop code in `board_codes.py` and fails for a stop with no `next`.
- P? - auto mode refuses `deploy.py` and the page is silent -> the deploy page and the look name the hand-over. Need: S7 and G35. Done when: the page has the paragraph from U10 and the look's `next` is one complete line without `--port` when one board is on USB (G36).

## Not checked

- I did not run any script. All wording is a proposal and no output was reproduced here.
- I did not check the exact function that prints the doctor's text, so P-C5d names the place only as "the doctor output".
- Whether `look.py --board-only` can reuse the board reader without a project folder is not checked. The technology lens owns that.
