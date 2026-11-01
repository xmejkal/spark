# Refuter, second pass (close), independent

An agent that did not write the folder ran this pass. It read only. It opened no serial port.

## 1. What was read

The start is an existing product, and the PO is its only user (n = 1). Sections read: brief.md's Hand-off, Options,
Riskiest, D4 to D17 and the Questions statuses. Also shape-for-design.md, items.md, story-map.md,
risks-and-tests.md's Results and A11, upstream-report.md and docs/observations/2026-10-15-p235-reach-test.md. The
sources for the comparison: verification.md, council/refuter-close.md, INDEX.md AT185 to AT187 and P218's story map.
Also developing.md's "Patterns and names in spark's core" and the git history of upstream-report.md.

## 2. Caveats dropped, claims stronger than the source

### The brief

- Riskiest says "Each miss was a silent console after a power-on (AT187)". The bench log does not show that. Half 2's
  three misses are mpremote's `could not enter raw repl`. Only miss 1 got a second look, and that look was a port open
  that restarted the chip. Nobody listened before it, so a silent output was not shown even there. Misses 5 and 7 got
  no retry and no listen. H3 (10 s is too early on some boots) is not ruled out for them. The log itself says "None
  was tested" (reach-test.md:50).
- The Results row says "A1 stays open". A1's status says "retired 2026-10-15". One of the two is wrong.
- The Results row says "a port open restarted the board and the next try passed". That happened once, after miss 1. The
  row reads as a rule for each miss.
- The cause hunt (rounds A to C) changed the decision (D5, D6), but it has no Results row. A11's evidence points at it
  with no Results line to anchor it.
- A11's evidence says "the cure worked 2 of 2 times (08:25, 08:48)". At 08:25 the board was not shown silent (see the
  first point). Only 08:48 is a cure of a shown silence. That is 1 of 1.
- A11's belief says "every board". The only test planned is one XIAO C6 on one Mac. The test cannot support "every".
- The Hand-off's "Success and its proof" gives "10 replugs, 10 of 10 reached, each cure named" as the proof. That pass
  line is the facilitator's proposal, pending the PO (Riskiest, Test). The Hand-off drops "proposed".
- The Hand-off names `spark live --code ... --json`. No D names the command. items.md P253 says the name is a sketch.
  The Hand-off, P247's title and the story map's "Live 0" done-when drop that caveat.
- The Hand-off's constraints list D13 (one look per grant) without ★C13's caveat: the look is an esptool reset that
  restarts the gadget, and a board put in download mode by hand stays there. It lists D14 without D14's own caveat (a
  pin number built at run time passes). It lists D12 without ★C5's keep words "the grant's shape is H".
- Q5 and Q9 say "answered by D10's first story (pending)". Nothing answered them. D10 deferred them. items.md P252 even
  says the PO "then picks" the meaning, so a PO decision is still open behind an "answered" label.
- Q10 and Q11 say "deferred". No D row records a deferral. The Chosen line states it as the PO's. Its source is the
  facilitator.
- Q14 to Q24 say "not asked: no slice 0 decision rests on it". The value row in Risks names Q14 and Q20 as the way to
  retire the value risk, and Riskiest names A2 (value, tested by Q14) as the rival. So slice 0's value does rest on
  Q14. The collection plan's reason, "D9 to D17 were decided without them", is circular.
- D9 holds a class name, "(RetryingBoardConsole)". shape-for-design.md says the design picks the real names. The folder
  does not show that the PO saw that name. A D row now fixes a sketch name.
- D14 holds the facilitator's caveat (H) inside the PO's D row. The row mixes his words with an inference.

### items.md against the D rows

- P252 (bench): D10 calls it a story. The PO's standing rule says a research item is a spike with the `spike` label,
  and its answer is a finding. A bench log that answers three questions is research. The item's label conflicts with
  that rule. It also adds "whether the port stays after each reset", which D10 does not name.
- P251 (the cure): "10 of 10 reached" is the facilitator's proposed pass line, not a D. "Built as
  `RetryingBoardConsole` around a platform-neutral `BoardConsole`" goes past D6 and D7, which name no classes. The
  baseline "1 to 6 silent of 10" mixes counts of different kinds (see part 3).
- P251's proof can pass without a single cure. At 1 silent in 10 (rounds A and C), the chance that 10 replugs give no
  silent boot is 0.9^10, about 35 %. Then "10 of 10 reached, each cure named" is met with zero cures. The proof needs a
  floor of shown silences, or a forced silence.
- P253: `--minutes 30` has no D. D12 says "a time limit" only. refuter-close.md says 30 came from a preview.
- P254: "the output says that a pin number built at run time is not caught" turns the facilitator's caveat into a
  requirement. D14 does not ask for it.
- P246: "passes in Wokwi", "prints `ready`" and "shows what a live try changed" go past D16, which says only "a new
  board-only project". #260's quote supports "without anything", not the three proofs.
- P247: "unknown" as a third verdict and the class `LiveTryResult` are sketch content. D9, D11 and D15 do not name them.
- P256: "OK on the text given with 'ok, lets go' (D8)". D8 was committed at 09:07 (4f9ede0). The draft gained a line at
  09:19 (4926248): "We have not ruled out a loss on the Mac's side". The PO's OK covers an earlier text.
- P255: the quote "remember to name the classes and objects well so they're understandable" has no pointer. It appears
  nowhere else in the repository. D8 holds a different quote.
- The Board actions line says every action "needs the PO's yes to this list", including the moves in
  scrum/STORY_MAP.md and Miro. D17 says only the issue moves wait for that yes. The line is stricter than D17. The
  brief's Board actions say "pending, D17". The two files disagree on what D17 already allows.

### story-map.md against the D rows

- The delta keeps P218's slice 4 row "Change it and put it on again" (D20) with P218. D17 says "its deploy map's slices
  4 and 6 move under P235". Splitting slice 4 is a choice the PO did not make. It can be right, but it needs his word.
- The map's status says D17 applies it "after the PO confirms". D17 says "at the close, in this PR". Same split as above.
- Every tag cell drops verification.md's keep words. P253 cites "E ★C5" without "the grant's shape is H". P254 cites
  "E ★C7" without "MCP extracts". P246 cites "E ★C2" without "one run". P247 cites "E ★C1" without "no live try ran".
  Slice 1 cites "★C6" without "bare opens". Slice 2 cites "★C8" without "ran on a board" (that is, none did).
- P251's row tags "E reach-test.md" and gives "10 of 10 reached (A11)" as its proof. The cure's evidence is 1 shown case,
  and the pass line is a proposal.
- "Live 0" done-when says Claude's call "cures a silent console after a power-on". Whether a silence occurs on that
  bench is chance (about 35 % none in 10 at the low rate).
- P256 and P255 sit in the walking skeleton with no job. Live 0's done-when does not cover them. A docs row and an
  outside report do not move a live try end to end.

### shape-for-design.md

- It stays mostly a sketch, and it says so. Four points still go past a D or the naming table.
- `LiveGrantStore` is marked Adapter. The table defines Adapter as a wrapper of "an outside program". Grant files in the
  store are not a program.
- `RestrictedPins` is marked Value. The table defines Value as "facts with no actions". It has `why_refused(code)`, an
  action.
- `FakeBoardConsole` is marked Fake. The table has no Fake role, and D8 adds only Decorator. The preface says "plus
  Decorator (D8) and Fake" with no D for Fake.
- `reset_from_usb()` sits in the platform-neutral Strategy `BoardConsole`. D7 asks for neutral board-facing code. A USB
  reset is a transport fact, not a platform fact, and the sketch fixes it in the base.
- The sequence shows "Ctrl-C, Ctrl-A, the code" inside `RetryingBoardConsole`'s lane. Those are MicroPython raw-REPL bytes
  in a neutral decorator.
- `ConsoleResult` has `reached`, `output` and `silence_cured`. D11: after the cure fails, spark names both causes. The
  sketch has no field for a cause. From mpremote's one error, the decorator cannot tell a silent console from a
  firmware that does not read its console. The bench told them apart with a separate probe and the PO's eyes.
- `--minutes 30` in the sequence has no D.

## 3. Rival explanations not ruled out

### AT187 (output dead, input works)

- The Mac drops the bytes (its USB driver or pyserial). The folder now names this. Nothing tests it.
- MicroPython's own drop rule latches. ★C6 says v1.29.0 drops output that no reader takes within 200 ms. If the host
  does not read during boot, the driver can stay in a drop state. A soft reset does not reinit that driver, so "a soft
  reset does not cure it" does not rule this rival out. It is H2 under another name, inside MicroPython, not the chip.
- How the plug went in. A slow or angled insert, or a short time unplugged, can give a partial power-on. The bench log
  records plug times for half 2 only, and no unplug times. Rounds A to C have no times at all in the log.
  refuter-close.md says "The logs record the unplug and plug times". The committed log does not.
- The LED as proof that input works. The PO saw 3 blinks for 6 toggles, as expected. Nobody recorded it, and the PO knew
  what to expect. It is one observation, on one silent boot.

### The cure (a port open with DTR and RTS off)

- The reset may come from a change of line state, not from the open itself. Both cures came after mpremote had opened
  the port with DTR and RTS True. Round A's probe opened with both True and did not restart the chip. If P251's call
  opens a fresh port in its first state, the same open may not reset the chip. The folder does not test the cure from
  a cold port.
- Any fresh boot cures, at the base rate. A replug works 4 to 9 times in 10. A chip reset is another boot. 1 shown cure
  in 1 is what a plain reboot gives most of the time too. Nothing shows that the cured boot cannot go silent again.
  A11's "one retry" rests on that.
- The cure also makes the Mac enumerate the port again. That fits the host-side rival as well as the chip-side one.

### The rate "1 to 6 of 10"

- The rounds measured different things. Half 2 counted mpremote failures (3 of 10), not shown silences. Round A used a
  probe (1 of 10). Round B ran esptool on each silent board (6 of 10). Round C stopped at its first silence (1 of 4),
  which is a stop rule, not a rate. refuter-close.md leaves round C out. upstream-report.md keeps it in.
- Chance alone. 1 of 10 against 6 of 10 gives a two-sided Fisher exact p of about 0.057. One rate near 0.3 with
  sampling noise fits the data. "The rate varies" is not shown.
- Drift over the session. The rounds ran in order from 08:24 to about 08:48. The Mac's USB state, the board's heat or
  the PO's way of plugging can change across rounds. Nothing separates them from the procedure.

## 4. Numbers without unit, population, period or provenance

- "1 to 6 silent of 10" (P251's baseline, AT187): mixed populations (mpremote failures, probe silences, esptool-touched
  boots). No times for rounds A to C.
- "1, 3, 6 and 1 of 10, 10, 10 and 4" (reach-test.md:78, upstream): the 3 are not silences, and the 1 of 4 is a stop rule.
- "2 of 2 times" (A11): 1 of 1 is shown.
- "10 of 10 reached" (P251, story map, Hand-off): a proposal, set by the facilitator, not marked so in the Hand-off.
- "--minutes 30" (P253, sketch): no D, no unit source beyond a preview.
- "200 ms" (★C6, `usb_serial_jtag.c`): no file path, line or commit.
- "line 51" of light.py (round A, Q15): light.py changed at 02:10, and the log gives no hash.
- "10 s" (wait after the port appears): no source for why 10, and H3 says it may be too short.
- The quote under P255: no pointer, no time.
- "3 blinks" (round C): seen by the PO, not recorded, with no timing.

## 5. The upstream draft

- Public-safe: no home path, no token, no MAC, no port path. "Darwin 24.6.0" and "mpremote 1.29.0" are fine. The bench
  log, not the draft, holds the MAC 8C:BF:EA:XX:XX:XX and /dev/cu.usbmodem1101. The draft does not need them.
- "1, 3, 6 and 1 silent boots": the 3 are mpremote failures, not shown silences.
- "with the try 10 s after the port appears": true of half 2 and rounds A and B. Round C replugged until silent.
- "To reproduce: ... run `mpremote connect <port> exec`": only half 2 used mpremote. Rounds A to C used a custom probe
  with esptool in round B. A minimal `main.py` was never run. The draft offers an untested repro.
- "`main.py` runs" on a silent boot: not shown. Round C shows code sent in the raw REPL ran.
- "prints `b''`": not in the 10-15 bench log. It comes from 2026-10-14-p215-bench.md:18, a different event after a flash.
- The firmware string comes from 2026-10-14-p215-bench.md:23, not the 10-15 log. It is likely the same image, but the
  draft does not say where it was read.
- "after that boot the output works": 1 shown case (08:48), plus 08:25, where silence was not shown.
- The draft does not say n = 1 board, one Mac, one firmware, which the bench log states (reach-test.md:76).
- The text changed after the PO's OK (09:07 OK, 09:19 edit). D8's OK does not cover the added line.

## Searches

none
