"""
The requirements file from the picks (P97, P708): which records it lists, which needs nothing on the board serves, and the
power it lacks. `parts.py --requirements` calls it. It reads the needs file and the store through `needs`.
"""

import collections
import json
from pathlib import Path

from spark.design import loader
from spark.design import board_emitter
from spark.design import footprint_emitter
from spark.sourcing import drawer
from spark.sourcing.part_records import broken_problems
from spark.records import board_records, record_kind, records_codes, store
from spark.records.record_kind import _parse, _problem, owes
from spark.design.needs import as_record, read, unfiled_boards


# --- MVP ---
def parts_left_listed(project, dropped, after):
    """
    The parts requirements.json still lists after a need is dropped (P514): those the `dropped` need picked as a record
    (`as_record`) that no need `after` picks. A requirements file that is missing or not in shape lists none.
    """
    path = Path(project) / REQUIREMENTS
    try:
        held = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        listed = {_part_of(entry) for entry in held.get("parts") or []}
    except (ValueError, AttributeError, TypeError, OSError):
        return []
    known, entries = {row[:2]: row for row in drawer.linkable(project)}, drawer.entries()

    def picked(wanted):
        return {key for each in wanted for pick in each.get("pick") or [] for kind, key in [next(iter(as_record(pick, known, entries).items()))]
                if kind == "part"}
    return sorted((picked([dropped]) - picked(after)) & listed)


REQUIREMENTS = "requirements.json"
#: What `requirements` works out (§5.3, §8 L): the file as it would be, the records to shelve, the picks with no record to place,
#: the entries already in the file that no pick explains, the board the file named before, what refuses it, the picks laid out
#: at a placeholder outline, the needs nothing on the board serves, and what the board's power would lack (`_power_gaps`).
Requirements = collections.namedtuple("Requirements", "content shelving unplaced kept board_was problems placeholder unserved "
                                                      "no_supply no_receiver no_driver")
#: The note a requirements file keeps of the needs it leaves off the board (C-2): `check_spine` reads it into its verdict.
UNSERVED = "unserved"
#: The key a requirements file says the board alone with (P236): `--requirements` writes it, `check_spine` reads it.
BOARD_ONLY = "board_only"
#: The `why` of an unserved note: the codes `--requirements` writes and reads (C-2, F16). The values stay, because
#: requirements.json keeps them.
WHY_NO_PICK, WHY_GAP, WHY_NO_RECORD = "no pick", "a gap", "no record"
#: What `parts.py --requirements` says of a need nothing on the board serves (C-2), by why: plainly, and what the person can do.
NOT_ON_THE_BOARD = {WHY_NO_PICK: "no pick; --match lists its candidates",
                    WHY_GAP: "marked a gap: nothing like it is in the store yet; research it before it can be built",
                    WHY_NO_RECORD: "{picks} has no record: fine for what is wired off the board (a speaker, a battery); what sits on the "
                                 "board needs one — link its drawer entry to a record with `is`, or research one"}


def unserved_keys(content):
    """
    The drawer entry keys a requirements file names (F16): the picks of each `unserved` note "no record" — keys made from the
    person's labels, which `--requirements` says once, as `--pick` does of needs.json's. A note that is no such note names none.
    """
    notes = content.get(UNSERVED) if isinstance(content, dict) else None
    return {key for note in (notes if isinstance(notes, list) else []) if isinstance(note, dict) and note.get("why") == WHY_NO_RECORD
            for key in (note.get("picks") if isinstance(note.get("picks"), list) else []) if isinstance(key, str)}
#: The facts that place a part, not wire it (the PO, 2026-10-08; P165): a pick that owes only these is written, and the PCB step
#: lays it out at a placeholder size, said; one that owes a fact the circuit needs — a footprint, a pin order and its proof, a
#: simulation stance — is refused, as before.
LAYOUT_FACTS = ("body_mm",)


def _part_of(entry):
    """The part an entry of a requirements file's `parts` names — a bare id, or {part, name} — or None when it names none."""
    named = entry.get("part") if isinstance(entry, dict) else entry
    return named if isinstance(named, str) else None


def _name_of(entry):
    """The name an entry of `parts` gives its instance, or None."""
    name = entry.get("name") if isinstance(entry, dict) else None
    return name if isinstance(name, str) and name else None


def entry_label(entry):
    """An entry of `parts` in a sentence: tactile-button (BtnOpen), l9110s-module, or an entry that names no part."""
    return "%s%s" % (_part_of(entry) or "an entry that names no part", " (%s)" % _name_of(entry) if _name_of(entry) else "")


def _name_after(need_id):
    """A need's id as the name of its instance: open-lid is OpenLid."""
    return "".join(word.capitalize() for word in need_id.split("-"))


def _called(part_id, name):
    """What the generator calls an instance (`board_emitter.component_name`): the name it is given, else its part id in capitals."""
    return name or "".join(word.capitalize() for word in part_id.replace("_", "-").split("-"))


#: A name as the build tells names apart — `loader.one_name`, the one definition (P163, W16); this was a second copy of it.
_one_name = loader.one_name


def _serve_picks(existing, picked_by):
    """
    (the entries a pick explains, as indexes into `existing`; the picks no entry serves, as (position, need id, part id)).
    `picked_by` is {part id: [(position, need id)]}. An entry named after a need — whatever its capitals — is that need's; the
    entries of a part that are left pair off with its other picks in order — so what a pick leaves unserved is added, and
    what no pick serves is the entry nobody asked for.
    """
    explained, unserved = set(), []
    for part_id, picks in picked_by.items():
        free, unnamed = [number for number, entry in enumerate(existing) if _part_of(entry) == part_id], []
        for position, need_id in picks:
            its_own = _one_name(_name_after(need_id))
            own = next((number for number in free if _one_name(_name_of(existing[number]) or "") == its_own), None)
            if own is None:
                unnamed.append((position, need_id))
            else:
                free.remove(own)
                explained.add(own)
        paired = min(len(unnamed), len(free))
        explained.update(free[:paired])
        unserved += [(position, need_id, part_id) for position, need_id in unnamed[paired:]]
    return explained, unserved


def _merge_parts(existing, wanted):
    """
    (the parts after, the entries no pick explains, problems): the file's `parts` with its picks read into them (the PO,
    2026-10-08). What is there stays, unchanged and in its order — a name, `rails` and any other key are the person's — and an
    entry is added at the end for each pick it lacks. `wanted` is [(need id, part id)], one per pick, in pick order; a part
    picked n times needs n entries (`_serve_picks` says which are there). What no pick explains — added by hand, or left by a
    pick since changed — is kept, and said. An entry added for a part with two or more instances is named after its need, and
    refused by need id when the file already has that name, in any capitals (`_one_name`): the build refuses two components
    of one name.
    """
    picked_by = collections.defaultdict(list)
    for position, (need_id, part_id) in enumerate(wanted):
        picked_by[part_id].append((position, need_id))
    explained, unserved = _serve_picks(existing, picked_by)
    held_by = {}  # {one name: (who has it, what it is called there)}
    for entry in existing:
        if _part_of(entry):
            called = _called(_part_of(entry), _name_of(entry))
            held_by.setdefault(_one_name(called), ("%s in requirements.json" % _part_of(entry), called))
    added, problems = [], []
    for _, need_id, part_id in sorted(unserved):
        name = _name_after(need_id) if len(picked_by[part_id]) >= 2 else None
        called = _called(part_id, name)
        if _one_name(called) in held_by:
            holder, its_name = held_by[_one_name(called)]
            problems.append(_problem(need_id, 'its %s would be called %s, and %s is called %s — %s; give one of them a name of '
                                     'your own in requirements.json, {"part": "%s", "name": …}, and run this again'
                                     % (part_id, called, holder, its_name, loader.ONE_NAME_RULE, part_id)))
            continue
        held_by[_one_name(called)] = ("need %s's %s" % (need_id, part_id), called)
        added.append(part_id if name is None else {"part": part_id, "name": name})
    kept = [{"part": _part_of(entry), "name": _name_of(entry)} for number, entry in enumerate(existing) if number not in explained]
    return list(existing) + added, kept, problems


def _board_problems(board_picks, unfiled, project):
    """
    What refuses the board (§8 L): it is one, picked as its record. A board picked from the drawer that spark has no board
    file for is named, with the boards spark has a file for — the library's and the project's — that build, and those that stop
    at the footprint stage, which are never suggested (C-7); no board, or two, is said so.
    """
    if len(board_picks) == 1:
        return []
    if unfiled and not board_picks:
        filed = board_records.records(project)
        stopping = {board_id: footprint_emitter.footprint_stop_line(_parse(path)) for board_id, (_, path) in filed.items()}
        builds = [board_id for board_id in filed if not stopping[board_id]]  # C-7: a board that stops is never suggested
        said = "; ".join(["spark has one that builds for %s" % ", ".join(builds) if builds else "spark has no board file that builds"]
                         + ["%s %s" % (board_id, line) for board_id, line in stopping.items() if line])
        return [_problem(key, "picked as the board, but a board needs a board file — a record in boards/ — before spark can "
                              "build with it, and it has none; %s" % said,
                         '%swrite a board file for %s first (docs/guide/how-it-works.md, "Your own dev board")'
                         % ("pick %s, or " % " or ".join(builds) if builds else "", key)) for key in unfiled]
    return [_problem("board", "pick one board — %s" % (
        "picked: " + ", ".join(board_picks) if board_picks else "none is picked"))]


def _unserved(needs, known, entries):
    """
    The needs nothing on the board serves (the PO, 2026-10-08; C-2), as {"need", "why", "picks"}: one with no pick — "no pick",
    or "a gap" when it is marked one — and one whose every pick is a drawer entry with no record ("no record"), which the
    building list reserves and does not place. A record-less pick beside a placed one (the speaker beside its amplifier) leaves
    its need served. Said, never refused: whether a thing belongs on the board is the person's to say.
    """
    said = []
    for need in needs:
        picks = [as_record(pick, known, entries) for pick in need.get("pick") or []]
        if not picks:
            said.append({"need": need["id"], "why": WHY_GAP if need.get("mark") == "gap" else WHY_NO_PICK, "picks": []})
        elif all("entry" in pick for pick in picks):
            said.append({"need": need["id"], "why": WHY_NO_RECORD, "picks": [pick["entry"] for pick in picks]})
    return said


def _power_gaps(listed, known):
    """
    What the board's power would lack (C-3; the PO, 2026-10-08), from the records of every part the file lists, on the rails the
    file gives them: each rail a part draws from and nothing listed supplies — `board_emitter.rails_without_a_source`, the rule the
    schematic stage stops on — as {"rail", "drawn_by"}; each net a part drives that nothing listed receives
    (`board_emitter.outputs_with_nothing_on_them`) as {"net", "driven_by"}; and, split out of the first, each side of a driven pair
    nothing listed drives (`board_emitter.pair_sides_without_a_driver`: an amplifier's, never a supply's; F15) as {"net",
    "received_by"}. A part whose record is not found or is broken is left to the build to name. Said before the build, never
    refused: the inlet, the supply, the amplifier or the terminal is the person's pick.
    """
    part_list = []
    for entry in listed:
        part_id = _part_of(entry)
        path = known.get(("part", part_id), (None,) * 4)[3] if part_id else None
        record = _parse(path) if path else None
        if not isinstance(record, dict) or broken_problems(record, path):
            continue
        rails = entry.get("rails") if isinstance(entry, dict) and isinstance(entry.get("rails"), dict) else None
        try:
            # named by its id here, so what is said names what was picked rather than the record's long name
            part_list.append(dict(loader.on_rails(record, rails) if rails else record, name=part_id))
        except (loader.DesignError, TypeError, AttributeError):
            continue  # a rail given to a pin the part does not have: the build names it
    no_supply = [{"rail": net, "drawn_by": sorted({"%s.%s" % (part["name"], supply["pin"])
                                                   for part, supply, on in board_emitter.power_connections(part_list)
                                                   if on == net and supply.get("direction") != "out"})}
                 for net in board_emitter.rails_without_a_source(part_list)]
    no_receiver = [{"net": net, "driven_by": "%s.%s" % (name, pin)} for net, name, pin in board_emitter.outputs_with_nothing_on_them(part_list)]
    pair_sides = set(board_emitter.pair_sides_without_a_driver(part_list))
    no_driver = [{"net": gap["rail"], "received_by": gap["drawn_by"]} for gap in no_supply if gap["rail"] in pair_sides]
    return [gap for gap in no_supply if gap["rail"] not in pair_sides], no_receiver, no_driver


def _how_to_fill(path):
    """Where what a record owes is filled (§5.4): a record in spark's own library in spark's repository; any other with --fact-set."""
    if Path(path).parent.resolve() == record_kind.LIBRARY.resolve():
        return "it is in spark's own library, so it is filled in spark's repository, by a commit — --fact-set does not change the library"
    return "fill it in its own home with --fact-set"


def _part_picks(picks, known):
    """(the records to shelve, the (need id, key) placed, the picks at a placeholder outline, the problems) of the part picks
    among `picks`, for `requirements`."""
    shelve, wanted, placeholder, problems = [], [], [], []
    for need_id, (kind, key) in picks:
        if kind != "part":
            continue
        _, _, where, path = known.get(("part", key), (None, None, None, None))
        record = _parse(path) if path else None
        owed = owes(record) if isinstance(record, dict) else []
        wrong = (["no record called %s any more" % key] if path is None else
                 ["its record at %s does not parse as a JSON object — repair the file by hand" % path] if not isinstance(record, dict) else
                 ["owes %s — %s" % (", ".join(owed), _how_to_fill(path))] if set(owed) - set(LAYOUT_FACTS)
                 else broken_problems(record, path))
        problems += [_problem(key, sentence) for sentence in wrong]
        shelve += [(path, None if where == "catalog" else where)] if not wrong and where not in ("project", "shelf", "library") else []
        placeholder += [(key, _how_to_fill(path))] if owed and not wrong else []
        wanted.append((need_id, key))
    return shelve, wanted, placeholder, problems


def _held_file(project):
    """(the project's requirements file as a dict, its `parts` list), {} and [] when there is none; a StoreError when
    either is no JSON of its kind, for `requirements`."""
    file = Path(project) / REQUIREMENTS
    try:
        held = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {}
    except ValueError as broken:
        raise store.StoreError("%s is not JSON (%s) — fix it by hand", file, broken, code=records_codes.RECORD_FILE_BROKEN)
    held = held if isinstance(held, dict) else {}
    existing = held.get("parts") or []
    if not isinstance(existing, list):
        raise store.StoreError("%s: `parts` is not a list — fix it by hand", file, code=records_codes.RECORD_FILE_BROKEN)
    return held, existing


def requirements(project):
    """
    The picks read into the project's requirements file (§5.3, §8 L): a `Requirements` of (the file as it would be, the records
    to shelve, the picks not placed, the entries it keeps that no pick explains, the board it named before, the problems, the
    picks laid out at a placeholder outline with where theirs is filled). The board pick, and every part pick whose record owes
    nothing the circuit needs — one owing only its outline (`LAYOUT_FACTS`) is placed and said — and one in the catalog or in
    another project goes onto the shelf, so the build finds it; a pick with no record is reserved, not placed. A pick of a drawer
    entry is read as the record that entry is, when spark knows it (`as_record`). The file's own `parts` stay as they are and
    gain an entry for each pick they lack (`_merge_parts`); the keys the person added to the file (signals) stay. The file
    says `board_only` when it lists no part and every need is served (P387), and loses it when it lists a part.
    """
    known, entries, needs = {row[:2]: row for row in drawer.linkable(project)}, drawer.entries(), read(project)
    picks = [(need["id"], next(iter(as_record(pick, known, entries).items()))) for need in needs for pick in need.get("pick") or []]
    board_picks = sorted({key for _, (kind, key) in picks if kind == "board"})
    problems = _board_problems(board_picks, unfiled_boards(needs, known, entries), project)
    shelve, wanted, placeholder, wrong = _part_picks(picks, known)
    problems += wrong
    held, existing = _held_file(project)
    after, kept, naming = _merge_parts(existing, wanted)
    content = dict(held, board=board_picks[0] if board_picks else None, parts=after)
    unserved = _unserved(needs, known, entries)
    if unserved:
        content[UNSERVED] = unserved
    else:
        content.pop(UNSERVED, None)  # an old note goes once every need is on the board
    # --- MVP ---
    if not after and not unserved:
        content[BOARD_ONLY] = True  # P387: the board itself serves every need
    elif after:
        content.pop(BOARD_ONLY, None)  # the build refuses board_only beside parts; else the person's own word stays
    problems += naming
    problems = [problem for number, problem in enumerate(problems) if problem not in problems[:number]]  # a part picked twice is refused once
    return Requirements(content, list(dict.fromkeys(shelve)), list(dict.fromkeys(key for _, (kind, key) in picks if kind == "entry")),
                        kept, held.get("board"), problems, list(dict.fromkeys(placeholder)), unserved, *_power_gaps(after, known))
# --- end MVP ---
