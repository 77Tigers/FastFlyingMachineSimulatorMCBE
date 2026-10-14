# n3_158  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B13`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B15 push L12->B13; s1 B14 push L12->B13; s2 B33 pull L12->B13
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 5 pistons): B0 B1 B13 B14 B15 B16 B33; power cells kept alone: B35[23, 3, 4]
Prescribed (removed hardware): b16 slots [2, 3, 4] caps [10, 11, 12]; b33 slots [0, 3, 4] caps [12, 11, 11]; pw_b35_9_4_4 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (2, 12)]
Ports: b13:output, b16:input, b33:input, pw_b35_9_4_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (27 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 7a94846c1035b878.
dedup twins: none.
