"""
The design area (W6-D3a, P702): what a design is and the values it is made of, the requirements file loaded once
(`loader`), the pin each signal goes on (`pin_assigner`), the pins a live try may not write (`restricted_pins`), the
built design as connectivity (`netlist`), what a board house can make (`fab`) and the copper rules (`copper`). The CLI
`assign_pins.py` stays in `scripts/` and calls these modules. This file imports nothing, because an `__init__` that
imports its modules made the cycles of wave 5.
"""
