# n3_120  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B16`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B4 push L10->B16; s3 B0 push L11->B16; s4 B24 pull L11->B16
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (30 cells, 7 pistons): B0 B4 B7 B10 B12 B16 B17 B18 B24; power cells kept alone: B47[21, 1, 11]
Prescribed (removed hardware): b7 slots [0, 1, 4] caps [12, 12, 11]; b24 slots [2] caps [11]; pw_b47_7_1_11 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 11), (3, 11), (4, 11)]
Ports: b7:input, b16:output, b24:input, pw_b47_7_1_11:input
Pinned: required_cells = every cell of every kept glue body + power cells (24 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 8ef31416eb0fb489.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:L:B17, flyers/bank/pl13/exclusive_roles_3bps.flyer:L:B17.
