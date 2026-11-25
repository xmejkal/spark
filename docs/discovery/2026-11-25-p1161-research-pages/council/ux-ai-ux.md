# P1161 council: the UX and AI-UX lens

The lens of the PO's rule of 2026-10-18: each job names what the person does and sees, and what Claude reads and calls.
Read on 2026-11-25 (Prague): the canvas copies of that evening (cited `canvas:<file>:<line>`, lines as the files stand),
the P1113 council folder in the store (`<store>/councils/p1113/`), the commands, the agents, the code named below, and
`parts.py --describe --json` and `parts.py --need display --json` (keys only). Every sketch below is a proposal, not a
decision.

## 1. Findings

### The four findings that change the design most

- **UX-1 · Typed criteria and typed values cannot travel on the page's channel. A form on the page can only fill the "Ask Claude" sentence.**
  The decided channel carries `id, key, seen` and never text. "Ask Claude" sends nothing: it copies a sentence. So
  criteria the person sets (volts, size, shops) and a new fact value reach Claude only as words in the copied sentence,
  never as fields. There are two ways for a later direct channel to carry them: (a) write the criteria and the values
  into a record first, so the offer's `tell` names only ids (for example "Find a part for the %s need of this project",
  filled by spark the way `PICK_LABEL` is), or (b) keep these jobs as copy-only for good. The canvas's "could be one
  click later" for drawer edits (canvas:Store.dc.html:175, :178; canvas:StorePart.dc.html:59) holds only for an edit
  with no typed value, such as "turn off unsure".
  · E `<store>/councils/p1113/architect-page-actions.md:52` ("A channel carries `id, key, seen`. Never text, argv or a path"), :22 · E commands/page.md:113 · E scripts/spark/flow/flow_codes.py:148-155 (every `tell` today is a fixed sentence with no slot) · D the PO, 2026-11-25, P1122 #1652 ("a test pins that no channel carries text")
  · supports only: the sentence is the hand-over today. It does not show which of (a) or (b) the PO wants.

- **UX-2 · No edit of a store record or a drawer entry is a kept step, so the "Undo" moment cannot take one back. A fact write cannot empty a fact either.**
  D8 keeps only the project's decided records (brief, needs, picks, requirements, board). A drawer write, a fact write
  into a shelf or catalog record, and a record that a research writes are outside D8's list. `fact-set` refuses to
  empty a fact ("a write fills a fact, it never empties one"). So a wrong value that replaced a `null` cannot go back to
  `null`. `fact-set` does answer `was` and `now`, the only trace of what an edit replaced. StoreMove already promises
  "undo that brings both holds back" (canvas:StoreMove.dc.html:32), and D8 itself marks the store as outside git.
  · E docs/discovery/2026-11-25-spark-and-git/brief.md:125 (D8 and its caveat UX-3) · E scripts/spark/sourcing/set_facts.py:29 (`data_keys` with `was`, `now`), :49 · E canvas:Undo.dc.html:90 ("Kept the goal, the needs, the picks, the parts list, the board")
  · supports only: today the page cannot offer "take this edit back" for the store. Whether store writes become kept steps is the decider's choice.

- **UX-3 · "Tell me the cost first" has nothing behind it. No research command or agent works out a cost before it runs, and the page shows none.**
  The canvas sentences ask Claude for the cost (canvas:Store.dc.html:177; canvas:StorePart.dc.html:65), and StoreAdd
  promises it (canvas:StoreAdd.dc.html:33, "Claude tells you the cost first"). `commands/research.md`,
  `commands/identify.md`, `agents/part-finder.md` and `agents/parts-researcher.md` have no cost step: a grep for "cost"
  and "token" finds none. What exists:
  - each agent's hard budget (part-finder: 3 searches and 2 fetches, haiku; parts-researcher: 8 searches and 12 fetches, opus);
  - three measured runs from 2026-10-03 (one LED about 0.55 M tokens and 148 s; part-finder about 0.17 M tokens and 91 s; the old protocol about 5.0 M);
  - `cost.py`, which measures a run afterwards from its transcript.

  The page's cost line should be spark's words from those: the budget, the model and the last measured run of that kind.
  Claude should not estimate it freely.
  · E agents/part-finder.md (header `model: haiku`, "How — and the budget") · E agents/parts-researcher.md:11 · E docs/guide/research-cost.md:9-11 · E scripts/spark/sourcing/run_cost.py:1-15
  · supports only: a range from one past run of each kind (n = 1 each). No module research by opus was measured.

- **UX-4 · Find by criteria has an agent only for commodity parts. For a module or board, the research picks the first vendor's fit and writes its record before the person chooses.**
  part-finder returns at most two candidates and writes nothing, but only for an LED, diode, button, connector or
  regulator. A module goes to parts-researcher, which stops "at the first vendor with a part that fits the need unless
  you were asked to compare" and writes a record. The PO's "a part/board/module that could do what we need, setting up
  criteria" therefore has no path where he sees two module candidates and picks before tokens go on reading
  datasheets. Candidates that are not chosen do get a home: a catalog record with `why_not`, or an `alternatives` line.
  · E commands/research.md:37-48, :69-75 · E agents/parts-researcher.md:35-38, :78-82 · E agents/part-finder.md:16 · H the PO's words in #1697
  · supports only: the gap in the flow. Whether a module find should become two-step is open.

### Screens: what changes, what is new (job a to d, plus the journey)

- **UX-5 · Job (a), editing a fact: StorePart lists each fact's state and source but has no way to edit a fact. The confirm must name where the write lands and who reads it.**
  StorePart's "What spark knows" lists 14 facts with "? Not checked" and a source (canvas:StorePart.dc.html:33). Its
  actions are an entry edit, a move, sources, documents and keep (:59-63). `op:fact-set` appears only in the Now card's
  key line (:26). `fact-set` writes "in the record's own home". For a shelf copy, that home is the project the record came
  from, and the shelf copy follows. A record in spark's library is refused. So before the yes, the person must see three
  things:
  - which file changes (for example "p581-sound-joystick's record, and your shelf copy follows");
  - that a library record cannot be edited here;
  - which projects use the record and what goes out of date. A pin-order edit makes a holder's board files and wiring
    stale, which the Change moment already draws.

  · E scripts/spark/sourcing/record_home.py:179-217, :165-176 · E canvas:Change.dc.html:104 · E canvas:StoreMove.dc.html:20 (the "before/after per project" pattern to reuse)
  · supports only: the pieces exist, but the edit answer has no `makes_stale` or holders field today (`data_keys` at set_facts.py:29).

  Sketch, StorePart changed (a fact row gets "Edit", and one edit card opens in place of the Now card):

  ```
  +--------------------------------------------------------------------------------+
  | Fermion 2.0 in IPS display   DFR0664  · held by p581-sound-joystick             |
  |                                                                                |
  | NOW · Edit one fact · you                                                      |
  |  Order of the 10 header pads                                    ? Not checked   |
  |  Now:  VCC … SDCS        from: dimension drawing, page 1 (read off an image)    |
  |  New:  [ VCC GND SCLK MOSI … SDCS                      ]                        |
  |  Where from?  (o) I read it on the part   ( ) a maker's page   ( ) I measured   |
  |               words: [ silkscreen, back face, 25 Nov            ]               |
  |  This writes  p581-sound-joystick's record; your shelf copy follows             |
  |  Out of date  p581: wiring and board files  ↻                                   |
  |  [ Ask Claude ]  "Set the header pad order of dfr0664-tft-2in to …, from the    |
  |                  silkscreen I read on 25 Nov. Show me the lines first." [Copy]  |
  |  Claude shows was → now and waits for your yes. Today an edit is no kept step.  |
  +--------------------------------------------------------------------------------+
  | › What spark knows   14 facts: 6 checked, 8 not          [Edit] on each row     |
  | › Your drawer        count 1 · place not set             [Edit]                 |
  | › Change this part   move · sources · documents · keep a file                   |
  +--------------------------------------------------------------------------------+
  ```

- **UX-6 · Job (a), the drawer entry: StorePart's drawer block shows count, place and holder but edits only through one sentence that has its value already written in.**
  The block (canvas:StorePart.dc.html:33, "Count 1 piece … Place not set") and Store's "Edit an entry" (canvas:Store.dc.html:178)
  carry a fixed sentence with the value in it ("parts box 2"). No field exists. The canvas's one input is Store's search
  (canvas:Store.dc.html:37). Two sentences copy a hole where the person's words go: "Add to my drawer: ." (canvas:StoreAdd.dc.html:45;
  canvas:Store.dc.html:175) and "with its URL ." (canvas:StorePart.dc.html:63). The person sees first the entry's fields
  as they are. He confirms the drawer-set's dry-run lines ("~ count 4 → 6"), which StoreAdd already draws (:33).
  · E canvas lines named
  · supports only: the sketch below is a proposal.

  ```
  | Your drawer · Fermion 2.0 in IPS display                                       |
  |  Count  [ 1 ]   Place [ parts box 2      ]   ( ) not sure I own it            |
  |  Held by p581-sound-joystick ×1 · free 0                                       |
  |  You see first:  ~ place: not set → "parts box 2"                              |
  |  [ Ask Claude ] "In my drawer, set … place to “parts box 2”. Show me the       |
  |                  lines first."  [Copy]                                         |
  ```

- **UX-7 · Job (b), research a named part: the record-less entry has no screen of its own. Store's row says "○ no record · spark does not know it yet", and the research is one folded line among four.**
  Store's row (canvas:Store.dc.html:162) and the fold "Change your store: add, move, research, edit" (:84, :177) are the
  only places. StorePart is drawn only for a part that has a record. Proposal: StorePart has a second state, "Not known
  yet", whose main card is the research. Its cost line follows UX-3. Its "what it will not gather" line follows D-e: no
  prices, stock or sellers. While a research runs, the page can show nothing. It is a snapshot, written again only at
  `/spark:page`, and "Ask Claude" sends no request row the page could watch. So "running" lives in the chat, and the page
  says so in words. Afterwards the record shows as StorePart's normal state, with "N facts checked, M not" and the
  unchecked list as the next card.
  · E commands/page.md:113 · E docs/discovery/2026-11-23-p1038-page-design/README.md (the page is a snapshot, D5) · E commands/research.md:87-88 (no prices, stock or sellers)

  ```
  +--------------------------------------------------------------------------------+
  | Fermion 1.8 in IPS display, MicroSD   · in your drawer ×1 · free                |
  | ○ spark does not know it yet                                                    |
  |                                                                                |
  | NOW · Research it · you, with Claude                                            |
  |  Spark finds its maker's page and datasheet and writes what a build reads.      |
  |  Cost  up to 8 web searches and 12 page reads, by the larger model.             |
  |        The last module research measured: — (none measured yet).               |
  |  Not gathered  prices, stock, sellers.                                          |
  |  [ Ask Claude ] "Research the Fermion 1.8 in IPS display (DFR0928) from my      |
  |                  drawer. Tell me the cost first."                     [Copy]    |
  |  It runs in Claude Code. This page shows the result after /spark:page.          |
  +--------------------------------------------------------------------------------+
  | after:  ✓ record dfr0928-…   14 facts: 6 checked, 8 not  → "Check what is not   |
  |         checked" becomes the Now card                                           |
  ```

- **UX-8 · Job (c), identify from photos: the photo can only go to the chat, and the person's confirm of Claude's reading has no place on the page. StoreAdd's fold also says something that does not match the command.**
  StoreAdd's fold says "every fact marked not checked" (canvas:StoreAdd.dc.html:33). identify.md marks facts from the
  chip's datasheet `verified: true` and only what the photo alone supports `verified: false` (commands/identify.md:53-56).
  Three more gaps:
  - The command shows its reading as "Read / Not read" to the person before any search (identify.md:22-33). That is
    the natural yes point, before tokens go on searching. The page has no step for it.
  - The page sends no file, and the photo must stay in the person's store, never in a repository (identify.md:75). So
    the page's job is to show how to take the photo (both sides, flat, with a ruler) and hand over to the chat.
  - AGENTS.md: never commit a photo with GPS data. The page should say that the photo stays private.

  · E lines named · E commands/page.md:113

  ```
  +--------------------------------------------------------------------------------+
  | NOW · Identify a part from photos · you, with Claude                            |
  |  1 Take both sides, out of the bag, flat, a ruler in frame.   [ill.: two faces] |
  |  2 Drop the photos into the chat with Claude.                                   |
  |  3 Claude lists what it read and what it could not. You say yes before it       |
  |    searches.                                                                    |
  |  Cost  up to 8 searches and 12 page reads after your yes.                       |
  |  Your photos stay in your store, never in a project's repository.               |
  |  [ Ask Claude ] "Identify the module in the photos I send next. Show me what    |
  |                  you read before you search."                         [Copy]    |
  +--------------------------------------------------------------------------------+
  | after: the record (facts from the chip's datasheet ✓, from the photo ?) and a   |
  |        drawer line to confirm: + "<name>", count 1, photos 2                    |
  ```

- **UX-9 · Job (d), find by criteria: a new moment. Three of the PO's six criteria already have homes, at the project level. Per-need limits have none, and "what I own" must not reach the agent.**
  - What it does: a need's `does` and `what`.
  - Shops: the brief's `prefer` (vendors to research in) and `sellers` (where he buys).
  - Limits such as voltage, current, size and breadboard fit: no per-need field exists. The brief's `must` holds
    project lines. The word `limits` already means something else in `parts.py --match`: what a passed run does not test.
  - What he owns: `--need` and `--match` already rank owned parts first, on the machine. drawer.md says "A research
    agent gets the need, never the drawer". part-finder's input says "what they already own", so the two rules conflict.

  The page should run the free local search first ("you own these"). Only on "none fits" does it offer the online find,
  with a cost line. The two candidates then show "fits because" and "not" (part-finder's own return format), plus what
  is unknown until the datasheet is read.
  · E scripts/spark/records/brief.py:3-7 · E scripts/spark/design/needs.py:144, :234 · E commands/drawer.md:94 · E agents/part-finder.md:16, "What you return"
  · supports only: where the fields could live. Whether a per-need limit enters the records is "records grow by need", the decider's call.

  ```
  +--------------------------------------------------------------------------------+
  | Find a part for: "A screen" · E-paper quotes clock                              |
  | ●──●──◐──○──○ ...                                       (the line of steps)     |
  |                                                                                |
  | NOW · What should it do, and within what limits · you                           |
  |  Does      [ indicate ▾ ]  [ shows a quote, e-paper                ]            |
  |  Limits    supply [ 3.3 ] V  current ≤ [    ] mA  width ≤ [ 70 ] mm             |
  |            [x] plugs into a breadboard (through-hole, 2.54 mm header)           |
  |  Shops     DFRobot, Seeed  (from your project; change)                          |
  |  First, free, on your machine:  your drawer has 1 fit, 1 held → [ see them ]   |
  |  Online:  up to 3 searches, 2 page reads, small model. About 0.17 M tokens the  |
  |           one time it was measured. No prices or stock.                         |
  |  [ Ask Claude ] "Find at most two parts for the screen need of the e-paper      |
  |                  clock: …limits…. Tell me the cost first."            [Copy]    |
  +--------------------------------------------------------------------------------+
  | after (in the chat, then on this page once kept):                               |
  |  1 Maker A  PN-1234   fits: 3.3 V, 2.54 mm header   lacks: no width published   |
  |  2 Maker B  PN-5678   fits: e-paper, 66 mm          lacks: 5 V only             |
  |  [ Research 1 ] [ Research 2 ]   each: cost line again, then a record           |
  +--------------------------------------------------------------------------------+
  ```

- **UX-10 · On the project page, the Parts moment has no "none of these" exit, and the bench has no place for a measured fact.**
  - Parts shows only store options for each need (canvas:Parts.dc.html:153-161). Even with the IPS display "off"
    (held), no tile says "not here: add a part". P992 #1445 asks for exactly that: research, identify, draw. The
    proposal is a last tile on each need card that opens the three ways of UX-7, UX-8 and UX-9. The need's words fill the
    criteria. The new record then shows as an option for that need, as P992's Done-when asks.
  - The bench: StorePart tells the person "Check the silkscreen before wiring" and "Confirm on the bench"
    (canvas:StorePart.dc.html:33). The Bench artboard's wiring step has only a power note
    (`<store>/councils/p1113/Bench.dc.html:74`, the 25 Nov 07:48 copy). The P1161 copies hold no Bench file. So a step
    that wires a part with an unchecked pin order could ask "Does the silkscreen read VCC first? Yes / No / Can't tell".
    A yes is a bench fact (`fact-set`, `verified: true`, with a source of who, when and how), sent as "Ask Claude".
  - The Change moment (canvas:Change.dc.html:102-107) is where a fact edit's effect lands in each project that holds the
    part.

  · E lines named · E #1445 Done when · E commands/research.md:108-109 (a bench result's source)

  ```
  Parts moment, one need card, changed:
  | Need 2 · A screen · shows the quote: a display, e-paper                         |
  | [ MH-ET 2.9 e-paper  In your drawer ] [ Fermion 2.0 IPS  Held ] [ + Not here? ] |
  |                                                    └→ I own it: photos          |
  |                                                       I know its name: research |
  |                                                       Find one by what it does  |

  Bench, phone, one step, changed:
  | Wiring · 4 of 12                                                               |
  | Display VCC to the + rail                                                      |
  | ? Not checked: the pad order. Look at the back: is the first pad VCC?          |
  |   [ Yes ]  [ No ]  [ Can't tell ]   → Ask Claude: "Record on dfr0664-tft-2in:  |
  |   the silkscreen shows VCC first, seen by me on 25 Nov." [Copy]                |
  ```

- **UX-11 · The Undo moment lists only project steps. Store edits need either their own list or a plain line saying they cannot come back yet.**
  The Undo list holds the goal, needs, picks, parts list and board (canvas:Undo.dc.html:108-121). Until the decider
  rules on UX-2, the edit card should say "Today an edit is no kept step. Its old value is: <was>". `fact-set` answers
  `was`. That beats implying the "undo that" line covers the edit, a line spark says after every kept step
  (canvas:Undo.dc.html:86-87).
  · E lines named · E set_facts.py:29

### AI-UX: what Claude reads, calls and reports back

- **UX-12 · Claude has no Operation to call for identify or find, and no single one for research. `--describe` lists their pieces but not the jobs, so a page offer has no key to name.**
  `parts.py --describe` lists `need`, `match`, `offer`, `unverified`, `skeleton`, `fetch`, `sources`, `find-documents`,
  `keep`, `read`, `drawer-set` and `fact-set`. `op:research-part` is DFRobot geometry only. Identify and find live only
  in commands and agents. The canvas keys show this: "op:need → /spark:research" (canvas:Store.dc.html:177),
  "op:need · op:fetch · op:read" (canvas:StoreAdd.dc.html:33). A chat offer needs a key and a `tell` sentence. Per
  P1122, research, identify and find become chat offers (`from_page` false), each with a `tell`. They are never sent from
  the page, because they declare `fetches` (P1122's rule: never from a page).
  · E `parts.py --describe --json` run 2026-11-25 (op names and effects) · E docs/guide/design-basis.md:144-148 · E `<store>/councils/p1113/architect-page-actions.md:63-64`
  · supports only: which keys are missing. Whether each job becomes one Operation is the architecture lens's question.

- **UX-13 · Claude reports in prose that the page cannot read. The page draws only records, so a result shows only once it is written into one.**
  The page takes no fact from anything but `flow.py show` and the records (P1060). The agents report differently:
  - part-finder returns numbered text and writes nothing;
  - parts-researcher returns a path and a list of what it could not confirm;
  - identify's reading is a chat list.

  So the two candidates of UX-9 vanish from the page unless they are kept: a catalog record with `why_not`, as
  parts-researcher already does for candidates not chosen. The "what each lacks" a page can show is `parts.py --match`'s
  `owes` and `limits` for store candidates. For web candidates it is part-finder's `not:` line, which no JSON key holds.
  `parts.py --need --json` answers `found[]` with `id, entry, is, kind, name, in, owned, score, why`, and no "lacks" key.
  · E commands/page.md (the "take no fact from page.html" rule) · E agents/part-finder.md "What you return" · E agents/parts-researcher.md:21, :78-82 · E `parts.py --need display --json` keys, run 2026-11-25
  · supports only: the shapes today.

- **UX-14 · What Claude must never decide alone, as the evidence states it:**
  - **No write without the person's yes.** Every write needs his yes after the shown lines: `--dry-run` for drawer-set
    and fact-set, or the `was → now`. The canvas words already say "Show me the lines first".
  - **No fact without a source.** `fact-set` takes `{value, verified, source}`, and a bench result is verified with
    who, when and how.
  - **`verified` is not Claude's to choose for a person's typed value.** Today the person's "I read it on the part" has
    no stated state. The research rule makes a reading off an image `verified: false`, so a person's reading of the
    silkscreen is a case the rules do not name.
  - **No start of a research because a part is owned** (D-e).
  - **No drawer text in a search or an agent's prompt** (drawer.md:94).
  - **No stand-in for a `null`.** A value it cannot find stays `null` (never-assume).

  · E scripts/spark/sourcing/set_facts.py:30 (the argument's help) · E commands/research.md:12-14 · E commands/drawer.md:94 · E AGENTS.md (never assume) · E agents/parts-researcher.md (the rule on `null`)
  · supports only: the rules exist. Whether "I read it on the part" counts as checked is open (Q3).

### Words

- **UX-15 · "Checked" on the canvas covers three different sources, and it collides with spark's status word "not checked".**
  On StorePart, "✓ Checked" stands beside "wiki specification table" (canvas:StorePart.dc.html:33). In the records,
  `verified: true` means the maker's text at a cited page or a bench result. `verified: false` means it was read off an
  image. So the maker's datasheet, the person's own measurement and Claude's reading of a drawing collapse into two
  marks. Spark's status words also use "not checked by spark" for a missing status and "?" for not checked
  (patterns-and-names.md:40). The page's "? Not checked" next to a fact means something else.

  Proposal: one word per source, shown with the mark:
  - "the maker says" ✓
  - "you measured" ✓
  - "read off a picture" ?
  - "not found" — (null)

  · E commands/research.md:12-14 · E docs/guide/patterns-and-names.md:40 (status words and marks) · E canvas lines named
  · supports only: the collision. The words are proposals.

- **UX-16 · Word collisions the screens and Claude would meet:**

  | word | the canvas means | spark also means | collision |
  | --- | --- | --- | --- |
  | record | what spark knows of a part | part, board and deploy records; the records area | low. The layer (project, shelf, library, catalog) matters for an edit (UX-5) and is not shown on StorePart |
  | entry | a drawer line | requirements.json's entries (`EntryOriginStore`), the projects list's entries | medium in Claude's words, none on screen |
  | fact | one line of "What spark knows" | `facts` in a record; "the facts" of a CLI's text view | low |
  | source | where a fact came from | a fact's `source`; `parts.py --sources` (do the URLs answer); `research_source` (wiki, kept documents) | medium: "Check its sources" (canvas:StorePart.dc.html:61) checks URLs, not facts |
  | research | the whole job of finding and writing a record | `/spark:research`; `op:research-part` (DFRobot geometry only) | high: the op's name promises more than it does |
  | identify | photo to record | only a command; no op | none yet |
  | find | the Store search box (canvas:Store.dc.html:37); "Find its documents" (:62) | `--need` (a search in what you own); part-finder (online); `find-documents` | high: three different reaches (local, the store, the web) under one verb and one icon ("search", canvas:Store.dc.html:113) |
  | criteria | — (absent) | brief `must`, `prefer`, `sellers`; need `does`, `what`; match `limits` (another meaning) | high for "limits" |
  | candidate | a part offered for a need | `--match` candidates (store); part-finder candidates (web); `parts.py --offer` = one candidate's self-description, while a flow *offer* is a step | high: "offer" means two things |
  | checked | see UX-15 | | high |

  · E docs/guide/patterns-and-names.md:21, :40 · E docs/guide/design-basis.md:56-62, :160-169 · E canvas lines named

## 2. What I could not check, and why

- Bench.dc.html, States.dc.html, Done.dc.html, Board.dc.html, Breadboard.dc.html and Icons.dc.html are in canvas.json,
  but the brief's copy folder holds only Main, Start, Parts, Change, Undo, Store, StorePart, StoreAdd and StoreMove. I
  read the older Bench copy in `<store>/councils/p1113/` (25 Nov 07:48), which may differ from tonight's.
- docs/discovery/2026-11-23-p1038-page-design/design.md and docs/guide/design-basis.md were read only in part, by grep
  and the README.
- How the pages look and behave: I read the markup, not a rendered page.
- The token cost of a module research by parts-researcher (opus). No measure exists in the repository.
- Whether `fact-set` accepts a person's reading with `verified: false` and a source of "silkscreen, me". The help text
  allows `{value, verified, source}`. I ran no write.
- The PO's view of a criteria form against a sentence. Nobody asked him.
- No web search, per the brief.

## 3. Questions for the decider

- Q1 · Do criteria and typed values go into records first (the need, the brief), so a later direct channel carries only ids? Or do these jobs stay copy-only with the criteria in the sentence? · decides: UX-1, whether the find form writes a record, and whether "one click later" holds for any edit with a value
- Q2 · Is an edit of a store record or a drawer entry a kept step that "undo that" brings back? Or does the edit card say plainly that it is not, and show the old value? · decides: UX-2, UX-11, the Undo moment's list, and StoreMove's promise
- Q3 · Does the page show four sources ("the maker says", "you measured", "read off a picture", "not found") in place of "checked / not checked"? And which state does a person's own reading of a part get? · decides: UX-14, UX-15, StorePart's fact rows, the bench's yes/no step
- Q4 · For a module or board found by criteria, should the person see two candidates and pick before any datasheet is read, as for a commodity part? · decides: UX-4, UX-9, whether research becomes two-step for modules
- Q5 · What cost line does the page show before a research: the budget and model alone, or also the last measured run of that kind? And who keeps that measure? · decides: UX-3, the cost line's words and their source
- Q6 · Where does each job enter the project page: a "+ Not here?" tile on every need card in Parts (P992), and a yes/no on the bench for an unchecked pin order? · decides: UX-10, the screens that change outside the store

## 4. Searches

None.
