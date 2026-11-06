# P639 flames in front of a burning body: rows

What the plan refuter, the Mac frames, the board runs, the PR review and the PR refuter found. Card:
[P639 #854](https://github.com/xmejkal/spark/issues/854). PR: https://github.com/xmejkal/pixel-games/pull/40.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The Mac PNG could not show a body under the flames: the test canvas `Recorder.fill` only logs, and `render_scene.py` reads `tft.frame` alone | the plan refuter (Fable) | acted | the Mac `Tft` got `fill_rect`, and the render tool paints through `lcd.TftCanvas` |
| 2 | `tests/test_burning.py:99` expects `nearest` after one tap, and three modes make it `picture` | the plan refuter | acted | the test expects `picture` |
| 3 | Names after Godot's `Environment.BGMode` (`BG_NONE`, `BG_COLOR`, `BG_SKY`) for a third ground | the plan refuter | rejected | the PO's two-pass pick made the opaque field the black ground, so the old blend flag stayed and the constants went |
| 4 | Design A, one blend at the fire's alpha over the bodies, hid each burning body inside its burn: the burn sits on the body at heat 200, and the alpha is full from heat 96 | the Mac frames, 2026-11-06 | acted | the PO picked two passes, then a soft cutout from five front layers (rows 5 and 6) |
| 5 | Front layers on the board, linear: half opaque 17.30 to 18.04 ms of draw, a second field 14.30 to 14.39 ms with 6.8 ms more step, the soft cutout 14.80 to 15.03 ms | the board, runs 119 to 121 | acted | `bench.md`, the P639 section. The cutout is cheaper than the half-opaque front, because the blend skips alpha 0 and copies alpha 255 |
| 6 | D5's line (13.5 ms of draw, 23 fps) does not hold: linear draws 1.3 to 1.5 ms over it (0.7 ms of it the body fills the old draw never timed), and the picture mode falls to 21 to 22 fps | the board, run121 | raised | the PO judges the look and the line on the panel. P601 #802's trigger (a blended draw over its line) now fires |
| 7 | The PO: "maybe we can generalize it and offe more kinds of combinations like that" | the PO, 2026-11-06 | acted | card P643 #861 in Idea, under #812 |
| 8 | The PO asked whether the chip's PIE helps the blend. No PIE runs in the engine today, and P580's estimate is 100 against 337.5 ns a pixel, never measured | the PO, 2026-11-06 | raised | P601 #802 holds the SWAR rung, then one PIE `.S` probe. The order waits on the PO |
| 9 | The burning scene's `MODES` became a copy of the fire's, and its docstring named two modes | the reviewer (Sonnet) | acted | `MODES` inherited, the docstring names three modes (077439a) |
| 10 | NITs: three `--- MVP (P639) ---` markers in one class, `draw_over` has no guard for a missing field, "(P639)" twice in a docstring | the reviewer | acted | markers trimmed, the docstring says its callers check (077439a) |
| 11 | Stale cites in the docs the PR touched: `fire.py:166-169`, `:90-91`, `:240` | the PR refuter (Fable) | acted | moved to `fire.py:129-136`, `:94-95`, `:277-280` |
| 12 | The no-engine test asserted no draw count, so bodies drawn twice or never would pass | the PR refuter | acted | the test counts eight fills |
| 13 | `docs/engine-walkthrough.md` and `docs/engine-deep-dives.md` hold older stale cites outside this card (`rain.py:50`, `burning.py:56`, `:58`, `:69`, `:80` in the walkthrough) | the lead's sweep | raised | for the docs council's next pass (P498), not this PR |
| 14 | The earlier per-mode run script set `self.mode` without `set_mode`, so its filter and blend did not change | the lead | acted | P639's run scripts start a mode through `setup` |
| 15 | The mutation run: 12 planted, 10 caught. `draw_over` passing `ALPHA` in place of its alpha escaped, because the test mocked `draw_over` and never saw what reached the C draw. `heat <= FRONT_CLEAR` escaped as an equivalent mutant (the ramp gives 0 at 120 too) | the mutation tester | acted | the engine stand-in records each alpha, and the test asserts the tables that reach the C draw. The replanted defect fails |
| 16 | Over the bright sky the flames had dark borders: the cool edge cells are dark red to black, and the normal blend mixed them into the sky. Additive and screen blends remove the borders but wash the fire out to white over that sky | the PO on the panel, then Mac frames, 2026-11-06 | acted | `BLEND_PALETTE` (alpha bleeding): below heat 96 each heat takes heat 96's red, and only the alpha fades it. No cost on the board (run122) |
| 17 | The PO: "let's generalize it and like have a base class, the fire is just a type of, use general standard words" | the PO, 2026-11-06 | acted | card P644 #863 in Idea, under #812, after P643, P601 and P640 |
| 18 | After `mpremote cp` the board waited at its prompt, and the PO found it "stuck" | the PO, 2026-11-06 | acted | the board reset, and a rule in `~/.local/share/spark/learned-rules.md`: end each board session with a reset and read the boot lines |
