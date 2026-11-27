# P1067: several picks in one page click: rows

Card: [P1067 #1565](https://github.com/xmejkal/spark/issues/1565). The plan council ran on 2026-11-26 and 2026-11-27, from about
23:30 to 01:00 CET: the architecture lens, the UX lens and the refuter, all on Opus. The delegated council of three on Opus (the
PO assistant, the tech lead and the architect) answered the open choices at 00:15 CET, delegated and the PO's to change. A second
refuter round ran at 00:58 CET. The page was checked in Chrome against the canvas at about 02:40 CET. This file holds the acted,
raised and rejected findings only. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a public `run_page_request(project, request, outside)` lets another interface skip the masking, because only `run_cli` picks the privacy (cli.py:267, :318) | the architecture lens, confirmed by the refuter | acted | no such function; the tests write the request file; the core gap is P1263 #1822 |
| 2 | `--describe` shows the shape of the row | the plan | rejected | `flow.py --describe` fails, and `DescribeOperations` prints no `details` (describe_operations.py:71-77); `--help` prints `details` |
| 3 | the shape of the row is written in seven places | the architecture lens and the refuter | acted | `RunRequest.details` is the one text; the other pages link to `flow.py run-request --help` |
| 4 | only two old tests change | the plan | rejected | test_run_request.py:150, :386 and :349, the `without_script` helper, the offers test in test_flow.py and the node count in test_flow_script.py change, each named with its old and new text |
| 5 | the answer of a several-picks run carries `keys` | the delegated council, 2 of 3 | acted | the card's Done when gets it as a delegated edit (#1565, comment of 27 Nov) |
| 6 | the new page always writes `keys` | the architecture lens | rejected | the council chose `key` or `keys`, 3 of 3: published pages send `key` for as long as they live |
| 7 | Send reads "Send %d picks (%s)" with the needs named, any subset of needs | the UX lens, from the design | acted | `flow_codes`; "Choose a part first." shows as visible text while nothing is chosen |
| 8 | one native radio per need, with "not now" checked first, as the design draws it | the architect, from design.md:323-326 | acted | the browser keeps one choice per need |
| 9 | the choices vanish while the request waits | the UX lens | acted | the radios stay chosen and disabled while it waits, and come back after a refused send and after Withdraw |
| 10 | the Send box repeats each shared sentence once per pick | the UX lens, confirmed by the refuter | raised | P1135 #1670: a pick's effect is one joined string (phase_readers.py:315-317) |
| 11 | a refusal of a `keys` row lists the keys spark still offers, and the other problems go in `note` | the UX lens | raised | P1137 #1672 |
| 12 | Claude does not learn that no pick was saved when one fails | the UX lens | acted | commands/page.md: "not ok: no pick was saved"; the Send box: "Spark checks the picks together. If one fails, spark saves none." |
| 13 | `data-need` on each offer's `<li>` breaks test_flow_page.py:2156 | the refuter | acted | `data-need` is on `<li class="need">`, read through `closest()` |
| 14 | GLOSSARY.md and commands/build.md:186 become untrue | the refuter | acted | both say several picks in one Send |
| 15 | eight mutation anchors move, not six | the refuter, round 2 | acted | p829 (5), p1008 (1), p1030 (1) and p1062 (1) moved; `tools/mutate.py --anchors` passes |
| 16 | the radios miss the 44 px target | the refuter, round 2 | acted | each radio's label gets the button height through `style`; Chrome measured 44 px |
| 17 | `RunRequest.data_keys` lacks "keys", and the ran line reads `offer.label` when `offer` is None | the refuter, round 2 | acted | both fixed, with a test |
| 18 | a committed copy of today's page script, so a test can load an old page | the plan | rejected | today's script was run on a `keys` row in node: it showed "a step this page no longer offers" and did not crash; a node test pins that a row of an unknown shape reads as `request_other` |
| 19 | the three new rows of the run's rule are not marked critical | the builder | raised | the critical cap is full at 50 of 50; which row leaves is the PO's call |
| 20 | each radio came after its offer's long words, while the design draws the choice first | the Chrome check | acted | the radio's label leads its row; a node test pins it |
| 21 | the Send box ran a pick's label into its words ("for board If you wired") | the Chrome check | acted | a colon joins them |
| 22 | the canvas draws a small picture of each part in the pick rows; the page shows none | the Chrome check | raised | no card yet: spark-main files it with the next batch |
