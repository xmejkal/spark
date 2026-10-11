# P158 part 1 — diagnosis: needs, matching and the vocabulary (K33–K42, K44)

Written 2026-10-10 by the diagnostician for the area *needs-matching-vocabulary*, against spark 0.8.1 (main `a8aa34d`,
`git log -1`, 2026-10-10). Every behaviour below was read from the code first and then reproduced on a **copy** of the
PO's store (`cp -R` of `~/.local/share/spark` into `<scratch>/store`, 2026-10-10 11:49; every command prefixed
`SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp`; `env | grep SPARK_HOME` under the prefix printed
the scratch path). Two scratch edits were made to that copy and are named where they matter: nine synthetic drawer
entries for the cap run (removed afterwards, `grep -c` 0), and the bin's hold on the S3 released (`--drawer-set`
`{"entry": "dfrobot-dfr0975", "used_in": {}}`) so that the irrigation copy could pick a board. Nothing touched the real
store, `~/Development/irrigation`, `~/Development/plant-alarm` or the bin.

Tags: **E** a pointer (file:line in spark unless another repository is named; a command and what it printed); **H** a
claim with its source only; **D** a decision, by whom and when; **—** unknown. The catalogue's rows are
`docs/discovery/2026-10-10-p158-gaps-and-refactoring/catalogue.md`, K33–K44.

The PO's criteria (2026-10-10, verbatim): *"we want the system to be well designed so its well testable and
understandable where a mistake is happening and why"*. Each root cause ends with the diagnosability test — what output,
if any, pointed at it — and each change says how it becomes testable and what its failure prints.

## 1. Root causes

### RC-needs-matching-vocabulary-1 · Two matchers, two vocabularies, and neither reads the other's data

**where.** `scripts/parts.py:1326-1329` — `_matches(words, part_id, record)` builds one haystack of `id`, `name`,
`kind` and `also_known_as` and requires `all(word.lower() in haystack for word in words)`; `scripts/parts.py:1332-1352`
(`need`) walks `available(project)` = project → shelf → library (`scripts/store.py`, `layers`: the catalog only with
`drafts`), then `catalog_matches` (`scripts/parts.py:891-894`) adds the catalog with the same `_matches`. The drawer is
not walked and `function` is not read. The second matcher is `scripts/needs.py:126-130` (`_what_matches`: every word of
the need's `what` inside a same-verb `function.what`, or inside the name or an alias) behind the verb gate of
`scripts/needs.py:163-196` (`candidates`), which does read the drawer and `function`, and never `kind` words.

**why.** `--need` is the research command's reuse check (E `commands/research.md` §1 "Reuse first"; it entered on
2026-09-29, `6557c71`, "Need-based from here"); `function` arrived on 2026-10-04 (`84443db`) and `--match` the same day
(`008fc55`), as a second matcher in a second module, and nobody went back to teach the first one the new field or the
drawer. The AND makes every extra word a filter, so a unit or a number in the person's phrase ("12 V inlet") hides the
part, and a synonym ("soil sensor" for a record whose name says "Soil Moisture Sensor") finds nothing. The data was
patched instead of the code: the catalog's two screw terminals carry the alias `"12 V inlet"`, the PJ-002A jack
`"power inlet"`, and irrigation's jack `"power inlet", "12 V inlet", "12v inlet"` (E `<scratch>/store/catalog/
mkds-1-5-2-5-08-screw-terminal.json`, `wj500v-5-08-2p-screw-terminal.json`, `pj-002a-dc-jack.json` `also_known_as`;
E `~/Development/irrigation/parts/dc-barrel-jack-12v-inlet.json` `also_known_as`; E `~/Development/irrigation/DIARY.md:218-223`
"the inlet's record carries the phrase as an alias, and `--need` still requires every word"). So the words that work
are the words someone already typed into an alias — the vocabulary the person has to guess is the one the aliases
happen to hold.

**reproduced** (`<scratch>`, 2026-10-10, exit 0 each): `--need 12 V inlet` → the two screw terminals (catalog), not
`jst-ph-2-power-inlet`; `--need power inlet` → `jst-ph-2-power-inlet` and `pj-002a-dc-jack`; `--need soil sensor` →
"nothing in the library matches 'soil sensor'. Research it: /spark:research "soil sensor""; `--need soil moisture` and
`--need moisture sensor` → `sen0193-soil-moisture`; `--need footswitch`, `--need foot switch`, `--need temperature` →
nothing; `--need inlet` → four inlets. Meanwhile `--match` on a project with `input / footswitch` offered
`tactile-button (library) button [other words]` — the two matchers disagree about the same store.

**kind.** design (two matchers for one question) and implementation (the AND over free words).
**explains.** K33 whole; the research hint half of K42 (a gap reached through `--need` is declared before the drawer
or the functions were looked at).
**how anyone would have known.** The answer says "nothing in the library matches" and sends the person to research; it
does not say which words were looked for where, that the drawer is not searched, or which of the words missed. USER-9
found it by trying synonyms (E `council/user.md:17`); I1 found it on 2026-09-29 (E `DIARY.md:26-31`). No test pins the
behaviour as wrong: `tests/test_parts.py:791-797` pins the AND as right (`["motor", "driver"]` → exactly
`l9110s-module`).

### RC-needs-matching-vocabulary-2 · The pick does not consult the match, and nothing records that a pick was a looser fit

**where.** `scripts/needs.py:267-330` (`plan_pick`) resolves each id (`_resolve`, `:285`), refuses a need or an id
spark does not have (`:285-287`), then does the reservation arithmetic (`:297-311`); it never calls `candidates()` or
`_what_matches`, so `what_matches`, `owes`, "no record" and `stops_at` — all computed by `--match` — are not in reach
when the decision is written. `scripts/parts.py:1988-2015` (`_op_pick`) prints the reservations and `need: id`.
`scripts/needs.py:66-70` (`faults`) checks each field alone, so `mark` and `pick` are never read together.
`scripts/parts.py:1940-1946` (`_op_needs`) prints `id does / what (condition) [mark]` — the pick is not in the text
listing at all (it is in `--json`). `commands/idea.md:50-52` says of `[other words]` "whether it is similar enough is
your call, said to the person" and gives no rule for the case where every candidate is `[other words]`.

**why.** By decision the agent judges fit and the code only lists (D the PO, 2026-10-04, store design §5.6 and §11 "the
matcher: a function field and the agent's judgement"; §6.2's matcher seam: "the mark (agent; its reason is said to the
person)"). The split between `--pick` and `--requirements` is also by design — "`--pick` takes the record either way;
`--requirements` decides" (E `docs/guide/journey.md:448`) — so that a pick can stand while owed facts are filled. What
was left out is the hand-over: the judgement happens in the conversation and the project file keeps only its result
(`pick`), with no trace of "this pick does not say the need's words", and the reason goes to the history only when the
agent writes a `--passed-over` file for the parts *not* taken (`scripts/needs.py:318-328`). The record of intent and
the record of the choice can therefore disagree silently.

**reproduced** (`<scratch>`, 2026-10-10): `--match` for `temp — sense / temperature` offered
`sen0193-soil-moisture (shelf) soil-moisture [other words]` and `vl6180x-breakout (library) distance [other words]`;
`--pick <node> temp=sen0193-soil-moisture` → exit 0, "set dfrobot-sen0193: used_in {"plant-alarm": 1} →
{"plant-alarm": 1, "node": 1}" / "temp: sen0193-soil-moisture" / "wrote to your history: 1 reused" — not a word about
the fit; `needs.json` then holds `{"id": "temp", "does": "sense", "what": "temperature", "pick": [{"part":
"sen0193-soil-moisture"}]}`; `--needs <node>` prints `temp sense / temperature` with no pick; `--needs-set`
`[{"id": "temp", "mark": "gap"}]` on that picked need → `would set temp: mark null → "gap"`, exit 0 — a need marked a
gap and holding a pick is accepted.

**kind.** design.
**explains.** K34 whole; the "pick → requirements split" the area scope names (its board half is K29, another area).
**how anyone would have known.** Nothing printed by `--pick`, `--needs` or `--needs-set` points at it; only `--match`
run again shows `[other words]` beside the picked id, and only to someone who remembers the pick. USER-2 and USER-10
knew because they had made the pick themselves (E `council/user.md:10`, `:18`).

### RC-needs-matching-vocabulary-3 · The needs file has no way to say "gone": no removal, no rename, no un-pick

**where.** `scripts/needs.py:74-102` (`plan_set`): `after = dict(before or {}, **item)` (`:89`) sets or adds; `order
+= [] if need_id in current else [need_id]` (`:96`) appends; nothing removes. A `null` `does` or `what` is refused by
`CHECKS` (`:29-30`); any other key is refused by `faults` (`:66-70`, "not a need's field"). A pick cannot be cleared
either: `--pick <project> temp=` reaches `_resolve("")` and is refused as "no record or drawer entry called  —
--match lists the candidates" (`scripts/needs.py:287`; note the empty name between "called" and the dash). The module's
docstring states the rule — "Every write sets, never adds" (`scripts/needs.py:7`) — and `commands/idea.md:25` tells the
agent "there is no removing or renaming a need yet, so a wrong one is fixed by hand in `<project>/.spark/needs.json`".

**why.** The set-only rule was carried over from the drawer, where it works because the drawer has a tombstone:
"nothing is deleted — gone is count 0" and `skip` (E `scripts/drawer.py:6-7`, `:24`). The needs file got the rule
without a tombstone, so the only way to express "this need was wrong" is outside the tool, in a file the tool
otherwise validates on read and refuses with "fix it by hand" (`scripts/needs.py:40-62`). A rename is also not a
field change: the need's id names the component in the requirements file (`_name_after`, `scripts/needs.py:425`), so
renaming has consequences the hand edit cannot see.

**reproduced** (`<scratch>`, 2026-10-10): `[{"id": "temp", "does": null, "what": null}]` → refused, "`does` is one of
sense, …" and "`what` is a few words", exit 1; `[{"id": "temp"}]` → "nothing to change", exit 0; `[{"id": "temp",
"remove": true}]` → "remove: not a need's field — a need holds does, what, condition, mark, pick, and no part number,
count, place or reason (§5.3)", exit 1; a "rename" `[{"id": "soil-temp", …}]` → "would set soil-temp: …" — an addition,
the old need stays.

**kind.** design (a rule borrowed without its tombstone).
**explains.** K35 whole; it also closes the exit from K34 (a wrong pick cannot be undone, only replaced).
**how anyone would have known.** The refusals name the fields and the verbs correctly, and never say how to remove;
the single pointer is the sentence in idea.md. An agent that has read idea.md knows; a person at the terminal does not.

### RC-needs-matching-vocabulary-4 · Candidacy needs a verb the imported thing was never given, and nothing counts what that hides

**where.** `scripts/needs.py:191` — a drawer entry is skipped unless `any(f.get("does") == need["does"] for f in
functions)` where `functions = entry.get("function") or []`; an entry with an `is` is reached through its record
(`:189-191`), one with neither is unreachable by any need. `scripts/drawer.py:359` — the DFRobot importer's values are
`label`, `count`, `part_number`, `from`, `bought`, `unsure`: no `function`. `scripts/drawer.py:276-284` (`listing`)
shows `entry`, `label`, `count`, `is`, `in`, `unsure`, `skip` — not `function`. `scripts/parts.py:134-172` (`audit`)
lists "says nothing of what it does" for *records* only (`:172`, `silent.append(found)` inside the records walk); the
drawer's silent entries are counted nowhere. The behaviour is pinned as intended:
`tests/test_needs.py:472` `test_an_owned_part_that_says_nothing_of_what_it_does_is_no_candidate`.

**why.** The design made `function` optional on an entry — "An entry may have none ('function unknown', asked once)"
(store design §5.6) — and "imported parts count as owned; the person corrects" (§11). The import never asks the
question, and no later step asks it either, so the drawer that the owned-first promise (§5.5 "drawer → project → shelf
→ library → catalog") runs over is mostly mute: on the 2026-10-10 copy, **110 entries; 12 with `is`, 12 with
`function`, 5 with both; 91 with neither; 1 marked `skip`** (E my count over `<scratch>/store/drawer/*.json`; the
P162 council's "91 of the 110" on 2026-10-08, #99 comment 2026-10-08T12:28, agrees; its "17 of 110" reachable is 19
on this copy — two entries were linked since, H). Among the 91: four ESP board SKUs (`dfrobot-dfr0575` ×2,
`dfrobot-dfr0994` ×1, `dfrobot-dfr1075` ×2, `dfrobot-dfr1117` ×3) and five distance sensors (`dfrobot-sen0042`,
`-sen0311`, `-sen0395`, `-sen0589`, `-sen0623`) (E the same listing). The ranking then shows a record-less drawer
entry above a library record of the same function — `l298n-board-hw-095 (drawer)` above `l9110s-module (library)` for
`drive / motor-dc` — because the sort key is `(owned == 0, not what_matches, LAYERS.index, id)`
(`scripts/needs.py:195-196`) and the drawer is layer 0 (§5.5, by design); the entry's candidate carries `"owes": []`
exactly like a complete record (`scripts/needs.py:155-160`, the default dict), so "cannot be placed" shows only as
`"id": null` in JSON and as "(drawer)" in text.

**reproduced** (`<scratch>`, 2026-10-10): `--match` for `board — compute / microcontroller` → two candidates,
`firebeetle2-esp32s3 (library) … free 0` and `xiao-esp32-c6 (library) … free 0 stops at the footprint stage (P121)`,
while the drawer holds six ESP SKUs (the two linked ones plus the four above); `dist — sense / obstacle ahead` → the
soil probe and the VL6180X only, none of the five owned distance sensors; `motor — drive / motor-dc` → the L298N entry
first, the L9110S record second, both `owes []`.

**kind.** data (the entries) and design (nothing asks, nothing counts, nothing says).
**explains.** K36 whole; the "every owned module with that function" half of K44; the data half of K42 (a gap is
declared over a drawer that cannot answer).
**how anyone would have known.** No output. `--match` shows what it found, never what it could not look at; `--drawer`
cannot show a missing function (the listing has no such column); `--audit` is silent about entries. The idea command's
only hint is about records: "a record may say nothing of what it does — such a record is never offered. Look: --audit"
(`commands/idea.md:63-67`). The #99 council found the 91 by counting files.

### RC-needs-matching-vocabulary-5 · Research writes records that owe what the chain reads and say nothing of what they do, and no test ties the skeleton to the contract

**where.** `scripts/parts.py:1354-1378` (`skeleton`) writes `schema, id, name, kind, //, vendor, sku, sources, needs,
power, unused_pins, pin_order, footprint, body_mm, facts, host_requirements, sourcing, //sourcing` — no `function`, no
`pin_order_proof`, no `simulation` (E `--skeleton x-probe --kind sensor … --dry-run --json`, keys printed 2026-10-10).
`scripts/parts.py:98` `CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")`;
`scripts/parts.py:107-110` (`owes`). `scripts/parts.py:65-70` `KIND_FUNCTION` maps eleven kinds and the comment above
it says `sensor` and `connector` are "written once, through `--function-set`" — the two kinds research produces most.
`tests/test_parts.py:853-867` asserts a skeleton is refused until filled, not that it holds every chain fact.
`skills/spark-design/references/part-data.md:12-31` (the worked record agents are told to read) shows `pin_order_proof`
and no `function` or `simulation`; `agents/parts-researcher.md:76-104` lists the fields and names neither;
`commands/research.md` §4 checks `--validate`, `--sources`, `--unverified` and never `--audit` or `--function-set`.

**why.** The skeleton is of 2026-09-29 (`6557c71`); `simulation` became a record fact the same day (`1e77b88`, P31),
`pin_order_proof` on 2026-10-03 (`c2afc47`, P81), `function` and `CHAIN_FACTS` on 2026-10-04 (`84443db`, `b9fcf8a`)
(E `git log --date=short -S…`). Each added a fact the chain reads without revisiting the file research starts from, and
no test says "the skeleton holds every chain fact", so the drift had no alarm. The consequence is systematic: every
researched record arrives owing `pin_order_proof` and `simulation` at least, and a sensor or connector arrives with no
function, so `--match` never marks it `what_matches` and, for a `sensor`, never lists it at all.

**reproduced** (`<scratch>`, 2026-10-10): `--audit` → "catalog 0 current, 17 owe facts, 0 broken"; every one of the 17
owes `pin_order_proof` and `simulation`; "says nothing of what it does — set it once with --function-set <part> <file>:"
names 10 (six jacks and terminals, four flow meters and sensors). `--audit --project <irrigation copy>` adds
`dc-barrel-jack-12v-inlet`, `sen0217-flow-meter`, `sen0308-soil-moisture`: so `--match` on the irrigation copy offered
for `flow — sense / flow` only the soil probe and the VL6180X `[other words]` — neither the owned SEN0217 (drawer
`dfrobot-sen0217`, linked) nor the catalog's SEN0550 — and for `soil` the shelf's SEN0193, not the project's own
SEN0308. `inlet — connect / power-inlet (12 V)` offered the JST inlet, not the project's own jack.

**kind.** implementation (a stale skeleton, a missing test) and documentation (the agents' schema and the research
checklist).
**explains.** K37 whole; the `[other words]`-only lists of K34 where the fitting part is a researched record.
**how anyone would have known.** `--audit` does say both things, in the right words ("owes: pin_order_proof,
simulation"; "says nothing of what it does — set it once with --function-set"), but the research command never runs it
and `--match` shows the consequence without the cause. An agent following research.md ends with "`--validate` passes"
and a record the matcher cannot see.

### RC-needs-matching-vocabulary-6 · The candidate list ranks by place, then cuts at eight, and the cut is unreachable

**where.** `scripts/needs.py:195-196` sort key `(owned == 0, not what_matches, LAYERS.index(in), id)`;
`scripts/parts.py:1955` `kept = [c for rank, c in enumerate(need["candidates"]) if rank < 8 or c["what_matches"]]`;
`:1956` `need["more"], need["candidates"] = len(…) - len(kept), kept` — the cut candidates leave the data before
`page()` runs (`:1957`), so `--from` pages needs, never the hidden candidates; `:1969` prints "… %d more, none with the
need's words". The page budget is `scripts/outcomes.py:82` (`page(…, limit=20, budget=3400)`, "an agent's answer stays
under 4 KB by default", §6.4.4).

**why.** The only measure of fit is the exact-word test, so when a person's words match no `what` (the normal case for
words of their own — "obstacle ahead"), every candidate is equally unfit and place decides; owned drawer entries come
first by design (§5.5), fill the eight, and the right kind drops behind the fold. The cap protects the 4 KB answer, but
unlike `page()` it has no `next`: nothing lists what it cut. The P162 analysis read this as "hides an answer only when the
need's words match nothing" (#99 comment 2026-10-08T12:28) — true, and that is precisely the case a person's own words
produce.

**reproduced** (`<scratch>`, 2026-10-10, nine synthetic owned entries `zz-synthetic-<word>` with `sense / <co2, gas,
humidity, light, ph, pressure, rain, thermometer, uv>` added to the copy, removed afterwards): `--match` for `dist — sense
/ obstacle ahead` listed eight synthetic entries and "… 3 more, none with the need's words"; `--json` carried
`shown 8, more 3` and no id of the three — among them `vl6180x-breakout`, the one rangefinder. No `--match` argument
reaches them.

**kind.** design.
**explains.** K41 whole; it sharpens K34 (the fitting candidate is not just marked `[other words]`, it can be absent).
**how anyone would have known.** The line says three were cut and that none shares the need's words; it does not say
which `what` words they carry, and there is no command to ask. An agent cannot tell "distance" was behind the fold.

### RC-needs-matching-vocabulary-7 · A need holds picks, not quantities; a pick is one piece

**where.** `scripts/needs.py:292` `elif pick not in picked.setdefault(need_id, [])` — the same id given twice for one
need is taken once; `:297` `wanted = collections.Counter(…)` counts one piece per pick; `scripts/needs.py:463-495`
(`_merge_parts`) adds one `parts` entry per pick; `commands/idea.md:37` "A need holds no reason, count or place".

**why.** The design's "no counts" means no *owned* counts in the project file (§5.3 "holds no owned counts, places or
reasons" — privacy, §5.8); the walking skeleton was the plant alarm, one of each (§8 S–L); irrigation is the first design
with multiples (four valves, three probes, E `~/Development/irrigation/irrigation.requirements.json` `parts`: `Valve1`–`Valve4`,
`Soil1`–`Soil3`), and "how many the design uses" was never separated from "how many are owned". The only way to say
four is four needs.

**reproduced** (`<scratch>`, 2026-10-10): `--pick <irr> … valve=dfr0457-mosfet-power-controller
valve=dfr0457-mosfet-power-controller …` → "set dfrobot-dfr0457: used_in null → {"irr": 1}" and "valve:
dfr0457-mosfet-power-controller" once; `needs.json` holds one pick; the drawer entry (count 8) is reserved 1.

**kind.** design.
**explains.** K39 whole.
**how anyone would have known.** The doubled argument produced no "given twice, taken once"; the drawer line says
`→ {"irr": 1}`, which is only wrong if you know the design uses four. `--requirements` over an existing file then
says "kept, not from a pick: Valve2 …" (E FEAS-8, `council/tech-lead.md:18`) — a sentence that blames the file for
holding what the model cannot express.

### RC-needs-matching-vocabulary-8 · `--requirements` knows one file name and never looks beside it

**where.** `scripts/needs.py:381` `REQUIREMENTS = "requirements.json"`; `:607` `file = Path(project) / REQUIREMENTS`
is the only file read and merged into; `scripts/parts.py:2070-2075` writes the same path. The chain's readers take any
name: `scripts/emit_board.py:1037` `parser.add_argument("requirements")`, `scripts/check_spine.py:573-574`
`parser.add_argument("requirements", nargs="?", help="a requirements.json; omit for the reference design")`.

**why.** The chain's commands were written with a positional file (irrigation's convention `<project>.requirements.json`
dates from 2026-09-29, E `DIARY.md`), and the store's writer, added on 2026-10-08 (P97), was given a fixed name with no
look-around. Two conventions for one file, and the newer one does not know the older exists.

**reproduced** (`<scratch>`, 2026-10-10, irrigation copied with its `irrigation.requirements.json` of 12 parts and one
signal): `--requirements <irr> --dry-run` → "would write <irr>/requirements.json: board firebeetle2-esp32s3; parts
dc-barrel-jack-12v-inlet, dfr0831-buck-5v, dfr0457-mosfet-power-controller, sen0308-soil-moisture, sen0217-flow-meter,
ds3231-at24c32-rtc-module"; the real run wrote it (keys `board`, `parts`; 6 parts, no `signals`, no names) and said
nothing of the 12-part file beside it (keys `board`, `parts`, `signals`, `//`).

**kind.** implementation (a missing check) over a design inconsistency (positional file versus fixed name).
**explains.** K40 whole.
**how anyone would have known.** Not from the output: "wrote requirements.json: …" is the whole of it. A person who
then runs `/spark:build` is in the other area's K-rows (which file the build reads).

### RC-needs-matching-vocabulary-9 · `does` is closed and `what` is open — by decision — and the store's own `what` words are shown nowhere before a need is written

**where.** `scripts/parts.py:60-61` `VERBS` (13); `scripts/needs.py:29` refuses any other `does`;
`scripts/parts.py:65-70` `KIND_FUNCTION` hard-codes `what` words (`audio-player`, `load-switch`, `light`, `rtc`,
`motor-dc`, …) while drawer functions are typed freely (`mp3-player` on `dfrobot-dfr0768` and `mp3-mini-module`, E
`<scratch>/store/drawer/*.json`); `scripts/parts.py:1472-1537` (`OPERATIONS`): no operation lists the vocabulary;
`scripts/parts.py:1944`, `:1960` print `condition` and nothing reads it (E `grep -n condition scripts/*.py`: those two
lines and the field's check).

**why.** The 13 verbs are the PO's (D 2026-10-04, §5.6, §11), `what` is "open words" by the same decision, and the
agent judges similarity; the drift between a drawer's `mp3-player` and the library's `audio-player` is therefore
designed in, and `[other words]` flags it honestly on both sides. What is missing is the lookup: the whole store's
vocabulary is **19 distinct (does, what) pairs** across the library, the catalog, the shelf, the two boards and the
drawer (E my count over `~/Development/spark/parts`, `boards`, `<scratch>/store/{catalog,shelf,drawer}`, 2026-10-10),
and nothing exposes it to the agent writing a need, so the need is written in the person's words and matched against
words nobody showed them. `condition` is the agent's input by design ("the agent judges similarity") but the output
gives no sign that code ignores it.

**reproduced** (`<scratch>`, 2026-10-10): `--needs-set` with `{"does": "switch"}` → "refused, so nothing was written:
sw — `does` is one of sense, input, indicate, sound, move, drive, power, keep-time, store, compute, communicate,
connect, mount", exit 1; `--match` for `mp3 — sound / mp3-player` marked the two drawer entries and showed
`dfr0534-module (library) audio-player [other words]`; for `audio — sound / audio-player` the reverse.

**kind.** design (intended) and implementation (no listing).
**explains.** K38 whole; it feeds K41 and K34 (a need written in the store's words would match, rank first and never be
cut).
**how anyone would have known.** The verb refusal is the one well-diagnosed failure in this area: it lists the 13. The
word drift shows as `[other words]` with no explanation; the condition is printed in the header and silently unread.

### Noted, not a root cause of this area: G and "equivalents" are absent features

K42 (research only the gap) and K44 (choosing among equivalent owned modules) are P162 (#99) and P157 (#93): features
the design names (§8 G; the PO's words of 2026-10-07) and 1c left out on purpose (W14, #99 body). Where the seams end
today, from the code: a gap is the line "nothing in the store does this — a gap" (`scripts/parts.py:1970`) or the
research hint (`:1634-1636`); `/spark:research` has flows for a module and for a commodity part and none for a board
(E `commands/research.md` §2 and "What this does not do"); `cost.STEPS` names a step `G` (`scripts/cost.py:43`) that no
operation marks or serves; a candidate carries `id, kind, entry, owes, broken, proof, in, label, what, what_matches,
owned, free, unsure[, stops_at]` (`scripts/needs.py:155-160`) and no fact a "minimal one" could be chosen by. Both
depend on RC-4 and RC-5 (the data a recommendation would read) and RC-6 (a ranking that is not place): built on
today's data, "every owned module with that function" would list two of six boards.

## 2. What the design gets right and must be kept

- **A verb gate plus the agent's judgement**, with the word test as a flag, not a filter (store design §5.6, §6.2 matcher
  seam; `scripts/needs.py:126-130`, `:163-196`). `[other words]` is honest; `what_matches` is in the JSON; the words are
  normalised (`tests/test_needs.py:297`, "soil moisture", "Soil Moisture ", "soil-moisture" all match); a word-matching
  candidate is never cut by the cap (`tests/test_needs.py:327`). Replace the ranking and the cut, not the gate.
- **Set-only writes with a dry run and "was → now" lines**, refusals that write nothing, a file validated on read with
  the need and the fault named (`scripts/needs.py:40-62`, `:74-102`; `tests/test_needs.py:53-201`). Removal must join
  this discipline, not bypass it.
- **The needs file keeps no reasons, counts of ownership, places or part numbers** (§5.3, §5.8): the project may be
  public. A design quantity (RC-7) is not an owned count and does not break this; a reason still goes to the history.
- **The reservation arithmetic and its refusals** — "N owned, held by X — M picked here" with `_how_to_free`'s exact
  fix (`scripts/needs.py:297-311`, `:250`); one stock however it is named (`_as_record`).
- **`--audit`'s sentences**: "owes: pin_order_proof, simulation" and "says nothing of what it does — set it once with
  --function-set <part> <file>" (`scripts/parts.py:1929-1931`) name the fault and the fix command. RC-5's change
  routes research through them rather than inventing new words.
- **The pick → requirements split itself**: a pick stands while facts are filled; `--requirements` refuses by name with
  `_how_to_fill` (`scripts/needs.py:571`); `unserved` reaches the build's verdict (C-2). RC-2 adds a hand-over
  to the pick, it does not merge the two.
- **One `OPERATIONS` table, one envelope** (`scripts/parts.py:1472-1537`; `outcomes.page` with `truncated.next`),
  **`--need` surviving a researcher's draft** (I3; `scripts/parts.py:1340-1348`), **drawer entries with a function but
  no record are candidates** (§5.2's light entry; `tests/test_needs.py:262`), **`function_of` falls back to `kind`** for
  eleven kinds (`scripts/parts.py:72-78`).

## 3. Changes

Each block: kind · size (S under an hour, M a day, L more) · fixes · removes or adds · testable · diagnosable · proof.
Remove before add: C1 and C5 delete a code path or a gap; C2, C4, C6, C9 add sentences to answers that exist; C3, C7
and C8 add a field or a check and are the PO's to order.

### C1 · One matcher: `--need` reads `function.what` and the drawer, matches by words hit, and says which words missed
kind: bug · size: S · fixes: K33, the research-hint half of K42
- **removes** `parts._matches` as a separate rule (`scripts/parts.py:1326-1329`) and the alias workarounds' reason to
  exist (the PO's catalog aliases "12 V inlet"/"power inlet" stay his data; irrigation's are its own).
- **adds** one function `words_hit(words, texts) -> set` used by `--need` and by `needs._what_matches` over the same
  texts (id, name, kind, aliases, every `function.what`); `--need` keeps every record and every live drawer entry with at
  least one word hit, sorted by hits desc, and prints `matched: inlet · missed: 12, v` per line; a drawer entry prints
  `(drawer, no record)`.
- **testable**: `tests/test_parts.py` — `test_need_12_v_inlet_finds_the_jst_inlet_and_says_which_words_missed`
  (asserts `jst-ph-2-power-inlet` present, `missed: 12, v`); `test_need_reads_a_function_word_the_name_does_not_say`
  (a catalog record `function: sense/temperature`, name "SEN0xxx probe" found by `--need temperature`);
  `test_need_offers_a_drawer_entry_with_the_word_and_names_it_record_less`. The existing AND test (`:794`,
  `["motor", "driver"]` → exactly the L9110S) becomes "ranked first with 2 of 2 hits".
- **diagnosable**: every line says what matched and what did not; the empty answer becomes
  `nothing holds any of: soil, sensor — the store's words near this verb: distance, soil-moisture (parts.py --match
  lists them per need); the drawer was searched (110 entries, 91 say nothing of what they do)`.
- **proof** the PO can read: `--need 12 V inlet`, `--need soil sensor`, `--need footswitch` on a copy of his store, each
  answer naming a part he has or the words that missed; I1 closed in the irrigation diary.

### C2 · The pick says what the match knew, and the needs listing shows the pick
kind: story · size: S–M · fixes: K34
- **adds** to `plan_pick` (`scripts/needs.py:267-330`) one call of `candidates()` per picked need and a note per pick:
  `temp: sen0193-soil-moisture does soil-moisture, not temperature — [other words]: say why to the person, or pick
  another`; `…: no record — reserved, not placed`; `…: owes footprint, simulation — --requirements will refuse until
  filled`. Adds `pick` and `mark` to `--needs`' text line (`scripts/parts.py:1940-1946`). Adds to `faults`
  (`scripts/needs.py:66-70`) one pair rule: `mark: gap` with a pick, or `have`/`know` with none, is refused — "a need
  marked gap holds a pick; mark it, or un-pick it".
- **removes** nothing; idea.md's M step gains the rule for the all-`[other words]` case: mark the need `gap` and pick
  nothing, or pick and say why — never both silently.
- **testable**: `tests/test_needs.py` — `test_a_pick_of_a_candidate_with_other_words_says_so`,
  `test_a_pick_with_no_record_says_reserved_not_placed`, `test_a_mark_that_contradicts_the_pick_is_refused`,
  `test_the_needs_listing_shows_each_pick_and_mark`.
- **diagnosable**: the sentence above, at the moment of the decision, in the pick's own answer; and `--needs` shows a
  `temperature` need carrying a soil probe on one line.
- **proof**: the USER-2 walk re-run on a copy: the pick prints the note; the needs listing shows it; the brief's
  "needs.json says one thing and the board another" cannot happen silently.

### C3 · A need can be dropped, and a pick cleared, through the same set-only door
kind: story · size: M · fixes: K35 (and the exit from K34)
- **adds** `{"id": "temp", "drop": true}` to `--needs-set`: the need leaves the file, its holds are recomputed by the
  same arithmetic `--pick` uses (extract `_reserve(after, entries, name)` from `plan_pick` `:297-311` so both call one
  function — a refactor, not a copy), and the answer says `dropped temp — released dfrobot-sen0193: 1 of 1`; `--pick
  <project> temp=` (empty) clears the need's picks and says `temp: no pick — released …`. A rename is drop plus add and
  the answer says so, because the id names the component in requirements.json (`_name_after`).
- **removes** the sentence "there is no removing or renaming a need yet, so a wrong one is fixed by hand"
  (`commands/idea.md:25`) and the double-space refusal for an empty pick (`scripts/needs.py:287`).
- **testable**: `test_a_dropped_need_releases_its_holds_and_is_said`, `test_an_empty_pick_clears_and_releases`,
  `test_a_drop_is_set_only_a_retry_changes_nothing`, `test_a_drop_of_a_need_the_requirements_file_names_says_so`.
- **diagnosable**: "dropped temp — released …" / "temp: no pick — released …"; a drop of an unknown id: "no need called
  temp — --needs lists them" (the existing sentence).
- **proof**: the K35 sequence on a copy ends with the need gone and the drawer's `used_in` back to what it was, by
  commands alone.

### C4 · Every answer that runs over the drawer says how many entries it could not look at
kind: story · size: S (code) + the PO's data pass · fixes: K36; the data half of K42 and K44
- **adds** one line to `--match` when any live entry has neither `is` nor `function`: `91 of 110 drawer entries say
  nothing of what they do, so no need reaches them — /spark:drawer sets function; the nearest by label for this
  verb: …` (the label words that contain any of the need's words, at most three — the hand-off the #99 council asked
  for); `drawer_silent` in `--audit` (count and keys) beside `no_function`; a `function` column in `--drawer`'s text
  (`—` when none). Then, as data, the PO's pass over his 91 labels in `/spark:drawer` — proposals by the agent, written
  only after his yes (C-35; #99 pitch 1).
- **removes** nothing.
- **testable**: `test_match_counts_the_entries_no_need_can_reach`, `test_audit_lists_silent_drawer_entries`,
  `test_the_drawer_listing_shows_a_missing_function`.
- **diagnosable**: the count, the fix command and the nearest labels, on the answer that is otherwise short.
- **proof**: on his store, `--match` for `compute / microcontroller` lists six boards after the pass, and before it says
  why it lists two.

### C5 · The research skeleton carries every fact the chain reads, and research ends with `--audit`
kind: bug · size: S · fixes: K37
- **adds** `function: null`, `pin_order_proof: null`, `simulation: null` to `skeleton()` (`scripts/parts.py:1354-1378`,
  with one `//` line each saying what fills it); a test `set(CHAIN_FACTS) | {"function"} <= set(skeleton(...))` so the
  next chain fact cannot drift; `--audit --project .` to `commands/research.md` §4 with its two sentences quoted;
  `function` and `simulation` to the worked record in `skills/spark-design/references/part-data.md` and to
  `agents/parts-researcher.md`'s field list; `KIND_FUNCTION` unchanged (a `sensor` still says nothing until written —
  the PO's rule).
- **removes** the gap between what research writes and what `--match` reads; no code path.
- **testable**: the set test above; `test_a_researched_sensor_with_no_function_is_named_by_audit_in_the_research_flow`
  (the docs gate `tests/test_docs.py` already reads commands; extend its read list if research.md is outside it, K in
  the docs area).
- **diagnosable**: `--validate` already refuses the nulls by name; `--audit` already prints both sentences; the change
  makes research run into them.
- **proof**: `--skeleton … --dry-run --json` prints the three keys; `--audit` on a fresh research run prints the
  function sentence before the record is picked.

### C6 · Nothing a need could reach is unreachable: the cut lists its words and ids
kind: story · size: S–M · fixes: K41 (and K34's silent absence)
- **replaces** the `… N more, none with the need's words` line (`scripts/parts.py:1969`) and the drop at `:1955-1956`
  with: the kept eight as now, then `… 3 more under other words — distance: vl6180x-breakout (library), sen0311 (drawer);
  soil-moisture: sen0193-soil-moisture (shelf)` — grouped by `what`, ids under each, and in `--json` the cut candidates
  kept under `more` (word → ids) so an agent can pick from them. The whole store has 19 `what` words (E §1 RC-9), so
  the line is bounded by words, not entries, and the 4 KB budget holds (`page()` still pages needs).
- **removes** the unreachable state.
- **testable**: the existing cap test (`tests/test_needs.py:327`) plus
  `test_the_cut_candidates_are_listed_by_their_words_and_reachable_in_json` (the synthetic nine; asserts
  `vl6180x-breakout` under `distance` in `more`).
- **diagnosable**: the line names the words and ids that were cut.
- **proof**: the #5 example ("obstacle ahead") on a copy: the rangefinders appear under `distance` on the first page.

### C7 · A need says how many the design uses
kind: story · size: M · fixes: K39 · **a PO decision first** (§5.3 "no counts" was about owned counts; this is a design
quantity)
- **adds** `count` to a need (`CHECKS`, default 1, whole, ≥ 1): the reservation takes `count` pieces per pick
  (`wanted` at `scripts/needs.py:297` multiplies), `_merge_parts` wants `count` entries named `Valve1…Valve4` (the
  convention irrigation already uses), `--pick` prints `valve: dfr0457-mosfet-power-controller × 4 — 4 of 8 reserved`
  and, for a doubled argument, `given twice, taken once — a count is set on the need`.
- **removes** the "kept, not from a pick" blame for entries the model could not express.
- **testable**: `test_a_need_of_four_reserves_four_and_the_building_list_names_four`,
  `test_a_count_past_what_is_free_is_refused_naming_the_holder`, `test_a_doubled_pick_argument_is_said`.
- **diagnosable**: the pick's line carries the quantity and the reservation; a shortfall uses the existing refusal.
- **proof**: irrigation's seven needs on a copy produce a `requirements.json` with twelve parts and the four valve
  names, with no hand edit.

### C8 · `--requirements` refuses when a differently named requirements file sits in the project
kind: bug · size: S · fixes: K40
- **adds** before the write (`scripts/needs.py:578-610`): list `*requirements*.json` in the project folder; when one
  exists and `requirements.json` does not, refuse: `irrigation.requirements.json is here and is not the file
  --requirements reads and writes (requirements.json): rename it (git mv) or copy it, then run again — the chain's
  commands take either name, this one takes one`.
- **removes** the silent second file.
- **testable**: `test_a_requirements_file_under_another_name_refuses_the_write_and_names_it`,
  `test_the_same_name_merges_as_before`.
- **diagnosable**: the sentence above, exit 1, nothing written.
- **proof**: the FEAS-8 (1) run on a copy stops at that sentence instead of writing six parts.

### C9 · The store's words are shown where a need is written and matched
kind: story · size: S · fixes: K38 (its lookup half); feeds C1, C6
- **adds** to `--match`, under a need with no word match, `the store's words for sense: distance, soil-moisture — your
  need says 'obstacle ahead'`; to `--describe`'s data nothing new (no new operation); to `commands/idea.md` S step one
  sentence: "write `what` in the store's words where one fits — `--match` shows them — and in the person's words
  otherwise"; and one sentence that code never reads `condition` (it is the agent's).
- **removes** nothing; the 13 verbs stay (D the PO).
- **testable**: `test_a_need_with_no_word_match_is_shown_the_verb_s_words`.
- **diagnosable**: the words are on the answer that failed to match.
- **proof**: the `mp3-player` / `audio-player` pair on a copy: the answer shows both words under `sound`.

## 4. What could not be checked, and why

- **A human typing.** Every reproduction here is an agent's (★C9); whether a person reads "[other words]" as a warning
  or as a match is H (USER-2's "a hobbyist would either quit here or accept a sensor that does not do what they
  wanted" is one walker's reading).
- **The raw P162 reports** (`ai-matching.md`, its refuter) are outside the repository (#99 comment 2026-10-08T23:41);
  the #99 summary comment was read instead.
- **The real store's counts.** 110 / 91 / 19 are from the 2026-10-10 copy; C-35's "17 of 110" was on 2026-10-08 — the
  difference (two entries linked since) is H, not checked against the real store, which this task does not read with
  commands.
- **The irrigation repro** needed the S3's hold released in the copy; on the real store the board pick is refused (K3,
  K29 — another area), so K39/K40 as reproduced here are one step past what the PO's store allows today.
- **Whether a quantity belongs on a need** (C7) is the PO's decision; §5.3's "no counts" was written about owned
  counts (H: my reading of §5.3 and idea.md:37 together).
- **The test suite was not run** here: running it writes `__pycache__` under `~/Development/spark`, outside the folder
  this task may write in. The tests cited were read, not executed.
- **AliExpress import** does not exist yet; whether it asks for `function` is —.
- **Line numbers** are of `a8aa34d` and were pinned with `grep -n` on 2026-10-10; a later commit moves them.

## 5. Searches

none — every claim is from files, commands and cards named above.
