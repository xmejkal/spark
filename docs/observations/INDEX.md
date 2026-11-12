# What the observations found, and what happened to it

Until 2026-10-18 every review wrote its findings here (P296, #358 moved them to one rows file per card under `rows/`). On
2026-11-12 P776 ([#1074](https://github.com/xmejkal/spark/issues/1074)) read the 274 rows of this table that were still open: 44 were
a card, 10 fixed since, 200 notes about plans, counts, wording or code since rewritten, and these 15 still name a gap a person
building a board meets. The rest is deleted; `git log -- docs/observations/INDEX.md` holds every row. A row leaves this table
when a card takes it. New findings go to `rows/<card>-<topic>.md`, never here.

## Status, and what each one obliges

| status | meaning | what has to happen next |
| --- | --- | --- |
| `raised` | an observer claimed it | reproduce it, or reject it |
| `verified` | reproduced here, by running something | put it in `BACKLOG.md` or fix it |
| `acted` | fixed, or in the backlog with a named item | nothing; keep the row as history |
| `rejected` | reproduced and found wrong, or judged not worth doing | nothing; **keep the row**, so it is not raised again |
| `closed` | true and needing nothing — a confirmation, a measurement of the past, or work superseded by later work | nothing; keep the row as history. Added 09-29 (audit B15): before it, these sat under `acted` |

`rejected` matters as much as `acted`. An observer that is confidently wrong will be wrong the
same way next time, and a claim with nowhere to retire comes back every run.


## What still waits (P776, 2026-11-12)

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| K13 | A project's own copy of a record falls behind spark's silently (rc-car's `tactile-button` lacks two of spark's four later improvements), and a record the project does not copy changes under it. | P158 part 1 catalogue, 2026-10-10 (#17 (P94), P148, P149, P150) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K13 and `diagnosis/store-levels-and-holds.md`; severity guess: harms silently; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K23 | `physical.pad_aliases` is undocumented and does not reach the footprint. | P158 part 1 catalogue, 2026-10-10 (G0.4) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K23 and `diagnosis/board-records.md`; severity guess: blocks the journey; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K24 | The `physical` schema is documented nowhere: how-it-works.md sends the reader to boards/README.md "for the format", which carries no schema for `physical` (`flush_edge`, `row_<n>`, whether `drill_mm` is required, nulls. | P158 part 1 catalogue, 2026-10-10 (G0.2, P127 #61, P0.6) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K24 and `diagnosis/board-records.md`; severity guess: friction; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K25 | `pin_roles` is a closed list documented nowhere, learnt from a refusal (`pin_roles.jtag is not a role any script reads … Known`. | P158 part 1 catalogue, 2026-10-10 (G0.5) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K25 and `diagnosis/board-records.md`; severity guess: friction; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K26 | Repeated and NC pads have no documented form. | P158 part 1 catalogue, 2026-10-10 (G0.10) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K26 and `diagnosis/board-records.md`; severity guess: friction; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K27 | The generated footprint's header prints `The holes are 1.00 mm, NOT the ? mm on the vendor drawing.` when `drill_mm` is absent, and mounting holes are recorded but not emitted. | P158 part 1 catalogue, 2026-10-10 (G0.2 tail, round 0 diary 18:24) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K27 and `diagnosis/board-records.md`; severity guess: polish; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K31 | What the dev board gives for free has no record, so needs the board itself serves show as gaps: `report / communicate / wifi` → "nothing in the store does this — a gap" (the S3 has WiFi). | P158 part 1 catalogue, 2026-10-10 (USER-4, USER-6, FEAS-4, FEAS-5, PHYS-4) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K31 and `diagnosis/board-records.md`; severity guess: misleads; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K39 | A need holds one pick: four valves and three probes become one pick plus "kept" entries, so the store never learns that irrigation uses 4 × DFR0457 and the reservation counts one. | P158 part 1 catalogue, 2026-10-10 (FEAS-8 (2)) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K39 and `diagnosis/needs-matching-vocabulary.md`; severity guess: misleads; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K43 | The ways in beyond goal-first — extend, swap, module-first, combination, whole-drawer, revive — have no verb: `--match` scores needs, not projects. | P158 part 1 catalogue, 2026-10-10 (PO-7, P76 #5, FEAS-8 (the "simple sense" that runs)) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K43; severity guess: blocks the journey; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| K44 | Choosing among equivalent owned modules does not exist: a pick for a need does not list every owned module with that function, nor recommend the minimal one. | P158 part 1 catalogue, 2026-10-10 (P157 #93, FEAS-1, FEAS-3) | **raised** | see `docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md` K44 and `diagnosis/needs-matching-vocabulary.md`; severity guess: friction; ranked in P158's proposal (`docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md`) |
| BB8 | Off the board, the motor, the battery pack and the board's own power are listed nowhere, and the inlet has no `legs` for its plus contact | P191 council, 2026-10-11 (U-7, PA-4; fix) | **raised** | P191 ([#143](https://github.com/xmejkal/spark/issues/143)): partly: a supply from off the board is now named (BB22); the motor, the pack, the board's own power and the inlet's `legs` are raised, since the records do not say them yet — see `2026-10-11-p191-council.md` |
| BB10 | A JST PH 2.0 mm inlet does not fit a breadboard | P191 council, 2026-10-11 (PA-3; fix) | **raised** | P191 ([#143](https://github.com/xmejkal/spark/issues/143)): raised with BB8 — see `2026-10-11-p191-council.md` |
| CC1 | The resistor-power rule looks only at resistors with an end on a rail, so the LED's series resistor (GPIO to anode) is never assessed, and physics reads `ok` over it | P197 build, 2026-10-12 | **verified** | acted, the PO's choice of 2026-10-12: physics assesses every resistor. Was: `check_physics.check_resistor_power` looped `components_on(rail)`; on the fresh button-and-LED board `LedRed5mmSeriesA` is on no rail. The P197 bound would clear it at 3.3 V, but on a board with a 6 V rail a 330 ohm 0603 would turn could-not-run |
| AT52 | P229 E4: The boards README's "Adding a board" steps are the smart bin's | P229 walk (`docs/discovery/2026-10-13-p218-deploy-and-board/bench/p229-xiao-board.md`), 2026-10-13 | **raised** | for P230's discovery (#218) and P229 (#217) |
| AT53 | P229 E5: The board schema is not written down | P229 walk (`docs/discovery/2026-10-13-p218-deploy-and-board/bench/p229-xiao-board.md`), 2026-10-13 | **raised** | for P230's discovery (#218) and P229 (#217) |
