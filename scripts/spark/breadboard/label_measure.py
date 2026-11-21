"""
The room a label takes on the drawn breadboard as one view draws it (P969, #1388): the Strategy `LabelMeasure` and
`PxLabelMeasure`, the SVG's. The scene maker (`breadboard_scene`) places every pill, caption and pad label through it,
and the board's marks (`board_marks`) set each mark's baseline through it, so both read one measure and neither
imports the other's module. A *drop* is how far a text's baseline lies below the middle of its letters; a *baseline*
is an absolute y. Nothing here draws.
"""


class LabelMeasure:
    """Strategy: the room a label takes on the drawn breadboard as one view draws it, in the scene's px, so that the
    maker places every pill, caption and pad label for that view: `pill(words)` gives (width, height) of a wire's pill
    with these words, along its words and across them; `caption(words)` gives (size, width) of a part's caption, its
    height and its width; `pad_label()` gives (gap, drop) of a pad's label: the room between the pad and the near end
    of its words, along them, and its drop, across them; `mark_drop(size)` gives the drop of a board's mark of that
    size."""

    def pill(self, words):
        raise NotImplementedError

    def caption(self, words):
        raise NotImplementedError

    def pad_label(self):
        raise NotImplementedError

    def mark_drop(self, size):
        raise NotImplementedError


class PxLabelMeasure(LabelMeasure):
    """Strategy: the labels as the SVG draws them, in its px: a pill PILL_HEIGHT high, with DISC_ROOM for the white
    disc with its number, END_ROOM after its words, and PER_CHARACTER a character of its words (6.1 px bold); a
    caption at the palette's `caption_size`, CAPTION_PER_CHARACTER of it a character plus CAPTION_ROOM of it; a pad's
    label PAD_GAP from its pad, with a drop of PAD_DROP; a board's mark with a drop of MARK_DROP of its size."""

    #: The pill's height, the room its disc takes, the room after its words, and the width a character of its words takes,
    #: in px: the old page's at spark's pitch (the visual spec, section 7, P953).
    PILL_HEIGHT, DISC_ROOM, END_ROOM, PER_CHARACTER = 9.6, 9.6, 3.6, 3.57
    #: The width a character of a caption takes, and the room added to its words' width, each times its size. Chrome
    #: draws the fixtures' names 0.50 to 0.54 of the size a character wide.
    CAPTION_PER_CHARACTER, CAPTION_ROOM = 0.55, 0.5
    #: The room between a pad and its label, and the label's drop, in px.
    PAD_GAP, PAD_DROP = 5, 2
    #: The drop of a board's letter, number or sign, times its size.
    MARK_DROP = 0.35

    def __init__(self, caption_size):
        self.caption_size = caption_size

    def pill(self, words):
        return self.DISC_ROOM + self.END_ROOM + self.PER_CHARACTER * len(words), self.PILL_HEIGHT

    def caption(self, words):
        return self.caption_size, (self.CAPTION_PER_CHARACTER * len(words) + self.CAPTION_ROOM) * self.caption_size

    def pad_label(self):
        return self.PAD_GAP, self.PAD_DROP

    def mark_drop(self, size):
        return size * self.MARK_DROP
