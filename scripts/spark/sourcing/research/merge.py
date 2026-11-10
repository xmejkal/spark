"""
Folding what research found into the part record (P737, step 4). `fold_replies` writes each reply to an open question as
a fact: unverified, with a source that says who read it where (★C16 of the discovery brief: a value read off a drawing is
never `verified: true`). `fold_facts`, for the facts a source offers itself, follows in step 5 with the `conflicts` list.
"""

import copy

from spark.sourcing.part_records import PHYSICAL_WHY

# --- MVP ---
#: The `source` of a fact a reply gave: read off the cited document, or given with no citation.
READ_FROM, GIVEN_BY = "read from %s %s by %s", "given by %s"
#: The blocks a reply fills, and the two sizes a `body_mm` reply carries (its provenance is the block's own).
PHYSICAL, PROOF, BODY = "physical", "physical_proof", "body_mm"
BODY_KEYS = ("width", "height")
NOT_PUBLISHED = "not_published"


def source_of(reply):
    """One sentence: where this reply was read, by whom."""
    return READ_FROM % (reply.cites["document"], reply.cites["at"], reply.answered_by) if reply.cites else GIVEN_BY % (reply.answered_by,)


def _distinct(sentences):
    return [sentence for index, sentence in enumerate(sentences) if sentence and sentence not in sentences[:index]]


def provenance_of(replies, why):
    """The provenance block of a fact these replies gave: unverified, their distinct sources joined, `why`, the first
    citation when one has it, and their notes when any has one."""
    block = {"verified": False, "source": "; ".join(_distinct([source_of(reply) for reply in replies])), "why_it_matters": why}
    cited = [reply.cites for reply in replies if reply.cites]
    notes = _distinct([reply.note for reply in replies])
    block.update({"cites": cited[0]} if cited else {})
    block.update({"note": "; ".join(notes)} if notes else {})
    return block


def fold_replies(record, replies, questions, whys):
    """
    A deep copy of `record` with each reply (key to Reply) to one of the open `questions` written as a fact, and the sorted
    top-level keys it wrote. `physical.<key>` goes under `physical`, with one `physical_proof` beside it whose `not_published`
    keeps the old proof's minus the keys written. `body_mm` takes the reply's width and height. `whys` maps a key to the
    sentence that becomes `why_it_matters`; the proof's is the rule's own `PHYSICAL_WHY`. Nothing else changes.
    """
    after, written = copy.deepcopy(record), set()
    open_keys = {question.key for question in questions}
    folded = [reply for key, reply in replies.items() if key in open_keys]
    physical = [reply for reply in folded if reply.key.startswith(PHYSICAL + ".")]
    if physical:
        block = after.setdefault(PHYSICAL, {})
        keys = [reply.key.split(".", 1)[1] for reply in physical]
        block.update({key: reply.value for key, reply in zip(keys, physical)})
        proof = provenance_of(physical, PHYSICAL_WHY)
        left = [key for key in (after.get(PROOF) or {}).get(NOT_PUBLISHED, []) if key not in keys]
        after[PROOF] = dict(proof, **{NOT_PUBLISHED: left}) if left else proof
        written |= {PHYSICAL, PROOF}
    for reply in (reply for reply in folded if reply.key == BODY):
        sizes = {key: reply.value[key] for key in BODY_KEYS if key in reply.value} if isinstance(reply.value, dict) else {}
        after[BODY] = dict(sizes, **provenance_of([reply], whys.get(BODY)))
        written.add(BODY)
    return after, sorted(written)
# --- end MVP ---
