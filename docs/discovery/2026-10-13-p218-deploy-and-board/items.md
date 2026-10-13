# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

Every item is a proposal. Nothing is filed. An item on an existing card is a story or a checklist for that card.
Once the PO says yes, it goes into the card's body or a comment. An item marked new takes the next free number, P229 on 2026-10-13
(read from `gh issue list --state all`), read again at filing. Each item's logic sits in the core, and its interfaces
stay thin (D8). Slice names are the board's Slice options.

## P228 (#215) — the read-only bench: the checklist the discovery asks of it
- type: task, on the existing card <!-- REQUIRED:item-type -->
- needed by: "the not checking and ereasing etc cannot happen" (the PO, 2026-10-13, D4) and "and yes, its ok to splt it" (the PO, 2026-10-13, D12) <!-- REQUIRED:needed-by -->
- value proven by: the bench log keeps outputs as test fixtures: `mpremote devs`, and `flash-id`, `chip-id`, `read-mac` and `get-security-info` with esptool 5.5.0. It also keeps a read with `--chip esp32c6` and the revision read by eye. It says whether the board runs again with no button press (A4, A5, A6, A7, A11). Nothing is erased <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): task (the card's own label stays) <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P218 (#200) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v1 The basic journey <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P219 (#201), first story — deploy.py erases whatever board it reaches → the core reads the named board, says same, differs or unknown per field, and writes only after a yes bound to that board
- type: story, on the existing card
- needed by: "checksw if it all really applieas for the connected boar, if it really is the one it's meant for" (the PO, 2026-10-13, #201) and "it really has to be safe and check the board" (the PO, 2026-10-13, D4)
- value proven by: with no port, deploy refuses and lists the ports. Against a scratch record changed to the N4, it says "flash differs" and writes nothing. Fake-run tests refuse with no yes and with a yes for another MAC (A8). Flash size per SKU enters the record because this check needs it
- depends on: P228 (#215), for the real esptool lines. Q3 and Q7 shape the yes and the unknown
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): v1 The basic journey

## P215 (#196), the flash half — the image that passed goes on through the gate, and a command reads the start
- type: story, on the existing card
- needed by: "at least to breadboard including working firmware is important" (the PO, #144) and "and yes, its ok to splt it" (the PO, 2026-10-13, D12)
- value proven by: the PO's board, flashed once through the gate, prints `ready` in a log that a command read. `main.py` is listed, and `os.statvfs('/')`'s block count is written down (★C5 refuted). The record names the board's MAC, the image sha256, the date and whose yes (A1, A2, A3, A10)
- depends on: P219 (#201), first story
- status: proposed
- label (the repository's type label): story (the card's own label stays)
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): v1 The basic journey

## P213 (#192) — deploy answers in text only → `/spark:deploy` and `deploy.py --json` are thin interfaces over the core's answer
- type: story, on the existing card
- needed by: "Both the AI and humans should be able to use it well, find help, have json cli for ai, etc." (the PO, 2026-10-12, #192) and "a well architected core system that various interfaces use" (the PO, 2026-10-13, D8)
- value proven by: `deploy.py --json` returns the field states, the `unchecked` list, the refusal sentence and the next steps in `outcomes.envelope`. Claude relays a refusal word for word. The command page holds no gate of its own
- depends on: P219 (#201), first story
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): v1 The basic journey

## P229 (new) — a known board asks the same questions as a new one → its deploy runs silent checks and prints one receipt line
- type: story, new
- needed by: "if the board is known, we know its correct, the upgrade and deploy should be semless, but really being sure everything is ok" (the PO, 2026-10-13, D6)
- value proven by: the PO changes one line, gives one command, and reads one receipt line with the board's name and the image sha256. A board flashed by hand with another tool stops the deploy before any write (A9)
- depends on: P215 (#196), the flash half. Q2, Q5 and Q6
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## P219 (#201), second story — another board gets the project's image anyway → spark says what differs, ranks the records that fit, and offers stop, migrate, a general record or go ahead
- type: story, on the existing card
- needed by: "if not if at least the pin setup is correct or other settings to be determined or if it should just use another boars setpu or a general one. It should also howvwer allow this to be ignored" (the PO, 2026-10-13, #201)
- value proven by: a run against a wrong record names the field that differs and writes nothing. Another chip stops with both chips named
- depends on: P219 (#201), first story. Q7, Q10 and Q19
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## P230 (new) — two almost identical boards look the same to deploy → spark lists them by MAC and writes only to the one the person named
- type: story, new
- needed by: "what if there are two almost thee same boards connected to the computer" (the PO, 2026-10-13, D5)
- value proven by: with two boards plugged in, the core refuses until one is named. It binds a name to that MAC and finds the board by MAC after the flash
- depends on: P219 (#201), first story. Q6 and Q21
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## P231 (new) — the record cannot say which MicroPython build a board needs → spark offers the matching build on a yes and asks for the new run it needs
- type: story, new
- needed by: "offer a more suiting one or even somehow offer to download the firmware base" (the PO, 2026-10-13, D4) and "A MicroPython build that the board needs, if any, becomes its own card" (#196)
- value proven by: the record names the build. A passed log names the new image, and deploy flashes it
- depends on: A3's result at P215's bench. Q11
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22). If A3 fails at the bench, v1 The basic journey

## P222 (#204) — the spike's questions from this discovery
- type: spike, on the existing card
- needed by: "updates, debugging, connection with agents" (the PO, 2026-10-13, #204) and "maybe we/claude can try things live on the board" (the PO, 2026-10-13, D7)
- value proven by: a finding with sources on four questions. The update gate with per-file hashes (Q4). Live tries over USB with classes, a pin list and a session that ends with a reset (Q12). The Wi-Fi REPL's facts (★C13). Whether a third-party MCP plugin or belay is tried (Q13)
- depends on: P215 (#196), the flash half, for a board that runs MicroPython
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## P232 (new) — nothing on a board says what spark put there → a facts file on the board that the core reads back
- type: story, new
- needed by: "is there any protocol / workflow between the spark plugin and the boardd firmware" (the PO, 2026-10-13, D5)
- value proven by: `deploy.py --check` prints the project, the board id and the per-file hashes found on the board, and says absent for a board spark did not flash
- depends on: Q5
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## P233 (new) — OTA and a Wi-Fi REPL have no design → a discovery of their own
- type: epic or discovery, new, a later version
- needed by: "what about OTA" (the PO, 2026-10-13, D5) and "or on the same wifi" (the PO, 2026-10-13, D7)
- value proven by: a finding on the OTA layout, the code on the board that listens, the secret, the rollback rule and the cable sentence, with sources
- depends on: Q14
- status: proposed
- label (the repository's type label): epic
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## P221 (#203) — the spike waits on the not-goal question
- type: spike, on the existing card
- needed by: "mostly arduino probably and platform IO" (the PO, 2026-10-13, #203)
- value proven by: a finding with sources on what the chain needs per platform: the pin header, the app-only binary that Wokwi takes, the merged image for deploy
- depends on: Q15
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P218 (#200)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## Later (new) — all the journeys, steps and options interconnected on one huge board
- type: an idea for later, new
- needed by: "I would like if somehow in the end all the user journeys and the steps and options and such were realy interconnected on one huge board, but that's just an idea for later, now let's just do the first versions, then we can experiment." (the PO, 2026-10-13, this session)
- value proven by: — (set when the PO starts it)
- depends on: the first version of the Miro board (D9)
- status: proposed, later
- label (the repository's type label): —
- parent (the epic, as a sub-issue): P218 (#200), or the PO's call
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Q22)

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- none taken. Filing and card edits wait on the PO's yes to this list (a D that names items.md) <!-- REQUIRED:board-actions -->
