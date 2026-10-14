# n3_60  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B35.B15<-B37.B35`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B35 pull L12->B15; s0 B37 pull L12->B35
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (35 cells, 7 pistons): B0 B1 B15 B32 B33 B34 B35 B37; power cells kept alone: B45[12, 2, 2]
Prescribed (removed hardware): b15 slots [0, 1] caps [12, 12]; b35 slots [3, 4] caps [11, 11]; pw_b45_14_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 12), (0, 12)]
Ports: b15:input, b35:input, b37:output, pw_b45_14_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (28 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash f12fb0756807eae1.
dedup twins: none.
