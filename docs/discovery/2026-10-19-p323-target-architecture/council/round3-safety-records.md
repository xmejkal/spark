# Round 3: safety, records and data lens

## G1. Gates are not tied to effects
Design 2.4 says an Operation with `erases` or `board` passes `ConsentStrategy`, but nothing enforces it. Today `require_open_gate` is the only road to the erase (D8) by convention only.
Fix: `Operation.__post_init__` raises if `erases` is set and no gate is named. `run_door` refuses to run it without a `consent` collaborator. Add rule S14: only `bench/deploy` imports the erase Adapter, and only through `require_open_gate`. A seam test plants an erasing Operation with no gate and expects the refusal.

## G2. A yes is never an input
`TerminalConsentStrategy` needs a tty, and an MCP door has none.
Fix: write in 2.4 that the door's process picks `consent`, never an Argument or a tool input. An MCP door gets only the terminal strategy, which fails closed and returns the `NEXT_DEPLOY` step.

## G3. Grants fail closed
Fix: `Grant.why_not_valid` stays pure in `bench`. A test: a corrupt or zoneless grant file means "no grant".

## G4. Schema versions and migration
Today `parts.py` has `SUPPORTED_SCHEMA`, `boards.py` reads `schema` itself, `needs.py` refuses any value but 1. `RecordSchema` names no version rule.
Fix: `RecordSchema(kind, version, rules)` with four rules.
1. A reader accepts its own version and refuses a newer one with code `schema_too_new` and a fix line.
2. An optional property needs no bump.
3. A bump needs one pure `migrate(record)` for the previous version, tested on a fixture. Spark never rewrites a person's file unasked.
4. A missing `schema` is 1 in a store file and a problem in a library record.

## G5. One Repository
`store.home()`, `layers()` and `records()` give the order today (library, store, project). The design splits them over `BoardRecords`, `PartRecords` and `tool_finder`, and each could re-read the environment.
Fix: `records/` builds one `Layers` Value (library, store and project folders, with `.spark/`) from `store.home()` and the project path. `BoardRecords`, `PartRecords` and `tool_finder` take a `Layers`. Only `records` reads `SPARK_HOME`, and S3 says so. No area builds a `.spark/` path by hand.

## G6. File writes
`store.write_file` writes `.part`, renames, skips unchanged bytes and sets 0600 for private files.
Fix: new rule: only `records` writes files, through `write_file`. The AST test flags `open(..., "w")` and `write_text` elsewhere. Project outputs go through a `FileWriter` collaborator, which is also the dry-run seam.

## G7. Dry run is a convention
84 lines mention `dry_run` today, one flag per script. `effects` states intent only.
Fix: `--dry-run` makes `run_door` swap the `FileWriter` and `run` for recording Fakes, so no write or process happens whatever the Operation does. The envelope lists `data.would_write`. An Operation with `board` or `erases` never reaches the Flasher on a dry run. One contract test per Operation: the folder tree hash is unchanged after a dry run.

## G8. The Wokwi token
It is read from the environment (`account_env` in `data/tools.json`) and never written.
Fix: `run_door` masks the value of every variable named in an `account_env` row in all it prints. No Adapter puts `env` into a `SparkError`. A test sets the token to a marker and fails if the marker appears in stdout, stderr or any file under the project.

## G9. Time and zone
`board_grant` already refuses a time with no zone.
Fix: `core` gets one `Clock` collaborator whose `now()` returns an aware time. A schema date is ISO 8601 with offset. A naive time is a problem with code `no_zone`.

## G10. Errors that leak paths
`SparkError.fix` and problems can hold `/Users/name/...`. Envelopes get pasted into public issues.
Fix: `run_door` prints paths under the project as relative and under the store as `$SPARK_HOME/...`. A `crash` envelope holds the exception class and a short message. The traceback goes to stderr only with `--debug`.

## Order
G1, G2, G8 and G10 first, as a guard line or one filter in `run_door`, so they fit slice 2. Then G7, G5, G4, G9 with the first story that needs each.
