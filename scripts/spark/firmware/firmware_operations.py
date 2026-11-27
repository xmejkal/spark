"""
The firmware area's Operations on the core by the `op` each prints, for the frontends (P1208, P1078): `check-firmware`
(`check_firmware.py`) and `run-scenario` (`run_scenario.py`). The table is a module, because the area's `__init__` imports nothing.
"""

from spark.firmware.firmware_check import CheckFirmware
from spark.firmware.firmware_scenario import RunScenario

# --- MVP ---
OPERATIONS = {CheckFirmware.name: CheckFirmware, RunScenario.name: RunScenario}
# --- end MVP ---
