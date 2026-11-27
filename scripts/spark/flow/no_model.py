"""The one rule that counts a build with no simulation as done (P977, P1008, P1207): Wokwi has no model of the board.
The guide, the build phase and the page's answer read a build record, or a run's own stages, through it. Beside it, the
flow's rule that says why a simulation was skipped (P999): the skipped code's own meaning."""

from spark.build import build_codes
from spark.build.stages import SIMULATION
from spark.core.outcomes import OK, SKIPPED
from spark.flow import flow_codes

#: The codes of a simulation stage whose build counts as done (the PO, 2026-11-21): Wokwi has no model of the board.
NO_MODEL_CODES = (build_codes.BOARD_NOT_IN_WOKWI,)


def stops_only_for_no_model(record):
    """True when the build `record`'s one stopped stage is the simulation, with a code of NO_MODEL_CODES. A stage is
    stopped when it ended neither ok nor skipped (an old record, could-not-run), or when its code is in NO_MODEL_CODES (a
    new record, skipped since P1207). An old record with no code is never counted as done."""
    stopped = [stage for stage in (record or {}).get("stages") or []
               if stage.get("status") not in (OK, SKIPPED) or stage.get("code") in NO_MODEL_CODES]
    return [stage.get("name") for stage in stopped] == [SIMULATION.name] and stopped[0].get("code") in NO_MODEL_CODES


def skipped_simulation_line(record):
    """What the build phase says of the build `record` whose simulation stage alone was skipped (P999): its code's meaning
    (`build_codes.CODES`), or SIMULATION_SKIPPED_MESSAGE for every_part_skipped and for a code CODES lacks (an old record)."""
    code = next((stage.get("code") for stage in (record or {}).get("stages") or [] if stage.get("name") == SIMULATION.name), None)
    if not isinstance(code, str) or code == build_codes.EVERY_PART_SKIPPED or code not in build_codes.CODES:
        return flow_codes.SIMULATION_SKIPPED_MESSAGE
    return build_codes.CODES[code]
