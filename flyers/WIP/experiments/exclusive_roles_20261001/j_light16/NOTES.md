# j_light16 notes (agent J-excl, 2026-10-01)

Result: exclusive-roles 3 bps (3000/10000) at PL15 and PL16 on the human tm_smol base.

Best: j_light16/run15/c0001.flyer  (push_limit 15, max load 15)
- 10,000 ticks: distance 3000, 0 extension/movement failures, conservation clean.
- Role audit (roles.exe FILE 10000 0 10): B18 PULL_ONLY glue13 (pulls 3000, pushes 0); push-only: B11, B20, B25, B37, B38, B42, B46; others MIXED (2000 push/1000 pull).
- 80-case samples.exe: 80/80 distance 3000, failures 0, conserved (pl15_c0001.samples.csv).
- Added: 13-glue rail (word mmwmw) pulled by 3 stickies: carriers B10 (s0), B36 (s1), B29 (s3), sources on B11, B41, B36. Light front bodies B36/B41 used.
PL16 backups: run1/c0001.flyer, run1/c0003.flyer; both 3000, 80/80 (c0001.samples.csv, c0003.samples.csv), role audit valid.

Method: jports.py = free_ports.py (--cached, free_human/ports.json, read-only) plus a per-body load budget
(base max load per body + 1 per added glue/RB/piston <= LIM), enumerated triples shuffled, rail BFS <= 14 glue.
LIM=16: 115k budget triples, clean candidates within a minute. LIM=15: 9214 triples, 1 clean in first 3.

Blocked at PL14: LIM=14 cached ports: 228 triples, 172 pass face check, none route a rail. Uncapped ports (400/slot,
jports400.py, run14b): 15,654 triples, 1 routed candidate, fails at tick 0 (push limit). LIM=13: 0 budget triples.
Base bodies already sit at load 12, so only +1 (the sticky piston itself) fits at PL13; the rail (13 glue) also
alone loads a pull at 13+.
Next: exhaust run14b (stopped early at ~13 min), or generate ports with smaller rails (rail pull load ~ rail glue + attached) / allow
carrier extension on light B41/B45 only; PL13/12 likely needs a shorter rail (<=10 glue) which needs closer ports.
All my processes stopped. No bank/src changes.

## PL14 result (agent J-excl14, subagent of J, 2026-10-02)
VERIFIED PL14: j_light16/ver14/cand14.flyer (push_limit 14; copy of run14g/s8/c0000.flyer, geometry in cand14.json: word mmmww, ports carriers B37,B18,B35 / sources B45,B15,B37).
- measure 10000 10 (ver14/measure.txt): distance 3000, extension_failures 0, movement_failures 0, conservation_mismatch_ticks 0.
- roles.exe FILE 10000 0 10 (ver14/roles.txt): B20 PULL_ONLY glue12 (pulls 3000, pushes 0); PUSH_ONLY B11,B18,B25,B37,B38,B42,B46 (3000/0); rest MIXED.
- 80 cases (ver14/cand14.samples.csv): 80/80 distance 3000, failures 0, conserved true (limit column 14).
- At limit 13 it fails (extension failures); several bodies and a rail pull (12 rail + 2 pistons) sit at load 14.
Why earlier PL14 runs found nothing, and what fixed it (this is the lesson):
1. The 3-sticky rail pull load is rail glue + 1 adhered earlier sticky piston on pulls 2 and 3 (ho13 P1 = 14; sl12 P2 = 14), so at PL14 the rail must be <=12-13 glue, not 14. RAILMAX 14 candidates fail at the push limit.
2. jports*.py ports/rails that passed its checks all abandoned the rail after the first pull (distance 2-3): the rail moved at slot 0 while touching the f=0 port's sticky piston (5,3,1), dragging it (moving piston cannot extend), so port 2 missed its first extension. Fix in jports_st.py: rail_ok_port forbids a rail cell adjacent to the sticky at slot f when the rail moves (k==f).
3. Screening each port alone in the real simulator (portscreen.py: base + one port, ledger first 60 ticks at LIM, require extend at 2f and retract at 2s, no FAIL) cut 782 cached ports to 140 valid at LIM=14 (64/60/9/4/3 per slot) and 63->58 at LIM=13.
4. jports_st.py: exact 3-terminal Steiner rail (BFS from each face + best meeting cell, rail_base/rail_port caches), port-conflict prefilter, SHARD/NSH sharding. 15 shards x ~10 min on run14g found cand14 (shard 8) after ~1 candidate rail-11 (shard 12 fails: rail abandoned). ~1/15000 triples routes a rail <=13.
Other runs: run14c (sharded jports14.py on unscreened ports): 7 candidates, all abandon the rail. run14e/run14f: with RAILMAX 14 / before the slot-f adjacency fix: 6+ candidates, all fail. PL13: run13g (screened ports at LIM 13, 286 budget triples, rail <=11): 0 candidates.
Scripts: jports14.py (sharded jports400), jports_st.py, portscreen.py, screen.sh.
