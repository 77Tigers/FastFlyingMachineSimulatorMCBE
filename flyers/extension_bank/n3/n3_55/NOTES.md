# n3_55  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B35`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B37 pull L12->B35; s3 B25 push L11->B35; s4 B30 push L11->B35
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (34 cells, 8 pistons): B24 B25 B30 B32 B33 B34 B35 B37; power cells kept alone: B45[12, 3, 2]
Prescribed (removed hardware): b24 slots [0, 1, 2] caps [12, 12, 11]; pw_b45_14_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 12), (3, 11), (4, 11)]
Ports: b24:input, b35:output, b37:output, pw_b45_14_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (27 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e512e5f939f84c37.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:L:B33, flyers/bank/pl14/mmwmw_two_pulls.flyer:L:B36.
