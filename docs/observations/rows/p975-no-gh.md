# P975: no gh on PATH is header_not_fetched, not a traceback: rows

Card: [P975 #1403](https://github.com/xmejkal/spark/issues/1403). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | With no gh on PATH `fetch_variant_header` raised FileNotFoundError, which the handler (RuntimeError only) did not catch | this build | acted | reproduced by a test (FileNotFoundError traceback); now `GH_MISSING_MESSAGE` under `header_not_fetched` |
| 2 | The code's fix text "fix what gh says in the sentence" reads oddly when gh is missing | this build | raised | dropped because the sentence itself says to install gh or use --offline; the PO-read text is unchanged |
