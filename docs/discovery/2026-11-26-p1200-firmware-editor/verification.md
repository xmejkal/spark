# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line. -->
- ★C1 · hosts.md H1-1, the spec 6.1 · refuter: partly — "The default allowlist for this feature is 'self'." The frame read could not be repeated without a browser · reproduced how: the main session read the frame's `allow` attribute in Chrome 158 at 15:08 CET. The brief now says the frame is not allowed the feature, and the result is H · result: reproduced · keep: nobody tried a port there <!-- REQUIRED:claims -->
- ★C2 · hosts.md H2 · refuter: could not open — no artifacts tool in its session. It quoted hosts.md:42-43 · reproduced how: the main session read describe_capabilities "desktop" with its types, contract 0.2.99, 15:06 CET · result: reproduced · keep: not run
- ★C3 · phase_readers.py:532-542 · refuter: holds — "return self.phase(None, [flow_codes.FIRMWARE_MESSAGE % stamp(...)])" · reproduced how: re-read the lines · result: reproduced · keep: none
- ★C4 · kept_files.py:27, :449-461 · refuter: holds — "Not spark's: left alone, as `board.tsx` is." · reproduced how: re-read the lines · result: reproduced · keep: none
- ★C5 · run_request.py:1-5, :44 · refuter: holds — "The values of the step come from spark's own offer key, never from the request." · reproduced how: re-read the lines · result: reproduced · keep: none
- ★C6 · fingerprint.py:17-18 · refuter: holds — "FILES = (needs.FILE, Path(REQUIREMENTS_FILE), BUILD_RECORD_FILE)" · reproduced how: re-read the lines · result: reproduced · keep: none
- ★C7 · deploy_stages.py:23-29, flasher.py:32-34, board_look.py:397-401 · refuter: holds — "The commands that put `image` on the board, in order, each an argv list." · reproduced how: re-read the lines · result: reproduced · keep: none
- ★C8 · flasher.py:3, board_facts.py:4 · refuter: partly — the first cited lines did not carry the claim. flasher.py:3 does: "erases the whole flash with esptool and writes one image at 0x0" · reproduced how: re-read image_builder.py:4-12 and the refuter's two lines. The brief now cites flasher.py:3 and board_facts.py:4 · result: reproduced · keep: none
- ★C9 · deploy_gate.py:117-126, :184-185, board_grant.py:243-268 · refuter: holds — "opens_erase = False" · reproduced how: re-read deploy_gate.py:184-185 · result: reproduced · keep: none
- ★C10 · replies.py:157-158 · refuter: holds, reproduced — a child under `pty.fork` printed "isatty True True" · reproduced how: the main session ran a child under Python's `pty.fork` that read "yes" from the parent and printed `live=True ans=yes`. Under a pipe the same child printed `live=False` (a script in the job's scratch folder, 2026-11-26 16:0x CET) · result: reproduced · keep: Python's pty
- ★C11 · council/user-ux.md UX-1 · refuter: holds as a count — recounted 15 of 15, 2 of 2, 0 of 1 · reproduced how: not run by the main session · result: not reproduced · keep: co-author line
- ★C12 · the store's board record · refuter: holds — 28 deploys, 24 typed, 4 standing, 18 seen, 10 unknown. The user lens's 11 is wrong · reproduced how: not run by the main session. The synthesis and the refuter counted the same record · result: not reproduced · keep: one project
- ★C13 · project_secrets.py:1-5, image_builder.py:38-42 · refuter: holds — "matches `*secret*.py`, such as `wifi_secrets.py`" · reproduced how: re-read the lines · result: reproduced · keep: none
- ★C14 · research.md · refuter: partly — "No npm library copies files" was stronger than "none found for ESP32", and pico-pipette does it for a Pico. "Needs HTTPS" dropped localhost · reproduced how: re-read research.md:30, :98, :132. The brief now says "none found for an ESP32" and "HTTPS or localhost" · result: reproduced · keep: none
- ★C15 · P218 brief.md:97, :153 · refuter: partly — D11 rests on "if its not adding anything to our case", and the stranger caveat is beside the point · reproduced how: re-read brief.md:97 and :153. The brief now leads with D11's own reason · result: reproduced · keep: none
- ★C16 · operation_catalogue.py:15-28, flash_image.py · refuter: holds — `grep -c run_cli` gives 0 · reproduced how: the same grep gave 0, and `grep firmware operation_catalogue.py` gave no line · result: reproduced · keep: none
- ★C17 · P1193 brief.md:18, :46, :76, items.md:56 · refuter: partly — items.md:56 is about a layout edit, a proposed comment, not a ruling · reproduced how: the brief now says that neither P1193's proposed item nor its D6 names a firmware edit · result: reproduced · keep: none
- ★C24 · p934-display2's git log, read by the refuter · refuter: its own finding · reproduced how: not run by the main session · result: not reproduced · keep: one project

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question. -->
- Agree: the Artifact in a browser gets no serial port (all four lenses, the synthesis, the refuter with "partly") <!-- REQUIRED:agree-split -->
- Agree: a browser flasher written in JavaScript would skip the gate, and a page yes stays relayed (the tech lead, the architecture lens, the synthesis, the refuter)
- Agree: a program can type a yes into a pseudo-terminal (three lenses, the synthesis's run, the refuter's run, the main session's run)
- Split: what "the generated code" means. The synthesis: main.py and pins.py. The refuter: maybe all the code Claude generated, and the walk's changes were mostly outside main.py · Q2
- Split: the read-back on the page. The user lens and the synthesis: it answers "what does the board run". The refuter: in all 10 cases the read-back itself failed · SQ13, A3
- Split: whether a page start of spark's own deploy reopens D9. The synthesis: yes. The refuter: no, D9 is about a click's yes, and the MVP plan's line binds only the MVP · Q4
- Split: whether "our server" means a server of spark's own with accounts or his own home server. The brief assumed the first. The refuter names the second · queued as a question for round 2
- Split: the second host. The tech lead: a local server. The architecture lens: the desktop app. The synthesis: decide after the desk spike · SQ6
- Rival explanations the folder does not rule out (council/refuter.md, part 3): the co-author line names the committer, not the typist. The 11-25 notes were framed by his rule to note the CLI's UX. An edit on the page saves time on a local or desktop host, which removes the carry through `/spark:page`
