# Vision

**Confirmed by the PO on 2026-10-03** (P69). A discovery council of four lenses — vision, personas,
story map, skeptic — read the repositories and their history, each claim marked evidence or
hypothesis; the PO chose among what they found. `STORY_MAP.md` turns this page into the order.

## What spark is

**The PO's overview of the direction, 2026-10-03** — in his words *an overview, not a full process*;
the process is designed with him (P76), and nothing below is read as its specification: *"We first need to make it work, really from just
talking about some vague idea the human says — the AI guides him through brainstorming the DIY idea,
what modules are available that do something we'd need, what else it could also do; helps the
human formulate the idea and walks him through the whole process to an actual circuit of connected
modules, or just a schematic first, without specific parts — just what it does, like an MP3 player
module. Then, if the human wants, a PCB he can order, with the firmware already working enough and
tested and improved agile-style — and later 3D model export, even Fusion 360, 3D-printed parts."*

Later the same day, building the quickstart with Claude: *"we should definitely add a breadboard
phase, before the user decides to go for a PCB — no SMD parts; only later, when the circuit is tested
and the firmware good, we offer the PCB."* Also an overview.

What it says about the shape, and no more: the journey starts earlier than spark does today — at a
conversation, not a requirements file — and can end later, at a board you can order and a printed
enclosure, both optional. How each step works is not decided.

spark is a Claude Code plugin for someone building a DIY gadget from an ESP32 dev board and
off-the-shelf modules. You start from an idea in words; spark helps shape it into what the device
must do and which kinds of module do it, then researches each part from
vendor documents, assigns every pin with a reason, generates a board that builds and simulates, and
checks it — refusing rather than guessing, and saying when a check could not look. Next, the
firmware you or Claude write imports spark's pin facts and is tested free on a laptop, then proven
on real hardware by a bench protocol.

## Who it is for

| | who | evidence |
| --- | --- | --- |
| **Primary** | **The hobbyist.** An idea in words, whatever ESP32 board is in the drawer, some modules. At home in a terminal; no EDA, maybe no meter, no Wokwi licence. Succeeds when `/spark:build` exits 0 on *their* board and then their firmware runs. Quits when their board is not one spark knows, when a paid simulator blocks them, or when `init` asks for values they cannot measure. | **Hypothesis.** The PO's choice. Every "stranger" so far was Claude in one of our sessions, and no person outside the project has installed spark. Slice 5 tests it with a real one. |
| **The test bench** | **The maker** (Petr). A dead bin and a drawer of modules; directs Claude rather than typing commands; buys from Czech shops. His bin is spark's second bench, after v0.10's button-and-LED walk. | **Evidence.** Its board is hand-written and spark checks it — spark never generated it. Nothing has run on hardware yet. |
| **A constraint** | **The agent at the keyboard.** Every logged run was one. It must act on a script's answer without reading the script's source. | **Evidence**: the 09-24 first-time run *"got there by reading Python source, not docs"*. It counts only through the two above. |
| **Not for** | **A professional ordering chip-down boards in volume.** spark is "a board made of modules"; its autorouter can emit shorts (README); real layout is out. | the PO's v1 line (now v0.10); the README |

**What would change this page:** the real outsider (slice 5) who meets their goal with a
breadboard and firmware alone and never wants a board file ends the hobbyist as written; one whose
board spark does not know, and cannot be taught in one sitting, puts *bringing your own board*
ahead of everything after it.

## Versions

Every planned version comes before the launch, and spark stays at 0.x until the PO says otherwise (the PO,
2026-10-14: *"it has to be an mvp"*). The basic journey is v0.10, then v0.11, v0.12 and v0.13. 1.0 is the launch.

Refinement decreases with distance (the PO, 2026-10-11: *"only the to of the backlog is really refined t detail and
the lowe on the backlog the less details"*). v0.10 is planned item by item on the board. The next version is one epic in
the PO's words, and each later one a line. Detail moves down only when work moves up. The order after v0.13 is
decided when v0.10 is done. This table is the one place versions are kept current; the replan of 2026-10-11 is where it came from.

| version | done when | how much is planned |
| --- | --- | --- |
| **v0.10 — the basic journey** (done at v0.10, the walk; v0.11, change and flash again, and v0.12, another board, follow) | from an idea in words, a hobbyist gets a parts list, a breadboard sheet and firmware that passes the simulation and runs once flashed onto their own board, with the PCB and 3D model on request. It is proved by the PO's walk of button-and-LED to a lit LED, and to be kept by `tests/test_journey_basic.py` (v0.10's item 1) | each Ready item in full, the next slice a line each: [the replan](../docs/2026-10-11-replan.md) and the board |
| **v0.13 candidate — one core** | *"a real object oriented system, a package or module, that then MCP or AI or human through CLI can be acccessed and its calling the same code, so we don't have extra artefacts and code that's not refactored and reused"* (the PO, 2026-10-11) | one epic, [P158](https://github.com/xmejkal/spark/issues/94); its 2026-10-10 design and plan are input, not its plan |
| **later** | the store, shared ([P178](https://github.com/xmejkal/spark/issues/123)) · checks for bigger projects · a board you can order · an enclosure · a stranger's first install · team and QA tooling · one front end for spark ([P199](https://github.com/xmejkal/spark/issues/152)) · interactive system maps ([P198](https://github.com/xmejkal/spark/issues/151)) | one epic each |

## Not goals

| not a goal | why |
| --- | --- |
| Production layout, chip-down design, volume | the anti-persona's needs. **Ordering a board of modules is IN the journey** (the PO, 2026-10-03, revising the morning's "later"): optional, after the firmware works — a later version |
| Analogue simulation; a link between two boards | out of v0.10 by the PO; R10 parked |
| A firmware generator, or anything that writes behaviour | P56: spark exports facts and a harness; the conversation writes the firmware |
| A knowledge skill per firmware runtime | P60: the current models already know the runtimes; the guarantee is a check against the real runtime, never a reference |
| Arduino or ESP-IDF before a design pulls them | F1, F2 parked |
| Reimplementing tscircuit, KiCad or Wokwi | spark checks and drives them |
| Shipping vendor documents | P61: records point; each person's store keeps the files |
| Anything designed on paper before a design needs it | W14; the 09-29 cut deleted 5,962 lines built that way |
