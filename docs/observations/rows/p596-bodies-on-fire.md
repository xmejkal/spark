# P596 bodies on fire: rows

What the plan, the review, the refuter's planted defects and the sanitizer run found. Card: [P596 #797](https://github.com/xmejkal/spark/issues/797).
PR: https://github.com/xmejkal/pixel-games/pull/20. Numbers are in pixel-games `bench.md`, section "P596 (#797)".

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan check found 4 MUSTs | PR 20, "Checks" | acted | fixed in the plan before code |
| 2 | The refuter planted 12 defects across the five claims and the tests caught all 12 | PR 20, "Checks" | verified | counted as this PR's mutation run. The Sonnet reviewer found nothing |
| 3 | An ASan and UBSan run of `fx_fire_burn` over every edge coordinate found nothing | PR 20, "Checks" | verified | no change |
| 4 | Smoke and its picture variant were cut by the PO: "you don't need to go to details with this yet" | [comment](https://github.com/xmejkal/spark/issues/797#issuecomment-6624863878) | closed | waits for later effects work |
| 5 | In C mode a frame that drops a body burns once at its old resting place | PR 20, scene tests | raised | harmless, one frame. Not fixed |
| 6 | With the base off, burned heat on the bottom row never rises | PR 20, `fx_fire_set_base` | raised | cosmetic. Not fixed |
| 7 | The fire's own look climbed to the top of the screen on bodies | PR 20, `tools/render_scene.py` | acted | the burning look (decay 32, cool 40, fade 16, heat 200) was set from Mac renders before the board |
| 8 | A feel slice stops at "ready to play" until the PO plays it | [comment](https://github.com/xmejkal/spark/issues/797#issuecomment-6625120559) | closed | the PO merged: "merged go on" ([comment](https://github.com/xmejkal/spark/issues/797#issuecomment-6625179950)) |
