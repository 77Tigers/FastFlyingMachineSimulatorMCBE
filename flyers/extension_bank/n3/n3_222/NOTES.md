# n3_222  N3 L (lifecycle (pushes+pull))  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B34`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B55 pull L11->B34; s3 B26 push L10->B34; s4 B23 push L10->B34
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (32 cells, 7 pistons): B15 B23 B26 B34 B45 B46 B47 B55; power cells kept alone: B65[25, 1, 8]
Prescribed (removed hardware): b15 slots [0, 1] caps [11, 12]; pw_b65_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (3, 10), (4, 10)]
Ports: b15:input, b34:output, b55:output, pw_b65_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (25 cells).
Plan notes: B47 moved at s0 by unkept B55 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 4600cb058d4e7272.
dedup twins: none.
