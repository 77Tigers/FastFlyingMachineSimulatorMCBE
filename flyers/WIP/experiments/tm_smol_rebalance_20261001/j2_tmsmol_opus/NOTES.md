# j2_tmsmol_opus (agent J2-front): more front pulls on tm_smol (builds on j2_front_smol/b24pull/o0_d1_L14)

Frame: snapshot = planner (base.bodytrack) - 2 in X. Tools: build.py (planner3x option -> flyer, deletes replaced
pusher), planner3x.py (= ../planner3.py; NOBAD=1 skips the "other observer pulses power no piston" check),
pullenum.py (all word-feasible front pulls not yet present), seg2.py (per-segment loads + front-push / front-pull
counts), p3dbg.py (why planner3 finds no option), pscreen.sh (16-way runner screen).

## Step 1 (works): B29 pulls B19 @s3, victim observer, B19's s3 pusher B12 (5,6,3) deleted
c1_p29v19_o001_L14.flyer / _o002_ (planner3 29 19 3 --conn=3 --oconn=3, options 1/2: B29 +1 sticky, B19 +observer+3 sl).
PL14, 10000 ticks distance 3000, 0 failures, conserved. back [11,12,12,12,11] (was o0 [12,12,12,12,11]),
front [14,14,13,13,11,11,9,9]. Front-segment pushes/period 22 (t100) -> 21 (o0) -> 20; front-puller pulls 6 -> 7 -> 8.
80-case samples: c1_*.samples.csv (speed/failure check; exact-recurrence `pass` is false, not required).

## Remaining word-feasible front pulls (pullenum.py): B41->B36 @s4 (delete B31), B45->B37 @s3 (delete B34)
- planner3 gives 0 options: every observer placement fails the other-pulse check. With NOBAD: 15 / 18 options.
- B41->B36: hosts B37 (relative offset to B41 identical at its s2 and s3 pulses -> sticky re-fires at s2 and pulls
  B36 a slot early in alternate periods; best o007/o010 travel 90/300 ticks with 12 failures, a near miss that cannot be
  fixed while B37 hosts) or victim B36 (+4-5 cells; dies at tick 0 even at PL16).
- B45->B37: all 18 die within 6 blocks (push limit exceeded at start).

## Step 2: c2_L14.flyer = c1 o001 minus B19's slime planner (7,6,3) (it only carried the deleted pusher B12)
PL14, back [11,12,12,12,11], front [13,14,13,13,11,11,9,9]; front pushes 20/period, front-puller pulls 8.
80/80 cases at 3000/10000, 0 failures, conserved (c2_L14.samples.csv; c1 o001 also 80/80). No further single
deletion on middle/front (122) or rear (84) bodies of c2 survives.

## planner3x fix
New cells of different bodies were never checked for adhesion with each other: the B45->B37 near misses
(nm_p45v37_o003_L16.flyer, 90/300 ticks, 8 failures, needs PL16) had the victim observer touching B45's new slime
connector, so B45 dragged it and the sticky fired a slot early. planner3x now rejects that; with it B45->B37 and
B41->B36 have 0 options (conn/oconn up to 4, vconn 2) and B29->B19 keeps 8 of 53 options (incl. the working one).
Host timing: for B41->B36 only victim B36 has distinct relative offsets at its 3 pulses (B37/B24/B15/B41 hosts
re-fire the sticky); B36 then needs +4-5 cells on top of B41's 3 riding pushers -> >14.

## Step 3 (PL13 shrink of c2 = bank/pl14/human_tm_smol_back11x2): bounded negative for keeping both back-11s
- The only 14 in c2 is B24 (12 cells = 9 + observer + 2 support, 2 riders = B35's pushers) on all three moves.
- Cheaper B35->B24 victim-observer power: planner3 (no adhesion fix) minimum is exactly o0's {B24: 3} for
  oconn<=3, vconn<=2 (oconn=1: 0 options). Alternative host B45 (+4 on a 7-cell front body) dies at 8-9 blocks
  (PL13/14). planner3b gives 0 options at B24 cost 3: its adhesion check is conservative (it ignores piston state), so it
  rejects o0's real working option -> treat planner3b 0-results as "no safe option", not proof.
- c2 single deletions (all original middle/front cells, 122) and B24 delete-2-add-1 at PL13 (1431, d2a1.py): best 6 blocks.
- Start-frame brute-force observer placement for B35's sticky (obsbrute.py, 13): all die at tick 0 (start frame is not
  the slot geometry).
- PL13 fallback: c3_b19only_L13.flyer = c2 without the B24 pull (B22 restored): PL13, 3000/10000, 0 fail; back
  [11,12,12,12,12] front [13,12,13,12,11,11,9,9]; front pushes 21, front pulls 7. 80-case audit c3_b19only_L13.samples.csv.
