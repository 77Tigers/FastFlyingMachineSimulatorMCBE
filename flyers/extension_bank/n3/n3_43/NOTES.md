# n3_43  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B17 push L12->B15; s1 B16 push L12->B15
Variant: lone-piston passengers not kept
Kept bodies (19 cells, 2 pistons): B15 B16 B17 B18; power cells kept alone: none
Prescribed (removed hardware): b15 slots [2] caps [12]; b18 slots [2, 3, 4] caps [10, 11, 12]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (1, 10)]
Ports: b15:input, b18:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash cee68fd55cbbb4ba.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:C:B13.
