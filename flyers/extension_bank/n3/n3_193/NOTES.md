# n3_193  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B15:s0`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B11 push L11->B15
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (27 cells, 4 pistons): B2 B11 B13 B15 B16 B17 B26; power cells kept alone: none
Prescribed (removed hardware): b15 slots [2] caps [12]; b16 slots [0, 3] caps [12, 11]; b17 slots [2, 3, 4] caps [10, 11, 11]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11)]
Ports: b15:input, b16:input, b17:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 152b0bdb1dd19581.
dedup twins: none.
