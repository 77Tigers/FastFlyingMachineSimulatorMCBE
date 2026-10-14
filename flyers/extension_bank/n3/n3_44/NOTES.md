# n3_44  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B18`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B8 push L10->B18; s3 B6 push L11->B18
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B6 B8 B11 B18; power cells kept alone: none
Prescribed (removed hardware): b11 slots [0, 1, 4] caps [12, 11, 12]; b18 slots [4] caps [12]
Endogenous (natural) max load 8; primitive loads in fixture: [(2, 8), (3, 7)]
Ports: b11:input, b18:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 0d045fa764d35030.
dedup twins: flyers/bank/pl13/human_tm_smol_back11.flyer:S:push:B16:s3, flyers/bank/pl13/human_tm_smol_back11.flyer:C:B16.
