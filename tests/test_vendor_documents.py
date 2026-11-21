"""
Proof that the DFRobot finder names a board's top view and dimension drawing on the maker's wiki page by exact words
only, so a changed page gives a Decline and never a wrong file (P952 #1358). Every page is made up (`wiki_fixture`).

    python3 -m unittest tests.test_vendor_documents
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
import wiki_fixture as wiki  # noqa: E402
from fakes import FakeStoreFetch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard.picture_makers import Decline  # noqa: E402
from spark.sourcing.research.research_source import dfrobot_wiki_page  # noqa: E402
from spark.sourcing.vendor_documents import DfrobotDocumentFinder, FoundDocuments, FoundFile  # noqa: E402


def find(sections=wiki.SECTIONS, documents=wiki.DOCUMENTS, record=None):
    """What the finder finds on a made-up page, and the fetch it was given."""
    fetch = FakeStoreFetch({wiki.PAGE: wiki.page(sections, documents)})
    return DfrobotDocumentFinder().find(record or wiki.board(), fetch), fetch


class TheTopViewTest(unittest.TestCase):
    def test_the_board_overview_sections_first_image_is_the_top_view_without_the_cdns_webp_ending(self):
        found, fetch = find()
        self.assertIsInstance(found, FoundDocuments)
        self.assertEqual(found.page, wiki.PAGE)
        self.assertEqual(found.top_view, FoundFile("top-view", wiki.TOP_VIEW, "Board Overview", True))
        self.assertEqual(fetch.asked, [wiki.PAGE], "one fetch: the page; the finder fetches no file")

    def test_a_jpeg_loses_the_cdns_webp_ending_and_a_plain_webp_keeps_it(self):
        for src, url in (("https://dfimg.dfrobot.com/a/wiki/b_0x0.jpg.webp", "https://dfimg.dfrobot.com/a/wiki/b_0x0.jpg"),
                         ("https://dfimg.dfrobot.com/a/wiki/b_0x0.webp", "https://dfimg.dfrobot.com/a/wiki/b_0x0.webp")):
            with self.subTest(src=src):
                found, _ = find(sections=(("h3", "Board Overview", (src,)),))
                self.assertEqual(found.top_view.url, url)

    def test_the_heading_is_matched_trimmed_and_in_any_case(self):
        found, _ = find(sections=(("h2", "  BOARD \n Overview ", (wiki.TOP_VIEW_SRC,)),))
        self.assertEqual(found.top_view.url, wiki.TOP_VIEW)

    def test_an_image_off_the_cdns_wiki_folder_is_passed_over(self):
        sections = (("h4", "Board Overview", ("https://www.dfrobot.com/static/icon.png", "https://dfimg.dfrobot.com/a/other/x.png",
                                              wiki.TOP_VIEW_SRC)),)
        found, _ = find(sections=sections)
        self.assertEqual(found.top_view.url, wiki.TOP_VIEW)

    def test_an_empty_board_overview_section_declines_naming_the_page_and_the_section_and_takes_no_later_image(self):
        # DFR0975's shape: the section is empty, and the next section has a picture
        found, _ = find(sections=(("h4", "Board Overview", ()), ("h4", "Pinout", (wiki.PINOUT_PICTURE,))))
        self.assertIsInstance(found.top_view, Decline)
        self.assertIn(wiki.PAGE, found.top_view.reason)
        self.assertIn('"Board Overview"', found.top_view.reason)
        self.assertEqual(found.top_view.maker, "dfrobot")

    def test_an_image_whose_alt_says_board_overview_outside_that_section_is_not_taken(self):
        # DFR0534's shape: no Board Overview section; a pinout picture's alt and a longer heading say the words
        sections = (("h4", "Pinout and Board Overview", ((wiki.PINOUT_PICTURE, "DFR0534 Board Overview"),)),)
        found, _ = find(sections=sections)
        self.assertIsInstance(found.top_view, Decline)
        self.assertIn('no "Board Overview" section', found.top_view.reason)

    def test_a_changed_section_heading_declines_not_a_wrong_file(self):
        found, _ = find(sections=(("h4", "Product Overview", (wiki.TOP_VIEW_SRC,)), ("h4", "Pinout", (wiki.PINOUT_PICTURE,))))
        self.assertIsInstance(found.top_view, Decline)
        self.assertIsInstance(found.drawing, FoundFile, "the drawing is found on its own")


class TheDrawingTest(unittest.TestCase):
    def test_the_drawing_is_the_json_ld_document_named_dimension_not_the_first_listed(self):
        found, _ = find()
        self.assertEqual(found.drawing, FoundFile("drawing", wiki.DRAWING, "Dimension", True))

    def test_the_name_is_matched_trimmed_and_in_any_case_and_a_longer_name_is_not_it(self):
        listed = (("Dimension drawing", "https://dfimg.dfrobot.com/x/other.pdf", "application/pdf"),
                  (" DIMENSION ", wiki.DRAWING, "application/pdf"))
        found, _ = find(documents=listed)
        self.assertEqual(found.drawing.url, wiki.DRAWING)

    def test_a_drawing_in_a_zip_is_found_and_not_keepable(self):
        found, _ = find(documents=(("Dimension", "https://dfimg.dfrobot.com/wiki/1/DFR0975_dimension.zip", "application/zip"),))
        self.assertEqual(found.drawing, FoundFile("drawing", "https://dfimg.dfrobot.com/wiki/1/DFR0975_dimension.zip", "Dimension", False))

    def test_a_dimension_document_off_dfrobot_com_declines(self):
        for url in ("https://evil.example.net/dim.pdf", "https://notdfrobot.com/dim.pdf"):
            with self.subTest(url=url):
                found, _ = find(documents=(("Dimension", url, "application/pdf"),))
                self.assertIsInstance(found.drawing, Decline)
                self.assertIn(url, found.drawing.reason)

    def test_a_page_that_lists_no_dimension_document_or_no_list_declines(self):
        for documents in ((("Schematics", wiki.SCHEMATICS, "application/zip"),), None):
            with self.subTest(documents=documents):
                found, _ = find(documents=documents)
                self.assertIsInstance(found.drawing, Decline)
                self.assertIn(wiki.PAGE, found.drawing.reason)
                self.assertIsInstance(found.top_view, FoundFile, "the top view is found on its own")


class TheVendorTest(unittest.TestCase):
    def test_a_board_whose_vendor_is_an_object_is_dfrobots_by_its_sources_wiki_url(self):
        record = wiki.board()
        self.assertIsInstance(record["vendor"], dict)
        self.assertTrue(DfrobotDocumentFinder().knows(record))

    def test_a_vendor_word_dfrobot_in_any_case_is_dfrobots(self):
        self.assertTrue(DfrobotDocumentFinder().knows({"vendor": " DFRobot ", "sources": []}))

    def test_only_dfrobot_com_and_its_subdomains_are_dfrobots_hosts(self):
        for url, known in (("https://dfrobot.com/x", True), ("https://www.DFRobot.com/product-1.html", True),
                           ("https://notdfrobot.com/x", False), ("https://dfrobot.com.example.net/x", False),
                           ("https://example.net/dfrobot.com", False)):
            with self.subTest(url=url):
                self.assertIs(DfrobotDocumentFinder().knows({"vendor": "seeed", "sources": {"vendor": url}}), known)
                self.assertIs(DfrobotDocumentFinder().knows({"sources": ["read on %s, 2026-11-20" % url]}), known)

    def test_a_record_of_another_vendor_is_not_known(self):
        self.assertFalse(DfrobotDocumentFinder().knows({"vendor": "seeed", "sources": ["https://wiki.seeedstudio.com/x/"]}))
        self.assertFalse(DfrobotDocumentFinder().knows({"vendor": None, "sources": None}))

    def test_a_record_with_no_sku_declines_and_fetches_nothing(self):
        record = wiki.board()
        record["sku"] = [None, " "]
        fetch = FakeStoreFetch({})
        declined = DfrobotDocumentFinder().find(record, fetch)
        self.assertIsInstance(declined, Decline)
        self.assertEqual(declined.missing, ("sku",))
        self.assertEqual(fetch.asked, [])

    def test_the_page_is_the_first_string_sku_in_lower_case(self):
        self.assertEqual(dfrobot_wiki_page({"sku": [None, " DFR1075 ", "DFR9"]}), wiki.PAGE)
        self.assertEqual(dfrobot_wiki_page({"sku": "DFR0954"}), "https://wiki.dfrobot.com/dfr0954/")
        self.assertIsNone(dfrobot_wiki_page({"sku": None}))

    def test_the_finder_says_it_asks_first_because_it_reaches_the_network(self):
        self.assertIs(DfrobotDocumentFinder().uses().asks, True)


if __name__ == "__main__":
    unittest.main()
