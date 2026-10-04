"""
What a goal needs, and what the store offers for each (P96; docs/2026-10-04-store-design.md §5.3, §6.2, §8 S and M).

A need is a verb and a few words — `{"id": "soil", "does": "sense", "what": "soil-moisture"}` — with a condition only when
it decides a part, and later a mark: have, have-unknown, know or gap. The file is `<project>/.spark/needs.json`. It holds
no part numbers, no owned counts, no places and no reasons: it belongs to a project, which may be public (§5.8). Why a
need is marked as it is, is said to the person, and 1c's history keeps it. Every write sets, never adds.
"""

import json
import re
from pathlib import Path

import drawer
import parts
import store

#: How a need stands against the store (§3).
MARKS = ("have", "have-unknown", "know", "gap")
#: A need's fields besides its `id` (§5.3). A pick is 1c's.
NEED_FIELDS = ("does", "what", "condition", "mark")
FILE = Path(".spark") / "needs.json"


def read(project):
    """The project's needs, in order — [] when it has none yet; a file not in the needs shape is a StoreProblem."""
    path = Path(project) / FILE
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as broken:
        raise store.StoreProblem("%s is not JSON (%s)" % (path, broken))
    if not (isinstance(data, dict) and isinstance(data.get("needs"), list)
            and all(isinstance(need, dict) and isinstance(need.get("id"), str) for need in data["needs"])):
        raise store.StoreProblem('%s is not {"schema": 1, "needs": [{"id", "does", "what", …}]} — fix it by hand' % path)
    return data["needs"]


def _problems(need):
    said = []
    if need.get("does") not in parts.VERBS:
        said.append("`does` is one of %s" % ", ".join(parts.VERBS))
    if not (isinstance(need.get("what"), str) and need["what"].strip()):
        said.append("`what` is a few words: soil-moisture, alarm, microcontroller")
    if need.get("condition") is not None and not (isinstance(need["condition"], str) and need["condition"].strip()):
        said.append("`condition` is words, or null")
    if need.get("mark") is not None and need["mark"] not in MARKS:
        said.append("`mark` is one of %s, or null" % ", ".join(MARKS))
    return said


def plan_set(project, items):
    """
    What a `--needs-set` would do (§8 S rule 5, M2): (the needs after, changes, problems). Each item sets fields on one
    need, by `id`; a new need needs `does` and `what`. A later item sees what an earlier one set. Nothing is written here.
    """
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return None, [], [parts._problem(None, "a needs write is a JSON list of needs, each an object with an `id`")]
    current = {need["id"]: dict(need) for need in read(project)}
    order, changes, problems = list(current), [], []
    for item in items:
        need_id = item.get("id")
        if not (isinstance(need_id, str) and store.PLAIN.fullmatch(need_id)):
            problems.append(parts._problem(None, "a need's `id` is lower-case letters, digits and '-'"))
            continue
        extra = sorted(set(item) - set(NEED_FIELDS) - {"id"})
        if extra:
            problems.append(parts._problem(need_id, "%s: not a need's field — a need holds %s, and no part number, count, "
                                                    "place or reason (§5.3)" % (", ".join(extra), ", ".join(NEED_FIELDS))))
            continue
        before = current.get(need_id)
        after = dict(before or {"id": need_id})
        after.update({key: (drawer.clean(value) if isinstance(value, str) else value) for key, value in item.items() if key != "id"})
        problems += [parts._problem(need_id, sentence) for sentence in _problems(after)]
        changed = [key for key in NEED_FIELDS if after.get(key) != (before or {}).get(key)]
        if changed:
            changes.append({"need": need_id, "new": before is None,
                            "was": {key: before.get(key) for key in changed} if before else {},
                            "now": {key: after.get(key) for key in changed}})
        order += [] if need_id in current else [need_id]
        current[need_id] = after
    return [current[need_id] for need_id in order], changes, problems


def write(project, needs):
    """The needs file, whole (`.part`, then renamed) — the project's folder made when it is new (§8 S rule 5)."""
    path = Path(project) / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    part.write_text(json.dumps({"schema": 1, "needs": needs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    part.replace(path)
