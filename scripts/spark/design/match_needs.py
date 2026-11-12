"""
`parts.py --match`: each of a project's needs with the store's candidates, owned first, each with its score and why, as an
Operation on the core (P726). It was `goal_handlers._op_match`. A board that serves a need through its own LED, button or
display has `limits` (P397). It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.core.text_guards import printable
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation
from spark.records.record_kind import Answer, _cannot
from spark.sourcing import matching
from spark.design import design_codes, needs
from spark.design.find_offers import MATCHER_HELP

# --- MVP ---
#: The sentence of a project with no needs yet.
NO_NEEDS_SENTENCE = "%s has no needs yet — /spark:idea writes them"


class MatchNeeds(AnswerOperation):
    """Operation: `match` as parts.py answers it: per need, the candidates the matcher keeps, paged from `--from`; the
    problems `needs.match` found; a project with no needs and a matcher name that does not fit are could-not-run items."""

    name = "match"
    data_keys = ('needs',)
    arguments = (Argument(("--match",), "project", str, "each of a project's needs with the store's candidates: owned first, what each owes, "
                          "each with its score and why; --matcher picks the matcher that ranks them; a board that serves a need through its own "
                          "LED, button or display has `limits`, the sentences for what a passed run does not test of it", metavar="PROJECT"),
                 Argument(("--matcher",), "matcher", str, MATCHER_HELP, metavar="NAME"),
                 ANSWER_ARGUMENTS["start"],
                 COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, project, matcher, start):
        try:
            chosen = matching.matcher(matcher or needs.MATCHER, "match")
        except matching.UnknownMatcherError as wrong:
            return Answer(unchecked=[_cannot(str(wrong), code=wrong.code)])
        matched, problems = needs.match(project, chosen)
        if not matched and not problems:
            return Answer(unchecked=[_cannot(NO_NEEDS_SENTENCE % project, code=design_codes.NO_NEEDS_YET)])
        for need in matched:
            kept = [c for rank, c in enumerate(need["candidates"]) if matching.shown(rank, c["what_matches"], c["score"])]
            need["more"], need["candidates"] = len(need["candidates"]) - len(kept), kept
        lines = []
        for need in matched:
            lines.append("  %s — %s / %s%s%s" % (need["need"], need["does"], need["what"], "  (%s)" % need["condition"] if need["condition"] else "",
                                                "  [%s]" % need["mark"] if need["mark"] else ""))
            for c in need["candidates"]:
                lines.append("      %-10s %-46s %s" % ("owned %s" % c["owned"] if c["owned"] else "", "%s (%s)" % (c["id"] or c["entry"], c["in"]),
                                                      "  ".join(filter(None, [", ".join(c["what"]) + ("" if c["what_matches"] else " [other words]"),
                                                                              ("free %s%s" % (c["free"], ", held by " + ", ".join(map(printable, c["held_by"])) if c["held_by"] else "")) if c["owned"] else "",
                                                                              "owes " + ", ".join(c["owes"]) if c["owes"] else "",
                                                                              c.get("stop_line") or ""])))
                             + ("  maybe owned — check the drawer" if c["unsure"] else "") + ("  BROKEN" if c["broken"] else ""))
                lines += ["          " + c["about"]] if c["about"] else []
                lines += ["          " + sentence for sentence in c["limits"]]  # P397: the JSON keeps them as data
                del c["about"]  # the text shows it; the JSON gains only `score` and `why`
                c.pop("stop_line", None)  # likewise: the JSON has `stops_why`, the list
            hidden = "none with the need's words" if chosen.name == needs.MATCHER else "each scoring under %s" % matching.MIN_SHOWN
            lines += ["      … %d more, %s" % (need["more"], hidden)] if need["more"] else []
            lines += ["      nothing in the store does this — a gap"] if not need["candidates"] else []
        lines += ["  %s: %s" % (p["subject"], p["sentence"]) for p in problems]
        shown, truncated = store.page_with_store(matched, start, "match", ["--match", project] + (["--matcher", matcher] if matcher else []))
        return Answer({"needs": shown}, lines, problems=problems, truncated=truncated)
# --- end MVP ---
