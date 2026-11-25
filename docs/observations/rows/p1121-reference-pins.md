# P1121: a reference build names spark's earlier pin map: rows

Card: [P1121 #1650](https://github.com/xmejkal/spark/issues/1650). This file holds the acted, raised and rejected
findings only. The plan (Opus) had its council, the lens on Sonnet and the refuter on Opus, who built the change on a
copy. 2026-11-25. Row 7 of `p1109-keep-pins.md` is closed by this PR; its own status stays as written.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | after a reference `--keep` build spark's `firmware/pins.py` stays with no kept entry | P1109 row 7, probe 1 | acted | fixed: `keep_pins` with no requirements names spark's file `left alone`, "so it is an earlier build's"; T1 |
| 2 | the card's Done-when names four files; `schematic.svg`, `pcb.svg` and `page.html` get no entry (B3, D2). Delegated, the PO's to change | plan, lens 1 | acted | handled, not named: the pictures sit inside `dist/`, which the `dist` entry names (P1088, P816; T1); a kept entry naming `page.html` would stop the follow-up's rewrite (T3) |
| 3 | a person's own `pins.py` gets no entry after a reference build (D3). Delegated | plan | acted | T2 |
| 4 | an unreadable `pins.py` now gets a `not written` entry, where main gave none (B2) | refuter 3 | acted | pinned by the T2-style test for `chmod 0` |
| 5 | after an unfinished reference build the rewritten page shows the earlier schematic and PCB, and only the build phase says "did not write dist/" (B5) | refuter 2 | raised | dropped because: it is how P816 works today; the follow-up is the page's, not this card's |
| 6 | mutation rows 4 and 5 share one line (B6) | lens 4, 5 | acted | T1 reads the real exit code for both cases; each row is killed by a different test, proved by hand |
| 7 | the follow-up writes a flow page into a `--keep` folder that is no project | plan, probe 2 | raised | card P1127 #1657 (B7) |
| 8 | `kept_files.py` is at its 600-line limit | plan D5 | acted | fixed: two docstrings open on their `"""` line, so the file stays at 600 |
