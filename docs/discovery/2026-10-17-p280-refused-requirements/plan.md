# P280 — a refused requirements file removes an earlier build's sheet and page

Card: https://github.com/xmejkal/spark/issues/318 (Build). Branch `p280-refused-requirements`. One PR.

## Council

Round 1 ran: tech lead (Sonnet) and refuter (Opus). It changed:

- No new keep function. The two existing ones (`keep_breadboard`, `keep_tabbed_page`) learn one more reason through
  one shared `why_not_built(stages, board_only_why)`. `report()` runs its normal keep block without a workdir.
- The why is the requirements stage's own detail (`str(broken)`), not a fixed sentence. `design.read` also refuses
  a file that it read, for example two part names that differ only in capitals, so "cannot be read" was false.
- A missing requirements file removes nothing. `design.read` raises the same `DesignError` for a missing file, so a
  typo (`requirements.jsn --keep .`) would delete a good build. Only a file that exists and is refused cleans up.
- A spark-written `pins.py` is removed too, at no cost: `keep_pins` already removes it on a `DesignError` and leaves a
  person's own `pins.py` alone. This is one file more than the card names, and the PR says so.
- Tests: a helper that keeps stderr. Red tests and guard tests are labeled apart.
- Accepted as they are: removal is by file name, as for a failed build today. `--sim-dir` is out of scope.

Round 2 ran: tech lead (Sonnet) and PO assistant (Sonnet). No high or medium gap. It changed:

- One test asserts the card's four files by name, each with its own entry and the why, apart from `pins.py`.
- Tests also pin the no-workdir paths: an old `dist/` stays (no SKIPPED stage), and `page.html` is removed with
  the stage detail as its why.
- The PR names the `pins.py` removal (one file more than the card) and the missing-file guard (a narrowing) as two
  choices that the PO can overrule. `agents.md` states the missing-file exception.
- `commands/build.md:98` gets the same sentence for a person.
- Two follow-up cards are proposed, not filed: a renamed or deleted requirements file leaves a stale sheet and page;
  an `OSError` from `unlink` in `_left_from_earlier` gives a traceback.
- `REQUIREMENTS_STAGE` is the first stage-name constant. The PR says that other stage names can follow (P260).

## Context

`check_spine.py requirements.json --keep .` reads the requirements file first (`scripts/check_spine.py:652`). If
`design.read` refuses it, `main()` calls `report([...], args)` with no workdir, and `report()` keeps nothing and
cleans nothing (`:906`). The earlier build's `breadboard.md`, `breadboard.json`, `breadboard.svg` and `page.html`
stay beside a file that no longer builds, and they describe another board. P269 (#304) needs the page to never
show a board that the requirements no longer describe.

## Design

```
main()
  design.read() raises DesignError ──> report([Stage(REQUIREMENTS_STAGE, could-not-run, str(broken))], args)
                                          │
report(stages, args, workdir=None)
  keeps = args.keep and (workdir is not None or requirements file exists)
  kept  = _kept(workdir, keep) if workdir else []          (copies dist/ and *.tsx only with a workdir)
  kept += keep_breadboard(...)   ─┐
  kept += drop_an_older_build()   │ unchanged calls; drop_an_older_build is a no-op (no SKIPPED stage)
  kept += _kept_pins(...)         │ keep_pins: DesignError -> removes a spark-written pins.py
  kept += keep_tabbed_page(...)  ─┘
              └─ both ask why_not_built(stages, board_only_why) -> the refused stage's detail
  print verdict; print kept lines on stderr (moved above the workdir check); rmtree only with a workdir
```

1. `scripts/check_spine.py`: constant `REQUIREMENTS_STAGE = "requirements"`, used in `main()` and below.
2. New `why_not_built(stages, board_only_why)`: None when the build stage is OK. Else the detail of a failed
   `REQUIREMENTS_STAGE`, else `board_only_why` when a stage is SKIPPED, else "the build did not finish in this
   run". `keep_breadboard` uses it with "board only: nothing to wire", and `why_no_page` with "board only: nothing
   to draw". Today's texts for the other cases stay the same.
3. `report()`: the keep block runs when `args.keep` and (a workdir exists, or `Path(args.requirements).is_file()`).
   `_kept` and `keep_simulation` still run only with a workdir. The stderr loop moves above the `workdir is None`
   return. All other callers pass a workdir, so their output does not change.
4. Follow-up cards, proposed to the PO, not filed: (a) a requirements file that was renamed or deleted leaves a
   stale sheet and page; (b) `_left_from_earlier` does not catch an `OSError` from `unlink`.

## Tests (`tests/test_check_spine.py`, `TheInputIsReadBeforeAnythingRunsTest`)

A helper `_main_with_stderr` returns code, stdout and stderr. Red before the fix:

- Malformed `requirements.json` in a folder with the four files and a spark-written `pins.py`, run with `--keep`
  that folder: exit `EXIT_COULD_NOT_RUN`, the five files are gone, and stderr says `no breadboard sheet: <detail>;
  removed`.
- The same with `--json`: `kept` has five entries, each `did: removed`, and each why holds the detail.
- A refused file that is valid JSON (two part names that differ only in capitals): the why names both spellings.
- The card's four files by name: `breadboard.md`, `breadboard.json`, `breadboard.svg`, `page.html` are gone, and
  each has its own `removed` entry whose why is the stage detail.

Guards, which pass before and after:

- A missing requirements file with `--keep` removes nothing.
- A `--keep` folder that does not exist is not created.
- A `pins.py` that spark did not write, a `board.tsx` and a `notes.txt` stay.
- Without `--keep`, nothing in the folder changes.
- An old `dist/` stays after a refused file (follow-up territory, pinned so a change is seen).

## Docs (same PR)

- `docs/guide/agents.md:171` and `:179`: an old sheet, drawing, page and spark-written pin map are also removed when
  the requirements file exists but is refused, and the kept entry gives the reason. A missing file removes nothing.
- `commands/build.md:98`: the same sentence for a person.
- `--keep` help text (`:630`): no change, because it does not list removals.
- No status change in the README's journey table.

## Verification

- `python3 -m pytest tests/test_check_spine.py -q`, then the whole suite through the push hook.
- By hand in a scratch copy of a kept example: break `requirements.json`, run `check_spine.py requirements.json
  --keep .`, and see the five files removed and five lines. Then rename it and see a missing file remove nothing.
- Review: one reviewer (Sonnet) and the refuter (Opus), and the mutation tester on the changed lines. Rows in
  `docs/observations/INDEX.md`.
