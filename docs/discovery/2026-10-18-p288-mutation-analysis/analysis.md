# P288: do we need the mutations? An analysis with numbers

> **TL;DR.** Yes, keep mutation testing, but run it once per story. In the 33 runs whose counts the rows give, the
> mutation-tester or a story agent planted 384 defects and 67 escaped (17%); 26 of the 33 runs found at least one
> missing test, and all escapes but 2 got a test or a fix. The cost is two full suites per call (about 4.5 min
> today) plus one more suite per escape, and a story often pays it two or three times. One pass per story, a cap of
> 12 plants on new logic, and four number fields on board #2 keep the value and drop the repeats.

Card: [#344](https://github.com/xmejkal/spark/issues/344). The PO, 2026-10-18: *"do we even need the mutations? has
it been helpful? when can we get rid of them? do we just run them once or multiple times? and how many mutations do we
run? who should do it and when?"* Numbers were read on origin/main `61d5f63`, 2026-10-18.

## 1. How it works today

| Part | What it does | Source |
| --- | --- | --- |
| `tools/mutate.py` | Puts one defect back (`find` once in a file), runs the near tests (modules that import the file) with failfast, and the whole suite only on a miss. Runs the clean suite before and after. | docstring, `near_tests`, `_run` |
| `--copy`, `--for`, `--anchors` | Mutate a temp copy; keep rows for named files; check anchors and syntax in seconds. | `--help` |
| `mutation-tester` agent | Reads the branch diff, plants at most 12 defects, runs the table once with `--copy`, reports "N planted, M caught". | `.claude/agents/mutation-tester.md` |
| Rule: when | Only a change that holds logic; the council launches the tester before the PR. | `GLOSSARY.md` line 106, `developing.md` line 46 |
| Rule: kept | A table stays in `tests/mutations/` only when a defect escaped (P208, 2026-10-12). | `WORKING_AGREEMENTS.md` W3 |
| Rule: epic sweep | When an epic is done, every row for its files runs in one sweep. | `scrum/README.md` line 308 |
| Push gate | Checks anchors only; it never runs the tables. | `developing.md` line 110 |

## 2. The tables

| Measure | Number |
| --- | --- |
| Tables in `tests/mutations/` | 156 |
| Rows (a JSON count) | 1823 |
| Rows refused now (`--anchors`: anchor missing or mutant does not parse) | 62 (3.4%); the card says 61 |
| Files mutated | 80; `parts.py` 314 rows, `needs.py` 202, `check_backlog.py` 146 |

## 3. Value: what the rows say

`docs/observations/INDEX.md` has 1049 rows; 98 mention mutation, escaped or planted. 33 runs state counts (DP4 on
2026-10-12 to AT402 on 2026-10-18), run by the tester or a story agent.

| Measure | Number |
| --- | --- |
| Defects planted | 384 |
| Caught / escaped | 317 / 67 (17% escaped) |
| Runs with at least one escape | 26 of 33 (79%) |
| Runs with none | 7 (AT112, AT243, AT261, AT267, AT280, AT289, AT306) |
| Escapes recorded as a test or a fix | all but 2 |
| The 2 others | AT320, an equivalent mutant (`ignore_errors=True`); the cache in PR #338 (AT332), left untested |
| The last 11 runs (AT295 to AT402, 2026-10-17 to 18) | 24 escapes; 10 of the 11 runs had one |

The rows count escapes, not shipped bugs. None says a user hit one. Each escape is a defect that the suite would
have passed. Reviews find another class (AT298, AT304: crashes, wrong docs), so the two do not replace each other.

Three examples:

1. **AT130** (P215 step 3, PR #231): 12 planted, 6 caught. The port, the MAC key, the verdict and the private place
   escaped; three tests added.
2. **AT300** (P254): 12 planted, 11 caught. The `ValueError` catch escaped; a null byte raises it on Python 3.10, a
   real crash path with no test. A null-byte test added.
3. **AT382** (P272, PR #341): 12 planted, 6 caught, in the same PR where the reviewer and refuter found other defects
   (tests below `unittest.main()`, a page that scrolls sideways). Five tests and five rows added.

## 4. Cost

Measured here on 2026-10-18 on a loaded machine, so read it as a scale:

| Measure | Number |
| --- | --- |
| Full suite | 2616 tests, 133 s (22.8 s for 1144 tests in `developing.md` line 110) |
| `tests.test_check_spine` alone | 137 tests, 5 s |
| Slowest modules | test_mutate 24 s, test_docs 17 s, test_journey_basic 17 to 23 s (real builds), test_needs 14 to 16 s |
| Near set of `check_spine.py` | 9 modules, 52 s (it includes `test_journey_basic` and `test_needs`) |
| Near set of `tools.py` / `deploy.py` / `store.py` | 52 s / 36 s / 35 s |
| Near set of `check_backlog.py` / `cost.py` / `drawer.py` | 0.3 s / 0.5 s / 1.9 s |
| Fixed cost of one `mutate.py` call | 2 full suites, about 266 s |
| One escape | a near run plus a full suite, 133 s or more |

So the slow run is not one slow test. It is the fixed 4.5 min, plus up to 52 s per caught row whose near set holds
real builds, plus 133 s per escape. A 12-row table on `check_spine.py` with 3 escapes adds up to about 266 + 9 x 52
+ 3 x 185 = 21 min, the size of P287's run. PR #339 states 368 s for a re-run of 2 rows, near the fixed cost.

Passes per story, from the PR bodies:

| Story | PR | Passes | Plants |
| --- | --- | --- | --- |
| P239 PR 4 | #335 | 1 table, 6 rows re-anchored | 7 |
| P239 PR 5 | #338 | table, then tester | 8, then 12 |
| P273 slice 1 | #339 | tester, then a re-run of 2 rows (368 s) | 32 |
| P272 | #341 | tester, then the 19-row table | 12, then 19 |
| P242 | #342 | agent run, then a re-run of 4 rows | 48, then 4 |
| P239 PR 6 | #343 | table, fix, anchors re-checked | 7 |

Four of the six ran two or more passes. Only one PR body states a time, so minutes are a gap.

## 5. Backfilled per-run data

Empty means the source is silent. No source splits near from full catches, so those columns are left out.

| date | card | pr | table | run_by | planted | escaped | refused | real_gaps | equiv | sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10-17 | P253 | | | tester | 15 | 3 | | 3 | | |
| 10-17 | P254 | | | tester | 12 | 1 | | 1 | | |
| 10-17 | P247 | | | tester | 12 | 0 | | 0 | | |
| 10-17 | P282 | | | tester | 12 | 2 | | 2 | | |
| 10-17 | P280 | 330 | | tester | 12 | 1 | | 0 | 1 | |
| 10-17 | P283 | 333 | | tester | 12 | 2 | | 2 | | |
| 10-17 | P239-4 | 335 | p239-pr4 | story agent | 7 | 0 | 6 | | | |
| 10-17 | P239-5 | 338 | p239-pr5 | story agent | 8 | 0 | 4 | | | |
| 10-17 | P239-5 | 338 | | tester | 12 | 2 | | 1 | | |
| 10-17 | P273-1 | 339 | p273-keep-moves | tester | 32 | 2 | | 2 | | 368 (2 rows) |
| 10-17 | P272 | 341 | p272-page-as-artifact | tester | 12 | 6 | | 6 | | |
| 10-17 | P242 | 342 | p242-deploy-grant | story agent | 48 | 4 | | 4 | | |
| 10-18 | P239-6 | 343 | p239-pr6 | story agent | 7 | 1 | 0 | 1 | | |

## 6. Options

| Option | Saves | Risks |
| --- | --- | --- |
| A. Keep as is | nothing | 2 to 3 passes per story; 20 min runs |
| B. One pass per story: the tester's plants are the only table, run once after fixes, with `--copy` | the story agent's table run and the re-runs: one fixed 4.5 min, not 9 to 14 | a late escape costs a fix round |
| C. Fewer, targeted mutants: new logic lines only, cap 12 (the agent's rule) | rows of 48 (P242) and 32 (P273) | a rarely-hit line goes unplanted (AT306 lists 4 not planted) |
| D. Faster near sets: leave real-build modules out of a set | up to 52 s per caught row | a faster set can catch by import side effect |
| E. Run only before the PR, not per review round | the repeats after each round | a defect from a review fix is not planted |
| F. Drop the agent, keep the tool | one Sonnet agent per story | the author plants; AT379 shows the author's first tests accepted either code |
| G. Drop mutation testing at a stage | the whole cost | 26 of 33 runs found a gap |
| H. Delete or re-anchor the 62 refused rows; run `--anchors` in the gate | silent decay of 3.4% of rows | none |
| I. Number fields on board #2, one value per card, summed over its runs: "Mutants planted", "Mutants escaped", "Real gaps found", "Mutation minutes" | the PO reads totals on the card; no file | one value per card, no history per run, not in git |
| J. `mutate.py` appends its counted columns itself; the agent fills only real_gaps and equivalent | hand-copied numbers | needs a file or an API write from the tool |

How a story agent fills I: at its last step it adds the tester's "planted" and "escaped", the tests it wrote for
"Real gaps found", and the tool's printed seconds as minutes. A re-run adds to the same card. Nothing is created
until the PO decides.

**Stop rule.** Drop the tester for a class of change when 5 stories in a row show 0 escapes in the fields. In the 33
runs there is no streak of 3, so it does not fire. Check at each epic.

## 7. Recommendation

Do B with C, E, H and I: one tester pass per story after the fixes, a cap of 12 plants, `--anchors` in the gate and
the board fields, because 79% of runs find a missing test while every extra pass pays the same 4.5 min again.

## 8. Open questions for the PO

1. Create the four fields on board #2? Or keep a git file for per-run history?
2. Delete the 62 refused rows or re-anchor them (P284, #331)?
3. Stop rule: 5 stories in a row with 0 escapes, or another number?
4. Drop the epic sweep, or run it only when a card's fields show escapes?
5. Does a story agent still run its own table, when the tester covers the same lines?

## Checked by

(after the refuter)
