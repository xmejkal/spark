# P1161 council: the refuter

Read on 2026-11-25 from about 20:45 to 21:15 CET by the machine clock (`date` read 21:02:04 CET and 21:03:34 CET
during this run), on branch p1161-research-pages at cceba566. Read only: the repository, `gh`, `<store>/` (no write),
`canvas:` copies, `<walks>/`. Experiments ran in a scratch folder outside the tree: `parts.py --unverified`, python
counts over `<store>/drawer`, `<store>/shelf`, `<store>/catalog` and `<store>/history.jsonl`, and `git show` of older
commits. Nothing in the tree was changed but this file. During the run an untracked `council/delegated-answers.md`
appeared; I did not read it.

## Check first: existing product, and the PO's own idea

- What breaks for current users is not covered. "Must not get worse" (brief.md:21) names `/spark:research`,
  `/spark:identify`, "the store pages as designed" (not built) and the records' contract. It leaves out the built
  project page: `flow.py`, `/spark:page`, `run-request` and P1122's test. Slices 0 and 4 change exactly these.
- Q7 A (the build stamps each record it read) says nothing about the build records that exist now. A `.spark/build.json`
  written before the change has no such stamp. Either every existing build turns "out of date" on upgrade, or the
  check stays silent for old builds. A4 tests only "false marks across the walk" (risks-and-tests.md:35).
- Items close P1002 #1461 "as absorbed by the slice 1 story" (items.md:108). P1002 is the PO's ask that spark
  "always" offers a new finding at the bench or in a session (`<walks>/p934-display2/diary.md:288`). Slice 1 is a page
  offer over a picked part's unchecked facts (items.md:26). Its trigger is the page, his was the finding. Two of the
  three findings he kept on 2026-11-22 (`deep_sleep_wake`, the BUSY level, PO-2) were not unchecked facts first.
  Closing P1002 drops his "always offering".
- Confirmation bias. A1 is named riskiest (brief.md:95), and the collection plan says it can be tested "before any build
  with the canvas's sentences" (risks-and-tests.md:47). Yet items.md files slice 0 and has no item for the A1 test.
  The epic's outcome (brief.md:17) is the card's Done-when, which the coordinator wrote, not the PO. Its pass line, "3 of
  the first 5 moments", has no stated reason. The walk's observer is the same agent that writes the sentences, and the PO
  reads this brief before the walk.
- The team stands in for both roles. No user beyond the PO is reachable. The PO's choices, including Q1's importance
  ratings of assumptions about his own behaviour, go to a council of three agents. That council also judges which
  choice is "really important" enough to go to him (delegated-brief.md:5). The brief names no rule for that judgement.

## 1. The starred claims, each against its source

- ★C1 · holds. run_request.py:3-4: "The values of the step come from spark's own offer key, never from the request."
  tests/test_run_request.py:274: `self.assertEqual(PageRequest._fields, ("id", "key", "seen"))`.
- ★C2 · holds. research_part.py:145: `effects = (READS, WRITES, ASKS, FETCHES)`.
  `<store>/councils/p1113/architect-page-actions.md`:63-64: "Never from a page: … an Operation that declares `board`,
  `deletes`, `asks` or `fetches` (`operation.py:31`). No test pins this today (P1082)." The PO's acceptance: #1652
  "And yes, I want the architect stuff". The rule is in the architect's §3, not in the PO's decisions table (lines
  98-110). The brief's word "accepted" rests on his general yes.
- ★C3 · holds. set_facts.py:47: `set(facts) <= set(CHAIN_FACTS + drawer.DESCRIBING + drawer.PROVENANCE_KEYS +
  drawer.SHEET_KEYS)`. I listed those keys: footprint, pin_order, pin_order_proof, body_mm, simulation; about,
  description, tags; facts, body_mm, pin_order_proof, pin_roles, physical, physical_proof, own_socket, joined_pads;
  legs, host_requirements, short_name. There is no name, vendor, sku, needs or power. set_facts.py:56: "a write fills a
  fact, it never empties one".
- ★C4 · holds, with a stale caveat. fingerprint.py:18: `FILES = (needs.FILE, Path(REQUIREMENTS_FILE),
  BUILD_RECORD_FILE)`. build_record.py:32: `OWN_FILES = ("board.tsx",)`. phase_readers.py:447 compares only
  `requirements_sha256`. The caveat "P1160 #1696, a spike in Build" is wrong: `gh issue view 1696` gives CLOSED
  2026-11-25T19:43:22Z (20:43 CET). Its finding on origin/main (e882d7b5, finding.md:78) already states this claim as
  "link 12": "part records, boards, `.spark/rules.json` → build | none". Change the caveat to: "P1160 #1696 (Done
  2026-11-25) maps this as link 12 and change 6, on main, not on this branch."
- ★C5 · holds. physics_check.py:193: `elif load["unverified"] or not supply["verified"]:`, so a verified supply gives no
  needs-measurement finding. part_rules.py:138: `on_module = (facts.get("module_has_i2c_pullups") or
  {}).get("value") is True`. It reads only the value, so `verified` does not matter there. provenance.py checks that
  `source` is non-empty words (provenance.py:39-40), never who or when. The rival reading is in part 3.
- ★C6 · partly. git brief:125: "D8 · … the records the person decided (the brief, the needs, the picks, the requirements,
  the board), one step per decision". store.py:146-147: `PRIVATE = ("drawer", … "shelf", …)`. The PO assistant reads
  it the other way, at po-assistant.md:198: "A part-record edit in a project is a decided record (D8)". The lenses
  split on whether D8's list is complete, and the brief shows no split. "Today" is empty, because nothing is a kept
  step today (P1152 is in Idea). Change it to: "D8's list does not name part records, and the lenses read it two ways
  (PO-28 against TL-23 and ARCH-12). The shelf, the catalog and the drawer sit in the store, outside every project's
  git."
- ★C7 · holds. I reproduced it read only: 114 files; `is` in 19; 95 without, 93 of them with `part_number`; `from.seller`
  lower-cased "dfrobot" in 99; `photos` in 4. Its population is the seller field. 12 entries have no `from`.
- ★C8 · partly. `<walks>/p934-display2/diary.md`:161-164: "Only a test on the module settles it, so the bench trial is
  the way. This is the case of P998 #1457 (a fact research cannot settle) and P997 #1454 (research by the panel marking
  HINK-E029A10-A3)." The research by marking that the diary itself names was never run. "Research did not settle it"
  holds only for the earlier research, which left three candidates (PO-6). Change it to: "the earlier research left
  three candidates; a bench trial settled it; research by the panel marking (P997) was not tried".
- ★C9 · partly. research-cost.md:9: "the full research protocol P80 replaced: a median of 78 tool calls, about 5.0 M
  tokens processed and about 25 minutes". "Tokens processed" counts cache reads (research-cost.md:4-6 says cost.py's
  new-token count "differ[s]"). In the source, "median" may attach only to the tool calls. "No G" proves nothing: no
  command writes a G step. Only `commands/idea.md:17` calls `--step`, and its sections are S, M, C, L and T. The STEPS
  tuple is at run_cost.py:45. Change it to: "about 5.0 M tokens processed (cache reads included) …; no command writes a
  research (G) step, so the history cannot show one".
- ★C10 · holds. canvas:Parts.dc.html:196: `sendLabel: ready ? 'Send 4 picks to spark' : 'Pick ' + (4 - picked) + '
  more first'`. Its defs (lines 153-160) have no "not here" option. `<walks>/p934-display/diary.md`:88: "And also what
  if it's not in the store ?" It drops his "But mostly the already created board from the last project shouls also be
  in the common store" (:90); see part 3.
- ★C11 · partly. parts-researcher.md:36-37: "Stop at the first vendor with a part that fits the need unless you were
  asked to compare." The brief drops "unless you were asked to compare", which USER-7 keeps, and its caveat says
  "none". README.md:122: "The part-finder and datasheet-reader did not" holds. Add: "unless asked to compare".
- ★C12 · partly. I fetched the DigiKey page: "Search for product information based on part number, description,
  manufacturer or category." It does not say that an account is needed. It shows only "Register / Login" links.
  Nexar: "Up to 100 matched parts", "Sign up, it's free". TME: "Register now", "get access". The PO assistant could not
  check Mouser (timed out), LCSC's website and the Czech shops (po-assistant.md:236-241). The brief keeps only "one
  module query". Change it to: "no outside service checked (DigiKey, Nexar and TME landing pages; jlcpcb once; Mouser
  not reached) shows free, keyless, local parametric search for modules".
- ★C13 · holds. write_skeleton.py:2: "a record to fill in, written to the project's parts/". run_request.py:153-157
  reads the project's request and fingerprint.
- ★C14 · partly, and stronger than its source. record_home.py:181: "Set fields of a part record in its own home (§5.4)
  — the catalog's, a project's, or a listed project's behind a shelf copy". So `fact-set` does write into a catalog
  record. ARCH-11 says so (architecture.md:93-94), against ARCH-9 in the same lens. The synthesis's own line is
  narrower: "No code creates a catalog record" (synthesis.md:560). Change it to: "No Operation creates a catalog record;
  `fact-set` edits an existing one in place."
- ★C15 · partly. The cited range holds `<walks>/p934-display2/diary.md`:281-283: "`--fact-set` has no key for
  host_requirements, so it stays wrong until a card fixes the route". He was blocked then; it has since been fixed
  (PO-9). A board's physical facts still have no command: "no command writes a board's physical fact"
  (`<walks>/p934-epaper/diary.md`, PO-10). "Nobody is blocked" is too broad. Change it to: "No part-record edit or
  research is blocked today; a board's physical facts are edited by hand outside any Operation".
- ★C16 · partly. I reran `parts.py --unverified dfr0664-tft-2in`: "9 thing(s) nobody has checked". USER-3 (user.md:27-33)
  assigns pin order, the pulls, peak current, GDI pins, the series resistors and the cable order. It assigns no one to
  input_high_v, input_low_v or gdi_used_signals. The record's note says input_high_v "is assumed", not that no source
  exists. "0 of 9" counts 3 facts that nobody sorted.
- ★C17 · refuted in one clause. docs/discovery/2026-10-16-p269-views-and-editors/brief.md:108: "number 7 is the most
  importatnt … So J7 is the most important". jobs-and-journeys.md:16 there: "J7, the most important (D9): When I look at
  one circuit, I want the same circuit as a schematic, a breadboard, a perfboard and a PCB". The catalogue editor is J4
  and step 7 (D8), not J7. PO-20 confused "step 7" with "job 7". Change it to: "P276 #312 (the catalogue editor, step 7
  of P269, J4)". Also, #1700 is about photos of a wired breadboard. It shares the photo path, not the research engine.

## 2. The brief against its detail

- What we found:
  - ★C4's caveat is stale (part 1). The synthesis's F7 found this and the brief kept it.
  - ★C14 is broader than synthesis.md:560 and contradicts ARCH-11.
  - ★C11 and ★C12 drop the qualifiers "unless asked to compare" and "Mouser, LCSC site, Czech shops not checked"
    (PO-5, What I could not check).
  - ★C15 drops USER-4's "it was fixed by hand that evening" and PO-10's board facts.
  - ★C6 hides PO-28's opposite reading.
  - ★C9 drops "tokens processed".
- Options:
  - Q7 A's caveat cites "the P1160 finding rated it 'Can wait'". The synthesis points to commit e20c05d9
    (synthesis.md:128, :577). At e20c05d9 the finding has no link 12, and its "Can wait" items 5 and 6 are about firmware
    files. The cited text is at e882d7b5 (finding.md:78, :146-147), with the tech lead's remark "Changes 5 to 7 can
    pause". The pointer is wrong; the claim holds at another commit.
  - Q5 A's caveat treats "a record whose home is another project" as a choice to be made. ARCH-11 and
    record_home.py:46-48 show that `fact-set` already writes another project's record behind a shelf copy today. Q5 B's
    risk ("project A's page changes project B's file") is therefore not new to B.
- Riskiest assumption: the brief keeps synthesis A1. It drops PO-16's own point that "the page can add value through
  what it shows". It keeps that point only as the failure branch.
- Found on the way: the synthesis says three misfits "need the PO": M1 (agents write whole records with the Write tool),
  M2 and M3 (shelf and catalog outside the Storage seam) (synthesis.md:294-296). The brief has no question and no
  Found-on-the-way line for M1 or M3. Items push M1 to "P735's first step" and drop M3.
- Frame: "Seven agents" and the P900 cost comment (brief.md:35) carry no pointer.
- Readiness: verification.md is still the template (its fill marks), although commit c4dcc073 is titled "the findings, each
  claim reproduced".
- Items: the slice 0 card's "value proven by … `run_cost.py` counts the run" (items.md:9), A6 and the collection plan
  (risks-and-tests.md:48) all assume that `run_cost.py` can isolate a research run. It cannot: no command writes a G
  step (★C9 above). The research would fold into whichever step's window it fell in.

## 3. Rival explanations not ruled out

- ★C15 and A1: he asked for pages because he spent that session designing pages, and he wants to see a record's state
  more than to start jobs there. His own words route the job through Claude: "or I want claude to search the net".
  Nothing in the folder separates "a place to see" from "a place to start".
- ★C10 and P992: his main point at that moment was "mostly" that a board a project made did not reach the shelf
  (diary :90). The way out of the Parts screen was his second point. Slice 0 rests on the second.
- ★C8: the research was shallow (a community README) and not that research cannot settle it. The marking search (P997)
  was not tried.
- ★C5: the risk exists today in the chat and is the same under Q2 A. Under the recommended option the epic adds no new
  path to `verified: true`, so this is not a risk this epic creates.
- ★C16 and A5: "0 of 9 for the web" may come from how the lens sorted the facts. A photo of the unnamed buffer chip,
  then its datasheet, could settle two of them.
- ★C12: the finding is "absent" only because of the 6-search budget and the landing pages; the services were not shown
  to lack it.
- ★C9 "no G": the absence comes from logging, not from research never running.
- ★C7 "99 of 114 DFRobot": this reflects one order import. It does not describe his parts in general.
- The A1 test: he copies the page's sentence because it is the only path drawn, or he types because the sentence is
  wrong. The pass line cannot tell these apart.

## 4. Numbers without unit, population, period or provenance

- ★C9 "about 5.0 M tokens": the unit is tokens processed, cache reads included. Over how many runs the "median" is taken
  is not stated.
- The P900 cost "6 agents, 499 calls and about 90M input tokens" (brief.md:35): no pointer, and "input tokens" is
  undefined.
- A2 and USER-15 "3 to 6 minutes per research": n = 3 runs, two of them one part's two rounds. The risk table says "per
  research".
- PO-8 and A5 "107 of 194", "45 of 235": I reproduced them. The unit is any JSON object holding both `value` and
  `verified` at any depth, not a record's `facts` entries. That unit is not stated in A5.
- A5's pass line "60 % or more": its population is the 107 facts, sorted by a lens's judgement. Who sorts is
  unspecified.
- A1's "3 of the first 5": no reason given, and n = 1 person.
- Options' cost cells "small", "medium", "large", "a cheaper walk", "one session": no unit.
- ★C7's "come from DFRobot" means the `from.seller` field, and 12 entries have none.
- "10 H" in Stands on: it counts A1 to A10, which the reader must infer.

## Clock times (synthesis F8)

Times that cannot be right by the clock:
- brief.md:15 and #1697: "about 20:45 CET". #1697 was created 2026-11-25T19:29:13Z, which is 20:29:13 CET. The frame
  commit 7b6add11 (20:39:18 CET) already quotes it.
- #1700: "about 21:25 CET" and "about 21:30 CET". It was created 19:42:50Z (20:42:50 CET) and last updated 20:43:12 CET.
- po-assistant.md:3 "about 21:00 to 21:40 CET", :47 "about 21:30 CET" and :77 "about 21:20 CET". The file entered in
  afc9b458 at 20:47:26 CET with these lines.
- Outside the folder, cited by Q7: the P1160 finding says "Delegated by the PO, 2026-11-25 about 20:55 CET" in commit
  e882d7b5, made at 20:36:03 CET.

Consistent with the clock: synthesis.md:3 "about 20:55" (commit 21:01:24), ★C7 "before 20:57", and F7's "20:43 CET".
user.md:5 "20:20 to 20:45" fits its commit, but it starts 9 minutes before #1697 existed. That is implausible, though
the clock does not exclude it. Each impossible time is consistent with one hour ahead. "One hour" is consistent, not
proven.

## Searches

None. Pages fetched: https://developer.digikey.com/products/product-information-v4, https://nexar.com/compare-plans,
https://developers.tme.eu/ (2026-11-25), to re-read ★C12.
Not checked: the two jlcpcb MCP calls (no tool here); the architecture, tech-lead and UX reports beyond the ids cited;
story-map.md and jobs-and-journeys.md line by line.
