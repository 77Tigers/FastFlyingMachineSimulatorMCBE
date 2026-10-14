# n3_159  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B8`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B21 pull L11->B8; s3 B1 push L10->B8; s4 B0 push L11->B8
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (37 cells, 7 pistons): B0 B1 B2 B3 B8 B11 B12 B13 B21; power cells kept alone: B27[21, 3, 5]
Prescribed (removed hardware): b13 slots [0, 1, 2] caps [12, 12, 12]; b21 slots [3] caps [13]; pw_b27_7_6_5 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(0, 11), (3, 11), (4, 11)]
Ports: b8:output, b13:input, b21:input, pw_b27_7_6_5:input
Pinned: required_cells = every cell of every kept glue body + power cells (29 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e121ec3931692e8d.
dedup twins: flyers/bank/pl14/human_tm_smol_back11x2.flyer:L:B8.
