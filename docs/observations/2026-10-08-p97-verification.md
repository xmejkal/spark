# The verification of the council's fix wave on spark PR #98 (P97, store 1c) — 2026-10-08

What was verified: the fix wave that followed the council on spark PR #98, P97 store 1c, read at `6924f54` on
2026-10-08. Three finders read it: a hallucination hunt over the pages the wave changed, a walk that followed README as
written, and a review of the whole wave. Then one refuter per finding checked it against the checkout. Of 32 unique
findings, 30 held and 2 were refuted. The controller ruled on each. The fixes are the commits whose subject begins
`P97 verification`: the code half from `72ebe96` to `23d1413`, then the pages. Every finding is a row in
[`INDEX.md`](INDEX.md): V1 to V32 are F1 to F32, in order.

Each line: the finding, where it was found, the claim in a few words, the verdict, and where it went.

- **F1** · `README.md:113` · Road 1's block cannot run in a fresh project: no line writes the needs · holds · `e09088f`
- **F2** · `README.md:117` · README never says what `$CLAUDE_PLUGIN_ROOT` is, or how to set it · holds · `e09088f`
- **F3** · `README.md:125` · the agent's dry-run preview leaves out the board, so it previews no hold · holds ·
  `e09088f`
- **F4** · `README.md:27` · with the library LED the XIAO stops at the schematic, not the footprint · holds · `72b7ad6`
  (now a named refusal), `5efadd5`
- **F5** · `docs/guide/agents.md:302` · `check_spine.py` reports an `emit_board.py` crash as problems, exit 1 · holds ·
  `0dd2975`, `88b50d3`
- **F6** · `README.md:86` · on Linux `/spark:setup` installs bun itself through npm; README said bun is yours · holds ·
  `1ee44c7`
- **F7** · `docs/guide/journey.md:410` · the hand-written soil-probe record, and that store's needs and drawer, are not
  shown · holds · `99c74bb`
- **F8** · `docs/guide/journey.md:478` · the gap example leaves out the board pick, without which `--requirements`
  refuses · holds · `99c74bb`
- **F9** · `scripts/emit_board.py:1069` · a series resistor emit_board cannot size is a traceback the chain reads as a
  defect in the design · holds · `72b7ad6`
- **F10** · `scripts/parts.py:1816` · `--fact-set`'s and `--function-set`'s refusals print without the part's name ·
  holds · `6f42aea`
- **F11** · `scripts/emit_board.py:713` · a `*/` in a record's name ends the board's comment, and what follows runs in
  `tsci build` · holds · `72ebe96`; P87's follow-through: `6c3a68e`, `01a4305`, `e8e3266`, `23d1413`, `2890e62`
- **F12** · `scripts/init_project.py:475` · a board that stops at the footprint stage is offered and picked without a
  word · holds · `61db204`, `729bc00`, `8b7d01d`
- **F13** · `commands/idea.md:48` · step M says an owed `simulation` stops only the simulation stage; L refuses the pick
  · holds · `448cfb1`
- **F14** · `scripts/needs.py:349` · the cleaning of a passed-over reason misses common URL and price forms, and a cut
  can leave junk · holds · `d124d66`, `50180f8`, `39d9901`
- **F15** · `scripts/parts.py:2032` · a speaker terminal picked without its amplifier is told to pick a supply · holds ·
  `058a449`, `447ad64`, `8b7d01d`
- **F16** · `scripts/needs.py:592` · `--requirements` writes drawer keys into `requirements.json` without a word · holds
  · `4f0d03f`, `8b7d01d`
- **F17** · `scripts/parts.py:1871` · "stops at the footprint stage" overstates the XIAO: with a computed series
  resistor it stops at the schematic · holds · declined for this PR → card: the XIAO's board file owes
  `power.io_volts` (3.3 V, cited)
- **F18** · `commands/setup.md:2` · "one yes" in seven places, while an install takes three answers · holds · `3101a22`
- **F19** · `docs/guide/journey.md:250` · the M step's question, whether the LED pack is `led-red-5mm`, is missing from
  the recorded run and Road 1 · holds · `c533c15`
- **F20** · `.claude-plugin/marketplace.json:11` · the marketplace entry names only the build chain · holds · `e80ee85`
- **F21** · `docs/observations/INDEX.md:229` · E36 credits too little and places none of the rest of C-36; E37 was only
  premature · holds · `5e4e70c`, `a08b3dd`
- **F22** · `docs/observations/2026-10-08-p97-store-1c-council.md:5` · "on the most capable model": nothing in the
  repository records which model ran the refuter · holds · `ca59e18`
- **F23** · `docs/2026-10-04-store-design.md:496` · §8 L's example above the amendment was not edited · refuted: the
  spec keeps an original sentence and amends beside it
- **F24** · `docs/guide/agents.md:19` · "Claude Code asks" holds only when the person's own settings do not answer
  first · holds · `8b9942c`
- **F25** · `docs/observations/2026-10-08-p97-store-1c-council.md:139` · a machine-local temp path in a committed file ·
  holds · `ca59e18`
- **F26** · `docs/observations/INDEX.md:228` · E36 is `acted` while most of C-36 was neither fixed nor a named item ·
  holds · `5e4e70c`, `a08b3dd`
- **F27** · `docs/observations/INDEX.md:196` · E4 and E16 are `acted`, but defer parts of their claims to an unnamed
  card · holds · `a08b3dd`
- **F28** · `docs/observations/INDEX.md:200` · the rows promoted to #94's checklist cannot be confirmed offline ·
  refuted: the controller confirmed that the checklist holds the 26
- **F29** · `docs/guide/journey.md:45` · the first `--audit` under "owed facts and gaps" ran in the shared store, not
  in one of its own · holds · `99c74bb`
- **F30** · `GLOSSARY.md:272` · the `built` digest covers only some of the facts the build reads · holds · `5670ac9`
- **F31** · `docs/2026-10-04-store-design.md:539` · §11's "then raise the budget" is not marked as replaced by P99 ·
  holds · `cb7b678`
- **F32** · `docs/2026-10-04-store-design.md:200` · the quoted `--audit` row has its padding collapsed · holds ·
  `cb7b678`

## Found on the way, not fixed

Three more, found while the code half was fixed. They are cards, not rows here.

- **A record's simulation chip name is unchecked.** `simulation.wokwi.chip` names the chip's files beside the record
  (the name plus a suffix), so a `../` in it reaches outside the record's chip folder when `sim_project.stage_chips`
  copies them. It is also written into `wokwi.toml` unescaped, as `name = "…"` and `binary = "chips/….chip.wasm"`, so a
  quote in it injects TOML. One name rule in `parts.validate` (letters, digits and `_`) would close both.
- **The simulation note is unescaped Markdown** (low). `WHAT-THIS-CANNOT-SHOW.md` carries each record's `stand_in` or
  `skip` sentence as it is. It is not code, but a line break there can forge Markdown structure, a heading or a list
  item, in the note beside the diagram.
- **The `--firmware` value lands in `wokwi.toml` unescaped** (low). `check_spine.py` writes it as `firmware = "…"`. It
  is the person's own argument, not record text.
