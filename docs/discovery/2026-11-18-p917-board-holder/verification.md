# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · scripts/spark/bench/known_board.py:397 · refuter: holds — "hashlib.sha256(str(Path(project).resolve()).encode()).hexdigest()[:16]" · reproduced how: a grep of that file, the same line · result: reproduced · keep: not run with a board
- ★C2 · scripts/spark/records/deploy_record_store.py:100 · refuter: holds, with a pointer that does not show what `project` is — "deploy = {\"project\": facts[\"project\"], ...}" · reproduced how: the 32 deploys in the store carry folder names · result: reproduced · keep: a folder name
- ★C3 · `ls` of the store · refuter: holds — "No such file or directory" · reproduced how: the same `ls`, twice on 2026-11-18 · result: reproduced · keep: one store on one day
- ★C5 · #1298 · refuter: partly — "What no record holds today is who holds a board now and until when." · reproduced how: the card's body and comment 2 read again, and the claim reworded as the refuter wrote · result: reproduced · keep: the agreed comment was not used so far
- ★C6 · pixel-games-account.md:11 · refuter: holds — a grep of the worktree's .py and .sh files finds none of the five scripts · reproduced how: a grep of `tools/box.py` for the five script names, 0 lines · result: reproduced · keep: read in box.py only
- ★C7 · pixel-games-account.md:17 · refuter: partly — "spark/0.4.0", four design skills and no board script · reproduced how: `ls` of the plugin cache and a grep for the two stop codes, 0 files, and the claim reworded · result: reproduced · keep: an upgrade alone brings no gate
- ★C9 · pixel-games-account.md:22 · refuter: partly — "What I needed to know before a take and could not read anywhere:" · reproduced how: the account read again, and the USB serial read with `system_profiler` · result: reproduced · keep: one session on one day
- ★C12 · council/tech-lead.md:11 · refuter: holds for spark's code — board_look.py:116 "which only lists, never opens a port or runs code on a" · reproduced how: `cannot_tell` found in known_board.py:40, and the `devs` line taken from the refuter · result: reproduced · keep: some serials give cannot tell
- ★C13 · council/tech-lead.md:16 · refuter: holds — board_grant.py:54-58 "return WHY_EXPIRED if" · reproduced how: `expires_at` in board_grant.py:41, "1 to 1440" in issue_grant.py:59, and the grant file that ended 2026-10-19 · result: reproduced · keep: one ended grant in one store
- ★C14 · council/tech-lead.md:15 · refuter: partly — run_cost.py:73 "os.environ.get(\"CLAUDE_CODE_SESSION_ID\")" · reproduced how: a grep of scripts/spark for the variable and for getpass, and the claim reworded · result: reproduced · keep: session ids not compared
- ★C15 · council/tech-lead.md:38 · refuter: partly — reach_board.py:30 "the firmware is stop" · reproduced how: flasher.py:51 `--after watchdog-reset` only, and the claim reworded · result: not reproduced · keep: read in the code, not measured
- ★C17 · council/po-assistant.md:24 · refuter: partly — "Nobody is blocked now: the agreement of 15:43 works by messages and a card comment" · reproduced how: `tools/board.py status`, where P892 waits on the PO · result: reproduced · keep: the agreement was never used
- ★C24 · council/refuter.md:39 · refuter: holds — its own finding, "USB Serial Number" = "348518xxxxxx0000" · reproduced how: `system_profiler SPUSBDataType` and the board record read with Python: 14 deploys, 5 names, 2026-11-01 to 2026-11-17 · result: reproduced · keep: only the PO knows whether it is the game box <!-- REQUIRED:claims -->

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: the three lenses and the refuter say that a record binds only a tool that reads it, and that `box.py` reads nothing of spark's today
- Agree: the tech lead and the refuter say that a view with no touch is possible from the USB list and the store's records
- Split: the riskiest assumption. The facilitator named A2, the PO assistant A1 and the refuter A6. The brief now proposes A6 · Q1
- Split: the holder's key. The tech lead and the facilitator name the resolved folder, and the refuter shows that worktrees then split one project · Q4
- Split: on another holder's board. The PO assistant says that a tool only says so, and the tech lead shows where a stop fits · Q5
- Split: a session's identity. The tech lead found no reader of a session in the board tools, and the refuter found the variable set in a child process · the collection plan
- Split: slice 0. The refuter's rival says that the view alone is a chore and needs no discovery · Q3 <!-- REQUIRED:agree-split -->
