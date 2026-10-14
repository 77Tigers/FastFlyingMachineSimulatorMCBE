# n3_313  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B16 push L12->B15; s1 B17 push L12->B15
Variant: lone-piston passengers not kept
Kept bodies (21 cells, 3 pistons): B15 B16 B17 B19; power cells kept alone: none
Prescribed (removed hardware): b15 slots [2] caps [12]; b19 slots [2, 3, 4] caps [12, 13, 14]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (1, 10)]
Ports: b15:input, b19:input
Pinned: required_cells = every cell of every kept glue body + power cells (19 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash dad853f84db50bb4.
dedup twins: none.
