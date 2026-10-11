# Verification — store-levels-and-holds (P158 part 1)

Written 2026-10-10 by the refuter for this area, against spark 0.8.1 (main `a8aa34d`, `git log -1`), of
`store-levels-and-holds.md` (the diagnosis) and the rows K1–K19, K58 of `../catalogue.md`. I did not write the diagnosis;
every root cause below was re-read at its cited lines, and where a run settles a point I ran it on a copy of the PO's store
(`cp -R` to `<scratch>/store`; one further copy per destructive run: `store-k11`; a hand-made two-line store `store-case`;
rsync copies of the repository without `.git` for the mutation runs, `<scratch>/mut/spark-step`, `spark-pick`), with
`SPARK_HOME`, `HOME` and `TMPDIR` as three separate words on every command. `env | grep SPARK_HOME` under the prefix printed
the scratch path once, first. The real store was read with `ls -ld` only (its modes, for RC-7); no spark command ran against
it and nothing was written under it. Tags: **E** a pointer or a run and its output; **H** a claim with its source; **D** a
decision (who, when); — unknown.

The PO's criteria, applied to every change (D PO 2026-10-10): testability, diagnosability (where and why, to a person and
to an agent), simplicity (remove before add).

## Verdicts

### RC-store-levels-and-holds-1 · identity by spelling — **partly**

Lines read, verbatim:

- `scripts/store.py:250` — `return next((name for name, where in projects().items() if where.resolve() == folder), None)`
- `scripts/store.py:255-256` (the docstring of `add_project`) — `Put a project on the list under its folder's name — `name-2`
  when another folder that still exists has it. A folder already on the list keeps its name, however its path is spelled.`
- `scripts/store.py:264` — `while name in listed and Path(listed[name]).is_dir():`
- `scripts/drawer.py:92` — `found[path.stem] = json.loads(path.read_text(encoding="utf-8"))`
- `scripts/store.py:204-205` — `if key is not None and not PLAIN.fullmatch(key):` / `raise StoreProblem("%r is not a plain
  key — lower-case letters, digits and '-' — so it could leave %s" % (key, name))`
- `scripts/drawer.py:40` — `return CONTROL.sub(" ", str(text)).strip()[:LABEL_MAX]`
- `scripts/store.py:125` — `made = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:60].rstrip("-")`
- `scripts/drawer.py:238` — `while key in current and current[key].get("label") != label:`
- `scripts/needs.py:328-329` — `used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}` /
  `used_in.update({name: mine[entry_id]} if mine[entry_id] else {})`
- `scripts/parts.py:2013` — `"  %s%s: %s — no pick of this project explains it"`

Runs (**E**, mine): on `store-case` listing `{"Proj-E": "<scratch>/Proj-E"}`: `os.path.exists("<scratch>/proj-e")` → `True`
(APFS, case-insensitive); `store.project_name("<scratch>/Proj-E")` → `Proj-E`; `store.project_name("<scratch>/proj-e")` →
`None`; `os.path.samefile(...)` → `True`; `store.add_project("<scratch>/proj-e", dry_run=True)` → `proj-e`. `store.slug` on
NFC `Čidlo půdní vlhkosti` → `idlo-p-dn-vlhkosti`, on NFD → `c-idlo-pu-dni-vlhkosti`, on `датчик влажности` → `entry`;
`drawer.clean(NFC) == drawer.clean(NFD)` → `False`. The mechanism is as the diagnosis says, all three identities.

Corrections:

1. **kind** is overstated as "design". The copy half and the vanished-folder half are deliberate — `:255` says `name-2` is
   given only "when another folder that still exists has it", so a gone folder's name is meant to be reused. The spelling
   half is an implementation shortfall against the function's own contract: `:256` promises "however its path is spelled",
   and `resolve()` cannot keep that promise on a case-insensitive file system. Sentence to change: "**kind** · design." →
   "**kind** · design for the copy and the vanished folder (the docstring says so, `store.py:255`); implementation for the
   spelling — `store.py:256` promises what `resolve()` cannot do on APFS."
2. **where** leaves out a fourth name-keyed place: the history. Every `EVENT_KEYS` tuple carries `"project"`
   (`store.py:273-274`), and `--tally` tests `event.get("event") == "built" and event.get("project") == name`
   (`parts.py:2148`). A name passed to a new folder (K4c) hands it the old folder's `built` as well as its holds; C6's
   `--forget-project` leaves those lines by design, so a re-registered same name inherits them again. Add the two pointers.
3. "`ls ~/Development/irrigation/parts/`: nine records" → seven records and two chip folders (**E** `ls`: 7 `.json`,
   `sen0217-flow-meter/`, `sen0308-soil-moisture/`). The shelf's four of them (dfr0457, dfr0831, ds3231-at24c32, sen0217:
   **E** `ls <scratch>/store/shelf`) is right.
4. The catalogue's severity clause for K10 — "the PO's shop labels are Czech" — is **H** and the data says otherwise:
   **E** over the copy's `drawer/`: 110 entries, 99 carry `from.product` (imports), 7 labels have a non-ASCII character
   (6 are DFRobot's own English names with `×`, `”`, `±`, `Ω`, `°`; the one hand entry is `6×6 tactile buttons (a bag)`),
   0 keys match `entry(-N)?`, and 0 hand entries would get another key under an NFKD slug. The mechanism holds; it has
   no occurrence in the store today. The diagnosis does not claim one — this corrects the catalogue, not RC-1.

### RC-store-levels-and-holds-2 · the home is a spelling with no existence check — **partly**

Lines read, verbatim:

- `scripts/store.py:48-49` — `if os.environ.get("SPARK_HOME"):` / `return Path(os.environ["SPARK_HOME"])`
- `scripts/store.py:215` — `target.parent.mkdir(parents=True, exist_ok=True)`; `:395` — `folder.mkdir(parents=True, exist_ok=True)`
- `scripts/outcomes.py:73-74` — `return {"envelope": 1, "tool": tool, "op": op, "status": status_of(problems, unchecked),
  "data": data,` / `"problems": problems, "unchecked": unchecked, "next": list(next_steps), "truncated": truncated}`
- `scripts/store.py:40-41` — `if "unittest" in sys.modules:` / `os.environ["SPARK_HOME"] = _suite_home = tempfile.mkdtemp(prefix="spark-suite-")`
- `scripts/check_vendor_pins.py:99` — `PLUGIN_ROOT = Path(__file__).resolve().parent.parent`; `:111-112` — `own =
  path.parent.parent / CACHE_DIR / name` / `return own if own.is_file() else PLUGIN_ROOT / CACHE_DIR / name`; `:137-138` —
  `cache.parent.mkdir(parents=True, exist_ok=True)` / `cache.write_text(header)`; `:52` — `CACHE_DIR = ".spark/cache"`

Runs (**E**, mine): `SPARK_HOME=<scratch>/store-missing … parts.py --drawer --json` → `{"envelope":1,"tool":"parts",
"op":"drawer","status":"ok","data":{"entries":[]},"problems":[],"unchecked":[],"next":[],"truncated":null}`, exit 0; `ls
<scratch>/store-missing` → `No such file or directory`. `grep -n 'home()' scripts/parts.py` → no match (exit 1), as the
diagnosis says. `git ls-files .spark` → `.spark/cache/XIAO_ESP32C6.pins_arduino.h`, `.spark/cache/dfrobot_firebeetle2_esp32s3.pins_arduino.h`
(tracked); `git status --short` → `?? .spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h` (the live write K14 names).

Corrections:

1. "no answer carries the home it read" is wider than the code. No **ok** answer and no envelope field does; a refusal
   about a broken store file names that file's full path, which contains the home: `store.py:241` (`"%s is not JSON (%s)
   — fix it, or delete it and run /spark:init in each project" % (path, broken)`), `:243`, `:294`; `drawer.py:96`;
   `needs.py:600`. Sentence to change: "because no answer carries the home it read, the empty-store answer and the
   right-store answer are word-for-word the same" → "because no *ok* answer and no envelope field carries the home, the
   empty-store answer and the right-store answer are word-for-word the same; only a broken file names its path".
2. **why** misses the empty-string case, which is the #101 class exactly. `os.environ.get("SPARK_HOME")` is falsy for `""`,
   so `SPARK_HOME=` — a `$VAR` that expanded to nothing — falls through to the default home. **E** my run:
   `SPARK_HOME="" HOME=<scratch>/home python3 -c 'import store; print(store.home())'` → `<scratch>/home/.local/share/spark`.
   C1 as specified ("when `SPARK_HOME` is set and `is_dir()` is false") never sees it. Add the sentence and see C1 below.
3. The rival "the suite guard fires in a real run" (any script importing something that imports `unittest`, as `doctest`
   does) was checked and is clear: **E** importing `store, parts, needs, drawer, boards, init_project, check_vendor_pins,
   check_spine, cost, tools, outcomes, emit_footprint, emit_board, assign_pins` under a scratch `SPARK_HOME` → `unittest
   loaded: False`, `SPARK_HOME` unchanged. `store.py:38`'s claim holds for the scripts.

### RC-store-levels-and-holds-3 · independent writes, a lock keyed outside the store — **holds**

Lines read, verbatim:

- `scripts/store.py:186-187` — `named = hashlib.sha256(str(home().resolve()).encode()).hexdigest()[:16]` / `lock_file =
  Path(tempfile.gettempdir()) / ("spark-%s.lock" % named)`; `:192-194` — `with open(lock_file, "a") as held:` / `if fcntl:` /
  `fcntl.flock(held, fcntl.LOCK_EX)`
- `scripts/parts.py:2198` — `writes = "writes" in next(effects for name, _, _, effects, _ in OPERATIONS if name == op)`;
  `:2200` — `with store.locked() if writes else contextlib.nullcontext():`; `:926` — `with store.locked():` (in `note_built`)
- `scripts/init_project.py:417` — `listed = "on your projects list as %r" % store.add_project(project)`; `grep -n locked
  scripts/init_project.py` → nothing (exit 1)
- `scripts/store.py:262-268` — `listed = {name: str(where) for name, where in projects().items()}` … `write_json("projects", None, listed)`
- `scripts/parts.py:2003-2008` — `store.add_project(target)` / `drawer.apply(changes)` / `for event in events:` /
  `store.append_event(event)` / `# the project's own file last: …` / `needs.write(target, after)`
- `scripts/drawer.py:269-273` — `for change in changes:` / `if change["shelve"]:` / `parts.shelve(*change["shelve"])` /
  `if change["now"]:` / `store.write_json("drawer", change["entry"], change["after"])`
- `scripts/parts.py:960-962` — `changed = store.write_json("shelf", path.stem, copy)` / `if (path.parent / path.stem).is_dir():`
  / `store.copy_folder("shelf", path.parent / path.stem, path.stem)`
- `scripts/parts.py:1755` — `drawer.apply(changes)`; `:1758` — `shelved = [Path(path).stem for path, project in wanted if shelvable(path, project)]`
- `scripts/parts.py:2202-2203` — `except (OSError, json.JSONDecodeError) as unreadable:` / `answer = Answer(unchecked=[_cannot("--%s: %s" % (op, unreadable))])`

Runs (**E**, mine): `TMPDIR=<scratch>/tmp python3 -c 'import tempfile; print(tempfile.gettempdir())'` → `<scratch>/tmp` —
fact (1). Two of K6's four rows re-run on rsync copies, `python3 -B -m unittest discover -s tests`: the `step` row's
`("writes",)` → `()` → `Ran 1699 tests in 31.179s` / `OK (skipped=3)` — the escape the diagnosis reports; the `pick` row's →
`FAIL: test_a_pick_waits_while_another_holds_the_store (test_needs.ThePicksTest)` / `FAILED (failures=1, skipped=3)` —
the pin the diagnosis read at `tests/test_needs.py:1137-1144` and did not run, now E. (`skipped=3` against the diagnosis's
`skipped=2` is a machine-dependent skip I did not trace.) `python3 -c 'import shutil; print(shutil.Error.__mro__)'` →
`Error, OSError, Exception, …` — so a `copytree` that fails mid-loop is caught at `:2202` and its text is the list repr K8
shows.

Additions, not corrections:

- Fact (1) is wider than `TMPDIR`: macOS gives every user a private temp root (`/var/folders/<uid>/…/T`), so two users on
  one shared `SPARK_HOME` lock two files with no `TMPDIR` set at all (**H**, macOS `confstr(_CS_DARWIN_USER_TEMP_DIR)`,
  which `tempfile` consults; not run).
- The writers that could carry C3's check are few: **E** `grep` over `scripts/*.py` for `store.write_json(`, `write_file(`,
  `copy_folder(`, `append_event(`, `store.keep(` outside `store.py` → `drawer.py:273`; `needs.py:115` (the project's file);
  `parts.py:927, 960, 962, 1031, 1797, 1850, 1851, 2006, 2081, 2120`; plus `store.add_project` (store-internal) from
  `init_project.py:417` and `parts.py:2003`. See M4 for what no check in these can see.

### RC-store-levels-and-holds-4 · a record may live in three kinds of place — **partly**

Lines read, verbatim:

- `scripts/parts.py:45` — `LIBRARY = Path(__file__).resolve().parent.parent / "parts"`
- `scripts/parts.py:1296` — `to = Path(to) if to else (Path(project) / "parts" if home in (store.place("catalog"), store.place("shelf")) else LIBRARY)`
- `scripts/needs.py:604` — `shelve += [(path, None if where == "catalog" else where)] if not wrong and where not in ("project", "shelf", "library") else []`
- `scripts/parts.py:940` — `copy["based_on"] = {"project": project_name, "digest": digest(record)}`
- `scripts/parts.py:1835` — `if _parse(store.place("shelf") / path.name) == copy:`
- `scripts/parts.py:134-173` — `audit()`: no `digest` in it
- `agents/datasheet-reader.md:5` — `tools: Read, Bash, Write, Edit, mcp__plugin_spark_espressif-docs__search_espressif_sources`
- `grep -rn '\.local/share' agents commands` → six hits: `agents/parts-researcher.md:53`, `:58`; `commands/setup.md:11`, `:51`;
  `commands/research.md:105`; `commands/drawer.md:10` — as the diagnosis says
- `scripts/store.py:77-80` — `rows = [("project", Path(project) / kind)] if project else []` / `rows += [("shelf",
  place("shelf"))] if kind == "parts" else []` / `rows.append(("library", Path(library)))` / `rows += [("catalog",
  place("catalog"))] if kind == "parts" and drafts else []`
- `docs/2026-10-04-store-design.md:274-275` — `the table of layers nearest-first (each row naming its record-store
  implementation and whether it is writable)`

Runs (**E**, mine): `grep -l 'sen0308\|barrel' <scratch>/store/{drawer,catalog,shelf}/*.json` → eight dc-jack and screw-terminal
catalog records (the word `barrel`) and `sen0193-soil-moisture.json`; no file carries `sen0308` — irrigation's soil probe
is in no store layer, as the diagnosis says.

Corrections:

1. "the only reader of that digest is `_refresh_shelf_copy`" — nothing reads `based_on.digest` by name: **E** `grep -n
  '\["digest"\]\|\.get("digest")' scripts/*.py` → no match; `based_on` is read only for its `project` (`parts.py:1804-1805`).
  `_refresh_shelf_copy` compares the whole recomputed copy with the stored one (`:1835`), which is where a stale digest
  would show. The conclusion — drift is seen only on a write — stands; the sentence should say "compared whole, as part
  of the shelf copy, by `_refresh_shelf_copy`; read by name by nothing".
2. **kind** "design" is half right. The design doc asked for the thing whose absence RC-4 describes: §6.1 wants each
  layer row to say "whether it is writable" (`design.md:274-275`), and `layers()` returns `(layer, path)` with no such
  column. So "where a record goes" had a specified home that was not built. Sentence to change: "**kind** · design." →
  "**kind** · design in the writers' three choices; implementation in that §6.1's writable column (`design.md:274-275`) was
  never built — the one place the rule would have lived."
3. "nine records" → seven, as RC-1 (3).

### RC-store-levels-and-holds-5 · readers not symmetrical with writers — **partly**

Lines read, verbatim:

- `scripts/parts.py:1271-1274` — `try:` / `return json.loads(path.read_text())` / `except ValueError:` / `return None`
- `scripts/parts.py:266` — `part = json.loads(path.read_text())` (in `load`, no `try`, no encoding); `:972-977` `any_record`
  → `load(part_id, project)` for anything not in the catalog — the path `--show` takes
- `scripts/parts.py:2202` — `except (OSError, json.JSONDecodeError) as unreadable:`
- `scripts/drawer.py:92` and `scripts/store.py:239` — `encoding="utf-8"`
- `scripts/store.py:294` — `raise StoreProblem("%s line %d is not a history event — fix it by hand" % (path, number))`
- `scripts/parts.py:1203` — `for path in sorted(kept.glob("*/*")) if kept.is_dir() else []:`; `store.py:387-388` (the
  rival, see 2 below) — `A keep that fails for any reason leaves no `.part` behind`
- `scripts/parts.py:1260-1261` — `payload = (fetch or _download)(url)` / `if payload is not None:`; `:1266` — `_write_record(path, record)`;
  `:1279-1282` — `try:` / `return store.fetch(url)` / `except store.StoreProblem:` / `return None`
- `scripts/parts.py:879` — `for path in sorted(store.place("catalog").glob("*" + DEFINITION_SUFFIX)):`
- `scripts/parts.py:901-903` — `#: Some of the facts a build reads from a part record (§5.7) — not its outline (`body_mm`)
  or its simulation stand-in: a` / `#: digest of these vouches for a record until one of them changes.` / `BUILD_FACTS =
  ("needs", "power", "unused_pins", "pin_order", "footprint", "host_parts")`
- `scripts/parts.py:924-925` — `if name is None:` / `return False`; `scripts/check_spine.py:625-629` — `if handed is not
  None and verdict(stages) == EXIT_OK:` / `try:` / `parts.note_built(handed)` / `except (store.StoreProblem, OSError) as
  unrecorded:` / `print("  the build was not recorded in your history: %s" % unrecorded, file=sys.stderr)`

Runs (**E**, mine) on `store-k11` (one `0xE9` byte written at offset 61 of `shelf/sen0193-soil-moisture.json`): `--show
sen0193-soil-moisture` → traceback ending `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 61: invalid
continuation byte`, exit 1; `--need soil moisture` → the same traceback, exit 1; `--audit` → `shelf 4 current, 0 owe facts,
1 broken`, exit 1. On the clean copy: `--catalog | tail -1` → `18 record(s), 0 broken`; `--audit | head -3` → `catalog 0
current, 17 owe facts, 0 broken` / `shelf 5 current, 0 owe facts, 0 broken` (K18 reproduced).

Corrections:

1. K19 does not belong under this mechanism. `BUILD_FACTS` is a deliberate, documented exclusion (`parts.py:901-902`), and
   the design doc lists the same six facts (`design.md:250-251`: `("needs", "power", "unused_pins", "pin_order",
   "footprint", "host_parts")`) — spec and code agree; the gap is between both and `CHAIN_FACTS` (`parts.py:98`). It is not
   a reader/writer asymmetry. And the digest has no reader at all (M3): **E** the only consumer of `built` lines is
   `--tally`, `parts.py:2148` — `built = any(event.get("event") == "built" and event.get("project") == name for event in
   history)` — which never compares a digest. Sentence to change: "**explains** · K11, K16, K17, K18, K19." → "K11, K16,
   K17, K18. K19 is a different fault: a proof that is written and never read (M3)."
2. K16's rival, a deliberate rule: `keep()`'s docstring says `A keep that fails for any reason leaves no `.part` behind`
   (`store.py:387-388`) and its `except BaseException: part.unlink(missing_ok=True)` (`:402-403`) makes that true for every
   Python-level failure; only a process killed outright (SIGKILL, power) leaves one. The finding stands, narrower: "a
   `.part` left by a process killed mid-write", not "a crashed keep". The one-line skip in `find_kept` is still right.
3. The write side has the same encoding assumption: `store.py:145` — `if path.is_file() and path.read_text(encoding="utf-8")
   == text:` — so a non-UTF-8 record cannot be repaired through `--fact-set` either (read, not run). C8's reader list must
   include this line, or the repair path tracebacks the way `--show` does.

### RC-store-levels-and-holds-6 · a hold has no operation and no listing — **partly**

Lines read, verbatim:

- `scripts/parts.py:1472-1529` — `OPERATIONS` rows: list, show, validate, signals, unverified, need, skeleton, sources,
  fetch, keep, read, kept, promote, catalog, drawer, drawer-set, drawer-import, function-set, fact-set, audit, needs,
  needs-set, match, pick, requirements, step, tally, describe — no release, un-pick or forget row
- `scripts/parts.py:1772-1774` — `lines = ["  %-44s %6s  %-38s %s" % (str(e["label"])[:44], "?" if e["count"] is None else
  e["count"],` / `"%s %s" % next(iter(e["is"].items())) if e["is"] else "—",` / `"maybe owned — check the drawer" if
  e["unsure"] else ("skip: %s" % e["skip"] if e["skip"] else ""))`
- `scripts/drawer.py:281-283` — `shown.append({"entry": entry_id, "label": entry.get("label"), "count": entry.get("count"),
  "is": target,` / `"in": resolve(target, known)[0] if target else None, "unsure": bool(entry.get("unsure")),` / `"skip": entry.get("skip")})`
- `scripts/needs.py:254-255` — `return ("free it — a file holding [%s] without %s, given to --drawer-set <file> after a dry
  run — or pick another"` / `% (", ".join('{"entry": "%s", "used_in": …}' % key for key in entry_keys), ", ".join(holders)))`
- `commands/idea.md:96-98` — `A pick another project holds is **refused, naming the holder** ("1 owned, held by` / `…"):
  say so; the person frees it — `--drawer-set` with a file setting that entry's `used_in` without the holder, after a` /
  `dry run — or picks another.`
- `docs/2026-10-04-store-design.md:104` — `… "1 owned, held by smartbin-local" — the person frees it or picks another`;
  `:471`, `:474` the same words. The design names the act in prose, three times, and never as an operation.
- `scripts/parts.py:2182-2184` — `if not answer.lines:` / `for item in list(answer.problems) + list(answer.unchecked):` /
  `print("parts.py: %s%s" % (item["sentence"], " — " + item["fix"] if item.get("fix") else ""), file=sys.stderr)`

Runs (**E**, mine) on the copy, the ★C1 case (`<scratch>/proj-b/.spark/needs.json` with one need `board`): `--pick
<scratch>/proj-b board=firebeetle2-esp32s3 --dry-run --json` → `status problems`; `problem: firebeetle2-esp32s3 | 1 owned,
held by smartbin-local — 1 picked here | fix: free it — a file holding [{"entry": "dfrobot-dfr0975", "used_in": …}] without
smartbin-local, given to --drawer-set <file> after a dry run — or pick another`. The same without `--json` → `refused, so
nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here` — no fix, no key. The holds in
the copy: `1s-lipo-battery-1000-mah {smartbin-local: 1}`, `dfrobot-dfr0975 {smartbin-local: 1}`, `dfrobot-dfr0954`,
`dfrobot-fit0502`, `dfrobot-sen0193`, `seeed-xiao-esp32-c6` each `{plant-alarm: 1}` (**E** a python walk over `drawer/`).

Corrections:

1. "whose key the person cannot see in the listing made for people" holds for the plain `--drawer` and the plain refusal.
   The `--json` refusal's `fix` names the key and the template — so for an agent (the design's first reader, §6.4) the
   missing thing is the operation only; for a person at the terminal the key is withheld by `_say` dropping `fix`
   whenever an answer has lines (`parts.py:2182`, catalogue K56), which is a second mechanism. Sentence to change: "the way
   out is the generic `--drawer-set` with a hand-written file whose key the person cannot see in the listing made for
   people" → "the way out is the generic `--drawer-set` with a hand-written file; the `--json` refusal names the key and the
   template, the plain refusal and the plain `--drawer` never do (K56: `_say` prints `fix` only when there are no lines)".
   C6's own proof depends on this (see C6 below).
2. The rival "a release exists — a re-pick releases" was checked: a re-pick of the **same** project drops what its picks no
   longer explain (`parts.py:2053-2060`, said as `released`); no pick of another project and no `--needs-set` touches
   `used_in` (**E** `grep -n used_in scripts/*.py`: writers are `needs.py:328-331` and the generic drawer field). Holds.

### RC-store-levels-and-holds-7 · the spec says "all private"; the code says five places — **holds**

Lines read, verbatim:

- `docs/2026-10-04-store-design.md:120` — `Under the home (§6.1), all private (folders `0700`, files `0600`):`
- `scripts/store.py:96` — `PRIVATE = ("drawer", "drawer-import", "shelf", "projects", "history")`
- `scripts/store.py:217-218` — `for folder in {home(), target.parent}:` / `os.chmod(folder, 0o700)`
- `scripts/store.py:27-30` — `try:` / `import fcntl` / `except ImportError:  # spark installs on macOS and Linux (README);
  where there is no fcntl, a write takes no lock` / `fcntl = None`
- `scripts/store.py:357` — `return b"" if method == "HEAD" else answer.read()`
- `scripts/store.py:371-378` — the three checks: a name that is a path, a control character, more than 255 bytes

Run (**E**, mine, `ls -ld` on the real store — a read): home `drwx------`; `catalog`, `downloads`, `sources` `drwxr-xr-x`;
`drawer`, `shelf` `drwx------`; `projects.json`, `history.jsonl` `-rw-------`; a `sources/<sha256>/` folder `drwxr-xr-x` and
its PDF `-rw-r--r--`. Exactly the diagnosis's list.

Addition that bears on C12: the spec says sources are private not once but twice. §5.8 (`design.md:264-265`): `spark never
publishes, uploads or puts into a URL: the drawer, the drawer imports, the history, the projects list,` / `document bytes,
photos.` — document bytes are `sources/`. And one kept document is marked so in a record: `boards/firebeetle2-esp32s3.json:325`
— `"private_only": true,` with `:326` "No public copy of v1.1 exists (searched 2026-10-04)". So "the spec claims more than
the code does" is right, and the diagnosis's lean in C12 — shrink the spec — would un-say a privacy promise the spec makes
on purpose. Also: because `home()` itself is chmod'ed 0700 on every private write (`:217`), the 0755 places under it are
unreachable by another user on one machine today; the exposure is a shared or copied `SPARK_HOME`, as K15 says.

## Missed root causes

**M1 · An empty `SPARK_HOME` is the default home.** `store.py:48` tests truthiness, so `SPARK_HOME=` (a `$VAR` that expanded
to nothing — the shape of the #101 incident, "its `export` did not survive to a later tool call") falls through to
`~/.local/share/spark` with no sign. **E** my run above. Rival "data, not code": no — the shell gives an empty string for
an unset name in `SPARK_HOME=$X`, and the code treats it as "not set". C1 as written skips it. Fix: treat set-but-empty as a
refusal: `SPARK_HOME is set but empty — a failed expansion? mkdir a scratch store and name it, or unset it`. Test:
`home_in({"SPARK_HOME": ""})` raises and names the cause. Size: two lines.

**M2 · A hold is two things at once, and nothing says which.** For the picking project a hold is *derived*: `plan_pick`
rebuilds `used_in[name]` from the project's picks every time (`needs.py:297-312`, `:326-331`; `_released` says what fell
away, `parts.py:2053-2060`). For every other project it is *stored*: read as given (`:308-309`, `:313`) and never
re-derived from that project's `needs.json`. So a hand edit of a project's `needs.json` — which `commands/idea.md:25` tells
people to make for a wrong need (**H**, catalogue K35; I did not re-read that line) — leaves its holds as they were until
that project picks again; a vanished folder's holds stay (RC-1); another project cannot free them (RC-6). The diagnosis
files these under three root causes; they are one: `used_in` is a cache with no invalidation and no stated owner. Two
coherent designs, the PO's to choose (D): (i) *derive on read* — compute every project's holds from the listed projects'
`needs.json` at pick time and delete `used_in` (no state to drift, no `--release`, a gone folder holds nothing; costs: one
read per listed project per pick — five today, **E** `projects.json`; a project on an unmounted volume silently holds
nothing; and the ★C1 case still needs the bin's pick changed, because the hold *is* the bin's pick); or (ii) *a decision* —
keep `used_in`, add C6's operations, and make `--audit` compare each listed project's picks with its holds and name each
disagreement (`hold dfrobot-sen0193 × 1 by plant-alarm — its needs.json picks it 0 times`). Testability favours (i); the
PO's wish to say "the bin keeps this one" without touching the bin's design favours (ii). The diagnosis offers only (ii)
and does not name the choice.

**M3 · The built proof is written and never read.** `note_built` writes a digest per board and part (`parts.py:927-929`);
the design says why (`design.md:252`: "so a proof of an old pin order does not vouch for a corrected one"). Nothing
compares one: **E** `grep -n '\["digest"\]\|\.get("digest")' scripts/*.py` → no match; the one reader of `built` lines,
`--tally` (`parts.py:2148`), tests only the event and the project name. So today an old `built` line vouches for a record
forever, whatever changed — the opposite of §5.7's sentence — and `--tally`'s `built: true` says "proven" for a design whose
pin order may have been corrected since. K19 (the digest's width) and C13 both act on a number nobody compares; the root
cause is the missing reader. Remove before add: either build the reader (`--tally`/`--audit`: `built on <date> with another
pin_order for sen0193 — rebuild to re-prove`) or drop the digests until one exists. Test: write a `built` line, change the
record's `pin_order`, assert the tally says the proof is stale.

**M4 · The store's guarantees are opt-in per writer.** `write_json` gives the key check, the git refusal, the modes and
the `.part` rename (`store.py:163-170`, `:202-218`); `write_file` gives the `.part` only (`:138-160`); `write_text` gives
nothing (`check_vendor_pins.py:138`; `promote`'s `shutil`, `parts.py:1292`). Which door a writer takes is its own choice —
`_write_record` decides by `path.parent == store.place(name)` (`parts.py:1848-1851`). The diagnosis names two instances
(the cache, an agent's `Write`); the cause — there is no one door and no check that store-bound bytes went through it — is
unnamed, and it is what C3's `_HELD` check cannot see: a writer that never calls the store cannot be refused by the store.
The honest size is small — twelve call sites (**E**, RC-3 above) — and the check is grep-shaped, like `test_docs.py`'s:
`no script writes under store.home() except through store.write_* / copy_folder / append_event / keep`.

**M5 · The catalogue's K10 severity rests on data that is not there** (RC-1 (4)): 0 Czech labels, 0 `entry-N` keys in the
PO's drawer today. Not a root cause; a correction the council should carry so K10 is ranked by its mechanism, not by the
clause.

## The changes, judged

**C1 · a missing `SPARK_HOME` is refused; every answer names its store.** Mechanism for K1 (the check), symptom for K2 (the
field helps a reader see the wrong store; it prevents nothing — C2 does). The named tests would catch a regression. Three
holes: (a) M1 — the set-but-empty case passes the `is_dir()` check unseen; add it. (b) Ordering with the git refusal: two
existing tests point `SPARK_HOME` at a folder inside a fake repository that does not exist yet and assert the **privacy**
sentence — `tests/test_drawer.py:214-221` (`test_the_drawer_is_never_written_inside_git`, `assertIn("git work tree", …)`,
`assertFalse((repo / "spark" / "drawer").exists())`) and `tests/test_store.py:159-166` (`assertIn(str(repo.resolve()), …)`).
With the check in `home()` both answer "not a folder" instead, and the person who points a store into a repository loses
the sentence that explains the rule. The refusal must say both, or `home()` must not be where the check lives for a write
(`_make_ready` is). (c) `tests/test_store.py:39`'s `home_in(...)` fixtures pass a `scratch` that exists; `test_docs.py:90`
only tests the variable is non-empty — unaffected. Message: names where (the path) and why (not a folder) and two ways
out — good for both readers. Simpler removal: none; the field `"store"` is one key and the right one. Size S holds, plus
the two test rewrites.

**C2 · the real store is written only on purpose.** Addresses the incident's mechanism only for projects under a temp
root. The diagnosis's "the twelve scratch projects of 2026-10-08 were [under the temp root]" is **H**: #101's body says
"Twelve scratch projects `p1`–`p12` were listed in his `projects.json`" and names no folder (**E** `gh issue view 101`,
read-only). A scratch *copy* of a real project under `~/Development` (the refuter's `irr`, K4) is under no temp root and
C2's rule lets it through; only the `SPARK_STORE=real` form closes that (D the PO, as the diagnosis says). The rule must
cover `tempfile.gettempdir()` (under an agent brief that *is* the scratch path), `/tmp` and its macOS alias — the diagnosis
says so. The named test would catch its own rule. Message good. Honest claim for the card: "closes the temp-folder case;
the copy-under-home case stays until the flag".

**C3 · one lock beside the data; a writer with no lock refuses.** Mechanism — yes, both halves. Test 1 would catch K5
(two children, two `TMPDIR`s). Test 2 would catch the K6 escapes, and the `step`/`pick` runs above show what it buys:
today `step`'s row can lose its lock with a green suite. Costs the diagnosis does not size: (a) the `_HELD` check inside
`write_json`/`copy_folder`/`append_event` is met by 33 direct calls in the suite (**E** `grep -c` → `tests/test_store.py`
32, `tests/test_drawer.py` 1) that write with no `locked()` — each needs the wrapper, or the check needs a suite exemption,
which would be a second guard of the K2 kind; S becomes M. (b) `home()/.lock` needs the home to exist before `open(…,
"a")`, so `locked()` must `mkdir` it — a write that then refuses (a bad key) has still created the store folder; C1 before
C3, or `locked()` refuses a missing home itself. (c) The claim "the store is outside every repository by `_make_ready`'s
rule" is narrower than written: the rule refuses only **private** targets (`store.py:211-212`); a `SPARK_HOME` inside a
repository holding only `catalog/` and `sources/` is allowed today and `.lock` would land in it — small. (d) What C3 cannot
see: M4's third door. Message: where (function, place) and why (no lock), the fix (the row) — right for the AI reader; for
a person it is code-speak, acceptable for a programming error. Keep.

**C4 · an operation's writes land all or none.** Mechanism for K8/K9 in principle, but as written it breaks a wall the
diagnosis itself lists to keep: "The history as an append-only line per event". Staging an append as `.part` + rename
means rewriting the whole `history.jsonl` on every pick, and the open-last-line handling (`store.py:299-305`, `:323`) goes
with it. Either the history leaves the set — and a pick is two steps again — or the wall goes. Also: `needs.json` lives in
the project folder, possibly another file system; a rename-set across file systems is not one unit; and a failure *during*
the renames still leaves a partial set, as the diagnosis says. The symptom the PO meets is that the answer lies about what
landed. A simpler change addresses that: keep the ordered sequence, record each step as it lands, and on an exception say
`written before the stop: drawer/k8-widget-one.json, shelf/led-test-k8.json — the rest was not; the same command,
retried, finishes it` (the sentence C4 already drafts for its rare case) — about twenty lines, no new primitive, every
write still idempotent so the retry is still safe; and move `add_project` after `drawer.apply` in `_op_pick` so a pick
that cannot write the drawer lists no project (K9). Check `shelvable` before `apply` as C4 says. Test: the K8 fixture
asserts the sentence names what landed and what did not. Size: C4 as written is L, not M; the alternative is S.

**C5 · a project is its folder.** (a) `os.path.samefile` raises `FileNotFoundError` when the **listed** side is gone; the
string fallback must come first for a missing listed folder, not only a missing argument. (b) "`add_project` never reuses a
listed name" removes a deliberate behaviour (`store.py:255`) that serves one common case well: a project **moved** (`mv
~/a/proj ~/b/proj`) today keeps its name and its holds — the old path is gone, the name is reused, the holds follow —
which is right for a move. Without the id, C5 turns a move into `proj-2` with no holds and a `proj` that holds for a folder
that is gone, until `--forget-project` and a re-pick: a regression for the most ordinary folder change a hobbyist makes.
So the spelling half is safe alone; the "never reuse" half is safe only with the id (C5's own second half, M), and the card
should say so. (c) The id travels with a copy and C5 refuses the copy — a deliberate fork then needs a new `/spark:init`,
said in the sentence; fine. Tests would catch; the case test skipping on a case-sensitive file system is honest. For the
five listed projects (all folders exist, **E** `projects.json`) nothing changes.

**C6 · holds are listed and released.** Mechanism for K3 — yes, an operation is what is missing. Three notes: (a) decide
M2 first; under (i) `--release` has no target. (b) C6's own proof ("USER-3's walk ends in one command the page names")
depends on the plain refusal carrying the command, and `_say` drops `fix` whenever an answer has lines (`parts.py:2182`,
**E** the plain run above prints no fix) — so either K56 is fixed with it or the command goes into the problem's
`sentence`, not its `fix`; otherwise the person still sees `1 owned, held by smartbin-local — 1 picked here` and nothing
more. (c) `--release <project>` run by another project's agent is, in a shared store (P178), a permission question; for
one person on one Mac it is fine — a sentence for the council. The key column in `--drawer` is right: it is what every
other command takes. Tests would catch. `--audit`'s "folder is gone" line is right and cheap.

**C7 · reads refuse what writes refuse.** Mechanism — yes. Tests would catch. What breaks today: nothing — **E** 0 non-plain
stems in the copy's `drawer/` (110), `shelf/` (5), `catalog/` (18), spark's `parts/` (8) and `boards/` (2), irrigation's
`parts/` (7) and `boards/` (1), the bin's `boards/` (1), plant-alarm's and the bin's `parts/` (0); 0 hand entries whose
key changes under an NFKD slug; imports are keyed by SKU, not label (`drawer.py` `plan_import`: `by_product.get(sku) or
store.slug("%s-%s" % (source, sku))`), so the slug change touches hand labels only. One sentence for the card: NFC on
read means an entry whose label was typed in NFD shows one `set label x → x` line (same look, other bytes) on its next
write. The existing `tests/test_drawer.py:242` (`test_labels_without_ascii_get_their_own_entries_and_a_retry_changes_nothing`)
exists, **E**, and is rewritten as said. Message names the file, the likely cause and the fix — good.

**C8 · one reader; no store problem is a traceback.** Mechanism — yes. Tests would catch. Two cautions: (a) `main()`
catching every `ValueError` hides programming errors as `could-not-run: <message>` with no location — against "where a
mistake is happening"; catch `UnicodeDecodeError` and the new `StoreProblem` by name and leave any other `ValueError` a
traceback (a traceback is *where*, for the agent that reads it). (b) Add `store.py:145` to the reader list (RC-5 (3)), or
the repair path tracebacks. The thirteen call sites are the diagnosis's grep (**H** here; not recounted). Message with
the byte offset and `0xE9` — good, better than Python's own.

**C9 · `--fetch` names what it could not keep.** Mechanism — yes; the test would catch; the record written only when a
document was kept is right. Status `problems`, exit 1: `commands/research.md:44` and `agents/parts-researcher.md:52` run
`--fetch` without asserting exit 0 (**E** grep), so nothing downstream breaks; the agent pages should say what exit 1 means
here. Keep.

**C10 · one layer, one count.** Mechanism — yes (the one walk). The shadowed id in `--catalog`'s last line is the right
sentence. **E** the two counts reproduced above. Keep.

**C11 · a record has one home that is the store.** The biggest change and the one to slow down. (a) Promote-to-shelf with
`based_on`: mechanism for K12, yes. (b) Dropping `"project"` from `needs.py:604` shelves **every** project record that passes
the contract on the next `--requirements` — **E** on the copy, `parts.shelvable(path, "irrigation")` for irrigation's seven
records → all seven `True`; four of them say "placeholder" in the record (`dc-barrel-jack-12v-inlet`, `dfr0831-buck-5v`,
`dfr0641-ds3231m-rtc`, `sen0217-flow-meter`; the catalogue's "Not a fault" section names jack, buck and flow meter as
placeholder footprints), and `dfr0641-ds3231m-rtc` owes `simulation`. So C11 puts four placeholder footprints on the shelf,
where every project's `--list` offers them as records to build with — "proven in one project" needs a definition C11
lacks, and the `built` line (M3) is the obvious one: shelve what a `built` line vouches for. (c) Simpler removal: with
`--requirements` shelving, `promote` project→library is redundant; delete that branch and the `LIBRARY` target (the library
changes by pull request, `parts.py:1865` says so already) and keep catalog→project. The PO as maintainer loses the shortcut
he alone used (**H**: the library records' route in was not traced). (d) The cache under the store with the folder named
in `source`: right; the named test would catch. (e) The `.local/share` grep fails until the six pages are rewritten — that
is the point. (f) `datasheet-reader` losing `Write`/`Edit` presumes `--fact-set` can set every field the agent fills
(`documents.*.title`/`version`, `verified`, `source`): not checked (—); if it cannot, the agent is stuck. Size L holds; (b)
needs its rule before it is safe.

**C12 · spec and code agree on privacy; the no-lock case is said.** The lean "the smaller change is the spec" is wrong on
the spec's own words: §5.8 lists document bytes among what spark never publishes (`design.md:264-265`) and a kept document
is marked `private_only` (`boards/firebeetle2-esp32s3.json:325`) — shrinking §5.1 would un-say a promise made twice. The
smaller *true* change is to say in §5.1 that the home's 0700 is the wall (it is: `store.py:217`), that the per-place modes
matter for a shared or copied store, and to add `sources` to `PRIVATE` for the §5.8 reason; `catalog` and `downloads` are
the PO's call (D) — and a 0700 catalog cuts against P178's "shared online store" direction, which the council should hear.
The doc-reading test is in the suite's style. The fetch cap: pick `FETCH_MAX_BYTES` from the largest kept document (—, not
measured) and say it in the refusal — good. The no-`fcntl` line on stderr — good.

**C13 · the `built` line vouches for what the chain reads.** Addresses nothing observable (M3): no reader compares digests,
so a wider digest changes no answer, and the named test proves a write nobody reads. Build M3's reader first, or drop
C13's digest half; keep its other half — `note_built` returning a sentence and `check_spine.py:625-629` printing it — which
is S and right.

**The existing-mechanism option (the PO's question).** The four invariants are the right frame. Two notes for the P178
council, both **H**: a *synced* folder (iCloud, Dropbox) is where `flock` and SQLite's own locking are weakest (SQLite's
"How To Corrupt An SQLite Database File" page warns against network and synced file systems — not fetched here) and where
per-entry files plus conflict-copy detection (C7) are strongest, so the PO's "synch" wish points away from a single
database file for the drawer and toward the fourth bullet (content-addressed files with a manifest, which `sources/` and
`based_on.digest` already half are) plus an explicit merge rule; and git-as-transport needs `inside_git` rewritten, as the
diagnosis says. A lock-file library changes nothing — agreed.

## What breaks for current users

Read from the copy of the store (**E** `projects.json`: irrigation, smartbin-local, rc-car, spark-quickstart, plant-alarm)
and the three project folders (read only).

- **The bin (smartbin-local)** holds `1s-lipo-battery-1000-mah` and `dfrobot-dfr0975`, one each (**E**). C6 lets plant-alarm
  take the S3 with one command — the same person on both sides, so a decision he makes, said in the output. C11 shelves
  nothing from it (0 records in its `parts/`, **E**). C1/C3: the bin's `make check` does not set `SPARK_HOME` — unaffected.
  C5: its folder exists — unaffected.
- **Irrigation** is the one C11 changes: its next `--requirements` would shelve all seven records, four of them
  placeholders (**E** above) — the shelf then offers them to every project. C9: a dead cited URL turns its `--fetch` to
  exit 1 — honest. Its `irrigation.requirements.json` name (catalogue K40) is outside this area but is the file
  `--requirements` would not read while shelving — worth one sentence on C11's card.
- **Plant-alarm** holds `dfrobot-dfr0954`, `dfrobot-fit0502`, `dfrobot-sen0193`, `seeed-xiao-esp32-c6`, one each (**E**).
  C6 makes them visible and releasable; C11 shelves nothing (0 records in `parts/`, **E**); C7 changes none of its keys.
- **Every project**: C1 changes the sentence for a `SPARK_HOME` inside a repository unless ordered with the git refusal (two
  tests, **E**); C3's writer check meets 33 direct writes in the suite (**E**); C5's "never reuse" strands the holds of a
  moved project until the id lands; C12's chmod of `sources`/`catalog`/`downloads` to 0700 on the next write touches only a
  store shared across users or machines — the PO's is neither (**H**, one Mac).

## Searches

none — every claim rests on the cited lines, the runs listed below, `gh issue view 101` (read-only) and the discovery files.
The two library notes in "The existing-mechanism option" are tagged H with their sources and were not fetched.

## Appendix — the runs, in order (sanitised; every one on a copy or a hand-made scratch store)

```text
SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp env | grep SPARK_HOME        → the scratch path
RC-1  store-case: projects.json {"Proj-E": …}; python -c project_name(Proj-E)/project_name(proj-e)/samefile/add_project(proj-e, dry_run)
RC-1  python -c store.slug / drawer.clean on NFC and NFD "Čidlo půdní vlhkosti", "датчик влажности"
RC-1  labels.py over <scratch>/store/drawer: imports 99, non-ASCII labels 7, entry-N keys 0, hand keys that would change 0
RC-2  SPARK_HOME=<scratch>/store-missing … parts.py --drawer --json ; ls store-missing
RC-2  SPARK_HOME="" HOME=<scratch>/home python -c store.home()
RC-2  python -c import store, parts, needs, drawer, boards, init_project, check_vendor_pins, check_spine, cost, tools, outcomes,
      emit_footprint, emit_board, assign_pins; 'unittest' in sys.modules → False
RC-3  TMPDIR=<scratch>/tmp python -c tempfile.gettempdir() ; python -c shutil.Error.__mro__
RC-3  <scratch>/mut/spark-step (step row writes → ()) python3 -B -m unittest discover -s tests    → Ran 1699 … OK (skipped=3)
RC-3  <scratch>/mut/spark-pick (pick row writes → ()) python3 -B -m unittest discover -s tests    → FAILED (failures=1, skipped=3)
RC-4  grep sen0308|barrel over the copy's drawer/catalog/shelf ; grep based_on / ["digest"] over scripts
RC-5  store-k11 (0xE9 at byte 61 of shelf/sen0193-soil-moisture.json): --show ; --need soil moisture ; --audit
RC-5  <scratch>/store: --catalog | tail -1 ; --audit | head -3
RC-6  <scratch>/proj-b/.spark/needs.json with need "board"; --pick proj-b board=firebeetle2-esp32s3 --dry-run --json ; the same plain
RC-6  python walk over <scratch>/store/drawer for used_in
RC-7  ls -ld on the real store's home, catalog, downloads, drawer, shelf, sources, projects.json, history.jsonl and one sources/<sha256>/
C7    non-plain stems: the copy's drawer/shelf/catalog, spark parts/ boards/, irrigation parts/ boards/, plant-alarm parts/, bin parts/ boards/
C11   python -c parts.shelvable(path, "irrigation") for irrigation's 7 records ; grep -l placeholder irrigation/parts/*.json
C2    gh issue view 101 --json body (read-only)
```
