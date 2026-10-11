# Diagnosis — store-levels-and-holds (P158 part 1)

Written 2026-10-10 by the diagnostician for this area, against spark 0.8.1 (main `a8aa34d`, `git log -1`). The findings
are K1–K19 and K58 of `../catalogue.md`. Everything below was read from the code (`scripts/store.py`, `scripts/parts.py`,
`scripts/needs.py`, `scripts/drawer.py`, `scripts/init_project.py`, `scripts/check_vendor_pins.py`, `scripts/outcomes.py`,
`tests/`, `tests/mutations/`), and where a run settles a point it was run on a copy of the PO's store (`cp -R` to
`<scratch>/store`, one copy per destructive run: `store-k4`, `store-k7`, `store-k8`, `store-k9`, `store-k11a/b/c`,
`store-k16`, `store-k17`) with `SPARK_HOME`, `HOME` and `TMPDIR` set as three separate words on every command
(`env | grep SPARK_HOME` under the prefix printed the scratch path once, first). The real store was not run against and not
written. Scratch projects (`proj-b`, `proj-c`, `proj-d`, `proj-k9`, `Proj-E`, `k7/x1…y12`) hold only a `.spark/needs.json`
or a `parts/` record made for the run. Tags: **E** a pointer or a run and its output; **H** a claim with its source; **D** a
decision, who and when; — unknown.

The suite as a baseline, run on an rsync copy of the repository without `.git` (`<scratch>/mut/spark`,
`python3 -B -m unittest discover -s tests`, the command `docs/guide/developing.md:8` names): **E** `Ran 1699 tests in
34.627s — OK (skipped=2)`, exit 0.

## 1. Root causes

Seven. The first four are design (the mechanism does what it was built to do, and that is the fault); the fifth and
seventh are implementation and documentation; the sixth is a missing piece of the design. Each names where, why, what it
explains, and what a person or an agent reading the output could have known — the diagnosability test the PO set
(*"well testable and understandable where a mistake is happening and why"*, D PO 2026-10-10).

### RC-store-levels-and-holds-1 · A thing is identified by its spelling, not by what it is

**where** · `scripts/store.py:247-250` — `project_name()` compares `where.resolve() == folder`, two path strings;
`:258-266` — `add_project()` names a project `folder.name` and reuses a listed name as soon as `Path(listed[name]).is_dir()`
is false; `scripts/drawer.py:87-92` — `entries()` keys the drawer by `path.stem` of every `*.json`, with no plain-key check,
while every write refuses a key that is not plain (`store.py:202-206`, `_target`; `store.py:99`, `PLAIN`);
`scripts/drawer.py:38-40` — `clean()` strips control characters and nothing else; `scripts/store.py:123-126` — `slug()`
keeps `[a-z0-9]` and drops every other letter; `scripts/drawer.py:235-241` — `_free_key()` tells two labels apart by raw
string equality; `scripts/needs.py:300-331` — a hold is `used_in[name]`, keyed by the project's listed **name**.

**why** · The store has three identities — a project, a drawer entry, a label — and all three are strings compared as
strings. A project is the resolved path spelled at registration: the same folder reached under another case
(`Proj-E`/`proj-e`, one inode on APFS) is "not on the list" and gets a second name; a copy of a folder is, by the code's
own definition, a second project, so the copy reserves the same stock again; a folder that vanished frees its name for the
next folder of that name, and because holds are keyed by name, the newcomer inherits them and — on its first pick — is
told it is "releasing" a hold "no pick of this project explains" (`parts.py:2053-2060`). The drawer's reads accept any
file stem as an entry key while its writes accept only plain keys, so a file a sync client or a hand `cp` leaves behind
(`x (conflicted copy).json`) is counted as owned stock on every read and refused by the first write that touches it. A
label is identity for `_free_key` and for `plan_import`'s "already says it is" question, yet two Unicode normal forms of
one Czech word are two labels, and `slug()` turns `Čidlo` into `idlo` (NFC) or `c-idlo` (NFD) and any non-Latin label into
`entry`, `entry-2`, … by insertion order.

**kind** · design.

**explains** · K4 (all three cases), K9 (the doubling), K10, the "a hold outlives its folder" half of K3.

**how one would have known** · Nothing in the output. **E** runs on `store-k4`: `--pick <scratch>/proj-b
soil=sen0193-soil-moisture` then the same from a `cp -R` copy `proj-b-copy` → `set dfrobot-sen0193: used_in {"plant-alarm":
1, "proj-b": 1} → {"plant-alarm": 1, "proj-b": 1, "proj-b-copy": 1}` · `listed proj-b-copy on your projects` — no word that
the folder is a copy. `store.project_name('<scratch>/proj-e')` → `None` while `os.path.samefile('…/Proj-E', '…/proj-e')` →
`True`, and `add_project('…/proj-e', dry_run=True)` → `proj-e` — a second project for one folder, said as a plain listing.
After `rm -rf proj-b-copy` and a new folder `elsewhere/proj-b-copy`, its dry-run pick printed `would release:
dfrobot-sen0193 — no pick of this project explains it` — the inherited hold, presented as this project's own clean-up. **E**
run on `store-k9` with `drawer/dfrobot-sen0193 (conflicted copy).json` beside the original: `--match` printed `owned 16 …
free 14` (the drawer holds 8); the pick's refusal reads `'dfrobot-sen0193 (conflicted copy)' is not a plain key —
lower-case letters, digits and '-' — so it could leave drawer`, which names a key as if the person had typed it and says
nothing of a file the reader accepted and the writer refused. **E** `python3 -c` on `store.slug`/`drawer._free_key`:
`slug(NFC "Čidlo půdní vlhkosti")` = `idlo-p-dn-vlhkosti`, `slug(NFD …)` = `c-idlo-pu-dni-vlhkosti`, `slug("датчик
влажности")` = `entry`, and `_free_key` filed the two forms as two entries.

### RC-store-levels-and-holds-2 · The home is a spelling with no existence check, and no answer names the store it came from

**where** · `scripts/store.py:46-52` — `home()` returns `Path(os.environ["SPARK_HOME"])` as given; the folder comes into being
at the first write (`store.py:215` `target.parent.mkdir(parents=True, …)`; `store.py:395` `folder.mkdir(parents=True, …)`);
`scripts/outcomes.py:73` — the envelope's fields are `envelope, tool, op, status, data, problems, unchecked, next,
truncated`: no store; `grep -n 'home()' scripts/parts.py` → nothing is ever printed from it (**E** 2026-10-10);
`scripts/store.py:35-43` — the only guard against writing the real store is the `unittest` branch, for the suite;
`scripts/check_vendor_pins.py:99`, `:102-112`, `:137-138` — a second, implicit home: `PLUGIN_ROOT / ".spark/cache"`, written
by a live run whenever the project has no cached copy yet.

**why** · The design made the home a lookup read on every call so the suite could point it elsewhere (`store.py:1-11`,
docstring; design §6.1, `docs/2026-10-04-store-design.md:273-274`) — right, and it leaves two things undone. A `SPARK_HOME`
that names nothing is treated exactly like a store with nothing in it: reads answer "empty" with `status: ok`, writes
create the folder, and the person's real store — one unset variable away — is reached by every command run in a fresh
shell. And because no answer carries the home it read, the empty-store answer and the right-store answer are
word-for-word the same. The plugin cache is the same fault one level down: a tool with its own idea of where to write,
saying nothing.

**kind** · design.

**explains** · K1, K2, K14.

**how one would have known** · **E** run with `SPARK_HOME=<scratch>/store-missing` (no such folder): `--pick <scratch>/proj-b
board=firebeetle2-esp32s3 soil=sen0193-soil-moisture --dry-run` → `firebeetle2-esp32s3: to get — known, not owned` and
`refused …: soil — no record or drawer entry called sen0193-soil-moisture — --match lists the candidates`, exit 1; the
same command on the store copy → `refused …: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here`. The
only hint is a line that blames the id. `--drawer --json` on the missing store → `{"status": "ok", "data": {"entries":
[]}, …}`, exit 0, and `ls <scratch>/store-missing` → `No such file or directory` — the folder did not even exist after the
run. **E** #101: the twelve projects were noticed by another agent reading `projects.json`, not by any output. **E** `git
status --short` in spark → `?? .spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h`; `check_vendor_pins.py
boards/firebeetle2-esp32s3.json --offline` → `ok (25 pins against cache (dfrobot_firebeetle2_esp32s3.pins_arduino.h))` —
which of the two cache folders is not said.

### RC-store-levels-and-holds-3 · A write is a sequence of independent file writes, and the lock meant to serialise them is keyed to a path outside the store

**where** · `scripts/store.py:186-187` — the lock file is `Path(tempfile.gettempdir()) / "spark-<sha256(home)[:16]>.lock"`;
`:192-194` `flock(LOCK_EX)` on it; `scripts/parts.py:2198-2200` — the lock is taken by `main()` only when the operation's
row in `OPERATIONS` says `writes`; `parts.py:926` — `note_built` takes it; `scripts/init_project.py:416-419` — `/spark:init`
calls `store.add_project(project)` with no lock (`grep -n locked scripts/init_project.py` → nothing, **E** 2026-10-10);
`scripts/store.py:258-268` — `add_project` reads `projects()`, edits, `write_json` — a read-modify-write;
`scripts/parts.py:2002-2008` — a pick writes, in order, `projects.json` (`add_project`), the drawer (`drawer.apply`), the
history (`append_event` per event), then the project's `needs.json`; `scripts/drawer.py:267-273` — `apply()` is a loop,
per change: shelve, then write the entry; `scripts/parts.py:949-963` — `shelve()` is `write_json("shelf", …)` then
`copy_folder(…)`; `scripts/parts.py:1751-1759` — `_drawer_answer` applies first and computes `shelvable` after.

**why** · Three facts combine. (1) The lock's place depends on `TMPDIR`, which every agent brief sets, so two processes on one
store with two `TMPDIR`s lock two files — the docstring's reason for the temp folder ("never a stray file in a repository",
`store.py:181-183`) chose a location whose spelling is per process. (2) The lock is applied from the outside, by the
`OPERATIONS` table, and the functions that write do not check that it is held — so a writer that bypasses the table
(`init_project.py`) or a row whose `writes` is dropped writes unlocked, and the suite notices only where a test probes
that one row. (3) Inside the lock there is still no unit of work: a pick writes four files in sequence and a drawer-set
writes two per entry in a loop; a failure at step N leaves steps 1…N−1 on disk, and the answer — `could-not-run` with the
exception's text — says nothing of what landed. The idempotence of every single write (`write_file`, set-only entries,
`recorded()` for events) makes a *retry* safe, which is why the design felt whole; it does not make the *first run's
answer* true.

**kind** · design.

**explains** · K5, K6, K7, K8, and the half-write in K9.

**how one would have known** · Nothing says it. **E** K5, two processes `with store.locked(): print; sleep 1.5; print` on one
store: `TMPDIR=<scratch>/tmp` and `<scratch>/tmp2` → `B in 506830.512 · A in 506830.512 · A out 506832.022 · B out
506832.022` (both inside for 1.5 s); the control with one `TMPDIR` → `D in …555 · D out …065 · C in …065 · C out …574`
(serialised). The two lock files: `<scratch>/tmp/spark-3cf9c3ac4793e857.lock` and `<scratch>/tmp2/spark-3cf9c3ac4793e857.lock`
— same name, two folders. **E** K7, 12 pairs of `store.add_project()` started together on `store-k7`: `registrations
attempted: 24; listed: 18; missing: x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 y3 y9` — six lost (the count is the run's;
another run loses another set), every call returned its name and printed nothing. **E** K6, the suite with one row's
`writes` dropped, on rsync copies (`<scratch>/mut/spark-<op>`): `drawer-set` → `FAILED (failures=1)`, caught by
`test_store.OneWriterAtATimeTest.test_a_write_waits_while_another_holds_the_store` (its probe is `--drawer-set`,
`tests/test_store.py:263-272`); `step` → `Ran 1699 tests … OK (skipped=2)`; `requirements` → `OK (skipped=2)`;
`drawer-import` → `OK (skipped=2)`. Three of the four escaped a green suite; `pick` is pinned by
`tests/test_needs.py:1137-1144` (**H** read, not re-run); the other seven writing operations (`skeleton, fetch, keep,
promote, function-set, fact-set, needs-set`; 12 rows carry `writes`, **E** `python3 -c` over `parts.OPERATIONS`) were not
run. `tests/mutations/p97-one-writer.json` mutates the whole `with store.locked() if writes` line, not a row. **E** K8, a
two-entry `--drawer-set` on `store-k8`, entry 2 linking a record in listed `proj-c` whose chip folder holds a file at mode
000 (a stand-in for any write that fails mid-loop): dry run → `would add k8-widget-one … · would add k8-widget-two … — is
part led-test-k8`, exit 0; real run → exit 2, `parts.py: --drawer-set: [('<scratch>/proj-c/parts/led-test-k8/chip/notes.txt',
'<scratch>/store-k8/shelf/led-test-k8/chip/notes.txt', "[Errno 13] Permission denied: …")]` — a Python list repr; on disk
`drawer/k8-widget-one.json`, `shelf/led-test-k8.json` and an empty `shelf/led-test-k8/chip/` had landed and
`drawer/k8-widget-two.json` had not. **E** K9 on `store-k9`, a fresh `proj-k9`: the pick → exit 2 (could-not-run), yet
`grep -c proj-k9 projects.json` went 0 → 1; history and `needs.json` unchanged; the `--json` envelope's `unchecked`
sentence names the key and nothing of the listing.

### RC-store-levels-and-holds-4 · A record may live in three kinds of place, two of them not the store, and nothing carries or compares

**where** · `scripts/parts.py:45` — `LIBRARY` is the plugin's own `parts/`; `:1296` — `promote()`'s target for a project record
is `LIBRARY`; `scripts/needs.py:604` — `--requirements` shelves a pick only when `where not in ("project", "shelf",
"library")`: a record in the project's own `parts/` is never shelved; `scripts/parts.py:932-941` — a shelf copy records
`based_on: {project, digest}`; `:1828-1843` — the only reader of that digest is `_refresh_shelf_copy`, run by `--fact-set`
and `--function-set`; `:134-173` — `audit()` compares no digest; `scripts/check_vendor_pins.py:99`, `:102-112`, `:137-138` —
the live cache lands in `PLUGIN_ROOT` whenever the project has none; `agents/datasheet-reader.md:5` — `tools: Read, Bash,
Write, Edit`; the six literal paths: `agents/parts-researcher.md:53`, `:58`; `commands/setup.md:11`, `:51`;
`commands/drawer.md:10`; `commands/research.md:105` (**E** `grep -rn '\.local/share' agents commands`, 2026-10-10).

**why** · The layer table (`store.py:71-81`) says where records are *read* from: project → shelf → library → catalog. It
does not say where a record *goes* when it has proven itself, so each writer chose: `promote` goes up to the plugin
folder (the original, pre-store meaning of "the library"), `--requirements` shelves what came from the catalog or another
project and skips the project's own, a drawer link shelves what it links. A record proven in one project reaches the
next project only through the drawer or the catalog; `irrigation/parts/sen0308-soil-moisture.json` and its barrel jack
are in neither (**E** `ls ~/Development/irrigation/parts/`: nine records; the shelf holds four of them). The plugin
folder is also written by a check's cache, and an agent with `Write`/`Edit` can write a record anywhere, around
`--fact-set`'s checks, the lock and the shelf refresh. Copies that exist (a project's copy of a library record, a shelf
copy of a project record) carry no mechanism to notice drift except the shelf digest, which is read only on a write.

**kind** · design.

**explains** · K12, K13, K14, K58.

**how one would have known** · **E** `--promote mypart --project <scratch>/proj-d --dry-run` → `would promote to
~/Development/spark/parts/mypart.json`, exit 0 — the folder is named; that an update discards it is not. **E** `diff
~/Development/rc-car/parts/tactile-button.json spark/parts/tactile-button.json`: rc-car's copy lacks `host_parts` (8 lines)
and `simulation` (13 lines) and keeps a prose line spark's dropped; no command prints a comparison. The four irrigation
records on the shelf: **E** `parts.digest(source) == shelf["based_on"]["digest"]` → `True` for all four today, so the
digest would work as a drift detector if anything read it. **E** `git status` in spark → the untracked cache file
(RC-2's pointer); `cached_header()` prefers the project's copy and falls back to the plugin's, and the `--offline` line
says `cache (<name>)` with no folder.

### RC-store-levels-and-holds-5 · Readers are not symmetrical with writers, and a failure to read names the wrong thing or nothing

**where** · `scripts/parts.py:1270-1274` — `_parse()` returns `None` on any `ValueError` (a non-JSON file and a non-UTF-8 file
look the same); `:264-266` — `load()` does `json.loads(path.read_text())` with no encoding and no `try`; `:2202` — `main()`
catches `(OSError, json.JSONDecodeError)` only, so `UnicodeDecodeError` (a `ValueError`, not a `JSONDecodeError`) is a
traceback; `scripts/drawer.py:92` and `scripts/store.py:239` — `encoding="utf-8"` (a BOM is `utf-8-sig`'s); `scripts/store.py:286-294`
— the history reader names the file and the line number and says "fix it by hand", not what the line holds; `:1203-1206` —
`find_kept` lists `sources/*/*` and skips nothing by `PART_SUFFIX` (`store.py:108`); `:1259-1265` with `:1277-1282` — a
download that raises `StoreProblem` becomes `None` and is skipped with no sentence, and `_write_record` writes the record
regardless; `:876-888` — `catalog_records()` counts the catalog **folder**, while `audit()` (`:134-173`) walks
`store.records(…)`, where the shelf shadows a catalog record of the same id; `:901-915` — `BUILD_FACTS` leaves out
`body_mm`, `simulation`, `pin_order_proof` (by its own comment) and `BOARD_FACTS` the pin roles; `:923-925` — `note_built`
returns `False` with no reason when the project is not listed, and `scripts/check_spine.py:625-629` prints only on an
exception.

**why** · The store's contract is enforced on the write side (plain keys, set-only, checked keep) and mostly assumed on
the read side. Where a reader does check, the failure is reported in one of three inconsistent ways: a `StoreProblem`
sentence (the drawer, the projects list, the history), a silent `None` (every `_parse` caller, `_download`), or an
unhandled exception. The exit code then says the wrong kind of wrong: a traceback exits 1, which the design reserves for
"ran, found problems" (`outcomes.py:20`, `:28`), not "could not read". Two operations that count one layer use two walks.
The `built` digest covers what §5.7 listed on 2026-10-04 (`docs/2026-10-04-store-design.md:250-253`), and the chain has
since read more (`CHAIN_FACTS`, `parts.py:98`).

**kind** · implementation.

**explains** · K11, K16, K17, K18, K19.

**how one would have known** · **E** `store-k11a`, a BOM prepended to `drawer/cjmcu-111.json`: `--audit`, `--drawer`,
`--match`, `--pick --dry-run` → `parts.py: <scratch>/store-k11a/drawer/cjmcu-111.json is not JSON (Unexpected UTF-8 BOM
(decode using utf-8-sig): line 1 column 1 (char 0)) — fix it by hand; the drawer is read whole or not at all`, exit 2 each
— the file is named and the fix is in Python's own words; `--catalog` and `--list` exit 0 (they never read the drawer).
**E** `store-k11b`, a half line appended to `history.jsonl`: `--pick … --dry-run` and `--tally` → `history.jsonl line 9 is
not a history event — fix it by hand`, exit 2; `--step … --dry-run` exit 0 (a dry run reads no history). **E**
`store-k11c`, one 0xE9 byte in `shelf/sen0193-soil-moisture.json`: `--show`, `--validate`, `--need soil` → `Traceback …
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 67`, exit 1; `--audit` → `shelf 4 current, 0 owe
facts, 1 broken · BROKEN sen0193-soil-moisture (shelf): does not parse as a JSON object`, exit 1 (it does parse — it is
not UTF-8); `--pick … --dry-run` → exit 0, `would set dfrobot-sen0193: used_in …` (a pick never opens the record);
`--requirements … --dry-run` → `refused …: its record at <scratch>/store-k11c/shelf/sen0193-soil-moisture.json does not
parse as a JSON object — repair the file by hand`, exit 1. Six commands, four different answers. **E** `store-k16`,
`sources/<64×a>/leftover-datasheet.pdf.part`: `--kept leftover` → `leftover-datasheet.pdf.part: kept; no record here
cites it … present`, exit 0. **E** `store-k17`, a catalog record citing `https://127.0.0.1:9/nothing.pdf`: `--fetch
--dry-run` → `would fetch https://127.0.0.1:9/nothing.pdf`; `--fetch --json` → `"status":"ok","data":{"documents":{},
"would_fetch":[]}`, exit 0, and the record now holds `"documents": {}`. **E** the store copy: `--catalog` → `18 record(s),
0 broken`; `--audit` → `catalog 0 current, 17 owe facts, 0 broken · shelf 5 current …`; `sen0193-soil-moisture.json` is in
both `catalog/` and `shelf/`.

### RC-store-levels-and-holds-6 · A hold has no operation of its own and no listing a person can read

**where** · `scripts/parts.py:1472-1529` — `OPERATIONS` has no release, un-pick or forget-project row (**E** `--describe |
grep -i -E 'release|forget|unpick|free'` → nothing); `:1772-1775` — the plain `--drawer` prints label, count, `is`,
unsure/skip: no key, no `used_in`; `scripts/drawer.py:276-284` — `listing()` carries `entry`, `label`, `count`, `is`, `in`,
`unsure`, `skip`: no `used_in`, so `--drawer --json` cannot show a hold either; `scripts/needs.py:250-257` — `_how_to_free`
prints `a file holding [{"entry": "<key>", "used_in": …}] without <holder>, given to --drawer-set <file> after a dry run`
with a literal ellipsis; `scripts/parts.py:134-173` — `audit()` reads no `used_in`; `commands/idea.md:96-98` — the page
repeats the procedure in prose.

**why** · A hold is a field (`used_in`) on a drawer entry, written by `--pick` as a side effect (`needs.py:326-331`) and
by nothing else on purpose. The design named the reservation (§3, §8 C) and the refusal; it did not name the act that
undoes one, so the way out is the generic `--drawer-set` with a hand-written file whose key the person cannot see in the
listing made for people. Every second project on the one FireBeetle meets this (★C1, USER-3), and because holds are keyed
by name (RC-1) a hold also outlives its folder with no listing that would show it.

**kind** · design (a missing operation), with a documentation half (the key is shown only with `--json`).

**explains** · K3.

**how one would have known** · **E** on the store copy: `--pick <scratch>/proj-b board=firebeetle2-esp32s3` → `refused, so
nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here`, exit 1 (the `fix` text with
the template is in the `--json` envelope); the plain `--drawer` row reads `FireBeetle 2 Board ESP32-S3 (N16R8) AIoT Mic
1  board firebeetle2-esp32s3` — no `dfrobot-dfr0975`, no `used_in`; `--drawer --json` entry keys: `count, entry, in, is,
label, skip, unsure`; `--audit | grep -i -E 'used_in|hold|reserv'` → nothing.

### RC-store-levels-and-holds-7 · The spec says "all private"; the code says five places

**where** · `docs/2026-10-04-store-design.md:120` — "Under the home (§6.1), all private (folders `0700`, files `0600`)";
`scripts/store.py:96` — `PRIVATE = ("drawer", "drawer-import", "shelf", "projects", "history")`: `sources`, `catalog`,
`downloads` are not; `:217-218` — `_make_ready` chmods `home()` itself to 0700 on every private write (a shared
`SPARK_HOME` becomes one person's); `:27-30` — without `fcntl` a write takes no lock and nothing is said; `:345-361` —
`fetch()` reads the whole body with no size cap; `:364-379` — `file_name_problem` checks POSIX rules only.

**why** · The spec's sentence and the tuple were written apart; nothing checks one against the other, and the tuple is
the one the files follow.

**kind** · documentation (the spec claims more than the code does) and implementation (the no-`fcntl` silence, the cap).

**explains** · K15.

**how one would have known** · **E** `ls -ld` in the copy (`cp -R` keeps modes, less the umask): `store` 0700, `drawer`
0700, `shelf` 0700, `sources` 0755, `catalog` 0755, `downloads` 0755, and each `sources/<sha256>/` folder 0755. No command
says which places are private.

## 2. What the design gets right and must be kept

Each is a load-bearing wall; the changes in §3 are built against them, not through them.

- **One home, read on every call, never an import-time constant** — `scripts/store.py:46-52`, and the reason it is so,
  `store.py:4-8`; the suite guard `store.py:35-43` with its proofs `tests/test_store.py:57-82`. RC-2 adds a check and a
  field to this; it does not move the home.
- **One walk over the layers, nearest first** — `store.py:71-91` (`layers`, `records`), tested `tests/test_store.py:104-126`.
  Every reader but `catalog_records` uses it (RC-5's count fix is to make the last one use it too).
- **A single file is written whole and only when it differs** — `.part` then rename, `store.py:138-160`; `tests/test_store.py:141`,
  `:237`, `:244` (a write that fails halfway leaves the old file whole, no `.part` behind). RC-3's unit of work is this
  pattern applied to a *set* of files, not a replacement for it.
- **Every write sets, never adds; every write has a dry run that prints was → now** — `scripts/drawer.py:197-232` (`settle`),
  `scripts/parts.py:1724-1748` (`_change_line`, `_write_lines`), `needs.py:74-102`; the answer says what a pick wrote beyond
  the drawer (`parts.py:2023-2041`) and what it released (`:2053-2060`). This is why a retry after a half-write is safe
  (**E** K8's retry dry run: `would add k8-widget-two …` only).
- **One envelope, three statuses, exit codes from one table** — `scripts/outcomes.py:20`, `:28`, `:65-74`; a bad argument is
  an envelope too (`parts.py:1553-1557`, `:2192-2195`). RC-5 is about the readers that escape it.
- **`OPERATIONS` as the one table** — the parser, `--describe`, the effects and the lock all derive from it
  (`parts.py:1472-1529`, `:1560-1568`, `:2159-2168`, `:2198-2200`). It is the right place to hang a per-operation guarantee;
  RC-3 is that the guarantee is applied around the table instead of checked inside the writers.
- **The history as an append-only line per event, idempotent by key, read as bytes** — `store.py:272-327`;
  `tests/test_store.py:325-445` (sixteen tests on this alone, **E** `awk … /def test_/ | wc -l` → 16).
- **Private places refused inside a git work tree, 0600 in 0700** — `store.py:94-96`, `:209-218`; `tests/test_store.py:147-213`.
  The rule exists so that a `git add .` in a project never publishes the drawer; RC-7 is only that three places are left
  out of it.
- **The checked keep and the one network door** — `store.py:364-405` (`file_name_problem`, `keep`), `:345-361` (`fetch`);
  `fetch_plan` is all-or-nothing by name (`parts.py:1230-1242`). RC-5's fetch fix keeps this and adds the sentence for a
  URL that did not answer.
- **Plain keys on every write** — `store.py:99`, `:202-206`. The invariant is right; RC-1 is that reads do not hold it.
- **A shelf copy carries its source and a digest** — `parts.py:932-941`. The drift detector exists; RC-4 is that nothing
  reads it on read.
- **Writes into spark's own library refused by the set operations** — `parts.py:1864-1866`. `promote` is the one exception
  (RC-4).
- **Mutation tables as the acceptance bar** — `tests/mutations/*.json`, `tools/mutate.py` (its docstring's three rules). The
  per-row escapes of K6 are found with exactly this tool; the fix is more rows and one structural check, not a new tool.
- **Text is data** — every agent and command carries the sentence (`agents/datasheet-reader.md:7`, design §6.4.6).

## 3. Changes

Each block: title · kind · size (S under an hour, M a day, L more) · fixes · what it removes or adds · how it becomes
TESTABLE · how it becomes DIAGNOSABLE · proof the PO can read. Sizes are estimates (H, mine). Nothing here is decided;
the PO orders.

### C1 · A `SPARK_HOME` that names nothing is refused, and every answer names its store

- kind: bug · size: S · fixes: K1, K2 (the "no sign in the output" half)
- removes/adds: adds two lines to `store.home()`: when `SPARK_HOME` is set and `Path(SPARK_HOME).is_dir()` is false, raise
  `StoreProblem`. The default home (no `SPARK_HOME`, no `XDG_DATA_HOME`) keeps being made on first write — a new person
  has none yet. Adds one field to the envelope, `"store": "<home>"` (`outcomes.envelope`, one argument; `parts._say` passes
  `str(store.home())`), and one line to every plain write answer: `in store <home>` (in `_write_lines`'s `said`, once).
- TESTABLE: `test_store.py::test_a_spark_home_that_does_not_exist_is_refused_and_named` (set `SPARK_HOME` to a fresh
  `mkdtemp()/missing`, call `home()`, assert the sentence names the path); `test_parts.py::test_every_envelope_names_the_store`
  (run `--describe --json` and one write's `--dry-run --json`, assert `said["store"] == os.environ["SPARK_HOME"]`); a
  mutation row `"the missing home is made": find the new `is_dir()` check, replace with `True`.
- DIAGNOSABLE: `parts.py: SPARK_HOME names <path>, which is not a folder — mkdir it if you mean a new store, or unset it to
  use ~/.local/share/spark`, status could-not-run, exit 2; and `"store": "…"` in every envelope, so an agent's log of
  the run shows which folder answered.
- proof: the K1 command above answers with the sentence and exit 2 instead of `known, not owned`, exit 0; the refuter's
  reproduction (`council/refuter.md:54-62`) cannot recur with the same output.

### C2 · The real store is written only on purpose (P164, #101)

- kind: story · size: M · fixes: K2 (the incident half)
- removes/adds: adds a guard in `store._make_ready` and `append_event` (the two places bytes enter a private place) that
  refuses a write to the **default** home when the run is not marked as the person's own. Two mechanisms are on the
  table in #101; the one that burdens the PO least and is testable: a write to the default home is refused when the
  calling project (the `--project` or the pick's project folder) or the current folder is under the system's temp root
  (`tempfile.gettempdir()`, `/tmp` and its macOS alias) — the twelve scratch projects of 2026-10-08 were. The stronger one — `SPARK_STORE=real` set once
  in the PO's shell, everything else refused — is his to choose (D, the PO; #101 says so). C1's `"store"` field makes
  either visible.
- TESTABLE: `test_store.py::test_a_write_from_a_temp_folder_never_reaches_the_default_home` (unset `SPARK_HOME`, point
  `HOME` at a scratch folder — the test's default home — run `--pick` on a project under `mkdtemp()`, assert nothing under
  that home changed and the envelope says why); the mirror test that a project under the person's home writes.
- DIAGNOSABLE: `parts.py: <project> is in a temporary folder, so it is not written into your store at <home> — set
  SPARK_HOME to a scratch store for this run`, exit 2.
- proof: `#101`'s own "value proven by" sentence: an agent's command in a fresh shell with no `SPARK_HOME` answers
  could-not-run naming the rule; the PO's commands write as before.

### C3 · One lock, beside the data, held by every writer — and a writer that holds no lock refuses to write

- kind: bug · size: S · fixes: K5, K6, K7
- removes/adds: changes `locked()`'s lock file from `tempfile.gettempdir()/spark-<hash>.lock` to `home()/.lock` (inside the
  store, so it follows the store, not the process; the store is outside every repository by `_make_ready`'s rule, so the
  docstring's "stray file in a repository" cannot happen for a private place — the docstring is rewritten to say so). Adds
  one check to `write_json`, `write_file`-through-the-store, `copy_folder` and `append_event`: `if (threading.get_ident(),
  lock_file) not in _HELD: raise StoreProblem(…)`. Adds `with store.locked():` around `store.add_project` in
  `init_project.py:417`. Removes nothing else; the re-entrancy (`_HELD`) stays.
- TESTABLE: `test_store.py::test_two_processes_with_two_tmpdirs_cannot_hold_one_store_at_once` (two children, `TMPDIR`
  differs, assert their in/out instants do not overlap — #114's sentence); `test_store.py::test_a_write_outside_the_lock_is_refused`
  (call `write_json` with no `locked()`, assert the sentence). With the second, every existing test of every writing
  operation becomes a lock test: dropping any row's `writes` effect makes that operation's own tests fail — the three
  escapes of K6 (`step`, `requirements`, `drawer-import`) close without a test each. A mutation row per writing operation
  in `tests/mutations/p158-one-writer-rows.json` (12 rows: `("writes",)` → `()`) pins it the way `tools/mutate.py` pins
  everything.
- DIAGNOSABLE: `store.write_json("drawer", …) was called with no lock held — the operation's row in OPERATIONS must say
  writes`, a `StoreProblem`, could-not-run; and `init` prints `on your projects list as 'x'` only after a locked write.
- proof: `tools/mutate.py tests/mutations/p158-one-writer-rows.json` reports every row caught; the K5 and K7 runs above
  come out serialised and 24 of 24.

### C4 · An operation's writes land all or none, and a stop says what landed

- kind: story · size: M · fixes: K8, K9 (the half-write), and the pick's `projects.json`-first order
- removes/adds: adds `store.write_set(items)` — every target checked first (key plain, folder writable, record parses), every
  `.part` staged, then every rename; a failure before the renames leaves nothing, a failure during them is a list of what
  was renamed. `drawer.apply` and `_op_pick` build one set (the shelf copy, the chip folder, the entries, the history
  line, `projects.json`, `needs.json`) and hand it over; `_drawer_answer` computes `shelvable` **before** it applies, and a
  change whose shelve cannot be made is refused with the rest (today it is applied first, `parts.py:1754`). Removes the
  per-change loop in `drawer.apply` (`drawer.py:267-273`) and the four-step sequence in `_op_pick` (`parts.py:2002-2008`).
  A folder copy (`copy_folder`) is staged to `<key>.part/` and renamed like a file.
- TESTABLE: `test_drawer.py::test_a_drawer_set_whose_second_entry_cannot_be_written_writes_nothing` (the K8 fixture: a chip
  folder with a file at mode 000; assert no `k8-widget-one.json`, no shelf copy, and a sentence naming the entry and the
  file); `test_needs.py::test_a_pick_that_cannot_write_the_drawer_lists_no_project` (the K9 fixture; assert `projects.json`
  unchanged); a mutation row "writes are applied as they come" that reverts to the loop.
- DIAGNOSABLE: `refused, so nothing was written: k8-widget-two — its record led-test-k8 (proj-c) has a chip folder spark
  cannot read: <path>` — and, for the rare failure during the renames: `written before the stop: drawer/k8-widget-one.json,
  shelf/led-test-k8.json — the rest was not; the same command, retried, finishes it`.
- proof: the K8 dry run and real run print the same two entries or the same one refusal; the K9 pick leaves
  `projects.json` as it was.

### C5 · A project is its folder, not its spelling; a vanished folder keeps its name and its holds

- kind: bug · size: S for the spelling, M with the id · fixes: K4, the "a hold outlives its folder" half of K3
- removes/adds: `project_name()` compares with `os.path.samefile` (inode) for a folder that exists and falls back to the
  resolved string for one that does not; `add_project` never reuses a listed name (removes the `is_dir()` clause at
  `store.py:264`: a vanished folder's name stays taken — `name-2` for the newcomer — until `--forget-project` (C6) releases
  it). For the copy case, which no path check can see: `/spark:init` already writes `.spark/project.json`
  (`init_project.py:202`, `PROJECT_TEMPLATE`); adding an `id` there (made once at init) and listing `{name: {folder, id}}`
  lets `add_project` say "this folder carries the id of listed project X" and refuse to list it twice. The id is the
  project's, travels with a copy, and is the handle a later shared store (P178) needs anyway.
- TESTABLE: `test_store.py::test_a_folder_under_another_spelling_is_the_same_project` (make `Proj-E`, call `project_name`
  with `proj-e` — skipped where the file system is case-sensitive, said as such);
  `test_store.py::test_a_vanished_folder_s_name_is_not_given_to_a_new_folder`;
  `test_store.py::test_a_copied_project_folder_is_refused_as_a_second_project` (with the id).
- DIAGNOSABLE: `<scratch>/proj-e is the listed project 'Proj-E' spelled differently — listed once`; `<folder> carries the
  id of your project 'proj-b' (a copy?) — spark lists one folder per project; --forget-project proj-b first, or give the
  copy its own init`; `'proj-b-copy' is taken by a folder that is gone (<old path>); its holds: dfrobot-sen0193 × 1 —
  --forget-project releases them`.
- proof: the K4a/K4b/K4c runs each answer with one of these sentences and reserve nothing twice.

### C6 · Holds are seen in the listing and released by an operation

- kind: story · size: M · fixes: K3
- removes/adds: adds to `drawer.listing()` the field `held: {project: n}` and to the plain `--drawer` a key column (the
  key is what every other command takes) and a `held by …` note; adds two `OPERATIONS` rows with `writes` and a dry run:
  `--release <project> [entry …]` (drops that project's `used_in` on the named entries, or on all of them) and
  `--forget-project <project>` (releases every hold, removes the project from the list; its history lines stay — they are
  events). `_how_to_free` names the operation instead of a JSON template (removes the `…` text at `needs.py:253-257`).
  `--audit` adds a line per hold whose project folder is gone.
- TESTABLE: `test_needs.py::test_a_release_lets_another_project_pick_the_board` (the ★C1 case on a fixture);
  `test_drawer.py::test_the_listing_shows_the_key_and_who_holds_it`; `test_parts.py::test_audit_names_a_hold_whose_folder_is_gone`;
  the `--describe` test already pins that every writing row has a dry run (`tests/test_parts.py:1695`).
- DIAGNOSABLE: the refusal becomes `firebeetle2-esp32s3 — 1 owned, held by smartbin-local (dfrobot-dfr0975) — 1 picked
  here · release it: parts.py --release smartbin-local dfrobot-dfr0975 --dry-run, then without`; `--audit` prints `hold:
  dfrobot-sen0193 × 1 by proj-b-copy, whose folder <path> is gone — --forget-project proj-b-copy`.
- proof: USER-3's walk (`council/user.md:11`) ends in one command the page names, not a grep of the store.

### C7 · Reads refuse what writes refuse: keys, and labels in one form

- kind: bug · size: S · fixes: K9 (the doubling), K10
- removes/adds: `drawer.entries()` and `store.records()` check `PLAIN.fullmatch(path.stem)` and name the file;
  `drawer.clean()` normalises to NFC (`unicodedata.normalize`) before anything compares labels; `store.slug()` goes through
  NFKD and drops combining marks, so `Čidlo půdní vlhkosti` is `cidlo-pudni-vlhkosti` in either form; a label that leaves
  no ASCII letter gets `entry-<8 hex of its sha256>` instead of `entry`, `entry-2`. Removes nothing.
- TESTABLE: `test_drawer.py::test_a_conflict_copy_in_the_drawer_is_named_not_counted` (the K9 file; assert the sentence and
  that `--match` says owned 8); `test_drawer.py::test_two_spellings_of_one_label_are_one_entry` (NFC and NFD; assert one key
  and a retry that changes nothing — the existing `test_labels_without_ascii_get_their_own_entries…`
  (`tests/test_drawer.py:242`) is rewritten to the hash key); a mutation row "a drawer key is any file stem".
- DIAGNOSABLE: `<scratch>/store/drawer/dfrobot-sen0193 (conflicted copy).json is not a drawer entry: its name is not a plain
  key (a sync client's conflict copy?) — compare it with dfrobot-sen0193.json and delete one; the drawer is read whole or
  not at all`, could-not-run.
- proof: the K9 `--match` line reads `owned 8 … free 7`; the K10 one-liner prints one key for both forms.

### C8 · One reader for a store file, and no store problem is ever a traceback

- kind: bug · size: S · fixes: K11, K16
- removes/adds: adds `store.read_json(path, what)` — opens with `utf-8-sig`, says `<path> is not UTF-8 at byte N` or `<path> is
  not JSON: <Python's reason> at line L` or `<path> is not a JSON object`, as a `StoreProblem` — and replaces the store-file readers that each do
  `json.loads(path.read_text(…))` on their own (**E** grep 2026-10-10: `parts.py:266`, `:937`, `:1257`, `:1272`, `:1591`,
  `:1675`, `:1867`, `:2077`; `drawer.py:92`; `store.py:239`; `needs.py:46`, `:609`; `check_vendor_pins.py:116` — thirteen;
  `parts.py:851`, `:1318` read the project brief and `:1719` the person's input file, which keep their own sentences);
  `_parse` keeps its `None` for the one place that wants a quiet answer (linking by number) and every other caller takes
  the sentence. `main()` catches `ValueError` (`parts.py:2202`) so
  nothing escapes as a traceback. `events()` adds the first 40 characters of the bad line. `find_kept` skips
  `PART_SUFFIX` and names what it skipped.
- TESTABLE: `test_parts.py::test_a_non_utf8_record_is_could_not_run_naming_the_file_never_a_traceback` (the K11c byte; run
  `--show`, `--validate`, `--need`, `--audit`, `--requirements`; assert one sentence and exit 2 from all five);
  `test_parts.py::test_a_bom_on_a_drawer_file_is_read_or_named_once` (the K11a file; either `utf-8-sig` reads it, or every
  reader says the same sentence); `test_parts.py::test_a_part_left_in_sources_is_named_as_interrupted_not_kept`.
- DIAGNOSABLE: `parts.py: <path> is not UTF-8 at byte 67 (0xE9) — re-save it as UTF-8`, exit 2; `history.jsonl line 9 is not a
  history event: {"event":"reused","project":"x","need":"y" … — the end of the line is missing; fix it by hand`;
  `leftover-datasheet.pdf.part: an interrupted keep, not a kept document — delete it`.
- proof: the K11c commands exit 2 with one sentence instead of 1 with a traceback; `--kept` lists no `.part`.

### C9 · `--fetch` names every URL it could not keep, and says problems

- kind: bug · size: S · fixes: K17
- removes/adds: removes `_download`'s `return None` (`parts.py:1277-1282`); `fetch_documents` collects `(url, why)` for each
  `StoreProblem` and returns them beside `documents`; `_op_fetch` puts one problem per URL into the answer, so the status is
  `problems`, exit 1; the record is written only when a document was kept.
- TESTABLE: `test_parts.py::test_a_url_that_does_not_answer_is_named_and_the_fetch_is_problems` (the K17 record with
  `fetch=lambda url: (_ for _ in ()).throw(store.StoreProblem(…))`); the existing
  `test_a_fetch_that_fails_halfway_leaves_the_record_whole` (`tests/test_parts.py:973`) stays.
- DIAGNOSABLE: `not kept: https://127.0.0.1:9/nothing.pdf — does not answer (Connection refused) — the record still cites it;
  --sources lists every URL's answer`, exit 1.
- proof: the K17 `--fetch --json` answers `"status":"problems"` with the URL in `problems`.

### C10 · One layer, one count

- kind: chore · size: S · fixes: K18
- removes/adds: `--catalog` lists through `store.records("parts", LIBRARY, project, drafts=True)` filtered to `layer ==
  "catalog"` (the one walk) and says `18 files, 1 shadowed by the shelf (sen0193-soil-moisture)`; or `audit()` counts the
  catalog folder — one of the two, the same number either way. Removes `catalog_records`' own glob (`parts.py:879`).
- TESTABLE: `test_parts.py::test_catalog_and_audit_agree_on_the_catalog_s_count` (a fixture with one id in both places).
- DIAGNOSABLE: the shadowed id is named in `--catalog`'s last line.
- proof: `--catalog` and `--audit` on the store copy print one catalog count.

### C11 · A record has one home that is the store: promote to the shelf, shelve the project's own, read the digest

- kind: story · size: L (P91 #22's remaining half, with #23's grep) · fixes: K12, K13, K58, K14
- removes/adds: `promote()` from a project goes to the **shelf** with `based_on` (`shelve(path, project_name)` — the function
  exists), never to `LIBRARY`; writing spark's library becomes an explicit maintainer flag (`--into-library`) or is removed
  from `parts.py` altogether (the library changes by pull request, as `_set_in_home` already says, `parts.py:1865`).
  `needs.py:604` drops `"project"` from its exclusion so `--requirements` shelves the project's own records too. `--audit`
  compares each shelf copy's `based_on.digest` with its source's digest today and each project copy of a library record
  with the library's, and says which is behind. `check_vendor_pins.cached_header` writes the live header under the store
  (`store.place("downloads")`-like `cache/`), reads the plugin's shipped cache read-only, and names the folder in `source`.
  `agents/datasheet-reader.md:5` loses `Write, Edit` and writes through `--fact-set`; the six literal paths become "your
  store ([how it works](docs/guide/how-it-works.md#your-store))". Compiled Wokwi chips (P148–P150) are out of this area's
  code and not sized here.
- TESTABLE: `test_parts.py::test_promote_from_a_project_goes_onto_the_shelf_with_based_on`;
  `test_needs.py::test_requirements_shelves_the_project_s_own_record`; `test_parts.py::test_audit_says_which_copy_is_behind`
  (change the source after shelving; assert the line); `test_check_vendor_pins.py::test_a_live_run_never_writes_the_plugin_folder`
  (run with a scratch `SPARK_HOME`, assert `PLUGIN_ROOT/.spark/cache` unchanged); `test_docs.py` gains #23's grep (`grep
  '\.local/share' agents commands` prints nothing) and a `tools:` check that no agent but the one that must holds `Write`.
- DIAGNOSABLE: `promoted to your shelf: sen0308-soil-moisture (based on irrigation, digest …) — every project finds it`;
  `shelf copy of dfr0831-buck-5v is behind irrigation's record (digest differs) — --reshelve dfr0831-buck-5v`; `rc-car's
  copy of tactile-button is behind spark's library (host_parts, simulation differ) — compare, then --fact-set or delete the
  copy`; `cache (<store>/cache/dfrobot_firebeetle2_esp32s3.pins_arduino.h)`.
- proof: from `spark-quickstart`, `--need soil` lists irrigation's `sen0308` (#22's own sentence); `git status` in spark
  stays clean after a live `check_vendor_pins` run.

### C12 · The spec and the code say the same about privacy; the no-lock case is said

- kind: chore · size: S · fixes: K15
- removes/adds: either `PRIVATE` gains `sources`, `catalog`, `downloads` (and `_make_ready` chmods the place, not `home()`),
  or §5.1's "all private" becomes the tuple's five with a sentence why — one or the other (D the PO; the catalog holds
  nothing of the person's, the sources are vendor documents, so the smaller change is the spec). Where `fcntl` is `None`,
  `locked()` prints once to stderr `no file locking on this platform — one spark command at a time`. `fetch()` reads at
  most a stated cap (`FETCH_MAX_BYTES`, named) and refuses beyond it with a sentence.
- TESTABLE: `test_store.py::test_the_private_places_are_the_ones_the_spec_names` (reads §5.1's list from the doc, compares
  with `PRIVATE` — the suite already reads docs in `test_docs.py`); `test_store.py::test_a_download_past_the_cap_is_refused`.
- DIAGNOSABLE: `<url> is 61 MB and spark keeps at most 50 MB — download it yourself and --keep it`.
- proof: `ls -ld` of the store matches the spec's sentence.

### C13 · The `built` line vouches for what the chain reads, and says when it is not written

- kind: chore · size: S · fixes: K19
- removes/adds: `BUILD_FACTS` = `("needs", "power", "unused_pins", "host_parts") + CHAIN_FACTS` (one tuple built from the
  other, so a new chain fact cannot be forgotten); `BOARD_FACTS` gains `pin_roles`, `adc_gpio`, `wake_capable_gpio` (what
  `assign_pins` reads, by the comment at `parts.py:904-905`); `note_built` returns a sentence instead of `False` and
  `check_spine.py:625-629` prints it.
- TESTABLE: `test_parts.py::test_the_build_digest_covers_every_chain_fact` (change `body_mm`; assert the digest changes);
  `test_check_spine.py::test_a_build_of_an_unlisted_project_says_it_was_not_recorded`.
- DIAGNOSABLE: `the build was not recorded in your history: <project> is not on your projects list — /spark:init or
  parts.py --step puts it there`.
- proof: §5.7's digest sentence (`docs/2026-10-04-store-design.md:250-253`) and the code name the same facts.

### An existing mechanism instead of hand-rolled files? — the PO's question of 2026-10-10, as an option for the P178 council

The PO asked (verbatim, 2026-10-10): *"maybe some new file formats or synch libraries or techinques could be used from an
existing library that does somwthing that would make the whole store synch and global and loval and project store sync
and rules and editor?"* What RC-1…RC-5 need is four invariants — identity by thing, one lock beside the data, a unit of
work, one reader — and each is 20–60 lines in `store.py` (C3, C4, C5, C7, C8). Of the mechanisms that would supply some
of them ready-made (all **H**, mine, no search run; sources: the Python standard library's `sqlite3` documentation and
the git documentation; the trade-offs are for the council):

- **SQLite (standard library, nothing to install)** for `projects.json`, the holds and `history.jsonl`: transactions give
  C4's all-or-nothing; its lock lives beside the database file, so K5 cannot happen; `UNIQUE` keys refuse K9's doubles;
  a schema refuses K11's half line. Cost: the PO reads his store with `cat`, `diff` and `grep` today (the drawer is
  112 files he can open), a sync client treats one binary file as one conflict, and the drawer's per-entry set-only
  writes are already right. Fit: the small, often-written, cross-project tables (projects, holds, history), not the
  records.
- **Git as the store's own history and transport** (the store folder a repository; a shared store = a remote, P84):
  every write a commit, conflict copies become merge conflicts git names, `git status` is the drift check for K13, and
  it is the one tool spark already requires. Cost: `inside_git()` (`store.py:129-135`) refuses private places inside a
  work tree — the rule that keeps a drawer out of a project's `git add .` — so a store that *is* a repository needs that
  rule rewritten to "inside a project's work tree"; and a hobbyist's drawer in a remote is a privacy decision (§5.8).
- **A lock-file library** (`filelock` and the like): changes nothing — the fault is the lock's *place*, one line (C3).
- **Content-addressed files with a manifest** (what `sources/<sha256>/` already is, extended to records): drift detection
  for free (K13), no transactions. The `based_on.digest` is this, half built.

Recommendation, as a proposal: do C3/C4/C5/C7/C8 in `store.py` first — they are the invariants any later backing needs
and they close eleven findings without a dependency; take SQLite-for-the-tables and git-as-transport to the P178 council
as two questions with the costs above. D: the PO's.

## 4. What you could not check, and why

- The real store (`~/.local/share/spark`) was neither run against nor written — by rule. Every run above is on a copy;
  the copies' modes and contents are the real store's as of the `cp -R` at 11:48 on 2026-10-10.
- K8's trigger as #94's comment C-10 states it ("a shelve whose record id is not a plain key"): on `a8aa34d`
  `shelve()` runs `validate(copy, path)` first (`parts.py:958`), and `validate` refuses an id that differs from the file
  stem or is not plain (`parts.py:564-570`) — it returns `None`, no exception. That exact trigger is closed; the loop it
  exposed is not (reproduced with a different trigger, above). Whether C-10's run predates `:564-570` was not traced.
- The lock escape was run for four of the twelve writing operations (`drawer-set`, `step`, `requirements`,
  `drawer-import`); `pick`'s pin is read from `tests/test_needs.py:1137-1144`, not run; the other seven were not run.
  Each run is 35 s; the claim "three escape" is about those three.
- K7's six lost registrations are one run's count; the race is timing-dependent and another run loses a different set.
- K14's write into the plugin folder was not reproduced live (it needs the network and would write under
  `~/Development/spark`, which the rules forbid); the code path (`check_vendor_pins.py:102-112`, `:137-138`) and the
  untracked file in `git status` stand as the evidence.
- K13's compiled Wokwi chips (P148–P150) are outside `store.py`/`parts.py`/`needs.py` and were not opened.
- K15's Windows/exFAT names and the no-`fcntl` path were not run (no such machine); K15's size cap was read, not probed.
- K19's renamed-project case was read (`note_built` returns `False`, `check_spine.py:625-629` prints nothing) and not run
  through `check_spine` (it needs a built design).
- Sizes in §3 are estimates (H). Test names are proposals in the suite's style, not written.
- The incident behind K2 (#101) is the card's account; the mechanism was shown on the copy (the K9 pick listed `proj-k9`
  with no `SPARK_HOME` guard involved), not by writing the real store.

## 5. Searches

none — every claim rests on the code, the runs above, the cards read with `gh issue view` (read-only: #101, #114,
#102, #22, #23) and the discovery files named in the header. The library options in §3 are tagged H with their sources
and were not searched.

## Appendix — the runs, in order (commands sanitised; every one on a copy)

```text
SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp env | grep SPARK_HOME        → the scratch path
K1   SPARK_HOME=<scratch>/store-missing … parts.py --pick <scratch>/proj-b board=firebeetle2-esp32s3 soil=sen0193-soil-moisture --dry-run
K3   … parts.py --pick <scratch>/proj-b board=firebeetle2-esp32s3 ; --drawer ; --drawer --json ; --describe ; --audit
K4   store-k4: --pick proj-b soil=… ; --pick proj-b-copy soil=… ; --step Proj-E S ; python -c project_name/samefile ; rm -rf proj-b-copy, new folder, --pick … --dry-run
K5   two python children, store.locked(), TMPDIR tmp vs tmp2 ; control tmp vs tmp
K7   store-k7: 12 pairs of store.add_project() started together
K8   store-k8: proj-c listed; parts/led-test-k8.json + led-test-k8/chip/notes.txt (mode 000); --drawer-set k8-set.json --dry-run ; real ; retry --dry-run
K9   store-k9: cp drawer/dfrobot-sen0193.json "… (conflicted copy).json" ; --match ; --pick proj-k9 soil=… ; --json
K10  python -c store.slug / drawer.clean / drawer._free_key on NFC and NFD "Čidlo půdní vlhkosti", "датчик влажности"
K11  store-k11a (BOM) --audit --drawer --match --pick --catalog --list ; store-k11b (half line) --pick --tally --step --drawer ;
     store-k11c (0xE9) --show --validate --audit --need --match --pick --requirements
K12  --promote mypart --project <scratch>/proj-d --dry-run
K13  diff rc-car/parts/tactile-button.json spark/parts/tactile-button.json ; parts.digest(irrigation record) vs shelf based_on
K14  git status --short (spark) ; check_vendor_pins.py boards/firebeetle2-esp32s3.json --offline
K15  ls -ld store store/sources store/catalog store/downloads store/drawer store/shelf
K16  store-k16: sources/<64×a>/leftover-datasheet.pdf.part ; --kept leftover
K17  store-k17: catalog/fake-fetch-test.json citing https://127.0.0.1:9/nothing.pdf ; --fetch --dry-run ; --fetch --json
K18  --catalog | tail -1 ; --audit | head -4
K6   <scratch>/mut/spark (baseline) and spark2/spark-step/spark-requirements/spark-drawer-import, one row's ("writes",) → ()
     python3 -B -m unittest discover -s tests    → OK 1699 ; FAILED 1 ; OK ; OK ; OK
```
