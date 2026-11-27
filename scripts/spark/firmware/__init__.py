"""
The firmware area (W6-F3, P685): the flash image, the import check and the simulation's run of a scenario. The three CLIs
`flash_image.py`, `check_firmware.py` and `run_scenario.py` stay in `scripts/`; the last two hand their Operation to the core
(`firmware_operations`, P1208, P1078). This file imports
nothing, because an `__init__` that imports its modules made the cycles of wave 5.
"""
