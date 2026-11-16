# P459: the X2 rule counts every route to print, read or exit: rows

Card: [P459 #619](https://github.com/xmejkal/spark/issues/619), a chore: the card and the change, no plan. New logic: one
lens and the refuter on the PR. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-16.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | five mutation rows of four tables find nothing: p190-serial, p468-serial-warning, p484-onboard-parts and p778-stages-agree-on-simulation, in `scripts/spark/build/build_service.py` and `tools/circuit-to-wokwi/cli.ts`, which this PR does not touch | build (`mutate.py --anchors` on every table) | raised | a comment on [P284 #331](https://github.com/xmejkal/spark/issues/331), the card for rows that find nothing |
