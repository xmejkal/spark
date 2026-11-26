# P1089: the council's answers

The council of three answered the ten questions of [finding.md](finding.md) section 6 on 2026-11-26, 07:44 to 07:47
CET. Each seat ran on Fable: the tech lead, the architect and the PO assistant. Each answer is delegated, the PO's to
change. The recommendation itself is the PO's to decide.

How the facts were checked: every count comes from runs in a scratch copy, as [notes.md](notes.md) says. The refuter
on Opus reproduced the main claims before the council read them.

## The answers

| # | Question | Answer | Seats | Condition |
|---|---|---|---|---|
| 1 | Does spark move its board engine to KiCad now? | (a) No. KiCad comes after the build as an export. | all three | The PO decides this one himself, because it turns his words of 2026-11-26 on a switch to KiCad around. |
| 2 | Which pour does a generated board ask for? | (a) One GND pour per layer. | all three | The pour is one named value in one place. Try more boards before the merge. Name the clearance that the check uses, from one source. |
| 3 | A KiCad MCP server in the tools list? | (a) No, and `docs/mcp.md` says today's reasons. | all three | Ask again at KiCad 11. |
| 4 | Does the export card go to Ready now? | (a) Yes, after the pour card. | all three | Each KiCad finding names the clearance it used and that number's source. The PO assistant puts F4 first, because a STEP of a bare board gives Fusion nothing. |
| 5 | How does the export enter? | (a) A new Operation `export-board` with a role for kicad-cli. | all three | It goes in `build_operations.OPERATIONS` and names no tool itself. No kicad-cli gives `could-not-run`. Its findings name kicad-cli's version. |
| 6 | When does the seam card run? | (a) Now, as a small card with no behaviour change. | architect, PO assistant. The tech lead chose (b), with the second engine. | Say plainly that the seam makes the engine selectable, not yet exchangeable. No rename. The card covers every selection site (below). |
| 7 | Does the spike run Freerouting? | (a) No, for the council. | all three | Only the PO can allow the run of the downloaded binary. He asked for the run through spark-main at about 07:35 CET, and his own yes in the kicad-spike window decides it. |
| 8 | Is F5, the placement, in scope? | (a) No. One line under P203, with the 80 cm² measure. | all three | The PO looks at the pictures first. If the empty board is his "weird", it becomes (b). |
| 9 | Does F8, the 0.7 mm silkscreen, get a card? | (a) No, until a fab's rule with a source says that 0.7 mm fails. | all three | none |
| 10 | Which body does F4 use? | (a) A box from the record, with the height as a new fact. | all three | A null height gives no box, and the build says so. The PO assistant puts this card first among spark's fault cards. |

## What the seats added

- Tech lead: the clearance has one number already. `pour_contact.py:43` to 61 judges by the board's
  `min_trace_to_pad_edge_clearance`, and it says that tsci cuts pours at 0.2 mm. The export uses that number, not a
  third one.
- Tech lead: by the MVP bar, the pour card, F10 and F9 serve the breadboard first. The export, the seam and F4 are P203
  work. Proposed order: the pour card, then F10 with F9, then `export-board`.
- Architect: the seam card covers every selection site. These are `build_service.py:211`, `board_engine.py:129`,
  `requirements_build.py:93`, and the two places that build `TscircuitExport` (`build_board.py:141`,
  `kept_files.py:577`).
- Architect: the engine and its board writer are one choice. One table gives the pair.
- Architect: the contract `tscircuit-board` says what it promises, for example "gives `dist/board/circuit.json`". The
  table keys on a fact in the tool's entry, not its name. An unknown key is `could-not-run`, never tscircuit.
- Architect: the Fake subclasses the base, as `FakeFirmwarePlatform(FirmwarePlatform)` does.
- Architect: the export asks the engine for the KiCad files, through a method of the Strategy. It adds no third wrapper
  of `tsci`.
- Architect: the kicad-cli entry in the tools list is off by default, as `rich` is. `/spark:setup` names the 1.4 GB
  download and asks before an install.
- Architect: a netlist already exists before the build in one case. For a board alone, `board_alone_input` writes
  `netlist.json`, and the converter reads it (`build_service.py:478`). A later neutral plan reuses that shape.
- PO assistant: the first pair of pictures was not like for like. The session replaced it with a fair pair: today's
  board with today's footprint, with and without the automatic pour.
- PO assistant: `tsci export -f step` needs no KiCad. The session ran it: one product named "PCB", 618 KB, and no
  module bodies.

## What the PO decides himself

- Question 1, the move to KiCad, because it turns his own words around.
- The run of Freerouting, in the kicad-spike window.
- Whether the "after" picture is no longer "weird", and the Ready order of the cards.
