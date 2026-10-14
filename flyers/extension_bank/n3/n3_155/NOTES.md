# n3_155  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B27`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B20 push L12->B27; s4 B20 push L12->B27
Variant: actors of 3 consecutive periods kept, lone-piston passengers not kept
Kept bodies (27 cells, 5 pistons): B20 B21 B24 B27; power cells kept alone: B34[6, 0, 6], B34[6, 0, 9]
Prescribed (removed hardware): b21 slots [1, 2] caps [13, 13]; b27 slots [1] caps [13]; pw_b34_8_4_6 slots [2, 3, 4] caps [1, 1, 1]; pw_b34_8_4_9 slots [2, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(0, 10), (4, 11)]
Ports: b21:input, b27:input, pw_b34_8_4_6:input, pw_b34_8_4_9:input
Pinned: required_cells = every cell of every kept glue body + power cells (23 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8f784fad4bbf8136.
dedup twins: none.
