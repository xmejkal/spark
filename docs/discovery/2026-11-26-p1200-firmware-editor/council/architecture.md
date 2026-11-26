# P1200 council: the architecture lens

Read on 2026-11-26 in the worktree of branch p1200-firmware-editor (base 5fecdbfe). Tags: E is a fact with a pointer.
H is a claim with its source. D is a decision with who and when. The mark — is an unknown. Paths are from the
repository. This file decides nothing. Every option below is the architecture lens's opinion unless it names another.

## Findings

### The seams as I see them

```text
  INTERFACES (thin)          page (TS, one script)        CLI / Claude            MCP later
                             |  RequestChannel (Strategy) |                       |
                             |  DbChannel | (desktop) | (local server)            |
                             v                            v                       v
  RELAY             [ carry-requests ]  <- today prose in commands/page.md:74-101, AR-4
                             |
  CORE                       v
            run-request (key from spark's offer)  +  payload guard for a text edit (AR-2)
                             |
     +-----------------------+------------------------+----------------------------+
     v                       v                        v                            v
  firmware area (no table today, AR-1)          bench area                   flow area
   show-firmware  (reads)                        look   (exists)              show-flow / write-flow-page
   save-firmware  (reads, writes, asks?)         deploy (exists)                reads HOST_FEATURES (AR-4)
   build-image    (wraps flash_image.py)            |
     |                                              v
     v                                        DeployService: plan, look, gate, flash, verify (one pipeline)
  ProjectTimeline.keep_step  (P1193, AR-3)         |            |                |
     |                                             v            v                v
     v                                    FirmwarePlatform   ConsentStrategy   port string
  FolderTimeline (git | none | by-hand)    (Micropython)     (typed | grant |  (/dev/cu.* today,
  KeptRecords row: firmware/main.py                           relayed: shut)    URL port? AR-5)

  SETTINGS (P1194 seam, AR-7): page host · firmware view member · where the deploy runs · page edits on/off
  TOOLS LIST: bytes of a page library (download kind) · flasher, board-shell (programs)
```

### AR-1 · The three features need four Operations, and the firmware area has no table for any of them

- Claim: the catalogue lists eight tables and no firmware table. Its own docstring says it is the one list that
  `--describe` and a later MCP server read. So a firmware job that is no Operation is reachable from no interface but
  its CLI · E scripts/spark/operation_catalogue.py:1-5, :27-30 · E preanalysis.md section 6 table.
- Claim: the convention for an area whose `__init__.py` imports nothing is a `<area>_operations.py` table. The
  firmware area is such an area · E docs/guide/patterns-and-names.md:40 ("An area whose `__init__.py` imports
  nothing (design, records, build, checks, breadboard, firmware) holds its table in `<area>_operations.py`").
- Claim: the features need these Operations. Each is owned by the area that already holds its logic · H, my reading
  of the code below:

  | job | Operation (working name) | area | exists? | effects | pointer |
  |---|---|---|---|---|---|
  | show the firmware and the generated files | `show-firmware` | firmware | no | reads | preanalysis.md:343 |
  | the same text on the page | inside `show-flow`'s FlowReading, through the same firmware reader | flow, reading firmware's reader | no | reads | scripts/spark/flow/flow_reading.py:1-4 |
  | save an edit of `main.py` | `save-firmware` | firmware | no | reads, writes (and asks, if a commit yes is asked) | preanalysis.md:345 |
  | build the image of the edit | `build-image` (wraps `flash_image.py`) | firmware | no, a CLI off the core | reads, runs, writes | preanalysis.md:347 |
  | look at the board | `look` | bench | yes | reads, runs, board, asks | scripts/spark/bench/__init__.py:25 |
  | deploy | `deploy` | bench | yes | reads, runs, board, deletes, writes, asks | scripts/spark/bench/deploy_image.py:458-499 |
  | carry a page click | `run-request` | flow | yes, three steps | reads, runs, writes | scripts/spark/flow/run_request.py:44 |

- Claim: the page's text must come from the one reading, not from a second route. P1038's D22 makes `FlowReading`
  the one read that `show` prints and the page draws. A firmware reader in the firmware area can feed both
  `show-firmware` and the reading, so the text is read once · E flow_reading.py:1-4 · H the shape.
- Claim: the show path must pass the run's Privacy and the secrets mask. The page can be published as shared
  (`shared_live`), and `ProjectSecrets` masks only the values of `firmware/*secret*.py`. A Wi-Fi password written as a
  literal in `main.py` is in no secrets file, so no mask covers it · E commands/page.md:70-71 · E
  scripts/spark/firmware/project_secrets.py:1-12 · H the literal gap, not tested. P1038 D24 already rejects the
  Artifact `files` capability on raw project files for the same kind of reason (preanalysis.md:242-243).
- Claim: a deploy started after a page edit needs `build-image` on the core first. Deploy flashes "the image that
  passed, not the change", and only `flash_image.py`, a CLI off the core, makes an image from `firmware/` · E
  commands/deploy.md:108-113 · E preanalysis.md:102-104, :347.
- Supports only: which Operations and which owner. It does not say any of them should be built now (AR-8).

### AR-2 · A text edit breaks run_request's rule by its nature, so it needs a second guard, not an exception to the first

- Claim: the rule is that the step's values come from spark's own offer, never from the request. The row the page
  writes is `{id, key, seen, at}`. The command tells Claude to "add nothing and change nothing" when it copies it ·
  E scripts/spark/flow/run_request.py:1-5, :171-176 · E scripts/spark/flow/page_script.ts:53-59 · E
  commands/page.md:84-85.
- Claim: an edit's text cannot come from an offer, because spark did not write it. So the rule can hold for the
  key only. Three options:
  - (a) Key from the offer, text as a payload with its own guard. An offer kind such as `firmware-save:main` names
    the file from spark's own list (the conversation's files in `firmware/`, never `pins.py`, never a secrets file,
    never a path from the request). The text travels as one payload Argument. The core already has the shape:
    `Argument.payload` and `cli.load_payloads` (E scripts/spark/core/operation.py:20-25, scripts/spark/core/cli.py:222).
    The guard: (1) a base sha256 of the bytes the page showed must equal the file on disk now, so an edit never
    overwrites a newer write by Claude. (2) a cap on size, UTF-8 and printable lines. (3) the answer never echoes the
    text, as `refused_answer` already never echoes a request (E run_request.py:129-132). (4) the yes of AR-3. Cost: M.
    It also changes commands/page.md step 4.2 and the row's shape.
  - (b) The edit goes back through the chat. The page shows the change with Copy and a sentence "Apply this edit to
    main.py". Claude then saves it through `save-firmware`. Cost: S. It follows P820's "free words go to the chat"
    (preanalysis.md:215-216) and P1194 D17's "an Ask Claude sentence now, one button later" (E
    docs/discovery/2026-11-26-p1194-settings/brief.md:135).
  - (c) The desktop host's `fs` writes the file. Cost: S. It skips the core, so every rule in (a) is written again or
    lost. I reject it under "one core, many interfaces" (AGENTS.md).
- Claim: the fingerprint cannot be the staleness guard for an edit. It reads the needs, `requirements.json` and the
  build record, and nothing in `firmware/`. Adding `main.py` to it would make every pick and build click stale after
  any firmware write. A per-file base hash in the edit is narrower · E scripts/spark/flow/fingerprint.py:17-18 · H the
  side effect.
- Supports only: the shape of the guard. Whether a page edit is wanted at all is D-q2, the PO's.

### AR-3 · One write path for main.py, and main.py as a declared kept record through P1193's one Service

- Claim: today nothing in spark writes `main.py`. The conversation writes it with its own tools, and spark reads
  only its file time · E docs/guide/agents.md:27-29 · E scripts/spark/flow/phase_readers.py:532-542.
- Claim: if the page writes through `save-firmware` and Claude keeps writing directly, `main.py` has two write paths.
  Under P1193 D6 "an outside change said and kept on a yes", each of Claude's writes would then show as changed
  outside spark and ask for a yes · E restore-after-1775:docs/discovery/2026-11-26-p1193-change-tracking/brief.md:117
  · H the noise. Option: Claude also writes through `save-firmware` on the CLI, so the page, Claude and MCP share one
  path. P1194 D8 and D9 ask that every feature be reachable from every interface, at least the CLI (E
  docs/discovery/2026-11-26-p1194-settings/brief.md:126-127). Cost: the agents' contract and the firmware command
  text change. Option: Claude keeps its own tools, and the noise is accepted.
- Claim: P1193 D6 took the synthesis's recommendation for every row, and the synthesis's D-q1 option is (b): each
  area declares its kept records in one table, `KeptRecords`, and `ProjectTimeline.keep_step(kind, words)` keeps a
  step over the lower Strategy `FolderTimeline` · E P1193 brief.md:76, :117 · E P1193 council/synthesis.md:43-49,
  :64-76, :108, :146.
- Claim: no row of P1193 names `firmware/`, so a page edit has no path to a kept step today. `main.py` must become a
  declared kept record, a row the firmware area adds · E preanalysis.md:375-386.
- Claim: `main.py` fits a row more simply than the layout files. C15 keeps `board.tsx` and `breadboard.json` "only
  while the bytes are the person's, with a stamp", because spark also writes them. Spark never writes `main.py`, so
  its row needs no such condition · E P1193 synthesis.md:266 · H the consequence.
- Claim: `pins.py` stays a build output, made again and never kept. Its header says not to edit it · E P1193
  brief.md:18 (D-d) · E scripts/spark/design/pin_assigner.py:484-485.
- Claim: the save calls the same Service as any kept step. P1193 already rules this for a page layout edit: "the same
  Service ... with no second seam" · E preanalysis.md:379-382 (P1193 items.md:56).
- Claim: D14 lets spark commit one named file of a declared kept record after his yes, including a file git does not
  hold yet · E P1193 brief.md:125. — Whether a yes relayed from the page (a click carried by Claude) counts as D14's
  "his yes". The gate treats such a yes as relayed (AR-6).
- Claim: a take-back can split the pair. A take-back of a build step makes `pins.py` again from the older design, and a
  `main.py` kept as its own step may still import a signal that is gone · H, from D-d and the import of `pins.py`
  by `main.py` (agents.md:27-29). Not tested.
- Supports only: where the edit lands. It does not size the KeptRecords table, which P1152 #1688 owns.

### AR-4 · The host's ability is one seam with two halves: a data table spark writes, and a probe the page runs only to hide

- Claim: a check per feature would scatter one fact over many places. The page already gates itself on its host
  inline: it starts only with the Artifact database and only for the owner · E scripts/spark/flow/page_script.ts:452-460.
- Claim: `OfferKind.from_page` is a one-column version of the host table today: a kind is sendable from the page or
  asked in the chat · E scripts/spark/flow/flow_codes.py:146-160.
- Claim: Python cannot know the browser when it writes the page, and the host can change its frame at any time. The
  frame's `allow` attribute was read once, on one artifact, in one browser · E hosts.md:8-19 (H1-1 and its caveat).
- Claim: the page may not decide. P820's no-go: "no logic in the page's script ... decides nothing again" · E
  docs/discovery/2026-11-15-p820-artifact-interface/brief.md:103.
- Option (my opinion): one Value table, `HOST_FEATURES` (working name), with a row per host (Artifact in a browser,
  Artifact as a desktop app, local server, server of spark's own, the page from disk) and a cell per feature (show,
  edit, deploy over this computer's Python, deploy over Web Serial), each `able`, `not able` or `not tested` with its
  evidence. It is the outcome's table itself. The page writer reads it to decide which buttons exist. The docs render
  it, as `StageMarkdownTable` renders the build's stages (E docs/guide/patterns-and-names.md:40). `--describe` can
  list it. The page's script then runs a feature probe (`navigator.serial`, `claude.use("desktop")`) only to hide a
  button the host refused at run time, never to show one the table withholds. One direction, so the probe adds no
  decision. Cost: S for the table, S for the probe.
- Claim: the relay loop is prose, not code. The steps that read the waiting rows, write the request file, run
  `run-request`, write the page and write the answer live in commands/page.md:74-101. A host that carries requests
  without Claude (the desktop app with `childProcess`, a local server) would write that loop a second time · E
  commands/page.md:74-101 · E hosts.md:36-41 · H the duplication. Option: one Operation, `carry-requests` (working
  name), over a Python request channel that mirrors the page's `RequestChannel` Strategy (E page_script.ts:74-79,
  :160-165). The command and every host call it. Cost: M.
- Supports only: the shape. Which hosts are wanted is D-q4, the PO's.

### AR-5 · A browser flasher is a different shape from Flasher and FirmwarePlatform, and only one option keeps the pipeline written once

- Claim: `Flasher.build_commands` returns argv lists, and `DeployService` runs them through `outside.run` with its
  retry and its board log · E scripts/spark/bench/flasher.py:32-34 · E scripts/spark/bench/deploy_service.py:174-185,
  :218-235.
- Claim: every `make_` method of `FirmwarePlatform` returns a Python Adapter over a program on this computer · E
  scripts/spark/bench/firmware_platform.py:38-79, :84-123.
- Claim: the gate's token binds the board and the image that the Python look read · E
  scripts/spark/bench/deploy_gate.py:175-183.
- Claim: in a browser, no Python process sees the port. So esptool-js cannot be one more member of `Flasher` or
  `FirmwarePlatform` without a second pipeline beside `DeployService` · H, from the three facts above.
- Options:
  - (a) The browser holds the port, and Python keeps the whole pipeline. esptool 5.5.0 and mpremote open a port
    through pyserial's `serial_for_url`, so a URL port such as `rfc2217://` could reach a port the page holds over Web
    Serial through a local bridge · E esptool 5.5.0, `esptool/loader.py:455` in the installed package · E mpremote,
    `mpremote/transport_serial.py:70` in the installed package (both read on this Mac, 2026-11-26). `DeployService`
    would then run unchanged with a `port` string, and no stage is written in JavaScript. It needs a local process for
    the bridge, because the Artifact frame blocks a WebSocket to another host (E hosts.md:26-28). — Whether the reset
    lines survive the bridge, and whether mpremote's `connect` accepts a URL. Not tested. Cost: M to L.
  - (b) Python plans and judges, the page only does the I/O. A plan Value names the image's sha256, the chip, the
    offset and the files to check. The page reads the chip and the MAC, erases, writes with esptool-js's MD5 check
    and reads back, and returns the readings. Python judges them. Each stage needs a round trip, and today nothing
    runs until the person types `/spark:page` · E commands/page.md:19-20 · E research.md:70-71 (esptool-js's checks).
    The pipeline stays in Python, with a thin JavaScript executor. Cost: L.
  - (c) The page runs its own look, flash and verify with esptool-js. Every stage is written twice. P218's study and
    P820's no-go both reject it · E preanalysis.md:421-423 (WF-12, WF-15, WF-16) · E P820 brief.md:103. I reject it
    under the PO's DRY line.
  - (d) The desktop app's `childProcess` runs `deploy.py` as it is. No new flasher. Only an artifact of the person's
    own organization gets `"full-access"` · E hosts.md:36-44 (H2-1, H2-2). Cost: S.
- Claim: under every option but (c), the stages stay the one table `DEPLOY_STAGES` and the one Service · E
  scripts/spark/bench/deploy_stages.py:23-29.
- Supports only: the shape of a browser deploy. D-a ("no browser flasher for now") stands until the PO reopens it.

### AR-6 · A yes given on a page stays a relayed yes by construction, and the desktop terminal is a hole in the gate's test

- Claim: a relayed yes never opens the erase. The gate refuses it after the token checks · E
  scripts/spark/bench/deploy_gate.py:117-126, :184-185.
- Claim: every page path today carries the click through Claude, who writes `.spark/page-request.json`. Spark cannot
  tell a person's click from an agent's write. "Never write a key or a `seen` of your own" is an instruction to the
  agent, not a check · E commands/page.md:84-85 · H the consequence.
- Paths that open the erase without changing D-d:
  - (i) A deploy grant the person typed earlier in his own terminal. `StandingConsentStrategy` has `opens_erase =
    True`, and the page's click only starts a deploy inside that grant · E scripts/spark/bench/board_grant.py:243-268.
    P1194 D19 keeps the deploy grant as it is (E P1194 brief.md:137). Cost: none in the gate.
  - (ii) The desktop app's `pty`. `Terminal.live` is `isatty` on stdin and stdout, and a pty is a tty, so a yes in
    that window passes as typed · E scripts/spark/core/replies.py:157-158 · E hosts.md:38-41 · H that a pty passes.
    But the page's own script holds the pty and can write `yes` into it. The gate would then count a scripted yes as
    typed. The gate's docstring says it "guards against a frontend's mistake, not against code in the same process"
    (deploy_gate.py:55-56). Here the code is in another process, so even that line does not cover it. — Whether the
    gate can tell a pty that a page drives.
  - (iii) A new `ConsentStrategy` member with `opens_erase = True`. It reopens D-d (P675) and P218 D19, both the PO's.
- Supports only: which paths keep the gate as it is. It does not say which path the PO wants.

### AR-7 · The settings, and where the tools list fits a member that is a JavaScript library

- Claim: the tools list maps a role to a tool whose `find` returns an argv command. A kind outside `KIND_NEEDS`
  fails · E scripts/spark/records/tool_finder.py:285-325, :541-556.
- Claim: the list already holds members that are no program. The `mcp` kind sits behind three roles, and `find`
  raises `tool_missing` for them. `status` special-cases them · E a run on 2026-11-26 with a temporary empty store
  (removed after): `find("parts-search")` gave `ToolMissingError tool_missing`, `find("flasher")` gave `esptool` · E
  tool_finder.py:333-350.
- Claim: P1193's synthesis names the same gap for its `none` and `by-hand` members, which "need entries of one new
  kind" · E P1193 synthesis.md:127.
- Claim: a page library's bytes fit the existing `download` kind (`file`, `url`, `sha256`). Spark could fetch it once
  into the store and inline it, so the page loads no CDN at view time and the bytes are pinned · E tool_finder.py:541
  (`download` needs `file`, `url`, `sha256`) · H the use. P1038's rules hold: a spark user installs nothing and the
  page compiles nothing at write time (E preanalysis.md:265-267). — Whether the 16 MiB page cap and a ~170 kB editor
  fit together with the images. research.md:33 gives CodeMirror 5's size.
- Claim: which member is chosen is a setting, not a tool. P1194 keeps the tools list's own merge in its first slice
  and moves it later · E P1194 brief.md:133 (D15).
- The settings each choice needs (all proposals, the lens's, until P1194's seam names them):

  | setting | members | default | layer | why |
  |---|---|---|---|---|
  | the page host | artifact, desktop-app, local-server, file | artifact (today's) | project, then user | the published id is per project today, `.spark/page.json` (patterns-and-names.md:40, `PublishedPageStore`) |
  | the firmware view | none (read-only text), textarea with a highlighter, CodeMirror 5, a CodeMirror 6 bundle | read-only text | user | a preference of the person, research.md:32-36 |
  | page edits of the firmware | off, on | off | user | D-q2 is open, and AR-2's guard is not built |
  | where the deploy runs | this computer's Python, the browser | this computer's Python | user, a project may only narrow | D-a, and P1194 D12 and D25's rule for a setting that reaches his board or money (brief.md:130, :143) |

- Supports only: names, defaults and layers to hand to P1194. None is decided.

### AR-8 · The smallest set of seams to build now

- Claim: the epic is after the MVP, and for a website only the seams are built now · D the PO, 2026-11-26, #1748
  (brief.md:18, D-i) · D the PO, 2026-11-25, the git discovery's D12
  (docs/discovery/2026-11-25-spark-and-git/brief.md:129).
- Options, each the lens's:
  - (a) Nothing in code. The host table lives in this folder as a document, and the seams stay names in the design.
    Cost: none. Risk: the table goes stale, as H1-1's caveat says.
  - (b) Two small seams that no later choice changes: the firmware area's `firmware_operations.py` table in the
    catalogue with `show-firmware` (reads only), and the `HOST_FEATURES` Value with `from_page` read from it. Cost: S.
    It proves that a new area joins the catalogue and the page reads the host from one table.
  - (c) (b) plus `save-firmware` with AR-2's guard, `build-image` on the core and `carry-requests`. Cost: M to L. It
    is the base for any page edit and any page deploy, and it touches the MVP's click path.
- Claim: none of (a) to (c) needs a browser flasher, a new `ConsentStrategy` or a server. Those wait on D-q3 and D-q4.

## What I could not check, and why

- No web search ran. The WebSearch tool is not available in this session. The one claim I wanted to check on the
  web (URL ports in esptool) I read in the installed esptool 5.5.0 and mpremote instead.
- Whether a URL port bridged to Web Serial works with esptool and mpremote, with the reset lines. No board, no bridge,
  no test.
- Whether a pty from the Claude desktop app's `pty` module is a tty to Python, and whether a page script can write
  into it. I read only hosts.md's account of the types, not the module.
- Whether a relayed yes counts as P1193 D14's "his yes". No line of P1193 says.
- The P1193 folder is on the local branch `restore-after-1775` (commit 1fb154e2, 2026-11-26 15:10 CET).
  `origin/restore-after-1775` does not exist after `git fetch origin`, and origin/main has no P1193 folder. I read the
  local branch.
- P1193 council/c-answers.md, which holds D6's refinements, I did not read. I read the brief and the synthesis only.
- The size of an Artifact page with an inlined editor, an image and the pictures. No page was written.
- Whether Claude's own writes to `main.py` would really show as "changed outside" under P1193. No code of the project
  timeline exists yet (P1193 brief.md:46).

## Questions for the decider

- Does a page edit come back as text on the page (AR-2 a), or as a sentence for the chat (AR-2 b)? · decides: whether
  run_request gains a payload and a second guard, and the shape of the page's row.
- Does Claude write `main.py` through `save-firmware` too, so the page, Claude and MCP share one path? · decides: one
  write path or two, and the noise of outside changes under P1193 D6.
- Is `firmware/main.py` a declared kept record, and do the other files the conversation writes in `firmware/` join
  it? · decides: the firmware area's row in P1193's KeptRecords.
- Does a yes relayed from the page count as D14's "his yes" for a commit? · decides: whether a page save keeps a step
  at once or asks again in the chat.
- Which path opens the erase for a deploy started on a page: a deploy grant typed before, the desktop terminal, or a
  new kind of yes? · decides: whether D-d (P675) and P218 D19 stay, and whether the gate must refuse a pty a page
  drives.
- If a browser deploy comes back, is it the browser as the port under spark's Python (AR-5 a), or the browser as an
  executor of spark's plan (AR-5 b)? · decides: whether the deploy pipeline stays one, and which hosts can deploy.
- Is the host table one Value that the page writer reads, with a page probe that may only hide? · decides: one host
  seam or a check per feature.
- Which of AR-8 (a), (b) or (c) is built, and when? · decides: the slice of this epic that reaches code.

## Searches

- `esptool remote serial port rfc2217 socket:// URL support documentation` · the decision it served: whether a port
  the browser holds can sit under spark's one Python deploy pipeline (AR-5 a) · not used: the WebSearch tool was not
  available. I read the installed esptool and mpremote instead (AR-5).
