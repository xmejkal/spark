# P271 plan council, 2026-10-16

The plan in [plan.md](plan.md) is the version after both rounds. Each finding below is acted unless it says otherwise.

## Round 1: the tech lead and the PO assistant (Sonnet), the refuter (Opus)

- The refuter, reproduced in headless Chrome: inline, the schematic's `.boundary` rule turns the PCB's black background
  beige. Acted: each picture is an `<img>` data URI.
- The refuter, reproduced: the fixture's `circuit.json` keeps only `source_*` elements and exports blank pictures.
  Acted: step 1 measured button-light's full build.
- The refuter, reproduced: tsci 0.0.2600 fails on a bare relative `circuit.json`. Acted: the path is always absolute.
- The tech lead: `report()` had no toolchain, the breadboard tab read the disk, and a `dist/` that failed to copy could
  mix two builds. Acted: an injected exporter, the tab from the kept entry, and a gate on the kept `dist/`.
- The tech lead: "view" already meant `WIRING_VIEWS`. Acted: "tab" and "page".
- The PO assistant: the records still described the TS viewer, and Q5, Q6 and Q9 had no new status. Acted: D16,
  S3, A7, items and the Q lines.

## Round 2: the PO assistant, the tech lead and a senior engineer (Sonnet)

- The tech lead: the layout check could not be built from the layout alone, since it holds Wokwi pins and anonymous
  holes. Acted: the PO chose "One source now, check later" (D17), and the check is P279 (#317).
- The tech lead: export and sheet must read the same circuit. Acted: both read the kept `circuit.json`, behind one gate.
- The senior engineer: no mutation table, the temporary file was unspecified, and step 1 named no real path. Acted:
  `tests/mutations/p271-page.json`, a `TemporaryDirectory` with an empty-output check, and `/Users/petr/Development/button-light`.
- The PO assistant: no list of what waits on the PO, and `tabs.html` is not his word. Acted: "Waits on the PO" and
  `page.html`.
