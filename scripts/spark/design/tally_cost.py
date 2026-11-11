"""
`parts.py --tally`: the cost line of a project, as an Operation on the core (P726). It was `goal_handlers._op_tally`, in
design because it reads `needs`, which sourcing may not import (P721). The picks, how many came from the store and how
many you own, and what the project's steps cost (C-2, C-16). It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records import store
from spark.records.answer_operation import AnswerOperation
from spark.records.record_kind import Answer, _cannot
from spark.sourcing import drawer, run_cost
from spark.design import design_codes, needs

# --- MVP ---
#: The fix of a folder nobody listed.
NOT_LISTED_FIX = "mark a step with parts.py --step <project> <step> in a Claude Code session: that puts it on the list"
#: The fix of a step whose cost is not known.
NO_TRANSCRIPT_FIX = "mark each step with parts.py --step <project> <step> in a Claude Code session"


class TallyCost(AnswerOperation):
    """Operation: `tally` as parts.py answers it: the cost line, the needs picked, the gloss of what was counted, and why a
    cost was not counted; a folder nobody listed is a could-not-run item with its code."""

    name = "tally"
    arguments = (Argument(("--tally",), "project", str, "the cost line: the picks, how many came from the store (known to spark before the project: "
                          "its library, your store, your projects) and how many you own, and what the project's steps cost", metavar="PROJECT"),
                 COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, project):
        name = store.find_listed_name(project)
        if name is None:
            return Answer(unchecked=[_cannot("%s is not on your list of projects, so no step of it was marked" % project,
                                             NOT_LISTED_FIX, code=design_codes.PROJECT_NOT_LISTED)])
        history, entries, listed = store.events(), drawer.entries(), needs.read(project)
        picks = [(need["id"], pick) for need in listed for pick in need.get("pick") or []]
        unpicked = [need["id"] for need in listed if not need.get("pick")]  # C-2: the picks are counted against the needs they serve
        reused = [event for event in history if event.get("event") == "reused" and event.get("project") == name]
        from_store = sum(1 for need_id, pick in picks if dict({"event": "reused", "project": name, "need": need_id}, **pick) in reused)
        owned = sum(1 for _, pick in picks if needs.owned(pick, entries))
        try:
            counted, unchecked = run_cost.cost([event for event in history if event.get("event") == "step"], name), []
        except run_cost.NoTranscriptError as missing:
            counted, unchecked = None, [_cannot(str(missing), NO_TRANSCRIPT_FIX, code=missing.code)]
        said, unreadable = run_cost.line(len(picks), from_store, owned, counted), run_cost.unreadable_note(counted)
        built = any(event.get("event") == "built" and event.get("project") == name for event in history)
        needs_said = "%d of %d needs picked%s" % (len(listed) - len(unpicked), len(listed),
                                                  " — not picked: %s" % ", ".join(unpicked) if unpicked else "")
        return Answer({"picks": len(picks), "from_store": from_store, "owned": owned, "cost": counted, "built": built, "line": said,
                       "needs": len(listed), "needs_picked": len(listed) - len(unpicked)},
                      ["  " + said, "  " + needs_said] + ["  " + glossed for glossed in run_cost.gloss(counted)]
                      + ["  " + item["sentence"] for item in unchecked] + (["  " + unreadable] if unreadable else [])
                      + ([] if built else ["  not built yet — check_spine records it when the chain runs end to end, and a board-only build records none"]),
                      unchecked=unchecked)
# --- end MVP ---
