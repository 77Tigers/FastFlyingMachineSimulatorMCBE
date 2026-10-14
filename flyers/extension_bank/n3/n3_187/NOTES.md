# n3_187  N3 P (power trick pair)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `P:B24:s1+s2`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B16 push L14->B24; s2 B31 pull L14->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (34 cells, 7 pistons): B15 B16 B20 B24 B27 B31; power cells kept alone: none
Prescribed (removed hardware): b15 slots [2, 3] caps [10, 11]; b24 slots [0] caps [14]; b31 slots [0] caps [13]
Endogenous (natural) max load 14; primitive loads in fixture: [(1, 14), (2, 14)]
Ports: b15:input, b24:input, b31:input
Pinned: required_cells = every cell of every kept glue body + power cells (30 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5236a69c103e8492.
dedup twins: none.
