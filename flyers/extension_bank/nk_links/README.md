# N_k back links

Interfaces for the N_k constructor (`flyers/WIP/experiments/nk_constructor_20261022`), stored here as allowed
precomputation (user, 2026-10-24). Unlike the contracts in the rest of this bank they are **abstract ring modules**
in that experiment's `nk.py` frame, not simulator fixtures.

`links.json`: `{n: [entry, ...]}` keyed by the number of hoppers n of one back body (towers use n = k-1). Entry:
`mod` (hopper lanes `P` (y, z), redstone blocks `R` (x, y, z), `PLATE` cells, `CONT` = the next body's cover cells in
this body's frame at its local slot 0, `size` lane box), `step` (straight step to the next body, lanes), `back_max` /
`back_sum` (largest / total back body, glue + RBs, on a k-ring with balanced frame offsets), `k`, `lateral` (lanes the
connector runs sideways: 0 or 1 by construction, 2 for the human link), `source`.

Entries are **appended only** (a k's 10-bit word stores an index into the list). Lookup:
`bank_links.links(n)`; the tower family (`human_link.construct(k, link, cv)`) uses it.

Rederive / add: `python bank_links.py N K [LAT MINSTEP]` (in the experiment folder) enumerates links
(`link0.links`: hopper lanes, minimal RB lanes, cover lanes beside the hoppers, a column lane beside the front
cluster, step = cover lane - column lane (+1 lane if LAT=1)), builds each as a back ring and keeps the best.

Current entries: n=2: `human_n3_A` (copied from `bank/pl12/human_3bps_original` body A; step (4,0); with towers
k=3 flies at PL13), `link0_n2_lat1_*` (1 lane sideways, back max 9 / mostly 8; towers on them reach only PL15),
`link0_n2_lat0_best` (0 lanes, back 8/9, too compact for towers). n=1: `link0_n1_lat0_*` (k=2 back, max 6; towers
predict PL11 > the plain ring's 10).
