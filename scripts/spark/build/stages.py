"""
The outcome of one stage of the build (P705): `Stage`, which `board_engine` and `build_service` both make, so neither
imports the other for it, and the hint a build stopped at the footprint still gives. Every importer imports the two
names, never the module: `stages` is a list of them in `run`, `main` and the tests.
"""

from spark.core.outcomes import SKIPPED

# --- MVP ---
#: What a build stopped at the footprint stage still gives, after the gaps `footprint_emitter.why_no_footprint` lists (P407).
NO_FOOTPRINT_HINT = ("The schematic was not tried. The pin map needs no footprint: with --keep, the kept lines say "
                     "whether firmware/pins.py was written. The breadboard sheet and the simulation read the built "
                     "board, so they wait for the footprint.")


def skipped_the_build(stages):
    """Whether `stages` are a board-only build's (`build_service.board_alone`): its build stage is SKIPPED, so no board was built.
    A full build whose simulation stage is SKIPPED (every part skipped, P778) built its board, so it is not."""
    return any(stage.name == "build" and stage.status == SKIPPED for stage in stages)


class Stage:
    """Value: one link, what became of it, and the `code` (build_codes, or the design's own) of one that did not end ok."""

    def __init__(self, name, status, detail="", code=None):
        self.name, self.status, self.detail, self.code = name, status, detail, code

    def __repr__(self):
        return "Stage(%r, %r)" % (self.name, self.status)
