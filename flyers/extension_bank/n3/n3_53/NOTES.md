# n3_53  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B18`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B8 push L10->B18; s3 B6 push L11->B18; s4 B24 pull L12->B18
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (33 cells, 8 pistons): B6 B8 B11 B16 B17 B18 B20 B21 B22 B24; power cells kept alone: B35[9, 2, 4]
Prescribed (removed hardware): b11 slots [0, 1, 4] caps [12, 11, 12]; pw_b35_11_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 11), (3, 11), (4, 12)]
Ports: b11:input, b18:output, b24:output, pw_b35_11_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 5316735f8aba7c5e.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:L:B16.
