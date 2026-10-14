# n3_213  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B65:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B63 push L6->B65
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 3 pistons): B55 B63 B64 B65; power cells kept alone: none
Prescribed (removed hardware): b55 slots [1, 2, 3] caps [11, 11, 11]; b65 slots [4] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(0, 6)]
Ports: b55:input, b65:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B63 moved at s2 by unkept B46 without adjacent glue | B63 moved at s3 by unkept B47 without adjacent glue | B63 moved at s2 by unkept B46 without adjacent glue | B63 moved at s3 by unkept B47 without adjacent glue
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 76e08d4cbb21f65b.
dedup twins: none.
