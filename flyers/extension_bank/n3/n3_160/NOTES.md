# n3_160  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B9`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B9; s2 B2 push L11->B9; s3 B27 pull L12->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (46 cells, 8 pistons): B2 B3 B4 B5 B7 B8 B9 B21 B27; power cells kept alone: B34[22, 2, 6], B34[22, 2, 9]
Prescribed (removed hardware): b8 slots [3, 4] caps [10, 11]; b21 slots [1, 2] caps [13, 13]; b27 slots [0, 1, 4] caps [12, 13, 12]; pw_b34_8_4_6 slots [2, 3, 4] caps [1, 1, 1]; pw_b34_8_4_9 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(1, 11), (2, 12), (3, 12)]
Ports: b8:input, b9:output, b21:input, b27:input, pw_b34_8_4_6:input, pw_b34_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (39 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 993e5f5590176604.
dedup twins: none.
