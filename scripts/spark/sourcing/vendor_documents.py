"""
Where a board's maker keeps its top view and its dimension drawing (P952 #1358): an ordered list of vendor finders,
each reading one maker's page by the record's sku. A finder only reads: it names the two files by the page's exact
words, so a changed page gives a Decline and never a wrong file. `find_documents.FindDocuments` keeps what it names.

    DfrobotDocumentFinder().find(record, fetch)  ->  FoundDocuments(page, top_view, drawing), or a Decline
"""

import collections
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from spark.breadboard.picture_makers import Decline, MakerUses
from spark.sourcing.datasheets import URL, keepable_url
from spark.sourcing.research.research_source import DfrobotWikiSource, dfrobot_wiki_page

# --- MVP ---
#: The two roles of a found file.
TOP_VIEW, DRAWING = "top-view", "drawing"
#: Value: one file a finder named: its role, its URL, the page's own word for it, and whether the store keeps its kind.
FoundFile = collections.namedtuple("FoundFile", "role url title keepable")
#: Value: what a finder found on one page: the page, and the top view and the drawing, each a FoundFile or a Decline.
FoundDocuments = collections.namedtuple("FoundDocuments", "page top_view drawing")


def _words(text):
    """`text` trimmed, its runs of white space made one space, case-folded: how a page's word is compared."""
    return " ".join(str(text or "").split()).casefold()


class VendorDocumentFinder:
    """Strategy: one maker's way to find a board's top view and dimension drawing. `knows(record)` says whether the record
    is that maker's; `uses()` gives its MakerUses; `page_of(record)` the page a run reads, or None; `find(record, fetch)`
    gives FoundDocuments, or a Decline when the record cannot name the page. It never raises for missing input; a
    StoreError of `fetch` passes up to the Operation."""

    NAME = None

    def knows(self, record):
        raise NotImplementedError

    def uses(self):
        raise NotImplementedError

    def page_of(self, record):
        raise NotImplementedError

    def find(self, record, fetch):
        raise NotImplementedError


class _PageReader(HTMLParser):
    """Adapter: the standard library's HTML parser over one page: its headings h2 to h4 and its images outside them, in
    page order, as ("heading", text) and ("img", src)."""

    HEADINGS = ("h2", "h3", "h4")

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.parts, self._heading = [], None
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag in self.HEADINGS:
            self._heading = []
        elif tag == "img" and self._heading is None:
            self.parts.append(("img", dict(attrs).get("src")))

    def handle_data(self, data):
        if self._heading is not None:
            self._heading.append(data)

    def handle_endtag(self, tag):
        if tag in self.HEADINGS and self._heading is not None:
            self.parts.append(("heading", "".join(self._heading)))
            self._heading = None


class DfrobotDocumentFinder(VendorDocumentFinder):
    """
    Strategy: DFRobot's wiki page of the board (`https://wiki.dfrobot.com/<sku>/`). A record is DFRobot's when its
    `vendor` is the word "dfrobot" or a URL in its `sources` is on dfrobot.com or one of its subdomains. The top view is
    the first image on the CDN's wiki folder in the section whose heading is exactly "Board Overview", without the
    CDN's `.webp` ending; the drawing is the JSON-LD document named exactly "Dimension".
    """

    NAME = "dfrobot"
    HOST = "dfrobot.com"
    SECTION = "board overview"
    DRAWING_NAME = "dimension"
    #: Where the wiki's pictures are: the CDN's host and a folder in the picture's path.
    IMAGE_HOST, IMAGE_FOLDER = "dfimg.dfrobot.com", "/wiki/"
    #: The endings of a picture the CDN serves as WebP: the picture itself is the name without `.webp`.
    WEBP_OF = (".png.webp", ".jpg.webp")

    def knows(self, record):
        vendor = record.get("vendor")
        if isinstance(vendor, str) and _words(vendor) == self.NAME:
            return True
        sources = record.get("sources")
        texts = sources.values() if isinstance(sources, dict) else (sources if isinstance(sources, list) else ())
        return any(self._on_host(url) for text in texts if isinstance(text, str) for url in URL.findall(text))

    def _on_host(self, url):
        host = (urlsplit(url).hostname or "").lower()
        return host == self.HOST or host.endswith("." + self.HOST)

    def uses(self):
        return MakerUses((), ("sku", "sources"), None, True)

    def page_of(self, record):
        return dfrobot_wiki_page(record)

    def find(self, record, fetch):
        page = self.page_of(record)
        if page is None:
            return Decline(self.NAME, "%s has no sku, so its DFRobot wiki page has no address" % record.get("id"), ("sku",))
        html = fetch(page).decode("utf-8", "replace")
        return FoundDocuments(page, self._top_view(html, page), self._drawing(html, page))

    def _top_view(self, html, page):
        parts = _PageReader(html).parts
        start = next((at for at, (kind, text) in enumerate(parts) if kind == "heading" and _words(text) == self.SECTION), None)
        if start is None:
            return Decline(self.NAME, 'the DFRobot wiki page %s has no "Board Overview" section' % page,
                           ('a top view: the page\'s "Board Overview" picture',))
        for kind, src in parts[start + 1:]:
            if kind == "heading":
                break
            url = urljoin(page, src or "")
            where = urlsplit(url)
            if (where.hostname or "").lower() == self.IMAGE_HOST and self.IMAGE_FOLDER in where.path:
                if where.path.lower().endswith(self.WEBP_OF):
                    url = where._replace(path=where.path[:-len(".webp")]).geturl()
                return FoundFile(TOP_VIEW, url, "Board Overview", True)
        return Decline(self.NAME, 'the DFRobot wiki page %s has no picture in its "Board Overview" section' % page,
                       ('a top view: the page\'s "Board Overview" picture',))

    def _drawing(self, html, page):
        listed = DfrobotWikiSource.listed_documents(html) or ()
        found = next(((url, file_format) for title, url, file_format in listed if _words(title) == self.DRAWING_NAME), None)
        if found is None:
            return Decline(self.NAME, 'the DFRobot wiki page %s lists no document named "Dimension"' % page,
                           ('a dimension drawing: the page\'s "Dimension" document',))
        url, file_format = found
        return FoundFile(DRAWING, url, "Dimension", file_format in DfrobotWikiSource.KEEPABLE_FORMATS or keepable_url(url))


#: Every finder by its name, and the order a run asks them in: the first that knows the record reads its page.
FINDERS = {DfrobotDocumentFinder.NAME: DfrobotDocumentFinder}
FINDER_ORDER = (DfrobotDocumentFinder.NAME,)
# --- end MVP ---
