# j2_front_orig (agent J2-front): rear-chain 12s in 3bps_original — checkpoint 1 (bounded negative)

Target: bank/pl12/human_3bps_original.flyer (= ../orig.flyer). `oscore.py` baseline: dist600=180, 0 fail,
all12=14, rear12=8, rear loads B8/B9/B15/B16 = [11,12,12], B17 = [10,11,11].

## Accounting (why a fresh front alone cannot change rear 12s)
Every rear move = rear glue body (7 glue + RB = 8) + 4 riders, all adhered by slime/honey stick links:
2 pushers of a REAR neighbour (rear ring) + 2 pushers of its MIDDLE body. No front-layer piston rides a rear body,
and the middle's pull is already on its last move (one pull per mmmww victim), so changing the front cannot remove a
rear rider. `roles.py` (from a tick-0 trace): every rear glue cell is a carry face for >=1 rider or a bridge
between carry faces (e.g. B15 (0,5,9) carries B5+B7; deleting it drops 2 riders and the flyer stalls).

## Bounded negatives (screen 300 ticks, runner `screen`; best distance in blocks)
| family | script | n | best |
|---|---|---|---|
| delete 1 rear glue cell, PL12/13 (start file and t100 snapshot) | gen_rear.py del1 | 28x3 | 3 |
| delete 2 rear cells + add 1 rear cell touching the body, PL13 | gen_rear.py del2add1 | 980 | 2 |
| delete 1 rear cell + add 1 glue cell to ANY body within r=2, PL13 | gen_rear.py del1addany | 833 | 4 |
| carry transfer: delete rear carry cell of a middle pusher, give the middle a <=3-cell arm to carry it, PL14 | xfer.py | 26 | 2 |
| replace a rear RB by an observer (+<=3 support) on a body that moved 2 ticks before each push, PL14 | rbobs.py | 80 | 2 |
Results: del1_12.csv del1_13.csv s_del1.csv d2a1all.csv d1any.csv xfer14.csv (rbobs: 0/80 > 2 blocks).
No candidate reached the 30-block near-miss threshold.
