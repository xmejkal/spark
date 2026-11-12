"""
`parts.py --requirements`: the picks as the project's requirements.json, as an Operation on the core (P726). It was
`goal_handlers._op_requirements`. The board, and every part pick with a record; a catalog one goes onto the shelf; what
the file already holds stays; `board_only` when the board itself serves every need (P387). The dry run says what it would
write and writes nothing.
"""

import json
from pathlib import Path

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation
from spark.records.record_kind import Answer
from spark.sourcing.part_facts import shelve
from spark.sourcing.part_handlers import _write_lines
from spark.design import board_components, footprint_emitter, need_requirements
from spark.design.goal_handlers import _names_your_entries

# --- MVP ---
def _gap_lines(problems, no_supply, no_receiver, no_driver):
    """What `--requirements` says of a rail with no supply, a net with no receiver or no driver: none on a refusal."""
    said = []
    said += ["  rail %s has no supply — pick a power inlet or a supply (%s draw%s from it)"
             % (gap["rail"], ", ".join(gap["drawn_by"]), "s" if len(gap["drawn_by"]) == 1 else "") for gap in ([] if problems else no_supply)]
    said += ["  net %s is driven by %s and nothing listed receives it — pick what it drives (a speaker terminal, a motor, a connector)"
             % (gap["net"], gap["driven_by"]) for gap in ([] if problems else no_receiver)]
    said += ["  net %s is one side of a driven pair and nothing listed drives it — pick what drives the pair (the amplifier this "
             "terminal hangs off), never a supply (%s %s on it)" % (gap["net"], ", ".join(gap["received_by"]),
                                                                    "is" if len(gap["received_by"]) == 1 else "are")
             for gap in ([] if problems else no_driver)]
    return said


class WriteRequirements(AnswerOperation):
    """Operation: `requirements` as parts.py answers it: the file written, or what a dry run would write, and every line of
    what the picks leave off the board, owe, or shelve; a refusal writes nothing (`needs.match`'s problems)."""

    name = "requirements"
    arguments = (Argument(("--requirements",), "project", str,
                          "the picks as the project's requirements.json: the board, and every part pick with a record — one that owes only its outline "
                          "is written with a warning, one that owes more is refused; a catalog one goes onto the shelf; what the file already holds stays; "
                          "board_only when the board itself serves every need", metavar="PROJECT"),
                 ANSWER_ARGUMENTS["dry_run"],
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, project, dry_run):
        content, shelving, unplaced, kept, board_was, problems, placeholder, unserved, no_supply, no_receiver, no_driver = need_requirements.requirements(
            project)
        path, changed = Path(project) / need_requirements.REQUIREMENTS, False
        # F16: the drawer keys the file names before this write — need_requirements.requirements has read it as JSON already
        held = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        named = need_requirements.unserved_keys(held)
        if not problems and not dry_run:
            for record, source in shelving:
                shelve(record, source)
            changed = store.write_file(path, json.dumps(content, indent=2, ensure_ascii=False) + "\n")
        said = [] if problems else ["  %s %s: board %s; parts %s" % (
            "would write" if dry_run else "wrote" if changed else "unchanged", path, content["board"],
            ", ".join(need_requirements.entry_label(entry) for entry in content["parts"]) or "none")]
        said += ["  board: %s → %s" % (json.dumps(board_was), json.dumps(content["board"]))] if board_was not in (None, content["board"]) and not problems else []
        # P387: board_only is said both ways, never silently written or dropped
        said += ["  board only: nothing to build but the board; the build skips the parts, schematic and footprint"
                 ] if content.get(need_requirements.BOARD_ONLY) is True and not problems else []
        said += ["  board_only removed: the file lists parts"] if isinstance(held, dict) and need_requirements.BOARD_ONLY in held and content["parts"] and not problems else []
        stop = "" if problems else footprint_emitter.footprint_stop(content["board"], Path(project))
        said += ["  board %s: %s" % (content["board"], stop)] if stop else []  # F12 (C-7): said, never refused
        said += ["  onto the shelf, so every project builds with it: %s" % ", ".join(Path(r).stem for r, _ in shelving)] if shelving and not problems else []
        said += ["  placeholder outline — %s owes body_mm, so the PCB step lays it out at a placeholder %g x %g mm: a dimension drawing "
                 "(fetched after the person's yes) or a measurement fills it — %s" % ((part_id,) + board_components.DEFAULT_BODY_MM + (how,))
                 for part_id, how in ([] if problems else placeholder)]
        said += ["  reserved, not placed — no record: %s" % ", ".join(unplaced)] if unplaced and not problems else []
        said += ["  kept, not from a pick: %s" % ", ".join(need_requirements.entry_label(entry) for entry in kept)] if kept and not problems else []
        said += _gap_lines(problems, no_supply, no_receiver, no_driver)
        said += ["  not on the board: %s — %s" % (item["need"], need_requirements.NOT_ON_THE_BOARD[item["why"]].format(picks=", ".join(item["picks"])))
                 for item in ([] if problems else unserved)]
        said += [] if problems else _names_your_entries(need_requirements.REQUIREMENTS, need_requirements.unserved_keys(content) - named, dry_run)
        return Answer({"path": str(path), "requirements": content, "shelved": [Path(r).stem for r, _ in shelving],
                       "unplaced": unplaced, "kept": kept, "board_was": board_was, "placeholder_outline": [part_id for part_id, _ in placeholder],
                       "unserved": unserved, "no_supply": no_supply, "no_driver": no_driver,
                       "no_receiver": no_receiver, "written": not problems and not dry_run},
                      _write_lines([], problems, dry_run, said), problems=problems)
# --- end MVP ---
