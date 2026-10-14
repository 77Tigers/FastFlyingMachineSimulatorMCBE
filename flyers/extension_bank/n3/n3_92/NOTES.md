# n3_92  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B54:s1`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B49 push L6->B54
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (16 cells, 3 pistons): B40 B49 B53 B54; power cells kept alone: none
Prescribed (removed hardware): b40 slots [2, 3, 4] caps [12, 12, 12]; b54 slots [0] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(1, 6)]
Ports: b40:input, b54:input
Pinned: required_cells = every cell of every kept glue body + power cells (14 cells).
Plan notes: B49 moved at s3 by unkept B26 without adjacent glue | B49 moved at s4 by unkept B27 without adjacent glue | B49 moved at s3 by unkept B26 without adjacent glue | B49 moved at s4 by unkept B27 without adjacent glue
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 1658475dad4397a7.
dedup twins: none.
