#!/usr/bin/env python3
"""
Draw the journey picture on the README's front page (P226): eight steps, what you do, what you get, and how far each
works today. Each step's status comes from the README's "What works today" table, so a status changes there first.

    python3 tools/journey.py    # writes docs/guide/journey.svg; tests/test_journey.py fails while it is stale

The same picture is on the Miro board https://miro.com/app/board/uXjVEavQ4JQ=/ ; change it there in the same PR.
"""

import re
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
PICTURE = "docs/guide/journey.svg"
#: The strip at the bottom: where we are, and what is next. Each line holds at most STRIP characters.
WHERE = "the button-and-LED firmware read ready seen on a XIAO ESP32-C6 on 2026-10-15."
NEXT = "wire its breadboard and press the button."
STRIP = 100
#: Each step: its name in the README's table, its command, what you do, what you get, a note on how far it works, and
#: the status that note was written for. A step whose status changes in the table needs a new note here.
STEPS = [
    ("Drawer", "/spark:drawer", "Say which parts you own.", "Your drawer, kept in your own store.",
     "Listing and writing entries ran. Your words to entries, and the DFRobot import, did not.", "partly"),
    ("Idea", "/spark:idea", "Describe the gadget in your own words.",
     "Needs matched to your drawer, a part per need, and a requirements file.",
     "The scripts ran from needs to a requirements file. The conversation was not run.", "partly"),
    ("Research", "/spark:research", "Pick a part for a real gap.", "A part record with a source for every fact.",
     "The library search runs. Research by agents was not run.", "partly"),
    ("Build", "/spark:build", "Run it on the requirements file.",
     "A board that builds, a Wokwi diagram, a breadboard sheet and its drawing.",
     "Ran end to end on 2026-10-11. The drawing is on the XIAO C6 only, since 2026-10-16.", "works"),
    ("Checks", "check_all.py", "Run the checks on the project.", "What holds, and what a check could not look at.",
     "A fresh button-and-LED project passes.", "works"),
    ("Firmware", "import_firmware.py", "Write the firmware with Claude.", "A pin map that the firmware imports.",
     "The import passes on a Mac. No check yet that it drives every signal.", "partly"),
    ("Simulate", "run_scenario.py", "Say in words what must happen.",
     "The firmware running in Wokwi, with a dated log.", "The button-and-LED project passed on 2026-10-12.", "works"),
    ("Bench", "look.py, deploy.py", "Wire the breadboard and flash the board.", "The tested firmware on the real board.",
     "look.py reads the board on USB and checks it. deploy.py asks your yes first. It flashed a XIAO ESP32-C6 and read ready. No wired breadboard yet.", "partly"),
]
#: Each status: the stop's fill, the label's fill, the label's text color, and its line in the legend.
COLORS = {"works": ("#2dc75c", "#adf0c7", "#067429", "works: it ran end to end for the docs"),
          "partly": ("#ffdc4a", "#fff6b6", "#af7e04", "partly: it stops before its goal, or part of it was not run"),
          "not yet": ("#ff6464", "#ffc6c6", "#bd0a0a", "not yet: nothing does it yet")}
INK, BODY, ROAD, CARD, LABEL = "#1a1a1a", "#595959", "#b0b0b0", "#f0f5fd", "#305bab"
FONT = "&apos;Noto Sans&apos;, &apos;Helvetica Neue&apos;, Helvetica, Arial, sans-serif"
#: The canvas width, its margin, a card's width, the gap between cards, characters per line, and the line height.
W, PAD, COLW, GAP, WRAP, LINE = 1600, 48, 358, 24, 27, 34


def section(readme):
    """The README's "What works today" section, whose table holds each step's status; empty when it has none."""
    return readme.partition("\n## What works today\n")[2].split("\n## ")[0]


def statuses(readme):
    """Each step's status in the "What works today" table: {"Drawer": "partly", ...}."""
    rows = re.findall(r"^\| \[(\w+)\]\(docs/guide/journey\.md#[\w-]+\) \| \*\*(works|partly|not yet)\*\*",
                      section(readme), re.M)
    return dict(rows)


def runs_up_to(readme):
    """The newest date in the "What works today" section: the last run behind its statuses."""
    return max(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", section(readme)), default="")


def svg(status, runs_up_to):
    """
    The picture as SVG text, from each step's status in the table. Exits when the table and STEPS name different
    steps, when a step's note was written for another status, or when the strip's lines are too long.
    """
    steps = [step[0] for step in STEPS]
    said = ["the README's table names no status for %s" % name for name in steps if name not in status]
    said += ["the picture has no step %s, which the README's table names" % name for name in status
             if name not in steps]
    said += ["the note for %s was written for %s, but the README's table says %s: change it in STEPS"
             % (step[0], step[5], status[step[0]]) for step in STEPS if status.get(step[0], step[5]) != step[5]]
    said += ["the strip's line is over %d characters: %s" % (STRIP, line) for line in (WHERE, NEXT)
             if len(line) > STRIP]
    if said:
        sys.exit("journey.py: " + "\njourney.py: ".join(said))
    out = []

    def text(x, y, s, size, fill=BODY, weight="normal", anchor="start"):
        out.append('<text x="%d" y="%d" font-size="%d" font-weight="%s" fill="%s" text-anchor="%s">%s</text>'
                   % (x, y, size, weight, fill, anchor, escape(s)))

    def lines(s):
        return textwrap.wrap(s, WRAP)

    n_do, n_get, n_note = (max(len(lines(step[k])) for step in STEPS) for k in (2, 3, 4))
    card_h = 20 + 20 + n_do * LINE + 44 + n_get * LINE + 30 + 36 + 6 + n_note * LINE + 24
    row_h = 40 + 36 + 16 + 30 + 32 + 22 + card_h
    rows_y = [236, 236 + row_h + 40]
    strip_y = rows_y[1] + row_h + 32
    h = strip_y + 92 + PAD

    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" font-family="%s">'
               % (W, h, W, h, FONT))
    out.append("<title>The spark journey: eight steps from an idea to a working gadget, and how far each works today"
               "</title>")
    out.append('<rect width="%d" height="%d" rx="24" fill="#ffffff"/>' % (W, h))
    text(PAD, 96, "From an idea to a working gadget", 44, INK, "bold")
    text(PAD, 140, "The spark journey, and how far each step worked in the runs up to %s." % runs_up_to, 24)
    x = PAD
    for name, (stop, _, _, legend) in COLORS.items():
        if name in status.values():
            out.append('<circle cx="%d" cy="180" r="10" fill="%s"/>' % (x + 10, stop))
            text(x + 30, 188, legend, 22)
            x += 30 + len(legend) * 11 + 52

    for row, y0 in enumerate(rows_y):
        road = y0 + 40
        cx = [PAD + i * (COLW + GAP) + COLW // 2 for i in range(4)]
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="4"/>'
                   % (cx[0], road, cx[3], road, ROAD))
        for i in range(4):
            n = row * 4 + i
            name, command, do, get, note, _ = STEPS[n]
            stop, label_fill, label_ink, _ = COLORS[status[name]]
            x = PAD + i * (COLW + GAP)
            out.append('<circle cx="%d" cy="%d" r="36" fill="%s"/>' % (cx[i], road, stop))
            text(cx[i], road + 11, str(n + 1), 30, INK, "bold", "middle")
            y = road + 36 + 16 + 30
            text(cx[i], y, name, 30, INK, "bold", "middle")
            y += 32
            text(cx[i], y, command, 22, BODY, "normal", "middle")
            top = y + 22
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s"/>' % (x, top, COLW, card_h, CARD))
            tx, y = x + 20, top + 20 + 20
            for heading, body, n_lines in (("You do", do, n_do), ("You get", get, n_get)):
                text(tx, y, heading, 20, LABEL, "bold")
                for k, part in enumerate(lines(body)):
                    text(tx, y + LINE * (k + 1), part, 24)
                y += n_lines * LINE + 44
            y -= 14
            out.append('<rect x="%d" y="%d" width="96" height="36" rx="18" fill="%s"/>' % (tx, y, label_fill))
            text(tx + 48, y + 25, status[name], 20, label_ink, "bold", "middle")
            y += 36 + 6
            for k, part in enumerate(lines(note)):
                text(tx, y + LINE * (k + 1) - 6, part, 24)

    out.append('<rect x="%d" y="%d" width="%d" height="92" rx="12" fill="%s"/>' % (PAD, strip_y, W - 2 * PAD, INK))
    out.append('<text x="%d" y="%d" font-size="24" fill="#ffffff"><tspan font-weight="bold">Where we are:</tspan> %s'
               '</text>' % (PAD + 24, strip_y + 38, escape(WHERE)))
    out.append('<text x="%d" y="%d" font-size="24" fill="#ffffff"><tspan font-weight="bold">Next:</tspan> %s</text>'
               % (PAD + 24, strip_y + 72, escape(NEXT)))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    readme = (ROOT / "README.md").read_text()
    (ROOT / PICTURE).write_text(svg(statuses(readme), runs_up_to(readme)))
    print("wrote %s" % PICTURE)


if __name__ == "__main__":
    main()
