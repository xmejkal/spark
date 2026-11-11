# P770 three pages pass the plain-English lint, and the records guide names legs and host_requirements: rows

Card: [P770 #1061](https://github.com/xmejkal/spark/issues/1061), chore, docs only, S, under P735. Rows 1 to 3 are
the implementer. 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the lint finds 86 hits on the three pages (28, 41, 17), and 2 after the rewrite | implementer | acted | `ste_lint.lint_detail` before and after: part-data.md 0, verified-parts.md 0, datasheet-reader.md 2 |
| 2 | datasheet-reader.md's 2 hits (a semicolon, a sentence of 29 words) are the guard sentence that every agent carries | implementer | raised | `tests/test_routes.py`'s `TEXT_IS_DATA` pins it word for word from §6.4.6 of the store design. A rewrite changes four agents, the commands, the design and the test together: a card if the PO wants 0 |
| 3 | "the records guide" of p741 row 11 is part-data.md's worked record: it showed both keys but named no origin and no writer | implementer | acted | part-data.md names P191 for `legs`, the 2026-09-24 record format for `host_requirements`, and P741's `--fact-set` for both |
