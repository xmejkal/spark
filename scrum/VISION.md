# Vision

**Confirmed by the PO on 2026-10-03** (P69). A discovery council of four lenses — vision, personas,
story map, skeptic — read the repositories and their history, each claim marked evidence or
hypothesis; the PO chose among what they found. `STORY_MAP.md` turns this page into the order.

## What spark is

spark is a Claude Code plugin for someone building a DIY gadget from an ESP32 dev board and
off-the-shelf modules. You describe the idea and list what you have; spark researches each part from
vendor documents, assigns every pin with a reason, generates a board that builds and simulates, and
checks it — refusing rather than guessing, and saying when a check could not look. Next, the
firmware you or Claude write imports spark's pin facts and is tested free on a laptop, then proven
on real hardware by a bench protocol.

## Who it is for

| | who | evidence |
| --- | --- | --- |
| **Primary** | **The hobbyist.** An idea in words, whatever ESP32 board is in the drawer, some modules. At home in a terminal; no EDA, maybe no meter, no Wokwi licence. Succeeds when `/spark:build` exits 0 on *their* board and then their firmware runs. Quits when their board is not one spark knows, when a paid simulator blocks them, or when `init` asks for values they cannot measure. | **Hypothesis.** The PO's choice. Every "stranger" so far was Claude in one of our sessions, and no person outside the project has installed spark. Slice 5 tests it with a real one. |
| **The test bench** | **The maker** (Petr). A dead bin and a drawer of modules; directs Claude rather than typing commands; buys from Czech shops. His bin is where spark meets hardware first. | **Evidence.** Its board is hand-written and spark checks it — spark never generated it. Nothing has run on hardware yet. |
| **A constraint** | **The agent at the keyboard.** Every logged run was one. It must act on a script's answer without reading the script's source. | **Evidence**: the 09-24 first-time run *"got there by reading Python source, not docs"*. It counts only through the two above. |
| **Not for** | **A professional ordering chip-down boards in volume.** spark is "a board made of modules"; its autorouter can emit shorts (README); real layout is out. | the PO's v1 line; the README |

**What would change this page:** the real outsider (slice 5) who meets their goal with a
breadboard and firmware alone and never wants a board file ends the hobbyist as written; one whose
board spark does not know, and cannot be taught in one sitting, puts *bringing your own board*
ahead of everything after it.

## v1, and what comes next

| | done when | proved by |
| --- | --- | --- |
| **v1 — a stranger's checked board** | from an empty directory and the docs alone, on **the documented example and irrigation** | `check_spine.py` exits 0, and `check_all.py` shows no `!!`, every `????` naming the fact to state |
| **Next — firmware tested before hardware, then on it** | the firmware fails on a Mac when it misses a pin it should drive; then the first bench run anywhere | a command that exits 1 on irrigation today and 0 after its fix; the bin's bring-up 01–06 logged with a verdict per step |

## Not goals

| not a goal | why |
| --- | --- |
| Ordering a board, production layout | **Later, pulled by a named design: the bin, once its first copper passes (slice 2).** Until then the fab pieces (`fab.py`, `data/fabrication.json`, `check_bom`) are kept working, not grown. The PO, 2026-10-03. |
| Analogue simulation; a link between two boards | out of v1 by the PO; R10 parked |
| A firmware generator, or anything that writes behaviour | P56: spark exports facts and a harness; the conversation writes the firmware |
| A knowledge skill per firmware runtime | P60: the current models already know the runtimes; the guarantee is a check against the real runtime, never a reference |
| Arduino or ESP-IDF before a design pulls them | F1, F2 parked |
| Reimplementing tscircuit, KiCad or Wokwi | spark checks and drives them |
| Shipping vendor documents | P61: records point; each person's store keeps the files |
| Anything designed on paper before a design needs it | W14; the 09-29 cut deleted 5,962 lines built that way |
