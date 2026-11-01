# P482 diagram merge: rows

What the plan, its two council rounds and the build found. Card: #661.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The temp `sim/` is made in `run()` (:530), not at :705; `keep_simulation` copies the temp `sim/` over the project | plan, planner | verified | read in `check_spine.py` |
| 2 | The converter already merges (`readExisting`, `mergeWithExisting`) and prints a summary (cli.ts:133-141), so no TypeScript change and no bundle rebuild | plan, planner | verified | the summary text is the pattern `kept_note` reads |
| 3 | The board-only path (:586) writes its diagram fresh | plan, planner | raised | P484 (#663) moves it onto the converter path |
| 4 | Round 1, blocker: a converter failure was decided only by the missing diagram file, so a failed run beside a copied diagram would pass | refuter (Opus) | acted | `made.returncode or not diagram_path.is_file()`; a test with a faked failing converter |
| 5 | Round 1: copying in `main()` would let `keep_simulation` print a false "wrote" line when the build stops earlier | refuter (Opus) | acted | the copy is inside `run()`, just before the converter; `main()` only links the project's sim folder |
| 6 | Round 1: the merge keeps a wire from a hand-added part to a generated part the requirements dropped, drops a hand-drawn wire between generated parts, and drops a position whose generated id changed | refuter (Opus) | acted | the docs say so (ARCHITECTURE.md, build.md, agents.md) |
| 7 | Does diagram-lint refuse a kept wire to a generated part that the requirements dropped? | refuter (Opus) | raised | the dangling wire row: not tested; a later card if it reaches Wokwi |
| 8 | Round 1: the summary counts every matched id, so the note must not say "moved" | refuter (Opus) | acted | the note says "part positions" |
| 9 | Round 2: `main()` (82) and `run()` (208) have their own R1 baselines | council (Sonnet) | acted | `main()` 81 and `run()` 208 lines; module 1029 (baseline 1030), by shortening three comments |
| 10 | Round 2: a diagram that is not valid JSON gets a verdict note, not a silent rebuild | council (Sonnet) | acted | `copy_kept_diagram` returns the note; `{}`, `[]` and a non-list `parts` count as not a diagram |
| 11 | Round 2: the docs say a generated part that the person deleted comes back | council (Sonnet) | acted | in the three docs |
| 12 | Round 2: names `copy_kept_diagram` and `kept_note` | council (Sonnet) | acted | one word "kept", beside `keep_simulation` |
| 13 | The plan said `run()` gets the simulation folder; `run` already takes 6 parameters (R3 baseline 6), so a 7th would raise a baseline | build | verified | `main()` links the folder as `workdir/"kept-sim"`; `run()` reads it. `kept_into` copies only `*.tsx` and `dist/`, so the link is never copied to the project |
| 14 | A hand-added part of a type Wokwi knows attributes for (`wokwi-led`) fails the converter's own lint: `Unknown attribute "handAdded"`. The build stage now says "no diagram was produced" with that line | build, real run | raised | the merge keeps `handAdded` parts, but the lint refuses the marker on a typed part; the test uses `wokwi-gnd`, which has no known attributes. A card to let the lint skip `handAdded` (needs cli.ts or lib/, so the bundle's sha) |
| 15 | The anchor count `--anchors` is 120 refused on main before this change, not 119 | build | verified | the same 120 with and without the change |
| 16 | The `--sim-dir` mutation row has no test that builds with `--sim-dir` (a 10 s real build) | build | raised | the row may escape; the symlink line is shared by both paths |
| 17 | `run()` reads the kept diagram through a hidden link named in two places | PR reviewer 1 | acted | `main()` now copies the person's `diagram.json` to `sim_project.KEPT_DIAGRAM` in the work folder, and `run()` copies from that file; nothing points into the project (the refuter found the link safe, the file copy is simpler) |
| 18 | A kept diagram with a parts list but no connections list is a Wokwi diagram | PR refuter 2 | rejected | merge.ts calls `existing.connections.find` and crashed in a real rebuild; `copy_kept_diagram` now requires a connections list and parts that are objects; tests and a mutation row |
| 19 | The docs say hand-added parts stay | PR refuter 5 | acted | fixed by P497 (#681): a hand-added `wokwi-led` fails the converter's lint (`Unknown attribute "handAdded"`) and so does a hand-added part with no wire; the three docs said so, and P497 removed that: the lint passes the mark and warns on an unwired part |
| 20 | The --sim-dir mutation row has a test | builder row 16 | rejected | no test builds with --sim-dir; the row now drops the copy in `main()`, which the double build catches |
| 21 | A first build is unchanged byte for byte | PR refuter 4 | raised | with no kept diagram the converter prints no summary and the note is empty; no byte diff was run |
