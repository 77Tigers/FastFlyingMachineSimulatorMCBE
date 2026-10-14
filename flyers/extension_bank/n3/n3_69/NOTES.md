# n3_69  N3 S (single primitive)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:pull:B24:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B47 pull L11->B24
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (21 cells, 5 pistons): B24 B31 B39 B43 B47; power cells kept alone: B63[8, 0, 12]
Prescribed (removed hardware): b24 slots [0, 1] caps [10, 10]; pw_b63_10_0_12 slots [1, 2, 3] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(2, 11)]
Ports: b24:input, b47:output, pw_b63_10_0_12:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash e780de1d1ad13a4b.
dedup twins: flyers/bank/pl12/human_3bps_original.flyer:S:push:B47:s0, flyers/bank/pl12/human_3bps_original.flyer:C:B47, flyers/bank/pl12/human_3bps_original.flyer:L:B47, flyers/bank/pl15/human_original_victim_observer.flyer:S:pull:B25:s2.
