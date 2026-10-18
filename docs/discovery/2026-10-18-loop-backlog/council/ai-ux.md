# AI-UX lens: what Claude reads, calls and hands over in one loop

Opus, 2026-10-18. Read from the worktree at 4ebb59d, with no USB and no store writes.
> **TL;DR.** For one loop ("a thing that beeps when I press a button" through a second deploy), Claude follows 5
> command pages and calls 11 scripts. 5 of the 11 answer only in text, and the person copies something by hand up to
> 5 times. Do not add a `/spark:loop` page. Put `--json` on the text-only scripts, then let one script answer "where
> is this project, and what is the next step", then add `/spark:deploy`. The page edit should land in the project file
> itself, so Claude learns about it from a file and not from a paste.

## Claims and evidence

1. **The chain, counted.** The command pages are `init`, `setup`, `idea`, `research` and `build` (build holds simulate
   and deploy, build.md:210, :280). The scripts are `init_project`, `tools`, `parts` (about 12 ops: `--step`,
   `--needs-set`, `--match`, `--pick`, `--requirements`, `--need`, `--kept`, `--keep`, `--skeleton`, `--read`,
   `--validate`, `--tally`; idea.md:3, research.md:3), `check_spine`, `import_firmware`, `check_all`, `run_scenario`,
   `look`, `deploy`, `grant --check` and `live`. That is 11 scripts. No page writes the firmware or the scenario: Claude
   writes both from build.md:240-266. gaps.md says "seven command pages and scripts". That figure counts the steps,
   not the calls.
2. **5 of the 11 are text only.** agents.md:428 lists `deploy.py`, `look.py`, `run_scenario.py`, `init_project.py` and
   `tools.py` as taking no `--json`. A grep for `"--json"` in look, deploy, run_scenario and flash_image found 0 each.
   So Claude parses from text: look's token and stop line (agents.md: "the stop line or the token line tells them
   apart"); deploy's `no terminal`, `yes: standing yes`, `ready seen`, `ready unknown`; run_scenario's verdict
   (run_scenario.py:255).
3. **The deploy JSON is unblocked.** P213 PR a waited for `DeployService` (i192.txt). `DeployService` is now on main
   (deploy.py:37, scripts/deploy_service.py, merge 4393121), and `outcomes.envelope` exists (outcomes.py:68).
   `commands/deploy.md` does not exist.
4. **The person copies or acts by hand at:** (a) the Wokwi token, read only from the env var `WOKWI_CLI_TOKEN`
   (run_scenario.py:248-251), so it reaches Claude's shell only through the person's profile, and setup does not walk
   them through it; (b) the deploy grant line, pasted into their terminal (build.md:315); (c) the live grant line
   (agents.md, `grant.py --check`); (d) a typed `yes` with no grant (deploy_gate.py:21, :68 need a tty);
   (e) `breadboard.json`, pasted into wokwi.com and back after a move (journey.md:447, build.md:82); (f) the R press
   (build.md:320), which needs hands and stays. Not a copy: Claude passes look's token to deploy itself; with JSON it
   stops scraping it.
5. **The serial read after a deploy is half built.** `ConsoleProbe.console()` already reads the port for `READ_S = 2`
   seconds, with DTR and RTS off (board_console.py:20, :100). deploy and the doctor use it, but no CLI exposes it.
   P248 #270 asks for "a read of N seconds".
6. **The `next` slot is there but empty.** The `parts.py` envelope has `next`, and "no operation fills it" (agents.md,
   the envelope notes).

## Judgement: one entry point?

A `/spark:loop` page would repeat the other pages' logic in a prompt. AGENTS.md rules that out: "An agent prompt never
repeats its logic". Better is a fact answer from one script: `loop_status.py --project . --json`. For each stage it
gives `done`, `stale` or `missing`, read from files that already exist: the needs, `requirements.json`, the age of
`dist/` against the requirements and `breadboard.json`, whether the firmware imports, a passed log for the current
image, the last deploy record. It also gives the one next command, in the envelope's `next`. That is a fact, not behaviour, so it fits "spark exports
facts". The command pages stay as they are. The person can ask "where am I?", and Claude answers from the same JSON.
Do it after the JSON for look, deploy and run_scenario, because it reads their records.

## How Claude learns about a page edit (P293 story 2) with no copy

- The page saves straight into `<project>/breadboard.json`, through a small local server Claude Code starts or
  Chrome's file-system access. The keep logic of P273/P287 reads the file as today.
- Claude learns of it when the person says "done" (then `check_spine --keep --json`, whose `kept` names each move), or
  from `loop_status`: `breadboard.json newer than dist/`. A Monitor file watcher is later. A saved download (p294.md
  option a) brings the paste back: fallback only.

## How Claude reads the serial after a deploy (P248)

First, `deploy --json` carries the board log it already writes under `sim/runs/board/` as `data.console`: no new tool.
Then `console.py --seconds N --json`, a thin CLI over `ConsoleProbe` with N capped, which says first that opening the
port can restart the board. It writes no flash; whether it needs a live grant is the PO's question.

## Proposed slices, in order

| # | id | title | done when | interface | size |
|---|---|---|---|---|---|
| 1 | P213 a #192 | look and deploy `--json` | the token, stops, `needs_yes`, `ready` and `data.console` are in the envelope, and agents.md lists both scripts | Claude | M |
| 2 | NEW | run_scenario `--json` | the verdict, log path and missing token are codes, not text | Claude | S |
| 3 | NEW | Wokwi token, set once | setup asks for it in the person's terminal (getpass) and keeps it in the store with mode 0600. run_scenario reads it when the env var is unset, and the token is never in chat | both | S |
| 4 | P213 b #192 | `/spark:deploy` | one page runs look, the gate and the flash, then a redeploy after a change, and build.md points to it | both | S |
| 5 | P248 #270 | bounded console read | Claude reads 5 s after a deploy on the XIAO, and the answer keeps the ROM line | Claude | S |
| 6 | NEW | loop status with `next` | in a fixture project, each stage reads done, stale or missing, and `next` names the right command after each change | both | M |
| 7 | P293 s2 | page saves into the project | a drag on the local page changes `breadboard.json` with no paste, and `--keep --json` names the move | both | M |
| 8 | NEW | one grant line for a session | the PO decides whether one typed line may cover deploy and live, with the line put on the clipboard | person | S |

## Drop or park

Park a `/spark:loop` page (prompt logic, see above), a deployer agent (#192 decided), and the Monitor watcher until
story 2 works.

## Vision after the MVP: is an Artifact the AI-first surface?

Partly. **Known:** a private Artifact renders spark's `page.html`. The PO saw it on 2026-10-17 and said "it shows well"
  (#308, PR #341). Claude republishes it to the same URL after each build, so the person watches Claude's change land.
  That is the AI-first view the PO describes.
- **Unverified:** whether the person's drag can flow back through Artifact runtime capabilities or ArtifactData shared
  state on this account (p294.md:63-64 says unknown). An Artifact also lives on claude.ai. It cannot reach USB or the
  project folder, so Claude must sync its state into `breadboard.json`.
- **A local page plus a server that Claude Code writes to** reaches the files and the board. It works only on this
  machine, and it is the natural shell for a later Electron or TypeScript app.
- **What keeps both open:** the layout lives in one JSON file (`breadboard.json`); the page is one self-contained
  TypeScript bundle that reads and writes it through one small adapter (file, local server, or Artifact state); spark's
  core never knows which surface ran. Build the local adapter first, then spike one private Artifact with shared state.

## Risks

- A token in the store is readable by any agent with store access, as the PO accepted for grants; name it in slice 3.
- `loop_status` rots if a record changes: pin it with a fixture test. A local server is a new process: bind it to
  localhost, and let Claude start and stop it where the person sees it.
