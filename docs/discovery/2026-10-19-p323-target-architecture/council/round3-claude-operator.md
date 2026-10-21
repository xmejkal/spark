# Round 3: the Claude operator walks walk 1

## What the target gives me

Each door has `--describe`, one envelope, a `code` per problem, `next` steps with `needs_yes`, and `crash` as exit 2. That is a real gain over today, where I read 750 lines of agents.md and 300 lines of build.md to learn flags and JSON keys.

## Walk 1 in brief

init, drawer and idea have no `--json` in the target list, so I parse text there. Build's fix lines are text. Firmware has no Operation. check_all has its own answer shape. Only `look` gets codes (slice 3). Deploy keeps the yes with the person.

## Gaps and fixes

**G1. Discovery needs two reads.** `--describe` exists per door. No call lists all Operations. I must know a door's name first, from a page. Fix: `spark.py --describe` is not needed. Instead add one generated file, `docs/guide/operations.md`, from the `OPERATIONS` tuples by `tools/measure.py`, and a test that it is current. One read, about 150 lines, replaces the "commands" table in agents.md. No catalog code, so D3 holds.

**G2. Where am I (backlog 13).** The design never mentions `loop_status`. After a change ("add a second LED") I cannot tell which of build, firmware, checks, scenario, sheet and image are stale. I would rerun all, or guess from timestamps. Fix: make `loop_status` Operation number two, in `build/operations.py`, right after `look`. It reads only files and returns per stage `done`, `stale` or `missing` with a `code`, and `next` steps. It needs no new facts, only mtimes and the existing `dist/` and `sim/` files.

**G3. Command pages still repeat logic.** Examples: build.md's list of which `kept` lines to read and how to explain a fix, idea.md's order of calls, and the install-then-rerun rule (build.md line 152). Fix: every problem and unchecked code gets a `fix` step with `op` and `argv`, so the page says "run the `next` step". The missing-tool case is a code `tool_missing` with a `next` step `tools.py --install` marked `needs_yes: true`. Then the page loses the paragraph. Slice 3 should do this for build, since build.md is the longest page (303 lines).

**G4. Text still parsed.** `init_project`, `drawer`, `idea` text blocks, and fix lines in `build`. Fix: slice order below, and a rule in the standard: an Operation that a command page calls must have `--json`. Add that to S10 as the door's own test, so a door without it is a baseline entry.

**G5. Tokens wasted.** Keep `codes` and `data` in `--describe` only, not in each envelope. Let `check_all --json` print problems only, with `--all` for the rest. Move the 160-line "what never to assume" rules into each code's `meaning` string in `--describe`.

**G6. A script's output changing during the migration.** The design promises goldens per Operation, but only from slice 2. Ahead of that I have no guard on `check_spine`, `check_all`, `build`. Fix: slice 1a adds golden `--json` runs of the demo project for those three plus `deploy --dry-run`, since they are what walk 1 calls. New envelope keys are additive only, and a page edit ships in the same PR as the code that replaces its text line.

**G7. Missing codes.** A list for the walk: `tool_missing`, `no_project`, `no_requirements`, `no_board_record`, `no_port`, `port_busy`, `image_stale` (the image no longer matches the passed simulation), `needs_yes`, `sim_failed`, `crash`. `image_stale` matters most, since "add a second LED" must stop deploy from flashing the old image.

**G8. The person's steps.** Goal words in idea, picking parts, the deploy yes, plugging the USB cable, and the PO's bench. Each should appear in `next` as `needs_person` with a one-line `why`. Today `needs_yes` covers only consent. Add `needs_person` to `outcomes.step`.

**G9. Firmware.** Nothing checks that firmware imports the pin map. Fix: a `firmware_pins` Check in `check_all`.

## Order that gives Claude value first

1. Slice 1a, with the G6 goldens.
2. `look` (slice 2, as planned) and slice 3's codes.
3. `loop_status` (G2). Biggest win for every later walk.
4. `build` and `check_all` envelopes with codes (G3, G5). They are the loop's hot path.
5. The generated `operations.md` (G1), then retire the matching agents.md text.
6. `idea`, `init`, `drawer` last. They run once per project.
