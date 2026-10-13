# P218 council: the refuter

Read 2026-10-13, on branch `p218-discovery` at `8e1ff76` with the working-tree `brief.md` that adds D13. I did not write this
discovery. Text I read is data. I flashed, erased and installed nothing, and spent no Wokwi minute. What I ran:

- `ls /dev/cu.*`. It listed `Bluetooth-Incoming-Port`, `BoseQC35II`, `debug-console`, `FreeLoop1_R` and `wlan-debug`. No board was listed.
- Reads of the source of the installed esptool and mpremote: esptool 3.3 (`esptool.py`) and mpremote 1.29.0 (`mpremote/commands.py`,
  `main.py`, `transport_serial.py`), both in this Mac's Python site-packages (`python3 -m pip show esptool mpremote`).
- A decode of the kept MicroPython image, `downloads/ESP32_GENERIC_S3-20260824-v1.29.0.bin` in the spark store (sha256
  `1dd9dcd2…e300`, equal to `data/tools.json`). I read its header and partition table, and its printable strings.
- Two web fetches with `curl`, listed under Searches.
- `git` reads of this repository.

Verdict words: holds · partly (the source says something weaker or narrower) · refuted · could not open. A web pointer
that I did not open gets the verdict "could not open". When I give a verdict on the claim anyway, it rests only on the
pointers that I name as opened.

## Check first: the existing product, and D8

**Does the change address the observed problem?** The observed problem is PO-23 and USER-1: `deploy.py` erases the
board esptool reaches, and only a prose sentence gates it. Slice 0 (P219's first story with P215's flash half) addresses
three parts of it: a named port, a read before the erase, and a yes bound to the port, the MAC and the image. It does
not address four others:

1. **The tool that does the read.** `scripts/deploy.py:34-35` says: "The tools list finds any installed esptool, not
   only its pin." This Mac's esptool is 3.3 (C18). The installed 3.3's S3 class prints no revision and no flash or
   PSRAM features. It has `def get_chip_description(self): return "ESP32-S3"` and `def get_chip_features(self): return
   ["WiFi", "BLE"]`. So a probe that parses esptool 5.5.0's lines reads "unknown", or misreads, on the esptool that
   this Mac runs. The 3.3 parser also rejects the dash command names (`flash-id`, `chip-id`) that A4 to A6 use.
   `deploy.py:34` says esptool 3 and 4 "know only" the names with `_`. The story map does not list the tool pin as a
   precondition of slice 0. The brief keeps it as C30, "found on the way".
2. **The agent.** The yes bound in the core stops a stale yes. It does not stop Claude from forming a fresh, correctly
   bound yes from the look's own output. See the D8 list below and ★C10.
3. **A same-module board.** A board with the same module but a different carrier reads the same on every field the core
   can read (TLJ-8, POJ-26). A7 names this, and its test does not present such a board (part 3).
4. **D13.** The PO's own board is now missing (brief, D13). The first real deploy is to a board that is not the
   project's. Slice 0 detects that board and stops. It does not make a deploy possible:
   - `data/tools.json` holds no C6 interpreter. Its only MicroPython entry is `micropython-esp32s3`.
   - `flash_image.interpreter_path` falls back to the tools list's `firmware-image`, which is the S3 build
     (`scripts/flash_image.py:72-76`).
   - Three of the four C6 and S3 boards in the drawer have no record (D13: only `firebeetle2-esp32s3` and
     `xiao-esp32-c6` exist).

**What breaks for current users.** There is one current user, the PO, and he has never run `deploy.py` on a board
(USER-10). So no use breaks. Code and pages do:

- **A required `--port` breaks two tests and a page.** It breaks
  `tests/test_deploy.py::test_without_a_port_esptool_and_mpremote_find_the_board`, which asserts that a dry run without
  `--port` exits 0. It breaks `tests/test_journey_basic.py` `_deploy`, which calls `deploy.main([... "--dry-run"])` with
  no port. It breaks the sentence in `commands/build.md:264`, "Without `--port`, esptool tries each serial port".
- **A read in the dry run.** The brief says: "must not get worse: … its dry run runs nothing". A probe in the dry run
  resets the board (★C8) and breaks that line. A dry run without the probe no longer shows what the real run decides.
  No file in the folder says which of the two the design takes.
- **The record's shape.** A flash size per SKU changes the shape of the record (TLJ-7). TLJ-7 also says that
  `scripts/boards.py` checks the keys. The folder does not name the tests and checks that read `sku`.
- **The journey picture.** A change to the Bench step's status updates the README's "What works today" table and
  `tools/journey.py` in the same PR. AGENTS.md says so, and `tests/test_journey.py` fails on a stale picture. The
  current picture is `tools/journey.py:41-42`: "deploy.py is ready. It did not run on a real board yet." No item lists
  this.
- **The PO's DE2 ruling is not in the product.** The merged product lacks it, so the start the brief describes is not
  the whole existing product.
  - PR #191 merged at 2026-10-12 21:05 (`aaba3ee`).
  - Ten minutes later, commit `3188a62`, "P192, DE2 as the PO ruled: a run log that tested another image refuses the
    flash, --ignore-older-runs flashes anyway", was pushed. It is only on `origin/p192-deploy` (`git branch -a
    --contains 3188a62`). It is not in `main`, `origin/main` or `HEAD`.
  - `docs/observations/INDEX.md:726` still says DE2 was "acted on the branch as a note, not a refusal. Refusing instead
    is the PO's call".
  - The folder builds on the note behaviour: UC5 step 3, "names stale logs", "works". The ruling itself is H to me. Its
    only source is the commit message.

**D8: does any option or story put the gate's logic in an interface?** Yes. In every option, the part of the gate that
answers "did a person say yes" sits outside the core, or in prose. The core cannot see a person. It can only check that
a yes matches what it read. The places:

- Q3 "typed in the person's own terminal · small, in the core". A terminal prompt belongs to the CLI. An MCP server or a
  web server cannot answer it. One way, the core reads a TTY, and then the core is tied to one interface. The other way,
  the CLI reads it, and then the proof sits in an interface. The brief labels it "in the core".
- Q2 H1, "a record only the person's answer writes". `council/user-journeys.md:437` lists among H1's risks: "the record
  is a file Claude could write". Nothing in the core can enforce "only the person's answer". The brief's H1 caveat drops
  this.
- Q2 H3, "silent checks and a manifest in the core". In `council/user-journeys.md:439`, H3's stop rule for an unread
  field is Claude's: "Claude reads the receipt's `unchecked` list; if it is not empty, Claude asks as if the board were
  unknown". That is logic in the agent. The brief does not say so.
- Q3 token: "Claude can copy it" (kept in the brief). POJ-25's "an explicit `--yes` that Claude may pass only after the
  person said yes" is a prose rule on the agent.
- `council/user-journeys.md:96` (UC1, Claude's view): "It must stop at step 5 and ask in its own turn … It may not pass
  a yes flag in advance or from an allow rule". `:443` (UC-K): "it may not create, widen or renew the yes". Both are
  rules that only prose enforces. The jobs file's gate (G6) inherits them.
- Q7, "May Claude pass ignore". Only an interface can enforce the answer, unless an ignore also needs the person's proof.
- UC7 step 5 (jobs-and-journeys). Claude classes each try. TLJ-37 says "A text filter on free-form `exec` code cannot be
  complete". So the class of a free-form `exec` is the agent's judgement.
- Story map slice 0, "No interface can skip it", and the D8 section, "no interface, command page or agent prompt can
  skip it". These are stronger than the parts above support. An interface cannot skip the binding, but any interface
  can satisfy it.
- ★C26. The irreversible loop that erases and then writes sits in `main()` (`scripts/deploy.py:177-186`), not in a core
  function. A gate added to `plan()` leaves the order of the erase and the write in the interface.

## 1. The ★ claims, source by source

- **★C1.** Opened: `scripts/deploy.py`, `council/user.md` USER-1, and the installed esptool 3.3.
  - Read `deploy.py:166`: `help="the board's serial port, e.g. /dev/cu.usbmodem1101. Omitted, esptool tries each port"`.
  - Read `deploy.py:117`: `return boards.get(project, "chip", json.loads(requirements.read_text()).get("board"))`.
  - Read esptool 3.3, `get_default_connected_device`: `except (FatalError, OSError) as err:` / `if port is not None:` /
    `raise` / `print("%s failed to connect: %s" % (each_port, err))`.
  - Read esptool 3.3, lines 686-690: `if warnings and actually is None:` / `print(("WARNING: This chip doesn't appear to
    be a %s (chip magic value 0x%08x). " "Probably it is unsupported by this version of esptool.") …)` / `else:` /
    `raise FatalError("This chip is %s not %s. Wrong --chip argument?" …)`.
  - Verdict: **partly**. `deploy.py` checks nothing on the board. It passes the record's chip to esptool. When no port is
    named, esptool skips a port whose chip it knows to be another: it raises, catches the error and moves on. A chip it
    does not know gets only a warning. So esptool erases the first board of the named chip that answers, or the first
    board of a chip it does not know. It does not erase "the first board it reaches".
  - Change: "`deploy.py` checks only the chip name it passes to esptool. With no `--port`, esptool tries each port and
    erases the first board it reaches". Why: the installed esptool's loop says otherwise. The difference decides what a
    second board of the same chip risks, and what a C6 risks under D13.
- **★C2.** Opened: `commands/build.md`, `scripts/deploy.py`, `council/po-assistant.md` PO-23.
  - Read `commands/build.md:263-264`: "Ask the person before that run, because it erases the board's whole flash."
  - Read `commands/build.md:3`: the `allowed-tools` list does not name `deploy.py`.
  - Read `commands/build.md:120`, for a command no `allowed-tools` names: "Claude Code asks before it runs (unless the
    person's own settings already let it run: an allow rule of theirs, or auto mode), and the person's answer there is
    the yes."
  - Verdict: **partly**. No prompt, no `--yes` and no `--json` holds (`deploy.py:160-188`, `docs/guide/agents.md:352`).
    "The only gate is a sentence" is too strong. Claude Code's permission prompt is a second gate. It sits in the
    interface, and an allow rule or auto mode turns it off. This session runs in auto mode.
  - Change: "The only gate is a sentence in `commands/build.md` that tells Claude to ask". Why: the observed weakness is
    the person's permission rules as well as the prose. That matters for where a fix sits.
- **★C3.** Opened: `council/tech-lead.md` TL-3 and TL-7, and the installed esptool 3.3. Not opened (budget):
  `https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/basic-commands.html`.
  - Read TL-3: "Not read: which of these lines a module-with-external-flash N16R8 prints. The PSRAM line depends on
    whether the PSRAM eFuse fields are programmed on that module (—)."
  - Read esptool 3.3, `ESP32S3ROM`: `return "ESP32-S3"` and `return ["WiFi", "BLE"]`.
  - Verdict: **partly**. The list is the list of esptool master. The "eFuse flash" line is for in-package (embedded)
    flash, by TL-3's own words, so it does not report the N16R8's module flash. The esptool that this Mac runs prints
    neither revision nor flash nor PSRAM features.
  - Change: "esptool reads an S3's chip, revision, eFuse flash and PSRAM, MAC, flash size and security state". Why: the
    claim drops TL-3's own caveat and the installed version. A5 and A7 rest on it.
- **★C4.** Opened: `boards/firebeetle2-esp32s3.json`.
  - Read `:5`: `"chip": "esp32s3",`. Read `:9`: `"//sku": "DFR0975 is the N16R8 (16 MB flash, 8 MB octal PSRAM); DFR1145
    is the N4 (4 MB, no PSRAM). The header pinout is identical on both, which is why one definition covers them. …"`.
  - Verdict: **holds**. One detail is left out: `sku` is a field, but it lists both codes, so it does not name the board
    in hand.
- **★C5.** Opened: `council/tech-lead-journeys.md` TLJ-11, the kept image, and
  `https://raw.githubusercontent.com/micropython/micropython/v1.29.0/ports/esp32/main.c` (fetched by curl, 334 lines,
  sha256 `37cb251bd9ee6dbe62e9ba0825cf3ad6ae445e0d6bfe12a7d25c539dd9d4eb08`).
  - Read `main.c:251-253`: "    // Query the physical size of the SPI flash and store it in the size" / "    // variable
    of the global, default SPI flash handle." / "    esp_flash_get_physical_size(NULL, &esp_flash_default_chip->size);".
  - Read `main.c:272-273`: "        if (offset > 0 && esp_flash_default_chip->size > offset) {" / "            size_t size =
    esp_flash_default_chip->size - offset;".
  - Read the kept image: the header bytes are `e9 03 02 2f`, which is DIO, 4 MB and 80 MHz. The table is `nvs`
    0x9000/0x6000, `phy_init` 0xf000/0x1000 and `factory` 0x10000/0x1f0000, with no `vfs` entry (measured).
  - Verdict: **refuted**. MicroPython v1.29.0 overwrites the flash size with the chip's physical size before it creates
    the `vfs` partition. So the header's 4 MB does not bound the filesystem. On a chip that reports 16 MiB, the partition
    runs from 0x200000 to 0x1000000: 14,680,064 B, or 3584 blocks of 4096 B (calculated). The image's littlefs has 512
    blocks. This is the case that TLJ-12(c) put outside the read's result. TLJ-11 step 1 came "via a summarising
    fetch". The fetch's summary did not carry lines 251-253 into TLJ-11. What the mount does with a 512-block littlefs on a 3584-block partition is
    H: refuse, or accept.
  - Change, in the brief: "By a read, the 4 MiB image on the 16 MB board gives a 2 MiB filesystem at `0x200000` that
    matches the image's, because the image header keeps 4 MB". Change the same reading in jobs-and-journeys UC1
    "Mechanics", A2's pass line, the story map's slice 0 proof, and P215's "value proven by": each expects 512 blocks.
    Why: the cited file says the opposite.
- **★C6.** Not opened (budget): `https://micropython.org/download/ESP32_GENERIC_S3/`. Opened `council/tech-lead.md`
  PHYS-5, which quotes both statements. I read the kept Standard image's strings: "Found %luMB PSRAM device", "PSRAM chip
  is not connected, or wrong PSRAM line mode" and "quad_psram". Verdict: **could not open**. The strings suggest a
  third reading that reconciles the two statements (part 3). They are not a source for either statement.
- **★C7.** Opened: `docs/2026-10-12-p192-deploy-plan.md`, `scripts/deploy.py`, `council/tech-lead.md` PHYS-1.
  - Read decision 6: "6. `deploy.py` does not watch the serial port. It prints the mpremote line that shows the board
    start. Whether the S3's USB keeps a boot-time `ready` is a bench question, item (c)."
  - Read `deploy.py:41`: `WATCH = "then, to see it start: %s, press Ctrl-C, then Ctrl-D: the firmware prints `ready`"`.
  - Verdict: **holds**.
- **★C8.** Opened: TLJ-2, the installed esptool 3.3 and the installed mpremote 1.29.0. Not opened (budget):
  `https://docs.micropython.org/en/latest/reference/mpremote.html`.
  - Read esptool 3.3: `default=os.environ.get('ESPTOOL_AFTER', 'hard_reset')`.
  - Read mpremote 1.29.0: `main.py:536` `self._auto_soft_reset = True`. `main.py:550-552` `soft_reset =
    self._auto_soft_reset if soft_reset is None else soft_reset` … `self.transport.enter_raw_repl(soft_reset=soft_reset)`.
    `commands.py:482-483` `def _do_execbuffer(state, buf, follow):` / `state.ensure_raw_repl()`. `main.py:304`
    `"resume a previous mpremote session (will not auto soft-reset)"`.
  - Verdict: **holds** on the installed tools, for what the brief claims. The installed code also shows more. `exec`
    soft-resets the interpreter before it runs, unless `resume` comes first. That contradicts TLJ-2 row 1, "not reset",
    and TLJ-36, "heap kept". Jobs-and-journeys G3 and UC0 build on those rows.
- **★C9.** Opened: `https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_device_const_COM.html`
  (fetched by curl, HTML sha256 `46ee9d22669097b653ceb64ef63b23522254f0ec5d46f619e5f7f9a8ec35fe94`), and the installed
  mpremote 1.29.0.
  - Read: "In the ESP ROM Code, the configuration of USB descriptors is as follows:". The table's columns are ESP32S2,
    ESP32S3, ESP32C3, ESP32C5, ESP32C6, ESP32C61, ESP32H2 and ESP32P4. The Serial row reads `0` for the S2 and "MAC
    address" for the others.
  - Read: "For ESP32S3 (usb-serial-jtag) or other chips with usb-serial-jtag interface, the Serial is set to the device
    MAC address."
  - Read mpremote `commands.py:57`: `if p.serial_number == serial_number:`.
  - Verdict: **holds**, for the ROM. The page covers the C6 too, which D13 makes relevant.
- **★C10.** Opened: `council/user-journeys.md` USERJ-4.
  - Read: "No code can tell a person's yes from Claude's flag. Any `--yes` flag Claude can pass." Read option (b): "a
    token … so a yes cannot be reused for another board or image, but Claude can copy it". Read option (a): "(H: shell
    without a terminal is model knowledge, not tested here)".
  - Verdict: **partly**. The first sentence holds as H. The "So" does not follow from it. A yes bound to the port, the MAC
    and the image keeps a yes from being reused for another board or image. It does not tell the person from Claude, and
    USERJ-4 says so.
  - Change: "So the yes binds to what the check read (port, MAC, image), or comes from a terminal Claude lacks". Why: the
    claim offers the binding as an answer to a question it does not answer. A8 inherits the gap (part 3).
- **★C11.** Opened: the deploy plan and TL-13. Read decision 1: "1. "The image that passed" is exact: the log of each run
  names the image's sha256. `deploy.py` refuses an image that no passed run names, or that any run names with another
  verdict." Read `scripts/run_scenario.py:50`: `IMAGE_LINE = "image sha256: "`. Verdict: **holds**.
- **★C12.** Opened: TL-14 and the kept image (my own decode, above). Not opened (budget):
  `https://docs.micropython.org/en/latest/library/esp32.html`. Verdict: **holds** for the table: no `otadata`
  and no second app slot. The OTA half rests on the page I did not open.
- **★C13.** Not opened (budget): `https://docs.micropython.org/en/latest/esp32/quickref.html`. Opened TLJ-34 and the
  installed mpremote 1.29.0. Read `transport_serial.py:30-31`: "support multiple transports (webrepl, socket, BLE, etc).
  At the moment," / "SerialTransport is just the old Pyboard+PyboardExtended class". No websocket code is present.
  Verdict: **holds** that mpremote cannot drive WebREPL. The verdict is **could not open** for the WebREPL facts (boot code, one
  password, `webrepl_cli.py`).
- **★C14.** Opened: TLJ-33 and the installed mpremote 1.29.0. Not opened (budget): the mpremote docs.
  - Read `commands.py:518-522`: `do_mount` calls `state.ensure_raw_repl()` and never `state.did_action()`.
  - Read `main.py:627-630`: "# If no commands were "actions" then implicitly finish with the REPL" / "if
    state.run_repl_on_completion():" / "disconnected = do_repl(state, argparse_repl().parse_args([]))".
  - Verdict: **partly**. `mount` on its own ends in the interactive REPL, so it is not one of the non-interactive
    commands unless an `exec` or a `run` follows it. Every `exec`, `run` and `fs` soft-resets the board first (★C8).
  - Change: "Over USB, Claude can already run mpremote's non-interactive commands (`devs`, `exec`, `run`, `fs`, `mount`).
    Only `repl` is interactive". Why: when Claude runs `mpremote mount .`, the command ends in a REPL and does not return. "Already" hides that each
    read restarts the interpreter.
- **★C15.** Opened: POJ-4, POJ-36 and POJ-39. Not opened (budget): `https://github.com/esphome/esp-web-tools`.
  - Read POJ-4: "asks the person for the port, the file and "Erase flash before installing" (ticked on first install)".
  - Read POJ-39: "· H (Claude, from POJ-35 to POJ-38; not a test)".
  - Read POJ-36: "(page not opened; the listing is a third-party catalogue)".
  - Verdict: **partly**. Thonny's erase tick is a person's choice before the erase. What POJ-39 says no tool guards is
    the board's identity, the line between reading and acting, and a log, not a pre-erase yes. The brief tags the claim
    E, but its synthesis source, POJ-39, is H.
  - Change: "No tool read guards a pre-erase yes or a live session". Why: the claim is wider than POJ-39, and the tag is
    stronger than its source.
- **★C16.** Opened: `scripts/assign_pins.py` and the record.
  - Read `assign_pins.py:410`: `lines.append("%s = %d  # %s" % (entry["signal"], entry["gpio"],
    parts_library.one_line("; ".join(said))))`.
  - Read the record: the keys of `pins` are the silkscreen names `D2` to `RX`, with no GPIO19 or GPIO20 pad.
    `pin_roles` holds `strapping`, `onboard_led`, `onboard_button` and `console_uart`.
  - Verdict: **holds**. One detail is left out: `pins.py` also carries `_PULL = "up"` lines (`:413-415`).
- **★C17.** Opened: the record, at `:298-312`.
  - Read `how_to_tell`: "Look at the chip between the BOOT button and the USB-C. A QFN marked AXP313A is V1.1 or
    earlier; a tiny SOT-563 next to two SOT-23-5 LDOs is V1.2 or later. The back silkscreen also carries the revision."
  - Read `v1_1_and_earlier.i2c_pullups`: "5.1k to 3V3 already present on SDA/SCL — they are the PMIC's own bus pull-ups,
    and the PMIC is another device on your I2C bus".
  - Verdict: **holds**, read narrowly. The record says "V1.1 and earlier" and "V1.2 and later", where the brief says V1.1
    and V1.2. D13 makes the claim moot.
- **★C19.** Opened: `scripts/deploy.py:14`, `tests/test_deploy.py` and the installed esptool 3.3.
  - Read `deploy.py:14`: "The chip comes from the project's board (requirements.json's `board`), and esptool refuses a
    board with another chip."
  - Read `test_deploy.py:72`: `run=run or (lambda argv, **kw: ran.append(argv))`. The fake run never refuses, and no test
    names a second chip.
  - Verdict: **partly**. That the line is only a docstring's claim holds. "Tested only with a fake `run`" overstates: no
    test exercises a refusal at all. The installed 3.3 refuses only a chip it knows (lines 686-690). The only C6 class in
    3.3 is the beta, `ESP32C6BETAROM` with `CHIP_DETECT_MAGIC_VALUE = [0x0da1806f]`. So whether 3.3 refuses or warns on a
    release C6 is unknown.
  - Change: "tested only with a fake `run`", and jobs-and-journeys J3 "today" and UC3 step 1, "esptool refuses in a test
    with a fake run only". Why: there is no such test. Under D13 the refusal is the path the first bench takes.
- **★C20.** Opened: TLJ-10 and `scripts/deploy.py:79-93`.
  - Read `:84`: `digest = hashlib.sha256(image.read_bytes()).hexdigest()`. Read `:90-92`: `if not named:` / `return ("no
    run in sim/runs/ tested %s as it is now…`.
  - Verdict: **holds**. D13 sharpens the caveat. "another chip also needs another interpreter (H)" is E for the missing
    entry: `data/tools.json` has no C6 interpreter.
- **★C21.** Opened: `council/po-assistant.md` PO-17 and PO-18, `council/user.md` USER-13, `ls /dev/cu.*`, and the brief's
  D13.
  - Read USER-13: "If the PO flashes a second board of another family (a XIAO ESP32-C6, a C6 FireBeetle he owns)".
  - Read D13: "the drawer (the PO's store, read 2026-10-13) holds a Seeed XIAO ESP32-C6 (1), a FireBeetle 2 ESP32-C6
    DFR1075 (2), a Beetle ESP32-C6 Mini DFR1117 (3), a Romeo ESP32-S3 DFR0994 (1) and a Beetle ESP32 DFR0575 (2)".
  - Verdict: **refuted**, on "with one board". "None on a USB port" holds (my `ls`). Under D13, "J1 is the only job with
    a blocked person" no longer holds either: J3 now blocks the PO.
  - Change: "The PO is the only user (n = 1), with one board, none on a USB port. J1 is the only job with a blocked
    person". Why: a lens already had the contrary fact, and D13 makes the other board the first path.
- **★C22.** Opened: POJ-30, USERJ-10 and TLJ-27.
  - Read POJ-30, (b): "a small facts file written into the image by `flash_image.py` (the project, the board id, the
    pin-map's hash, the image's sha256)".
  - Read TLJ-27: "the file cannot hold the sha256 of the image that contains it".
  - Verdict: **holds** as a summary of the split. The brief does not say that POJ-30's version holds a field TLJ-27 and
    USERJ-10 show to be impossible.
- **★C23.** Opened: TL-15, TL-16 and `scrum/VISION.md:69`.
  - Read TL-16, quoting Wokwi: "A plain `.bin` provides application only, while Wokwi adds its own bootloader and a
    default partition table, and simulates 4 MB of flash. For custom partitions, filesystems, or exceeding 4 MB, load a
    full image instead."
  - Read `VISION.md:69`: "| Arduino or ESP-IDF before a design pulls them | F1, F2 parked |".
  - Verdict: **partly**. Wokwi also loads a full image, so an Arduino or PlatformIO pass can name a merged whole-flash
    image. Only the toolchains' plain output is app-only.
  - Change: "For Arduino and PlatformIO, Wokwi runs an app-only binary, not the whole image deploy writes". Why: the
    quoted page says a full image can be loaded.
- **★C25.** Opened: PO-20 and POJ-26.
  - Read PO-20: "Riskiest belief overall: that a full-flash image proven in Wokwi's ESP32-S3 model boots identically on
    the physical DFR0975".
  - Read POJ-26: "Riskiest belief under D4: that the facts spark can read from the connected board (chip, flash size,
    MAC) are enough to tell it is the board "the project is for"".
  - Verdict: **partly**. The two quotes hold. The clause "whose arithmetic TLJ-11 then settled" is refuted by ★C5.
  - Change: "the boot of the image (PO-20), whose arithmetic TLJ-11 then settled". Why: PO-20's belief is open again, and
    it was the reason the synthesis moved to A7.
- **★C26.** Opened: `scripts/deploy.py:160-188` and TL-19.
  - Read TL-19: "Fit: yes, already in the shape of AGENTS.md "One core": functions in the module, `main()` prints."
  - Read `deploy.py:177-186`: `for command in commands:` … `run(command, check=True)` … `return EXIT_COULD_NOT_RUN`.
  - Verdict: **partly**. `main()` runs the irreversible sequence (erase, then write, stop on the first failure). It does
    more than print.
  - Change: "`deploy.py` has the one-core shape (functions in a module, `main()` prints)". Why: under D8 the run has to
    move into the core with the gate. "has the shape" makes that move look free.

## 2. The brief against its detail

**Frame**

- "Already decided": the line "pins esptool 5.5.0 and mpremote 1.29.0" is stronger than its source. Decision 4 of the
  plan says: "The tools list finds any installed esptool, not only its pin, so the commands must work on every
  version." The pin is the install line, not a check. This Mac runs 3.3 (C18, C30).
- "Already decided" leaves out DE2. The PO's ruling to refuse a run log that tested another image is on
  `origin/p192-deploy` only (Check first).
- "must not get worse: … its dry run runs nothing" conflicts with a probe in slice 0. No row says how the two fit.
- "Open questions": "Which boards does P219 have to handle" now has D13's words beside it. Q19 is still queued.

**What we found: dropped caveats and claims stronger than their source, beyond part 1**

- ★C5 drops TLJ-11's "via a summarising fetch". That is the step that failed.
- ★C3 drops TL-3's "module-with-external-flash" caveat. It also does not say that TL-3's list is esptool master, not the
  installed 3.3.
- ★C9 drops TLJ-19's caveat: "it is not guaranteed after the person flashes other firmware". TLJ-19 also notes that the
  serial is "123456" in an ESP-IDF example, and the MAC with colons in arduino-esp32.
- ★C10 drops USERJ-4 (b)'s "Claude can copy it". The brief keeps that caveat only on the Q3 token row.
- ★C15's tag (E) is stronger than POJ-39's (H).
- C18 is not starred, although D13 puts it on the first path. With 3.3, `--chip esp32c6` fails in the argument parser
  before any board is touched.
- C27, "ESPHome asks nothing on an update", is stronger than POJ-31. POJ-31 says ESPHome targets a configured device
  "through the dashboard or CLI", which the person starts, and that "What each checks about the board type: — (not
  read)".
- C30 is filed as "a `/spark:setup` matter, a proposal of its own". Under Check first, item 1, it is a precondition of
  slice 0.

**Options**

- Q2 H1 drops two of USERJ's risks: "the record is a file Claude could write", and "a yes for "update" is read as
  "erase"" (`council/user-journeys.md:437`).
- Q2 H3 drops "a manifest listing needs MicroPython running". It also drops that the stop on `unchecked` is Claude's
  rule (`:439`).
- Q3 "typed in the person's own terminal · small, in the core" conflicts with D8 (Check first). It also loses USERJ-4's
  "(H: shell without a terminal is model knowledge, not tested here)". The brief keeps that only on ★C10.
- Q4 "per-file hashes · opinion (the tech lead lists it first)". TL-13 lists three readings and says "This report decides
  nothing". Listing an option first is not an opinion.
- Q4 frames the metered cost wrongly. "full flash only · … · caveat: metered minutes per change" puts the cost on the
  full flash. Under the per-file option, a passed run must still name the changed files (UC6 step 3). Only the
  "untested" path skips the meter. PO-6 said: "J2's real cost is the "must pass in the simulator" gate colliding with
  fast iteration, not missing tooling". The brief drops that.
- Q15 "the not-goal stands · opinion (the PO assistant, PO-29)" misattributes the opinion. PO-37, by the same lens,
  says: "The spike costs a read, so it can run any time; implementation waits". That is closer to "lifted for the
  spike's reading".
- The "No-go: a chip table" sits beside UC2 step 2 ("ranks the board records that fit") and TLJ-8's ranking over
  `boards/*.json`. POJ-28 item 5 warns that a better-board offer "turned into a table of boards (a chip table)". The
  brief does not link the two.

**Riskiest assumption and its test**

- The test runs on "the PO's board", which D13 says is missing. The pass line's N4 step edits a record. It tests the
  comparison against an edited record, not a wrong board. The case that falsifies A7 is a same-chip, same-flash
  other board that reads "same". The pass line names that case only as "if a second board is at the desk". D13's drawer
  holds such a candidate, the Romeo ESP32-S3 (part 3).

**Questions**

- No question asks which esptool the bench runs (C18, C30). It decides A4 to A7 under D13.
- No question carries DE2.

**Jobs and journeys**

- "Who": "The PO, a maker with one ESP32 dev board" is refuted by USER-13 and D13.
- J3 "today": "esptool refuses only another chip, and that claim is tested only with a fake `run`" has the same defects
  as ★C19.
- J7 "today": "erases the first board it reaches" has the same defect as ★C1.
- G3 and UC0 step 2 say a look is "read-only" with `mpremote exec`. The installed mpremote soft-resets first (★C8).
- UC1 "Mechanics, by reading" is refuted (★C5).
- UC3 step 1, "partly (esptool refuses in a test with a fake run only)", has no such test (★C19).
- UC-K step 3 lists "the tools are at their pins" among silent checks. That check does not exist (C30). "partly (the
  image checks work)" is right only for the image.

**Story map**

- Slice 0 "See it run": the proof `os.statvfs('/')` shows 512 blocks of 4096 B is wrong for any board whose flash is
  over 4 MiB (★C5).
- Slice 0 "Say yes": "No interface can skip it" is stronger than its parts (D8 list).
- Order: "Slice 1 comes next in value, because most of the PO's deploys go to his one known board". D13 makes this moot.
  There is no known board until a first flash on a board at hand, and that board is slice 2's case.

**Risks and tests**

- Feasibility row: "E ★C3, ★C5, ★C7 read from sources". ★C5 is refuted and ★C3 is partly.
- A2's pass line (512 blocks) is wrong for a board over 4 MiB. The collection-plan row "Which IDF version builds
  MicroPython v1.29.0 (★C5 caveat)?" no longer decides A2: `main.c` overrides the size whatever the IDF does.
- A4's test, `esptool --chip esp32c6 flash-id` against the S3, needs a board D13 says is missing. On this Mac, 3.3
  rejects `esp32c6` and `flash-id` in its argument parser. That meets the pass line, "a non-zero exit with a message that
  names the chip", with no board contact (part 3).
- A6's pass line, "the board runs again with no button press", misses the soft reset that `mpremote exec` does (★C8).
- A8's test cannot falsify A8 (part 3).
- Budgets: the 91 s and 364 s bounds use 460,800 baud. `deploy.py` passes no `--baud`. The installed 3.3's default is
  115200 (`default=os.environ.get('ESPTOOL_BAUD', ESPLoader.ESP_ROM_BAUD)`, `ESP_ROM_BAUD = 115200`). "10 bit" per byte
  is H in TLJ-2, not "stated" (part 4).

**Items**

- P215's "value proven by" ("512 blocks of 4096 B") is wrong for a board over 4 MiB.
- P228's checklist is the FireBeetle's: the revision by eye, `--chip esp32c6` against the S3, the N4 copy. D13 makes it
  stale.
- P231 depends on A3 (octal PSRAM), which a C6 board cannot test.

**Found on the way**

- C29 holds: I measured the header, DIO at 80 MHz, 4 MB.
- C30 holds: `deploy.py:34-35`.
- C28 is moot for deploy under D13.

**verification.md** is still the template (`⟨fill⟩`), so it adds nothing to compare yet.

## 3. Rival explanations, and what D13 changes

Each interpretation in the folder, with the strongest rival the folder does not rule out.

1. **"The arithmetic is settled, and the boot is the bench's question" (TLJ-11, ★C5, ★C25).** Rival: the cited code sizes the
   filesystem by the physical flash (`main.c:253`). So on any board over 4 MiB, the image's 512-block littlefs meets a
   larger partition. What happens then is H. Either the mount fails, and MicroPython's first-boot setup runs, so
   `main.py` is gone and no `ready` appears. Or the mount accepts the superblock, and the board works, and `statvfs`
   perhaps reports the partition's count (H). In the first case, and probably in the second, A2's pass line, "512
   blocks", fails. In the second case the pass line, set before the run, reads a working board as a failure. The simulation passes with 4 MB (Wokwi's default), so a simulated pass
   cannot catch this.
2. **"A7 is the riskiest assumption" (the synthesis, after POJ-26).** Rival: PO-20 is the riskiest. The synthesis
   dropped PO-20 because TLJ-11 settled it, and TLJ-11 is refuted. Under D13 a third rival is stronger. The riskiest is
   now that a project can be moved to a board at hand at all: a C6 interpreter, records for three of the drawer's four
   C6 and S3 boards, S3-sized constants in `scripts/flash_image.py:28-30`, and a new metered run.
3. **"A7's test shows whether the read facts catch a wrong board."** Rival: the test can pass while A7 is false. The real
   record reads "same", the edited N4 copy reads "flash differs", and revision and wiring read "unknown". That run proves
   the comparison works. It does not prove that a harmful wrong board differs. D13 offers the falsifier: the Romeo
   ESP32-S3 (DFR0994) against the FireBeetle S3 record. Its module and flash are unknown. If they match, it reads "same" on
   every readable field, which is A7's failure case.
4. **"A yes bound in the core to port, MAC and image stops an agent" (A8, slice 0).** Rival: it stops only a stale or
   misdirected yes. A8's test runs with no yes and with a yes for another MAC. An agent that runs the look and passes the
   matching yes passes both tests. So the test cannot falsify the belief as A8 states it.
5. **"A yes typed in a terminal comes from a person, because Claude has no terminal" (Q3 typed, ★C10).** Rival: Claude's
   shell can make a pseudo-terminal for a child process with `script`, `expect` or Python's `pty`, and pipe the answer
   into it. This is H, from model knowledge. I did not try it. If it works, `isatty()` is not proof of a person.
6. **"esptool refuses another chip" (★C19, J3 today).** Rival: it refuses only a chip its own version knows, and it
   warns and goes on for one it does not (installed 3.3, lines 686-690). Under D13 this is the first bench case: an S3
   project against a C6 board, through whichever esptool is installed. Reading does not settle what 3.3 does next on a release C6.
7. **"With no port, esptool erases the first board it reaches" (★C1, J7).** Rival, from the installed code: esptool tries
   the ports in reverse sorted order and skips a port whose known chip differs. It also sends its reset and sync sequence
   to every serial device first: on this Mac the Bluetooth headset port and `FreeLoop1_R`. `deploy.py` runs the erase and
   the write as two esptool processes. With no port, each process searches again on its own. That this can pick two boards
   is H: the order is the same, but the ports can change after the erase's reset.
8. **"A look is read-only and leaves the gadget idle" (TLJ-2 row 1, TLJ-5 "None of these is destructive", G3, A6).**
   Rival: the installed mpremote soft-resets before `exec`, so the look restarts the interpreter. On a soft reset
   MicroPython runs `boot.py` but not `main.py`, and resets the pins it had configured (H, from MicroPython's soft-reset
   path, not read). So a look changes the outputs the gadget was driving.
9. **"The two MicroPython page statements are unresolved" (★C6, PHYS-5).** Rival that reconciles them, from the kept
   Standard image's strings: the Standard build carries a PSRAM driver ("Found %luMB PSRAM device") with a quad mode name
   ("quad_psram") and a message for "wrong PSRAM line mode". On this reading it detects quad PSRAM and runs without an
   octal one. That explains both "Standard detects PSRAM" and "use spiram-oct for Octal SPIRAM". H: strings are not
   a configuration. Under D13 this is moot for a C6 board. It still matters for an S3 with octal PSRAM.
10. **"A boot-time `ready` is lost because native USB re-enumerates at a hard reset" (★C7, PHYS-1).** Rival: the line is
    lost because no reader holds the port while the board prints. One example is a USB-Serial/JTAG driver that drops output it
    cannot send (H). This cause acts with or without a re-enumeration. A1's capture of a soft reset and a hard
    reset separates the two causes. For that, the capture must start before the reset in both cases.
11. **"The serial number is the MAC, so the port list tells two boards apart" (★C9, A10, UC-T).** Rival: that is a ROM
    fact. A MicroPython console on TinyUSB sets its own serial (TLJ-19). Under D13 the case is real: the drawer holds
    three Beetle ESP32-C6 Minis and two FireBeetle 2 ESP32-C6. The page I opened lists the C6 ROM with serial = MAC. The
    Beetle ESP32 (DFR0575, the original ESP32) is not in the page's table. D13's words name only "the c6 ones or another
    s3".
12. **"The only gate is prose" (★C2).** Rival: the gate that exists is Claude Code's permission prompt, held by the
    person's permission rules. The weakness is that the PO runs with auto mode or allow rules, which is an account question
    (Q23), not only a code fact.
13. **"For Arduino and PlatformIO, the passed artefact differs from what deploy writes" (★C23, TLJ-24).** Rival: Wokwi
    takes a full image (TL-16's quote). So a merged image can stay the passed artefact, and decision 1 can hold
    unchanged for those platforms.
14. **"`deploy.py` already has the one-core shape" (★C26, TL-19).** Rival: the part that must be guarded, the run loop,
    sits in the interface (`main()`). So D8 asks for a move, not an addition.
15. **"Most of the PO's deploys go to one known board" (story map order, PO-18).** Rival under D13: the PO's deploys go
    to whichever board he finds. "Known" needs a first flash, so the first several deploys are the other-board path.
16. **"The PO assistant thinks the not-goal stands" (Q15).** Rival from the same lens, PO-37: the spike can run any time,
    and only the implementation waits.

### What D13 changes or makes moot

- **The 4 MiB image on a 16 MB chip (★C5, A2, PHYS-3, PHYS-4):** moot for the FireBeetle and refuted anyway.
  - It is live again for "another S3" whose flash is over 4 MiB. The Romeo ESP32-S3's flash size is unknown.
  - For a 4 MiB C6 board, `main.c` gives 4 MiB − 0x200000 = 2 MiB = 512 blocks (calculated). This matches only if
    the C6 build's table also ends at 0x200000. That is unknown: no C6 interpreter is kept to decode, and the XIAO record
    holds no flash size (TLJ-6).
  - A 4 MiB C6 bench cannot test the large-flash failure at all.
- **The octal PSRAM build (★C6, Q11, A3, P231, UC4):** moot for a C6 board (H: the C6 has no PSRAM interface, model
  knowledge). It stays live only for an S3 with octal PSRAM.
- **The FireBeetle revision (★C17, A11, PHYS-7, PHYS-9, the I2C scan in the contract row, PHYS-8 and C28's VCC pad):**
  moot.
- **esptool 3.3 having no `esp32c6` choice (C18, C30):** it moves from a note to the first blocker.
  - For a project moved to `xiao-esp32-c6`, `deploy.py` passes `--chip esp32c6`, which 3.3's parser rejects. Nothing
    deploys until `/spark:setup` installs 5.5.0.
  - For an S3 project against a C6 board, the outcome on 3.3 is the warn-or-refuse question in rival 6.
  - A4's test inverts to the record's chip against the board at hand, and on 3.3 it passes spuriously.
- **C20 and migration:** they become slice 0, not slice 2. Missing for the drawer's boards:
  - records, for every board except the XIAO C6.
  - a C6 interpreter entry, because `flash_image.py` falls back to the S3 build.
  - a metered run per moved project.
- **★C9, UC-T and P230:** they become concrete. The drawer holds near-identical C6 boards, and the page I opened covers
  the C6 ROM.
- **★C21 and the value row ("J1 is the one job with a blocked person"):** refuted. J3 now blocks the PO's first flash.
- **The story-map order (slice 1 before slice 2) and P228's FireBeetle checklist:** stale.
- **Questions:** Q10 (migrate, go ahead, or a general record) and Q19 (which boards) now have the PO's words in D13:
  "migrated or somehow even checked if its even possible to deploy". I decide nothing on them.

## 4. Numbers without unit, population, period or provenance

- "Stands on: 11 H". A count of the open assumptions, A1 to A11. It is not a count of H claims, of which the brief has
  more. The unit is not named.
- ★C4 and PHYS-3 give "16 MB" and "8 MB", "stated" (vendor). They lack the provenance word, and the unit is ambiguous:
  PHYS-3 says "the stated unit is —". The calculations in ★C5, A2 and TLJ-12 use 16 MiB.
- ★C5: "2 MiB filesystem at `0x200000`" carries no provenance word. It was calculated, and it is now contradicted.
- ★C17: "5.1 k I2C pull-ups" lacks the unit Ω and the provenance. It is stated, from the record, which cites DFRobot's
  V1.0 schematic.
- ★C3: "flash size" with no unit or source rung. Datasheet-typ? No: it is read by `flash-id` from the JEDEC ID, so
  measured once run. Not yet run.
- A2 and the story map: "512 blocks of 4096 B". The unit is given, the provenance (calculated) is missing, and the
  calculation's input is wrong for flash over 4 MiB (★C5).
- A11: "within 1 minute, by the PO's own clock". This has unit and source. Its population is the FireBeetle S3, now
  missing.
- The risks table, power row: "the VCC pad gives 3.6 to 4.5 V on USB by #73's reading". The provenance word is missing.
  It is datasheet-min/max (ETA6003 p.3, via #73, not read again, PHYS-8), not measured. Moot under D13.
- The risks table, supply row: "chips dated before 2219". The unit is missing: it is an Espressif date code, and the
  errata also names "module PW before PW-2022-06" (PHYS-2). The population is S3 chips, moot for a C6.
- The risks table, feasibility row: "each about an hour". It lacks a provenance word. It is Claude's estimate (TL-21,
  TLJ-18 "H"), not stated or measured.
- Budgets:
  - "upper bound 91 s (calculated: 4 MiB × 10 bit / 460,800 baud, no compression, inputs stated)". "10 bit" per byte is
    H in TLJ-2, not stated.
  - 460,800 baud is the MicroPython page's example, not `deploy.py`'s command. `deploy.py` passes no `--baud`, and the
    installed 3.3's default is 115200 baud. At 115200 baud the same bound is 364 s for 4 MiB and 1456 s for 16 MiB
    (calculated). For 5.5.0 the default is unknown.
  - The 364 s backup bound has the same input problem.
  - Over native USB (S3 and C6 USB-Serial/JTAG) the baud rate does not apply (H). Over a UART bridge it does.
- Story map: "most of the PO's deploys go to his one known board". "Most" has no population, period or provenance. It
  is a prediction (H), and D13 contradicts its premise.
- TL-15's "`grep -c -i micropython`" counts, behind ★C23, have a period (2026-10-13) but no stated population beyond
  "scripts and commands". That is minor.
- POJ and PHYS ranges not carried into the brief, such as PHYS-5's "a heap near 100-300 KB means PSRAM is off", are
  marked H at their source. Any summary must keep the H.
- D13's drawer quantities ((1), (2), (3)) have their provenance, "the drawer, read 2026-10-13". No number lacks one.
- The cost comment: "6 agents, 499 calls and about 90M input tokens (2026-10-06)". It has a unit, a period and
  "measured once". Its population is one rehearsal, which is stated.

## Searches

None: I made no search-engine query. I opened two web sources that the brief cites, by fetch. The folder counts fetches
against the budget, so these are my 2:

1. `curl https://raw.githubusercontent.com/micropython/micropython/v1.29.0/ports/esp32/main.c`, for ★C5. 334 lines,
   sha256 `37cb251bd9ee6dbe62e9ba0825cf3ad6ae445e0d6bfe12a7d25c539dd9d4eb08`, read 2026-10-13. Used.
2. `curl -L https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_device_const_COM.html`,
   for ★C9. HTML sha256 `46ee9d22669097b653ceb64ef63b23522254f0ec5d46f619e5f7f9a8ec35fe94`, read 2026-10-13. Used.

The budget left these cited web pointers unopened:

- the esptool basic-commands page (★C3)
- micropython.org's ESP32_GENERIC_S3 page (★C6)
- the mpremote docs (★C8, ★C14)
- the esp32 library page (★C12)
- the esp32 quickref (★C13)
- esp-web-tools (★C15)

In their place I read local sources: the installed esptool 3.3 and mpremote 1.29.0, and the kept MicroPython image.
