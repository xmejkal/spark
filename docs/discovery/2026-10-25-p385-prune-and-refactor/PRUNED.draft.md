# PRUNED (draft)

This is a draft of the file `PRUNED.md`, which lands at the repository root with the prune PR, after the PO answers
lesson 1. It lists each verdict "prune" and "move behind a module" of the [pruning list](pruning-list.md#the-verdicts).

Every entry names what goes, why, what keeps it, and the command that brings it back. The tag
`pre-refactor-2026-10-25` (commit `d064a65`) keeps every file below. A restore command puts the files back in the working
tree. It changes nothing else.

## tools/match_eval.py (prune)

- Goes: `tools/match_eval.py` (115 lines), `tests/test_match_eval.py` (102 lines) and the five flags of the tool.
  The prune PR also drops the mention in the docstring of `scripts/matching.py` and in a comment of `scripts/needs.py`.
- Why: No page names it and nothing imports it. A docstring, a comment and the P211 papers only mention it.
- Kept by: the tag `pre-refactor-2026-10-25`.
- Back: `git checkout pre-refactor-2026-10-25 -- tools/match_eval.py tests/test_match_eval.py`. Bring it back when
  someone tunes a second matcher. The tool reads its cases from `tests/matching/` (27 files), which the verdict does not
  name. The prune PR decides about them. When they go, add `tests/matching` to the command.

## scripts/check_bom.py (move behind a module)

- Moves: `scripts/check_bom.py` (185 lines) and `tests/test_check_bom.py` (187 lines). It is the order check of a fab
  package, the class `TheOrder` in `scripts/check_all.py`.
- Why: Only `check_all` imports it, and no fab package exists yet.
- Kept by: the plug-in point `check_all.CHECKS`, a list of check instances. Step one is the marker
  `# --- Later, not MVP: the PCB order, P136 ---` over the module, its test and its row. Nothing leaves yet. Step two,
  a card, moves `TheOrder` into one module that `CHECKS` reads. The tag keeps the version before both steps.
- Back: `git checkout pre-refactor-2026-10-25 -- scripts/check_bom.py tests/test_check_bom.py`, then add
  `TheOrder("the-order", ["package"], ...)` to `CHECKS` again.

## scripts/check_footprints.py (move behind a module)

- Moves: `scripts/check_footprints.py` (570 lines) and `tests/test_check_footprints.py` (573 lines). It is the
  "will this board be buildable" check, the class `Buildability` in `scripts/check_all.py`.
- Why: It asks a PCB question, and `check_all` and `check_physics` import it. The build does not.
- Kept by: the plug-in point `check_all.CHECKS`, with the same two steps as `check_bom.py`.
- Back: `git checkout pre-refactor-2026-10-25 -- scripts/check_footprints.py tests/test_check_footprints.py`, then add
  `Buildability("buildability", ["circuit"], ...)` to `CHECKS` again. Restore it together with `check_physics.py`,
  which imports it.

## scripts/check_physics.py (move behind a module)

- Moves: `scripts/check_physics.py` (662 lines) and `tests/test_check_physics.py` (728 lines). It is the physics check
  of a PCB, the class `Physics` in `scripts/check_all.py`.
- Why: Only `check_all` imports it. It grades a board for the PCB order of P136, not the breadboard journey.
- Kept by: the plug-in point `check_all.CHECKS`, with the same two steps as `check_bom.py`.
- Back: `git checkout pre-refactor-2026-10-25 -- scripts/check_physics.py tests/test_check_physics.py`, then add
  `Physics("physics", ["circuit", "rules"], ...)` to `CHECKS` again. The module needs `scripts/check_footprints.py`, `scripts/copper.py` and `scripts/netlist.py`. The last two stay with the
  build, so they are always there.

## Not decided yet

- The 19 flags that no page names (group (b) of the pruning list). The rule: a flag that a test or a script passes gets
  a line on its script's page, and a flag that nothing passes goes. The prune PR applies the rule and lists each flag
  that goes here, with the same four parts.
- The later spans of the pruning list (for example `REQUIRED_FOR_FAB` in `scripts/boards.py`). They stay in place under
  the marker `# --- Later, not MVP: <why kept> ---`. Nothing leaves, so they need no restore command.
