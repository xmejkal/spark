# P1150, spark's section of the project's .gitignore, with P1156 inside it: rows

Cards: [P1150 #1686](https://github.com/xmejkal/spark/issues/1686) and [P1156 #1692](https://github.com/xmejkal/spark/issues/1692),
one PR. The PO approved the plan after two plan-council rounds on 2026-11-25. The PR review was one lens (Sonnet) and the
refuter (Opus) on 2026-11-26, and both checked the PO's words of that day: "the architecture needs to be well made so
that we can change these strategies and tools and its reusable, dry".

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | An empty AGENTS.md gets one newline before spark's section, where main wrote two, so the "same bytes" claim fails | the lens, finding 1, and the refuter, point 3 | acted | `SparkSection.placed` keeps main's expression. `test_spark_section` pins two newlines for an empty text |
| 2 | With git missing, init rewrites a `.gitignore` that git tracks, because None counts as untracked | the refuter, point 4 | acted | inside a repository, None leaves the file alone with its own note. `test_no_git_on_the_path_inside_a_repository_leaves_a_tracked_gitignore_alone` and a new mutation row |
| 3 | The `**` branch for a pattern that ends in `/` changes nothing, so its row never fails | the lens, finding 2, and the refuter, point 6 | acted | the branch and its row are gone. Git reads a folder pathspec as everything below it |
| 4 | The row "a new file gets a leading blank line" survives every test | the lens, finding 3, and the refuter, point 5 | acted | the no-repository test checks the file's first and last line, and the row names it. Planted by hand: caught |
| 5 | The `:(top)` row's name says "a plain pathspec", but it plants another pathspec | the lens, finding 4 | acted | the row plants `"./" + pattern`. Planted by hand: caught |
| 6 | `SECTION_MARKS` and `MARKERS` name the same kind of Value | the lens, finding 5 | acted | `MARKERS` in both modules |
| 7 | `commands/init.md` says only spark's section keeps `CLAUDE.local.md` out, but a tracked `.gitignore` leaves that to `.git/info/exclude` | the lens, finding 6, and the refuter, point 8 | acted | the page names both, and the git-unknown case |
| 8 | The handed-in git's two reads are written down nowhere, so a project timeline cannot know what to answer | the lens's follow-up (d), and the refuter, point 6d | acted | `IgnoreList`'s docstring names `tracks` and `tracked_files`, what each gives, and that `GitProjectTimeline` passes both to `ProjectCommit` |
| 9 | The guard "a link, a folder or not UTF-8, so it is left alone" is written for AGENTS.md and again for `.gitignore` | the lens's follow-up (b) | raised | a comment on [P1151 #1687](https://github.com/xmejkal/spark/issues/1687) (spark-main, 2026-11-26), which moves `AiFiles` and `IgnoreList` behind init's Operation. The two guards differ today: AGENTS.md follows a link inside the project |
| 10 | `sim` and `runs` have no shared constant, and `LINES` adds a fourth spelling | the refuter, point 6b | raised | a line on [P794 #1106](https://github.com/xmejkal/spark/issues/1106), the clean-up epic for names and repeats (spark-main, 2026-11-26). The three older spellings are in `board_log.py:23`, `project_image.py:64` and `scenario_run.py:128` |
| 11 | A `.gitignore` that already holds the three lines outside spark's markers gets them twice | the refuter, point 8 | rejected | git reads a repeated line once, and the person's own lines stay theirs |
| 12 | A tracked `sub/CLAUDE.local.md` is ignored by the section but not named by the check | the refuter, point 8 | rejected | spark writes `CLAUDE.local.md` only at the project's top, which the check names |
| 13 | The splice exists once, git runs only in `ProjectCommit`, and `IgnoreList` reuses `ai_files.read`, `store.write_file` and `ai_files.LOCAL` | the lens's follow-up (a, c), and the refuter, point 6 | verified | both checked with grep and found no second splice and no git call outside `project_commit.py` |
| 14 | The scratch proof, the count over the 9 repositories (0 track `CLAUDE.local.md`) and 12 of the 14 rows hold | the refuter, points 1, 2 and 7 | verified | reproduced by the refuter |
