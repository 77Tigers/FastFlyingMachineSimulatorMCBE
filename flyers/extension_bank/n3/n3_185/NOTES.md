# n3_185  N3 P (power trick pair)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `P:B19:s2+s3`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B11 push L13->B19; s3 B25 pull L13->B19
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (33 cells, 6 pistons): B8 B11 B18 B19 B22 B25; power cells kept alone: none
Prescribed (removed hardware): b8 slots [3, 4] caps [10, 11]; b19 slots [1] caps [13]; b25 slots [1] caps [13]
Endogenous (natural) max load 13; primitive loads in fixture: [(2, 13), (3, 13)]
Ports: b8:input, b19:input, b25:input
Pinned: required_cells = every cell of every kept glue body + power cells (28 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0b9f7e7bff5a3e14.
dedup twins: none.
