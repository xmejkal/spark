# P215 council: the user and PO lens

Verdict: the flash worked and the report was still unreadable. He asked "What's actually going on?" because deploy.py
told him about its tools, not about his board.

## What went wrong

Raw mpremote lines, "non-zero exit status 1", log paths before any plain sentence, and Ctrl-C advice for a non-expert.
He replugged on a guess. The unknown was probably only timing: the C6's USB console returns after the reset.

## What deploy.py does itself before it asks him anything

1. After esptool's reset, wait for the serial port to vanish and return (up to 15 s), then 2 s more. Say "Waiting for
   the board to restart." once.
2. Try the copy and the read up to 3 times, with a pause between. Keep mpremote's error text in the board log, not on
   screen.
3. Only then give a verdict. Never ask him to replug before the retries ran out.

## Exact lines (after the flash, and after esptool's output is cut to one line: "Flashed 4 MB, verified.")

Seen (exit 0):
```
The board restarted and runs your program: it printed "ready", and its files match the run that passed.
Done. Nothing more to do.
Details: sim/runs/board/<log>
```

Not seen (exit 1):
```
The board restarted but your program did not print "ready" within 20 s (or its files differ from the run that passed).
This is NOT a pass. What the board said: <last 3 lines of its output>
Next: ask Claude to look at the board log: sim/runs/board/<log>
```

Unknown after waiting (exit 2):
```
The image is on the board, but I could not talk to it, even after waiting and 3 tries.
So I do not know if your program runs. This is NOT a pass.
Next: leave the board plugged in, wait 10 seconds, then run: deploy.py --check
```
No Ctrl-C advice, no replug advice, and no raw commands. Those go in the log.

## The re-check: one command

`deploy.py --check` (no erase, no yes needed, no flash): waits for the port, reads the board, prints one of the three
messages above, and adds a line to the store's `boards/<MAC>.json` with its time. It may upgrade an earlier
`ready unknown` only by a real `seen` with matching sha256s. An unknown stays unknown; it never turns into a pass by
repeating.

## Docs

- `--help`: name `--check`; say the cause in plain words.
- agents.md rule 7: add that an agent relays the three messages as printed, never says "the flash is fine" on
  `unknown`, never asks for a replug before `--check`, and never runs mpremote by hand to turn an unknown into a seen.
- commands/build.md: show the three messages and the `--check` step. Tell the person the XIAO's red LED is its charge
  LED, not the program.

## Account questions worth asking him

1. Is waiting up to about 30 s acceptable before an `unknown`?
2. Should `--check` be the only re-check, or also run by `look.py`?
3. Is a board-only blink bench (P236, #233) the next test before the button-light project? My view: yes. It removes
   the wiring doubt, so a failure can only be the flash path.
