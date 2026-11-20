"""
Each drawn part's words on the breadboard picture outside its body (P953, #1359): its caption, the human name from its
record (`PartCaption`, `Caption`), and its line of the note under the picture (`PartNotes`). `svg_diagram`'s renderer
places them after the wires and their pills and draws them; nothing here draws.
"""

import collections

from spark.breadboard.spacing import BodyBox


class Caption(collections.namedtuple("Caption", "words named x y size")):
    """Value: one part's caption (P953): its words, `named` when they are the record's name (else an id, drawn muted),
    the start of its baseline (x, y) and its font size in px."""

    #: The width a character takes, the room added to the words' width, and the reach of the letters above and below
    #: the baseline, each times the size. Chrome draws the fixtures' names 0.50 to 0.54 of the size a character wide.
    PER_CHARACTER, ROOM, ASCENT, DESCENT = 0.55, 0.5, 0.75, 0.25

    def box(self):
        return BodyBox(self.x, self.y - self.ASCENT * self.size,
                       self.x + (self.PER_CHARACTER * len(self.words) + self.ROOM) * self.size,
                       self.y + self.DESCENT * self.size)


class PartCaption:
    """
    Renderer helper: each part's caption (P953), its human name outside its body: the record's `name` up to its first
    comma, else the record's id, else the part's own id. It lies GAP px above the body, left-aligned with it; below the
    body when anything it must keep clear of is in that box: a body, a printed letter, number or rail sign, a wire, an
    end dot, a pill or a caption placed before it, by CLEAR px. When both are taken, the two lines slide right a pitch
    at a time along the body, then move a pitch further out, up to FARTHEST pitches; with no free place at all, the
    caption sits above its body, left-aligned.
    """

    #: The space between a caption and its body, and the space it keeps from everything else, in px; its font weight.
    GAP, CLEAR, WEIGHT = 4.8, 1.0, "600"
    #: The most pitches a caption moves out from its body's edge.
    FARTHEST = 6

    def __init__(self, size, pitch):
        self.size, self.pitch = size, pitch

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
            caption = Caption(words, named, body.left, body.top - self.GAP - Caption.DESCENT * self.size, self.size)
            below = body.bottom + self.GAP + Caption.ASCENT * self.size
            tries = [caption._replace(x=body.left + step * self.pitch, y=y + side * away * self.pitch)
                     for away in range(self.FARTHEST + 1) for step in range(int((body.right - body.left) // self.pitch) + 1)
                     for side, y in ((-1, caption.y), (1, below))]
            captions[part.id] = next((one for one in tries if not any(one.box().meets(box, self.CLEAR) for box in taken)),
                                     caption)
            taken.append(captions[part.id].box())
        return captions


class PartNotes:
    """Renderer helper: the note under the picture (P953), one line for each part that has a fact not verified: its
    caption's words, then the `words` of each such group of its part_px, "DFRobot FireBeetle 2 ESP32-C6: pads, row side
    and USB end not verified.", then its picture's own note (P946). It names no record id where the record has a name."""

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
