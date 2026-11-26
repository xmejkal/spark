# C1 to C18: the council of three on Fable

Delegated by the PO's standing rule for an away session (spark-main's brief, 2026-11-26), and the PO's to change.
Seats on Fable: the PO assistant, the architect and the tech lead, one written brief (`c-brief.md`), run 2026-11-26
between 09:32 and 09:34 CET. Every seat chose the synthesis's recommendation for every question, so each answer is
3 of 3. The seats added the refinements below. A refinement from one seat is the council's proposal for the design,
not a vote.

| # | Answer (3 of 3) | Refinements from one seat | PO only |
| --- | --- | --- | --- |
| C1 | One lower Strategy under two Services. `ProjectTimeline` becomes a Service, `FolderTimeline` is the working name below it, words.md:21 is amended | The architect: `send` and `receive` go on a second small interface that only a member with a remote fills, named by the `shared-records` role's contract (scripts/spark/records/tool_finder.py:300-302). The first interface keeps the project's verbs only | none |
| C2 | Two roles in the tools list, `none` as a Null Object member, one new kind for a member that is no program | The tech lead and the architect: six kinds exist today, not four (`KIND_NEEDS`, tool_finder.py:542-545), and each role needs a contract row, because `use` checks nothing without one (tool_finder.py:535). The architect: `on: false` on the one git entry raises `TOOL_OFF` for both roles (tool_finder.py:306), so `none` on the role is the only documented way to turn project keeping off | none |
| C3 | The by-hand member says what to copy and keeps nothing first. A copying member is a later class | The architect: it returns the paths as data for a Renderer, and answers "cannot say" | none |
| C4 | Plain words: "name this point", "back to <name>", "share", "get shared parts". Never tag, mark, pull, push, pin or snapshot | — | none |
| C5 | Every new Operation name carries "kept-step" or "shared" whole | — | none |
| C6 | A new effect word, `sends` | The architect: a receive declares `fetches`, and `NETWORK` is computed from `fetches` only (scripts/spark/operation_catalogue.py:32), so it must also list `sends`. The tech lead: add it with the share slice | none |
| C7 | An outside change is said, and kept on a yes. A record with no stamp says "cannot tell". Nothing is stamped silently | The architect: the seam's three answers stay three, and the docstring at scripts/spark/build/ignore_list.py:32 changes | none |
| C8 | The next reading, no folder watcher | — | none |
| C9 | P1160 Q4 stays until the A2 spike has a result, with the refusal shown in the list before the person picks a point | The architect: the answer lives in the Service's preview, so a later flip costs one method | the pass line that decides it (P9) |
| C10 | A named point is a name on a kept step | — | none |
| C11 | Merge is paused as a proposed no-go, and P1160 Q3 stands | The architect: `merge_preview` is built only when the take-back slice needs the dry check | the confirmation (P8) |
| C12 | A receive stands beside a local record and never overwrites it. Order: project, shelf, library, shared, catalog | — | none |
| C13 | An allow-list of fields, and a closed `made_by` set before a picture is shared | The architect: the allow-list is data per record kind, beside the record's contract, read by one filter class | which text may leave (P1), the traced drawing (P4) |
| C14 | The `origin` block before the first share. The first receive needs only `id` and the digest | All seats: this rests on reading, CH-70's experiment was never run | none |
| C15 | board.tsx and breadboard.json are kept only while the bytes are the person's, with a stamp, decided at slice 5 | The architect: the row reuses the build's own test of whose bytes they are (`_spark_wrote`, scripts/spark/build/kept_files.py:111) | none, but it reopens the delegated P1160 Q2 |
| C16 | `kept_step.id` stays the member's id, the Service lists the ids it made, and a named point is a ref of spark's own | The architect: the id is opaque above the seam, and the member's `points` answers which steps spark made, with no second id file. The PO assistant: the preview says that a named point stays on one machine. The tech lead: P1155's spike confirms it against a host's squash | none |
| C17 | `GitRunner` moves onto `outside.run` later | The architect: before the first `send` slice, and until then `GitRunner` takes its process starter through its constructor, and a test pins that each Operation that builds the git member declares `runs`. The PO assistant: file it as a card | none |
| C18 | D12 does not forbid a hosted repository: a git host is an outside tool, not spark's server | — | none |
