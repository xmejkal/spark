# P741 `--fact-set` writes `legs` and `host_requirements`: rows

Card: [P741 #1017](https://github.com/xmejkal/spark/issues/1017), XS, under P735. Plan `~/.claude/plans/p741-wiring-keys.md`. Rows 1 to 8 are the plan
refuter (Fable), 9 to 12 the implementer's rulings, 13 to 20 the PR refuter (Fable), 21 the implementer. 2026-11-11.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `legs` is keyed by the record's pin names, but only `pin_order` names ever become ports (board_sections.py:249, netlist.py:96, wiring_steps.py:292), so a leg on a need's or power pin outside `pin_order` would be accepted and never read | plan refuter | acted | a leg's pin is checked against `pin_order` alone |
| 2 | the contract already checks `legs` or `host_requirements`, so the plan checks twice | plan refuter | rejected | no rule in record_kind.py or part_records.py reads them |
| 3 | "add lines, drop none" has no precedent (`tags` is replaced whole) and a wrong line could never be corrected by the command, TL-15's gap again | plan refuter | acted | `host_requirements` is replaced as a whole, like `tags`; `legs` merges leg by leg, like `facts` |
| 4 | an empty `legs` or an empty list is already refused by `_absent` ("a write fills a fact, it never empties one") | plan refuter | acted | the whole-value empty check was dropped; `list_sheet_key_problems` checks each item |
| 5 | `--audit` or `--unverified` would flag a written `legs` with no `verified` | plan refuter | rejected | neither reads `legs`; `--audit` stays clean |
| 6 | the golden tests/golden-records/parts-fact-set-problems-not-a-fact.txt holds the refusal sentence verbatim, so the plan's sentence change fails the golden net | plan refuter | acted | the golden regenerated with `SPARK_ACCEPT=parts` |
| 7 | the anchors of p97-fact-set and p373-p374-facts were stale before this card (`+ ("facts", "pin_roles")` while the code reads `+ drawer.PROVENANCE_KEYS`) | plan refuter | acted | four stale anchors repointed (p97 "any key is a fact", p373 "facts is not a key a write may set" and "a bench result is written unclean", p464 "the text and keys of pin_roles are written raw", stale since step 3 added `physical`) |
| 8 | `WIRING_KEYS` says the wrong reader: `host_requirements` is not wiring; the code's own words are "the sheet" | plan refuter | acted | `SHEET_KEYS`, "the keys the breadboard sheet reads as text" |
| 9 | the leg and line texts are cleaned and cut like a provenance text (1000 characters), because the longest host requirement in the library is 781 characters | implementer | closed | `scrub` treats SHEET_KEYS as PROVENANCE_KEYS; test |
| 10 | a leg key with a control character is refused, never cleaned, through `list_key_problems` | implementer | closed | as for the provenance keys (P374); test |
| 11 | the records guide documents neither `legs` nor `host_requirements` (only archives do) | implementer | raised | a docs card for the records guide; the `--help` text and scripts.md say what `--fact-set` writes |
| 12 | the breadboard sheet printing a written line was not walked, only the readers were read | implementer | closed | the unit tests prove the write; the sheet's reader is unchanged |
| 13 | `legs` reaches the catalog record, a listed project's record and its shelf copy like any fact; the refuse lambda's `record` is the raw file, so `pin_order` is a list in every layer | PR refuter | verified | part_handlers.py:355, :363; a scratch store with three layers |
| 14 | a skeleton with no `pin_order` refuses `legs` with "pin_order (none)", which tells the person to fill it first | PR refuter | verified | reproduced |
| 15 | one sentence for two failures: a leg whose pin is in `pin_order` but whose text is empty or not words read "each pin one of pin_order (A, K); A is not", which contradicts itself | PR refuter | acted | LEGS_SHAPE reads "legs is {pin of pin_order (A, K): words that tell the leg apart}; A is not"; the two test strings follow |
| 16 | `scrub` runs before the key check and never touches dict keys | PR refuter | verified | parts.py scrub then the refuse lambda; drawer.py `_scrubbed` keeps keys |
| 17 | a host requirement that is a number, null, an object, or a non-list is refused | PR refuter | verified | `_words` |
| 18 | the 6 mutants are caught and the 58 anchors of the four tables hold | PR refuter | verified | `mutate.py --copy` 6 of 6, `--anchors` |
| 19 | `--show` prints a written `host_requirements` but has no reader for `legs`, so a person reads a written leg back only in the file | PR refuter | acted | `--show` prints "leg A: …" per leg after the physical lines; test |
| 20 | the help text, the golden and scripts.md claim only what the code does | PR refuter | verified | parts.py:102, scripts.md:288 |
| 21 | an integer entry in `pin_order` would read "pin_order (1, 2); 1 is not" | implementer | closed | the contract takes `pin_order` as strings; a near miss of row 15, not reachable through a valid record |
