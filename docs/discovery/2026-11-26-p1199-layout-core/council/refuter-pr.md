# The PR's refuter: PR #1777 (P1199), docs only

Opus, 2026-11-26, at 747e769d. The refuter agent is read-only, so it returned this report as text. The main session
saved its findings here in short and acted on each (docs/observations/rows/p1199-layout-core-discovery.md).

Verdict: not ready to merge. Points 1, 4 and 5 block it. The rest are small fixes.

1. Blocks. D12 and the readiness line do not match the option the PO picked. "Yes, that is it" was described as "Confirms the frame, the jobs, the direction and the remaining risk, so the discovery hands off to design after the MVP." D12 recorded only the jobs, the direction and the riskiest test, and the Ready line said no D accepts the remaining risk. By the rule at the top of brief.md, D1 and D12 meet "design". "An experiment" needs the test chosen before an option, and D3 to D8 chose options before or with D9.
2. D12 to D14 say "about 14:38". The dialog's answers came at 14:40:26 CET. D10's relay arrived at 14:34:51, so "read by `date` when the relay came" is not quite right.
3. Two D lines claim more than the PO was asked: D7's "stays `first-fit` on the breadboard" and D14's "bench day" note.
4. Blocks. Four places still say all 9 goldens stay the same, against D13's 8 of 9: items.md:74, story-map.md:19, brief.md:70 and outcome (1) at brief.md:17.
5. Blocks. items.md:63 and the Needed by of #1789 quote "one seam per strategy, … nothing twice" as the PO's words. That is spark-main's gloss. His own words are "…its reusable, dry, etc etc".
6. Stale text: brief.md:12 lists Q1 to Q8 as open. risks-and-tests.md:22, :35 and :51 still offer the seller's page, which Q8 dropped. The hand-off lists the unconfirmed no-gos as constraints. items.md:8 says spark-main files the items, but this session did. items.md:9 leaves out item 7 under Q4.
7. Holds: D1 to D6 and D8 to D11 match the relays. Every A row matches D11. The four cards have the right parent, Status Idea, the Slice Views and editors, and unused P-numbers. The nine comments match items.md and quote the PO word for word. The code citations hold. No /Users/ path, no secret, no vendor file in the diff.

Could not check: spark-main's "about 13:15" and "about 14:20".

## Searches

None.
