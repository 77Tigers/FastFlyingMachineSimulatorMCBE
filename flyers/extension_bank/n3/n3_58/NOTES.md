# n3_58  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B24.B18<-B35.B15`. Generator: extract/extract.py + publish.py.
Selected actions: s4 B24 pull L12->B18; s2 B35 pull L12->B15
Variant: lone-piston passengers not kept
Kept bodies (36 cells, 2 pistons): B15 B18 B24 B35; power cells kept alone: B37[9, 4, 4]
Prescribed (removed hardware): b15 slots [0, 1] caps [12, 12]; b18 slots [2, 3] caps [10, 11]; b24 slots [0, 1, 2] caps [12, 12, 11]; b35 slots [0, 3, 4] caps [12, 11, 11]; pw_b37_11_4_4 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 10; primitive loads in fixture: [(4, 7), (2, 10)]
Ports: b15:input, b18:input, b24:input, b35:input, pw_b37_11_4_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (36 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 47169a8017f514b3.
dedup twins: none.
