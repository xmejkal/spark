# Where a project stands, for AI agents

Part of the [guide for AI agents](../agents.md). `flow.py show` says where a project stands, phase by phase
([P825](https://github.com/xmejkal/spark/issues/1183)). The phases go from the idea to the deploy. It reads the project's
files and the store, and writes nothing. `flow.py` with no verb shows too. `flow.py page` writes the same phases as a page ([below](#the-page)).

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/flow.py" show --project . --json
```

With `--json` it prints the envelope, as `parts.py` does, with `tool` `flow` and `op` `show-flow`. Its `data` holds two keys:

- `phases`: the nine phases in order, `idea`, `needs`, `parts`, `requirements`, `build`, `breadboard`, `firmware`,
  `simulate` and `deploy`. Each is `{phase, status, mark, by, says, offers}`.
- `stands_at`: the first phase that is open. It passes a phase whose `status` is `ok` or `null`. Only `ok` is a pass
  that spark judged. The deploy is never done here, so `stands_at` always names a phase.

The words of a phase:

| key | holds |
| --- | --- |
| `status` | `ok`, `problems` or `could-not-run`, a phase word, or `null`. The phase words: `not-started` (nothing done yet), `partial` (some needs have no pick, or a build skipped a stage) and `stale` (done, but requirements.json changed after it). See `null` below |
| `mark` | the glyph a page shows for the status |
| `by` | who does the phase: `you`, `claude` or `your terminal` |
| `says` | sentences for a person. A value nobody recorded reads `unknown` |
| `offers` | `{key, effect}`: a next step, and one line that says what it does. `flow.py` runs none |

A `null` status means spark does not judge the phase, and `says` tells where it stands. The idea has `null`. A
hand-written project (requirements.json and no needs) has `null` for its needs and parts. Written firmware and a
simulated image have `null`, because you judge them. Without firmware/main.py, or without an image, they are
`not-started`. A firmware line in sim/wokwi.toml that spark cannot use gives the simulate phase `problems`.

A phase that spark did not judge is never a pass, and a skipped stage is not one either
([P878](https://github.com/xmejkal/spark/issues/1246)). These phases have `null` too, and their mark is the dot, not the tick:

- A requirements file with no needs beside it. Spark compared it with nothing.
- A breadboard sheet that is current. Spark does not judge the wiring.
- A build on the board alone, whose `build` stage is skipped. No board was built, and the breadboard phase has
  nothing to wire. A rebuild skips the same stages, so `stands_at` passes both phases and the build phase has no offer.
- A build that ended `ok` and skipped only its `simulation` stage, because every part is skipped from the simulation.

A build that ended `ok` and skipped any other stage is `partial`. No build does that today. With no log in
`sim/runs/`, the simulate phase says to run a scenario. It blames an older spark only for a log that names no image.

The offer keys are `needs-drop:<need>`, `pick:<need>:<id or entry>`, `requirements` and `build`. A pick's effect says
how many the person has. If none is free, it also names the projects that hold them.

The build phase reads `.spark/build.json`. If the folder of `check_spine.py --keep` is a project, the build writes this
file and lists it under `kept`. It holds the build's `status`, its `stages`, the `requirements` file, its sha256 and the
time. The file is named relative to the project when it is inside the project, else by its whole path. If the sha256 of that file is different now, the build phase is `stale`, and the breadboard phase is `stale` too.

A phase with problems adds one item to `problems`, with the code `phase_problems`. A phase that spark cannot read adds
one item to `unchecked`, with the code `phase_could_not_run`. A build that ended in `could-not-run` does the same. The
subject of each item is the phase. The exit is 0, 1 or 2 by those items. If both kinds are there, the status is
`problems` and the exit is 1, and the phase that could not run is still under `unchecked`. Every phase answers either way. For example,
a broken `.spark/needs.json` makes the needs, parts and requirements phases `could-not-run`, and the others still answer.
A `.spark/build.json` that is not JSON, or is no build record, makes the build phase `could-not-run` with one sentence, and
the breadboard phase too when the sheet exists ([P886](https://github.com/xmejkal/spark/issues/1256)).

## The page

`flow.py page` writes `page.html` in the project ([P827](https://github.com/xmejkal/spark/issues/1185)). It reads the
same phases as `show`, so a person reads them from the disk, in a browser, with no script. It has a rail of links, one
for each phase, then one section for each phase. Each has the phase name, a mark and a status word, who does it, what it
says and its offers as plain text. A section `Wiring` follows the last phase, when the project holds a
`requirements.json` ([P828](https://github.com/xmejkal/spark/issues/1186)). It has the lines "Before you power it" first, then
the wiring steps, one connection each, which a person can follow to wire a breadboard. When the project is not built, or
was built from other requirements, the section shows no steps and says why in the refusal's own words. A failure that is not the sheet's own refusal gives one fixed sentence: run the build again. The sentence about the Breadboard picture shows only when that picture is drawn. The pictures
follow, in one section. The breadboard comes first when the project holds `breadboard.svg`. The schematic and the PCB are
files too, `dist/board/schematic.svg` and `dist/board/pcb.svg`, which the build with `--keep` writes in a project, so
`flow.py page` alone shows them. It never runs `tsci`. The full rules are in `commands/build.md`. Until a build kept them, the two pictures say why they are not drawn. In a project,
the build writes the same page with all three pictures, after it kept the simulation project. A build that did not finish
removes `page.html` in a project, and `flow.py page` writes it again. If the flow page cannot be written, the build keeps
its own result and lists one `not written` entry.

The breadboard stands in the page as inline SVG ([P949](https://github.com/xmejkal/spark/issues/1353)), so a player can
find its parts. Each jumper's group carries `data-step`, the number of its step, and each part's group carries
`data-part`, the part's id in the steps. A step that places a part has no jumper, so it has no `data-step`: the step's
part comes from the guide's own data. No key is an `id`. The page inlines the breadboard only when it is plain shapes:
it parses, has no DOCTYPE, uses only `svg`, `g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`,
`text`, `tspan` and `title`, and only attributes of geometry and colour that spark draws with, and its three keys
(`part_pictures.PLAIN_ATTRIBUTES`; no `style`, no `href`, no handler). No value may hold `url(`, `image-set`,
`javascript:`, `expression` or a backslash, read after the parse in any case. One more element may stand
([P946](https://github.com/xmejkal/spark/issues/1349)): an `image` whose one `href` is a JPEG embedded as base64
(`data:image/jpeg;base64,...`), the rule `picture_check.is_embedded_jpeg` that a kept picture of a part passed, with
only `x`, `y`, `width`, `height`, `preserveAspectRatio`, `transform` and `opacity` beside it. No element may stand
inside a `title`. Else the page shows it as an `<img>`, as
it shows the schematic and the PCB, so a script in a hand-edited `breadboard.svg` never runs, and nothing loads. The
dot on each pin is yellow when its row joins a wire or another part and gold when it is free. Under the picture a
legend names the states that the dots draw: "pad in use" and "pad free". "Pad held: do not use" shows only when a pad
is held, and spark draws none yet ([P950](https://github.com/xmejkal/spark/issues/1354)). The page takes the colours of
the wiring page that the PO chose as the model, light and dark, with the system's fonts. It still has no script and loads nothing.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/flow.py" page --project . --json
```

With `--json` it prints the envelope with `op` `write-flow-page`. Its `data` holds `file` (`page.html`, relative to the
project), `did` (`wrote`), `stands_at` and `phases`, each only `{phase, status}`. A page that cannot be written is one
`unchecked` item with the code `page_not_written`, and the exit is 2. A phase that holds problems does not change this
status. Read it with `show`.

For an agent or a later script, the page has hooks. Each rail entry and each section has `data-phase` (the phase name) and
`data-status` (the flow's code, or `none` for no status). The `<body>` has `data-stands-at` (the first open phase, or `none`
when no phase is open). All the pictures stand together in the section `id="pictures"`, which the rail links to. The
wiring is in the section `id="wiring"`, which the rail links to as "Wiring". Its steps are the items of `<ol id="steps">`,
each `<li id="step-N" value="N">`, and the lines before power are a `<ul>` of their own, never inside the steps.

One at a time lives in the URL. The link "One at a time: start at step 1" goes to `#step-1`. While a step is the target of
the URL, the page shows that step alone, with its menu, the element `class="nav"`. The menu says "Step N of M" and has the
links Back, Next, All steps and Picture. Picture shows only when the breadboard picture is drawn. So the browser's Back
button walks the steps. The links "Wiring", "Pictures", "All steps" and "Picture" leave that view, and the browser's Back
returns to the step. In a
browser that does not know the CSS `:has()`, every step shows. When the page prints, every step shows. In a published
Artifact, the fragment may not survive a reload of the outer page. The page has no script and no checkbox on a step, and
it never says that the board is wired.

The words on the page:

| status | word |
| --- | --- |
| `ok` | ok |
| `problems` | problems |
| `could-not-run` | could not run |
| `not-started` | not started |
| `partial` | partly done |
| `stale` | out of date |
| `null` | not checked by spark |

The page adds no tick. A phase that is not `ok` never shows the tick, whatever mark it carries. It shows the could-not-run
mark. A code that the flow does not know shows as itself. No color says a status. The page does not know whether the board is
wired or flashed, and says so in one line. Every text on it is masked, so no path of the home folder reaches the file.

Never take an offer only because `flow.py` lists it. A pick, a drop and a build change files, so say what the effect
line says and ask the person first.
