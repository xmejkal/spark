# P381 the naming and responsibility standard: findings rows

Findings from writing P381 (2026-10-21, Prague). The PO and Claude agreed the rules in chat. One reviewer on Sonnet
read the PR, because it is docs only.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The example `board.py identify` clashes with `tools/board.py`, the Kanban status tool | implementer, reviewer | acted | the example is now `parts.py show` and `ShowPart`; the clash is noted on P382 #489 |
| 2 | The glossary's probe row had a third cell in a two-column table | reviewer | acted | the sentence joined the meaning cell |
| 3 | "helper" meant a class and also the function `run_cli` | reviewer | acted | the clash row now calls `run_cli` a function |
| 4 | The level table said "Script" where the glossary says "CLI" | reviewer | acted | the table says CLI |
| 5 | "the same words" did not fit a subcommand that drops the object, and "op name" was not defined | reviewer | acted | rule 4 says the subcommand is the verb alone and defines the op |
| 6 | The examples drifted from the role table (`ChipReader`, `GrantStore` as a helper), and Service had no place | reviewer | acted | rule 2 uses `BoardReader` and `EsptoolBoardReader`; one sentence says a Service, Store or Adapter is a helper with its role word |
| 7 | `tools/check_docs.py` fails on a planned script name such as `identify_board.py`, with no way to mark it proposed | implementer | raised | the docs name the planned module without `.py`; a later card can add a "proposed" marker if more pages need it |
