# n3_100  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B64:s3`. Generator: extract/extract.py + publish.py.
Selected actions: s3 B50 push L6->B64
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (17 cells, 3 pistons): B41 B50 B59 B64; power cells kept alone: none
Prescribed (removed hardware): b41 slots [0, 1, 4] caps [12, 12, 12]; b64 slots [2] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(3, 6)]
Ports: b41:input, b64:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Plan notes: B50 moved at s0 by unkept B38 without adjacent glue | B50 moved at s1 by unkept B32 without adjacent glue | B50 moved at s0 by unkept B38 without adjacent glue | B50 moved at s1 by unkept B32 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash a609f3601d6a68e1.
dedup twins: none.
