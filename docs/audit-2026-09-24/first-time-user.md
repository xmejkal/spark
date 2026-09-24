# spark, used cold on someone else's project

**Scenario:** ESP32 DevKitC (WROOM-32) + SSD1306 OLED on I2C + EC11 rotary encoder (A/B/SW) + two buttons. Bench tool. Scratch project at `/private/tmp/claude-501/-Users-petr-Development-smartbin-local/662ade08-78a3-435e-9d12-c451b87f999a/scratchpad/benchtool`.

**Bottom line:** I did get real value — `check_design.py` found two genuine bugs in my first draft and `assign_pins.py` gave me a pin map with reasons. But I got there by reading Python source, not docs, and I hit three bugs, two of which cause the plugin to report **"nothing to fix" on designs that are broken**.

---

## 1. The first wall

The README never says how to install spark itself. It tells me how to install *kicad-happy* (`/plugin marketplace add aklofas/kicad-happy`) and five MCP servers, but there is no line for spark. I guessed `claude plugin list` and found it already installed.

The first hard failure was running the one command `spark-check/SKILL.md` documents:

```
$ ./scripts/check_design.py examples/smartbin.design.json
(eval):1: permission denied: ./scripts/check_design.py
EXIT=126
```

Every script is mode `100644` in git (`git ls-files -s scripts/` — all 14). That matters more than a chmod, because the skill's own grant is

```yaml
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_design.py *)
```

— it whitelists exactly the form that cannot execute. `python3 scripts/check_design.py` works but falls outside the grant, so it prompts. Same in `spark-review` (`findings.py`, `check_all.py`).

## 2. Three real bugs

**(a) `check_all.py` cannot run the headline check. `scripts/check_all.py:86`**

```
[????] pin-capability     every pin can do what it is being asked to do
         AttributeError: module 'check_design' has no attribute 'check'
```

It calls `check_design.check(...)`; the function is `run(design, board)`. The pin-capability check has *never* run through the aggregator that `spark-review` is built on. Exit code is 2 (honest), but the human-readable summary still prints **"nothing found by the checks that ran"** on a design that `check_design.py` directly flags with 2 problems.

**(b) The two shipped boards use different role vocabularies, and each tool knows only one.**

| | roles in board file | |
|---|---|---|
| `xiao-esp32-c6.json` | `boot_log_tx`, `onboard_led` | |
| `firebeetle2-esp32s3.json` | `console_uart`, `onboard_button`, `onboard_led`, `strapping`, `adc2_unusable_with_wifi`, `not_wake_capable` | |

`check_design.py` hardcodes `boot_log_tx`. `assign_pins.py` hardcodes `console_uart`/`onboard_button`/`onboard_led`/`strapping`. Nothing validates role names — `boards.py --validate` says "ok" for both. Consequences, both reproduced:

```
$ python3 check_design.py firebeetle-bootlog.design.json     # NEO-6M, reads_serial, on TX/RX
firebeetle-bootlog.design.json: 1 parts against DFRobot FireBeetle 2 ESP32-S3
nothing to fix.
EXIT=0
```

A serial-parsing GPS sitting on the console UART of a shipped board — one of the five headline checks — passes silently. Symmetrically, `assign_pins.py`'s 40-point console penalty never fires on the XIAO.

**(c) A shared I2C bus is reported as a pin collision.** My OLED and my AHT20 both on IO21/IO22:

```
TempSensor: SDA wants IO21, already taken by Display.SDA
TempSensor: SCL wants IO22, already taken by Display.SCL
```

The exclusivity check keys a flat `claimed[label]` and never looks at the `"i2c": {"bus": "i2c0"}` field sitting on both parts. Two I2C devices is the normal case; the author's design has exactly one, so it never surfaced. To get a clean run I had to **delete the second device's SDA/SCL from the design file** — which silently disables exclusivity checking on those pins.

## 3. Every place I had to read source or guess

- **Design-file `board:` resolution.** `check_design.py` reads only the plugin's own `boards/` (`BOARDS = Path(__file__).parent.parent / "boards"`). It never calls `boards.py`, never reads `boards/active.json` or `.spark/board.json`. So after adding my board and having `boards.py --list` show `* esp32-devkitc (project)`, the headline check said:
  ```
  no board definition for 'esp32-devkitc'.
    shipped: firebeetle2-esp32s3, xiao-esp32-c6
  ```
  This directly contradicts `boards/README.md`: *"a project's own `boards/<id>.json` overrides the library. Nothing you have checked can be replaced by a plugin update."* Fix was to guess a relative path, `"board": "boards/esp32-devkitc.json"`.
- **`boards.py --list` is documented as "what is available" but fails before listing anything** unless `boards/active.json` already exists: `boards.py: no board selection at .../boards/active.json`. Chicken-and-egg — you list to find out what to select. It also accepted a selection naming a board that doesn't exist without a word.
- **The board schema.** I learned it by running `--validate` repeatedly and by dumping `xiao-esp32-c6.json`. `physical` and `wokwi_part_type` are required even for a paper pin check, so I had to invent a Wokwi part type and dimensions before anything would run. Nothing validates `wokwi_part_type` against Wokwi's catalogue.
- **`assign_pins.py`'s requirements format** is documented nowhere — not README, not any SKILL.md. I read `main()` to learn it's `{"signals":[{"name","needs","bus","pin"}], "parts":[...], "board":...}`.
- **`parts.py`, `scripts/`, `parts/` are mentioned in no README and no SKILL.md** (`grep -rn "parts/" README.md skills/*/SKILL.md` → zero hits). There is no `parts/README.md`, so the part schema is copy-a-JSON-file only.
- **Which of the six skills to start with.** The README table describes them, but nothing says spark-check is the cheap first thing and spark-design is a prose workflow with no scripts behind it.

## 4. Where the tool assumed the author's project

- **`pin_roles` is a schema the validator enforces but nothing consumes.** I typed `input_only` (GPIO34/35 have no internal pull-up — the #1 ESP32 button bug) and `strapping` (GPIO12 high at reset bricks a WROOM-32). `--validate` *demanded* a non-empty note for each. Then `check_design.py` printed nothing for either. Only `boot_log_tx` is wired up — the one role the author's board has.
- **`check_design.py` resolves boards from the plugin only** (above). A plugin that ships a board library and a documented override, where the override doesn't reach the main tool.
- **`parts.py` has a project overlay that no CLI flag can reach.** `search_path(project)` exists in every function, the comment says *"a project may keep its own in `parts/`. A project's own wins"* — but `main()` never passes `project` and there is no `--project` flag. With my `parts/ssd1306-oled.json` sitting right there:
  ```
  $ parts.py --list
    dfr0534-module   audio          DFRobot DFR0534 voice module
    l9110s-module    motor-driver   L9110S dual motor driver module
    vl6180x-breakout rangefinder    VL6180X time-of-flight rangefinder breakout
  $ parts.py --show ssd1306-oled
  parts.py: no part called 'ssd1306-oled'.
  ```
  (`assign_pins.py:291` calls `parts_library.signals_for(wanted["parts"])` with no project either, so naming my own part there fails too.)
- **Two disjoint parts libraries.** `parts/*.json` (machine-readable, 3 parts: VL6180X, L9110S, DFR0534 — all smart-bin) and `references/verified-parts.md` (prose: XIAO, TB6612FNG, MAX98357A, SSD1306, RZ7899, IR module). Overlap is essentially zero. My SSD1306 *is* covered — in the prose one, which no script can read.
- **No rotary encoder anywhere.** `grep -rin "encoder\|quadrature\|EC11"` across `skills/ scripts/ parts/ boards/ README.md` → zero hits. No part, no design rule (debounce, pull-ups, interrupt-capable A/B).
- **`design-rules.md` Part 2 is "ESP32-C6 / XIAO ESP32-C6 checklist".** There is no equivalent for my chip, and no note that Part 1 is the generic half.
- **`boards/README.md` step 4 says `python3 tools/boards.py --validate`** — `tools/` exists in neither the plugin nor the author's own repo (`ls /Users/petr/Development/smartbin-local/tools/boards.py` → No such file). Same stale path in `scripts/boards.py`'s own docstring, line 11.
- **`findings.py` requires `dist/board/circuit.json` and tells me to run `make`.** My project has no Makefile; nothing scaffolds one. The `hooks.json` Makefile-with-`check:` assumption is the same. So `spark-review`'s memory is unreachable until you're already inside the author's build layout.
- **`spark-design/SKILL.md` has zero references** to `check_design.py`, `assign_pins.py`, `parts.py`, `boards.py` or `boards/`. The design workflow and the script layer are two halves that don't touch — the headline check isn't in the design workflow.
- **Three version numbers:** README `v0.1.0`, `plugin.json` `0.6.0`, `claude plugin list` `0.4.0`.

## 5. What worked well — don't break this

- **`check_design.py` output.** Once it ran, it found two real bugs in my first draft and the messages are excellent — they name the part, the pin, the reason, *and the way out*:
  ```
  ButtonBack: A wants IO21, already taken by Display.SDA
  BatterySense: SENSE needs a adc pin, but IO26 (GPIO26) cannot do that
      pins that can: IO32, IO33, IO34, IO35, IO36, IO39
  TempSensor: answers to 0x3c on i2c0, and so does Display
      one of them needs its address strap changed, or its own bus
  ```
  The I2C address clash is exactly the thing no EDA tool catches, and the pitch is honest.
- **Adding a board actually works**, and the validator teaches the schema one error at a time (`missing required key 'wokwi_part_type'`). That loop is good.
- **`assign_pins.py` is the best thing in here** and the README doesn't mention it. It explains every choice — *"needs adc; this pin also does wake, which is spent here because nothing else was available"* — and lists what's left with capabilities. Spend-the-scarce-pins-last is right, and the rationale comments in the source are the best writing in the project.
- **The refusals are principled.** `--validate --for-fab` correctly blocked my footprint-less board, and `emit_board.py` said *"this board has no verified footprint, so a board file would reference nothing"* rather than emitting junk.
- **`boards/README.md`'s "a board fact vs a design decision" section**, and `FORBIDDEN_KEYS` enforcing it, is a genuinely good idea I'd copy.
- 216 unit tests, all green in 0.05s (`python3 -m unittest discover -s tests -t tests`). They just don't cover the three bugs above.

One caveat on the above: two things I could not exercise as a user. spark's skills were not loaded into my session (`Skill(spark-check)` → `Unknown skill: spark-check`), so I ran the scripts by hand as the SKILL.md files specify rather than through the skills. And `kicad-cli` is not installed here, so the `spark-verify` KiCad tier is untested.

## 6. The one change that would most improve my first hour

**Make `check_design.py` resolve boards through `boards.py`** — so my `boards/<id>.json` plus `boards/active.json` just works, and `board` becomes optional in the design file. That single change turns "add a board" from a documented promise the main tool doesn't honour into the plugin's actual on-ramp, and it's the step everything else is gated behind: findings, review, emit.

Close second, and nearly free: **`chmod +x scripts/*.py`** — one commit, and it makes the plugin's own `allowed-tools` grants function.

If there's room for a third, **validate `pin_roles` names against the vocabulary the scripts consume**, and make the two shipped boards agree. That turns bug (b) from a silent miss into a startup error.

### Files I produced (all under the scratch dir above)
`boards/esp32-devkitc.json` (a working DevKitC/WROOM-32 board definition, passes `--validate`), `boards/active.json`, `benchtool.design.json`, `benchtool.requirements.json`, `parts/ssd1306-oled.json`, plus `roles-probe.design.json` and `firebeetle-bootlog.design.json` — the last two are minimal reproducers for bugs (b) and the dead `pin_roles`, and are worth lifting into `tests/`.
