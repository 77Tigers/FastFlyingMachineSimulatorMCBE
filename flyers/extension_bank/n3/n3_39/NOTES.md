# n3_39  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B45:s4`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B43 push L9->B45
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 4 pistons): B37 B42 B43 B44 B45; power cells kept alone: none
Prescribed (removed hardware): b37 slots [1, 2, 3] caps [11, 11, 11]
Endogenous (natural) max load 9; primitive loads in fixture: [(4, 9)]
Ports: b37:input, b45:output
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b87a194e7a4d15e2.
dedup twins: flyers/bank/pl12/human_tm_smol_3bps.flyer:C:B45, flyers/bank/pl12/human_tm_smol_3bps.flyer:L:B45.
