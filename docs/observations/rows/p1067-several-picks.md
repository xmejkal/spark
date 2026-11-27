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
| 19 | the three new rows of the run's rule are not marked critical | the builder | dropped | dropped because the critical cap is full at 50 of 50: the rows run as new rows in every sweep, and a critical place for them needs the PO to free one, which is on his morning list |
| 20 | each radio came after its offer's long words, while the design draws the choice first | the Chrome check | acted | the radio's label leads its row; a node test pins it |
| 21 | the Send box ran a pick's label into its words ("for board If you wired") | the Chrome check | acted | a colon joins them |
| 22 | the canvas draws a small picture of each part in the pick rows; the page shows none | the Chrome check | raised | [P1275 #1835](https://github.com/xmejkal/spark/issues/1835): each pick row shows the part's picture from its record |
| 23 | the review ran on the five commits, 2026-11-27, about 03:04 to 03:31 CET: one lens and the refuter, both on Opus | the review | acted | rows 24 to 34; the refuter reproduced four picks in one request, the all-or-nothing failure, every refusal, a page published before the change, and the CLI path |
| 24 | `joined_picks` breaks the family of `*_step` names in offer_steps.py | the lens | rejected | the test `test_every_op_a_flow_step_names_has_its_script` calls every `*_step` function with a fixed set of arguments, and `steps` is not one of them; this function joins steps and is not one, so its name stays out of that family |
| 25 | flow.md lost the sentence that a deploy, a simulation, a look or a grant is never an offer here | the lens | acted | the sentence is back |
| 26 | json.md says "`keys` what ran", but a refused row that names an offered key also answers `keys` | the lens | acted | "`keys` the keys it names" |
| 27 | the script makes two separators of its own | the lens | acted | `flow_codes.NEEDS_JOIN` and `LABEL_JOIN`, as the page words `needs_join` and `label_join` |
| 28 | commands/idea.md says "in one click", but sending takes Send and the box's Send | the lens | acted | "in one Send" |
| 29 | a double full stop in flow.md | the lens | acted | removed |
| 30 | a row of picks that ran with problems never says that no pick was saved | the refuter | acted | "No pick was saved." leads the line, from `flow_codes.NO_PICK_SAVED_SAYS`; a node test and mutation row 16 |
| 31 | a row with both `key` and `keys` is refused, yet its answer names the key | the refuter | acted | its answer names no key; a test and mutation row 17 |
| 32 | `request_malformed` has two texts | the refuter | acted | flow.md says the code's meaning word for word; the detail of `key` and `keys` stays in `RunRequest.details` |
| 33 | old tests beyond the Done when's words change: the `without_script` helper, the offers test, the node count | the refuter | acted | each follows a decision in the council's record (`data-need` on `li.need`, the `part` field for the radio's label, the new node tests); the PR body names each with its old and new text |
| 34 | the page's golden, tests/golden-design/flow-ok-page.txt, differs from today's output, and the hook refused the push | the hook, 2026-11-27 | acted | rewritten with `SPARK_ACCEPT=flow`; read hunk by hunk: only new page words and the new embedded script changed, and no HTML line outside the script |
