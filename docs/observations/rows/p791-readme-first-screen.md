# P791: the README's first screen shows the animated wiring guide: rows

Card: [P791 #1098](https://github.com/xmejkal/spark/issues/1098), the PO's ask of 2026-11-12 ("update the README to show the
artifact ... an animated gif if its nice"). No plan: a docs change with a docs tool. PR review: the documentation lens on
Sonnet and the refuter on Fable, one round. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the caption says "drawn from spark's records", but the page draws the microphone and the encoder from bench photos ("from your photos where they do not") | refuter, lens | acted | "spark's records and the bench photos drew it" |
| 2 | "its breadboard sheet" overclaims: the page names the sheet for the encoder's wires only (its sources, "spark's breadboard sheet for P758") | lens | acted | "and, for the encoder's wires, its breadboard sheet" |
| 3 | "the board's dimension drawing" is DFRobot's, read through spark's board record | lens | acted | "the board's record (from DFRobot's dimension drawing)" |
| 4 | "every part is to one scale" hides that the encoder's size is estimated from a photo (page: "about 15 x 32 mm, estimated") | lens | acted | "and the encoder's size is estimated from a photo" |
| 5 | the GIF links to the page's HTML source on GitHub, 2,449 lines, not the animation; neither repository has GitHub Pages | lens, refuter | acted | the GIF links to the pixel-games repository; the caption names the page and says GitHub shows its source; Pages or a shared artifact is the PO's call, on the card |
| 6 | the buttons in the picture invite a click that does nothing | lens | acted | "The buttons in the picture work only there." |
| 7 | the first screen never says what the GIF is, and "pixel-games" has no gloss | lens | acted | "small arcade games on an ESP32-S3 with a display, a speaker and a knob" |
| 8 | the alt text omits the speaker and the display | lens | acted | both named |
| 9 | the recorder's palette comes from frame 0, which holds the fewest colours | lens | acted | the palette comes from the last frame, with its comment |
| 10 | the recorder prints its shots (105) as frames, but the file holds 91 after Pillow merges the identical rest | refuter | acted | it reports `n_frames` of the file |
| 11 | `Image.Quantize.MEDIANCUT` and `Image.Dither.NONE` need Pillow 9.1 or later; `device_scale_factor=1` is the default | lens | acted | the docstring names 9.1; the argument is gone |
| 12 | "the agents of `spark-review`, the `spark-design` and ... skills" reads as if the skills belong to the agents | refuter | acted | "and the" restored |
| 13 | the line that points to *What it is* and *What works today* points away from the first screen | lens | rejected | it stays: the caption now says what the picture is, and the pointer is the one line a stranger needs to find the two sections the PO asked for |
| 14 | a Miro picture on the first screen, as the PO's "maybe" asked | the PO | raised | the board's composer SVG is a layout, not a drawing, and the Miro screenshot timed out three times; on the card for the PO (a screenshot of his, or a Miro export) |
