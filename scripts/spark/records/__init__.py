"""
The records area (W6-R3a and W6-R3b): the JSON records spark reads and the person's store. The store's
folder, its writes, its events and `fetch` (`store`), the board records (`board_records`), the project's brief
(`brief`), what the store says of the board on USB (`deploy_record_store`), what a fact must carry (`provenance`), the
pad aliases (`board_pads`), the onboard parts a scenario wires (`onboard_parts`), the facts a board record owes
(`missing_facts`), the records' codes (`records_codes`), the tools list and its lookups (`tool_finder`) and version
numbers compared (`versions`). The CLIs `boards.py` and `tools.py` stay in `scripts/` and call these modules. This file
imports nothing, because an `__init__` that imports its modules made the cycles of wave 5.
"""
