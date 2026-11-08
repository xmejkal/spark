"""
The checks area (W6-C3, P695): the checks that grade a built design against facts in records (the rules, the physics,
the footprints, the vendor's pin header and the order list) and the runner of them all. The six CLIs `check_all.py`,
`compare_design.py`, `check_physics.py`, `check_footprints.py`, `check_vendor_pins.py` and `check_bom.py` stay in
`scripts/` and call these modules. This file imports nothing, because an `__init__` that imports its modules made the
cycles of wave 5.
"""
