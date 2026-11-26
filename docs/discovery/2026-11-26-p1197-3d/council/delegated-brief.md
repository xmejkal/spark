# P1197: the delegated brief for Q9 and Q13 to Q18

The PO delegated these seven technical choices on 2026-11-26 (D12 in brief.md): "delegate all seven to the council of
tech lead, architect and PO assistant, each recorded as delegated and his to change". Three seats answer this one brief
on their own: the tech lead, the architect and the PO assistant. The facilitator acts on the majority per question and
records each answer as delegated, the PO's to change.

What he already decided (brief.md, Decisions): the frame (D1). His Fusion licence is Personal (D2). He drew his last
case in Fusion (D3). He prints on a Prusa (D4, the MK3S to confirm). The first slice: the two tests first, then a box
body per module with a STEP export (#1729 and #1727, extended), then the case Operation (D5). Yes to both tests, and he
has callipers (D6). His modules sit in sockets (D7). Both case paths, with spark's own case Operation built only if the
test print fits (D8). A3, that his Fusion opens spark's STEP with each part named at real size, is the one high belief,
and T1's pass line stands (D9). A plain STEP export goes first, before the catalogue editor (D10). This epic writes only
the height facts it needs, and P735 #1010 writes the rest (D11).

The standing rules: one seam per strategy, chosen by a setting, behind an Operation, thin interfaces, nothing twice.
Every configurable choice names its setting, default and layer (P1194). Records grow by need, each fact with its
source. A null is not a value to fill in (AGENTS.md). Never commit a vendor file. Free, few, local, a CLI first.

The seven questions, each with its options as the brief holds them:

- Q13 the body's form and source · (a) one neutral body Value (boxes in mm from the record's numbers) that each engine's writer turns into its own form. The tscircuit writer writes a JSCAD plan · S · that the body shows in the 3D tab, the GLB and the STEP under its reference, with no new tool · opinion (the architect, from TL-1 and AR-9) · E ★C21 (a probe board) (brief.md:64) · caveat: tscircuit's KiCad export drops a JSCAD body, and the JSCAD body also replaces the header body that each module shows today, in KiCad and below the board in the STEP (★C33 (one probe board)). A union of the box and the pin row was not run
- Q13 · (b) spark writes a STEP file per part, kept like a fetched one, and every engine takes a file · M: about 110 lines for boxes, more for cylinders and holes, or build123d at 62.5 MB · one form for tscircuit, KiCad and Fusion · opinion (the architecture lens, AR-8 b. The tech lead showed that it runs, TL-4) · E ★C20 (boxes only) ★C9 (to download) (brief.md:63) · caveat: a merged STEP body loses its reference in tscircuit's STEP (★C4 (Whether Fusion shows them is not run)). A file per placed part that carries the reference was not run (TL-3)
- Q13 · (c) a fetched or kept vendor STEP first · M, and a licence read per library · the real look of a part · opinion (no lens holds it for the first slice. It is his "existing solutions") · E ★C7 (never commits a vendor file) ★C8 (vendor downloads) (brief.md:51) · caveat: no library holds the dev boards. DFRobot's FireBeetle file is 25 MB and shows a camera he does not have (PA-2, US-17). The name problem of ★C4 (Whether Fusion shows them is not run) and ★C21 (a probe board) is the same under all three: test T1 below settles what Fusion shows
- Q14 the words for the z facts · (a) `above_mm` and `below_mm` · XS · that the plain word works · opinion (the architecture lens, AR-5) · H · caveat: `above` already names a kind of limit in the rules-file words (E docs/guide/words.md:11)
- Q14 · (b) `z_max_mm` and `z_min_mm`, in the shape's own frame, with z up from the board's top face · XS · that no reader can take a z fact for a plane size · opinion (the architect) · H · caveat: "z" has no other meaning in spark's code or guide today (E, a grep on 2026-11-26). A reach below the top face is a negative number, so the question to the person stays in plain words
- Q14 · (c) the industry's words: `height` means z everywhere, and the plane's second size becomes `length` · L: 30 records, `PartShape`, fixtures and goldens · the root fix for "height" · opinion (the architect names it. PHY-3 asks for "a rule that moves the existing keys") · E ★C1 (3 of 40) (brief.md:45) · caveat: a job for the names pass P382 #489, not for this epic's first slice
- Q15 where a body file lives · (a) the store's `sources/<sha256>/`, named by a `documents` entry, with a `body_file` block in the record: the document key, the maker, the likeness, the credit, an offset and a rotation · S · one home and one check for pictures and bodies · opinion (the architecture lens AR-6, and the architect) · E ★C7 (never commits a vendor file) ★C14 (brief.md:51) · caveat: the block's check is shared with the `pictures` block, never copied
- Q15 · (b) a URL in the record, fetched at export · XS · nothing new · opinion (none. It is the bin project's past practice, US-18) · E ★C22 (one run each) (brief.md:65) · caveat: the export then reaches the network, and a missing file passes in silence
- Q15 · (c) a models folder in each project · S · that a project carries its own bodies · opinion (none) · H · caveat: a CC-BY-SA or private-use file can then reach the project's git and a shared place (AR-19)
- Q16 the first member behind `CaseMaker` · (a) tscircuit's case solver, called direct with numbers from the board's mechanics, never as an element in `board.tsx` · S · a base and a lid with a lip and openings, from installed code · opinion (the tech lead TL-6, the architecture lens AR-11) · E ★C5 ★C20 (boxes only) (brief.md:49) · caveat: version 0.0.4, no release since 2026-08-19, no bosses (PA-8). Its export through `tsci` appends records that spark does not own (TL-6)
- Q16 · (b) spark's own generator on its own STEP writer · M to L · no outside solver · opinion (listed by AR-11, held by nobody for the first member) · E ★C20 (brief.md:63) · caveat: boxes only today. A boss or a round hole needs curved surfaces
- Q16 · (c) build123d · M and a 62.5 MB wheel · named solids, STEP, STL and 3MF from one tool · opinion (research.md section 4) · E ★C9 (to download) (brief.md:53) · caveat: not installed, not run. "A user installs nothing heavy" (AGENTS.md), so it waits for a need that (a) cannot meet
- Q17 the print files · (a) STEP straight into PrusaSlicer, with no STL or 3MF writer · none · that the print path needs no new export · opinion (the PO assistant, PA-6) · E ★C24 (is not used) (brief.md:67) · caveat: read from search results, not run. The case needs its own file, or the board lands on the print plate too
- Q17 · (b) STL written by spark from the case's plan · S: about 30 lines · a file that every slicer takes · opinion (the tech lead, TL-7) · E ★C20 (boxes only) (brief.md:63) · caveat: 16 of 50 and 32 of 82 edges are open. Whether PrusaSlicer repairs them was not run
- Q17 · (c) 3MF through `tsci` · a toolchain bump from CLI 0.1.2113 to 0.1.2490 · that tscircuit's own print export works · opinion (none) · E ★C6 (brief.md:50) · caveat: it fails in the pinned CLI, and a bump is its own risk to every reader of `circuit.json` (PA-10)
- Q18 the order of the body card and the engine seam · (a) #1729 first: the function that writes the `<chip>` line also writes the body, from a value already resolved on the part · S · F4 fixed with no new parameter on `emit` · opinion (the architect. The P1089 council put F4 first) · E ★C2 C27 (brief.md:46) · caveat: `board_sections.py` is already tscircuit's writer, so no new tscircuit fact enters the design area. The line moves with the writer when #1728 lands
- Q18 · (b) #1728 first, so that only the tscircuit Adapter writes the body · S more, and F4 waits · the seam before its second user · opinion (the architecture lens, AR-9) · E C27 (brief.md:70) · caveat: none
- Q9 an unknown z fact · (a) refuse and ask: the null is named, the question goes on `data.open`, and the reply may be an estimate kept as unverified with its source · S · that no number is invented · opinion (the architect, from US-19 and AGENTS.md "a `null` is not a value to fill in") · E ★C25 (n = 1) (brief.md:68) · caveat: more questions to the person at the bench
- Q9 · (b) a named default that the person accepts out loud · S · a case sooner · opinion (offered by the user lens, US-26) · H · caveat: tscircuit's 6 mm default already fails on spark's boards (★C19 (calculated, not printed)) <!-- REQUIRED:options -->

Also read: brief.md (the claims, above all ★C3, ★C4, ★C19, ★C20, ★C21, ★C22 and ★C33, the regression that a JSCAD
body removes the header's own body), council/synthesis.md (the seams and the decisions), council/refuter.md, and
verification.md.

## Searches

none
