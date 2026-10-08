# j2_front_smol (agent J2, 2026-10-02): tm_smol rear-first

## B15 (10 glue, three rear 12s: s0, s1, s2-pull = 10 + 2 riders)
- Single/pair B15 cell deletions at PL13/14 (`b15del.py`, 40 variants): all leave a block behind (loadhist distance = min-x,
  so 0 = something stranded, not a stall). Trace (`tr_base.txt` vs `tr_d254.txt`): the tail cell (2,5,4) only CARRIES
  pusher B0 (2,6,4), which pushes B9 at s3. So B15's 10th cell is a pure push cost (user principle, measured).
- Relocating B0 (delete tail + B0, +X piston at any empty cell x2-7 y3-8 z1-8, PL12/13/14; `b0move.py`, 714 variants):
  none keeps all blocks travelling. Bounded negative for single-pusher relocation.
- Implication: removing B15's tail needs B9's s3 push removed, i.e. B9 pulled at s3 = FIRST move of its mwwmm run,
  which the role model forbids for mmmww-type words. => rear words must change (e.g. mmwmw-type rear bodies).

## Layered role model (`layered.py`, scipy milp; ~2 s per solve)
Any words per body; each move push or pull (free or fixed); per piston, per body adjacency timelines (rider_floor rules);
objective = weighted excess of load over 11 (rear weight 1000), cap 12. Options: allow=graph (who may touch whose
pistons), K = max foreign touchers per target.
- VALIDATION: tm_smol real words/kinds + real carrier graph (from role_ledger) reproduces the ledger exactly:
  8 rear 12s, 12 total (`python layered.py excess`).
- Free graph K=2 (fantasy, non-local): 0 rear 12s, 2 total with tm_smol's own words and glue -> words are not the limit.
- Geometric graph (bounding boxes within 2 cells, `near 2`), free kinds: rear12 5, all12 9, 11 pulls (adds pulls on
  B11 s1, B19 s3, B24 s2, B36 s4, B37 s3). Remaining rear 12s: B15 x3 (glue 10) + B9 x2.
- What-if (`whatif`): B15 glue 9 -> rear12 2, all12 6. Changing only B9's word to an mmwmw rotation: 4/5 infeasible,
  mwmwm worse (rear12 4): mmwmw rear needs a whole-structure redesign, not single-body swaps.

## Per-segment objective + user hint (front pushers) (`python layered.py seg`)
Max load per back segment (B9,B10,B11,B15,B18 order): best plan = same 5 pull flips (B11s1, B19s3, B24s2, B36s4,
B37s3), back [11,11,11,12,12] even at cap 12; front-segment pushers 22 -> 18. With B15 at 9 glue: [11,11,11,11,12].
A cost on front-segment pushes changes nothing: within tm_smol's neighbour graph no further front pull is feasible.
Built so far: B24s2 (b24pull/o0_d1_L14, o1_d1_L14) at PL14: segpl back [12,12,12,12,11] (B18), front [11,14,12,13,...].
User: don't bank PL14 until more back segments are at 11. Opus (j2_tmsmol_opus/) builds the other flips on o0.

## mmwmw flyer (bank/pl14/mmwmw_two_pulls) for back-at-11 (user asked; then "brief try, drop if unsuccessful")
- `ledger_ilp.py BT rear... [fix=B]`: builds the role ILP from any bodytrack ledger; validation on m14.bt.txt matches
  13/14 segment maxima (one off by 1). Best plan: back 5 [11,11,11,12,14] at PL14: its wwmmm back segment stays 14
  because it also carries the rail's pistons. Not better than tm_smol for this goal.
- `transplant24.py`: o0's B24-pull edit transplanted (alignment offset (-2,0,0), 136/145 cells match): m14t/o0_sh0_L14_c0
  runs 180/600 clean at PL14; that back segment 14 -> 13, mmwmw still pulled twice, flyer still PL14. 13 is the floor via
  pulls (both rider owners already use their one pull). Dropped per user.

2026-10-08 cleanup: variant flyers in b0move/ (714), b15del/ (40), del_o0/, del_o1/, m14t/ (except o0_sh0_L14_c0) and b24pull/ (except o0_d1_L14, o1_d1_L14) removed; result CSVs, tr_base.txt/tr_d254.txt and bodytracks kept; update_bank*.log removed. `git show 1222fbe:<path>` for tracked csv/txt/json/log; .flyer in FastFlyer_WIP_uncommitted_backup_20261008.
