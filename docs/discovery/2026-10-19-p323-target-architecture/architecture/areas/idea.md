# Area: idea

Back to [level 1](../README.md). Words are in the [glossary](../glossary.md). Added by P783 (p710 row 20): the area map
had no idea area, while `scripts/spark/idea/` imports design and sourcing.

## Level 2: what idea does

The idea area holds the Operations on a project's needs and what they hold, the stage /spark:idea works in
(`scripts/spark/idea/__init__.py`). `needs-drop` is the first on the core (P514); `--needs-set`, `--pick` and
`--requirements` can move here later.

### Its operations

| Operation | CLI | Effects |
|---|---|---|
| `needs-drop` | `parts.py --needs-drop PROJECT NEED` | reads, writes (reads alone with `--dry-run`) |

### Its components

| Module | Holds |
|---|---|
| `idea/drop_need.py` | `DropNeed`, the drop of one need and the release of the holds only its pick explained (P514) |
| `idea/idea_codes.py` | the reasons a need cannot be dropped, each a code with one sentence (a leaf) |
| `idea/__init__.py` | the index docstring and `OPERATIONS`, which maps each printed `op` to its class, for the frontends |

Idea imports design (`needs`, `need_requirements`), sourcing (`drawer`), records (`store`) and core. Nothing imports
idea but its CLI, `parts.py`.

### How idea is tested alone

`tests/test_needs.py` runs `DropNeed` through `run_operation`, with a fake drawer or needs file where a test swaps one.
Idea has no golden net yet: for a changed idea module the story run names `test_golden_idea`
(`tools/story_tests.py:110`, as `GOLDEN_NET_ELSEWHERE` maps build and sourcing alone), a module that does not exist yet.
