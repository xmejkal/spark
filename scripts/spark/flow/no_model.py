"""The one rule that counts a build with no simulation as done (P977, P1008, P1207): Wokwi has no model of the board.
The guide, the build phase and the page's answer read a build record, or a run's own stages, through it."""

from spark.build import build_codes
from spark.build.stages import SIMULATION
from spark.core.outcomes import OK, SKIPPED

#: The codes of a simulation stage whose build counts as done (the PO, 2026-11-21): Wokwi has no model of the board.
NO_MODEL_CODES = (build_codes.BOARD_NOT_IN_WOKWI,)


def stops_only_for_no_model(record):
    """True when the build `record`'s one stopped stage is the simulation, with a code of NO_MODEL_CODES. A stage is
    stopped when it ended neither ok nor skipped (an old record, could-not-run), or when its code is in NO_MODEL_CODES (a
    new record, skipped since P1207). An old record with no code is never counted as done."""
    stopped = [stage for stage in (record or {}).get("stages") or []
               if stage.get("status") not in (OK, SKIPPED) or stage.get("code") in NO_MODEL_CODES]
    return [stage.get("name") for stage in stopped] == [SIMULATION.name] and stopped[0].get("code") in NO_MODEL_CODES
