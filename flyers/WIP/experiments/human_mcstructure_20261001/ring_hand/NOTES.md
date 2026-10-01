# ring_hand (agent J-ring, 2026-10-01/02)

Result: a working 3-body 3.333 bps ring at PL29. `ring_pl29.flyer`: 10,000 ticks -> distance 3334, 0 extension
failures, conservation clean, period 12 (+4); samples.exe 80-case audit 80/80 (3334, 0 failures, conserved)
(`ring_pl29.samples.csv`). PL28 fails (`ring_pl28.flyer`). Also `ring_pl30.flyer` (80/80). NOT banked (still
above PL26 3.333 record; 82-ish cells, ~25 glue per body).

What was done: hand placement not needed. The ring3.py template + routing (`seedpool.py`, ~240 s per pool) already
yields working rings: of ~450 routed layouts in 7 pools, ~16% (24) run clean at 360 ticks at diagnostic PL60 (loads
29-39). The earlier 0/1404 was a screen/limit artefact of the previous run (its 'working' filter), not the contract.
`harvest.py` screens pools; `trim.py` greedily deletes non-essential glue (1 cell per round, 3-8 rounds, load -3 to -6);
best = pool seed 12 sample 3 (`w_12_3.flyer`, trimmed `t_w_12_3.flyer`, load 29). `climb.py`/`lowload.py` (simulator-guided
mutation) found no further improvement in 420 s.

Load structure: body (23-29 glue + RB) + 3 riding pistons; every push is 28-32. To go below ~26 the routed arms must
shrink (compact layout, glue beside pistons); rigid: random glue mutation almost never keeps the ring valid.
Next step: seed many more pools (cheap), trim, then constrained swap/shift search on the trimmed ring that keeps
timing (only edit glue; fitness = max load); or hand-shorten the arms between face glue and carrier glue.
