# Refuter, the PR's review: P1193 change tracking

The refuter on Opus, 2026-11-26, on PR #1741 and the local commit d789123f. Its role is read-only, so the main session
wrote this file from its returned report, word for word. Each finding is a row of docs/observations/rows/p1193-change-tracking-discovery.md.

Verdict: not mergeable as docs yet. The PR on GitHub (240d3ed8) does not hold D19, D20 or the hand-off, but six cards and eight comments already cite them. Three lines also claim more than the PO's words say.

R-1 · The cards and comments cite "D19 ("all 14")" and "D20 ("Yes, that is it")" as recorded in PR #1741. Neither exists there or on #1738 · E the branch is 1 ahead of origin. d789123f was committed 12:35:39 CET, after the comments of 12:34:56 to 12:35:07 · fix: push d789123f, and post D19 and D20 on #1738.

R-2 · D9 adds "the dry run and the yes stay", and the hand-off repeats it as a constraint. The PO wrote only "spark does", to P3, which asked "who creates it **and gives the first yes**". The no-go "the PO's first yes in his own terminal (P3)" is now stale · E #1738 comment 7187346215, synthesis.md:279, brief.md:83 · fix: mark that sentence as the author's reading, or ask the PO.

R-3 · The hand-off and the #123 comment say "never a photo". The PO called photos configurable, and the settings table gives photos as a default · E #1738 comment 7187346215 (P4) · fix: write "no photos by default, a setting".

R-4 · The #1688 comment says "take-back … (D7, D9, D14)". Those are P1148's D numbers, but in this discovery D7, D9 and D14 mean other decisions · E story-map.md:44 · fix: write "P1148 D7, D9, D14".

R-5 · Stale lines:
- The Ready line says "No D confirms … a direction", but the hand-off says "Confirmed by D20".
- A3 to A11 still say "waits for Q1 (P9)".
- The PR body still says "P1 to P9 wait", "only drawn pictures" and "items list waits for his yes".
- Fix: update all of them.

R-6 · D10 to D13 lost their measured "received 11:17 CET by `date`" (d292e037). They now say "by 12:15 CET" · fix: restore 11:17. Also "12:33" in the board actions: #1750 was created at 12:32:56 CET.

R-7 · A home path: council/refuter.md:100 quotes "<walks>/p934-display2/…" · fix: replace it with `<walks>/p934-display2`.

R-8 · Cards against items.md: N4's card says "Depends on: —" where items says D7. N8's card says "D2 to D4, D7 to D12" where items says D2 to D4 · fix: align them.

R-9 · D8 drops "for new projects" from "asks until configured … for new projects" · fix: add it back.

Confirmed true:
- The ratings and counts (10 H, 5 high).
- Parents, Slice and Idea on all six cards.
- The code lines cited: project_commit.py:6, keep_picture.py:33, store.py:129.
- `commit --only` exits 1 on an untracked file (git 2.49.0, scratch, removed).
- The second pass's fixes.

Could not check: what the PO said for D19 and D20 (relayed only), and the 12:31 `date`.

## Searches
none
