# Diagonal connected-glue bound

Run from the repository root:

```powershell
python -B tools/extension_route.py flyers/WIP/experiments/extension_contract_20261011/phase_shift/route_bound/diagonal.json --search-depth 9
```

The request models target `wwmmm` against blocker `mmmww`, with their three B cells at `(0,0,0)`, `(0,1,1)`, and `(0,1,0)`. Before-slot relative x offsets are `0,1,2,2,1`, so the tool forbids these blocker cells at relative x positions 0 through 2. The two C contact cells are `(3,0,0)` and `(-1,1,1)`. The reserved cell `(2,0,1)` represents the observer and cannot be part of the glue route.

With glue budget 8, the unbounded depth-limited BFS visits the complete finite frontier and proves no 6-face path fits in 8 cells. Searching to 9 returns a shortest 9-glue path, so this topology's connected-glue accounting is 3 B cells + 9 C glue + 1 observer = 13 blocks. This is only a necessary occupancy bound for the declared contacts and blockers. The tool does not model power, piston arms, state changes, adhesion recruitment, or full movement legality; it does not prove global impossibility.
