# P945: a module with no Wokwi part is drawn from its record's physical facts: rows

Card: [P945 #1348](https://github.com/xmejkal/spark/issues/1348). This file holds the acted, raised and rejected findings
only. The plan check: one lens on Sonnet and the refuter on Opus; the lead's revisions decide where they differ from the
plan. Then the build's own findings. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | one row along an edge needs a second number, `physical.header.inset_mm`, the row's distance from the edge | the plan, finding 1 | rejected | the lead: the done-when says one new field, and the refuter ran the planner with 0, 1.27 and 2.5 mm: the same pins, covered holes and free groups. The pads sit half a pitch inside the edge, an assumption in the placer's docstring and the record's source |
| 2 | no `HeaderPlacer` base and no `BoardHeaderPlacer`: the board's path stays as it is | the plan check | acted | `OneRowHeaderPlacer` goes straight into `ModuleShapeSource`; `RecordShapeSource` is unchanged |
| 3 | the fixture is the walk's real record, with its physical block and `short_name` "e-paper" | the plan check | acted | `tests/data/breadboard/epaper/parts/`: a project's own parts folder, because the loader reads a part there, not `tests/data/parts/`. Its provenance is in `physical_proof`, since the part contract keeps `physical` to bare values. Searched for a home path and a secret; no photo |
| 4 | each pin maps to its printed pad (DC to D/C), so the planner finds every pin | the plan check | acted | `find_pin_names` from `needs[].printed` and `power[].printed`; a test plans the pin DC into the pad D/C |
| 5 | the picture names the module by its short name, not its component | the plan check | acted | `part_px["name"]`; a test |
| 6 | `flush_edge` has one meaning on a board and a module | the plan check | acted | the module frame is written in `OneRowHeaderPlacer`'s docstring |
| 7 | `End`'s docstring called an end's label its short name | the plan check | acted | it says "end label" now, so `short_name` has one meaning |
| 8 | a new `_end_key` shape would change every part end's key in every old wiring-record.json | the plan check, refuter | acted | the lead: `_end_key` stays `(kind, words)`. A project whose record gains a short name sees its ends as changed once: the walk's copy printed 8 `changed` lines on its first rebuild |
| 9 | the `no_drawing_fact` sentence names both ways to draw a part | the plan check | acted | `NO_DRAWING_MESSAGE`; the regex of `test_breadboard_layout`, the not-drawn golden and the motor sheet change with it |
| 10 | the kept entry's fix only when a record is known, never `--part None` | the plan check | acted | `not_written_entry`; a test of both cases and a mutation row |
| 11 | commit 1 builds the module's part_px by hand | the plan check | acted | the spike commit says so; commit 4 swaps the helper for the build's own inputs |
| 12 | "Holes: e12 to e14" reads as e13 too for a button whose pins are e12 and e14 | the build | acted | a range covers only neighbouring columns: "e12, e14, j12, j14"; a test and a mutation row |
| 13 | `drawing.py` grew to 730 lines and `kept_files.py` to 617, over rule R1's 600 | the build | acted | the SVG renderer moved to `svg_diagram.py`, the research step to `build_board.py` |
| 14 | a `physical` entry in `RECORD_TYPES` replaced the part contract's own sentence for a `physical` that is no object | the build | acted | the entry is dropped; the contract checks the block, and the source refuses a face or an edge that is no string |
| 15 | the part contract refuses `physical.header_order` on a module (`PHYSICAL_KEYS`), so a module's labels come from `pin_order` only | the build | raised | to file as a card (the lead): a module whose header order is not its `pin_order` needs it |
| 16 | the steps name a pin as the circuit does ("e-paper DC") while the silkscreen prints D/C | the build | raised | to file as a card (the lead); the picture and each step's holes show the printed label today |
| 17 | page.html's step data has no holes, so the page and the sheet differ | the plan, risks | raised | [P887 #1257](https://github.com/xmejkal/spark/issues/1257), the guide-first page |
| 18 | "breadboard.json not written: Wokwi has no part with this board's pins" names the board when a module is the part Wokwi lacks | the build | raised | to file as a card (the lead); true for the FireBeetle, whose record has no Wokwi part either |

The rows: tests/mutations/p945-module-drawing.json.
