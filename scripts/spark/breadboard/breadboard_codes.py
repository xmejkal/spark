"""
The reasons `sheet.write` writes no sheet, each a code with one sentence (P692, W6-B2), and the rules a part's picture
breaks (P946, `PICTURE_CODES`), all in `CODES`.

A leaf: it imports nothing of spark. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). A NotBuiltError carries its code, and `sheet.refusal_code` gives the code of each error
`main` catches. breadboard.py has no `--json`, so the codes wait in the library for the Operation that comes later. A
drawing not written has its own codes, in drawing.CODES.

STORE_PROBLEM is also board_codes', as an equal literal in two leaves, with the same meaning.
"""


# --- MVP ---
#: NotBuiltError: the built circuit is missing, stale, failed or cannot be read. Each asks to build again, but a failed
#: build first asks to fix what failed.
NOT_BUILT, BUILT_FROM_OTHER_REQUIREMENTS = "not_built", "built_from_other_requirements"
BUILD_FAILED, BUILD_UNREADABLE = "build_failed", "build_unreadable"
#: The errors from outside that main catches: each asks for another fix.
REQUIREMENTS_UNUSABLE, STORE_PROBLEM, FILE_UNUSABLE = "requirements_unusable", "store_problem", "file_unusable"

#: Each code and the one sentence that says what it means.
CODES = {
    NOT_BUILT: "nothing is built yet, or the build did not finish, so there is no circuit to wire",
    BUILT_FROM_OTHER_REQUIREMENTS: "the built circuit was built from other requirements than the file names now",
    BUILD_FAILED: "the last build failed, so its circuit is not a board to wire",
    BUILD_UNREADABLE: "the built circuit, or the record of what it was built from, cannot be read",
    REQUIREMENTS_UNUSABLE: "the requirements file cannot be loaded as a design: a part, a board or a field is wrong",
    STORE_PROBLEM: "spark's store cannot be read or written",
    FILE_UNUSABLE: "a file the sheet reads or writes cannot be opened: its path, its folder or its permissions",
}

#: The rules a part's picture breaks (P946, `picture_check.PictureCheck`): a picture that breaks one is not kept, and a
#: kept one that breaks one is not drawn.
PICTURE_NOT_SVG, PICTURE_VIEW_BOX, PICTURE_ELEMENT = "picture_not_svg", "picture_view_box", "picture_element"
PICTURE_ATTRIBUTE, PICTURE_LINK, PICTURE_JPEG = "picture_attribute", "picture_link", "picture_jpeg"
PICTURE_GUIDE_LEFT, PICTURE_PAD_LABEL, PICTURE_TOO_BIG = "picture_guide_left", "picture_pad_label", "picture_too_big"
#: Each picture rule's code and the one sentence that says what it means.
PICTURE_CODES = {
    PICTURE_NOT_SVG: "the picture is no SVG: its bytes are no UTF-8, do not parse, hold a DOCTYPE or an entity, or its root is no svg",
    PICTURE_VIEW_BOX: "the picture's viewBox is not 0 0 W H with W and H the part's frame size in mm, within 0.1 mm",
    PICTURE_ELEMENT: "an element is no plain shape and no image, or stands inside a title",
    PICTURE_ATTRIBUTE: "an attribute is not one a picture holds, or its value can load or run something (url(, http and the like)",
    PICTURE_LINK: "a link that is not a JPEG embedded as base64 on an image, or a text that holds a web address",
    PICTURE_JPEG: "an embedded JPEG is no whole JPEG, or holds an APP1 segment (EXIF, which can say where a photo was taken)",
    PICTURE_GUIDE_LEFT: "the frame's guide group (data-guide) is left in: the pads are spark's to draw",
    PICTURE_PAD_LABEL: "a text is a pad's printed label: spark draws the labels over the picture",
    PICTURE_TOO_BIG: "the picture is over 250000 bytes with no embedded JPEG, or over 400000 with one",
}
CODES.update(PICTURE_CODES)  # one table of the area's codes: the sheet's refusals and the picture rules

#: The rules a part's measured features break (P956, `feature_check.FeatureCheck`): features that break one are not
#: written, and written ones that break one are not drawn.
FEATURE_OUTSIDE, FEATURE_OVER_PAD, FEATURE_OFF_DRAWING = "feature_outside", "feature_over_pad", "feature_off_drawing"
FEATURE_NO_ANCHOR, FEATURE_PAD_LABEL, FEATURE_UNREADABLE = "feature_no_anchor", "feature_pad_label", "feature_unreadable"
#: Each feature rule's code and the one sentence that says what it means.
FEATURE_CODES = {
    FEATURE_OUTSIDE: "a feature's box lies more than 0.5 mm outside the part's outline (a USB socket may hang 2 mm past the USB edge)",
    FEATURE_OVER_PAD: "a feature's box covers part of a pad: spark draws the pads, and a part there would hide one",
    FEATURE_OFF_DRAWING: "an anchor or a mounting hole lies more than 0.5 mm from where the record's dimension drawing puts it, or a hole is not round or not the record's diameter",
    FEATURE_NO_ANCHOR: "fewer than two anchors at pads half the board apart, or an anchor that names no pad: nothing proves the turn and the scale",
    FEATURE_PAD_LABEL: "a label's text is a pad's printed label, which spark draws, or holds a web address (http or www.)",
    FEATURE_UNREADABLE: "the features file cannot be read: no JSON, a field missing, or a picture document the record does not hold",
}
CODES.update(FEATURE_CODES)  # the measured features' rules too (P956)
# --- end MVP ---
