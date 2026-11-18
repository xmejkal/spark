# Lens: the user's journey (P917)

Read 2026-11-18. Personas: (a) the PO at his bench; (b) a Claude session on one project. Nothing was run on a board. `ls /dev/cu.*` showed one `usbmodem` port, so one board on USB now.

## Findings

Scenario walks first, then the findings that carry them. A step reads "persona types or reads -> what the tool prints".

### Walk 1: a session in project A deploys to the board that project B used last
1. A's session runs `look.py` in A. It prints the board's last deploy, taken from the board's record in the store, and a token. -> `look.py --help` says it restarts the board while esptool reads it. Nothing in the print says another project holds the board now.
2. A's session runs `deploy.py --token ...`. P892's gate asks the board question against A's own kept board only. -> If A kept the same board, it asks nothing and goes on to erase (comment 2 on #1298).
3. The erase and the write run. B's firmware is gone, and B's running program stopped at step 1 already.
Stall or harm: no step shows B's hold. The only warning is a message to the other session (jobs-and-journeys "Today they", J2).

### Walk 2: a session asks who uses the board now and until when, touching nothing
1. The session looks for a read-only command. -> `look.py` touches the board (restarts it). `grant.py`, `reach.py`, `live.py` and `deploy.py` all ask the board question and then read or run on the board. No spark command is read-only on the board and names a holder.
2. The remaining read is the card: `gh issue view <card> --comments` for a "I take the board ... until ..." line. -> On #1298 that count is 0, and I found no take line in the #1283 comments (see USER-6).
Stall: the session cannot answer with what it can type. It must message the other session and wait. Silence is not a yes (agreement item 2).

### Walk 3: a session gives the board back and the next user needs it as it was
1. The holder writes "The board is free" (agreement item 3). -> Nothing records what was on the board before the take.
2. The next user reads "free". -> It does not say which firmware, which lineup, or whether the PO's game was running. The pixel-games session named these as unreadable before a take (brief C9).
3. The next user runs `look.py` to learn the board. -> It prints the last deploy of spark's record. A hand copy by `box.py deploy` leaves none (see USER-4).
Harm: the box keeps a test lineup after step 2c (brief C10). The next user plays or deploys on it without knowing.

### Walk 4: the PO sits down while a session holds the board
1. The PO says it in the chat. The holder stops at its next safe point and writes "The board is free" (agreement item 5). -> The PO's first words go to one session. He must know which one holds. Only the card comment says so.
2. A second session, with no message from the PO, may still run `live.py` inside its grant. -> A grant allows it for N minutes (`grant.py --help`) and holds no session. So the PO's presence stops nothing a tool checks.
Harm: a running `exec`, or `look.py`'s restart, can interrupt the PO's game or his hands on the board (J4).

### Walk 5: a session stopped (crash or /clear) with no release
1. The next session starts. -> It has no memory of the take. The agreement says "A session that restarts reads the card comment" (agreement item 4), so it has to know which card.
2. It reads a take line with an end time, or none. -> Nothing in the store ends the hold. A hold ends by its stated time "by itself" only in the sense that a reader compares the clock. Nothing enforces it.
3. A grant that outlives the session is the one thing the store records. -> The store's `grants/` holds one deploy grant that ended 2026-10-19T09:50:37+02:00 and is still a file there. So the store keeps ended records.
Stall: no tool tells a restarted session that the hold is its own, someone else's or dead.

### Findings table

| id | claim | tag | pointer | supports only |
| --- | --- | --- | --- | --- |
| USER-1 | No spark command reads the holder without touching the board. `look.py` restarts the board while it reads. `grant.py`, `reach.py`, `live.py` and `deploy.py` read or run on it after the question. | E | `look.py --help`: "The board restarts while esptool reads it: a running program stops"; `grant.py --help`: "reads the board on USB once with esptool (the board restarts)"; read 2026-11-18 | that J2 has no free read today; not how often it hurts |
| USER-2 | P892's gate compares the board on USB with the record of the project the script runs in, and no other project's. With one board kept by two projects the gate asks nothing in either. | E | comment 2 on #1298, read 2026-11-18, `KnownBoardService` in `scripts/spark/bench/known_board.py`; the code read by the facilitator, not run by me | what the code does; not that two projects keep one board today |
| USER-3 | The store holds no hold record. The only record of a use is a deploy record (per MAC, with `project`, `image_sha256`, `deployed`, `yes`) and a grant (MAC, token, `granted_by`, `granted_at`, `expires_at`, `scope`). Neither names a session. | E | brief C2, C5; `grants/` file read 2026-11-18 (keys listed) | that a hold must be a new record or a new field; not which |
| USER-4 | A deploy made with the pixel-games project's own `tools/box.py` (mpremote copy, hard reset) leaves no spark deploy record, so "which project was put on the board last" is wrong or missing for the game box. | E | `box.py` docstring in the pixel-games worktree (copies with mpremote, writes `:lineup.py`, hard-resets; it does not call spark); brief C4, C6 | what `box.py` does by its own text; not what the PO's store would show after step 2c |
| USER-5 | `box.py` picks "the first USB serial port, sorted", so with two boards on USB it can reach the wrong one. A holder record that names a port would not stop it. | E | `box.py` docstring, `log:` paragraph; brief C8 | that a record cannot protect a tool that does not read it (scope names `box.py` reading it through one spark command) |
| USER-6 | The agreed take line has no use in the one card that was to use the board. I found no take line in #1283's comments, and #1298's comments hold none (0 matches for "I take"). | E | `gh issue view 1283 --comments` and `gh issue view 1298 --comments`, grep, read 2026-11-18 | that the take line is not used yet (step 2c has not run); not that it will fail |
| USER-7 | A hold's end time is chosen by the holder before it knows the work. The pixel-games session estimates 60 to 90 minutes with about 5 deploys and 5 to 10 console reads. | E | brief C11, an estimate | that an end time is a guess; —(how long a hold really runs) |
| USER-8 | A session knows its project folder (every script takes `--project`, default "here"), but not a board name, a port, or its own session id. The port comes from `look.py` or `ls`. The board's MAC is printed by `look.py`. A session has no id the tools read. | E (project) / H (no session id, from the tools' flags: none takes one) | `deploy.py --help`, `look.py --help`, `grant.py --help`, `reach.py --help`, `live.py --help` | who can write a hold (a project, not a session); not that a session id is impossible |
| USER-9 | A session cannot supply the PO's yes or his presence. The yes is typed in his terminal; a pipe, a heredoc or Claude Code's `!` is no terminal. The PO's arrival at the bench is known to nobody but him. | E | `grant.py --help` ("A pipe, a heredoc or Claude Code's ! is no terminal") | that J4 needs the PO to say it or a mark of his own; not how |
| USER-10 | Ended records stay in the store. The grant for one board ended 2026-10-19 and the file is still there. A reader must compare `expires_at` to the clock each time. | E | the store's `grants/` listing and the file's `expires_at`, read 2026-11-18 | that a stale hold would stay too unless a reader checks the time; not that it harms |
| USER-11 | A hold keyed by project folder name (as `deploy` records now key `project`) can collide when two folders share a name. | E | brief C2 caveat; comment 2 on #1298 ("Not checked: whether `project` there is the folder's name or its whole path") | that the key matters; not which key |
| USER-12 | The agreement relies on silence being no yes and on messages between two sessions. A third session or a session that never saw the messages has no way to know the agreement. The PO's restart rule is "one topic per session; restart near 100k of context", so stops without a release will happen. | E (rule) / H (frequency) | project `CLAUDE.local.md`, "Start of a session"; agreement items 2 and 4 on #1298 | that a /clear happens by the PO's own rule; how often a hold is open at that time is — |
| USER-13 | `reach.py` is "the PO's bench tool", and `live.py` is Claude's. So the PO himself touches the board with a tool that runs a line and restarts it. The PO is not a session, and he is a holder in J4. | E | `reach.py --help`: "It is the PO's bench tool for P251" | that the PO is a holder who needs a way to take, not only to override |

## What you could not check, and why
- That the board is held now: I touched no board and read no hold, so nothing says it is held. `ls /dev/cu.*` lists one `usbmodem` port only.
- What `look.py`, `deploy.py` and the rest print for the walks: I ran only `--help`. The printed lines in the walks are from the help text and the brief, not from a run. The bench check of #1266 is the PO's and was not done when I read it (the card is in Review and waits on his bench).
- Whether two projects keep the same board: I did not read `known-boards/`; brief C3 says there is none in the store. The code claim in comment 2 on #1298 I did not re-read.
- Whether a /clear or a crash ever left a hold: no dated record in what I read shows one. There is no real use of a hold yet.
- The pixel-games `bench.md` and `docs/overview.md` on this subject: I grepped them. They hold bench logs of other cards and say nothing of a second user of the board. The agreement and the take line are on the cards only.
- `box.py`'s lines after line 80: I read only the docstring and the constants.
- The session-id question: I read no Claude Code internal. Whether a session can read its own id is —.

## Questions for the decider

Each is a past-tense account question about his own use (answer = E, account, n = 1).

1. When did you last find, on the bench, that a session had touched the board while you wanted it, or that the board did not hold what you left? What happened, and what did you do? · decides whether J4 is a felt friction or only a plan (USER-4, USER-9, walk 4)
2. Since 2026-11-18 15:43, the day of the agreement, did you have to ask one session whether the other was done with the board? How long did you wait, and what did you do meanwhile? · decides whether a read without a message (J2) is worth building
3. Before today, did you ever deploy firmware from one project onto a board and then find the firmware of another project there, or lose a game's lineup on the box? When, and what did it cost? · decides whether J1 and J3 happened or are a fear (USER-2, USER-4)
4. The last time a session stopped (a /clear, a crash, the 100k restart) while it used the board, what did the next session do? Did you tell it, or did it read the card? · decides what a hold must hold for a restarted session (walk 5, USER-12)
5. When did you last type "free" or "I take" yourself, or decide an end time? How long did the hold really last compared with what was said? · decides whether the end time is a field, a default or a renewal (USER-7)
6. When you used the board yourself in the last weeks (`reach.py`, a grant, a flash), did you tell a session first? How? · decides whether the PO is a holder who takes, or only an override (USER-13)
7. Have you had two boards on USB at once since P892, and which tool said which board? · decides whether the port in a hold matters (USER-5)
8. When you read a list of past deploys (`look.py`'s last deploy) did it tell you what you wanted to know about the box, even though `box.py` leaves no record? · decides whether the record needs the pixel-games tool to write it (USER-4)

## Searches
none
