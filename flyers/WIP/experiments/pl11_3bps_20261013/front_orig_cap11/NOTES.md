# front_orig_cap11 (n3_135 front, back pushes supplied; back bodies frozen, all prescribed caps 11, target natural 11)
Seed check: cap-11 copy passes 80/80 (bounded, before+after): back strokes already <=11 (b7 [10,10,-,-,9], b8 [-,9,10,10,-], b9 [10,11,11,-,-], b15 [10,-,-,9,10], b16 [-,-,8,9,9]); nothing breaks 11; the 12s are natural front pushes (seed excess 36 = 18 actions at 12 per order).
run1 (seed 1, bounded, 1200 s, 202k evals): best excess 28 (14 actions at 12 per order), max 12, 191 blocks; piston moves/adds only, no <=11 candidate.
run2 (seed 2, bounded, 1200 s): best excess 28, max 12, 203 blocks. run3 (advance) not run: seed fails advance recurrence (rotating lone pistons, identity 30 not at origin+3).
No candidate reached endogenous max 11, so nothing to confirm with the Python checker.
