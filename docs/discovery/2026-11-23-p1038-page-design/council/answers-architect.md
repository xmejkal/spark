# P1038 delegated council: the architect's answers

The architect agent, 2026-11-23, about 16:42 to 16:55 CET, read-only. This session wrote this file from the agent's
returned text, without changes to its answers. Each answer is "delegated to the council, the PO's to change".

## Q1: the assumptions

- Q1 A1 · high · keep the line, add its instrument (2026-11-23): "in the next walk after the build he opens the page on his own at least once before he asks Claude where the project stands, and the session did not name the page first. The session writes it in the diary when he says so." · The old line had no instrument, and QA1 primes him. · council/refuter.md:227-230, :206-208
- Q1 A2 · high · keep "at least 3 of 5", with one marking rule added (2026-11-23): goal and must lines count as a spark record, a decided line counts as "the project's file, not yet a record". · It sets Q2's boundary. `Brief` reads goal, must, prefer and sellers and has no `decided` field. · scripts/spark/records/brief.py:4-9
- Q1 A3 · high · keep · Item 1 rests on it, and the three ready words are fixed in code. · scripts/spark/bench/ready_probe.py:38, scripts/spark/bench/deploy_service.py:65-71
- Q1 A4 · low · keep "not proposed" · No option that keeps one core needs the files capability. · council/tech-lead.md:121-128
- Q1 A5 · high · keep · It is the one problem the PO named in his own words. · council/refuter.md:15-21, P1011 #1470
- Q1 A6 · low · keep · A miss costs a token change: the fonts are two tokens in one dict. · scripts/spark/flow/flow_page.py:244-246
- Q1 A7 · high · change (2026-11-23): "zero hits for the Wi-Fi name, the secrets file, home paths and the store's path on every route. On any copy shared beyond the PO, also zero names of other projects." · A leak cannot be undone. · risks-and-tests.md:29, council/refuter.md:149-150
- Q1 A8 · low · keep. If the live step is pulled, it runs then · Q3 does not pick O3c now. · brief.md:70
- Q1 A9 · high · change (2026-11-23): "at the end of the next walk page.html on disk and `flow.py show --json` name the same stand, the page's stamp is the newest time of every file the page reads, and no step was taken on a stale page's word." · O3a rests on it. · council/refuter.md:22-29, scripts/spark/flow/write_flow_page.py:132-136

## Q2 to Q10

- Q2 · O2a now. O2c's link waits for QA2 and A2's result. Not O2b · The page shows only what a core reader derives from a record spark holds, and the same lines go into `show --json`. "decided" enters as a new property with its origin. O2b needs gh and the network on every write. · scripts/spark/records/brief.py:4-9, scripts/spark/flow/show_flow.py:80-83, :127-128, council/refuter.md:137-139
- Q3 · O3a now, built so that O3c is an added adapter later. O3b is dropped · Five rules follow. First, one value and one renderer: `write_page` injects readers, parts, renderer and store. Second, the state is an answer (`flow.py show --json`), never a stored file. Third, freshness is a core fact with its own file list. That list is separate from the click fingerprint of three files. Fourth, the core decides when the page is written again (P793 piece 3). Claude reads the stand with `flow.py show`. Fifth, a live page later needs two adapters: a Reporter for the page's host and a watch beside `RequestChannel`. The first live step is a notice with a time and a fingerprint only. · scripts/spark/flow/write_flow_page.py:139-155, scripts/spark/flow/flow_page.py:41, :230, scripts/spark/flow/fingerprint.py:18, scripts/spark/core/events.py:14, :40-56, scripts/spark/flow/page_script.js:71-76, commands/page.md:27-30
- Q4 · O4a · D7 is the PO's decision and a test pins it. The fonts are two tokens, so O4b stays a small later change if A6 fails. The design hands the tokens to the renderer as one value. · tests/test_flow_page.py:88-89, scripts/spark/flow/flow_page.py:233, :244-248
- Q5 · O5a, on the condition that Q8 is answered first. Not O5c · The phases are one source for show, the page and a request. The story also changes the guide: "no phase is open" needs its own sentence. P873 gets a note of Q8's answer. · scripts/spark/flow/show_flow.py:80-83, scripts/spark/flow/phase_readers.py:554-560, scripts/spark/flow/guide.py:84-93
- Q6 · O6a, user level. No /spark:setup line · "for everybody, not just this session" contrasts sessions, not users. A spark user never styles the page. No copy enters the repository. The install waits for the PO. · #1521 comment (the skill decision), council/tech-lead.md:208-216
- Q7 · O7a, later on P834 #1196 · No account of a share exists (QA4). Another host costs an adapter later. · scripts/spark/flow/page_script.js:71-76
- Q8 · no · "ready seen" on the current image is ok; "ready unknown" is partial (no tick, the phase stays open, NOW says to look at the board); "ready not seen" is problems. No log is not-started. Firmware newer than the last image is stale. The reader says "deployed <time>, image <sha>, start not seen". · scripts/spark/bench/ready_probe.py:38, scripts/spark/flow/guide.py:78-81, docs/guide/patterns-and-names.md:40
- Q9 · the stand in the core under P793, in parallel. P1038's first slice is the readability, structure first, then the graphic style · The PO's words are about readability. A style pass before the sections settle is redone. · council/refuter.md:15-21, council/tech-lead.md:225-229
- Q10 · a slice of this epic, the last and small. The design holds its outline. The how-to points to the Artifact server's `guide` and does not copy it. The "read page.html whole" defect is fixed in slice 1 · A how-to is proven by a fresh session that follows it. · commands/page.md:34, :62, council/refuter.md:179-182

## Open choices it names for the PO

- Which trigger writes page.html again: only /spark:page, or the core's hook after each writing run (recommended: the hook, P793 piece 3).
- Whether "decided" becomes a field of the brief record (recommended: yes, with its origin, when Q2's section is built).
- Whether a rewrite with new code over an old build needs a guard (recommended: the page names the build it draws from).

## Not checked by the architect

Nothing on the Artifact server. The 27 logs (taken from the tech lead and the refuter). P820's D7 and D10 at their source. Council/user.md and council/po-assistant.md in full.

## Searches

none
