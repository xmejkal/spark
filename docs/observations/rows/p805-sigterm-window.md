# P805: a SIGTERM never leaves a scratch folder: rows

Card: [P805 #1139](https://github.com/xmejkal/spark/issues/1139). Plan check: one refuter (Opus), 2026-11-13. This file
holds the acted, raised and rejected findings only (rules.md), with the build's own rows. 2026-11-13.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a SIGTERM right after `tempfile.mkdtemp` and before its name is stored leaves the folder: `_from_source` (`mutate-run-*`, `mutate-import-*`) and main's `where = copy_of(root) if args.copy else root` (`mutate-copy-*`); one right before `_from_source`'s `shutil.rmtree(run, ignore_errors=True)` stops the removal | card, plan | acted | each is made and stored, or removed, under `sigterm_held()`; `test_a_sigterm_right_after_a_scratch_folder_is_made_or_right_before_it_is_removed_leaves_nothing`, red on 985196c4 in all five subtests (made copy, run, import; removed run, import), green after; mutation rows 1 to 3 caught by hand; the anchors' texts of p172 and p208 kept |
| 2 | `run()` writes `.mutate.lock` before its `try`, so a SIGTERM right after the write leaves a lock that refuses every later run in that tree | plan check, raised | acted | fixed in this PR: the write moved inside the `try` (a hold alone would deliver the signal before the `try`), and the `finally`'s `lock.unlink` is held; `test_a_sigterm_right_after_the_lock_is_written_or_right_before_it_is_removed_leaves_no_lock`, red on d7583f62 (before this fix) in both subtests, green after; mutation rows 4 and 5 caught by hand |
| 3 | the hold over `copy_of` lasts about 0.6 s, and its `git ls-files` child inherits the blocked SIGTERM for a few ms | plan check | acted | said in `sigterm_held`'s docstring |
| 4 | the two load-sensitive tests stay green beside a CPU load | card, Done-when | acted | two `yes > /dev/null` processes on an 8-core Mac: `test_a_sigterm_in_a_copy_run_keeps_the_lines_recorded_before_it` 20 of 20 passed, `test_a_stop_by_sigterm_leaves_nothing_in_the_temp_folder` 20 of 20 passed |
