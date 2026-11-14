# P810: a lock whose process is gone is stale, and the next run takes it: rows

Card: [P810 #1152](https://github.com/xmejkal/spark/issues/1152), the PO's top of Ready on 2026-11-14. Size XS: one plan
check (refuter Opus) and one PR refuter. This file holds the acted, raised and rejected findings only (rules.md), with
the build's own rows. 2026-11-14.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a lock that a killed run left blocks every later run in the tree until a person removes it | card | acted | `RunLock` in `tools/mutate.py`: a lock whose process is gone (`os.kill(pid, 0)` raises ProcessLookupError), in a tree git shows clean, is taken over; `main` says it in one line on stderr and `--json` gains `stale_lock`. Plan `~/.claude/plans/p810-stale-lock.md` |
| 2 | a run without `--copy` killed during a row leaves its mutant in the file, and a blind takeover would run on it | plan | acted | the takeover needs `git status --porcelain --untracked-files=no` empty over the whole tree; a changed file keeps the lock, and the refusal names up to three paths and says "check `git diff`, restore a file that holds a mutant" |
| 3 | plan check: checking only the run's own files misses a mutant in another file | plan check | acted | the whole tree is checked |
| 4 | plan check: `git diff --quiet HEAD` says 0 for a missing file and 1 both for "differs" and for "no repository" | plan check | acted | `git status --porcelain` with the GIT_* variables stripped (`git_environment`, now shared with `ignored_by_git`); no git answer keeps the lock |
| 5 | plan check: a lock text "-5" parsed as gone, and a huge number ended the tool with OverflowError | plan check | acted | `holder_gone` accepts only an id above 0; OverflowError and PermissionError mean "not known gone"; tested with "-5", "0", a 20-digit number, "", "not a pid" and this process's id |
| 6 | plan check: two runs that read the same gone id could both take the lock, or one remove the other's live lock | plan check | acted | the lock is created with O_EXCL; a takeover renames the stale lock to `.mutate.lock.<pid>`, checks that it still holds the gone id, and puts a live one back with `os.link`; tested by a run that takes the lock while git is asked |
| 7 | plan check: removing the lock in `main` is logic in `main` | plan check | acted | the logic sits in `RunLock`; `run(..., lock=None)` takes one; `main` passes it and prints |
| 8 | plan check: "restore it with git" could throw away a person's own edits, as a run without `--copy` on an edited tree is allowed | plan check | acted | the refusal says "check `git diff`, restore a file that holds a mutant" |
| 9 | a `--copy` run copies a mutant that a killed run without `--copy` left in the tree, as the copy never looks at the tree's lock | plan check | raised | dropped because it is older than P810 and needs a run without `--copy` killed mid-row; a sweep runs with `--copy` (W3), so a mutant in the tree comes only from a hand run; a refusal there names the files |
| 10 | `test_a_sigterm_right_after_the_lock_is_written_or_right_before_it_is_removed_leaves_no_lock` finds its moment through `Path.write_text` | build | acted | the lock is created empty with O_EXCL, then its id is written with `write_text`, so the test runs unchanged; an empty lock meanwhile reads as no process id and is kept |
| 11 | a refusal must remove no lock: the old `finally` removed whatever lock was there | build | acted | `release()` removes the lock only when this run holds it; "a refusal removes no lock" is asserted for each kept lock |
| 12 | the PR's rows | build | acted | `tests/mutations/p810-stale-lock.json`, 9 rows, each planted by hand in a scratch copy and red against its named test (9 of 9); three older rows re-anchored on the moved lines (P787 row 6, P805 row 4, P807 row 3), each red by hand (3 of 3); `--anchors`: 3304 rows in 289 tables, every anchor present once |
