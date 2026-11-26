# P1200 council: the refuter

Read at 24b898fd on branch p1200-firmware-editor, 2026-11-26. I wrote nothing in the tree. My one scratch folder is deleted. I did not reread a claim because it was written down. Each verdict below rests on a line I opened or a command I ran today.

## Check first: the existing product

1. **The change does not address the problems that were observed.** Nobody observed a need for an edit on the page or a deploy from the page (PO-1, PO-2, UX-18). Two problems were observed:
   - The terminal's words, and lines that do not copy whole (UX-4). The brief touches this only in D-q3 (a) and item 11.
   - 10 of 28 deploys ended "ready unknown". I opened all 10 board logs in p934-display2's `sim/runs/board/`. Nine say `ready unknown: mpremote could not read the board's files` (eight with `could not enter raw repl`). One says `mpremote could not start the firmware`. So in each case the read-back failed. A page that shows the read-back per file (D-q1 b, item 4, story-map slice 1) would show "not read" on every file of those 10 deploys. No option in the brief addresses why the raw REPL failed.
2. **A fold with main.py and pins.py misses where the walk's changes were.** p934-display2's `firmware/` holds main.py, pins.py, epd.py, quotes.py, quotes.txt, czfont.py and schedule.py. `git log` shows commits outside main.py: quotes.txt 6, quotes.py 5, czfont.py 3, schedule.py 1. One of the decisions asked of the PO was about the quote list ("Drop group B ... on the PO's word", a23c433). ★C11 counts main.py only.
3. **What breaks for current users.**
   - (i) The fold goes stale. P1038 design.md:170: "A firmware edit, `init_project.py` and `breadboard.py` write no page." So the fold can show an older main.py than the one on disk or on the board. Outcome (a), "the page shows main.py and pins.py as spark holds them", is not met between two runs of `/spark:page`. The brief drops this. PO-8 and jobs-and-journeys.md:52 keep it.
   - (ii) Firmware text goes into a hosted Artifact. Only `firmware/*secret*.py` is masked (★C13).
   - (iii) A guard that widens the fingerprint to `firmware/` would refuse a waiting pick or build click after every edit Claude makes to main.py (H, from run_request.py:98-99, `if request.seen != fingerprint[:SHORT]`). The brief's "must not get worse" list has no check for (i) or (iii).

## 1. The ★ claims

- **★C1 · partly.** Spec section 6.1, fetched: "The default allowlist for this feature is 'self'." I could not reproduce the frame read in hosts.md H1-1. risks-and-tests.md A6 says "E ★C1 for the attribute and the standard, H for the result". The brief states the result as fact. Change "The Artifact in a browser cannot open a serial port" to "The Artifact's frame is not allowed the `serial` feature, so by the standard `requestPort()` rejects there. Nobody tried it."
- **★C2 · could not open.** The source is describe_capabilities "desktop", contract 0.2.99, and no artifacts tool runs in my session. hosts.md:42-43 reads: "`"full-access"` is allowed only on an artifact of the person's own organization that no one outside it wrote in, or one written by an owner Anthropic approved." The brief drops the contract version, even though A10 says the contract moves. Nobody checked whether the PO's account counts as an "organization".
- **★C3 · holds.** phase_readers.py:542: `return self.phase(None, [flow_codes.FIRMWARE_MESSAGE % stamp(datetime.datetime.fromtimestamp(main.stat().st_mtime))])`. flow_codes.py:71: `FIRMWARE_MESSAGE = "firmware/main.py written %s"`. The "caveat: none" leaves out D16's limit above.
- **★C4 · holds.** kept_files.py:27: `PIN_MODULE = Path("firmware") / "pins.py"`. kept_files.py:452: "Not spark's: left alone, as `board.tsx` is." I found no other spark writer under `firmware/`.
- **★C5 · holds.**
  - run_request.py:4-5: "The values of the step come from spark's own offer key, never from the request."
  - run_request.py:44: `STEP_OPERATIONS = {operation.name: operation for operation in (PickParts, WriteRequirements, BuildBoard)}`.
  - Small point: the RequestRow at page_script.ts:53-59 also has `withdrawn?: boolean`.
- **★C6 · holds.** fingerprint.py:18: `FILES = (needs.FILE, Path(REQUIREMENTS_FILE), BUILD_RECORD_FILE)`. Line 17, which the brief cites, is the comment above it.
- **★C7 · holds.** flasher.py:33: "The commands that put `image` on the board, in order, each an argv list." board_look.py:398: "4 hex of sha256(MAC), a dash, 4 hex of sha256(image): this board, this image." I reran `wc -l` on TL-5's 17 files and got 3559. See part 4 for what that count leaves out.
- **★C8 · partly.** flasher.py:3 holds: "`EsptoolFlasher` erases the whole flash with esptool and writes one image at 0x0, where the simulator loaded it." The other cited lines do not carry the claim:
  - image_builder.py:2 says the image is "for a headless simulation", and :5 says "On real hardware you copy your .py files over USB afterwards". That is a stale docstring, and it says the opposite of the claim.
  - flasher.py:41-42 and :80-82 say nothing about mpremote or spark.json. The support is board_facts.py:4: "`ReadingFile` copies a small facts file, FACTS_FILE, with mpremote after the flash and reads it back".
  - research.md:84 does not assume a raw-REPL copy. It names the filesystem image as "one more `part`" (H) and calls the raw REPL "simpler".
  - Change: cite flasher.py:3 and board_facts.py:4, and say that this corrects research.md:89.
- **★C9 · holds.**
  - deploy_gate.py:124: `opens_erase = False`.
  - deploy_gate.py:184: `if not consent.opens_erase:  # P675: after the token checks, ...`.
  - board_grant.py:244: "the yes the person gave once in their own terminal, kept as a valid deploy `grant`", with `opens_erase = True`.
- **★C10 · holds, reproduced.** replies.py:158: `return self.stdin.isatty() and self.stdout.isatty()`. In a scratch folder, a child under Python's `pty.fork` printed `isatty True True` and read `yes`. TerminalConsentStrategy has `opens_erase = True` (deploy_gate.py:97).
- **★C11 · holds as a count.** I recounted with the co-author line: p934-display2 15 of 15, irrigation 2 of 2, blink-c6 0 of 1. The population is missing. See parts 2 and 4.
- **★C12 · holds.** From the store's record of the walk's C6: 28 deploys, 24 "typed in a terminal", 4 "standing yes", 18 "ready seen", 10 "ready unknown". The user lens's 11 is wrong, because the 13:44 deploy under the standing yes was "ready seen". The causes in the logs are dropped (see Check first, point 1).
- **★C13 · holds.** project_secrets.py:3-4: "a file directly in `firmware/` whose name, in lower case, matches `*secret*.py`, such as `wifi_secrets.py`." image_builder.py:39: "Every file under the tree, as (path inside the image, bytes), sorted."
- **★C14 · partly.** The npm registry, fetched, gives `"license":"Apache-2.0"`, `"latest":"0.7.1"` and `"0.7.1":"2026-11-02T08:23:15.514Z"`. Two parts are stronger than research.md:
  - "No npm library copies files to a MicroPython board over Web Serial" is stronger than research.md:98, "none found for ESP32". It also contradicts research.md:30, where pico-pipette does files for a Pico from `cdn.jsdelivr.net/npm/`.
  - "ESP Web Tools needs HTTPS" drops research.md:132: "requires https:// is met by localhost through the same rule (H)".
  - Change the first part to: "No npm library found copies files to an ESP32 under MicroPython over Web Serial. pico-pipette does it for a Pico."
- **★C15 · partly.** The P218 brief.md:97 caveat holds verbatim: "revisit only for a first install by a person with no Python". That line is a caveat on a proposed no-go. D11 itself (brief.md:153) carries the PO's words: "we don't need to use the js flasher if its not adding anything to our case". PO-3 also says: "The 11-26 request is a new wish from the PO, not the revisit condition." So "has not fired" is true, and it is beside the point. Change it to: "D11 rests on whether a browser flasher adds anything to our case. The 11-26 request asks that again. The caveat about strangers has not fired."
- **★C16 · holds.** `grep -c run_cli scripts/flash_image.py` gives 0. In operation_catalogue.py:26-27, TABLES holds no firmware table.
- **★C17 · partly.** The quoted phrase is P1193 items.md:56: "a layout edit on the page is a kept step through the same Service". It is about a layout edit (P1163), and it is a proposed comment, not a ruling. Change it to: "Neither P1193's proposed item for layout edits nor its D6 ('an outside change said and kept on a yes') names a firmware edit."

Claims without a ★:
- **C18 · stronger than its source.** The brief tags it E. research.md:132 tags it "(H, from sections 1 and 9)".
- **C19 · partly.** P472 finding.md:70-72 says that TinyUSB "also starts the bootloader on a DTR/RTS pattern ... Untried on its own". PH-5 says the C6's cause is unproven, and whether a settle alone is enough is unknown. The spec has `setSignals()` once the port is open (section 4.8).
- **C21, C22, C23 · hold.** #1795 was merged at 15:58:30 CET.

## 2. The brief against its sources

- **Stale state lines.** Three lines say Q0 still waits: "Ready for" (line 10), Board actions (line 110) and Hand-off (line 118). D1 (line 97) says the PO answered it.
- **The ready-unknown count.** jobs-and-journeys.md:14 and :36 and UX-15 still say 11 of 28. The brief says 10.
- **D-q1 (b), what it would prove.** The brief drops the synthesis's "after a deploy that ended `ready unknown`". The logs show no files were read in those deploys.
- **D-q2 costs.** The brief drops "which waits on P1152 #1688". "Every lens rejects c" is stronger than the synthesis's "every lens that looked" (n12).
- **D-q4 costs.** The brief drops "M to use it" for (c).
- **The caveat "a server of spark's own is not an option, by D12" is stronger than D12.** D12 says "nothing for a server is built" (the git brief, line 129). The PO's request names "our server".
- **D-c and Q4 say option (b) "reopens his D9".** D9 is about what a click's yes covers. In (b) the yes is a grant he typed. mvp-plan.md:188 binds "in the MVP" only, and D-i puts the epic after the MVP.
- **C10 and C20 drop PO-10's caveat:** "the typed yes was never proof against a program".
- **★C11 drops its population.** 13 of the 28 registered projects hold `firmware/main.py`. Only 3 of those 13 have its git history.
- **The standing line's source.** The brief quotes it as the PO's words. The store's source is spark-main's handover (spark-main-handover-2026-11-26.md:29), and no message from the PO is cited.

## 3. Rival explanations the folder does not rule out

- **★C11, "he directs Claude".** The co-author line names who made the commit, not who typed the change. Also, VISION:39 defines the maker as someone who "directs Claude rather than typing commands". So the evidence describes that persona, not the primary hobbyist "at home in a terminal" (VISION:38).
- **A3 from ★C12.** The 10 unknowns are failures of the mpremote raw REPL. They are not a sign that he did not know what the board ran. Either way, a page read-back would also fail.
- **A4, "the friction is words".** The notes of 2026-11-25 were taken under the PO's own rule to note the CLI's UX at each step. Notes framed that way would not record a wish for an editor.
- **"The generated code".** It may mean all the code the AI generated, epd.py and quotes.py included. It need not mean spark's generator.
- **"Our server".** It may mean his own home or LAN server. It need not mean a server of spark's own with accounts (item 16).
- **UX-17, "an edit on the page saves nothing".** This holds only under the Artifact's carry through `/spark:page`, which a local or desktop host removes.

## 4. Numbers without unit, population, period or provenance

- **"17 files, 3,559 lines" (★C7).** The population is TL-5's chosen list. It leaves out deploy_image.py (545 lines), board_grant.py (378) and image_builder.py. No commit is named in the brief.
- **"17 of 18" (★C11).** No period is given for irrigation or blink-c6. The population is 3 of 13 projects.
- **★C12.** The board and the record are not named in the brief. The period runs to 2026-11-23 21:30.
- **Costs S, M and L.** No unit is given anywhere.
- **★C2 and ★C14.** The brief drops contract 0.2.99 and ESP Web Tools 10.5.2.
- **A10's pass line, "one change in two weeks".** What counts as a change is not defined.
- **"6 agents, 499 calls, about 90M tokens".** No source is linked.

## Q2 to Q5

- **Q2** rests on ★C4, which holds. Its preamble, "Spark generates only pins.py", frames his word in spark's sense.
- **Q3** rests on ★C11 and A2. It asks the test-bench persona, from memory, three days later. One named moment passes it. If it fails, that decides D-q2 for a primary user nobody asked.
- **Q4** leaves out the Web Serial path. That is the literal reading of "deploy directly rfom the broswer, if that's supported", and it is item 3 on the card. Q4's third option bundles a start from the page with a page yes that opens the erase. Its opinion rests on A4.
- **Q5** option 2 rests on "the firmware table lands with P1208 #1757". The card names one Operation, `check-firmware`, and no table. It is an MVP card ("MVP part now"). So option 2 can bring the show slice before the MVP walk, against D-i.

## What I could not check

- The Artifact frame's `allow` attribute and Chrome's real behaviour: I had no browser session.
- describe_capabilities "desktop", and the desktop app's pty: no artifacts tool runs in my session.
- The walk diary lines: I did not open diary.md.
- The ESP Web Tools page and esptool-js issue #97: not fetched.

## Searches

- WebFetch https://serial.spec.whatwg.org/ · served ★C1 and C19 · used: the default allowlist in 6.1, requestPort steps 2 and 3 in 3.1, and SerialOptions and open() in 4.4.
- WebFetch https://registry.npmjs.org/esptool-js · served ★C14 · used: the licence, the latest version and the time of 0.7.1.
- none beyond the two fetches above: no web search.
