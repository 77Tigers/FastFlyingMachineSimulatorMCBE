# Reference timing and interfaces (read-only investigation)

Read root SIMULATION.md. No reference or project file modified.

## Existing N4 is not mmwmmw

`flyers/WIP/astra_ringgen_safe.py:make(n, centers, seed, limit=100)` is the verified full-cross generator. `flyers/WIP/experiments/astra_ringgen_spans.py:make(..., spans=None)` (deleted; `git show 1222fbe:flyers/WIP/experiments/astra_ringgen_spans.py`) exposes the same architecture with adjustable axial spans. Both use L=n+2 action slots, phases `(2*i)%L`, and front position `h+n*cycle+1+min(phase,n)`. Their motion word is n consecutive moves followed by two waits. Each slot is two Rust ticks.

For N4: three carriers, phases [0,2,4], words mmmmww/mmwwmm/wwmmmm. Carrier move-slot sets are {0,1,2,3}, {0,1,4,5}, {2,3,4,5}. Translation four cells per 12 Rust ticks = 3.333 bps. These words are not cyclic rotations of mmwmmw. N4 reference `flyers/bank/pl22/four_push_ring.flyer` (also `flyers/WIP/four_push_ring_pl22.flyer`) is seed 0 at centers [(0,0),(0,4),(3,1)], sticky counts [16,16,17], 66 serialized blocks, PL22, RNG5. Do not relabel it as the requested new architecture.

For N3: five carriers, phases [0,2,4,1,3], word mmmww and its rotations. Translation three cells per 10 ticks = 3 bps. Reference `flyers/bank/pl19/five_segment_ring_low.flyer` uses centers [(0,0),(0,4),(3,5),(5,2),(3,-1)], seed0, sticky counts [14,14,14,14,15].

## Generator interface geometry

Cross offsets are center plus three/four cardinal YZ offsets. Interface i's front cross belongs to target carrier i; its rear cross belongs to carrier i-1. Redstone is one X cell behind front cross. Normal +X piston bases occupy the cardinal arms. A fired piston becomes immovable until retracted; otherwise it can transfer between front/rear sticky groups. Actual loads include carried hardware and can exceed sticky count significantly.

Initial fronts F are computed with `F[i+1]=F[i]+2+min(ph[i+1],n)-max(0,ph[i+1]-2)-spans[i]`; rear of interface i+1 is `F[i]-spans[i]`. Hence each successive carrier can connect to pickup geometry behind the preceding carrier's front. Default N3 fronts [0,1,1,1,2], spans [3,3,3,3,4]. Default N4 fronts [0,1,2], spans [3,3,4]. Changing spans changes the X length and endpoint conditions; sum must be 16 (N3) or 10 (N4) to close those rings.

make() returns `(flyer, sticky_counts, (sticky_sets, phases))`. This is useful for extracting a carrier, identifying its boundary ports, recording minX, and building a chain. Ring closure itself is built in via modulo indexing, so an extension builder must replace the wraparound boundary with an explicit driver/terminal contract. Safe router checks all nominal phases and prohibits contact with nonowned hardware. It does not by itself prove actual motion, connected sticky components, dynamic conservation, or exact recurrence.

## More reusable architecture

`flyers/WIP/experiments/astra_diagonal/search_mwmw.py` (deleted; `git show 1222fbe:flyers/WIP/experiments/astra_diagonal/search_mwmw.py`) defines a small local interface via interface(t, material, observer_axis), with separate worlds and nominal displacement. Its generic `make` joins endpoint sticky sets, routes each carrier until all mandatory components connect, then lets Rust validate. This is a better small-module coding pattern for a new word than changing min(phase,n) in the full-cross template without rederiving piston pickup/power timing.

`flyers/WIP/experiments/astra_pull3/hybrid_ring.py` (deleted; `git show 1222fbe:flyers/WIP/experiments/astra_pull3/hybrid_ring.py`) models hardware owners explicitly at every phase and outputs segment coordinate sets in metadata. Interface j has two +X pushers and a -X sticky; the sticky pulls carrier j-2, is carried by j-1, and shares interface j redstone timing. Unvalidated routed search; do not use as a working driver.

`flyers/WIP/experiments/astra_pull3/helper_ring.py` (deleted; `git show 1222fbe:flyers/WIP/experiments/astra_pull3/helper_ring.py`) models separate back/middle/front carriers, with phase offsets p,p+2,p+4 modulo five and explicit hardware owners. Back is two pushes plus front-assisted pull; middle/front still use three drive sites. This offers the friend's intended modular role separation but known best candidate stalls after ten cells. `flyers/WIP/experiments/sol_extra_front_20260927/FINDINGS.md` (deleted; `git show 1222fbe:flyers/WIP/experiments/sol_extra_front_20260927/FINDINGS.md`) covers a further relay role, also unfinished.

Relevant evidence: `FINDINGS_2026-09-26.md`, `FINDINGS_CONTINUATION_2026-09-26.md` (deleted; summarised in [ARCHIVE.md](../ARCHIVE.md), `git show 1222fbe:flyers/WIP/experiments/FINDINGS_2026-09-26.md`); N4 bridge candidates survive short runs then fail due to changed ownership/adhesion, so repeat tests must compare owner lists and block states, not only minimum-X displacement.

## Recommended chain validation contract

Use a banked N3/N4 reference as an untouched driver copy, with diagnostic limit if necessary, then append 1, 2, 4 and 8 copies of the proposed extension. Store each copy's initial coordinate port and material/phase metadata. Measure hardware/driver loads separately from extension actions. Test each chain for 160 ticks first, 1,000 next, then exactly 10,000 at its claimed limit. Require each tagged carrier's displacement to match the driver and the intended complete-state translation period (N3 ten ticks/+3; N4 twelve ticks/+4; mmw repeating phase can additionally be checked every six ticks/+2). Check conserved permanent kinds on every tick, equality of all encoded blocks plus movement owner lists at each translated cycle, and the added copy's minX relative to its predecessor at equal phase. Probe copied initial states with RNG [0,1,2,5,42] and X/Z phases independently [0,7,8,15] after sustained candidates exist. A successful single attachment is insufficient; loads, recurrence, and endpoint contact must persist when a second and subsequent copy is appended.

Rust portable patterns: `flyers/WIP/experiments/astra_diagonal/verify.rs` (deleted; `git show 1222fbe:flyers/WIP/experiments/astra_diagonal/verify.rs`) (fixed eight-tick audit; adapt period and displacement), `flyers/WIP/experiments/sol_diagonal/audit_cycle.rs` (deleted; `git show 1222fbe:flyers/WIP/experiments/sol_diagonal/audit_cycle.rs`) (independent owner-aware audit). Prefer the `fastflyer-research` binary (`measure`/`batch`/`trace`) now; the old `flyer_measure`/`flyer_batch`/`flyer_trace_window` exes remain in `flyers/WIP/experiments/bin/archive/`. Python public editor APIs used by generators: Flyer(rng_state=5,push_limit=...), Block.piston(direction,state=...,sticky=...), Block.observer(direction,powered=...), Flyer.save/load/validate; generators manipulate _cells directly as established experiment code. Never score between separately saved states because serialization renormalizes chunks.

# Bounded repeated-schedule chain baseline, 2026-09-28

Preserved `chain_baselines.py` and the generated `derived_generator.py`, derived from existing hexsmart temporal routing. Only bounds and repeated span allocations change. These are closed rings of repeated phase blocks, not identical freely attachable extension copies: transversely circular/six-corner layouts require different per-carrier routes. Useful for proving that more carriers can maintain throughput while measuring attachment reach throughout the cycle.

All six seed-zero baselines ran exactly 10,000 Rust ticks at diagnostic PL100 with zero movement/extension failures and permanent-kind conservation at every tick:

| Speed | Phase-block copies | Carriers | Blocks | Distance | Maximum traced action |
|---|---:|---:|---:|---:|---:|
| 3 bps | 1 | 5 | 91 | 3000 | 18 |
| 3 bps | 2 | 10 | 179 | 3000 | 18 |
| 3 bps | 4 | 20 | 371 | 3000 | 20 |
| 3.333 bps | 1 | 3 | 66 | 3333 | 22 |
| 3.333 bps | 2 | 6 | 136 | 3333 | 23 |
| 3.333 bps | 4 | 12 | 256 | 3333 | 21 |

Evidence: `chain_results.json`, `chain_metadata.json`, `n*_copies*_s0_full.txt`; generator, compact runner source/API references, and representative flyer files retained here. Increasing copies does not pool action load across the whole ring, but local route length changes the maximum (18/18/20 and 22/23/21). Per-driver vs extension loads are not isolated because these baselines have no separate external driver.

**These safe interfaces fail a stricter all-phase nonpositive-minX screen.** `chain_metadata.json` gives every carrier's minX relative to its immediate predecessor over all nominal action phases, plus the stricter screen boolean. Most output carriers are ahead by one cell in some phases; the 20-carrier N3 routes include a two-cell excess. Repeating a whole phase block restores the same front-X boundary, but does not rescue individual carrier reach. Exact encoded-cell/owner-list signatures also vary at nominal period boundaries; do not call these strict repeatable extensions based on speed/conservation alone.

## Side lead: N3 PL18

Smart-router five-carrier seed0 uses sticky counts [14,14,13,13,14], rather than safe-router [14,14,14,14,15]. `n3_copies1_s0_pl18.flyer` ran 3000/10000 at encoded PL18, full traced max action18, zero failures, conservation. `n3_pl18_samples.csv` checks all80 RNG/phase samples at 10,000 ticks: every row distance3000, failures0, conservation true. Exact cell/owner signature recurrence varies, so this is not automatically a bank-ready strict recurrence proof. Investigating the angry-bit difference is separate from lowering capacity; no mechanics changed.

These full-cycle reach offsets are measurements, not proof that the intended backward-reach requirement fails: the user did not explicitly require output minX <= predecessor minX at every phase. This bounded baseline establishes sustained repeated-schedule operation and two useful capacity leads, but does **not** solve the user's repeatable low-PL extension requirement because modules are not identical and exact state/owner recurrence remains unproved. Next geometry work should shorten/reposition each output's rear pickup while retaining hardware ownership, and validate an actually duplicated module on a preserved driver.

Further side-lead checks: `n4_copies4_s0_pl21.flyer` (12 carriers) achieved3333/10000 at encodedPL21 with traced maximum21, zero failures and conservation (`n4_copies4_pl21_full.txt`). This has no phase/RNG audit yet and has256 blocks; it is a larger architecture, not the requested compact three-segment result. `tools/src/bin/sol-samples-ignore-angry.rs` masks only the encoded angry bit while retaining owner lists; all80 N3PL18 cases still show inconsistent ten-tick signatures (only10–26 of1000 boundaries equal their initial signature). Thus recurrence variation is not explained by the angry flag alone. Retain the strict repeatability caveat.

## Cleanup 2026-10-08

Only rebuildable binaries were removed: all `.pdb`, `research_runner.exe` (use `target/release/fastflyer-research`), `sol-mmw-samples` and `sol-samples-ignore-angry` (rebuild from the `.rs`). `sol-samples` is kept because other folders' notes and `speed_range_b_20260930/verify_speed.sh` invoke it.
