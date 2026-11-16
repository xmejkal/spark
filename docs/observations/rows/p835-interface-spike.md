# P835: the interface spike's finding: rows

Card: [P835 #1197](https://github.com/xmejkal/spark/issues/1197), a spike, PR #1199. Docs only: one refuter (Opus) on
the PR. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-16.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | finding.md misquoted ai-interface.md §8: it dropped "not before the catalog covers every operation", said a host "now has a name" when §8 already names Claude Desktop, and missed that the app's Code tab has a shell | PR refuter (Opus) | acted | §8 quoted whole; "the app's chat has no shell, but its Code tab runs Claude Code" |
| 2 | "already on the page" is untrue of the Artifact page: the tsci SVG sits in the kept page.html as an `<img>` data URI, and P828 still brings the views | PR refuter | acted | the tscircuit row says so, citing kept_files.py:267-268 |
| 3 | "the runtime blocks other scripts" contradicts the research: cdnjs, jsdelivr and unpkg are allowed; the reason is D7 | PR refuter | acted | finding.md and tool-frontends.md give D7 and the offline case as the reason |
| 4 | "no tool offers a breadboard view" is too strong: Wokwi's editor draws breadboards | PR refuter | acted | "no tool that spark can embed offers a breadboard view" |
| 5 | the answer stated flatly that the mod acts on a click, which the research marks H and untested | PR refuter | acted | the blockquote says untested and calls it a plan |
| 6 | "one db row per build stage" is H, and "under 1 s" is from the store's save, 2.7 s and 3.8 s from the page's stamp | PR refuter | acted | both said, with brief.md Results step 2 |
| 7 | the guide and describe_capabilities claims (room, the CSP, `host:`, Mermaid, `hot?.snapshot`) were not re-checked by the refuter, which had no such tool | PR refuter | rejected | dropped because the research agent read each from the runtime itself on 2026-11-16 (artifacts-and-plugin.md, tool-frontends.md section 0), tagged D with its source |
