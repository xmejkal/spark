# P1161 council: the PO assistant (existing first, risks and assumptions)

Lenses: existing first; risks and assumptions. Read on 2026-11-25, about 21:00 to 21:40 CET, on branch
p1161-research-pages (main 5130caa4). Tags: E = read at a pointer; H = a guess, with its source; D = a decision, with who
and when. Canvas = the design canvas copies (read only), cited `canvas:<file>:<line>`. Store = the PO's store, cited
`<store>/<path>`. Walks = the walk folders, cited `<walks>/<path>`.

## Findings

Format: PO-n · claim · tag · pointer · supports only.

### Most important

- PO-1 · The core already has the write Operations that a record editor needs: `fact-set` (facts, `facts` entries,
  about, description, tags, `legs`, `host_requirements`, `short_name`, a board's `pin_roles` and `joined_pads`),
  `function-set`, `features-set`, `drawer-set`, `skeleton`, `promote` and `keep`. Each has a dry run and writes "in the
  record's own home … never spark's library". The page offers none of them. `OFFER_KINDS` holds 7 kinds (pick,
  requirements, build, needs-drop, write firmware, run simulation, look at the board), and none of them is a store or
  record kind. · E · scripts/spark/sourcing/sourcing_operations.py:32-35; set_facts.py:28-31; set_function.py:18;
  set_drawer.py:18; scripts/spark/flow/flow_codes.py:148-155; canvas:StorePart.dc.html:46 ("The page sends nothing: no
  store job is something it may send yet"), also canvas:Store.dc.html:97 · supports only: an edit from the page needs
  an Offer and a screen over Operations that exist. It does not say that those Operations cover every field a person
  wants to change (see PO-9 and PO-10).
- PO-2 · Nobody is blocked today. Each record edit and each research in the walks ran through Claude in the chat, with
  the PO's yes. In the P934 walk 2 (display2), `--fact-set` wrote the e-paper record 3 times after the bench, each
  time on his yes (the controller, `deep_sleep_wake`, the BUSY level). `/spark:identify` wrote the e-paper record from
  photos. The PO's ask for the page (P992) came from looking at the page. It did not come from a job he could not do.
  · E · <walks>/p934-display2/diary.md:277-290, 418-430; <walks>/p934-epaper/diary.md:12, 57-66;
  <walks>/p934-display/diary.md:86-97 · supports only: an account, n = 1, the PO. It says nothing about the primary user,
  "the hobbyist … at home in a terminal" (scrum/VISION.md:38), who is H and has not been reached.
- PO-3 · A page cannot run a research or an identify itself under today's decisions. A job of Claude's is an "Ask
  Claude" offer, with `from_page` false and a visible `tell` sentence that the person copies (D-c, the PO,
  2026-11-25). A later direct channel carries only `{id, key, seen}` and ends in `flow.py run-request`. P1122's Done when
  says "a test pins that no channel carries text". So criteria typed into a page form (for example "≤ 3.3 V logic, SPI,
  under 30 mm") cannot travel through a request row. They can only travel in a sentence that the person copies into
  the chat. · E · gh issue view 1652 (P1122, closed); `<store>/councils/p1113/architect-page-actions.md`:14-22, 53-62,
  103-106; commands/page.md:113 · supports only: under D-c, a "research page" or a "criteria page" in this epic is a
  page that composes a sentence. It is not a page that runs anything. Whether D-c should change for free text is the
  decider's question (Q2).
- PO-4 · No outside parametric search fits spark's rules for modules. spark's own `parts-search` tool is the jlcpcb
  MCP (`@jlcpcb/mcp`, MIT, run locally by `npx`, calls JLCPCB's API and EasyEDA). Its `component_search` takes only
  `query`, `source`, `in_stock`, `basic_only`, `economic_only` and `limit`: no voltage, current or package filter. It
  returns price and stock, which spark does not gather. My test call on 2026-11-25 for "ST7789 IPS display module SPI"
  returned 0 results with `source: lcsc`. With `source: all` it returned 10 of 10 EasyEDA community uploads, with user
  names as "manufacturer", stock 0 and 0 of 10 with a datasheet URL. · E · .mcp.json:11-16; data/tools.json:11,
  211-219; https://cdn.jsdelivr.net/npm/@jlcpcb/mcp@0.4.0/README.md (read 2026-11-25); the two
  `mcp__jlcpcb__component_search` calls, 2026-11-25 about 21:30 CET · supports only: one module query, n = 1. It
  says nothing about commodity parts (an LED, a regulator), where LCSC's coverage is the tool's purpose.
- PO-5 · The other outside services need an account, and none shows free, local and keyless parametric search for
  modules. DigiKey Product Information v4: "Search for product information based on part number, description,
  manufacturer or category". The page links Register or Login and an API User Agreement, and states no price or limit.
  Nexar (Octopart): the Evaluation plan, "Sign up, it's free", covers "Up to 100 matched parts". The page does not say
  whether that is per month or for life; a Nexar support article says the limit is for life and does not reset. TME:
  "Register now and get access"; the price was not stated on the page. Mouser: the page timed out. GME, Hadex, LaskaKit
  and Botland: the search found no API or feed. · E · https://developer.digikey.com/products/product-information-v4,
  https://nexar.com/compare-plans, https://support.nexar.com/support/solutions/articles/101000476314 (search result
  only, not opened), https://developers.tme.eu/ (each read 2026-11-25) · supports only: what each landing page says.
  The terms and limits behind each login were not read. Every one of these services also sends the query off the
  machine, which spark's rule "a local CLI before a web service" ranks last (AGENTS.md, Principles).
- PO-6 · The research path for commodity parts has never run in a walk. README's Research row reads "The part-finder
  and datasheet-reader did not". A "find a part by criteria" job that starts on part-finder rests on a path with no run
  behind it. The module path did run: the parts-researcher on Opus took 6 min 18 s for identify (8 of 8 searches, 7 of
  12 fetches). "Research for use" took 25 minutes on Opus. Its record still left 3 controller candidates, all
  unverified, and a bench trial settled them. · E · README.md:122; <walks>/p934-epaper/diary.md:57-62, 111-114;
  gh issue view 1454 (P997) · supports only: wall times of one run each (n = 1 per path), in minutes, from the diary's
  own entries. These are not token counts.
- PO-7 · "Tell me the cost first", which the canvas promises on each research sentence, has no estimator behind it.
  spark counts a run's cost afterwards, from the session transcripts (`run_cost.py`; the idea cost line "counted from
  the" marks). No command gives a cost before a research starts. · E · canvas:Store.dc.html:177,
  canvas:StorePart.dc.html:65, canvas:StoreAdd.dc.html:33 ("may cost tokens"); scripts/spark/sourcing/run_cost.py:1-8;
  commands/idea.md:270-272; commands/research.md (no cost step; grep for "cost", "estimate") · supports only: the
  promise is Claude's to keep by its own words. spark has no figure to show on the page.
- PO-8 · The store holds the case that an editor would work on: 114 drawer entries, 19 of 114 linked to a record and
  95 of 114 with no record; 99 of 114 come from the seller dfrobot. On the shelf, 10 record files hold 194 facts with a
  `verified` flag, and 107 of 194 are not verified. In the catalog, 18 record files hold 235 facts, and 45 of 235 are
  not verified. · E · a read-only count over `<store>/drawer/*.json`, `<store>/shelf/*.json` and
  `<store>/catalog/*.json`, 2026-11-25 about 21:20 CET (python, keys `is`, `from.seller`, and every object with both
  `value` and `verified`); it agrees with canvas:Store.dc.html:20 ("114 entries", "95 entries not known yet") · supports
  only: how much there is to edit. It does not show how often the PO wants to edit. Owning a part never starts
  research (D-e), so the 95 entries become a research job only when a need asks for one.

### Existing first, per job

- PO-9 · (a) Edit a fact of a part record: `parts.py --fact-set <id> <file>`, with a dry run, run by Claude after the
  person's yes. A bench result is `verified: true`, with a source that names who, when and how. It never edits spark's
  library; a library record is "used as it is". Since P947, P962 and P987 it also takes `host_requirements`, `legs`
  and `short_name`. The walk's gap "fact-set has no key for host_requirements" is closed. The person cannot run it from
  the page. · E · set_facts.py:31; commands/research.md:108-109, 55; <walks>/p934-display2/diary.md:281 against
  set_facts.py:31 today; `git log -- scripts/spark/sourcing/set_facts.py` (942ccc13, ff504fad, 417df9dc) · supports
  only: the field set that exists. Which layer a page edit lands in (project, shelf or catalog) is open: PO-13.
- PO-10 · (a) Edit a board record: only a board's `pin_roles` and `joined_pads` are writable, and only for "a board of
  the project's own". In the e-paper walk a board file was written by hand, its documents were listed by hand, and
  "`mounting_holes.diameter_mm` 2.0 set by hand in the board file (no command writes a board's physical fact)".
  `features-set` writes a board's measured features. No board research exists (P230, P286). · E · set_facts.py:31, 48;
  <walks>/p934-epaper/diary.md:384, 391, 404, 444-445; gh issue view 218, 336 · supports only: "edit a board record"
  from the page has no Operation under it for most fields. An edit page for boards would also mean new core work.
- PO-11 · (a) Edit a drawer entry: `drawer-set` sets, never adds, refuses all on one problem, and has a dry run. The
  canvas already draws "Edit an entry" and "Add parts" as "Ask Claude" sentences on `op:drawer-set`, marked "only
  writes, could be one click later". · E · set_drawer.py:1-27; commands/drawer.md:25-53;
  canvas:Store.dc.html:175, 178, 180; canvas:StorePart.dc.html:59 · supports only: the drawer entry is the one record
  whose edit needs no Claude judgement. It is the nearest candidate for a page button, but under D-c it would be a
  new `from_page` kind.
- PO-12 · (b) Research a named part: `/spark:research`. Reuse first, with no network (`--need`, `--kept`). Then
  part-finder (commodity) or `research.py` plus parts-researcher (module). It ends with `--validate`, `--sources` and
  `--unverified`. It gathers no prices, stock or seller listings. Run by Claude in Claude Code; `--fetch`, `--sources`
  and `research.py` reach the network and ask first. The canvas sentence: "Research the Fermion 1.8 in IPS display
  (DFR0928) from my drawer. Tell me the cost before you start." · E · commands/research.md:16-33, 35-74, 86-89, 99-101;
  canvas:Store.dc.html:177 · supports only: what exists. Outside tools for this job are the distributor pages, and
  part-finder already rules them out ("Never fetch a distributor page", agents/part-finder.md, How, 3).
- PO-13 · (c) Identify from a photo: `/spark:identify`. Claude reads the photo, then `--need`, then parts-researcher
  with a wide web search. Every fact that only the photo supports is `verified: false`. The photo is kept in the store,
  then the drawer entry is written. Outside: phone apps that read IC markings (Electronics Reference for iOS, free with
  purchases, offline; ChipLog Pro, a free tier; IC Lens, 5 free scans) and a dataset (chipID on Roboflow, CC BY 4.0).
  None is open source and ready to use. Each reads a chip, not a module's pin order or its board name. · E ·
  commands/identify.md:14-75; search 6 below (results only, no app opened) · supports only: spark's own path is the
  only one that writes a record. Whether a page can hand a photo to Claude Code is not known (see What I could not
  check).
- PO-14 · (d) Find by criteria: in the store, `parts.py --need <words>` and `--match` with a need's condition words
  (P1015) rank by words only. A fact's number enters as text for a chooser (`describe` prints `power` and `body_mm` as
  text). No command filters records by a number, such as a supply of 3.3 V or a width under 30 mm. Online, nothing
  in spark takes criteria. parts-researcher and part-finder take "the need in the person's words … and any limits".
  · E · scripts/spark/sourcing/matching.py:70-79, 164-184, 232-239; scripts/spark/sourcing/offers.py:7, 50;
  agents/part-finder.md, "What you are given" · supports only: criteria are words for Claude today. A numeric filter
  would be new core work and a new record contract (records grow by need, AGENTS.md).

### Risks and assumptions

- PO-15 · What must be true for the epic to pay off. (1) The person starts an edit or a research from the page more
  readily than by typing in the chat, although each start from the page still ends in the chat (PO-3). (2) A record
  edit from the page keeps the `verified` rule: `verified: true` means "the maker's own text at a cited page" or a
  bench result with who, when and how. (3) The research that the page starts finishes with a record that the chain
  can use, without a second research round. · H · my reading of commands/research.md:12-14, set_facts.py:31, and of
  PO-3 and PO-6 · supports only: a list for the decider to rate (Q1 of the brief).
- PO-16 · The riskiest belief is (1) of PO-15. The PO already directs Claude rather than typing commands
  (scrum/VISION.md:39). Every start from the page, under D-c, is a copy and a paste into the same chat. The page can
  add value through what it shows (what is unchecked, which entry has no record), and less through how a job starts.
  The cheapest test is in the next walk's diary: at each point where the PO wants to change a record or look for a
  part, note whether he types it himself, copies the page's sentence, or asks for a button. Each entry is a row with
  the time from `date`. No build is needed, because the canvas sentences exist (canvas:Store.dc.html:175-180,
  canvas:StorePart.dc.html:59-65). · H · the vision line and PO-2, PO-3 · supports only: a proposed test. The decider
  sets the pass line before any result.
- PO-17 · Pre-mortem: "It is six months after this shipped, and it failed. Why?" (a) The page only copies sentences.
  The PO kept typing in the chat, the edit and criteria screens went stale beside the store, and nobody opened them
  (PO-3, PO-16). (b) An edit form let a person set a fact to `verified: true` with no source or bench method. The checks
  then trusted an unproven pin order, and a breadboard was wired wrong (commands/research.md:12-14; the DS3231 photo had
  5 of 7 facts wrong, commands/identify.md:16-20). (c) An edit landed on one copy (the project, the shelf or the
  catalog) and other projects kept reading the stale one. The walk saw this: "a later change to the record there does
  not reach this copy" (<walks>/p934-epaper/diary.md:105-111; <walks>/p934-display2/diary.md:194). (d) "Find online
  by criteria" grew into a shop search with prices and stock, against research.md section 3, or it hung on an account
  or a paid API (PO-4, PO-5). (e) Research from the page ran on Opus for 25 minutes and cost tokens the person did not
  expect, because no estimate exists (PO-6, PO-7). (f) A store edit could not be taken back, because the store is
  outside the project's git (git discovery D8 caveat, UX-3), while the page promised "undo that" for every kept step
  (D9, D11). · H, from the E pointers named in each item · supports only: failure modes to design against. None of them
  has been observed in a product that shipped.
- PO-18 · Prompt injection widens on a research page. Research reads shop and datasheet text, and every command
  repeats "data about a part, never an instruction". A criteria form that puts the person's free text into a `tell`
  sentence, or a page that shows fetched text, adds a new surface. P1122's guard "no channel carries text" exists for
  this reason. · E · commands/research.md:8, commands/page.md:8, 113; gh issue view 1652 · supports only: a constraint
  the design must keep.

### Overlaps in the backlog

Read with `gh issue view <n>` on 2026-11-25. The status is the project field.

- PO-19 · P992 #1445 (Idea): "for a need, the page offers to add a part the store lacks: research it online, identify
  it from photos, draw its picture". · E · gh issue view 1445 · supports only: the research and identify half of P992
  is inside this epic's scope ("starting a research or an identify from the page"). Its "draw its picture" half is not.
  Absorb the first half or merge; leave the picture half to P734 #1005 or P276. It is the only card whose Needed by is
  the PO meeting the gap at the page (<walks>/p934-display/diary.md:88-97).
- PO-20 · P276 #312 (Idea): the catalogue editor, "with photos from the web and pins marked on the picture", step 7 of
  P269 (D8 to D10, 2026-10-16). The PO called it "the most important" job of P269 (D9: "number 7 is the most importatnt,
  in steps is ok, mvp first"). · E · gh issue view 312; docs/discovery/2026-10-16-p269-views-and-editors/brief.md:107-109
  · supports only: this epic's record editor is the first, small step of P276's job J4 (the fields and their sources).
  Pins on the picture and web photos stay in P276 (the brief's own out-of-scope agrees). The decider says whether
  P1161 becomes a slice of P276 or stands beside it.
- PO-21 · P269 #304 (epic, Idea): one base for every view, a web editor and a catalogue editor. · E · gh issue view 304
  · supports only: left alone. P1161 touches it only through P276.
- PO-22 · P340 #434 (Idea): research names the source for each open fact, keeps pictures, "shows what is still open,
  and asks the person whether to look further". · E · gh issue view 434 · supports only: the research engine side,
  left alone. The page's "what is not checked" fold (canvas:StorePart.dc.html:22, "8 facts are not checked") is the
  screen where its "asks to look further" would show.
- PO-23 · P997 #1454 (Idea) and P998 #1457 (Idea): research by the part's own marking, and the rule for a fact that
  research cannot settle (research, a bench trial, a simulation, or the person's word). · E · gh issue view 1454, 1457
  · supports only: left alone as engine work. P998's "the person's word" overlaps the record editor: a person setting a
  fact from the bench is the same write as P998's last option. Keep one design for "the person sets a fact, with its
  source".
- PO-24 · P230 #218 and P286 #336 (both Idea): research a dev board and write its board record. · E · gh issue view
  218, 336 · supports only: left alone. A board edit or board research from the page waits on them (PO-10).
- PO-25 · P884 #1252 (Idea): buy lines from the records (maker, code, link, in the drawer), with "no price, no stock
  and no other shop". · E · gh issue view 1252 · supports only: left alone. It is the line that keeps "find online by
  criteria" from becoming a shop search (D-e).
- PO-26 · P1162 #1698 (Idea): drag and drop on the pages. · E · gh issue view 1698 · supports only: out of scope by the
  brief. A dropped photo on an identify screen would be the one place where they meet.
- PO-27 · P1124 #1654 (Build): moving a hold between projects in one step. · E · gh issue view 1654 · supports only:
  left alone. It is a store screen beside this one (canvas:StoreMove.dc.html:45) with no record edit.
- PO-28 · P1152 #1688 (Idea) and P1160 #1696 (Build): kept steps, history and take-back; what goes out of date after
  a take-back. · E · gh issue view 1688, 1696; docs/discovery/2026-11-25-spark-and-git/brief.md:125-128 (D8, D9, D11)
  · supports only: left alone, but the record editor depends on them. A part-record edit in a project is a decided
  record (D8). An edit on the shelf, the catalog or the drawer lives in the store, outside git. P1160's link map should
  list "a record fact changed" as a link that makes the board files and the sheet stale.
- PO-29 · P1002 #1461 (Idea, not in the brief's list): "spark offers each new finding to be kept in the store". The
  PO's words, 2026-11-22: "lets make it so that its always offering the new findings to be stored to the store in
  general". · E · gh issue view 1461 · supports only: the strongest overlap outside the given list. It is the edit
  that the PO asked for in a real walk, and it goes from the bench to a record. The brief's line "P1002 #1461 in
  Discovery" does not match the board, which says Idea (gh, 2026-11-25).

### MVP and later

- PO-30 · Against AGENTS.md's bar ("does it move a basic project closer to a breadboard with working firmware?"), the
  part that moves a project is the one that unblocks a pick. That is a need with no fitting part (P992), and a record
  that "still lacks what spark needs" before the parts list (`OWED_MESSAGE`, "Ask Claude how to fill it in"). Both are
  page offers on screens that exist (Parts, StorePart), and both stay "Ask Claude" sentences under D-c. Editing a
  drawer entry or a fact for its own sake, the online search by criteria, a board editor and photo upload do not move
  a basic project today, because each path runs in the chat already (PO-2). · H, from E: flow_codes.py:181-183
  (OWED_MESSAGE), gh issue view 1445, AGENTS.md Principles · supports only: a proposed split for the tech lead and the
  decider, not an order.
- PO-31 · Proposed MVP, smallest first: (1) on Parts, a need with no fitting pick gets "Ask Claude" offers to research
  or identify, each with a `tell` (P992's first half). (2) On StorePart, the unchecked facts get "Ask Claude" to check
  them or to write a bench result, through `fact-set` (canvas:StorePart.dc.html:65 already has this sentence).
  (3) The journey picture names where research sits: between Needs and Parts, and again after the Bench. Later: a
  `from_page` drawer edit, a criteria form, numeric filters, board edits (after P230), photo upload, and pins on a
  picture (P276). · H · PO-1, PO-3, PO-11, PO-14 · supports only: a proposal.

### Found on the way

- PO-32 · Drawer seller names differ in case: `aliexpress` in 2 entries, `AliExpress` in 1. An edit screen would show
  both as two shops. · E · the count in PO-8 · supports only: a data fix, outside scope.
- PO-33 · The brief lists P1002 #1461 as "in Discovery". The board says Idea. · E · gh issue view 1461 --json
  projectItems, 2026-11-25 · supports only: a correction to brief.md's item line.

## What I could not check, and why

- Whether a Claude Artifact page can take a photo or a file upload and hand it to Claude Code. I did not call
  `describe_capabilities`: the lens has no need to load the Artifact tools, and the brief keeps the web for
  existing-first searches. The architecture lens should check it before (c) gets a page screen.
- Mouser's Search API: the page timed out after 60 s (2026-11-25). Its terms, limits and parametric filters: —.
- DigiKey, TME and Nexar terms behind the login (rate limits, whether a hobby use is free, the TME price): the landing
  pages state none of these. I did not register.
- GME, Hadex, LaskaKit and Botland: the one search found no API or feed. I did not open their sites, so whether their
  web shops filter by parameters for a person is —.
- LCSC's own website parametric filters (for a person, not the MCP): not opened. Only the MCP was tried.
- The token cost of a research run: the diaries give wall time, not tokens. I did not run `run_cost.py` on a walk.
- The primary user (the hobbyist): nobody beyond the PO is reachable (brief, Start and reach). Every account here is
  n = 1.
- Whether the shelf-copy staleness of PO-17 (c) is fully fixed: the display2 diary (line 194) names a fix with a test
  (PR #1460). I did not re-run `--fact-set` on a shelf copy.

## Questions for the decider

- Q-a · Does an edit from the page stay an "Ask Claude" sentence, or does a drawer-entry edit become the first store
  kind that the page sends itself (`from_page` true), like Pick? · decides: whether the record editor in this epic is
  a screen of sentences or a form with a button, and whether D-c's "no free text in a channel" needs a new answer.
- Q-b · May a person set a fact to `verified: true` from a page, and if so, what must the source say (who, when, how,
  as `fact-set` asks for a bench result)? · decides: the edit form's fields and the guard against PO-17 (b).
- Q-c · Is "find online by criteria" Claude's web search under parts-researcher's rules, with criteria as words, or a
  numeric filter on records spark already knows, or both? · decides: whether the epic needs new core work (a
  numeric filter, a criteria record) or only a sentence.
- Q-d · Does P1161 absorb P992's research-and-identify half, and does it become a slice of P276 (the catalogue editor),
  or stand beside both? · decides: the cards to merge or close, and the epic's parent.
- Q-e · Does P1002 #1461 (a finding offered to the store) belong in this epic as its first edit? · decides: whether the
  first edit is the one the PO asked for at the bench.
- Q-f · Is a board-record edit in scope before P230 (board research) exists? · decides: whether the epic carries core
  work for board facts (PO-10).
- Q-g · What pass line must the next walk meet for PO-16's test, set before the walk? For example, "at k of n points
  the PO uses the page's sentence rather than his own words". · decides: whether a page-first start is worth building
  beyond sentences.

## Searches

Six web searches, the budget.

1. `@jlcpcb/mcp npm component_search license` · served: whether spark's own parts-search tool is free, local and
   parametric (Q-c) · used (PO-4); then the README was fetched.
2. `DigiKey Product Information API v4 KeywordSearch parametric filters free developer account rate limit` · served:
   whether DigiKey's search is a free, parametric outside option (Q-c) · used (PO-5); then the product page was fetched.
3. `Nexar Octopart API free plan parts per month 2026` · served: the cost of Octopart's parametric search (Q-c; the
   rule "name any cost") · used (PO-5); then compare-plans was fetched.
4. `TME API products search parameters GetParameters developer free` · served: whether an EU shop the PO prefers offers
   a parametric API (Q-c) · not used: the results were off topic. developers.tme.eu was fetched directly instead (PO-5).
5. `GME Hadex LaskaKit Botland API XML feed produkty parametry` · served: whether the Czech and Polish shops the PO
   prefers offer a machine-readable search (Q-c) · not used: no result named the shops.
6. `identify electronic module or IC from photo chip marking recognition app free open source` · served: whether an
   outside tool does job (c), free and local · used (PO-13).

Also, not web searches: two `mcp__jlcpcb__component_search` calls with the query "ST7789 IPS display module SPI" and
`source` `all` and `lcsc` (PO-4), and one fetch of https://www.mouser.com/api-search/, which timed out.
