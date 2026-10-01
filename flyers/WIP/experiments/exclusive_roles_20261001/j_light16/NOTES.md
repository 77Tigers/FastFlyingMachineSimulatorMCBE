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
