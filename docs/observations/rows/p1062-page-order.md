# P1062: the page's order (story 1a-ii): rows

Card: [P1062 #1560](https://github.com/xmejkal/spark/issues/1560), PR [#1619](https://github.com/xmejkal/spark/pull/1619).
The plan passed two rounds (round 1: one lens on Sonnet with UX and AI-UX questions and the refuter on Opus, E1 to E12;
round 2: the refuter on Opus, E13 to E17). Rows 1 to 4 are the build's. Rows 5 to 14 are the PR review's: the lens on
Sonnet and the refuter on Opus, each item decided by spark-main (delegated, the PO's to change).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The page's words for NEXT can be named `NEXT_LABEL` | the plan, pieces table | acted | `flow_codes.NEXT_LABEL` is the step nav's "Next: step %d", so the box's label is `NEXT_ACT_LABEL`; `GUIDE_NOW` stays for the CLI's text |
| 2 | `map.md` does not move | the plan, docs | acted | `tools/map.py --write` adds `tests/test_flow.py` as `deploy_reading.py`'s test, one line, which `test_map` needs |
| 3 | The golden page changes only in its order and words | the plan, fixtures | acted | its freshness line holds the copied fixture's time, so `tests/golden_bench.py` masks it (`FRESH_TIME`) |
| 4 | The new tests may read `zone_time.MONTHS` | the build | acted | the hook of 72877e43 failed on `test_self_confirmation`; 14ca5d49 reads a January time |
| 5 | The retired p828-step2 row on `<div id="phase-%s">` still anchors and is caught | the refuter | acted | restored as "the developer fold's phase text loses its id"; 8 rows retired, not 9 |
| 6 | `lastRequest` falls back to a fragment of the key ("... 11:36: pick.") | the refuter | acted | Python writes `request_kinds` and `request_other`; a node test for a request whose offer left the page; a row |
| 7 | `_wiring_open` decides in the page that a breadboard phase with no status is a current sheet | the refuter | acted | `guide.with_wiring` gives `now.with_wiring` in `show --json`; the page reads it; E16's test moves to `TheWiringWithNowTest`, its rows to `guide.py` |
| 8 | The parts fold repeats one refusal sentence per need | the lens (UX) | acted | a line the parts phase says twice stands once, above the need rows, with a test and a row. On p934-display2 the four lines differ (each names its need and the others), so they stay four: one sentence for them all needs the reading's words, the next row's destination |
| 9 | One sentence for a pick plan that refuses every new pick | from row 8 | raised | destination: a line on P1070 [#1568](https://github.com/xmejkal/spark/issues/1568), which changes the parts reader: it says the shared refusal once |
| 10 | The freshness line's "as of <time>, its newest change" reads older than ON THE BOARD's deploy | the lens (UX) | acted | `FRESH_LINE` says "as its files last changed, <time>" |
| 11 | Two blank lines before `def counted` (phase_readers.py) | the refuter | acted | one was missing; fixed |
| 12 | The TZ `mock.patch.dict(os.environ, ...)` in test_flow_page.py | the lens | rejected | `in_prague` is test_wired_board's pattern (P1044), restoring with `time.tzset` at cleanup; the hook's architecture test accepts it, and no new `mock.patch` was added in the review |
| 13 | DONE lists "firmware" while the deploy is not confirmed | the lens | raised | destination: P1106 [#1626](https://github.com/xmejkal/spark/issues/1626): the PO chose that DONE says "firmware (written)" in that case. Beyond this card |
| 14 | "✓ Parts ok" should say "4 of 4 picked" | the lens | rejected | the reading has no count field yet (D3 of the plan) |
| 15 | The freshness line covers only the fingerprint's three files | the build, the lens | acted | destination: P1064 [#1562](https://github.com/xmejkal/spark/issues/1562) (story 1c, FlowStamp) |
