"""
The sources of research (P737, steps 4 and 5). A `ResearchSource` offers what it can for the gaps of one part record:
documents, Questions it cannot answer itself, the URLs it read and the problems it met. `ResearchPart` runs the sources
in its order as a pipeline: each offer is folded into the record before the next source asks. `DfrobotWikiSource` reads
the module's wiki page by its `sku` and keeps the documents the page lists. `KeptDocumentsSource` reads no network:
when the record keeps a dimension drawing, it asks one AGENT Question per geometry gap that cites that drawing.
"""

import abc
import json
import re
from collections import namedtuple
from urllib.parse import urlsplit

from spark.core.errors import SparkError
from spark.core.replies import AGENT, EITHER, VALUE, Question
from spark.records import store
from spark.records.store import StoreError
from spark.sourcing.datasheets import KEEPABLE, document_entry, document_key, document_name, keep_in_store
from spark.sourcing.sourcing_codes import MORE_DOCUMENTS, NO_DOCUMENT_LIST, NO_SKU

# --- MVP ---
#: The "where" words of a source, printed in the run's source order: this machine alone, or the web at no cost.
WHERE_LOCAL, WHERE_WEB = "local", "web, free"
#: The page a question about a kept drawing cites: a dimension drawing is one page.
FIRST_PAGE = "page 1"
#: A document whose key or title holds one of these words is the drawing a geometry question cites.
DRAWING_TITLE_WORDS = ("dimension", "drawing")
#: The `why` of a Question, from its FactNeed: who reads the fact today, or will, and the card that makes it read.
READS_WHY, WILL_READ_WHY = "%s reads it", "%s will read it (%s)"

#: Value: what one source offers for the gaps it was given. `documents` is key to entry, as a record's `documents` block;
#: `questions` the Questions the source cannot answer itself, each citing where the answer is when the source knows;
#: `problems` the SparkErrors it met (a page that did not answer), each one unchecked item of the run; `urls_read` the
#: pages it read this run, which enter the record's `sources`.
SourceOffer = namedtuple("SourceOffer", "documents questions problems urls_read", defaults=({}, (), (), ()))


def why_of(need):
    """The sentence that says why a fact matters: its consumer and whether it reads the fact today."""
    return READS_WHY % need.consumer if need.reads else WILL_READ_WHY % (need.consumer, need.card)


def question_for(need, question, cites=None):
    """The Question for one gap: the file's `question` (text, unit, answer_form, example) for the need's fact path. With
    `cites`, an AGENT reads the answer off the cited document; without, EITHER answers, because nobody knows where it is."""
    return Question(need.fact_path, question["text"], VALUE, AGENT if cites else EITHER, why_of(need),
                    question["unit"], question["answer_form"], question["example"], None, cites)


def _entries(documents):
    """The (key, entry) pairs of a `documents` block that are objects; the record's rules say what is wrong with the rest."""
    return [(key, entry) for key, entry in (documents.items() if isinstance(documents, dict) else ()) if isinstance(entry, dict)]


def _says_drawing(key, entry):
    said = ("%s %s" % (key, entry.get("title") or "")).lower()
    return any(word in said for word in DRAWING_TITLE_WORDS)


def names_a_drawing(documents):
    """Whether any entry, kept or not, is a drawing by its key or title: what a page listed, whether or not the store holds it."""
    return any(_says_drawing(key, entry) for key, entry in _entries(documents))


def drawing_key(documents, kept):
    """The key of the first drawing whose file is kept under `kept` (the store's sources folder), or None. An entry with
    `kept: false` has no file, so it is never cited."""
    for key, entry in _entries(documents):
        if _says_drawing(key, entry) and (kept / str(entry.get("sha256")) / str(entry.get("file"))).is_file():
            return key
    return None


class ResearchSource(abc.ABC):
    """Strategy: one place research looks. `offer(gaps, record, outside)` gives a SourceOffer for the gaps (FactNeed rows)
    of `record`, reaching the outside only through `outside`. It takes the `FactNeeds` for the question texts, and `kept`,
    the store's sources folder, or a test's."""

    where = WHERE_LOCAL

    def __init__(self, needs, kept=None):
        self.needs = needs
        self._kept = kept

    @property
    def kept(self):
        return self._kept or store.place("sources")

    @abc.abstractmethod
    def offer(self, gaps, record, outside):
        """The SourceOffer for these gaps."""


class KeptDocumentsSource(ResearchSource):
    """
    Strategy: the documents the record already keeps in the person's store, with no network. When one of them is a
    drawing (`DRAWING_TITLE_WORDS` in its key or title) and its file is kept, it asks one AGENT Question per gap, each
    citing that drawing at page 1. Otherwise it offers nothing.
    """

    def offer(self, gaps, record, outside):
        drawing = drawing_key(record.get("documents"), self.kept)
        if drawing is None:
            return SourceOffer()
        cites = {"document": drawing, "at": FIRST_PAGE}
        return SourceOffer(questions=[question_for(need, self.needs.question_of(need.fact_path), cites) for need in gaps])


class DfrobotWikiSource(ResearchSource):
    """
    Strategy: the DFRobot wiki page of the module, by its `sku`. It fetches the page once per record (never when the
    record's `sources` already hold the page's URL), reads the page's document list (the JSON-LD block, `DigitalDocument`
    entries with a `name`, a `url` and a `fileFormat`), keeps each keepable file in the store and lists the rest as
    `kept: false`. It asks no question itself: the kept drawing is the next source's. A page or a file that does not
    answer is a problem, never silence; a record of another vendor gets no fetch and no problem.
    """

    where = WHERE_WEB
    VENDOR = "dfrobot"
    PAGE = "https://wiki.dfrobot.com/%s/"
    #: The `fileFormat` words of a file the store keeps, beside the `KEEPABLE` endings.
    KEEPABLE_FORMATS = ("application/pdf", "image/png", "image/jpeg", "image/webp", "image/svg+xml")
    #: The most files kept from one page: the researcher's own fetch budget (agents/parts-researcher.md).
    MOST_DOCUMENTS = 12
    RETRY_FIX = "run again when the page answers; the other sources still ran"
    NO_SKU_FIX = "write the maker's part number as the record's sku (parts.py --skeleton --sku, or by hand), then run again"
    NO_LIST_FIX = "keep the page's documents by hand: parts.py --fetch after their URLs are in the record's sources"
    LD_JSON = re.compile(r'<script\s+type="application/ld\+json"\s*>(.*?)</script>', re.S)

    def page_of(self, record):
        """The page's URL from the record's first string `sku`, lower case, or None."""
        sku = record.get("sku")
        skus = sku if isinstance(sku, list) else [sku]
        first = next((one for one in skus if isinstance(one, str) and one.strip()), None)
        return self.PAGE % first.strip().lower() if first else None

    @staticmethod
    def listed_documents(html):
        """[(title, url, file_format)] of the `DigitalDocument`s with a URL that the page's JSON-LD lists (under any node's
        `subjectOf`), or None when the page has no such list spark can read."""
        found = DfrobotWikiSource.LD_JSON.search(html)
        try:
            data = json.loads(found.group(1)) if found else None
        except ValueError:
            data = None
        if not isinstance(data, dict):
            return None
        nodes = data.get("@graph") if isinstance(data.get("@graph"), list) else [data]
        listed = [(doc.get("name"), doc["url"], doc.get("fileFormat")) for node in nodes if isinstance(node, dict)
                  for doc in (node.get("subjectOf") or []) if isinstance(doc, dict)
                  and doc.get("@type") == "DigitalDocument" and isinstance(doc.get("url"), str)]
        return listed if any(isinstance(node, dict) and "subjectOf" in node for node in nodes) else None

    @staticmethod
    def _sources_hold(record, url):
        sources = record.get("sources")
        held = sources.values() if isinstance(sources, dict) else (sources if isinstance(sources, list) else ())
        return url in held

    @staticmethod
    def _keepable(url, file_format):
        return file_format in DfrobotWikiSource.KEEPABLE_FORMATS or url.split("?")[0].lower().endswith(KEEPABLE)

    @staticmethod
    def _is_file(url):
        """A URL whose path ends in a file extension: a page (a GitHub repository) is not a document."""
        return "." in urlsplit(url).path.rsplit("/", 1)[-1]

    @staticmethod
    def _problem(error, fix):
        return SparkError("%s", error, code=error.code, fix=fix)

    def offer(self, gaps, record, outside):
        if str(record.get("vendor") or "").strip().lower() != self.VENDOR:
            return SourceOffer()
        url = self.page_of(record)
        if url is None:
            return SourceOffer(problems=(SparkError("%s has no sku, so its DFRobot wiki page has no address", record.get("id"), code=NO_SKU, fix=self.NO_SKU_FIX),))
        if self._sources_hold(record, url):
            return SourceOffer()
        try:
            html = outside.fetch(url).decode("utf-8", "replace")
        except StoreError as unreached:
            return SourceOffer(problems=(self._problem(unreached, self.RETRY_FIX),))
        listed = self.listed_documents(html)
        if listed is None:
            return SourceOffer(problems=(SparkError("%s lists no documents spark can read", url, code=NO_DOCUMENT_LIST, fix=self.NO_LIST_FIX),), urls_read=(url,))
        documents, problems = self._keep(listed, record, outside)
        return SourceOffer(documents=documents, problems=tuple(problems), urls_read=(url,))

    def _keep(self, listed, record, outside):
        """The entries for the first `MOST_DOCUMENTS` listed files: kept ones through the store, the rest `kept: false`;
        a file that does not answer, or that the store refuses, is one problem and no entry."""
        documents, problems = {}, []
        taken = dict(record.get("documents") or {}) if isinstance(record.get("documents"), dict) else {}
        held = {entry.get("url") for entry in taken.values() if isinstance(entry, dict)}
        files = [(title, url, file_format) for title, url, file_format in listed if self._is_file(url) and url not in held]
        for title, url, file_format in files[:self.MOST_DOCUMENTS]:
            name = document_name(url)
            key = document_key(name, taken)
            if not self._keepable(url, file_format):
                documents[key] = {"url": url, "kept": False, "title": title}
            else:
                try:
                    digest = keep_in_store(outside.fetch(url), name)
                except StoreError as refused:
                    problems.append(self._problem(refused, self.RETRY_FIX))
                    continue
                documents[key] = document_entry(url, digest, name, outside.clock.now().date().isoformat(), title)
            taken[key] = documents[key]
        if len(files) > self.MOST_DOCUMENTS:
            problems.append(SparkError("the page lists %d files; the first %d were taken and these were not: %s", len(files), self.MOST_DOCUMENTS,
                                       ", ".join(url for _, url, _ in files[self.MOST_DOCUMENTS:]), code=MORE_DOCUMENTS, fix=self.NO_LIST_FIX))
        return documents, problems


#: Every source by the name the run prints, as `bench.OPERATIONS` maps each op to its class. The order is `research_part.SOURCE_ORDER`.
RESEARCH_SOURCES = {"dfrobot-wiki": DfrobotWikiSource, "kept-documents": KeptDocumentsSource}
# --- end MVP ---
