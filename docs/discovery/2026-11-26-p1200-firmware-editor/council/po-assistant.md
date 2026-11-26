# P1200 council: the PO assistant (existing first, risks and assumptions)

Read on 2026-11-26 in the worktree of branch p1200-firmware-editor. Tags: E (pointer), H (source), D (who, when), — unknown. This report decides nothing.

## Findings

- PO-1 · Nobody is blocked without this epic now. In every walk diary I read, the conversation wrote `firmware/main.py`. The PO deployed in his own terminal and got `ready seen` on 2026-11-22 (P934) and on 2026-11-25 (T-Display). He wrote 22 notes on 11-25, and all of them are about the CLI's text: the next step was unclear, the output was a wall of text, a command was too long to copy, the yes prompt was one long line. None asks for an editor or a browser path. The README marks Firmware "partly" (the import check proves names only) and Bench "partly". · E the spark-walks folder beside the repository: p711-walk4-button-led/diary.md:18, p711-sound-demo/diary.md:31, p934-display2/diary.md:14 · E the store's bench-2026-11-25.md:1-94 · E README.md, What works today, rows Firmware and Bench · supports only: measured against the MVP bar, the epic moves no basic project closer to a breadboard with working firmware today. This matches the PO's own "not an MVP thing" (#1748, D-i).

- PO-2 · The PO does not type firmware. VISION's maker "directs Claude rather than typing commands". No walk diary line has him reading or changing main.py himself. Code editors are installed on his computer, and their use for firmware is unknown (redacted by the main session after the PR review: details of the PO's own computer stay out of a public file). · E scrum/VISION.md, "Who it is for" · caveat: installed is not the same as used for firmware. n = 1 · supports only: the edit half (D-q2) has no observed user. The show half (D-q1) has a thinner but real case: reading what Claude wrote.

- PO-3 · P218 D11's revisit condition has not fired, and it cannot fire while spark needs Python. The condition is "revisit only for a first install by a person with no Python". VISION says no person outside the project has installed spark. Every spark step is a Python script, and `/spark:setup` installs esptool and mpremote with pip. · E docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:97, :153 · E scrum/VISION.md, the hobbyist row · E data/tools.json:131-150 · supports only: D11's reason still holds for the PO's known board and for Claude ("a browser flasher adds nothing for the known board or for Claude"). The 11-26 request is a new wish from the PO, not the revisit condition. The condition's home is the card "Later: a stranger's first install" (#159, Idea), and P217 #199 (spark from Claude chat, with no Python on the person's side).

- PO-4 · What changed since D11 (2026-10-13):
  - (a) The page exists and takes clicks: P820's MVP, and P829 #1187 is closed.
  - (b) P675 #905 (closed) built `RelayedConsentStrategy` with `opens_erase = False` (deploy_gate.py:117-126).
  - (c) The Artifact desktop host appeared. Its `childProcess` and `pty` work after a "full-access" yes. P820 recorded runtime contract 0.2.96 on 11-15 without `desktop`, and hosts.md read 0.2.99.
  - (d) esptool-js 0.7.1 came out on 2026-11-02, and the pico-pipette repository was created on 2026-11-16.
  - (e) The Artifact frame's `allow` attribute names no `serial` and no `usb`.

  Not changed: Firefox 151 (2026-05-19) and Chrome for Android 148 (2026-05-05) shipped before D11. P218's WF-3 already saw the Firefox claim and left it unverified. · E preanalysis.md section 8 · E `gh issue view 905` · E hosts.md:8-19, :38-45 · E research.md:7, :13, :97 · E council/po-assistant-web-flasher.md:13 · supports only: the one new route to a deploy from a page is a host that runs spark's own Python (the desktop app or a local server), not Web Serial in the Artifact.

- PO-5 · The Deploy-button no-go is weaker than the brief's D-c says. In P820 it was a proposal: "proposals until the decider confirms … none confirmed" (P820 brief.md:96-97). The PO's own confirmed lines are D9 and the plan line. D9 says a confirmed click is a yes "never for the board or a simulation" (brief.md:182). The MVP plan says "Firmware, simulate and deploy stay chat or terminal only in the MVP" (mvp-plan.md:188), and D11 approved that plan. P1038's D24 confirmed the no-go through a delegated council, the PO's to change (P1038 brief.md:80, :141). design.md:489 keeps it "through the walk". · E those lines · supports only: the epic reopens D9 and the MVP plan's line (both the PO's own) and one delegated no-go. D-c should name D9.

- PO-6 · The epic reopens four more decisions that the brief's "Already decided" list does not name:
  - (a) P820 D7: `page.html` "still loads nothing from the web" (P820 brief.md:180). An editor or esptool-js loaded from unpkg or cdnjs breaks this unless it is inlined (the esptool-js bundle is 315,949 bytes, research.md:13).
  - (b) P820's request rule: "a request carries a key from an allowlist, never a command line or a path" (mvp-plan.md:7-8, :89-92). RunRequest takes values "never from the request" (run_request.py:1-5), and "Free words go to the chat" (mvp-plan.md:155). An edit carries text by nature. The brief lists this rule only under "must not get worse".
  - (c) P1038 D24's "no logic in the page's script" and P867 LV-18, where Web Serial in the page "breaks 'Python writes every word'" (P867 council/live.md:182-191). A browser flasher that reads back and compares is logic in the page.
  - (d) P269 D16, "no framework and no Node build" (P269 brief.md:115), and P1038's rule that a spark user installs nothing, with no compile at page write (P1038 design.md:199-215). CodeMirror 6 asks for a bundler (research.md:16, :103), which leaves CodeMirror 5 (archived) or a textarea with Prism.

  · E as cited · supports only: D-q2, D-q3 and the editor seam each cross a decision that the PO made or delegated.

- PO-7 · An edit made on the page has no home in P1193's kept steps. D-d says kept steps are "the records the person decided … Build outputs and the page are made again". D-h says "A take-back takes only spark's own steps". No row and no option names `firmware/`. D14 lets spark commit a declared kept record, one named file, after his yes. A save from the page would be the first file spark writes whose bytes it did not derive, and no take-back covers it. · E `git show 1fb154e2:docs/discovery/2026-11-26-p1193-change-tracking/brief.md`, lines 18, 76, 117 and 125 (the local branch restore-after-1775. origin/restore-after-1775 is missing after `git fetch`) · E preanalysis.md:375-386 · supports only: D-q2 needs one of two things. Either firmware gets its own kept-record row (P1193 D-q1 option b), or an edit goes to the chat and the conversation writes the file.

- PO-8 · There are two writers of main.py, and nothing checks freshness. The fingerprint reads only the needs, the requirements and the build record (scripts/spark/flow/fingerprint.py:17-36). A firmware edit writes no page (P1038 design.md:170, "D16's limit"). So a person could edit an old copy of main.py on the page and overwrite a newer one that the conversation wrote. RunRequest's fingerprint check would not see it. · E those lines · supports only: an edit path needs a sha256 of the shown bytes, checked at save. Showing alone needs a "written at" line.

- PO-9 · Secrets. spark masks only files named `firmware/*secret*.py` (project_secrets.py:1-5). A password typed into main.py or config.py is not masked. The flash image "can hold a Wi-Fi password" (scripts/spark/build/ignore_list.py:1-5). An Artifact cannot fetch the image from another host, so a browser deploy there needs the image inside the published page (research.md:125). That puts the password on the Artifact host. P1091 #1602 (masking in the bench output) is still open. · E as cited · supports only: showing firmware text and carrying an image both need the secrets rule first. A deploy from the Artifact adds a privacy cost that the local hosts do not.

- PO-10 · The desktop host's `pty` passes spark's "real terminal" test. `Terminal.live` is `stdin.isatty() and stdout.isatty()` (scripts/spark/core/replies.py:158). A page with `pty` (hosts.md:38-41) can run deploy.py in a pseudo-terminal. A yes typed there counts as TYPED and opens the erase (deploy_gate.py:92-112). The page's own script can also write "yes" into that pty. · E as cited · caveat: not run. A program could fake a tty with `script` today too, so the typed yes was never proof against a program · supports only: the desktop route reopens what P675 meant (a yes that another program collected never opens the erase), even though the code would call it a typed yes.

- PO-11 · What already does this, what it does not do, and its licence:
  - spark's `/spark:deploy`: the look, the typed yes, esptool's erase and write, the read-back with mpremote, the ready probe (commands/deploy.md:2, :132-141). Not from a page. MIT.
  - spark's page: it shows the deploy phase and, under P820's no-go, "the line to type, with Copy". It holds no firmware text (preanalysis.md:180-182).
  - P218's web-flasher study: Shape B, a local page that the core generates with esptool-js, was the only shape that keeps the gate (WF-11). Shape C forks the checks into JavaScript (WF-12).
  - ViperIDE: a browser MicroPython IDE with an editor, a file manager, a REPL and an esptool-js flasher. It is an app, not a library, and knows nothing of spark's gate. MIT (`gh api repos/vshymanskyy/ViperIDE`, last push 2026-10-05).
  - ESP Web Tools: flashes the parts of a manifest. It writes no file to the MicroPython filesystem and needs HTTPS. Apache-2.0 (research.md:23).
  - esptool-js: a library that flashes, reads and MD5-checks over Web Serial. Apache-2.0 (research.md:22).
  - Wokwi's editor: a browser editor and simulator. Upload to a physical board is an open feature request from 2023 (wokwi-features #454, "Upload code from Wokwi to a physical Arduino board"). The wokwi-features repository has no licence. wokwi-elements and wokwi-cli are MIT (`gh api`, 2026-11-26). — the editor's own terms (not read).
  - Arduino Lab for MicroPython: a desktop Electron app, not a browser page. AGPL-3.0 (research.md:29).
  - pico-pipette: a browser editor for the Pico only, 10 days old. MIT (research.md:30).
  - Desktop editors such as Thonny (MIT, a desktop MicroPython editor with a REPL and file transfer) exist. Which ones the PO has is redacted by the main session after the PR review: details of the PO's own computer stay out of a public file.

  · E as cited · supports only: Thonny and ViperIDE already do "see and edit main.py on the board". What no tool has is spark's gate and records.

- PO-12 · Backlog cards that overlap (from `gh issue list --search`, 2026-11-26):
  - P889 #1259 (Idea): a pin table on the page, the pin-map part of D-q1.
  - P882 #1250: compare the pin names in main.py with the pin map. This is the fact a firmware view would show.
  - P834 #1196 (Idea): the page on GitHub Pages or in Electron. This is the core of D-q4's host table.
  - P494 #674 (a spike): which interface to build first.
  - P199 #152 and P269 #304: one front end, and the base for editors.
  - P235 #224, P870 #1237 and P350 #446: live on the board, streaming, WebREPL. A page that holds the serial port competes with these.
  - P1163 #1699, P1216 #1765 and P1162 #1698: other editors on the page, which would share the edit seam.
  - P1193 #1738: kept steps.
  - P1194 #1740: settings. Its D4 considered a "firmware editor" and the PO picked settings instead (P1194 brief.md:122).
  - #159: a stranger's first install, D11's revisit condition.
  - P217 #199: spark from Claude chat.
  - P836 #1198: acting on a click while the session is idle.
  - P1235 #1787: accounts, which a server of spark's own implies.
  - P1106 #1626 and P1217 #1766: deploy facts on the page.
  - P1091 #1602: secrets in the bench output.

  · E the searches named · supports only: the pin map in D-q1 and the host table in D-q4 already have cards. The epic can cite them instead of filing again.

- PO-13 · A browser deploy saves no time. esptool wrote the whole 4 MB image in 109 s on 11-25 (bench note 20). A browser flasher writes the same whole-flash image, because the image is one file at 0x0 (flasher.py:42-53). · E the store's bench-2026-11-25.md, note 20 · H: Web Serial's speed was not measured · supports only: the value of a browser deploy is where it runs, not speed.

What must be true for the epic to pay off (each an H, from the findings above):
- T1: the page is where the PO works during the firmware and deploy steps. Today he uses it for picks and wiring (README, Idea row), not for firmware (PO-1).
- T2: someone wants to read or change firmware outside the chat (PO-2, no observed case).
- T3: a host the PO uses can reach the board. In the Artifact in a browser it cannot (hosts.md H1-1, one read). The desktop app is untested. A local server is not built.
- T4: a deploy from the page goes through deploy.py's gate, not a JavaScript copy of it (WF-12, PO-10).
- T5: a shown file is the file on disk, and secrets stay masked (PO-8, PO-9).
- T6: an edit reaches the conversation, and a kept step if the PO wants take-back (PO-7).

Riskiest belief (proposed, mine, H): the PO will read, and later edit, the firmware on the page instead of asking Claude in the chat (T2). Feasibility is nearly settled already: H1-1 makes the Artifact a "no" for serial. Value is not settled at all. Cheapest test, an account question (n = 1, past tense): "On 11-22 and 11-25, did you want to read main.py or pins.py yourself? Where did you look, and what did you want to change?" Proposed pass line, set before any answer: he names one moment he wanted to read the firmware (this keeps D-q1), and a separate moment he wanted to change it himself, not through Claude (this keeps D-q2). Second cheapest, for the deploy: the one-button test page of research.md section 8, run in Chrome and in the Claude desktop app. It needs no board.

Pre-mortem, "six months after it shipped, it failed. Why?":
- The PO kept asking Claude to change the firmware, and the editor went unused (PO-2).
- A save from the page overwrote a newer main.py that Claude had written. Firmware was no kept step, so nothing took it back (PO-7, PO-8).
- A Wi-Fi password in main.py, or inside the image, ended up on the Artifact host (PO-9).
- The Artifact never granted `serial`. The deploy lived only on a local server or in the desktop app, which nobody started, or whose permission dialog came back after every republish (hosts.md H2-4). Most cells of the host table stayed "not tested".
- A JavaScript read-back drifted from deploy_gate.py, or a pty yes opened the erase that P675 meant to keep shut (PO-10).
- The host changed under the page. P1038's ★C5 saw the Artifact contract move twice in six days.
- Copied ViperIDE code and an editor bundle needed upkeep that the no-build rule had forbidden (PO-6d).
- Post-MVP epics filed on the same day (P1199, P1203, P1223, P1235, P1200) delayed the MVP walk.

## What I could not check, and why

- origin/restore-after-1775 did not exist after `git fetch`. I read the P1193 brief from the local branch restore-after-1775 (commit 1fb154e2). Whether it matches what returns to main: —.
- Web Serial in an Artifact, and `childProcess` or `pty` in the desktop app. I ran no test page and installed no artifact.
- Whether the PO ever used a desktop editor for MicroPython.
- The terms of Wokwi's web editor. I fetched no terms page.
- Whether a page-hosted pty passes `isatty`. I read the code and ran nothing.
- The council folders of P235, P820 and P1038 beyond the lines cited. The store's councils folder: not read.

## Questions for the decider

- Is the first slice showing only (D-q1), with editing (D-q2) waiting for an observed need? · decides: whether D-q2, P820's request rule and a P1193 kept-record row are in scope at all.
- Does an edit on the page go to the chat as words for the conversation to apply, or does the core write the file? · decides: D-q2, the request rule (PO-6b), the kept steps (PO-7).
- In D-c, are you reopening your own D9 ("never for the board") and the MVP plan's line, or only the delegated no-go? · decides: whether a Deploy button may exist on any host.
- Does a yes typed in a terminal that a page opened (the desktop app's pty) count as your own terminal? · decides: the desktop host's deploy, and P675's reach (PO-10).
- May the page load scripts from a CDN (this reopens P820 D7), or must every library be inlined in the page? · decides: the editor and flasher choice, and the page's size.
- Does the 11-26 request replace D11's revisit condition, or does a browser flasher still wait for #159 (a person with no Python)? · decides: D-q3's scope.
- Which hosts do you use: the Artifact in Chrome, the Claude desktop app, both? · decides: which column of the host table is filled first.

## Searches

All were GitHub issue searches in wokwi/wokwi-features, run with `gh search issues`. There were four, one over the budget of three.
- `upload to real device` · served D-q3: does an existing browser editor already deploy to a physical board · not used (no result).
- `web serial` · served D-q3 · not used (one unrelated result).
- `flash physical board` · served D-q3 · not used (unrelated results).
- `real hardware` · served D-q3 · used (#454, open: "Upload code from Wokwi to a physical Arduino board").

Not counted as searches: `gh api` reads of the repositories of wokwi-elements, wokwi-cli, wokwi-features and ViperIDE, and `gh issue list --search` in spark's own repository.
