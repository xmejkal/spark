"""
The stages of a deploy (P655): the last one reached is the envelope's `data.stage` and each Event's code.

A leaf: it imports nothing of spark, so a Service and the envelope both read the names from here.
"""

# --- MVP ---
STAGE_PLAN, STAGE_LOOK, STAGE_GATE, STAGE_FLASH, STAGE_VERIFY = "plan", "look", "gate", "flash", "verify"
