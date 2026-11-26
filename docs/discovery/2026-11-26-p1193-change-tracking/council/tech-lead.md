# Tech lead lens: P1193 change tracking

The tech lead lens on Opus, 2026-11-26. Its role is read-only, so the main session wrote this file from its returned
report, word for word.

## Findings

- TL-1 · One git runner can serve the project and the store. `ProjectCommit` holds nothing project-specific: `_git` runs `git -C <folder>` with the GIT_* variables stripped, a timeout and a stop of the whole process group. `held_as_is`, `tracks` and `commit` take a file name from a folder that is handed in · E scripts/spark/records/project_commit.py:32-67, 69-110 · supports only: one lower git Adapter can be reused. It does not say whether one Strategy or two sit over it.
- TL-2 · The store's refusal blocks a repository at the store's root, not a clone in a sub-folder · E a scratch run (SPARK_HOME in $TMPDIR/tl-p1193.CWS7, removed after). With a repository at <home>/shared, a shelf write passed and `inside_git` of the shelf file gave None. With a repository at <home>, a shelf write raised `store_in_repository` and a catalog write passed. The rule is in scripts/spark/records/store.py:202-208 and 385-390 · supports only: a new place that is not private (a clone, say "shared") can sit in the store and become one more layer in `layers()` (store.py:121-132). It does not show that a push works.
- TL-3 · Shelf records hold private text and a project name · E shelf/ds3231-at24c32-rtc-module.json `//sourcing`: "Owned; in the drawer, in its bag, unused." · E shelf/dfr0664-tft-2in.json `"based_on": {"project": "walk4", ...}` · E grep: 9 shelf files carry `based_on` and 2 mention the drawer, 2026-11-26 · supports only: a field filter must exist before any push (D-q8 before D-q5).
- TL-4 · The store's one SVG has no record of its origin, so D4 (only pictures spark or the person drew) cannot be applied to it · E `ls` of sources/f6a03caa…/ shows epaper-breadboard-top.svg alone, with no JSON, 2026-11-26 · supports only: a picture needs an origin field before it can be shared.
- TL-5 · Spark can already tell that someone else edited board.tsx, but only the build reads it · E scripts/spark/build/build_record.py:31-32 (`OWN_FILES = ("board.tsx",)`). E `written_sha256` is read only in scripts/spark/build/kept_files.py:231 and 506-520. No phase reader reads it (grep). The BuildReader is at scripts/spark/flow/phase_readers.py:479-507 · supports only: a small slice of D-q2 that needs no git.
- TL-6 · breadboard.json has no stamp of the bytes spark wrote · E grep finds no sha or written stamp for it in scripts/spark. The earlier file is read only to keep the person's moves (scripts/spark/breadboard/sheet.py:474-475, kept_moves.py:1-5, drawing.py:549) · supports only: to notice an outside edit of it, spark needs a new stamp or a git status against the last kept step.
- TL-7 · One setting already points a job at a tool, in three layers with the project winning: the `roles` of data/tools.json (14 roles), the person's tools.json in the store and the project's .spark/tools.json · E data/tools.json "//", scripts/spark/records/tool_finder.py:42-44, 91-95. git is not a listed tool · supports only: D-q6 could use a role (for example timeline → git) and `on: false` for D6's turn-off. It would need no new settings file (H, my proposal).
- TL-8 · Spark's only git code says it never pushes, and nothing an Operation can reach has a push or a pull · E project_commit.py:5 · E scripts/spark/core/outside.py:42 (fields: run find_tool report clock make_consent replies fetch add_diagnostics) · supports only: a push is new behaviour. It brings credentials, the network and hooks, and needs an effect declared through the core.
- TL-9 · Under D3 (a public repository under the PO's account), only the PO can push to it directly. Anyone else contributes by a fork and a PR · H (GitHub's permission model, from general knowledge, not read today). It matches the 10-04 plan's "`--contribute` and a reviewer's CI" (docs/archive/2026-10-04-store-discovery.md:209-211) · supports only: "push" means two different things.
- TL-10 · Order of the cards. P1150 #1686 and P1157 #1693 are closed. ignore_list.py:31-32 already expects a `GitProjectTimeline` that P1151 hands in. By their bodies, P1151 #1687 is built together with P1152's first slice. P1155 #1691 depends on both. P1153 #1689 depends on P1152 · E `gh issue view`, 2026-11-26 · supports only: P1151 with P1152's first slice, then P1155, then P1152's later slices, then P1153. P1154 #1690 is outside this epic.
- TL-11 · P390 #505's premise is out of date. Its body says `layers()` adds the shelf for parts only. store.py:129 now gives a board shelf for every other kind (P989, merge 4966b4cf) · E · supports only: re-read P390 before ordering it.
- TL-12 · By the MVP bar and D5, four verbs serve a breadboard: keep (D8, widened by D-q1), notice an outside change (D-q2), a named mark, and a take-back to that mark. Compare is a convenience. Merge in a project gives a record nobody decided (P1160, "The two cases", cited by J5 and not re-read). A pull at a pinned commit (10-04 plan) needs no merge · H, the tech lead's judgement · supports only: pause merge in both places.
- TL-13 · The P158 proposal tags "a public repo of records … cloned read-only at a pinned commit" as "D the PO 2026-10-04". The primary source puts that line in the council's plan (item 9) and the PO's decisions at lines 221-227 · E proposal.md:423-425 against store-discovery.md:209-227 · supports only: the brief reads the primary source correctly.
- TL-14 · The PO's new decisions · D, the PO, 2026-11-26, 09:08 CET (brief.md:89-92): D2 the shared side starts now, D3 a new public repository under his account, D4 only drawn pictures, D5 the timeline first and the shared side second.

## What I could not check, and why

- A push to GitHub and credentials: there was no network and no account in scope.
- Git's union merge on history.jsonl (CH-70): not run.
- The P1160 finding, the past-breadboard council files and the P342 RecordAdder code: not re-read, because of the time limit.
- Whether P390's "onto the shelf on --requirements" is already done: not checked.
- How fast git runs over 153 source folders: not measured. This machine has git 2.49.0 and no other version was tried.
- Windows: not checked.

## Questions for the decider

- Is a person's or Claude's edit of board.tsx or breadboard.json a kept step (this reopens D-h)? · decides D-q1, and whether a build commits a file of the person's.
- On an outside change, does spark only say it, or also keep it as a step at its next write? · decides D-q2, and whether spark ever commits bytes it did not write.
- Is a mark a named tag on a kept step, and is a return to it a take-back of a range of steps? · decides D-q3.
- Is "push" a git push for the PO and a PR for everyone else? · decides D-q5's transport.
- Is the strategy chosen by a role in tools.json or by a new settings file? · decides D-q6.
- Which fields of a shelf record may leave the store (`based_on.project`, the `//` notes)? · decides D-q8's filter.

## Searches

none
