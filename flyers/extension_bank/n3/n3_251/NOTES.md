# n3_251  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B65:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B60 push L6->B65
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 4 pistons): B43 B49 B60 B65; power cells kept alone: none
Prescribed (removed hardware): b43 slots [0, 1, 2] caps [13, 13, 13]; b65 slots [3] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(4, 6)]
Ports: b43:input, b65:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Plan notes: B49 moved at s0 by unkept B36 without adjacent glue | B49 moved at s1 by unkept B38 without adjacent glue | B49 moved at s2 by unkept B37 without adjacent glue | B49 moved at s0 by unkept B36 without adjacent glue | B49 moved at s1 by unkept B38 without adjacent glue | B49 moved at s2 by unkept B37 
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 74ec098647dc9f81.
dedup twins: none.
