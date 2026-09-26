# Continued research — three speed tracks

This pass used the Python editing library and Rust simulator, without changing simulation or project code. The best **verified limits** remain PL13 for2500 distance, PL19 for3000, and PL22 for3333 after exactly10,000 ticks. The following is useful intermediate progress, not a claim that PL12/18/21 is solved.

## A new 2.5bps topology in the bank

`bank/pl15/four_segment_ring.flyer` is a four-segment, two-push ring with phases `[0,2,0,2]`, centers `[(0,0),(0,4),(4,4),(4,0)]`, safe-generator geometry seed0, simulation RNG5, and encoded push limit15. It has62 blocks and scores exactly2500 after10,000 Rust ticks (minX13 to2513; 10,000 extensions). The four sticky segments have12 cells each. At PL14 and below, an unchanged copy stalls at distance0. This distinct ring was added to `bank/results.csv` for design variety; it does not improve the PL13 limit.

`check_n2_fourseg.py` reran the PL15 ring at RNG `[0,1,2,5,42]` and X/Z phases `(0,0),(7,7),(8,8),(15,15)`. All20 full10k runs scored2500 (`n2_fourseg/phase_sample.csv`). This is a sample, not exhaustive phase coverage.

## The user's pull mechanism works locally

`build_pull_fixture.py` saved a five-block, externally pulsed fixture at RNG0/5/42. A +X normal piston first moves a slime target one block while a stationary -X sticky piston extends into the gap. The sticky piston then retracts and pulls the target another block. The standard Rust simulator ran four ticks for all three inputs; the target moved from normalized X16 to18 every time. Inputs and end states are in `pull_fixture/`. This verifies the proposed q-3 contact/timing arithmetic and simultaneous first action. The observer starts powered as a one-time pulse; the fixture is **not** a repeating flyer. Next work must create a pulse from the carriers themselves, remove a rear push, and account for the support hardware in every movement load.

The four-segment PL15 ring is a concrete carrier layout for that next test: A and C can be distinct segments with the same `wwmm` timing. Its current full-cross groups are heavy, so merely adding the fixture's sticky piston will raise the load. Delete a normal last-push site and its pickup branch, and verify the front group has enough spare capacity. The current square puts opposite carriers far apart transversely; a folded or reordered center layout may shorten the pull support.

## 3bps at PL18: bounded negative results

`three_push_ring_pl19.flyer` reproduced distance3000 at19. A copy at18 moved only1 block in120 ticks. A high-limit trace shows most actions move18 blocks and several move19. The safe generator reproduced the known flyer with sticky counts `[14,14,14,14,15]`; the last carrier is the obvious peak-load target, although actual dynamic movement sets remain authoritative.

- `probe_n3_reduction.py` removed each of the15 cells of that carrier in turn; none sustained the120-tick target (best distance4). This rules out simple deletion of a cell from this saved geometry.
- `search_n3_local.py` tried78 generated one-step center/geometry-seed perturbations at18; all scored1 after120 ticks (`n3_local/summary.csv`). `search_n3_sites.py` tried68 more geometry seeds at the verified centers; all scored1 (`n3_sites/summary.csv`). `search_n3_order.py` tried65 phase/material center rotations and reversals; scores were0 or1 (`n3_order/summary.csv`). The smallest maximum sticky count in each family was15.
- `search_n3_bridge.py` replaced the seven-cell connector of the peak carrier with each of two admissible shortest five-cell routes and tried10 whole-ring seam assignments per route. Six variants reached distance35 after120 ticks, then stalled at distance37 by1,000 ticks. One continued to stall at a high encoded limit19, so load count alone does not explain the break. A Rust trace at tick14 shows an immovable obstruction near `(18,0,16)` during competing extensions (`n3_bridge/summary.csv` and saved lead flyers). The shortened route needs a safer pickup/ownership sequence, not merely another push-limit point.
- Eight generated N3 side-pickup variants were screened at high encoded limit30. Three reached distance36 over120 ticks but stalled by10k (distances45,38,104). Their sticky counts were often16–22, so this naive side-pickup topology also failed to reduce the18-limit load (`n3_side/`). The exploratory generation was stopped after eight; it is not a complete family search.

These results do not rule out PL18. They narrow the next move to a different pickup geometry or a real push/pull replacement, followed by a complete-cycle Rust test. Do not repeat those unchanged local grids or interpret short screens as successes.

## 3.333bps

No new N4 design was promoted in this continuation. The verified PL22 ring and the earlier PL21 failure analysis remain in `FINDINGS_2026-09-26.md`. The four-tick pull fixture above validates a building block of the A31 high-limit hybrid experiment. Its integration still needs a stationary front support, correct power shutoff, deletion of the corresponding normal push, and a full action-load ledger.
