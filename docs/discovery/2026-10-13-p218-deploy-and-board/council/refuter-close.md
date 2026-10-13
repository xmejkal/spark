# P218 council: the refuter, closing pass

Second pass, 2026-10-13, on the sections changed after `council/refuter.md` (`git diff 93167a1..HEAD`). Read:
verification.md, brief.md (What we found, Options, No-gos, Riskiest, Hand-off, D16 to D40), items.md, story-map.md,
jobs-and-journeys.md, risks-and-tests.md, and two sources (`commands/build.md:120`, `scripts/assign_pins.py:411`).
Nothing was flashed, erased, installed or simulated. Line numbers are this branch at 34418c4.

## 1. verification.md against my verdicts, and the ★ rewrites against their sources

Verdicts: 24 of 24 ★ rows carry my verdict word faithfully. One row adds a false note, and 3 rows count my read as
their own reproduction.

- verification.md:12 (★C2): "The quoted permission sentence moved, and the refuter's line was not found again at `:120`".
  False. `commands/build.md:120` still reads: "Claude Code asks before it runs (unless the person's own settings
  already let it run: an allow rule of theirs, or auto mode), and the person's answer there is the yes." Edit: delete
  the sentence.
- verification.md:24 (★C14), :27 (★C17), :18 (★C8's mpremote half): "not repeated, the refuter's read stands" and
  "The mpremote line is the refuter's read, not repeated", each with "result: reproduced". One reader is not a
  reproduction. Edit: "result: not reproduced (the refuter's read only)".

Rewrites: 20 of 24 claim no more than their source. 3 claim more, and 1 has a stale pointer.

- brief.md:51 (★C6): "caveat: octal needs SPIRAM_OCT, so the N16R8's PSRAM is unused on Standard". The page says only
  that an octal board needs the "spiram-oct" variant. It does not say what Standard does then. The kept image holds
  "PSRAM chip is not connected, or wrong PSRAM line mode", which can be an error, not an unused PSRAM. Edit: "so what
  Standard does with the N16R8's octal PSRAM is H".
- brief.md:58 (★C13): "WebREPL starts from boot code with one password on all interfaces. mpremote cannot drive it, and
  `webrepl_cli.py` only gets and puts files · E". verification.md:23 reproduced only the start and the password call,
  and "`webrepl_cli.py` stay[s] as TLJ-34 read them", with keep: none. Edit: tag "one password on all interfaces" and
  the `webrepl_cli.py` clause H (TLJ-34), and set keep: "webrepl_cli.py not re-read".
- brief.md:53 (★C8): "esptool ends with a hard reset (v3.3 default)". The pointer is 5.5.0's `__init__.py:432`. Edit:
  "(the default in 3.3 and 5.5.0)".
- brief.md:61 (★C16): "E `scripts/assign_pins.py:410`". The line is now `:411` (verification.md:26 says so). Edit: `:411`.

Also stale against D15 (not ★): brief.md:63 [C18] "This Mac's esptool is v3.3, not the pinned 5.5.0", and brief.md:191
[C30] "so this Mac runs v3.3". D15 reads "taken: `python3 -m esptool version` printed `5.5.0`". Edit both to "ran
v3.3 until D15". risks-and-tests.md:38 A4 "E ★C19: shown only with a fake run" contradicts ★C19 itself ("No test
exercises a refusal"). Edit: "E ★C19: no test exercises a refusal". risks-and-tests.md:9 still reads "E ★C21: J1 is the
one job with a blocked person", the clause ★C21 now marks refuted. Edit: "★C21: J1 and J3 both block the PO".
The first pass's changes to jobs-and-journeys J3, J7, UC1 and UC3 were not applied: :31 "tested only with a fake
`run`", :35 "erases the first board it reaches", :113 "A2: does `os.statvfs('/')` show 512 blocks?", :196 "partly
(esptool refuses in a test with a fake run only)". Edit them as ★C19, ★C1 and ★C5 now read.

## 2. Places that contradict D16 to D40

29 places. In each, the edit is the smallest one that makes it agree.

Brief.
- brief.md:12 "**Decision needed:** Q1, the importance of each assumption and the pass lines". D16 answered Q1. Edit: "the PO's confirmation of the jobs, a direction and the remaining risk".
- brief.md:209 "Q24 is next". D12 answered Q24 and the queue is empty. Edit: "The queue is empty".
- brief.md:99 "No-go: a write to the first port found (`mpremote connect auto`, esptool's port search)". D25 lets spark pick the one board. Edit: "a write to a port the look did not read".
- brief.md:108 and risks-and-tests.md:41 (A7), adopted by D16: "Against a scratch copy changed to the N4, they read "flash differs"". The bench board is the XIAO ESP32-C6 (D14). Compared with an S3 N4 record, it reads "chip differs". Edit: "Against a scratch copy of the XIAO ESP32-C6 record with its flash size changed".

items.md.
- items.md:10 "Slice names are the board's Slice options", with :61, :71, :81, :91, :101, :111, :121, :131, :141 "ask the decider for a new one (Q22)". D39 says there is no Slice field. Edit: "placed when filed (D39)".
- items.md:15 (P228): "a read with `--chip esp32c6`". With a C6 board at the bench (D14), that read tests no refusal. Edit: `--chip esp32s3`. The same applies to risks-and-tests.md:38 (A4) "`esptool --chip esp32c6 flash-id` against the S3" and story-map.md:24.
- items.md:26 (P219, first story): "with no port, deploy refuses and lists the ports". This contradicts D25. Edit: "with two or more boards and no port, deploy refuses and lists them. With one board, it picks that board after the look".
- items.md:26-27 do not name D19's terminal yes before a first erase, D24's warning on an unknown field, or D37's look as its own command. Edit: add "The look is its own read-only command (D37). An unknown field needs the person's yes in the terminal (D24). A first erase asks in the terminal (D19)". Change "Q3 and Q7" to "D19 and D24".
- items.md:36 (P215): "prints `ready` in a log that a command read". D33 also asks that the board's files match the per-file hashes. Edit: add "and the board's files match the passed log's per-file hashes (D33, D20)".
- items.md:63 (P219, second story): "offers stop, migrate, a general record or go ahead". D27 says migrate first. Edit: "offers migrate first, then a metered run (D27). Another chip stops (D24)". At :67, change "Q7, Q10 and Q19" to "D24, D27, D36".
- items.md:76-77 (P232): "the core refuses until one is named … Q6 and Q21". D38 says a blink ends the case, and that its item names the exception. Edit: add "When the person cannot tell them apart, spark blinks one board's LED. This is the exception to "Spark exports facts, never behaviour" (D38)".
- items.md:87 and :91 (P233): "depends on: A3's result at P215's bench. Q11" and "If A3 fails at the bench, v1". D28 waits for a project that needs PSRAM, and D16 rates A3 low until the S3 is found. Edit: "depends on: a project that needs the PSRAM (D28)". Drop the v1 clause.
- items.md:96 (P222): "Live tries over USB with classes" contradicts D29 (free `exec`, one yes per session, a reset after each try). "The Wi-Fi REPL's facts (★C13)" contradicts D31 (a later epic, P235). Edit: "free `exec` after one yes per session, each try ending with a reset (D29)", and move the Wi-Fi REPL to P235.
- items.md:106-107 (P234): "`deploy.py --check` prints …" and "depends on: Q5". D37 makes the look its own command, and D22 copies the file after the flash. Edit: "the look command (D37) prints …" and "depends on: D22".
- items.md:123 and :127 (P221): "the spike waits on the not-goal question" and "depends on: Q15". D32 lifted the not-goal for the reading. Edit: "the not-goal lifts for this reading (D32)".

story-map.md.
- story-map.md:25: "needs a named port before any write. It never takes the first port found". This contradicts D25. Use the same edit as items.md:26.
- story-map.md:27: "(Q3 and Q9 decide where it lands)". Edit: "(D19: a token and a terminal yes. D26: the order)".
- story-map.md:29: the proof lacks the hashes. Edit: add "the files match the per-file hashes (D33)".
- story-map.md:32: "offer stop, migrate, a general record or go ahead". This contradicts D27. Use the items.md:63 edit.
- story-map.md:33: no blink. Use the P232 edit (D38).
- story-map.md:34 "new (Q11, after A3)" and :55 "If the PO adds a Slice option to the board (Q22)". These contradict D28 and D39. Edit: "new, when a project needs PSRAM (D28)", and delete :55-57.
- story-map.md:35 "with per-file hashes in the passed log or a labelled untested path". D20 chose per-file hashes. Edit: delete "or a labelled untested path".
- story-map.md:36 "classed tries" and :83 `live["live session: classed tries"]`. These contradict D29. Edit: "free `exec`, one yes per session, a reset after each try".
- story-map.md:41-44 "most of the PO's deploys go to his one known board … That split is part of Q9". This contradicts D13 and D26. Edit: "D26 set the order: P228, P219's first story, P215, P213".

jobs-and-journeys.md.
- :67 G2 "Person: names the port when two or more are listed. spark and Claude never choose". This contradicts D25. Edit: "With one board, spark picks it after the look. With two or more, the person names one (D25)".
- :59 "classed tries in a session" and :277 UC7 step 5 "before each try, its class (read, read that drives, write)". These contradict D29. At :280, UC7 step 7 resets once at the end, where D29 resets after each try. Edit: "free `exec` after one yes", and "resets after each try".
- :138 UC-K step 6 "the yes, as Q2 decides (H1 …, H2 …, H3 …)". Edit: "a remembered yes per board, asked again on a difference, an unknown or lost data (D18)".
- :136 "Q5: a marker on the board?". Edit: "the facts file, read back (D22)".
- :179 UC2 step 4 "offers four choices. Stop. Migrate … Go ahead", and the :189 branch "go ahead". These contradict D27. Edit: put migrate first, then a metered run.
- :235 UC-T step 3 "names the target, or unplugs the other one", and :244 `p3["P: name one, or unplug the other"]`. D38 chose the blink. Edit: "names the target, or spark blinks one board's LED (D38)".
- :256 UC6 step 3 "or the person says "untested"". This contradicts D20. Edit: delete it. Change :251 "(waits on Q4)" to "(D20)".

risks-and-tests.md.
- :10 "answers the account questions (Q23)" and :57 "as the PO chooses". D40 says that the account questions wait for P228's bench. Edit both to the D40 wording.
- :12 "Q4's answer on the update gate" and :13 "then the PO's answers to Q2 and Q3". Edit: "D20" and "D18, D19".
- :39 A5 "of the N16R8 … H for 5.5.0". The bench board is the C6 (D14, D16 rates A5 medium), and verification.md:13 read 5.5.0. Edit: "of the bench board (D14) … E for 5.5.0's source".
- :42 A8's change, "the yes must come from the person's own terminal (Q3 option a)". D19 already has the terminal. Edit: "every erase, not only the first, asks in the terminal".
- :43 A9's change, "the known board also needs the board's files or a marker read (Q5)". Edit: "the facts file (D22) is read before every write".
- :51-55 Collection plan: "Q1 … next" (D16), "on the N16R8" (D14), and "Q7, Q10, Q19", "Q11, Q16", "Q3" (D24, D27, D36, D28, D33, D19). Edit: mark Q1 done, and replace each Q with its D.

## 3. Decisions that conflict with each other or with AGENTS.md

8 conflicts, said plainly. The PO made the decisions.

1. D38 against AGENTS.md: "Spark exports facts, never behaviour. … never thresholds, timings, state tables or drivers."
   A blink is code that spark writes and runs on the board. D38 names the exception itself.
2. D26 against D14, D24 and D28. The ladder puts P215's flash right after P219's first story. The only board at hand
   is a C6 (D13, D14). The project's image is for the S3. "another chip is always a stop" (D24). "The C6 build comes
   with the C6 migration" (D28), and `data/tools.json` has no C6 interpreter (★C20). D27 migrates only the same chip.
   So no card before P215 makes an image for the C6 board.
3. D33 against D26. "ready seen" needs the files to match the per-file hashes (D20). No card before P215 changes the
   log so that it names per-file hashes, so P215 cannot pass D33's line as ordered.
4. D34 against D22 and the order. A backup is offered "only when the look finds firmware spark did not put there (no
   facts file, D22)". The facts file is P234 (slice 5), after P215. Until then no board has one, so every board reads as
   other firmware, and spark offers a backup each time. The PO declined "always".
5. D22 against D20. D22 copies the facts file after the flash "so the image stays the one that passed". D20 lets an
   update copy "only files that a passed run names". A file written at deploy time is named by no passed run unless
   the simulation also ran with it. D22's own caveat says the log must name it.
6. D29 against D4 and D19. With free `exec` after one yes per session, Claude can delete or overwrite the board's
   files with no look-bound token and no terminal yes. D4 says "never erases or writes a board it did not check, and
   never without the person's yes". D29 does not say whether its one yes goes through D19's token and terminal.
7. D19 and D18 against D4, through an interface with no terminal. The terminal prompt sits in the CLI (D19's caveat),
   Claude can copy the token (★C10), and a remembered yes skips later prompts (D18). An MCP or web path has no
   person-only gate, while D8 asks for those interfaces.
8. D35 against D23. `requirements.json`'s `board` names a board type (a record such as `xiao-esp32-c6`). D23 keeps
   "one record per physical board" and says "the project names the board it targets". The decisions do not say whether
   the project names the type or the physical board, which is the MAC.

## Searches

None
