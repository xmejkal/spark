# Round 4: the interface people and Claude meet (UX and AI-UX lens)

> **TL;DR.** Today 23 doors speak about 11 output shapes, 4 names for the message, 12 wordings of `--json` and
> 11 of `--project`. The design already fixes the envelope, codes, steps and exit codes in `run_door`. Add one thing:
> the contract lives in `spark/core` as data (common Arguments, one Item shape, one help footer). Each frontend only
> renders it: text for a person, `--json` for Claude, MCP later. A new door or a new frontend then gets it for free.

Summary: I ran `--help` on the 23 argparse doors and read-only `--json` runs on missing inputs, SPARK_HOME unset.
Claude trips on a `--json` run that prints text, a missing input that exits 1, and a message under a new key per door.
A person trips on flags with no help words and exit codes named in only 8 of 23 helps.

## 1. Inconsistencies seen (real output)

1. Only `parts`, `look` and `deploy` print the envelope. agents.md:363-373 has to list a different shape for each of 11 doors.
2. The door's name sits under `tool` (`compare_design`), `check` (`check_spine.py:967` `"spine"`, `emit_footprint.py:236`
   `"emit-footprint"` with a hyphen), or nowhere (`grant.py:63`).
3. The message sits under `sentence` (parts), `reason` (`compare_design.py:66`, `check_physics.py:636`, `check_all.py:530`),
   `message` (`emit_footprint.py:236`), `detail` (check_spine stages) or `why` (`grant.py:63`, value `"could not run"` in English).
4. `check_vendor_pins --offline --json` prints a bare list. `assign_pins --json` has no `status` (agents.md:367).
5. `status` holds words beyond the three: `mismatch` (`check_vendor_pins.py:231`), and per module `imported`, `raised`,
   `timed out` (agents.md:370). Claude must learn which `status` is an outcome.
6. `check_footprints.py /x/c.json --json` prints "no built design at /x/c.json, build it first" (dash shown as a comma)
   as plain text, exit 2 (`check_footprints.py:547`). `assign_pins.py` does the same (`:465`). A JSON parser breaks.
7. `look.py --bogus --json` prints argparse usage text, exit 2. `parts.py --bogus --json` prints an envelope. Same mistake, two answers.
8. `boards.py --get nope.x` with no `boards/active.json` exits 1, which means `problems`. It could not look, so 2.
   `parts.py --show no-such-part` exits 1 too: a missing input reads as "found something".
9. `tools.py --status` exits 2 while any tool is missing, even one the step does not need, and has no `--json` (agents.md:54, 462).
10. Eight doors have no `--json` at all: boards, breadboard, check_bom, emit_board, flash_image, init_project, run_scenario, tools.
11. A fix is free text when it exists: `"fix": "build it first: \`make\`, or \`tsci build\`"` (compare_design). check_physics
    gives no fix for the same missing file. `boards.py` gives none.
12. `boards.py --get nope.x` prints the whole home path `/Users/petr/Development/spark/...` (S18 would catch it).
13. The project is `--project` in 15 doors, a positional `requirements` file in 4 (assign_pins, breadboard, check_spine,
    emit_board), a positional `project` in import_firmware, and a value of a selector in parts (`--needs PROJECT`)
    beside parts' own `--project`. The default is "here", "found upwards" (grant) or not said.
14. One word, two meanings: `--keep FILE` puts a file in the store (`parts.py:1595`). `--keep DIR` writes the build (`check_spine.py:639`).
15. Output is `--out` (`breadboard.py:577`), `-o/--out` (`emit_footprint.py:198`), `-o/--output` (`flash_image.py:130`).
    Timeouts: `--timeout SECONDS` (`import_firmware.py:99`), `--timeout-ms` (`run_scenario.py:238`). The circuit is a
    positional in 3 checks and `--circuit` in check_all and check_bom.
16. `--json` has 12 help wordings, `--project` 11. No help words: `tools.py --status --on --off --use`, `emit_board.py
    --project --board`, `assign_pins.py --json`. Exit codes are in only 8 helps. Effects are prose: look says "without
    changing it", then "the board restarts". The last line is a next step (look), why (grant), a log path or nothing.

## 2. What the design already has

The envelope with `status` and EXIT_FOR (2.4, 2.6). A `code` per item and starter codes. `fix` and `next` as
`outcomes.step` with `needs_yes` and `needs_person`. A bad argument turned into an answer by `run_door`. A crash as exit 2.
Path shortening and secret masking before print (S18). `--describe` from the Operation. Consent outside the Arguments.
That covers items 1 to 8, 11 and 12 once each door is converted.

## 3. The contract, defined once in the core

The PO (2026-10-21) wants frontends that can be switched. So the contract is data in `spark/core`, never code in a door.

- **C1. One answer.** `run_operation` returns the answer: `status`, `data`, `problems`, `unchecked`, `next`, `notes`,
  `assumptions`, `wrote`, `diagnostics`. Every frontend renders this one value. None adds a key or a message.
- **C2. One Item.** Every problem and unchecked item is `code`, `subject`, `sentence`, `fix` (a step or null). No
  `reason`, `message`, `detail` or `why`. `status` is only an outcome word. A per-item state uses a declared constant
  under its own key (such as `compare`: same, differs, unknown).
- **C3. Common Arguments.** `spark/core/arguments.py` holds the shared Arguments once: `--project` (a folder,
  default "here"), `--json`, `--dry-run`, `--out`, `--timeout SECONDS`, `--port`, `--describe`, `--debug`. Each has
  one help line. An Operation names them; it cannot respell them. Today's other spellings stay as hidden aliases in
  a baseline that only shrinks, so no door breaks (design line 97).
- **C4. Frontends render, they never decide.** A `Frontend` Strategy with `TextFrontend` (a person), `JsonFrontend`
  (Claude: exactly one envelope on stdout, diagnostics on stderr, always, even for a bad flag) and later `McpFrontend`
  (`isError` exactly for `could-not-run`). `run_door` picks Text or Json from `--json`, and every Operation gets `--json`.
- **C5. One help footer.** The help is generated from the Operation: summary, Arguments, then three fixed lines:
  `Effects:` (from `effects`, so "restarts the board" is said), `Exit codes: 0 ok, 1 problems, 2 could-not-run`, and
  `--json: one envelope (docs/guide/agents.md)`.
- **C6. One text order.** A person reads problems, then unchecked, then the status word, and the last line is the first
  `next` step or the first fix. Claude reads the same order in the envelope's keys.
- **C7. One test.** A parity test runs each Operation through Text and Json and checks the same codes and steps reach both.
Smallest slice: C2, C3 and C5 with `look` in slice 2. C4's JsonFrontend for bad flags at once (item 7).

## Rows

1. 11 output shapes across doors (agents.md:363-373); covered by the envelope; convert per door, drop rows from agents.md as each lands.
2. Message under 5 keys (sentence, reason, message, detail, why); adopt C2, add to `ArchitectureRules` as a key check.
3. `--json` prints plain text on could-not-run (check_footprints, assign_pins); JsonFrontend always prints an envelope; add a contract test now.
4. `look.py --bogus --json` prints usage text; JsonFrontend renders a bad flag as an envelope, as parts does.
5. Missing input exits 1 (boards `--get`, parts `--show`); code `no_record` or `no_board`, could-not-run, exit 2.
6. `status` carries mismatch, imported, raised, timed out; only outcome words in `status`, item states under their own key (C2).
7. `--keep` means two things (parts, check_spine); card for the PO to rename one; it is a user-facing flag.
8. Project given 4 ways, circuit 2 ways, output 3 ways, timeout 2 ways; common Arguments in core (C3), old spellings as shrinking aliases.
9. 12 `--json` and 11 `--project` help wordings, flags with no help; help lines live once in C3; S-rule: every Argument has help.
10. Exit codes in 8 of 23 helps, effects in prose; generated footer (C5).
11. Last line differs per door; one text order (C6) in TextFrontend.
12. `tools.py --status` exits 2 for an unneeded tool, no `--json`; scope its status to the step's roles; convert with P92.
13. `boards.py` prints a home path; S18 marker test covers it; add boards to the first doors it runs on.
14. Frontends must be switchable (PO 2026-10-21); `Frontend` Strategy (C4) plus a parity test (C7); MCP renders the same answer.
