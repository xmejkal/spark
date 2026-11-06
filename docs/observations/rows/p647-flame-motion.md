# P647 flames in fixed columns: rows

What the plan refuter, the Mac clips, the PO's looks and the finding's review found. Card:
[P647 #869](https://github.com/xmejkal/spark/issues/869). PRs: https://github.com/xmejkal/pixel-games/pull/45 (the
finding) and the draft prototype https://github.com/xmejkal/pixel-games/pull/44.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The page has nowhere to load the GIFs from: both repositories are private, and a 100-frame GIF is about 2.2 MB | the plan refuter (Fable) | acted | the GIFs went up as files of the Artifact itself (`publish_files`) |
| 2 | The heat shift `D(y) - D(y+1)` is right only for the row below; the far read and a fast cell's reads are two and three rows down | the plan refuter | acted | per read `d[k] = D(y) - D(y + k)`, k 1 to 3 |
| 3 | Wander alone keeps the heat rising straight from the spots, and one wave bends every column at once | the plan refuter | acted | said on the page; the clips confirmed both (rows 6 and 7) |
| 4 | `map_x`, `phase` and `drift_v` hide their unit or role | the plan refuter | acted | `map_dx` (1/256 cell), `tick`, `drift_vx` |
| 5 | `map_x` grows without bound | the plan refuter | acted | masked to 16 bits; `tick` wraps at one wave |
| 6 | Bend 4 with one wave for the whole field makes a regular zigzag; bend 2 looks natural in one frame | the Mac clips, round 1 | acted | then the PO: "the flames should not always bent the same all at once" (row 8) |
| 7 | Wander 64 and 160 leave the columns in the 100-frame average: the heat rises straight from 12 spots that walk 1 cell at a time | the Mac clips, rounds 1 and 2 | acted | the finding names the spots as the second cause; P649 #871 for a real flow |
| 8 | One wave for all columns does not look natural | the PO, 2026-11-06 | acted | each stretch of 16 columns takes its phase from the cooling map's row 0, mixed linearly |
| 9 | Every number a setting, less bend, more wander | the PO, 2026-11-06 | acted | `fx_fire_set_flow(bend, rows, steps, width, wander)`, wander 0 to 1023; wander 512 and up blurs the columns |
| 10 | The motion is a fluid: physics and graphics reusable for water and other materials | the PO, 2026-11-06 | acted | P649 #871 (spike, Idea, under P609 #812) |
| 11 | Do not spend long on code that P649 redoes | the PO, 2026-11-06 | acted | the review and the mutation run of the prototype were skipped; it stays a draft; story P650 #872 is refined after P649 |
| 12 | The per-cell bend breaks the byte rows that P601 #802's 16-byte vectors need | the lead, from the code | raised | the finding's cost section and P650's notes |
| 13 | A test's heat buffer was freed while the C field still stepped, and the suite aborted with exit 134 | the lead's test run | acted | the test keeps the buffer on the field (`f.keep_heat`) |
| 14 | A new worktree of the games repository lacks `engine/driver`, a nested submodule; `git submodule update --recursive` aborts on the engine's local changes | the lead | acted | `git submodule update --init` inside `engine/` |
| 15 | The finding's reviewer (Sonnet, `feature-dev:code-reviewer`) had no shell, so it could not read a file that lives only on a branch | the review, round 1 | acted | the lead copied the finding to the scratchpad and resumed the same agent. Brief a reviewer with a readable path, or pick an agent type with Bash |
| 16 | "about five table reads" is six (two map reads for the phase, four sine reads); only the cooling map reads `x & 255`, the fast map `(x + 128) & 255`; the spots also jump 1 step in 64 | the review, round 2 | acted | fixed in the finding before the merge, https://github.com/xmejkal/pixel-games/pull/45 (c9e1045) |
| 17 | The flow's header comment ran to 196 columns and still said "one sideways speed per row" after the bend became per cell | the review, round 1 | acted | rewrapped and corrected on the prototype branch (pixel-games 97e7483) |
