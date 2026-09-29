---
description: Set up a project for spark — writes the rules and brief files every check and reviewer needs, with nothing guessed.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/boards.py *)
---

# spark:init

Create what the checks need before any of them can run.

## 1. Which board

```
${CLAUDE_PLUGIN_ROOT}/scripts/boards.py --list
```

If the user has already said which board, use it. If not, show them the list and ask — do not
pick one. The board decides every pin capability downstream, so guessing it wrongly makes every
later check confidently wrong rather than silent.

If their board is not listed, `boards/README.md` in this plugin has the schema, and a project's
own `boards/<id>.json` beats the library.

## 2. Initialise

```
${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py --project . --board <id>
```

It writes `.spark/rules.json`, `.spark/project.json`, `boards/active.json` and a `package.json`
naming tscircuit's cli (so `npm install && npx tsci build` works in the project; without the file
tsci climbs to your home folder looking for a root — never rewritten once you add to it), and names the
rails from the built design if there is one. Existing files are left alone unless `--force`.

## 3. Read what it could not answer

It ends with every field left `null`. **That list is the output, not a shortfall.** Nothing here
is guessed, because a guessed rail current would poison the one check that does arithmetic — and
a check reading a null reports it as unverifiable rather than passing it, which is the correct
answer until somebody measures it.

Go through the list with the user. Two kinds of field:

- **Decisions they can make now.** `i2c_hz` is whatever the firmware configures. `nominal_volts`
  is what the supply is. `capacitor_chemistry` is what is on the board. Fill these in together.
- **Numbers somebody has to measure.** `max_current_a` on a motor rail is a stall current, and
  that needs a meter. Leave it null and say so. That is the state the tool is designed to carry.

Fill in `project.json`'s `must` list in terms that can be violated — "runs a year on one charge"
can be checked against a current budget, "low power" cannot. The reviewers judge every finding's
consequence against it, so a vague brief makes a vague review.

## 4. Confirm it works

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py --project .
```

Read the resolution block it prints first. Anything `not found` is a check that will be skipped,
and it says where it looked.
