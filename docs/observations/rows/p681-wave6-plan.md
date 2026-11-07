# P681 the wave 6 plan: rows

What the plan council found while Fable 5.1 wrote the wave 6 plan. Card:
[P681 #916](https://github.com/xmejkal/spark/issues/916). Plan: `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`, whose Council section lists each change.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A W6-F1 mutation row could start a paid Wokwi run: the real wokwi-cli is on PATH, the PO's shell exports WOKWI_CLI_TOKEN, and the golden harness passes it on | refuter, round 1 | acted | a fake token in every child, `"also": []` on the shim, a test that the shim is the tool found |
| 2 | The shim never read the token, so the "fake token not set" row survived on the PO's machine | refuter, round 2 | acted | the shim exits non-zero unless the token is the fake one |
| 3 | Moving `import_child.py` unchanged adds an X2 breach | refuter, round 1 | acted | its `main` becomes `import_one` |
| 4 | W6-F3 missed four path sites and `tools/check_commit.py:94` | refuter, rounds 1 and 2 | acted | in W6-F3's fix list |
| 5 | W6-F2 broke 5 mutation rows, and 4 of them name `board_codes.X` in `replace` too (`p429`'s one, `p433`'s three) | refuter, rounds 1 and 2, PR council | acted | both `find` and `replace` rewritten, with the right counts per table |
| 12 | The token check belongs in the temp-folder shim, not in `fake_wokwi_cli.py`, which four places run directly | PR reviewer | acted | W6-F1's guard line and its Files paragraph name the shim and the four places |
| 13 | One word for one thing: golden net, codes, move; shim versus `fake_wokwi_cli.py` | PR reviewer | acted | the PR titles and the batching text use the three words |
| 14 | W6-F2's size differed between its section and Review size | PR reviewer | acted | one pair, 80 and 80 |
| 15 | The `run_scenario.py` split needs its own commit, with the goldens as the gate after each commit | PR refuter | acted | W6-F3's Moves paragraph |
| 16 | `check_commit.py:94` is in `scripts_size()`, the size line's code count (P99), not the lint | PR refuter | acted | W6-F3's fix list |
| 17 | The round-1 `effects` bullet read as if it still held | PR reviewer | acted | it says round 2 dropped it |
| 6 | W6-F2 overlaps files of #906 and #915 | refuter, round 1 | acted | W6-F2 branches after both |
| 7 | `needs_person` means hands, not consent, and W6-F2's step fields had nowhere to show | refuter, rounds 1 and 2 | acted | W6-F2 is the codes only. The step fields go with a later `--json` card |
| 8 | `--json` for run_scenario and flash_image does not serve spark's bar | architecture lens | acted | dropped from W6-F2, a later card |
| 9 | The batching default was too serial | architecture lens | acted | a later area's net PR may open beside a move PR, one move PR at a time |
| 10 | Three numbers were wrong (emit_board lines, DeployError codes, imports among the six) | refuter, round 1 | acted | corrected |
| 11 | One open question for the PO: batching (decision 4) | Fable | raised | the plan's default holds until he answers |
