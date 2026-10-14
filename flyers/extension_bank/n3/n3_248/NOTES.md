# n3_248  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/exclusive_roles_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B64:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B57 push L6->B64
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 3 pistons): B48 B57 B58 B64; power cells kept alone: none
Prescribed (removed hardware): b48 slots [0, 3, 4] caps [13, 13, 13]; b64 slots [1] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(2, 6)]
Ports: b48:input, b64:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Plan notes: B58 moved at s0 by unkept B44 without adjacent glue | B58 moved at s0 by unkept B44 without adjacent glue
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 124a4a6d2ab29125.
dedup twins: none.
