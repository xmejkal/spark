# P948: how spark's wiring view gets as nice as the praised pages: the finding

Card: [P948 #1352](https://github.com/xmejkal/spark/issues/1352), a council analysis under P734
[#1005](https://github.com/xmejkal/spark/issues/1005). The council met on 2026-11-20, from 12:12 to 12:29 Prague. The
PO read the finding and ordered the stories. This file keeps the finding from the card's comments.

## The answer

> Python keeps the facts, the planner and the one renderer. Each part keeps one plain SVG picture in the person's
> store. A small TypeScript player only plays the steps in the page. The first wave starts with P947: one lane per
> jumper, printed labels in the steps and wires coloured by role.

- Python keeps the facts, the planner and the one renderer. The page, `breadboard.svg` and `breadboard.md` all show
  the same picture.
- A small TypeScript player (`tools/flow-page/`, no dependencies) only plays the steps in the page. Its built file is
  committed with a sha256 pin, as `tools/circuit-to-wokwi/` is. The player draws no shape and holds no word.
- Each part keeps one plain SVG picture in mm in the person's store (`pictures.breadboard`). The conversation draws
  it inside a frame that spark prints from the record. It draws from photos, a maker's drawing or a listing.
- `PictureCheck` checks the picture's structure: the frame size, plain shapes, every pad marked and a size cap. The
  look is judged by eye: first the conversation's eye, then the PO's. Spark has no renderer that compares a picture
  with a photo by itself.

## The PO's words

Just before 12:13 Prague, while the council ran:

```text
Like really we want it at least as good and nice as it was, later we can even go further, make it even more interactive and good looking, etc.
```

Just before 12:15 Prague, while the council ran:

```text
And really, ltes think about how to make it reusable, so we can use it n the artfact, but also it works standalone, maybe only some parts, maybe not interactive, but the comonennts store their pretty images, spark knows how to reate them from the web, datasheets, photos, etc, it makes sure t all is well made, stores it, etc.
```

What the council took from them:

- The bar for the first cut is the praised pages. The next level (more interactive, better looking) comes later, and
  the design leaves room for it.
- One set of reusable components works in the Artifact and standalone: a plain page or an SVG file, maybe only some
  parts, maybe not interactive.
- Each part stores its own pretty picture. Spark knows how to make that picture from the web, datasheets and photos.
  It checks that the picture is well made, and it stores it.

## The council

Three lenses on Opus looked at reuse, the options and the architecture. The architect agent (the best model) wrote
the synthesis. The refuter (the best model) tried to prove it wrong. The verdict: sound with changes.

## What can be reused

- The praised pages came from two scripts that sessions wrote. `draw.py` came from session 55108c99, in 17 versions
  written by heredoc (the first was 9,204 bytes). `build.py` came from agent ada6433322fbce0e3, in two writes. Both can
  be recovered from the transcripts. pixel-games is MIT.
- The wire style of the praised page is in pixel-games, `docs/wiring.html`, lines 2158 to 2165. Each wire is drawn
  twice: first a white under-stroke 7.5 wide, then the colour 4 wide, both with round joins, and a dot at each end.
  The page's wire table is at line 1097 of the same file.

## The options

- No open library covers the PO's parts.
- Fritzing core (https://github.com/fritzing/fritzing-parts, CC BY-SA) holds 2 DFRobot parts and no ESP32-S3. Its parts
  could go into the store only, in wave 2.
- wokwi-elements (https://github.com/wokwi/wokwi-elements, MIT) has no FireBeetle, no e-paper and no breadboard.
- The view needs no library: plain SVG and the Web Animations API, as on the praised page.

## The PO's choices

His answers to four questions, just before 12:29 Prague:

- "By role": the wires are red for 3V3, black for GND and other colours for signals. The step number stays on the
  wire.
- "P947, page look, P946": wave 1 goes in that order.
- "Recover and rescale": the FireBeetle's picture comes from the recovered `draw.py`, moved to mm and kept in his
  store.
- "All at once, then steps": the guide draws all the wires when it comes into view. Step by step is one click away.

## The stories

Wave 1, in order:

1. P947 [#1351](https://github.com/xmejkal/spark/issues/1351): lanes, printed labels, the wire style by role.
2. P949: the page's look: inline SVG, CSS tokens, a legend.
3. P946 [#1349](https://github.com/xmejkal/spark/issues/1349): kept pictures. The e-paper is drawn from photos. The
   FireBeetle, the DFR0664 and the encoder are recovered.
4. P888 [#1258](https://github.com/xmejkal/spark/issues/1258), then P887
   [#1257](https://github.com/xmejkal/spark/issues/1257): the player, the guide first.
5. P889 [#1259](https://github.com/xmejkal/spark/issues/1259): the pin table, plus the praised page's wire table with
   holes and "how to read the holes".

Wave 2 goes further: P890 [#1261](https://github.com/xmejkal/spark/issues/1261), a Fritzing import into the store with
credit, a photo crop, a page per part (front, back, dimension arrows and a facts table with sources), hover and click,
and a theme switch.

## Sources

- The card and its comments: [P948 #1352](https://github.com/xmejkal/spark/issues/1352).
- The praised page: pixel-games, `docs/wiring.html` (the wire style at lines 2158 to 2165, the wire table at line
  1097).
- The transcripts, by id only: session 55108c99 (`draw.py`) and agent ada6433322fbce0e3 (`build.py`).
- Fritzing parts: https://github.com/fritzing/fritzing-parts (CC BY-SA).
- wokwi-elements: https://github.com/wokwi/wokwi-elements (MIT).
