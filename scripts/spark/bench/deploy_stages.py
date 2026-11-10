"""
The stages of a deploy (P655): the last one reached is the envelope's `data.stage` and each Event's code.

A leaf: it imports nothing of spark, so a Service and the envelope both read the names from here.
"""

# --- MVP ---
class DeployPhase:
    """Value: the five stages of a deploy, in their order. Each is a JSON `stage` word: "phase" is the code's name for
    it, because "stage" means a build stage. A holder of constants by design, never instantiated."""

    PLAN, LOOK, GATE, FLASH, VERIFY = "plan", "look", "gate", "flash", "verify"


# --- MVP ---
#: The sentence a person reads when a stage starts: why spark does it (P476). One table, so no stage says it twice.
PHASE_WHY = {
    DeployPhase.PLAN: "why: spark checks the image and finds its tools first, so a wrong image stops before the board is touched",
    DeployPhase.LOOK: "why: spark reads the chip and flash size, so another chip or too little flash for the image is stopped",
    DeployPhase.GATE: "why: the erase cannot be undone, so the write needs a yes for this board",
    DeployPhase.FLASH: "why: the erase and the write replace what the board runs, and esptool then restarts the chip with its watchdog where it has one, because a plain reset can leave an ESP32-S3 in download mode",
    DeployPhase.VERIFY: "why: a written image is not yet a running one, so spark checks its files on the board and waits for ready",
}
