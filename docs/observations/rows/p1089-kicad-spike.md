# P1089: what is wrong with today's tscircuit boards, and where KiCad fits: rows

Card: [P1089 #1600](https://github.com/xmejkal/spark/issues/1600), a spike. The finding is
`docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/finding.md`. The architect wrote it from the session's notes, and
the refuter on Opus checked it on 2026-11-26. This file holds the acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the notes said that spark owns the netlist before the build, but `netlist.Netlist` reads the built `circuit.json` | architect | acted | notes.md and finding.md section 3.1, gap 4 |
| 2 | the 133 and 34 GND pieces and the 127 exported zones did not agree | architect | acted | they describe two routes: the 11-22 build and the export's new route. finding.md section 9 |
| 3 | "0 errors" in KiCad holds only at the export's 0.1 mm netclass clearance. At 0.2 mm both boards give 6 clearance errors | refuter (Opus) | acted | reproduced from the refuter's DRC files. finding.md sections 1.3, 5 and 9, README.md |
| 4 | "3V3 then reaches the e-paper by a trace" describes no change: 2 of 10 traces carry V33 in every build | refuter (Opus) | acted | finding.md section 1.4 and the pour card's title, notes.md |
| 5 | option D's cost named KiCad 11, but the MCP server's SWIG path runs headless today | refuter (Opus) | acted | finding.md section 4, option D |
| 6 | tsci exports `specctra-dsn` itself, so Freerouting can route a tscircuit board with no KiCad | refuter (Opus) | acted | finding.md section 2.2 |
| 7 | the reuse table missed the pad aliases and the toolchain's install and pin | refuter (Opus) | acted | finding.md section 3.2 |
| 8 | "F5 blocks the Fusion import" claims more than one search summary supports | refuter (Opus) | acted | finding.md section 2.3 says "at risk", and section 9 names the HTTP 403 |
| 9 | six cited line numbers had slipped | refuter (Opus) | acted | finding.md sections 3 and 8 |
| 10 | the refill hides unrouted nets | refuter (Opus), its own test | rejected | with every zone removed, KiCad reports 0 unconnected items |
| 11 | the 199 isolated copper areas have one count on both exports | architect, refuter (Opus) | raised | cause not found. finding.md section 9 keeps it for the pour card |
| 12 | Freerouting 2.6.0 was not run: the permission check refused the downloaded binary | the session | raised | waits on the PO's yes. finding.md section 6, question 7 |
