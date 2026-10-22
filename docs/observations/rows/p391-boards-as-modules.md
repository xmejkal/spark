# P391 boards as modules: findings rows

Findings from spike P391 (2026-10-22, Prague). Three Sonnet 5.5 mappers, one Fable 5.1 architect, one Opus 5.5 refuter.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Boards get no shelf and no catalog layer, only because `store.layers` adds them for `kind == "parts"` | map 1, map 2 | verified | `store.py:80,82`, pinned by `tests/test_store.py:108-109`. Stage 1 |
| 2 | Two files name the project's board: `boards/active.json` and `requirements.json` | map 1 | verified | `boards.py:203`, `needs.py:643`. Stage 3 |
| 3 | The store's `boards/` place holds deployed units by MAC, a second meaning of "boards" | map 1 | verified | `store.py:61`, `board_facts.py:65-74`. Question 2 |
| 4 | The part-then-board walk exists three times, the footprint-stop test three times, the validator switch twice | map 1 | verified by the architect | design section 1. Stage 2 |
| 5 | The one board is assumed in about 20 places; `emit_board`'s single `Mcu`, `Design.board` and `assign_pins`'s one namespace are deep | map 3 | raised | design section 4. Stage 6 |
| 6 | The design shipped its refactor before P390 | refuter | acted | stage 1 is now P390 alone |
| 7 | Stage 1b missed the path compares in `parts.py`, the "/" refusal in `store._target`, the research prompts, the `active_id` and `project_root` callers | refuter | acted | each named in its stage |
| 8 | The per-kind move skipped the sim-chip folder and `photos/`, and about 124 test lines spell the flat folders | refuter | acted | the move went to stage 5, out of MVP |
| 9 | Names: subclasses end in their base's name, the Operation's module matches it, `DeployedBoardStore` reused "board"; `owes` and `function_of` were speculative | refuter | acted | `PartRecordKind`, `BoardRecordKind`, `shelve_record.py`, `DeployedStore`; both methods dropped |
| 10 | Wokwi's support for two MCUs in one diagram | architect | raised | not checked. Needed before stage 6 |
