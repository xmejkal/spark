# R9 retro: the PO assistant

**What helped**
- The retro inbox. Each slip was written the day it happened, so the board facts and the inbox agree (WIP slips 10-17 P272 and 10-18 P295; the epic label missing on #224 on 10-15).
- The push hook caught the slip on 10-17 (5 > 4 in flight) and P272 went back to Ready with its plan kept on a branch. Nothing was lost.
- Per-row yes on findings moved to the PO assistant and the tech lead. The "PO assistant lens" run took 3.1 min and 25 tool calls (logs.json).

**What slowed or wasted**
- Epics hold slots. 3 of the 5 cards in working stages are epics (facts.md), so only 2 cards are in flight. P218 sat 4+ days in Design with Waiting since set but no Waiting on, so nobody could tell whose move it was.
- A card that waits only on the PO still counts against the limit. On 10-16 the hook refused the #315 fix because Design held 3. The PO pushed with --no-verify.
- Waiting since is set on 1 open card only, and Review entry time is not kept. The wait in Review cannot be read.
- I pulled work with the stage count, not the in-flight count. Twice in two days.
- The hygiene sweep hit the rate limit 4 times in 5.3 min and read 5.6 M input tokens for 44 tool calls (logs.json).

**One change I ask for**
Make the in-flight count the only gate input, and make it exclude epics and cards whose Waiting on is the PO. Then the pull step prints that count before any card moves. A card in a stage column gets Waiting on and Waiting since in the same edit that sets either one. This removes the slip, the --no-verify exception and the blind P218 wait together.
