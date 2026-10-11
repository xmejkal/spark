# P158 part 1 — verification of the diagnosis *needs-matching-vocabulary* (RC-1 … RC-9, C1 … C9)

Written 2026-10-10 by the refuter for this area, against spark 0.8.1 (main `a8aa34d`, `git log -1`, 2026-10-10;
`.claude-plugin/plugin.json` → 0.8.1). I did not write the diagnosis; I tried to refute it. Every cited line was opened and
is quoted verbatim below; every reproduction ran on a **copy** of the PO's store (`cp -R ~/.local/share/spark` into
`<scratch>/verifier-nmv/store`, 2026-10-10; every command prefixed `SPARK_HOME=<scratch>/verifier-nmv/store
HOME=<scratch>/verifier-nmv/home TMPDIR=<scratch>/verifier-nmv/tmp`, verified once with `env | grep SPARK_HOME`, which
printed the scratch path; `python3 -B` so no bytecode was written under spark). Two scratch edits to that copy, both
undone: nine synthetic drawer entries `zz-synthetic-<word>` for the cap run (removed; `ls | grep -c zz-synthetic` → 0),
and a scratch project `node` plus a copy of `~/Development/irrigation` under `<scratch>/verifier-nmv/projects/`. Nothing
touched the real store, the bin, irrigation or plant-alarm; irrigation's and plant-alarm's files were read only.
`git status --short` in spark after my runs showed the same three untracked paths it showed before (`.spark/cache/…`, the
two discovery folders). A `find -mmin -90` also listed `tests/__pycache__/*.pyc` and
`tools/circuit-to-wokwi/tests/.mapping-under-test.json` as recently modified — not by this verifier (I ran no test and
used `-B`); another process of this discovery did.

Tags: **E** a pointer (file:line in spark unless another repository is named; a command and what it printed); **H** a
claim with its source only; **D** a decision, by whom and when; **—** unknown. Numbers carry their provenance. The PO's
criteria (2026-10-10, verbatim): *"we want the system to be well designed so its well testable and understandable where a
mistake is happening and why"*; each change below is judged on testability, diagnosability and simplicity (remove before
add).

The diagnosis did not run the test suite and neither did I, for the same reason (the suite writes bytecode under
`~/Development/spark`; `-B` would avoid it, but a test that writes elsewhere in the tree cannot be ruled out without
reading all 38 files). Every test cited was read, not executed.

## Verdicts

### RC-needs-matching-vocabulary-1 · Two matchers, two vocabularies — **holds**

Lines read (E):

- `scripts/parts.py:1327-1329`:
  `    haystack = " ".join([part_id, record.get("name") or "", record.get("kind") or "",` /
  `                         " ".join(aliases(record))]).lower()` /
  `    return all(word.lower() in haystack for word in words)`
- `scripts/parts.py:253` (`available`): `    return sorted(store.records("parts", LIBRARY, project))` — no `drafts`, so
  `scripts/store.py:80` `    rows += [("catalog", place("catalog"))] if kind == "parts" and drafts else []` leaves the
  catalog out; `catalog_matches` (`:891-894`) adds it with the same `_matches`. The drawer is in neither walk.
- `scripts/needs.py:129-130`:
  `    return bool(wanted) and (any(wanted <= _words(f.get("what")) for f in functions if f.get("does") == need["does"])` /
  `                             or wanted <= set().union(*(_words(name) for name in names)))`
- `tests/test_parts.py:794`: `        self.assertEqual([p["id"] for p in parts.need(["motor", "driver"])[0]], ["l9110s-module"])`

Reproduced on the copy (my runs, 2026-10-10, exit 0 each; identical to the diagnosis): `--need 12 V inlet` → the two
screw terminals, no `jst-ph-2-power-inlet`; `--need power inlet` → `jst-ph-2-power-inlet`, `pj-002a-dc-jack`;
`--need soil sensor`, `footswitch`, `foot switch`, `temperature` → "nothing in the library matches"; `--need soil moisture`
and `moisture sensor` → `sen0193-soil-moisture`; `--need inlet` → four. `--match` for `foot — input / footswitch` →
`tactile-button (library) button [other words]`. The aliases named are there (E `<scratch>/…/store/catalog/
mkds-1-5-2-5-08-screw-terminal.json`, `wj500v-5-08-2p-screw-terminal.json` carry `"12 V inlet"`; `pj-002a-dc-jack.json`
`"power inlet"`; `~/Development/irrigation/parts/dc-barrel-jack-12v-inlet.json` `"power inlet", "12 V inlet", "12v inlet"`).
Git dates hold: `6557c71` 2026-09-29, `84443db` and `008fc55` 2026-10-04 (E `git log -1 --date=short` each).

Three sentences are narrower or looser than the code, none changing the verdict:

1. *"behind the verb gate … which does read the drawer and `function`, and never `kind` words"* — the kind does reach
   the matcher: `scripts/needs.py:177` `        functions = parts.function_of(record, board=kind == "board") + [f for e in holding for f in e.get("function") or []]`
   and `function_of` (`parts.py:72-78`) maps eleven kinds to a function, so a `motor-driver` record with no `function`
   matches `drive / motor-dc` (my `--match`: `l9110s-module (library) motor-dc`, `what_matches True`). Change to: "never the
   kind string itself — the kind reaches it only as the `what` word `KIND_FUNCTION` maps it to".
2. *"it does not say which words were looked for where"* (how anyone would have known) — the empty answer does print the
   phrase (`parts.py:1634`: `nothing in the library matches 'soil sensor'`), and `--describe`'s row says the four fields
   (`parts.py:1478`: "words matched in id, name, kind, alias"), as does `commands/research.md:24` ("searches the project's
   parts, the library and the catalog"). What no output says is which *word* missed, that every word must hit, and that the
   drawer and `function` are outside the search. Narrow the sentence to that.
3. *kind: "implementation (the AND over free words)"* — the AND is documented in the function's own docstring
   (`parts.py:1334`: "The records matching every word — in id, name, kind or an alias") and pinned by the test at `:794`.
   It is a documented choice the use outgrew, not a slip; naming it so matters for C1, which changes documented behaviour.

### RC-needs-matching-vocabulary-2 · The pick does not consult the match — **holds**

Lines read (E):

- `scripts/needs.py:282` `        pick = _resolve(pick_id, known, entries)` (the diagnosis says `:285`; the refusals it
  places at `:285-287` are at `:284-287`): `:286-287` `        elif pick is None:` /
  `            problems.append(parts._problem(need_id, "no record or drawer entry called %s — --match lists the candidates" % pick_id))`
- `grep -n "candidates(" scripts/needs.py` → `:163` the definition and `:210` the one call, inside `match()`;
  `plan_pick` (`:267-350`) has none, nor a call of `_what_matches` (`:126`, `:160` only).
- `scripts/needs.py:70` `        sentence for key, (test, sentence) in CHECKS.items() if (key in need or not held_only) and not test(need.get(key))]`
  — one field at a time.
- `scripts/parts.py:1943` `    return Answer({"needs": listed}, ["  %-10s %s / %s%s%s" % (n["id"], n.get("does"), n.get("what"),`
  — id, does, what, condition, mark; no pick.
- `commands/idea.md:50-51`: "`[other words]` / means the candidate has the need's verb but not its `what`: whether it is
  similar enough is your call, said to the person."

Reproduced exactly (my runs): `--match` for `temp — sense / temperature` → `sen0193-soil-moisture (shelf) soil-moisture
[other words]` and `vl6180x-breakout (library) distance [other words]`; `--pick <node> temp=sen0193-soil-moisture` → exit 0,
`set dfrobot-sen0193: used_in {"plant-alarm": 1} → {"plant-alarm": 1, "node": 1}` / `temp: sen0193-soil-moisture` /
`wrote to your history: 1 reused`; `--needs <node>` → `temp       sense / temperature`; `--needs-set [{"id": "temp",
"mark": "gap"}] --dry-run` → `would set temp: mark null → "gap"`, exit 0. The decisions cited are where the diagnosis says
(E `docs/2026-10-04-store-design.md:234` "the agent judges similarity and marks the need, saying why and what would change";
`:288` "the mark (agent; its reason is said to the person, §5.3)"; `docs/guide/journey.md:448` "`--pick` takes the record
either way; `--requirements` decides").

The code says something *stronger* than the diagnosis: the pick checks the verb no more than the words. My run:
`--pick <node> temp=l9110s-module --dry-run` (a motor driver for a temperature need) → exit 0, `temp: l9110s-module`,
`would write to your history: 1 reused`, no note. See missed cause M1.

### RC-needs-matching-vocabulary-3 · No removal, rename or un-pick — **holds** (two line numbers off, the "why" gains an E)

Lines read (E):

- `scripts/needs.py:93` (the diagnosis says `:89`): `        after = dict(before or {}, **{key: (drawer.clean(value) if isinstance(value, str) else value) for key, value in item.items()})`
- `scripts/needs.py:100` (the diagnosis says `:96`): `        order += [] if need_id in current else [need_id]`
- `scripts/needs.py:7`: "Every write sets, never adds."
- `commands/idea.md:24-25`: "An `id` stays: there is no removing or renaming a need yet, / so a wrong one is fixed by hand
  in `<project>/.spark/needs.json`, then checked with `parts.py --needs <project>`."
- `scripts/drawer.py:7`: "so a retried write changes nothing, and nothing is deleted — gone is count 0."
- `scripts/needs.py:425` `def _name_after(need_id):` ✓.

Reproduced exactly (my runs, dry runs): `does: null, what: null` → refused with both sentences, exit 1; `[{"id": "temp"}]`
→ `nothing to change`, exit 0; `remove: true` → `remove: not a need's field — a need holds does, what, condition, mark,
pick, and no part number, count, place or reason (§5.3)`, exit 1; a new id → `would set soil-temp: …`, the old need stays;
`--pick <node> temp=` → `temp — no record or drawer entry called  — --match lists the candidates` (two spaces), exit 1.

The "why" rests on drawer.py as the rule's home (H in the diagnosis). It is a store-wide rule with an E:
`docs/2026-10-04-store-design.md:328` "5. **Safe writes:** every write takes `--dry-run`; slice 1 deletes nothing (gone is
count 0)." — the no-delete rule and the drawer's tombstone are one sentence; the needs file got the rule and no tombstone.
Cite that line. idea.md's "yet" (`:24`) says the omission was known, which the diagnosis should say: it is an acknowledged
gap in the command page, not an unnoticed one.

### RC-needs-matching-vocabulary-4 · Candidacy needs a verb the import never gave — **holds**

Lines read (E):

- `scripts/needs.py:191` `        if points_at_a_record or entry.get("skip") or entry.get("count") == 0 or not any(f.get("does") == need["does"] for f in functions):`
- `scripts/drawer.py:359` `            values = {"label": item["name"], "count": total, "part_number": {"maker": source, "number": sku},` (then
  `from`, `bought`, `unsure` — no `function`).
- `scripts/drawer.py:281-283` (`listing`): `            shown.append({"entry": entry_id, "label": entry.get("label"), "count": entry.get("count"), "is": target,` /
  `                          "in": resolve(target, known)[0] if target else None, "unsure": bool(entry.get("unsure")),` /
  `                          "skip": entry.get("skip")})` — no `function`.
- `scripts/parts.py:171-172` `        if isinstance(record, dict) and not function_of(record, board=kind == "board") and (kind, found, layer, path) not in linked:` /
  `            silent.append(found)` — inside the walk over `walked + linked` records; no entry is counted.
- `scripts/needs.py:195-196` the sort key `(c["owned"] == 0, not c["what_matches"], LAYERS.index(c["in"]) …, c["id"] or c["entry"])`;
  `:155-157` the default `{"id": None, "kind": None, "entry": None, "owes": [], "broken": False, "proof": []}`.

Counts on the copy (my script over `<scratch>/…/store/drawer/*.json`, 2026-10-10): **110 entries; 12 with `is`; 12 with
`function`; 5 with both; 91 with neither; 1 `skip`; 19 reachable** — identical to the diagnosis. The nine SKUs named
(`dfrobot-dfr0575`, `-dfr0994`, `-dfr1075`, `-dfr1117`, `-sen0042`, `-sen0311`, `-sen0395`, `-sen0589`, `-sen0623`) each
hold `is: None, function: None` (same script). The #99 comment of 2026-10-08 reads "91 of the 110 drawer entries carry
neither a record nor a function (label-only imports)" (E `gh issue view 99 -R xmejkal/spark --comments`, read-only).
Reproduced: `board — compute / microcontroller` → the two library boards only; `dist — sense / obstacle ahead` → the soil
probe and the VL6180X; `motor — drive / motor-dc` → `l298n-board-hw-095 (drawer)` above `l9110s-module (library)`, both
`owes []` (my `--match --json`).

Two sentences to tighten, neither changing the verdict:

1. *"The behaviour is pinned as intended: `tests/test_needs.py:472`"* — that test (`:472-473`:
   `    def test_an_owned_part_that_says_nothing_of_what_it_does_is_no_candidate(self):` /
   `        self.assertNotIn("x-silent", [c["id"] for c in self.needs["soil"]["candidates"]])`) pins a catalog **record**
   with no function behind a linked entry (fixture `a_store_with_a_drawer`, `x-silent` in `catalog/`, entry `silent` with
   `is`). It pins the record gate (`needs.py:177-179`), not the label-only entry gate (`:191`). No test pins the
   label-only case as intended; say "the record half is pinned".
2. *"The import never asks the question, and no later step asks it either"* — true, and the mechanism is the command page,
   not the importer: the importer's payload is `{sku, name, count}` by the PO's decision (D `docs/2026-10-04-store-design.md:357`;
   `commands/drawer.md:55` "It returns `{sku, name, count}` per product … nothing else"), so `function` cannot ride the
   import; the words-to-entries step does carry `function` and asks when the agent would guess one (`commands/drawer.md:28`,
   `:34` "a function you would be guessing"); the import step (`:47-80`) asks about packs and "the same item" only. The
   "asked once" of §5.6 (`:231`) has no step to live in after an import. C4's data pass needs that step named.

### RC-needs-matching-vocabulary-5 · Research writes records that owe what the chain reads — **partly**

Lines read (E):

- `scripts/parts.py:98` `CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")`
- `scripts/parts.py:63-64` "#: A kind that says by itself what a part does (§5.6). A `sensor` or a `connector` does not: theirs is written /
  #: once, through `--function-set`, with a dry run."
- `scripts/parts.py:1364-1375` the skeleton's dict; its one chain-facts line `        "needs": [], "power": [], "unused_pins": [], "pin_order": [], "footprint": None,`
  and `body_mm` below it; no `function`, `pin_order_proof` or `simulation` key — my `--skeleton x-probe --kind sensor
  --project <node> --dry-run --json` printed 18 keys: `schema, id, name, kind, //, vendor, sku, sources, needs, power,
  unused_pins, pin_order, footprint, body_mm, facts, host_requirements, sourcing, //sourcing`.
- `tests/test_parts.py:853-867` asserts `name`, `footprint` null, `body_mm.verified` false, and that `validate` refuses the
  skeleton — not that it holds every chain fact ✓.
- `agents/parts-researcher.md:92` "With it, `pin_order_proof` `{verified, source}`" — `grep -n "function\|simulation"`
  over the file: nothing ✓. `commands/research.md:83-85` `--validate`, `--sources`, `--unverified`; `grep -n "audit\|function-set"
  commands/research.md` → nothing ✓.
- Dates (E `git log -1 --date=short`): `6557c71` 2026-09-29 (skeleton); `1e77b88` 2026-09-29 (simulation); `c2afc47`
  2026-10-03 (pin_order_proof); `84443db` 2026-10-04 (function); `b9fcf8a` 2026-10-04 (CHAIN_FACTS) ✓ all five.

Reproduced: `--audit` → `catalog 0 current, 17 owe facts, 0 broken`; every one of the 17 lines carries `pin_order_proof`
and `simulation` (read line by line); the "says nothing of what it does" line names 10.

Where it is narrower or wrong:

1. *"names 10 (six jacks and terminals, four flow meters and sensors)"* → **seven connectors** (`d228a-dc-jack-hadex`,
   `dc-005-dc-jack-laskakit`, `ds-214b-dc-jack-gme`, `mkds-1-5-2-5-08-screw-terminal`, `pj-002a-dc-jack`,
   `seeed-320120010-dc-jack`, `wj500v-5-08-2p-screw-terminal`) **and three flow meters** (`sen0217-flow-meter`,
   `sen0550-flow-meter`, `yf-s201-flow-meter-generic`) (my `--audit`, 2026-10-10). Total 10 holds; the split does not.
2. *"`--audit --project <irrigation copy>` adds `dc-barrel-jack-12v-inlet`, `sen0217-flow-meter`, `sen0308-soil-moisture`"*
   → adds two; `sen0217-flow-meter` was already named through its shelf copy (my run: the project audit lists the same ten
   plus `dc-barrel-jack-12v-inlet` and `sen0308-soil-moisture`; `shelf 1 current` because the project's copies shadow the
   shelf's).
3. The sentence that matters, in "how anyone would have known" and repeated as C5's diagnosability: *"`--validate` already
   refuses the nulls by name"*. It holds for `pin_order_proof` only once a pin order has a pad (`parts.py:376-377`
   `    if not any(pad for pad in part.get("pin_order") or []):` / `        return []`), and is false for `simulation`
   (`parts.py:483-485` `    sim = part.get("simulation")` / `    if sim is None:` / `        return []`) and for `function`
   (`parts.py:82` "absent is fine: the kind may say it"). E from the copy: `--validate --project <irrigation copy>` →
   `dfr0641-ds3231m-rtc              ok` while `--audit --project <irrigation copy>` → `dfr0641-ds3231m-rtc (project) owes:
   simulation`. Change to: "`--validate` refuses a null `pin_order_proof` once a pin order is stated and says nothing of a
   null `simulation` or `function`; only `--audit` names them". The mechanism this hides is missed cause M3.
4. The claim *"every researched record arrives owing `pin_order_proof` and `simulation` at least"* holds for what the
   skeleton produces today (the catalog's 17); irrigation's seven records, researched with the same skeleton on
   2026-09-29, now owe only `simulation` on one (`dfr0641-ds3231m-rtc`) because they were filled by hand since (E the
   project audit above). Say "every record research leaves as it wrote it".

### RC-needs-matching-vocabulary-6 · Ranks by place, cuts at eight, the cut is unreachable — **holds**

Lines read (E): `scripts/parts.py:1955` `        kept = [c for rank, c in enumerate(need["candidates"]) if rank < 8 or c["what_matches"]]`;
`:1956` `        need["more"], need["candidates"] = len(need["candidates"]) - len(kept), kept`; `:1957` the `page(…)` call
after it; `:1969` `        lines += ["      … %d more, none with the need's words" % need["more"]] if need["more"] else []`;
`scripts/outcomes.py:82` `def page(items, start, op, argv, limit=20, budget=3400):`. The "none with the need's words" is
true by construction (every cut candidate has `what_matches` false).

Reproduced with nine synthetic owned `sense` entries on the copy (removed afterwards): `dist — sense / obstacle ahead`
listed eight `zz-synthetic-*` and `… 3 more, none with the need's words`; the string `vl6180x-breakout` occurred nowhere in
the `--json` envelope; `truncated.next` carries `--from`, which pages needs (`page(matched, …)`), never candidates. The
#99 comment line holds verbatim: "The candidate cap of 8 (parts.py, not needs.py) hides an answer only when the need's
words match nothing — not new (P136's inputs found it); removing it would break the 4 KB answer limit." (E gh, read-only).

### RC-needs-matching-vocabulary-7 · A pick is one piece — **holds**

Lines read (E): `scripts/needs.py:292` `        elif pick not in picked.setdefault(need_id, []):`; `:297`
`    wanted = collections.Counter(next(iter(pick.items())) for need in after for pick in need.get("pick") or [])`;
`_merge_parts` docstring (`:464-475`) "a part / picked n times needs n entries"; `commands/idea.md:37` "A need holds no
reason, count or place"; `docs/2026-10-04-store-design.md:184` "The needs file holds no owned counts, places or reasons".
Irrigation's file (read-only): `parts` names `Valve1`–`Valve4` and `Soil1`–`Soil3` ✓.

Reproduced: `--pick <node> valve=dfr0457-mosfet-power-controller valve=dfr0457-mosfet-power-controller --dry-run` → `would
set dfrobot-dfr0457: used_in null → {"node": 1}`, `valve: dfr0457-mosfet-power-controller` once, no "given twice"; `--json`
`picks: [{"need": "valve", "pick": [{"part": "dfr0457-mosfet-power-controller"}]}]`, `reserved … {"node": 1}`.

The diagnosis's H ("§5.3's 'no counts' was about owned counts — my reading") is an E for the design page (`:184` says
"owned counts") but not for the code or the command: the commit that made the file says "no reasons, counts or places"
(`2ef034a`, 2026-10-04, its title), `faults`' sentence says "no part number, count, place or reason (§5.3)", and
`tests/test_needs.py:141-146` refuses `{"count": 8}`. Two readings exist, so "a PO decision first" is right. See M7 for
the alternative the diagnosis names but does not weigh.

### RC-needs-matching-vocabulary-8 · `--requirements` knows one file name — **partly** (the where holds; the why overstates)

Lines read (E): `scripts/needs.py:381` `REQUIREMENTS = "requirements.json"`; `:607` `    file = Path(project) / REQUIREMENTS`
(no glob, no look-around in `:600-625`); `scripts/parts.py:2075` `    path, changed = Path(args.requirements) / needs.REQUIREMENTS, False`;
`scripts/emit_board.py:1037` `    parser.add_argument("requirements")`; `scripts/check_spine.py:573-574`
`    parser.add_argument("requirements", nargs="?",` / `                        help="a requirements.json; omit for the reference design")`.
Irrigation's file was born `f50e135` 2026-09-29 (E `git log --diff-filter=A` in `~/Development/irrigation`, read-only) ✓.

Not re-run by me (it needs the S3's hold released on the copy; the diagnosis and FEAS-8 ran it, and `:607` is one line
with no alternative path, E by reading).

Two corrections:

1. *"the store's writer, added on 2026-10-08 (P97)"* → `1d9bb1c`, **2026-10-07** 20:25 +0200, author and commit dates
   alike (E `git show -s --format='%ad | %cd' --date=iso 1d9bb1c`). P97 holds.
2. *"Two conventions for one file, and the newer one does not know the older exists"* — spark has one documented name:
   `requirements.json` wherever a document names the file (E `commands/build.md:48` "`parts.py --requirements` writes this
   file's board and parts", `:64` `check_spine.py requirements.json --keep .`; `README.md:148` "Save it as
   `requirements.json`"; `docs/guide/journey.md:655`; `commands/idea.md:134` "It writes `requirements.json`"). The chain's
   positional argument tolerates any name; `irrigation.requirements.json` is one project's name from eight days before the
   writer existed. Change to: "One documented name, which the chain's positional argument does not enforce, and one older
   project that used another; the writer does not look for a second file." The fault that stands is K40's missing look
   (and the cheapest fix is in irrigation — M6).

### RC-needs-matching-vocabulary-9 · `does` closed, `what` open, the words shown nowhere — **holds**

Lines read (E): `scripts/parts.py:60-61` `VERBS = ("sense", "input", "indicate", "sound", "move", "drive", "power", "keep-time", "store", "compute",` /
`         "communicate", "connect", "mount")` — 13; `scripts/needs.py:29` `CHECKS = {"does": (lambda v: v in parts.VERBS, "`does` is one of %s" % ", ".join(parts.VERBS)),`;
`scripts/parts.py:65-70` `KIND_FUNCTION` with `audio-player`, `load-switch`, `light`, `rtc`, `motor-dc` ✓;
`scripts/parts.py:1472-1537` `OPERATIONS`: no row lists a vocabulary ✓; `grep -n condition scripts/*.py` → `parts.py:1508`
(the `--needs` description), `:1944`, `:1960` (printing) and `needs.py:31` (the check): nothing reads it ✓. `dfrobot-dfr0768`
and `mp3-mini-module` carry `sound / mp3-player` (E the drawer files on the copy); `dfr0534-module` is kind `audio` →
`audio-player` through `KIND_FUNCTION`.

The count: **19 distinct (does, what) pairs** holds — my script through `parts.function_of` (kind fallback included) over
`parts/`, `boards/` (less `active.json`), and the copy's `catalog/`, `shelf/`, `drawer/` (2026-10-10). State the method:
only **14** are written `function` fields; five exist only through `KIND_FUNCTION` (`drive/load-switch`, `indicate/light`,
`power/regulator`, `sound/amplifier`, `sound/audio-player`). A reader counting `function` keys gets 14 and thinks the
diagnosis wrong.

Reproduced: `{"does": "switch"}` → `refused, so nothing was written: sw — `does` is one of sense, input, indicate, sound,
move, drive, power, keep-time, store, compute, communicate, connect, mount`, exit 1; `mp3 — sound / mp3-player` marks the two
drawer entries and shows `dfr0534-module (library) audio-player [other words]`; `audio — sound / audio-player` the reverse.

### The "Noted" paragraph (G and equivalents) — holds where checked

`scripts/parts.py:1970` the gap line ✓; `:1634-1636` the research hint ✓; `scripts/cost.py:43` `STEPS = ("S", "M", "C",
"G", "L", "T", "I", "F", "R")` ✓. The citation *"`commands/research.md` §2 and 'What this does not do'"* for "no flow for a
board" is loose: that section (`:111-114`) names picking between parts, pinouts and prices; the absence of a board flow is
by omission of the whole page, not a sentence in it. Say "by omission".

## Missed root causes

Each with the rival explanation it rests on, and what in the diagnosis it sharpens.

**M1 · The pick checks the verb no more than the words — a category error passes with the same silence.** `plan_pick`
resolves an id (`needs.py:282`) and never asks what the record does; `--pick <node> temp=l9110s-module --dry-run` (a
motor driver for `sense / temperature`) → exit 0, `temp: l9110s-module`, `would write to your history: 1 reused` (my run).
`--match` would never list it (the verb gate, `needs.py:178`), yet the pick takes it. RC-2's example is `[other words]`;
the stronger case is "other verb", which C2's note must cover — "does drive, not sense" before "does soil-moisture, not
temperature". E.

**M2 · The matcher's own word test is the same AND the diagnosis names for `--need`.** `scripts/needs.py:129` requires
`wanted <= _words(f.get("what"))` — every word of the need's `what` inside one function's `what`. On the copy, the need
`far — sense / distance sensor` lists `vl6180x-breakout distance` with `what_matches False` (my run): "sensor" is not in
`distance`. `wet — sense / soil moisture probe` matched the SEN0193 only through its long name (the names clause, `:130`:
"Gravity: Analog Capacitive Soil Moisture Sensor … probe"). So the `[other words]` flood that RC-6 and RC-9 lay on the
person's vocabulary is produced for every need carrying one word more than the store's function — the normal case for a
person's words. The diagnosis's §2 keeps "the word test as a flag" and C1 routes `_what_matches` through `words_hit`, but
no root cause names the subset rule as a mechanism of K34/K41; it should, because the ranking key (`:195`) and the cap
(`parts.py:1955`) both read that boolean. Rival to RC-9's "vocabulary drift": here the words are the store's own, plus one.
E.

**M3 · `--validate` is silent about owed facts by design, and research's done-check is `--validate`.** `broken_problems`
(`parts.py:127-131`) filters every problem about an owed key (`_about`, `:113`); `simulation_problems` returns nothing for `None`
(`:483-485`); `function_problems` says absent is fine (`:82`); the proof check runs only when a pin order has a pad
(`:376-377`). The split is deliberate — commit `b9fcf8a` (2026-10-04): "a record owes what is absent and is broken only by
what is wrong" — and `commands/research.md:83-85` predates it (`6557c71`, 2026-09-29), when `--validate` was the only gate.
E from the copy: `--validate --project <irrigation copy>` → `dfr0641-ds3231m-rtc ok`; `--audit --project <irrigation copy>`
→ `dfr0641-ds3231m-rtc (project) owes: simulation`. This is the reason an agent "ends with `--validate` passes" (RC-5) and
the reason C5's "`--validate` already refuses the nulls by name" is wrong for two of its three keys. Rival to RC-5's "a
stale skeleton": the skeleton is half of it; the other half is a done-check that cannot see what the chain refuses. C5's
`--audit --project .` in research.md addresses it, but the diagnosis should say why that line, not `--validate`, is the
alarm.

**M4 · The marks cannot say "fits loosely".** `MARKS = ("have", "have-unknown", "know", "gap")` (`needs.py:23`) answer "is
it available", not "does it do the need's words"; there is no value an agent could write for RC-2's judgement even when it
makes it. C2 presses `gap` into that service with a pair rule, but `gap` + pick is a documented state: `commands/idea.md:63-64`
sends a `gap` to `/spark:research` and says "Pick that record for the need afterwards (C)", and no sentence after `:56`
re-marks it (`grep -n mark commands/idea.md` → `:54`, `:56` only); `_unserved` (`needs.py:532`) reads `gap` as unserved
only when there is no pick. Rival to RC-2's "the hand-over was left out": the vocabulary for the hand-over does not exist.
E.

**M5 · `--need`'s test is a substring test, not a word test** — `parts.py:1329` `word.lower() in haystack`. Today the
AND hides it; under C1's OR, the one-letter word in "12 V inlet" hits every record whose id, name, kind or alias contains the
letter v (most of them). `needs.py:122-123` already has the tokeniser (`_words`). C1 must say "tokens", or its first
reproduction floods. E.

**M6 · Data, not code, for K40.** The one project with the other name is irrigation; `git mv irrigation.requirements.json
requirements.json` in that repository ends K40 for it with no spark change, and `emit_board`/`check_spine` take the new
name unchanged (positional). C8's check still earns its place for the next person, but remove-before-add puts the rename
first. H (my reading of the two repositories; the rename is the irrigation owner's call).

**M7 · The model already expresses quantity — as needs — and yields irrigation's names.** `scripts/needs.py:484`
`        name = _name_after(need_id) if len(picked_by[part_id]) >= 2 else None`: a part picked by two or more needs is
written once per need, named after the need (`valve-1` → `Valve1`). Four needs `valve-1 … valve-4` picking the DFR0457
produce `Valve1 … Valve4`, reserve four, and write four `reused` events — what RC-7 says the store "never learns". The
diagnosis names "four needs" as the only way and then proposes a schema change (C7); the alternative it does not weigh is
one sentence in `commands/idea.md` ("one need per instance; a part picked by several needs is placed once per need, named
after it"). E for the mechanism; the choice is the PO's.

**M8 · The import's "asked once" has no step to live in.** §5.6 "An entry may have none ('function unknown', asked once)"
(`docs/2026-10-04-store-design.md:231`) and the importer's payload fixed to `{sku, name, count}` (`:357`, D the PO) together
mean the question belongs to the command page after the import; `commands/drawer.md:47-80` asks about packs and duplicates
and never about what each thing does. RC-4's C4 counts the silence; the step that ends it is a drawer.md paragraph (the
agent proposes `function` from the label, the person says yes), which no change names. E.

## The changes, judged

Each: mechanism or symptom · would the named test catch the regression · does the failure name where and why · would a
simpler removal do · what it changes for the bin, irrigation and plant-alarm (details in the next section).

**C1 · One matcher, hits not AND, says which words missed.** Mechanism (one word test for two commands) — with two
conditions the diagnosis leaves out: tokens, not substrings (M5), and a statement of what "a match is the answer"
(`commands/research.md:24`) means when answers are ranked by hits. The named tests would catch a regression of each case;
`test_need_12_v_inlet_…` asserts both the hit and the `missed: 12, v` line, so the diagnosability is tested too. The
failure text proposed names where (the words, the layers, the drawer's 91) and why (which word missed). Simpler
alternative: keep the AND and add only the two sentences (which words missed; the drawer and `function` are not searched)
— that removes the misdirection of K33 at a tenth of the change, and leaves the ranking for a later decision. Changes
documented behaviour: `parts.py:1334`'s docstring, `tests/test_parts.py:791-797`, the recorded runs in
`docs/guide/journey.md:524` (`--need motor driver`) and `:533` (`--need soil moisture`), and the five pages that send
agents to `--need` (`commands/research.md:20`, `commands/build.md:145`, `commands/identify.md:31`,
`agents/parts-researcher.md:12`, `skills/spark-design/SKILL.md:21`).

**C2 · The pick says what the match knew; `--needs` shows the pick; a mark/pick pair rule.** The note at pick time is the
mechanism (the hand-over) and must include the verb (M1). The `--needs` text line gaining `pick` and `mark` is right and
trivial. **The pair rule is wrong as written.** `faults` runs on read too (`needs.py:60` `faults(need, held_only=True)` →
"fix it by hand"), and the rule "`have`/`know` with none [no pick] is refused" refuses the state idea.md's M step writes
on purpose (marks at `:54-56`, picks later in C at `:85`) — and refuses plant-alarm's real file today (`battery` is
`mark: have`, no pick; E `~/Development/plant-alarm/.spark/needs.json`, read-only). "`gap` with a pick is refused" refuses
the documented gap → research → pick path (M4). Drop the pair rule; if the PO wants fit recorded, that is a new mark value
or a `fit` field — a decision, not a check. The tests named would catch regressions of the note; none of them would reveal
that the rule breaks M-before-C, because they would be written to the rule.

**C3 · Drop a need, clear a pick, through the set-only door.** Mechanism (the missing tombstone/removal), the shared
`_reserve` is a refactor that reduces two copies to one (good for "where a mistake is happening"), the sentences name what
was dropped and released, the tests cover retry and release. Two additions: a rename is drop plus add, but the history's
`reused` events keep the old need id (`needs.py:332` writes `"need": need_id`) — say so in the answer, or the tally's
"needs_picked" and the history disagree; and the proposed `--pick <project> temp=` reuses a form today refused with a
double-space sentence (`:287`) — fine, but the refusal for a *mistyped* empty id must then be distinguishable from a
clearing. On the PO's relayed question of a synced store (2026-10-10): a tombstone that stays in the file
(`{"id": "temp", "dropped": true}`) travels through sync and merge tools better than a vanished object; the needs file is a
project file under git, where either works. Not this task's decision.

**C4 · Say how many entries no need can reach.** Symptom-level by design (a count), and the right first step because the
fix is data: the sentence names the count, the fix command and the nearest labels — where and why. Tests would catch the
count going missing. Add the drawer.md step (M8), or the count has no path to zero except an agent's improvisation. The
`--drawer` text column is cheap; `--audit`'s `drawer_silent` beside `no_function` keeps one vocabulary. Nothing removed,
nothing broken.

**C5 · The skeleton carries every chain fact; research ends with `--audit`.** Mechanism, and the set test
(`set(CHAIN_FACTS) | {"function"} <= set(skeleton(...))`) is the one test in this diagnosis that catches the *next* drift,
not only this one. Correct the diagnosability line (M3): validate accepts `function: null`, `simulation: null` and a null
proof beside an empty `pin_order` (`parts.py:82`, `:483-485`, `:376-377`), so the alarm is `--audit`'s two sentences,
which C5 rightly adds to `research.md` §4 — say that, or the next reader trusts `--validate` again. Nothing breaks:
`tests/test_parts.py:853-867` still holds (it asserts other nulls), existing records are untouched, `function_problems`
and `simulation_problems` accept the new nulls. The docs gate (`tools/check_docs.py:30-33`) reads README, AGENTS.md and
`docs/guide/` only, so a test of research.md's new line needs its own read, as the diagnosis says.

**C6 · The cut lists its words and ids; the cut candidates stay in `--json` under `more`.** Mechanism (an unreachable state
removed). `more` has no reader outside `parts.py:1955-1969` (E `grep -rn '"more"'` over `scripts/`, `commands/`,
`docs/guide/`, `agents/`, `tests/test_needs.py`: nothing) — the shape change from an integer to a word→ids map breaks no
page. Budget: on the copy a `--match` of 8 needs already pages at 4 (my `--json`: `truncated shown 4, total 8`); grouped ids
per need shrink that further, and ids per word are unbounded (once the 91 entries carry functions, dozens could share one
word), so cap the ids per word and print "+n" — the diagnosis bounds by words only. The named test would catch the
rangefinder vanishing again.

**C7 · A need says how many the design uses.** A PO decision first, as the diagnosis says. Mechanism for K39, but the
simpler path exists today (M7): one need per instance, which already yields irrigation's names and four reservations.
Remove before add: the idea.md sentence first; `count` only if the PO finds four needs too many. If made: `faults`' sentence
and `tests/test_needs.py:141-146` (refuses `{"count": 8}`) flip; §5.3's "no owned counts" stays true; `commands/idea.md:37`
is rewritten; `_merge_parts`'s naming (`:484`) gains an index for one need with `count` ≥ 2. The tests named would catch
the arithmetic; the "given twice, taken once" line is the diagnosability win either way and costs one sentence.

**C8 · Refuse when a differently named requirements file sits in the project.** Mechanism for K40's silent second file; the
sentence names where (the file), why (one name is read) and the fix; the two tests cover both branches. Do M6 first (one
`git mv` in irrigation). The glob `*requirements*.json` meets nothing in a spark project root today (E `find
~/Development/spark -name "*requirements*.json"` → only `tests/mutations/…` and `.superpowers/…`); it refuses only when
`requirements.json` is absent, so a project with both files is still merged silently — say that in the text, or extend the
check to "both exist, and differ".

**C9 · The store's words shown where a need is written and matched.** Cheap and right; the line is on the answer that
failed. Add M2's case to the same line: "your need says 'distance sensor'; the store's word is 'distance' — one word more",
because that is the commonest cause of `[other words]` on the copy, and the vocabulary list alone would not explain it.
The named test catches the line going missing.

## What breaks for current users

Read from the three projects on 2026-10-10 (read-only): the bin has no `.spark/needs.json` and no `*requirements*.json`
(its board is hand-written tscircuit); plant-alarm has `requirements.json`, `board.tsx` and `.spark/needs.json` with four
needs — `soil`, `alarm`, `board` picked and marked `have`, `battery` marked `have` with no pick; irrigation has
`irrigation.requirements.json`, no `needs.json`, seven records in `parts/`.

- **The bin:** nothing in C1–C9 touches it. Its CLAUDE.md scripts `parts.py --kept`, not `--need`.
- **plant-alarm:** C2's pair rule as written refuses its needs file on read (`battery`: `have`, no pick) — every `--needs`,
  `--match`, `--pick`, `--requirements` on the project would end in "fix it by hand". Drop the rule. C3, C7 (default 1), C8
  (its file is `requirements.json`) change nothing. C6's `more` shape: no reader.
- **irrigation:** C8 refuses `--requirements` until the file is renamed — the intended effect, and M6 gets there first.
  C1 changes what `--need` answers for the phrases its DIARY recorded (I1); the diary is history and is not re-run. C5
  changes the skeleton, not its seven existing records; `--validate --project .` still says `ok` for `dfr0641-ds3231m-rtc`
  while `--audit --project .` says it owes `simulation` (M3) — C5's research.md line does not re-run on old records, so the
  project's `--audit` is the command that tells it.
- **spark itself:** C1 rewrites `tests/test_parts.py:791-797` and re-records `docs/guide/journey.md:524`, `:533` (K68's
  gate); C7 flips `tests/test_needs.py:141-146`; C6's `--json` shape has no reader to break; C2 and C3 add to `faults` and
  `plan_set`, which `tests/test_needs.py:53-201` pin as set-only — the new verbs must be added there, not around them.

## Searches

none — every claim is from files, commands and cards named above.
