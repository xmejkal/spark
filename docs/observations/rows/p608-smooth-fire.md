# P608 the smooth fire: rows

What the plan, the review, the mutation run and the board found. Card: [P608 #810](https://github.com/xmejkal/spark/issues/810).
PR: https://github.com/xmejkal/pixel-games/pull/25. The plan is named "the plan" here.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The refuter (Fable 5.1) found a MUST in plan round 1: the Mac tests' ctypes mirror of `fx_fire_t` lacked the new field, so `fx_fire_init` would write past it | the plan, round 1 | acted | the mirror gained the field in the plan |
| 2 | Plan round 1 SHOULDs: one-word mode names (the report grammar), centre-sampled bilinear weights instead of a half-pixel shift, a `set_filter` args probe, and the draw ms as the gate (`FRAME_MS` caps fps at 25) | the plan, round 1 | acted | all four went into the plan |
| 3 | The plan said "engine is None on the Mac". It was wrong: `import engine` finds the empty `engine/` folder as a package | the implementer | acted | the code reads the engine with `getattr` fallbacks |
| 4 | On the board, the first image: the LINEAR draw cost 12.69 ms (nearest 4.29 ms) and the picture mode fell to 21 to 22 fps. The Fable PR refuter found the cause: the neighbour, the clamps and half the sum were recomputed for 76,800 pixels | PR 25, "On the board" and "Review" | acted | cbbd865 uses a sliding window per panel row: 6.41 to 6.43 ms |
| 5 | Lesson: a per-pixel helper that looks inline can still cost 3x. Time the board before the review. The refuter's Mac -O2 ratio had predicted it | PR 25, "Review" | closed | a lesson for the retro, no change in code — P776: stale note: Lesson, no code change. |
| 6 | The Sonnet review found two SHOULDs: `set_mode` unpacks a mode once, and no name shadows the builtin `filter` | PR 25, "Review" | acted | both fixed |
| 7 | The refuter REJECTED the plan claim that a test catches a blend that does not skip alpha 0: `alpha_blend_565` returns the background at alpha 0, so the skip only saves time | PR 25, "Review" | closed | equivalent, no test can tell the two apart |
| 8 | The mutation run planted 25 defects and the tests caught 23. One was equivalent (row 7). One escaped: burning's linear mode blending | PR 25, "Review" | acted | c0f5797 adds a test that fails on the planted defect |
| 9 | The PO played it: "yeah, great, looks good." | bench.md, P608 row | verified | the feel slice is ready |
