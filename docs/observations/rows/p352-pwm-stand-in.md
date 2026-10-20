# P352 PWM in the stand-in: findings rows

Findings from the review of PR #475 (2026-10-20, Prague): one Sonnet reviewer, one Opus refuter and one Sonnet
mutation run. The plan is item 2 of the P351 plan (PR #449).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `init` after `deinit` left `deinited` True, but MicroPython turns the PWM on again | reviewer | acted | `init` sets `deinited = False`, test `test_init_after_deinit_turns_it_on_again` |
| 2 | Getters read None before a set, so `led.freq() * 2` at module level raises TypeError | reviewer | rejected | a default would be a value spark does not hold, and the docstring says None |
| 3 | No test passed `duty_ns` or `invert` to the constructor | reviewer | acted | test `test_duty_ns_and_invert_are_kept_from_the_constructor` |
| 4 | The ESP32 port takes `freq` by position, so `PWM(Pin(15), 1000)` gave a TypeError that does not name the stand-in | refuter | acted | MicroPython `ports/esp32/machine_pwm.c`: `freq` is `MP_ARG_INT` without KW_ONLY; the constructor and `init` take `freq` first, test `test_the_frequency_can_be_given_by_position_as_on_the_esp32` |
| 5 | `duty_u16(0)` is lost because 0 is falsy | refuter | rejected | `_kept` tests `value is None`, 0 reads back 0 |
| 6 | `docs/discovery/2026-10-18-p295-own-simulator/finding.md:49` still says the stand-in has a Pin and nothing else | refuter | rejected | a dated discovery record, kept as it was written |
| 7 | `duty()` does not convert from `duty_u16`, and a PWM leaves its Pin's level alone | refuter | closed | the docstring says the PWM keeps calls only and makes no signal |
| 8 | Mutation run: 12 planted, 12 caught, before rows 1 and 4 | mutation tester | verified | `tools/mutate.py --copy`, every row "caught full" |
