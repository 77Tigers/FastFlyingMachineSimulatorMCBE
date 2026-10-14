# n3_317  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B16 push L12->B15; s1 B17 push L12->B15; s2 B36 pull L12->B15
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (34 cells, 6 pistons): B0 B1 B15 B16 B17 B19 B36; power cells kept alone: B38[23, 3, 4]
Prescribed (removed hardware): b19 slots [2, 3, 4] caps [12, 13, 14]; b36 slots [0, 3, 4] caps [12, 11, 11]; pw_b38_9_4_4 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 12), (1, 12), (2, 12)]
Ports: b15:output, b19:input, b36:input, pw_b38_9_4_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (29 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 968d5b5691e91dae.
dedup twins: none.
