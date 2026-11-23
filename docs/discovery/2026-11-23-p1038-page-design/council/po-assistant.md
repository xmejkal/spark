# P1038 council: the PO assistant (lenses: Existing first, and Risks and assumptions)

Run 2026-11-23, about 16:20 to 16:45 CET, on Opus. Read-only: the one file written is this one. No Artifact was
published, declared or changed. `describe_capabilities` (files, db) was the only Artifact call.

## Findings

Format: PO-<n> · claim · tag · pointer · supports only.

### What causes the stale page (★C1)

- PO-1 · The deploy phase never reads the project. `DeployReader.read` returns `NOT_STARTED` every time, with the look
  hint and the deploy hint, and reads no file. So no deploy that `deploy.py` logged can move the page past "deploy, not
  started". ★C1 is how the reader is built, not drift · E `scripts/spark/flow/phase_readers.py:554-560` (docstring: "the
  deploy is done in the person's terminal ... so it is not started here") · supports only: why the page says "not
  started" for deploy. It does not show that reading the logs is allowed or wanted. See PO-2.
- PO-2 · An earlier decision already lets the bench count as state, but only through what spark wrote down: "only a witness counts, which
  is what spark saw and wrote down with its source and time" (P867 D8). Card P873 #1241 holds that rule as "not yet", in
  Idea. The deploy logs are such witnesses: `sim/runs/board/2026-11-23T14-09-49.log` has a time, a port, the image's
  sha256, "simulation: none" and a "ready unknown" line · E `docs/discovery/2026-11-17-p867-journey-redefined/brief.md:138`
  (D8), `gh issue view 1241` ("The bench is state only through a witness that spark wrote (D8)"), the log's first 8
  lines, read 2026-11-23 · supports only: a deploy witness exists, and a reader can use it. Whether a "ready unknown"
  deploy counts as deployed is open (P1022's ground).
- PO-3 · The page's own freshness marks cover only three files: `needs.json`, `requirements.json` and
  `.spark/build.json`. A change to the firmware, a deploy log or a doc changes neither `data-written` nor
  the fingerprint. On the walk's page, `data-written="2026-11-22T11:44:33+01:00"` stands beside the line "firmware/main.py
  written 2026-11-23T14:18:49+01:00" · E `scripts/spark/flow/fingerprint.py:18` (`FILES`),
  `scripts/spark/flow/write_flow_page.py:132-136` (`newest_change`), page.html `<body>` and the firmware phase, read
  2026-11-23 · supports only: neither the page nor a check that uses its stamps can tell that the work after the build
  changed. P829's stale-request guard is a different thing and does what it is for.
- PO-4 · The page itself says what it cannot know: "This page reads the project's files. It does not know whether the
  board is wired or flashed." That note sits at the bottom, under Notes. At the top, the NOW box tells the person to
  plug the board in and deploy · E `scripts/spark/flow/flow_codes.py:195` (BENCH_NOTE), page.html, the guide section
  and the notes section, read 2026-11-23 · supports only: the top of the page contradicts the page's own limit.

### Is anyone blocked? What does the job today?

- PO-5 · In the walk, the page was used for 11 minutes and not after that. There were five clicks between 11:25 and
  11:36 CET on 2026-11-22 (three picks, the parts list, the build). From 11:40 the work went on in the chat and the
  terminal: the drawn breadboard, the wiring, the trials, ten or more deploys, the clock, the button, the battery and
  the timing. That ran to about 23:00 and continued on 2026-11-23. The diary names no page use and no request for the
  page in that time. Its only later page line (diary:203) says "the page offers no build now", so the build ran in the
  chat · E `~/Development/spark-walks/p934-display2/diary.md` section headings 8 to 525, and `awk 'NR>186' diary.md |
  grep -i page` (2 hits, both in the 11:46 section or the rows table) · supports only: in this one walk (n = 1), nobody
  was blocked for lack of a page after the build. It does not say whether the PO opens a better page.
- PO-6 · The project already has its own "where it stands" tool, outside spark. The project's GitHub repository
  (the project's own repository, private) holds 13 issues with labels `doing` and `next`: #4, #7 and #8 (doing),
  #5 and #6 (next), #13 (open), titles withheld. It also holds PRs #9 and #12 (the
  battery steps, merged). There is also the walk's `diary.md` and `docs/*.md` (battery-finding, refresh-finding,
  candidates). spark holds none of these facts in a record · E `gh issue list --state all` and `gh pr list --state all`
  in p934-display2, 2026-11-23, `gh repo view` → `"isPrivate":true`, `ls docs/` · supports only: Job 1 is done today by
  the issues, the diary and asking Claude. It does not say that the PO reads those issues to find his place (an account
  question, Q-A below).
- PO-7 · Most of the state the brief's ★C1 and C3 say is missing (the firmware's behaviour, the decisions, the battery,
  the bench facts) lives in files and issues that spark does not hold as records. The principles say spark "writes only
  what it derives from a record it holds". Only the deploy logs (PO-2), the pin map and the part records' bench facts
  (diary row 15, `--fact-set`) are spark's · E AGENTS.md, "Spark exports facts, never behaviour", the project's file
  list (`ls firmware sim docs`), diary rows table, rows 15 and 20 · supports only: a page that shows "the project's own
  facts" (the frame's outcome) must either read files spark does not own, or show only spark's part, or get new records.
  This is a design choice and is not decided here.
- PO-8 · spark already has three page writers and two hosts. (1) `FlowHtmlPage` → `page.html`, a private Artifact
  through `/spark:page`, with one inline script and the `db` capability for the click path. (2) The tabbed page
  (`spark.breadboard.tabbed_page`), whose tokens the flow page reuses. (3) A hand-made, public GitHub Pages page:
  pixel-games `docs/wiring.html`, 223 KB, one script, a pin table and wires that play, served at
  https://xmejkal.github.io/pixel-games/ (status built). That page loads Google Fonts (`fonts.googleapis.com`), which
  breaks D7's "loads nothing from the web". The hand-made encoder Artifact of 2026-11-11 that the PO praised is not in
  the repository (P887 #1257 body) · E `flow_page.py:17-19, 230-266`, `~/Development/pixel-master/docs/wiring.html`
  head, read 2026-11-23, `gh api repos/xmejkal/pixel-games/pages` → built, README.md:8 · supports only: what exists and
  where. Not that the PO wants these merged.
- PO-9 · The PO's other "where it stands" tools are the board (GitHub project, stages), the Miro journey board (queued
  daily, a limit of 100 calls a day) and the README's "What works today" table. None of them is per project. The
  README's journey table has no row for the page · E CLAUDE.local.md (the board, Miro), README.md:107-125, read
  2026-11-23 · supports only: no PO tool shows one gadget's state today except that project's own issues (PO-6).

### Licences and terms of what exists

- PO-10 · Licences: spark and pixel-games are MIT and public. anthropics/skills reports no licence at the repository
  level (`license: null`), but `skills/frontend-design/LICENSE.txt` is Apache-2.0, and SKILL.md says "Complete terms in
  LICENSE.txt" (9,390 bytes, sha a5333457c414). Hackaday.io and GitHub Pages are hosted services under their own terms,
  which were not read (—) · E `gh repo view` for both repositories, `gh api repos/anthropics/skills` and the folder's
  contents, 2026-11-23 · supports only: the skill can be installed under Apache-2.0. It says nothing about its fit.
- PO-11 · The design skill conflicts with spark's page rules in at least two places. (a) "Choose your typefaces
  deliberately, not the default families", while D7 and `FlowHtmlPage` keep system fonts so that the page loads
  nothing. (b) "take aesthetic risk" and a distinct identity per brief, while `FlowHtmlPage` is a renderer that gives
  the same bytes for the same flow. Its list of generated-page tells includes a "terracotta or warm-clay accent (often
  near #D97757)", and spark's `--signal` is #c8500f · E SKILL.md text read through `gh api`, 2026-11-23,
  `flow_page.py:242-248`, P820 brief D7 · supports only: the skill fits a one-time design of tokens and layout better
  than per-page generation. That reading is H, mine, and the PO decides.
- PO-12 · A static host is costly or public for this project. GitHub's plans page says GitHub Pages in a private
  repository needs a paid plan, and the free plan covers public repositories only. A privately published Pages site
  needs GitHub Enterprise Cloud. The project's repository is private · E web search, 2026-11-23:
  https://docs.github.com/en/get-started/learning-about-github/githubs-plans and
  https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/about-privately-published-github-pages-sites
  (search summary, the pages themselves were not fetched), `gh repo view` → private · supports only: the brief's H1 (a
  static host shows the page) holds only at a cost (name the cost, ask first) or by making the page public. With D10,
  the drawer's "you have" counts then go public too.

### The Artifact facts the options rest on

- PO-13 · The `files` capability reads "a Claude Code project's files as the viewer". The page can declare it "only
  when you know the project's id (e.g. your session's): `{files: {project: "chan_..."}}`". Only project members can
  publish a page that declares it, and "new or just-edited files can lag a few seconds". The capability's text also
  says: "Don't copy file contents into the artifact's data, assets or versions unless the user asks: anyone it's shared
  with can read them." · E `describe_capabilities` capability `files`, runtime contract 0.2.98, 2026-11-23 · supports
  only: a live-reading page needs a `chan_` project id. Nothing read says that a local Claude Code CLI session in
  p934-display2 has such an id, or which files the "project" covers.
- PO-14 · Secrets on disk sit next to anything that a live reader or a richer page reads. `firmware/wifi_secrets.py`
  exists and is git-ignored. `sim/flash-with-firmware.bin` is git-ignored, and the diary (row 18) says the Wi-Fi
  password goes into "a project file and the image". `sim/runs/` (the deploy witnesses) is git-ignored too, so a page
  built from git alone does not see the deploys · E `.gitignore` of p934-display2, read 2026-11-23,
  `git ls-files | grep -i secret` → nothing, diary row 18. The secrets file was not opened · supports only: the page's
  "no secrets" rule (brief, start and reach) is under pressure from any option that reads files, firmware or the image.
- PO-15 · The `db` text says: "No secrets; shared data is untrusted". Its rules say who reads and who writes, `self` "is
  a rule, not encryption". `/spark:page` declares `read: view, write: owner` · E `describe_capabilities` capability
  `db`, 2026-11-23, `commands/page.md:45-51` · supports only: anything the page puts into `db` can be read by any
  viewer of a shared page.

### Which open cards overlap

- PO-16 · Ten open cards touch the page. All are in Idea except P829, which is in Build. P829's PR 2 to PR 4 merged on
  2026-11-21. P1011 #1470 (layout, several picks at once, no developer lines, the PO's words) has the most overlap: its
  "Done when" is "To be refined after P828 and P829". P307 #373 (style by words, "make it dark") overlaps the graphic
  style. P887 #1257 (wiring that plays, `tools/flow-page/` toolchain) and P889 #1259 (pin table) are content the PO
  asked for on 2026-11-17. P992 #1445 (add a part the store lacks) is a new action on the page. P834 #1196 (another
  host) and P494 #674 (spike: which interface first, open since 2026-11-01) cover the architecture and host. P829 #1187
  is the click path, out of scope (D1). Two more cards that the brief does not list also overlap: P873 #1241 (the table
  of phases, the bench as a step, D9, "where the bench step stands and its states" is open) and P870 #1237 (spike: what
  the Artifact page can show live from a board) · E `gh issue view` with `--json projectItems` for each card,
  2026-11-23, `gh pr list --search P829` · supports only: the design touches four layers (content, layout and style,
  host, live data), and each one already has a card in Idea.
- PO-17 · P494 #674's question ("which interface does spark build first: static page.html, an Artifact, a local live
  page, RunFrame?") was in effect answered when P820 D5 to D11 built the Artifact page, but the card is still open. Its
  "Done when" asks how four older page cards (#152, #304, #372, #601) merge · E `gh issue view 674`, P820 brief D5,
  D7, D11 · supports only: this epic can close or absorb P494. That is for the decider.
- PO-18 · Earlier no-gos still stand and bound the design. The page works with no Claude (every capability may be
  null, and the content is in the HTML). There is never color alone. There is no tick on could-not-run, skipped or
  null. There is no logic in the page's script. There is no Flash, Deploy or Run-live-code button. These rules are from
  P820 (proposed no-gos, D7 to D10 were decided) · E
  `docs/discovery/2026-11-15-p820-artifact-interface/brief.md:97-105, 180-183` · supports only: a redesign that adds a
  "deploy done" state, a live view or a richer script must stay within these, or the PO must lift one.
- PO-19 · An earlier value test was planned but not run as written. P820's A5 was "the PO would use the page, not the
  chat or the CLI, for the pick and the wiring steps", with the pass line "in one walk he picks or wires from the page
  at least once without being asked". The P934 walk shows picks from the page (PO-5). The wiring went through the chat:
  "I need to see the breadboard" (diary 11:46) · E P820 `risks-and-tests.md:37`, diary.md:72-186 · supports only: A5
  half-met for the picks in one walk (n = 1). The walk planned the clicks ("The PO clicks Pick ... on the page",
  diary:12-14), so "without being asked" is not met.

### Riskiest belief and its cheapest test (my ranking, the decider rates)

- PO-20 · Riskiest belief, my reading (H, from PO-5, PO-6 and PO-7): that the page can show "where the project really
  stands" from facts spark holds, so that the PO opens it after the build instead of the chat or the project's issues.
  The facilitator's candidate (the `files` capability works outside the session's folders) matters only if the design
  chooses a live reader. Its first unknown is the `chan_` id (PO-13). Cheapest test for mine: a desk check, about 30
  minutes, with no code and no publishing. The PO names the five things he wants to see first when he comes back to
  p934-display2. Each is then marked: held in a spark record or witness, in the project's own files or issues, or
  nowhere. The pass line must be dated before the result, for example "at least 3 of 5 come from a spark record or
  witness". A second, cheaper part is an account question: what did he open the last time he came back to this
  project? · H my opinion, the decider sets the pass line (Q1) · supports only: which test to run first.

### Pre-mortem: "six months after the new page shipped, it failed. Why?"

Each cause is H unless it is tagged. The E causes are already visible today.

- PO-21 · It went stale again. It is regenerated only when Claude runs `flow.py page` and republishes, at the PO's
  `/spark:page` (E `commands/page.md:55-93`). Its freshness marks ignore everything after the build (E PO-3). So after
  the build it showed an old state, the PO stopped opening it, as in the walk (E PO-5), and the project's issues stayed
  the real tracker (E PO-6).
- PO-22 · It showed facts that spark did not back. To look complete, the firmware, decisions and battery sections were
  filled from diary or issue text, or by Claude's prose. A "done" without a witness appeared, against "a `null` is not
  a value to fill in" and the no-tick rule (E PO-7, PO-18). Or the sections stayed "not checked by spark" and the page
  looked empty after the build.
- PO-23 · The showcase job (Job 3) needed a share, and a share leaked or cost. The private Artifact holds drawer counts
  (D10). A public static host needs a paid plan for a private repository, or a public page (E PO-12). A richer page
  carried the Wi-Fi name or more (E PO-14, diary rows 18 and 3, and issue #3 of the project, (title withheld: a private repository)).
- PO-24 · The style drifted or broke a rule. The design skill pushed web fonts or a "distinct identity" each time (E
  PO-11), against D7. Or the hand design was not tokenised in `FlowHtmlPage`, so the next build overwrote it.
- PO-25 · Overlap churn. Ten cards in Idea each changed the same renderer and the one script. P829's guards (the
  stale-request check, the waiting state) regressed, or the work took weeks while the walks moved on in the chat (E
  PO-16).
- PO-26 · The runtime moved under it. Contract 0.2.98 is below 1.0. `use()` may answer null, and permission errors come
  on the first call. A page whose state depends on `files` or `db` showed nothing when a capability was null (E PO-13,
  PO-15, and the capability text: "design for absence").
- PO-27 · Size and speed. The page is 714 KB today, with 607 KB in two data URIs (brief C2). Adding firmware, logs or
  photos made every click's republish and reload slower. The PO named the four round trips per click as friction (E
  diary:82-85).

### What must be true for a redesigned page to work

- PO-28 · (a) The facts the PO wants first are held by spark as records or witnesses, or the PO accepts that the page
  reads other project files and says which (PO-7, P867 D8). (b) The page is rewritten when those facts change, not only
  when needs, requirements or the build change (PO-3). (c) The PO opens it at the moment of Job 1 (PO-5, untested). (d)
  Unknowns stay visible as unknowns (PO-18). (e) No secret or drawer fact reaches a viewer beyond the PO (PO-14, PO-15,
  D10). (f) P829's click path and its tests still hold (D1, "must not get worse"). (g) D7 holds (loads nothing from the
  web, works with the script off), or the PO lifts it on purpose (PO-11) · H derived from the E pointers named ·
  supports only: the list of conditions to check against each option.

### Found on the way (outside scope, proposals only)

- PO-29 · The README's Bench row says "no breadboard wired from a sheet has run yet". On 2026-11-22 the PO wired
  p934-display2 from spark's sheet and deployed it, with "ready seen" at 16:46 and 19:32 CET · E README.md, the Bench
  row, diary.md:209-215, :474-489 · supports only: the journey table may be stale for the Bench step. Not checked
  against how the README defines "runs".

## What I did not check, and why

- Whether a local Claude Code CLI session (p934-display2 or spark-p1038) has the `chan_` project id that the `files`
  capability needs, and which files that "project" covers. The capability text names only `chan_...`. Testing it needs
  a publish, and this discovery allows none.
- The `files` capability's type definitions (I did not call `describe_capabilities` with `types: true`). The
  `artifact`, `room` and `sample` capabilities. The Design type's definition (the brief's C6).
- Whether the PO reads the project's GitHub issues to find where he stands (an account question, I did not ask him).
- The PO's GitHub plan (free or Pro), which decides the cost of a Pages site for a private repository.
- The GitHub plan pages themselves. I read the search tool's summary, not the pages, and the summary noted one
  conflicting GitHub Docs page.
- The hand-made encoder Artifact of 2026-11-11 that the PO praised (not in the repository, per P887). I did not search
  for it with `list_artifacts`.
- Outside Artifact examples of project dashboards, and maker status pages other than Hackaday.io. The search budget
  went to the static host and maker pages. Hackaday.io's features come from a search summary of its help threads
  (components list, logs, build instructions, details, discussions), not from its pages.
- `deploy.py`'s log format as a contract (I read one log's head only). What "ready unknown" should mean for a page
  (P1022's ground).
- The page's two scripts' output. I read page.html with the scripts and the data URIs removed.

## Questions for the decider

- Q-A · The last time you came back to the e-paper clock, what did you open first to see where it stood: the chat, the
  project's issues (doing/next), the diary, the page, or something else? · decides: whether Job 1 needs a page at all,
  or a page that reads or links the project's issues (PO-5, PO-6), account, n = 1.
- Q-B · Name the five things you want to see first on this project's page. · decides: the desk check of PO-20, and
  whether the design needs new spark records, a reader of other project files, or only spark's own facts (PO-7).
- Q-C · May the page show facts that spark does not hold as records (issues, diary, docs, firmware text), marked as
  such? Or does it show only records and witnesses, as P867 D8 and "spark exports facts" say? · decides: the content
  boundary, and whether P873 #1241's bench step comes first (PO-2, PO-7).
- Q-D · Does a deploy with "ready unknown" count as deployed on the page? · decides: the deploy phase's states from the
  witnesses (PO-1, PO-2), P1022's ground.
- Q-E · Is Job 3 (showing the project to someone) in this epic? If yes, where: a shared Artifact (with drawer counts,
  D10) or a public static page (a paid plan for a private repository, or a public repository)? · decides: the host
  question and P834 #1196's place (PO-12, PO-23).
- Q-F · D7 says the page loads nothing from the web. Does that still hold for the graphic style, so that system fonts
  only and the design skill are used for tokens once? · decides: how the design skill is used, and whether D7 is lifted
  (PO-11).
- Q-G · Which of the ten overlapping cards does this epic absorb, close or leave: P1011, P307, P887, P889, P992, P834,
  P494, P873, P870, with P829 out of scope? · decides: the epic's edge and the card churn risk (PO-16, PO-17, PO-25).
- Q-H · Is the rewrite of the page by hand at `/spark:page` enough, or must the page change without a republish
  (`db` rows or `files`)? · decides: whether the `files` spike (PO-13) is needed at all.

## Searches

- `GitHub Pages private repository which plans site visibility public` · served: whether a static host (P834, the
  brief's H1) is free and private for a private project repository · used (PO-12).
- `hackaday.io project page features project logs build instructions components list` · served: what an outside maker
  project page shows first, for Job 1 and Job 3 · used, weakly (the summary in "What I did not check", no finding
  rests on it).
- `gh api repos/anthropics/skills` with its `frontend-design` folder, and `gh api repos/xmejkal/pixel-games/pages` (not web searches, listed for the record) · served: the licence and fit of the design skill, and what the pixel-games page is · used (PO-8, PO-10, PO-11). The facilitator reformatted this line for the check.
