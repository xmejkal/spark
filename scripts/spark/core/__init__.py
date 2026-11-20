"""The core: the contract every area and frontend shares (an Operation, its result, the outside it reaches, the CLI frontend
in `cli`), and the leaf modules every script shares and that import nothing of spark (outcomes, text_guards, zone_time, codes).
It imports nothing, so the leaf modules of another area may import the core's, such as `codes.Code` (rule U1, P853)."""
