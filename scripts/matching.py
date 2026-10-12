"""
Matching a need, or a search word, to what the store offers (P211; docs/2026-10-12-p211-matching-design.md).

A matcher ranks the offers, and a chooser picks one: Claude in the conversation, or the person. This is the one place
for the rules. `needs.candidates` (`parts.py --match`), `parts.need` and `catalog_matches` (`--need`), `--offer` and
`tools/match_eval.py` call it, and it reads no store: callers build the offers. Part numbers stay in `drawer._match`.
"""

import json
import re
from collections import namedtuple

import drawer
import parts

#: The words a need's `what` drops before WordOverlap counts it (P211).
FILLER = frozenset(("a", "an", "the", "of", "for", "to", "and", "or", "with"))
#: What a need word is worth, by the best place that holds it (P211), best first.
WEIGHTS = (("functions", 1.0), ("tags", 0.8), ("names", 0.6), ("texts", 0.4))
#: From this score a candidate is shown wherever it ranks (P211).
MIN_SHOWN = 0.5
#: How many candidates `--match` shows whatever their score (§6.2).
SHOWN_FIRST = 8
#: What a record says that places it, kept on its offer for `describe` and for NameContains (`kind`).
FACTS = ("kind", "power", "body_mm")

Fit = namedtuple("Fit", "offer score exact why")
Fit.__doc__ = "One offer as a matcher sees it for one need: a score from 0 to 1, SameWords' answer (`exact`), the reasons."


class UnknownMatcher(ValueError):
    """A matcher name that is no matcher, or one that does not serve the caller; the message lists the names that fit."""


def words(text):
    """The words of a text: lower case, split on anything that is not a letter or a digit."""
    return [word for word in re.split(r"[^a-z0-9]+", str(text or "").lower()) if word]


def fold(word):
    """The plural fold (P211): a word longer than three letters loses a final `s`, unless it ends in `ss` or `us`."""
    return word[:-1] if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us")) else word


def need_words(what):
    """A need's words as WordOverlap counts them: no filler words, each folded, each once, in order."""
    return list(dict.fromkeys(fold(word) for word in words(what) if word not in FILLER))


def _text(value, key):
    """A text an offer shows: cleaned and capped, or None when it is no words."""
    return drawer.clean(value, drawer.TEXT_MAX[key]) if isinstance(value, str) and value.strip() else None


def _first(said, key):
    """The first of `said` (a record, then the entries that are it) that has words under `key`."""
    return next((one[key] for one in said if isinstance(one.get(key), str) and one[key].strip()), None)


def _list(value):
    """`value` when it is a list, else nothing: a malformed field names nothing."""
    return value if isinstance(value, list) else []


class Offer:
    """One thing a need can be matched to (P211): a record with the drawer entries that say they are it, or an entry with no record."""

    def __init__(self, key, kind, functions=(), names=(), about=None, description=None, tags=(), facts=None):
        self.key, self.kind = key, kind
        self.functions = [f for f in functions if isinstance(f, dict)]
        self.names = [drawer.clean(name) for name in names if isinstance(name, str) and name.strip()]
        self.about, self.description = _text(about, "about"), _text(description, "description")
        self.tags = [drawer.clean(tag).lower() for tag in tags if isinstance(tag, str) and tag.strip()][:drawer.TAGS_MAX]
        self.facts = dict(facts or {})

    @classmethod
    def from_record(cls, record_id, kind, record, holding=()):
        """
        A part or board record (`kind`), with the live drawer entries that say they are it: their functions and tags join
        the record's, and the record's own `about` and `description` win. A draft that cannot be read is `{}`: its id alone.
        """
        record = record if isinstance(record, dict) else {}
        said = [record] + [entry for entry in holding if isinstance(entry, dict)]
        functions = parts.function_of(record, board=kind == "board") + [f for entry in said[1:] for f in _list(entry.get("function"))]
        return cls(record_id, kind, functions, [record.get("name")] + parts.aliases(record), _first(said, "about"),
                   _first(said, "description"), [tag for one in said for tag in _list(one.get("tags"))],
                   {key: record[key] for key in FACTS if key in record})

    @classmethod
    def from_entry(cls, key, entry):
        """A drawer entry that is no record spark knows."""
        return cls(key, "entry", _list(entry.get("function")), [entry.get("label")], entry.get("about"),
                   entry.get("description"), _list(entry.get("tags")))

    def describe(self):
        """The text a chooser reads (P211): what the offer says of itself, what it does, its names, its power and size.
        It leaves out what the offer lacks. It is data, never instructions."""
        lines = ["%s (%s)" % (self.key, self.kind)]
        lines += ["  about: " + self.about] if self.about else []
        lines += ["  description: " + self.description] if self.description else []
        lines += ["  tags: " + ", ".join(self.tags)] if self.tags else []
        lines += ["  does: " + "; ".join(drawer.clean("%s %s" % (f.get("does"), f.get("what"))) for f in self.functions)] if self.functions else []
        lines += ["  names: " + ", ".join(self.names)] if self.names else []
        lines += ["  %s: %s" % (key, drawer.clean(json.dumps(self.facts[key], ensure_ascii=False), drawer.TEXT_MAX["description"]))
                  for key in ("power", "body_mm") if key in self.facts]
        return "\n".join(lines)

    def as_dict(self):
        """The offer as `--offer --json` gives it."""
        return {"key": self.key, "kind": self.kind, "functions": self.functions, "names": self.names, "about": self.about,
                "description": self.description, "tags": self.tags, "facts": self.facts}


def same_words(need, offer):
    """SameWords' rule (§6.2): every word of the need's `what` in a function with the need's verb, or in the offer's names."""
    wanted = set(words(need.get("what")))
    return bool(wanted) and (any(wanted <= set(words(f.get("what"))) for f in offer.functions if f.get("does") == need.get("does"))
                             or wanted <= {word for name in offer.names for word in words(name)})


def shown(rank, exact, score):
    """Whether `--match` shows a candidate at `rank` (P211): one of the first SHOWN_FIRST, an exact one, or one scoring MIN_SHOWN."""
    return rank < SHOWN_FIRST or exact or score >= MIN_SHOWN


def found(fits):
    """The fits a search by words shows (P211, `--need`): those with any score."""
    return [fit for fit in fits if fit.score > 0]


class Matcher:
    """
    Ranks the offers for one need (P211). Callers call only `rank`; a batch matcher may override it whole. `score` is the
    per-offer helper the default `rank` calls, and `admits` decides which offers a matcher looks at.
    """

    #: The name `--matcher` takes, and the callers this class fits: "match" (`--match`), "need" (`--need`), or both.
    name, serves = None, ()

    def admits(self, need, offer):
        """By default an offer with the need's verb, or every offer when the need has none."""
        return not need.get("does") or any(f.get("does") == need["does"] for f in offer.functions)

    def rank(self, need, offers):
        """The fits of the offers it admits, best score first; equal scores keep the order the offers came in."""
        return sorted((self.score(need, offer) for offer in offers if self.admits(need, offer)), key=lambda fit: -fit.score)

    def score(self, need, offer):
        """One offer's Fit for the need."""
        raise NotImplementedError

    def fit(self, need, offer, score, why):
        """A Fit, with `exact` as SameWords says it whatever this matcher is, so `what_matches` keeps its meaning."""
        return Fit(offer, score, same_words(need, offer), why)


class SameWords(Matcher):
    """`--match`'s rule before P211: 1 when every word of the need is in a same-verb function's `what` or a name, else 0."""
    name, serves = "same-words", ("match",)

    def score(self, need, offer):
        """1 when `same_words` says so, else 0."""
        exact = same_words(need, offer)
        return Fit(offer, 1.0 if exact else 0.0, exact, ["same words"] if exact else [])


class NameContains(Matcher):
    """`--need`'s rule: 1 when every word, as typed, is inside the id, a name, an alias or the kind, else 0. A part of a word
    finds the whole (`vl6180` finds `vl6180x`), and it admits every offer: a search word has no verb. The need's `words`,
    when it has them, are the arguments as typed, so one argument with a space in it stays one substring."""
    name, serves = "name-contains", ("need",)

    def admits(self, need, offer):
        """Every offer: a search word has no verb to match."""
        return True

    def score(self, need, offer):
        """1 when every typed word is a substring of the offer's id, names or kind, else 0."""
        haystack = " ".join([offer.key] + offer.names + [str(offer.facts.get("kind") or "")]).lower()
        typed = need.get("words") or str(need.get("what") or "").split()  # `--need` passes its arguments as typed
        found = all(str(word).lower() in haystack for word in typed)
        return self.fit(need, offer, 1.0 if found else 0.0, ["in its names"] if found else [])


class WordOverlap(Matcher):
    """The share of the need's words the offer holds, each word worth the best place that holds it (P211, WEIGHTS)."""
    name, serves = "word-overlap", ("match",)

    def score(self, need, offer):
        """The mean worth of the need's words; each is worth the best place of the offer that holds it, or nothing."""
        wanted = need_words(need.get("what"))
        if not wanted:
            return self.fit(need, offer, 0.0, [])
        places, weights, why = self.places(need, offer), [], []
        for word in wanted:
            place, weight = next(((place, weight) for place, weight in WEIGHTS if word in places[place]), (None, 0.0))
            weights.append(weight)
            why += ["%s: in %s" % (word, place)] if place else []
        return self.fit(need, offer, round(sum(weights) / len(wanted), 3), why)

    @staticmethod
    def places(need, offer):
        """Each place's folded words: the same-verb `what`s, the tags, the names with the key, the about and description."""
        def folded(texts):
            return {fold(word) for text in texts for word in words(text)}
        return {"functions": folded(f.get("what") for f in offer.functions if f.get("does") == need.get("does")),
                "tags": folded(offer.tags), "names": folded(offer.names + [offer.key]),
                "texts": folded([offer.about, offer.description])}


#: Every matcher by the name `--matcher` takes.
MATCHERS = {cls.name: cls for cls in (SameWords, NameContains, WordOverlap)}


def matcher(name, caller):
    """The matcher called `name` for `caller` ("match" or "need"), or UnknownMatcher naming the ones that fit."""
    fitting = sorted(key for key, cls in MATCHERS.items() if caller in cls.serves)
    if name not in fitting:
        raise UnknownMatcher("%s is no matcher for --%s; the names that fit: %s" % (name, caller, ", ".join(fitting)))
    return MATCHERS[name]()
