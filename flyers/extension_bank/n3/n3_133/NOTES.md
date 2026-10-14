# n3_133  N3 K (sticky chain)  `N3|C:mwwmm|S:-|pull@2|T:mmmww`  status: PASS before_natural, after_natural, interleaved (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_3bps_original.flyer period at tick 100 (state from extension-trace row 100, original rng/phase/push_limit); label `K2:B33.B9<-B55.B33`. Generator: extract/extract.py + publish.py.
Selected actions: s2 B33 pull L12->B9; s0 B55 pull L11->B33
Variant: spec-faithful (all passengers kept, strict reference caps)
Kept bodies (35 cells, 9 pistons): B5 B9 B19 B25 B33 B44 B45 B46 B55; power cells kept alone: B68[25, 1, 8]
Prescribed (removed hardware): b9 slots [0, 1] caps [11, 12]; pw_b68_11_3_8 slots [0, 1, 4] caps [1, 1, 1]
Endogenous (natural) max load 12; primitive loads in fixture: [(2, 12), (0, 11)]
Ports: b9:input, b33:output, b55:output, pw_b68_11_3_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Plan notes: B46 moved at s0 by unkept B55 without adjacent glue
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural', 'after_natural', 'interleaved'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash db22c385837d1a50.
dedup twins: flyers/bank/pl15/human_original_victim_observer.flyer:K2:B34.B15<-B55.B34.
