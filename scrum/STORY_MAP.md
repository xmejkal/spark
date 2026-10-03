# Story map

The order of the work, from `VISION.md`. **Confirmed by the PO 2026-10-03** (P69). Across: the
journey a person takes. Down: slices, each a milestone that ends in something a command or a bench
log proves. **An open backlog item sits on one slice below, or it is parked or deleted** —
`tests/test_orphans.py` fails on one that does not.

## The journey, and what spark offers at each step

| # | step | spark today | gap |
| --- | --- | --- | --- |
| 0 | **Shape the idea** — a conversation: what it must do, which *kinds* of module do it, what else it could do; a block diagram with no part numbers yet | nothing: `/spark:build` starts from a requirements file | **all of it** (P76) |
| 1 | Install, start a project | README; `/spark:init` (`init_project.py`) | public since 2026-10-03; an installed copy may not simulate (B10) |
| 2 | Know what you own | `/spark:identify` (a module from a photo) | never pointed at the bin's drawer (B1) |
| 3 | Choose parts | `/spark:research`, `parts.py --need/--kept`, the catalog | `--need measure distance` misses the rangefinder (P39) |
| 4 | Assign pins | `assign_pins.py`, `--emit-pins` | — |
| 5 | Generate, build | `emit_board.py`, `check_spine.py` | no capacitors (P38) |
| 6 | Check, review | `check_all.py` (5 checks), `/spark:review` | the agent loses `fix` (P43) |
| 7 | See it | `tsci dev`, Wokwi for VS Code (P65, P67) | — |
| 8 | Simulate | `check_spine` → Wokwi (paid minutes) | — |
| 9 | Firmware | `pins.py` only | nothing tests firmware against the board (P59, P74) |
| 10 | **Breadboard** — through-hole parts, wired from a table, the firmware tested on it | nothing: spark's only output is a PCB, its passives SMD | all of it (P79); the bin's `bringup/01..06` never run, no log of a verdict (P73) |
| 11 | PCB and fab — offered once the breadboard works | `emit_board` → tscircuit, `fab.py`, `check_bom`, the review's fab gate | optional, and only after the circuit and the firmware are proven (slice 8) |
| 12 | Enclosure — 3D export, Fusion 360, printed parts | `tsci export -f glb` only | everything past the board's own model (slice 9) |

Two halves: the maker uses spark to *check* a hand-written board; only the cold tests used the
generator. Steps 9–11 hold almost nothing from spark yet.

## The slices, in order

| # | slice | for | done when | items |
| --- | --- | --- | --- | --- |
| **1** | **Public** — a stranger can install it | hobbyist | the repository is public with no vendor file in its history; an unauthenticated clone works; nothing shipped names one person's machine | P71, P44, P75 (done), **B10** |
| **1b** | **From a vague idea** — the walking skeleton's first step | hobbyist | *not designed yet* — the PO's overview: brainstorm a vague idea into what it does and which kinds of module, a schematic first without specific parts | **P76** |
| **2** | **First copper** — the bin on a breadboard | maker | bring-up 01–06 logged with a verdict each; the motor current measured; a `wake_reason()` line after a wave | **P81**, **B1**, **P58**, **P73**, **B8**, **B5**, **B11** |
| **3** | **Firmware fails on a Mac** | both | irrigation's firmware imports without running, and a check reports Valve4 never driven | **P59**, **P74** |
| **4** | **v1 on two named projects** | hobbyist | the documented example and irrigation: `check_spine` exits 0; no `!!`; every `????` names its fact | **P64a**, **P39**, **P38**, **P78**, **P80**, **P83**, **P43** (the `fix` half), **P77** (its place is the council's) |
| **5** | **A real stranger, to running firmware** | hobbyist, tested | a person outside the project, README only, own machine and board, keeps a diary nobody helps with; someone else scores it | **R2.6**, then F3 and F4 as they pull |
| **7** | **Breadboard or wires → perfboard → PCB** | hobbyist | *not designed yet* — the PO's overview: through-hole parts, no SMD, the circuit and the firmware tested on a breadboard; a soldered perfboard build as an optional step; a PCB offered only after | **P79** |
| **8** | **A board you can order** | hobbyist | *not designed yet* — the overview: optional, with the firmware already working | pulled by the first design that wants one |
| **9** | **An enclosure** | hobbyist | *not designed yet* — the overview: 3D export, Fusion 360, printed parts | pulled by the first design that wants one |
| **6** | **Shared, not copied** | everyone | the bin builds with spark's converter, and its CI runs every check against public spark; claims checked against their sources | **P32b**, **P64b**, **P64c**, **B12** |

**The PO, 2026-10-03 — an overview, not a process:** slice 1b comes straight after going public — *"we first need to make it
work, really from just talking about some vague idea"*; slices 8 and 9 make ordering a board and
printing an enclosure part of the journey, optional and after the firmware works.
Slices 2 and 3 run side by side: the maker's share of 2 is parts and a bench, the team's is the
items. **The desk lane** — the PO's own process decisions, at most two open: **P70**, **P72**.

**Parked** (each with what pulls it back, in the backlog): P66, P68, P49, P50, R10, F1, F2, F5.
**Merged:** P2 into P59. **Deleted:** P17.

## Scenarios — and whether each runs today

| | scenario (Given · When · Then) | proof | today |
| --- | --- | --- | --- |
| 1.1 | a machine with no access to Petr's account · `/plugin marketplace add xmejkal/spark` · it installs | an unauthenticated `git clone`; the install in an empty config | **yes** (2026-10-03) |
| 1.2 | spark's whole history · searched for vendor files and secrets · none | `git rev-list --objects --all`, a secrets scan | **yes** (2026-10-03) |
| 2.1 | the bin's firmware README · Petr wires step 2 · every pin it names is in `config.py` | P58's check | **no** — it names the XIAO's pins and a deleted `04_mp3.py` |
| 2.2 | the drawer's audio module · `/spark:identify` on both sides · a record names it | the record | **no** (B1) |
| 2.3 | the bin on a breadboard · `bringup/01..06` · a log per step with a verdict, the motor current, a wake reason | the bench log | **no** |
| 2.4 | the firmware gate · run 200 times under load · no failure, or a named one | the runs, kept whole | **partly** — one failure named in 60 |
| 3.1 | irrigation's firmware · imported with a fake `machine` · it does not start running | an import | **no** — `main()` runs at import |
| 3.2 | requirements that ask for Valve4 and a mode button · the firmware is checked against `pins.py` · both reported | P74's check | **no** — no such check |
| 4.1 | an empty directory and the documented example · init → `check_spine` → `check_all` · exit 0, no `!!` | the commands | **yes, by record** (P51, P57) |
| 4.2 | irrigation · `check_all` · no `!!`; each `????` names what to state | the command | **yes** |
| 4.3 | "something to measure distance" · `parts.py --need` · the rangefinder | the command | **no** (P39) |
| 4.4 | a record with `verified: true` and only a prose source · `--validate` · refused | the command | **no** (P64a) |
| 5.1 | a domain the PO picks · a real outsider follows the docs · a checked board and running firmware; scored by someone else | the diary | **no** |
| 6.1 | the bin's public CI · runs · no line says SKIPPED | the CI log | **no** — spark's four checks are skipped |
