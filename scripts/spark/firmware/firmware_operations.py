"""
The firmware area's Operations on the core by the `op` each prints, for the frontends (P1208): `check-firmware`
(`check_firmware.py`). The table is a module, because the area's `__init__` imports nothing.
"""

from spark.firmware.firmware_check import CheckFirmware

# --- MVP ---
OPERATIONS = {CheckFirmware.name: CheckFirmware}
# --- end MVP ---
