# P251's plan council, 2026-10-15

Three rounds read the plan in [docs/2026-10-15-p251-reach-plan.md](../../2026-10-15-p251-reach-plan.md) before any
code. Each line is one finding in short. The plan's text says how each one was acted on.

## Round 1, on the first version

A gaps lens (Sonnet, L) and a refuter (Opus, R).

| id | finding | verdict |
| --- | --- | --- |
| L1 | `wait_for_reset` after the probe's own open sees no restart and waits the full 60 s | acted (cure() waits for the port to exist) |
| L2 | a failed first try is not a shown silence; a late boot (H3) also passes a retry | acted (`restart_heard` column, limit in the bench log) |
| L3 | the cold arm cannot fail | acted (round 3, `--cure-first`) |
| L4 | no FAIL line, and 30 replugs can bring too few silent boots | acted (FAIL and INCONCLUSIVE lines) |
| L5 | tests miss the real `TransportError` line, download mode and a timeout | acted (substring test; download mode cut, B3) |
| L6 | the fake cannot give an unread port or flip the connection | acted (`on_cure`, a given `Cure`) |
| L7 | `only_port` belongs to `Look`, not `PortFinder` | acted (`PortFinder.require_one_port`) |
| L8 | the Decorator duplicates deploy's flow | acted in part (the cure lives in the probe; deploy unchanged) |
| L9 | `silence_seen` and `retried_after_port_open` say more than they hold | acted (`first_try_failed`, `restart_heard`) |
| L10 | the rename is half done while the module says download mode | acted (`board_console.py`) |
| R1 | the wait after the probe's open misses the restart | acted, as L1 |
| R2 | a read that fails mid-restart is reported as not reached | acted (the retry still runs) |
| R3 | the plan dropped the diagnostic listen, so non-silent failures count | acted (round 3, G5: silent = a cure ran) |
| R4 | `machine.reset_cause()` is always 5 after `exec` | acted (no uptime, no cause) |
| R5 | the cold arm tests nothing | acted, as L3 |
| R6 | the fake cannot give `(None, why)` | acted, as L6 |
| R7 | an exact match on the error never fires | acted (substring, `RAW_REPL_REFUSED`) |
| R8 | the stateful `last` is a side channel | acted (`last_cure`, a `Cure` value, justified) |

## Round 2, on the fixed version

A bloat check (Sonnet, B) and a naming and architecture lens (Opus, N).

| id | finding | verdict |
| --- | --- | --- |
| B1 | a failed read loses `rst:`, so a cure could count as none | acted (cured = first try failed and reached) |
| B2 | the fake's `console()` is not needed | acted |
| B3 | the download-mode branch is not needed by D22 | acted (cut) |
| B4 | the uptime in the marker proves nothing | acted (`PRINT_REACHED`) |
| B5 | `output` and `console` fields are extra | acted in part (`output` kept for P247) |
| B6 | the slice plan now contradicts this plan | acted (its lines point here) |
| B7 | the cold arm cannot fail the story | acted (kept out of PASS and FAIL) |
| B8 | there are no `only_port` tests to move | acted (new tests) |
| N1 | the fake's `console` field hides a `console()` method | acted (`printed`) |
| N2 | `cure` names an action and its evidence | acted (`Cure` value, `last_cure`) |
| N3 | `MARKER` is a coined word | acted (`PRINT_REACHED`) |
| N4 | `only` is not a verb and clashes with `self.command` | acted (`require_one_port(script)`) |
| N5 | the Decorator is not a drop-in | acted (three pass-through methods) |
| N6 | platform strings in the Decorator | acted (the probe owns the cure) |
| N7 | `download_mode.py` misnames the probe's module | acted (`board_console.py`) |
| N8 | mpremote's words belong in `board_connection.py`; `reach()` must not read a field by chance | acted (`RAW_REPL_REFUSED`, `reach()` builds the Decorator) |

## Round 3, problems and gaps after the fixes

One reviewer (Opus, G), by the PO's standing rule.

| id | finding | verdict |
| --- | --- | --- |
| G1 | `reach.py` is named on no page, so `test_orphans` fails | acted (a line in developing.md) |
| G2 | the plan does not say where each constant goes; an import loop is easy | acted (`download_mode.py` stays a leaf) |
| G3 | "the port does not come back" has no field in `Cure` | acted (cut; always retry once) |
| G4 | the Decorator must take `keep_running_for` and live beside `BoardConnection` | acted |
| G5 | a timeout counted as a silent boot can fail the bench | acted (silent = a cure ran; JSON nested, `at`) |
| G6 | the cold arm's `python3 -c` cannot find `scripts/` | acted (`--cure-first`) |
| G7 | the shown cures used `resume exec`, `run_code` does not | acted (named in the bench log) |
| G8 | three test branches missing | acted |
