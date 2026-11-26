# P1197: 3D shapes, the board in 3D, the Fusion export and a simple case: rows

Card: [P1197 #1745](https://github.com/xmejkal/spark/issues/1745). The PO, 2026-11-26: "the whole thing openable in
fusion and the user or ai could use it and create the cover or other parts". The discovery is
`docs/discovery/2026-11-26-p1197-3d/`, and its first refuter pass on the brief is council/refuter.md. This file holds
the acted, raised and rejected findings of the PR's own review (one refuter on Opus, 2026-11-26, docs only,
council/refuter-pr.md). 2026-11-26.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The brief describes T1 as three files of a probe board with JSCAD bodies, but the PO holds two files of the amplifier fixture with boxes that replace the pins, so T1 cannot test D13's union of box and pins | PR refuter (Opus), RP-1 | acted | a third file, `t1-tscircuit-union.step`, joins each box to its pins (18:04 CET, 88 pin faces below the board). The README, the Test line, A3's test cell, #1804 and spark-main were told |
| 2 | D13 leaves out the seats' T1 condition, the split on a T2 miss, the tech lead's "never through tsci export" and "measure the build time", and the caveat on "manifold" | PR refuter (Opus), RP-2 | acted | each clause is in D13. #1729 carries the build-time measurement, and #1807 the "--info only, not printed" caveat |
| 3 | Header lines and rows that the later D rows made untrue: Decision needed, Stands on, the Hand-off, the waiting row, T2 as conditional, D4's round, Q7's depths, C30's caveat | PR refuter (Opus), RP-3 | acted | each line names the D that answered it |
| 4 | Q1 and the ratings are stronger than D9: D9 rated A1 to A4 only, and "not high" is not "low" | PR refuter (Opus), RP-4 | acted | Q1 reads "answered D9 for A1 to A4. A5 to A10 unrated", and A1, A2 and A4 read "not high D9" |
| 5 | The In short drops D5's caveat that options (d) and (e) were not shown, and ★C34 leans on D1, given before it | PR refuter (Opus), RP-5 | acted | both caveats are in the In short and in ★C34 |
| 6 | ★C35 and ★C36 state three things with no kept evidence: the board without bodies, the probe boards, and the cause of the missing FireBeetle | PR refuter (Opus), RP-6 | acted | the board without bodies has the same four NaN lines (`grep -c NaN plain-amp.step`, 4). The probe boards and the cause are marked H. The DIP-12 stand-in and the PCB-solid trace are named |
| 7 | The pass line's size check reads back the record's own numbers, and the terminal's generic body stands 12.8 mm above the board | PR refuter (Opus), RP-7 | acted | A3 and the Riskiest line say "at the record's size". The README and ★C35 name both |
| 8 | Numbers with no unit, population or provenance: "10 H", 25 minutes, 25 against 26.6 MB, "162 faces", the circular 27.7 mm, "3 of 40" | PR refuter (Opus), RP-8 | acted | each number carries its source or tag. The circular match is a note in verification.md |
| 9 | pre-analysis.md, jobs-and-journeys.md and verification.md still say what the corrected claims replaced | PR refuter (Opus), RP-9 | acted | 34 of 40, 56 x 42 x 15.4 mm, 3 of 40, and the reproduction times |
| 10 | Every pointer into pre-analysis.md is one line off, the PO assistant's seat cites old D lines, BUILD_MAKERS is at :186, and C29 to C31 point at a heading | PR refuter (Opus), RP-10 | acted | the pointers are computed from each target line's content. The seat file says the facilitator repointed them |
| 11 | items.md differs from #1804 and #1805, and items.md:30 contradicts D11 | PR refuter (Opus), RP-11 | acted | items.md carries the cards' wording |
| 12 | D13 and D16 do not say what the PO was shown | PR refuter (Opus), RP-12 | acted | D13: not put to him as questions, a summary in round 4. D16: the six items one line each and the comment's contents |
| 13 | No file holds an absolute home path, a secret, a vendor file or a photo. Tilde paths to the PO's sibling projects follow main's practice | PR refuter (Opus), RP-13 | closed | a confirmation. A search for an absolute home path finds no file in the folder |
