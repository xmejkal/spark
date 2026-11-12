# P468 the serial warning reads a board fact: rows

What the P468 plan, its two council rounds and the build found. Card: #636. The FireBeetle part is not in this card.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The FireBeetle's `serial_without_wires` (walk 3 matched `ready` with no connections, on 0.27.1) | refuter, lead | raised | waits for a run on wokwi-cli 0.28.0 and the PO's yes (it changes his installed tool) — P776: waits on the PO: needs wokwi-cli 0.28.0 run and PO's yes — P776: waits on the PO: needs wokwi-cli 0.28.0 run and PO's yes |
| 2 | `run_scenario.py:432-433` still asks about `$serialMonitor` wires when a run hears nothing, even for a board whose record says it needs none | lead | raised | wording to reconsider with the 0.28.0 run — P776: waits on the PO: wording waits for the 0.28.0 run — P776: waits on the PO: wording waits for the 0.28.0 run |
