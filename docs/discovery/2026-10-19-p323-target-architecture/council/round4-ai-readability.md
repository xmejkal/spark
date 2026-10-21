# Round 4: code that an AI agent reads and changes well

Lens: an agent that reads and changes spark's code at low token cost, and one that calls the doors. Opus, 2026-10-21.
Folds in the PO's words of 10-21: a designed system the scripts only call, switchable frontends, configured backends.

> **TL;DR.** The design serves the doors well and the code reader less. Add seven rules: one name for one thing,
> module imports only, one generated map, one verb per job, no hidden test mode, one home per code and shared flag,
> and every seam listed in its registry. None costs a human reader anything.

## What the design gets right

- Small reads: function 60 lines, module 600, door 40 (D7, S6). Today `parts.py` is 2,402 lines, and
  `parts.validate` (`parts.py:621`) is 240 lines, `check_spine.run` (`check_spine.py:347`) 192, `boards.validate`
  (`boards.py:340`) 161. An agent must read each whole to change one branch.
- One Operation feeds the door, `--help` and `--describe` (D2). `parts.py --describe --json` shows the cost today:
  9,057 bytes for 30 operations, about 2,300 tokens.
- Doors: one versioned envelope (`outcomes.py:68`), exit 0, 1, 2 from one table (`outcomes.py:19-31`), codes,
  `next` steps with `needs_yes` and `needs_person`, crash as exit 2, diagnostics on stderr, no decision on a sentence (S9).
- Role words (S1), hints (S11), no vague names (S12). Every module has a docstring. 2,831 test names state behaviour.

## A designed system an agent can walk

A long script forces a linear read: to change one branch of `parts.validate` an agent reads 240 lines. A designed
system lets it jump: door to Operation, Operation to Service, Service to the one Strategy that holds the branch. Three
things make that jump cheap. First, the role word in the class docstring (S1) says what kind of thing it is before the
body is read. Second, a Strategy's base class is the contract: its methods and their hints say what every Adapter
must do, and its `<Name>Contract` test (S14) shows it running. Third, the Service's `__init__` lists its
collaborators with real defaults (2.6), so its whole outside world is in one signature.

Frontends: the core never prints or parses (S5), and `run_operation` takes values, not argv (2.6). So a frontend is
only a door, and every door calls the same `run_operation`. An agent that adds an MCP door or a web page writes one
file and changes no Operation. Backends: a backend is a Strategy chosen by a record or a setting (`PLATFORMS`,
`ENGINES`, `CHECKS`, `data/tools.json` rows, 2.5). The agent's question is "which backend runs, and why". Rule A7
below answers it in one read.

## What it misses

**F1. One word names three things.** `parts` is the record folder `parts/`, the door `parts.py` and the area
`spark/parts/`. `boards`, `build` and `design` repeat this (`design/design` in 2.1). The bench area lists `look`,
`deploy`, `grant`, `live`, `reach`, also door names. A grep for `look.py` returns two files, and an agent edits the
door instead of the core. Today's prefixes (`board_look.py`, `deploy_service.py`) avoid exactly this.
**F2. `describe` and `render` overlap.** `render(result)` gives person text in 6 modules (`check_all.py:434`).
`describe(result)` gives person text in 4 more (`board_doctor.py:188`, `live.py:48`, `grant.py:53`, `reach.py:37`).
`parts.describe(part)` (`parts.py:1546`) prints a part. `--describe` is the machine description. A grep lands in all.
**F3. Private names cross through attributes.** `drawer.py:187` calls `parts._parse`, `drawer.py:226-228` call
`parts._problem`. A scan of `from x import _y` finds none, so S4 must also catch `module._name`.
**F4. Import style is unstated.** Today `import boards` then `boards.load`, which greps well. `from
spark.records.boards import load` loses the module name at the call site and makes S8's patch targets harder.
**F5. No map for the code.** G1 maps doors to operations. An agent changing code asks which module holds pin
assignment and where its test is. Today it reads `developing.md` (360 lines), `agents.md` (750) or 59 flat modules.
**F6. A hidden test mode.** `store.py:40` swaps `SPARK_HOME` and the session id when `"unittest" in sys.modules`,
and `store.py:339` allows `file:` URLs only then. A CLI bug can behave differently in a test, with no visible cause.
**F7. Codes and shared flags have no home.** 2.4 lists starter codes but not where each is defined or what it means.
`tool_missing` crosses areas. `--project`, `--json` and `--port` drift if each door spells its own `Argument`.
**F8. `--describe` returns everything.** The AI interface paper (section 3) had `--describe OP`. The design dropped it.
**F9. The chosen backend is not printed.** Nothing says which Platform, Engine or tool Adapter ran and which record or
setting chose it. An agent debugging a wrong flash must read the selection code.

## The rules

- **A1. One name, one thing.** A file basename is unique across `scripts/` and `scripts/spark/`. A module never
  repeats its area's name, and an area never reuses a record folder's name. Moves keep today's prefixed names.
- **A2. Import modules, not names.** `from spark.<area> import <module>`, then `module.Name`. Absolute only. A `_name`
  is never read from another module, as an import or as an attribute.
- **A3. One generated map.** `docs/guide/map.md`: doors and their operations (G1), then each area's modules with
  the first docstring line, the role, and the test file, then each registry with its keys. A test fails when stale.
- **A4. One verb per job.** `render(x) -> str` is person text. `describe` is only the machine description.
- **A5. No hidden modes.** Code never branches on what is imported. A test passes `Layers` or a collaborator.
- **A6. One home per code and shared flag.** A code is a constant with a one-line meaning in its area's `codes.py`,
  or `core/codes.py` when two areas emit it. A flag used by two doors is one `Argument` in core. `--describe OP`
  prints one entry with its codes' meanings.
- **A7. Every seam is listed and reported.** Each registry is a dict named in capitals beside its base class
  (`PLATFORMS`, `ENGINES`, `CHECKS`, and later `DOORS`). The envelope's `context` names each backend that ran and the
  record or setting that chose it, such as `platform: micropython (requirements.json)`.

## Rows

1. F1: `parts`, `boards`, `build`, `design` and bench door names mean two or three things. Adopt A1, keep prefixed
   module names, and let the synthesis rename the `parts` area.
2. F2: `describe` and `render` overlap (`board_doctor.py:188`, `parts.py:1546`). Adopt A4, rename per story.
3. F3: `drawer.py:187,226` reads `parts._parse` and `parts._problem`. S4 catches attribute access.
4. F4: import style unstated. Add A2 to 2.2.
5. F5: no code map. Adopt A3, merged with G1 into one generated file.
6. F6: test mode keyed on `sys.modules` (`store.py:40,339`). Remove it when `Layers` lands (A5).
7. F7: codes and shared flags have no home. Adopt A6 in slice 2 with `core/codes.py` and shared `Argument`s.
8. F8: no one-entry `--describe`. Add `--describe OP` in slice 2.
9. F9: the chosen backend is invisible. Adopt A7: `context` names each backend and its chooser.
10. 179 `sys.path` inserts in 78 test files (`tests/test_look.py:11,15`). One `tests/paths.py` helper in slice 2.
11. PO 10-21: a frontend is only a door over `run_operation`. Add one line to 2.6 that says so, and a seam test
    that a second door gets the same answer.
