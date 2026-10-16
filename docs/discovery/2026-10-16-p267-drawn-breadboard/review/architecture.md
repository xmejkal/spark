# PR #303 architecture, names and docs lens (Sonnet), 2026-10-16

Plan mode was on, so the lens wrote nothing and could not run `git diff`. It read the branch's files.

- A1: the planner decides "jumper or leg" from `act` and `end.kind`, a second copy of the rule in `move()` and
  `RowAnchor.setup()`. Fix: `Seated` says it, set in `anchored()`.
- A2: `_describe_parts` sits in the sheet module and reads `geometry.data` past `part()`; the literal "silkscreen";
  `BOARD_COMPONENT` defined twice ("Mcu" and "board"); `ROW_HOLES` a second source beside the geometry. Fix: a
  `WokwiPartCatalog` in `breadboard_drawing.py`, `PIN_NAMING_SILKSCREEN`, one constant.
- A3: the layout is Wokwi-shaped (type, attrs, px), so P268's own pictures need more than a second renderer. The
  file-views table of the plan is missing. Fix: a `DRAWING_VIEWS` table; `write()`, `Written` and `keep_breadboard`
  loop over it.
- A4: the sheet builds its own `StepColors`. Fix: one instance.
- A5: `place` finds and claims in one loop; `free_hole` and `free_row` claim. Fix: split find and claim, rename.
- Names: `FILE` and `GEOMETRY` are vague; several functions start with no verb; the loop variable `one` names steps,
  holes and ends; say "Renderer" in `WokwiBreadboardDiagram`'s docstring.
- Changes from the plan: one data file, a turn search in place of a straddle rule, any rail not drawn. List them
  in the PR.
- Docs: the README, `commands/build.md` and the journey guide omit the rail limit; a semicolon in `commands/build.md`.
