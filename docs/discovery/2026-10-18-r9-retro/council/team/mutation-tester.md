# R9 retro: the mutation tester
**Helped**
- It finds real gaps. On 10 Done cards it planted 213 defects, 25 escaped, 23 were real gaps (facts.md). P272 lost 6 of 12, all real. P247 lost 0 of 12, so a clean result also tells a story it is safe.
- Over 33 counted runs since 10-12, 27 found a missing test, and all escapes but 2 got a test or a fix (P288 analysis, section 3). Reviews find other defects (crashes, wrong docs), so neither replaces the other.
- Near tests first works: P283 ran 22 mutants in 399 s, about 18 s each (retro inbox, 10-17).
**Slowed or wasted**
- 11 runs cost 193 minutes summed, from 7.3 (PR 8) to 35.1 (P242). The slow runs made the most Bash calls: P242 16, P273 19 (logs.json).
- Repeats. P288 finds a story often pays for the tester two or three times, each call two full suites (about 4.5 min). The log holds separate runs for PR 5, 6, 7 and 8.
- 20 of 287 flagged tool errors came from the tester (facts.md). 62 of 1823 stored rows (3.4%) are refused today.
- The inbox asks how many full-suite runs per story are reviewers' own. I have no count for that.
**One change I ask for**
- Run the tester once per story, on the whole branch, capped at 12 plants, as P288 proposes. Run `--anchors` first (seconds), so a broken anchor costs no suite run. Evidence: 193 minutes over 11 runs, with repeat PR runs in the log.
