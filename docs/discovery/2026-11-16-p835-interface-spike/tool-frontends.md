# P835 part 2: original frontends or spark's own (research, 2026-11-16)

Tags: D a source says it directly; E tried read-only; H inference.

## 0. Claude Artifact runtime: what a page may load

- D: Scripts load only inline or from cdnjs, cdn.jsdelivr.net/npm, unpkg.com (and a few others); everything else is blocked silently. Source: claude-artifacts `guide` topic pages, read 2026-11-16. Caveat: the list may change.
- D: fetch, XMLHttpRequest and WebSocket to other hosts are blocked. Same source. Caveat: none.
- D: Iframes, <object> and <embed> of other sites are refused. Same source. So a wokwi.com iframe cannot run in the page.
- D: Images only as data: or blob: URIs; a remote image does not load. Same source.
- D: A plain <a href> to another site works; the viewer opens it outside the page. Same source.
- D: Web Workers from the page's own files or blob: URLs work; a page can be up to 16 MiB; a page published from files may load its own files by relative path. Same source.
- H: A bundled viewer (one inline script, or a script from jsdelivr/unpkg) can run in an artifact if it needs no network at run time. A CDN script breaks D7 ("loads nothing from the web") and the from-disk-offline case; inlining it keeps both.

Note: P294 (docs/discovery/2026-10-18-p294-wokwi-reuse/finding.md, 2026-10-18) already answered most Wokwi questions; it
left "does the Artifact frame allow a wokwi.com iframe" and "does an Artifact run a CDN module" unknown. The first is now
answered (refused, section 0). This part rechecks and adds the 2025 embed.

## 1. Wokwi

- D: wokwi-embed-example (pushed 2025-11-20) puts `<iframe src="https://wokwi.com/experimental/embed?client_id=...">` in the host page; the host sends diagram.json and code into it over a MessagePort (`client.fileUpload('diagram.json', ...)`, then `simStart`). Source: https://github.com/wokwi/wokwi-embed-example index.html and script.js, read 2026-11-16. Caveat: README says "Not officialy supported at this time"; needs a client_id Wokwi issues; no README licence (script.js carries an MIT SPDX line).
- D: So a local diagram.json can reach the embed without a saved project, but it is still sent to a wokwi.com frame; it is not "shown without uploading". Same source. Caveat: whether the ESP32 sim then runs in the browser or on Wokwi's server is not said (H: firmware build and part of the run are Wokwi-hosted).
- D: The older route `wokwi.com/_alpha/wembed/<project-id>` uses a saved project as a template; "early prototype ... subject to change", "may also impose limits". Source: https://github.com/wokwi/wokwi-embed-bridge-example, read 2026-11-16.
- D: An Artifact refuses iframes of other sites (section 0). So no Wokwi embed in the published page, by either route. Caveat: a local page.html opened from disk could hold the iframe, but then it needs the network, a client_id and an unsupported API.
- D: @wokwi/elements 1.9.2 is MIT, web components for single parts (lit 3), "only provide the presentation"; no simulation, no whole-diagram renderer. Sources: https://github.com/wokwi/wokwi-elements README; `npm view @wokwi/elements` (E, 2026-11-16: MIT, unpacked 2.2 MB; P294 measured the +esm bundle at 422 KB). Caveat: no breadboard, no diode, no XIAO ESP32-C6 (P294's count).
- D: Free (Community) plan: unlimited browser simulations, public projects only; Hobby+ (8.1 EUR/mo) adds Wokwi for VS Code; Pro (20 EUR/seat/mo) adds the offline VS Code plug-in and 2000 CI minutes. Source: https://wokwi.com/pricing, read 2026-11-16. Caveat: pricing pages change; docs say the free plan has 50 CI minutes per rolling 30 days, 5 min per session (https://docs.wokwi.com/wokwi-ci/getting-started).
- H: Opening the project in wokwi.com means the person pastes or uploads diagram.json and makes it a PUBLIC project on the free plan: a privacy cost the page must say before the link. Caveat: no deep link that carries a diagram in the URL was found (none searched past one search).
- H: For the page, Wokwi gives two usable things: the diagram.json format (already reused) and @wokwi/elements as part pictures (inline them, a few hundred KB). The simulator itself stays wokwi-cli in the terminal (MVP: simulate has no offer).

## 2. tscircuit

- E: spark ALREADY shows tscircuit's own drawing: the schematic and PCB tabs are `tsci export -f schematic-svg|pcb-svg` output (tscircuit's circuit-to-svg), inlined as SVG. Source: scripts/spark/breadboard/tabbed_page.py:39-63, scripts/spark/build/kept_files.py:267-268, read 2026-11-16. Caveat: static pictures, no pan, zoom or net highlight.
- D: tscircuit documents no non-React way to show Circuit JSON ("Displaying Circuit JSON without React" is a placeholder asking for upvotes); the route is `<CircuitJsonPreview circuitJson=...>` from @tscircuit/runframe in a React app. Source: https://docs.tscircuit.com/guides/running-tscircuit/displaying-circuit-json-on-a-webpage, read 2026-11-16. Caveat: docs page may lag the packages.
- E: Licences MIT for pcb-viewer, schematic-viewer, 3d-viewer, runframe (GitHub licence API); circuit-to-svg's npm field says ISC. Sizes (npm/jsdelivr, 2026-11-16): pcb-viewer 1.11.452 dist/index.js 1.3 MB plus React peers; schematic-viewer 2.0.110 dist/index.js 172 KB plus circuit-to-svg and Radix; 3d-viewer 0.0.652 pulls three.js and jscad; runframe 0.0.3256 ships dist/standalone-preview.min.js at 34 MB. Caveat: unbundled sizes; a real bundle of pcb+schematic viewer only is not measured (H: 1.5 to 3 MB minified).
- E: runframe's standalone bundle names tscircuit hosts: registry-api, api, modelcdn (3D models), kicad-mod-cache, jlcsearch, hd-cache, jscdn, postpig (grep of the 34 MB file, 2026-11-16). Caveat: names in the bundle, not calls observed; which views call which host is not traced. H: the 3D view needs modelcdn for part models, so 3D is not offline and is blocked in an Artifact (fetch to other hosts refused).
- D: 34 MB is over the Artifact's 16 MiB page cap and the 20 MiB per-file cap of publish_files. Sources: guide topic pages; publish_files description. Caveat: loading it from cdn.jsdelivr.net/npm/ is allowed by the CSP but breaks D7 and the from-disk-offline case.
- D: Link out: docs suggest "upload your Circuit JSON to circuitjson.com for a quick preview"; tscircuit.com shows a board only after `tsci push` to its public registry. Source: same docs page. Caveat: whether circuitjson.com keeps or sends the file is not documented (not checked); either way it sends the person's project to a third party.
- H: The viewers would add pan, zoom, hover and net highlight; the drawing is the same circuit-to-svg family spark inlines today. A bundled pcb-viewer plus schematic-viewer (bun, like tools/circuit-to-wokwi) could run offline and in an Artifact if inlined, at a few MB and with React; that is upkeep on fast-moving 0.0.x packages (runframe is at 0.0.3256).

## 3. KiCad

- D: KiCanvas is "an interactive, browser-based viewer for KiCad schematics and boards", "early alpha", vanilla TypeScript on Canvas and WebGL; KiCad 6 and later files only. Source: https://github.com/theacodes/kicanvas README, read 2026-11-16 (last push 2026-04-28). Caveat: one maintainer; alpha for over three years.
- D: Licence MIT, (c) 2022 Alethea Katherine Flowers. Source: LICENSE.md in the repo (GitHub's API reports NOASSERTION because the file also lists third-party notices). Caveat: the bundle carries third-party notices that must travel with it.
- D: Embedding: one bundled `kicanvas.js` ("download the bundled kicanvas.js, copy it into your project"), then `<kicanvas-embed controls="basic">`; `<kicanvas-source>` takes the KiCad text INLINE, so no fetch is needed. Source: docs/docs/embedding.md in the repo, read 2026-11-16. Caveat: "proposed API with an incomplete implementation"; inline sources are documented with a schematic example only, not tried with a .kicad_pcb.
- E: kicanvas.js is 477,451 bytes (HTTP HEAD on https://kicanvas.org/kicanvas/kicanvas.js, last-modified 2026-04-28). Caveat: not opened in an Artifact; WebGL inside the sandboxed frame is not tried.
- E: spark gets KiCad files without KiCad: `tsci export -f kicad_sch|kicad_pcb` (tsci export --help, 2026-11-16); KiCad itself is used only for `kicad-cli pcb drc` (docs/guide/agents.md:173-174). Caveat: the export's fidelity is not checked here.
- H: KiCanvas would show the same board tscircuit's SVG already shows, drawn a second way. Showing it while KiCad stays optional adds an export step, a 0.5 MB viewer and a second picture that can disagree, for no new fact. Worth it only in the PCB/order phase, where a person checks the file a fab or KiCad will read. Not in the MVP.
- H: Link out: kicanvas.org opens files from GitHub or a drop; a drop into the browser keeps the file local (H, not checked). Simpler: tell the person to open board.kicad_pcb in KiCad if they have it.

## 4. Embed, link or redraw: per tool

| Tool | Embed in the Artifact | Works from disk, offline | Privacy | Licence | Size | Upkeep | Verdict |
|---|---|---|---|---|---|---|---|
| Wokwi simulator / editor | No: iframes of other sites refused (D) | No: needs wokwi.com and a client_id (D) | Sends diagram and code to wokwi.com; free plan projects are public (D) | Closed service; embed "not officially supported" (D) | n/a | High: experimental API | Link out only, with a "this makes it public" line; simulate stays wokwi-cli in the terminal |
| @wokwi/elements (part pictures) | Yes if inlined (H) | Yes if inlined (H) | Nothing leaves (H) | MIT (D) | ~422 KB bundle (P294) | Low to medium | Optional later: part pictures inside spark's own breadboard SVG; not needed for P828 |
| tscircuit viewers (pcb, schematic, runframe) | Only a self-bundled pcb/schematic viewer, inlined; runframe's 34 MB bundle is over the cap (D, E) | 2D views probably yes; 3D needs modelcdn (H) | runframe bundle names tscircuit APIs (E) | MIT (D) | 1.5 to 3 MB plus React (H) | High: 0.0.x packages, React | Keep today's tsci-exported SVG (already tscircuit's own drawing); add pan and zoom with a few lines of spark's script if needed; viewer bundle only with the PCB/3D views, after the MVP |
| tscircuit.com / circuitjson.com | No (link only) | No | Upload to a third party (D) | n/a | n/a | Low | No link in the MVP |
| KiCanvas (KiCad files) | Yes if inlined, WebGL untried (H) | Yes, inline source (D) | Nothing leaves (D) | MIT (D) | 477 KB (E) | Medium: alpha | Not in the MVP; maybe in the PCB/order phase |
| spark's own SVG (breadboard) | Yes (today) | Yes (today) | Nothing leaves | spark's MIT | small | spark's own | Keep; it is the only breadboard view any tool offers spark (no Wokwi breadboard element) |

## 5. Recommendation and effect on the MVP cards

- H: Redraw nothing new and embed nothing in the MVP. The page already shows the tools' own pictures where they exist (tscircuit's schematic and PCB SVG from `tsci export`) and spark's own breadboard SVG where no tool has one.
- H: Link out to Wokwi only, and only with a line saying the free plan makes the project public; the simulate phase keeps its terminal line (MVP: no offer).
- H: Any later bundle (tscircuit pcb/schematic viewer, KiCanvas, @wokwi/elements) must be inlined to keep D7 and the from-disk case; spark is public and commits no vendor file, so the bundle is fetched into the store at setup or build time (a free download), not committed. That also breaks tools/flow-page's "no dependencies" rule, so it is its own card after the MVP.
- H: P827 (#1185): no change; add one acceptance line: the page loads no iframe (the runtime refuses one) and no outside script (D7; the runtime allows a few CDNs). P828 (#1186): no change to scope; the views stay the inlined SVGs; pan and zoom, if wanted, is spark's own few lines in tools/flow-page, not a viewer library.
- H: After the MVP, one card each: "PCB and 3D views with tscircuit's viewers, bundled offline" (tied to the existing PCB/3D after-MVP line) and "Open in Wokwi" with the public-project warning.
