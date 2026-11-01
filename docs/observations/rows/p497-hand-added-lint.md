# P497 hand-added lint: rows

What the P497 plan, its two council rounds and the build found. Card: #681.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Both messages (`Unknown attribute "handAdded"`, "unwired part") come from `@wokwi/diagram-lint` 0.1.1, kept as blocking by `lib/validate.ts`, and `cli.ts` throws `ConversionFailed` (exit 1) | planner | verified | read in `validate.ts` and `cli.ts` |
| 2 | `invalid-attribute` reads every `attrs` key of a part whose type has a known attribute list (`wokwi-led`); `redundant-parts` warns on any part in no connection (boards, custom chips, text, logo, ir-remote are skipped) | planner | verified | repro in the refuter's bun script |
| 3 | `LinterOptions.rules` switches or re-grades a whole rule only | planner | rejected | it would drop the checks on generated parts |
| 4 | Move the mark out of `attrs` | planner | rejected | `merge.ts` reads `attrs.handAdded === "true"`; moving it breaks kept files and the documented format |
| 5 | Lint a copy of the diagram with the mark deleted | plan, round 1 | rejected | each issue carries `context.attrName`; dropping the `invalid-attribute` issues whose name is `handAdded` needs no copy, so the written file cannot lose the mark (`merge.ts` pushes the person's own part object); the copy's mutation row goes away |
| 6 | Take the hand-added ids from the mark in the diagram | plan | rejected | refuter: a generated part whose id matches a hand-added one gets the mark through the attrs merge and would be downgraded; the ids come from the merge summary (`keptHandAddedParts`) |
| 7 | A misspelt attribute on a hand-added part is still reported | refuter, round 1 | verified | `colr` stays a problem; a test pins it |
| 8 | The warning would not reach the person: `check_spine.py` showed only `kept_note(made.stdout)` | refuter, round 1 | acted | `sim_project.hand_added_warnings` reads the converter's `warning:` lines, and `convert()` adds them to the notes; `run()` is at its R1 budget, so the code is in `sim_project.py` |
| 9 | Wording: "<id> is hand-added and has no wire yet: it stays in the diagram, and the build passed. ..." | round 2 | acted | fix round: "and the build passed" is false when the same part also has a problem; now "<id> was added by hand and has no wire yet. It stays in the diagram. Wire it in Wokwi if it should do something." |
| 10 | The plan's `unknown-part-type` stop for a type the converter does not know | plan | verified | the rule exists in the linter's dist; the three docs say it still stops |
| 11 | The bundle `dist/converter.mjs` and its sha go last, after every `.ts` edit | round 2 | acted | `bundle.sh` ran last |
| 12 | The worktree had no `node_modules`, so `bun run test` failed before any change | build | verified | `bun install --frozen-lockfile` in `tools/circuit-to-wokwi` (free, local) |
| 13 | p482 row 19 (a hand-added LED fails the lint) | p482 rows | acted | marked fixed by P497 (#681) |
| 14 | Mutation table: the `handAdded` filter dropped; every `redundant-parts` downgraded; the warning not printed | round 2 | acted | `tests/mutations/p497-hand-added-lint.json`; the full-suite mutation run printed "the suite is not green BEFORE any mutation", so each row was run by hand against the bun tests and the rebuild tests, and all three turn them red |
| 15 | Fix round: the Python side matched the converter's English sentence | lead | acted | `cli.ts` prints `warning[hand-added-unwired]: <sentence>`; `sim_project.converter_warnings` matches the tag shape, never the words; `validate` returns `{code, message}` |
| 16 | Fix round: a failing build could print a warning first | lead | acted | warnings print after the blocking check, so only a passing conversion prints them |
| 17 | Fix round: `bun run typecheck` red at the test file (TS2532) | lead | acted | `!` on the found part and its attrs |
| 18 | Fix round: `validate.ts` redefined `HAND_ADDED_ATTR` | lead | acted | imported from `merge.ts` |
| 19 | Fix round: the Python parser name was specific | lead | acted | `converter_warnings`, `CONVERTER_WARNING` |
| 20 | Row 14's claim that the flash-image tests were red before any change | lead | rejected | not reproduced: `tests.test_flash_image` is green in the worktree and on main. The full discover run showed errors there, cause unknown |
| 21 | Limit the `handAdded` attribute filter to hand-added ids | refuter | rejected | forgiving the mark on a generated part is harmless; its missing wire still blocks (refuter confirmed) |
