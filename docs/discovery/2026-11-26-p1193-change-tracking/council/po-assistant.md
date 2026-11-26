# PO assistant lens: Existing first, and Risks and assumptions

The PO assistant lens on Opus, 2026-11-26. Its role is read-only, so the main session wrote this file from its
returned report, word for word.

Read 2026-11-26, about 09:05 to 09:25 CET. D1 to D5 in brief.md:88-92 are taken as D.

## Findings

- **PO-1** · The maker already keeps board.tsx by hand in git, more often than the decided records. 9 of the 23 folders listed in the store's projects.json that still exist are git repositories.
  - Across them, 24 commits touch board.tsx: smartbin-local 15, irrigation 6, spark-quickstart 2, p934-display2 1. Only 5 commits touch requirements.json.
  - board.tsx is tracked in 4 of the 9.
  - No repository has a tag (0 in 9).
  - No commit message starts with "spark: " (0 in 9), the prefix of `ProjectCommit`'s brief commit (scripts/spark/build/project_setup.py:400).
  - Tag: E · read-only git with GIT_OPTIONAL_LOCKS=0 over projects.json's folders, about 09:15 CET.
  - Supports only this: J1 for board.tsx is done today by the person's own commits. J3 (tags) has no observed use. The git strategy has no field record in a real project. It does not show who made each board.tsx change (the person or Claude).

- **PO-2** · Making board.tsx a kept step (D-q1) runs into two of P1160's delegated answers.
  - Q4 (finding.md:186): spark refuses a take-back when a person's commit changed a file that a kept step holds. With PO-1's hand commits of board.tsx, every range take-back over it would refuse.
  - Risk 2 (finding.md:166-167): a taken-back board.tsx reads as the person's file, and every build leaves it alone (scripts/spark/build/kept_files.py:111-114). So taking back a pick would bring back an old board.tsx that the next build never makes again.
  - Tag: E · those pointers. Not tried in scratch.
  - Supports only this: D-q1 cannot reopen P1160 Q2 ("board.tsx stays a build output") without also reopening Q4 and the build's rule for the person's file.

- **PO-3** · The PCB and the perfboard have no record of their own to keep.
  - On #1600, closed 2026-11-26 09:01 CET, the PO chose "B: KiCad as an export". tscircuit stays the board engine, and the KiCad work comes after the MVP.
  - So the PCB's size and placement live in board.tsx, and dist/ is made again on every build (kept_files.py:89-123).
  - The perfboard exists only as a greyed station (scripts/spark/flow/flow_codes.py:464). The past-breadboard PO stand-in says "The perfboard layout is an example that spark did not plan" (the store's councils/past-breadboard/po-stand-in.md:31).
  - The brief still lists P1089 as open (brief.md:32) and as out of scope (brief.md:20).
  - Tag: E · #1600's last comment, read about 09:12 CET.
  - Supports only this: "keep the PCB" means "keep board.tsx" today. "Keep the perfboard layout" has nothing to keep yet. This fits Q0's rule that each area declares its kept step's records.

- **PO-4** · A push to the new public repository (D3) would carry private free text that the 10-04 filter does not remove.
  - The 10-04 plan filters the shelf "of `owned`, `sourcing`, `photo`" (docs/archive/2026-10-04-store-discovery.md:200). None of the 28 shelf and catalog records has a `sourcing` field. The filter covers fields only, so the `//` comments stay.
  - `//` comment keys sit in 28 of 28 records. Some examples:
    - `//sourcing` in shelf/ds3231-at24c32-rtc-module.json: "Owned; in the drawer, in its bag, unused".
    - `//photos`: "the top and back photos of 2026-09-29 are the PO's".
    - `//sourcing` in two shelf records: the shops he searched, with dates.
  - `based_on.project` names his private project folders (irrigation, walk4, p934-epaper, reaction-game) in 7 of 28.
  - `order_code_at` names shops in 4.
  - Whatever reaches a public git history stays there. His rule rewrites history only for a secret (his memory note "History rewrite only for secrets", PO 11-23).
  - Tag: E · key count over the store's shelf/ and catalog/, about 09:18 CET. Whether he counts project names as private: —.
  - Supports only this: D-q5 needs a list of which fields leave the store, including the `//` prose and `based_on`, before the first push. It does not show that a leak has happened.

- **PO-5** · Two earlier store plans describe the shared side differently from "one strategy that pushes and pulls".
  - The P158 proposal's "Three relations, three mechanisms" (STORE-8, docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md:423-433):
    - shared and local: records only, through git, read-only at a pinned commit
    - the person's own machines: the person's choice
    - local and project: a copy pinned by a digest
  - The 10-04 trust lens: "shared records read-only — editing one opens a pull request" (store-discovery.md:173).
  - P1160 Q3 refuses a merge on every interface: "No merge by Claude, because the CLI, MCP and a server have no Claude" (finding.md:185). J5 asks for a merge.
  - Tag: E · those pointers. They are council text, not the PO's D. D2 replaced only his trigger.
  - Supports only this: for one strategy to serve both, the shared part is at most one lower git Adapter. The verbs and the conflict rules differ: a project takes back only spark's own steps and refuses on a conflict. A shared record is pulled read-only and changed through a review. It does not decide one Strategy against two.

- **PO-6** · "Configurable, chosen once" has no home today.
  - No settings file of the person's is read anywhere in scripts/. A grep for settings.json, config.json and preferences finds only the firmware image's /config.json (scripts/flash_image.py:44).
  - D6's "turned off once in a configuration" is part of P1152's first slice, which is not built. P1151 #1687, P1152 #1688 and P1155 #1691 are open.
  - The A1 test of D13 (P1155) has not run, and P1152's later slices wait on it.
  - Tag: E · `gh issue view` states, about 09:10 CET.
  - Supports only this: J8 starts from zero for the setting. If one setting chooses the strategy for both, a person who turns git off for projects (D6) would also turn off the shared side. Nothing the PO said decides that coupling.

- **PO-7** · How firm each job is, in his words on #1738:
  - "maybe somewhwre it would also be useful to have a comparison of two  or even merging them": J4 and J5 are "maybe".
  - "definitely pushing and pulling things to some central repo, like the parts maybe and probably more things": push and pull are "definitely" (J6, J7). Which records go is "maybe" and "probably".
  - "we want to have a strategy to track them and be able to see if things changed from the outside or be able to go back, make tags or like snapshots": J1, J2, J3 are "want".
  - "we actually want to have that with all main steps that can be reverted": J1 is firm.
  - "probably the first implementation that comes to mind is again GIT": "probably" here, and firm in P1148 D5.
  - Tag: E · #1738 body.
  - Supports only this: the depth of each job, for D-q4 and D-q7.

- **PO-8** · Nobody is blocked by the missing feature, measured against the MVP bar.
  - The breadboard journey works without it: README.md:127, Bench, P934, "ready seen", 2026-11-22.
  - The harm today is that a Claude edit of board.tsx is kept by no spark step (the store's past-breadboard refuter.md, part 3). The maker's own commits already cover that in 4 repositories (PO-1).
  - The shared side has n = 1. D2 dropped the trigger that waited for a second person, so the only real user who can see it working is the PO with a second store. Outcome (4) uses a scratch store.
  - Tag: E · pointers. "Nobody else" is H, from jobs-and-journeys.md:8.
  - Supports only this: D5's order. It is a risk that the shared side's value is never seen.

- **PO-9** · A read-only pull already exists for spark's own library: parts/ (10), boards/, chips/ and 6 pictograms reach every maker inside the plugin's public repository (brief ★C9).
  - The 10-04 architect: P84 becomes "one more read-only folder on the search path" (store-discovery.md:147).
  - P390 #505, a board onto the shelf so that every local project finds it, is still open. It holds the PO's 2026-10-22 words "at least locally for all projects first".
  - Tag: E for the library and the issue. That a plugin update pulls at a pinned version is H (not read in code).
  - Supports only this: J7's first form can be one more read-only layer, reusing how layers are read. It does not show that a push fits that model.

- **PO-10** · Identity and tombstone (D-q8) are unbuilt.
  - The records hold `id` in 28 of 28 and `vendor` with `sku` in 28 of 28. `part_number` is in 2.
  - No record has `origin`, `review` or `written`, and nothing is a tombstone.
  - The 10-04 plan item 8, "Identity and provenance … Pulled by P84" (store-discovery.md:207), is now pulled by D2.
  - Tag: E · key count, about 09:18 CET.
  - Supports only this: D-q8 is real work before the first push.

- **PO-11** · D4 can be read from the record, not from the folder.
  - The store's one SVG, sources/f6a03caa…/epaper-breadboard-top.svg, sits among vendor documents.
  - Its record (shelf/epaper-2in9-bwr-mh-et-live.json, `pictures.breadboard-top`) says `made_by: conversation`, "drawn by the conversation from the PO's front photo, 2026-11-20", and `verified: False`.
  - Tag: E.
  - Supports only this: a push filter based on `made_by`. Whether a drawing traced from a photo of a vendor's product counts as "drawn" under D4: —.

- **PO-12** · The maker merges by hand.
  - firebeetle-games has 115 merge commits, 30 branches and 1063 commits. smartbin-local has 5 merges. Both have GitHub remotes, and so does p934-display2.
  - P1148 Q14 (which branch spark's kept steps go to in a project that merges by PR) is still queued (docs/discovery/2026-11-25-spark-and-git/brief.md:106).
  - Tag: E · the git read of PO-1.
  - Supports only this: J5 exists in git by hand. Whether these merges are PR merges of code or merges of records: —. The branch rule must be settled before a kept step lands in these 3 repositories.

- **PO-13** · Which earlier decisions this epic keeps, widens or conflicts with:
  - **Keeps:** P1148 D6, D7, D11, D14, and D-j (holds never leave the machine).
  - **Widens:** D5, from the project to the store. D8, by board.tsx and breadboard.json. D9, where a snapshot could be a named kept step.
  - **Open conflicts:**
    - P1160 Q2 and Q4 (PO-2). Delegated, his to change.
    - P1160 Q3 against J5 (PO-5).
    - The 10-04 read-only shared side against push (PO-5).
    - words.md:29 keeps "commit" and "history" out of the names, and D-f says no message names git. "Push", "pull" and "tag" are git words, and words.md has no rows for them yet.
    - The brief's scope, "out: … a git host account or a paid service" (brief.md:20), against D3's "a new public repository under the PO's account".
    - D12, "nothing for a server is built" (spark-and-git brief.md:129): a hosted central repository is not spark's server, but this is not settled.
    - Is a pull that changes a local record a take-back-like overwrite that needs D14's preview and yes? —
  - Tag: E · pointers.
  - Supports only this: the list of decisions the synthesis must name as reopened.

- **PO-14** · Pre-mortem: "It is six months after this shipped, and it failed. Why?" Tag: H (this lens), each reason resting on the E rows named.
  1. A `//` comment or a project name went to the public repository, and stays in its history (PO-4).
  2. Every take-back of a board refused, because the maker's own board.tsx commits sat between spark's steps (PO-1, PO-2).
  3. A taken-back board.tsx was never made again, so the PCB drifted from the circuit (PO-2).
  4. Nobody pulled. The shared repository has one writer and no reader, because the 10-04 trigger was dropped (PO-8).
  5. Turning git off for one project silently turned off sharing too (PO-6).
  6. A merge of two JSON records gave a record that reads but that nobody decided (P1160 risk 6, finding.md:171).
  7. Two copies of one part split, for lack of identity and a tombstone (PO-10, brief ★C11).
  8. Kept steps landed on a PR-flow main branch (PO-12).
  9. The strategy was widened before A1 had ever run (PO-6).

## What I could not check, and why

- Who made each of the 24 hand commits of board.tsx (the person or Claude). The messages were not read, to stay within the time limit.
- Whether the merges in firebeetle-games are PR merges. Not read.
- Whether a plugin update pins spark's library at a version. That is in the code, not read.
- The full text of every `//` comment. Only 6 keys were sampled.
- Whether the PO counts project folder names as private. Only he can say.
- The canvas artboard "Moment: undo that". It is a web artifact, and there was no web.
- The other lenses' reports did not exist yet.

## Questions for the decider

1. A person's own commit of board.tsx: does it block a take-back (P1160 Q4)? Or is board.tsx a kept step only when spark wrote it, or Claude wrote it through spark? · decides D-q1 together with P1160 Q2 and Q4.
2. One setting for both the project timeline and the shared side, or one setting per purpose that names the same strategy? · decides D-q6 and the coupling with D6.
3. Which fields, and which free text, leave the store on a push: `//` comments, `based_on.project`, `order_code_at`? · decides D-q5's filter.
4. Does a push go straight into his public repository, or as a pull request into it (store-discovery.md:173)? · decides D-q5 and whether a review exists.
5. Can a pull overwrite a local record, with D14's preview and yes? Or is the shared side a read-only layer that never overwrites? · decides D-q5 and the guard.
6. Is a snapshot a named kept step (D9), or a second kind of mark? · decides D-q3.
7. Does merge (J5, "maybe") stay in scope, given P1160 Q3 refuses a merge on every interface? · decides D-q4.
8. The brief's scope says "out: a git host account", and D3 puts a repository under his account. Which wins? · decides the brief's scope line.

## Searches

None.
