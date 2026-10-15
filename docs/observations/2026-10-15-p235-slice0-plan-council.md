# P235 slice 0 plan: the plan council, 2026-10-15

The first plan council under P257. It read the slice plan in plan mode, before the PO's OK. One lens on Sonnet
(architecture, the user's journey, the PO assistant) and one refuter on Opus, both read-only. The plan:
[docs/2026-10-15-p235-slice0-plan.md](../2026-10-15-p235-slice0-plan.md). Rows AT193 to AT203 in [INDEX.md](INDEX.md).

| row | finding | by | outcome |
| --- | --- | --- | --- |
| AT193 | `reach.py` with no grant breaks D9 ("one gated spark command") unless its scope is said | lens, refuter | acted: D24, the PO runs it at the bench, agents.md lists it only after P253 |
| AT194 | A new port class duplicates `DownloadModeProbe.console()`, which already opens the port with DTR and RTS off | lens, refuter | acted: reuse it, renamed `ConsoleProbe` |
| AT195 | AT187 does not prove the port open is the cure (1 clear case, 1 likely, the rival open) | lens, refuter | acted: the plan says "the likely cure" until P251's proof passes |
| AT196 | The retry came at once, before the restarted port and the firmware were back | lens, refuter | acted: wait for the reset or `ready`, then retry |
| AT197 | Retrying on any BoardUnreachableError also retries a timeout (the code may have run) and a missing port | lens, refuter | acted: retry only on "could not enter raw repl" |
| AT198 | The plan did not say that an exec leaves the firmware stopped | lens | acted: reach.py says so until P252's reset lands |
| AT199 | Counting the retry's own `cured` flag can count a boot that was not silent; no cold-port runs | refuter | acted: the bench protocol counts silent boots apart and adds cold-port runs, in P251's own plan |
| AT200 | `RetryingBoardConnection` (was `RetryingBoardConsole` in the draft) needs a Decorator row that only P255 adds | lens | acted: P255's rows land in P251's PR |
| AT201 | "Console" and "connection" named the same thing (the PO, in plan mode) | the PO | acted: one word, connection; console is what the board prints; the rule "check names when planning" is in his rules file |

Rejected (AT202): swap P251 before P252 (refuter). D10 makes P252 the first story. A new `sim/reach.log` file (lens, AT203) was
dropped: the bench collects `--json` lines into its log.
