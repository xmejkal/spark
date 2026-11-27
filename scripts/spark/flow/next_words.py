"""
NEXT's words in the NOW box over the firmware's and the simulation's tells (P1290, the UX lens of P1298, finding 1; the deploy's
sentences keep the whole sentence, P1338 #1920): the library of `tell_of` and `next_words`, which the page's guide section calls
(`page_sections.GuideHtmlSection`). There NEXT says the situation and where the tell goes (and, for a scenario, the cost), and
the tell's block holds the one ask. `flow.py show` never calls it, so the
CLI keeps the guide's whole sentence. NOW_BUTTON (`flow_codes`) is NEXT's other word table, for the sendable offers' button.
"""

from spark.flow import flow_codes

#: Where the tell under NEXT goes, said after the situation.
PASTE_TELL_HINT = "Paste the line below in Claude Code."
#: Who runs a scenario, and what it costs.
SCENARIO_COST_MESSAGE = "You run the scenario in your own terminal. " + flow_codes.WOKWI_COST_MESSAGE
#: The NOW sentences that stand over a tell, with NEXT's words in their place. As NOW_BUTTON, keyed by the sentence.
NOW_WITH_TELL = {
    flow_codes.FIRMWARE_NOW: " ".join(("No firmware yet.", PASTE_TELL_HINT, flow_codes.THIN_MAIN_RULE)),
    flow_codes.SIMULATE_NOW: " ".join(("No simulation tested this firmware yet.", PASTE_TELL_HINT, SCENARIO_COST_MESSAGE)),
    flow_codes.SCENARIO_FIRST_NOW: " ".join(("No scenario is written yet, so Claude writes one first.", PASTE_TELL_HINT,
                                             SCENARIO_COST_MESSAGE))}
#: TWO_JOBS_NOW's words over a tell, filled with the sheet's count of steps (`now.steps`).
TWO_JOBS_WITH_TELL_NOW = " ".join((flow_codes.TWO_JOBS_START, "and get the firmware from Claude.", flow_codes.WIRING_UNSEEN_MESSAGE,
                                   PASTE_TELL_HINT, flow_codes.THIN_MAIN_RULE))


def tell_of(now):
    """The tell of the chat offer the guide's `now` names (`now.chat_offer`, read with `.get`), or None for no chat offer
    or a key with no tell. The one rule of "the now has a tell", which `_ask` and `next_words` read."""
    row = flow_codes.OFFER_KINDS.get(now.get("chat_offer"))
    return row.tell if row else None


def next_words(now):
    """NEXT's words for the guide's `now` dict. Call it only where the tell is drawn under NEXT. With no tell (`tell_of`),
    `now.says` as it is, so a sentence never loses its ask where no block names Claude. With one: the two jobs' words filled
    with `now.steps` when it is set (`guide.now_sentence` sets it only with the two jobs' sentence, and `guide.guide_of` passes `count` only beside a current sheet),
    else the sentence's row in NOW_WITH_TELL, else `now.says`. Reads no file and writes nothing."""
    if tell_of(now) is None:
        return now["says"]
    if now.get("steps") is not None:
        return TWO_JOBS_WITH_TELL_NOW % now["steps"]
    return NOW_WITH_TELL.get(now["says"], now["says"])
