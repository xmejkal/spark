# P351 council: PO-assistant, UX and AI-UX lens

TL;DR: The walk reached the board only by going around spark. The stopper is row 7 (no path to the board without Wokwi). Rows 12 and 10 follow. Most others are polish.

## Rows judged (person / Claude)

| Row | Person sees | Claude reads | Class |
|---|---|---|---|
| 7 | Spark gives no way to the board | deploy.py refuses, no token | Stops the board |
| 12 | Wants the best build fetched for him | no build lookup, only one tools.json list | Stops the board (any non-C6 board) |
| 11 | T-Display (ESP32) cannot be flashed at all | no build listed, wrong offset | Stops the board for that board |
| 10 | Must type GPIO9 by hand | pins.py cannot name the button | Hurts next walk most |
| 14 | Must paste console text, and a console blocks copy | no console output in JSON | Hurts next walk most |
| 13 | Firmware with PWM is rejected, though it works | import check fails | Hurts next walk (dimmed LED is common) |
| 8 | Nothing | stale spark.json describes old deploy, look.py misleads | Hurts next walk (silent lie) |
| 5 | Level guessed, one wrong try | polarity null | Polish if row 10 style fix covers it |
| 2, 3 | Board LED not offered, verdict says light missing | false "unserved" | Hurts trust, not the board |
| 9 | One failed call | raw repl error | Polish (tell: retry once after look.py) |
| 6 | Odd warning | warning vs passing run | Polish |
| 1 | Extra board listed | noise | Polish |
| 4 | none | closed | closed |

## Gaps the rows missed

- A. No path for "board only plus its built-in button and LED". Rows 2, 3, 5, 10 are one gap: the board record's built-in parts need a GPIO, a polarity and a need they serve (P332 #426).
- B. No told way to leave the console. Ctrl-C and Ctrl-D failed, Ctrl-X works. Neither the guide nor the deploy output says so, and a held console blocks the next copy (row 14).
- C. No record of the person's verdict. "Works like a charm" lives only in the walk prose. Claude cannot read it from JSON, so the next stage cannot tell a played-and-liked board from a copied one.
- D. No spark copy step that keeps the facts file true (row 8). Any bench copy outside spark leaves spark.json stale.
- E. The three build words are mixed: "image", "firmware", "build". Use one word per thing: firmware = the person's code, build = the MicroPython binary, image = what is flashed. Today "image that passed a run" blurs these.
- F. "Stand-in" and "stub" both appear for machine. Pick "stand-in".

## Order of the first slice (by the PO's bar)

1. Deploy without Wokwi (row 7, gap D). Done when: the person runs one spark command, says yes, and the firmware is on the board with spark.json matching it.
2. Built-in button and LED in the board record and pins.py (rows 2, 3, 5, 10, gap A). Done when: for the XIAO, pins.py names the B button GPIO and the LED level, and the build verdict no longer says light has no pick.
3. A verdict slot (gap C). Done when: after a play, the person says "works" or "fails" and the next run of look.py or status shows that sentence in JSON.
4. Say how to leave the console and free the port (rows 14, 9, gap B). Done when: the deploy output prints "leave the console with Ctrl-X" and a copy that finds a busy port says so in one line.
5. PWM in the stand-in (row 13). Done when: the dimmed LED firmware from this walk passes import_firmware.py.
6. Most specific build, then generic (rows 11, 12, P349). Done when: for the XIAO, spark names the build it picked and why, and for the original ESP32 it names one or says none exists.

Order logic: 1 and 2 are on the path to a board. 3 to 5 stop the next walk repeating this walk. 6 is bigger and can start as a lookup that only names its pick.

## Not in the slice

Rows 1, 6, 9 as polish. Row 11's offset fix rides with item 6.
