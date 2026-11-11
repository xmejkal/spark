"""
Folding what research found into the part record (P737, steps 4 and 5). `fold_replies` writes each reply to an open
question as a fact: unverified, with a source that says who read it where (★C16 of the discovery brief: a value read off
a drawing is never `verified: true`). `fold_documents` writes what a source kept and read: its `documents` and the URLs
into `sources`. `fold_not_published` writes the keys a vendor's page did not publish into `physical_proof`. No source
offers a fact value yet; the first that does brings `fold_facts` and a `fact_conflicts` list (two sources, two values, neither overwritten).
"""

import copy

from spark.sourcing.part_records import PHYSICAL_WHY

# --- MVP ---
#: The `source` of a fact a reply gave: read off the cited document by whom (`answered_by` says it), or given with no citation.
READ_FROM, GIVEN_BY = "read from %s %s, %s", "given by %s"
#: The blocks a reply fills, and the two sizes a `body_mm` reply carries (its provenance is the block's own).
PHYSICAL, PROOF, BODY = "physical", "physical_proof", "body_mm"
BODY_KEYS = ("width", "height")
NOT_PUBLISHED = "not_published"


def source_of(reply):
    """One sentence: where this reply was read, by whom. A citation the file left incomplete is read as it is; the record's
    rules judge it."""
    cites = reply.cites if isinstance(reply.cites, dict) else None
    return READ_FROM % (cites.get("document"), cites.get("at"), reply.answered_by) if cites else GIVEN_BY % (reply.answered_by,)


def not_published_of(record):
    """The keys `physical_proof.not_published` names: a list of strings, else nothing (the rule says what is wrong with the rest)."""
    proof = record.get(PROOF)
    named = proof.get(NOT_PUBLISHED) if isinstance(proof, dict) else None
    return [key for key in named if isinstance(key, str)] if isinstance(named, list) else []


def body_sizes(value):
    """A `body_mm` value as a reply says it: its width and height alone, because the block carries its provenance too."""
    return {key: value.get(key) for key in BODY_KEYS} if isinstance(value, dict) else value


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


def merge_proof(old, new):
    """The new proof over an old one: nothing an earlier reading said is lost. The sources and notes join, `verified` is
    False (one block vouches for every key, and the new keys are read off a drawing), the citation is the new one, else the old."""
    joined = {key: "; ".join(_distinct([old.get(key), new.get(key)])) for key in ("source", "note") if old.get(key) or new.get(key)}
    cites = new.get("cites") or old.get("cites")
    return dict(new, **joined, **({"cites": cites} if cites else {}))


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
        block = after[PHYSICAL] if isinstance(after.get(PHYSICAL), dict) else {}
        keys = [reply.key.split(".", 1)[1] for reply in physical]
        block.update({key: reply.value for key, reply in zip(keys, physical)})
        after[PHYSICAL] = block
        old = after.get(PROOF) if isinstance(after.get(PROOF), dict) else {}
        proof = merge_proof(old, provenance_of(physical, PHYSICAL_WHY))
        left = [key for key in not_published_of(after) if key not in keys]
        after[PROOF] = dict(proof, **{NOT_PUBLISHED: left}) if left else proof
        written |= {PHYSICAL, PROOF}
    for reply in (reply for reply in folded if reply.key == BODY):
        sizes = {key: value for key, value in body_sizes(reply.value).items() if value is not None} if isinstance(reply.value, dict) else {}
        after[BODY] = dict(sizes, **provenance_of([reply], whys.get(BODY)))
        written.add(BODY)
    return after, sorted(written)


DOCUMENTS, SOURCES = "documents", "sources"
#: The key under which a dict `sources` (four library records keep one) gets a URL research read; a list appends it.
READ_KEY = "research"


def _free_key(taken):
    key, number = READ_KEY, 2
    while key in taken:
        key, number = "%s-%d" % (READ_KEY, number), number + 1
    return key


def fold_documents(record, offer):
    """
    A deep copy of `record` with the offer's `documents` added under their keys (a key the record holds is left as it is,
    so a hand-written title survives) and its `urls_read` added to `sources` once each (appended to a list, keyed in a dict),
    and the sorted top-level keys it changed. A `documents` or `sources` that is neither absent nor of its shape is left as
    it is: the record's rules say what is wrong with it.
    """
    after, written = copy.deepcopy(record), set()
    documents = after.get(DOCUMENTS)
    if documents is None or isinstance(documents, dict):
        new = {key: entry for key, entry in offer.documents.items() if key not in (documents or {})}
        if new:
            after[DOCUMENTS] = dict(documents or {}, **new)
            written.add(DOCUMENTS)
    sources = after.get(SOURCES)
    for url in offer.urls_read:
        if isinstance(sources, dict) and url not in sources.values():
            sources[_free_key(sources)] = url
        elif (sources is None or isinstance(sources, list)) and url not in (sources or []):
            sources = (sources or []) + [url]
        else:
            continue
        after[SOURCES] = sources
        written.add(SOURCES)
    return after, sorted(written)


def fold_not_published(record, keys, source):
    """A deep copy of `record` whose `physical_proof` names `keys` in `not_published` (the old keys kept, no repeats, minus
    what `physical` holds), with `source` the sentence that says which page lacks them and `verified: true` (it is the
    vendor's own page), merged over an older proof as `merge_proof` merges; and the keys it changed."""
    after = copy.deepcopy(record)
    held = after[PHYSICAL] if isinstance(after.get(PHYSICAL), dict) else {}
    named = _distinct(not_published_of(after) + list(keys))
    left = [key for key in named if key not in held]
    if not left:
        return after, []
    old = after.get(PROOF) if isinstance(after.get(PROOF), dict) else {}
    verified = bool(old.get("verified")) if old else True  # one block vouches for every key: an older unverified reading keeps it unverified
    after[PROOF] = dict(merge_proof(old, {"verified": verified, "source": source, "why_it_matters": PHYSICAL_WHY}), **{NOT_PUBLISHED: left})
    return after, [PROOF]
# --- end MVP ---
