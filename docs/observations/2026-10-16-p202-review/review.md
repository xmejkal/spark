# P202 (#161): the plan council, the review, the refuter and the mutation run

1. Plan council, architecture and names lens (Sonnet): the numbered steps would break the point-line tests, which read
   every numbered line. Mermaid labels with parentheses need quotes. The node text must stay short. The new names
   clashed with `breadboard.Point` and the "Wiring" heading. Three guides were missing from the docs list. Acted: the
   tests read only the Points section, every label is quoted with ids `n1`, `g1`, the class is `BreadboardSteps`.
2. Plan council, refuter (Opus): "a free row" per point wires a module wrong, because a module's pins sit in fixed rows
   (the L9110S header, the 6x6 button). A header pin cannot sit in a rail. The supply had no step. Acted: each part
   goes in first, each pin in its own row, and every other end joins the row of a part's pin, or a rail by a jumper.
3. Review (Sonnet, no shell): a supply's wire did not count toward the row's holes. No step placed the board. The two
   renderers were methods of `BreadboardSteps`, so a new one meant an edit there. Some names were vague
   (`joined`, `node`, `text`, `where`). Acted on all four: `len(ends) + bool(supply)`, "Put the board in" as step 1,
   `NumberedList` and `MermaidDiagram` with one `render()`, the sheet's `WIRING_VIEWS`, and `Step.edge`, `End.name`,
   `End.words`, `Anchor.destination`. Not acted: two rail points with one name, because the circuit merges them.
4. Refuter (Opus): it could not break the wiring on any shape it built. One doc sentence was false ("every wire goes
   to the row of a part's pin"). The promised literal test of the point lines was missing. Two board pads alone were
   joined pad to pad. Acted: the sentence names the anchor, a literal test holds the motor points, and a board-pad
   anchor gets a jumper to a free row first.
5. Mutation run (Sonnet), `tools/mutate.py --copy`: 12 planted, 12 caught. Not planted: the rail-name choice and
   `MermaidDiagram.render`. Acted: a test for a rail marked by its first end; the diagram tests check one edge's ids.
