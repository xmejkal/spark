"""
The stages of a deploy (P655): the last one reached is the envelope's `data.stage` and each Event's code.

A leaf: it imports nothing of spark, so a Service and the envelope both read the names from here.
"""

# --- MVP ---
class DeployPhase:
    """Value: the five stages of a deploy, in their order. Each is a JSON `stage` word."""

    PLAN, LOOK, GATE, FLASH, VERIFY = "plan", "look", "gate", "flash", "verify"
