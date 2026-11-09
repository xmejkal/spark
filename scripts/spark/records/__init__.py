"""
The records area (W6-R3a, P718): the JSON records spark reads and the person's store. The store's folder, its writes,
its events and `fetch` (`store`), the board records (`board_records`), the project's brief (`brief`), what the store
says of the board on USB (`deploy_record_store`), what a fact must carry (`provenance`), the pad aliases (`board_pads`),
the onboard parts a scenario wires (`onboard_parts`), the facts a board record owes (`missing_facts`) and the records'
codes (`records_codes`). The CLI `boards.py` stays in `scripts/` and calls these modules. This file imports nothing,
because an `__init__` that imports its modules made the cycles of wave 5.
"""
