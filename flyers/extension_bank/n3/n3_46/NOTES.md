# n3_46  N3 C (pusher column)  `N3|C:-|S:mmmww|push@1|T:mmmww`  status: PASS before_natural (80/80 Rust + Python), bounded recurrence
Source: flyers/bank/pl12/human_tm_smol_3bps.flyer period at tick 110 (state from extension-trace row 110, original rng/phase/push_limit); label `C:B29`. Generator: extract/extract.py + publish.py.
Selected actions: s0 B23 push L11->B29; s4 B23 push L11->B29
Variant: t0=110
Kept bodies (32 cells, 7 pistons): B19 B23 B26 B27 B28 B29 B36; power cells kept alone: B41[13, 1, 8]
Prescribed (removed hardware): b19 slots [1, 2, 3] caps [11, 11, 10]; b36 slots [3] caps [11]; pw_b41_12_5_8 slots [0, 1, 2] caps [1, 1, 1]
Endogenous (natural) max load 11; primitive loads in fixture: [(0, 11), (4, 11)]
Ports: b19:input, b29:output, b36:input, pw_b41_12_5_8:input
Pinned: required_cells = every cell of every kept glue body + power cells (26 cells).
Recurrence bounded (envelope = bbox of kept identities): lone pistons rotate roles (full state recurs every 48 ticks), exact fails.
Orders: ['before_natural'] (interleaved is the synthetic stress mode; index.json lists before/after only). Canonical hash b56dfa78259d5bea.
dedup twins: none.
