# P1200 council: the ratings of the assumptions

The council of three on Fable rated the importance of the open assumptions on the PO's delegation (brief.md D7), recorded as delegated and his to change. High means that if the belief is false, the decisions D2 to D9 or the show slice would change. Each seat read risks-and-tests.md and brief.md. Their tables follow verbatim.

## Searches

- none · no decision needed a search · not used

## The po-assistant seat

| id | importance | why |
| --- | --- | --- |
| A1 | high | The show slice is the only thing D5 builds and D2 names its two files, so if he names no moment when he wanted to read the firmware on the page, the slice waits and he gets nothing from this epic after the MVP walk. |
| A3 | high | D4 puts the last read-back on the page and D9 confirms job J3, so if he already learns what the board runs from the terminal, or the page can only say "not read" as in 9 of the 10 unknown deploys of ★C12, that part of D4 (items.md, item 4) gives him nothing. |
| A4 | high | D4 answers the deploy's friction with a line to type and Copy, so if the friction is the terminal itself, D4 does not remove it and D-q3 (b) comes back as a candidate. |
| A5 | low | It concerns a saved edit on the page, which D3 and D5 do not build, so a false belief changes only the wording of a later edit seam. |
| A6 | low | D4 allows no deploy from the page on any host, so a serial port that opens in the Artifact would change one cell of the host guide page (★C1) and nothing he gets. |
| A7 | low | D4, D5 and D9 build no host feature now, so a failed desk spike on P494 or his not using the desktop app only removes a column of the host guide page (★C2). |
| A8 | low | D4 keeps the yes in his own terminal whatever the app's pty does, and ★C9 holds in code, so the result only sizes the hole of C20, which is its own story (items.md, item 18). |
| A9 | high | D8 holds the show slice behind P1004 because of this belief (★C13), so if the mask did cover a literal the slice could ship without that wait, and if it is true a literal typed into main.py stays unmasked even after P1004. |
| A10 | low | The show slice is read-only text on the page as it works today and D9 builds no host-specific feature, so a moving contract delays nothing that D2 to D9 give him. |

## The architect seat

| id | importance | why |
| --- | --- | --- |
| A1 | high | D2 and D5 rest on it, and it is the only belief whose failure removes the one thing built, the `show-firmware` Operation and its fold (items.md, item 1). |
| A3 | low | The last read-back already exists in `show-flow`'s deploy phase (council/synthesis.md:203), its plain-words form is a comment on P1217 outside the show slice (items.md, item 4), and its stated consequence, that D-q1 (b) waits, already holds under D2. |
| A4 | high | D4 rests on it, because if the friction is the terminal itself then D-q3 (b) returns, and with it a second host and `build-image` on the core (items.md, dropped items 6, 9 and 15). |
| A5 | low | D3 leaves `save-firmware` a named seam with no save built, so a false belief changes nothing until an edit on the page is reopened. |
| A6 | low | D4 and D-a already rule out a browser flash whatever the port does, so a chooser that opens would change one dated cell of the host guide page (items.md, item 7) and no seam or Operation. |
| A7 | low | D4 dropped the desk spike and the desktop column's only use (items.md, dropped items 6 and 15), so no feature built now needs a second host. |
| A8 | low | In D4 the PO also rejected a page start with a yes he typed, so D4 does not rest on this belief, the relayed-yes rule is already in code (scripts/spark/bench/deploy_gate.py:126 and :184, ★C9), and either test result moves only the scope of item 18, which is out of scope. |
| A9 | high | D8 and the show slice's dependency on P1004 rest on it (★C13, scripts/spark/firmware/project_secrets.py:26 masks only `firmware/*secret*.py`), so if a mask did cover a literal the slice would lose that gate and its place in the order would change. |
| A10 | low | `show-firmware` reaches the CLI, `--describe` and the page through `FlowReading` and is not host-specific (D5, council/synthesis.md:104), and under D4 and D9 no host-specific feature is built, so a moving contract changes only the dates on the host guide page. |

## The tech-lead seat

| id | importance | why |
| --- | --- | --- |
| A1 | high | The show slice of D2 and D5 is the only thing built, and it rests on a wish with no account of a moment, so if he does not read firmware on the page the slice waits and nothing of the epic reaches code (★C3, scripts/spark/flow/phase_readers.py:532-542). |
| A3 | high | D4 puts "the last read-back" on the page and items.md item 4 sends it to P1217 in the MVP slice, yet in 9 of the 10 "ready unknown" deploys spark could not read the board's files (★C12), so the page may only repeat "not read" and that part of D4 would drop. |
| A4 | low | D4 already answered it, because he chose "no" with the page-started deploy on offer, and its test SQ14 was dropped after D3 and D4 (brief.md:92), so a false belief changes nothing that is built now. |
| A5 | low | D3 and D5 build no edit and no save, so no person saves an edit on the page, and the mechanism it guards (scripts/spark/firmware/project_image.py:121-125) matters only if the edit seam of D-q2 (b) is opened later. |
| A6 | low | D4 rules out a deploy from the page on every host, so a chooser that opens in the Artifact would change one cell of the host table (D-q4 a, a guide page) and no decision or build order. |
| A7 | low | No desktop host is built under D4 and D5, so a failed spike on P494 only removes a column of the host table, and the spike already sits after the MVP. |
| A8 | low | The rule stands in code whichever way the app's pty test goes (`opens_erase = False`, scripts/spark/bench/deploy_gate.py:117-126), and D4 keeps every deploy in the terminal, so the result only sizes the separate story of items.md item 18 (C20). |
| A9 | high | D8 and the show slice's dependency on P1004 rest on it, and the code confirms the mechanism (mask rule `*secret*.py` only at scripts/spark/firmware/project_secrets.py:26 and :34, every file in the image at scripts/spark/firmware/image_builder.py:38-42), so if the literal were masked the slice need not wait for P1004 and its order changes. Not checked: whether P1004 itself would mask a literal typed only into main.py. |
| A10 | low | The show slice of D5 is one Operation and one fold on the existing page with nothing host-specific in it, so a moving Artifact contract delays only the host features that D4 and D5 already left unbuilt (★C2). |

## The result, by majority

| id | importance | seats |
| --- | --- | --- |
| A1 | high | 3 of 3 |
| A3 | high | 2 of 3 (the architect: low) |
| A4 | high | 2 of 3 (the tech lead: low) |
| A5 | low | 3 of 3 |
| A6 | low | 3 of 3 |
| A7 | low | 3 of 3 |
| A8 | low | 3 of 3 |
| A9 | high | 3 of 3 |
| A10 | low | 3 of 3 |
