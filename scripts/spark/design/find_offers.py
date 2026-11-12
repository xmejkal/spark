"""
`parts.py --need`: what you own and what spark knows for a need, before researching (P743), as an Operation on the core
(P726). It was `goal_handlers._op_need`. The words go against what each record and drawer entry does, its tags, names and
text, owned first; a catalog row says how to build with it. It writes nothing.
"""


from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation
from spark.records.record_kind import Answer, _cannot
from spark.sourcing import datasheets, matching
from spark.sourcing.datasheets import NEED_MATCHER
from spark.sourcing.part_facts import _row
from spark.sourcing.brief_choices import sellers, vendor_order

# --- MVP ---
#: `--need`'s closing lines (P743): the fits the cutoff dropped, and nothing found.
NEED_MORE = "  and %d more with fewer of the words: add a word, or --matcher name-contains for the names alone"
NEED_NOTHING = ("  nothing in the drawer, the boards or the part records matches %r.\n"
                "  Research it: /spark:research \"%s\"  — vendors in order: %s; sellers: %s")
#: The help of the options the goal Operations share, worded as parts.py's OPTIONS rows.
MATCHER_HELP = ("with --match or --need: the matcher that ranks the offers (--match: same-words, word-overlap; "
                "--need: word-overlap, name-contains); a name that does not fit is refused with the names that do")


def _need_line(row):
    """One text row of `--need` (P743): `owned N` first when the drawer holds it, the id or the entry key, the kind (`drawer entry`
    for an entry, `board` for a board with no kind), the name, the layer when it is not the library, the first reason."""
    owned = "owned %s" % row["owned"] if row["owned"] != 0 else ""
    kind = "drawer entry" if row["is"] == "entry" else row["kind"] or row["is"]
    where = "" if row["in"] == "library" else "in %s" % row["in"]
    why = "[%s]" % row["why"][0] if row["why"] else ""
    return "  %-9s %-28s %-14s %s" % (owned, row["id"] or row["entry"], kind, "  ".join(filter(None, [row["name"] or "", where, why])))


class FindOffers(AnswerOperation):
    """Operation: `need` as parts.py answers it: the offers for the words, owned first, the drafts, the catalog rows and
    how many more the cutoff dropped; a matcher name that does not fit is a could-not-run item with its code."""

    name = "need"
    data_keys = ('need', 'vendor_order', 'found', 'drafts', 'catalog', 'more', 'matcher')
    arguments = (Argument(("--need",), "words", str, "what you own and what spark knows for a need, before researching: the words against "
                          "what each record (parts and boards, every layer) or drawer entry does, its tags, names and text, owned first (word-overlap); "
                          "--matcher name-contains for the names alone", nargs="+", metavar="WORD"),
                 Argument(("--matcher",), "matcher", str, MATCHER_HELP, metavar="NAME"),
                 ANSWER_ARGUMENTS["project"],
                 COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, words, matcher, project):
        try:
            chosen = matching.matcher(matcher or NEED_MATCHER, "need")
        except matching.UnknownMatcherError as wrong:
            return Answer(unchecked=[_cannot(str(wrong), code=wrong.code)])
        rows, drafts, more = datasheets.need(words, project, chosen)
        found = [row for row in rows if row["in"] != "catalog"]
        known = [row for row in rows if row["in"] == "catalog"]
        data = {"need": words, "vendor_order": list(vendor_order(project)), "found": found, "drafts": drafts, "catalog": known,
                "more": more, "matcher": chosen.name}
        lines = [_need_line(row) for row in found]
        lines += [_row(part_id, "(draft)", "does not yet meet the contract — being filled in") for part_id in drafts]
        lines += [_need_line(row) + "  [catalog: researched before; `--promote %s --project .` builds with it]" % row["id"] for row in known]
        lines += [NEED_MORE % more] if more else []
        if not lines:
            lines = [NEED_NOTHING % (" ".join(words), " ".join(words), ", ".join(vendor_order(project)),
                                     ", ".join(sellers(project)) or "none named in the brief")]
        return Answer(data, lines)
# --- end MVP ---
