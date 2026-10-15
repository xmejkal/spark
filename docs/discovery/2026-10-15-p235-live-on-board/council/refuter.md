# P235 live on the board: the refuter's report

Read 2026-10-15 by the refuter. I opened no serial port and ran nothing against a board. I ran `mpremote --version`,
`python3 -m mpremote connect --help`, `pip show mpremote` and `gh issue view`. I read mpremote 1.29.0 as installed. I
decide nothing. OBS is docs/observations/. P218B is docs/discovery/2026-10-13-p218-deploy-and-board/brief.md.

Check first, for an existing product. Does the change address the observed problem, and what breaks for current users?

- The request has two parts. The PO asked to review the options for the REPL, WebREPL, live code, a serial monitor and
  debugging. He also asked to "move all related stories there" and "update all journeys and use cases and story maps".
  #224's own body names P218's journeys J4 and J6 and the deploy map's slices 4 and 6 as belonging here. The folder
  never names J4, J6 or those slices. story-map.md says "The journey table in the same file gains nothing". So the
  second half of the request is not addressed, and the brief does not say it is left out.
- The observed problem the brief builds on is reach (★C3, A1). Most of the logged reach failures have a known cause.
  Spark has acted on each cause. P243 handles download mode after a manual BOOT press (AT165). P245 handles mpremote
  asking too early after a reset (AT173 "acted"). agents.md:577-578 handles a firmware that never reads its console
  (AT177 "acted"). One
  failure (02:00 on 10-15) stays unexplained. The brief treats reach as open "today" and makes it the riskiest
  assumption. It does not show that the open part is larger than that one run.
- What can break for the one current user:
  - The deploy gate. `require_open_gate` hard-codes the erase question and the image half of the token
    (scripts/deploy_gate.py:49-68). Option Q2 A changes it. The frame's "must not get worse" names this gate.
  - The "yes only in my own terminal" property. A stored grant (Q6 A, B) lets Claude act with no terminal yes. AT172
    and the P215 re-run record that this property is what stopped a faked terminal.
  - The port. A live session holds the one port, so look.py, deploy.py and the PO's own `mpremote repl` cannot run at
    the same time (finding.md round 2 item 5).
  - The board state after a try. `run_code` stops the firmware, and TL-4 says the firmware does not restart until
    something resets the board. The store record can still say `ready seen` while the gadget no longer runs.
  - D33's match. A `fs cp` breaks it (★C8). A `run` does not.
  - The agents.md rule at line 580 ("Never run mpremote by hand to turn an unknown into a pass"). A live command needs
    new words there.

## 1. The ★ claims against their sources

- ★C1 · holds · scripts/board_connection.py:52-63, read: "What the board printed while it ran `code`. With
  `keep_running_for` seconds, code that still runs then is left running, and what it printed until then is the answer.
  Without it, no answer in timeout_s is BoardUnreachableError." and line 85 `raise BoardUnreachableError(_last_line(err)
  or _last_line(out) ...`, line 84 `raise BoardCodeError(out, failed.returncode)`. tests/fakes.py:4 `class
  FakeBoardConnection:` and :18 `def run_code(self, code, keep_running_for=None):`. The claim holds. It drops one fact
  that matters for a live try: a try that runs longer than 20 s with no `keep_running_for` is reported as
  `BoardUnreachableError("no answer in 20 s")`, which is mpremote's failure in name only. A loop in a live try is then
  labelled "not reached".

- ★C2 · partly · OBS/2026-10-14-p238-spike/finding.md:9: "One cause is proven: when MicroPython's input buffer is full,
  a Ctrl-C never gets through." OBS/2026-10-15-p215-bench-rerun.md:27-28: "The input buffer was empty after that
  restart, so a full buffer (P238's proven cause) does not explain it." and :31-33: "With the PO's yes, its loop now
  reads the console without waiting and drops what it reads ... at 02:10 deploy.py printed `ready seen`". The
  first sentence holds. The second sentence ("button-light gave 'could not enter raw repl' until three lines ... were
  added") states a cause from one run after the change. That run was also a fresh flash with P245's second read, so
  the change is confounded. The edit in ~/Development/button-light/firmware/light.py is four lines (40-41 and 45-46),
  not three. Change to: "button-light gave 'could not enter raw repl' at 02:00. After its loop was changed to read and
  drop console input, one fresh deploy at 02:10 gave `ready seen`. One run, with a fresh flash, so the change is not
  shown to be the cause."

- ★C3 · partly · OBS/2026-10-15-p215-bench-rerun.md:5: "mpremote then got no bytes ("could not enter raw repl")",
  :19-20 for run 2: "mpremote had asked while the board still restarted after esptool's reset", :24-25 for run 3:
  "mpremote still said "could not enter raw repl"". INDEX AT173: "mpremote asks too early after the reset ... **acted**
  ... P245". OBS/2026-10-14-p236-bench.md:39: "Each time it happened, the chip was already in download mode before
  esptool ran". Run 2 does not quote the words, and its cause is known and fixed (P245). The P236 failures were
  download mode after a manual BOOT press, which P243 now handles. After those fixes the logs show run 4 at 02:10
  `ready seen`, and blink-c6's deploys at 14:03 and 14:12 `ready seen`. So "does not reach this C6 every time
  today" rests on failures that mostly predate fixes. Change to: "mpremote failed to reach this C6 in runs 1 to 3 of
  the P215 re-run and in the first P236 deploy. Two causes are known and acted on (P243 download mode, P245 early
  ask). One failure, at 02:00, is unexplained. The logs record one deploy since the fixes. It reached the board."

- ★C4 · holds · mpremote main.py:536 `self._auto_soft_reset = True`, :550-553 `soft_reset = self._auto_soft_reset if
  soft_reset is None else soft_reset` / `if soft_reset or not self.transport.in_raw_repl:` /
  `self.transport.enter_raw_repl(soft_reset=soft_reset)`. commands.py:530-531 `def do_resume(state, _args=None):` /
  `state._auto_soft_reset = False`. commands.py:483 (`_do_execbuffer`) and :381 (`do_filesystem`) call
  `state.ensure_raw_repl()`. main.py:304 `"resume a previous mpremote session (will not auto soft-reset)"`. The caveat
  that `resume` keeps values is correctly marked H.

- ★C5 · partly · scripts/deploy_gate.py:42 `if not (self.stdin.isatty() and self.stdout.isatty()):`, :64 `question =
  "erase ALL of this board's flash and write %s?" % image`. OBS/2026-10-15-p215-bench-rerun.md:12-14: "A probe that
  fakes a terminal was refused by Claude Code's auto mode ("Security Weaken")". #249 comment: "The PO, 2026-10-14:
  "yes to p242": the shape is a standing yes per board (by its MAC)". The facts hold. "A live session of several CLI
  calls needs a stored grant" is a design inference written as fact. The folder's own Option Q6 C needs no grant. In
  it, the PO runs the live command in his terminal. A long-lived process started in his terminal is another way. "Claude's
  chat has no tty" has no direct source. Change to: "Claude runs each try as a separate CLI call. Then the yes must stay
  somewhere between calls, for example in a stored grant like P242's standing yes. Other shapes exist (Q6 C)."

- ★C6 · partly, close to refuted for one number · OBS/2026-10-14-p238-spike/finding.md:21: "Bench: opening the port
  does not restart the board (4 opens, no boot text). The suspect is ruled out." :55-57: "A script ran `esptool
  chip-id` and then opened the port with DTR and RTS off, read 4 s and sent Enter. Three runs from the running
  firmware, and three pairs of `--after no-reset` then a normal reset: all 15 reads show the ROM boot lines, then
  `ready`. Even after `--after no-reset`, the chip restarted, so opening the port restarted it." :20: "output that the
  computer does not take within 200 ms is dropped." Each of the 15 reads came right after an esptool run, and most of
  those runs ended with esptool's own hard reset. Only the `--after no-reset` rows isolate the open. The source does not
  say how many of the 15 those were. So "a restart in 15 of 15 [opens] in round 2" is stronger than the source. Change
  to: "No restart in 4 opens in P238 round 1. In round 2, opens right after `esptool --after no-reset` still showed a
  boot. In those rows the open restarted the chip. Their count is not given. One open at 02:00 on 10-15 restarted
  the chip."

- ★C7 · holds for the pins, H part correctly marked · re-read through the Espressif docs MCP (see Searches). ESP-IDF
  esp32c6 gpio.html: "USB-JTAG: GPIO12 and GPIO13 are used by USB-JTAG by default. If they are reconfigured to operate
  as normal GPIOs, USB-JTAG functionality will be disabled." and "SPI0/1: GPIO24 ~ GPIO30 are usually used for SPI flash
  and not recommended for other uses." Datasheet page 25: "**GPIO27** : The VDD\_SPI pin". boards/xiao-esp32-c6.json:71
  `"pin_roles": {` with strapping, console_uart, onboard_led, spi and i2c only. One provenance gap: the brief says the
  pages were "read 2026-10-15", but tech-lead.md ends "I opened no web page". The text came from the docs MCP as chunks.
  The chunks match the claim, so the claim holds, but "read" needs to say "read as docs MCP extracts".

- ★C8 · partly · mpremote commands.py:499-506 `def do_run(state, args): ... buf = f.read() ...
  _do_execbuffer(state, buf, args.follow)` holds for `run`. For mount: commands.py:509-513 `do_mount` calls
  `ensure_raw_repl()` and does not call `did_action()`. main.py:625-627: "If no commands were "actions" then implicitly
  finish with the REPL" / `if state.run_repl_on_completion():`. So `mount` alone ends in the REPL, but `mount <dir> run
  f.py` or `mount <dir> exec ...` does an action and returns. tech-lead.md TL-10 says this ("It ends in the REPL unless
  chained with `run`"). The brief dropped the "unless". Change to: "`mpremote mount` alone ends in the REPL. Chained
  with `run` or `exec` in one call, it returns, so an agent can use it. Nobody ran this on a board." The caveat "a file
  that imports other project files needs them on the board already" is also weaker than it reads: after a passed
  deploy the project's files are on the board.

- ★C9 · partly · `python3 -m mpremote connect --help`, run 2026-10-15: "device        Either list, auto, id:x, port:x, or
  any valid device name/path". P218B:57: "The kept partition table has no OTA slot, so an OTA of the interpreter needs
  another layout". The mpremote help names no network transport, which supports "mpremote cannot drive WebREPL" only by
  absence. P218B ★C12 limits the OTA point to "an OTA of the interpreter". P218's Q14 also asked "which OTA: files or
  a new interpreter?". A file update over Wi-Fi needs no OTA slot. "Need Wi-Fi boot code that spark does not write" also
  fits every firmware feature, because the conversation writes all firmware. Change to: "WebREPL needs Wi-Fi code on
  the board. mpremote's connect help names no network transport. An OTA of the interpreter needs a new partition
  layout. An update of Python files over Wi-Fi does not."

- ★C10 · partly · OBS/2026-10-14-p236-bench.md:24-25: "Claude sent `200`, and the firmware answered `period 200 ms`."
  docs/guide/journey.md:1101: "Then `python3 -m mpremote connect /dev/cu.usbmodem101 repl` talks to the running
  firmware". #224 body quotes the PO's want verbatim. The log shows Claude's pyserial script reaching the board. No log
  shows the PO running `mpremote repl`. The brief's caveat says so. The claim's first sentence still says "He and
  Claude reach the running board by hand today". Change to: "Claude reached the running board by hand with pyserial on
  10-14. The guide documents `mpremote repl` for the PO. No log shows him using it."

- ★C11 · holds · OBS/2026-10-15-p215-bench-rerun.md:35: "The jumper test in the REPL was not run, because the PO has
  no wires." #260: "i dont have any cablues". The claim holds. Its caveat "none" leaves out that a bare-board read
  needs no wires (the BOOT button, the LED), which the story map's slice 3 itself uses.

- ★C12 · holds, wrong pointer · scripts/ready_check.py:15 `READY_WAIT_S = 20` and :53 `said =
  self.connection.run_code("import main", keep_running_for=READY_WAIT_S)`. scripts/download_mode.py:23 `READ_S,
  RESET_WAIT_S, POLL_S = 2, 60, 0.1` and :35 `s.port, s.baudrate, s.timeout, s.dtr, s.rts = sys.argv[1], 115200, 0.1,
  False, False`. The pointer ready_check.py:21 lands inside HASH_FILES. Use :15 and :53-58.

- ★C13 · partly · scripts/look.py:12: `RESTART = "the board restarts while it is read: a running program stops and
  starts again. Nothing is erased or written."` esptool troubleshooting for esp32c6, through the docs MCP: "If
  USB-Serial/JTAG is used for communication and the download mode is entered manually (typically by pressing the EN
  button while holding the Boot button on a DevKit), esptool cannot exit download mode using the default reset
  behavior." and "the USB-Serial/JTAG peripheral can only trigger a core reset, which does not re-sample the state of
  the boot strapping pin." look.py says the program "stops and starts again". The brief's "which stops the gadget" drops
  the restart. Espressif's condition is a manual entry into download mode, which the brief's "already in download
  mode" broadens. "Every session that starts with a look" assumes Q7's answer. Change to: "If a live session starts
  with a look, it starts with an esptool hard reset that restarts the gadget. Espressif says that a chip put in download
  mode by hand stays there after that reset."

- ★C14 · holds · run 2026-10-15: `mpremote 1.29.0`, `Version: 1.29.0`, `License: MIT`, pyserial `3.5`, `screen` at
  /usr/bin/screen. The claim holds for this Mac on this date.

## 2. The brief against its detail

Frame
- The request has a second half (move stories, update journeys, use cases and story maps). The decision line, the scope
  and the items leave it out with no word. #224 names J4, J6 and slices 4 and 6 of P218's map. Nothing maps them.
- "D31 OTA and a Wi-Fi REPL get their own discovery". P218B:173 says "OTA and a Wi-Fi REPL are a later epic, P235, with
  its own discovery". This is that discovery, and D1 moves Wi-Fi out of it. The brief needs to say that D1 narrows
  D31's epic, not that D31 put Wi-Fi elsewhere.
- "Search budget". tech-lead.md ends "I opened no web page", yet the brief says Espressif pages were "read 2026-10-15"
  (★C7, ★C13, risks-and-tests.md supply row and budgets). They were docs MCP extracts.

What we found
- ★C1 drops TL-4: a killed mpremote leaves the firmware stopped until a reset, and the board's state after a kill is —.
  It also drops that a try over 20 s is labelled unreachable.
- ★C2 drops that the console-reading rule already exists: agents.md:577-578 "The conversation's firmware reads the
  console without waiting", and INDEX AT177 is **acted** with "agents.md's flash rule". POA-14 cites these lines. So
  Q4, slice 0's first story ("The rule ... is written in docs/guide/agents.md") and item P246's value line ask for a
  rule that is already written.
- ★C3 drops that two of the causes are known and acted on (AT165, AT173, AT177). It also drops POA-21's own words
  "even with the console heard", which fit run 3 only.
- ★C6 carries "15 of 15" without the esptool reset that came before each read (see part 1).
- ★C8 drops TL-10's "unless chained with `run`".
- ★C9 drops P218B's limit "an OTA of the interpreter".
- user.md USR-13 says "The XIAO's USB data pins and strap pins are on the same header". The board record's strapping
  note says "None is on the XIAO's header", and PHY-3 says GPIO12, GPIO13 and GPIO24-30 are not on the header. The
  brief does not repeat USR-13, but jobs-and-journeys.md Job 3 step 3 cites it ("Strap and USB pins can be hit"). That
  stays true only for code that names the pin by number.
- POA-14 says reach "failed in 4 of the 6 bench deploys I read about (p236: 2 of 3 deploys needed R ...)". The P236 log
  says the 14:03 and 14:12 deploys "said "ready seen" by themselves", so 1 of 3 needed R. The brief does not carry
  the number, but A1's framing rests on POA-21 and POA-14.

Options
- Q2 B cost "no gate change (H, TL-8)". TL-8 does not say that. It is the brief's own inference. A read that restarts
  the board (★C6) may be a live act the PO wants gated. Name it as the facilitator's H.
- Q3 A caveat "none". Narrowing P222 to four bench questions overrides D30 ("the P222 spike also reads a third-party
  MicroPython MCP plugin and belay") and #204's question ("What is possible, what is safe, and what it costs"). The
  caveat needs to say that it needs the PO to change D30 and the card's question.
- Q8 A "what it would prove: a wrong pin cannot drop the port" contradicts its own caveat "free `exec` can still name a
  pin by number". A refusal in spark's pin-read command does not cover free `exec`. Change to "spark's own pin read
  cannot drop the port".
- Q2 A rests on ★C3, which part 1 rates partly. The main argument for A ("test reach first") weakens if reach is mostly
  fixed.
- The rabbit hole "`mpremote mount` for an agent (★C8)" rests on the dropped "unless chained".

Riskiest assumption and its test
- "pass line: 19 of 20 answers ... proposed — the PO assistant's opinion (POA-22)". POA-22 says "Pass line: the PO sets
  it (Q1)" and Q-f gives "for example 9 of 10". No council report proposes 19 of 20. The provenance is wrong.
- The test runs 10 tries "after fresh deploys". A1 is about "the running C6". After a fresh deploy the board is in the
  post-flash state that P243 and P245 already handle. The test mixes the deploy path with the live path.
- risks-and-tests.md A1 "under 17 of 20: fix reach". Results of 17 and 18 of 20 meet neither line.

Risks and tests
- EMC and ESD row: "E ★C6: the port drops are resets, not EMC symptoms". ★C6 says nothing about EMC. This is an
  untagged opinion written as E.
- A2's pass line "3 of his next 5 bench sessions" and A6's "2 or more of 20 opens" name no proposer.
- A2's cheapest test says "for one bench week", and its pass line counts sessions. The two periods differ.

Found on the way
- "look.py and deploy.py have no `--json` yet · E `/usr/bin/grep -n json scripts/look.py scripts/deploy.py` found
  none". I ran that grep. It finds 2 hits in look.py and 10 in deploy.py (requirements.json, `import json`). None is a
  `--json` flag, so the conclusion holds, but the cited evidence is false as written. Use `/usr/bin/grep -n -- '--json'`.
- The agents.md:580 line holds verbatim: "Never run mpremote by hand to turn an unknown into a pass."
- The P236 contradiction holds: line 23 "So esptool's reset alone leaves this chip in download mode." against line 39
  "Each time it happened, the chip was already in download mode before esptool ran".

Story map and items
- Slice 0's first story asks the bench project to read its console and answer a typed line. blink-c6 already does both
  (OBS/2026-10-14-p236-bench.md:10 "typed lines change the period", blink.py:77-81). Q13 asks this, but the map does not
  say that blink-c6 already meets the proof.
- items.md takes "P247 on 2026-10-15 (read from `gh issue list --state all`)". I found titles up to P246. That holds.

verification.md
- It is still the template, with every slot unfilled. The brief's Hand-off says "the refuter has not run", which is true until this
  report.

## 3. Rival explanations the folder does not rule out

- ★C3 and A1 (reach is unreliable): the failures came from three causes that spark already handles (download mode
  after a manual BOOT press, an early ask after esptool's reset, a firmware that does not read its console). On that
  reading only the 02:00 run is open, and A1 is close to retired. The riskiest assumption is then value (A2) or
  the grant (A7).
- ★C2 (reading the console fixed button-light): the 02:10 success came from the fresh flash, the timing after it, or
  P245's second read. One run cannot separate these.
- ★C6 (opening the port restarts the C6): in round 2 the boot that each read saw came from the esptool run just
  before it, or from the reset window after it. At 02:00 the two failed `mpremote exec` probes before the open may have
  left the line states set. pyserial on macOS may also toggle DTR and RTS during `open()` before the False values
  apply. None was measured.
- ★C10 (the PO is not blocked): the PO is not blocked, but the agent is. agents.md:580 and the gate (★C5) stop Claude,
  and Job 4 is what #204 asks for ("connection with agents"). So "not urgent" holds for the PO's hands only.
- ★C5 (a stored grant is needed): one long-lived process started in the PO's terminal can hold the yes and the port
  and take Claude's tries. Or the PO runs each try (Q6 C). Neither needs a grant in the store.
- ★C8 and Q2 C (a file run cannot import project files): after a passed deploy, the project's files are on the board,
  and `mount ... run` in one call serves local ones. The file run may be stronger than the brief says.
- ★C11 (Job 3 cannot be shown without wires): a bare-board read of the BOOT button or the LED pin shows a live read
  works. The map's slice 3 already uses it.
- ★C13 (a look stops the gadget): the look restarts it, so the gadget runs again after the look. The real cost is a
  restart, plus the download-mode case after a manual BOOT press.
- Q2 A's pick (reach and read first): it repeats what deploy.py's ReadyCheck already shows after each flash (mpremote
  `exec`, reached or unknown, mpremote's words kept). POA-38's pre-mortem names this. A first slice that adds a gate
  change for a `print(1)` may add little that the PO can see.
- A4 (a firmware can always read its console without harm to its timing): the rule already ships in agents.md, and two
  firmwares follow it. The rival is that the rule is already in force, so A4 is a check on new firmware, not an open
  belief.
- The PO's want (#224): the request may be a review of plans and a move of cards ("lets please revew the plans and
  options ... move all related stories there"), not a want for a new command now. The folder reads it as a build
  decision.

## 4. Numbers that lack a unit, a population, a period or a provenance

- "19 of 20" (brief riskiest test, A1): provenance given as POA-22, which does not propose it. No reason for 95 %. With
  n = 20, 19 successes is consistent with a true rate well below 95 %.
- "under 17 of 20" (A1, change line): no proposer. It leaves 17 and 18 of 20 undefined.
- "3 of his next 5 bench sessions" (A2): no proposer. "Bench session" is not defined. The cheapest test says "one bench
  week".
- "2 or more of 20 opens" (A6): no proposer. Which DTR and RTS states, which firmware, which reset before.
- "15 of 15" (★C6): population mismatch. The source counts reads after esptool runs, not bare opens.
- "4 opens" (★C6): one firmware (button-light), 2026-10-14, line states not given.
- "one at 02:00 on 10-15" (★C6): a population of one open.
- "three lines" (★C2): no pointer to the lines. The file shows four.
- "runs 1 to 3" (★C3): from prose, run 2's words not quoted.
- "200 ms" (★C6): the source is MicroPython v1.29.0 `usb_serial_jtag.c`. The brief gives no version.
- "about 97 mA" (★C7) and "about 79 mA" (budgets): calculated from datasheet-typ points with an assumed 2.0 V LED drop.
  The brief's ★C7 says it overstates, but gives no lower bound.
- "10 H" (Stands on): ten what? It means ten assumptions A1 to A10. The unit is missing.
- "6 agents, 499 calls and about 90M input tokens" (brief comment): "the P900 rehearsal, 2026-10-06" with no pointer to
  a log.
- "20 s" and "2 s" (★C12): units given. Their source lines are wrong (part 1).
- "4 of the 6 bench deploys" (POA-14, not in the brief): the count is wrong for P236 (1 of 3 needed R).
- "the next free number, P247" (items.md): read 2026-10-15, holds today. It is to be read again at filing, as stated.

## Searches

- Espressif docs MCP: "ESP32-C6 GPIO12 GPIO13 USB-JTAG reconfigured as normal GPIO disabled" · to re-read ★C7's source · used.
- Espressif docs MCP: "esptool troubleshooting USB-Serial/JTAG core reset does not re-sample strapping pin chip stays in download mode watchdog-reset" · to re-read ★C13's source · used.
- none on the web. Local runs: `mpremote --version`, `python3 -m mpremote connect --help`, `pip show mpremote`, pyserial
  version, `command -v screen`, `gh issue view` 224, 249, 260 and 204, `gh issue list --state all`, and greps in
  scripts/ and docs/.
