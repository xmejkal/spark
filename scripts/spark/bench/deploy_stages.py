"""
The stages of a deploy (P655): the last one reached is the envelope's `data.stage` and each Event's code.

A leaf: it imports nothing of spark, so a Service and the envelope both read the names from here.
"""

from collections import namedtuple

# --- MVP ---
class DeployPhase:
    """Value: the five stages of a deploy, in their order. Each is a JSON `stage` word: "phase" is the code's name for
    it, because "stage" means a build stage. A holder of constants by design, never instantiated."""

    PLAN, LOOK, GATE, FLASH, VERIFY = "plan", "look", "gate", "flash", "verify"


# --- MVP ---
#: Value: one stage of a deploy as data (P478): its `name`, a DeployPhase word, its `summary`, the sentence that says
#: why the stage happens, and its `endings`, none yet, so a page's stages block reads the rows as it reads build's
#: StageDefinitions. `DeployImage.stages` holds the rows, so the text view numbers its headings from them.
DeployStage = namedtuple("DeployStage", "name summary endings", defaults=((),))
#: The five stages, in their order, each with its why (P476). One table, so no stage says it twice.
DEPLOY_STAGES = (
    DeployStage(DeployPhase.PLAN, "spark checks the image and finds its tools first, so a wrong image stops before the board is touched"),
    DeployStage(DeployPhase.LOOK, "spark reads the chip and flash size, so another chip or too little flash for the image is stopped"),
    DeployStage(DeployPhase.GATE, "the erase cannot be undone, so the write needs a yes for this board"),
    DeployStage(DeployPhase.FLASH, "the erase and the write replace what the board runs, and esptool then restarts the chip with its watchdog where it has one, because a plain reset can leave an ESP32-S3 in download mode"),
    DeployStage(DeployPhase.VERIFY, "a written image is not yet a running one, so spark checks its files on the board and waits for ready"),
)
#: The sentence a person reads when a stage starts: why spark does it (P476), made from the rows.
PHASE_WHY = {stage.name: "why: " + stage.summary for stage in DEPLOY_STAGES}
#: The lines of deploy's silent waits (P478 slice 2), each an Event of kind WAIT: the look's read and the verify stage's
#: read, and the wait for the board to restart after the person pressed RESET. Only reported, never compared.
READ_WAIT_MESSAGE = "reading the board"
RESET_WAIT_MESSAGE = "waiting for the board to restart"
