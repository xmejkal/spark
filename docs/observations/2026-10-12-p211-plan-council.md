# P211 plan council (one reviewer, read-only)

Method: I copied the worktree outside the repo. There I applied Tasks 1-5 as the plan writes them. Then I ran the plan's own tests and the full suite. Findings are most severe first.

1. **`--matcher` is lost on page 2.** Task 3 step 4: `page(matched, args.start, "match", ["--match", args.match])`. I ran `--match P --matcher word-overlap --json` on 12 needs. `truncated.next.argv` was `['--match', P, '--from', '7', '--json']`. The next page ranks with the default matcher, so page 2 does not continue page 1. The existing fixture already fills a page with 4 needs, and `score` and `why` make each candidate bigger. Fix: when `--matcher` is given, append `["--matcher", args.matcher]` to the argv. Add a test that reads `truncated.next`.

2. **`match_eval` does not measure what `--match` shows.** Task 5, `evaluate`. `needs.candidates` re-sorts by `(owned==0, -score, layer, id)` before `shown(rank, ...)` (Task 3). `evaluate` cuts straight after `rank`. The invented drawer is all owned and in one layer, so the two agree there. They differ on a real drawer. Ties keep file-name order, so SameWords' "shown 15/21" (my run) comes from alphabetical position: 13 offers per verb, and the first 8 are always shown. `main` also builds the class with `MATCHERS[name]()` and skips `matching.matcher(name, "match")`, so `--matcher name-contains` is accepted. Fix: put the cut in the core (`matching.shortlist(fits)`, used by both callers), and make `main` call `matching.matcher(name, "match")`.

3. **`match_eval --json` is not the repo envelope (the PO's rule).** Task 5 step 5 prints `{"tool","status","matchers"}`. §6.4.1 and `outcomes.envelope` give `envelope, op, data, problems, unchecked, next, truncated`. This adds a sixth shape that `test_json_contracts` already lists as a problem. Fix: `outcomes.envelope("match_eval", "evaluate", data={"matchers": results}, unchecked=[{"sentence": ..., "fix": None}])`, and update `test_json_answers_for_an_agent` to read `data.matchers`.

4. **Task 6 step 1 tells Claude to run `parts.py --offer`, but `commands/idea.md` line 3 `allowed-tools` has no `--offer *`.** `--match *` already covers `--matcher`. Without the entry every `--offer` call is a permission prompt, or a denial in a non-interactive run. Fix: add `Bash(${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --offer *)` to step 1.

5. **The plan contradicts the spec's parity promise.** Task 4 says `--need "soil moisture"` (one argument holding a space) goes from one substring to two words. `parts.py:1336-1339` shows the old rule. The spec's "What does not change" and the Global Constraints say nothing moves under the defaults. Fix: let `_found` pass the typed words (`need["words"] = list(words)`) and have NameContains prefer them. Or tell the PO of the deviation in the PR.

6. **Review Focus 1 describes a path that cannot happen.** `drawer.entries()` (`drawer.py:88-101`) runs `CHECKS` on every field. I ran `--match` with an entry `{"tags": "knob", "about": 5}`. The whole `--match` ended `could-not-run` with "the drawer is read whole or not at all". That is safe. But `test_a_malformed_text_is_ignored` calls `Offer.from_entry` directly. Only a catalog record can reach it. Fix: reword the focus, and add a `--match`-level test that expects `could-not-run`.

7. **`describe()` is not clean for `power` and `body_mm`.** Task 2 `describe`: `json.dumps(self.facts[key], ensure_ascii=False)` prints record strings raw, including U+202E. Review Focus 2 and the data-not-instructions rule cover only about, description, tags and names. Fix: `ensure_ascii=True`, or run `facts` through `drawer._scrubbed` in `__init__`.

8. **Two visibility rules in two layers.** Task 4 `_found` filters `fit.score > 0` in `parts.py`. The `--match` rule is `matching.shown` in the core. A later fractional `need` matcher then needs its threshold in the CLI. Fix: `matching.found(fits)` beside `shown`.

9. **`NameContains.admits` is untested.** With `does: None` the base `admits` also returns True. A test with `{"does": "sense", ...}` against an `input` offer is needed, or the mutation tester will keep that mutant alive (the spec lists `admits` per class).

10. **Task 2 leaves `test_orphans` red.** `matching.py` has no importer until Task 3 (`test_every_script_is_routed_to_or_imported`). Task 2 runs one file only, so a per-task reviewer who runs the suite sees a failure (read from `test_orphans.py`, not run). Fix: one sentence in Task 2 step 4.

11. **Task 6 step 4 grep is a poor guide.** `used_in` hits `journey.md:289,311` (command output) and `GLOSSARY.md:319`. The only field list is `commands/drawer.md:31`. Fix: name that file.

12. **`--offer --json` carries the text twice** (`data.offer` and `data.text`), against MT11's 4 KB aim. Fix: keep `text` in the lines and only the dict in `data`. The Task 4 test then drops its `text` assertion.

**Checked and sound:** with Tasks 1-5 applied as written, every plan test passes: Task 1, 4; Task 2, 18; Tasks 3-4, 7 and the edited whole-candidate test; Task 5, 4. The full suite, 1978 tests, has one failure: the whole-candidate test that Task 3 edits. That run includes `test_suite_temp`, `test_orphans`, `test_docs` and the glossary test. The `SCORES` table, the plural fold and the filler words check out by hand. There is no import cycle. Every new test fails for the missing feature before it exists. `linkable` dedups by `(kind, id)`, so `context` cannot collide. Candidate lists, order and `what_matches` are unchanged under the defaults. The eval gives WordOverlap 21/21 and SameWords 15/21 shown, with `about` only.
