# P215 council, test and quality lens

## Why no test caught it

Every fake answers at once and keeps no state. No code waits after the reset (no sleep or clock in the three
scripts). `Unreachable` raises `CalledProcessError(1, command)` with no stderr, and the libraries print only
`str(error)`, "non-zero exit status 1", so the lost error text was invisible.

## One shared FakeBoard (tests/fake_board.py)

One class, used by `GateCase` and `test_board_ready`/`test_board_facts`. It is a script, not a switch: a list of
phases the board goes through, counted in mpremote calls and in fake seconds.

- `FakeBoard(silent_for=N, gone_for=M, error=RAW_REPL, boot=BOOT_TEXT, files=...)`.
- `__call__(command, **kw)` is the `run`. mpremote commands: while `silent_for > 0`, decrement and raise
  `CalledProcessError(1, command, output="", stderr=<the recorded text>)`. While `gone_for > 0`, the same with the
  recorded "Device not configured" text (and `connect` to a missing port). Then answer as `on_board` and `fs` do
  today, keeping `copied`.
- esptool commands succeed and arm the silence, so "silent after the reset" holds by construction.
- `FakeClock`: `now()` and `sleep(s)` advance a number, and `sleep` can also tick the board's silence. A board that
  is silent "for 6 seconds" is then answered by the code's own waiting, with no real wait.

## Tests to write first (red before the fix)

1. `test_ready_waits_for_a_board_that_is_silent_for_n_reads`: `silent_for=3`, expect `ready seen`, and fake time
   advanced by the retry schedule only.
2. `test_a_board_silent_past_the_bound_is_unknown_and_keeps_mpremote_s_words`: `silent_for=99`; the verdict is
   unknown, the sentence and the board log contain "could not enter raw repl", the retry count is exactly the
   bound, and fake time never passes the cap.
3. `test_a_port_that_vanishes_and_returns`: `gone_for=2` is retried like silence; the last error text names
   "Device not configured".
4. The facts file is written after a late board too (BoardFacts shares the wait).
5. `test_deploy_exit_and_store_record_when_never_ready`: still exit 2, a log with the error text, and a printed
   re-check command that is the real command line (assert it with `shlex`, as `again` is tested).
6. `test_the_recheck_command_runs_the_two_reads_and_no_flash`: no esptool in `ran`, so the person is not asked to
   erase again.
7. Guard: retries never rerun esptool, and a timeout on `import main` stays `ready not seen`.

## Injectable time

Only what the fix adds: a `Waiter(clock, sleep)` handed to `BoardReady`, `BoardFacts` and `main`, defaulting to the
real ones, as `run` is. Old `wait=` is a read timeout; leave it. The settle delay goes through the same `sleep`, so
old tests assert it was called with fake seconds.

## Never checked by any test, from the bench log

- Step 4: both mpremote steps fail after a good flash: the verdict is tested, the error text and re-check line are not.
- Steps 5 to 8: Ctrl-C answered only just after boot text. Bench-only; no fake should pretend to model it.
- Step 9: a port that vanishes mid-run, and its OSError text.
- Real ROM noise mixed with `ready` in `import main` output: only clean text is tested.

## Fixtures under tests/data (new folder tests/data/bench_c6/, with a README giving date, tool versions, sha256, as board_look does)

- `rom-boot.txt`: the real `rst:0x15 (USB_UART_HPSYS),boot:0x1e (SPI_FAST_FLASH_BOOT)` lines plus `ready`, so the
  ready check is tested on real noise, not on `ready\n`.
- `mpremote-raw-repl-error.txt`: the real stderr ("could not enter raw repl", with its traceback).
- `mpremote-device-not-configured.txt`: the real `[Errno 6]` text.
- `esptool-5.5.0-write.txt`: the real write and reset output, as `c6-flash-id.txt` is for the look.

Capture them from the PO's bench terminal (the log of step 3 to 9), with the home path removed from the text.
Fixtures keep the suite honest: when mpremote words change, the fixture is dated and visible.
