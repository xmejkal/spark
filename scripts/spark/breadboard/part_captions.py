"""
Each drawn part's words on the breadboard picture outside its body (P953, #1359): its caption, the human name from its
record (`PartCaption`, `Caption`), and its line of the note under the picture (`PartNotes`). The scene maker
(`breadboard_scene`) places the captions after the wires and their pills, and `svg_diagram` draws them; nothing here
draws.
"""

import collections

from spark.breadboard.spacing import BodyBox


class Caption(collections.namedtuple("Caption", "words named x y size width")):
    """Value: one part's caption (P953): its words, `named` when they are the record's name (else an id, drawn muted),
    the start of its baseline (x, y), its font size and its width in px, as the view's label measure gives them (P969)."""

    #: The reach of the letters above and below the baseline, each times the size.
    ASCENT, DESCENT = 0.75, 0.25

    def box(self):
        return BodyBox(self.x, self.y - self.ASCENT * self.size, self.x + self.width, self.y + self.DESCENT * self.size)


class PartCaption:
    """
    Service: places each part's caption (P953), its human name outside its body, for the scene maker: the record's `name` up to its first
    comma, else the record's id, else the part's own id. It lies GAP px above the body, left-aligned with it; below the
    body when anything it must keep clear of is in that box: a body, a printed letter, number or rail sign, a wire, an
    end dot, a pill or a caption placed before it, by CLEAR px. When both are taken, it moves out a pitch at a time
    above and below, still at the body's left edge, up to FARTHEST pitches, so it stays by its own body and is never
    read as a pill's words (the review of PR #1379); only then do the same tries slide right a pitch at a time along
    the body. With no free place at all, the caption sits above its body, left-aligned. The canvas holds it wherever
    it lies.
    """

    #: The space between a caption and its body, and the space it keeps from everything else, in px; its font weight.
    GAP, CLEAR, WEIGHT = 4.8, 1.0, "600"
    #: The most pitches a caption moves out from its body's edge: 9 lifts the walk's board caption over the top rails
    #: and the wires that leave its pads.
    FARTHEST = 9

    def __init__(self, measure, pitch):
        """`measure` (a LabelMeasure) gives each caption's size and width; `pitch` is the board's, in px."""
        self.measure, self.pitch = measure, pitch

    @staticmethod
    def words(part):
        """(the caption's words, True when they are the record's name)."""
        record = part.record if isinstance(part.record, dict) else {}
        name = record.get("name").split(",")[0].strip() if isinstance(record.get("name"), str) else ""
        return (name, True) if name else (record.get("id") or part.id, False)

    def place(self, parts, bodies, taken):
        """{part id: Caption} of `parts`, in order, their BodyBoxes `bodies`; `taken` lists the BodyBoxes a caption keeps
        clear of, each placed caption's added."""
        taken, captions = list(taken), {}
        for part, body in zip(parts, bodies):
            words, named = self.words(part)
            size, width = self.measure.caption(words)
            caption = Caption(words, named, body.left, body.top - self.GAP - Caption.DESCENT * size, size, width)
            below = body.bottom + self.GAP + Caption.ASCENT * size
            tries = [caption._replace(x=body.left + step * self.pitch, y=y + side * away * self.pitch)
                     for step in range(int((body.right - body.left) // self.pitch) + 1) for away in range(self.FARTHEST + 1)
                     for side, y in ((-1, caption.y), (1, below))]
            captions[part.id] = next((one for one in tries if not any(one.box().meets(box, self.CLEAR) for box in taken)),
                                     caption)
            taken.append(captions[part.id].box())
        return captions


class PartNotes:
    """Renderer helper: the note under the picture (P953), one line for each part that has a fact not verified: its
    caption's words, then the `words` of each such group of its part_px, "DFRobot FireBeetle 2 ESP32-C6: pads, row side
    and USB end not verified.", then its picture's own note (P946). It follows the caption's rule: a record id only
    where the record has no name."""

    @staticmethod
    def lines(layout, pictures):
        lines = []
        for part in layout.parts:
            words = [note["words"] for note in layout.geometry.part(part.type).get("notes", [])]
            said = ["%s: %s not verified." % (PartCaption.words(part)[0], _listed(words))] if words else []
            said += [pictures[part.id].note] if pictures[part.id].note else []
            if said:
                lines.append(" ".join(said))
        return lines


def _listed(words):
    """"a", "a and b", "a, b and c"."""
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]
