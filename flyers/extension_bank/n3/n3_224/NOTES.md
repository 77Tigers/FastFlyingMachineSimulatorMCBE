# n3_224  N3 P (power trick pair)  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl15/human_original_victim_observer.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `P:B33:s2+s4`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B12 push L14->B33; s4 B43 pull L15->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (33 cells, 7 pistons): B8 B10 B12 B33 B36 B37 B38 B43; power cells kept alone: none
Prescribed (removed hardware): b8 slots [0, 4] caps [12, 11]
Endogenous (natural) max load 15; primitive loads in fixture: [(2, 14), (4, 15)]
Ports: b8:input, b33:output, b43:output
Pinned: required_cells = every cell of every kept glue body + power cells (28 cells).
Plan notes: B37 moved at s4 by unkept B43 without adjacent glue
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 26d390f6154f6874.
dedup twins: none.
