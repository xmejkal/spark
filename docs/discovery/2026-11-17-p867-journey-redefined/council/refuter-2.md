# The refuter's report on P867 (the whole journey redefined), second pass

Read and run on 2026-11-17 (Europe/Prague) by the refuter (Fable 5.2), on the changed sections only. Nothing but this
file was written. No build, pick, look, deploy, live.py, reach.py or simulation ran, and no `assign_pins.py` run was
made in this pass, so ★C4's counts are not reproduced a third time. "Read" means I opened the source. "Lens line"
means I read only the council report's line.

## 1. The new ★ claims, each against its source

| claim | the line I read, verbatim | verdict |
| --- | --- | --- |
| ★C29 | Rows counted in the three rows files: 16, 7 and 9. spark-walks/p711-sound-demo/rows.md row 13: "After the design changed, "traces differ: board.tsx" for the board.tsx that spark itself wrote for the earlier design, never edited. The person must delete it by hand."; row 12: "The way around: repeat the box's whole design (p581's requirements), so the assigner places the bus on the same pins."; #1234's comment: "`--requirements` kept the old parts as "kept, not from a pick". A person removes them by hand."; council/risks.md:21: "Each is a behaviour of a script, so redefining the journey on paper does not remove them; they need cards" | partly |
| ★C30 | spark-walks/p711-sound-demo/.spark/needs.json: `"what": "rotary encoder", "pick": [{"part": "cjmcu-111-rotary-encoder"}]`; requirements.json: `"parts": ["dfr0664-tft-2in", "max98357a-dfr0954", "joystick-module-mh", "speaker-terminal"]`; row 12 as above | holds |
| ★C31 | council/live.md:224-225: "Nothing must change now in a card in Ready. The evidence is LV-1 to LV-8: read from the plan, the cards and the code, not from a test."; :231: "To P829 #1187's Notes, one sentence"; spark-walks/p711-walk4-button-led/diary.md:42: "my read (DTR off) saw no line, because MicroPython's USB sends nothing to a host with DTR off." | partly, and one part refuted (below) |

★C29, the sentence to change and why. Change "what the walks saw of a change is hand work in commands: row 13 of
walk 3 ..., row 12 ... and #1234's comment" to "one row of 32 names a file deleted by hand (row 13, one person, one
project); row 12 is a blocker whose way around is a requirements file rewritten by hand; the session's comment on
#1234 adds a third case, which no row holds". Why: a search for "not from a pick" finds no file in the three walk
folders, so the comment's bullet has no row and no diary line behind it. The comment's heading is "What P711's walks
saw", and the first refuter (S-2) already said that the session wrote it. The claim now cites it as a walk's sight,
and items.md's third item cites it as its proof. The base of "hand work" is 2 rows of 32. A search of the rows for
"tick", "out of date" and "stale" matched only the word "joystick" (two rows), so the first half of the claim holds.
"none of the first six proposed items fixed those": the earlier items.md (commit 38f4a6f2) has 7 headings, six items
and the board actions; I did not read its six proofs.

★C30 holds. Narrower than written in one detail: the picks also hold the board and a catalog entry
(`{"entry": "dfrobot-fit0502"}`), and requirements.json also holds four named signals (TFT_RST, TFT_CS, SD_CS,
TFT_BL). I did not run `flow.py show` on the sound demo in this pass; the four need ids are read from needs.json.

★C31, part by part.

- (a) "asks for no change now in P827, P828 or P829": the lens's own judgement, tagged H by the lens, and weaker in
  the lens than in the brief. I read the three card bodies (not their 3, 2 and 2 comments) and mvp-plan.md:50-65,
  :86-104, :130-156. None names the port, the bench or a stream; mvp-plan.md:148 says "so no click reaches a look, a
  deploy, a grant, live code or a simulation". Three limits the brief dropped: (1) the lens proposes a sentence for a
  Ready card ("To P829 #1187's Notes, one sentence ... the third touches a card the PO ordered"), so "nothing in a
  Ready card must change" and "one sentence keeps the door open" (open question 10) understate the lens's three
  sentences; (2) LV-2: a live line "does contradict "`db` holds only requests and answers" if the stream goes through
  `db`"; (3) "none fixes a transport" is true only of a board stream: P829 fixes the page's one route, `db` rows
  read "at the PO's next message" (D8), and the lens found no documented way for a local process to write `db`
  (LV-17), `room` untested, `mcp host:` in the desktop app only. So "no change now" is "no text conflicts today";
  what a live page costs later is not known. Sentence to change: "asks for no change now" to "conflicts with no
  text of P827, P828 or P829 as read (H, the lens); the lens proposes one sentence for P829's Notes, and the page's
  only route today is a row read at the PO's next message".
- (b) "the port has one holder": in the code, narrower than worded. scripts/spark/bench/board_console.py:42
  `KIND_READ, KIND_BUSY, KIND_UNREAD = "read", "busy", "unread"`; :48 `s.port, s.baudrate, s.timeout, s.dtr, s.rts,
  s.exclusive = sys.argv[1], 115200, 0.1, False, False, True`; installed mpremote 1.29.0 transport_serial.py:52 `def __init__(self, device,
  baudrate=115200, wait=0, exclusive=True, timeout=None):`; installed esptool loader.py:456 `port, exclusive=True,
  do_not_open=True`. The lock is pyserial 3.5 serialposix.py:385 `fcntl.flock(self.fd, fcntl.LOCK_EX |
  fcntl.LOCK_NB)`, an advisory lock: it excludes programs that ask for it. A reader that does not ask (a browser's
  Web Serial, another terminal program) is not shown to be excluded. Sentence to change: "the port has one holder"
  to "mpremote, esptool and spark's console read each take the port's lock, so they exclude each other".
- (c) "every board read in spark today is bounded and is its own process": holds for the reads that live.py and
  reach.py make (board_console.py:20 `READ_S, POLL_S = 2, 0.1`, :101 `timeout=READ_S + 10`; board_connection.py:24
  `DEFAULT_TIMEOUT_S = 20`, :90 `timeout=timeout_s`; ready_probe.py:17 `READY_WAIT_S = 20`). I read live.py in full
  and reach.py's hits only; board_reach.py and reach_board.py were not opened. Not covered by the sentence: the flash
  runs with no time limit (deploy_service.py:125 and :137, `self.run(command, check=True)`), and the deploy prints an
  unbounded read for the person, `mpremote repl` (deploy_image.py:47, board_connection.py:85). Add "that spark runs
  itself".
- (d) the MCP page says it. "The protocol currently defines two standard transport mechanisms for client-server
  communication: 1. stdio ... 2. Streamable HTTP"; "This replaces the HTTP+SSE transport from protocol version
  2024-11-05". Dropped: "Server can optionally make use of Server-Sent Events (SSE) to stream multiple server
  messages", so SSE is still the stream inside Streamable HTTP and not only "the old name"; "Clients and servers MAY
  implement additional custom transport mechanisms"; and the revision read is 2025-06-18, not the newest (the lens
  names 2026-07-28, not read by anyone). "a standard MCP server pushes nothing into a Claude Code session" holds on
  code.claude.com/docs/en/channels: "Standard MCP server | Claude queries it during a task; nothing is pushed to the
  session". The same page: "A channel is an MCP server that pushes events into your running Claude Code session", a
  research preview. The brief's sentence drops the channel.
- (e) "a live event is never state": no conflict found in D1 to D24 of docs/discovery/2026-10-15-p235-live-on-board/
  brief.md, read as lines cut at about 400 characters, so this is "no conflict in the part read", not "holds". The
  grant (D12, "spark keeps a grant record in the store") and the look bound to a token (D13) are written down, which
  fits. Two gaps: the sentence says "its files and records", and the grant and the deploy record are per board, not
  per project (walk 2, row 6 is that case); and a live try can change the bench with no project record (live.py's
  help: "A pin that the code set and the firmware never sets can keep its value through that reset").
- Refuted in part: "console output needs no firmware change". The lens (LV-20) rests it on "the read with DTR and RTS
  off takes what the board prints". The walk's diary says the opposite for the walk's board: "my read (DTR off) saw
  no line, because MicroPython's USB sends nothing to a host with DTR off" (diary.md:42; council/user.md US-20 quotes
  it as "a read with DTR off sees nothing"). The observation is an account from the bench, one board; its cause is the
  diary's reading. The live lens did not cite it. Sentence to change: "console output needs no firmware change" to
  "console output needs no firmware change only if a read reaches it: the one bounded read spark has (DTR off) saw
  no line on the FireBeetle 2 in walk 2, and a read with DTR on may restart the board (P235 ★C6)".
- "a button, an LED or a pin cannot be read from outside while the firmware runs": the lens says "supports only: the
  mpremote route". The brief dropped that limit.

## 2. The changed sections against the detail they summarise

Asked for by the first refuter and not applied, or applied in part (h):

- H-1 · Q5 still reads "opinion (the facilitator's): 2, started with 1's first slice". OQ6 now says option 1 and
  "not chosen now" for 2. The question the PO is asked carries the opinion that the brief withdrew.
- H-2 · Q3 still reads "keep by default". OQ5 (b) now says a bus line can be kept only after P868 #1235 and "until
  then the person is asked". Q3's options have "ask per change", and the opinion does not point to it.
- H-3 · OQ1's new line says "Q6 asks which he meant". Q6 is unchanged: "Which of your phases is a step of its own
  and which is a view of another step". It does not ask whether his list was about what the page shows when (I-6).
- H-4 · D-3: OQ6 (2) still says "proves: "did the kept pins move" and "does the firmware name old pins" as facts read
  from files". Unchanged.
- H-5 · D-4: OQ6 (2) still says "three mechanisms folded into one check", while ★C3's new caveat says "one check
  over recorded inputs does not replace them". The brief now holds both.
- H-6 · ★C3: "seven edges" was not added. "two of them (the copy of what the sheet told, and the deploy record)":
  the deploy record is not one of the brief's four mechanisms (comparison, stored checksum, stored copy, file times),
  and ★C2 says the flow reads no deploy record. council/architecture.md:27-40 lists it as its own edge, "a stored
  hash, readable only with the board on USB". The first refuter's sentence was loose, and it was copied as it stood.
- H-7 · D-1: no guard against a rule that marks everything out of date. The outcome still says "names every phase
  that is out of date", and slice 0's second row says "every phase made from the changed thing reads out of date".
  Neither says "and no other phase", and no line is written down before the run. `/usr/bin/grep "before running"`
  finds 0 lines in risks-and-tests.md, items.md and story-map.md.
- H-8 · D-5 and D-6: "proves: a wired breadboard stays right after an added part" (OQ5 b) and "proves: "the board
  holds an older image than the project" is said without a look" (OQ9 b) are unchanged. The second is now beside a
  caveat that speaks against it.
- H-9 · D-7: no question asks which of the two meanings of "simulation" the PO's order names.
- H-10 · S-2: "#1234's comment" is still cited as E in ★C7 and is now a source of ★C29 and of two items.
- H-11 · ★C16's old keep words survive: risks-and-tests.md's viability row and A6 cite "★C16 (rework, not a stop)".
  verification.md's split still says "P829 exposed", the word ★C15 dropped. verification.md cites ★C12 at
  council/feasibility.md:28-32, the brief at :28-33.
- H-12 · risks-and-tests.md's feasibility row still says "the paper spike of the brief's Riskiest section", which no
  longer exists; its usability row still says "the PO reads slice 0's output on the sound demo", the folder that
  ★C30 rules out.
- H-13 · N-8: "five new phases" and "marks five phases out of date" are unchanged.
- H-14 · R-0c (1): "must not get worse" still lists the keys of the JSON and not the meaning of `stands_at`.

Dropped caveats and stronger claims in the changed text:

- S-1 · ★C4. The brief names four added parts, three of which move pins. The first refuter's table has seven parts
  on two projects with 0 moves in most rows (the LED, the motor driver, a second button, the joystick on the
  amplifier project). "7 runs" has no breakdown; the list gives six cases.
- S-2 · Open question 10: "every claim about it was H until the live lens read it". LV-21 is "H this lens". The
  wording reads as if the tag changed.
- S-3 · Q16: "P248 #270 (a bounded console read, which answers walk 2's row 7)". The lens: "answers row 7 if LV-12's
  cause allows". The card (#270, in Idea): "a read of N seconds on the XIAO C6 keeps a boot with its ROM line, says
  that opening the port can restart the board". It names another board and no read that leaves the firmware running.
  With diary.md:42, a DTR-off read on the walk's board saw nothing.
- S-4 · Q16's "which cause stops main.py": the lens lists three causes and did not read the deploy's own line,
  deploy_image.py:47: "then, to see it start: %%s, press Ctrl-C, then Ctrl-D: the firmware prints `ready`". Spark
  tells the person to press Ctrl-C. That is a fourth cause, in spark's text, and it needs no bench row to find.
- S-5 · Q4: the added sentence stands after "status: queued" and puts a second decision into one question.
- S-6 · OQ9's rule line: "cost: one sentence in the definition, no code". LV-3 names a cost: a bench reader with "no
  field for the source". items.md's later line carries it; the option's cost cell does not.
- S-7 · D3 says "if it does, the cards are edited, added and reordered". The lens proposes one reorder (LV-24) and
  two new rows (LV-23). Open question 10 reports only "nothing ... must change"; LV-23's rows are in no item.
- S-8 · The Frame says "the seven lenses ran" and names a model per lens. council/live.md is an eighth report, and
  neither it nor D3 names the model that wrote it.
- S-9 · story-map.md slice 0, row 1: tag "E ★C29". Half of the story ("the requirements drop what no pick explains")
  rests on the comment with no row. Its proof says "with no hand action", and the story says "on a yes".
- S-10 · story-map.md slice 1, row 1 and items.md: "the signals on no bus keep their pins". The first refuter's run
  showed what that costs (new signals on the SDA pad and on the board's own button). The proof does not ask where
  the new signals land.

## 3. The strongest rival explanation for each interpretation

- I-1 · A11's test and its pass line (f). The one who counts can set the result in five ways. (1) "A hand action" has
  no definition: a second run of a command, a read of two pin maps and a yes can each count or not. (2) The two
  classes are not defined before the run, and the brief's own example sits in both: row 13 "needs one [checksum], of
  board.tsx", which is a record written in one build and read in a later one. (3) The projects are chosen toward a
  low count: the button-and-LED project has no build to redo (its line reads "parts: skipped, schematic: skipped,
  footprint: skipped, build: skipped") and no breadboard.md, and the amplifier project has no firmware/main.py
  (`flow.py show`: "○ firmware: not started, no firmware/main.py yet"). So neither project meets the test's own
  condition, "after the build and the firmware exist". (4) "With no board" removes the actions at the bench: the
  rewiring of a moved pin, the order of flash and wire, the board that holds the old image. Those are the ones that
  span phases (★C5, ★C6, ★C9). (5) The counter knows three candidates before the run (moved pins not named, firmware
  names not checked, the mark that stops at the requirements), so 3 can be met without a new finding. The line can
  be passed or missed at will. Rival to the whole test: the PO asked for the definition (D-a is his decision), so a
  count of hand actions cannot say whether it "earns a slice"; it can only order the first cards.
- I-2 · OQ6, the line as a table of phases (g). The table has three columns: states, made from, makes out of date.
  The PO's words ask for more: "what the steps are for each of the states", "when we can go back", "how", and each
  interface (D-a). The table has no column for the way back, none for the steps inside a state, and none per
  interface. The fail branch of A11 ends in "a table and a page of documentation", while the outcome line still
  promises "the phases, their states, the ways back and the rule for a change in the middle". Rival: the first
  refuter's point was about which slice comes first, and the brief answered by shrinking the definition itself.
  ★C11 (several vocabularies) and ★C13 (two shapes for the next step) are reasons for a definition that no hand
  count touches.
- I-3 · ★C31, "nothing must change". Rival: the page's design (a row read at the PO's next message, no route from a
  local process to the page) is the thing a live view cannot use, so the cost is deferred, not absent. The lens
  could not check the sandbox, `room` or a `db` rate.
- I-4 · OQ9's rule ("a live event is never state"). Rival: the rule is free only because nothing live exists. It
  also makes the deploy's own "ready seen" a live event that becomes state when the deploy writes it, which nobody
  checked in the deploy record.
- I-5 · OQ8 (a), "weaker than first written". Rival unchanged from I-7: P827's Done-when says "shows the nine
  phases", and nobody read a plan. Q8's opinion is still a plain "yes".
- I-6 · ★C29 read as "the pain is in commands". Rival: the rows record what broke while Claude typed (★C18), so
  they under-count what a person would not know to do next; no walk made a change on a wired and flashed project.
- I-7 · Row 7 (Q16). Rival to "a bounded read answers it": the person pressed Ctrl-C because spark's line said so,
  and a DTR-off read sees nothing on this board; the fix may be the deploy's sentence, not P248.

## 4. Numbers that lack their unit, population, period or provenance

- N-1 · "at least 3 of the counted hand actions": no denominator, no definition of the unit, no reason for 3, and
  two projects that do not meet the test's condition (I-1).
- N-2 · "12 H" (Stands on): twelve assumptions; A4, A10 and A11 carry E in risks-and-tests.md.
- N-3 · "7 runs by the facilitator": six cases are listed (S-1).
- N-4 · "6 of 15", "3 of 4", "4 of 4", "0 on both": simulated, one board model, two projects; not reproduced in this
  pass.
- N-5 · "none of the 32 rows": 16 + 7 + 9, counted; 2026-11-16 to 2026-11-17, one person. "Hand work" is 2 of them.
- N-6 · "walk 2" and "walk 3": the folders are p711-walk4-button-led and p711-sound-demo. The brief gives no key from
  walk number to folder, and one folder name says "walk4".
- N-7 · "four pages fetched", "two of the four pages came back as summaries": which two is in live.md only.
- N-8 · A1's "at least 5 of the 7 things", "kept only as a side result": a pass line for a test that no longer runs.
- N-9 · "the first six proposed items": a count of a file version that the reader cannot see (commit 38f4a6f2).
- N-10 · ★C31's "bounded": 2 s for the console read and 20 s for an exec are in the lens, not in the brief.
- N-11 · LV-13's "200 ms": P235's reading for the C6, not re-read, "not known for the FireBeetle 2" (the lens says
  so; it is not in the brief, and it bears on Q16).

## What I could not check, and why

- The comments of #1185, #1186 and #1187, and the full text of P235's decisions (lines were cut): time.
- council/live.md's LV-15 on code.claude.com/docs/en/mcp, LV-17 (the Artifact runtime's text) and LV-18 (MDN): not
  opened. None of them is "holds" here.
- board_reach.py, reach_board.py, run_live_code.py and board_live.py beyond search hits; whether the deploy record
  stores "ready seen".
- ★C4's counts: no assigner run in this pass.
- The session's messages behind D2 and D3: only #1237's text was read ("Btw one more think to note down and consider
  for our architecture and system design"), which matches D2's quote as far as it goes.
- Anything on a board, by the rules.

## Searches

- none

Fetched: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports and https://code.claude.com/docs/en/channels (both for ★C31). Commands: `gh issue view` for 1185, 1186, 1187, 1234 (with comments), 1237 and 270; `flow.py show` on the amplifier and the button-and-LED walk folders; `git diff 38f4a6f2 HEAD` and `git show 38f4a6f2:` on the folder; `/usr/bin/grep` and `sed` in scripts/spark/bench/, scripts/live.py, scripts/reach.py, the two older discovery folders and the three walk folders; a search of the installed mpremote, esptool and pyserial packages for the port's lock.
