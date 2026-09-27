# N3 pure-push rear pickup retrofit screen

The `astra_ringgen_safe.py` geometry seed 3 at centers
`[(0,0),(0,4),(3,5),(5,2),(3,-1)]` reproduces the reference:
`base_pl19.flyer` scores 3000/10000 Rust ticks, with 15,000 extensions and
94 initial permanent blocks. Its sticky counts are `[14,14,14,14,15]`.
`base_pl18.flyer` scores only 1/120.

`screen.py` tried 40 distinct rear-terminal corner edits on the fifth carrier.
Each removed two rear sticky cells and added one nearby diagonal or axial
corner. All were tested at encoded PL19 for 120 ticks using
`flyer_measure.exe`; none stayed near the required 36/120 distance. The best,
`best_corner_pl19.flyer`, reached 28/120 before staggered piston actions
caused immovable obstruction failures. The same geometry reaches 4/120 at
PL18 and 0/120 at PL17. `summary.csv` records every edit.

The earlier five-cell shortcut in `n3_bridge/r0_rot1_inv0.flyer` reaches
35/120 but fails at tick 14 because its connected pickup attempts to include
an immovable block at `(18,0,16)`. Increasing its limit to 19 does not avoid
that obstruction. `bridge_material.py` tested 186 variants replacing every
nonempty subset of that five-cell connector with glazed terracotta across
six productive material seams, all at encoded PL19. Every variant scored at
most 1/120. Removing adhesion at any connector cell loses the early carrier
transfer, so this straight shortcut cannot be fixed by a nonadhesive spacer.
`bridge_material.csv` records the full screen.

This bounded screen does not rule out a moved piston site, a different
contact schedule, or a pull stage. The static corner edits did not produce a
PL17/3000 lead. The tick-14 bridge failure is a contact timing/ownership
problem, since it persists above the candidate's movement load.
