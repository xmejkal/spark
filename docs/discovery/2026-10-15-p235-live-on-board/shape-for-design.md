# P235: shape for design (sketch, not a design)

A sketch of D7, D9, D12 to D15 and P251 for the design step. The design picks the real names. Each box names its role
from the table in docs/guide/developing.md ("Patterns and names in spark's core"), plus Decorator (D8) and Fake.
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
    <<Decorator>>
    wraps any BoardConsole
    on silence it resets from USB and retries once
  }
  class FakeBoardConsole {
    <<Fake>>
    silent on cue, for tests
  }
  class ConsoleResult {
    <<Result>>
    reached
    output
    silence_cured
  }
  class LiveGrant {
    <<Value>>
    board_mac
    look_token
    expires_at
  }
  class LiveGrantStore {
    <<Adapter>>
    wraps the store's grant files
    save(grant)
    find_valid(board) LiveGrant
  }
  class RestrictedPins {
    <<Value>>
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
  participant B as the board
  PO->>G: spark live --grant --minutes 30
  G->>B: one look (esptool), D13
  G->>PO: board, token, type yes
  PO->>G: yes (a real terminal, the gate)
  G->>S: save LiveGrant (board, token, expiry)
  C->>L: spark live --code "print(1)" --json
  L->>S: find_valid(board)
  S-->>L: LiveGrant, or none: refused
  L->>P: why_refused(code), D14
  P-->>L: None, or the pin and its role: refused
  L->>R: run_code(code)
  R->>B: Ctrl-C, Ctrl-A, the code
  B-->>R: silence (AT187)
  R->>B: reset_from_usb, retry once (P251)
  B-->>R: 1
  R->>B: reset_at_end (its meaning comes from D10's story)
  R-->>L: ConsoleResult(reached, "1", silence_cured)
  L-->>C: LiveTryResult as JSON, D15
```

The design step settles what this sketch leaves open: the meaning of `reset_at_end` (D10's story), the grant's file
and its expiry check (D12, P242 reuses it), whether `LiveTryService` takes the gate's `ConsentStrategy` for the grant
step, and how `BoardConnection` today becomes `MicroPythonBoardConsole` without breaking deploy's ReadyCheck · H the
facilitator's sketch · caveat: no class here exists yet, except BoardConnection and ConsentStrategy
