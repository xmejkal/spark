# P605 the core's schemas, trace hook and Privacy step: rows

What the plan council (two rounds), the review and the build found. Card:
[P605 #807](https://github.com/xmejkal/spark/issues/807) under [P158 #94](https://github.com/xmejkal/spark/issues/94).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The first plan's `run_operation(..., hooks)` had 5 parameters, so W4-2 could not add `backends` (R3 allows 5) | the refuter (Fable) and the architecture lens (Sonnet), round 1 | acted | `RunOptions` holds how a run is done. W4-2 adds `backends` to it as a field (refactor-plan.md, rule 3) |
| 2 | `time.perf_counter()` in `cli.py` breaks T1, a clock call outside an Adapter. reproduced on a copy | the refuter, round 1 | acted | `SystemClock` moved into `spark/core/clock.py`, and `RunOptions.clock` times the run |
| 3 | A trace test that asserts "seconds at least 0" passes a mutant that returns 0.0 | the refuter, round 1 | acted | a ticking test clock gives 10.0 then 12.5, and the test asserts 2.5 |
| 4 | One `schema()` dict fits neither MCP (`inputSchema`, `outputSchema`) nor LangChain (`args_schema`) | the architecture lens, round 1 | acted | `input_schema()` and `output_schema()` |
| 5 | `"default": null` on a string argument (`port`) contradicts its type | the lens and the refuter, round 1 | acted | `argument_schema` leaves the default out when it is None |
| 6 | The card says "every `Argument.dest` is a property". `json` is the frontend's flag, and `run_cli` pops it | the refuter, round 1 | acted | the input schema leaves `json` out. the test name says "but json", and a comment on #807 says why |
| 7 | A `Privacy` that raises escapes the crash catch, because the mask runs after `_guarded_result` | the refuter, round 1 | raised | it cannot raise while it passes through. S10 decides it when it fills the rules |
| 8 | Rule 4's test ("a store path reaches trace and the Renderer shortened") cannot run while Privacy passes through | the refuter, round 1 | acted | refactor-plan.md rule 4 says it waits for S10. P605's test marks with a Privacy subclass |
| 9 | A group of arguments that exclude each other (`look`'s evidence group) is not in the input schema, so an MCP client can pass both | Claude, plan | raised | for P417, when its tool needs it |
| 10 | After the move, `board_console.py`'s `time` and `datetime` imports are unused, and patterns-and-names.md:37 names the old home | the refuter, round 2 | acted | both imports dropped. the guide names `spark.core.clock` |
| 11 | Both guide pages sit exactly at their line budgets (379 and 279), so a docs change can add no line | Claude, plan | acted | every doc edit rewrites lines in place |
| 12 | The trace gets seconds, not a start time. Langfuse and OpenTelemetry spans take a start time | the architecture lens, round 1 | raised | the tracer can back-date from the seconds. P417 decides |
