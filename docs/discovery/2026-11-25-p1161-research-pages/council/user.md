# P1161 council: the user lens (the user's journey)

Lens: the PO as the one user (n = 1). Four jobs: (a) a fact in a record is wrong or not checked, (b) an owned part
has no record, (c) an owned module has no marking he knows, (d) a need has no part and he wants candidates found online
by his criteria. Read on 2026-11-25 between about 20:20 and 20:45 CET. Pointers: `canvas:<file>:<line>` is the
design canvas copy, `<store>/<path>` the PO's store, `<walks>/<path>` the walk folders, other paths are this
repository. Tags: E with a pointer, H with its source, D with who and when, — for an unknown.

## Findings

USER-1 · In the one past case where a record's fact was wrong and mattered, research did not settle it, and the bench
did. The e-paper record named SSD1675A (from a community README), with SSD1680 and SSD1675B as other answers. A
three-candidate trial firmware on his breadboard showed that the IL0373 command set draws, and the other two "changed
nothing". Job (a) for a fact that the module hides (the controller is bonded on the glass) ends at a bench trial, not at
a web search · E `<walks>/p934-display2/diary.md:157-165`, `:268-271`; `gh issue view 1457` (P998) · supports only:
that a page for job (a) needs a "settle it on the bench" path beside "research it again"; not how often this happens
(1 of 1 case seen).

USER-2 · The StorePart design's main offer sends two facts to the datasheet that the same artboard calls "not
published". The NOW sentence is "check the peak current and the logic thresholds from its datasheet", while the fact
rows say "Peak current … not published … Measure on the bench" and "Logic high and low thresholds … not published".
The record's own note for the peak current is "measure on the bench with BL high and a card writing". He would pay
tokens for a search that cannot answer · E `canvas:StorePart.dc.html:65` against `canvas:StorePart.dc.html:33`;
`parts.py --unverified dfr0664-tft-2in`, run 2026-11-25 (exit 0) · supports only: that the page must say, per fact,
who can settle it (the net, a datasheet already kept, his eyes, a meter, a trial).

USER-3 · Of the DFR0664's unchecked facts, most are for his eyes or his meter, not for the net. `--unverified` lists
9 (the canvas says 8, because it joins input_high_v and input_low_v). Pin order against the silkscreen (his eyes,
a photo), on-board pulls (a meter), peak current (a meter), GDI pins on the board (a library test on the bench),
series resistors and the GDI cable order (read off a kept schematic image: a datasheet read, no new search). So 0 of
9 need a new web search, by the record's own notes · E `parts.py --unverified dfr0664-tft-2in`, 2026-11-25 · H the
split into who settles each one is this lens's reading of the notes, not a field of the record · supports only: that
job (a) on the page is mostly "tell spark what you saw or measured", which needs an input of his.

USER-4 · No page and no command lets him change one fact the way he thinks of it ("this is wrong, it is X"). Today a
fact changes only through `parts.py --fact-set <id> <file>`: a JSON file with a `write` key and a `source` naming
who, when and how, written by Claude after his yes. In the e-paper case the record's `host_requirements` kept the
wrong driver after the bench because `--fact-set` had no key for it; it was fixed by hand that evening. The design's
"Edit the entry" edits the drawer entry (its place), not a fact of the record · E `commands/research.md:108-109`;
`<walks>/p934-display2/diary.md:280-281` and `:551` (row 15); `canvas:StorePart.dc.html:59` · supports only: that
an edit page needs a fact-level edit with a source, and that "entry" and "record" read alike to him.

USER-5 · A record has copies, and he cannot see which one he edits or which one a build reads. A shelf copy written
with no `based_on` was never refreshed, so a build of the next project read a stale copy and lost the drawn
breadboard he needed while wiring ("I need to see the breadboard, i've already connected it"). The fix merged (P1006
#1465), but the page designs name no copy · E `<walks>/p934-display2/diary.md:190-201`, `:546`; the shelf record
`<store>/shelf/epaper-2in9-bwr-mh-et-live.json` now carries `based_on` p934-epaper · supports only: that an edit
page must say where the edit lands and what it reaches.

USER-6 · The parts-pick design has no way out for a need with no fitting part. Its Send stays grey ("Pick N more
first") until every need is picked, and no card says "none of these", "I have one that is not here" or "find one
online". This is the moment where he said "what if it's not in the store ? I can still have it and want to add it" ·
E `canvas:Parts.dc.html:47`, `:196`; `<walks>/p934-display/diary.md:86-90`; `gh issue view 1445` (P992) · supports
only: that jobs (b), (c) and (d) start on the Parts screen as well as on the store screens.

USER-7 · Job (d), candidates online by his criteria, has no path today. A need's `condition` words only order the
candidates already in the store and never change a score; `parts-researcher` stops "at the first vendor with a part
that fits the need unless you were asked to compare", in the order DFRobot then Seeed; `part-finder` is for commodity
parts, returns at most two, runs on Haiku, and has not run in a walk; prices are never gathered · E
`commands/idea.md:40`; `agents/parts-researcher.md:36-37`; `agents/part-finder.md:4`, `:11-12`, `:43-45`;
`README.md:122` ("The part-finder and datasheet-reader did not") · supports only: that a criteria search is new
behaviour, not a page over an existing command.

USER-8 · Some of his criteria map to a fact a record keeps, some to none. "Under 20 mA asleep" maps to a module's
"Current asleep"; "fits on a breadboard" maps to `physical.header`; "readable outdoors" and a price map to no fact
kind, and prices are excluded by rule · E `commands/research.md:84`, `:86-88`; `commands/identify.md:31-34` · supports
only: that a criteria page must say which criteria spark can check against a record and which stay his judgment.

USER-9 · He asked for job (d) himself, in a walk, at the moment a picked part could not do the need: "it might also be
nice if spark offered me other options I have or can order onine … this module can only do x,y,x, not the thing you
need, so here are the alternatives options … and ask if I want it to search for alternatives online". The conflict
(cursor drawing against a 27 s full refresh) was found by him, not by spark · E `<walks>/p934-epaper/diary.md:196-205`,
`:251-261` · supports only: that (d) arises at the parts pick and again after a part disappoints, not only as a blank
search.

USER-10 · A page request carries a key only, so neither a photo nor criteria nor a measured value can travel from the
page. Every research job on the design is an "Ask Claude" Copy: copy, switch to Claude Code, paste, answer the
questions there, wait, then type /spark:page, then reload. A need's drop and every "chat offer" is refused from the
page by design · E `commands/page.md:113`; `scripts/spark/flow/request_codes.py` (REQUEST_IN_CHAT);
`canvas:Store.dc.html:97`, `canvas:StorePart.dc.html:46` ("The page sends nothing") · H that an Artifact page can take
an upload: the claude-artifacts server's own instructions mention pages that "take uploads"; not tried · supports
only: that the four jobs on the page are today a sentence to copy, and that photos are the hardest input to move.

USER-11 · Research writes into a project, and the store pages have no project. `/spark:research` writes
`parts/<id>.json` "in the project", and a record reaches his shelf only when a drawer entry links to it. The Store
design offers "Research a part spark does not know" from the store and says "Type /spark:page", while /spark:page
reads and republishes one project's page · E `commands/research.md:12`; `commands/drawer.md:48-49`;
`canvas:Store.dc.html:177`, `:97`; `commands/page.md:10-11` · — where a record researched from the store page lands,
and which command refreshes a store page · supports only: that job (b) outside a project has no home today.

USER-12 · Job (b) in his drawer is mostly a DFRobot part number. Of 114 entries, 19 link to a record; of the 95 that
do not, 90 carry a DFRobot part number, 3 a number with no maker and 2 none (the LiPo and the MP3 module) · E a count
over `<store>/drawer/*.json`, 2026-11-25 · supports only: that research by part number (the DFRobot wiki path,
`research.py`) covers most of his drawer; not that he wants them all researched ("owning a part never starts
research", `commands/drawer.md:11-12`).

USER-13 · Job (c) from photos is rare in his store: 4 of 114 entries keep a photo (the e-paper, the joystick, the
INMP441, the CJMCU-111), all four linked to a record · E a count over `<store>/drawer/*.json`, 2026-11-25 · supports
only: that identify from photos happened four times; not how many unmarked modules wait in the drawer (—).

USER-14 · Identify from photos broke in four places in the one walk that ran it end to end. No ruler in his photos,
so the size stayed null, `--validate` failed and `--unverified` refused to list anything until a size was guessed
from the header pitch; the agent kept two datasheets and one wrong file in his store without asking; the record was
linked to the drawer before the research for use, so the shelf copy froze; and nothing told him before the photos
that a module with no maker's document gets its size only from a ruler · E `<walks>/p934-epaper/diary.md:42-43`,
`:66-73`, `:78-81`, `:85-91`, `:106-111` · supports only: that a photo page must ask for the ruler shot before he
takes the photos, and show what each photo can and cannot settle.

USER-15 · A research run keeps him waiting in the chat for minutes. Seen: about 3 minutes (DFR0664, walk 4), 6 min 18
s and 6 min 20 s (the e-paper's two rounds), each with a 25 minute limit given; the designs say "may cost tokens"
and give no number · E `<walks>/walk4/walk4-diary.md:25-26`; `<walks>/p934-epaper/diary.md:57`, `:123`;
`canvas:Store.dc.html:177`, `canvas:StoreAdd.dc.html:33` · supports only: that a page needs a "running" state and a
cost line before the start; the token cost of these runs is —.

USER-16 · "Research" on a part spark already knows ends at once, so deepening a record has no command. In P711 he
wanted pictures for the known DFR0954; reuse-first found the record and the skill ended there. In the e-paper walk:
"no command searches further for one fact of a record that exists" · E `<walks>/p711-identify-amp/diary.md:14-24`;
`commands/research.md:23-25` ("A match is the answer"); `<walks>/p934-epaper/diary.md:96-98` · supports only: that
job (a) "check this one fact online" is a missing operation, not a missing page.

USER-17 · What he learns at the bench rarely reaches the record. Walk 4: "No spark command records this bench result";
the display's landscape setting (MADCTL 0x20, after 0x60 drew mirrored) is in no record (0 matches for madctl,
rotation or mirror in the shelf record). He asked: "lets make it so that its always offering the new findings to be
stored" · E `<walks>/walk4/walk4-diary.md:22`, `:151`, `:36-40`; grep of `<store>/shelf/dfr0664-tft-2in.json`,
2026-11-25; `<walks>/p934-display2/diary.md:288` · supports only: that job (a) also starts at the bench and firmware
moments, with a value he supplies.

USER-18 · Two rules pull against a store-page research button. The drawer rule: "A research agent gets the need,
never the drawer" and no drawer entry goes into a web search; the Store design's sentence is "Research the Fermion 1.8
in IPS display (DFR0928) from my drawer" · E `commands/drawer.md:93-94`; `canvas:Store.dc.html:177` · H that the
person naming a part from his own drawer is his words, not the drawer, is this lens's reading · supports only: a
question for the decider, not a defect.

### What he can supply, and what not

| input | can he supply it | evidence |
| --- | --- | --- |
| photos of both sides | yes, three in the e-paper walk | E `<walks>/p934-epaper/diary.md:8-10` |
| a ruler or a scale in the photo | not at hand once ("no ruler at hand") | E `<walks>/p934-epaper/diary.md:78` |
| a part number or SKU | yes for 90 of 95 unlinked entries (DFRobot) | E USER-12 |
| words of a need, with conditions | yes ("e-paper", "keeps the picture with the power off") | E `<walks>/p934-epaper/diary.md:175-178` |
| what he sees at the bench | yes ("3 bars and 1 red block", "the led is always on", "it is mirrored") | E `<walks>/p934-display2/diary.md:268-270`; `<walks>/walk4/walk4-diary.md:39` |
| a measured current or voltage | — no meter seen in any diary; "meter trials wait for a meter" | E `<walks>/p934-display2/diary.md:310-311` |
| a JSON file with a `write` key and a source | no sign he ever wrote one; Claude wrote each | H the diaries show only session-written `--fact-set` |
| a price limit | he can, spark keeps none | E `commands/research.md:86-88` |

### Journey (a): a fact is wrong or not checked

Moment: at the parts pick (he compares candidates; `--offer`), at the build (a before-power line says it), at the
bench (a trial shows the truth), or in store work (StorePart lists "8 facts not checked").

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | sees a doubtful fact on a sheet, a page or the bench | E `<walks>/p934-display2/diary.md:186`, `:280` | the sheet's before-power line named the wrong driver; nothing marks it as a guess | partly |
| 2 | asks "what do we know, from where?" | E `<walks>/p934-epaper/diary.md:96-98` | no command groups a record's facts by source; the StorePart design does (not built) | not yet |
| 3 | asks Claude to check it online | E `commands/research.md:23-25` | a match ends research; no "check this one fact" step | not yet |
| 4 | finds that only the bench settles it | E `<walks>/p934-display2/diary.md:157-165` | no step offers the trial; the session wrote it by hand | not yet (P1003) |
| 5 | runs the trial and says what he sees | E `<walks>/p934-display2/diary.md:268-271` | works when Claude writes the firmware | partly |
| 6 | asks Claude to keep the finding | E `<walks>/p934-display2/diary.md:277-287` | Claude writes `--fact-set` after his yes; one field had no key | partly |
| 7 | the next project uses it | E `<walks>/p934-display2/diary.md:190-201` | a stale shelf copy cost the drawn breadboard (fixed, P1006) | works since P1006 |

```
 StorePart · DFR0664 · 9 facts not checked
 +-----------------------------------------------------------+
 | Peak current        ?  not published                      |
 |   who can settle it:  [ I measured it: ___ mA  (meter) ]  |
 |                       [ Offer a bench trial ]             |
 | Pin order           ?  wiki and schematic disagree        |
 |   who can settle it:  [ I read the silkscreen: ____ ]     |
 |                       [ Add a photo of that face ]        |
 | Driver chip         v  ST7789  (wiki + datasheet)         |
 |                       [ This is wrong: ____ ]             |
 +-----------------------------------------------------------+
 | Lands in: your shelf copy -> every project reads it       |
 | [ Ask Claude: check the 2 a datasheet can settle ]  ~cost |
 +-----------------------------------------------------------+
```

### Journey (b): an owned part has no record (by name or part number)

Moment: at the parts pick, when an owned entry is offered "owned, no record" (walk 4: "research it and lets update our
records"), or in store work on the Store screen.

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | sees "spark does not know it yet" on an entry | E `canvas:Store.dc.html:20` (95 not known), `<store>/drawer` count | 95 of 114 entries; nothing says which a project needs | partly (design only) |
| 2 | asks to research it, in a project | E `<walks>/walk4/walk4-diary.md:24-25` | needs a project; the record goes into its `parts/` | works in a project |
| 3 | answers network and cost questions in Claude Code | E `commands/research.md:56-58` | each fetch asks; no cost number | partly |
| 4 | waits 3 to 6 minutes | E USER-15 | the page shows nothing meanwhile | partly |
| 5 | reads the result: 9 facts unchecked | E `<walks>/walk4/walk4-diary.md:26` | goes to job (a) | works |
| 6 | the entry is linked, the record goes to the shelf | E `commands/drawer.md:48-49` | from the store page, no project: where it lands is — | not yet |

```
 Store · Fermion 1.8 in IPS (DFR0928) · o no record
 +-----------------------------------------------------------+
 | spark does not know it yet.                               |
 | [ Look it up by DFR0928 ]  DFRobot wiki, ~2-6 min, cost ~ |
 |   writes: a record on your shelf, every fact "not checked"|
 |   asks you: geometry questions it cannot read             |
 | Running ...  3 of 5 documents kept      [ see in chat ]   |
 +-----------------------------------------------------------+
```

### Journey (c): a module with no marking he knows, from photos

Moment: before any project (store work, "add a new module to the store"), or at the parts pick when the need's part is
in his hand but not in the store (P992's moment).

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | takes photos (phone) and gets them to the Mac | E `<walks>/p934-epaper/diary.md:8-10` | how they reach the Mac is —; the page cannot take them (USER-10) | partly |
| 2 | gives them to /spark:identify in Claude Code | E `commands/identify.md:22-29` | no ruler in frame; the skill does not ask for one more photo | partly |
| 3 | reads Claude's reading (Read / Not read) | E `<walks>/p934-epaper/diary.md:16-40` | works; the agent corrected 3 readings | works |
| 4 | waits for the agent (6 min 18 s) | E `<walks>/p934-epaper/diary.md:57` | files kept in his store with no question | partly |
| 5 | the record fails `--validate`; the checklist is refused | E `<walks>/p934-epaper/diary.md:66-69` | blocked until a size is guessed | fixed by hand |
| 6 | says yes to the drawer entry and the kept photo | E `<walks>/p934-epaper/diary.md:105-111` | linking before the research for use froze the shelf copy | partly |
| 7 | a fact the photos cannot show stays a guess (the controller) | E USER-1 | settled only on the bench, two days later | not yet |

```
 Add parts · From photos
 +-----------------------------------------------------------+
 | 1 Front   [ drop photo ]   needed: labels, chips          |
 | 2 Back    [ drop photo ]   needed: header order           |
 | 3 Ruler   [ drop photo ]   without it: size is a guess    |
 |-----------------------------------------------------------|
 | Read so far:  MH-ET LIVE · 8 pins VCC..Busy · HINK-E029A10|
 | Not read:     size · controller (on the glass: bench)     |
 | [ Identify ]  ~6 min · keeps files in your store: ask me  |
 +-----------------------------------------------------------+
```

### Journey (d): a need has no part; find candidates online by criteria

Moment: at goal and needs or the parts pick, when no owned part fits; or after the build or the bench, when a picked
part cannot do the must line (the e-paper and the cursor).

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | says the need with conditions | E `commands/idea.md:40` | conditions only order store candidates | partly |
| 2 | sees no fitting part, or a part that cannot do it | E `<walks>/p934-epaper/diary.md:182-185`, `:201-205` | he found the conflict himself | not yet |
| 3 | asks for alternatives online | E `<walks>/p934-epaper/diary.md:253-256` | no command; part-finder is for commodity parts, max 2, never ran in a walk | not yet |
| 4 | sets criteria (sleep current, outdoors, breadboard, price) | E USER-8 | two map to record facts, two to none | not yet |
| 5 | compares candidates | E `agents/parts-researcher.md:36-37` | stops at the first fitting vendor | not yet |
| 6 | picks one to order, research keeps it as a catalog record | E `commands/research.md:151-158` | buying is outside spark | partly |

```
 Parts · Need 2: A screen · no part of yours fits
 +-----------------------------------------------------------+
 | Your drawer: Fermion 2.0 IPS (held) · MH-ET e-paper (27 s |
 |   full refresh: cannot move a cursor)                      |
 | [ I have one that is not here ]  [ Find one online ]      |
 |-----------------------------------------------------------|
 | Find one online · your criteria                            |
 |  shows text            [x]  (any display)                 |
 |  asleep under  [20] mA [x]  spark checks: "current asleep" |
 |  fits a breadboard     [x]  spark checks: header          |
 |  readable outdoors     [x]  your call: no fact for it     |
 |  vendors  DFRobot > Seeed > any          ~cost, ~min       |
 | [ Search ]  -> up to N candidates, each with what it lacks |
 +-----------------------------------------------------------+
```

### Friction moments as candidate questions about his own past use

- After the e-paper walk, did you look for the record's facts anywhere other than the chat (the JSON, the page)? (USER-2, USER-4)
- When a fact was wrong, did you ever want to type the right value yourself, or always tell Claude? (USER-4)
- How did the three e-paper photos get from your phone to the Mac, and how long did that take? (USER-10, journey c step 1)
- Have you ever had a meter on the bench during a spark walk? (the table of inputs)
- Of the 95 drawer entries with no record, how many would you want researched before a project needs one? (USER-12)
- Are there modules in the drawer with no marking you know, and roughly how many? (USER-13)
- When you asked for alternatives to the e-paper, would you have ordered one, and which criteria did you have in mind? (USER-9)
- Did you watch the research agent run, or do something else while it ran? (USER-15)

## What you could not check, and why

- Whether an Artifact page can take a photo upload or a free-text field and hand it to Claude: the brief allows no
  web and no Artifact calls, and this lens changes nothing; the claude-artifacts instructions only mention uploads.
- The token cost of the research runs seen (3 to 6 minutes): no diary records tokens.
- Whether the PO ever opened a record's JSON himself: no diary row shows it, and he was not asked.
- How the photos reached the Mac in the e-paper walk: the diary says "The PO sent three photos", no more.
- The rendered look of the canvas artboards: read as source text, not seen in a browser.
- Whether a meter exists at his bench: no diary names one.
- Whether job (c) or job (b) is the more frequent for him: the store shows only what was done (4 photo entries), not
  what waits.

## Questions for the decider

| question | what it decides |
| --- | --- |
| Is job (a) on the page "tell spark what you saw or measured" first, or "research it again" first? | the main control of the edit page (USER-1, USER-2, USER-3) |
| Does a person edit a fact's value on the page directly, with a source he types, or only through Claude? | whether an edit is a page request with a value, which the request rows cannot carry today (USER-4, USER-10) |
| Where does a record researched from the store page live, with no project? | the store's research button and the shelf (USER-11) |
| Does the Parts screen offer "I have one that is not here" and "Find one online" per need, and may Send go with a need left open? | the P992 moment on the Parts design (USER-6) |
| Is the criteria search (d) a new Operation that compares several vendors, or the existing researcher asked to compare? | whether (d) is a page over an agent or new behaviour (USER-7) |
| Which criteria may a person set: only those that map to record facts, or also free words that stay his call? | the criteria form (USER-8) |
| Do photos travel to spark from the page, or does the page only say "send them in Claude Code"? | the photo screen, and whether a page upload is in scope (USER-10, USER-14) |
| May a store-page research button send a drawer entry's name to a research agent? | the drawer rule against the Store design (USER-18) |
| Does the page show a research run while it runs, with its cost before it starts? | the running and cost states (USER-15) |

## Searches

None.
