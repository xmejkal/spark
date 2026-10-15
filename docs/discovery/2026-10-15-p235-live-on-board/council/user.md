# User lens report, P235 live on the board

Tags: E has a pointer, H says its source, D says who and when. — is an unknown. Paths: OBS is docs/observations/. BL is
~/Development/blink-c6/firmware/blink.py. BTN is ~/Development/button-light/firmware/light.py. P218J is
docs/discovery/2026-10-13-p218-deploy-and-board/jobs-and-journeys.md. All evidence is n = 1: the PO, one XIAO ESP32-C6, one Mac.

## Findings

### Findings list

- USR-1 · Today the only live path on the running board is `mpremote ... repl`, run by the PO in his own terminal, or Claude's one-off pyserial script. spark has no command for either. · E · journey.md:1102-1105 (the `repl` line and its keys), OBS/2026-10-14-p236-bench.md:24-25 (Claude sent `200`, board answered `period 200 ms`) · supports: Job 1, Job 2, Job 4 start state
- USR-2 · Both bench firmwares end in a loop that never returns, started from main.py. The REPL only appears after Ctrl-C stops the gadget. Every live look therefore stops the thing he is watching. D29 ends each try with a reset, so the gadget restarts. · E · BL:70-81 (`run()` never returns), journey.md:1102-1104 (Ctrl-C stops, Ctrl-D starts), P218J UC7 step 7 · supports: Jobs 1, 3, 4 (a try is never "alongside" the gadget)
- USR-3 · Ctrl-C only works if the firmware reads its console. button-light did not, so mpremote failed with "could not enter raw repl" on four runs (10-14 to 10-15 02:00). The fix was three lines in the firmware that read and drop console input. The consequence for a live REPL: any firmware the conversation writes without that loop cannot be entered at all. · E · OBS/2026-10-15-p215-bench-rerun.md:22-33, INDEX AT176, AT177, OBS/2026-10-14-p238-spike/finding.md:7-13 · supports: Job 1 and Job 4 need a rule on firmware, not only a command
- USR-4 · In button-light the loop drops every typed byte (`sys.stdin.read(1)` and discard). A line typed to this firmware goes nowhere. In blink-c6 it changes the period. So "send it a line and see its answer" works with one bench project and not the other. · E · BTN:51-53 against BL:75-79; OBS/2026-10-14-p236-bench.md:24-25 · supports: Job 1 (the P235 evidence for it is one firmware that was written for it)
- USR-5 · Opening the serial port can restart the XIAO C6. Round 1 of P238 saw 0 restarts in 4 opens. Round 2 saw restarts in 15 of 15. The 10-15 02:00 probe saw one. macOS also dropped the device ("Device not configured") during resets with the port open. A serial monitor or any "just listen" tool may reset the board on attach and miss the boot text it was started for. · E · OBS/2026-10-14-p238-spike/finding.md:16-17 (round 1), finding.md round 2 item 4, OBS/2026-10-14-p215-bench.md:24-25, INDEX AT161, AT178 · supports: Job 2 (a monitor changes what it watches), Job 4
- USR-6 · One program holds the port at a time. While the PO's mpremote held it, esptool failed with "Could not exclusively lock port", and one esptool reset froze his mpremote session. A live session by Claude and a REPL by the PO cannot run together. · E · OBS/2026-10-14-p238-spike/finding.md round 2 item 5; P218J UC7 step 3 ("close your own REPL") · supports: Jobs 1, 2, 4 (who owns the port)
- USR-7 · The board can sit silent in the ROM download mode and look dead. A press of R fixes it, but only when the PO knows to press it. The word `waiting for download` was seen only by Claude's own port listen. deploy.py now detects it and asks for R. A live session or monitor has no such detection yet. · E · OBS/2026-10-14-p236-bench.md:15-23, OBS/2026-10-14-p243-bench.md:19-28, INDEX AT157, AT165 · supports: Job 2 (a monitor must tell silent from download mode)
- USR-8 · What the PO supplied at the bench so far: presses of R and B, replug of the USB cable, typing `yes` in his own terminal, running commands in his own terminal, watching the LED, saying what he saw. What he said he cannot supply: wires ("i dont have any cablues"). · E · OBS/2026-10-14-p236-bench.md:15-17 (R and B pressed, eleven port drops), OBS/2026-10-15-p215-bench-rerun.md:34-35, issue #260 body · supports: Job 3 (no wires means no jumper test, so no live pin read can be checked against a known signal)
- USR-9 · Claude's chat has no tty. The yes gate is `isatty` on stdin and stdout. A pipe fails it. A pseudo-terminal passes it, and Claude Code's auto mode refused a probe that faked one ("Security Weaken"). So Claude cannot type the yes, and `!` commands in the chat are not a terminal for it either. A live session's one yes (D29, D43) has to come from the PO's own terminal. · E · scripts/deploy_gate.py:42, OBS/2026-10-15-p215-bench-rerun.md:12-14, INDEX AT172 · supports: Job 4 (the session yes), D43
- USR-10 · Issue #249 (P242) asks for a standing yes per board, kept in his store. The PO said "yes to p242" and ordered it after the P238 fix. It sits in P218's epic, not P235. If P235's live session needs a yes each session (D29), the two decisions touch the same gate. · E · gh issue view 249 (comments, 2026-10-14) · supports: order of P235 against P242
- USR-11 · Claude's current way to talk to a running board is by hand: open the port with pyserial (DTR and RTS off), listen, write a line. It is not a spark command, leaves no log in the board log, and each script chose its own timing and line settings. The guide says "Never run mpremote by hand to turn an unknown into a pass." Claude did it anyway at the bench, to find the cause, not to pass. · E · OBS/2026-10-14-p236-bench.md:19-25, OBS/2026-10-15-p215-bench-rerun.md:26-29, docs/guide/agents.md:580 · supports: Job 4 (the agent guesses its timings and has no named rule for live use)
- USR-12 · Claude guessed or got wrong inputs at the bench at least twice. It gave `SPARK_HOME` as the repo, and spark refused to write inside a git work tree. It also tried to fake a terminal for the yes. Two ordinary agent misses in one session. A live board adds a third kind: driving a wrong pin. · E · OBS/2026-10-15-p215-bench-rerun.md:8-9, 12-14 · supports: Job 4 (a guard is needed on what Claude may drive)
- USR-13 · Pin harm is real in this repo. A signal named ONBOARD_LED got a second line that shadowed it, and the firmware drove the board's LED instead (caught in review, PR #246). A live `Pin(n, Pin.OUT)` from Claude has no such review. pins.py holds no direction (P218J D29 note, ★C16). The XIAO's USB data pins and strap pins are on the same header. · E · INDEX AT150, P218J UC7 step 5 · supports: Job 3, Job 4 (a name-and-number rule before a pin is driven)
- USR-14 · Output the computer does not take within 200 ms is dropped by MicroPython on this port. A monitor started after boot sees no boot text, and one that reads slowly loses lines. `ready` can be lost before the port opens. · E · OBS/2026-10-14-p238-spike/finding.md:14-15, INDEX AT138, P218J UC1 step 5 · supports: Job 2 (a monitor must be running before the reset to be trusted)
- USR-15 · "Ready" is one word read once. After a pass, a bare board with an external LED shows nothing. deploy.py does not say so. The PO reported it. For a live session this means a "works" from the console alone may not match what he sees. · E · INDEX AT179, OBS/2026-10-15-p215-bench-rerun.md:33-35 · supports: Jobs 2 and 3 (what proves a live try worked)
- USR-16 · The port name changed across runs: `/dev/cu.usbmodem101` on 10-14, `/dev/cu.usbmodem1101` on 10-15. A monitor or session that stored the name will point at nothing after a replug or a reset that drops the device. · E · OBS/2026-10-14-p215-bench.md:5, OBS/2026-10-15-p215-bench-rerun.md:3 · supports: Job 2
- USR-17 · The cause of the repeated "could not enter raw repl" is still not fully known. Round 1 found a full input buffer. At 02:00 the buffer was empty after a restart and Ctrl-C still got nothing. Round 2 found download mode and port holds. Nobody measured the rate of each sequence ("20 tries per row" was proposed, not run). A live REPL built on mpremote inherits this unknown. · E · OBS/2026-10-14-p238-spike/finding.md (what this means, item 4), INDEX AT176, OBS/2026-10-15-p215-bench-rerun.md:26-29 · supports: whether P222 or a spike runs before a build (the user lens only reports that the unknown stands)
- USR-18 · There is no failure the PO has met that is specific to WebREPL or OTA. He has never run either. Wi-Fi is not in any bench log. · E · absence in all four bench logs and AT131 to AT180 (read in full, no hit for WebREPL or OTA) · supports: later slices, no account exists for them
- USR-19 · What the PO himself did live today is a typed number into the blink console, and he did it with `mpremote repl` from his terminal, per the docs. The jobs file ties Job 1 to "the PO runs mpremote repl". I found no bench log in which the PO ran his own REPL session. The one live exchange recorded was Claude's `200`. · E · OBS/2026-10-14-p236-bench.md:24-25 (Claude sent `200`); the memory line "PO trying live REPL now (mpremote repl)" is cited by the jobs file and was not available to me as a log · supports: care with Job 1's "today" cell (D or an account is needed)
- USR-20 · Debugging (Job 3) has no run at all. The jumper test was not run because he has no wires. Job 3's evidence is a wish ("debugging maybe?") and a missing test. No fault was found with a live read on this board, so nobody knows which reads he would want. · E · OBS/2026-10-15-p215-bench-rerun.md:34-35, issue #224 body · supports: Job 3 is the least evidenced job

### Journey: Job 1, try a change live

Start state: the firmware is flashed, `ready seen`, on a XIAO C6 on a Mac. Evidence is the blink-c6 run unless marked.

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | Finds the port name | E OBS/p243-bench.md:6, `mpremote devs` named in the deploy sentence | Name changed between days (101, then 1101) | works, by hand |
| 2 | Makes sure no other program holds the port | E finding.md round 2 item 5 | A held port freezes esptool or mpremote. No tool names the holder | partly |
| 3 | Runs `python3 -m mpremote connect <port> repl` in his own terminal | E journey.md:1102 | Needs the right path, the module form, and the port name typed | works |
| 4 | Types `200` and Enter | E p236-bench.md:24-25, BL:75-79 | Works only because blink reads input. In button-light the byte is dropped | works for blink-c6 only |
| 5 | Wants to run a line of Python, not feed the firmware | H none found | Needs Ctrl-C first, which stops the gadget. Needs the firmware to read its console | partly |
| 6 | Leaves with Ctrl-] and restarts the gadget with Ctrl-D or a reset | E journey.md:1103-1104 | A tuned period is lost at restart. What stays changed is not listed | works |
| 7 | Turns what he learned into firmware | D AGENTS.md "spark exports facts, never behaviour" | Nothing carries the tried value into a file | not yet |

### Journey: Job 2, see what the board says

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | Wants to see the console after a flash or on a fault | E p236-bench.md:4-6 | He cannot read it himself. The words `waiting for download` came only from Claude's script | partly |
| 2 | Opens a monitor (mpremote repl, screen, Thonny) | H none for the PO's choice | Opening the port can restart the C6 (AT161, AT178) and can drop the macOS device | partly |
| 3 | Reads boot text and `ready` | E p243-bench.md:19-24 | Output is dropped after 200 ms of no reader. A late monitor misses the boot | partly |
| 4 | Silent board | E p236-bench.md:4, AT157 | Silence can be download mode, a firmware that is stuck, or a held port. Nothing tells them apart outside deploy.py | partly (deploy only) |
| 5 | Presses R | E p243-bench.md:9, AT165 | He must know where R is. The board record lacks the place (AT158). Docs now say the top corners | works |
| 6 | Replugs the cable | E p215-bench.md:19-21 | A replug did not bring the console back at once. The cause is unknown (AT133) | partly |
| 7 | Decides pass or fail from the text | E AT179 | A bare board shows nothing when the firmware drives external parts | partly |

### Journey: Job 3, find a fault on the board

| step | what he does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | The part does not answer (button-light with no wires) | E p215-bench-rerun.md:34-35 | He has no wires, so he cannot test the signal | not yet |
| 2 | Asks Claude what the pin reads | H P218J UC7 step 1 | Claude must stop the firmware to read it. A `Pin(n, Pin.IN)` can change a pin the firmware set as output | not yet |
| 3 | Claude names the pin by name and number | E P218J UC7 step 5, AT150 | pins.py holds no direction. Strap and USB pins can be hit | not yet |
| 4 | Presses the button or moves a wire while Claude reads | H P218J UC7 step 6 | He must be told when. Claude cannot see his hand | not yet |
| 5 | Compares the read with the diagram | E OBS/p215-bench-rerun.md:34 | The XIAO has one LED he can see and no wired parts, so the check is weak | not yet |
| 6 | Learns wire, part or code | H none | No run exists, so this step has no evidence | — |

### Journey: Job 4, let the agent test the real board

| step | what Claude does | evidence | friction or harm | today |
| --- | --- | --- | --- | --- |
| 1 | Writes firmware in the conversation | E AGENTS.md | The firmware must read its console or nothing later works (AT177) | works |
| 2 | Looks, then deploys with the PO's yes in his terminal | E deploy_gate.py:42, AT172 | Claude has no tty and cannot type the yes. Fake-tty probe refused | works with the PO's hands |
| 3 | Gets one word, `ready` | E p215-bench-rerun.md:33 | It tells that the loop started. It tells nothing of pins, sensors or timing | works, thin |
| 4 | Wants to run a small try | E P218J UC7 step 5 | No command. Claude writes pyserial by hand and picks DTR, RTS and timings by guess | not yet |
| 5 | Gets a result and decides whether to trust it | H P218J UC7 | The simulation gate has no board counterpart. Only Claude reads the answer | not yet |
| 6 | Resets and frees the port | D D29 (PO, 2026-10-13) | The PO may have his own REPL open. A freed port is not announced | not yet |
| 7 | Reports and does not turn a try into firmware by itself | E AGENTS.md | The line between a fact learned and behaviour is a rule, not a check | partly |

## What you could not check, and why

- The PO's own live REPL sessions. No bench log records one, and the memory line cited by jobs-and-journeys.md was not given to me as a file. Job 1's "today" for him is therefore an account question.
- Whether `mpremote repl` in the PO's terminal ever stalled for him. The logs record Claude's stalls and the deploy ones. They do not record his REPL ones.
- How often a port open restarts the C6. Round 1 saw none in 4 opens. Round 2 saw it in 15 of 15 and 02:00 saw one. The rate with and without DTR and RTS off is not measured.
- Anything on Linux, Windows or another board. The only board is one XIAO C6 on one Mac. The earlier FireBeetle S3 had no run.
- Wi-Fi, WebREPL and OTA. No run exists.
- The Miro journey board, the #224 page on the board, and the memory directory. I did not open them. The Miro board has no tool allowed for this lens.
- Whether the ~/Development/button-light and blink-c6 firmwares on disk match what was flashed at each bench time. I read the files as they are today.
- `scripts/` beyond deploy_gate.py:42 and the deploy.py grep. I did not read the live-session code paths, since none exist as far as the guide says.

## Questions for the decider

Account questions are past-tense questions about his own use. The answer is E, account, n = 1.

1. (account) Did you ever run `mpremote repl` or another REPL on the XIAO yourself, outside a Claude-driven run? What did you type, and what went wrong? · decides: Job 1's "today" cell and whether a spark REPL command saves him anything
2. (account) When you had the REPL open, did you ever want to run a line of Python and find that Ctrl-C stopped your gadget first? What did you do next? · decides: whether a live session must keep the firmware running (USR-2)
3. (account) Did another program ever hold the port when you wanted it (esptool against your mpremote, a Claude script against your REPL)? How did you find out, and how did you free it? · decides: port ownership in a session (USR-6)
4. (account) When the board was silent after a flash or a replug, how did you tell download mode from a dead firmware, before Claude read `waiting for download`? · decides: whether a monitor must report the mode (USR-7)
5. (account) Have you watched the serial output on a screen, other than through deploy.py or Claude's script? Which tool, and what did you miss or lose, for example the boot text? · decides: Job 2's first slice and whether a monitor must start before a reset (USR-5, USR-14)
6. (account) After pressing R or replugging the cable, did you ever need to look for the port name again? When did it change? · decides: whether the session finds the port by itself (USR-16)
7. (account) When Claude read the board for you, did you ever not trust the answer? What would have made you trust it, for example a log you could read after? · decides: Job 4 and what a try must log (USR-11)
8. (account) Did Claude ever drive or read a pin on your board that you did not expect? Did the LED, a strap pin or the USB lines react? · decides: whether a pin guard comes before any live try (USR-13)
9. (account) When the button-light pass showed nothing, what did you want to see on the board or in the console? · decides: what a live read must show for Job 3 (USR-15, USR-20)
10. (account) Did you ever want to change a value on the running gadget and keep it, for example the blink period, and lose it at the next reset? What did you do? · decides: whether a try can leave a fact for the conversation (USR-1, step 7 of Job 1)
11. (account) Did you ever type the yes for Claude, or want to? How many times a session was it too much? · decides: whether one yes per session (D29) is the right count, and the order against P242 (USR-9, USR-10)
12. (decision) Does the rule "the firmware must read its console" become a stated spark rule before any live REPL is built, since nothing enters a firmware that does not? · decides: the first slice's scope (USR-3, USR-4)
13. (decision) Does P222 run before the first build, given that the cause of the failed Ctrl-C and the rate of port-open restarts are not measured? · decides: the order (USR-5, USR-17)
14. (decision) Is P246's board-only project a project of its own that reads console input and changes something you can see, or is blink-c6 enough? · decides: what the bench shows for a first slice without wires (USR-8, USR-20)

## Searches

none
