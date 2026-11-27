# P1247: the follow-up trial with KiCad's JST model: rows

Card: [P1247 #1804](https://github.com/xmejkal/spark/issues/1804). The finding is
`docs/discovery/2026-11-26-p1197-3d/spikes/s2-jst-model.md`. This file holds the acted, raised and rejected findings of
the PR's own review (one refuter on Opus, docs only). 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The width claim rests on search result text, and the record's 7.9 x 5.8 mm mixes the 3-pin header's width with the 2-pin plug's width. JST's drawing gives 5.9 x 4.5 mm | PR refuter (Opus), finding 1 | acted | the finding now cites JST's drawing with its sha256. Page 3 was read again with `pdftotext` |
| 2 | The wrong record has no card | PR refuter (Opus), finding 2 | raised | filed as P1335 #1915 |
| 3 | The side of the model's latch was not compared with the footprint | PR refuter (Opus), not checked list | acted | the finding says it |
