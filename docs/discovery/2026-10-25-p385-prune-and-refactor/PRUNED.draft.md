# PRUNED (draft)

This is a draft of the file `PRUNED.md`, which lands at the repository root with the prune PR, after the PO answers
Question 1 of [lessons.md](lessons.md). It lists each verdict "prune" and "move behind a module" of the
[pruning list](pruning-list.md#the-verdicts).

Every entry names what goes, every file it touches, why, what keeps it, and the command that brings it back. The tag
`pre-refactor-2026-10-25` (commit `d064a65`) keeps every file below. A restore command puts the files back in the working
tree. It changes nothing else.

The README's Checks row and the picture in `tools/journey.py` change in the same PR as the three PCB entries
(AGENTS.md's journey rule), and `tests/test_journey.py` fails on a stale picture. The team's Miro journey board follows.
The 12 mutation tables that name the three checks are `tests/mutations/p143-severity.json`, `p197-clean-check.json`,
`sprint-2.json`, `sprint-3-p13.json`, `sprint-6-p34.json`, `sprint-6-p35.json`, `sprint-6-p41.json`, `sprint-6-p42.json`,
`sprint-6-p46.json`, `sprint-8-p52.json`, `sprint-8-p54.json` and `sprint-8-p57.json` (`git grep -l` over the three
module names lists them).

## tools/match_eval.py (prune)

- Goes: `tools/match_eval.py` (115 lines), `tests/test_match_eval.py` (102 lines), the five flags of the tool and its
  cases in `tests/matching/` (`cases.json` and the folder `drawer/`, 27 files). Three more files change. The docstring
  of `scripts/matching.py` and a comment of `scripts/needs.py` drop the mention. `docs/2026-10-12-p211-matching-design.md`
  names the tool on three lines and gets a note that points at `PRUNED.md`. The pages under `docs/archive/` and
  `docs/observations/` keep their text, because they are history.
- Why: Nothing imports it. A docstring, a comment and the P211 design page only mention it.
- Kept by: the tag `pre-refactor-2026-10-25`.
- Back: `git checkout pre-refactor-2026-10-25 -- tools/match_eval.py tests/test_match_eval.py tests/matching`, then
  restore the docstring of `scripts/matching.py`, the comment of `scripts/needs.py` and the three lines of the P211
  design page from the same tag. Bring it back when someone tunes a second matcher.

## scripts/check_bom.py (move behind a module)

- Moves: `scripts/check_bom.py` (185 lines) and `tests/test_check_bom.py` (187 lines). It is the order check of a fab
  package, the class `TheOrder` in `scripts/check_all.py`. The same PR edits these files too: `scripts/check_all.py`
  (`CHECKS`), `tests/test_check_all.py`, `tests/test_outcomes.py` (its exit table names `check_bom`), `tools/snapshot.py`
  (it runs `check_bom.py`), `tests/mutations/sprint-8-p54.json`, the Checks row of `README.md`, `tools/journey.py`, the
  the-order row of `skills/spark-review/SKILL.md` and the pages `docs/guide/agents.md`, `docs/guide/developing.md`
  and `docs/guide/how-it-works.md`.
- Why: Only `check_all` imports it, and no fab package exists yet.
- Kept by: the plug-in point `check_all.CHECKS`, a list of check instances. Step one is the marker
  `# --- Later, not MVP: the PCB order, P136 ---` over the module, its test and its row. Nothing leaves yet. Step two,
  a card, moves `TheOrder` into one module that `CHECKS` reads. The tag keeps the version before both steps.
- Back: `git checkout pre-refactor-2026-10-25 -- scripts/check_bom.py tests/test_check_bom.py
  tests/mutations/sprint-8-p54.json`, then add `TheOrder("the-order", ["package"], ...)` to `CHECKS` again and restore
  the other files of the Moves line from the same tag.

## scripts/check_footprints.py (move behind a module)

- Moves: `scripts/check_footprints.py` (570 lines) and `tests/test_check_footprints.py` (573 lines). It is the
  "will this board be buildable" check, the class `Buildability` in `scripts/check_all.py`. The same PR edits these
  files too: `scripts/check_all.py` (`CHECKS`), `tests/test_check_all.py` (it imports the module and tests
  `Buildability`), `tests/test_outcomes.py`, the six mutation tables `p143-severity.json`, `sprint-2.json`,
  `sprint-3-p13.json`, `sprint-6-p42.json`, `sprint-6-p46.json` and `sprint-8-p57.json`, the Checks row of `README.md`,
  `tools/journey.py`, `skills/spark-review/SKILL.md`, the pages `docs/guide/agents.md` and `docs/guide/how-it-works.md`,
  and `scripts/check_physics.py`, which imports it. `scripts/parts.py`, `scripts/emit_board.py`,
  `scripts/emit_footprint.py`, `scripts/copper.py`, `scripts/fab.py` and `tests/test_fab.py`, `test_parts.py`,
  `test_json_contracts.py` and `test_self_confirmation.py`, `data/fabrication.json`, `agents/design-reviewer.md`,
  `GLOSSARY.md` and `DECISIONS.md` name it in text, and the PR reads each.
- Why: It asks a PCB question, and `check_all` and `check_physics` import it. The build does not.
- Kept by: the plug-in point `check_all.CHECKS`, with the same two steps as `check_bom.py`.
- Back: `git checkout pre-refactor-2026-10-25 -- scripts/check_footprints.py tests/test_check_footprints.py
  tests/mutations/p143-severity.json tests/mutations/sprint-2.json tests/mutations/sprint-3-p13.json
  tests/mutations/sprint-6-p42.json tests/mutations/sprint-6-p46.json tests/mutations/sprint-8-p57.json`, then add
  `Buildability("buildability", ["circuit"], ...)` to `CHECKS` again and restore the other files of the Moves line
  from the same tag. Restore it together with `check_physics.py`, which imports it.

## scripts/check_physics.py (move behind a module)

- Moves: `scripts/check_physics.py` (662 lines) and `tests/test_check_physics.py` (728 lines). It is the physics check
  of a PCB, the class `Physics` in `scripts/check_all.py`. The same PR edits these files too: `scripts/check_all.py`
  (`CHECKS`), `tests/test_check_all.py`, `tests/test_outcomes.py`, `tools/snapshot.py` (it runs `check_physics.py`),
  the eight mutation tables `p143-severity.json`, `p197-clean-check.json`, `sprint-3-p13.json`, `sprint-6-p34.json`,
  `sprint-6-p35.json`, `sprint-6-p41.json`, `sprint-6-p46.json` and `sprint-8-p52.json`, the Checks row of `README.md`,
  `tools/journey.py`, the physics row of `skills/spark-review/SKILL.md`, the pages `docs/guide/agents.md`,
  `docs/guide/developing.md` and `docs/guide/how-it-works.md`, and the text of `scripts/check_spine.py`,
  `scripts/init_project.py`, `scripts/copper.py`, `scripts/emit_board.py`, `scripts/netlist.py`, `commands/init.md`,
  `data/fabrication.json`, `GLOSSARY.md`, `skills/spark-design/references/design-rules.md` and `tests/test_board_look.py`,
  `test_copper.py`, `test_emit_board.py`, `test_fab.py`, `test_init_project.py`, `test_json_contracts.py`,
  `test_netlist.py` and `test_self_confirmation.py`, which name it.
- Why: Only `check_all` imports it. It grades a board for the PCB order of P136, not the breadboard journey.
- Kept by: the plug-in point `check_all.CHECKS`, with the same two steps as `check_bom.py`.
- Back: `git checkout pre-refactor-2026-10-25 -- scripts/check_physics.py tests/test_check_physics.py
  tests/mutations/p143-severity.json tests/mutations/p197-clean-check.json tests/mutations/sprint-3-p13.json
  tests/mutations/sprint-6-p34.json tests/mutations/sprint-6-p35.json tests/mutations/sprint-6-p41.json
  tests/mutations/sprint-6-p46.json tests/mutations/sprint-8-p52.json`, then add
  `Physics("physics", ["circuit", "rules"], ...)` to `CHECKS` again and restore the other files of the Moves line from
  the same tag. The module needs `scripts/check_footprints.py`, `scripts/copper.py` and `scripts/netlist.py`. The last
  two stay with the build, so they are always there.

## Not decided yet

- The 19 flags that no page names (group (b) of the pruning list). The rule: a flag that a test, a script or a caller
  outside the repository passes gets a line on its script's page, and a flag that nothing passes goes. A project
  Makefile and `tools/snapshot.py` pass `boards.py --path`, `--id` and `--paths`, so those stay. The prune PR applies the
  rule and lists each flag that goes here, with the same four parts and the files it touches.
- The later spans of the pruning list (for example `REQUIRED_FOR_FAB` in `scripts/boards.py`). They stay in place under
  the marker `# --- Later, not MVP: <why kept> ---`. Nothing leaves, so they need no restore command.
- `tools/snapshot.py`: the PO decides whether it is a later span (pruning list, verdicts table).
- `chips/wokwi-api.h`: no verdict. Card P415 [#542](https://github.com/xmejkal/spark/issues/542) asks the PO.
