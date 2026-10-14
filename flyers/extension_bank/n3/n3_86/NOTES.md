# n3_86  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `S:push:B42:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B37 push L11->B42
Variant: t0=110
Kept bodies (25 cells, 6 pistons): B29 B35 B36 B37 B42 B60 B65; power cells kept alone: none
Prescribed (removed hardware): b29 slots [2, 3] caps [10, 10]; b65 slots [0, 3] caps [5, 7]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11)]
Ports: b29:input, b42:output, b65:input
Pinned: required_cells = every cell of every kept glue body + power cells (21 cells).
Plan notes: B36 moved at s3 by unkept B14 without adjacent glue | B36 moved at s4 by unkept B42 without adjacent glue | B36 moved at s3 by unkept B14 without adjacent glue | B36 moved at s4 by unkept B42 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 9e209396dd8e0216.
dedup twins: none.
