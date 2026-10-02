# j_333 notes (agent J-excl333, 2026-10-02)

Result: exclusive-roles 3.333 bps at PL22 (was PL26).
Best: j_333/exclusive_3p333_pl22.flyer (= run22/c0003.flyer, push_limit 22; limit 21 fails at once: 239855 extension failures).
- measure 10000 12: distance 3334 (>=3333), 0 extension/movement failures, conservation clean (exclusive_3p333_pl22.measure.txt)
- roles.exe 10000 0 12: B0 PULL_ONLY glue16 (pulls 3334, pushes 0) + 12 PUSH_ONLY bodies (exclusive_3p333_pl22.roles.txt)
- samples.exe 12: 80/80 distance 3334, failures 0, conserved (exclusive_3p333_pl22.samples.csv). Other PL22 candidates also 80/80: run22/c0005, c0006, c0008 (pl22_c*.samples.csv).
Method: jports333.py = jports.py with per-body ML = base body glue+RB+4 pistons (n4 base loads: 21 for 16-17 body, 20 ho15, 18 sl13), pruned DFS over port 4-tuples (free_n4/ports.json cached copy, ports_free_n4.json), RAILMAX=LIM-2.
LIM=22: 142 budget combos, 60 candidates, 18 clean at 240 ticks (s22.csv). LIM=23/24 runs exist (run23, run24) but unneeded.
PL21 blocked: base has loads 21; carriers on slots 0,1 are all load-21 bodies, so 4-slot word needs slots 2..5 whose carriers are 49,21 (18) and 19,2 (20) and donors (RB-carriers) with ML+1<=21 (only 2,19,21,49); regeneration of ports restricted to LIM=21 (gen21, PCAP=300) found 0 ports for carriers 21 and 49, so no routable set. PL21 is also the bank minimum for any 3.333 base (bank/pl21/n4_twelve_body), so PL22 is probably the floor for this construction.
No bank/src changes. All processes stopped.
