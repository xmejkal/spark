# The PO assistant lens (P1352 #1939, the perfboard step)

Opus, 2026-11-28. Read-only on the tree and the store. This file is the only one written. Questions: what the PO
wants from the perfboard step in his own words, what it costs against the MVP bar, which of his words are decisions,
which are open, the smallest result he would call done, and any evidence that he has soldered a perfboard or plans to.

## Findings

PA-1 · His words on the perfboard, in date order. Two wants repeat six weeks apart: one shared code base with the
breadboard, and a plan that spark makes. Soldering itself has no date. · E · supports only: what he said he wants, not
how soon he will use it.
- 2026-10-16, the P269 request: "probably we will want to reuse code for the perfboard stagte, so please also create
  some common base, think about what the differences are, how making routes works there, etc, what other data we
  would nreed to store for parts/modules/boars to also enable the perfboard visualisation and editing" (E
  docs/discovery/2026-10-16-p269-views-and-editors/brief.md:15).
- 2026-10-16, P269 D3: he will solder a perfboard or stripboard, "Yes, but later". D7: "OK, rework later", the base is
  checked against the perfboard "on paper only". D15: stripboard dropped (E the same file, lines 102, 106, 114).
- 2026-11-20: the same part pictures as the breadboard, "only without pins and with th esoldered vias", and "we don't
  need toa dd this step right now" (E #311, first comment).
- 2026-11-23, P1039 D11, an account (n = 1): after the clock and the bin ran on the breadboard, they needed "A
  permanent build", then "including the perfboard optional step, not just pcb" (E
  docs/discovery/2026-11-23-p1039-rd-direction/brief.md:115).
- 2026-11-26: the three notes on #311 (Spark plans, Claude changes. The drawer's sizes, cut smaller never bigger. The
  joins are soldered, "I am not sure what the best practices are actually"). On #1747: "options to go for the
  smallest size or to take up the whole perfobard and use the space" and "being also able for humans to edit the
  connections and move the parts around" (E #311 second comment, #1747 body).
- 2026-11-28: the request ("it should actually maybe not be so much different from the breadboard, they will
  definitely share some modules or strategies and interfaces") and, on #1937, "lets just leave the penalties for
  turning and crossing and such configurable or at least as constants in the code" (E the brief's Frame, #1937
  comment).

PA-2 · The request of 2026-11-28 asks for paper and gives a licence to refactor. It asks for no soldered board and no
date. Its verbs are "refining and planning and designing", "including the designs". The one line that can pull code
work forward is "feel free to refactor anytime you think something could be dried out". P1199 D3 says the layout core
is built after the MVP, in the first slice that needs it. Two readings fit his words. (a) Refactor inside a card that
touches the code anyway, such as P1350 #1937, now in Build on wire_routing.py, whose costs become named constants by
D-h. (b) His words widen D3, and a shared-part refactor may run before the MVP. · E the request in brief.md Frame, P1199
brief.md:124 (D3) · H (my reading) · supports only: an open question with a direct MVP cost. It is Q-1.

PA-3 · Against the MVP bar the perfboard step scores zero, and the MVP is not done. AGENTS.md's bar asks "does it move a
basic project closer to a breadboard with working firmware?". The perfboard starts after that point: in the screens
design its station opens only after the person says "it works" (E the store's councils/past-breadboard/architect.md,
section 1). scrum/VISION.md holds no line with "perfboard", "permanent" or "solder" (E grep, 0 lines). The MVP cards
still come first: "MVP cards first", with P1208 #1757, P1207 #1756, P1220 #1769 and P999 #1455 named, and the MVP walk
after (E the store's spark-main-handover-2026-11-27.md:8). Since 2026-11-27 08:00 CET the rules allow one coordinator
and at most one lane session (E the same file, line 99). The cost of this discovery is Opus agent time and, if this
perfboard lane holds the one lane, an MVP card that does not run in a lane meanwhile (H, I did not check which sessions
run now). AGENTS.md says "Plans shrink with distance. Only Ready and the next slice are refined in detail", and the
PO's rule of 2026-11-16 says write once, after the state is final (E memory note no-work-that-gets-redone). A full
design of a post-MVP step rests on code that P1237 #1790 and P1350 #1937 will change. · E and D · supports only: keep
the paper short and decision-shaped, and build nothing before the MVP unless Q-1 says so.

PA-4 · No evidence that he has soldered a perfboard, and no date for when he will. A grep for perfboard, protoboard
and solder over the store's bench files (bench-2026-11-20.md, bench-2026-11-25.md), bench-layout-log.md, the handoffs
and the 15 walk projects found no bench line about soldering a perfboard. The only solder traces are on modules: the
round INMP441 mic board was "soldered to header pins in a breadboard" (E the store's
shelf/inmp441-i2s-mic-round.json:12, photo of 2026-11-10, the record does not say who soldered it), and the e-paper
display's header is "soldered at one long edge" (E walk project p934-epaper/diary.md:19, which P1199's user lens read
as factory-made, council/user.md:56). His own "I am not sure what the best practices are actually" suggests little
perfboard practice (H, from #311 note 3). The plans are "Yes, but later" (D, 2026-10-16) and a permanent build for the
clock and the bin (D11, 2026-11-23, an account). Neither names a date or a board. On 2026-11-24 the backlog review
proposed closing #311 "as not now" (E the store's backlog-review-2026-11-24.md:143). He then added three notes
(2026-11-26) and asked for the design (2026-11-28). P1199's question "What did you solder before?" was never asked (E
P1199 council/user.md:66, not among D1 to D15). · E and D · supports only: his interest rises, the soldering date is
unknown, and the step sheet's depth for a first-time solderer is open.

PA-5 · He owns two kinds of prototyping board, and the brief names only one. The store's drawer/dfrobot-fit0193.json
says "ProtoBoard Pro - Double Sided (100x75mm)", count 2. The store's drawer/dfrobot-dfr0481.json says "Proto Board -
FireBeetle Covers", count 1. Both came from his DFRobot order history, read 2026-10-04, which keeps no dates and says
"bought is not the same as still in the drawer" (E the store's drawer-import/dfrobot-orders.json:2). His working
gadget, the e-paper clock, runs on a FireBeetle 2 C6 (E README.md, the Bench row). A cover stacks on the dev board, so
"cut smaller" does not apply to it (P1199 council/user.md:65), and D-c's model of a board cut down from the drawer does
not fit it. P1199's ★C15 noted the DFR0481, and its D8 names only the FIT0193. The 100 x 75 mm is the seller's label,
not a measurement. At 2.54 mm pitch, which D8 leaves unmeasured, a 100 mm edge holds at most 39 pitches before any
margin (H, a calculation: 100 / 2.54 = 39.4). I did not check that a FireBeetle cover fits the FireBeetle 2 C6's
header. · E · supports only: which board he would solder first decides D-q5 (one record kind or two) and D-q4. It is
Q-2.

PA-6 · The Done line on #311 is the team's words, not his. The card's body quotes him only for "how making routes
works there" (2026-10-16). "Done when: A button-light perfboard layout that the circuit check accepts" came from P269's
discovery (E #311 body). The smallest result I would propose, H (my opinion): one CLI run on button-light writes the
perfboard plan in text. Each part's holes, each join with its kind (a solder bridge, a bare wire on the back, an
insulated jumper over a crossing), and the cut size in holes across and down with mm beside it (D7). The same-pins check
passes over the joins. That check exists for breadboard jumpers today (E P279 #317, Done). No drawing, no page, no
drag, no step player. The drawing with the part pictures (D-e) is the next slice. Button-light is a XIAO ESP32-C6, a 6x6
mm tactile button, a 5 mm red LED and a 330 Ω through-hole resistor, with 4 wiring points (E the button-light
project's breadboard.md, lines 1 to 4 of its Wiring, written 2026-10-13). The plan rests on the pitch assumed at 2.54
mm until D8's calipers. Whether he calls this done, or needs the sheet he solders from or the picture, is his (Q-3). ·
E and H · supports only: a candidate for the smallest slice, not his acceptance of it.

PA-7 · The two canvas artboards disagree on where the dev board goes. The store's
councils/hosts-2026-11-27/canvas/LayoutPerfboard.dc.html draws button-light on the FIT0193 "wired to the board by a
3-pin header", so the dev board sits off the perfboard. The store's councils/hosts-2026-11-27/canvas/Perfboard.dc.html
puts the FireBeetle on the perfboard, in a plan of "26 × 18 holes" and 14 steps. That plan is an example that spark
did not make (E the store's councils/past-breadboard/po-stand-in.md, section 3). The Perfboard artboard now explains
soldered joins in place of the "green wire" that his note 3 questioned (E its "Why a fresh plan" text). · E ·
supports only: D-q4 has three live answers on the canvas and none from him. It is Q-4.

PA-8 · Decided, open and delegable, by his words.
- Decided, not to reopen: the brief's D-a to D-k, P1199 D3, D4, D6, D7, D8 and D13, P269 D3, D7 and D15 (D, each
  with its date in the brief and the files above).
- D-b says "the perfboard still comes after the editor that keeps moves (D8, step 5)" (E #311 note 1). After P1199 D4
  there is no kept_moves editor to wait for. The editor that keeps moves is now P1237 #1790's `edit-layout` on the CLI
  (H, my reading of D4 and #311). The layout log ties them the same way: with fewer than 3 lines, "the walking skeleton
  P1237 #1790 waits until the perfboard card is pulled" (E the store's bench-layout-log.md:14). So pulling P275 is the
  likely slice that births the layout core under D3, and this discovery's shared part is partly P1237's design (H).
  On day 3 of 14 the log's day table is empty, with no bench day marked for 2026-11-26 or 2026-11-27 (E the same file).
- Open and his to delegate, by his own pattern: D-q2, what is shared ("feel free to refactor anytime you think",
  "Make sure the architecture is good as usual"). D-q3, the join practice and its costs ("I am not sure what the best
  practices are actually", and on 2026-11-28 "you pick whatever you think its best" for the router's holes, with the
  costs as named constants by D-h). The rules send a misfit with the core to him, never accepted in silence (the
  store's rules.md, How to work). D-q5's record shape follows D-c once Q-2 names the board. D-q4's lead spans and the
  part pictures without pins are technical (D-e decided the pictures).
- Open and his: the order against the MVP (Q-1), the first gadget and board (Q-2), what done looks like (Q-3), how the
  dev board is held (Q-4). · E and D · supports only: four questions, the rest delegable.

PA-9 · The riskiest belief on the value side, and a pre-mortem. The belief: he solders a perfboard within a few months
of this design, before the code it describes moves (H, my reading of PA-4). Pre-mortem, "six months after the design,
nobody had used it". The clock went straight to a PCB, because D11's "not just pcb" names both and P79 #16 has its own
gate. He reached for the FireBeetle cover, and the plan assumed a plain board cut down. The design was refined in
full and redone when P1237 split drawing.py and P1350 changed the router. The cheapest test is Q-2, one question. The
next cheapest is P1074 #1575, the spike in Idea that takes the clock or the bin toward a perfboard and records where
spark stops (E #1575 body). · H (failure stories), E (cards) · supports only: the order of the questions.

## What I could not check, and why

- Which sessions run now, so whether this lane holds the one lane slot (PA-3). I read no session list.
- Whether the DFR0481 fits the FireBeetle 2 C6, and whether the FIT0193 has single pads or bus strips. No search was
  allowed, and D8 leaves the calipers to him.
- Whether he soldered anything outside spark's files. A soldering session leaves no trace in the store or the walks.
- The 5 projects on projects.json whose temp folders are gone (P1199 PA-1). I did not re-read projects.json.
- The canvas artboards as rendered. I read their text only.

## Questions for the decider

Asked one at a time, in this order. Each names the decision it changes.

- Q-1 · D-q6 the order · "Your words 'feel free to refactor anytime': may the shared-part refactor of the breadboard
  code start before the MVP walk?" · options: (a) No, D3 stands. Refactor only inside a card that touches the code
  anyway (P1350 #1937 now, its costs as named constants), the rest after the MVP. (b) Yes, one refactor PR may run once
  the MVP cards in Build are merged, before the walk. (c) Yes, now, beside the MVP cards. · I would pick (a), because
  the bar gives the perfboard zero (PA-3).
- Q-2 · D-q5 the record, D-q4, D-q6 · "Which gadget would you solder on a perfboard first, and on which board?" ·
  options: (a) the e-paper clock on a FIT0193 cut down, (b) the e-paper clock on the DFR0481 FireBeetle cover, (c)
  another gadget, which you name, (d) none planned yet, button-light is a test only. · No pick: it is his account and
  plan.
- Q-3 · D-q1 the step for a person · "What is the first perfboard result you would call done?" · options: (a) a plan in
  text from the CLI on button-light: holes, joins with their kind, the cut size, and the same-pins check passes, (b) (a)
  with the drawing of both sides, from the breadboard's part pictures, (c) (b) with the page screen and its step
  player. · I would pick (a), with (b) as the next slice.
- Q-4 · D-q4 parts on a perfboard · "How is the dev board held on the perfboard?" · options: (a) on female headers, so
  it comes off to reflash or reuse, (b) soldered straight in, (c) off the perfboard, joined by a pin header and wires,
  as the LayoutPerfboard artboard draws, (d) the team picks, yours to change. · I would pick (a) (H, it keeps the
  tested board reusable).
- Queued, only if the team needs it, an account: "When did you last solder anything, and what was it?" · decides: how
  much the step sheet teaches (D-q1).

## Searches

none
