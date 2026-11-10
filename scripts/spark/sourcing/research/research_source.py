"""
The sources of research (P737, step 4). A `ResearchSource` offers what it can for the gaps of one part record: facts,
documents and Questions it cannot answer itself. `ResearchPart` runs the sources in its order and asks the questions
through `outside.replies`. The first source, `KeptDocumentsSource`, reads no network: when the record keeps a dimension
drawing, it asks one AGENT Question per geometry gap that cites that drawing. `DfrobotWikiSource` follows in step 5.
"""

import abc
from collections import namedtuple

from spark.core.replies import AGENT, EITHER, VALUE, Question
from spark.records import store

# --- MVP ---
#: The "where" word of a source that reads this machine alone, printed in the run's source order.
WHERE_LOCAL = "local"
#: The page a question about a kept drawing cites: a dimension drawing is one page.
FIRST_PAGE = "page 1"
#: A kept document whose key or title holds one of these words is the drawing a geometry question cites.
DRAWING_TITLE_WORDS = ("dimension", "drawing")
#: The `why` of a Question, from its FactNeed: who reads the fact today, or will, and the card that makes it read.
READS_WHY, WILL_READ_WHY = "%s reads it", "%s will read it (%s)"

#: Value: what one source offers for the gaps it was given. `facts` and `documents` are step 5's; `questions` are the
#: Questions the source cannot answer itself, each citing where the answer is when the source knows.
SourceOffer = namedtuple("SourceOffer", "facts documents questions", defaults=((), (), ()))


def why_of(need):
    """The sentence that says why a fact matters: its consumer and whether it reads the fact today."""
    return READS_WHY % need.consumer if need.reads else WILL_READ_WHY % (need.consumer, need.card)


def question_for(need, question, cites=None):
    """The Question for one gap: the file's `question` (text, unit, answer_form, example) for the need's fact path. With
    `cites`, an AGENT reads the answer off the cited document; without, EITHER answers, because nobody knows where it is."""
    return Question(need.fact_path, question["text"], VALUE, AGENT if cites else EITHER, why_of(need),
                    question["unit"], question["answer_form"], question["example"], None, cites)


class ResearchSource(abc.ABC):
    """Strategy: one place research looks. `offer(gaps, record, outside)` gives a SourceOffer for the gaps (FactNeed rows)
    of `record`, reaching the outside only through `outside`. It takes the `FactNeeds` for the question texts."""

    def __init__(self, needs):
        self.needs = needs

    @abc.abstractmethod
    def offer(self, gaps, record, outside):
        """The SourceOffer for these gaps."""


class KeptDocumentsSource(ResearchSource):
    """
    Strategy: the documents the record already keeps in the person's store, with no network. When one of them is a
    drawing (`DRAWING_TITLE_WORDS` in its key or title) and its file is kept, it asks one AGENT Question per gap, each
    citing that drawing at page 1. Otherwise it offers nothing. `kept` is the store's sources folder, or a test's.
    """

    where = WHERE_LOCAL

    def __init__(self, needs, kept=None):
        super().__init__(needs)
        self._kept = kept

    @property
    def kept(self):
        return self._kept or store.place("sources")

    def drawing_of(self, record):
        """The key of the first kept document that is a drawing, or None."""
        for key, entry in (record.get("documents") or {}).items():
            said = ("%s %s" % (key, (entry.get("title") if isinstance(entry, dict) else None) or "")).lower()
            if any(word in said for word in DRAWING_TITLE_WORDS) and (self.kept / str(entry.get("sha256")) / str(entry.get("file"))).is_file():
                return key
        return None

    def offer(self, gaps, record, outside):  # --- Later, not MVP: `outside` is step 5's, where a source fetches through it ---
        drawing = self.drawing_of(record)
        if drawing is None:
            return SourceOffer()
        cites = {"document": drawing, "at": FIRST_PAGE}
        return SourceOffer(questions=[question_for(need, self.needs.question_of(need.fact_path), cites) for need in gaps])


#: Every source by the name the run prints, as `bench.OPERATIONS` maps each op to its class. The order is `research_part.SOURCE_ORDER`.
RESEARCH_SOURCES = {"kept-documents": KeptDocumentsSource}
# --- end MVP ---
