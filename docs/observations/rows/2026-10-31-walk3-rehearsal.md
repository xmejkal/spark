# Walk 3 rehearsal: the FireBeetle 2 onboard button lights its onboard LED

Findings of Claude's rehearsal of walk 3 part 1, 2026-10-31, Prague, on main 4dc0af9d, before the PO's free walk. Every step up to the flash ran with exit 0. Spark's two flashes wrote and verified, but the board did not start. Plain MicroPython plus `mpremote cp` by hand worked: the D13 LED lit while D14 was held. The diary stays outside the repository, in the PO's walk folder, with the board logs.

The council: one agent on Sonnet 5.5 with four lenses (PO assistant, tech lead, senior developer, AI and UX), and the refuter on Opus 5.5 for the flash causes. The refuter broke the first claim that deploy reads the board without waiting for the RESET press (row 21) and showed that the octal build did not cause the failed flash. It found the real cause in MicroPython's source, tag v1.29.0, commit 0fd6c573ea815774668bbb16b8e197c8822368b2 (https://github.com/micropython/micropython/tree/v1.29.0), and reproduced the littlefs refusal with littlefs-python 0.19. The lead checked the deploy and diagram claims in the code.

New cards, all in Idea under their epics: P461 (#629), P462 (#630), P463 (#631), P464 (#632), P465 (#633), P466 (#634), P467 (#635), P468 (#636), P469 (#637).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The button idles at 1 and reads 0 while held | diary, bench | raised | a bench fact. Written only on the PO's yes — P776: waits on the PO: bench fact written only on PO's yes (P490 #669 seen_on_bench open) — P776: waits on the PO: bench fact written only on PO's yes (P490 #669 seen_on_bench open) |
