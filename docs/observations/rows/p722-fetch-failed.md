# P722: `--fetch` says the download failed, with a code: rows

Card: [P722 #973](https://github.com/xmejkal/spark/issues/973), bug, under #94. An XS card: no plan, one refuter on the PR
(rules.md). Built in parallel with P706 (the PO, 2026-11-12: "anything we can do in parallel while this is running?"). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `fetch_documents` keeps its shape (`documents`, seven tests call it); the Operation computes the failed URLs from the plan and the kept entries, one read of the record more | build | acted | `FetchDocuments.build_answer` |
| 2 | the W6-R1 golden pinned the wrong text with exit 0; it is renamed `parts-fetch-problems-unreachable` with exit 1 and regenerated after a read | build | acted | tests/golden-records |
