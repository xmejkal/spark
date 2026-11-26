# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. -->

From council/synthesis.md, section 8. None is filed. spark-main files them on the PO's yes. Comments widen an existing card instead of filing a new one.

## 1. The page shows the firmware as one file time → `show-firmware` and one fold with main.py and pins.py as masked, read-only text
- type: story (new) <!-- REQUIRED:item-type -->
- needed by: "it might also be nice to offer some on the page editing and display of the generated code and maybe even deploy directly rfom the broswer" (the PO, 2026-11-26, #1748) <!-- REQUIRED:needed-by -->
- value proven by: `show-firmware --json` and the fold on a scratch project show main.py and pins.py, with who writes each and when, and a secrets file shows as "not shown" <!-- REQUIRED:value-proven-by -->
- depends on: P1208 #1757 (the firmware area's table), and the secrets rule (item 13) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1200 #1748 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## 2. Comment on P889 #1259: the pin table is the pin-map part of P1200's D-q1
- type: comment <!-- REQUIRED:item-type -->
- needed by: "it might also be nice to offer some on the page editing and display of the generated code and maybe even deploy directly rfom the broswer" (the PO, 2026-11-26, #1748) <!-- REQUIRED:needed-by -->
- value proven by: the comment on #1259 links the brief <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors, as today <!-- REQUIRED:spark-process:slice -->

## 3. Comment on P882 #1250: the firmware fold shows this compare's result once it exists
- type: comment <!-- REQUIRED:item-type -->
- needed by: "it might also be nice to offer some on the page editing and display of the generated code and maybe even deploy directly rfom the broswer" (the PO, 2026-11-26, #1748) <!-- REQUIRED:needed-by -->
- value proven by: the comment on #1250 <!-- REQUIRED:value-proven-by -->
- depends on: item 1 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors, as today <!-- REQUIRED:spark-process:slice -->

## 4. Comment on P1217 #1766, with P1106 #1626: widen to the read-back in plain words, per file "matches", "differs" or "not read"
- type: comment <!-- REQUIRED:item-type -->
- needed by: the user lens's UX-15, an inference from one walk, and Q2 of round 1 <!-- REQUIRED:needed-by -->
- value proven by: the comment, and A3's account question <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as today <!-- REQUIRED:spark-process:slice -->

## 5. Comment on P1132 #1666: one more chat offer, "Change a value in the firmware" (D-q2 a)
- type: comment <!-- REQUIRED:item-type -->
- needed by: "it might also be nice to offer some on the page editing and display of the generated code and maybe even deploy directly rfom the broswer" (the PO, 2026-11-26, #1748) <!-- REQUIRED:needed-by -->
- value proven by: the sentence pasted into the chat changes the value <!-- REQUIRED:value-proven-by -->
- depends on: Q3's answer <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as today <!-- REQUIRED:spark-process:slice -->

## 6. Comment on P494 #674: widen the spike with desk tests that need no board (the serial test page in Chrome and in the desktop app, childProcess running `flow.py show`, whether the app's pty reports a tty and takes the page's input)
- type: comment <!-- REQUIRED:item-type -->
- needed by: the PO's words on #1748: "maybe some of these functionalities are available but only for a version of the page running on our server or local server" <!-- REQUIRED:needed-by -->
- value proven by: the spike's finding picks the second host <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors, as today <!-- REQUIRED:spark-process:slice -->

## 7. Comment on P834 #1196: P1200's table of features by host is this card's input, as a guide page with a date on each cell
- type: comment <!-- REQUIRED:item-type -->
- needed by: the same words of #1748 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors, as today <!-- REQUIRED:spark-process:slice -->

## 8. Comment on P1152 #1688: the firmware needs a row in the kept records, never pins.py
- type: comment <!-- REQUIRED:item-type -->
- needed by: P1193's D-q1 and P1200's SQ8 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: SQ8's answer <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Project timeline, as today <!-- REQUIRED:spark-process:slice -->

## 9. Comment on P793 #1105: the `flash_image` line is the `build-image` Operation that any page deploy needs first
- type: comment <!-- REQUIRED:item-type -->
- needed by: the tech lead's TL-10 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, as today <!-- REQUIRED:spark-process:slice -->

## 10. Comment on P1082 #1587: a step that carries text needs a second guard of its own
- type: comment <!-- REQUIRED:item-type -->
- needed by: the architecture lens's AR-2 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as today <!-- REQUIRED:spark-process:slice -->

## 11. Comment on P1144 #1679: the notes of 2026-11-25 say lines that copy whole may remove the friction a page deploy was meant to remove
- type: comment <!-- REQUIRED:item-type -->
- needed by: the store's bench-2026-11-25 notes (UX-4) <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as today <!-- REQUIRED:spark-process:slice -->

## 12. Comment on P1194 #1740: the settings rows of council/synthesis.md, section 5, as proposals
- type: comment <!-- REQUIRED:item-type -->
- needed by: "every configurable choice names its setting, its default and its layer" (the PO, 2026-11-26, P1193 D8) <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->

## 13. Comment on P1004 #1463, with P1091 #1602: the firmware fold depends on the secrets rule, and an image never goes into an Artifact
- type: comment <!-- REQUIRED:item-type -->
- needed by: the PO assistant's PO-9 and the tech lead's TL-7 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as today <!-- REQUIRED:spark-process:slice -->

## 14. Comment on #159: P218 D11's revisit condition lives here, with research.md and PH-3 to PH-7 as inputs
- type: comment <!-- REQUIRED:item-type -->
- needed by: P218 D11's no-go: "revisit only for a first install by a person with no Python" <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 5 A real stranger (ask the decider: the card has no slice today) <!-- REQUIRED:spark-process:slice -->

## 15. Comment on P836 #1198: the Allow dialog returns after each republish, and a click waits for `/spark:page`
- type: comment <!-- REQUIRED:item-type -->
- needed by: the user lens's UX-7 and UX-17 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors, as today <!-- REQUIRED:spark-process:slice -->

## 16. Comment on P1235 #1787: a server of spark's own implies accounts, and nothing is built for it
- type: comment <!-- REQUIRED:item-type -->
- needed by: the git discovery's D12 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->

## 17. An edit of main.py has no path from an interface without file tools → `save-firmware` with a listed file, the sha256 of the text shown, a size cap, a compile check and a kept step (parked until SQ5)
- type: story (new, parked) <!-- REQUIRED:item-type -->
- needed by: "it might also be nice to offer some on the page editing and display of the generated code and maybe even deploy directly rfom the broswer" (the PO, 2026-11-26, #1748) <!-- REQUIRED:needed-by -->
- value proven by: a save refused after Claude changed the file, from the CLI <!-- REQUIRED:value-proven-by -->
- depends on: P1152 #1688, and SQ5's answer <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1200 #1748 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## 18. A yes that a program writes into a pseudo-terminal counts as typed and opens the erase → the guides say what a typed yes proves, a rule test keeps spark's own interfaces from driving a terminal for a step that asks, and the PO decides whether the gate does more (out of scope)
- type: story (new) <!-- REQUIRED:item-type -->
- needed by: the PO's P675: a yes that another program collected never opens the erase <!-- REQUIRED:needed-by -->
- value proven by: a rule test that fails when a spark interface drives a terminal for an Operation whose effects hold `asks` <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.11 Change it and put it on again (or spark-main's choice) <!-- REQUIRED:spark-process:slice -->

## 19. P218's D19 says the token binds the port, the MAC and the image, and the code binds the MAC and the image → the guides and a note on the decision say what the token binds (out of scope)
- type: chore (new) <!-- REQUIRED:item-type -->
- needed by: P218 D19 of 2026-10-13 <!-- REQUIRED:needed-by -->
- value proven by: the guide line and the decision's note <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): spark-main's choice <!-- REQUIRED:spark-process:slice -->

## 20. The deploy never asks a running MicroPython S3 to enter its bootloader, so the person presses BOOT → a software entry before the erase, as P472's bench did twice (out of scope)
- type: story (new) <!-- REQUIRED:item-type -->
- needed by: P472's finding, docs/discovery/2026-10-31-p472-no-hands/finding.md:5-9 <!-- REQUIRED:needed-by -->
- value proven by: an S3 deploy with no BOOT press, on the bench <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.11 Change it and put it on again <!-- REQUIRED:spark-process:slice -->

## 21. Comment on P1146 #1681: the write's 109 s fits esptool's default baud (PH-9)
- type: comment <!-- REQUIRED:item-type -->
- needed by: the store's bench-2026-11-25, note 20 <!-- REQUIRED:needed-by -->
- value proven by: the comment <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as today <!-- REQUIRED:spark-process:slice -->

## Board actions
- file items 1, 17 to 20 and post the comments 2 to 16 and 21 · pending, needs the PO's yes to this list <!-- REQUIRED:board-actions -->
