# J-mmwmw2 (2026-10-02): mmwmw body pulled twice + pushed once at 3 bps -- WORKS (PL14 best)

Result: best/c552_003.flyer (push_limit 18; also c552_000/002/005/006). tm_smol human base (exclusive_roles_20261001/human_base.flyer)
plus ONE new 16-honey + 1 redstone-block rail (word mmwmw = moves 0,1,3) with 3 new pistons.
- research_runner measure 10000: distance 3000, extension_failures 0, conservation ok. 80/80 samples (best/*.samples.csv).
- bodytrack (best/c552_003.bt.txt), rail = B24 (ho16 RB1, mmwmw): s0 push by normal piston B19 (carrier B19, power from B24's own RB),
  s1 pull by sticky B37, s3 pull by sticky B30. => pulled 2x, pushed 1x per 10-tick cycle.
- Loads: rail actions 17, max 18 (some carrier extension). Lower limits fail as built (see lowering log below).

## Why the pl15-graft idea could not work, and what does
Graft (replace B18's slot-1 pull on pl15 by a pusher): a normal pusher left behind after its push lags 1 cell per cycle (B18 can
carry it by adhesion in only 2 of its 3 moves; the fire move itself skips the initiator). It needs an external +1 hop at a slot where
the rail is idle, and no existing body is near in time/space. Instead the pusher is carried RIGIDLY by a ww-window carrier body
(idle at fire slot f and f+1, here B19 wwmmm f=0) and the rail is routed so that at slot f the rail face is directly in front.
Geometry rule: d(k)=rail_face_x - P_x obeys d(f)=1, d(k+1)=d(k)+rail_m-carrier_m, must stay >=1.  Viable (carrier,f,rail) combos:
wwmmm f=0 + mmwmw/mwmmw/mwmwm, mwwmm f=1, mmmww f=3, mmwwm f=2, wmmmw f=4 (see pushports tables).
POWER: no existing donor body has the mmwmw word needed to flash a redstone block next to P only at slot f, so the RAIL CARRIES ITS OWN
redstone block next to P (lateral, glued to a rail cell G in front-diagonal): P is powered exactly when d=1 (slot f, unique in the viable
combos), the moving RB emits no power during the push, and at f+1 the rail has moved on so P retracts.

## Tools (this dir)
- pushports.py: first attempt, push ports with donor RB (found 0 eligible: donor words must be mmwmw-type).
- selfpush2.py: final generator (derived from exclusive_roles_20261001/j_light16/jports.py): carrier-rigid P (+X, extras routed like the
  stickies' carriers), rail-borne RB, 2 sticky pull ports, BFS-routed rail. env ONLY=tw:kind:pushslot LIM RAILMAX NMAX COMBOS; --cached reuses run3/ports.json.
- run3/ (generated candidates), best/ (verified), ev.sh (loadhist screen), runshard.sh/cfgs.txt (sharded lower-limit runs run16/run15).

## Results by limit (all: 10000t distance 3000, 0 failures, conserved, 80/80 samples csv next to file)
- PL18 best/c552_003.flyer (+000/002/005/006): rail 16 honey+RB.
- PL15 best/pl15_c780_003.flyer (+c780_007, c572_007, c780_000): rail B20 11 slime+RB.
- PL14 best/pl14_c168_000.flyer (+_001, _002): rail B20 12 slime+RB (load 13), push @s0 by B19's carried normal piston (power: rail's own RB),
  pull @s1 by B37 sticky, pull @s3 by B30 sticky (best/pl14_c168_000.bt.txt). measure: best/pl14_c168_000.measure.txt.
- PL13: generator budget model (base bodies already at 12, +1 per added cell) leaves no combos; extras-free pull ports are nearly
  nonexistent (run13/, run13b/ logs). Not reached.
Added to the tm_smol base: rail glue + RB, 1 normal +X piston (carried by a ww-window body), 2 sticky pullers (+ their carriers' extensions/RBs from the old jports scheme).
