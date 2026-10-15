# Refuter, second pass (close)

No independent review: the fork that prepared the close ran this pass itself, because a fork cannot start an agent.
The directive asked for a separate agent on the strongest model. The PO decides whether a separate pass runs before
he confirms the hand-off.

Sections read: the Hand-off draft, the Shape for design (shape-for-design.md), Options (the Chosen line), Riskiest,
items.md, story-map.md, risks-and-tests.md (A1, A11, the collection plan), the question statuses.

## 2. Caveats dropped, claims stronger than the source

- The Hand-off's outcome said that a silent console "no longer stops it". That is P251's goal, and A11 is untested.
  Changed: the outcome now says so.
- P253's `spark live --grant` is a command name from the PO's chosen preview, and spark has no `spark` command today
  (its commands are scripts). Changed: items.md says the name is a sketch.
- Q17's status says that esptool's `Invalid head of packet (0x08)` tells a silent firmware from the ROM. It shows that
  the ROM did not answer. It does not show what sent the byte. Kept, with this note.
- Q19's status: the port name stayed `/dev/cu.usbmodem1101` in the 10 replugs of the reach test (10 of 10 lines in the
  watcher's log). The cause hunt's logs do not record the name, so the claim is limited to those 10. Holds as written.
- The P251 baseline "1 to 6 silent of 10" covers three rounds of 10 (3, 1 and 6). Round C stopped at its first silent
  replug (1 of 4) and is left out of that range. Holds.
- story-map.md cites scrum/STORY_MAP.md lines 67-68 for J4 and J6, and P218's map lines 35, 36 and 38 for slices 4
  and 6. Re-read with grep: holds.

## 3. Rival explanations not ruled out

- AT187 says that the board's output dies while its input works. A rival: the output leaves the chip and is lost on
  the Mac's side (its USB driver or pyserial). The cure, a chip reset, also makes the Mac enumerate the port again, so
  it does not tell the two apart. Changed: the bench log and the upstream draft now name this rival.
- The silent rate varied from 1 to 6 of 10. A rival not measured: how long the cable stayed out, or how fast it went
  back in. The logs record the unplug and plug times, so a later look at them can test it.
- The sketch draws `reset_at_end` inside `RetryingBoardConsole`'s lane. A rival design calls it from
  `LiveTryService`. The sketch says the design settles it.

## 4. Numbers without unit, population, period or provenance

- "30 minutes" in P253 is an example from the PO's preview, not a decided limit.
- A11's pass line, 10 of 10, is the facilitator's proposal, dated 2026-10-15, and waits on the PO.
- "1 to 6 of 10": measured, one XIAO C6, one Mac, button-light, 2026-10-15 08:24 to 08:46.

## Searches

none
