# n3_97  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B63:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B56 push L6->B63
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (15 cells, 3 pistons): B47 B56 B57 B63; power cells kept alone: none
Prescribed (removed hardware): b47 slots [0, 3, 4] caps [11, 11, 11]; b63 slots [1] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(2, 6)]
Ports: b47:input, b63:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B57 moved at s0 by unkept B39 without adjacent glue | B57 moved at s0 by unkept B39 without adjacent glue
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash eb4b5dafb2a8fa7d.
dedup twins: none.
