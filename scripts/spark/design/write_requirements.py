"""
`parts.py --requirements`: the picks as the project's requirements.json, as an Operation on the core (P726). It was
`goal_handlers._op_requirements`. The board, and every part pick with a record; a catalog one goes onto the shelf; what
the file already holds stays; `board_only` when the board itself serves every need (P387). The dry run says what it would
write and writes nothing.
"""

import json
from pathlib import Path

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.core.outcomes import step
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation
from spark.records.record_kind import Answer
from spark.sourcing.part_facts import shelve
from spark.sourcing.part_records import PartError, any_record, limits_of_part
from spark.sourcing.write_answers import names_your_entries, write_lines
from spark.design import board_components, entry_origin, footprint_emitter, need_requirements

# --- MVP ---
#: What is said of an entry spark wrote for a pick that is gone (P877): the entry and the need it was written for.
GONE_SENTENCE = "written for a pick that is gone: %s (need %s)"
#: What is said of the entries the file keeps that no pick explains and spark did not write.
KEPT_SENTENCE = "kept, not from a pick: %s"
#: What a person at a terminal can do instead of the yes, after the entries are named.
BY_HAND_LINE = "  to remove one, delete it from requirements.json by hand, or answer yes (see next)"
#: The line of a no, and of a yes whose previous version could not be kept (so nothing was removed and the yes is spent).
NO_LINE = "  kept as yours: %s (you said no)"
LEFT_ALONE_LINE = "  left alone: %s (%s; your yes is used up, write it again to try again)"
#: The help of `--replies`, and the `why` of the step that removes the entries: the agent's own file, after the person's yes.
REPLIES_HELP = ('a file of your own with the person\'s yes to the removal of the entries data.unexplained names, {"replies": {"<remove_key>": true}}. '
                "One yes removes those entries once: the run sets it back to null. A person at a terminal can delete the lines by hand")
REMOVE_WHY = ("ask the person whether to remove the entries data.unexplained names; on a yes write {\"replies\": {\"%s\": true}} "
              "to a file of your own and run this with --replies <that file>")


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
    data_keys = ('path', 'requirements', 'shelved', 'unplaced', 'kept', 'board_was', 'placeholder_outline', 'no_simulation_stance', 'unserved', 'no_supply',
                 'no_driver', 'no_receiver', 'written', 'unexplained', 'remove_key', 'previous')
    arguments = (Argument(("--requirements",), "project", str,
                          "the picks as the project's requirements.json: the board, and every part pick with a record — one that owes only its outline "
                          "or its simulation is written with a warning, one that owes more is refused; a catalog one goes onto the shelf; what the file already holds stays; "
                          "board_only when the board itself serves every need; it names each entry that spark wrote for a pick that is gone "
                          "(data.unexplained), and removes them on the person's yes in --replies", metavar="PROJECT"),
                 ANSWER_ARGUMENTS["dry_run"],
                 COMMON_ARGUMENTS["replies"]._replace(help=REPLIES_HELP),
                 COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, project, dry_run, replies=None):
        found = need_requirements.requirements(project)
        removal = entry_origin.EntryRemoval(Path(project) / need_requirements.REQUIREMENTS, found, replies, dry_run)
        found = found._replace(unexplained=found.unexplained.disowned()) if removal.verdict is False else found  # a no is not asked again
        try:
            if removal.agreed:  # P877: the yes was read and the previous version staged; the file is merged again without the entries
                found = need_requirements.requirements(project, removing=found.unexplained)
            answer = self._answer_of(project, dry_run, found)
            removal.settle(found, dry_run)
        finally:
            removal.release()
        return _with_origin(answer, found, removal, Path(project) / need_requirements.REQUIREMENTS)

    def _answer_of(self, project, dry_run, found):
        """The answer for the picks `found`: the file written, or what a dry run would write, and what the picks leave off."""
        (content, shelving, unplaced, kept, board_was, problems, placeholder, unserved, no_supply, no_receiver, no_driver, unexplained,
         unsimulated) = found
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
        said += [] if problems else _part_limit_lines(content["parts"], Path(project))  # P778: what the simulation cannot show of each part
        said += ["  onto the shelf, so every project builds with it: %s" % ", ".join(Path(r).stem for r, _ in shelving)] if shelving and not problems else []
        said += [] if problems else _owed_lines(placeholder, unsimulated)
        said += ["  reserved, not placed — no record: %s" % ", ".join(unplaced)] if unplaced and not problems else []
        said += [] if problems else ["  %s" % sentence for sentence in _unexplained_sentences(unexplained)[0]]
        said += [] if problems else _gone_lines(unexplained)
        said += _gap_lines(problems, no_supply, no_receiver, no_driver)
        said += ["  not on the board: %s — %s" % (item["need"], need_requirements.NOT_ON_THE_BOARD[item["why"]].format(picks=", ".join(item["picks"])))
                 for item in ([] if problems else unserved)]
        said += [] if problems else names_your_entries(need_requirements.REQUIREMENTS, need_requirements.unserved_keys(content) - named, dry_run)
        return Answer({"path": str(path), "requirements": content, "shelved": [Path(r).stem for r, _ in shelving],
                       "unplaced": unplaced, "kept": kept, "board_was": board_was, "placeholder_outline": [part_id for part_id, _ in placeholder],
                       "no_simulation_stance": [part_id for part_id, _ in unsimulated],
                       "unserved": unserved, "no_supply": no_supply, "no_driver": no_driver,
                       "no_receiver": no_receiver, "written": not problems and not dry_run},
                      write_lines([], problems, dry_run, said), problems=problems, notes=[] if problems else _kept_notes(unexplained))


def _owed_lines(placeholder, unsimulated):
    """The warning lines of the picks placed though their records owe a fact (each `(part id, where it is filled)`): the
    outline the PCB step lays out at a placeholder size, and the simulation (P996: said, never refused)."""
    return (["  placeholder outline — %s owes body_mm, so the PCB step lays it out at a placeholder %g x %g mm: a dimension drawing "
             "(fetched after the person's yes) or a measurement fills it — %s" % ((part_id,) + board_components.DEFAULT_BODY_MM + (how,))
             for part_id, how in placeholder]
            + ["  no simulation yet — %s: spark cannot simulate it yet, so /spark:deploy asks your yes for firmware that no "
               "simulation tested — %s" % (part_id, how) for part_id, how in unsimulated])


def _unexplained_sentences(unexplained):
    """(kept, gone): what is said of the entries the file keeps that no pick explains. `kept` is one sentence for the person's
    entries, or none; `gone` one sentence per entry spark wrote for a pick that is gone. The text's lines and the notes say them."""
    kept = [KEPT_SENTENCE % ", ".join(need_requirements.entry_label(entry) for entry in unexplained.persons)] if unexplained.persons else []
    gone = [GONE_SENTENCE % (need_requirements.entry_label(each.shown), each.row.need) for each in unexplained.removable]
    return kept, gone


def _kept_notes(unexplained):
    """The notes of the entries the file keeps that no pick explains (P1139), each with no subject and the words of its line,
    so the text says it once and the page says it beside its answer."""
    kept, gone = _unexplained_sentences(unexplained)
    return [{"subject": None, "sentence": sentence} for sentence in kept + gone]


def _gone_lines(unexplained):
    """One line per entry spark wrote for a pick that is gone (P877): `  written for a pick that is gone: led-red-5mm (need light)`."""
    said = ["  %s" % sentence for sentence in _unexplained_sentences(unexplained)[1]]
    return said + [BY_HAND_LINE] if said else said


def _with_origin(answer, found, removal, path):
    """
    The `answer` with what the origin record adds (P877): the three data keys, the line of a removal or of an entry left alone, the
    notes of the record and of a reply, and the step that says how to remove the entries. The key is of the bytes the run left in
    the file, so the next run finds it; a refused run names no entry and holds no key.
    """
    gone = found.unexplained
    key = None if found.problems else gone.key(path.read_bytes() if path.is_file() else b"")
    data = dict(answer.data, unexplained=[] if found.problems else gone.to_dicts(), remove_key=key, previous=removal.previous)
    count = len(removal.unexplained.removable)
    said = ["  removed %d %s (the previous version is %s)" % (count, "entry" if count == 1 else "entries", removal.previous)] if removal.previous else []
    labels = ", ".join(need_requirements.entry_label(each.shown) for each in removal.unexplained.removable)
    said += [LEFT_ALONE_LINE % (labels, removal.left)] if removal.left else []
    said += [NO_LINE % labels] if removal.verdict is False else []
    other = entry_origin.NOTE_OTHER_KEY % key if removal.stale and key else None
    unwritten = entry_origin.NOTE_UNWRITTEN if removal.unwritten else None
    notes = [{"subject": subject, "sentence": sentence} for subject, sentence in
             ((entry_origin.ORIGIN_FILE.name, gone.note), ("replies", other), (entry_origin.ORIGIN_FILE.name, unwritten)) if sentence]
    follow = [step("requirements", ["--requirements", str(path.parent), "--replies", "<your replies file>"],
                   REMOVE_WHY % key, [WRITES], needs_person=True)] if key else []
    return answer._replace(data=data, lines=list(answer.lines) + said, notes=list(answer.notes) + notes, next=list(answer.next) + follow)


def _part_limit_lines(entries, project):
    """One line per part of `entries` whose record has limits (`limits_of_part`, P778): `  part <label>: <sentence>`, the
    pick's note in the file's words. An entry with no record, or none that names a part, gives no line."""
    said = []
    for entry in entries:
        part_id = entry if isinstance(entry, str) else (entry.get("part") if isinstance(entry, dict) else None)
        if not part_id:
            continue
        try:
            record = any_record(part_id, project)
        except PartError:
            continue
        said += ["  part %s: %s" % (need_requirements.entry_label(entry), sentence) for _, sentence in limits_of_part(record, part_id)]
    return said
# --- end MVP ---
