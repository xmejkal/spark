# The live-streaming lens (P867 #1234), and the pre-research of the spike P870 #1237

Read on 2026-11-17, 08:40 to 09:10 Europe/Prague. Nothing ran on a board, a port, esptool or mpremote: code, `gh issue
view`, the Artifact runtime's own text and four web pages only. Every design below is an option with its cost. Nothing
is decided.

Tags: E (a pointer), H (where it comes from), D (who, when), — (unknown).

## Findings

### What would be wrong or costly later (d), first

- LV-1 · Nothing in P827 #1185, P828 #1186 or P829 #1187 contradicts a later live stream, and none of the three has to
  change its "Done when". P827 renders `data.phases`, P828 the wiring views, P829 a click's row and its answer. None
  holds the serial port, none reads the bench, and none fixes a transport · E `gh issue view 1185`, `1186`, `1187`
  (2026-11-17); docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md:59, :90-93, :146-153 · supports only:
  "fits as it is" is read from the cards' and the plan's text. No prototype of a live row on the page exists.

- LV-2 · "The project's files are the truth" leaves a place for a live event only if the definition says that an event
  is not state. The plan's sentence is "The project's files are the truth. The page is one renderer of them; `db` holds
  only requests and answers". A live line (a console line, "button pressed") is in no project file and is neither a
  request nor an answer. It does not contradict the first sentence, because it claims nothing about where the project
  stands. It does contradict "`db` holds only requests and answers" if the stream goes through `db` · E
  mvp-plan.md:90-93, :59 (request `{id, key, seen, at}`, answer `{for, status, mark, line, revision}`) · supports only:
  the seam is one sentence in P867's definition (LV-21, proposal 1) and, if `db` is ever the route, a third kind of
  row. It is not a change to a card in Ready.

- LV-3 · A bench node needs no fourth word for "seen live at a time". The reader rule already has RECORDED "with what
  the witness says and when", NONE_RECORDED and NOT_CHECKED, and the architecture lens puts the bench node on exactly
  these three. A live sighting is one more witness: recorded, with its source and its time. What would be costly later
  is a bench reader that knows exactly two witnesses by name (the last sheet, the last deploy) and has no field for
  the source · E scripts/spark/core/outcomes.py:33-49; council/architecture.md:84-92 (AR-9), :183-187 (AR-13);
  brief.md:83 (OQ9 b) · supports only: the seam is a value with `source` and `at`, on the later item "the bench
  witnesses in the flow" (items.md, the last line), which is not filed and not built. A sighting is still what spark
  heard, never what is on the bench now (AR-9's caveat holds for it too).

- LV-4 · "Python writes every word" survives a live value only if the value arrives as a finished row. The plan's
  script "switches panels, steps through the wiring, and writes and shows rows". Showing a row that a Python process
  wrote, masked, is inside that sentence. A script that receives raw bytes or pin numbers and makes a sentence or a
  mark from them ("GPIO4 high" into "the LED is on") is outside it, and so is a script that talks to the board itself
  (Web Serial, LV-14) · E mvp-plan.md:90-93, :135; council/architecture.md:292-294 (AR-17's page bullet) · supports
  only: the rule holds for transports 2, 3 and 4 below when a local Python process is the writer; it does not hold for
  transport 5.

- LV-5 · The plan says "No path and no command line reaches the page or `db`: the page holds keys and masked text". A
  console stream is free text from the firmware. It can hold a Wi-Fi name, an address or a path, and it would reach
  `db` and the page unless it passes `spark.core.privacy` first. The masking is per field today, not per stream · E
  mvp-plan.md:91-93, :101 (`facts` masked by `spark.core.privacy`); scripts/spark/bench/bench_privacy.py (53 lines,
  named, not read in full) · supports only: a cost of the live epic, to name in its one sentence. No card of now
  changes.

- LV-6 · The serial port has one holder, and the code already enforces it. mpremote 1.29 opens with `exclusive=True`,
  `ConsoleProbe` opens with `s.exclusive = True` and answers `KIND_BUSY` (exit 3) when another program holds the port,
  and mpremote says "failed to access" then. So a stream, a look (esptool), a deploy and `live.py` exclude each other
  on one port. A stream that holds the port makes the deploy phase and a look answer "busy" until it lets go · E
  scripts/spark/bench/board_console.py:35-37, :41-53, :97-110; scripts/spark/bench/board_connection.py:21-23; mpremote
  1.29.0 transport_serial.py:52 (cited in board_console.py:36) · supports only: for the phases this means "watch the
  bench" and "deploy" are never open at the same time on one board, and a look restarts the board (rows.md row 5), so
  a look ends a stream. P235's discovery named the rival, one long-lived process that holds the yes and the port, and
  the PO did not pick it (LV-10). Nothing in P867's three shapes depends on this.

- LV-7 · The allowlist of four offer kinds and D9 ("a confirmed click is the yes for the four kinds, never the board or
  a simulation") mean that a page button "start watching the board" would be a fifth kind and a click that reaches the
  board. Opening the port can restart the board (P235 ★C6). That is a decision of the live epic, not of now. P820's
  Q31 (may a page click lead to running live code) is the same question and is still queued · E `gh issue view 1187`
  (D9); docs/discovery/2026-11-15-p820-artifact-interface/brief.md:58 (★C11), :97, :152 (Q31);
  docs/discovery/2026-10-15-p235-live-on-board/brief.md:51 (★C6) · supports only: no contradiction today, because the
  MVP has no such button.

- LV-8 · The contract of `flow.py show` takes a live key as an addition: "New keys beside `phases` and `stands_at` ...
  are additive for a reader that ignores unknown keys, the `data_keys` test must name them". A live stream is not a
  key of `show` at all in any option below; it would be an Operation of its own · E council/architecture.md:278-291
  (AR-17) · supports only: the envelope. Whether an Operation can return a stream is not designed: `OperationResult`
  is one value per run (H, from the bench Operations read here; scripts/spark/core/operation.py not read today).

### What exists today (a)

- LV-9 · Every read of the board that spark has is bounded, and none is a stream. (1) `ConsoleProbe.console()` reads
  the port for `READ_S = 2` seconds with DTR and RTS off and returns `ConsoleReadResult(kind, printed, why)`; the 2 is
  a constant, not an argument. (2) `ReadyProbe` runs `import main` with `keep_running_for=20` and keeps what the board
  printed until mpremote is stopped. (3) `BoardConnection.run_code` returns what `mpremote exec` printed, within 20 s.
  (4) `LiveTryService.run` runs one piece of code inside a grant and then resets the chip. Each call is its own
  subprocess (`subprocess.run`, `capture_output=True`), so the output arrives only when the call ends · E
  scripts/spark/bench/board_console.py:20, :97-110; scripts/spark/bench/ready_probe.py:15-17, :62;
  scripts/spark/bench/board_connection.py:24, :58-69, :87-103; scripts/spark/bench/board_live.py:76-103 · supports
  only: the code. No script in scripts/ is a monitor: `ls scripts/*.py` shows live.py, reach.py, look.py, deploy.py,
  grant.py and no console or monitor command (2026-11-17).

- LV-10 · P235's discovery already decided the shape that the live work has today, and the code matches it: slice 0 is
  reach and read with a reset at the end (D9), one grant typed in the person's terminal and kept in the store (D12;
  "a long-lived process in his terminal" was the option not picked), the look once at the grant (D13), the USB and
  flash pins refused (D14), board-facing code behind a platform-neutral interface (D7), WebREPL and OTA not in the
  first slices (D31, the no-go line). Its ★C12 says "A monitor without an end does not exist", and that still holds
  (LV-9). Its Q10 option B, "a monitor that never restarts the board", has "no way found" · E
  docs/discovery/2026-10-15-p235-live-on-board/brief.md:57 (★C12), :79-80 (Q10), :82, :131-138 (D7, D9, D12, D13,
  D14); scripts/spark/bench/board_live.py:1-15; scripts/spark/bench/board_grant.py (280 lines, its header only) ·
  supports only: what still holds against the code. shape-for-design.md and the council folder of P235 were not
  re-read line by line (part 2).

- LV-11 · The cards that would carry a stream exist, all in Idea: P248 #270 (a bounded console read), P520 #716 (the
  deploy reports later console lines), P350 #446 (the REPL over Wi-Fi), P199 #152 (a live page), P493 #673 (a Walk
  tab), P494 #674 (a spike on the interface to build first), P736 #1012 (one control interface for a running game) ·
  E `gh issue view` 270, 716, 446, 152, 673, 674, 1012 (2026-11-17) · supports only: their titles and state. P248 is
  the nearest to walk 2's row 7.

- LV-12 · Row 7 of the button-and-LED walk says the deploy's REPL line "opens mpremote, which stops main.py until
  Ctrl-D". mpremote 1.29's `repl` command itself sends no Ctrl-C at the open: `do_repl` calls `ensure_friendly_repl`,
  which writes only when the transport is already in the raw REPL. The Ctrl-C is in `enter_raw_repl` ("ctrl-C:
  interrupt any running program"), which `exec`, `run`, `fs` and `reset` use. And the deploy's ready check starts the
  firmware with `exec "import main"` and then stops mpremote after 20 s, so after a deploy the firmware runs inside a
  raw-REPL exec, not from boot · E spark-walks/p711-walk4-button-led/rows.md:11; mpremote 1.29.0 repl.py:59-60,
  main.py:555-558, transport_serial.py:178-179 (the installed package, `python3 -c "import mpremote"` says 1.29.0);
  scripts/spark/bench/ready_probe.py:15-17, :62 · supports only: the row's observation stands (the PO saw the firmware
  stop), its stated cause is not confirmed by mpremote's source. Three causes are open: the port's open restarted the
  board (P235 ★C6), the state the ready check left, or a key typed in the REPL. Which one is — (no bench today). This
  decides what a "read that leaves the firmware running" has to avoid.

- LV-13 · What stops a stream today, from the code: any `mpremote exec`, `fs`, `run` or `reset` interrupts the running
  program (LV-12); each exec soft-resets first unless `resume` is used (P235 ★C4); `live.py` ends with a hard reset;
  a look is an esptool read that restarts the board; and the port's lock refuses a second reader (LV-6). MicroPython
  1.29 drops output that no reader takes within 200 ms (P235 ★C6), so lines printed while nobody holds the port are
  lost, not queued · E scripts/spark/bench/board_live.py:11-13, :91-96;
  docs/discovery/2026-10-15-p235-live-on-board/brief.md:49, :51; rows.md:9 (row 5) · supports only: the 200 ms is
  P235's reading of `usb_serial_jtag.c` for the C6, not re-read today, and not known for the FireBeetle 2.

### The transports (b)

- LV-14 · (1) An MCP server of spark's own. "MCP SSE" as a transport is deprecated: the specification's 2025-06-18
  revision defines two standard transports, stdio and Streamable HTTP, and says Streamable HTTP "replaces the HTTP+SSE
  transport from protocol version 2024-11-05". SSE lives on inside Streamable HTTP: the server may answer a POST with
  an SSE stream and "MAY send JSON-RPC requests and notifications before sending the JSON-RPC response", and a GET
  opens a stream for messages unrelated to a request. Claude Code's own page says "The SSE (Server-Sent Events)
  transport is deprecated. Use HTTP servers instead", and lists stdio, HTTP, SSE and WebSocket · E
  https://modelcontextprotocol.io/specification/2025-06-18/basic/transports (read 2026-11-17);
  https://code.claude.com/docs/en/mcp (read 2026-11-17, through a fetch that summarised the first 100,000 characters) ·
  supports only: the protocol can carry a stream. Takes: P417's MCP half and the MCP SDK (P820's brief, OQ2 c), which
  do not exist; spark has no MCP server (`.mcp.json` lists two third-party servers, P820 ★C9). The revision read is
  2025-06-18; Claude Code's page names a revision 2026-07-28, which was not read.

- LV-15 · What Claude Code does with a stream from an MCP server, from its own pages. A standard MCP server: "Claude
  queries it during a task; nothing is pushed to the session". Progress notifications keep a tool call alive against
  the idle limit and are not described as shown to the model. `list_changed` refreshes the lists. What does push is a
  channel: "A channel is an MCP server that pushes events into your running Claude Code session"; the model receives
  each as a `<channel source=...>` event; "Events only arrive while the session is open"; it is a research preview,
  needs `--channels` at start, accepts only plugins from an Anthropic-maintained allowlist, and a channel of one's own
  needs `--dangerously-load-development-channels`; the official channel plugins need Bun · E
  https://code.claude.com/docs/en/channels (read 2026-11-17, text returned in full);
  https://code.claude.com/docs/en/mcp (read 2026-11-17, summarised; resource subscriptions and logging notifications
  were not in the part read) · supports only: the pages' text. Not tested. A channel event is a turn for the model, so
  a console line per event costs tokens; the pages give no rate limit. This is a route for "tell Claude when the
  button was pressed", not for a page that shows every line. Against AGENTS.md's "a local CLI before a web service or
  an MCP server", it is the setting-switched MCP version, not the first route.

- LV-16 · (2) A local process that holds the port and appends events to a file. It takes one Python process started in
  the person's terminal (the gate checks a real terminal, P235 ★C5), which holds the lock, masks each line and appends
  it with its time. The CLI tails the file. Claude Code reads it with a background command: this session's Bash tool
  has `run_in_background` ("re-invokes you when it exits") and a `Monitor` tool is listed · E this session's tool list
  (2026-11-17); scripts/spark/bench/board_console.py:46-61 (the read loop that such a process would keep open) ·
  H for the rest: no such process exists, and P235's D12 picked the grant over "a long-lived process in his terminal",
  so this reopens Q6's option D with a new reason. Cannot do: reach the Artifact page by itself (★C12: the page cannot
  fetch a local host). It is the base that transports 1, 3 and 4 would each read from. It is the one that fits "free,
  few and local" and "one core, many interfaces" with no new dependency (pyserial is already there, P235 ★C14).

- LV-17 · (3) The Artifact's `db`, and (4) its `room`. The runtime contract is 0.2.96 today, the same number that
  P820's claims cite, and the list of capabilities is artifact, assets, comments, db, dictation, downloads, files,
  mcp, room, sample, self, tts, user. `db` today: "One write at a time per doc, only on change", `onSnapshot` for
  reading, no number for a rate limit in the text. `room` today: "NOTHING persists and messages can drop", it reaches
  "whoever has the page open RIGHT NOW ... plus your publishing session when admitted (kind "agent")", "Send absolute
  state". `mcp`: `host:<name>` for a local MCP server is "Claude app only; else `server_not_connected`", with
  `watchTool` that "polls only via `refetchInterval`". `files`: "reads a Claude Code project's files as the viewer",
  needs a `chan_` project id, "new or just-edited files can lag a few seconds" · E `describe_capabilities` with no
  argument, and with db, room, mcp and files (2026-11-17, contract 0.2.96);
  docs/discovery/2026-11-15-p820-artifact-interface/brief.md:53-59 (★C6 to ★C12) · supports only: nothing in the text
  read today contradicts ★C6, ★C7, ★C9, ★C10 or ★C12; a word-for-word comparison with the text of 2026-11-15 was not
  made, because that text is not kept in the folder. `watch` is not a capability in today's list; it is a tool of the
  server (`watch`, `unwatch`), whose description was not read today. For a stream: `db` persists and both sides can
  write, but each event is a write by Claude (a turn) or by a process that has no documented way in (a local process
  cannot write `db`; only Claude's tools and the page can). `room` fits "what happens now" by its own words, but the
  only local writer it names is the publishing session "when admitted", which P820's Q32 left untested. `mcp` with
  `host:` is the one documented way a page reads a local process directly, in the desktop app only (★C9).

- LV-18 · (5) Web Serial from the page itself. MDN: "Limited availability. This feature is not Baseline because it does
  not work in some of the most widely-used browsers", secure contexts only, a port is asked for on a user's click. A
  `serial` Permissions-Policy directive controls whether a document may use it · E
  https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API (read 2026-11-17, summarised by the fetch) · H: that
  the browsers are the Chromium ones and that an embedded frame needs an explicit allow (the fetch's own model
  knowledge, not the page). Whether the Artifact's sandbox grants `serial` is — (the `guide` pages were not re-read for
  it). Cost against the plans: the page's script would hold the port and make the words, which breaks "Python writes
  every word" (LV-4) and "one core" (the parsing would live in TypeScript); it would also hold the port's lock against
  the CLI (LV-6). It needs no local process and no Claude turn. It is the only option that contradicts the page's rule
  as written.

- LV-19 · (6) WebREPL or a websocket from the board over Wi-Fi, and (7) a terminal view only. (6): P235 ★C9 holds
  ("WebREPL needs Wi-Fi code on the board", mpremote names no network transport), P350 #446 is in Idea and wants the
  passwords asked on the console, and the page cannot open a socket to a board on the local network if ★C12's block
  on other hosts covers websockets (H, ★C12 names `fetch`) · E docs/discovery/2026-10-15-p235-live-on-board/brief.md:54;
  `gh issue view 446` · H: MicroPython's WebREPL page was not read today. It frees the USB port, so it is the only
  option where a stream and a USB deploy do not exclude each other; it costs firmware that the conversation writes and
  a password. (7): a bounded or open read printed in the person's terminal is P248 #270 with a longer time; it takes
  the least (one argument on LV-9's read loop and a thin command), answers row 7 if LV-12's cause allows, and shows
  nothing on the page.

### What each live fact needs on the board (c)

- LV-20 · Console output needs no change to the firmware if the firmware prints: the read with DTR and RTS off takes
  what the board prints. A button pressed, an LED on and a pin high cannot be read from outside while the firmware
  runs: reading a pin with `mpremote exec` enters the raw REPL, which interrupts the program (LV-12), and P250 #272
  (read a pin by name) is that kind of read. So these three are seen live only when the firmware reports them as
  lines, or over a second channel that the firmware serves. spark has one precedent for a word the firmware prints
  and spark reads: `READY` ("ready"), from `spark.firmware.scenario_steps`. What spark can export as facts is the
  pin map (which GPIO is which part's which signal, `firmware/pins.py`), so that a reader labels a line; what the
  firmware prints and when is behaviour, and the conversation writes it · E
  scripts/spark/bench/ready_probe.py:13, :72-74; scripts/spark/bench/board_console.py:43-61; AGENTS.md ("Spark exports
  facts, never behaviour"); P235 brief.md:82 (the no-go "spark writes no firmware logic, for example aiorepl or a REPL
  loop on the board") · supports only: the mpremote route. Whether a line format ("pin name, value") counts as a fact
  like `ready` or as behaviour is the PO's (question 3). P736 #1012 proposes one general control interface for a
  running game "for tests, data and live control", MicroPython first; it is an epic in Idea with a feasibility spike
  as its first piece, and its one fact is that the games loop reads the USB console without waiting
  (`games/app.py:7` in pixel-games, cited by the card, not opened here). It and the live epic ask for the same thing
  from the firmware: a way to report and to take a command while it runs.

### Proposals (e), as proposals only

- LV-21 · Nothing must change now in a card in Ready. The evidence is LV-1 to LV-8: read from the plan, the cards and
  the code, not from a test. Three sentences keep a door open at no cost in code:
  1. To P867's definition (brief.md, under OQ9 or OQ10), one sentence: "The state of a project is read from its files
     and records. A live event (a console line, a pin seen) is never state; it becomes state only when spark writes it
     down as a witness, with its source and its time."
  2. To the later item "the bench witnesses in the flow" (items.md, the last line; not filed): "A witness is a value
     with what it says, its source and its time, so a third witness (seen live) needs no new status word."
  3. To P829 #1187's Notes, one sentence: "The page's script shows a row by its kind and ignores a kind it does not
     know, so a later kind beside request and answer needs no change to the rows of now." Whether the plan's rows
     already sit in separate collections was not checked (part 2); if they do, the sentence is already true and is
     dropped.
  · H this lens · supports only: sentences to weigh. Each is a proposal, and the third touches a card the PO ordered.

- LV-22 · The live epic, one sentence (plans shrink with distance): "Live on the board, on the page: done when the PO
  presses the button on a wired project and sees the firmware's line in his terminal and on the project's page within
  a stated time, with the firmware still running, and a look or a deploy says who holds the port." Needed by: "so if I
  want to be able to see live REPL or output ... It could then also show live on the artifact page whateverr is
  currently happening, like a button pressed, console ouput, led on, pin high" (the PO, 2026-11-17, #1237). It is
  P235 #224 itself, or a child of it · H this lens.

- LV-23 · New cards, one line each, none filed. (a) A bench row for the spike P870 #1237: which of LV-12's three causes
  stops `main.py` at the deploy's REPL line, and whether a read with DTR and RTS off for 60 s leaves the firmware of
  the button-and-LED walk running; needed by: "how would we do it?" (the PO, 2026-11-17, #1237). (b) A desk row for
  the same spike: whether `room` admits a local Claude Code session and whether a development channel delivers a line
  to this session; needed by: "MCP SSE? other ideas?" (the PO, 2026-11-17, #1237). This is P820's Q32 again. No other
  card is needed now: P248 #270, P520 #716 and P350 #446 already hold the first slices · H this lens.

- LV-24 · Order. P827, P828 and P829 keep their order, and so do P867's six proposed items. One reorder to weigh:
  P248 #270 (a bounded console read) answers row 7's "a walk that checks a must line on the bench needs a read that
  leaves the firmware running", and the walks start over only after the gaps of the three walks are fixed (D-c, #1236).
  So P248, with LV-23 (a) before it, belongs with P869 #1236's fixes or right after them, before the new walks, and
  not behind the whole Artifact page. It needs none of the transports 1, 3, 4, 5 or 6 · E rows.md:11; brief.md:18
  (D-c); `gh issue view 270` · H for the order itself.

## What I could not check, and why

- Anything on a board: which cause stops `main.py` in row 7, whether a long read with DTR and RTS off leaves the
  firmware running, the 200 ms drop on the FireBeetle 2. Another session held the USB port, and the rules of this read
  forbid it.
- Whether the Artifact page's sandbox allows Web Serial or a websocket to a local address: the `guide` pages were not
  re-read today, and no page was published.
- Whether `room` admits a local Claude Code session, and whether a channel of spark's own registers on the PO's plan:
  both need a test (P820's Q32 is still queued).
- The `db` rate limit as a number: today's `describe_capabilities db` gives none, and `db_usage` was not called.
- What changed in the runtime's text since 2026-11-15, word for word: the contract number is the same (0.2.96), but
  the text read on 2026-11-15 is not kept in P820's folder.
- The MCP specification's newest revision (Claude Code's page names 2026-07-28), resource subscriptions and logging
  notifications in Claude Code: the fetch of code.claude.com/docs/en/mcp covered the first 100,000 of 156,911
  characters, as a summary.
- MicroPython's WebREPL page and MDN's Permissions-Policy page for `serial`: not opened, the time went to the code.
- P235's shape-for-design.md and its council folder, P867's council/refuter.md beyond a search for "bench" and "live",
  scripts/reach.py, board_look.py, board_grant.py and deploy_gate.py in full, and the collection paths of P829's rows
  in mvp-plan.md.
- P736's claim about `games/app.py:7`: the pixel-games repository was not opened.

## Questions for the decider

- Is a live event ever state, or only a witness once written down (LV-2, LV-3)? · decides: whether P867's definition
  gains the one sentence of LV-21 (1), and whether the bench node stays at three words.
- Who holds the port during a live session: one long-lived process in your terminal (P235's Q6 option D, not picked
  on 2026-10-15), or bounded reads that let go between calls? · decides: whether a look, a deploy and a stream share
  one holder or exclude each other (LV-6), and the base of transports 1, 3 and 4.
- May spark name a line that the firmware prints for a pin or a button, as it names `ready`, or is every such line
  behaviour that only the conversation writes (LV-20)? · decides: whether a button, an LED and a pin can be shown
  live at all without P736's control interface.
- Is the first live view the terminal (P248 #270, before the new walks) and the page later, or the page first? ·
  decides: the order of LV-24, and whether any Artifact transport is researched before the page's MVP is done.
- May a click on the page start anything that touches the board, such as opening the port (LV-7, P820's Q31)? ·
  decides: whether the live epic needs a fifth offer kind or starts only from the terminal.
- Is the desktop app an acceptable place for the page's live view (`mcp` with `host:`), or must it work in a browser
  (LV-17)? · decides: whether transport 1 is a candidate for the page at all.
- Should the two rows of LV-23 run inside P870 #1237 now, with the bench free, or wait for the epic? · decides:
  whether the pre-research ends with this read or with a test.

## Searches

- none (no web search was made; four pages were fetched directly, listed below with the decision each served)
- "https://modelcontextprotocol.io/specification/2025-06-18/basic/transports" · whether "MCP SSE" is still a transport (LV-14) · used
- "https://code.claude.com/docs/en/mcp" · what Claude Code shows of a stream while a tool runs (LV-14, LV-15) · used, in part
- "https://code.claude.com/docs/en/channels" · whether an MCP server can push an event into a local session (LV-15) · used
- "https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API" · whether the page itself could hold the port (LV-18) · used
