# P323 council: the code standard (senior Python engineer)

In short: spark already has a good standard on paper (`docs/guide/developing.md` lines 220-290) and good code in the deploy area. The gap is enforcement and reach. Keep the role table, add eleven short rules, and check eight of them with one stdlib lint script `tools/check_style.py` run by the push hook. No ruff, no mypy.

## Keep

- The role table and the "role word first" docstring (`developing.md:231-243`). Keep Service, Strategy, Adapter, Value, Store, Decorator, Renderer, Platform, Fake.
- `main()` only parses and prints, a script exits through `outcomes.EXIT_FOR` (`outcomes.py:25`).
- Three outcomes decided once by `outcomes.status_of` (`outcomes.py:37`). Nobody declares a status.
- Stdlib only, unittest, the temp-folder line (`tests/suite_temp.py`), and "a test must run the thing" (`developing.md:14`).
- Mutation tables (`tests/mutations/`) for any fix with logic.
- `tests/fakes.py` holds fakes of swappable parts (`fakes.py:8`).

## The rules

**1. One role per class, named by the table.**
Good: `DeployService` (`deploy_service.py:69`) holds steps, `Flasher` (`flasher.py:18`) is the swap point, `EsptoolFlasher` (`flasher.py:35`) fills it in. Bad: `parts.py` (2402 lines, 126 top-level defs) mixes Store, Value, Policy and a CLI. Check: lint reads each class docstring and fails when the first word is not a role from the table (P322 measures 56 of 103 today, so start as a ratchet).

**2. Add a Policy role.**
A Policy is a small class that decides yes or no from facts, with no I/O. Today these are loose functions such as `parts.validate` (`parts.py:621`, 242 lines of one function). Name it `<What>Policy` with `decide()` or `why_not()`. Check: review only.

**3. Values are frozen.**
Rule: a Value is a frozen dataclass (`@dataclass(frozen=True)`) or a NamedTuple. Python 3.10 has both in the stdlib, so use `dataclass(frozen=True, slots=True)` for new Values, and keep the old `collections.namedtuple` Results (`deploy_service.py:31`) until touched. Bad: `ButtonPlaces` (`boards.py:269`) is a hand-written class with public mutable fields, and `BoardLog` (`deploy_service.py:43`) is a namedtuple subclass. Check: lint fails on a class whose docstring starts with `Value` and has no `frozen=True` or NamedTuple base. Dicts that cross a module boundary (`outcomes.answer`, `outcomes.py:48`) stay allowed only as the `--json` shape at the edge. Inside the core, pass Values.

**4. Collaborators come in through the constructor, never through patching.**
Good: `DeployService.__init__(..., run=subprocess.run, clock=None, probe=None)` (`deploy_service.py:78`). Bad: 336 `mock.patch` uses in tests, such as `test_parts.py:961` patching `parts.sources_resolve`. Rule: anything that touches the process, the clock, the disk outside the store, the network or the environment is a constructor argument with a real default. Check: lint counts `mock.patch` per test file and fails when a file goes up. Ratchet down to patching only `os.environ` (already a helper at `test_parts.py:47`).

**5. Fakes over mocks, one fake per swappable part, with a contract test.**
Good: `FakeBoardConnection` (`fakes.py:8`) records calls and raises when over-asked. Rule: each Strategy or Adapter base class gets a contract test module that runs the same cases against the real class (with its tool faked at the process boundary) and against the Fake. Check: lint fails when a class in `tests/fakes.py` has no matching name in a `test_*contract*.py` or other test that imports both. `Mock()` and `MagicMock` are banned in new tests.

**6. One error family per context, mapped to an outcome once.**
Today there are a dozen unrelated roots: `BoardError`, `DesignError`, `PartError`, `LookStop`, `DeployError`, `GateClosedError`, `UnknownStepError` (`boards.py:122`, `design.py:64`, `parts.py:223`, `board_look.py:53`). Rule: every library module raises a subclass of one `SparkError(Exception)` in `scripts/errors.py`, with a class attribute `outcome` that is one of `outcomes.PROBLEMS` or `outcomes.COULD_NOT_RUN`. The CLI edge has one function `outcomes.exit_for_error(exc)` and no script catches by message. Name ends in `Error`, per context (`DeployError`, `DesignError`). Never catch bare `Exception` except at `main()`. Check: lint fails on a new `class X(Exception)` outside `errors.py`, a bare `except:` and `except Exception` outside `main`.

**7. No magic strings, and enums for closed sets.**
Good: `outcomes.OK, PROBLEMS, COULD_NOT_RUN` (`outcomes.py:21`). Rule: a closed set of words (status, severity, stage, op) is a `str`-mixin `enum.Enum` (`class Status(str, Enum)`) so `--json` still prints the plain word. A sentence a person reads is a `_MESSAGE` or `_HINT` constant, imported by writer and reader. Check: `tests/test_no_magic_strings.py` already fails on a spaced literal in a comparison. Extend it to dict keys `"status"` and one-word codes compared to a string literal in `scripts/`.

**8. Type hints on the public surface, no checker in the push hook.**
Rule: every new public function and method in a library module has parameter and return hints, and Values have typed fields. `from __future__ import annotations` is allowed on 3.10. Only 531 lines in `scripts/` carry hints today, mostly `parts.py`. A checker is "free, few and local" only if it is one tool: mypy is free but heavy and a user install. Decision: add no checker to the gate. Offer `python3 -m mypy scripts/` as an optional dev command in `developing.md`, never required, never in CI until the PO says. Check: lint fails on an unannotated new public def (ratchet by a baseline file of the old ones).

**9. Size limits.**
Rule: a function is at most 60 lines, a class at most 300, a module at most 600. Bad: `parts.validate` 242 lines, `check_spine.run` 194 (`check_spine.py:347`), `emit_board.py` 1172 lines, `parts.py` 2402. Good: `deploy_service.py` 202, `flasher.py` 66. Check: lint with `ast`, a baseline file lists today's over-limit names with their length, a baseline entry may only shrink. This is the ratchet that moves scripts toward a package.

**10. Docstring rule: role word first.**
Rule: a class docstring starts `Role:` then one sentence (`ButtonPlaces`, `boards.py:270`, does this with `Value:`). A function docstring starts with a verb in the third person or the noun it returns, and says what it raises. A module docstring says what it is a library for and who calls it (`deploy_service.py:1-10`). Check: lint, same pass as rule 1, plus a module docstring on every file in `scripts/`.

**11. Layout: a core package, interfaces thin.**
Rule: target `spark/` package with subpackages by layer: `spark/core` (Values, Policies, Services), `spark/adapters` (esptool, mpremote, tsci, wokwi), `spark/store`, and `scripts/*.py` as CLI shims under 40 lines that call `spark.cli`. Dependency direction is one way: interfaces, services, policies and values, with adapters injected from the edge. A core module never imports an interface module (P322 counts 3 private imports today) and never imports `argparse`, `sys.exit` or `print`. Check: lint with `ast` imports, a layer table in the script, fails on an upward import, on `print` in core, and on a `main` function holding more than 25 lines. Until the move, apply it to `scripts/` library modules, the ones with no `main`.

## Names, one word per thing

Keep `developing.md:256-270`: a function starts with a verb, `why_` returns a reason or None, a unit suffix on number constants, subclass is what varies then the base name. Add: one word per idea, listed in a small glossary table (`Result` for what a method returns, `Report` only for a Value that a person reads, `Check` for a thing that returns problems, never `Validator`, `Verifier` and `Doctor` for the same job). Check: the glossary has a banned-synonym list that lint greps in class names.

## Tests per role

- Value: a plain table test, equality, and `to_dict()` round trip. No fakes.
- Policy: table test of facts to verdict, plus one mutation table.
- Service: built with Fakes through the constructor, asserts on the result Value and on what the fakes recorded. Never `mock.patch`.
- Strategy and Adapter: a contract test run on every implementation. The Adapter test fakes only the outside process, with a stub script like `tests/fake_wokwi_cli.py`.
- Store: a real temp folder from `suite_temp`, never a fake filesystem.
- CLI: one test per exit code, running `main(argv)` and reading the `--json` envelope.

## What a tool can check, and how

One script, `tools/check_style.py`, stdlib `ast`, about 200 lines, run by `check_commit.py` beside the suite. It reports with the three outcomes. It reads a `tools/style_baseline.json` of today's violations, fails on any new one, and fails when a baseline entry no longer exists (so the file only shrinks). It covers rules 1, 3, 4 (count), 5, 6, 8, 9, 10, 11 and the glossary. Rule 2 and the quality of rule 7 stay with the reviewer.

## Order to adopt

1. Write the lint with a full baseline, no code changes (green on day one).
2. Add `errors.py` and `Status` enum, migrate one context (deploy, already has the Error suffix).
3. Each story that touches a file pays one baseline entry down. This keeps "something always works" and matches the PO's small steps.
