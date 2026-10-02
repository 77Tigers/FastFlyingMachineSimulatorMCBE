# J2-mmwmw3 (2026-10-02): TWO bodies pulled 2x per cycle at PL17, 3 bps
Method: selfpush2.py (from j_mmwmw2) applied a SECOND time to bank/pl14/mmwmw_two_pulls.flyer (base14.flyer), LIM=17, MLJ=ml.json (real glue-body
load budget), MAXX=7 (bias new rail rearwards), cached ports r2/ports.json. 31 candidates, 15 clean at 400t; best/ holds 5 verified.
Each: 10000t distance 3000, extension_failures 0, conservation ok, 80/80 samples (sol_reference_20260928/samples.exe, period 10; no recurrence requirement), encoded limit 17.
Pulled-twice bodies (bodytrack, pulls.py): old rail (x4-6,z7-9, mmwmw): pulls slots 1,3, push 0; new rail (x2-8, z0-1, mmwmw, 14 slime): pulls slots 0,1, push 3 (c148_001 numbering B21 / B18).
Max action load 17 (B12/B20/B26 pistons+fronts at 16-17); rear glue bodies B9,B10,B11 stay at 12 (new rail is rear-ish, x2-8, but rear chain unchanged).
Note: research_runner samples requires exact recurrence (fails here); not needed per standard.
