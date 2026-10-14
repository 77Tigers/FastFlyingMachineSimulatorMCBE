# n3_42  N3 C (pusher column)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `C:B10`. Generator: extract/extract.py + publish.py.
Selected actions: s1 B3 push L11->B10; s2 B2 push L11->B10
Variant: lone-piston passengers not kept
Kept bodies (18 cells, 2 pistons): B2 B3 B9 B10; power cells kept alone: none
Prescribed (removed hardware): b9 slots [0, 3, 4] caps [12, 10, 11]; b10 slots [3] caps [12]
Endogenous (natural) max load 10; primitive loads in fixture: [(1, 10), (2, 9)]
Ports: b9:input, b10:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash ece9f26e71179967.
dedup twins: flyers/bank/pl14/exclusive_roles_3bps.flyer:C:B10, flyers/bank/pl14/mmwmw_two_pulls.flyer:C:B10, flyers/bank/pl17/mmwmw_two_bodies_pulled_twice.flyer:C:B10.
