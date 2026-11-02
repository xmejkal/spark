# P518: the deploy page offers the grant once

The rows of P518 (#714), the walk 4 council's N6a: the deploy page offers the deploy grant once per session, at the first stop for a typed yes. A page change only, written by the lead in the PO's full auto mode on 2026-11-02.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | deploy.py prints the grant line only where a grant can cover the deploy, and `--json` puts it in `next` as a `grant` step with `needs_yes`. | card | verified | `deploy.py:134-148` adds `grant_hint` only when `board_grant.grant_may_cover(report, evidence)`. `board_envelope.py:95-98` appends `outcomes.step("grant", ..., needs_yes=True)` |
| 2 | An image that no simulation tested gets no grant line, so the offer does not help those deploys. | card, P510 decision 1 | verified | `commands/deploy.md` "No simulation" step 3: a deploy grant never answers it, and deploy.py offers no grant line. Decision 1 kept "never" (P510 plan, taken in auto mode) |
| 3 | `commands/deploy.md` has 32 older hits of the simple-english lint (long sentences, semicolons, a "could"), none in the lines P518 changed. | the lint hook on the edit | raised | row only: for the docs council P498 (#682) and its next pass |
| 4 | "At the first stop for a typed yes" misses the offer when that first stop has no grant line (a look with a warning, a `--no-simulation` deploy). The `--json` step's argv carries 60 minutes, while the page says N. | PR refuter 7, 8 | acted | step 3 now says "where deploy.py printed the deploy grant line" and "In `--json`, its argv says 60: put in the person's N" (`deploy.py:266`) |
