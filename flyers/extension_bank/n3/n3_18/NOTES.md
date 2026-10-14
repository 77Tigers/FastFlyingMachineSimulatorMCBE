# n3_18  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B18:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B8 push L10->B18
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 4 pistons): B6 B8 B11 B17 B18 B20; power cells kept alone: none
Prescribed (removed hardware): b11 slots [0, 1, 4] caps [12, 11, 12]; b18 slots [4] caps [12]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 10)]
Ports: b11:input, b18:input
Pinned: required_cells = every cell of every kept glue body + power cells (16 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b8004abb13377230.
dedup twins: none.
