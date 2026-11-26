# P1200 pre-analysis: the firmware in spark today, and the seams for an editor and a browser deploy

Read on 2026-11-26 in the worktree of branch p1200-firmware-editor (base d14acce2). Each claim has a tag. E is a fact
with a pointer (file:line, or a command and its output). H is a claim with its source. The mark — is an unknown.
Paths are relative to the repository. "The store" is the person's spark store. This file decides nothing.

## Summary

1. The firmware is MicroPython in `firmware/`. The conversation writes `firmware/main.py`. Spark writes only `firmware/pins.py`, the pin map, and its header says "do not edit it" (E, sections 1 and 7).
2. The page shows no firmware text today. The firmware phase is one line with the file time of `firmware/main.py`. Its "Write the firmware" offer is a chat offer, and the page never sends it (E, sections 3 and 4).
3. A page click is a row `{id, key, seen, at}`. `flow.py run-request` takes every value from spark's own offer, never from the request. Its allow-list holds three Operations: pick, parts list and build (E, sections 3 and 6). No path exists for an edit that carries text.
4. esptool (role `flasher`) and mpremote (role `board-shell`) do the deploy, behind the `FirmwarePlatform` and `Flasher` strategies. A yes that another program collected never opens the erase (P675). The PO said "no browser flasher for now" (P218 D11) (E, sections 2, 3 and 9).
5. The firmware is in no kept step and no declared kept record of P1193. The fingerprint reads nothing in `firmware/`. The firmware jobs have no Operation on the core (E, sections 4, 6 and 7).

## 1. The firmware area

### The language and the place of the firmware

- E The firmware is MicroPython. The image builder makes "The flash image of MicroPython and a project's files"
  (scripts/spark/firmware/image_builder.py:2). The board record names its MicroPython build, `micropython_port`
  (image_builder.py:13-14). The tools list's role `firmware-image` points at `micropython-esp32s3` (a print of the
  `roles` key of data/tools.json).
- E `MicroPythonPlatform` "is the one platform spark has today". "A platform for another language (Arduino,
  PlatformIO) would be another subclass" (scripts/spark/bench/firmware_platform.py:2-6).
- E A project's firmware is the folder `firmware/`. `firmware/main.py` is the entry. MicroPython looks for drivers in
  `firmware/lib` (scripts/spark/firmware/import_probe.py:18-23). The flow names `firmware/main.py` "The firmware
  Claude writes" (scripts/spark/flow/phase_readers.py:28-29).
- E The test fixture `tests/data/breadboard/button-light/firmware/` holds `main.py` and `light.py` (`ls -R`). It has
  no `pins.py`.

### The files spark writes and the files the conversation writes

- E The rule: "Spark exports facts, never behaviour. It writes only what it derives from a record it holds, and never
  thresholds, timings, state tables or drivers. The conversation writes the firmware" (AGENTS.md:53). The record of
  the decision says "the conversation writes the firmware", and "the PO ruled one [a generator] out"
  (docs/archive/2026-10-01-firmware-and-tests.md:17-18). It never exports "thresholds, timings, profiles, state tables,
  sound tables, drivers" (same file:97).
- E The agents' contract: after a build with `--keep`, read `missing_facts`. "Then write `firmware/main.py` from
  `pins.py` and follow `next`" (docs/guide/agents.md:27-29). The build's verdict says the same (commands/build.md:219).
- E Spark writes `firmware/pins.py` (scripts/spark/build/kept_files.py:27). `keep_pins` writes it on each build with
  `--keep`. It writes again a file that spark wrote. It leaves alone a file that spark did not write
  (kept_files.py:449-472). It knows its own file by the header (kept_files.py:457).
- E The header is `# The pin map: written by spark's assign_pins.py` (scripts/spark/design/pin_assigner.py:562). The
  next line is "# for the <board>. Regenerate it; do not edit it." (pin_assigner.py:484-485). Each line is one signal
  with its GPIO number, its pad, why spark chose it and the board's note. A pin that the internal pull-up holds gets a
  `<SIGNAL>_PULL = "up"` line (pin_assigner.py:472-498). `assign_pins.py --emit-pins FILE` writes the same text
  (scripts/assign_pins.py:32, :56-62).
- E The build's kept entry for it: `{"file": "build/firmware/pins.py", "did": "wrote", "why": "the pins the firmware
  imports"}` (docs/guide/agents.md:52).
- E Spark writes two more fact files. `flash_image.py --config '{...}'` "also writes /config.json into the image"
  (scripts/flash_image.py:7). After a flash, deploy.py copies `spark.json` to the board (commands/deploy.md:132-136).
- E A project's secrets files are `firmware/*secret*.py`, directly in `firmware/`
  (scripts/spark/firmware/project_secrets.py:1-6, `is_secret_file` at :34). Spark parses them with `ast` and never
  imports them. It shows each value as `***` (project_secrets.py:7-12). When spark cannot parse a secrets file, it
  writes no page (scripts/spark/flow/write_flow_page.py:31-34, :141-143).

### The three firmware jobs: the flash image, the import check and a scenario run

- E The area holds "the flash image, the import check and the simulation's run of a scenario". The three CLIs
  `flash_image.py`, `import_firmware.py` and `run_scenario.py` call these modules (scripts/spark/firmware/__init__.py:1-5).
- E The flash image is MicroPython's interpreter plus a 2 MB littlefs partition at 0x200000. That partition holds the
  project's files, so the simulator starts `main.py` (image_builder.py:4-12). The same image goes to the board
  (commands/deploy.md:110).
- E The import check runs one child Python for each module, with stand-ins for `machine` and MicroPython's `time`
  (scripts/spark/firmware/import_child.py:2-21). It does not import `main.py`, `boot.py` or `pins.py`. The reason for
  `pins.py`: it "is not firmware someone wrote" (import_probe.py:16-18).
- E The scenario run starts wokwi-cli on the image. The log names the image by its sha256 and each file by its sha256.
  So a deploy can compare the board's files with the log (scripts/spark/firmware/scenario_steps.py:22-26, :467-472).
- E None of the three jobs is an Operation on the core. `scripts/flash_image.py`, `import_firmware.py` and
  `run_scenario.py` hold no `run_cli` call (a grep count of 0 each). The catalogue has no firmware table
  (scripts/spark/operation_catalogue.py:15-28). The codes "wait in the library for the Operation that comes later"
  (scripts/spark/firmware/firmware_codes.py:5-6).
- E Spark reads two more facts from the firmware's text and never from the board: the `machine.deepsleep` calls
  (scripts/spark/firmware/sleep_calls.py:1-9) and the values in the secrets files.

## 2. The deploy

### The command and its steps

- E `/spark:deploy` puts the flash image on the board on USB: "look at the board first, then the person's yes, then
  erase and write, then read the board back" (commands/deploy.md:2). Its allowed tools are `look.py`, `deploy.py`
  and `flash_image.py` (commands/deploy.md:3). No deploy skill is in `skills/` (`ls skills`: spark-design,
  spark-reverse-engineer, spark-review).
- E The deploy has five stages as data: plan, look, gate, flash and `verify`, each with its reason
  (scripts/spark/bench/deploy_stages.py:10-29). The gate's reason: "the erase cannot be undone, so the write needs a
  yes for this board" (:26).
- E Step 1, the look. `look.py --json` reads the board and changes nothing. It compares the chip and the flash size
  with the board record, names the last deploy in the store's record, and prints a token
  (commands/deploy.md:13-46). For an unknown board it asks first, with `needs_reply` and a replies file
  (commands/deploy.md:33-41).
- E Step 2, the yes. `deploy.py --json --token <token>` runs the gate, `require_open_gate`. The gate checks for no
  stop, then a token for this board and this image, then a consent that `opens_erase`. Then it asks "erase ALL of this
  board's flash (...) and write <image>?" (scripts/spark/bench/deploy_gate.py:166-193). A yes is one of three kinds:
  typed in a real terminal, a standing deploy grant, or relayed (deploy_gate.py:29-30). With no terminal and no grant,
  deploy.py prints the line for the person's own terminal and exits 2 (commands/deploy.md:65-71).
- E Step 3, the erase and the write. esptool runs two commands: `erase-flash`, then `--after watchdog-reset
  write-flash 0x0 <image>` (scripts/spark/bench/flasher.py:42-53, :80-82). An erase that exits 2 runs once more after
  5 s (flasher.py:63-68).
- E Step 4, the read back. deploy.py copies `spark.json` to the board. mpremote then hashes each file that the
  evidence names, starts the firmware and waits for a line that starts with `ready`. `ready seen` exits 0, `ready not
  seen` exits 1 and `ready unknown` exits 2 (commands/deploy.md:132-141).
- E With no simulation: `flash_image.py --files firmware -o <image>` builds the image. `look.py --no-simulation` gives
  a token for an image of `firmware/` as it is now. `firmware/main.py` must exist and every `.py` must compile. Then
  `deploy.py --no-simulation` asks its own question (commands/deploy.md:118-124).
- E A file in `firmware/` that changed after the run does not go to the board: "the board gets the image that passed,
  not the change" (commands/deploy.md:111-113). `find_newer_files` compares the file times with the image's time
  (scripts/spark/firmware/project_image.py:121-125).

### The tools and the seams

- E esptool writes the image and reads the board. mpremote talks to the board. The roles are `"flasher": "esptool"`
  and `"board-shell": "mpremote"` (data/tools.json:15-16). The pins are esptool 5.5.0 (oldest 5.0) and mpremote
  1.29.0, both pip packages (data/tools.json:131-150).
- E The flasher strategy: "`Flasher` is the base. `EsptoolFlasher` erases the whole flash with esptool and writes one
  image at 0x0". The module only builds the commands, and "nothing here touches USB"
  (scripts/spark/bench/flasher.py:1-6, :18-34).
- E The strategy for all board tools is `FirmwarePlatform`. It makes the flasher, the shell command, the port finder,
  the board reader, the connection, the ready probe and the console probe (firmware_platform.py:37-79).
  `MicroPythonPlatform` fills them with esptool and mpremote (firmware_platform.py:82-123). "The five bench CLIs and
  `deploy_service.DeployService` take a platform" (firmware_platform.py:4-6).
- E Every board tool is a program on the person's computer. The flasher's commands are argv lists (flasher.py:32-34).
  The Operation's outside world gives `run` and `find_tool` (scripts/spark/bench/__init__.py:29-42). No code talks to
  a serial port from a browser. — Whether a `Flasher` subclass can hand its work to a page: no such case exists.

### The Operations and their effect words

- E The effect words are `reads`, `runs`, `board`, `deletes`, `writes`, `asks` and `fetches`
  (scripts/spark/core/operation.py:27-31).
- E The bench table holds ten Operations (scripts/spark/bench/__init__.py:25-26). A print of the catalogue gives their
  effects:

  ```text
  bench look LookAtBoard ['reads', 'runs', 'board', 'asks']
  bench deploy DeployImage ['reads', 'runs', 'board', 'deletes', 'writes', 'asks']
  bench issue-grant IssueGrant ['reads', 'runs', 'board', 'asks']
  bench check-grant CheckGrant ['reads', 'runs']
  bench live RunLiveCode ['reads', 'runs', 'board', 'asks']
  bench reach ReachBoard ['reads', 'runs', 'board', 'asks']
  bench show-bench ShowBench ['reads', 'runs']
  bench register-project RegisterProject ['reads', 'writes']
  bench record-deploy RecordDeploy ['reads', 'runs', 'writes']
  bench disallow-direct-flashing DisallowDirectFlashing ['writes']
  ```

- E A dry run narrows the deploy's effects to `reads`, or to `reads` and `runs` with `--no-simulation`
  (scripts/spark/bench/deploy_image.py:496-499).

### The yes that a browser would carry

- E The code: "`RelayedConsentStrategy` is a yes that another program collected (an MCP or web yes, D19; P675): it
  makes a live grant only, and it never opens the erase (decision 6 of the refactor plan, the PO's to change)"
  (deploy_gate.py:8-10). The class sets `opens_erase = False` (deploy_gate.py:117-126). The gate refuses it with
  `relayed_yes_refused` after the token checks (deploy_gate.py:184-185). The guides say the same
  (docs/guide/agents/never-assume.md:166, docs/guide/agents/json.md:354).
- E P218's D19, the PO, 2026-10-13: "a token and a terminal". The core needs a token from its own look, bound to the
  port, the MAC and the image, and the CLI asks the person in their own terminal before a first erase
  (docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:161). Its caveat: "an MCP or web path needs its own way to
  ask" (same line). D45 says that conflict is "open for any interface without a terminal" (brief.md:187).
- E So the gate stops a deploy that a page starts through any path that hands spark a relayed yes. A page that
  flashes the board with Web Serial does not reach the gate at all. Section 9 has the P218 study of that case.

### Live on the board

- E `live` runs "a short piece of code on the running board inside a grant, say whether the board ran it, and reset
  it" (scripts/spark/bench/run_live_code.py:1-5, :114). A relayed yes can make a live grant (deploy_gate.py:9-10,
  docs/guide/how-it-works.md:124).
- E The REPL is the person's: "the REPL line is the person's" (commands/deploy.md:150). mpremote's `repl` is
  interactive, and each `exec`, `run` and `fs` resets the board (P235 brief.md:49, :59, read by a sub-agent).
- E P235's D1, the PO, 2026-10-15: USB first, and Wi-Fi (WebREPL, OTA) a later option
  (docs/discovery/2026-10-15-p235-live-on-board/brief.md:125). WebREPL "needs Wi-Fi code on the board" (★C9,
  brief.md:54). P235's D12 is the live grant: one yes in his terminal for a board and a time limit (brief.md:136).

## 3. The page

### What the page shows of the firmware and the pin map

- E The page is `page.html`, which `flow.py page` and the build write (commands/page.md:10). Its sections are the
  freshness line, the station line, the NOW box, the Parts, Wiring and Pictures folds, the notes and the developer
  fold (scripts/spark/flow/flow_page.py:1-11, section classes at scripts/spark/flow/page_sections.py:222-516).
- E No section holds the text of a firmware file or of `pins.py` (a grep of page_sections.py, flow_page.py,
  write_flow_page.py and page_script.ts for firmware, pins and main.py found only the secrets mask). The firmware
  shows as its phase: one line with the file time, in the station line and in the developer fold (section 4).
- E P1038's reading of the walk's page, 2026-11-23: the page "holds nothing on the firmware, the deploys, the bench
  facts, the decisions or the battery" (C3, docs/discovery/2026-11-23-p1038-page-design/brief.md:45). The issue of
  P1038 says the same (`gh issue view 1521`).
- E The pin map reaches the page only through the wiring steps and the breadboard picture, which the build draws from
  the same design (H, from the Wiring and Pictures folds at page_sections.py:408-459). Pin roles reach `pins.py`
  comments and not the sheet (docs/discovery/2026-11-15-p820-artifact-interface/risks-and-tests.md:21, read by a
  sub-agent).
- E P1038's design: "A firmware edit, `init_project.py` and `breadboard.py` write no page" (D16's limit,
  docs/discovery/2026-11-23-p1038-page-design/design.md:170). An edit of the firmware outside the core leaves the page
  old until the next `/spark:page`.

### How a click reaches spark

- E The page's script runs only for the owner, in a published page with the Artifact database. It adds a button for
  each offer that the page can send. After the person says yes in the page, it writes one row `{id, key, seen, at}` in
  `requests` (scripts/spark/flow/page_script.ts:1-10, :173, :246, owner check at :452-464).
- E `/spark:page` reads the waiting rows, copies the four fields to `.spark/page-request.json`, runs `flow.py
  run-request`, writes the page again, republishes it and writes the answer row `answers/<id>`
  (commands/page.md:74-101). "Nothing runs until the person types `/spark:page`" (commands/page.md:19-20).
- E `RunRequest` runs a step "only when spark offers that key now and the page was read at the project's fingerprint
  now. The values of the step come from spark's own offer key, never from the request"
  (scripts/spark/flow/run_request.py:1-5). The rule comes from P820's plan: "a request carries a key from an
  allowlist, never a command line or a path" (docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md:7-8), and
  "No path and no command line reaches the page or `db`" (mvp-plan.md:89-92).
- E The fingerprint is the sha256 of the offers and of three files: the needs, `requirements.json` and the build
  record (scripts/spark/flow/fingerprint.py:17-36). It reads nothing in `firmware/`.

### What the page cannot do today

- E The page cannot send a chat offer. "Write the firmware", "Run the simulation" and "Look at the board" have
  `from_page` False. The page shows their sentence with a Copy button (scripts/spark/flow/flow_codes.py:144-160).
  `run-request` refuses such a kind with `request_in_chat` (run_request.py:84-85).
- E The page cannot carry text that the person types. "Free words go to the chat"
  (docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md:153-155). — No decision in P820 or P1038 speaks of
  text typed on the page reaching the project (a sub-agent's read of both folders).
- E A no-go of P820: "no Flash, Deploy or Run-live-code button; the deploy step shows the look, the caveats and the
  line to type, with Copy" (P820 brief.md:97). P820's D9: a confirmed click is a yes for four actions only, "never for
  the board or a simulation" (brief.md:182). "Firmware, simulate and deploy stay chat or terminal only in the MVP"
  (mvp-plan.md:188).
- E P1038 kept that no-go through the walk: "Q-B, 3 of 3: the Flash and Deploy button no-go stays through the walk.
  P820's Q31 stays his" (docs/discovery/2026-11-23-p1038-page-design/design.md:489). In P1038's D24, the PO seat
  proposed "not now" for that no-go, and it goes to the PO (brief.md:141). P820's Q31, whether a click can lead to live
  code on the board, is queued (P820 brief.md:152).

### The host: what an Artifact page can load and do

- E P820's ★C12, 2026-11-15: "The page's sandbox blocks `fetch` to other hosts and holds at most 16 MiB, with scripts
  inline or from listed CDNs, so a page cannot call a local spark over HTTP"
  (docs/discovery/2026-11-15-p820-artifact-interface/brief.md:59). The full list is in council/existing.md:34 (EX-23):
  scripts inline or from cdnjs, jsdelivr, unpkg and a few more. `fetch`, XHR and WebSocket to other hosts are blocked.
  No alert, confirm or prompt.
- E P1038's ★C5 read it again on 2026-11-23 at contract 0.2.98, with "the contract moved twice in six days"
  (docs/discovery/2026-11-23-p1038-page-design/brief.md:47).
- E The `db` capability is "the one documented store a page and Claude Code can both read and write" (P820 ★C7,
  brief.md:54). The spike of 2026-11-15 passed: a click row reached Claude Code 3 of 3, and rows survived 3 of 3
  republishes (P820 brief.md:158-165).
- E `mcp` reaches a local server only in the Claude desktop app (P820 ★C9, brief.md:56). `files` is read-only and
  needs a `chan_` project id (★C10, brief.md:57). It reads raw project files "without spark's mask" (P1038 ★C16,
  brief.md:58).
- E P1038's D24, a delegated council, 2026-11-23 17:57 CET, the PO's to change: "no Artifact files capability on raw
  project files and no public host, in this epic" (P1038 brief.md:141).
- E Out of P820's scope, confirmed by D1 on 2026-11-15: "a hosted spark server" and "any paid service" (P820
  brief.md:20, :174). P820's Q9, "Should spark ship its own MCP server", is queued (brief.md:130).
- E This folder's hosts.md, written by another session on 2026-11-26, read the frame of one Artifact in Chrome. Its
  `allow` attribute names eight features, and `serial` and `usb` are not among them (hosts.md:8-19). The desktop
  app's installed artifact can run a program with `childProcess` after a "full-access" yes (hosts.md:36-45).
- — No D row in P820 or P1038 names a local server for the page or a website of spark's own (a sub-agent's read of
  both folders).

### The store row and the undo moment

- E Neither term is in P820, P1038 or the Artifact how-to. Both come from the research-pages discovery of 2026-11-25.
  "The canvas draws a store row with folds that hold each job as an 'Ask Claude' sentence to copy"
  (docs/discovery/2026-11-25-p1161-research-pages/jobs-and-journeys.md:26). "The Undo moment lists only project steps"
  (UX-11, docs/discovery/2026-11-25-p1161-research-pages/council/ux-ai-ux.md:238). Its Q2 asks whether a store edit
  is a kept step that "undo that" brings back (ux-ai-ux.md:337).

### The older editor discovery, P269

- E P269's D-c, the PO, 2026-10-16: "start the editor as a web page, TypeScript, reusable for an Artifact and
  Electron" (docs/discovery/2026-10-16-p269-views-and-editors/brief.md:18). The editor is the breadboard editor.
  Firmware is out of P269's scope (brief.md:20).
- E P269's D16, the PO, 2026-10-16: "Plain HTML now: one page.html, each picture in its own <img>, no framework and no
  Node build" (brief.md:115). P1038's D29 adds that "A spark user installs nothing", and it rejects a compile at page
  write (P1038 design.md:201, :215, read by a sub-agent).
- E P269's ★C5: "Today nothing in spark keeps a person's edit across a build" (brief.md:50). Q4, where a person's
  edits live, is queued for step 5 (brief.md:67-68, :88).
- E P269 has no code editor, no pin map view and no Web Serial (a sub-agent's read of the folder).

## 4. The flow phases

- E The nine phases: idea, needs, parts, requirements, build, breadboard, firmware, simulate, deploy
  (scripts/spark/flow/flow_codes.py:11-12). The firmware phase is done by `claude`. Simulate and deploy are done by
  `your terminal` (phase_readers.py:536, :550, :576, flow_codes.py:19).
- E The firmware phase reads one fact, the file time of `firmware/main.py`. The reader has no status, "because spark
  cannot judge the firmware" (scripts/spark/flow/phase_readers.py:532-542). Its line is `"firmware/main.py written
  %s"` (flow_codes.py:71). It reads no other file in `firmware/`.
- E A read-only run on the fixture:

  ```text
  SPARK_HOME=<the store> python3 scripts/flow.py show --project tests/data/breadboard/button-light --json
  {"phase": "firmware", "status": null, "mark": "·", "by": "claude", "says": ["firmware/main.py written 2026-11-26T15:00:58+01:00"], "offers": []}
  {"phase": "simulate", "status": "not-started", ... "says": ["No simulation files yet (sim/wokwi.toml). Ask Claude to build the board."]}
  {"phase": "deploy", "status": "not-started", ... "says": ["Ask Claude to look at the board first (/spark:deploy).", "Claude then gives you the deploy line. Run it in your terminal and type yes, unless you gave Claude a standing yes for this board."]}
  ```

- E The time in that line is the checkout time of this worktree today. Nobody wrote the file then. So the file time
  says when any hand last changed the bytes on this disk.
- E The simulate phase reads `ProjectImage`: the image that `sim/wokwi.toml` names, the run logs that name its sha256,
  and the files in `firmware/` that are newer than the image (phase_readers.py:545-567).
- E The deploy phase reads the newest board log in `sim/runs/board/`. Only `ready seen` on the image that the project
  holds now is ok (phase_readers.py:570-587). Its fact `FIRMWARE_NEWER` uses the same compare of file times
  (scripts/spark/flow/deploy_reading.py:29-41).
- E When the firmware phase is not started, `CHAT_NOW` gives the firmware sentence "Write the firmware for this
  project's board." (flow_codes.py:155, :492).

## 5. Settings

- E Today the tools list is the one choice with layers. Spark's defaults are in `data/tools.json`, the person's in the
  store's `tools.json` and the project's in `.spark/tools.json`. They merge "entry by entry and field by field, the
  project winning" (scripts/spark/records/tool_finder.py:4-7, :38-45). `roles` points a job at a tool, and `contracts`
  says what the job needs (the `//` line of data/tools.json). `tool_choices.choice_file` writes a choice to the
  person's file or to the project's (scripts/spark/records/tool_choices.py:18-24).
- E The roles: pdf-text, simulator, board-engine, diagram-converter, js-runtime, littlefs, firmware-image,
  parts-search, chip-docs, bench, ts-runtime, flasher, board-shell, text-colour (a print of `roles`). `flasher` and
  `board-shell` have no contract (a print of `contracts`).
- E No setting or role names an editor, a page host, a server or a browser. A grep of `data/` and `scripts/` found only
  the Wokwi diagram's `"editor": "wokwi"` (scripts/spark/breadboard/drawing.py:588,
  scripts/spark/build/board_alone_input.py:48).
- E P1194, the PO, 2026-11-26: "every new plan names its setting, default and layer" (D3,
  docs/discovery/2026-11-26-p1194-settings/brief.md:121). The layers are global (spark's default), user and project,
  with the account later (D11, brief.md:129). A project's settings move to `.spark/settings.json` (D24, brief.md:142).
  The tools list keeps its own merge in the first slice (D15, brief.md:133). Two Operations are the whole surface,
  `show-settings` and `set-setting` (D23, brief.md:141). The page changes a setting "through an Ask Claude sentence
  now, one button per choice later" (D17, brief.md:135). These come from a sub-agent's read.
- E In P1194's D4, a firmware editor was an option that the PO did not pick (brief.md:122).
- E A setting and a board write: "A deploy grant is a consent, not a setting" (★C13, brief.md:58). D19 lets a paid-run
  setting say yes. It says the deploy grant and the direct-flashing switch "stay as they are" (brief.md:137). The
  no-go "no setting that answers a yes to write a board" is still a proposal (brief.md:87).
- H The roles for a flasher and a board shell exist, and the platform seam reads them (section 2). No role or setting
  for an editor or a page host exists (E above). — Which layer such a choice belongs in.

## 6. The core, and how a click becomes an Operation run

- E An Operation is "one job, with one public method, `run`. A CLI, an agent or an MCP tool calls it through
  `spark.core.cli`" (scripts/spark/core/operation.py:1-3, class at :68-101). `run_operation` "runs one Operation for
  any frontend" (scripts/spark/core/cli.py:1-4, :59). After a run that writes, `written_project` lets a frontend write
  the page again (operation.py:108-112, scripts/spark/core/follow_up.py:1-5).
- E The catalogue holds every area's `OPERATIONS` table, and "A later MCP server lists it"
  (scripts/spark/operation_catalogue.py:1-5, :27-30). Spark has no MCP server of its own: `.mcp.json` lists
  `espressif-docs` and `jlcpcb` only (`cat .mcp.json`). Spark has no local server: a grep of `scripts/` and `tools/`
  for `http.server`, `HTTPServer`, `socketserver`, `localhost` and `127.0.0.1` found nothing.
- E The path of a click is in section 3: a row, `/spark:page`, the request file, `RunRequest`, an answer row. The
  allow-list `STEP_OPERATIONS` holds PickParts, WriteRequirements and BuildBoard (run_request.py:40-43).
- E The Operations for a firmware view, a firmware edit and a deploy, against what exists:

  | job | today | pointer |
  |---|---|---|
  | say where the firmware stands | `show-flow`, the firmware phase: a file time only | phase_readers.py:532-542 |
  | write the page | `write-flow-page`, effects `reads, writes` | write_flow_page.py:169, :184 |
  | show the text of `firmware/*.py` and `pins.py` | none. No page section holds firmware text | page_sections.py:222-516 |
  | write `firmware/pins.py` | inside `build-board` (`keep_pins`), and `assign_pins.py --emit-pins`, a CLI off the core | kept_files.py:449, scripts/assign_pins.py:32 |
  | save an edit to `firmware/*.py` | none | — |
  | check the firmware | `import_firmware.py`, a CLI off the core. `look --no-simulation` compiles every `.py` | commands/deploy.md:121 |
  | build the flash image | `flash_image.py`, a CLI off the core | scripts/flash_image.py:1-8 |
  | run a scenario | `run_scenario.py`, a CLI off the core | section 1 |
  | look at the board | `look` | bench/__init__.py:25 |
  | deploy | `deploy`, effects with `deletes`, `writes`, `asks` | deploy_image.py:458-499 |
  | run code on the board | `live` (with a grant) and `reach`. The REPL line is the person's | run_live_code.py:113-122, commands/deploy.md:150 |
  | carry a page click | `run-request`, three steps allowed | run_request.py:40-43 |

## 7. Change tracking

- E `ProjectCommit` makes "One git commit of one file spark changed in a person's project", so `git revert --no-edit
  <sha>` takes that change back. It asks `held_as_is` before a write. It commits the one file with `--only`. It never
  stages with `git add` and never guesses an author (scripts/spark/records/project_commit.py:1-8, :69-79, :95-104). It
  is "The only code in scripts/spark/ that runs git" (project_commit.py:28-31). Its one writer today is the project
  brief, `.spark/project.json` (scripts/spark/build/project_setup.py:382-421). `IgnoreList` reads `tracks` and
  `tracked_files` from it (scripts/spark/build/ignore_list.py:13, :27-36).
- E Spark's `.gitignore` section lists the local AI file, `sim/*.bin` and `sim/runs/`. The flash image "can hold a
  Wi-Fi password" (ignore_list.py:1-5, :16-19). `firmware/` is not in the section.
- E The P1193 discovery (in the first-line checkout): kept steps are "the records the person decided (the brief, the
  needs, the picks, the requirements, the board), one step per decision. Build outputs and the page are made again"
  (D-d, brief.md:18). The options D-q1: "(a) D8's records only · (b) each area declares its kept records in one table,
  D8's first, then board.tsx and breadboard.json while the bytes are the person's ... · (c) the whole folder"
  (brief.md:76).
- E D6 (brief.md:117): the council's direction is "one lower Strategy under two Services", with two tools-list roles,
  `none` as the off member, `sends` as a new effect word and "an outside change said and kept on a yes". The council
  decided it as a delegate on 2026-11-26, and it is the PO's to change. D13 (brief.md:124), the PO, by 11:17 CET: kept
  steps go on the checked-out branch, and a named point is a ref of spark's own. D14 (brief.md:125), the PO, by 12:15
  CET: spark can commit two kinds of file "for a declared kept record and after his yes". One is a file that git does
  not hold yet. The other is a file with his own uncommitted edit. It commits "the one named file only, never a folder-wide add".
- E No row, no D and no option of P1193 names `firmware/`, `firmware/main.py` or `pins.py` as a kept step or a declared
  kept record. P1193 names the firmware only as a fact that spark reads: "the firmware reader shows a file time" (★C5,
  brief.md:50). In one test, `git restore --source=<ref>` "left the firmware alone" (★C23, brief.md:67). (A
  sub-agent's read of the folder, with brief.md:50, :67, :76, :117, :124-125 checked by me.)
- E The one named case of a page edit: "a layout edit on the page is a kept step through the same Service, and its
  effects are D-q2's `changed` list, with no second seam" (the P1193 discovery, items.md:56). The Service is
  `ProjectTimeline.keep_step(kind, words)`. It sits over a lower Strategy. The members of that Strategy are git, by
  hand, none, a Fake and a later server (the P1193 discovery, council/synthesis.md:43-46). "No code of the project timeline exists yet"
  (brief.md:46).
- H So a firmware edit on the page has no path to a kept step today. Under D-q1 (a) the firmware is no kept record.
  Under (b) it needs a row of its own. Under (c) it is one because it is in the folder. The decision line for D-q1 is
  at the P1193 discovery, brief.md:16 (E). — Which option the PO took for the firmware.
- E `pins.py` is a build output with a do-not-edit header (section 1). Under D-d a build output is "made again", not
  kept.

## 8. The related cards

- E P820 #1173 (open): spark in one Artifact page, from the idea to the breadboard by click or by chat, with people and
  Claude on one state. It records the runtime contract 0.2.96 on 2026-11-15 with `sample`, `db`, `files` and `mcp`. It
  names P269's D-c, "start the editor as a web page, TypeScript, reusable for an Artifact" (`gh issue view 1173`).
- E P199 #152 (open, epic): one front end for spark, "a live web version" and a simpler CLI view, later. It names the
  one core (P158 #94) as what a front end calls (`gh issue view 152`).
- E P494 #674 (open, spike): which interface to build first. The options are the static page, a published Artifact,
  a local live page and a tscircuit RunFrame, each with cost and the order of the front-end cards. It is the open spike
  for the host question in P1200's table (`gh issue view 674`).
- E P1038 #1521 (open, epic): the page design. The walk's page "does not show the firmware, the deploys, the bench
  facts or the decisions". Its Done when asks "which Artifact capabilities it uses, for example files or db for a live
  state without a republish" (`gh issue view 1521`).

## 9. Earlier mentions of Web Serial, esptool-js, ESP Web Tools, WebREPL, CodeMirror or Monaco

- E The grep from the brief, with "esp web tools" added, hits 21 files. All are docs: no code and no JSON. Hits per
  file: P218's council/po-assistant-web-flasher.md 44, council/tech-lead-journeys.md 27,
  council/po-assistant-journeys.md 25, brief.md 11, verification.md 8, council/po-assistant.md 8,
  jobs-and-journeys.md 6, council/refuter.md 6, council/refuter-close.md 5, council/user-journeys.md 4. P235's brief.md
  9, council/tech-lead.md 8, council/po-assistant.md 4, council/user.md 3, council/refuter.md 3, story-map.md 2.
  P867's council/live.md 8, council/refuter-2.md 1, brief.md 1. scrum/STORY_MAP.md 1. This folder's hosts.md 2.
- E CodeMirror and Monaco have no hit. Nobody studied an editor component in the repository.
- E The P218 study of browser flashers, 2026-10-13, answered the PO's question on "the web version f a flashing tool
  for esp32" (docs/discovery/2026-10-13-p218-deploy-and-board/council/po-assistant-web-flasher.md:1-3):
  - WF-1: Web Serial needs a secure context and a person's click on `requestPort()`. MDN calls it "limited" (:9).
  - WF-2: esptool-js is Espressif's, under Apache-2.0. It flashes, erases and reads flash in Chrome and Edge 89 or
    later (:10).
  - WF-3: ESP Web Tools (esphome) is under Apache-2.0. It has a manifest for each chip family and an "erase data"
    prompt (:11).
  - WF-7: ViperIDE (MIT) is a browser editor, REPL and file manager for MicroPython, over USB or WebREPL (:15).
  - WF-10 to WF-12: three shapes. A hosted page goes around spark's gate. A local page that the core makes keeps the
    gate. Checks written again in JavaScript repeat the core's logic (:24-26).
  - WF-15 and WF-16: the image gate and the erase must stay in the core, not in the page (:32-33).
- E The PO's answer, P218's D11, 2026-10-13: "no browser flasher for now: the Python esptool stays the one flashing
  tool, because a browser flasher adds nothing for the known board or for Claude"
  (docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:153). The no-go: "a browser flasher", with the caveat
  "revisit only for a first install by a person with no Python" (brief.md:97).
- E P867's live council, 2026-11-17, LV-18: Web Serial in the page "would hold the port and make the words, which
  breaks 'Python writes every word' ... and 'one core'". It left the Artifact's `serial` grant unknown
  (docs/discovery/2026-11-17-p867-journey-redefined/council/live.md:182-191). LV-19: WebREPL needs Wi-Fi code on the
  board, and it frees the USB port (:193-199).
- E scrum/STORY_MAP.md:45 names "live on the board beyond Live 0 (P235 #224: WebREPL and OTA, D31)" as a later epic.
- E hosts.md in this folder, written today by another session: the frame's `allow` attribute names no `serial`
  (hosts.md:8-19). Scripts load only inline or from a few CDNs (hosts.md:24-27). This file cites those reads as data.

## What I could not check

- Whether an Artifact page can use Web Serial. I tested nothing. hosts.md:8-19 read the frame's `allow` attribute on
  one artifact, in one browser, on one day.
- Whether a local spark project folder has a `chan_` id for the `files` capability (hosts.md:30-32 leaves it open).
- The licences of esptool-js, ESP Web Tools and ViperIDE at their source today. The P218 study read two of them on
  2026-10-13, and I opened no web page.
- Which option of P1193's D-q1 the PO took, as it bears on the firmware. I did not read the decision line
  (brief.md:16) word for word.
- Three sub-agents read the briefs of P820, P1038, P269, P218, P235, P1194 and P1193 for me. I checked eleven of
  their pointers against the files. I did not check the rest.
- I ran `flow.py show` once, on the test fixture, with the person's store. I wrote no page, read no board and
  published nothing.
- The council folders of P820, P1038, P269 and P235, past what their briefs point to.
