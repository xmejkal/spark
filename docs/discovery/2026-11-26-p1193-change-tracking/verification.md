# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->

The refuter on Opus read HEAD b9e95a68 on 2026-11-26. The main session reproduced each claim between 09:36 and 09:44
CET by the command or the read named. The claims marked partly or refuted were rewritten in brief.md after the pass.

- ★C1 · scripts/spark/build/ignore_list.py:31 · refuter: holds — "ProjectCommit Adapter answers both and is the default until P1151 hands in the project timeline (`GitProjectTimeline`" · reproduced how: `grep -rn -E "ProjectTimeline|KeptStep|TakeBack" scripts` gave 1 line · result: reproduced · keep: none
- ★C2 · scripts/spark/records/project_commit.py:5, 28-29 · refuter: holds — "Spark never stages with `git add`, never runs `revert`, `reset` or `push`, and never skips a hook." · reproduced how: `grep -rn '"git"' scripts/spark` gave project_commit.py:42 alone · result: reproduced · keep: none
- ★C3 · scripts/spark/build/kept_files.py:92-93, 116 · refuter: partly — "A `.tsx` is a person's to edit, so one that is there is left alone and named, unless `written` … holds its bytes" · reproduced how: re-read kept_files.py:89-123 · result: reproduced, rewritten as the refuter said · keep: none
- ★C4 · docs/discovery/2026-11-25-p1160-take-back-chain/finding.md:184 · refuter: holds — "board.tsx stays a build output, not a kept step | 3 of 3" · reproduced how: re-read finding.md:184 · result: reproduced · keep: none
- ★C5 · scripts/spark/flow/phase_readers.py:413, 447, 545 · refuter: partly — "sha256_of(path) != record.get("requirements_sha256")" · reproduced how: re-read the three lines · result: reproduced, rewritten · keep: none
- ★C6 · scripts/spark/flow/flow_codes.py:11 · refuter: holds — `PHASES = ("idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy")` · reproduced how: `sed -n 11p` · result: reproduced · keep: none
- ★C7 · scripts/spark/records/store.py:146-147, 387 · refuter: holds — "if private and inside_git(target):" · reproduced how: re-read store.py:380-392 · result: reproduced · keep: none
- ★C8 · the store, `git rev-parse` and `find` · refuter: holds — "fatal: not a git repository" · reproduced how: `ls` counts, 2026-11-26 09:36 CET · result: reproduced after a correction: the shelf holds 10 part records and 2 board records, 13 JSON files with one more in a part's folder, not "13 shelf records" · keep: n = 1
- ★C9 · `ls parts`, `find data/pictograms` · refuter: holds — 10 entries in parts/, 8 JSON records and 2 folders · reproduced how: `ls parts | wc -l` gave 10 · result: reproduced · keep: none
- ★C10 · docs/archive/2026-10-04-store-discovery.md:135, 209-217, 225 · refuter: holds for the quotes, caveat partly wrong — "(4) P84 **drops the database/NoSQL/Markdown half**" · reproduced how: re-read lines 186-240 · result: reproduced, caveat rewritten · keep: a delegated reading
- ★C11 · docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md:342, 449-450 · refuter: holds — "What any transport needs first is R4 plus a tombstone (FEASIBILITY §2.2): without them every transport corrupts quietly." · reproduced how: re-read proposal.md:410-455 · result: reproduced · keep: none
- ★C12 · scripts/spark/records/storage.py:22 · refuter: holds — `NAMESPACES = ("registered-projects", "boards")` · reproduced how: re-read storage.py:1-40 · result: reproduced · keep: none
- ★C13 · scripts/spark/sourcing/part_facts.py:119-120 · refuter: partly — "if project_name: copy["based_on"] = {"project": project_name, "digest": digest(record)}" · reproduced how: re-read the lines · result: reproduced, rewritten · keep: none
- ★C14 · scripts/spark/operation_catalogue.py:30 · refuter: holds — `len(CATALOGUE)` gave 51 · reproduced how: `python3 -I` import, 2026-11-26 09:36 CET · result: reproduced · keep: none
- ★C15 · scripts/spark/breadboard/kept_moves.py:3-4 · refuter: partly — "reads the earlier file before the build writes the new one, keeps each part where the person put it when it still fits" · reproduced how: re-read kept_moves.py:1-12 · result: reproduced, rewritten · keep: none
- ★C16 · `git log --all -- board.tsx` over the store's projects.json folders · refuter: refuted on "by hand" — 22 of 24 commits carry "Co-Authored-By: Claude" · reproduced how: the same count with the commit bodies, 2026-11-26 09:44 CET: 24 commits, 22 co-authored by Claude, 23 between 2026-09-22 and 2026-10-11, 0 tags, 0 "spark: " commits · result: rejected as first written, rewritten · keep: co-authored by Claude
- ★C17 · council/ux-ai-ux.md (UX-6) · refuter: partly — "Only 2 of the 6 build.json files have a board.tsx stamp" · reproduced how: not reproduced by the main session · result: not reproduced, rewritten to the refuter's count · keep: predicted, not observed
- ★C18 · scripts/spark/flow/phase_readers.py:169-170 · refuter: holds as a code path — "if held is None: return False, []" · reproduced how: re-read the lines · result: reproduced as a code path · keep: none
- ★C19 · council/ux-ai-ux.md (UX-2), council/po-assistant.md (PO-12) · refuter: partly — "The id loss after a squash is H" · reproduced how: not reproduced by the main session · result: not reproduced, rewritten to the refuter's first-parent counts · keep: no host tested
- ★C20 · the store's shelf and catalog · refuter: holds — `//` keys in 28 of 28, `based_on.project` in 7 of 28 · reproduced how: a python count, 2026-11-26 09:36 CET: 28 records, 28 with a top-level `//` key, 7 with `based_on.project` · result: reproduced · keep: none
- ★C21 · council/tech-lead.md (TL-2) · refuter: holds — reproduced in its own scratch store · reproduced how: a scratch SPARK_HOME with a repository at `<home>/shared`: `store.write_json('shelf', …)` gave True and `inside_git` gave None, 2026-11-26 09:36 CET, removed after · result: reproduced · keep: none
- ★C22 · scripts/spark/records/tool_finder.py:531, 535 · refuter: holds — "def use(role, tool_name, project=None, personal=None):" · reproduced how: a python read of data/tools.json: 14 roles, no git tool · result: reproduced · keep: none
- ★C23 · council/synthesis.md (part 3) · refuter: holds, but weaker than it looks — the ref is safe from gc because it is a ref, a fresh clone and a default fetch did not carry it, and `git restore` overwrote an uncommitted edit · reproduced how: a scratch repository, a local `git merge --squash`, a branch delete, `git gc --prune=now`, `git restore --source=<ref>`, 2026-11-26 09:36 CET, removed after · result: reproduced · keep: tests nothing at risk <!-- REQUIRED:claims -->

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: every lens and the refuter find that the store itself cannot be the repository, and that a clone in a sub-folder works (TL-2, ARCH-6, the refuter's run) · no question <!-- REQUIRED:agree-split -->
- Agree: an allow-list is needed before any share, because a field block-list misses the `//` notes and the names in fact sources (PO-4, UX-4, TL-3, the refuter's ★C20) · P1 (Q24)
- Agree: merge waits (TL-12, PO-7, the synthesis, the council C11) · P8 (Q31)
- Split: the seam. The architecture lens and the synthesis chose one lower Strategy under two Services. The Q0 architect seat chose two Strategies over one git Adapter. The refuter finds that after C1's refinement and C2's two roles the two designs are close · answered by D6 (C1, 3 of 3, delegated), the PO's to change
- Split: TL-4 says the store's one SVG has no record of its origin. PO-11 says its record has `made_by: conversation`. Both hold: the SVG's folder holds no JSON, and the shelf record that names it holds the maker · P4 (Q27)
- Split: the riskiest assumption. The synthesis chose A2 (feasibility). The refuter names A3 or A9 (value: 0 tags, one reader) as possibly riskier · Q1 (P9)
- Split: the PO assistant lens found that nobody is blocked against the MVP bar (PO-8). The council's order (D-q7, D6) still plans every slice · Q1 and the Ready order, the PO's
- Split: the synthesis narrows the P158 rule to "a transport that merges", while the source says "any transport" · C14 stands as delegated, the PO's to change. The A2 spike does not test it
- Not covered by any lens before the refuter: a project whose own .gitignore excludes `.spark/` (zigbee-stick), and P1027's guard against committing a person's own edits · P7 (Q30), revised at 09:45 CET

## Searches

none
