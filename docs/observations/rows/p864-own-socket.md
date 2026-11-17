# P864: the DFR0954 says its speaker outputs end in its own socket: rows

Card: [P864 #1230](https://github.com/xmejkal/spark/issues/1230), a story. New logic: a plan council of two rounds (one lens
on Sonnet, the refuter on Fable, who read the drawing and ran a stand-in of the whole suite in round 2) and a build to the plan.
This file holds the acted and raised findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | C1: the record block is exactly the council's, and its `source` says only what page 1 shows (no "JST"; no wire drawn) | plan council, round 1 | acted | `own_socket` in `parts/max98357a-dfr0954.json`, `verified: false`, `cites` the drawing's key |
| 2 | C2, D4: the validator goes through `RECORD_TYPES`; a block that is a list or a string never crashes a reader | plan council | acted | `own_socket` in `RECORD_TYPES`, `own_socket_problems` for the rest; a test per malformed block |
| 3 | C3: no new module and no class | plan council, round 1 | acted | one function, `part_facts.own_socket_pins`, and its docstring line (D6) |
| 4 | C4, D1: `own_socket` does not join `BUILD_FACTS`; nothing reads a digest to call a build out of date | plan council, round 2 | acted | `BUILD_FACTS` unchanged; the `PROVENANCE_KEYS` line keeps its old text (`... + ("own_socket",)`), so no older row moved |
| 5 | C5: the filter and `own_socket_ends` in `power_rails.py` | plan council, round 1 | acted | `_unreceived` is the one walk; the two public functions are filters of it |
| 6 | C6: a comment in place of the trace; `power_note_lines` is not touched | plan council, round 1 | acted | `module_power_lines` |
| 7 | C7, D2: two before-power kinds with the item's `pin` field, and the words of the council | plan council | acted | `own-socket` and `own-socket-unverified`; the HTML follows from `TEMPLATES`; the hand list of kinds in `test_flow_page.py` grows by the two |
| 8 | C8: later steps renumber when the SPEAKER traces are gone | plan council, round 1 | acted | said in the PR |
| 9 | C9, D5: tests cut the amplifier fixture in code and fail on main; the `islands_in` test is a pin | plan council | acted | `fakes.amplifier_alone`; the pins are named as pins in their tests |
| 10 | C10: only `test_needs.py:2881-2891` changes, onto a copy `x-amp` | plan council | acted | named in the PR under "An existing test changed" |
| 11 | C11, D3: the bench result needs a command | plan council, round 2 | acted | `own_socket` in `drawer.PROVENANCE_KEYS`; `scripts.md`, `parts-researcher.md`, `idea.md`; the refusal sentence of `--fact-set` is pinned by a golden and stays |
| 12 | C12, D7: the PR says what is not proved, and that the no-socket case cannot be built without a `speaker-terminal` | plan council | acted | the PR body |
| 13 | R1: the PR broke the anchor of the p737 row on `PROVENANCE_KEYS` | PR refuter | acted | the line keeps its old text; the P864 row re-anchored; every file under `tests/mutations/` compared with main: no anchor that passes on main fails here |
| 14 | D1, D2: `json.md` lists `own_socket` among the `write` keys; the `how-it-works.md` cell says an output in its part's own socket is no note, in 300 characters | PR lens | acted | docs |
| 15 | W1: the board-file comment says "the record says" while `verified` is not true | PR lens | acted | two comments by the record's `verified`; a test for each |
| 16 | W2: the verified sheet line is true for one pin as for two; the unverified one ends "the pads {pin}" | PR lens | acted | the templates and a one-pin test |
| 17 | W3: the PR body does not state the socket as a fact | PR lens | acted | the PR body |
| 18 | T1: the filter matches the part and the pin | PR refuter | acted | a pin: the code already did it; a test with a second part |
| 19 | T2: `verified` is the JSON true or false | PR refuter | acted | two more malformed blocks; `own_socket_pins` is empty for a `verified` that is no bool; a `verified` that is no bool gives no socket: a gap and a trace, as with no block |
| 20 | T3: what `RAILS_THE_MODULE_PROVIDES` leaves out in `_unreceived` | PR refuter | acted | a pin test on an output on the logic rail |
| 21 | T4: the pins of one socket share one rail | PR refuter | acted | a problem when they do not; `parts-researcher.md` says it, and what `cites` and `source` hold |
| 22 | B1: one real build of the amplifier alone | PR refuter | acted | `TheAmplifierAloneBuildsForRealTest`: build ok, 8 traces, 0 errors; no terminal and no SPEAKER in the circuit; the simulation stage is skipped (not a pass) |
| 23 | thirteen older mutation row files refuse an anchor on main (p124, p190, p219, p458, p462, p468, p484, p507, p677, p737, p778, p802, sprint-7-p51b) | plan council, round 2 | raised | P897 #1273 |
| 24 | the schematic PDF that the record's notes name is not in the store; the record's older words say "JST"; "looked, not there" cannot be written by `--fact-set`; the refusal sentence omits `own_socket` | plan council, PR lens | raised | a line on P735 #1010 |
| 25 | a look at the real module | plan council | raised | a line of the PO's first bench sitting |
| 26 | half a bridged pair is wired when one SPK pin is received and the other ends in the socket | PR refuter | raised | dropped because: reached only with a hand-made receiver record; both the trace and the sheet line are true |
