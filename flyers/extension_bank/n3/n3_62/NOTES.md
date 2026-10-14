# n3_62  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K3:B24.B18<-B35.B15<-B37.B35`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B24 pull L12->B18; s2 B35 pull L12->B15; s0 B37 pull L12->B35
Variant: lone-piston passengers not kept
Kept bodies (45 cells, 3 pistons): B15 B18 B24 B35 B37; power cells kept alone: B45[12, 3, 2]
Prescribed (removed hardware): b15 slots [0, 1] caps [12, 12]; b18 slots [2, 3] caps [10, 11]; b24 slots [0, 1, 2] caps [12, 12, 11]; b35 slots [3, 4] caps [11, 11]; b37 slots [1, 2, 3] caps [11, 11, 11]; pw_b45_14_3_2 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(4, 7), (2, 10), (0, 9)]
Ports: b15:input, b18:input, b24:input, b35:input, b37:input, pw_b45_14_3_2:input
Pinned: required_cells = every cell of every kept glue body + power cells (44 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 1e0715236e05b2e0.
dedup twins: none.
