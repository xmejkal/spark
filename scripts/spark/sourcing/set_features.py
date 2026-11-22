"""
`parts.py --features-set`: a board's main features, measured on the maker's top view, written into its record as facts
in mm (P956 #1362), all or nothing. The features file holds what a person or the conversation read off the picture, in
its pixels; `feature_measure.FileFeatureMeasurer` scales and turns it into the board's frame, `feature_check.FeatureCheck`
checks it against the record's pads and mounting holes, and the record's `physical.features` and `physical.colour` are
replaced whole in one write. Every feature is written verified false, with its source. Boards only in this version: a
module's record holds no features yet.
"""

from spark.breadboard import breadboard_codes, drawing
from spark.breadboard.feature_check import FeatureCheck
from spark.breadboard.feature_measure import FileFeatureMeasurer, MeasuredFeatures
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _parse, _problem, feature_problems
from spark.sourcing import record_home, sourcing_codes
from spark.sourcing.keep_picture import _frame
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class SetFeatures(PartOperation):
    """Operation: `features-set` as parts.py answers it: each feature in mm, each anchor's offset from its pad, the board's
    colour and whether it was written; a features file that cannot be read, a board with no frame, a part's record, and
    each rule a feature breaks are problems, and nothing is written."""

    name = "features-set"
    data_keys = ("record", "features", "anchors", "colour", "written")
    arguments = (Argument(("--features-set",), "file", str, "write a board's main features (chips, sockets, buttons, LEDs, "
                          "holes, labels), measured in the pixels of the maker's top view that the record keeps, into its "
                          "record in mm: scaled by the outline, turned so the USB end is at the bottom (never mirrored), "
                          "checked against the record's pads and mounting holes; verified false, each with its source",
                          metavar="FILE"),
                 Argument(("--part",), "part_id", str, "with --features-set: the board record the features are of (--project "
                          "picks the project's record; never spark's library)", required=True, metavar="BOARD"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, file, part_id, project, dry_run):
        home, source = record_home.record_path(part_id, project, "board")
        record = _parse(home) if home is not None else None
        if not isinstance(record, dict):
            part, _ = record_home.record_path(part_id, project, "part")
            why = ("%s is a part's record: measured features are a board's in this version" % part_id if part is not None
                   else "no record of a board called %r — `boards.py --list` finds what exists" % part_id)
            return Answer(problems=[_problem(part_id, why, code=sourcing_codes.NO_SUCH_PART)])
        if record_home.in_library(home):
            return Answer(problems=[record_home.library_problem(part_id)])
        shape, why = _frame(record)
        if shape is None:
            return Answer(problems=[_problem(part_id, "%s has no frame to measure in: %s" % (part_id, why), code=drawing.NO_HEADER_FACT)])
        measured = FileFeatureMeasurer(file).measure(record, shape)
        if not isinstance(measured, MeasuredFeatures):
            return Answer(problems=[_problem(file, measured.reason, code=breadboard_codes.FEATURE_UNREADABLE)])
        check = FeatureCheck(shape, record)
        refused = check.problems(measured)
        if refused:
            return Answer(problems=[_problem(problem.feature or part_id, problem.sentence, code=problem.code) for problem in refused])
        features = [check.fitted(feature) for feature in measured.features]
        physical = dict(record["physical"], features=features, **({"colour": measured.colour} if measured.colour else {}))
        answer = record_home.write_fields(part_id, (home, source), {"physical": physical}, dry_run,
                                          lambda held, after, path: feature_problems(after))
        if answer.problems:
            return Answer(problems=answer.problems)
        anchors = [{"pad": pad, "x": x, "y": y, "off_mm": round(((x - shape.pins[pad][0]) ** 2 + (y - shape.pins[pad][1]) ** 2) ** 0.5, 2)}
                   for pad, x, y in measured.anchors]
        lines = ["  %s %d features of %s (%s), in mm in its frame:" % ("would write" if dry_run else "wrote", len(features), part_id,
                                                                     answer.data["path"])]
        lines += ["    %s (%s) at %g, %g, %g x %g, %s" % (feature["name"], feature["kind"], feature["x"], feature["y"], feature["w"],
                                                        feature["h"], feature["colour"]) for feature in features]
        lines += ["    anchor %s at %g, %g: %.2f mm from its pad" % (anchor["pad"], anchor["x"], anchor["y"], anchor["off_mm"])
                  for anchor in anchors]
        return Answer({"record": part_id, "features": features, "anchors": anchors, "colour": measured.colour,
                       "written": not dry_run}, lines + answer.lines[1:])
# --- end MVP ---
