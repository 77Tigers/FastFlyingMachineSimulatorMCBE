# n3_138  N3 S (single primitive)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl13/human_tm_smol_back11.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `S:push:B16:s2`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B10 push L10->B16
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (20 cells, 4 pistons): B6 B10 B15 B16 B18; power cells kept alone: none
Prescribed (removed hardware): b10 slots [0, 1, 4] caps [12, 11, 12]; b16 slots [4] caps [12]
Endogenous (natural) max load 10; primitive loads in fixture: [(2, 10)]
Ports: b10:input, b16:input
Pinned: required_cells = every cell of every kept glue body + power cells (17 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash c10cab1eef3c6418.
dedup twins: none.
