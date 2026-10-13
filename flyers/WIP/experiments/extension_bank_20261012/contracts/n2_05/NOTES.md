# n2_05  N2 `C:wwmm|S:-|pull@1|T:mmww+wmmw`  (reference load 7) = the PL7 rear cap
Status: PASS both orders (80/80 samples each). Regenerate: `python build.py` (reproduces the 15-cell candidate.flyer and drive.txt of
  extension_contract_20261011/prescribed_fixture/rear_cap byte-identically; only contract names/ports file layout differ).
Source: flyers/bank/pl7/tm_7pl_2.5bps.flyer, slot 1: K1 sticky (3,1,16) retracts, pulling K0 (mmww, 5) and N (wmmw, 2); load 7. Rear region is steady from tick 0.
Kept (15 cells): K0 (0,0,15)(0,1,15)(0,0,16)(0,1,16)(0,1,17); N (2,0,15)(2,1,15)+arm (1,1,15); K1 (2,0,17)(3,0,16)(3,0,17)(3,1,16)(3,1,17)(3,2,17); redstone relay (3,2,16).
Provenance split (exact, from the worked example): redstone (3,2,16) mmww PRESCRIBED slots 0,1 cap 1; K1 slime (3,1,17) wwmm: slot 2 NATURAL (K0 piston push, 6),
  slot 3 PRESCRIBED cap 6 (prescribing both would carry K0's piston as an untagged passenger). K0 (mmww) and N (wmmw) are outputs, fully endogenous.
Measured loads: whole-action max 7 (the K1 pull = the primitive); input maxima redstone [1,1], K1 [-,-,6,6].
Fixture score to beat: max load 7, 1 action at 7 per period, 15 permanent cells. Not touched: the front hop pistons of pl7 (their identity swaps randomly, so pl7 is not periodic past the rear).
