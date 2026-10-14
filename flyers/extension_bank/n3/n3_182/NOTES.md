# n3_182  N3 L (lifecycle (pushes+pull))  `N3|C:wwmmm|S:mmmww|push@0|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), exact recurrence
Source: flyers/bank/pl14/human_tm_smol_back11x2.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `L:B15`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B10 push L10->B15; s3 B6 push L11->B15; s4 B24 pull L11->B15
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (35 cells, 7 pistons): B6 B10 B14 B15 B16 B17 B24; power cells kept alone: B31[7, 2, 4]
Prescribed (removed hardware): b10 slots [0, 1, 4] caps [12, 11, 12]; b24 slots [2] caps [14]; pw_b31_9_2_4 slots [0, 3, 4] caps [1, 1, 1]
Endogenous (natural) max load 13; primitive loads in fixture: [(2, 11), (3, 11), (4, 11)]
Ports: b10:input, b15:output, b24:input, pw_b31_9_2_4:input
Pinned: required_cells = every cell of every kept glue body + power cells (31 cells).
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash 1b0a45264f95026e.
dedup twins: none.
