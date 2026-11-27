# P1264: the board tools are found where the person's shell finds them: rows

Card: [P1264 #1823](https://github.com/xmejkal/spark/issues/1823). The plan was written by the plan-writer, checked by a
lens (Sonnet) and the refuter (Opus), and given its yes by the delegated council (tech lead, architect, PO assistant,
Opus), delegated and the PO's to change. This file holds the acted, raised and rejected findings only. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | with the two `exe` fields, `tests.test_orphans` fails (`board_connection.py: mpremote`, `board_look.py: esptool`) | plan refuter (Opus) | acted | D1 wins over the council's line: `NOT_YET_MOVED` stays empty. `board_connection` names mpremote from its module's own name (`mpremote_main.__name__`). `board_look.py` must say which tool it reads, so it is a separately named exemption `READS_ITS_OWN_TOOL` with its reason. The stale-entry test covers both dicts and finds the file anywhere under `scripts/` |
| 2 | `ToolPythonFinder` resolves `which` and the reader at call time | plan refuter | acted | both default to `None` and are looked up when used. A test swaps `shutil.which` by hand and sees it |
| 3 | the cache keeps a found answer only | plan refuter, plan lens | acted | a test: the module appears between two finds. `forget()` runs after `install` |
| 4 | three texts hard-code `python3 -m mpremote devs` | plan refuter | acted | `deploy.md` and `json.md` say `mpremote devs`. `download_mode.PORT_GONE` takes the line from the finder's own command, so the person runs what spark ran. A test pins both forms |
| 5 | a probe takes 0.45 to 0.58 s through the shim and 0.14 to 0.16 s direct | plan refuter | acted | the module docstring and the risks say about half a second. The answer is kept per process |
| 6 | `build.md`, `research.md` and `journey/build.md` join the docs table | plan lens | acted | `build.md` and `research.md` carry the exception for the fixed phrase. `journey/build.md` is unchanged: it shows a recorded run of 2026-10-05, and the page is at its budget of 209 lines (`test_docs` failed at 211) |
| 7 | `commands/setup.md` says what Claude does when the tool is on the PATH but in no Python spark can use | plan lens, council C3 | acted | the fixed phrase is the constant `tool_python.NO_PYTHON_HOLDS_IT`. A test pins it in `setup.md`, `build.md`, `research.md` and `scripts.md` |
| 8 | `exe` keeps one meaning and `KIND_NEEDS` keeps its shape | plan lens, D2 | acted | `KIND_NEEDS` is unchanged. `setup.md`, `scripts.md` and `words.md` say "optional for python". A test pins that an empty `exe` means no PATH lookup |
| 9 | `ModuleReader` is a Probe | plan lens | acted | the class is `ModuleReader`. `words.md` gains the running Python, the PATH, the tool's Python and `exe` |
| 10 | the on-PATH sentence leads with that fact, and the install line comes after it | plan lens | acted | the start `is not installed — install:` is read by no code, only by docs. It stays for a tool found nowhere. The new sentence ends with one step to copy, with its own test |
| 11 | the `[ok]` row reads `mpremote 1.29.0, runs with <Python> (found through <executable>)` | plan lens, C1 | acted | pinned as a literal in two tests |
| 12 | each test names its red | plan lens | acted | each docstring says what failed first |
| 13 | the venv fixture skips with a reason when `python3 -m venv` is absent | plan lens | acted | `setUpClass` raises `SkipTest` with the error. The temporary folder is resolved, because macOS names `/var` as `/private/var` |
| 14 | step 0 was a full-suite trap run | plan, C6 | raised | the machine was under load, so the trap ran 54 test modules only. 64 tests reached the new branch. 59 of them find `littlefs`, which has no `exe`, so their answer cannot change. One is `to_install` and gets an explicit PATH. Three are `status` runs with a controlled PATH. Dropped because: no other test changed its answer with this PATH on this Mac, which the same-failures diff of 17 modules on main and here shows |
| 15 | the probe child exits 1 for "no module" | plan | acted | a crashing Python also exits 1, so the child exits 3 for no module. Any other failure is "cannot ask", never "no module". A mutation row pins the 3 |
| 16 | `tests/golden-records/tools-status-could-not-run.txt` fails under Homebrew's Python | the build | raised | it fails the same on origin/main: its child needs a Python that holds mpremote and esptool metadata. It passes with the pyenv Python. No change here. A card to make the golden independent of the running Python is the PO's to order |
| 17 | `--help` says how spark finds the tools once | plan | acted | `firmware_platform.FINDING_THE_TOOLS` is in the look's and the deploy's `DETAILS`. In the deploy it sits before the gate paragraph, because a test holds the `why:` paragraph last |
| 18 | `tool_finder.py` stood at 598 of 600 lines | plan | acted | the module docstring and two docstrings were shortened and two pairs of lines joined. It is 599. Three older mutation rows were re-anchored on the new text (P214 no metadata, P725 plain ToolError, sprint-10 P82 install line) and each still fails a test |
| 19 | `docs/guide/agents/bench.md` and `firmware-codes.md` | plan lens | acted | read and unchanged: they name `mpremote devs` as the command that lists the boards, which is right |
| 20 | `tools.py --status` has no Operation and no `--json` | plan, council | raised | a card filed by the delegated council, in Idea. Not part of this card |
| 21 | the page shows no missing board tool | plan, council | raised | a card filed by the delegated council, in Idea. Not part of this card |
| 22 | Homebrew's Python refuses `pip install --user` (PEP 668), so the install line fails there | plan, council | raised | a card filed by the delegated council, in Idea. Not part of this card |
