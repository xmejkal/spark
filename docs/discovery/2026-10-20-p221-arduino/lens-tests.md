# P221 lens: tests (what survives a refactor, the pyramid for the platform seam)

PO 2026-10-20: "use tests we have that should basically stay the same if we change the insides, but also test on other levels."
Counts are by grep in tests/ on this worktree (2823 `def test_` lines, 77 test files, 166 mutation tables). I did not run the suite.
Unverified = not opened or not run.

## 1. Stable boundary or coupled to the insides

Stable (survive an inside refactor unchanged):
- `tests/test_json_contracts.py` (15 tests): key sets and status word of every `--json` envelope, "never values"
  (docstring line 1-17). The best golden level today.
- CLI tests that call `main([...])` and read exit code plus stdout: about 310 `.main(` / `main([` lines in tests/.
- `tests/test_deploy_json.py`: drives deploy through the CLI with recorded tool output in tests/data/board_look
  (`esptool="s3-flash-id-8mb.txt"` :74, `devs="mpremote-devs-none.txt"` :96). Real fixtures, not mocks.
- Fake wokwi: `tests/fake_wokwi_cli.py` is a real subprocess stand-in (env-driven), so run_scenario is tested through its CLI.
- Snapshot level: `tools/snapshot.py` records exit, stdout, stderr of spark's documented commands on 3 real projects plus
  fixtures in tests/data/snapshot (README there); `--against` shows every output change. Not in `unittest`, run by hand.
  Pure golden test of "same outside, new inside".
- Constructor-injected fakes in `tests/fakes.py` (159 lines): FakeBoardConnection :8, FakeConsent :41, FakeClock :59,
  FakeLocalClock, FakeConsoleProbe, FakePartPictures, FakeTscircuitExport. These fake the seams P239 made, so they are
  the model for the platform seam.

Coupled to internals (break on a move or rename):
- 336 lines of `mock.patch` / `patch.object` in 46 of 77 files; 265 are `patch.object`. Top targets: `tools` x60
  (`patch.object(tools, "find", ...)`, e.g. tests/test_deploy_service.py:45,145,151,157,184), `tools.shutil` x29, `board` x28,
  `check_spine` x14, `Path` x13, `check_backlog.subprocess` x13, `check_commit` x10.
  Only 2 patch a `_private` name: the habit is "patch the module global", not "patch the private helper". Still, a patch of
  `deploy_service.DeployService.sleep` (:46) or `project_image.ProjectImage.find_passed_log` (:102,:114) names a method of
  a class by path.
- Tests import modules by file name: `sys.path.insert(0, ROOT/"scripts")` then `import flasher` (tests/test_flasher.py:16-20).
  79 files do some `sys.path`/importlib setup. A module that moves or merges breaks every importer.
- About 462 lines match a private-name import or `mod._name(` call (loose grep: includes `self._x` style, so an overcount;
  unverified how many are real private imports).
- `tests/mutations/*.json` hold `find` strings of exact source lines plus the file name; 152 of 166 tables name `scripts/`.
  A refactor that rewrites a line orphans its mutation. This is the biggest hidden cost.

Evidence, PR #454 (p337-no-simulation, `git diff main..p337-no-simulation -- tests`): a refactor replacing the
`ignore_older_runs` flag by an `ImageEvidence` strategy touched 12 test files, 155 insertions and 50 deletions. Of those, 6
test files had one-to-five line changes only to build the service the new way (tests/test_deploy.py:26,73-75 builds
`PassedRunEvidence(...)` and passes it positionally; test_board_grant, test_board_look, test_deploy_gate, test_deploy_json,
test_deploy_service the same). 2 mutation tables changed (p239-pr8.json: the `find` text moved to a new file). The 6 edits are
one shared coupling: every test builds `DeployService(project, platform, ...)` itself. A single `make_service()` helper would
have made it one edit (unverified: not every file shares one builder; test_deploy.py:72 has one, the others have their own).

## 2. Test pyramid for the platform seam (cheapest at the bottom)

| Level | What | Catches | Cost per run | Exists now? |
|---|---|---|---|---|
| 1 Contract | one `PlatformContract` TestCase mixin, subclassed per strategy (`MicroPythonPlatformTest`, `ArduinoPlatformTest`); asserts the interface: `pin_map_text` gives text the platform's own check accepts, `make_image` returns bytes+elf, `layout` names the boot file, `make_flasher().plan()` has the same keys | an Arduino strategy that breaks the shared promise; a new platform proves itself by passing | ms each, no tools | No. `FirmwarePlatform.micropython(project)` is the only factory (tests/test_deploy_service.py:59,164,176; test_deploy.py:74; test_deploy_json.py:261) |
| 2 Unit with fakes | fakes of each role: FakeBoardConnection exists; add FakeFlasher (esptool), FakeCompiler, FakePortFinder | wrong call order, wrong args, wrong hint text | ms | Partly (tests/fakes.py). esptool is faked by recorded output files and a `PYTHON` path string (tests/test_flasher.py:20-23), not by a fake class; mpremote likewise |
| 3 CLI and envelope golden | test_json_contracts, test_deploy_json, snapshot.py `--against` | any change a user or an agent can see | seconds (snapshot: minutes, unverified) | Yes, strong. Keep fixed; add `--platform arduino` runs as new goldens, never edit the old ones |
| 4 Compile only | `arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C6 sketch/` on the generated sketch plus `pins.h` | C++ syntax, missing include, wrong pin symbol, wrong core | first run downloads the esp32 core (hundreds of MB, I believe around 300-500 MB installed; unverified, check at arduino.cc), then about 10-60 s per sketch, cached core (unverified) | No. No `.github/workflows` dir exists in this repo, so there is no CI at all; the gate is the local pre-push hook (tools/pre-push). Run it as an opt-in test, skipped when `arduino-cli` is missing |
| 5 Simulation | Wokwi run of the scenario; `fake_wokwi_cli.py` in unit tests, real wokwi-cli only on demand | logic that compiles but does the wrong thing; the `ready` line on serial | real: minutes plus Wokwi CI minutes (spark spends none in tests, per fake header); fake: ms | Yes (fake). Real run is a walk step. Arduino needs `elf` to be the real .elf (lens-chain) |
| 6 Bench | the P100 walk on a real board: flash, ready read, pins | a wrong pin, a wrong boot, a download-mode board, anything a model cannot know | PO time, minutes to an hour | Manual only (walk 1, P326 #418) |

What no level below the bench catches: electrical truth (a pin that is strapping, a 3.3 V level) and the real flash offset.
Level 5 does not prove timing. Level 4 does not prove behaviour. Do not count a compile as a pass of the firmware.

Rule: a test at level 3 or 1 never names a module path or a private helper. Level 2 may name a role, never a file.

## 3. Smallest first step (pays off without Arduino)

Add one `tests/service_case.py` (or extend tests/fakes.py) with a `ServiceCase.make_service(**options)` and a
`make_platform()` that the 6 deploy test files call instead of each building `DeployService(...)` and
`FirmwarePlatform.micropython(...)` themselves. Then the next constructor change (PR #454's kind) edits one place.
Same slice: turn `tests/test_deploy_service.py`'s `patch.object(tools, "find", ...)` into an injected `FakeToolFinder`
(`tools.find` is patched 60 times in 19 files, so this is the largest single coupling). Size: one helper, then move files
one at a time, each its own small PR; no behaviour change, suite green after each.

Second, as a pair: make the mutation tables find by a named marker comment or a function name rather than an exact line
(unverified how tools/mutate.py matches: I did not open it).

Third, once `FirmwarePlatform` has a second strategy: the contract mixin of level 1. Write it against MicroPython first
(a refactor with no new platform), then the Arduino strategy only has to pass it.

## Risks
- A contract test is only as good as its fakes: a FakeCompiler that always succeeds proves the call, not the code.
- Pyramid levels 4-5 depend on tools a user may not have: tests must report `skipped`, never `passed` (AGENTS.md: a
  `skipped` is not a pass).
- Snapshot baseline is from 2026-10-11 (docs/observations/2026-10-11-baseline.json): Arduino must be an additive key, or
  every old line shows as changed.
