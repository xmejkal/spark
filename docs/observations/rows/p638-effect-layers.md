# P638 ordered effect layers, a discovery: rows

What the writers, the refuter, the review and the discovery check found. Card: [P638 #853](https://github.com/xmejkal/spark/issues/853).
PR: https://github.com/xmejkal/pixel-games/pull/39. Rows PR: (this PR).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | After a /clear, the folder still showed the templates, so a second writer started while the first was still running. Both wrote one folder for about 10 minutes, and their question numbers split | the resume, 2026-11-05 | acted | the second writer stopped. The lens files now use the brief's queue (a0656f4). Logged in `~/.local/share/spark/learned-rules.md` and the retro inbox: list the running agents before a re-launch |
| 2 | One agent wrote all three lens reports, so the council is not an independent review | the writer | closed | the brief's Depth line says so. The refuter was the first second reader |
| 3 | The card's "each full-panel pass through PSRAM costs about 5 ms (P612)" is not a sentence in P612. P612:70's arithmetic gives 4.2 ms for a write and 6.8 ms for a read and a write | both writers, the refuter | raised | brief F1. A wording fix on #853 when the PO answers |
| 4 | ★C1 said that no C layer can go over another C layer today. A blended C layer can, because `fx_fire_blend` reads the frame | the refuter (Fable) | acted | ★C1's caveat in eae3a72 |
| 5 | ★C4 named 4 to 7 ms as one full-panel pass, but cited 11.5 to 13.3 ms for a lit blend | the refuter | acted | ★C4 separates the opaque pass and the lit blend |
| 6 | Option C's compose cost, about 6.8 ms, is an opaque copy. An alpha composite is 11.5 to 13.3 ms with skips and up to 25.9 ms without (337.5 ns × 76,800 px) | the refuter | acted | option C's cost cell |
| 7 | The fps pass line "23 or more" cannot fail, because FRAME_MS 40 caps the fps at 25 and the scene has about 14 ms free | the refuter | acted | the pass line adds the draw ms at 13.5 or less (brief, risks-and-tests, items) |
| 8 | The brief cited council ids that do not exist (TL-6, TL-11, TL-17, PA-3, PA-9 b), and Q3 meant two questions | the refuter | acted | ids now FE-6, DI-3, RA-1, RA-5, the tech lead's Q5. The list's home is Q8. The next scene with two C layers is Q9 |
| 9 | NITs: A3 cited for the fps (A2 is the fps), slice 3 on job 3 (job 4), SDL's blend names, option A's "+5 ms" (+5 to +7), the engine README's words | the refuter | acted | all fixed in eae3a72 |
| 10 | Bevy's `SortedPhaseItem` page holds the quote, but no file recorded its URL | the refuter | acted | the brief says "URL not recorded". The Unity Sorting Layers quote could not be opened (a redirect) |
| 11 | The `discovery.py check` wants each citation of a ★ claim to carry its keep words. Long keep phrases made 36 problems | the check | acted | the keep words are now short phrases from each claim line. The check passes |
| 12 | The simple-english lint hook flags the skill's own format (the `·` separators, the `—` unknown marker, verbatim quotes) | the writer | raised | brief F3, for the retro: one of the two formats must give way in discovery folders |
| 13 | `bench.md:366` says "heat * 128 // 255", but `fire.py:95` computes the alpha as `min(255, heat*255//ALPHA_FULL)` | the refuter | raised | out of this card's scope. A one-line fix in bench.md with the next bench PR |
| 14 | The review: the Hand-off said that the refuter had not run, the open questions stopped at Q3, FE-6 cited `bench.md:454` for a number on `:433`, and C13 pointed to a lens id with no URLs and quoted pages the lenses had not read | the PR review (Sonnet) | acted | 1c0b3b5. C13 now points to `council/po-assistant.md:10-13`. Bevy stays H, because its URL was not recorded |
| 15 | The review: nine NITs. A2's fail path waited for slice 2, Q5 on slice 2 in items only, the outcome allowed 22 fps, pass lines not marked proposed, "nobody saw a front blend" against Q7, the part placement written as decided, #854 taking slice 0 as a fact, the PR diagram without "option B", "A2's cost" for option A's cost | the PR review | acted | 1c0b3b5 and the PR body |
| 16 | The review: the option lines are blocks of 80 to 150 words, and "frame", "composite" and "surface" have loose meanings | the PR review | raised | for the PO's answers to Q0 and Q1: the brief is rewritten after them, and the names then follow one word for one thing |
| 17 | C13 changed after the refuter ran on step 6. The skill's step 8 says that the refuter re-reads sections that changed after step 6 | the skill | raised | at the close, after the PO's answers |
