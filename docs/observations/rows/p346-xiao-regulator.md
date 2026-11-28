# P346: the XIAO ESP32-C6's 3.3 V regulator rating: rows

Card: [P346 #441](https://github.com/xmejkal/spark/issues/441). Data only: no new mutation rows, because the change
adds no logic and the rule's rows are in `tests/mutations/sprint-8-p52.json`. This file holds the acted, raised and
rejected findings only. 2026-11-28.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan's rating needs `verified` true by the library's rule, from SGMICRO's page 3 | plan check, council | acted | `power.regulator_3v3_a` is 1.0, verified, cited to `sgm6029-datasheet-rev-a-1` |
| 2 | the C6's column in Seeed's Power Consumption row settles the doubt on `deep_sleep_ua` | plan | raised | P1345 [#1929](https://github.com/xmejkal/spark/issues/1929) |
| 3 | the new test leaves the SGM entry's `file` unguarded, the name the kept file sits under | PR refuter, finding 7 | acted | `assertEqual(document["file"], "SGM6029.pdf")` in the rating test |
| 4 | the PR body cites GLOSSARY.md:371, whose next sentence makes an inferred fact false, and calls the row choice an inference | PR refuter, finding 8 | acted | the PR body says why the 1 A row is the vendors' printed words, not an inference |
| 5 | `parts.py --keep` prints "kept, but listed in no record" for a file that the library record cites | PR refuter, finding 9 | raised | P1346 [#1930](https://github.com/xmejkal/spark/issues/1930) |
