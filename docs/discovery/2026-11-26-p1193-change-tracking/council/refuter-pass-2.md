# Refuter, second pass: P1193 change tracking

The refuter on Opus, 2026-11-26, on commit 566c4882, the sections changed after the first pass only. Its role is
read-only, so the main session wrote this file from its returned report, word for word. Its fixes are in commit 89e319dc.

Three findings that matter most:
1. The revised A2 pass line counts a destructive return as a pass. In my scratch repo, `git restore --source=<point> -- a.json new.json` exited 0. It overwrote the person's own commit on a kept record and deleted a kept record made after the point. Both results meet "kept records equal the point, 0 other files change".
2. P7 and P9 were "revised at 09:45 CET" (brief.md:101), but no revised text exists in the folder. P9 (synthesis.md:285) still points to part 6's old pass line (synthesis.md:333), the one that cannot fail.
3. Slice 5's "Reopens P1027" was not added (story-map.md:47). Outcome (1)'s "noticed" for breadboard.json was not changed either.

## 2. Changed sections against their sources
- C24 leaves out two caveats from PO-8 (po-assistant.md:70-73). One is "The maker's own commits already cover that in 4 repositories". The other is "'Nobody else' is H".
- ★C23 cites synthesis.md:139. That line is the heading "## 3. The decisions". The scratch run is at :179 and :473.
- ★C23's two "real risks" rest on the first refuter alone. verification.md's "how" for ★C23 lists no clone, no fetch and no uncommitted edit.
- ★C19 cites the `pull --rebase` run without saying it was not reproduced. verification.md marks ★C19 "not reproduced".
- The note at the top of synthesis.md says "Three … corrected". Its :152 and :320 still say "24 hand commits", and :241's "the digest `based_on` holds already" carries no note.
- verification.md dates its reproductions "09:36". The refuter's report came after 09:37:05, because it names that HEAD.

## 3. Rival explanation
- The setup puts "one own commit on a kept record" before the return. If P1160 Q4 is kept (C9), the return refuses, so "3 of 3 equal" cannot pass. A plain `git restore` passes by overwriting the commit.
- "Refuses an uncommitted edit" tests a check the spike agent writes itself, because no code exists yet (★C1).
- "Resolves with spark's own refspec": reproduced, so it passes by construction. A plain clone did not get the point. Three risks stay out of every pass line: the plain clone, the host, and a preview of steps that left the branch.
- The ignored `.spark/` case (zigbee-stick) is in no test.

## 4. Numbers
- ★C17 "few project folders": no number, no population.
- ★C19 "2 of 2": squash-style commits by subject, period not given.
- ★C20 "7 to 9": unchanged.
- "Stands on: 11 H": unchanged.
- The collection plan's "about one hour": not marked as an estimate.

Fixes still missing: slice 5, outcome (1), P7 and P9 text, and jobs-and-journeys J2, which still says "each phase reader compares sha256 stamps".

Reproduced: ★C16 (24 commits, 22 co-authored by Claude, 4 repositories), and firebeetle-games with 29 first-parent merges.

Not checked: a host's squash merge or custom refs (no account), and the 09:36 timing.

Scratch: $TMPDIR/refuter2-p1193.k8NB, removed.

## Searches
none
