# Story map

The order of the work, from `VISION.md`. **Confirmed by the PO 2026-10-03** (P69). Across: the
journey a person takes. Down: slices, each a milestone that ends in something a command or a bench
log proves. A card names its slice from Ready on (`tools/check_backlog.py`). **The order of the versions is
[VISION.md's *Versions*](VISION.md#versions)** (2026-10-11): v0.10, the basic journey, item by item; later versions
one epic each. The rows below are read by release. The rows v0.10 to v0.12 are the board's Slice values, and so is Live 0, which has no row here. The rows v0.9.0 and "v0.13 and later" are not, and most old numbered rows keep their Slice names: v0.9.0 is out, v0.10 to v0.12 are next, and the rest wait. The open cards of the old slices 1, 3 and 4 carry the Slice "parked, after v0.10" (the PO, 2026-10-13), P139 (#73) among them while the FireBeetle S3 is missing. The other old numbered slices stay as names on their cards.

## The journey, and what spark offers at each step

| # | step | spark today | gap |
| --- | --- | --- | --- |
| 0 | **Shape the idea** — a conversation: what it must do, which *kinds* of module do it, what else it could do; a block diagram with no part numbers yet | `/spark:idea` (S): a goal in words becomes needs — a verb and a few words each, no part numbers, at most three questions, one at a time — written to the project's `.spark/needs.json` | brainstorming what else it could do and which *kinds* of module; a block diagram; the ways in beyond goal first (P76) |
| 1 | Install, start a project | README; `/spark:init` (`init_project.py`) | public since 2026-10-03; `/spark:setup` installs what is missing in one go after the person's yes (P82), and the simulation needs only Node (B10) |
| 2 | Know what you own | `/spark:drawer` (your drawer, in your store: what you say in plain words and what your DFRobot orders held, linked to the record spark has for the part by its exact part number), `/spark:identify` (a module from a photo) | DFRobot's is the only order importer; AliExpress orders come later (the store spec, §7) |
| 3 | Choose parts | `/spark:idea`: M matches each need against your drawer and spark's records, store first (`parts.py --match`); C picks a part per need, reserves what you own and refuses a pick another project holds, naming it (`--pick`); L writes the picks as `requirements.json`; T ends with one cost line (`--tally`). `/spark:research` for a gap, `parts.py --need/--kept`, the catalog | `--need measure distance` misses the rangefinder (P39) |
| 4 | Assign pins | `assign_pins.py`, `--emit-pins` | — |
| 5 | Generate, build | `emit_board.py`, `check_spine.py` | no capacitors (P38) |
| 6 | Check, review | `check_all.py` (5 checks), the `spark-review` skill | the agent loses `fix` (P43) |
| 7 | See it | `tsci dev`, Wokwi for VS Code (P65, P67) | — |
| 8 | Simulate | `check_spine` → Wokwi (paid minutes) | — |
| 9 | Firmware | `pins.py` only | nothing tests firmware against the board (P59, P74) |
| 10 | **Breadboard** — through-hole parts, wired from a table, the firmware tested on it | `breadboard.md` from `/spark:build --keep` (P191): the parts and how to wire them | the safe deploy: the read-only bench (P228, done), the check and the gate in the core (P219), the flash through it (P215), `/spark:deploy` and `--json` (P213). Then the first walk to a lit LED (P100, round A); the bin's `bringup/01..06` after it (P73) |
| 11 | PCB and fab — offered once the breadboard works | `emit_board` → tscircuit, `fab.py`, `check_bom`, the review's fab gate | optional, and only after the circuit and the firmware are proven (a later version) |
| 12 | Enclosure — 3D export, Fusion 360, printed parts | `tsci export -f glb` only | everything past the board's own model (a later version) |

Two halves: the maker uses spark to *check* a hand-written board; only the cold tests used the
generator. Steps 9–11 hold almost nothing from spark yet.

## The slices, in order

| # | slice | for | done when | items |
| --- | --- | --- | --- | --- |
| **v0.9.0** | **Done, the chain to a simulated run** (PR #221) | hobbyist | released 2026-10-13: an idea to a board, a breadboard sheet, the pin map and firmware that passes in Wokwi, and a known dev board path | P195, P196, P59, P197, P130, P192, P193, P228, P229, P185, P113 (all closed; the board keeps them in the Slice v0.10), among others: [the release notes](https://github.com/xmejkal/spark/releases/tag/v0.9.0) have the full list |
| **v0.10** | **The basic journey** — the board's Slice "v0.10 The basic journey" | hobbyist | the PO's walk: button-and-LED from an idea to a lit LED on a breadboard, firmware that passed the simulation, every stage handing over ([v0.10](VISION.md#versions)). Deploy slice 0: the check and the gate (P219), the flash through it (P215), `/spark:deploy` (P213), then the walk (P100) | P219 (#201), P215 (#196), P213 (#192), **P100** (#6), P138 (#72), P214 (#194), P202 (#161), P204 (#167), P218 (#200, the deploy epic) |
| **v0.11** | **Change it and put it on again** — deploy slice 1, the Slice "v0.11 Change it and put it on again" | hobbyist | the PO changes one line, gives one command, and sees one receipt line with the image sha256 ([the deploy map](../docs/discovery/2026-10-13-p218-deploy-and-board/story-map.md)) | no card yet (a new story under P218 #200) |
| **v0.12** | **Another board, the matching base** — deploy slices 2 and 3, the Slice "v0.12 Another board" | hobbyist | a wrong board record names the difference and writes nothing. Two near-identical boards are told apart by MAC. A project that needs PSRAM gets the matching MicroPython build | a second P219 story (no card yet), P230 (#218), two new stories |
| **1** | **Public** — a stranger can install it (done 2026-10-03, P104 closed) | hobbyist | the repository is public with no vendor file in its history; an unauthenticated clone works; nothing shipped names one person's machine | P71, P44, P75, B10, P82, P104 (all done). The open P137 (#71, what init says) and P147 (#81, the version) are parked, after v0.10 |
| **1b** | **From a vague idea** (after v0.10, not scheduled) — the walking skeleton's first step | hobbyist | goal first runs today: `/spark:drawer`, then `/spark:idea` from a goal in words to a requirements file that `/spark:build` turns into a board (store 1a–1c, done 2026-10-04 to 2026-10-08). *Not designed yet* — the PO's overview: brainstorm a vague idea into what it does and which kinds of module, a schematic first without specific parts | **P76** (#5) — the brainstorm, the block diagram and the ways in beyond goal first; P100 (#6) moved to v0.10 |
| **2** | **First copper** — the bin on a breadboard, after v0.10's button-and-LED walk | maker | bring-up 01–06 logged with a verdict each; the motor current measured; a `wake_reason()` line after a wave | P81 (done), B1 (done 2026-10-06), **P58** (bin #5), **P73** (bin #2), **B8** (bin #3), **B5** (bin #4), B11 (done) |
| **3** | **Firmware fails on a Mac** | both | irrigation's firmware imports without running, and a check reports Valve4 never driven | P59 (#7, done in v0.9.0), **P74** (#8, parked, after v0.10) |
| **4** | **Checks on two named projects** (stale: the old v1 is now the basic journey, v0.10; its open cards wait, none is in v0.10; the board's Slice is "4 Checks on two projects") | hobbyist | the documented example and irrigation: `check_spine` exits 0; `check_all` shows no `[FAIL]`; every `????` names its fact | **P64a** (#12), **P39** (#10), P38 (#9, closed), P78 (#14, closed), P80 (done), P83 (done), B13 (done), P43 (#11, closed), **P77** (#13) (its place is the council's) |
| **5** | **A real stranger, to running firmware** | hobbyist, tested | a person outside the project, README only, own machine and board, keeps a diary nobody helps with; someone else scores it | R2.6 (#15, done); later, after v0.10: a stranger's first install |
| **Live 0** | **Live on the board, the walking skeleton**: Claude runs a line of code on the PO's running board | hobbyist | on the bare XIAO C6 with P246's project, the PO types one grant in his terminal, and Claude's live call (sketch name `spark live --code ... --json`) reaches the board, cures a silent console after a power-on when one occurs, refuses the USB and flash pins, ends with the chosen reset, and keeps a log (`docs/discovery/2026-10-15-p235-live-on-board/story-map.md`) | P252 #263, P251 #264, P253 #265, P254 #266, P246 #260, P247 #267; beside it P256 #268, P255 #269; later P248 #270, P249 #271, P250 #272 |
| **v0.13 and later** | **Later versions** — v0.13 is one core (P158 #94, on the board still in the Slice 1b), the rest one epic each: live on the board beyond Live 0 (P235 #224: WebREPL and OTA, D31), breadboard to perfboard to PCB, a board you can order, an enclosure, the store shared | hobbyist | one epic each, in the PO's words: [VISION.md's *Versions*](VISION.md#versions) | P79 (#16) stays the breadboard's epic, met by v0.10's walk |
| **6** | **Shared, not copied** | everyone | the bin builds with spark's converter, and its CI runs every check against public spark; claims checked against their sources | **P32b** (bin #6), P64b (parked), P64c (parked), B12 (done) |

**The PO, 2026-10-03 — an overview, not a process:** slice 1b comes straight after going public — *"we first need to make it
work, really from just talking about some vague idea"*; later versions make ordering a board and
printing an enclosure part of the journey, optional and after the firmware works.
Slices 2 and 3 run side by side: the maker's share of 2 is parts and a bench, the team's is the
items. **Order and status live in the projects:** spark (https://github.com/users/xmejkal/projects/2) and the bin
(https://github.com/users/xmejkal/projects/1), since 2026-10-05 (P102a; Kanban, the stages and limits in
`docs/2026-10-05-backlog-in-github-design.md`). This map keeps the slices and which items sit in each, as text for
P102b to draw.
**Team tools:** **P102** (#24), the tools chore, with its stories P102a–f and **P103** (#32). **Desk lane:** **P72** (#31).
**Parked** (each with what pulls it back, in the archive): P66, P68, P49, P50, R10, F1, F2, F5, P64b, P64c, P84, P86.
**Merged:** P2 into P59, P70 into P102, P101 into P102e. **Deleted:** P17.

### Journeys, by release

The deploy journeys J1 to J7 are in [`jobs-and-journeys.md`](../docs/discovery/2026-10-13-p218-deploy-and-board/jobs-and-journeys.md). The basic journey itself is P100's walk.

- J1, put the passed firmware on my board: v0.10.
- J3, the board is not the one the project is for: v0.10 (the stop) and v0.12 (what differs, and the offers).
- J2, change the firmware and put it on again: v0.11.
- J7, two near-identical boards: v0.12.
- J4, debug on the board live: the epic P235 (#224), slice Live 3 (P250 #272, a pin read by name); the spike P222 (#204) keeps its wide question.
- J6, try things live over USB or Wi-Fi: the epic P235 (#224), slice Live 0 over USB (P247 #267); Wi-Fi later (D31 of P218's discovery).
- J5, Arduino or PlatformIO: later (spike P221, #203).
- Proposed, new, not yet in the discovery file: J8, a stranger takes the basic journey on their own machine: after v0.10.
- Proposed, new, not yet in the discovery file: J9, the PCB and a printed body from the same conversation: later (the north star, P203 #163).

## Scenarios — and whether each runs today

| | scenario (Given · When · Then) | proof | today |
| --- | --- | --- | --- |
| 1.1 | a machine with no access to Petr's account · `/plugin marketplace add xmejkal/spark` · it installs | an unauthenticated `git clone`; the install in an empty config | **yes** (2026-10-03) |
| 1.2 | spark's whole history · searched for vendor files and secrets · none | `git rev-list --objects --all`, a secrets scan | **yes** (2026-10-03) |
| 2.1 | the bin's firmware README · Petr wires step 2 · every pin it names is in `config.py` | P58's check | **no** — it names the XIAO's pins and a deleted `04_mp3.py` |
| 2.2 | the drawer's audio module · `/spark:identify` on both sides · a record names it | the record | **settled otherwise** — B1 named the DFR0954 from the DFRobot order history (2026-10-06) |
| 2.3 | the bin on a breadboard · `bringup/01..06` · a log per step with a verdict, the motor current, a wake reason | the bench log | **no** |
| 2.4 | the firmware gate · run 200 times under load · no failure, or a named one | the runs, kept whole | **partly** — one failure named in 60 |
| 3.1 | irrigation's firmware · imported with a fake `machine` · it does not start running | an import | **no** — `main()` runs at import |
| 3.2 | requirements that ask for Valve4 and a mode button · the firmware is checked against `pins.py` · both reported | P74's check | **no** — no such check |
| 4.1 | an empty directory and the documented example · init → `check_spine` → `check_all` · exit 0, no `[FAIL]` | the commands | **yes, by record** (P51, P57) |
| 4.2 | irrigation · `check_all` · no `[FAIL]`; each `????` names what to state | the command | **yes** |
| 4.3 | "something to measure distance" · `parts.py --need` · the rangefinder | the command | **no** (P39) |
| 4.4 | a record with `verified: true` and only a prose source · `--validate` · refused | the command | **no** (P64a) |
| 5.1 | a domain the PO picks · a real outsider follows the docs · a checked board and running firmware; scored by someone else | the diary | **no** |
| 6.1 | the bin's public CI · runs · no line says SKIPPED | the CI log | **no** — spark's four checks are skipped |
