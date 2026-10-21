# Area: checks

Back to [level 1](../README.md). Words are in the [glossary](../glossary.md). Names marked "proposed" do not exist
in the code yet.

## Level 2: what checks does

Checks grades a built design against facts in records: the rules, the physics, the footprints, the vendor's pin
header and the order list. Each check says what it found and what it did not look at, and `check_all` runs them all.

### Its operations

| Operation | CLI | Effects |
|---|---|---|
| `check-all` (proposed name) | `check_all.py` | reads |
| `check-physics` | `check_physics.py` | reads |
| `check-footprints` | `check_footprints.py` | reads |
| `check-bom` | `check_bom.py` | reads |
| `check-vendor-pins` | `check_vendor_pins.py` | reads, network through `gh` |
| `compare-design` | `compare_design.py` | reads |

The Operation names are proposed. Each CLI keeps its flags and positionals.

### Its components

| Module | Holds |
|---|---|
| `checks/check.py` | `Check`, `CHECKS`, `CheckedFolder`, from `check_all.py` (proposed path) |
| `checks/rules_check.py` | `RulesCheck` and `compare_design`'s logic |
| `checks/physics_check.py` | `PhysicsCheck` and `check_physics`'s logic, `CircuitBoard` |
| `checks/build_check.py` | `BuildCheck` and `check_footprints`'s logic |
| `checks/vendor_pins_check.py` | `VendorPinsCheck`, `check_vendor_pins`'s logic, `GhVendorHeaders` (proposed Adapter) |
| `checks/order_check.py` | `OrderCheck` and `check_bom`'s logic |
| `checks/codes.py` | every code a check emits, with a one-line meaning |
| `checks/operations.py` | the area's `OPERATIONS` and its index docstring |

### Its ports and adapters

| Port | Real adapter | Fake | Registry |
|---|---|---|---|
| `Check` Strategy: `run(inputs) -> OperationResult` | the five checks | a toy `Check` in the test | `CHECKS` |
| vendor headers: `header(variant) -> str` | `GhVendorHeaders` over `gh api` (`check_vendor_pins.py:67`) | a dict from variant to header text | none |

Checks depends on design (the `Design` Value and `Netlist`), records and core.

```mermaid
flowchart LR
  OPS["check-all"] --> CF["CheckedFolder: finds the inputs"]
  CF --> REG["CHECKS"]
  REG --> RC["RulesCheck"]
  REG --> PC["PhysicsCheck"]
  REG --> BC["BuildCheck"]
  REG --> VC["VendorPinsCheck"]
  REG --> OC["OrderCheck"]
  VC --> GH["GhVendorHeaders: gh"]
  RC --> DES["design: Design, Netlist"]
  PC --> DES
```

## Level 3: how checks is built

```mermaid
classDiagram
  class Check {
    <<Strategy>>
    name$
    inputs$
    codes$
    what$
    run(inputs) OperationResult
  }
  class RulesCheck
  class PhysicsCheck
  class BuildCheck
  class VendorPinsCheck
  class OrderCheck
  class CheckedFolder {
    <<Value>>
    inputs()
    ambiguous()
  }
  class CheckService {
    <<Service>>
    run(folder, names) list
  }
  class Finding {
    <<Value>>
    severity
    subject
    code
    sentence
    fix
  }
  Check <|-- RulesCheck
  Check <|-- PhysicsCheck
  Check <|-- BuildCheck
  Check <|-- VendorPinsCheck
  Check <|-- OrderCheck
  CheckService --> Check
  CheckService ..> CheckedFolder
  Check ..> Finding
```

`Check` (`check_all.py:63`) and `CheckedFolder` (`check_all.py:316`) exist. Today a check is an instance with
`name`, `needs` and `what` given in `__init__` (`check_all.py:71`), and `run` returns a dict with a `reason` key. In
the target, `name`, `inputs` and `codes` are class attributes, and `run` returns an `OperationResult` with Findings.
`CheckService` is proposed: it runs the asked checks, marks a missing input `skipped` and an ambiguous one
`could-not-run`, as `check_all.py:76-89` does now. `check_all`'s `codes` are the union of each check's `codes`.

### The main flow: check-all

```mermaid
sequenceDiagram
  participant OP as check-all Operation
  participant CF as CheckedFolder
  participant CS as CheckService
  participant C as each Check
  OP->>CF: find the inputs in the project
  CF-->>OP: inputs, ambiguous inputs
  OP->>CS: run(folder, asked names)
  loop each Check in CHECKS
    alt an input is ambiguous
      CS-->>CS: could-not-run, code input_ambiguous
    else an input is missing
      CS-->>CS: skipped
    else
      CS->>C: run(inputs)
      C-->>CS: OperationResult with Findings
    end
  end
  CS-->>OP: one result per check
  OP-->>OP: OperationResult, status from status_of over all Findings
```

### How checks is tested alone

- Each check runs on a built design under `tests/data/`. No tool, no network.
- `VendorPinsCheck` takes a vendor header source. Its test passes a dict, so no `gh` call and no patch.
- A `CheckContract` test (proposed): every Check in `CHECKS` declares `name`, `inputs` and `codes`, and every Finding
  it emits holds a listed code.
- The goldens of `check_all.py` and each `check_*.py` stay unchanged through the move.

### How a new implementation is added

- A new check is one `Check` subclass with `name`, `inputs`, `codes` and `run`, and one entry in `CHECKS`. Its codes
  go in `checks/codes.py`. `check_all` runs it with no other change.
- A SPICE rung (P136) is one such Check that calls a simulator Adapter. It waits for its card.

### What moves into checks

| Today | Becomes |
|---|---|
| `check_all.py` `Check`, `CHECKS`, `CheckedFolder`, `render` (`check_all.py:63`, `:285`, `:316`, `:434`) | `checks/check.py`. `render` stays the person text. |
| `RulesVsNetlist`, `Physics`, `Buildability`, `VendorTruth`, `TheOrder` (`check_all.py:121-264`) | `RulesCheck`, `PhysicsCheck`, `BuildCheck`, `VendorPinsCheck`, `OrderCheck` |
| `check_physics.Finding` (`check_physics.py:93`), `check_footprints.Finding` (`check_footprints.py:54`), `compare_design.Failure` (`compare_design.py:44`) | core's `Finding`. `needs-measurement` maps to severity `unmeasured`. |
| `check_physics.Board` (`check_physics.py:114`) | `CircuitBoard` |
| `check_vendor_pins.fetch_variant_header` (`check_vendor_pins.py:64`), `CouldNotKeep` (`:175`) | `GhVendorHeaders`, `CouldNotKeepError` |
| `EXIT_MISMATCH` alias (`check_vendor_pins.py:44`) | `EXIT_FOR`, same exit code |
| `status: mismatch` (`check_vendor_pins.py:231`) | unchanged in the move. Its envelope card puts the state under its own key, so `status` holds only status words. |
| the person text keys `reason` (`check_all.py:82`), `detail` | new JSON says `sentence`. The old keys stay until a card retires them. |
