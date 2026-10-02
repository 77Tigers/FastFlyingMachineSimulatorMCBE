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
