# P1200 council: the tech lead (Feasibility, and electronics-firmware:physics)

Read on 2026-11-26 in the worktree of branch p1200-firmware-editor. Tags: E is a fact with a pointer. H is a claim with
its source. D is a decision with who and when. The mark — is an unknown. Paths are relative to the repository. "The
store" is the person's spark store, read only. No board was touched and no port was opened. This file decides nothing.

Number provenance words: stated (a document or the code says it), datasheet-typ, datasheet-max, calculated, simulated,
measured (spark's own bench, with n), field (someone else's report of their own hardware).

## 1. Findings

### Feasibility (TL)

- TL-1 · The deploy writes no project file over the raw REPL. It writes one whole-flash image at 0x0. The project's
  files are inside that image, in a littlefs partition at 0x200000. After the flash, only `spark.json` goes to the board
  over mpremote. Then the board hashes its own files and imports `main`. So shape (A) needs no raw-REPL file writer for
  `main.py` or `pins.py`. It needs a raw-REPL driver for three small jobs: copy `spark.json`, run the hash code, and run
  `import main` and read for 20 s. research.md assumes the other way: "A raw-REPL step after the flash is simpler"
  (research.md:84), and "Spark today uses mpremote for this on the bench: code on the board, a file copied, a file read
  back" (research.md:89). The brief's physics question also names "the MicroPython image plus files written over the raw
  REPL". The code says one image · E · scripts/spark/firmware/image_builder.py:4-12, :31-32 (FLASH_SIZE 4 MiB, stated),
  :82-89, scripts/spark/bench/flasher.py:41-42, :80-82, scripts/spark/bench/deploy_service.py:341-351,
  scripts/spark/bench/ready_probe.py:25-38, :88-95 · supports only: the size of (A)'s serial work. It does not say
  whether to build (A).

- TL-2 · Every page-started deploy meets the gate, and only two kinds of yes open it. `require_open_gate` opens the erase
  for a `TerminalConsentStrategy` (a yes typed where stdin and stdout are both a tty) or a standing deploy grant. A yes
  that another program collected is a `RelayedConsentStrategy` with `opens_erase = False`, and the gate refuses it with
  `relayed_yes_refused`. A page click, a db row and an MCP elicitation are all relayed. Shape (A) does not meet the gate
  at all: esptool-js `eraseFlash()` is a call the page makes, so the gate is skipped (P218's WF-10 said the same of a
  hosted page). Shape (B) run by a program with no tty exits 2 and prints the line for the person's own terminal, unless
  a grant stands · E · scripts/spark/bench/deploy_gate.py:92-113, :117-143, :184-185, scripts/spark/core/replies.py:157-158,
  docs/discovery/2026-10-13-p218-deploy-and-board/council/po-assistant-web-flasher.md:26 · supports only: a deploy that
  starts on a page needs the PO's word on D-d (P675, decision 6) and D-c (P820's no-go). Code alone cannot settle it.

- TL-3 · The desktop app's `pty` passes spark's terminal check. `Terminal.live` is `stdin.isatty() and stdout.isatty()`.
  A pseudo-terminal is a tty. So `deploy.py` run under the page's `pty` would ask its erase question there, and a `yes`
  typed there opens the erase as kind `typed`. The page's script holds the input side of that `pty`. So the page's code,
  and Claude who writes the page, could type the yes. That keeps the letter of P675 and loses its point · E for the check
  (scripts/spark/core/replies.py:150-158, scripts/spark/bench/deploy_gate.py:96-113) and for `pty` (hosts.md:39-41, H2-1)
  · H for "the page's code can write to the `pty`" (from the capability's shape, not tested) · supports only: a design
  that runs (B) under `pty` needs a decision on whose yes that is.

- TL-4 · A local server that the person starts in their own terminal keeps the gate unchanged. Its stdin and stdout are
  that terminal. So `TerminalConsentStrategy` asks there, and the page only starts the Operation and shows the answer.
  The yes stays typed by the person in their own terminal. The cost: the person watches two windows, and two requests at
  once share one terminal · H (from scripts/spark/core/replies.py:150-158 and the Operation path in
  scripts/spark/bench/__init__.py:29-42. Not built and not tried) · supports only: one (B) option that needs no change to
  P675.

- TL-5 · Shape (A) means writing the deploy pipeline a second time, unless spark's core runs beside the page. The
  pipeline is 17 Python files with 3,559 lines (measured: `wc -l` of deploy_stages, deploy_gate, deploy_service, flasher,
  firmware_platform, board_look, known_board, board_start, board_console, board_facts, board_log, download_mode,
  board_connection, ready_probe, image_evidence, deploy_record_store and project_image). Three of its test files hold
  206 tests (measured: `grep -c "def test"` gives 173, 18 and 15). What carries over as data: the stage table, each
  file's expected sha256, the hash code's text, the `ready` word, the board record's facts and the question's words. What
  is logic, tuned on the bench: the look's compare and token, the known-board check, the gate, and the verify's recovery
  (find the port by the MAC, read the console for `waiting for download`, wait for RESET, the quiet open with its 2.5 s
  settle, read again). That recovery came from P243, P245, P462, P1007, P1022 and P1092 to P1112 · E · the files and
  commands above, scripts/spark/bench/deploy_service.py:237-301 · supports only: the cost and the drift risk of (A). Not
  a verdict.

- TL-6 · In the Artifact, (A) loses the store and the project's records. The look reads the last deploy, the known board
  and the grant from the store. The deploy writes its board log to `sim/runs/board/` and its entry to the store's
  `boards/<MAC>.json`. The Artifact cannot fetch from another host, and the `files` capability is read only. A deploy in
  the Artifact could keep its log only as a db row that `/spark:page` imports later. That is a new record path whose
  facts another program collected · E for the limits (hosts.md:26-33, H1-3 and H1-5) and the writes
  (scripts/spark/bench/deploy_service.py:269-272, :303-306) · H for the db path · supports only: what (A) in the Artifact
  keeps of "the look" and "the read-back": the board's reads, not spark's records.

- TL-7 · The flash image holds the project's secrets, so (A) in the Artifact uploads them. `files_under` takes every file
  under `firmware/`, a `*secret*.py` file too. ignore_list.py says the image "can hold a Wi-Fi password". A page that
  flashes needs the image inside the page or among the artifact's files, so the password goes to the host, even on a
  private artifact. Size is no block: 4 MiB (stated) in base64 is 5,592,408 bytes (calculated), under the 16 MiB page
  limit (stated, research.md:117) · E · scripts/spark/firmware/image_builder.py:38-42, scripts/spark/build/ignore_list.py:1-5
  · supports only: (A) in the Artifact needs a rule for secrets first, or an image built without them.

- TL-8 · Showing `main.py` and `pins.py` is the cheap feature. It works on every host as text that the page writer
  bakes in, as it bakes the wiring today. The page writer already reads the secrets and refuses a page when a secrets file
  cannot be parsed. The mask covers only values found in `firmware/*secret*.py`. A password written inline in `main.py`
  is not masked, and it would be published. An edit cannot round-trip masked text: a saved `***` would replace the real
  value · E · scripts/spark/firmware/project_secrets.py:1-12, :34, scripts/spark/flow/write_flow_page.py:31-34 · H for the
  round-trip rule · supports only: the view needs a rule for inline secrets, and a secrets file stays read-only and
  hidden on the page.

- TL-9 · A save carries text, and `run-request` forbids that by design: "The values of the step come from spark's own
  offer key, never from the request". So a save is a new Operation with its own rule: a path from an allow-list
  (`firmware/*.py`, never `pins.py`, never `*secret*.py`), the sha256 of the text the page showed (to refuse a lost
  update), a size limit, a compile check, and a kept step. The fingerprint reads nothing in `firmware/`. So today a page
  read before Claude changed `main.py` does not count as stale. `ProjectCommit` already commits one named file, and D-f
  (P1193 D14) allows that after the person's yes · E · scripts/spark/flow/run_request.py:1-5, :40-43,
  scripts/spark/flow/fingerprint.py:17-36, preanalysis.md:356-360 · supports only: the shape of a save Operation.

- TL-10 · An edit, then a deploy from the page, needs the image build on the core first. The deploy writes the image,
  not `firmware/`. A file newer than the image is reported and not flashed. `scripts/flash_image.py` has no `run_cli`
  (`grep -c run_cli` gives 0). With a simulation, a new scenario run is needed too, and `run_scenario.py` is also off the
  core. So "edit, then deploy" from a page is three Operations, and two of them do not exist · E · commands/deploy.md:110-113,
  scripts/spark/firmware/project_image.py:121-125, preanalysis.md:69-72 · supports only: the order of the cards.

- TL-11 · The two board seams assume a program on the person's computer. `Flasher.build_commands` returns argv lists.
  `BoardConnection` runs mpremote's argv. `OutsideWorld.run` runs a program. A Web Serial flasher is no tools-list role,
  because the roles name programs spark finds and runs. It does not fit `build_commands`. A browser path needs one seam
  above `FirmwarePlatform`: where the board work runs, in spark's process or in the page · E ·
  scripts/spark/bench/flasher.py:32-34, scripts/spark/bench/firmware_platform.py:38-77,
  scripts/spark/bench/board_connection.py:103-156, scripts/spark/records/tool_finder.py:1-12 · H for "a setting under
  P1194, not a tools-list role" · supports only: the seam's place if (A) is ever built.

- TL-12 · One untried way keeps a single pipeline in the Artifact: Pyodide. The Artifact's script list allows
  `cdn.jsdelivr.net/pyodide/`. The pure-Python parts (the look's compare, the token, the gate's question) could run in the
  page, with esptool-js as their transport. It is not a drop-in: the bench modules import `subprocess` and `getpass`, and
  `tool_finder` reads the store. It does not bring back the store (TL-6) · E for the script list (research.md:118) and the
  imports (scripts/spark/bench/deploy_gate.py:13-14, scripts/spark/bench/deploy_service.py:10-14,
  scripts/spark/records/tool_finder.py:16-25) · H for the rest · supports only: a spike to name if the PO wants (A)
  without a second pipeline.

- TL-13 · Each host that can run a program fits the core the same way: the page names an Operation by its op, and the
  host runs it through `run_operation`. The catalogue is the list a frontend reads, and "A later MCP server lists it". The
  desktop app's `mcp` capability reaches a local server (P820 ★C9). So a local server, the desktop app's `childProcess`,
  and a later spark MCP server can share one path, and no page holds argv. Shape (A) in a browser does not fit this unless
  the core runs in the page (TL-12) · E · scripts/spark/operation_catalogue.py:1-5, :27-30, preanalysis.md:239,
  :327-334 · H for the shared path · supports only: the core-fit question of the brief.

- TL-14 · Spark has no local server, and one that runs `deploy` is reachable by any web page the person opens, unless it
  checks the request's origin and a secret that only spark's page holds. Binding to 127.0.0.1 alone does not stop a page
  in the same browser · E that none exists (preanalysis.md:333-334) · H for the cross-site risk (model knowledge, not read
  today) · supports only: a local server needs an origin check and a per-run secret in its first slice.

- TL-15 · The desktop host serves the PO, not a stranger. `full-access` is allowed only on an artifact of the person's own
  organization, or one written by an approved owner. Each Allow ends when a newer published version loads, and spark
  republishes after each request · E · hosts.md:42-50 (H2-2, H2-4) · supports only: the table's "desktop app" column is
  for n = 1.

- TL-16 · Two documents disagree on the token. P218's D19: "The core needs a token from its own look, bound to the port,
  the MAC and the image" (docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:161, and preanalysis.md:155-156 repeats
  it). The code: "4 hex of sha256(MAC), a dash, 4 hex of sha256(image): this board, this image"
  (scripts/spark/bench/board_look.py:397-401). The port is not in the token · E both · supports only: a browser path can
  bind the same two things, because the browser's chooser picks the port and spark cannot see which.

- TL-17 · What a read, a desk spike and a bench rung can settle. A read of the code settled TL-1, TL-2, TL-9, TL-10,
  TL-11 and TL-16. A desk spike with no board can settle: whether the Artifact frame allows `serial` (one test page, as
  research.md:123 describes), whether esptool-js and an editor load under the Artifact's script list, whether a `.bin`
  can sit among an artifact's files, whether the desktop `pty` reports a tty (a one-line Python that prints
  `sys.stdin.isatty()` under it) and whether the page's script can write to it, and whether spark's look modules
  import in Pyodide. A bench rung with a board settles PH-4 to PH-7. Nothing can settle: whether a `pty` yes is the
  person's yes (a decision), whether anyone but the PO needs a browser deploy (no user is reachable), and whether the host
  keeps its `allow` list (the host can change it any day, hosts.md:18-19) · H (the classification is mine) · supports
  only: the order of the tests.

### Physics (PH)

- PH-1 · The boards spark knows. The repository's `boards/` holds two records: `firebeetle2-esp32s3` (chip `esp32s3`,
  build `ESP32_GENERIC_S3`, `flash_mb` [16, 4]) and `xiao-esp32-c6` (chip `esp32c6`, build `SEEED_XIAO_ESP32C6`,
  `flash_mb` 4). `chips/` holds only `wokwi-api.h`, Wokwi's C header for a custom simulated chip, and no chip record. The
  store knows five boards by MAC: one `firebeetle2-esp32s3`, two `lilygo-t-display`, one `firebeetle2-esp32c6` and one
  `xiao-esp32-c6`. The T-Display and the FireBeetle 2 C6 have no record in the repository. The tools list names a
  MicroPython build for the original ESP32 "for the LILYGO T-Display" · E · `ls boards chips`, a read of each record's
  keys, the store's `boards/*.json`, data/tools.json:152-160 · supports only: which boards a page deploy would meet.

- PH-2 · The USB path of each board.
  - FireBeetle 2 ESP32-S3: the chip's own USB. Under MicroPython it lists as 303a:4001 (TinyUSB). In ROM download mode it
    lists as 303a:1001 (USB-Serial/JTAG). Both on the same macOS name `/dev/cu.usbmodem1101` (measured, P472 bench
    2026-10-31, scripts/spark/bench/board_start.py:3-7). Its record names no USB path: it has no `usb` pin role (E, a read
    of `pin_roles`).
  - Seeed XIAO ESP32-C6: the chip's own USB-Serial/JTAG on GPIO12 (D-) and GPIO13 (D+) (stated in the record's
    `pin_roles.usb`, citing the ESP32-C6 datasheet v1.5, Table 2-9). The same port serves MicroPython and the ROM (E,
    docs/observations/rows/p1007-quiet-connection.md:19, row 11).
  - FireBeetle 2 ESP32-C6: 303a:1001, "Espressif USB JTAG/serial debug unit" (measured, bench 2026-11-22,
    scripts/spark/bench/board_connection.py:26-28).
  - LilyGO T-Display (original ESP32): a Silicon Labs bridge. macOS lists `/dev/cu.SLAB_USBtoUART` beside
    `/dev/cu.usbserial-<serial>` (measured, the store's bench-2026-11-25.md note 5). The code names it a CP2104
    (scripts/spark/bench/board_look.py:189-190, stated). DTR and RTS reach EN and GPIO0 through the board's auto-reset
    circuit (H, the usual devkit circuit, the T-Display schematic not read).
  - CH340 (1a86:7523) appears only in test fixtures, on no known board (E, tests/test_grant.py:238). No ESP32-C3 board is
    known (E, no record, no bench).
  · supports only: the per-board rows of the host table.

- PH-3 · Neither esptool can reset a running MicroPython S3 into its bootloader by DTR and RTS, because TinyUSB owns the
  port. On the bench, `esptool flash-id` against the running board ended "Failed to connect ... No serial data received"
  (measured, n = 1, P472 23:29:52). `machine.bootloader()` through mpremote entered download mode with no hands (measured,
  n = 2). Spark's deploy has no software entry today: a grep of `scripts/` finds no `bootloader()`, and esptool's
  `silent_step` is `hold_boot`. esptool-js has the same gap as an open issue since 2023-05-29: "Is there any interest in
  supporting flashing of TinyUSB devices?" (#97, 9 comments, read 2026-11-26) · E · docs/discovery/2026-10-31-p472-no-hands/finding.md:5-9,
  :19-21, :36-39, data/tools.json:135, https://github.com/espressif/esptool-js/issues/97 · supports only: on the S3, (A)
  and (B) both need the person's BOOT press, or a raw-REPL `machine.bootloader()` first.

- PH-4 · The S3's port changes its USB product twice in one deploy: 303a:4001, then 303a:1001 in the bootloader, then
  303a:4001 again under MicroPython. Python copes by listing the ports with `mpremote devs` and finding the board by its
  MAC. A web page gets a port only through the browser's chooser, after a click (research.md:54). Whether Chrome keeps one
  grant across the two product ids: —. If it does not, a page's first deploy on the S3 asks the person to pick a port
  more than once (H). Cheapest rung: the bench, a localhost page with no flash and no erase, that opens the 303a:4001 port,
  sends `machine.bootloader()` over the raw REPL, logs the `disconnect` and `connect` events and `getPorts()`, then waits
  for RESET. What it cannot show: Windows or Linux, another Chrome version, or the write itself · E for the ids and the
  MAC search (scripts/spark/bench/board_start.py:3-7, :50-58) · — for Chrome · supports only: the number of clicks of
  (A) on the S3.

- PH-5 · The C6's open. Opening the C6's port restarts the chip, and bytes sent during that boot left MicroPython deaf
  until a ROM download. Spark's cure opens with DTR and RTS off, sends nothing for 2.5 s (measured, 9 of 9 runs, bench
  2026-11-22), and waits up to 10 s for a port that vanished (measured, 1 of 9 runs). A page cannot copy the first half.
  The Web Serial standard's `open()` takes no signal options, and `setSignals()` rejects unless the port is already
  "opened". A page can copy the settle only. Whether that is enough: —. P1007's row 8 saw `ready` read with DTR and RTS
  on, and row 13 left the cause unproven. Cheapest rung: the bench, a localhost page that opens the XIAO C6 nine times,
  waits 2.5 s, then enters the raw REPL, counting the entries. What it cannot show: the cause inside the chip · E ·
  scripts/spark/bench/board_connection.py:29-35, :42-49, docs/observations/rows/p1007-quiet-connection.md:10, :17, :22,
  https://raw.githubusercontent.com/WICG/serial/main/index.bs, the `open()` steps and the `setSignals()` steps (read
  2026-11-26) · supports only: (A)'s read-back on the C6 is untested physics.

- PH-6 · A bridge board after an esptool-js write. An open esptool-js issue of 2026-11-19 says that in 0.7.1
  `after("hard_reset")` "logs 'Hard resetting via RTS pin...' but the chip is not reset. It stays in the flasher stub".
  The reporter names two causes: `HardReset.reset()` never asserts RTS, and `setSignals()` keeps DTR only when it is
  true. One reporter, an unnamed board, no answer yet (0 comments). On the T-Display that would leave the board silent
  for the verify. Python esptool on the same T-Display printed "Watchdog hard reset is not supported on ESP32, attempting
  classic hard reset instead", and the board printed `ready` (measured, n = 1, the store's bench-2026-11-25.md notes 13
  and 14) · E for spark's bench · field for esptool-js (https://github.com/espressif/esptool-js/issues/279, read
  2026-11-26) · supports only: (A) on a bridge board may need a reset of its own after the write. Cheapest rung: the
  T-Display, esptool-js `flashId` then `after("hard_reset")` with no write, watching for MicroPython's banner. It cannot
  show the behaviour after a real write.

- PH-7 · The restart after the write differs by chip. Spark passes `--after watchdog-reset`. On the S3 the watchdog
  resets the whole system and samples the boot pin again, so a board entered with BOOT can leave download mode (stated,
  esptool-5.5.0 targets/esp32s3.py:337-345, as flasher.py cites it). The bench ran it only after a software entry
  (measured, n = 1, 23:29:16). esptool 5.5.0 turns the C6's watchdog reset off, so after a BOOT entry only RESET or power
  helps (stated from the esptool troubleshooting page, measured n = 1 on 2026-11-23 14:09 CET, strap state not read).
  Whether esptool-js has a watchdog reset: — (not read. Issue #210 "Allow custom reset in after() calls" is closed, title
  only). If it has none, (A) leaves a BOOT-entered S3 in download mode where (B) does not · E ·
  scripts/spark/bench/flasher.py:47-58, docs/discovery/2026-10-31-p472-no-hands/finding.md:21-22 · supports only: one
  more row in the table for the S3. Cheapest rung: a desk read of esptool-js's `src/esploader.ts` and its reset module.
  It cannot show the board.

- PH-8 · The read-back keeps its strength in both shapes. Python esptool checks the written data's MD5 on the chip
  (measured: "hash verified", the store's bench-2026-11-25.md note 14). esptool-js `writeFlash` compares each image's MD5
  with the chip's (stated, research.md:71). The file check is SHA-256 computed on the board by spark's `HASH_FILES` text
  and compared with each file's sha256 in the passed run's log. MicroPython has SHA256 in its core (stated,
  research.md:111). A page can send the same text over the raw REPL. What does not carry over is the recovery when ready
  is unknown (TL-5, PH-4, PH-5) · E · scripts/spark/bench/ready_probe.py:25-38, :82-113,
  scripts/spark/firmware/scenario_steps.py:22-26 (preanalysis.md:67-68) · supports only: "the read-back" in (A) as data
  plus a raw-REPL driver, without the recovery.

- PH-9 · The write's time is a baud choice, the same in both shapes. Spark passes no `--baud` (flasher.py:80-82), so
  esptool's default applies (H: 115200, not read today). The T-Display took 109 s for the 4 MiB image (measured, n = 1,
  bench-2026-11-25.md note 20). At 115200 baud, 8N1, the line carries at most 11,520 bytes/s (calculated), so 109 s moves
  at most about 1.26 MB (calculated). That fits a compressed image of the 1,790,544-byte interpreter (calculated from
  the bench line "MicroPython at 0x1000-0x1b6250") and a mostly blank filesystem. An esptool-js reporter wrote 16 MiB at
  921600 in 123 s against about 820 s at 115200, on a CH343 bridge and an ESP32-P4 (field,
  https://github.com/espressif/esptool-js/issues/277, read 2026-11-26). On the chip's own USB the baud does not limit the
  rate (H). So a browser does not make the write faster by itself · supports only: a faster deploy is a `--baud` row for
  (B), not an argument for (A).

- PH-10 · Two smaller physical limits. esptool-js sets a 64 KiB serial buffer because Chrome's default of 255 bytes "drops
  bytes during large transfers" (stated, research.md:75). A raw-REPL driver that spark writes for (A) needs the same.
  mpremote stops with "failed to access <port> (it may be in use by another program)" when another program holds the port
  (stated, board_connection.py:21-23). So a mixed design, where the page flashes and spark reads back, must close the
  page's port first. Whether Chrome holds a port exclusively on macOS: — · supports only: rules for a later design.

## 2. What I could not check, and why

- Whether Chrome keeps one Web Serial grant when the S3 switches between 303a:4001 and 303a:1001. It needs a board and a
  page, and the brief forbids opening a port.
- esptool-js's own source for its reset modes and a watchdog reset. I spent the third web query on the Web Serial
  standard, and read only issue titles for #210 and #255.
- Python esptool's default baud. I did not open esptool's source.
- Whether the desktop app's `pty` can be written by the page's script, and whether it reports a tty. I read hosts.md, not
  the capability's types myself, and ran no installed artifact.
- Whether spark's look modules import in Pyodide. Not tried.
- Whether issue #279 holds on a CP2104. The reporter's board is not named, and nobody answered yet.
- Whether Chrome opens a serial port exclusively on macOS.
- The store's bench logs: I read bench-2026-11-20.md and bench-2026-11-25.md whole, not bench-layout-log.md. I read the
  P472 finding, not its full bench.log.
- The T-Display's auto-reset circuit and its bridge part number. The board has no record in the repository, and I did not
  read its schematic.
- P1193's decision on whether `firmware/` is a declared kept record. I relied on preanalysis.md section 7.

## 3. Questions for the decider

- Does a yes typed in a terminal that a page draws (the desktop app's `pty`) count as the person's typed yes, or as a
  relayed one? · decides: whether (B) on the desktop host can open the erase without a change to P675.
- May any page deploy skip spark's gate, as shape (A) does, or must every erase pass `require_open_gate`? · decides:
  whether (A) stays in scope at all, or only as a spike with spark's core in the page (TL-12).
- May a flash image that holds the project's secrets go into an Artifact? · decides: (A) in the Artifact.
- Which host comes first for a deploy: a local server the person starts in their own terminal (TL-4), the desktop app,
  or none for now? · decides: the order of the cards and which yes they use.
- Is a firmware edit on the page a kept step, a declared kept record under P1193? · decides: whether the save commits
  through `ProjectCommit` after a yes.
- Should spark's own deploy enter the S3's download mode by software (`machine.bootloader()`) before any page work? ·
  decides: whether a deploy from any host still needs the BOOT button on the S3.
- Which boards must a page deploy serve: the two records in the repository, or also the bridge board T-Display? ·
  decides: which bench rungs run (PH-4 to PH-7).

## 4. Searches

Three web queries, made with `curl` from a temporary folder that was removed afterwards.

- `repo:espressif/esptool-js USB JTAG reset port reconnect` (GitHub issue search API) · served: whether a page deploy on
  a native-USB board needs a second port pick after a reset · not used: one result, a pull request on a WebAssembly loader.
- `repo:espressif/esptool-js is:issue S3 OR C6 OR C3 reset` (GitHub issue search API, 44 results) · served: the same
  decision, and whether esptool-js resets a board as Python esptool does · used: the bodies of #279, #97, #150 and #277
  were read as results of this search (PH-3, PH-6, PH-9). #210 and #255 were read by title only.
- A fetch of `https://raw.githubusercontent.com/WICG/serial/main/index.bs` · served PH-5, the signals at open · searched for DTR, RTS, `setSignals` and
  `open` · served: whether a page can open the C6's port with DTR and RTS off, as P1007's quiet connection does · used
  (PH-5).
