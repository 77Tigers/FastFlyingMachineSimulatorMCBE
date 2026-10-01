# RESUME checkpoint (agent E, session started 2026-10-01 01:31, deadline ~12:30)
User asleep. Order: A/B category first (2.5, 3, 3.333 bps, then minimize PL), then mmwmmw pull-twice (speed_range_b_20260930/mmwpull), then PL16-24 frontier.
A/B rules (user-confirmed): pistons riding on A only push B; stickies riding on B only pull A (their extensions move nothing); no A-A or B-B moves; power may touch anything.
Bank A/B results occasionally (variety good, no spam). Lowest PL is the target.
Hourly cron (session-only) re-prompts me to read this file.
## Status
- (01:50) designing 2-body 2.5bps A/B (classic flying machine generalization). Builder: ab25.py
- (02:00) 2.5bps A/B WORKS: ab25_v1_pl15.flyer 80/80 (exact). gen25.py (obs power) best load 12: g1/c00000.flyer (A 8 honey+2 obs+2 riders, B 8 slime+2). Redstone-on-B variant (gen25b) worse. anneal4 run in ann/.
- Theory: stationary-anchor A/B at 3 and 3.333 needs >=6 bodies = 3 A/B pairs sharing words; feasible word sets (carrier-transition rule): 3.333 (mmwmmw,mwmmwm,wmmwmm) or (mmmwmw,mwmmwm,wmwmmm); 3bps (mmwmw,mwmmw,wmmwm) or (mmmww,mwmmw,wmwmm). Every extension needs a body moving at f-1 and resting at f; no moving glue may touch a piston at its extension tick.
- 3.333 plan: cross modules per fire slot f (abmodel.py): center = alpha-pair redstone (alpha = pair resting at f+2) at x=0; 4 pistons N/E/S/W: P(B_alpha),P(B_beta),Q(A_alpha),Q(A_gamma); diagonals NE,SW = A_gamma at x=0 (anchor + carry j=4,5), SE,NW = B_beta at x=-1 (carry j=2,3, Q anchor). D at +1, C at -2. Generator abgen333.py (in progress).
- Subagent F launched on mmwpull (speed_range_b_20260930/mmwpull/).
- (04:20) BANKED bank/pl12/ab_push_pull_2body.flyer (2.5 A/B, PL12, 80/80). abverify.py checks A/B rules on a run.
- KEY RULE found by validator: push of a B second consecutive move needs an A anchor resting at BOTH s-1 and s (else anchor+victim both carry the pusher -> obstruction merge). feas.py/feas2.py: 3bps min 6 bodies A{mmmww,mmwmw,mwmmw,wmmmw} B{mwmwm,wmwmm}; 3.333 min 9 bodies (5A with ww + 4B). mmwmmw-pair cross design (abgen333.py) is INVALID for this reason.
- Tools: abcheck.py (discovery-rule validator per slot), abdiff.py + bin/dumpstate.exe (sim vs model per slot), abroute.py (World/routing).
- Next: generic generator abgen_g.py for 3bps 6-body.
- (05:00) 3bps A/B FIRST WORKING: ab3_first_working.flyer (6 bodies, 492 blocks, limit 250; 300/1000 exact). Generator: abinc.py (incremental hazard-checked module placement + abworld routing + abcheck). Next: compaction (cluster placement, spacing 2-3, trim).
- (05:50) BANKED bank/pl24/pull_twice_mmwmmw.flyer (subagent F, mmwpull). Subagent F still running.
- (06:15) abpr.py = place&route generator (+abrules.py carried-front rule, power check in abinc.Inc.power_ok, front-item rule). Runs: pr3/ (6-body 3bps), pr3b/ (7-body 3bps), pr333/ (9-body 3.333 exploratory). Screen with research_runner screen DIR 500 at limit 250. abre.py rebuild(Aw,Bw,seed) recreates World for abdiff/abcheck debugging.
- (06:40) 3bps A/B 7-body works: ab3_7body_l53.flyer (load 53). Relaunched pr3/pr3b/pr333 with balanced objective + partial_ok validator.
- (06:55) launched subagent G (frontier_pull_20261001/): pull-on-first-move-after-wait for 3bps mmmww (<=17) and 3.333 (<=20).
- (08:00) stack=1 (modules share YZ lines at different x) -> 7-body maxglue 30, load 45 (pr3s/s00200). Riders now dominate; added est_load objective (glue+sources+carried pistons). Runs pr3s_300/320 logs. 80-case audit of ab3_7body_pl46 running (slow). anneal ann/a3 at 44.
- (06:40 real clock) usage reset. BANKED pl22 mmwmmw. 3.333 A/B works (pr333/s00125 load 85). 3bps best pr3s/s00379 load 34. ab3_7body_pl46 80/80 passed. Subagents F,G died at limit -> resume.
- BANKED bank/pl34/ab_push_pull_7body.flyer (3bps A/B PL34). 3.333 A/B pl85 audit running (ab333_9body_pl85.samples).
- BANKED pl85 3.333 A/B. Continue: lower 3.333 A/B load; 3bps runs.
- (08:00) 9-body set c (A wwmmmm,mwwmmm,mmwwmm,mmmwwm,mmmmww; B wmmwmm,mwmmmw,mmwmmw,mmmmww) better: pr333c/s00002 load 71, auditing ab333_pl71. Runs pr333c*.log, pr333e.log
- (11:45) FINAL: banked pl12/pl34/pl71(+pl85) A/B, pl22(+pl24) mmwmmw. Generators stopped. Lead: pr333c/s00012 load 61 (audit at 61 not run). Subagents asked to write FINDINGS and stop.
