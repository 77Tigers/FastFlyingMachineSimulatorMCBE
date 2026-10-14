# n3_209  N3 S (single primitive)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B61:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B58 push L6->B61
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (15 cells, 3 pistons): B48 B58 B59 B61; power cells kept alone: none
Prescribed (removed hardware): b48 slots [0, 3, 4] caps [11, 11, 11]; b61 slots [1] caps [7]
Endogenous (natural) max load 6; primitive loads in fixture: [(2, 6)]
Ports: b48:input, b61:input
Pinned: required_cells = every cell of every kept glue body + power cells (13 cells).
Plan notes: B58 moved at s0 by unkept B40 without adjacent glue | B58 moved at s4 by unkept B31 without adjacent glue | B58 moved at s0 by unkept B40 without adjacent glue | B58 moved at s4 by unkept B31 without adjacent glue
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash bf7d2bdd176f4c06.
dedup twins: none.
