# P1038 council: the tech lead (Feasibility, fit with the technical direction, spark-process)

Read-only. Written 2026-11-23 by the tech lead agent (Opus) for the P1038 discovery. Read: brief.md, jobs-and-journeys.md,
scripts/spark/flow/*, scripts/flow.py, scripts/spark/core/{events,renderers,operation,outside,cli,describe_operations}.py
(their headers), scripts/spark/bench/{deploy_service,record_deploy}.py and scripts/spark/records/deploy_record_store.py
(their headers), commands/page.md, docs/guide/map.md, tests/test_flow_page.py:80-88, the cards #1521 (with comments),
#1196, #1187 and #1105 (body and comments), docs/discovery/2026-11-15-p820-artifact-interface/{brief,mvp-plan}.md, the
walk project ~/Development/spark-walks/p934-display2 (file list, page.html without its data URIs, one board log),
the Artifact server's guide topic "pages" and describe_capabilities for files, db, sample, artifact and room
(contract 0.2.98), and the text of anthropics/skills@frontend-design. One command ran on the walk project:
`flow.py show`, which reads and writes nothing. `flow.py page` was not run, because it writes page.html.

## Findings

### Why the page shows a stand that does not match the project (★C1)

- TECH-1 · ★C1 has two separate causes, and no page direction fixes the first: (i) the core does not know the deploys,
  (ii) the published page is a snapshot. A restyle, a state document, a live read or a static host each change only
  (ii). · E (i) TECH-2 and TECH-3 · (ii) TECH-4 · supports only: the direction choice and the reader fix are two
  decisions. Each direction (a) to (d) inherits ★C1 until the readers know the deploys.
- TECH-2 · The deploy phase is hard-coded as not started. `DeployReader.read` returns `NOT_STARTED` with two fixed
  sentences, and it reads no file. · E scripts/spark/flow/phase_readers.py:554-560 · supports only: the page cannot show a
  deploy, whatever the project holds.
- TECH-3 · The guide puts NOW on the first open phase. The build counts as done when Wokwi has no model of the board.
  The firmware has no status, so it is not open. The deploy is always open. So every project that gets past the
  firmware stands at deploy for ever. The code says so: "The deploy is never done here, so there is one". · E
  scripts/spark/flow/guide.py:80-89 (now_phase and its docstring), :49-56 (no_model_phases) · `flow.py show --project .`
  in p934-display2, 2026-11-23 (`NOW (deploy): When the breadboard is wired, plug the board into USB…`, `DONE: … build (no
  simulation), breadboard (spark cannot see it), firmware`) · supports only: TECH-1 (i).
- TECH-4 · The published page is a copy, and only `/spark:page` writes it again and republishes it: the publish step and
  each carried request. A deploy run outside the page (deploy.py) does not republish it. · E commands/page.md:19-66, :87;
  write_flow_page.py:139-155 · supports only: TECH-1 (ii).
- TECH-5 · The facts that a deploy reader will need exist. Some are in the project and some are in the store. In the
  project: one board log per deploy in sim/runs/board/<time>.log. Each log has a header with the time, the port, the
  image's sha256, the simulation and a ready line ("ready seen", "ready not seen" or "ready unknown"). In the store: one
  record per board, keyed by its MAC. · E deploy_service.py:65-71 (write_board_log) · ready_probe.py:38 · p934-display2
  sim/runs/board/2026-11-23T14-09-49.log lines 1-6 · deploy_record_store.py:1-10, :94-102 · supports only: a deploy
  reader can be built from the project's own logs. The store's record needs the board's MAC, and the logs read here hold
  none (`grep -il mac` on the 27 logs: 0 files).
- TECH-6 · The project's sim/runs/ is gitignored. So the deploy facts exist only on this machine's disk. A page built
  from the git tree, or a static host fed from git, will not see them. · E p934-display2/.gitignore (`sim/runs/`) ·
  supports only: (d) and any CI-built page need the core's state written out first. They cannot read the logs from the
  repository.
- TECH-7 · The gap is known, but no open card owns it. P793's last comment names it for "piece 6": "the deploy phase never
  ends (DeployReader is always not-started)". P1034, core piece 2, is closed. A search for an open card for piece 6
  found none. · E #1105 comment 2026-11-23T14:17:14Z · #1517 CLOSED · `gh issue list --search "piece 6 in:body"` (none) ·
  supports only: a card for the reader fix, if the decider wants one (PROC-3).
- TECH-8 · The firmware and the simulate phases carry no judgement by design. The firmware phase says only the file's
  time, and the simulate phase reads sim/wokwi.toml. In the walk project the simulate phase says "No simulation files
  yet (sim/wokwi.toml)" while sim/flash-with-firmware.bin is there. The project's bench facts, decisions and battery
  (★C3) live in files that no reader reads: .spark/project.json `decided`, docs/*.md and diary.md. · E
  phase_readers.py:516-551 · `flow.py show` output above · p934-display2 `ls sim` and .spark/project.json · supports only:
  "the project's own facts" (the Outcome) needs new readers or a new section, whichever direction is chosen. Each one is
  a record that grows by need (AGENTS.md, "Records grow by need").

### How the page is built today

- TECH-9 · One core path feeds three frontends. `phases_of` → `guide_of` → `ShowFlow` (CLI text and `--json`),
  `WriteFlowPage` (page.html) and `RunRequest` (the page's click). The page is a pure render of
  `FlowPage(title, phases, stands_at, pictures, notes, wiring, fingerprint, written, guide)`, masked by `Privacy` before
  and after the render. · E show_flow.py:67-82 · write_flow_page.py:139-155 · flow_page.py:41-42, :230-271 · supports only:
  the state the page needs already exists as one value in Python. Its JSON half (phases, stands_at, fingerprint, guide)
  is already `flow.py show --json`'s data. The wiring and the pictures are not in that JSON.
- TECH-10 · The page's records: .spark/needs.json, requirements.json, .spark/build.json (these three also make the
  fingerprint), breadboard.md and dist/board/built-from.json, firmware/main.py (its time only), sim/wokwi.toml and
  sim/runs/*.log, the store's drawer and records (picks and holds), breadboard.svg, and the kept schematic and PCB SVGs.
  · E phase_readers.py:84-560 · fingerprint.py:17-18 · write_flow_page.py:51-56, :91-115 · supports only: the list that
  any state document or live read must cover. The store part is outside the project folder.
- TECH-11 · The page holds no logic of its own. Python writes every word into an inert JSON block. The one script adds
  buttons only when `claude.use("db")` resolves and the viewer is the owner. From disk, or with no `window.claude`, it
  does nothing. A test pins this: two `<script>` tags, and no "http", `<button>`, `<input>`, `onclick` or `<iframe>` in the
  markup. · E page_script.js:1-9, :317-333 · flow_page.py:273-280 · tests/test_flow_page.py:80-88 · supports only: the page
  already works as a static, read-only file (H1 in brief.md becomes E for "it renders with no host"). The test also
  blocks any web font or CDN link that a restyle might want (TECH-22).
- TECH-12 · The request channel is already a Strategy with one adapter (`DbChannel`). The server side is the Operation
  `RunRequest`, which takes a key from any source and checks it against the offers now. · E page_script.js:70-113;
  run_request.py:131-173 · #1196 Notes ("Already neutral") · supports only: the click path (P829, out of scope) does not
  tie the page to the Artifact more than the channel adapter does.
- TECH-13 · Size: 714,020 bytes on disk. Without its data URIs it is 106,576 bytes, a python count that keeps the inline
  breadboard SVG. Each republish sends the whole file. · E python count over p934-display2/page.html, 2026-11-23;
  commands/page.md:62-66 · supports only: a split into files (TECH-16) cuts what each republish sends. The brief's 43.6
  KB for "the rest" excludes the inline SVG too (C2). Both counts hold.

### What each direction takes and touches

- TECH-14 · (a) Keep one file and restyle it. It touches FlowHtmlPage's TOKENS and STYLE, the order of the sections
  (`_body`, `_guide`, `_rail`), flow_codes' words, tests/test_flow_page.py (1,549 lines) and the mutation rows p949-page-look,
  p977-page, p827-flow-page and p828-wiring-page. It needs no new capability and no new route. It does not touch (ii)
  freshness or (i) the readers. · E flow_page.py:242-271 · `wc -l tests/test_flow_page.py` · `ls tests/mutations` · H size
  S to M per piece, the tech lead's estimate from the file sizes · supports only: (a) is the cheapest, and it leaves ★C1
  as it is.
- TECH-15 · (b) A state document that the core writes and several views render. The data exists (TECH-9). Two shapes are
  possible, and they differ in cost and fit:
  (b1) The core writes .spark/state.json (or answers it, as `show --json` already does), and Python still renders the
  HTML from the same value. This adds a file and no renderer.
  (b2) A JS page renders the JSON. This is a second renderer of the same state, beside FlowHtmlPage. It goes against
  "Python writes every word, the script only…" (mvp-plan.md:89-92 · page_script.js:6-8) and against W16 (two formats for
  one thing), unless the Python HTML renderer is deleted in the same change. Then the disk view breaks: TECH-17.
  · E as cited · H the split into b1 and b2 is the tech lead's · supports only: b1 is cheap and fits "one core". A stored
  file is only as fresh as its last write, so b1 alone does not fix TECH-1 (ii).
- TECH-16 · (b) on the Artifact. A page published from files may load its own files by relative path. A republish in
  patch mode changes only the files it names. So a small state.json, and the pictures as files, can be republished
  without the 714 KB HTML. Each republish still needs Claude, through an MCP tool and a `base_version`. · E guide topic
  "pages", 2026-11-23 ("A page published from files may also load its own files by relative path" · "put any dataset over
  about 100 KB beside the page as a .csv file, or a .json file … and fetch() it") · publish_files tool description
  ("patch (default): only the files named change") · H whether an `<img src="breadboard.svg">` of the artifact's own
  file loads is not read. The guide's image line lists only data: and blob: URIs. · supports only: a cheaper republish.
  It does not give a push.
- TECH-17 · (b2) or (c) break the page from disk. A page opened from file:// cannot fetch() a JSON file beside it in
  Chrome, so the disk page (`flow_page.py`'s docstring: "readable from disk") will need the state inlined as well. · E
  MDN "Reason: CORS request not HTTP", https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors/CORSRequestNotHTTP,
  read in search results 2026-11-23 · flow_page.py:1-7 · supports only: keep the state inlined in the HTML, as today's
  words block is, and treat a fetched file as an Artifact-only addition.
- TECH-18 · (b) with db as the live channel. Claude can `db_write` a state doc and the page can `onSnapshot` it, so an
  open page updates with no reload and no republish. This is the one documented push from Claude's session to an open
  page. Two things stand against it. D10 says "db rows hold no drawer facts", and the parts phase's sentences carry
  drawer holds ("held by reaction-game"). And the db text says "No secrets · shared data is untrusted". · E
  describe_capabilities db, 2026-11-23 · P820 brief.md:183 (D10) · `flow.py show` parts line in p934-display2 · supports
  only: a live page through db needs D10 to change or a state doc with the drawer facts left out. Either is the PO's
  call.
- TECH-19 · (c) A page that reads the project live through `files`. It needs: a Claude Code project id ("chan_...")
  known when the page is declared · a viewer in the organisation (else `null` or `not_found`) · a publisher who is a
  project member. Reads can lag "a few seconds". It reads raw files, so either (c1) the page computes the state in JS,
  a second copy of phase_readers.py (566 lines) and guide.py (197 lines), against "one core" · or (c2) the core writes
  .spark/state.json and the page reads only that file, which is (b1) with `files` as the transport. The store (drawer,
  deploy records) is outside the project, so `files` cannot read it. · E describe_capabilities files, 2026-11-23;
  `wc -l` on the two modules · deploy_record_store.py:1-10 · supports only: (c2) is the only shape of (c) that keeps one
  core. Its freshness is the core's last write, the same as (b1).
- TECH-20 · (c) and privacy. `files.read(path)` reads any path of the project as the viewer, with no spark `Privacy`
  mask. The walk project holds firmware/wifi_secrets.py (gitignored · not opened by me). .spark/build.json and the logs
  may hold home or store paths that the page masks today. · E p934-display2 `ls firmware` and .gitignore;
  write_flow_page.py:123-155 (masked_page, and masked again after the render) · describe_capabilities files ("Don't copy
  file contents into the artifact's data … anyone it's shared with can read them") · H that build.json or the logs hold
  home paths: not read · supports only: (c) will weaken "must not get worse: the privacy of the page" (brief.md
  Start and reach), unless the page reads only a masked state file that the core writes.
- TECH-21 · (d) The same page on a static host, read only. The page renders with no host (TECH-11), so the code cost is a
  publish route only. GitHub Pages: on GitHub Free it serves only public repositories, and a site from a private repo is
  public unless the organisation is on Enterprise Cloud. So the drawer counts and holds (D10: "go with any share"), the
  names of other projects and the masked text become public. The deploy facts are gitignored (TECH-6), so CI cannot make
  the page: the local core must write it and push it. · E page_script.js:320-323 · GitHub Docs "About privately published
  GitHub Pages sites" and "Creating a GitHub Pages site", read in search results 2026-11-23,
  https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/about-privately-published-github-pages-sites ·
  supports only: (d) is cheap in code and costly in privacy. It serves P834 (another host). It brings no live state and
  no buttons.

### Fit with the technical direction

- TECH-22 · "Free, few and local". (a), (b1) and (d) use no new service. (b) on db, (c) and the Artifact itself depend on
  Anthropic's host. That was Q10 of P820, and it stayed queued there. A restyle that loads a web font breaks D7 and the
  test in TECH-11. Fonts can be inlined as data: URIs (the Artifact guide allows it), at a size cost on every republish. ·
  E P820 brief.md:131 (Q10 queued), :180 (D7) · tests/test_flow_page.py:87-88 · guide "pages" (Fonts) · supports only: a
  graphic style that keeps system fonts, or inlines a font, keeps D7.
- TECH-23 · "Facts, not behaviour". Every direction keeps the page a renderer of facts. (c1) and (b2) move the logic, or
  the words, into JS, which is a second core rather than behaviour. · E TECH-15, TECH-19 · supports only: a ranking on
  this rule: (a) = (b1) = (c2) = (d) > (b2) > (c1).
- TECH-24 · Ready for streaming and async (the PO's rule on P793, 2026-11-23 11:54Z: "ready for streaming … work async,
  notify when things happen"). The core has an event seam: `Event` (LINE, BEGIN) through `outside.report`, with a
  TerminalReporter. The flow's Operations report no events. A build run by `run-request` reports to the terminal, never to
  the page. On the Artifact, the paths to an open page are a db snapshot (TECH-18) or a republish, which reloads every
  view (the `artifact` capability). `room` admits "your publishing session when admitted (kind agent)", but this
  session's claude-artifacts tools include no room tool. · E core/events.py:1-4, :40-65 · `grep report( scripts/spark/flow/`
  (none) · describe_capabilities artifact and room, 2026-11-23 · the deferred tool list of this session · supports only:
  (b) is the direction that keeps the door open: one state value that the core emits on each change, and a reporter per
  host. (a) and (d) are snapshots. (c) is a pull.
- TECH-25 · The eight option families (#1521's second comment). Today's code follows: (1) a core of scripts with a stable
  `--json` envelope and thin views (flow.py → run_cli · ShowFlow, WriteFlowPage, RunRequest) · (2) partly ports and
  adapters (Operation and OutsideWorld, Strategy readers, Renderers, the JS RequestChannel with DbChannel) · (7) skills as
  folders of text (commands/page.md carries the publish and request loop as prose). It does not follow (3): no state
  document is stored, and the page inlines its state. It does not follow (5): spark has no MCP server, and .mcp.json
  lists only espressif-docs and jlcpcb. (4), (6) and (8) are absent. · E scripts/flow.py:9-20 · core/operation.py:1-4;
  page_script.js:70-76 · commands/page.md · .mcp.json · supports only: the needs per direction: (a) (1)+(2)+(7) as today;
  (b) adds (3) · (c) adds (3) as c2, with the Artifact runtime as a client that reads files, close to (4) · (d) (1)+(3) as
  a static snapshot. (5) is optional for each: an MCP resource could serve the same state value. No direction needs (4),
  (6) or (8).
- TECH-26 · The P820 finding in P793 names the fat interface: the commands hold the loop. commands/page.md runs
  db_query, writes .spark/page-request.json, runs run-request, republishes and runs db_write, all as prose. Any direction
  that adds a step (state.json, a db state doc) adds prose there, unless an Operation owns it. · E #1105 comment
  2026-11-23T11:45:52Z ("The commands are the fat interface") · commands/page.md:68-93 · AGENTS.md ("An agent prompt never
  repeats its logic") · supports only: a design that moves the "what to republish" rule into the core's answer, so the
  command only carries it.

### Artifact capabilities and limits that matter (contract 0.2.98)

- TECH-27 · Scripts load only from the listed CDNs. Stylesheets come only from fonts.googleapis.com. Images are data: or
  blob: only, and remote images do not load. fetch goes only to the artifact's own files. The frame refuses alert,
  confirm, prompt, downloads the page starts, and clipboard reads. A plain `#name` hash route works, and the page's
  step links (`#step-3`) fit it. `claude.use(x)` resolves null with no host, which the script already handles. · E guide
  "pages" and describe_capabilities preamble, 2026-11-23 · flow_page.py:154-173 · supports only: the current page meets
  these limits. A design must keep its own dialogs (it does, page_script's confirm) and keep `#name` anchors.
- TECH-28 · The capabilities that matter, ranked by need: `db` and `user` (today: requests and answers · possibly a state
  doc, TECH-18) · files in the publish (TECH-16) · `files` (TECH-19, with its preconditions) · `artifact` (the page
  republishes itself on a viewer's action, which does not fit a state that Claude changes) · `sample` (asks Claude from
  the page: memoryless, with a consent prompt · nothing in the page's jobs needs it) · `room` (no persistence, and no tool
  for this session). · E describe_capabilities for each, 2026-11-23 · supports only: no direction needs a capability
  that is not documented. (c) depends on the one whose preconditions are unknown here (TECH-31).

### The design skill anthropics/skills@frontend-design

- TECH-29 · The skill is one text file plus its licence. SKILL.md is 9,390 bytes (sha a5333457…), Apache-2.0, last
  commit 41bbe19d on 2026-09-03. It has no scripts and no tools of its own. It asks a two-pass process: a token plan
  (4–6 named hex colours, typefaces, ASCII wireframes, principles), a review of the plan against the brief, then the
  code and a self-critique with screenshots "if your environment supports it". It lists the generated-page tells: all-caps
  labels, meta joined with middle dots, the SaaS card kit, cream with terracotta, a "→" on buttons. · E `gh api
  repos/anthropics/skills/contents/skills/frontend-design/SKILL.md` (decoded), `…/LICENSE.txt`, `…/commits?path=…`,
  2026-11-23 · supports only: what it adds to the page work is a design-plan step and a list of tells to check. What it
  asks of the tools is a way to take screenshots (the Chrome extension or a headless browser) and nothing else.
  Installing it copies text. It runs nothing.
- TECH-30 · Where the skill and spark's rules meet. (i) It asks for "deliberate" typefaces. D7 and the test forbid web
  loads (TECH-22), so a typeface must be a system stack or inlined. (ii) It says the designer writes the copy. In spark,
  flow_codes and the readers write every word, so copy changes are flow_codes changes with their tests. (iii) Today's page
  uses the patterns it calls tells: "NOW", "DONE", "LATER" and "SET ASIDE" as all-caps labels, and middle dots as the
  idea's mark. (iv) Licence: Apache-2.0, so vendoring its text into spark will put a vendor file in the repository,
  against AGENTS.md "Never commit a vendor file". An install at user level, or a /spark:setup line that installs it from
  its source, does not. · E flow_page.py:320-333 and flow_codes GUIDE_* (rendered in page.html: "NOW (deploy)", "DONE",
  "LATER") · phase_readers.py:32-34 (`None: (None, "·")`) · AGENTS.md (vendor rule) · supports only: the install question
  on #1521 (user level, /spark:setup, or both). Under (b), /spark:setup offers to install it and spark does not ship it.

### Spark-process extension

- PROC-1 · The reader fix (TECH-2, TECH-3) is a story under P793, not under P1038. It changes the core's flow, which CLI
  `show`, the guide and `next` share. P793's comment already holds it for "piece 6", and P1038's scope says "out: the
  storage seams, P1039's questions". · E #1105 comment 2026-11-23T14:17:14Z · brief.md Scope · supports only: the decider
  can put it under P793 and keep P1038 on the page. Folding it into the page design will hide a core change inside a
  page epic.
- PROC-2 · A change to the page's look touches pinned tests and mutation rows. tests/test_flow_page.py (1,549 lines),
  tests/flow_script/page_script.test.js (298 lines) and the rows p827, p828, p829 (four files), p949 and p977. W3: a PR
  that adds logic writes its rows and proves them with `tools/mutate.py --anchors`. W2: a restyle is checked by running the
  page, not by reading it. · E `wc -l` · `ls tests/mutations` · scrum/WORKING_AGREEMENTS.md:39-78 · supports only: the size
  of each story · the frontend-design skill's screenshot pass is a natural W2 check, if a browser tool runs.
- PROC-3 · A card exists before work starts (W19). The reader fix has no open card (TECH-7), and P793 counts in no stage
  as an epic (W6). A story filed for it in the spark lane counts against the lane's limits: Ready 4, Build 3, in flight 5.
  · E scrum/WORKING_AGREEMENTS.md:83-92, :238-250 · supports only: filing it waits on the decider's yes to items.md (the
  brief's Decisions rule), not on this report.
- PROC-4 · W16 ("a replacement deletes what it replaces, in the same commit") applies if (b2) or (c) replaces the Python
  HTML renderer. Two renderers of one state will be "two formats for one thing". · E scrum/WORKING_AGREEMENTS.md:231-236
  · supports only: (b1) and (c2) add a file and replace nothing. (b2) must delete FlowHtmlPage, or say why both stay.
- PROC-5 · Review depth by the rules: a design or an epic gets the full council, and the architecture lens and every lens
  of a design run on Opus. The page design is a design, so this TRIO discovery feeds a later full council
  (brief.md "Decision needed"). · E CLAUDE.local.md "Review by what the change holds" · #1521 first comment ("spark-main
  runs the architect and the full council on the design") · supports only: the order of the steps. No finding here is a
  decision.
- PROC-6 · The README journey rule. If the page step's status or note moves (for example "the page shows the deploys"),
  the README's "What works today" and tools/journey.py change in the same PR, and tests/test_journey.py fails on a stale
  picture. · E AGENTS.md "Keep the journey current" · supports only: the PR list of the stories that come out of this
  epic.

## What could not be checked, and why

- Whether a local Claude Code session has a "chan_" project id that `files` accepts, and whether a page declared with it
  reads a folder outside the session's folders. No such id was found in this session, and the check needs a publish and a
  declare, which this discovery forbids. It is a spike (the riskiest candidate in brief.md). Status: —.
- Whether an `<img>` of the artifact's own file (breadboard.svg published beside index.html) loads under the CSP. The guide
  names data: and blob: for images and "its own files by relative path" for the page. Not tested. Status: —.
- Whether a `db` state doc's size and write rate fit a state the size of the flow (the db text names a rate limit and no
  size). Not tested. Status: —.
- Whether the store's deploy record can be tied to a project without the board's MAC. The logs read hold no MAC, and
  RecordDeploy keys by MAC. The project-to-board link (requirements.json `board` against a kept board) was not read. Status: —.
- What the 27 board logs say, beyond the one read and the brief's count (18 "ready seen", 9 "ready unknown"). Not
  recounted. `grep -l "^ready seen"` gave 18, the same as the brief.
- How long `flow.py page` takes on the walk project. It was not run, because it writes page.html. Status: —.
- Whether the PO's "for everybody" (the skill install) means user level, /spark:setup or both. That is his to answer
  (#1521 third comment).

## Questions for the decider

- Is the deploy reader fix (TECH-2, TECH-3) its own story under P793 piece 6, done before or beside the page design,
  or part of P1038? · decides: whether ★C1 is fixed in the core or carried into the page design (PROC-1).
- Must the page stay readable from disk, as one file that loads nothing from the web (D7 and tests/test_flow_page.py:87-88)?
  · decides: whether (b2) or (c) may move the state into a fetched file (TECH-17), and whether a web font is allowed
  (TECH-22, TECH-30).
- Should an open page update by itself when the project changes (a db state doc, or a `files` read), or is "reload after
  /spark:page" enough? · decides: (a), (b1) or (d) against (b) on db or (c2) (TECH-18, TECH-19, TECH-24).
- May a state doc in the Artifact's db hold the drawer's holds and counts, which D10 now keeps out of db? · decides:
  whether the live db route is open (TECH-18).
- Is a public static copy (GitHub Pages on a free plan) acceptable, given that the drawer facts and other projects' names
  will be public? · decides: (d), and P834's first host (TECH-21).
- Which of the project's own facts must the page show (deploys, bench facts, decisions, battery, firmware), and from
  which records? · decides: the new readers or sections, and their records with an origin (TECH-8).
- Does the frontend-design skill's screenshot pass run in the page stories (with the Chrome extension or a headless
  browser), and where is the skill installed? · decides: the tool needs and PROC-2's W2 check (TECH-29, TECH-30).

## Searches

- "GitHub Pages private repository which plans site visibility public" (docs.github.com only) · served: (d), whether a
  static host can keep the page private on a free plan · used: TECH-21.
- "Chrome fetch local JSON file from file:// page blocked CORS" · served: (b2) and (c), whether a page from disk can read a
  state file beside it · used: TECH-17 (the MDN page in the results).
