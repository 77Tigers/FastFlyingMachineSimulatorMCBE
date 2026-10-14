# n3_161  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B21.B8<-B27.B9`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B21 pull L11->B8; s3 B27 pull L12->B9
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (48 cells, 10 pistons): B2 B3 B4 B5 B7 B8 B9 B11 B12 B21 B27; power cells kept alone: B34[22, 2, 6], B34[22, 2, 9]
Prescribed (removed hardware): b8 slots [3, 4] caps [10, 11]; b27 slots [0, 1, 4] caps [12, 13, 12]; pw_b34_8_4_6 slots [2, 3, 4] caps [1, 1, 1]; pw_b34_8_4_9 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 11), (3, 12)]
Ports: b8:input, b9:output, b21:output, b27:input, pw_b34_8_4_6:input, pw_b34_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (39 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 183b59c2cb33d2e6.
dedup twins: none.
