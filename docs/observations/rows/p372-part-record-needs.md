# P372 what a part record needs: findings rows

Findings from the Opus refuter on the synthesis `finding.md` at 15a0560 (2026-10-20, Prague), after five Sonnet
council lenses. R10.2 (`scrum/RETROSPECTIVES.md`) applies: a row becomes a card only if it is a real bug or blocks the next walk.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `--fact-set` cannot write a `facts.*` entry, so the process steps 3 and 4 claimed a tool that does not exist, and the walk row 15 bench results have no way back into the record | refuter | acted | `parts.py:2040` accepts only `CHAIN_FACTS` and `about`, `description`, `tags`. A dry run with `{"facts": {"pot_resistance_ohms": ...}}` exits 1. Now card 2, it blocks P364 #466 |
| 2 | The bench citation form (old card 4) blocks P364 | refuter | rejected | a fact with `verified: true` and a prose source "bench 2026-10-21, meter, PO", without `cites`, validates today. The card is dropped and its note goes into card 2 |
| 3 | `--match` dropping a store record with no `function` (old cards 2 and 3) is a real bug that blocks the next walk | refuter | rejected | the drawer is one per store (`drawer.entries()` reads `store.place("drawer")`), and the PO's drawer entry gives the joystick its function in every project. A raised gap, not a card |
| 4 | The levels contradicted each other: `findable` needed `function`, the joystick has none, yet the finding called it `buildable` | refuter | acted | `findable` takes a function from the record, `KIND_FUNCTION` or a drawer entry. The joystick is `findable` only through its drawer entry |
| 5 | `proven` needed stored state spark does not hold (a picture, a bench result, an acceptance), and "every fact a stage reads" conflicted with bench checks of facts no stage reads | refuter | acted | `proven` is now `buildable` plus an empty `unverified` list over every fact. A picture, a symbol and a bench trial join it with the card that gives them a field (P370, P371) |
| 6 | The `buildable` column listed `power` among what `owes()` checks | refuter | acted | `owes()` checks the five required keys and the five chain facts. `power` is gone from the column |
| 7 | "The only fact of the 8 that a stage reads" was wrong | refuter | acted | `conflicts_of` reads `supply_range_v` (`parts.py:1500`), so two facts are read |
| 8 | Three names for one thing: "open", `--unverified` and `open_questions`, plus `usable` in card 5 | refuter | acted | the finding uses `unverified` and `level` throughout. `--level` returns `level`, `owes`, `unverified` |
| 9 | `--unverified` misses a guessed `body_mm`, and the pin map's unverified output reads the same list | refuter | verified | `open_questions_of` (`parts.py:889`) reads only `facts` and `pin_order_proof`. `assign_pins.py:489` calls it. Card 1, it blocks P364 |
| 10 | Docs review: a long table cell, `owes` and unverified not defined at first use, "the one above it" backwards, P331 and R10.2 without a pointer | Sonnet docs reviewer | acted | the note below the stage table, two definitions in the summary, PR #435 and `scrum/RETROSPECTIVES.md` named |
| 11 | The PO wants a trust rank per source: the exact part's photo or datasheet first, then a look-alike's datasheet, then a web search, and the better source wins | the PO, decision 1 | raised | his words in `finding.md` section 6 and on #477, a proposed card |
