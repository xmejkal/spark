# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

Prefix P, next free number P665 (read from `gh issue list --state all` on 2026-11-07: the newest is P664). Numbers below are placeholders until filing. The repository has `.github/ISSUE_TEMPLATE/item.yml` (the refuter listed it). It was not read in this step, so each block carries the core card plus the board's fields. The Slice is proposed as the board's "v0.10 The basic journey", because P663's parent P100 #6 sits there. The order of the stories follows Q2. If the PO says bridge, P665 goes first. If not, the design move goes first.

## P663 #892 — spark has no general way to handle pin conflicts → one conflict model in the core, shown and asked in every interface (the epic)
- type: epic (it carries the `epic` label today) <!-- REQUIRED:item-type -->
- needed by: "lets'have a good thought through general approach t conflicts like that, how each interface deals with it, the core, etc." (the PO, 2026-11-07, #892) <!-- REQUIRED:needed-by -->
- value proven by: `check_spine.py requirements.json --keep .` on the P581 project builds with no two claims on one pin, each conflict named or asked once, and a fixture per kind under tests/ <!-- REQUIRED:value-proven-by -->
- depends on: P664 #893 (the 300 s build time limit: the proof's build stops at 300 s today, P581 row 5), P460 #628 (the connector shape), P527 #726 (the strap), P660 #886 (the kept board), wave 6's design move (D2, Q2) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P100 #6 (as today) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, or ask the decider for a new one ("Pin conflicts") <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P665 — a left pin conflict is silent or one sentence → the assigner stops on K1, K2 and K5, names both claims, notes K3 on the run and the pin, and `--json` answers in JSON with a code (the walking skeleton, option C of D1), with D7: a strap named with no connector warns, and `accept_strap` on the signal lets it through
- type: story
- needed by: "A check that reads the record's taken pins stays as a safety net" (the PO's words in #892, D1, 2026-11-07)
- value proven by: `assign_pins.py --json` on a fixture per kind exits 1 with a JSON object that holds `code`, both claims and the pin. A K3 fixture exits 0 with a note. K3 is never a stop (PH-5, PH-15), pending Q10. The P581 file stops on GPIO18, GPIO9 and GPIO38 instead of exit 0 (★C4)
- depends on: P664 #893 (the 300 s build time limit, because the Outcome's proof is that build), D6 (a bridge on today's `assign_pins.py`), Q4 (the shape and exit code), Q10 (the K3 note), the connector fact (P460 or the part fact as a bridge)
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## P666 — the board record has no connector → the FireBeetle 2 record holds the GDI connector's pins with the schematic page cited, and the screen's record says it plugs into GDI
- type: story (the finding of spike P460 #628 applied)
- needed by: "we should have this noted because the firebeetle 2 and the displays have it" (the PO, walk 4, 2026-11-01, W4:24)
- value proven by: `boards.validate` passes the record. A reader lists the connector's eight GPIOs with `verified` per pin. The A1 check (the pins against the kept V1.3 schematic) is in the PR
- depends on: P460 #628 (its spike answer), Q7 (unverified pins allowed or not)
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## P667 — a part that fits a board's connector goes on wires → spark places it on the cable by default, says so in one line, and one line on the part in the requirements file ("wires") changes it (D4)
- type: story
- needed by: "ask 'cable or wires?' then place the connector's pins first" (the PO, D1, 2026-11-07), narrowed by D4 (2026-11-07) to a named default with no question
- value proven by: on P581, a run with no line places the screen's 8 pins on the GDI cable, DC on GPIO3 with the strap named (P527 #726), and prints one line that names the cable and the override. A run with "wires" on the part places the screen like any part. Neither run asks a question (D4)
- depends on: P665, P666, P527 #726, Q9 (Strategy or rule). Q3 is answered by D4
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## P668 — the sheet lists a wire per pin and knows no cable → the sheet says "plug the ribbon cable" for a part on a connector, and `pins.py` names the second job of a shared pin beside it
- type: story
- needed by: "the sheet says plug the ribbon cable" (the PO's words in #892, 2026-11-07)
- value proven by: `breadboard.md` of the P581 project holds the cable line and no wire for DC, CS, RST, SD_CS or BL. `pins.py` names `ONBOARD_LED` beside `TFT_BL` on GPIO21 (★C7)
- depends on: P667, P660 #886 (a kept board after a pin change). If the onboard half lands in P332 #426 (Q6), that too. The onboard half partly overlaps the body of P460 #628 (G31: it leaves `ONBOARD_LED` out of `pins.py` while a connector claims GPIO21) and touches P491 #670. Cite them, do not duplicate
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## P669 — Spike: does one shape (a claim on a resource) cover K1, K2, K3 and K5? → a one-page table of the four kinds against `Claim`, `Resource`, `Conflict`, with the rules left over counted (the A2 test)
- type: spike
- needed by: "design with good architecture respecting what we want from the architecture" (the PO, 2026-11-07, #892)
- value proven by: the table, with the count against the pass line set 2026-11-07 (at most one per-kind rule left over). A finding with the names checked against `docs/guide/patterns-and-names.md` and `GLOSSARY.md` (Q8)
- depends on: —
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## P670 — Spike: what does a part's pin hold at reset, and which record holds it? → a finding on the reset-time level and direction per part pin (driven, Hi-Z, floating, pulled) for the screen, the amplifier and the camera, with the datasheet pages
- type: spike
- needed by: "Maybe there can be more scenarios we didn't think about" (the PO, 2026-11-07, #892). The Physics lens: only the boot-affecting and two-driver kinds need it (PH-15, PH-16)
- value proven by: a finding that says which of K1 to K7 a severity per kind can tell apart by data, and which only a person can. Not code
- depends on: Q10 (is a severity in the first slice at all)
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one, or a later slice

## P671 — one refusal, two exit codes → `assign_pins.py`, `emit_board.py` and `check_spine.py` give one refusal one code, and `docs/guide/agents.md` says which
- type: bug (found on the way, F1)
- needed by: "A `could-not-run` or a `skipped` is not a pass" (AGENTS.md, the never-assume rule). No PO words yet
- value proven by: the three scripts on one K5 fixture exit with the same code, and `docs/guide/agents/json.md` (or `docs/guide/agents.md`) says which code a refusal gets. `agents.md:131` is not the defect: it is about input a script cannot read
- depends on: Q4
- status: proposed
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P663 #892. If the PO keeps it a standalone bug, none
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## P672 — the board record marks straps 0 and 3 only → add straps 45, 46 and JTAG 39 to 42, with the datasheet page cited, to the FireBeetle S3 record (the rest is P281 #323)
- type: story (found on the way, F2). P281 #323 (open, the FireBeetle S3 record's USB and flash pins) covers two of the four groups (USB 19, 20 and flash and PSRAM 35 to 37). If the decider prefers, this is "add to #323" and no new card (Q6)
- needed by: no PO words yet. The Physics lens: "a connector record that fixes camera pins on IO45 or IO46 has nothing to be checked against" (PH-8)
- value proven by: `boards.validate` passes, and the camera fixture's XMCLK on IO45 is refused or named as a strap
- depends on: P281 #323, Q6 (board record or chip record, physics Q3). Not in the first slice (RI-8)
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P663 #892
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## P673 — `assign_pins.py --json` without `--project` prints a `note:` line before the JSON → every note goes to stderr when `--json` is on
- type: bug (found on the way, F6)
- needed by: no PO words yet. The UX lens's run (UX-4)
- value proven by: `assign_pins.py req.json --json | python3 -m json.tool` parses
- depends on: —
- status: proposed
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file the nine items above as sub-issues of P663 #892 (P673 standalone) · pending, needs the PO's yes to this list
- run `tools/check_backlog.py` after filing · pending
- change `scrum/STORY_MAP.md` by the delta in story-map.md in the same change as the board's Slice field · pending
- none taken <!-- REQUIRED:board-actions -->
