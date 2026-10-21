# Notes: decisions, conflicts and what was cut

Back to [level 1](README.md). The council's rows are in
[p323-target-architecture.md](../../../observations/rows/p323-target-architecture.md), rows 111 on for round 4.

## Council

Rounds 1 to 3 are in [design.md](../design.md). Round 4 ran seven lenses on 2026-10-21: architect, naming, human
readability, AI readability, testability, UX and the PO's voice. The chief architect wrote this synthesis on Opus
and checked every kept claim against `scripts/` and `tests/`. Round 4 changed most: one result shape, one
collaborator Value, one place for backend choices, readability as goal one, and a test net before any move.

## Decisions

| # | Decision | Why, in one line |
|---|---|---|
| N1 | The five goals rank readable, testable, exchangeable, reusable, consistent. | The PO named readability "most of all". |
| N2 | One result shape, `OperationResult(data, findings, next, lines)`. | Six shapes cross boundaries today, and a reader learns one. |
| N3 | One `Finding(severity, subject, code, sentence, fix)`. | Five problem shapes today, and `outcomes.answer` already has the three severities (`outcomes.py:49`). |
| N4 | One `OutsideWorld(run, write, fetch, clock, consent)`, with only the declared effects filled. | Dry run, consent and the test seams become one mechanism. |
| N5 | `Backends` holds choices, and each area's registry turns a choice into a Strategy. | records sits at the bottom, so it cannot build a bench or firmware object. |
| N6 | An Operation is a plain function with keyword parameters, not a `values` bag. | A typo in a flag name fails at load, and a reader sees the inputs. |
| N7 | One registry form: a dict in capitals from the class attribute `name` to the class. | `MATCHERS` already has it (`matching.py:222`), and it greps well. |
| N8 | `FirmwarePlatform` becomes a Strategy base, and it also makes the port finder and the board reader. | 8 tool lookups bypass it today, so a platform swap would edit 5 callers. |
| N9 | "CLI" replaces "door", "status" replaces "outcome", `RecordFolders` replaces `Layers`. | Each new word clashed with an old one, and the new names cost nothing yet. |
| N10 | The parts area is named `sourcing`. | `parts` already names the record folder and the CLI. |
| N11 | Module names keep today's prefixes in a move, and no module repeats its area's name. | A grep for one name lands in one file. |
| N12 | Slice 0 is a golden per Operation and status, with fake tools as processes. | Only 17% of tests reach spark from the outside, and a process fake survives every move. |
| N13 | A tool's MCP version enters as an input file that Claude passes. | spark has no MCP client (`tools.py:162`). |
| N14 | `SparkError.status` is a class attribute, `could-not-run` by default. | An argument invites a wrong status, and only `Impossible` needs `problems`. |
| N15 | Pin map text and image building stay out of `FirmwarePlatform`. | They would add upward edges from design and firmware to bench. |
| N16 | The envelope gains `code`, `needs_person` and `backends`, and loses nothing. | Claude branches on codes and sees which backend ran. |
| N17 | Area pages run about 150 to 200 lines, above the 130 asked. | Each holds three diagrams. The prose stays within the budget. |

## Conflicts between the papers, and how they were settled

| Conflict | Settled | Why, in one line |
|---|---|---|
| Result name: `Answer` (architect), `OperationResult` (naming), "the answer" with 9 keys (UX) | `OperationResult` with four fields | "Result" is the role word, and `parts.Answer` (`parts.py:230`) already holds "Answer". |
| Problem name: `Finding` (architect), `Problem` (naming), `Item` (UX) | `Finding` | An unchecked item is not a problem, and "finding" covers all three lists. |
| Collaborators: `Outside` (architect), one `<Area>Dependencies` per area (readability), separate seams (testability) | one `OutsideWorld` in core | One Value is smaller than eight, and "Outside" alone did not say its role. |
| `Backends` builds objects (architect) or holds choices (testability) | holds choices | records cannot import bench without a cycle. |
| `Frontend` as a Strategy with three subclasses (UX) or a function (architect) | a function, `run_cli`, plus two Renderers | One frontend exists in code, and a base needs two cases (rule T3). |
| `lines` (architect) or `diagnostics` (UX, design.md) | `lines` | `parts.Answer` already says `lines`, and it is not a JSON key. |
| Function limit: 60 (design.md D7) or 40 (readability) | 40 in `spark/`, 60 for scripts not yet moved | New code fits 40, and old code pays down by ratchet. |
| Keep the `parts` area name (architect) or rename it (AI readability) | rename to `sourcing` | Three meanings for one word is the clash rule C1 forbids. |
| Exit 1 for a missing input (`boards.py --get`, `parts.py --show`) fixed now (UX) or later | a card outside the refactor | It changes a public exit code, so it is a behaviour change, not a move. |
| Slice 1a before walk 2 (design.md) or after (PO paper) | 0a only if it merges by 2026-10-23 | It is the PO's call, and this is the PO paper's own condition. |
| Slice 2 as one PR (design.md) or three (PO paper) | three: 3a, 3b, 3c | Each adds one thing, and 3a is purely mechanical. |
| Starter codes in core (design.md) or in `codes.py` per area (AI readability) | per area, and in core when two areas use one | One home per code, and the area that emits it owns it. |

## Rule reference

`ArchitectureRules` (proposed, `tests/test_architecture.py`) checks each AST rule. A breach that exists today goes
in `tests/architecture_baseline.json`, which only shrinks. The old ids are in brackets.

| Id | Rule | Check |
|---|---|---|
| R1 | A function in `spark/` is at most 40 lines, an old script's at most 60. A module is at most 600, a CLI file at most 40. [S6, D7] | AST |
| R2 | Nesting is at most 3 deep. An `elif` chain counts as one level. | AST |
| R3 | A function takes at most 5 parameters, without `self`. More become one Value. | AST |
| R4 | A module starts with its docstring, then its public entry. Private helpers come last. | AST |
| R5 | A comment block is at most 4 lines and says why, in the present tense. History goes to the card. | AST |
| R6 | A class docstring starts with its role word. A first docstring line is one sentence. [S1] | AST |
| R7 | A sentence over one line is a `_MESSAGE` constant. Code decides on a code, never on a sentence. [S9] | `test_no_magic_strings.py`, review |
| T1 | Only an Adapter calls `subprocess`, `time`, `urllib`, `os.environ` or writes a file. Only records reads `SPARK_HOME`. [S3, S16] | AST |
| T2 | No new `mock.patch` except `os.environ`. A file's count never rises. [S8] | AST |
| T3 | A Strategy base has two subclasses or a Fake in `tests/fakes.py`, and a `<Name>Contract` test that each subclass test inherits. [S13, S14] | AST |
| T4 | Code never branches on what is imported, such as `"unittest" in sys.modules`. | AST |
| T5 | Every Operation has a golden per status, and no move changes one. | the golden test |
| X1 | A concrete Adapter is named only in its area's `operations.py`, picked from `Backends` through a registry. | AST |
| X2 | No `main`, `print` or `sys.exit` in `spark/`. A CLI calls `run_cli`. [S5] | AST |
| X3 | A registry is a dict in capitals beside its base class, keyed by the class attribute `name`. | AST |
| U1 | Imports follow the area map, with no cycle. Another area is reached only through its public modules. [S4] | AST |
| U2 | Import modules, not names. No private name crosses a module, as an import or an attribute. | AST |
| U3 | A shared flag is one `Argument` in core. A code is one constant in its area's `codes.py`. | AST, contract test |
| C1 | The glossary's words. No vague class words (Validator, Manager and the rest). A file basename is unique. Every exception subclasses `SparkError` and ends in `Error`. [S7, S12] | AST |
| C2 | Every Operation a command page calls has `--json` and prints one envelope, even for a bad flag. `status` holds only status words. [S10] | contract test |
| C3 | An exit code comes only from `EXIT_FOR`. No `EXIT_` alias. | AST |
| C4 | An Operation declares its effects. An erase names its gate. No secret or home path reaches the output. A newer record schema is refused. [S15, S17, S18] | AST, seam and marker tests |

S2 (a Value is frozen) and S11 (public functions carry hints) stay as review rules under R6 and C1.

## What was cut

`Layers`, `BoardRecords`, `PartRecords`, `BuildResult`, the per-area `COLLABORATORS` and the `shorten`, `secrets`,
`writer` and `consent` keywords, `diagnostics`, `Operation.description` and `.epilog` (the CLI keeps its own help
text), the Platform role word, `pin_map_text` and `make_image`, a `Frontend` base class, a `Clock` class, a serial
port seam, one Adapter per MCP row, a `Renderer` registry beyond the two that exist, and "door" as a word.
