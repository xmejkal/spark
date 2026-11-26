# Refuter: P1193 change tracking

The refuter on Opus, 2026-11-26, on HEAD b9e95a68. Its role is read-only, so the main session wrote this file from its
returned report, word for word.

Five verdicts that matter most:

1. ★C16 is refuted on "by hand". 22 of the 24 board.tsx commits carry a "Co-Authored-By: Claude" trailer. 23 of the 24 date from 2026-09-22 to 2026-10-11. The pre-mortem, A4 and the risks table repeat "24 hand commits".
2. The A2 pass line "the named point survives the squash in 3 of 3" cannot fail on a local clone. Any ref keeps its commit and every ancestor safe from gc. In my run, a fresh clone did not get `refs/spark/*`, and a default fetch did not get it either, even after an explicit push. So ★C23 is true, but it tests nothing that is at risk.
3. ★C19 claims more than its evidence. Squash merges are not the only way a kept step's id leaves the branch: in a scratch run, `git pull --rebase` did the same with no squash. smartbin-local has only merge commits (5), which keep ids. firebeetle-games mixes 29 merge commits with 13 squash-style commits. Only p934-display2 squashes every PR (2 of 2).
4. The synthesis rejects "two Strategies over one Adapter" because "the choice is also made twice". Its own C2 answer then adds two roles, `project-timeline` and `shared-records`, so the choice is made twice anyway. D3 fixes the central repository as git, and C1's refinement moves send and receive onto a second interface. After those two changes, options (a) and (b) are close to the same design.
5. Existing repositories: zigbee-stick's own `.gitignore` ignores `.spark/`. firebeetle-games tracks no `.spark` file. requirements.json is tracked on the checked-out branch in 1 of 9 repositories. A kept step in these answers UNHELD unless P7 (stage files git does not hold) gets a yes, and the A2 spike on firebeetle-games depends on P7 as well.

## Check first: existing product

**Does the change address the observed problem?**
- Only one outside change has been observed (★C18). Slice 1 / N2 handles it with no git at all.
- The board.tsx layout edit is a predicted case. ★C17 rests on 2 stamped files, not 6 (see part 1).
- Named points (0 tags), compare and sharing (n = 1) answer requests the PO made, not harms anyone has seen.
- PO-8 found that "Nobody is blocked by the missing feature, measured against the MVP bar". The brief's findings leave that out.

**What breaks for current users**
- **The 9 repositories.** The `.spark` records are mostly untracked, as the counts above show. In zigbee-stick, `git check-ignore -v` gives `.gitignore:4:.spark/`. No option or question covers a project whose own ignore rules exclude `.spark/`. P7 covers untracked files, not ignored ones.
- **Init's brief commit (P1027).** `project_commit.py:5-6` says: "A file git does not hold, a person's own edits or a HEAD off a branch give a reason and no commit."
  - D-q2(a) ("kept on a yes") and slice 5 ("while the bytes are the person's") both commit bytes spark did not write. That reverses this guard.
  - D-q2 lists "Keeps: … P1148 D11 and D12" and does not name P1027's guard as reopened.
  - Smallest fix: add "Reopens: P1027's rule that a person's own edits give no commit" to D-q2 and to slice 5.
- **The ignore list (P1150).** No break. The change is limited to the docstring at ignore_list.py:32, which the folder names.
- **The store's refusal of private places inside git.**
  - Reproduced: with a repository at `<home>/shared`, a shelf write passed. With a repository at `<home>`, the write raised `store_in_repository` and a catalog write passed.
  - No break as long as the clone stays in a sub-folder.
- **The build's rule for a person's board.tsx.**
  - PO-2's risk is named: an older board.tsx that a take-back restores reads as the person's file, and no build makes it again.
  - Not named: `git restore --source=<ref> -- rec.json` silently overwrote an uncommitted edit (output: `rec=r2`, status ` M rec.json`).
  - So the git member must call `held_as_is` before every restore, or the pass line's "an uncommitted edit … stays" fails.

## 1. The ★ claims

- **★C1 · holds.** ignore_list.py:31: "ProjectCommit Adapter answers both and is the default until P1151 hands in the project timeline (`GitProjectTimeline`". words.md:16-17: "No code holds these names yet." The grep gives 1 line.
- **★C2 · holds.**
  - project_commit.py:5: "Spark never stages with `git add`, never runs `revert`, `reset` or `push`, and never skips a hook."
  - :28-29: "The only code in scripts/spark/ that runs git."
  - `grep '"git"' scripts` finds only project_commit.py:42.
- **★C3 · partly.**
  - kept_files.py:92-93: "A `.tsx` is a person's to edit, so one that is there is left alone and named, unless `written` … holds its bytes".
  - But :116 replaces dist/ only under `if (workdir / sheet.CIRCUIT).is_file():`.
  - Change "dist/ is replaced whole" to "dist/ is replaced whole when the build stage made a circuit".
- **★C4 · holds.**
  - finding.md:184: "board.tsx stays a build output, not a kept step | 3 of 3".
  - The store's refuter.md:30: "After Claude makes the PCB smaller (the screen's own suggestion), kept_files.py:106-115 leaves board.tsx alone on every rebuild".
  - That is a scenario, not an observed edit.
- **★C5 · partly.**
  - phase_readers.py:447: "sha256_of(path) != record.get("requirements_sha256")".
  - :413: "Strategy: requirements.json against what the picks give".
  - :545: the firmware line comes only from `main.stat().st_mtime`.
  - Change "each phase reader compares sha256 stamps" to "the needs and build readers compare stamps, the requirements and breadboard readers compare content again, and the firmware reader shows a file time". I did not check the image or the fingerprint.
- **★C6 · holds.** flow_codes.py:11: `PHASES = ("idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy")`.
- **★C7 · holds.** store.py:146-147 lists 11 names. :387: "if private and inside_git(target):".
- **★C8 · holds**, in its corrected wording.
  - The store gave "fatal: not a git repository".
  - Counts: 18 catalog records, 13 JSON files on the shelf, 153 source folders, 1 SVG in sources/.
  - Another 477 SVG files sit in toolchain/.
- **★C9 · holds.** `ls parts` gives 10 entries: 8 JSON records and 2 folders. There are 6 pictograms.
- **★C10 · holds** for the quotes, but its caveat is partly wrong.
  - store-discovery.md:209-210: "a public repo of records that pass the contract, cloned read-only". Line 215: "**Not building:** pluggable storage backends".
  - Line 225, the PO's own decision: "(4) P84 **drops the database/NoSQL/Markdown half**". Line 135: "**No pluggable backends now** — no database, NoSQL or Markdown store".
  - So "only the trigger … is the PO's decision" is too narrow. Change it to "the PO's decision (4) also dropped the database half, which the council's line 135 calls 'no pluggable backends now'".
- **★C11 · holds.**
  - proposal.md:449-450: "What any transport needs first is R4 plus a tombstone (FEASIBILITY §2.2): without them every transport corrupts quietly."
  - R4 (:342) is wider than "a record identity". It also includes "one `based_on` shape on every copy".
- **★C12 · holds.** storage.py:22: `NAMESPACES = ("registered-projects", "boards")`.
- **★C13 · partly.**
  - part_facts.py:119-120: "if project_name: copy["based_on"] = {"project": project_name, "digest": digest(record)}".
  - Only copies shelved from a project carry it: 9 of 13 shelf files, and 0 catalog records.
  - Change to "A shelf copy shelved from a project carries…".
- **★C14 · holds.** `len(CATALOGUE)` gave 51.
- **★C15 · partly.**
  - kept_moves.py:3-4: "reads the earlier file before the build writes the new one, keeps each part where the person put it when it still fits".
  - The file is rewritten on every build, and only part positions carry over.
  - Change to "The build rewrites breadboard.json and carries over each part position the person set, when it still fits".
- **★C16 · refuted on "by hand".**
  - The counts reproduce: 24 commits, 4 of 9 repositories, 0 tags, 0 "spark: " commits.
  - 22 of 24 carry "Co-Authored-By: Claude". One subject reads "The generated board carried spark's false wake fact; regenerated after spark P63".
  - The 5 commits for requirements.json count all refs. Only 2 are on checked-out branches.
  - Change to "24 commits touch board.tsx in 4 of 9 repositories, 22 of them co-authored by Claude, 23 of them between 2026-09-22 and 2026-10-11".
- **★C17 · partly.**
  - ux-ai-ux.md:38: "In the 6 projects that hold a build record, no board.tsx differs from its `written_sha256`."
  - Only 2 of the 6 build.json files have a board.tsx stamp (p934-epaper, p934-display2). Both match.
  - Change to "in the 2 of 6 build records that stamp a board.tsx".
- **★C18 · holds as a code path.**
  - phase_readers.py:169-170: "if held is None: return False, []".
  - Commit e5f6be0's body says: "Drop the press must line at the PO's word". project.json's "decided" list now holds "the press screen is dropped for now".
  - So the "Found on the way" caveat, "whether the need is still wanted is the PO's call", is already answered in the repository.
- **★C19 · partly.** UX-2: "The id loss after a squash is H".
  - First-parent counts: p934-display2 has 2 squash-style commits and 0 merges. smartbin-local has 5 merge commits and 0 squash. firebeetle-games has 29 merge commits and 13 squash-style commits.
  - Change to "p934-display2 squash-merges, the other two mostly keep merge commits, and a squash or a rebase moves spark's commits off the branch".
- **★C20 · holds.**
  - `//` keys: 28 of 28 records.
  - `based_on.project`: 7 of 28 records.
  - 2 fact sources name him and "<walks>/p934-display2/…" (the main session replaced a home path here).
- **★C21 · holds.** Reproduced in my scratch store, as described under "Check first".
- **★C22 · holds.** tool_finder.py:531: "def use(role, tool_name, project=None, personal=None):". tools.json has 14 roles and no git entry. Note that `use` checks a contract only when the role has one (:535).
- **★C23 · holds, but the claim is weaker than it looks.**
  - Reproduced with git 2.49.0. The ref resolved, and K1 is its ancestor, so gc can never prune it.
  - Not in the caveat: restore overwrote an uncommitted edit, and the ref was missing from a fresh clone and after a fetch.

## 2. The brief against its detail

- **PO-8's "Nobody is blocked"** is missing from the brief's findings. The tech lead's Q0 line, "Snapshots, compare, merge and sharing are tooling to pause", became an order (D-q7), and no option keeps them paused.
- **PO-5** ends with "It does not decide one Strategy against two". The brief says the PO assistant "held b".
- **PO-12's caveat** "Whether these merges are PR merges of code or merges of records: —" is missing from ★C19.
- **UX-6's caveat** "My count of 42 `.spark` folders includes nested and walk folders" is missing from ★C17. I found 30 `.spark` folders at depth 4 or less.
- **The synthesis narrows C11.** It says "C11 speaks of a transport that merges", but the source says "any transport". D-q8(a) and C14 rest on that narrowing.
- **The synthesis's "the digest that `based_on` holds already"** ignores R4's "two `based_on` shapes" and "digests written and read by nothing". It also ignores that catalog records have no `based_on` at all.
- **"24 hand commits"** in A4, the pre-mortem and the risks table is stronger than PO-1.
- **TL-4 and PO-11 contradict each other.** TL-4 says the SVG has no origin record. PO-11 says its record says `made_by: conversation`. No split row names this.
- **The Options cite "(C7, C8)", "(C10, C16)", "(C11)", "(C12, C13)" and "(C14)".** These are the synthesis's C-questions, but they collide with ★C7 to ★C16.
- **Outcome (1)** keeps a layout edit "noticed" as one step. breadboard.json has no stamp (TL-6) and is rewritten on every build.
- **jobs-and-journeys says "9 of 22 project folders".** PO-1 says 23 that still exist, and I counted 23.

## 3. Rival explanations not ruled out

- **The seam.**
  - The shared side has one real mechanism (git, after D3) and a Fake. So ARCH-3's "2 × N classes" is closer to N + 2.
  - Two roles mean the choice is made twice under (a) as well.
  - The rival: (a) and (b) end up almost the same design, and (a)'s only cost is the change to the delegated words.md:21.
- **The squash claim.**
  - Any history rewrite moves the ids: a squash, a rebase pull (reproduced) or an amend.
  - Merge commits keep the ids.
  - The old objects stay resolvable locally until the reflog expires. A `git revert` of K1 after the squash refused here only because of a content conflict.
- **The named ref.** It survives because it is a ref. The risk is somewhere else:
  - a second machine or a fresh clone does not have it
  - after a squash, the steps after the point are no longer on main, so a range take-back by ids cannot be computed there
  - the host's handling of custom refs was not tested.
- **A4's value.** The board.tsx commits look like Claude's fixes and spark regenerations from September and October, not a person's layout edits.
- **The riskiest assumption.** A3 or A9 (value: 0 tags, one reader) may be riskier than A2.
- **The 10-04 conflict.** Read as above, the PO's decision (4) covers "no pluggable backends now", so D1's "no conflict" is a delegated reading of his decision.

## 4. Numbers without unit, population, period or provenance

- **★C9's "10":** entries, not records.
- **★C16's "24" and "5":** no period is given, and the 5 counts all refs.
- **★C17's "1 of 42":** the population is unmatched to the projects list.
- **★C20's "7 to 9":** two populations, 7 of 28 records and 9 of 13 shelf files.
- **PO-12's "115", "30" and "1063":** these count all refs and local branches, which the text does not say.
- **UX-3's "79 + 32" and "186 + 124 uses":** no unit.
- **"Stands on: 11 H":** does not say which 11.
- **S, M, L and "about one hour":** unmeasured estimates.

**Home paths and times**
- No path starting with the home folder appears in the folder.
- Some times are later than the commit that holds them:
  - items.md:9 "09:40 CET", committed 09:34:55
  - ux-ai-ux.md:6 "09:10 to 09:35 CET", committed 09:19:00
  - po-assistant.md:6 "09:05 to 09:25 CET", committed 09:19:00
  - the sketch times of 26 Nov in ux-ai-ux.md (10:12 to 11:20)
- ux-ai-ux.md:183's "20:10" has no date.
- Note: HEAD moved to b9e95a68 (09:37:05) while I worked. My quotes match it.

**Could not check:** a host's squash merge or custom refs (no account test), the image and fingerprint parts of ★C5, and P1148's documents.

**Scratch:** I used $TMPDIR/refuter-p1193.3e9S with a scratch SPARK_HOME inside it, and removed it. I also removed one stray file I had made, /tmp/refuter_w_path_<pid>. The tree is clean.

## Searches

none
