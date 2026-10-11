# P158 part 2 — refuter, round 2, targeted (2026-10-11)

## Iteration 1

I0 ends in a whole that runs by construction (H0a, Hf0: 0 changed lines). The bin's cited `Makefile` lines exist as quoted.

- **fix** — a false green the whole cannot see. `SPARK ?= $(HOME)/Development/spark` (`Makefile:26`), `HAVE_SPARK := $(wildcard …)` (`:33`): `make check` on a scratch copy tests that checkout, not the card's worktree; with none there it prints `SKIPPED`, exit 0 (`:34`). Change: I0's whole and constraint 10 say `make check SPARK=<worktree under test>`; C1's snapshot fails on any `SKIPPED: needs the spark plugin` line.
- **fix** — H0b's pass line is refuted by today's code. Control mutant `EXIT_PROBLEMS = 0` after `check_bom.py:47`, on a scratch export of `5acbe42`: `test_check_bom.py` → `Ran 17 tests … OK`; `test_outcomes.py` → `FAIL: test_every_script_answers_in_the_one_vocabulary … AssertionError: 0 != 1 : check_bom`. `tests/test_outcomes.py:61-64` pins every script's constant to `outcomes` (0/1/2 at `:32`); `EXIT_MISMATCH = 0` is caught there and at `test_check_vendor_pins.py:159`. Change: replace both now with behaviour mutants on the bin's argv (`check_bom --circuit` contradiction → `EXIT_OK`; `check_vendor_pins --offline` mismatch → `EXIT_OK`); keep `check_physics`'s. Retitle C5: the gap is the call paths, not the constants.
- **fix** — "set before the work" carries two dates: design §12.3 "2026-10-11", plan's Iterations "2026-10-10". Change: one date and the commit that froze them.
- **suggest** — H0c can fail (n = 1, second reader). §12.3's "no code" is wrong: C13 is S–M of code.

## The first ten cards

- **fix** — order: rank 1 (CH-16) is C17, behind C15's frame, though part 1 says CH-16 "depends on —" (`proposal.md:618`) and §12.1 pulls fix cards by part 1's hard edges only. See *The one change*.
- **fix** — reuse: C8 says "reuses none (#10 is CH-53, C99)", but part 1 gives CH-18 "**card** #10 (P39), its first step" (`proposal.md:670`), and #10's body is C8's fault ("A miss then prints 'Research it'"). Change: C8 reuses #10 as its first step; C99 closes it.
- **suggest** — C7: "reuses none (#65 is the fix, C21)"; design §12.2's I0c-3 row reuses #65. Align them.
- **suggest** — one concern: C3 holds three (load refusal, `--rows-in`, a ≈12.3 h sweep that takes a slot); C10's `note_built` sentence and `test_a_build_of_an_unlisted_project_says_it_was_not_recorded` are a second concern. Split.
- All ten name tests and a failure line (C2: no code). Value lines measurable; C5's wrong (above).

## Decisions for the PO

- **fix** — DP19 is already decided: the PO, 2026-10-11, *"Size it to the change"* (#131; commit `914b48d`, after `5acbe42`), `scrum/README.md:216-222`: the light council for under about 50 lines. Change: drop DP19, and re-estimate §12.1's "53 council-days, about 4.8 billion tokens".
- **suggest** — §0's words exclude DP4 (c) (0.1, *"tolerates problems but informs about it"*) and DP15 (b) (0.7, *"not starting new epics or bigger things"*). Strike both. DP12, DP13 give no reason. DP21 (b)'s "standard library only" is the design's reading of §0.7, not his words.
- The rest are real choices, each with options and a recommendation.

## Code claims

1. `tools/mutate.py:88` — `return result.returncode == 0 and "\nOK" in verdict`: the verdict comes from the suite alone. **True.**
2. `parts.py:1329` — `return all(word.lower() in haystack for word in words)`; `drawer.py:54-55` `_words` is `isinstance(value, str) and bool(value.strip())`, while `needs.py:122-123` is a splitter. **True.**
3. `tests/test_check_bom.py:138` — compares with `check_bom.EXIT_PROBLEMS`. **True**, but the inference ("the gap shown") is **false** (the run above).

## The one change

Pull CH-16 (#58) into I0's fix lane right after C1, on today's envelope. The F→A route §12.1 gives CH-12/13a/20/36: I1b moves it onto `cli` later. Why: it is rank 1, part 1 gives it no hard edge, and its harm is an `ok` from `parts.py --json` without the CONFLICT line. That is the JSON H0c's cold run measures agents trusting. The plan ships 16 cards first.

## Searches

None on the web. Local: grep/sed, `git show 5acbe42:`, `gh issue view` (read) for the nine named cards and #6, #10, #103; one mutant run on a scratch export, `SPARK_HOME` an empty scratch folder.
