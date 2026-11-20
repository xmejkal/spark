"""
Proof that a part's picture is refused by rule and element before it is kept or drawn (P946 #1349): an SVG of the part's
frame size, of plain shapes, with at most embedded JPEGs that carry no EXIF, and no pad or label of spark's.

    python3 -m unittest tests.test_picture_check
"""

import base64
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import breadboard_codes, part_shape  # noqa: E402
from spark.breadboard.picture_check import PictureCheck, is_embedded_jpeg  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "pictures" / "epaper-synthetic.svg"
EPAPER = ROOT / "tests" / "data" / "breadboard" / "epaper" / "parts" / "epaper-2in9-bwr-mh-et-live.json"
JPEG = re.search(r'href="data:image/jpeg;base64,([^"]+)"', FIXTURE.read_text()).group(1)


def shape():
    return part_shape.ModuleShapeSource().find_shape(json.loads(EPAPER.read_text()))


def svg(inner, view_box="0 0 85 44", root=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s"%s>%s</svg>' % (view_box, root, inner)).encode()


def image(href):
    return '<image x="0" y="0" width="85" height="44" href="%s"/>' % href


def found(data):
    """[(code, element)] of each problem."""
    return [(problem.code, problem.element) for problem in PictureCheck(shape()).problems(data)]


class APictureThatHoldsPassesTest(unittest.TestCase):
    def test_the_synthetic_fixture_passes_and_its_base64_spells_no_web_address(self):
        self.assertEqual(found(FIXTURE.read_bytes()), [])
        self.assertNotIn("http", JPEG.lower())
        self.assertLess(len(FIXTURE.read_bytes()), 2048)

    def test_a_view_box_off_the_frame_is_refused_and_a_near_one_passes(self):
        self.assertEqual(found(svg("<rect width='1' height='1'/>", "0 0 85.2 44")), [("picture_view_box", "svg")])
        self.assertEqual(found(svg("<rect width='1' height='1'/>", "0 0 85 43.8")), [("picture_view_box", "svg")])
        self.assertEqual(found(svg("<rect width='1' height='1'/>", "1 0 85 44")), [("picture_view_box", "svg")])
        self.assertEqual(found(svg("<rect width='1' height='1'/>", "0 0 85.05 44")), [])
        self.assertEqual(found(b'<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'), [("picture_view_box", "svg")])


class EachRuleRefusesByElementTest(unittest.TestCase):
    def test_bytes_that_are_no_svg_are_refused(self):
        for data in (b"\xff\xfe not utf-8", b"<svg", b'<svg xmlns="http://example.org/other" viewBox="0 0 85 44"/>',
                     b'<html viewBox="0 0 85 44"/>'):
            with self.subTest(data=data):
                self.assertEqual([code for code, _ in found(data)], ["picture_not_svg"])

    def test_a_doctype_or_an_entity_is_refused_before_parsing(self):
        for head in ('<!DOCTYPE svg>', '<!DOCTYPE svg [<!ENTITY a "aaaa">]>'):
            with self.subTest(head=head):
                self.assertEqual(found(head.encode() + svg("<rect/>")), [("picture_not_svg", "svg")])

    def test_each_element_that_is_not_a_plain_shape_is_refused_by_rule_and_element(self):
        for tag in ("script", "foreignObject", "style", "use", "defs", "a"):
            with self.subTest(tag=tag):
                self.assertEqual(found(svg("<g><rect/><%s/></g>" % tag)), [("picture_element", "svg/g[0]/%s[0]" % tag)])

    def test_an_element_inside_a_title_is_refused(self):
        self.assertEqual(found(svg("<title>a<title>b</title></title>")), [("picture_element", "svg/title[0]/title[0]")])

    def test_each_attribute_that_can_load_or_run_is_refused(self):
        for inner, code in (('<rect onload="x()"/>', "picture_attribute"), ('<rect id="a"/>', "picture_attribute"),
                            ('<rect style="fill:red"/>', "picture_attribute"), ('<rect fill="url(#a)"/>', "picture_attribute"),
                            ('<rect fill="http://example.org/a"/>', "picture_attribute"),
                            ('<rect href="data:image/jpeg;base64,%s"/>' % JPEG, "picture_link"),
                            ('<image xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="data:image/jpeg;base64,%s"/>' % JPEG,
                             "picture_link"),
                            (image("http://example.org/a.jpg"), "picture_link"),
                            (image("data:image/png;base64,%s" % JPEG), "picture_link"),
                            (image("data:image/svg+xml;base64,%s" % JPEG), "picture_link"),
                            (image("data:image/jpeg;base64,%s!" % JPEG), "picture_link"),
                            (image("data:image/jpeg;base64, %s" % JPEG), "picture_link"),
                            ('<image width="1" style="a" href="data:image/jpeg;base64,%s"/>' % JPEG, "picture_attribute")):
            with self.subTest(inner=inner[:60]):
                element = "svg/%s[0]" % re.match(r"<(\w+)", inner).group(1)
                self.assertEqual(found(svg(inner)), [(code, element)])

    def test_an_href_in_any_case_or_a_name_repeated_once_lowercased_is_refused(self):
        # the review's refuter: HTML lowercases a name and keeps the first of two, so HREF="//..." loaded from the web
        jpeg = "data:image/jpeg;base64," + JPEG
        for inner, code in (('<image HREF="//example.com/x.jpg" href="%s"/>' % jpeg, "picture_attribute"),
                            ('<image href="%s" HREF="//example.com/x.jpg"/>' % jpeg, "picture_attribute"),
                            ('<image HREF="data:image/png;base64,%s"/>' % JPEG, "picture_link"),
                            ('<image HREF="%s"/>' % jpeg, "picture_link"),
                            ('<rect fill="red" FILL="blue"/>', "picture_attribute")):
            with self.subTest(inner=inner[:50]):
                element = "svg/%s[0]" % re.match(r"<(\w+)", inner).group(1)
                self.assertEqual(found(svg(inner)), [(code, element)])

    def test_an_image_with_no_href_is_refused(self):
        self.assertEqual(found(svg('<image width="1" height="1"/>')), [("picture_link", "svg/image[0]")])

    def test_a_jpeg_with_an_app1_segment_is_refused_and_the_same_without_it_passes(self):
        raw = base64.b64decode(JPEG)
        app1 = b"\xff\xe1\x00\x08Exif\x00\x00"
        with_exif = base64.b64encode(raw[:2] + app1 + raw[2:]).decode()
        self.assertEqual(found(svg(image("data:image/jpeg;base64," + with_exif))), [("picture_jpeg", "svg/image[0]")])
        self.assertEqual(found(svg(image("data:image/jpeg;base64," + JPEG))), [])

    def test_bytes_that_are_no_whole_jpeg_are_refused(self):
        raw = base64.b64decode(JPEG)
        for payload in (b"GIF89a....", raw[:20], b"\xff\xd8", b"AB\xff\xda\x00\x02"):  # the last: a scan right after two bytes that are no SOI
            with self.subTest(payload=payload[:8]):
                href = "data:image/jpeg;base64," + base64.b64encode(payload).decode()
                self.assertEqual(found(svg(image(href))), [("picture_jpeg", "svg/image[0]")])

    def test_the_link_rule_reads_the_attribute_so_http_by_chance_in_base64_passes(self):
        raw = base64.b64decode(JPEG)
        chance = base64.b64encode(raw + b"\x00" * (-len(raw) % 3) + base64.b64decode("http")).decode()
        self.assertIn("http", chance)
        self.assertEqual(found(svg(image("data:image/jpeg;base64," + chance))), [])
        self.assertEqual(found(svg("<text>see http://example.org</text>")), [("picture_link", "svg/text[0]")])

    def test_the_size_caps(self):
        filler = "<!--%s-->"
        under = svg(filler % ("a" * (250000 - 200)))
        over = svg(filler % ("a" * 250000))
        self.assertEqual(found(under), [])
        self.assertEqual(found(over), [("picture_too_big", "svg")])
        with_image = svg(image("data:image/jpeg;base64," + JPEG) + filler % ("a" * 300000))
        self.assertEqual(found(with_image), [])
        self.assertEqual(found(svg(image("data:image/jpeg;base64," + JPEG) + filler % ("a" * 400000))),
                         [("picture_too_big", "svg")])

    def test_the_frame_s_guide_left_in_is_refused(self):
        self.assertEqual(found(svg('<g data-guide="pads"><circle r="1"/></g>')), [("picture_guide_left", "svg/g[0]")])

    def test_a_text_that_is_a_pad_label_is_refused_and_another_word_passes(self):
        self.assertEqual(found(svg("<text>D/C</text><text>Busy</text>")),
                         [("picture_pad_label", "svg/text[0]"), ("picture_pad_label", "svg/text[1]")])
        self.assertEqual(found(svg("<text>2.9 inch e-paper</text>")), [])

    def test_two_problems_are_both_named(self):
        self.assertEqual(found(svg("<script/><rect id='a'/>")), [("picture_element", "svg/script[0]"),
                                                                ("picture_attribute", "svg/rect[0]")])

    def test_every_refusal_code_is_in_the_codes_table_with_a_sentence(self):
        codes = {"picture_not_svg", "picture_view_box", "picture_element", "picture_attribute", "picture_link",
                 "picture_jpeg", "picture_guide_left", "picture_pad_label", "picture_too_big"}
        self.assertEqual(set(breadboard_codes.PICTURE_CODES), codes)
        self.assertTrue(all(breadboard_codes.PICTURE_CODES[code] for code in codes))

    def test_the_embedded_jpeg_rule_is_the_one_the_page_reads(self):
        self.assertTrue(is_embedded_jpeg("data:image/jpeg;base64," + JPEG))
        for value in (None, "", "data:image/jpeg;base64,", "data:image/jpeg;base64,abc", "DATA:image/jpeg;base64," + JPEG,
                      " data:image/jpeg;base64," + JPEG):
            with self.subTest(value=value):
                self.assertFalse(is_embedded_jpeg(value))


if __name__ == "__main__":
    unittest.main()
