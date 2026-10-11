The same placeholder record, with a physical block that is invented whole: a two-row header (4 and 4 pins at
2.54 mm, rows 22.86 mm apart), its drill and pad sizes, the first pad's offset and flush edge, the header order,
the footprint names, the board's dimensions and the Wokwi size. That is what lets the chain build it. From
P158's part 2 (#94), the A3 approach's run 2.

What the baseline of 2026-10-11 recorded: `--validate --for-fab` ok, exit 0, and the chain runs end to end, exit 0
(9 traces written, 7 built, 7 wires in the diagram), the same numbers A3 recorded on 2026-10-10. Nothing in the output
says the header was invented: a placeholder passes in silence.

Under the placeholder name, the record is the FireBeetle 2 S3's: its SKUs, three sources, four documents and verified
power facts stay. A3's run 2 marked the I/O voltage unverified, an assumption; these fixtures do not.
