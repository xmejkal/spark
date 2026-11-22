# P975: no gh on PATH is header_not_fetched, not a traceback: rows

Card: [P975 #1403](https://github.com/xmejkal/spark/issues/1403). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | With no gh on PATH `fetch_variant_header` raised FileNotFoundError, which the handler (RuntimeError only) did not catch | this build | acted | reproduced by a test (FileNotFoundError traceback); now `GH_MISSING_MESSAGE` under `header_not_fetched` |
| 2 | The code's fix text "fix what gh says in the sentence" reads oddly when gh is missing | this build | raised | dropped because the sentence itself says to install gh or use --offline; the PO-read text is unchanged |
| 3 | a gh on PATH that cannot run (mode 644) still ended in a PermissionError traceback | PR refuter | acted | the catch is OSError, the sentence says "or cannot run", a test with a gh that is not executable |
| 4 | scripts.md did not tell Claude to relay the sentence rather than install gh | PR refuter | acted | one line in scripts.md |
