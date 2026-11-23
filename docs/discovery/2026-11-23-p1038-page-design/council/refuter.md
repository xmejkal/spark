# P1038 council: the refuter

Run 2026-11-23, 16:30 to 16:38 CET, read-only. This file is the one file written. Read: brief.md, the three
council reports, jobs-and-journeys.md, story-map.md, risks-and-tests.md, items.md, verification.md (still a template),
the cited lines of spark's code, the walk project (page.html, its git diff, the 27 board logs, diary.md,
.spark/project.json, .gitignore), the store's board record, P1011 #1470, the comments of P1038 #1521, and two GitHub
Docs pages. Ran: `flow.py show --project . --json` in the walk project (reads only; page.html kept its mtime 15:23:55
and its 714,020 bytes). Not run: `flow.py page`. This run had no Artifact tool, so nothing on the Artifact server was
read or changed. Tags: E with a pointer, H with its source, — for unknown.

## Check first: the existing product

**Does the change address the observed problem?** Only in part, and not in the order the PO's words give.

- R-1 · The PO's own words name three problems: the looks and the readability ("it's an mvp, I know, but it's not
  very readable or intuitive or readable or good looking, just to note", diary.md:89-90), one pick at a time
  (diary.md:82-83), and the request's four parts (UX, graphic style, architecture, the Artifact how-to). No PO sentence
  in the folder says the page showed a wrong stand. ★C1 is the facilitator's observation of 2026-11-23, not an account.
  The story map puts ★C1's fix as the walking skeleton (slice 0), the readability the PO named in slice 2, and the
  how-to in slice 3. · E brief.md:15, :18, story-map.md:17-24 · the brief does not say that its first slice answers a
  problem the PO did not report.
- R-2 · The wrong stand that existed during the walk is not the one the brief describes. From 2026-11-22 11:46 to
  2026-11-23 about 15:24 the page said `data-stands-at="build"` and "NOW (firmware) Two jobs, in any order: wire the
  breadboard (13 steps, power off), and ask Claude to write the firmware." The "deploy" stand of ★C1 exists only since
  the rewrite at 15:23:55. So for the whole walk the mismatch came from the second cause (the published page is a
  copy), not from the deploy reader. A deploy reader fix alone (item 1, O5a) would have left the walk's page at
  "firmware" for the same 27.5 hours. · E `git diff -- page.html` and `git show HEAD:page.html` in p934-display2
  (commit 1edc3ee, 2026-11-22 19:05), page.html mtime · the brief calls the deploy reader "the first cause" (★C10's
  caveat); for the walk it was no cause.
- R-3 · After the deploy reader fix, this project may still stand at deploy. The newest deploy's verdict is
  "ready unknown", and 4 of the last 5 deploys (since 13:19 on 2026-11-23) are "ready unknown". The rules in force
  say no tick on an unknown (PO-18, CLAUDE.local.md: "A `could-not-run` or a `skipped` is not a pass"). The PO
  assistant asked "Does a deploy with 'ready unknown' count as deployed on the page?" (Q-D). The brief dropped that
  question. Item 1's proof ("names a stand past the deploy") and slice 0's proof presume its answer. The flow also
  has no phase after deploy, so "a stand past the deploy" has no value today (`now_phase` returns None only "in a
  flow of other readers"). · E sim/runs/board/2026-11-23T14-09-49.log:5, the 27 logs' ready lines, guide.py:80-89,
  council/po-assistant.md:235

**What breaks for current users (the PO, n = 1, and Claude)?**

- R-4 · O3b as written breaks either the disk page or its own saving. It keeps the Python renderer (b1) and says "a
  republish sends the small state only". With b1 the HTML holds the state, so a state change changes the HTML and
  the HTML is sent again. Sending only state.json needs a page that reads the state in JS (b2), which the brief sets
  aside, and which breaks the page from disk (TECH-17). What b1 can save is the two pictures (607,060 bytes), and
  only if an `<img>` of the artifact's own file loads, which nobody read. · E council/tech-lead.md:92-113 · the
  brief's O3b line joins TECH-15's b1 with TECH-16's saving, and the two do not hold together.
- R-5 · `.spark/state.json` is a second snapshot. `.spark/` is not in the project's .gitignore, so each core write
  changes a tracked file, the same harm C18 names for page.html. No option says which command writes it (deploy.py
  runs outside the flow). · E p934-display2/.gitignore (4 lines, read in full)
- R-6 · The diary and the page disagree on the Build offer, and the folder does not settle it. diary.md:203 says "the
  page offers no build now". page.html:450 holds `<li data-key="build" data-makes-stale="">` in the committed copy
  and in today's copy. The PO assistant quotes the diary line (PO-5), the user lens rests USER-3 and item 2 on the
  page line. Whether the owner sees a Build button is H (the render was not seen). Item 2 is filed as a bug on it.
- R-7 · The rewrite at 15:23 made a new fault that the walk's page did not have: 12 steps beside a picture with 13
  wires (USER-4 says so: "the page was rewritten at 15:23 with today's code"). Item 3 and the journey rows present
  it as the page's state; it is the state of an old build rendered by new code. Any option that rewrites the page
  more often (O3a to O3c) makes this case more frequent. No option covers it.

## 1. The ★ claims

- ★C1 · **partly** · read, `flow.py show --project . --json`, 2026-11-23 16:32 CET: `stands_at deploy`, `build
  could-not-run`, `deploy not-started`, and `"now": {"phase": "deploy", "by": ["your terminal"], "says": "When the
  breadboard is wired, plug the board into USB. Ask Claude to look at it first, then run the deploy in your
  terminal."`. Counted: 27 logs, 18 "ready seen", 9 "ready unknown", 0 "ready not seen"; the store record
  boards/<the board MAC>.json (the MAC is left out: spark is public) holds 27 deploys. Those parts hold. Two parts are stronger than the evidence.
  (a) "a state that does not match the project": the phase status does not match (27 deploys against "not started"),
  but the NOW sentence may be the right next step now. The last log reads "ready unknown: mpremote could not read
  the board's files: mpremote.transport.TransportError: could not enter raw repl", and firmware commit e5f6be0
  (2026-11-23 14:18:46) is newer than the last image (14:05:33) and the last deploy (14:09:49). (b) The caveat omits
  that this state dates from the write at 15:23:55 (R-2). Change the claim's first clause to: "Since its rewrite at
  15:23 on 2026-11-23 the page says deploy 'not started' beside 27 recorded deploys (the newest 'ready unknown');
  before that, for 27.5 hours, it said 'NOW (firmware)'." Change the caveat's end to: "whether 'deploy' is the wrong
  next step now is —".
- ★C5 · **could not open** · this run had no Artifact tool (`guide`, `describe_capabilities`). Not a pass. Other
  records in the repository, written by other agents, give contract 0.2.96 on 2026-11-15, 11-16 and 11-17
  (docs/discovery/2026-11-16-p835-interface-spike/artifacts-and-plugin.md:4: "Runtime contract read: 0.2.96
  (describe_capabilities, no argument)."). They do not confirm 0.2.98 or the list of 12 capabilities. Against its own
  source the claim is vaguer: TECH-27 says "The frame refuses alert, confirm, prompt, downloads the page starts, and
  clipboard reads" and "Stylesheets come only from fonts.googleapis.com"; ★C5 says "alert and downloads are limited"
  and drops the stylesheet line, on which O4c rests.
- ★C10 · **partly** · read, phase_readers.py:554-560: `class DeployReader(PhaseReader):` / `"""Strategy: the deploy
  is done in the person's terminal, after Claude looked at the board, so it is not started here."""` / `return
  self.phase(flow_codes.NOT_STARTED, [flow_codes.LOOK_FIRST_MESSAGE, flow_codes.DEPLOY_HINT])`. guide.py:80-84: "The
  deploy is never done here, so there is one" and `now = next((phase for phase in phases if phase.phase not in
  no_model and is_open(phase, fact)), None)`. "Fixed at not started and reads no file" holds. "Every project past the
  firmware stands at deploy" is too wide: guide.py:74-77 makes a simulate phase with status not-started open, and it
  comes before deploy, so a project whose board has a Wokwi model stands at simulate first. Change to: "every project
  past the firmware and the simulation, or with no Wokwi model, stands at deploy for ever". The caveat's "the first
  cause of ★C1" is an order the walk does not support (R-2).
- ★C12 · **partly** · read, diary.md:74 "The PO clicked \"Pick DFRobot FireBeetle 2 ESP32-C6 for board\" at 11:25:30",
  :105 "at 11:28:32", :124 "at 11:31:27", :144 "at 11:35:21", :170 "The PO clicked \"Build the board\" at 11:36:57".
  Five clicks in 11 minutes 27 seconds hold. "The page was used for 11 minutes" does not: the diary logs clicks, not
  views. diary.md:189-190 reads "He wired already, from the text steps", and :203-205 reads "Page written (712 KB,
  the picture inline) and republished", after the PO asked "I need to see the breadboard". So the page was rewritten
  for the wiring at 11:46, and whether he wired from the page's steps, from breadboard.md or from the picture is —
  (the user lens asks it as Q-U4; the brief has no such question). "The project tracks its state in its own private
  GitHub issues (doing and next labels)": `gh issue list --state all` shows 12 issues and 2 PRs; `doing` sits on
  three closed issues (#2, #3, #7) and the two newest open issues (#13, #14) have no label. All are filed under one
  login, so who tracks there, the PO or the sessions, is —. Change to: "the page got 5 clicks in 11 minutes
  (11:25:30 to 11:36:57) and none after; it was republished at 11:46 with the breadboard picture at the PO's request;
  whether he read it after that is —. The project has 12 issues of its own; who reads them is —."
- ★C13 · **partly** · read, AGENTS.md:51: "- Spark exports facts, never behaviour. It writes only what it derives
  from a record it holds, and never thresholds," . The quote holds. The claim "decisions, battery ... in files and
  issues that spark holds as no record" does not: p934-display2/.spark/project.json holds `goal`, `must` (2 lines)
  and `decided`, with "2026-11-23, the PO: the press screen is dropped for now" and "2026-11-23, the PO: the battery
  will probably be 2000 mAh". That file is spark's brief record (scripts/spark/records/brief.py:2: "The project's
  brief: what `.spark/project.json` says, read on each call."). Its own note says of `decided`: "no script reads it".
  The store's board record (27 deploys with verdict, image and the standing yes) is spark's too and is not in the
  claim's list. Change the second half to: "spark's own: the deploy logs and the store's board record, the pin map,
  the parts' bench facts, and the brief record (.spark/project.json: goal, must lines, decided lines), which no flow
  reader reads."
- ★C16 · **partly** · four parts. (1) wifi_secrets.py: `ls firmware` lists it, and .gitignore line 1 is
  "firmware/wifi_secrets.py": holds. (2) .gitignore line 3 is "sim/runs/": holds. (3) GitHub Pages, fetched today,
  not a search summary: "If the account that owns the repository uses GitHub Free or GitHub Free for organizations,
  the repository must be public." and "GitHub Pages sites are publicly available on the internet, even if the
  repository for the site is private" and "To publish a GitHub Pages site privately, your organization must use
  GitHub Enterprise Cloud." Holds, and the fact is wider than the claim: a paid personal plan publishes publicly too.
  (4) "the files capability reads any project file unmasked": **could not open** (no Artifact tool). The earlier
  record artifacts-and-plugin.md:22 quotes the same capability as reading "with the viewer's own access", and TECH-19
  says a viewer outside the organisation gets `null` or `not_found`. So for the frame's one user (the PO, a private
  Artifact) the files route shows the secrets file to nobody who cannot already read it. Also "the drawer facts ...
  would go public" is presented as a limit, while P820 D10 reads "the page shows \"you have\" counts and holds, which
  go with any share" (P820 brief.md:183). Change to: "the files capability reads raw files with the viewer's own
  access and without spark's mask (not re-read today); GitHub Pages is public on every plan except an organisation
  on Enterprise Cloud; D10 already lets counts and holds go with a share, public is not decided."

## 2. The brief against its detail

Claims stronger than their source:

- R-8 · O2a, "opinion (the PO assistant and the tech lead lean here)". Its pointers say otherwise.
  council/po-assistant.md:54-60 (PO-7) ends "This is a design choice and is not decided here." council/tech-lead.md:17
  (TECH-1) is about the two causes, and TECH-8 says "needs new readers or a new section, whichever direction is
  chosen". Neither lens leans to O2a. The one lens that gives an order (the user lens, user.md:220-223) puts the goal,
  the must lines and "the one next step, which today comes from the PO's issues" first, which is O2b. So O2a is the
  facilitator's opinion alone, with one lens against.
- R-9 · O2b's caveat says the goal and the must lines are "facts spark does not hold". They are in spark's brief
  record (★C13 above). The line between O2a and O2b is drawn in the wrong place: goal, must and decided lines belong
  to O2a. Story-map slice 1 already treats them so, so the brief and its own map disagree.
- R-10 · O3b (R-4), and its dropped caveat: "b1 alone does not fix TECH-1 (ii)" (tech-lead.md:99-100). O3a carries
  "★C1's second cause stays"; O3b does not, though the same holds for it. O3b's "what it would prove" (one state
  for the CLI, the page and an agent) already exists: "Its JSON half ... is already `flow.py show --json`'s data"
  (TECH-9).
- R-11 · C17, "the one documented way to change an open page without a republish". TECH-18 says "the one documented
  push from Claude's session"; a `files` read is a second way, a pull (TECH-19, TECH-24: "(c) is a pull").
- R-12 · risks-and-tests.md, viability: "a private static host needs a paid plan". The fetched page says an
  organisation on Enterprise Cloud; a paid personal plan is still public. Only GitHub Pages was looked at; "a static
  host" stands for one host.
- R-13 · A7 and the no-go "no drawer fact ... reaches a viewer other than the PO" tighten D10 without saying so (see
  ★C16). O7b ("without the drawer facts") inherits it.
- R-14 · C2 does not add up. 714,020 − 607,060 = 106,960 bytes, not "about 43.6 KB". The inline breadboard SVG
  (62,983 bytes by my count) is missing from the sentence; TECH-13 says so, the brief does not.
- R-15 · C8 says the repository was "pushed 2026-11-16". The skill's own folder last changed on 2026-09-03 (commit
  41bbe19d, TECH-29, re-read today). The brief gives the newer date beside the skill's name.
- R-16 · O4c, "fonts.googleapis.com, which the runtime allows": the pointers given (C15, tests/test_flow_page.py:87)
  do not say it. The source is TECH-27, which I could not open.
- R-17 · C18, "a 714 KB page does not fit in one Read": the refused read was of the copy without data URIs, at 28,672
  tokens (USER-12). The whole-file cost is "not measured".

Caveats and findings the brief dropped:

- R-18 · Q-D of the PO assistant (does "ready unknown" count as deployed), and PO-2's line "Whether a 'ready unknown'
  deploy counts as deployed is open (P1022's ground)". Q5 offers only where the fix lives, as if what it shows were
  settled (R-3).
- R-19 · PO-2 and PO-16: P867 D8 ("only a witness counts") and P873 #1241 (the bench as a step, its states open, in
  Idea) own the question the deploy reader answers. Q5 has no option "under or after P873"; C23 names P873 only as an
  overlap.
- R-20 · PO-19: P820's A5 was the same value test ("in one walk he picks or wires from the page at least once
  without being asked") and "without being asked" was not met. A1 repeats the test and does not cite it.
- R-21 · PO-18: of five standing no-gos the brief keeps one ("no logic in the page's script"). "No tick on
  could-not-run, skipped or null" and "no Flash, Deploy or Run-live-code button" bound the deploy state directly.
- R-22 · PO-8: spark has three page writers and two hosts, among them a hand-made public page that loads Google
  Fonts and a hand-made Artifact "that the PO praised", not found. Nothing of this is in the brief. It is the only
  evidence in the folder of a page look the PO liked, and Q4 does not use it.
- R-23 · PO-11 (b) and its accent note: the skill asks for a distinct identity per brief, against a renderer that
  gives the same bytes; its list of tells names a terracotta accent, and spark's `--signal` is #c8500f. C15 keeps only
  caps labels and middle dots.
- R-24 · USER-4's cause (R-7) and the diary's "no build now" (R-6).
- R-25 · Parts of the request with no option and no question: the Artifact how-to (one map row, slice 3, filed under
  Job 4), the "later interactive part", and the open question "which of the eight option families", which is in the
  Frame's open list and absent from Questions. The eight families are "all hypotheses from its own knowledge (not
  read from a source today)" (#1521, comment of 14:31Z); O3b cites "family 3 of the card's eight" as what it proves.
- R-26 · Stale lines in the brief: "Ready for ... the lenses, options and the refuter are not run yet", "Stands on
  ... no assumption is written" (nine are written), and the Hand-off's "the frame is unconfirmed (Q0)" beside D1.
- R-27 · C19's pointer page_script.js:320-323 covers the db check only; the owner check is on :324-325.
- R-28 · verification.md is still the template; nothing to compare.

## 3. The strongest rival for each interpretation

- "The page follows spark's chain, not the project's real work" (★C1): the page was right when written and was not
  written again. Not ruled out: R-2 supports it for the walk.
- "Nobody used the page after the build, so its value is in doubt" (★C12, the value risk, A1): the page has no
  button after the build by design (no Deploy button, PO-18), and the walk's plan scripted the page for the picks,
  the list and the build (diary.md:12-14). No clicks after the build is what the design gives. The diary is written
  by sessions and holds no view. Not ruled out.
- "He will open it once it shows the true stand" (A1): he will open it once it reads well. His only words about the
  page are about its looks. The leaning tests the stand first and the looks in slice 2. Not ruled out.
- "Most of what he wants is not spark's" (★C13, A2 against O2a): the goal, the must lines, the decided lines and the
  deploys are spark's already, so O2a may carry more than the brief says. Not ruled out; QA2 would settle it.
- "The files route is unsafe" (★C16): it reads as the viewer, and the viewer is the PO. The unsafe case needs a
  share, which Job 3 puts later. Not ruled out.
- "A static host must be public" (★C16): only GitHub Pages was read. The page from disk is already a private static
  page (C19). Other hosts: —.
- "27 deploys were made" (★C1's caveat): 27 deploy runs were logged. One reads "ready unknown: mpremote could not
  start the firmware: OSError: [Errno 6] Device not configured"; whether each run put an image on the board is —.
- "Job 1: he comes back after a break and reads the page" (H, the facilitator's reading): he comes back by opening a
  Claude session, and the reader of the stand is Claude through `flow.py show`. Then the fix that matters is the
  core's JSON and commands/page.md:73, not the page. USER-13 supports it; QA1 would settle it.
- "Job 3: he shows the page" (H, the CV memory): he shows the repository or the gadget. No account (QA4).
- "1.2M installs show use" (C8): the count may include automated installs by agents; its counter is not named.

## 4. Numbers without unit, population, period or provenance

- "11 minutes" (★C12): the span between the first and the last click, 11 min 27 s; not time in use.
- "27 logs", "18", "9" (★C1): no period in the brief. It is 2026-11-22 13:04 to 2026-11-23 14:09 CET, one board, one
  port.
- "27.5 hours" (USER-10, used above): rests on H that the Artifact's version ids count seconds.
- "12 breadboard steps" (C3): true of the 15:23 rewrite; the build's sheet and picture have 13.
- "about 43.6 KB" (C2): does not sum (R-14); KB or KiB is not said. "Two scripts of 22,130 bytes": one of the two is
  the inert JSON words block; my count of the two blocks is 8,709 + 13,502 = 22,211.
- "contract 0.2.98" (★C5): no earlier value beside it. It was 0.2.96 on 2026-11-17, so it moved twice in six days,
  which the viability row needs.
- "1.2M installs" (C8): no counter, no period. "about 199k stars": 199,311 at 16:33 CET today.
- The project's issues: 13 (PO-6), 14 (USER-2), 12 (USER-10). `gh` shows 12 issues and 2 PRs, 6 open.
- "S", "M", "M to L" in every option: no unit. Only (a) has a provenance ("the tech lead's estimate from the file
  sizes").
- Pass lines: "within 30 seconds" (A5), "within 60 seconds" (A8), "within a minute" (story map), "3 of 5" (A2, from
  PO-20's "for example"): each is the facilitator's, with no source. A1's "at least once on his own" has no
  instrument: "there is no view log (the server cannot read view counts)" (user.md:237), so it rests on his report,
  after QA1 told him what is tested.
- "the eight option families": the epaper session's own knowledge, no source (R-25).
- "about 15 searches or fetches" (the budget): the folder shows 4 searches by the lenses; the facilitator's own count
  is not written.
- The template's "6 agents, 499 calls and about 90M input tokens (2026-10-06)": not checked.
- council/po-assistant.md:3 says the run lasted "about 16:20 to 16:45 CET"; the file was last written at 16:28 and I
  read it at 16:31. The end time was written before it happened.

## The options and the facilitator's leaning

- O2a rests on a lean that its sources do not hold (R-8) and on a boundary drawn wrong (R-9). Fair wording: O2a is
  the facilitator's alone; with the brief record counted, it holds the goal, the must lines, the decided lines and
  the deploys.
- O2a and O2c do not give "what to do next", which is half of the Outcome. With every phase done or unjudged, the
  guide has no NOW. Only O2b (issues) or a link (O2c) supplies a next step, and the brief does not say so.
- O3b rests on a saving that its own shape cannot give (R-4) and lacks the caveat O3a carries (R-10). As written, O3a
  and O3b differ by one stored file. A fair set states the real choice: snapshot (O3a, O3b) against a live channel
  (O3c).
- O4a to O4c are fair as a set. O4b's cost may be larger than "S": the test lowercases the page and forbids "http"
  anywhere, and a base64 font can hold those four letters by chance (not computed for a real font; today's page with
  607 KB of base64 has 0 hits).
- O5a and O5b both assume what the reader shows is settled (R-3, R-18, R-19). A third option is missing: decide the
  deploy states first (P873, Q-D), then the reader.
- O7a rests on H only, as the brief says. O7b carries the tightened D10 (R-13).
- No option family covers the how-to or the interactive part (R-25).

## What I could not check, and why

- ★C5, C6, C17 and the files half of ★C16: no Artifact tool in this run. "Could not open", not "holds".
- C4 and USER-6 (the requests and answers), USER-10 (the Artifact's versions): the same reason.
- How the page renders for its owner (the Build button, the top panel): no browser used; the time limit.
- Whether the image on the board holds today's firmware/: the image was not unpacked.
- Whether a rebuild moves the pins (C14): a build writes files. Read only: commit a3a5ba50 is in main and its
  subject names "EPD_RST on D11, EPD_BUSY on MISO"; firmware/pins.py:8 reads `EPD_RST = 19  # pad SDA`.
- C7 and C23 (the cards' bodies), C20 (the #1105 comment), C21, C22 beyond README.md:127 ("no breadboard wired from a
  sheet has run yet", which is there): not re-read, for time.
- The lane limits in PROC-3: not checked.

## Searches

- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages · served ★C16 (the plan
  rule) · not used: the page as fetched held none of the sentences.
- https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site · served ★C16 ·
  used (the Free plan sentence and the public warning).
- https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site · served ★C16 and R-12 · used (private publishing needs an organisation on Enterprise Cloud).
- `gh api repos/anthropics/skills` and its commits for skills/frontend-design (not a web search) · served C8 · used
  (R-15).
