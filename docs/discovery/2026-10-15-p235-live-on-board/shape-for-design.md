# P235: shape for design (sketch, not a design)

A sketch of D7, D9, D12 to D15 and P251 for the design step. The design picks the real names. Each box names its role
from the table in docs/guide/developing.md ("Patterns and names in spark's core"). Four roles here are not in that
table yet, so they are marked "to settle in design and in P255's table change": Decorator (D8 adds the row), Fake (no D
yet), a wrapper of the store's own files (the table's Adapter wraps an outside program), and a value with a `why_`
function (the table's Value has no actions).
No name in the core says MicroPython (D7): the platform shows only in its adapter's name.

```mermaid
classDiagram
  class LiveTryService {
    <<Service>>
    run(board, code) LiveTryResult
  }
  class BoardConsole {
    <<Strategy>>
    run_code(code) ConsoleResult
    reset_from_usb()
    reset_at_end()
  }
  class MicroPythonBoardConsole {
    <<Adapter>>
    wraps mpremote
  }
  class RetryingBoardConsole {
    <<Decorator, to settle>>
    wraps any BoardConsole
    on silence it resets from USB and retries once
  }
  class FakeBoardConsole {
    <<Fake, to settle>>
    silent on cue, for tests
  }
  class ConsoleResult {
    <<Result>>
    reached
    output
    silence_cured
    cause_if_not_reached
  }
  class LiveGrant {
    <<Value>>
    board_mac
    look_token
    expires_at
  }
  class LiveGrantStore {
    <<store wrapper, to settle>>
    wraps the store's grant files
    save(grant)
    find_valid(board) LiveGrant
  }
  class RestrictedPins {
    <<Value with why_, to settle>>
    pin, role, source per pin
    why_refused(code) reason or None
  }
  class LiveTryResult {
    <<Result>>
    verdict
    console ConsoleResult
    to_json()
  }
  BoardConsole <|-- MicroPythonBoardConsole
  BoardConsole <|-- RetryingBoardConsole
  BoardConsole <|-- FakeBoardConsole
  RetryingBoardConsole o-- BoardConsole : wraps
  LiveTryService --> BoardConsole
  LiveTryService --> LiveGrantStore
  LiveTryService --> RestrictedPins
  LiveGrantStore --> LiveGrant
  LiveTryService --> LiveTryResult
  BoardConsole --> ConsoleResult
```

```mermaid
sequenceDiagram
  actor PO as the PO, in his terminal
  participant G as live --grant
  participant S as LiveGrantStore
  actor C as Claude
  participant L as LiveTryService
  participant P as RestrictedPins
  participant R as RetryingBoardConsole
  participant M as MicroPythonBoardConsole
  participant B as the board
  PO->>G: grant command, a time limit (sketch name, no D for 30)
  G->>B: one look (esptool), D13
  G->>PO: board, token, type yes
  PO->>G: yes (a real terminal, the gate)
  G->>S: save LiveGrant (board, token, expiry)
  C->>L: live call with code and --json (sketch name)
  L->>S: find_valid(board)
  S-->>L: LiveGrant, or none: refused
  L->>P: why_refused(code), D14
  P-->>L: None, or the pin and its role: refused
  L->>R: run_code(code)
  R->>M: run_code(code)
  M->>B: the platform's bytes (MicroPython: Ctrl-C, Ctrl-A, the code)
  B-->>M: silence (AT187)
  M-->>R: not reached
  R->>M: reset_from_usb, then run_code again, once (P251)
  M->>B: USB-side reset, the bytes again
  B-->>M: 1
  R->>M: reset_at_end (P252 informs it, the PO picks)
  R-->>L: ConsoleResult(reached, "1", silence_cured)
  L-->>C: LiveTryResult as JSON, D15
```

The design step settles what this sketch leaves open: the meaning of `reset_at_end` (D10's story), the grant's file
and its expiry check (D12, P242 reuses it), whether `LiveTryService` takes the gate's `ConsentStrategy` for the grant
step, how `BoardConnection` today becomes `MicroPythonBoardConsole` without breaking deploy's ReadyCheck, whether
`reset_from_usb` belongs to a transport object rather than the platform-neutral base (a USB reset is a fact of the
port, not of the platform), and how `cause_if_not_reached` can tell a silent console from a firmware that does not read
its console (D11): from mpremote's one error the two look the same, and the bench told them apart only with a separate
probe and the PO's eyes · H the
facilitator's sketch · caveat: no class here exists yet, except BoardConnection and ConsentStrategy
