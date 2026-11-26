# P1200 council: the synthesis

The architect on Fable, 2026-11-26. Read at 33b01d57 on branch p1200-firmware-editor. Tags: E is a fact with a pointer. H is a claim with its source. D is a decision with who and when. The mark — is an unknown. A lens finding is cited by its id: PO-n (the PO assistant), UX-n (the user's journey), TL-n and PH-n (the tech lead), AR-n (the architecture lens). "Checked by me" means I opened the file or ran the command today. "Not rechecked" means I pass on the lens's pointer as it stands. Paths are from the repository. "The store" is the person's spark store. This file decides nothing. Every recommendation is marked as an opinion. No file I read asked me to run or change anything.

## Short version

1. Showing the firmware is cheap and works the same on every host, because the page writer bakes text into `page.html`. All four lenses agree [H TL-8, AR-1, PO-2, UX-11]. No section holds firmware text today [E preanalysis.md:180-182].
2. Nobody observed a need for an edit on the page or for a deploy from a browser. The PO directs Claude, and his friction on 2026-11-25 was the terminal's words and a line that did not copy whole [H PO-1, PO-2, UX-1, UX-4]. The wish is on record twice, as a wish [H UX-18].
3. The Artifact in a browser cannot open a serial port. Its frame's `allow` attribute names no `serial` [E hosts.md:8-19, read by the main session, not pressed]. The standard's default allowlist for `serial` is `'self'` [E https://serial.spec.whatwg.org/ section 6.1, checked by me 2026-11-26].
4. A deploy that a page starts can keep the look, the yes and the read-back only one way: the page starts spark's own `deploy` Operation on a host that runs a program. Then the pipeline is the one that exists [E scripts/spark/bench/deploy_stages.py:23-29, checked by me]. A flasher written in JavaScript skips the gate [H TL-2, AR-5].
5. A browser flasher is not one more member of `Flasher`. `Flasher.build_commands` returns argv lists for a program on the person's computer [E scripts/spark/bench/flasher.py:32-34, checked by me]. The token comes from a look that Python made [E scripts/spark/bench/board_look.py:397-401, checked by me].
6. A yes given on a page stays a relayed yes, and the gate refuses it [E scripts/spark/bench/deploy_gate.py:117-126, :184-185, checked by me]. Three lenses found one hole beside this: a program that holds a pseudo-terminal passes spark's terminal test. I ran it, and it does (section 4, the consent seam).
7. An edit has no home in P1193's kept steps yet, and the page's fingerprint reads nothing in `firmware/` [E scripts/spark/flow/fingerprint.py:17, checked by me]. A save needs its own guard and a row in P1193's kept records.
8. My opinion on the smallest set: one new Operation, `show-firmware`, in the firmware area's table, read once into `FlowReading`, drawn as one fold of the page. Everything else stays a named seam until the PO answers round 1 below.
9. My opinion on the riskiest assumption: that he wants to change firmware with his own hands on a page. Its cheapest test is one account question, with a pass line written below before any answer.

## 1. Where the lenses agree, and where they split

### Agree

- A1. Showing is the cheap feature, and it needs no host ability beyond showing the page [H TL-8, AR-1]. The page writer already reads the secrets and refuses a page when a secrets file cannot be parsed [E scripts/spark/flow/write_flow_page.py:31-34, :138-143, checked by me].
- A2. `pins.py` is shown and never edited. Spark rewrites a file that carries its header, and leaves a file without the header alone forever [E scripts/spark/build/kept_files.py:449-461, scripts/spark/design/pin_assigner.py:484-485, :562, checked by me] [H UX-11, AR-3, TL-9].
- A3. The Artifact in a browser cannot flash over Web Serial [H PO-4, UX-12, TL-17, all from hosts.md:8-25]. Nobody pressed a "pick a port" button in an Artifact [E hosts.md:24-25].
- A4. A page yes is a relayed yes. Spark cannot tell a person's click from an agent's write, because Claude carries the row and "Never write a key or a `seen` of your own" is an instruction, not a check [E commands/page.md:84-85, checked by me] [H AR-6, UX-6, TL-2].
- A5. A deploy pipeline written a second time in JavaScript is rejected by every lens that sized it. The Python pipeline is 17 files and 3,559 lines [E `wc -l` of the 17 files TL-5 names, rerun by me, same total] [H TL-5, AR-5 c, PO-11].
- A6. The desktop app's `pty` passes `Terminal.live`, and the page's script holds the input side [H PO-10, TL-3, AR-6]. Section 4 has my run.
- A7. The fingerprint is not the staleness guard for an edit. A save needs the sha256 of the bytes the page showed [H PO-8, UX-8, TL-9, AR-2].
- A8. Secrets block two things. A literal typed into `main.py` is masked nowhere, because the rule names only `firmware/*secret*.py` [E scripts/spark/firmware/project_secrets.py:1-5, :34, checked by me]. The flash image holds every file under `firmware/`, a secrets file too [E scripts/spark/firmware/image_builder.py:38-42, scripts/spark/build/ignore_list.py:1-5, checked by me] [H PO-9, TL-7, TL-8, AR-1, UX-16].
- A9. The firmware is in no kept step of P1193. It needs a row that the firmware area declares [H PO-7, AR-3, TL-9] [E the P1193 brief on branch restore-after-1775, lines 18 and 76, checked by me].
- A10. An edit followed by a deploy needs the image build on the core first. `scripts/flash_image.py` holds no `run_cli` [E `grep -c run_cli`, 0, rerun by me] [H TL-10, AR-1].
- A11. P218 D11's condition for a browser flasher has not fired. The condition is "revisit only for a first install by a person with no Python" [E docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:97, checked by me] [H PO-3, UX-13].
- A12. A browser makes the write no faster. The time is a baud choice [H PO-13, PH-9]. The 109 s for 4 MB is on the card P1146 #1681 already [E `gh issue list --search "109 s"`, run by me].
- A13. The desktop host serves the PO alone, and its Allow dialog returns after each republish [H TL-15, UX-7, from hosts.md:42-50].

### Split

- S1. How an edit travels. The architecture lens offers a text payload beside the key (AR-2 a, cost M) or a sentence for the chat (AR-2 b, cost S). The PO assistant says editing waits for an observed need (PO-2). The user lens says an edit from the Artifact saves nothing over the chat under today's carry (UX-17), and that the likely edit is one constant (UX-2). The tech lead gives only the save's shape (TL-9). Becomes SQ5.
- S2. Which host carries a deploy. The tech lead prefers a local server that the person starts in their own terminal, because the typed yes stays as it is (TL-4). The architecture lens rates the desktop app's `childProcess` at cost S (AR-5 d). The user lens counts about 7 Allow dialogs in about 20 minutes for the desktop host (UX-7). The PO assistant's pre-mortem says nobody starts either (PO pre-mortem, line 4). Becomes SQ6.
- S3. What is built now. The architecture lens proposes two seams in code now, the firmware table with `show-firmware` and a `HOST_FEATURES` table (AR-8 b). The PO assistant says the epic moves no basic project closer to working firmware today (PO-1). The git discovery's D12 says "only the seams now" and "nothing for a server is built" [D the PO, 2026-11-25, docs/discovery/2026-11-25-spark-and-git/brief.md:129, checked by me]. Becomes SQ4 and SQ17.
- S4. A feature the host lacks. The architecture lens lets the page's probe only hide a button (AR-4). The user lens says a hidden feature with no reason is today's flaw, and asks for hide or greyed out with why (UX-12, QD4). Becomes SQ11.
- S5. One write path or two. The architecture lens offers that Claude writes `main.py` through `save-firmware` too (AR-3). The standing rule says the conversation writes the firmware [E AGENTS.md, "Spark exports facts, never behaviour"]. The user lens says Claude needs a record it reads at its next turn, whoever wrote (UX-9, UX-19). Becomes SQ15.
- S6. What the page leads with. The user lens says a read-back in plain words may serve him more than an edit box (UX-15). The tech lead and the architecture lens lead with the file text (TL-8, AR-1). Becomes option (b) of D-q1 and SQ13.
- S7. Whether a yes typed into a terminal that a page opened is the person's typed yes. Three lenses ask the same question and none answers it (PO-10, TL-3, AR-6). Becomes SQ9.
- S8. The shape of a browser flasher, if one ever comes. The architecture lens names the browser as a port under spark's Python (AR-5 a) or as an executor of spark's plan (AR-5 b). The tech lead names spark's core in the page through Pyodide (TL-12). All three are untested. This matters only if SQ16 reopens D-a.

### Settled by the code, so no question

- C1. research.md:84 and :89 assume that a deploy writes project files over the raw REPL. The code writes one image at 0x0 with the files inside it, then copies only `spark.json` [E scripts/spark/firmware/image_builder.py:4-12, scripts/spark/bench/flasher.py:41-42, :80-82, checked by me] [H TL-1]. The tech lead is right. The brief's physics question should say so.
- C2. UX-15 says 11 of the 28 deploys of p934-display2 ended `ready unknown`, 7 typed and 4 under the standing yes. My read of the same store record gives 10 of 28: 7 typed and 3 under the standing yes, with 18 `ready seen` [E the store's `boards/` record for that board, counted by me 2026-11-26]. The other numbers of UX-3 hold: 28 deploys, 21 images, 24 typed, 4 under the standing yes.
- C3. The lenses cite `run_request.py:84-85` for the refusal of a chat kind. The lines are 96-97 [E scripts/spark/flow/run_request.py:96-97, checked by me].
- C4. P218's D19 says the token binds "the port, the MAC and the image" [E docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:161, checked by me]. The code binds the MAC and the image only [E scripts/spark/bench/board_look.py:397-401, checked by me] [H TL-16]. This is outside the item. Section 8 proposes it separately.

## 2. The decisions D-q1 to D-q5: options

Cost is S, M or L. "Would prove" is what a pass shows. No option is chosen here.

### D-q1: what the page shows of the firmware

| option | cost | what it would prove | whose opinion |
|---|---|---|---|
| (a) `main.py` and `pins.py` as masked, read-only text in one fold, each with who writes it and when it was written. The pin table stays P889 #1259. The read-back stays the deploy phase's line of today | S | A new area joins the catalogue, and the page and `show` read the firmware once. Whether he opens the fold | the tech lead (TL-8), the PO assistant (PO-2, "the show half has a thinner but real case"), the architecture lens (AR-8 b). Mine, as the first slice (my opinion) |
| (b) Option (a), plus every file the conversation wrote under `firmware/`, plus the read-back in plain words: for each file "matches", "differs" or "not read", from the newest board log | M | That the page answers "what does the board run" after a deploy that ended `ready unknown` | the user lens (UX-15). Mine, as the second slice (my opinion) |
| (c) A table of the named constants of `main.py` only, since his changes were single values (UX-2) | M | That a constants view covers his real edits | nobody recommends it first. The user lens raises it (QA2). I list it as a rabbit hole in section 6 (my opinion), because spark would start to read meaning into firmware |

Open inside D-q1: whether "the generated code" means `pins.py` only or `main.py` too [H UX-18]. Spark generates only `pins.py` [E scripts/spark/build/kept_files.py:27, checked by me].

### D-q2: whether a person edits the firmware on the page, and how the edit travels

| option | cost | what it would prove | whose opinion |
|---|---|---|---|
| (a) No edit box. The fold shows the text, and a chat offer gives one sentence with Copy, such as "Change a value in the firmware". Claude makes the change in the conversation | S | Whether a view plus a sentence covers the single-value changes he caused (UX-2) | the PO assistant (PO-2), the user lens (UX-17), the architecture lens (AR-2 b). It matches P1194's D17, "an Ask Claude sentence now" [D the PO, 2026-11-26, docs/discovery/2026-11-26-p1194-settings/brief.md:135, checked by me]. Mine (my opinion) |
| (b) An edit on the page. The request carries a key from spark's offer and the text as a payload. A new Operation `save-firmware` guards it and writes the file. The step is kept through P1193's Service | M for the Operation and its guard, L with the page's widget and the kept step, which waits on P1152 #1688 | That a text edit crosses the request rule safely, lands in `firmware/main.py`, and the conversation and the timeline see it | the architecture lens as the shape if he wants it (AR-2 a), the tech lead for the guard (TL-9) |
| (c) The host writes the file itself, for example the desktop app's `fs` module | S | Nothing about the core | rejected by the architecture lens (AR-2 c). I agree (my opinion): every rule of (b) is then written again in the page or lost |

Two questions hang on (b) only: which write wins when the page and Claude both changed the file (QD3), and whether a Send on the page counts as "his yes" of P1193's D14 (AR-3).

### D-q3: whether a deploy starts from the page, and through which path

Every option must keep three things: the look at the board first, the person's yes, and the read-back. I say for each how.

| option | cost | what it would prove | whose opinion | how the look, the yes and the read-back hold |
|---|---|---|---|---|
| (a) No start from the page. The page shows the deploy step: the look's result, the caveats, the line to type with Copy, and the last read-back | S | Whether the friction was the words and the copying, as the 2026-11-25 notes say (UX-4) | the user lens (UX-4, UX-17), the PO assistant (PO-3, PO-13). Mine (my opinion) | Unchanged. It is today's `/spark:deploy` [E commands/deploy.md:2, checked by me] |
| (b) The page starts spark's own `look` and `deploy` on a host that runs a program. The yes is a standing deploy grant that he typed before in his own terminal, or a yes typed in the terminal that a local server runs in | M once such a host exists, L counting the host | That one pipeline serves a page with no second copy, and that the gate needs no change | the tech lead (TL-4, TL-13), the architecture lens (AR-5 d, AR-6 i). Mine, if he reopens his D9 at all (my opinion) | The same `DeployService` runs plan, look, gate, flash, verify. The grant is `StandingConsentStrategy`, which opens the erase [E scripts/spark/bench/board_grant.py:243-268, checked by me]. The page's click itself stays relayed |
| (c) The browser flashes over Web Serial with esptool-js, on a localhost page or on a server of spark's own | L | A deploy for a person with no Python, the case of the card #159 | nobody recommends it now. D-a stands [D the PO, 2026-10-13, P218 D11] | It does not hold as written. The page's erase is a call the page makes, so `require_open_gate` is never reached [H TL-2]. It holds only if Python keeps the pipeline and the browser is its port (AR-5 a) or its executor (AR-5 b). Both are untested |

Option (b) reopens the PO's own D9, a click is his yes "never for the board or a simulation" [D the PO, 2026-11-15, docs/discovery/2026-11-15-p820-artifact-interface/brief.md:182, checked by me], and the MVP plan's line 188 [E docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md:188, checked by me]. The Deploy-button no-go itself was a proposal in P820, confirmed by a delegated council in P1038's D24 [E docs/discovery/2026-11-23-p1038-page-design/brief.md:80, :141, checked by me] [H PO-5].

### D-q4: which host offers which feature

| option | cost | what it would prove | whose opinion |
|---|---|---|---|
| (a) The Artifact in a browser stays the one host. The table of section 3 is kept as a document with a date on each cell | none | Nothing new. It keeps the MVP's page as it is | the PO assistant (PO-1). Mine, for now (my opinion) |
| (b) A local server on localhost becomes the second host. Spark serves `page.html`, takes requests, and runs Operations through `run_operation`. It is started in the person's own terminal | L | That the page acts without `/spark:page`, and that a deploy keeps the typed yes | the tech lead (TL-4, TL-13, with TL-14's origin check and per-run secret) |
| (c) The Artifact installed as a desktop app becomes the second host, after a desk spike with no board | S for the spike, M to use it | Whether a host that exists today can run spark's Python for the PO's own artifact | the architecture lens (AR-5 d). The PO assistant names it the one new route since D11 (PO-4) |

A server of spark's own is not an option here. Nothing for a server is built [D the PO, 2026-11-25, the git discovery's D12], and a hosted server is out of P820's scope [E docs/discovery/2026-11-15-p820-artifact-interface/brief.md:20, cited by preanalysis.md:244, not rechecked]. My opinion: take (a), and widen the open spike P494 #674 with the desk tests of TL-17 before choosing between (b) and (c).

### D-q5: the seams and their settings

| option | cost | what it would prove | whose opinion |
|---|---|---|---|
| (a) Names only. The seams and the settings stay in the design, and the host table stays a document | none | Nothing in code | the architecture lens lists it (AR-8 a) |
| (b) One seam in code that no later choice changes: `show-firmware` in the firmware area's table, read once into `FlowReading`. The settings rows of section 5 go to P1194 as proposals. The host table stays a document until a second host is chosen | S | That a new area's Operation reaches the CLI, `--describe`, the page and a later MCP server from one place | mine (my opinion). It is AR-8 b without the host table in code |
| (c) Option (b), plus the host table in code, plus `save-firmware` with its guard, `build-image` on the core and a `carry-requests` Operation | M to L | The base for any page edit and any page deploy | the architecture lens lists it (AR-8 b for the host table, AR-8 c for the rest) |

Why I leave the host table out of code for now: the first slice, showing, needs no host ability. A table with one real host is structure for a host that does not exist, which the git discovery lists as a proposed no-go [E docs/discovery/2026-11-25-spark-and-git/brief.md:81, checked by me]. The architecture lens disagrees (S3). SQ17 asks.

## 3. The table of features by host

No feature of this table is built. So "works" appears only where today's code already does that job. "Does not work" means evidence says the host refuses it. "Not tested" means nobody ran it, and the note says whether a route exists. I split two rows, because each holds two different jobs.

| feature | the Artifact in a browser | the Artifact installed as a desktop app | a local server on localhost | a server of spark's own |
|---|---|---|---|---|
| 1. show `main.py` | not tested. A route exists (n1) | not tested. The same page (n2) | not tested. No server exists (n3) | not tested. Nothing is built (n4) |
| 2. show `pins.py` and the pin map | not tested. A route exists (n1, n5) | not tested (n2, n5) | not tested (n3, n5) | not tested (n4, n5) |
| 3a. show the last recorded read-back | works in part, by the code (n6) | not tested in that window (n2, n6) | not tested (n3, n6) | not tested (n4) |
| 3b. read the board again now | does not work (n7) | not tested. Condition: after a full-access Allow (n8) | not tested (n9) | does not work for spark's Python. Not tested for the browser (n10) |
| 4. save an edit of `main.py` | does not work today (n11) | not tested. Condition: after a full-access Allow (n12) | not tested (n13) | not tested. Nothing is built (n4) |
| 5a. start a deploy, spark's own deploy on his computer | does not work (n14) | not tested. Conditions: after a full-access Allow, and with a yes the gate accepts (n15) | not tested (n16) | does not work (n10) |
| 5b. start a deploy, the browser over Web Serial | does not work (n17) | not tested (n18) | not tested, and it skips spark's gate (n19) | not tested, and it skips spark's gate (n20) |

Notes, each with its evidence and its condition:

- n1. The page writer bakes text into `page.html` and masks it with the project's secrets [E scripts/spark/flow/write_flow_page.py:138-143, checked by me]. `/spark:page` publishes that file as the Artifact [E commands/page.md:40-42, checked by me]. No section holds firmware text today [E preanalysis.md:180-182]. Conditions: the rendered page stays under 16 MiB [E https://code.claude.com/docs/en/artifacts.md, "Page constraints", checked by me 2026-11-26], and a literal secret in `main.py` is handled first (A8).
- n2. The installed app shows the same published page in its own window [E hosts.md:38-41]. Nobody installed spark's page as an app [H UX-13, "whether he ever installed an artifact as an app is —"].
- n3. Spark has no local server. A grep of `scripts/` and `tools/` found none [E preanalysis.md:333-334, not rechecked]. A server would serve the same `page.html` [H research.md:131-133].
- n4. Nothing for a server is built [D the PO, 2026-11-25, the git discovery's D12].
- n5. `pins.py` is one more file under `firmware/`, with spark's header. The pin map as a table is the card P889 #1259, not built [E `gh issue view 1259`, run by me]. Both come from the design's pin assignment [E scripts/spark/build/kept_files.py:449-472, checked by me].
- n6. The deploy phase reads the newest board log: its time, image, verdict and cause [E scripts/spark/flow/deploy_reading.py:1-6, :44-60, scripts/spark/flow/phase_readers.py:571-587, checked by me]. It never shows the facts line or a file's own result [E phase_readers.py:572-574]. I did not open a published page to see the line. The walk's page of 2026-11-22 said "not started" beside logged deploys [H UX-5, from P1038 brief.md:54, not rechecked].
- n7. "Look at the board" is a chat offer, so the page never sends it [E scripts/spark/flow/flow_codes.py:157, :159-160, checked by me], and `run-request` refuses a chat kind [E scripts/spark/flow/run_request.py:96-97, checked by me]. The frame cannot reach another host or a program [E hosts.md:26-28] [E the Artifact doc, "fetch, XHR, and WebSocket calls reach only the page's own origin", checked by me].
- n8. `claude.use("desktop")` gives `childProcess` after a "full-access" Allow, only on an artifact of the person's own organization [E hosts.md:38-44]. `childProcess` could run `look.py`. Not run by anyone. The Allow ends when a newer published version loads [E hosts.md:48-50].
- n9. A server process on his computer can run `look` through `run_operation` [H TL-13]. Not built.
- n10. Spark's Python on a remote server cannot reach his USB port. Only his browser could, over Web Serial [H research.md:134].
- n11. A request row holds `id`, `key`, `seen` and `at`, and no text [E scripts/spark/flow/page_script.ts:53-59, checked by me]. `run-request` takes "The values of the step" from "spark's own offer key, never from the request" [E scripts/spark/flow/run_request.py:1-5, checked by me]. One route exists today as a mechanism: a sentence with Copy that the person pastes into the chat [E scripts/spark/flow/page_script.ts:7-8, checked by me]. The host's own guide names this pattern: "An artifact can act as a lightweight editor for a decision you then send back to Claude" [E the Artifact doc, "Bring the result back to your session", checked by me].
- n12. `fs` could write the file directly, which every lens that looked rejects (D-q2 c). `childProcess` could run a `save-firmware` that does not exist yet.
- n13. Not built. The server would call `save-firmware` through `run_operation` [H TL-13].
- n14. Three facts, each enough. The frame runs no program (n7). `deploy` is not among the three steps the page may run [E scripts/spark/flow/run_request.py:44, checked by me]. A carried click is a relayed yes, and the gate refuses it [E scripts/spark/bench/deploy_gate.py:184-185, checked by me].
- n15. `childProcess` could run `deploy.py`. With no terminal it exits 2 and prints the line for his own terminal, unless a deploy grant stands [H TL-2, from deploy_gate.py:107-109]. Under the app's `pty` the terminal test passes, and that is the hole of section 4. Nobody ran any of it.
- n16. A server started in his own terminal asks the erase question in that terminal [H TL-4, not built and not tried]. It needs an origin check and a per-run secret, or any web page he opens can reach it [H TL-14, model knowledge].
- n17. The frame's `allow` attribute names no `serial` and no `usb` [E hosts.md:8-19, one artifact, one browser, one day]. The default allowlist of `serial` is `'self'`, and `requestPort()` rejects for a document that is not allowed to use it [E https://serial.spec.whatwg.org/, sections 6.1 and 3.1, checked by me]. Safari has no Web Serial at all [E research.md:47].
- n18. The desktop types name camera, microphone and location, and not serial or USB [E hosts.md:45-47]. Not tested.
- n19. `http://localhost` is a secure context, so Web Serial can work there with no certificate [H research.md:132]. The physics is untested on the boards spark knows: the S3 under MicroPython cannot be reset into its bootloader by DTR and RTS [E docs/discovery/2026-10-31-p472-no-hands/finding.md:5-9, checked by me] [H PH-3], and a page cannot open the C6's port with DTR and RTS off, because `open()` takes no signal option [E https://serial.spec.whatwg.org/ section 4.4.1, checked by me] [H PH-5].
- n20. As n19, and the server must serve HTTPS [E research.md:134]. D-a stands.

## 4. The seams

### The diagram

```text
 INTERFACES (thin: they parse, carry and print)

   CLI, and Claude in the chat        the page (page.html and its one script)          MCP, later
        |                                 |
        |                                 |  HOST SEAM (flow area): which host shows this page, and what it can carry
        |                                 |     artifact (today) | desktop app | local server | (a server of spark's own)
        |                                 |  CARRIER SEAM: RequestChannel, with DbChannel as its one member today
        |                                 |     the row is {id, key, seen, at}. A text payload joins only if D-q2 says so
        |                                 v
        |                     Claude carries it (/spark:page), or a host that runs a program calls the core itself
        |                                 |
        v                                 v
 CORE   run_operation  <-------------  run-request (flow): the key comes from spark's own offer
        |
        +-- firmware area  (its table arrives with P1208 #1757, check-firmware)
        |     show-firmware    reads              NEW    one read of firmware/: each file, who writes it, its sha256,
        |                                                its masked text, or "a secrets file, not shown"
        |     save-firmware    reads, writes      LATER  guard: a listed file, the sha256 of the text shown,
        |                                                a size cap, a compile check, then a kept step
        |     build-image      reads, runs, writes LATER wraps image_builder (flash_image.py, a line on P793 #1105)
        |
        +-- flow area  (exists)
        |     show-flow and write-flow-page: FlowReading is read once. One more entry of FlowHtmlPage.SECTIONS draws the fold
        |
        +-- bench area  (all of it exists)
        |     look, then deploy: DEPLOY_STAGES   plan > look > gate > flash > verify      (one DeployService)
        |                                                   |       |        |
        |        CONSENT SEAM: ConsentStrategy -------------+       |        +-- ReadyProbe over BoardConnection (mpremote)
        |           typed in his own terminal    opens              |
        |           a deploy grant typed before  opens      FLASHER SEAM: FirmwarePlatform.make_flasher() gives a Flasher
        |           relayed (a page, MCP)        stays shut    EsptoolFlasher builds argv lists, tools-list role "flasher"
        |                                                      a browser flasher has no argv and no Python look,
        |                                                      so it is no member here. A port that Python reaches
        |                                                      would be a kind of port, under the same pipeline
        |
        +-- records area  (P1152 #1688, not built)
              ProjectTimeline.keep_step(kind, words)
                 KeptRecords row "firmware": the files the conversation or the person wrote.
                                             Never pins.py, never a secrets file
                 FolderTimeline: git | none | by hand         tools-list role "project-timeline"

 SETTINGS (P1194's seam): the page host, the firmware view, the firmware edit, a deploy start on the page,
                          the firmware on a shared copy
```

### The Operations each feature needs, and the area that owns each

| feature | Operation (working name) | area | today | effects |
|---|---|---|---|---|
| show `main.py`, show `pins.py` | `show-firmware` | firmware | not built | reads |
| the same text on the page | `show-flow` and `write-flow-page`, through `FlowReading` | flow | exist, hold no firmware text | reads. reads, writes |
| the pin map as a table | inside the same reading, from the design (P889 #1259) | flow, reading design's pin assignment | not built | reads |
| the last recorded read-back | `show-flow`, the deploy phase | flow, reading bench's board log | exists | reads |
| read the board again now | `look`, `show-bench` | bench | exist | reads, runs, board, asks. reads, runs |
| save an edit of `main.py` | `save-firmware` | firmware | not built | reads, writes |
| keep the edit as a step | P1152's Operations over `ProjectTimeline.keep_step` | records, as P1152 #1688 decides | not built | — |
| build the image of the edit | `build-image` | firmware | a CLI off the core | reads, runs, writes |
| check the edit | `check-firmware` (P1208 #1757) | firmware | planned | — |
| start a deploy | `look`, then `deploy` | bench | exist | reads, runs, board, deletes, writes, asks |
| carry a page click | `run-request` | flow | exists, three steps | reads, runs, writes |

Evidence for the "today" column: the catalogue lists eight tables and no firmware table [E scripts/spark/operation_catalogue.py:15-28, checked by me]. The bench table holds `look`, `deploy` and `show-bench` [E scripts/spark/bench/__init__.py:25-26, checked by me]. The firmware area keeps its table in `firmware_operations.py` by the convention [E docs/guide/patterns-and-names.md:40]. P1208 #1757 moves `import_firmware.py` onto the core, and the `flash_image` move is a line on P793 #1105 [E `gh issue view 1757` and `1582`, run by me].

One name to avoid: the lenses say "a firmware reader in the firmware area". `phase_readers.FirmwareReader` already is the Strategy that reads the firmware phase [E scripts/spark/flow/phase_readers.py:532, checked by me]. One word has one meaning (patterns-and-names.md, rule 1). My working name for the new Value is `FirmwareFiles` (my opinion).

### The host capability seam

Today the seam is one column: `OfferKind.from_page` says whether the page sends a kind or the chat asks it [E scripts/spark/flow/flow_codes.py:147, :159-160, checked by me]. The page's script also gates itself on its host: it starts only with the Artifact database and only for the owner [E scripts/spark/flow/page_script.ts:452-460, checked by me].

The architecture lens proposes one table with a cell for each host and feature (AR-4). My opinion: do not write those cells by hand. Write two small tables and render the third from them.

- One row per host says what the host can carry: show the page, carry a key, carry text, run an Operation without Claude, reach a serial port. Each cell has its verdict, its evidence and the date it was read.
- Each offer kind names what it needs from the host. `from_page` is that column today.
- The table of section 3 is then a rendered view, as `StageMarkdownTable` renders the build's stages [E docs/guide/patterns-and-names.md:40]. A new host is one row. A new feature is one row. No cell is written twice.

The page may run a probe, for example for `navigator.serial`. It may only switch between two states whose words Python wrote, as it does for a request's states today [E scripts/spark/flow/page_script.ts:8-9, checked by me]. So the script still decides nothing about spark. Whether the weaker state is hidden or greyed out with its reason is S4 and SQ11.

When this becomes code is S3. Until a second host is chosen, the table is a document.

### The editor seam

"Editor" hides three separate things. Keeping them apart is what makes each one exchangeable.

1. What may be edited. This is the core's list inside `save-firmware`: the files under `firmware/` that the conversation or the person wrote. Never a file with spark's `pins.py` header, never a file that `is_secret_file` names [E scripts/spark/firmware/project_secrets.py:34, checked by me], never a path from the request.
2. How the edit travels: the carrier. Members: a sentence for the chat with Copy (the mechanism exists), a request row with a text payload through `RequestChannel` [E scripts/spark/flow/page_script.ts:74-79, checked by me], or a host that calls the Operation itself. The core already has the shape for a payload: an `Argument` with `payload`, read by `cli.load_payloads` [E scripts/spark/core/operation.py:21-25, scripts/spark/core/cli.py:222, checked by me].
3. What the person types into: the widget. Members: none (read-only text), a plain textarea, or one library inlined in the page. It is chosen by a setting. Its bytes would be a tools-list entry of the kind `download`, fetched once and inlined, so the page still "loads nothing from the web" [E scripts/spark/records/tool_finder.py:542, checked by me] [D the PO, 2026-11-15, P820 D7, brief.md:180] [H AR-7].

The widget is where two earlier decisions bind. "No framework and no Node build" [D the PO, 2026-10-16, P269 D16, docs/discovery/2026-10-16-p269-views-and-editors/brief.md:115, checked by me] rules out CodeMirror 6, whose docs advise a bundler, and Monaco [E research.md:103, :105]. CodeMirror 5 is one file and is archived [E research.md:104].

The guard of `save-firmware`, in one place for every carrier [H AR-2 a, TL-9]: the file is on the list. The sha256 of the text the page showed equals the file on disk now, so an edit never overwrites a newer write. A size cap. A compile check through the existing `CompileCheck` [E scripts/spark/bench/image_evidence.py:124, checked by me]. The answer never echoes the text, as a refusal never echoes a request today [E scripts/spark/flow/run_request.py:129-132, checked by me]. The fingerprint is not widened, because adding `main.py` to it would make every pick and build click stale after any firmware write [H AR-2].

### The flasher seam, and why a browser flasher is not one more member

The seam that exists has three layers. `Flasher` builds the commands, and "nothing here touches USB" [E scripts/spark/bench/flasher.py:1-6, :18-34, checked by me]. `FirmwarePlatform` builds every board tool for one firmware language [E scripts/spark/bench/firmware_platform.py:37-79, checked by me]. The tools list maps the roles `flasher` and `board-shell` to esptool and mpremote [E data/tools.json, the `roles` key, printed by me].

A browser flasher fails the membership test on four counts:

1. `build_commands` returns argv lists, and `DeployService` runs them through `outside.run`. esptool-js is a library with no argv [E flasher.py:32-34] [H TL-11].
2. The token is "4 hex of sha256(MAC), a dash, 4 hex of sha256(image)", made by the look that Python ran [E scripts/spark/bench/board_look.py:397-401]. In a browser, no Python process sees the port [H AR-5].
3. The verify's recovery (find the port by the MAC, read the console, wait for RESET, the quiet open) is Python over mpremote [H TL-5, not rechecked beyond the line count].
4. A tools-list role names a program that spark finds and runs [H TL-11].

So the browser path, if it ever comes, does not enter at `Flasher`. It enters one level up, as the question "where does the board I/O run". The one shape that keeps a single pipeline is the browser as a port that Python reaches. esptool and mpremote both open their port through pyserial's `serial_for_url` [E the installed `esptool.py:320` (version 3.3 in the `python3` on the path) and `mpremote/transport_serial.py:70`, read by me. The architecture lens read esptool 5.5.0's `loader.py:455`, which I did not find in this Python]. Whether the reset lines survive such a bridge is — [H AR-5 a].

For a host that already runs a program on his computer (the desktop app, a local server), this seam does not change at all. The host starts the existing `deploy`. That is why D-q3 (b) costs nothing in the bench area.

### The consent seam

`ConsentStrategy` is the seam, and `opens_erase` is False unless a member sets it [E scripts/spark/bench/deploy_gate.py:52-59, checked by me]. Three members exist: typed in a real terminal (opens), a standing deploy grant (opens), relayed by another program (stays shut) [E deploy_gate.py:92-97, :117-126, board_grant.py:243-249, checked by me]. Each frontend hands its own member through `make_consent` [E scripts/spark/bench/__init__.py:29-42, checked by me]. A page host is a frontend, so it hands a relayed yes by construction, and the gate refuses it after the token checks [E deploy_gate.py:184-185].

Three paths open the erase for a deploy that a page starts [H AR-6]:

- (i) A deploy grant that he typed earlier in his own terminal. The page's click only starts a deploy inside that grant. The gate does not change. P1194's D19 keeps the grant as it is [E docs/discovery/2026-11-26-p1194-settings/brief.md:137, checked by me].
- (ii) A local server started in his own terminal. The question appears there, and he types the yes there [H TL-4, not built].
- (iii) A new member with `opens_erase = True` for a page yes. This reopens P675 and P218's D19, both the PO's.

The hole. `Terminal.live` is `stdin.isatty() and stdout.isatty()` [E scripts/spark/core/replies.py:157-158, checked by me]. I ran spark's own `TerminalConsentStrategy` in a child process under a pseudo-terminal, in a temporary folder that I removed. The parent program wrote `yes` into it. The result line was `live=True yes_kind=typed opens_erase=True ask_returned=True`. Under a pipe the same child stopped with "no terminal to ask you in" [E my run, 2026-11-26, Python's `pty` module on macOS, n = 1, no board, no deploy]. So a typed yes proves a tty, not a person. The gate's own docstring says it "guards against a frontend's mistake, not against code in the same process" [E deploy_gate.py:55-56]. What I did not test: the desktop app's own `pty` module. The finding is outside this item, and section 8 proposes it separately.

### The path from an edit to P1193's kept steps

```text
 an edit on the page
   -> the carrier (a sentence for the chat, or a row with a payload)
   -> save-firmware: the guard, then the write of firmware/main.py
   -> ProjectTimeline.keep_step("firmware", words)        one Service for every kept step
   -> FolderTimeline, the member the tools-list role names  (git first)
   -> the answer names the kept step, so the conversation reads it at its next turn
```

- P1193 already rules that a page edit is "a kept step through the same Service", with "no second seam" [E the P1193 items.md on branch restore-after-1775, line 56, checked by me].
- No code of the project timeline exists yet [E the P1193 brief, line 46, checked by me]. The card is P1152 #1688.
- The firmware needs a row in `KeptRecords`. The synthesis of P1193 chose "each area declares its kept records in one table" [E the P1193 brief, lines 76 and 117, checked by me]. `main.py` fits a row more simply than the layout files, because spark never writes it [H AR-3].
- `pins.py` stays a build output that is made again [E the P1193 brief, line 18, D-d].
- D14 lets spark commit one named file of a declared kept record after his yes [D the PO, 2026-11-26, the P1193 brief, line 125, checked by me]. Whether a Send on the page is that yes: —.
- A take-back can split a pair: an older `pins.py` under a newer `main.py` that imports a signal that is gone [H AR-3, not tested].
- When Claude writes `main.py` with its own tools, P1193's direction is "an outside change said and kept on a yes" [E the P1193 brief, line 117]. That is the second way to the same Service, not a second Service.

### Nothing is written twice

| concern | its one home | who reads it |
|---|---|---|
| which files are firmware, and who writes each | `FirmwareFiles` in the firmware area, using `is_secret_file` and `PIN_MODULE_HEADER` | `show-firmware`, `FlowReading`, `save-firmware`'s list |
| the mask of a secret | `ProjectSecrets` and the run's Privacy step | every Operation's result, the page writer |
| the firmware's text for a person | `FlowReading`, read once [E scripts/spark/flow/flow_reading.py:1-4] | `show`, the page, a later MCP tool |
| whether an edit is stale | the base sha256 in `save-firmware` | every carrier |
| whether the firmware compiles | `image_evidence.CompileCheck` | the look with `--no-simulation`, `save-firmware` |
| the flash image | `image_builder`, behind `build-image` | the simulation, the deploy |
| the deploy's stages and their order | `DEPLOY_STAGES` and `DeployService` | the CLI's headings, a page's stages block, every host |
| who may open the erase | the `ConsentStrategy` members | `require_open_gate` only |
| a kept step | `ProjectTimeline.keep_step` | the page edit, the layout edit, P1152's Operations |
| which member a seam uses | P1194's settings seam, and the tools list's roles | each builder |
| what a host can carry | the host rows and each offer's need | the page writer, the docs, `--describe` |
| the steps a page may run | the catalogue, once P1082 #1587 derives the allow-list from it | `run-request` |

### The smallest set to build first

The git discovery's D12 says that for a website "only the seams now" and "nothing for a server is built". The epic itself is after the MVP [D the PO, 2026-11-26, #1748]. My opinion:

1. Build one thing when the epic's turn comes: `show-firmware`, the `FirmwareFiles` reading inside `FlowReading`, and one fold of the page. It is testable alone, it works on the one host that exists, and it reaches the CLI, `--describe` and the page from one place. It reuses the firmware area's table that P1208 #1757 brings.
2. Name the other seams and build none of them: the carrier's payload, `save-firmware`, `build-image`, the host rows, the port kind. Each has its place in the diagram, so a later card adds a member and changes no caller.
3. Build nothing for a deploy start, a second host or a server until SQ3 and SQ6 are answered.

Rejected for now (my opinion): AR-8 c, because it touches the MVP's click path for a need nobody observed. Also a `carry-requests` Operation, because in the Artifact only Claude's tools reach the page's database, so Python has no channel to mirror until a second host exists [E commands/page.md:77-78, :95, checked by me].

## 5. The settings

All are proposals until P1194 #1740 refines them. The layers are spark's default, the user and the project [D the PO, 2026-11-26, P1194 D11, brief.md:129, checked by me]. Every plan names its setting, default and layer [D the PO, 2026-11-26, P1194 D3, brief.md:121].

| setting (working name) | members | default | layer | the decision it comes from |
|---|---|---|---|---|
| the page host | artifact, desktop app, local server, file | artifact, as today | project, then user. The published id is per project today, in `.spark/page.json` | D-q4 |
| the firmware view on the page | off, text | text | user | D-q1 |
| the firmware on a shared copy of the page | hidden, shown with the mask | hidden | user only. P1194's D12 makes a setting that shares his data his alone [E brief.md:130] | D-q1, and A8 |
| a firmware edit from the page | off, a sentence for the chat, an edit on the page | a sentence for the chat | user. A project may only narrow it | D-q2 |
| the edit widget | textarea, an inlined library | textarea | user | D-q2, D-q5. It exists only if the edit on the page does |
| a deploy start on the page | off, on inside a standing grant | off | user only. It never answers a yes. P1194's proposed no-go is "no setting that answers a yes to write a board" [E brief.md:87] | D-q3, D-c |
| where the board I/O runs | this computer's Python, the browser as a port | this computer's Python | user. A project may only narrow it | D-q3, D-a. Not a setting until a second member exists |
| the tools-list role `flasher` | esptool | esptool | the tools list's own layers, kept by P1194's D15 [E brief.md:133] | D-a. Exists today |
| the tools-list role `board-shell` | mpremote | mpremote | the tools list's own layers | D-a. Exists today |
| the tools-list role `project-timeline` | git, none, by hand | git | the tools list's own layers | D-f. Proposed by P1193's D6, reused here |

Two things are rules, not settings (my opinion): a local server binds to 127.0.0.1 only [H research.md:131], and the editable list never holds `pins.py` or a secrets file.

## 6. Proposed no-gos and rabbit holes

Each line is a proposal until the PO confirms it.

Proposed no-gos:

- Proposal: no yes given on a page opens the erase. Not a click, not a database row, not the desktop window's Allow. D-d stands [E deploy_gate.py:117-126].
- Proposal: no deploy path skips `require_open_gate`. So no look, flash and verify written in the page's script [H AR-5 c, TL-2].
- Proposal: no spark frontend drives a terminal to answer an Operation whose effects hold `asks` (the hole of section 4).
- Proposal: no edit of `pins.py` from any interface. To move a pin, the person asks Claude to change the design [H UX-11].
- Proposal: a secrets file is never shown and never editable on the page, and firmware text is hidden on a shared copy by default [H UX-16, PO-9].
- Proposal: no flash image inside an Artifact, because the image holds the project's secrets [H TL-7, PO-9].
- Proposal: no write by a host's own file module. Every write goes through an Operation [H AR-2 c].
- Proposal: no library loaded from a CDN when the page is viewed. A library is inlined from pinned bytes or not used [D P820 D7].
- Proposal: no bundler and no Node build for the page. So no CodeMirror 6 and no Monaco now [D P269 D16].
- Proposal: no server of spark's own and no accounts in this epic [D the git discovery's D12]. Accounts are P1235 #1787.
- Proposal: spark derives nothing from an edit. It carries the person's bytes and judges only that they compile [D-e, AGENTS.md].
- Proposal: no REPL and no "run this code now" button in this epic. That is P235 #224.
- Proposal: no browser flasher until the card #159 is taken up. D-a stands.

Proposed rabbit holes:

- Proposal: spark's core in the page through Pyodide (TL-12).
- Proposal: a bridge that puts a Web Serial port under spark's Python (AR-5 a), and the plan-and-executor split (AR-5 b).
- Proposal: copying ViperIDE's raw-REPL code, or writing a raw-REPL driver in JavaScript [E research.md:92].
- Proposal: a constants-only editor that parses `main.py` to find the values a person may tune (D-q1 c).
- Proposal: merging a page edit with a change by Claude. A mismatch of the base hash refuses, and merge waits [D the PO, 2026-11-26, P1193 D15].
- Proposal: the browser matrix: WebUSB, Android, Firefox's add-on, Safari [E research.md:43-47, :62-66].
- Proposal: the S3's two USB product ids in Chrome's port chooser, and the C6's quiet open from a page (PH-4, PH-5).
- Proposal: curing the Allow dialog that returns after each republish. It belongs to a page state that changes without a republish (P836 #1198, and P1038's Done-when).
- Proposal: the `chan_` project id of the Artifact's `files` capability. P1038 already lists it [E P1038 brief.md:80].

## 7. Assumptions

Importance is the PO's to rate. Ten at most.

| id | belief | type | tag and evidence now | importance | cheapest test |
|---|---|---|---|---|---|
| A1 | He wants to read `main.py` and `pins.py` on the page, not in the chat or an editor | value | H. A wish on record twice (UX-18). No account of a moment | — (the PO) | account question SQ2, first half |
| A2 | He wants to change firmware with his own hands on a page, and telling Claude is not enough | value | H. Against it: 17 of 18 recorded commits of `main.py` carry a Claude co-author line (E via UX-1, not rechecked). His one hand edit was a Wi-Fi value in a secrets file (E via UX-1) | — (the PO) | account question SQ2 |
| A3 | After a deploy, his open question is what the board runs, and a read-back on the page answers it | value | H, from E: 10 of 28 deploys of one project ended `ready unknown` (the store's record, counted by me) | — (the PO) | account question SQ13 |
| A4 | The deploy's friction is the words and the copying, not the terminal itself | usability | H, from E: the notes of 2026-11-25 (E via UX-4, the store's bench-2026-11-25.md. I checked note 20 only) | — (the PO) | account question SQ14 |
| A5 | A person who saves an edit understands that the board still runs the old image | usability | H (UX-10). E for the mechanism: the board gets the image, not a newer file [E scripts/spark/firmware/project_image.py:121-125, checked by me] | — (the PO) | a paper sketch of the fold's "what comes next" line, read by him |
| A6 | The Artifact in a browser cannot open a serial port | feasibility | E for the attribute (hosts.md:8-19) and the standard (checked by me). H for the result, since nobody pressed | — (the PO) | the one-button test page of research.md:123, no board |
| A7 | The desktop-app host can run spark's Python for his own artifact, and he would use that host | feasibility | H, from E: the capability's types (hosts.md:38-44). Not run. Whether he uses the app: — | — (the PO) | account question SQ7, then the desk spike on P494 #674 |
| A8 | A yes on a page can be made by Claude, so it must stay relayed | ethics | E: Claude carries the row, and the rule is an instruction, not a check (commands/page.md:84-85). E: a program can also type the yes into a pseudo-terminal (my run) | — (the PO) | none needed for the first half. The desk spike for the app's `pty` |
| A9 | Firmware text and an image can carry a secret that no mask covers | ethics | E: the rule names only `firmware/*secret*.py` (project_secrets.py:1-5). H: a literal in `main.py` would be published. Not tested | — (the PO) | write a page from a scratch project with a fake literal in `main.py`, once the fold exists |
| A10 | The Artifact host stays stable enough to carry a host-specific feature | viability | H, from E: the contract moved twice in six days (P1038 brief.md:47, via preanalysis.md:234, not rechecked) | — (the PO) | read the contract version at each republish for two weeks |

The riskiest, in my opinion: A2. The most cost hangs on it. It alone brings a change of the request rule, a second guard, a kept-record row, an edit widget and two writers of one file. The only evidence on record points against it. Feasibility is not the riskiest, because it is close to settled: the Artifact cannot flash, and the deploy path that works is the one that exists. The PO assistant names nearly the same belief (T2), joined with A1.

Its cheapest test is an account question, with no build: SQ2 below, asked of the PO about his own past use (n = 1).

Proposed pass line, written on 2026-11-26 before any answer: he names at least one moment, by its day or its step, when he wanted to change a firmware value with his own hands and telling Claude was not enough. Then D-q2 (b) stays a candidate. If he names no such moment, D-q2 (a) is the answer for now, and the edit on the page stays a named seam behind its setting. Separately, for A1: he names one moment when he wanted to read `main.py` or `pins.py` himself, and where he looked.

## 8. Proposed items for the board

None is filed without the PO's yes. The main session numbers the new ones. "Widens" names the card that already covers the item. I searched the open issues for each new item and found no card for it (the searches are at the end).

| # | kind | title, or the comment | widens | slice |
|---|---|---|---|---|
| 1 | story (new) | the page shows the firmware as one file time, so a person cannot read what Claude wrote or what spark generated → `show-firmware` and one fold on the page: `main.py` and `pins.py` as masked, read-only text, each with who writes it and when | none found. Parent P1200 #1748. Depends on the firmware area's table (P1208 #1757) | Views and editors |
| 2 | comment | the pin table is the pin-map part of P1200's D-q1. It reads the design that `pins.py` is written from, so no second card is filed | P889 #1259 | Views and editors, as today |
| 3 | comment | the firmware fold shows this compare's result once it exists | P882 #1250 | Views and editors, as today |
| 4 | comment | widen to the read-back in plain words: for each file "matches", "differs" or "not read", from the newest board log (D-q1 b, UX-15) | P1217 #1766, with P1106 #1626 named beside it | v0.10 The basic journey, as today |
| 5 | comment | one more chat offer row: "Change a value in the firmware" (D-q2 a). The card already lists "a new image before a deploy" | P1132 #1666 | v0.10 The basic journey, as today |
| 6 | comment | widen the spike with desk tests that need no board: the serial test page in Chrome and in the desktop app, `childProcess` running `flow.py show`, whether the app's `pty` reports a tty and whether the page's script can write to it (TL-17). The result picks the second host | P494 #674 | Views and editors, as today |
| 7 | comment | P1200's table of features by host is this card's input. It becomes a guide page with a date on each cell | P834 #1196 | Views and editors, as today |
| 8 | comment | the firmware needs a row in the kept records: the files the conversation or the person wrote, never `pins.py`. It waits on SQ8 | P1152 #1688 | Project timeline, as today |
| 9 | comment | the `flash_image` line of piece 5 is the `build-image` Operation that any page deploy needs first (TL-10) | P793 #1105 | 10 The store, as today |
| 10 | comment | a step that carries text needs a second guard of its own. The allow-list does not cover it (AR-2) | P1082 #1587 | v0.10 The basic journey, as today |
| 11 | comment | the notes of 2026-11-25 are the evidence that lines which copy whole may remove the friction a page deploy was meant to remove (UX-4, D-q3 a) | P1144 #1679 | v0.10 The basic journey, as today |
| 12 | comment | the settings rows of this synthesis, section 5, as proposals | P1194 #1740 | as today |
| 13 | comment | the firmware fold depends on the secrets rule. A literal in `main.py` is masked nowhere, and an image never goes into an Artifact | P1004 #1463, with P1091 #1602 named beside it | v0.10 The basic journey, as today |
| 14 | comment | P218 D11's revisit condition lives on this card. research.md and the findings PH-3 to PH-7 are its inputs for a browser flasher | #159 | 5 A real stranger (the card has no slice today) |
| 15 | comment | two findings point here: the Allow dialog returns after each republish (UX-7), and a click waits for `/spark:page` (UX-17) | P836 #1198 | Views and editors, as today |
| 16 | comment | a server of spark's own implies accounts. Nothing is built for it (the git discovery's D12) | P1235 #1787 | as today |
| 17 | story (new, parked until SQ5) | an edit of `main.py` has no path from an interface that has no file tools → `save-firmware`: a listed file, the sha256 of the text shown, a size cap, a compile check and a kept step | none found. Parent P1200 #1748. Depends on P1152 #1688 | Views and editors |
| 18 | story (new, out of scope) | a yes that a program writes into a pseudo-terminal counts as typed and opens the erase → the guides say what a typed yes proves, a rule test keeps spark's own frontends from driving a terminal for an Operation that asks, and the PO decides whether the gate does more | none found. The gate's own card P675 #905 is closed | v0.11 Change it and put it on again, or the main session's choice |
| 19 | chore (new, out of scope) | P218's D19 says the token binds the port, the MAC and the image, and the code binds the MAC and the image → the guides and a note on the decision say what the token binds | none found | the main session's choice |
| 20 | story (new, out of scope) | the deploy never asks a running MicroPython S3 to enter its bootloader, so the person presses BOOT → a software entry before the erase, as P472's bench did twice | none found. P1047 #1537 is the nearest and is another thing | v0.11 Change it and put it on again |
| 21 | comment (out of scope) | the write's time is a baud choice: 109 s fits esptool's default baud (PH-9) | P1146 #1681 | v0.10 The basic journey, as today |

For item 20: a grep of `scripts/` finds no `bootloader()` [E my grep, 0 hits], and the bench measured the software entry on the S3 [E docs/discovery/2026-10-31-p472-no-hands/finding.md:5-9, checked by me] [H PH-3].

Not a board item, but a correction for this folder: research.md:84 and :89 and the brief's physics question (C1), and the count in UX-15 (C2).

## 9. A walking-skeleton story map

Proposed, not applied.

The backbone, as the person does it:

```text
 See the firmware  ->  See what the board runs  ->  Change a value  ->  Make the image  ->  Deploy  ->  Read the board back
```

| slice | activity | story | tag | proof the PO can read |
|---|---|---|---|---|
| 0 walking skeleton | See the firmware | the page's fold shows `main.py` and `pins.py` as masked text (item 1) | H A1 | `show-firmware --json` and the fold on a scratch project |
| 0 | See what the board runs | the deploy phase's line, as today | E n6 | the page of a project with a board log |
| 0 | Change a value | one "Ask Claude" sentence with Copy (item 5) | H A2 | the sentence pasted into the chat changes the value |
| 0 | Make the image | Claude runs `flash_image.py` in the chat, as today | E commands/deploy.md:118-124 | the new image's sha256 in the look |
| 0 | Deploy | the look, the line to type with Copy, his typed yes, as today | E commands/deploy.md:2 | the board log |
| 0 | Read the board back | the deploy's verify stage, as today | E deploy_stages.py:28 | `ready seen` on the page |
| 1 | See what the board runs | each file "matches", "differs" or "not read" (item 4) | H A3 | the page after a deploy that ended `ready unknown` |
| 2 | Change a value | `save-firmware` from the CLI, with the guard and a kept step (item 17) | H A2 | a refused save after Claude changed the file |
| 3 | Change a value | the edit on the page, carried as a payload | H A2 | the same refusal, from the page |
| 4 | Deploy | a second host, chosen by the spike (item 6) | H A7 | the spike's finding |
| 5 | Deploy | the page starts a deploy inside a standing grant (D-q3 b) | H | the board log names the grant as the yes |

The thinnest first slice is slice 0. It adds one new story and one row of offers. Every other step of the backbone already runs, on the one host that exists. Slices 2 to 5 wait on the answers of round 1.

## 10. The questions for the PO

Rounds of at most four. Each question stands alone. The first round holds the ones that change the most. "Mine" marks my opinion. He may delegate any technical one to the council, as his rules allow.

### Round 1

- SQ1 · decision · When you wrote "the generated code", which files did you mean? Example: `pins.py` is the only file spark generates, and Claude writes `main.py`. · options: `pins.py` only · `main.py` and `pins.py` · every file under `firmware/` except the secrets · decides: D-q1's reach, and whether D-q2 exists at all, since `pins.py` is never edited · mine: `main.py` and `pins.py`.
- SQ2 · account · In the display walk of 22 and 23 November, the picture was upside down and you timed the refresh at under 5 seconds. Did you want to change such a value yourself, or was telling Claude enough? And apart from the Wi-Fi value, did you ever open a firmware file yourself, and in which program? · decides: the riskiest assumption A2, and so D-q2 · the pass line is in section 7.
- SQ3 · decision · May a deploy ever start from the page? · options: no, the page shows the step, the line to type and the last read-back (today's rule) · yes, but only inside a standing yes that you typed before in your own terminal, on a host that runs spark's own deploy · yes, and a yes given on the page itself may open the erase · decides: D-q3, and whether your D9 of 2026-11-15 ("never for the board or a simulation") and P675 are reopened · mine: the first. The second is the only shape I would design if you want a start from the page.
- SQ4 · decision · When does any of this reach code? · options: nothing before the MVP walk, this discovery ends as a design · the show slice only (item 1), when the firmware area's table lands with P1208 · the show slice plus the save, the image build on the core and a request carrier · decides: D-q5's smallest set, and what "after the MVP" means for this epic · mine: the second.

### Round 2

- SQ5 · decision · How does a change to the firmware leave the page? · options: as a sentence that you paste into the chat, and Claude makes the change · as an edit on the page that spark's core checks and writes · not at all · decides: D-q2, the request rule of P820 and the kept-record row · mine: the sentence, unless SQ2 names a real moment.
- SQ6 · decision · Which second host, if any? · options: none now · a local server that you start in your own terminal · the Artifact installed as a desktop app · decide after the desk spike on P494 · decides: D-q4 and which column of the table gets tested first · mine: decide after the spike.
- SQ7 · account · Have you used the Claude desktop app for spark, and have you ever installed an artifact as an app? · decides: whether the desktop host is a real host for you (A7).
- SQ8 · decision · Is `firmware/main.py` a kept record of the project timeline, so a take-back can return it? · options: yes, with every file the conversation or you wrote under `firmware/` · only once an edit on the page exists · no, the firmware stays outside the timeline · decides: the firmware area's row in P1193's kept records, and whether a Send on the page can count as your yes for keeping the step · mine: yes, as a row, decided in P1152 and not here.

### Round 3

- SQ9 · decision · A page in the desktop app can open a terminal window. A yes typed there passes spark's terminal test, and the page's own script could type it too. Does such a yes count as typed in your own terminal? · options: no, it is a relayed yes, and spark's own interfaces never drive a terminal for a step that asks · yes, it is typed · decide after the desk spike · decides: the desktop host's deploy, and what P675 covers · mine: no.
- SQ10 · decision · May the firmware's text appear on a copy of the page that you shared? · options: never on a shared copy, the owner's private page only · on a shared copy too, with the mask · not on any page until secrets live in the store (P1004) · decides: the default of one setting, and the order of items 1 and 13 · mine: the first.
- SQ11 · decision · When a host cannot do a thing, what does the page show? Example: a deploy start in the Artifact in a browser. · options: nothing, the button is hidden · the button greyed out, with why and the sentence to ask Claude · decides: the face of the host seam for you and for Claude · mine: greyed out with why.
- SQ12 · decision · May the page carry a code library for an editor? · options: no library, plain text and a plain text box · one library inlined in the page from pinned bytes · a library loaded from a CDN when the page opens, which reopens P820's D7 · decides: the edit widget and the page's size · mine: no library until SQ5 says the edit is on the page.

### Round 4

- SQ13 · account · When a deploy ended "ready unknown" (10 of the 28 in the display walk), how did you find out what the board ran? · decides: whether the read-back comes before any edit (D-q1 b, A3).
- SQ14 · account · On 25 November the look's long line was cut when you pasted it. Which would have helped more: a button on a page, or a short line that copies whole? · decides: D-q3 (a) against (b), and A4.
- SQ15 · decision · Should Claude also write `main.py` through spark's save, so the page, Claude and the CLI share one write path? · options: no, the conversation keeps its own tools, and the timeline notices the change · yes, the agents' contract changes · decides: one write path or two, and how often spark says "changed outside" · mine: no, because the contract of the MVP's working path stays as it is.
- SQ16 · decision · Does your request of 26 November replace D11's condition for a browser flasher ("a first install by a person with no Python")? · options: no, a browser flasher still waits for the card #159 · yes, study it now as a spike · decides: D-q3 (c) and whether D-a is reopened · mine: no.

### Round 5

- SQ17 · decision, can be delegated · Is the table of features by host code now, or a document until a second host is chosen? · options: a document now · code now, as two small tables that render it · decides: S3 · mine: a document now.
- SQ18 · decision · When the page and Claude both changed `main.py`, what happens to the page's edit? · options: it is refused, with the newer text shown · the last write wins · decides: D-q2's conflict rule · mine: refused. It applies only if SQ5 puts the edit on the page.
- SQ19 · decision · Which boards must a deploy from a page serve? · options: the two board records in the repository · also the T-Display with its USB bridge · decides: which bench tests run (PH-4 to PH-7) · it applies only if SQ3 says yes.
- SQ20 · decision · How important is each assumption A1 to A10, and is the pass line of section 7 the right one? · decides: the brief's Q1.

### Round 6, account questions that sharpen the picture

- SQ21 · account · After the build at 11:40 on 22 November, did you go back to the published page during the firmware and deploy work, and what did you look for? · decides: A1.
- SQ22 · account · Over the 24 typed yeses of 22 and 23 November, did you ever type yes without reading the question? · decides: whether a yes on a page would be read less than a typed one.
- SQ23 · account · What made you take the 60-minute standing yes on 23 November, and not earlier? · decides: whether the grant already removes what a page deploy would remove.
- SQ24 · account · Have you ever opened a spark page in Safari or on your phone? · decides: the browsers the table must cover.

## Decisions of this synthesis, each with its reason and the option rejected

These are my choices in writing this text. They are not decisions of the PO.

1. I split two rows of the table, the read-back and the deploy. Reason: each holds two jobs with opposite answers on one host. Rejected: five rows, where one cell would say both "works" and "does not work".
2. I marked every cell of a feature that is not built as "not tested" and gave its route. Reason: the brief asks for "not tested" where nobody ran it. Rejected: "works" by reasoning alone.
3. I propose that the host table be rendered from two small tables. Reason: one row per host and one need per offer, so no cell is written twice. Rejected: AR-4's table with a hand-written cell for each host and feature.
4. I keep the flasher seam unchanged and place a browser path above it, as a port. Reason: four membership tests fail (section 4). Rejected: esptool-js as a member of `Flasher` or of the tools list.
5. I recommend `show-firmware` alone as the first build. Reason: it needs no host ability and no open decision. Rejected: AR-8 b's host table in code now, and AR-8 c.
6. I do not propose a `carry-requests` Operation now. Reason: in the Artifact only Claude's tools reach the page's database. Rejected: AR-4's relay Operation before a second host exists.
7. I propose the working name `FirmwareFiles`. Reason: `FirmwareReader` already names the phase's Strategy. Rejected: "a firmware reader in the firmware area".
8. I name A2 the riskiest. Reason: the most cost and the least evidence. Rejected: the feasibility of Web Serial in the Artifact, which is close to settled.
9. I keep the staleness guard as a base sha256 inside the save. Reason: widening the fingerprint makes every pick and build click stale after a firmware write. Rejected: `main.py` in the fingerprint.
10. I treat the pseudo-terminal finding as outside the item. Reason: it concerns the gate on every interface, not this epic. Rejected: folding it into D-q3.

## Claims I checked myself, with file and line

- The gate: scripts/spark/bench/deploy_gate.py:52-59 (`opens_erase` False by default, and the docstring's limit), :92-113 (typed), :117-126 (relayed), :166-193 (`require_open_gate`), :184-185 (the refusal).
- The standing grant: scripts/spark/bench/board_grant.py:243-268.
- The terminal test: scripts/spark/core/replies.py:157-158. My run under a pseudo-terminal, described in section 4.
- The request rule: scripts/spark/flow/run_request.py:1-5, :44 (three steps), :96-97 (a chat kind is refused), :129-132 (a refusal never echoes).
- The fingerprint: scripts/spark/flow/fingerprint.py:17 (three files, none in `firmware/`), :24-35.
- The offers: scripts/spark/flow/flow_codes.py:147, :151-160.
- The page's script: scripts/spark/flow/page_script.ts:1-10, :53-59, :74-79, :452-460.
- The catalogue: scripts/spark/operation_catalogue.py:15-28. `grep -c run_cli` is 0 for `flash_image.py`, `import_firmware.py`, `run_scenario.py` and `assign_pins.py`.
- The bench table and its outside: scripts/spark/bench/__init__.py:25-42.
- `pins.py`: scripts/spark/build/kept_files.py:27, :449-472. scripts/spark/design/pin_assigner.py:484-485, :562.
- The secrets: scripts/spark/firmware/project_secrets.py:1-13, :34. scripts/spark/flow/write_flow_page.py:31-34, :138-143.
- The flasher and the platform: scripts/spark/bench/flasher.py:1-6, :18-34, :80-82. scripts/spark/bench/firmware_platform.py:1-7, :37-79, :82-123.
- The deploy: scripts/spark/bench/deploy_stages.py:23-29. scripts/spark/bench/deploy_image.py:458-499. scripts/spark/bench/board_look.py:397-401.
- The image: scripts/spark/firmware/image_builder.py:4-12, :31-32, :38-42. scripts/spark/build/ignore_list.py:1-5. scripts/spark/firmware/project_image.py:121-125.
- The flow's reads: scripts/spark/flow/flow_reading.py:1-4. scripts/spark/flow/phase_readers.py:29, :532-542, :571-587. scripts/spark/flow/deploy_reading.py:1-6, :44-60.
- The payload shape: scripts/spark/core/operation.py:21-25. scripts/spark/core/cli.py:222.
- The compile check: scripts/spark/bench/image_evidence.py:124.
- The one git Adapter: scripts/spark/records/project_commit.py:1-8, :28-31, :69-79, :95-104.
- The tools list: the `roles` key of data/tools.json. scripts/spark/records/tool_finder.py:542.
- The commands: commands/page.md:19-20, :40-42, :70-71, :74-101. commands/deploy.md:2, :108-124.
- Earlier decisions: P218 brief.md:97, :153, :161. P820 brief.md:96-97, :103, :180, :182, and mvp-plan.md:7-8, :188. P269 brief.md:115. P1038 brief.md:80, :141, and design.md:170, :489. The git discovery's brief.md:80, :81, :105, :129. P1194 brief.md:58, :87, :121, :122, :126, :127, :129, :130, :133, :135, :137, :141, :142, :143.
- P1193 on branch restore-after-1775: brief.md lines 16, 18, 46, 50, 67, 76, 117, 124, 125. synthesis.md lines 43-76, 108, 127, 146, 179, 266. items.md line 56.
- The store, read only: the board record of the display walk (28 deploys, 21 images, 24 typed and 4 under the standing yes, 10 `ready unknown`). bench-2026-11-25.md, note 20 (109 s for 4 MB).
- The size of the deploy pipeline: `wc -l` of the 17 files gives 3,559.
- No `bootloader()` in `scripts/`: 0 hits. docs/discovery/2026-10-31-p472-no-hands/finding.md:5-9.
- The cards: `gh issue view` of #1748, #1259, #1250, #1196, #1626, #1766, #1602, #159, #674, #152, #304, #1187, #1198, #1787, #1688, #1740, #199, #1699, #905, #224, #1765, #1698, #1173, #1521, #1738, #1587, #94, #1757, #1582. The board's slices, and the slice of each card in section 8.
- On the web: the Web Serial standard (the feature name, the default allowlist, `requestPort()`'s two rejections, `SerialOptions` with no signal option, `setSignals()` only when opened). The Artifact documentation (the page constraints, the five script hosts, the sandboxed origin, 16 MiB, the published file types `.html`, `.htm` and `.md`, and the "send back to Claude" pattern).

## What I did not check

- The frame's `allow` attribute. I have no browser tool. I rely on hosts.md:8-25, read by the main session on one artifact, in one browser, on one day.
- The `desktop` capability's types (`fs`, `childProcess`, `pty`, "full-access", the Allow's life). I could not call the artifacts server. I rely on hosts.md:36-50.
- Whether the desktop app's own `pty` reports a tty and takes input from the page's script. My run used Python's `pty` module, not the app.
- Whether a `.bin` can sit among an artifact's own files (research.md:85). The documentation lists only `.html`, `.htm` and `.md` as published file types, which suggests no. I did not test it.
- The git history of the three projects behind UX-1 (17 of 18 commits). I did not open those repositories.
- The Thonny configuration and the list of installed programs behind PO-2.
- The bench notes of 2026-11-25 other than note 20, and the walk diaries.
- The esptool-js issues #97, #277 and #279, and the WebKit, Firefox and Android rows of research.md.
- esptool 5.5.0's `loader.py:455`. The `python3` on the path holds esptool 3.3, where the same call is at `esptool.py:320`.
- The council folders of P820, P1038, P269, P235 and P867 beyond the lines above. P1193's council/c-answers.md.
- The published page of a real project. I wrote no page, published nothing, opened no port and touched no board.
- `docs/guide/words.md` beyond the three timeline words.
- One thing I saw and did not cause: `git status` shows `jobs-and-journeys.md` of this folder as modified. I wrote nothing in the tree.

## Searches

- Two web fetches · served A6, n1, n7, n11, n17 and n19 · used: `https://serial.spec.whatwg.org/` (used, for n17, n19 and A6) and `https://code.claude.com/docs/en/artifacts.md` (used, for n1, n7 and n11).
- GitHub issue searches in spark's own repository · served section 8, a card before a new item · Used: "flash_image Operation core" (#1582, #1105), "import_firmware Operation" (#1757), "flash_image.py" (#1463, #1679), "109 s" (#1681), "pins.py page" (#1259, #1250), "firmware page shows" (#1666), "bootloader" (#1537, another thing), "deploy not started page" (#1626), "ready unknown" (#1656, #1537), "Electron" and "GitHub Pages" (#1196). Without a result: "secret main.py mask", "terminal isatty pty yes", "typed yes program", "carry requests command prose", "token port MAC image", "inline secret", "password main.py", "page host capabilities", "Allow dialog republish", "baud deploy", "ViperIDE", "Thonny".
- One experiment, not a search · served the consent seam (★C10) · used: spark's `TerminalConsentStrategy` under a pseudo-terminal, with the parent writing the yes. No board and no deploy.
