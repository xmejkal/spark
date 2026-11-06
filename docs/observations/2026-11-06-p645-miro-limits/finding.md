# P645: Miro's daily limit, and how the team keeps Miro current within it

Spike [P645 #864](https://github.com/xmejkal/spark/issues/864), 2026-11-06. One research agent (Sonnet) read
Miro's pages and called no Miro tool. E marks a fact read on the page. H marks an inference.

## Short version

The Free plan allows 100 Miro MCP calls a day, and every call counts, reads too. So many small edits use up the day
fastest. The facts support few large writes: one SVG call per frame, at most one read-back, and a daily budget. The
REST API has its own quota, but it is not yet known whether a Free account can make the app it needs.

## The facts

| question | fact | source | E or H |
| --- | --- | --- | --- |
| MCP limit | Free 100 tool calls a day, Starter 500, Business 2,000, Enterprise 10,000. No limit per minute is given | https://developers.miro.com/docs/mcp-usage-and-daily-limits, https://miro.com/pricing/ | E |
| What counts | every call to a Miro MCP tool | the same page | E. That reads count is H |
| Reset | 00:00 UTC, which is 01:00 in Prague in winter | the same page | E for UTC. The team's stop on 2026-11-05 did not match it, so the real reset is to be recorded |
| REST API | 100,000 credits a minute per user and app. A call costs 50 to 2,000 credits by its level. No daily limit is given | https://developers.miro.com/reference/rate-limiting | E |
| REST on Free | "REST APIs and WebSDKs are included on all plans" | https://miro.com/pricing/ | E. That REST does not use the MCP count is H. A community post says a Free account could not create an app (unconfirmed) |
| REST bulk | `POST /v2/boards/{board_id}/items/bulk`, at most 20 items a request | https://developers.miro.com/reference/create-items | E |
| One SVG call per frame | the SVG tools take one SVG that can hold many shapes | the tools' own schema | H, the item capacity is not documented |
| Chrome | no documented limit. Each screenshot and click is a turn, so it is slow, fragile and costly in tokens | none | H |
| Paid plans | Starter 500 calls a day at $8 a member a month, Business 2,000 at $20, both billed yearly | https://miro.com/pricing/ | E |

## The options

| option | supported | why |
| --- | --- | --- |
| Few large writes | yes | each call costs 1 of 100, whatever it writes |
| Often but small | no | it spends the day's calls fastest |
| REST beside MCP | maybe | its own quota, but a Free app is unproven, and 20 items a bulk call suits tables and cards more than drawn frames |
| Chrome | last resort | no limit found, but slow and fragile |

## The proposed rule

1. Budget 100 calls per UTC day. Plan each day's writes before the first call, and keep about 20 calls spare.
2. Write a frame in one SVG call (`canvas_create_from_svg` or `canvas_update_from_svg`), not in many small edits. Keep a
   small patch only for a small fix.
3. Read a frame back once after its write (the PO's rule, no overlaps). Do not read boards that did not change.
4. Queue the owed updates as a list, oldest first, and write them in daily batches. A bulk catch-up never runs at once.
5. Record the time of the first call that fails and of the first that works again, so the real reset is known.
6. Use Miro for what it helps with, in the PO's words: spark's story maps, and technical explanations such as the C
   lessons. Status that GitHub already shows does not go to Miro.

## Open

- Can a Free account create a developer app and a REST token? This is the PO's account, so it is his test or his OK.
- How many shapes one SVG call holds: test it once, on the next frame that the team writes.
