# n3_23  N3 S (single primitive)  `N3|C:-|S:mmmww|push@2|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B24:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B22 push L11->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 4 pistons): B18 B22 B24 B25 B30; power cells kept alone: B35[9, 2, 4]
Prescribed (removed hardware): b18 slots [2, 3] caps [10, 11]; b24 slots [0, 1] caps [12, 12]; pw_b35_11_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 11)]
Ports: b18:input, b24:input, pw_b35_11_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 6f3cfb74d08a30d1.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:S:push:B22:s2.
