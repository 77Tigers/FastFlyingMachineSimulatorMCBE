# Diagonal pickup and push/pull continuation

## Banked result

The user's diagonal-piston hint enabled the alternating two-carrier PL11/2.5 bps machine. Bank files are `../../bank/pl11/diagonal_alternating.flyer` and the PL12 copy. Both were audited over 80 full 10,000-tick RNG/phase combinations; all scored 2,500, conserved permanent kinds, and repeated complete physical state and owner lists translated +2 every eight ticks. The input has 8 slime, 6 honey, 2 observers and 4 normal pistons; one arm is present at the sampled boundary. Action loads alternate 11/9.

Generator and metadata: `astra_diagonal/search_mwmw.py`, `mwmw_metadata.json`, candidate c58. Exact parameters and negative PL10 evidence are in the active research log and `sol_diagonal/FINDINGS.md`.

## 3 bps timing is established; low limit is not

For target T moving in slots 0/1/2, a middle M moving 0/3/4 can carry a backward sticky. A front F moving 1/2/3 supplies power: M moves S into range at slot 0, S extends at slot 1 as F moves away, and S pulls T on slot 2. This is the friend's two-push/one-pull sequence.

`astra_pull3/retrofit.py` closes this mechanism on one interface of the existing five-carrier N3 engine. Its diagnostic g0 file moves 3,000 in 10,000 ticks but has loads up to 25. Sol's two deletions from g1 produce `sol_diagonal/pull3trim/double_pl22.flyer`, still 3,000/10,000, 99 end blocks. This is a self-running mechanism proof, not an improvement over the pure-push PL19 record. The existing widely spaced centers add a long target contact behind the next-next carrier.

The all-hybrid `astra_pull3/hybrid_ring.py` assigns two normals and one backward sticky to each interface. The sticky shares the first normal's power phase and pulls carrier j-2. Early conservative routing at an 18-sticky cap yielded no candidates; permitting correctly timed hardware adjacency produced one short-lived 109-block candidate. A high-cap screen yielded several repeating diagnostic layouts, but they remain too large. One failure was traced to a mandatory rear corner, not an added route cell: another carrier grabs a still-retracted sticky before it can extend. A useful next generator check is to apply hardware-ownership legality to mandatory terminals as well as new paths.

## 3.333 bps new hybrid and earlier bridge diagnosis

The same schedule generalizes: T moves slots 0/1/2/3, M moves 0/1/4/5, F moves 2/3/4/5. A sticky on M extends during T's third push and supplies its fourth move by pulling. `hybrid_ring.make(..., n=4)` implements three normal pushers plus one backward sticky per interface.

`astra_pull3/n4_hybrid/c1f0_0s35.flyer` completed 10,000 ticks at diagnostic PL100 for distance 3,334, 10,000 extensions, 76 end blocks. The portable full trace audit found conservation every tick, repeated translated shapes, no movement failures, and **maximum actual load 26**. Its extra startup block does not indicate speed above 3.333 bps. Two other high-limit layouts also repeated. None improves the established PL22 record.

The older shortened PL21 bridge has a substantially earlier problem than the previously highlighted tick-153 overload. Reproduced as `astra_n4_causal/r0m3pl21.flyer` (distance 117 at 10,000). At **tick 6**, the short slime bridge picks up retracted normal piston `(18,1,17)`. Its +X destination contains honey at `(19,1,17)`, so it pushes into an entire other carrier. An exact-state high-limit diagnostic, reached after six original-PL21 ticks, discovers **42 sources**, not merely 22. PL21 suppresses this bad action and the machine happens to move at target rate briefly despite early failures.

Evidence: `astra_n4_causal/encoded21_first160.txt`, `exact_tick6_diagnostic.txt`. The latter explicitly changes the limit only at tick 6. Raising the limit from the initial file creates a different early history and is not an equivalent diagnostic. The key repair is avoiding that piston pickup/destination collision, not simply trimming a 22nd cell at tick 153. A plain nonsticky replacement in a one-cell-wide dragging bridge disconnects its upstream part; that is why earlier material substitutions did not fix it.

## Friend's separate helper architecture

`astra_pull3/helper_ring.py` explores five primary backs, five middles, and five fronts. Middle/front helpers stay compact and separate from the principal ring routing. The first version is saved as `helper_ring_v1.py`; its 6,000 geometry proposals produced ten routable PL100 files, all failing the 160-tick screen. Local middle loads were 13, front loads 5–7, and several primary moves 13–15, but unintended timing and segment mergers stopped closure.

The middle uses two corner redstone sources and a five-cell horseshoe front instead of a source/solid at the axial center. That keeps the center clear for the back's pickup spine during its third stroke. The middle has seven sticky cells in total. The front has four. Each back begins with a five-cell local frame, plus a routed pickup of the next back's two diagonal normal pistons. The optimistic back cap is eleven sticky cells, giving a possible PL17 family, not a measured bound.

The first version placed a back power source adjacent to a middle normal piston at the wrong phase. Version 2 swaps the common corners of the back's diagonal pair: its source/front corner becomes local `(2,0)` in YZ, and its predecessor's pickup becomes `(1,-1)`. This moves the back source away from all three middle-piston lanes. Its completed 6,000-proposal screen found five routable layouts at nominal back cap 11, none sustaining the 160-tick screen. `helper_ring_v2/c1s1287.flyer` traveled farthest (10 blocks); an early trace shows an unintended 30-block sticky pull at tick 6. `helper_ring_v2.log`, metadata and results preserve the search. Diagnose that merger before rerunning or claiming a lower push limit.

The generators are hypotheses. Their collision filters and nominal ownership tables are not substitutes for Rust traces, especially where mandatory cells touch movable hardware or simultaneous actions can run in either order.

## New diagnostic tool

`research_runner.rs` and `build_research_runner.ps1` implement portable measurement, full movement-set audit, arbitrary-period recurrence checks, batch screens and detailed power/adhesion traces. See `RESEARCH_RUNNER.md`. No core simulator code changed. Proposed next tools in the active log include persistent identities, automatic divergence comparison, temporal routing, and checkpointed agent manifests.
