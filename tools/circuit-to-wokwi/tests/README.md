# What is here, and what deliberately is not

These tests are the CONVERTER's: a netlist, a mapping, a merge, a name, a pad alias. They take a
board file through `SPARK_BOARD_JSON` and know nothing about any particular design.

**`real-board.test.ts` stayed in the smart bin's repository** when the converter moved here
(backlog P32a). It reads that repo's `dist/board/circuit.json`, that repo's chips directory and
that repo's root `mcu-pins` module — it tests a nineteen-component board end to end, which is
knowledge of that board and not of this tool. Moving it would have meant shipping one project's
design as the plugin's test data.

The coverage is not lost. The plugin's own end-to-end proof is `check_spine.py`'s simulation
stage, which runs this converter over the reference design and is exercised by the Python suite.
