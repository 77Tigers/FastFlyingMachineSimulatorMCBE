# Sol execution backlog — 2026-09-26 (Astra planning pass)

## Active priority override — PL12/2500 before PL17/3000

The user's current order is strict: **first achieve a self-running 2.5 bps flyer at encoded push limit 12, then a 3 bps flyer at encoded push limit 17**. Do not spend effort on PL17 until PL12 is verified for 10,000 Rust ticks. Neither target has been achieved in the current pass. Do not promote short movement or high-limit fixtures.

New bounded PL12 findings from this pass:

- A self-running **hybrid front-push / rear-pull** has now been verified: `WIP/experiments/sol_pl12/hybrid/hybrid_pl14.flyer` advances 2539 blocks in 10,000 Rust ticks at PL14. It removes one normal rear piston and uses a backward sticky piston plus a moved observer to pull the rear carrier. Sol's rear reroute in `WIP/experiments/sol_pl12/rear_route/lead1_pl14.flyer` also sustains the run at PL14, reducing the tick4 rear normal push from 12 to 11 and tick6 sticky pull from 13 to 12. The remaining front strokes load 13 initially and 14 after the first cycle; **PL12 remains unmet**. Do not promote the PL14 design as a limit record, but retain it as the first genuinely repeating user-suggested pull topology.
- Replacing any of 9 original front slime cells with an observer in each of 6 orientations did not preserve the hybrid motion, even at PL20 (`search_n2_hybrid_observer_reuse.py`). On the rear reroute, deletion of front slime `(14,1,17)` makes the first two front strokes load12, but the next cycle's front stroke loads13. Deleting a second front slime and optionally adding one slime/honey/stone/glazed cell anywhere in the tested local box (4,584 new candidates) reaches at most distance1 at PL12 (`search_n2_hybrid_front_route.py`). This leaves temporal power-source relocation or different front support/pickup geometry as higher-value next work.
- Relocating the single observer through 1,560 local placements/orientations per limit found six self-running high-limit positions; the first three share the original action loads and the other three produce an early sticky retraction that still incurs recurring load13 (`search_n2_observer_relocate.py`). Replacing any existing honey/rod/slime cell with the observer (456 cases per limit) also failed to beat distance2 at PL12 (`search_n2_rear_observer.py`). A promising alternate source must change which blocks adhere, not just choose another observer coordinate.
- Replacing that observer with a stationary rod/redstone source in 1,820 local configurations per limit produced no self-running high-limit design (`search_n2_source_relocate.py`): continuous power prevents the sticky piston from resetting. For the current two-carrier contact, the observer's transient pulse is essential unless the source actually changes carrier between actions.
- An in-process 600-generation local optimizer started from the rear-rerouted hybrid plus front deletion. It preserved the first complete limit-12 cycle but never improved its distance2/24-tick score (`evolve_hybrid_pl12.rs`). This is a search result, not an impossibility proof.
- **New architectural lead under construction, not yet a flyer:** the historical two-carrier alternating `mwmw` schedule recycles each firing piston across both carriers. Let P0 fire in slot0 (each slot=2 Rust ticks). It stays behind while the support moves in slot1 and P0 retracts; the target picks it in slot2 after reset; the support picks it in slot3, leaving it two cells forward for the next cycle. P1 does the same with slots shifted by two. A promising one-interface stagger has support honey center `H=(q,0,0)` with observer above facing down into H; normal pistons P0 at `(q,0,+1)` and P1 at `(q-1,0,-1)`, both facing +X. Target slime pickup tails below the piston plane start at axial `q-1`; support honey side-pickup starts at `q`. After the target's slot0 move, P1 aligns with H; after support's slot1 move, H and P1 align again and the observer pulse can fire P1 in slot2. P0 is picked by target in slot2 and support in slot3, aligning with the new observer pulse for next slot0. **Need a Rust one-interface fixture, valid initial phase, and a closed second interface before any success claim.** Do not rely on initial `angry=True` as a power source: unpowered nonmoving pistons have angry cleared before updates.
- The verified PL13 two-carrier flyer still scores only distance 2 at PL12. Removing either honey `(16,0,15)` or `(16,1,18)` allows the return pair to move but strands a front piston; each reaches only distance 3. The actual first-cycle loads are in `WIP/experiments/n2_deletions/` and `probe_n2_deletions.py`.
- `search_n2_repickup.py` screened 430 one-honey reroutes; `search_n2_two_remove_one_add.py` screened 2,460 coordinated honey rewrites; `search_n2_conversion.py` screened 122 deletion/material conversions. None exceeded distance 3 in 80 ticks. These are bounded local results, not a lower bound on new topologies.
- Exact grid Steiner routing (`search_n2_steiner.py`) explains the local impasse. With the four original return-carrier terminals fixed at `(16,0,15)`, `(16,1,18)`, `(16,2,16)`, `(17,2,15)` and the two front strokes' occupied sweep excluded, the shortest connected honey set in the tested box has **10 cells**, matching the PL13 carrier. A 9-cell static route exists if the second return piston's front-sweep destination is allowed; Rust collision stops it after one block. This is a bound for those fixed terminals and that box only.
- A compact rod/spine reconstruction (`build_n2_spine.py`) reduced front action loads to 11–12, but the second front push meets the first piston's extended body, and no tested RNG avoided the sustained stall. A shifted-return-piston version delays power correctly but its honey connection requires at least 12 cells in the tested grid (`search_n2_rearshift_steiner.py`). A transversely shifted front pair supports both front moves at load 12, but its tested return pickup routes require at least 12 honey cells and stall (`search_n2_frontshift_steiner.py`). The next design needs different contact timing or a real front pull, not another local deletion of the PL13 honey tree.
- An in-process bounded genetic search (`evolve_n2.rs`) tried coordinated cell mutations from both the PL13 seed and the compact-spine variant. It improved partial matching but never sustained the required translated 2-block/8-tick cycle. Its WIP output is not a success.
- Making both return pistons sticky after deleting honey `(16,0,15)` gives a genuine but **slow** intermittent pull mechanism: 722 blocks after 10,000 ticks at PL12, versus the required 2,500. It repeatedly oscillates before moving again. Across 2,048 RNG/X-phase 160-tick screens of the two best sticky masks, the maximum was only 18 blocks, versus 40 required. One-cell honey/slime additions did not improve that ceiling (`search_n2_sticky_delete.py`, `search_n2_sticky_phase.py`, `search_n2_sticky_add.py`).
- Compact pure-push four-carrier squares/rectangles: 79 format-valid candidates from 108 center/seed combinations, minimum maximum sticky count 12, all distance 0 after 120 ticks at PL12 (`search_n2_fourseg_compact.py`). Two coupled six-block observer engines: 1,776 placements/material/pulse variants, best only 13 blocks after 80 ticks, matching the original 1.667 bps speed (`search_n2_dual_compact.py`). These bounded controls point toward a purpose-built mixed push/pull contact, not simple duplication.

## Latest Sol continuation — 2026-09-26

**Read this before the A/S backlogs.** Verified best limits are still PL13/2500, PL19/3000, PL22/3333 after10,000 Rust ticks. Bank has **52** verified rows now. A distinct four-segment 2.5bps ring at PL15 was added as `bank/pl15/four_segment_ring.flyer`; it scored2500 in the reference run and all20 sampled full-horizon RNG/phase runs. It is a platform for a hybrid push/pull engine, not a lower-limit record.

The user's final-push-to-front-pull mechanism **worked in a four-tick Rust fixture** at three RNG states: target X16→18. That fixture uses a one-time initially powered observer, so no self-running hybrid is claimed. A complete local/phase/seed search around the current N3 five-ring did **not** find PL18; the best shortened bridge stalls through an immovable obstruction despite initially reaching near3bps. No new N4 result was promoted. Exact files, bounds, and next physical obstacles are in `WIP/experiments/FINDINGS_CONTINUATION_2026-09-26.md`.

Next three concrete actions: **(1)** make the pull fixture self-powered for a repeating two-push cycle, using the four-segment ring's distinct same-phase A/C carriers and deleting one normal last-push site; **(2)** redesign the N3 pickup where the shortened bridge meets an immovable piston rather than repeating center/seed sweeps; **(3)** transplant the proven local pull sequence into one N4 interface at a high diagnostic limit, then measure whether the removed push hardware pays for support. Keep testing all three speed tracks.

## Latest direction from the user: improve ALL THREE speeds

**Astra's second planning pass; no simulations in this pass.** Work on reducing push limit and then size at **2.5, 3, and 3.333... bps**. Reaching the old3bps-at-PL20 milestone did not finish the3bps research. Current verified starting points are PL13/2500, PL19/3000, and PL22/3333. Seek PL12, PL18, and PL21 next, continuing toward lower limits, especially PL20 for3333. A smaller or more robust same-limit machine is useful secondary progress; identify which metric improved.

Give each speed a serious mechanism experiment before another large N4 sweep. Suggested order: **A01–A04 (common mechanism), A09–A12 (2.5), A21–A24 (3), A31–A33 (3.333)**. Use the old S tasks as supporting instructions. The40 A tasks below are new hypotheses/assignments, not successes. Batch caps from the operating contract still apply. Do not redo baseline/80-case robustness runs until a design actually changes.

### First reason carefully about the user's push-to-pull replacement

The proposal is `A pushes B; B pushes C; replace B's final advance by C pulling B`. **Changing who applies force does not by itself lower the limit:** pulling the same connected13-block payload still costs13. The possible saving comes from deleting a rear normal piston and its pickup/power structure, separating components previously dragged together, or moving hardware onto a carrier with spare capacity. Account for every action in every carrier after the change. Never sum concurrent piston capacities to move one oversized connected load.

There is a clean *candidate timing pattern* for all three speeds. Let B move during action slots `0..N-1`, then wait two; let C lead B by two slots. Each action slot is two Rust ticks. C is stationary during B's final two moves. A backward sticky piston on C can extend in B's penultimate move and retract in its last move, then be retracted before C next moves. These are scheduling hypotheses; contacts, power, ownership, and closure still need Rust verification.

| Target | B's motion over one cycle | C's motion | C extends backward | C pulls B | C next moves |
| --- | --- | --- | --- | --- | --- |
| 2.5bps | `mmww` | `wwmm` | slot0, ticks0–1 | slot1, ticks2–3 | slot2, tick4 |
| 3bps | `mmmww` | `mwwmm` | slot1, ticks2–3 | slot2, ticks4–5 | slot3, tick6 |
| 3.333...bps | `mmmmww` | `mmwwmm` | slot2, ticks4–5 | slot3, ticks6–7 | slot4, tick8 |

**Contact arithmetic, before actions:** for a stationary -X sticky piston at base X=q, put its future pull target at X=q-3 before the penultimate push. That push takes the target to q-2 while the sticky piston extends into empty q-1. Retraction then takes the target to q-1. Check the entire target shape and arm swept space, not only this one cell. A layout based on the target's post-move position is off by one. The simultaneous penultimate push/extension must work in either piston order.

**Power is a real unresolved part.** An observer riding C pulses after *every* completed move, so it can prematurely extend the sticky piston before C's last required movement and jam it. Do not assume its final-move pulse is the only pulse. A promising alternative is a source riding B: arrange it to align with the sticky piston's side/back only when C parks, then let B's penultimate advance move the source out of range. A side source initially at `(q,y+1,z)` is an adjacency sketch; earlier poses, moving-source suppression, connection cost, and all unintended powered pistons must also pass. Do not place the only source in the ignored -X front face.

**Two segments are not an automatic blocker for2.5bps.** In a two-segment cycle, A and C can be the same carrier, with different push and pull sites. Alternatively use four phases `[0,2,0,2]` so A and C are distinct carriers with identical timing. The latter still satisfies the pure template's phase closure and has an even material loop. More total blocks can be worthwhile if the maximum moving load falls. A three-segment mixed push/pull machine is another hypothesis, but its timing must be derived anew; do not run N2/k3 through the unchanged pure-push generator.

### Common mechanism experiments

- [ ] **A01 — Test one final-push replacement locally.** Build a tiny Rust-tested penultimate-push/extend/retract fixture using the q-3 contact rule. Show one-block forward pulling and both possible action orders. Label the fixture externally supported; it is not a self-propelled flyer.
- [ ] **A02 — Build a motion-switched power fixture.** Try one source on B and the -X sticky piston on C; enumerate side/back source offsets near one contact. Output tick-resolved power proving correct extension, subsequent retraction, and absence of premature firing in the whole cycle.
- [ ] **A03 — Audit observer gating.** If a moved observer supplies the pulse, explicitly test every earlier move of its carrier. Try relative-position gating through an existing solid or a source picked up only on the final carrier move. Save the first false pulse as a reproducer.
- [ ] **A04 — Close the support cycle.** After the local fixture works, track support piston, source, arm, and any connector for two complete cycles. Require the support to finish retraction before its carrier moves, and restore its relative position without an external pusher.
- [ ] **A05 — Compare whole-cycle load costs.** For a push-only reference and its hybrid, tabulate removed normal pistons/pickups, added sticky pistons/sources, and every actual load. Reject changes that merely transfer an excessive load to another carrier.
- [ ] **A06 — Replace one interface first.** Keep the other interfaces unchanged while validating one hybrid. Then consider replacement at two nonadjacent interfaces and finally all interfaces. Save which dependency breaks when the second replacement is added.
- [ ] **A07 — Determine which piston is removed.** Shared power changes firing order; deleting a geometrically named piston need not delete the *last* action. Either make all remaining normal sites interchangeable or gate the retained pushes. Verify all observed orders, not just the generator's initial permutation.
- [ ] **A08 — Separate phase initialization from self-reset.** Use allowed format-valid extended states to expose a mechanism quickly, but require a repeating translated cycle with identical physical state and valid owners. A one-time initialized pull or stationary external anchor is only a fixture result.

### 2.5bps: first priority for trying the user's hint

- [ ] **A09 — Try one push plus one pull on the existing two carriers.** Begin from `two_push_crosslayer_pl13.flyer`; attempt to replace a load13 return push by a backward sticky piston mounted on the opposite end of its source carrier. Use the N2 table; trace exactly which removed hardware leaves the overloaded payload.
- [ ] **A10 — Try the four-segment N2 hybrid.** Design phases `[0,2,0,2]`, with distinct A/B/C for the user's replacement. Start from an explicit schedule, then route. Compare peak load with the two-carrier variant even if the four-segment design has more total blocks.
- [ ] **A11 — Use the existing PL13 asymmetry.** Its front load is12 and return load13. First seek a hybrid that deletes at least one member from *each* overloaded return action while adding hardware only where spare capacity exists. Output a load ledger before spending on geometric sweeps.
- [ ] **A12 — Put the pull-power source on the existing powered carrier.** Try sharing its rod/redstone with the new backward piston through timed alignment. Output whether one source can serve both the normal push and sticky extension without holding the sticky piston powered through the pull.
- [ ] **A13 — Revive the rod/spine lead as a topology rewrite.** Implement old S21's y1,z0/2 piston pair and y1,z1 spine, with a rod hard-powering from below. Explore return pickup on both lateral sides. The previous broad safe-cross N2 sweep did not test this custom topology.
- [ ] **A14 — Combine the spine lead with a final pull.** Use A13's compact front structure but let a front-mounted sticky piston recover the return carrier. Solve the documented return-piston intersection by changing which carrier owns the final movement, then measure both loads.
- [ ] **A15 — Test staggered rather than planar pickup.** For N2's two piston sites, use separate axial pickup heights/offsets matched to retraction completion. Output a two-site pickup that needs fewer connector cells and works for both firing orders, or identify the order it necessarily depends on.
- [ ] **A16 — Replace permanent connectivity with timed contact.** Look for a return connector needed only during one of the two moves. Test collision-driven forward transfer during that action and adhesion pickup during the other. Require every piece to rejoin; falling-off blocks are failure, not savings.
- [ ] **A17 — Try mixed push/pull on three carriers.** Enumerate short schedules with2 forward blocks/8 ticks before routing. Keep source/action reset states explicit. Reject schedules with an extra hidden wait; the pure two-slot-lag closure formula does not certify this mixed topology.
- [ ] **A18 — Reconstruct the historical four-piston idea.** The old notes mention two normal pistons, two sticky pistons, two observers, and two slime segments at2.5bps. Turn that claim into a concrete schedule and fixture, comparing its load budget to PL13. Treat the description as a lead, not an existing verified build.
- [ ] **A19 — Try mirrored push/pull roles, not just mirrored geometry.** Compare B pushed first/pulled second with the alternative order under a newly derived cycle. The latter may free a different carrier from carrying a piston, but must still advance2 blocks in8 ticks.
- [ ] **A20 — Pursue lower limits after the first PL12 success.** Fully verify PL12, then try PL11/10 by deleting mechanism overhead identified in the successful load ledger. Keep a smaller robust PL13 design as secondary progress if PL12 is still unmet; avoid more blanket local mutation of the old seed.

### 3bps: active research, not a completed checkbox

- [ ] **A21 — Establish a PL18 bottleneck map.** Start from `three_push_ring_pl19.flyer`, use the existing19-run as control, and trace the first failed18-run. Name every distinct load19 action and its carrier. Prioritize shared bottleneck cells rather than optimizing the biggest visible structure.
- [ ] **A22 — Transfer the proven N4 routing improvement to N3.** The successful N4 change was a different center arrangement that shortened one carrier, not a new simulator rule. Perturb N3's five centers around the verified arrangement, ranking predicted connector savings, then screen only fresh layouts at18.
- [ ] **A23 — Test two pushes plus a front pull.** Apply the N3 timing row at one five-ring interface: normal pushes in slots0/1, C's pull in slot2. Remove one normal firing site and its now-unneeded pickup branch where feasible. Charge the new support hardware to C's actual movement sets.
- [ ] **A24 — Exploit the unused fourth cross arm.** N3 occupies three transverse piston sites. Test the vacant site as a backward sticky mount or a rod-to-solid power route, checking that its arm and pickup path do not intersect an active normal piston. This may avoid widening the interface.
- [ ] **A25 — Enumerate missing-arm patterns deliberately.** At each three-piston cross, choose which of four arms is absent to face its nearest connector. Keep firing permutation separate from site selection. Try a small coordinated set of patterns across the five interfaces rather than random whole-generator seeds.
- [ ] **A26 — Optimize the odd-loop material seam for N3.** There are five possible seam locations in an alternating five-ring. Move the seam to the pair with greatest phase-resolved clearance and reroute just those carriers. A global slime/honey swap leaves seam location unchanged.
- [ ] **A27 — Reallocate N3 axial spans.** For the existing pure-push phases `[0,2,4,1,3]`, the generator's span closure sum is16. Compare balanced `[3,3,3,3,4]` with allocations giving shorter spans to the worst carrier; verify closure and collisions. Don't copy the N4 sum10.
- [ ] **A28 — Replace a three-site rear cross with a purpose-built cover.** Enumerate the minimal contact sites for the actual three piston positions, including corner/side combinations and one staggered site. Count connected cost and unwanted pickups; a generic four-arm pickup may preserve unnecessary structure.
- [ ] **A29 — Try shared power across a phase boundary.** Search a single source/solid pair that powers the departing segment's final normal piston and the arriving segment's support at different times. Save a power truth table and full load delta; no source sharing without temporal isolation.
- [ ] **A30 — Recover the historical assisted-chain family.** Build a3bps schedule with a rear push chain and front sticky supports from the older notes, then close every support's reset. Compare its maximum load and block count with the94-block five-ring. Verify any PL18/17 improvement at10k; compact PL19 is also useful.

### 3.333...bps: change the mechanism where repeated geometry sweeps stopped helping

- [ ] **A31 — Make the N4 three-push-plus-pull interface.** Use `four_push_ring_pl22.flyer` as control and the N4 timing row. Build one hybrid at a high diagnostic limit first to establish recurrence; then measure whether deleting the fourth normal piston/pickup actually improves21/22-block actions.
- [ ] **A32 — Search span changes for pull contact, not standalone speed.** The108 old span candidates tested the unchanged all-push design. Revisit only allocations that produce the required pre-pull contact gap or eliminate a support connector in A31; score their hybrid geometry, not the old heavy interface.
- [ ] **A33 — Audit and repair the PL21 failure's causal link.** Start before its first deviation, not only at tick153. Capture the link by which an extra cell/piston joins a load. Modify that attachment or its owner/phase specifically; the static `[16,16,15]` counts do not identify the dynamic cause.
- [ ] **A34 — Decouple pickup topology from front-drive topology.** Keep the known front cross and substitute a side/staggered rear pickup at only one interface. The prior side generator changed every interface at once. Require sustained high-limit behavior before attempting lower-limit savings.
- [ ] **A35 — Budget every actual piston carried.** The familiar `sticky+one source+four pistons` is an empirical budget, not a universal minimum. Test whether one piston can stay with a different carrier until just before it fires, using timed pickup, without losing its next cycle's stroke.
- [ ] **A36 — Optimize six segments on peak load.** The six-segment seed is now10k-verified at30; measure it at23 and below first. Its alternating materials remove the odd-loop seam. Try short bridges that failed specifically through same-material adhesion in the triangle, checking new cross-ring contacts.
- [ ] **A37 — Fold the six-ring in three dimensions.** Keep alternating materials and correct phases, but bring each front/pickup pair closer through a staggered vertical layout instead of enlarging a planar hexagon. Output the changed longest-route length and actual maximum load; total size is secondary.
- [ ] **A38 — Search asymmetric piston sites.** Replace the symmetric four-arm cross with a compact row/L-shaped or staggered interface powered through an existing solid. Derive its power and pickup coverage explicitly; symmetric geometry may be spending cells on a site that a hybrid no longer needs.
- [ ] **A39 — Split a carrier only with a complete drive plan.** At an overloaded bridge, explore two nonadhering subcarriers moved by separate actions at the same scheduled rate. Specify both drivers, synchronization, pickups, and sources first. Two pistons touching one connected load do not add their capacities.
- [ ] **A40 — Follow intermediate improvements through.** Preserve and verify a structurally new PL21 flyer if found, then target PL20 with the next specific overloaded action. Limit long robustness batches to surviving designs; spend failed-family time on a different mechanism, especially the2.5/3bps tracks.

## Current verified state after Sol's research run — 2026-09-26

**New result:** `WIP/four_push_ring_pl22.flyer` reaches distance3333 after exactly10,000 Rust ticks at encoded PL22 (66 blocks, 10,000 extensions). It passed all80 sampled full-horizon RNG/X/Z phase combinations. This improves the earlier PL23 N4 minimum. PL20 at3333 and PL12 at2500 remain unsolved. The complete run record, bounded negative results, and the user's proposed pull timing window are in `WIP/experiments/FINDINGS_2026-09-26.md`.

The main PL21 lead used a five-cell bridge and reduced static sticky counts to `[16,16,15]`, but it stalled in all80 sampled full runs; a tick153 push-limit failure tried to move22 blocks. Do not promote its 120-tick distance40 screen. The preserved PL23 and PL13 WIP seeds remain reference controls. The latest A tasks above now set the order across all three speed tracks. The earlier handoff's “PL23 best” statement is historical.

The 60 items below were drafted before the research run. Use the current verified state and findings linked above to avoid repeating completed searches. Unchecked items are still useful work, but some now have partial evidence; an unchecked box does not erase the newer results. The older handoff and design reference are preserved below.

## Objective and operating contract

- Primary tracks: **2500 at PL12 or lower; improve3000 from its current PL19 toward PL18 and below; improve3333 from PL22 through PL21 toward PL20 and below**, each measured after exactly10,000 Rust simulator ticks. Smaller, more varied, or more robust same-limit machines are useful secondary results. The old PL20/3000 milestone does not retire the3bps track.
- Use the supplied Python editing library for candidates and actual Rust simulation for results. Do not change simulator, library, viewer, format, or unrelated project code. Put research scripts, standalone Rust diagnostic sources, candidate files, and evidence under `flyers/WIP/`; promote verified designs to `flyers/bank/`.
- Preserve the three named WIP reference flyers and existing bank entries. Work on copies. No ballast, detached debris used to manipulate the minimum-X score, favorable initial-phase score padding, or unsupported impossibility claims. Format-valid initial states are allowed; Minecraft startup reachability is a separate question.
- A task may finish with a useful negative result: include the tested family, bounded search range, first causal failure, and a reproducer. Mark it `[x]` only when its stated output exists. Record status beside the ID as `DONE`, `NEGATIVE`, `BLOCKED (dependency)`, or `DEFERRED (reason)`; reference evidence paths.
- Do not implement the whole tooling backlog before designing. The original suggested first pass was **S01 -> S02 -> S06 -> S07 -> S21 -> S22 -> S23**, then **S08 -> S31 -> S32 -> S33**; the latest findings supersede this ordering where they supply evidence. Pull generator fixes S11–S20 only as needed by the selected experiment. S41–S48 are conditional research, not mandatory prerequisites.
- Initial budget per design experiment: at most **500 unique candidates or 10 minutes of search**, whichever comes first. Record actual usage. Continue a family only when it lowers an observed bottleneck, extends sustained operation, or exposes a new failure mechanism. Use small deterministic grids before random expansion. A failed family is not proof of impossibility.
- Screen with short Rust runs, then 300/1,000 ticks as useful, then exactly10k for claimed results. Short-run scores are phase-sensitive: inspect cycle displacement and failures rather than demanding an exact scaled10k score. Never promote an 80-tick minimum-limit screen as a verified minimum.
- Use detailed traces only around early cycles/failures; do not accumulate10k detailed traces per candidate. Keep resumable summaries and the best/failing representatives, rather than thousands of indistinguishable files.
- Do not spawn agents just because tasks are independent. Execute as Sol unless the user separately authorizes delegation. No external research or in-game work is required to execute this queue.

## Evidence and reasoning that should guide Sol

**Load is the binding objective.** PL13's reported front loads are12 and rear loads13: fix every overloaded rear action while preserving the front. For PL23 N4, optimizing total block count is insufficient; optimize the maximum actual movement set. The reported sticky counts `[16,18,17]` plus carried blocks suggest several segments need savings. Count each action before deciding how many cells must disappear.

**The two-slot lag is an assumption of the current pure-push template.** Under that model, `k_min = (N+2)/gcd(2,N+2)` and speed is `5*N/(N+2)` bps: N2 gives2 segments/2.5bps, N3 gives5/3bps, N4 gives3/3.333...bps. Derive other schedules separately. An extra idle slot may reduce load but also misses the speed target unless compensated elsewhere.

**Odd material loops create a routing problem, not an impossibility theorem.** Alternating slime/honey around three or five segments leaves a same-material seam; spatial separation can make that seam harmless. Six N4 segments remove that particular seam but add routing and load. Compare measured costs rather than assuming six is better.

**The generator currently has several unchecked assumptions.** `safe`/`smart` use a fixed routing box and cost cutoff, random sequential routing, fixed span allocation, and a single initial permutation. Their `seed` chooses geometry while `Flyer(rng_state=5, ...)` fixes simulation RNG: these are distinct variables. Dictionary writes can overwrite overlapping mandatory blocks before validation. The cross template has only four piston sites, so passing N>4 cannot implement an N-piston interface. These are reasons to improve research generators, not the physics engine.

For every batch, record task ID, generator revision/hash and parameters, parent candidate, **geometry seed separately from simulation RNG**, push limit, X/Z phases, serialized candidate hash, validation result, tick budget, score, max observed load, first failure, and evidence path. Use JSONL or CSV under `WIP/experiments/`. Keep original saved coordinates and normalized loaded coordinates distinguishable.

## A. Reproduction and causal diagnostics

- [ ] **S01 — Inventory the preserved state.** Check that all three named WIP flyers and all51 CSV entries have matching files; load/validate and record encoded limits, RNG, phases, and hashes. Output `WIP/experiments/inventory.jsonl`; list missing/inconsistent entries without changing them.
- [ ] **S02 — Make Rust measurements reproducible.** Locate usable temporary tools, or save standalone runner source and build instructions under WIP using public Rust APIs. Record the actual library/build used; don't hard-code the old rlib hash. Output distance, start/end minX, blocks, extensions, ticks, and elapsed time. Check one saved baseline before bulk use.
- [ ] **S03 — Add a resumable screening driver.** Generate with Python, validate/save/reload, invoke Rust, and record outcomes. Deduplicate identical serialized inputs and support a candidate/time cap. Output a tiny successful batch and an invalid/stalled case; a subprocess timeout must be recorded as a timeout, not physical failure.
- [ ] **S04 — Export compact action evidence.** Use `tick_traced`/`TickTrace` to capture active piston, source/destination sets, failure and discovery links, power links, and owners for a requested tick window. Output one cycle trace per reference. Keep successful loads distinct from incomplete discovery sets on failed pushes.
- [ ] **S05 — Build an action/load ledger.** From traces, label front/rear interface membership and break each successful load into sticky, power, piston, and other cells. Output per-action membership and maximum load per segment. If PL rejects discovery early, use a clearly labeled higher-limit diagnostic copy to inspect the intended full set.
- [ ] **S06 — Reproduce the PL13 seed.** Run `two_push_crosslayer_pl13.flyer` for10k at13, then a copy at12. Output both scores and the first PL12 divergence with a causal trace. Confirm or correct the historical claim that only return actions exceed12; retain the original file.
- [ ] **S07 — Identify the PL12 deletion target.** For every load13 return action in S06, compute the common carried cells and why each enters the load. Output a ranked list of removable/reroutable cells and collateral front-load effects. A cell absent from some bottlenecks cannot alone solve all of them.
- [ ] **S08 — Reproduce the N4 seed.** Run `four_push_ring_pl23.flyer` at23 for10k and screen copies at20–22. Output the first failing action at each limit plus the high-limit load ledger. Distinguish excess count, immovable obstruction, unintended adhesion, and power loss.
- [ ] **S09 — Reproduce the N3 control.** Rerun `three_push_ring_pl19.flyer` at19 for10k and a copy at20. Save compact cycle evidence. Use this known3000-distance family as a regression control when changing ring generation; do not assume a larger limit always preserves timing.
- [ ] **S10 — Detect repeating shape and sustained motion.** Compare relative block states, flags, and moving-owner lists over cycle boundaries, track minimum-X increments, and count blocks by kind excluding transient arms. Output periods/translations or the first mismatch. Shape recurrence alone is not a deterministic proof: RNG and world chunk phase also affect future updates.

## B. Generator correctness and efficient search

- [ ] **S11 — Guard template inputs.** In a new WIP generator revision, reject unsupported N, duplicate centers, and loops violating `2*k % (N+2) == 0`. Output explicit rejection examples and successful N2/N3/N4 generation. A different lag/topology needs its own validator.
- [ ] **S12 — Reject mandatory-cell collisions before insertion.** Track intended owner/role of each piston, arm, power, and sticky cell at every modeled phase. Reject incompatible overlaps before dictionary/set writes erase the conflict. Output a collision witness and known-seed results; allow only explicitly justified shared roles.
- [ ] **S13 — Validate mandatory geometry as well as connectors.** Audit cross cells, pickup cells, and final routed cells for intersegment collision, unwanted adhesion, and unintended piston/power contact across phases. Output reason-coded rejection counts. Don't apply the connector's blanket adjacency ban to intentional piston contacts.
- [ ] **S14 — Check every required pickup component is connected.** Replace fixed connection counts or single-target assumptions with connectivity-to-completion and an explicit failure. Output component maps for a full cross and both side-corner choices. Already-connected terminals should succeed with zero extra cells.
- [ ] **S15 — Make generator outputs reproducible.** Sort set-derived starts/iterations and separate geometry RNG from simulation RNG. Save all generation parameters. Generate a small batch twice and compare serialized hashes; failures must reproduce too.
- [ ] **S16 — Expose search bounds.** Parameterize routing box, path-cost cutoff, and candidate limits. Record `out_of_box`, `cost_cap`, and `no_legal_route` separately where detectable. Test one expanded-box control before attributing a failed family to geometry; report bounded failure precisely.
- [ ] **S17 — Expose interface spans.** Parameterize the per-segment axial span vector, derive its closure condition from the phase equations, and enumerate bounded integer allocations with the same total. Output valid allocations and measured best load versus the existing fixed allocation. Validate final geometry at the seam.
- [ ] **S18 — Reduce route-order bias.** For the three-segment N4 case try all six routing orders and a bounded set of tie-break seeds, rerouting the current largest-load segment first. Output Pareto candidates by maximum load, total blocks, and size, with Rust results for finalists.
- [ ] **S19 — Separate contact safety from order conservatism.** Tabulate allowed carrier/piston adjacency by phase, owner, and movable state. Compare `safe` and `smart` rejection reasons on identical proposed cells. Output specific newly admitted contacts with Rust witnesses; potential-position unions may reject valid layouts and must not be treated as necessity proofs.
- [ ] **S20 — Audit action-slot abstraction against actual ticks.** Expand one modeled cycle into both simulator ticks per action slot, including moving flags, arm removal, cached power, and pickup ownership. Output the first discrepancy on a failing generated candidate and one passing control. Correct the research model only where traces justify it.

## C. Primary target: PL12 at2.5bps

- [ ] **S21 — Implement the preserved rod/spine lead.** Build the stated front B piston pair at y1,z0/2 with spine y1,z1 and rod at x0,y0,z1 pointing+Y, using explicit local coordinates and phases. Output a valid candidate, phase drawing/table, and Rust trace locating the reported return-piston intersection. Treat this as an experiment, not a proven seed.
- [ ] **S22 — Resolve that intersection systematically.** Starting from S21, vary the return honey pickup's lateral side, axial offset, and one-cell vertical offset in a small named grid. Output the best candidate and exact front/return load ledger; stop variants that collect an idle piston early.
- [ ] **S23 — Enumerate local hard-power placements.** Around the S21/S07 bottleneck, test rods facing each eligible existing solid, keeping direction and stationary timing explicit. Remove a redundant source only when all intended firings remain powered. Output the least-loaded valid power arrangement and its complete-cycle trace.
- [ ] **S24 — Test side pickup instead of a rear spine cell.** Enumerate the face-neighbor sites that can collect each recycled piston after retraction, then connect the smallest covers. Output covers, required connectors, and Rust screens. Account for displaced blocks and avoid an apparently smaller pickup that costs more routing.
- [ ] **S25 — Move power off the overloaded return carrier.** Try mounting its source on the other segment or an existing shared solid. Output a tick-by-tick power/position table before building and compare return loads afterward. Reject sources that move during the required power stage or power an extra piston.
- [ ] **S26 — Rebalance asymmetric segment geometry.** Allow unequal axial spans and different transverse arrangements for the two interfaces; optimize each return bottleneck rather than requiring symmetry. Output the bounded parameter grid and best maximum load. Preserve the two-slot timing relation unless separately rederived.
- [ ] **S27 — Search coordinated bridge rewrites.** Around the S07 causal bottleneck only, replace a connector subpath with another connected subpath of fewer cells, allowing several edits at once. Output topology before/after and trace evidence. Do not repeat the already exhausted unrestricted delete/relocate neighborhoods.
- [ ] **S28 — Test orientation/topology alternatives for N2.** Compare opposite versus adjacent piston sites around a shared source, and crossed versus parallel front/return layers. Output at least one valid representative per feasible family and actual max load; a simple mirror counts as a control, not a new topology.
- [ ] **S29 — Model a push/pull replacement.** Write a complete two-block cycle using a sticky pull to replace the overloaded return push, including source reset and load ownership. Build only schedules meeting2 blocks/8 ticks. Output either a valid screened candidate or the first specific timing/geometry contradiction.
- [ ] **S30 — Verify the best PL12 candidate.** If a candidate survives screening, run exactly10k at encoded12, inspect shape/block conservation and sustained cycles, then run the initial robustness sample in S49. Output the flyer plus evidence. If none passes, summarize the best near miss and next causal change without claiming impossibility.

## D. Primary target: PL20 at3.333bps

- [ ] **S31 — Set per-action saving budgets.** From S08, list all loads>20 and the cells common to each segment's overloaded actions. Output how many net removals/reroutes each action requires; include newly introduced connector/source costs. Prioritize changes that improve several bottlenecks together.
- [ ] **S32 — Compare rear pickup covers.** For the four piston sites, enumerate full-cross, cross-without-center, opposite-corner, and mixed rear/side pickups. Model every required firing/pickup phase. Output contact coverage, connected cost, and Rust behavior; covering four sites statically does not establish safe pickup timing.
- [ ] **S33 — Repair the side-contact generator family.** Apply S12–S14 to `astra_ringgen_side.py` in a new revision; derive the changed axial span closure instead of inheriting it blindly. Output one completely connected candidate, or a bounded routing failure, with the first segment-merging link identified in Rust.
- [ ] **S34 — Test center spacing4 versus5.** Use a small matched triangle grid with comparable spans/materials and identical geometry-seed sets. Output load and early-pickup failure rates plus shortest successful routes. Widening spacing is useful only if its safety benefit exceeds connector cost.
- [ ] **S35 — Optimize the axial spans of the triangle.** Apply S17 to the verified N4 centers `[(0,0),(0,4),(2,2)]`, then the best S34 centers. Output best max load at each span vector; check the closing interface explicitly. Avoid rerunning the old138-placement sweep unchanged.
- [ ] **S36 — Relocate the same-material seam.** Enumerate the nontrivial slime/honey assignments for three segments and route around the seam. Output seam clearance over a whole cycle and best load. Global material inversion is a control; moving the seam may change route cost.
- [ ] **S37 — Replace shared redstone only where it saves net load.** Enumerate rod-to-existing-solid power at each N4 interface, with all four pistons' required power times checked. Output net cell/load savings after including rod pickup and extra connections. Replacing one source with one source is not automatically a saving.
- [ ] **S38 — Allow selected correct-phase contacts.** Use S19/S20 to admit only a small named set of contacts rejected by `safe`, and reroute the longest bridge. Output the reason each contact is safe at each tick, plus Rust screens across several RNG states. Do not globally disable adjacency checks.
- [ ] **S39 — Minimize the worst movement set directly.** For a promising topology, score proposed connector rewrites by traced maximum load, number of overloaded actions, then total blocks. Output the nondominated candidates. Keep source sharing, early piston pickup, and destination obstructions in the objective/evaluation loop.
- [ ] **S40 — Verify the best PL20 N4 candidate.** Run a screened survivor at encoded20 for exactly10k and require distance>=3333 with sustained four-block/12-tick behavior, then S49. Output the candidate and evidence; retain PL21–23 improvements as WIP stepping stones if20 is still unmet.

## E. Conditional design branches (only after cheaper leads)

- [ ] **S41 — Finish the six-segment control.** Reproduce the recorded hex-family seed5 if its parameters can be recovered; otherwise record that missing provenance and generate a new named control. Run the high-limit survivor for10k before optimizing it. Output a complete-cycle and load ledger, not another300-tick success claim.
- [ ] **S42 — Compare matched three/six-segment designs.** Use the same pickup/power family and bounded routing effort. Output maximum load, total blocks, connector cost, and seam-related failures. Continue six segments only if it improves a relevant bottleneck or opens safe contacts unavailable in the triangle.
- [ ] **S43 — Prototype N4 push–push–push–pull timing.** Write all segment positions, ownership, and piston reset states over a complete cycle, targeting4 blocks/12 ticks. Output a schedule feasibility result before geometry. Reject any proposal whose last support cannot reset or be recovered.
- [ ] **S44 — Test mixed movement patterns.** Enumerate relative phase offsets of the historical `mmwmmw` support against `mmmmww`, explicitly declaring an action slot as two simulator ticks. Output contact windows and net translation over their common period. Build only cases with valid pull distances and resets.
- [ ] **S45 — Explore a different interface lag.** For one concrete push/pull mechanism derive lag d, its permissible action schedule, and loop closure `d*k mod L=0` when that model applies. Output the derivation and one local interface test; changing the congruence alone does not create a physical mechanism.
- [ ] **S46 — Measure local geometric lower bounds.** For fixed terminals and a stated finite legal-cell set, compute minimum connected pickup/bridge cost or a valid lower bound. Compare it with S31 budgets. Output assumptions and scope; this may rule out a template/box, never all PL20 flyers.
- [ ] **S47 — Optimize existing3bps rings belowPL19.** Apply only demonstrated pickup/routing savings to the verified five-segment seed. Screen lower encoded limits and fully verify any improvement. Output an intermediate bank-quality result if the harder N4 target remains open.
- [ ] **S48 — Explore a new N2 topology forPL10/11.** After learning a concrete saving from PL12 work, apply it to the lower limits. Output bounded experiments and full10k survivors. Do not divert into larger-N engines or raise the requested limits merely to accumulate fast records.

## F. Reliability and evidence quality

- [ ] **S49 — Run a small robustness screen.** For each novel target survivor use RNG states `[0,1,2,5,42]` and all16 combinations of phase_x/phase_z in `[0,7,8,15]`, initially300 ticks. Output the actual serialized starts and pass/failure matrix; these80 runs are a sample, not exhaustive order coverage.
- [ ] **S50 — Run full-horizon phase coverage for finalists.** For the strongest candidate per target, test all256 X/Z phase pairs at10k for its saved RNG, then the S49 phase sample for the other four RNG states at10k. Output minimum/median/max score and failures. Preserve differing outcomes rather than choosing a favorable alignment.
- [ ] **S51 — Turn a robustness failure into a witness.** Find the earliest mismatch against a passing run, save the initial inputs and a small tick window, and classify chunk order, piston order, lost power, merge, collision, or count. Output the smallest useful causal explanation; a late score difference alone is insufficient.
- [ ] **S52 — Check conservation and ownership.** On promoted candidates compare non-arm block-kind counts and segment connectivity across cycles, inspect leftover moving flags/owner lists, and identify detached or stationary pieces. Output any discrepancy with its first tick. End block count alone can change with arm phase and is not enough.
- [ ] **S53 — Report startup and steady-state separately.** Record the authoritative initial-to10k score plus complete-cycle displacement after startup. Compare several naturally reached cycle checkpoints only as diagnostics. Output any transient/phase contribution; don't select a new start merely to gain one scored block.
- [ ] **S54 — Use transformations as checks.** For promising designs test Z reflection, transverse Y/Z interchange with all directions/owners transformed, and slime/honey inversion, preserving+X travel. Output transformed10k results and classify geometry versus world-phase effects. Avoid Y-axis rotations that turn travel away from+X while retaining the same score interpretation.

## G. Bank completion and next handoff

- [ ] **S55 — Audit bank coverage and variety.** Count valid designs per limit10–20 against the required3–13 range; group simple material/orientation copies separately from topology families. Output gaps and redundant entries. Existing baselines may remain, but don't present copies or ballast as novel engines.
- [ ] **S56 — Propagate verified improvements carefully.** For a newly solved low-limit design, create useful higher-limit copies/variants where they improve bank quality, then rerun at each encoded limit. Output only verified additions, keeping each bucket within13. Higher limits can change failure-dependent timing.
- [ ] **S57 — Add useful geometric variants.** From a successful topology produce compact, upright, and alternate-routing designs where feasible, using S54 controls. Output distinguishing geometry/load notes and full10k evidence. Prefer meaningful alternatives over filling all13 slots mechanically.
- [ ] **S58 — Reconcile results and provenance.** Update `bank/results.csv` only from verified runs; retain its existing schema and store hashes, RNG/phases, runner provenance, and robustness results in a companion manifest. Output a consistency check for filenames, encoded limits, rows, and exact tick horizon.
- [ ] **S59 — Preserve failed-search knowledge.** Maintain `WIP/experiments/negative_results.md` keyed by task ID and topology, with parameter ranges, counts, causal failures, and one reproducer. Explicitly carry forward the prior PL12 mutation counts and triangle sweep so future runs don't unknowingly repeat them.
- [ ] **S60 — Refresh this handoff after each substantial session.** Put achieved targets, best verified seeds, next three actions, evidence paths, and unresolved mechanisms above the historical notes. Include one reproducible command per winner and remaining robustness gaps. Keep failed hypotheses labeled and never convert a screen into a verified result.

---

# Historical handoff — 2026-09-26 (Astra, before backlog planning)

This section records the state at the prior stopped search. Its completed-result claims remain the reference baseline until rerun. Its stop/resume statements describe that earlier session; the current Sol queue is above.

## User requirements and current results

Build varied flyers for push limits 10 through 20, 3–13 designs per limit. Use the provided Python editing library and actual Rust simulation. Score = minimum occupied X after exactly 10,000 simulator ticks minus minimum occupied X before simulation. A simulator tick is 0.1 seconds, so distances 2500/3000/3333 mean approximately 2.5/3/3.333 bps. Any format-valid initial state is allowed. Do not pad with ballast, game initial phase for a one-block score gain, or modify simulator/project code. User prefers useful work delegated to Sol and difficult design reasoning done by Astra.

Latest requested targets: (1) 2.5 bps at push limit 12; (2) 3 bps and 3.333 bps at push limit 20. **Only the 3 bps target is complete.** Best 2.5 bps is now PL13; verified 3.333 bps currently needs PL23. Neither PL12 nor PL20-for-3.333 has been achieved or disproved.

Bank now has 51 flyers. `bank/results.csv` includes all saved results. PL10–12 retain three trivial 1666-distance baselines each. PL13 has five new 2500-distance variants; PL14–18 have 2500-distance designs. PL19 and PL20 each now include two genuine five-segment 3000-distance rings (`five_segment_ring_low.flyer` and `five_segment_ring_high.flyer`); their suffixes distinguish geometry, not speed. Other older entries at PL19/20 remain 2500-distance. All new bank additions were tested for exactly 10,000 ticks with Rust. Multiple seeds/world alignments have NOT been exhaustively tested.

## Preserved WIP and verified seeds

Paths below are relative to `flyers/`:

| File | Encoded limit | Start min X | End min X | Distance | End blocks | Extensions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `WIP/two_push_crosslayer_pl13.flyer` | 13 | 14 | 2514 | 2500 | 26 | 5000 |
| `WIP/three_push_ring_pl19.flyer` | 19 | 13 | 3013 | 3000 | 94 | 15000 |
| `WIP/four_push_ring_pl23.flyer` | 23 | 13 | 3346 | 3333 | 68 | 10000 |

These three WIP copies were independently rerun at the limits shown immediately before this handoff. The PL23 flyer is outside the requested bank limits and intentionally remains WIP. It is the strongest starting point for the unfinished 3.333 bps work. The PL13 flyer is Sol's `flyer_refined13_seed2.flyer` (RNG2). Bank/pl13 contains crosslayer_rodpower, materialswap, mirrorz, upright, and upright_swap variants.

## Critical breakthrough: plan the segment timing, not a fixed piston order

A pure-push N-step extension has a target/front sticky group that moves for N action slots then waits two. Each action slot is TWO simulator ticks. Its source/rear group follows TWO action slots later. This recycles the normal pistons: each piston is carried by the front until it fires, remains immovable while extending/retracting, and is then picked up by the rear group. All N pistons ultimately advance N blocks per cycle. Shared power means their firing permutation can vary; correct pickup geometry must support every transverse piston site, rather than rely on one order.

A closed loop requires `2*k == 0 (mod N+2)`: N=2 uses 2 segments; N=3 uses 5; N=4 uses 3 (or a multiple such as 6). This was implemented and VERIFIED for both N3 and N4! Extending a two-segment engine to three pushes alone cannot produce 3 bps.

Template for one interface at local action phase p, 0 <= p < N+2, with X offset h:

- Front sticky cross plane: `x = h + 1 + min(p,N)`.
- Shared redstone: `x = h + min(p,N)`, at transverse center.
- Rear pickup cross plane: `x = h - 1 + max(0,p-2)`; belongs to the previous segment in the loop.
- Piston j (initial firing permutation index): if j >= p, x=h+p and state0. Otherwise x=h+max(j,p-2), state2 iff p==j+1, else state0. State2 gets an arm at x+1. All pistons face +X. Initial state2 is format-valid and needs no movement list.
- Segment i phase is `(2*i) % (N+2)`. It includes front interface i and rear pickup interface i+1.

For N4, arrange FOUR pistons on the four transverse neighbors of one shared redstone block, with a five-block sticky cross in front. This is much smaller than a long four-piston row. N3 uses three arms of the same cross. Rear pickup crosses cover every piston site. Slime/honey routing needs to avoid both unwanted adhesion and accidentally collecting idle pistons early.

## Preserved generators and their limits

`WIP/astra_ringgen*.py` are copies of temporary research generators, not simulator changes. They import `fastflyer` from the working directory, so run/import from repository root. Their CLI writes candidates to TEMP; the `make(N, centers, seed, limit=100)` function returns `(Flyer, sticky_counts, (sticky_sets, phases))`. Use the Python library to save candidates and Rust to evaluate; the generator itself is NOT a physics simulator.

- `astra_ringgen.py`: original temporal BFS routing. Many candidates co-move components or stall later; unsafe as a success criterion.
- `astra_ringgen_safe.py`: avoids connector adjacency to pistons and power sources. VERIFIED successes: N3 centers `[(0,0),(0,4),(3,5),(5,2),(3,-1)]`, seed3 or6, minimum19; N4 centers `[(0,0),(0,4),(2,2)]`, seed0 or9, minimum23. The stored WIP flyers come from N3 seed3 and N4 seed0. N4 sticky counts are [16,18,17], plus one redstone and approximately four carried pistons per segment movement; largest load23.
- `astra_ringgen_smart.py`: attempts to allow correct-phase piston adjacency and checks unions of potential piston positions for different firing orders. No better layout found; still [16,18,17].
- `astra_ringgen_side.py`: replaces five rear cross cells with two opposite corner side-contact cells, trying to save X span. Requires connecting multiple separate pickup components. Most candidates unroutable, and the tested survivor merged segments. NOT verified.
- `astra_ringgen_hex.py` / `hexsmart.py`: six-segment N4 loops so materials alternate around the whole ring. Still roughly 16–18 sticky cells/segment; one six-segment seed5 survived 300 ticks at high limit. No PL20 success, and no full10k verification. Work stopped here.

Sweeping 138 compact triangle placements with the safe generator did not find N4 PL20. This is a limitation of that geometry, NOT evidence PL20 is impossible. Likely next improvements: more compact pickup geometry; avoid source/target piston interference without blanket adjacency prohibition; center spacing5 might avoid early pickup that occurs at spacing4. At spacing4, a connector departing the front toward the next interface can touch that interface's still-unfired piston, merging movement sets. Rods may save a block by hard-powering a carrier; note the piston ignores sources directly in front of itself.

## PL12 work from Sol

The preserved PL13 crosslayer is substantially better than the earlier PL14 layout. Its front pair pushes loads12 twice; return pair pushes loads13 twice. Five transforms pass10k. Sol tried single deletions, 359 nearby honey relocations, 106 kind conversions, and 3462 small remove/remove/add mutations without a sustained PL12 result. A new topology is needed, not ballast changes.

Unverified lead from Sol: place front B pistons at y1,z0/2, pickup spine at y1,z1; replace conflicting center redstone with rod at x0,y0,z1 pointing +Y into spine slime. That hard-powers both pistons and might reduce front structure to three slime. Honey layer y2 can supply return pickup, but staggered pickup currently intersects a return piston. Build and inspect actual movement sets.

## Practical workflow / diagnostics

Use `from fastflyer import Flyer, Block, Kind`; load/save/validate supplied library. Python serialization canonicalizes by whole X/Z chunk shifts and minimum Y; inspect loaded coordinates rather than assuming unnormalized coordinates survive. Directions: +X0,-X1,+Y2,-Y3,+Z4,-Z5. Material/axis transforms must also transform observer/rod directions. See `SIMULATION.md` for authoritative implemented rules.

Temporary Rust tools still available in `%TEMP%` on this machine:
- `flyer_measure.exe 10000 FILE...` prints path, distance, start minX, end minX, end maxX, end block count, extensions, elapsed ms.
- `flyer_batch.exe TICKS DIRECTORY` quick screens .flyer files in one directory.
- `flyer_pistons.exe FILE` first30 ticks of piston positions/states, loads and failures.
- `min_limit.exe FILE...` finds the smallest limit matching an 80-tick reference score. This is ONLY a screen; verify any resulting limit for full10k.
- `flyer_failure_links.exe`, `fail_t7.exe`, `astra_expected.exe` are ad hoc diagnostics. They are not portable dependencies. Use Rust public `Flyer::load`, `tick`, `blocks`, `tick_traced` and `debug::TickTrace::new(&flyer)` to reproduce them.

Temporary diagnostic programs were compiled against `target/release/deps/libfastflyer-60489f4c006e8143.rlib` with `rustc --edition=2021 --extern fastflyer=... -L dependency=target/release/deps`; find current hash if rebuilding. No project simulator/library code was changed. The repository ALREADY had many dirty source files before this work; do not revert them. Git may require a command-local `-c safe.directory=C:/Users/Ruben/OneDrive/Documents/FastFlyerPlayground` because sandbox ownership differs.

All active agents were interrupted when the user said finish immediately. No more design search is required for this handoff. The saved WIP and CSV are the authoritative completed artifacts; do not infer success from an unfinished candidate or generator.

---

# Earlier research notes (preserved)

# Fast Bedrock flying machines: research log

This is a design guide for agents working on **horizontal, self-propelled Bedrock Edition flying machines** (“flyers”). It combines the project's current simulator rules with the author's experimental notes. It is not a claim that every simulator rule exactly reproduces every Minecraft version. Use `SIMULATION.md` for the implemented rules and test promising designs in Bedrock.

## First principles and vocabulary

- A **game tick** (`gt`) is 1/20 second; a **redstone tick** (`rt`) is 2 gt, or 1/10 second. This project advances its flyer by one rt per simulator tick. Speed in **blocks per second** (`bps`) is `10 × net forward blocks / elapsed rt`. For example, 2 blocks in 8 rt is 2.5 bps; 3 blocks in 10 rt is 3 bps. [Minecraft's tick-rate explanation](https://learn.microsoft.com/en-us/minecraft/creator/documents/tickjsonintroduction?view=minecraft-bedrock-stable)
- A **segment** is a group of blocks that travels together during a particular piston action. It may contain pistons and power sources; it is a planning unit, not a special Minecraft block. A **cycle** returns the flyer to the same relative arrangement, translated forward. Measure speed over complete cycles, not a single impressive-looking push.
- A **move** (`m`) in a timing sketch means a segment advances one block during that interval; a **wait** (`w`) means it does not. Strings such as `mwmw` describe a segment's displacement pattern, not an exact wiring diagram. Write an explicit rt-by-rt schedule before assuming two segments can interact.
- A piston extends **one block relative to itself**. A fast flyer gains more than one block per cycle by moving its pistons *with other segments* between their own actions. A piston cannot push or pull itself with its own stroke, but another piston can move it while it is movable.
- The design's forward direction is usually `+x`; `y` is vertical and `z` is lateral. Chunk boundaries are every 16 blocks in `x` and `z`. The saved flyer records its world alignment modulo 16, because crossing a boundary can change ordering.

Minecraft's own guides describe the basic 12-block piston limit, sticky-piston pulling, observer pulses, and the absence of Bedrock quasi-connectivity. [Redstone guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/redstoneguide?view=minecraft-bedrock-stable) · [Bedrock/Java differences](https://learn.microsoft.com/en-us/minecraft/creator/documents/differencesbetweenbedrockandjava?view=minecraft-bedrock-stable)

## What the blocks do in this project

| Block | Design role |
| --- | --- |
| Piston | Pushes on extension; may itself be carried by *another* piston. |
| Sticky piston | Pushes on extension and can pull on retraction. The direct pull begins two cells ahead of its base because the front cell is occupied by its arm before retraction. |
| Slime / honey | Sticky carriers: each can bring along face-adjacent compatible blocks. Slime and honey do **not** stick to one another, so alternating them can isolate neighboring segments. [Minecraft example](https://www.minecraft.net/en-us/article/honey-block-machines) |
| Smooth stone | Ordinary movable, solid block; useful as a load or power-transfer block. |
| Glazed terracotta | Movable and solid, but does not adhere to slime/honey. It can still be pushed as an obstruction. |
| Glass | Movable, non-solid, non-sticky spacer; does not transmit hard power here. |
| Redstone block | Soft-powers nearby pistons, except through a piston's front face. |
| Observer | Emits a brief pulse after it finishes moving. In this simulator, its stored `direction` is its **output** direction; its detecting face is opposite. A powered observer hard-powers a solid block ahead or directly powers an adjacent piston it faces. |
| Perma-powered rod | Persistent compact power source: hard-powers in its facing direction and soft-powers adjacent pistons. Particularly useful when a redstone block would exceed the push limit. |
| Piston arm | Appears during extension; not a separately movable design component. |

Here **solid** means eligible to receive hard power: slime, honey, smooth stone, and glazed terracotta. Pistons, observers, glass, rods, redstone blocks, and arms are not solid in this model. **Hard power** can energize a solid neighbor, which can then power a piston touching it; **soft power** can power an adjacent piston directly. A piston ignores power arriving from the cell **in front of its face**. There is no Java-style quasi-connectivity to rescue a circuit that does not actually power its piston.

All blocks have a `moving` state. A moving block is inert for power: moving sources emit none, moving solids cannot be hard-powered, and moving pistons cannot be powered or act. A moving observer becomes powered **when its movement finishes**, so its pulse matters at the *next* power stage. At the end of each power stage, all powered observers turn off. Ordinary block-change detection and detector rails are mentioned in the research notes but are **not yet modeled** by the simulator; do not rely on them in a simulated design.

## One piston action, in order

Each rt has a **power stage**, then a **piston stage**. First, determine power from the stationary blocks at the start of the tick. Then update eligible pistons. The four piston states are:

1. `0`, retracted: if powered or `angry`, try to extend. A successful start creates moving blocks one cell ahead and enters state `1`. A failed extension stays in `0` and becomes `angry`, ready to retry.
2. `1`, extending: finish the movement, make the listed destination blocks stationary, then enter state `2` (extended).
3. `2`, extended: if unpowered, start retracting and enter state `3`. The block directly in front is cleared regardless of what it is; a sticky piston may pull blocks from beyond it.
4. `3`, retracting: finish any pulled blocks' movement, then enter state `0`.

An uninterrupted extend–retract sequence thus occupies **four rt**, though power timing, failed pushes, and movement by other pistons can alter when a particular piston starts. Normal pistons do not perform a sticky pull. A failed sticky pull still allows retraction without the load. Each piston owns the moving blocks created by its action; its stored list contains their **destination coordinates**, not its arm. Blocks stay moving until that owner finishes the action.

### How a push or pull finds its load

Start at the block in front of the extending piston, or two cells ahead for a sticky pull. Add each occupied destination in the motion direction as an obstruction to push. For every slime/honey block in the load, also explore all six face-neighbors it adheres to. Keep doing both until no new blocks appear. Count each source block only once against the flyer’s `PUSH_LIMIT` (default 12); the initiating piston and its arm are not counted.

Slime and honey do not adhere to each other or to glazed terracotta. They do adhere to eligible ordinary blocks and other pistons when those pistons are movable. An immovable neighbor reached **only by adhesion** is ignored; an immovable block obstructing the destination makes the action fail. Moving blocks, arms, and pistons in states `1–3` are immovable. The piston attempting the action is itself immovable **and non-sticky** for that search, even if it is a sticky piston. This distinction prevents a piston from dragging itself into its own load.

Example: if a piston pushes a slime block with smooth stone attached to its side, both enter the load, unless a further obstruction or the 12-block cap prevents the move. Replace the smooth stone with honey or glazed terracotta and side adhesion disappears; place that same block *in front of the slime's destination* and it may still have to be pushed out of the way.

## Timing, chunks, and reliability

There is no single universal piston update order to design around. This simulator shuffles the occupied **chunk** list once at the beginning of the piston stage, then shuffles piston candidates within each chunk. Only chunks occupied at that point are visited; a new chunk entered by moving blocks does not get an extra turn. The simulator saves an RNG state for reproducible runs, but that is a replay mechanism, **not a promise that real Bedrock uses the same order**.

Within one rt, an earlier chunk can finish moving a piston into a later chunk. If that piston is eligible there, it may act in the same rt. The author's notes also identify an “angry” failed-extension case that can exploit or unexpectedly trigger this situation. Treat any same-tick cross-chunk activation as a special, order-sensitive design, and test multiple seeds and all relevant `x/z` phases. A fast result from one favorable order is not yet a reliable flyer. The author's current note is that 5 bps individual movements are reliable while 10 bps ones are not; this needs in-game verification for each design.

## A useful design process for speed

1. **Choose a complete-cycle target.** The author's existing examples report 2.5 bps from two-block advancement and 3 bps from three-block advancement. Record net displacement and total rt explicitly; do not infer speed merely from the number of pistons.
2. **Sketch segment timing and positions first.** For each rt, list every segment's `x` position, whether it moves or waits, and the piston responsible. A segment cannot be “pulled” unless the sticky piston and its target are in the required relative positions at that exact action.
3. **Draw the push/pull dependency graph.** A rear chain can push itself and forward segments; a forward **support segment** can pull a rear segment for its final forward move. This is valuable because the rear often faces the worst push-limit burden. The author's 3 bps example uses a five-segment rear chain plus forward segments that pull the rear and are themselves eventually pulled.
4. **Check each action's complete load.** Include sticky side attachments, destination obstructions, carried pistons, power sources, and the 12-block limit. Alternating honey and slime can split loads that would otherwise merge. A `push–push–pull` sequence may keep the final push load smaller.
5. **Add power last.** For every action, identify the actual stationary source or hard-powered solid, which side of the piston it reaches, and whether the source will be moving at that rt. Nearby segments with identical timing can sometimes share a source.
6. **Simulate and inspect several cycles.** Check state, moving ownership, observer pulses, and phase/seed sensitivity. Confirm the machine repeats its relative shape, progresses in `+x`, and does not merely achieve a one-off burst. Then verify viable candidates in Bedrock itself.

## Open questions and research leads

The author's notes describe a 2.5 bps `mwmw` engine using two slime segments, two normal pistons, two sticky pistons, and two observers; each piston is moved once by each segment per cycle. They describe 3 bps as the best existing design **known to the author**, not an independently established world record. A goal beyond 3 bps remains research, not an implemented result.

Promising ideas to test: a 3.33 bps extension that advances very little (or even retreats) relative to the main flyer so it can repeat; adding an rt of delay to reduce load; an `mmwmmw` segment to obtain two pulls and interoperate with `mmmmww`; or `push–push–push–pull` with an explicit way to reset the last support. Multiple side pulls may help, but ambiguous moving-block ownership and push-limit costs make them difficult. Chunk-border ordering might supply an extra pull, but reliability is a separate proof obligation. For every proposal, write the segment schedule and load counts before building geometry.

**Provenance:** Mechanical details specific to this project come from the author's supplied research notes and `SIMULATION.md`. The linked official Minecraft sources support general timing, piston, observer, edition, and honey/slime basics; they do not verify the claimed 2.5/3 bps builds or chunk-order exploits.

<!-- moved from RESEARCH_LOG.md on 2026-10-02 -->
## Pulling-only exploration — 2026-09-27

All artifacts are under `WIP/experiments/astra_pullonly_20260927/`. The PL10 winner has **7 slime, 7 honey, 2 observers, 4 -X sticky pistons**, plus one sampled arm. Its extensions move no blocks; each alternating retraction moves 10. Retracted pistons transfer between the two carriers. Generator `pull_mwmw.py`, candidate `mwmw/c448.flyer`; offset `(1,-1,2)`, transform `(swap=0,sy=1,sz=-1)`, both observer choices 0, geometry seed 0. Encoded-limit copy `mwmw_best.flyer`; evidence `mwmw_audit.csv`, `mwmw_load_audit.txt`, `mwmw_cycle.txt`.

Local target rail: `{(2,0,0),(1,0,0),(0,0,0),(0,0,1),(0,1,0)}`. Opposite-material support: `(2,1,1)`. Sticky P0 `(2,0,1)` starts extended, P1 `(2,1,0)` retracted. Target observer `(2,-1,0)` outputs +Y. Target moves slots 0/2, support 1/3. P0 extends in slot 3 and pulls in 0; P1 extends in 1 and pulls in 2. Two routed interfaces close the cycle.

Search: 504 layouts, 272 travelled 40/160 at diagnostic PL100. Ranking short successful loads found PL10; the winner then passed the full 80 × 10,000 audit. All 14 single sticky-cell deletions failed to preserve 40/160 at both PL9 and PL100. A cap-six-per-material closure screen over offsets `[-3,3]^3`, eight transverse transforms, and four observer combinations routed no candidates (10,976 parameter sets); this is not a global lower bound.

Earlier baselines: `baseline.flyer` repeats at 1.25 bps (short audit, load 10). `ring3_best.flyer` achieves 1,666/10,000 at encoded PL8, full six-tick recurrence and all 80 samples passed. The three-carrier generator routed 407 of 600 seeds. These are retained as simpler mechanisms, not banked speed improvements.

Faster lead: `three_pull_burst.flyer` makes three consecutive +X pulls at ticks 0/2/4, loads 17/18/19, then **stalls**. All 80 short samples conserve blocks and advance three; a 10,000-tick run still advances only three. `burst.py` and traces preserve the finite mechanism. It is not a repeating flyer or a speed record. Closing the piston reset/transport cycle is the next speed question; a naive shared support can recapture a piston during its intended extension slot.

