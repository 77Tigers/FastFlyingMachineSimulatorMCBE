# n3_74  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B16:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B4 push L10->B16
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (19 cells, 4 pistons): B0 B4 B7 B10 B16 B17; power cells kept alone: none
Prescribed (removed hardware): b7 slots [0, 1, 4] caps [12, 12, 11]; b16 slots [4] caps [11]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 10)]
Ports: b7:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (15 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 37519031a568214a.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:S:push:B17:s2.
