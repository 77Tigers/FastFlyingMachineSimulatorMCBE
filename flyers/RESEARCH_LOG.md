# Flyer research handoff — 2026-09-26, diagonal breakthrough

Keep this active handoff below **5,500 words**. Prior evidence is preserved in [RESEARCH_LOG_PRE_DIAGONAL_2026-09-26.md](RESEARCH_LOG_PRE_DIAGONAL_2026-09-26.md), [RESEARCH_LOG_ARCHIVE_2026-09-26.md](RESEARCH_LOG_ARCHIVE_2026-09-26.md), and experiment findings. Read root `SIMULATION.md` before implementing mechanics. Do not change the simulator, editor library, format, viewer, or unrelated project files to obtain a score.

**Research workflow and tooling:** Start with the short [active-experiment index](WIP/experiments/INDEX.md), then read only the linked files needed for the current question. [RESEARCH_RUNNER.md](WIP/experiments/RESEARCH_RUNNER.md) documents portable `screen`, `verify`, `samples`, and focused `trace` commands. Save full batch results and traces in the experiment directory; show compact summaries and the first relevant failure in chat. Search named directories with bounded output instead of listing all `.flyer` files. Reuse the runner before writing a one-off diagnostic. **Do not remove or shorten information about existing research tools unless a replacement tool and its usage are documented and available.** Preserve paths and evidence needed to reproduce prior claims.

**Maintain the handoff yourself:** Before finishing a research turn, update this log and the [active-experiment index](WIP/experiments/INDEX.md) when priorities, leads, status, best candidates, evidence paths, or next steps change. Update the experiment's `FINDINGS.md` with its bounds and outcome, and update [RESEARCH_RUNNER.md](WIP/experiments/RESEARCH_RUNNER.md) whenever runner commands or output meanings change. Keep the index short by moving completed detail to findings; do not leave stale pointers or ask the user to maintain these files. Occasionally clean up the research log by removing obviously outdated or irrelevant sentences. Last cleaned: 2026-10-02.

## New task — 2026-10-02: mv4 rear core

User requests **mv4**, 10/3 bps: move +1 over 2rt, wait 1rt, repeating; core phases offset 0/1/2rt. At least one of each phase **at the back**. Other-timing helpers allowed, but must not mostly push the mv4 core; prefer front pulling assistance. **Hard cutoff PL<50; aim below36, slightly above36 accepted. Usage is low: obtain a working sub50 build quickly, defer further optimization.** Sol 6.1 workers authorized. [mv4 findings](WIP/experiments/mv4_20261002/FINDINGS.md): PL101 timing reference passes10,000 ticks; redesign shared interfaces, do not trim it. Not banked. Model group winners carrying other ready pistons and same-tick settling/pickup.

**General user rule (2026-10-02): designs above PL50 usually are not worth incrementally shrinking. Change the architecture or shared interfaces instead; retain oversized builds only as bounded mechanism references.**

## Update — 2026-10-02 evening (agent J2): back segments to 11, role ILP

- **User metric now:** max push limit per segment, back->front; get tm_smol's 5 back segments to 11 (PL13/14 allowed, never above 14, then shrink). Hint: minimise pistons pushing front segments, maximise front segments pulling back segments.
- **Banked `bank/pl14/human_tm_smol_back11x2.flyer`** (80/80): tm_smol + B35 pulls B24 @s2 + B29 pulls B19 @s3, both powered by victim observers, replaced pushers deleted. Back segments [11,12,12,12,11] (was all 12), front [13,14,13,13,11,11,9,9]; front-segment pushers 22->20, front pulls 6->8. Builds: `j2_front_smol/b24pull/`, `j2_tmsmol_opus/`.
- **Banked `bank/pl13/human_tm_smol_back11.flyer`** (80/80): only the B29->B19 pull; back [11,12,12,12,12], front [13,12,13,12,11,11,9,9]. Two back@11 at PL13 blocked: B35->B24 always costs B24 +3 cells (~1,650 attempts, `j2_tmsmol_opus/NOTES.md` Step 3).
- **Role ILP** `tm_smol_rebalance_20261001/j2_front_smol/layered.py` (scipy milp): any words, push/pull per move, carrier timelines; validated (reproduces tm_smol's ledger exactly). `ledger_ilp.py` builds it from any bodytrack ledger. Best paper plan for tm_smol: 3 back@11 at PL12; remaining pulls (B41->B36, B45->B37) fail on observer adhesion/pulse hazards (planner3 lacked a cross-body adhesion check; fixed in `j2_tmsmol_opus/planner3x.py`).
- **Banked `bank/pl17/mmwmw_two_bodies_pulled_twice.flyer`** (80/80): two mmwmw rails each pulled twice + pushed once (added rails, not back segments: user only counts back-chain segments).
- Bounded negatives: 3bps_original fresh front cannot change rear loads (no front piston rides a rear body; `j2_front_orig/`). B15's 10th cell only carries B9's s3 pusher B0 (714 relocations fail). Back-segment word changes (e.g. B15 -> mwmwm, ILP-feasible) need pushers that change carrier mid-cycle; no generator supports this (`j2_mmwmw3/`). mmwmw_two_pulls: its back segment 14 -> 13 via the same pull (`j2_front_smol/m14t/`), flyer still PL14; dropped.

## Update — 2026-10-02 (agent J, incl. overnight): exclusive roles, mmwmw, victim-observer power

- **Exclusive roles** (one glue body only pulled, another only pushed), all 80/80: 3 bps **PL13** `bank/pl13/exclusive_roles_3bps.flyer` (on 3bps_original, 8-slime pull-only B41; also PL14/15/19 on tm_smol), 3.333 bps **PL22** `bank/pl22/exclusive_roles_3p333.flyer` (also PL26). Method: per-body load budget on port triples (`exclusive_roles_20261001/j_light16/jports*.py`, `j_333/jports333.py`); PL14 needed per-port simulator screening (`portscreen.py`), exact Steiner rails and forbidding rail cells next to a sticky at its fire slot (else the rail drags it). Rail pull load = rail glue + 1-2 adhered stickies; tm_smol is too tight for PL13, but 3bps_original has slack (only 6 bodies at 12) and gave PL13 with an 8-glue rail (`j_light13/`). PL12 there: 0 candidates (bounded). 3.333 PL21 blocked (base engine already 21).
- **mmwmw** (rests separated): `bank/pl14/mmwmw_two_pulls.flyer` is the first 3 bps flyer whose glue body (B20, word mmwmw) is **pulled twice and pushed once** per cycle (80/80). The pusher rides rigidly on a body idle at its fire slot; the rail carries its own RB beside it (`tm_smol_rebalance_20261001/j_mmwmw2/`). Paper contract for an all-mmwmw ring (one observer per body powers all 3 pistons): `j_mmwmw/NOTES.md`.
- **tm_smol fewer load-12 actions** (retrofit history; superseded by the J2 back-segment update above). Total load = 3 x (cells + free pushers) = 420 over 39 moves (~9 units slack); 9/13 bodies have zero slack. User principle: push costs a carried pusher on back bodies, pull costs a sticky on the front body, so convert back pushes into front pulls (rear 12 traded for a front 12 is a win). Role plan predicts rear 12s 8->6, but cell edits (41k), a 309-placement joint retrofit and a front re-lay all failed: the fronts are geometrically saturated.
- **Victim-observer power (new rule, simulator-verified):** a pull on the victim's last move s can be powered by an observer ON THE VICTIM (it moved at s-2, so it pulses at the extension slot s-1; later pulses miss because the victim has moved relative to the resting puller). Replaces helper-helpers. Proof: `bank/pl15/human_original_victim_observer.flyer` (3bps_original with helper B66 + pushers removed; PL15 from 3 support cells). In the human fronts the observer lane collides with the puller's pusher column, so use it in a fresh layout: `tm_smol_rebalance_20261001/FRESH_LAYOUT_CONTRACT.md` (3bps_original has 10 pulls, rear = 8 glue + 4 riders, i.e. glue-limited; model predicts 14 -> 11 load-12 actions with victim observers).
- 3-body 3.333 ring works at PL29 (`human_mcstructure_20261001/ring_hand/`); user: not novel, stop.

## Update — 2026-10-01 evening: human-built flyers (`human_` bank entries)

- The user supplied Bedrock builds in `mcstructures/`. Converter, tools and full notes: `WIP/experiments/human_mcstructure_20261001/FINDINGS.md`. Conversion needs a **Z mirror** of the raw NBT index order; observers output opposite their Bedrock facing.
- **3 bps at PL12 is real (friend's two-push + one-pull).** `bank/pl12/human_tm_smol_3bps.flyer` (145 blocks) and `bank/pl12/human_3bps_original.flyer` (195 incl. 9 glass) pass 80/80 at 3000/10000; both stall at PL11. Previous general 3 bps best was PL18. `bodytrack`: five `mmmww`-rotation classes, each pushed twice and sticky-pulled once per 10 ticks; most normal pistons are 1-cell passengers that hop carriers every slot.
- 2.5 bps human pieces: observer-only c1 at **PL9** after a mid-cycle snapshot start (`bank/pl9/human_observer_hop.flyer`; the human start needs PL10, also banked), c3 PL11, c4 PL12 (uneven bodies, loads 6/12).
- Glass in `3bps_original` is functional (7/9 needed) in the simulator, and the user confirms it mattered in-game too.
- **How the human designs get low loads:** each body's own redstone (or rod) powers a *column* of 2-4 normal pushers stuck to it; the first push drags the rest, so exactly one fires per slot. Spent pushers are carried by a neighbouring body. Sticky chains: each sticky pulls the body behind and is powered by the body in front; the frontmost sticky needs a push-only "helper-helper" body (`tm_smol` B41/B45). Loads = small body (7-10 cells) + 2-4 riding pistons.
- c5 (user: "3 bps with timing issues") is `tm_smol` with its helper-helpers replaced by glue arms on bodies with the **same movement word** as the bodies they replace — timing-correct (constant offset reproduces the power schedule) but the arms glue/collide. ~2,000 bounded repairs failed; `tm_smol` is effectively the repaired c5.
- c2/c6 (3.33 extensions): c2 is a push-push-push-pull chain (front body 2 slots ahead pulls the rear one; rear carries the front's pushers). A **2-body 3.33 ring is infeasible** (both-move-slot induction). A 3-body ring contract is worked out and implemented in `ring3.py`; a bounded 3,000-sample run found **0 working** because its router ignored +X sweep obstruction (all bodies merge on the first push) — a generator gap, not a contract result. A per-slot conflict check was added but makes routing too slow; the only near-miss (45 blocks) had 26-31-cell bodies and is not close. Next: hand-place one compact layout rather than sample. Details in the findings.
- c0 (observer-only, one glued blob) is a sketch; dead under all starts tried.

## Update — 2026-10-01 (agent E, overnight)

- **mmwmmw 3.333 bps: PL29 -> PL22** with the user's pull-twice idea (each segment is pulled twice per cycle by front stickies firing in its wait slots). Banked `bank/pl22/pull_twice_mmwmmw.flyer`, 80/80. Evidence: `WIP/experiments/speed_range_b_20260930/mmwpull/`.
- **New A/B category** (A segments only push B, B only pull A): banked 2.5 bps PL12 (`bank/pl12/ab_push_pull_2body.flyer`), 3 bps PL34 (`bank/pl34/ab_push_pull_7body.flyer`), and 3.333 bps PL71 (`bank/pl71/ab_push_pull_9body.flyer`). Under the stationary-anchor and order-hazard rules, the minimum body counts are 2 / 6 / 9. Theory, generator (`abpr.py`) and validators: `WIP/experiments/ab_20261001/FINDINGS.md`.
- 3 bps mmmww push+pull lifecycle is verified in the simulator but has no record yet: `WIP/experiments/frontier_pull_20261001/`.

## Current continuation — 2026-09-30

**Overnight instruction:** Prioritize lower push limits for3bps and3.333bps in **both `mmmmww` and `mmwmmw`**, plus a **pulling-only3bps flyer**. Use separate front helpers, the two-push/one-pull trick, abstraction contracts and literal chained extensions before closure. Do not buy credits or use an account usage reset. [Overnight checkpoints and next steps](WIP/experiments/overnight_20260930/FINDINGS.md).

**New banked mmwmmw result: PL36 at3.333bps.** Coplanar four-port choreography plus connected pruning gives3333/10000 with105 boundary blocks, improving pattern-specificPL65→57→37→36. All80 full cases pass all833 exact twelve-tick/+4 cell/owner recurrences, conservation and zero failures. Bank: `bank/pl36/planar_mmwmmw.flyer`. The separate mmmmww record remainsPL22. **Pulling-only3bps is banked atPL102**, with all80 full exact audits; ten distinct bodies and30 -X sticky pistons. Earlier106/126/127 steps are preserved. Further connected pruning and all-body rerouting reduced cell counts without lowering102;16 circular placements yielded no route. Every extension is empty in the127 trace. See current overnight findings before duplicating work.

The user reopened speed optimization across push limits **and pulling-only**, with freedom to choose stages, and suggested chaining tileable extensions before looping. This supersedes the older pulling-only deferral and bounded abstraction-trial restrictions below.

**New banked record: PL9 at2.5 bps, pulling-only.** `bank/pl9/pulling_loop4.flyer` travels2500/10000. Four separate alternating carriers have six sticky cells each, four observers and eight -X sticky pistons. All80 full RNG/phase samples passed complete +2/eight-tick cell/owner recurrence at all1250 boundaries, conservation and zero movement failures. Maximum action9; all eight extensions per cycle are empty, all eight pulls move9. The user's chain-first suggestion led to a working five-cell tile, then adding one connector cell per body enabled four-body closure. [Evidence and generator](WIP/experiments/continuation_20260930/FINDINGS.md).

**New open-chain proof, 2.5 bps:** a literal two-interface pulling tile with five sticky cells per added body chains on the PL10 reference driver. Encoded PL11 assemblies with **1/2/4/8 tiles** (2/4/8/16 added bodies) all passed 10,000-tick complete block/owner recurrence: +2/eight ticks, distance2500, zero failures/conservation errors. Driver loads11/10; internal extension loads8, terminal7. Both the1-tile and8-tile chains passed all80 full RNG/phase samples. This is a modularity result, **not a PL8 whole flyer**. The original tile advances backward by(-3,0,-2) per pair in initial placement. Full evidence and bounds are in the same findings.

**Latest user clarification:** the front helpers are distinct from the main back chain/loop. At3bps, pursue the friend's **two normal pushes plus one helper-provided pull**, not three pushers between the same back links. T/M/F roles and phases, axial pull reach and the first known helper failure are recorded in the [next interface contract](WIP/experiments/continuation_20260930/MIXED_EXTENSION_CONTRACT.md). This contract is proposed, not a new geometry result.

**New3bps local mixed interface:** an eight-cell added target receives two normal pushes and one separate helper pull, with actual load10–11. Literal1/2/4/8 copies all pass full10000-tick exact checks and tagged ledgers. Larger driver/helper loads70/91/133/217 are separate from local11;both1/8-copy assemblies pass all80 full samples. Sharing normal recovery reduces the next target to **five cells and local load7–8**, with full exact single-extension validation at whole-assemblyPL53. Literal1/2/4/8 copies all pass full10000-tick exact checks and tagged ledgers at whole limits66/83/119/195;both1/8-copy assemblies pass all80 full cases. [Realized sparse ports, helpers and copy contract](WIP/experiments/overnight_20260930/MIXED_TILE_CONTRACT.md). These are interface results, not globalPL8/11 records. A glazed-terminal/rod power interface for mmmmww now works in8/8 short hexagonal layouts (best47, full exact10000-tick audit passes), separating late-burst helper sources from targets; it does not beat mmmmwwPL22. use the current findings before repeating work.

Higher-speed route screens completed96 seeds each: five-body N3 best18, three-body N4 best22, six-body N4 best23. Fifteen selected candidates sustained their target speeds at10000 ticks but failed strict nominal-cycle recurrence. No higher-speed bank claims changed. Twenty-three connected single-cell trims of the new89-block PL18 lead yielded no survivor. Next: a chainable mixed interface with separate helper phases and actual load accounting.

## Prior highest-priority directions — 2026-09-28

**Abstraction workflow (2026-09-29):** This task improved and tested the [abstraction pipeline](ABSTRACTION_PIPELINE.md), delegating implementation to GPT-6 Sol Medium. Use piston-group lifecycle/contact contracts to keep high-level reasoning out of cell-by-cell repairs. Future agents should improve the pipeline when a concrete weakness appears, or record the example and proposed improvement in their findings; state whether the change was tested. Preserve old evidence and distinguish abstraction tests from new performance claims.

**Trial result:** A fresh Sol Medium worker built a PL10 `mwmw` flyer from the reference-derived sparse group/contact handoff without the full reference body geometry or old generator. Exact 10,000-tick verification and all 80 full RNG/phase samples passed. This establishes constrained realization, not novel architecture discovery or measured token savings. [Results and limits](WIP/experiments/abstraction_medium_20260929/RESULTS.md).

These supersede the older closed-engine search priorities below.

1. **Simple three-segment `mmwmmw` flyer at 3.333 bps.** All three segments must have different timings. Ignore push-limit optimization initially, while keeping the geometry reasonably compact; do not inflate it unnecessarily. Confirm the intended timing notation if needed before choosing an architecture.
2. **Repeatable low-push-limit extensions at both 3 bps and 3.333 bps.** Prioritize extensions whose geometry reaches at least as far back as the previous segment. They must be chainable repeatedly, not merely produce a finite burst or work as a single special attachment. Closing them into an engine is a later task the user plans to give Sol. Use the friend's additional front segments/pulling assistance where useful. Test with an existing engine or a long chain, and record timing, attachment geometry, actual action loads, conservation, and repeated translated behaviour. Distinguish driver overhead from extension loads and validate that adding copies preserves operation.

The user permits Sol subagents for sufficiently easy, concrete subtasks. The 5,500-word limit is a ceiling, not a target.

### Results from this direction — 2026-09-28

**Working three-segment `mmwmmw` mechanism:** `WIP/three_segment_mmwmmw_pl65.flyer`. Three connected sticky carriers follow `mmwmmw`, `wmmwmm`, and `mwmmwm`. Four cells per twelve ticks; the encoded PL65 copy travels **3,333 in 10,000 ticks**, with 177 sampled blocks, zero failures, permanent-kind conservation, and complete translated cell/owner-list recurrence every twelve ticks. It uses 12 normal pistons, six redstone blocks, six observers, and 151 sticky cells, plus two sampled arms. This is a working timing proof with substantial routing overhead, not a compactness or push-limit record. Further compaction is deferred.

Artifacts: `WIP/experiments/astra_mmwm_20260928/`. `search.py` synthesizes time-dependent pickup contacts and routes three carriers; `trim.py` trims connected rails. The final geometry comes from seed19, module spacing4, followed by five successful sticky deletions. Final evidence: `trim/pl65_full.txt`, `trim/pl65_80_samples.csv` (**all80 full10,000-tick samples passed**, every833 cycle boundaries matched exact cells/owner lists and +4 displacement), and `trim/geometry.json`. The earlier 206-block PL82 version passed all80 full-length exact-recurrence samples; Sol's evidence is `sol_reference_20260928/mmw_3segment_pl82_exact_samples.csv`.

Key correction: a free recovering piston grabbed by carrier A can push an occupied destination belonging to B, merging their loads and stealing B's scheduled firing piston. Routing must exclude that ownership transfer, not merely overlapping cells and direct sticky adhesion. Versions1/2 preserve failed screens; version3 fixes it. Use `diagnose.py`/`annotate.py` as diagnostic examples, noting they regenerate against the current generator and their original seed0 failure refers to version2.

**Extension work is unfinished.** Sol tested closed rings containing 1/2/4 phase blocks, not identical attachable extensions: N3 loads18/18/20; N4 loads22/23/21. All six baselines sustained the intended speed for10,000 ticks without conservation or movement failures. `sol_reference_20260928/chain_metadata.json` records changing full-cycle rear offsets. Do not mistake a positive gap in one phase for a general impossibility, or these varying routed rings for a proven chainable module. Actual open-chain duplication and the friend's pull-assisted low-load architecture remain next steps.

Useful side leads: `sol_reference_20260928/n3_copies1_s0_pl18.flyer` runs3bps at PL18 and passes all80 full-length speed/conservation samples; exact ten-tick cell/owner recurrence varies, even after masking angry bits, so it is not banked. `n4_copies4_s0_pl21.flyer` runs3.333bps at PL21 with twelve carriers/256 blocks; one full traced run passed, phase/RNG audit outstanding. See that directory's `FINDINGS.md`. These are leads, not replacements for the requested extension proof.

Prior objectives and 2026-09-27 record summary are preserved in [the prior-objectives archive](RESEARCH_LOG_PRIOR_OBJECTIVES_20261002.md).

## PL11 diagonal alternating engine

Generator: `WIP/experiments/astra_diagonal/search_mwmw.py`. Winning generated file: `astra_diagonal/mwmw/c58.flyer`. Metadata: second-interface offset `(-3,0,1)`, transverse transform `(swap=1,sy=-1,sz=-1)`, observer choices `oa=ob=1`, geometry seed 0. Simulation RNG 5, phase `(0,0)`.

It has **8 slime, 6 honey, 2 observers, 4 normal pistons**, plus one arm at the sampled boundary. Loads alternate **11/9/11/9**. The two carriers alternate actions (`mwmw`), each advancing two cells every eight ticks. One piston starts extended, a valid advanced-cycle initialization.

The successful local module uses support honey H `(0,0,0)`, +X pistons P0 `(0,0,1)` and P1 `(-1,1,0)`, and target slime `{(-1,1,1),(0,1,1),(1,1,1),(1,0,1),(1,1,0)}`. An observer at `(0,-1,0)` outputs +Y into H, or use its rotated equivalent. **Diagonal piston sites let one rear corner slime pick either piston**, reducing the previous eight-slime sketch to five local rail cells. Two routed modules close the cycle.

Evidence: `astra_diagonal/c58_pl11_audit.csv`, `c58_pl12_audit.csv`, and corresponding trace files. Rebuild `astra_diagonal/verify.rs` against the current release rlib. It checks all 80 cases, permanent-kind counts, encoded blocks and owner lists at all 1,250 translated cycles. Sol independently verified PL11 with `sol_diagonal/audit_cycle.rs`.

PL10 local screen: c58 cannot start its 11-cell move. All eight generated 7/7-sticky layouts stalled; every single slime deletion from c58 broke motion even at diagnostic PL20. c244's moved observer powers the wrong piston for an extra slot, causing a tick-4 immovable collision. Relocation repairs that action but changes observer ownership, loses the next pulse, and still exceeds ten. See `sol_diagonal/FINDINGS.md`; do not repeat those deletion screens or infer global impossibility.

## Pulling-only exploration — 2026-09-27

Moved to [the archive](RESEARCH_LOG_ARCHIVE_2026-09-26.md) (section "Pulling-only exploration — 2026-09-27", moved 2026-10-02): PL10 c448 details, local rail, 504-layout search, deletion/closure negatives, `three_pull_burst.flyer` lead.

## Friend's 3 bps mechanism

**2026-09-27 feedback:** “add even more front segments to reduce the back segments pl.” The intended revision is to distribute the front workload across additional carriers so each back segment only needs **two pistons** to push the segments in front, and to shorten the connections substantially. Sol acted on this in `WIP/experiments/sol_extra_front_20260927/`; see its `FINDINGS.md`.

Sol traced the prior helper's 30-block pull and screened 48 bridge deletions/material substitutions; none exceeded its transient distance 10/160. The new four-role architecture adds five front relays (20 carriers total), moving the next back's two-piston support burden onto a relay and reducing each nominal back sticky shape to five cells. An early one-drive relay incorrectly assumed three advances: all 54 Rust screens stalled at distance zero. The corrected three-drive relay routed no complete candidates in a bounded 50-seed screen (19 middle-route failures, 13 relay-route failures, 9 mandatory collisions, 8 middle distance-cap failures, 1 unwanted adhesion). This is unfinished geometry, **not a new 3 bps result**. Next: compact the relay's three drive sites near their supporting middle carrier without crossing the back pickup corridor. Do not repeat the invalid one-drive relay screen.

**New category, 2026-09-27:** explore pulling-only fast flyers. Every piston used to move anything must be a **sticky piston facing -X**. The user explicitly permits any motion caused by those pistons, including extension pushes; prioritize speed at any push limit. Intended net travel remains +X. Work is separate from the mixed 3 bps track, under `WIP/experiments/astra_pullonly_20260927/`.

The friend proposes five main back carriers. A back carrier drives the next back carrier and an additional middle carrier; the middle drives a front carrier. A backward sticky on the middle is powered by the front, making the back's **third movement a pull after two normal pushes**. Additional middle/front carriers may distribute hardware and shorten the back routes. Human builds of this design now exist (`bank/pl12/human_tm_smol_3bps.flyer`, `human_3bps_original.flyer`).

The five-slot timing already fits the N3 ring:

| Carrier | Moves in slots | Role |
|---|---|---|
| Target T | 0, 1, 2 | two pushes, then pull |
| Middle M | 0, 3, 4 | carries sticky; stationary during extension/pull |
| Front F | 1, 2, 3 | powers sticky at slot 1, then moves power away |

M moves S into power range during slot 0. At slot 1 S extends while T gets its second push and F moves its source away. At slot 2 S retracts and pulls T. S resets before M resumes moving in slot 3. A source behind a -X sticky (+X), or transversely adjacent, can work; a source in its -X-facing cell is ignored.

**Self-running timing proof exists.** `astra_pull3/retrofit.py` replaces one N3 last-push role, installs a middle-carrier sticky, and adds its target connection. `astra_pull3/one_hybrid/s-2_3_5r2g0.flyer` travels 3,000 in 10,000 ticks at diagnostic PL100. Normal pushes cost 24, sticky pull 25: mechanism proof, not a record. Unnormalized coordinates: S `(-2,3,5)` replaces a middle honey cell; F's redstone is `(0,3,5)`; T's added contact is `(-5,3,5)`.

Sol trimmed the g1 variant. `sol_diagonal/pull3trim/double_pl22.flyer` reaches 3,000/10,000 at **encoded PL22**, 99 ending blocks, 15,000 extensions. It deletes serialized cells `(14,0,16)` and `(16,0,16)` from g1. The untrimmed sticky pull carries one extra retracted normal piston beyond the preceding normal target set. This remains worse than the PL19 reference; full phase/conservation audit is outstanding. Check `screen_round2.py` and saved limit copies before repeating tests.

## Current search and useful next experiments

1. **Compact all-hybrid ring.** `astra_pull3/hybrid_ring.py` is an unvalidated generator. Each interface j has two +X normal pistons and one -X sticky sharing j's redstone. The sticky shares the first normal's extension/retraction phase, but pulls carrier `j-2`; support carrier `j-1` carries it. Its rear pickup must be sideways because its arm occupies/removes the cell behind it in X. The first bounded screen generated no viable routed candidates; inspect `hybrid_ring.log` and rejection diagnostics before expanding. A conservative router failure is not a physics impossibility.
2. **Extra middle/front branches.** `astra_pull3/helper_ring.py` implements separate back, middle, and front carriers. Version 2 screened 6,000 layouts: five routed at nominal back cap 11, but none completed the 160-tick screen. The best, `helper_ring_v2/c1s1287.flyer`, moved 10 blocks; its early trace shows an unintended 30-block sticky pull at tick 6. Diagnose the merged carrier and power/arm timing before widening the search. The nominal cap suggests a possible PL17 family, not a validated flyer.
3. **3.333 bps PL21 lead.** Earlier `n4_bridge`/phase-sample findings identify a short route that later captures a 22nd block. Diagnose the first owner/contact change before tick 153. New `sol_mwmw_fixture/n4/` contains diagonal rear-corner screens: `summary.csv`, `reduction.csv`, `swaps.csv`. Some high-limit layouts repeat, but no lower-limit record has been established. Inspect interrupted artifacts before restarting.
4. **Avoid exhausted N3 patches.** `sol_n3_retrofit/` contains 40 rear-corner substitutions and 186 glazed-connector variants that did not improve PL19. Existing shortened bridges collide with an immovable/moving block near `(18,0,16)` around tick 14 even at higher limits. Address ownership/timing rather than the limit alone.

## Research helpers

The portable runner (`WIP/experiments/research_runner.rs`, `RESEARCH_RUNNER.md`) supports screen, exact verify, 80-case samples, conservation and focused traces. Newer per-action tools: `human_bodytrack.exe` (bodies, words, actor/carrier/power), `human_ledger.exe`, `human_snapshot.exe`, `tm_smol_rebalance_20261001/loadhist.exe` (batch load histograms), `planner*.py` (role-level pull planners). Still wanted: persistent-identity movement ledgers and a temporal router that checks every slot (failed finite route searches are not lower bounds).

## Mechanics and proof contract

One Rust tick is 0.1 seconds. Speed is `10 × displacement / ticks`. Score is final minus initial minimum X **within the same in-memory simulation**, exactly 10,000 ticks. Saving renormalizes coordinates; never score by comparing separately saved minima. Directions: `+X=0,-X=1,+Y=2,-Y=3,+Z=4,-Z=5`.

Power runs before piston updates. Redstone/rods soft-power adjacent pistons; observers output only along their direction. Rods/observers hard-power a solid ahead: slime, honey, stone, glazed terracotta. Pistons ignore sources directly in front. Moving sources/targets do not supply/receive power. A moved observer pulses when movement finishes; the next power stage consumes it. Initial unpowered `angry=True` does not start a stationary piston.

States 0/1/2/3 are retracted/extending/extended/retracting; a clean cycle takes four ticks. Sticky retraction removes its front/arm cell, then discovers from **two cells ahead**, moving toward the base. Moving cells, arms and state-1/2/3 pistons are immovable. Adhesion skips an immovable neighbor; an immovable destination fails. Slime/honey do not adhere to each other or glazed terracotta. Discovery recursively adds allowed sticky face-neighbors and occupied destinations. The initiating piston/arm do not count. Two pistons cannot pool capacity.

**User rule (2026-10-01): a screened candidate that travels more than about 30 blocks, even if it stalls or fails, is likely close to a good design — investigate it (trace the first failure, try local repairs) instead of discarding it.** Screen 120–300 ticks, then longer, then exactly 10,000 at the encoded claimed limit. Verify permanent-kind conservation every tick and full translated repeat including states, moving bits, observer power and owner lists. Run all 80 phase/RNG samples before banking; this remains a sample, not a universal RNG proof. No ballast/debris or friendly-start tricks. Preserve references and unrelated dirty files. Simulator results require separate Bedrock testing before claiming in-game compatibility.

## Suggested don'ts (unvetted)

An agent (J2, 2026-10-02) suggested the following advice, distilled from failed attempts. Treat it as heuristics, not rules:
1. **Check what each cell carries before trimming a body.** A cell may exist only to carry another body's piston (tm_smol B15's tail carries B9's pusher B0); deleting it strands the piston. Move the role, not the cell.
2. **Check who rides the back before redesigning the front.** Read the rider ledger first: in 3bps_original no front piston rides a rear body, so front redesigns cannot lower rear loads.
3. **Constrain and validate role plans.** Limit carriers to nearby bodies and pullers to bodies in front of their victim, and require the model to reproduce the real flyer's loads before trusting its predictions (`tm_smol_rebalance_20261001/j2_front_smol/layered.py`).
4. **Check the generator can express the plan.** If the plan needs a piston to change carrier mid-cycle and the generator only has rigid carriers, it returns "0 ports" every time. Check capability before running it.
5. **Keep a victim observer clear of the puller's new glue,** and make sure its other pulses power no piston. Otherwise the puller drags it and it fires a slot early (the B45->B37 near-miss).
6. **Count a pull's cost on the victim, not just the added sticky.** A victim 3 cells behind the sticky needs about 3 observer support cells, about +3 load (tm_smol B24 always went to 14).

## Reproducible tools

Work from repository root. `fastflyer/` edits files; Rust `src/` simulates. Static sticky counts are not action loads. Compile diagnostics against the current `target/release/deps/libfastflyer-*.rlib`, not a hardcoded hash.

Preferred portable workflow: run `WIP/experiments/build_research_runner.ps1`, then `bin/research_runner.exe screen CANDIDATE_DIRECTORY 160 --out RESULTS.csv`, `verify CANDIDATE.flyer 10000 --period 12 --advance 4`, or `samples CANDIDATE.flyer --period 12 --advance 4 --out SAMPLES.csv`. Replace 12/+4 with the candidate's actual cycle contract. The runner prints short summaries and saves per-candidate/per-sample CSV; use `trace FILE START END` only around a relevant failure. Full syntax and interpretation are in [RESEARCH_RUNNER.md](WIP/experiments/RESEARCH_RUNNER.md).

```powershell
& "$env:TEMP/flyer_measure.exe" 10000 flyers/bank/pl11/diagonal_alternating.flyer
& "$env:TEMP/flyer_batch.exe" 160 CANDIDATE_DIRECTORY
& flyers/WIP/experiments/bin/archive/flyer_trace_window.exe CANDIDATE.flyer 0 24
```

TEMP helpers are host-local. Keep scripts, representative candidates, compact results, and findings. Never bank a diagnostic copy or a short-lived lead.

Latest completed front-interface result: pull/push/push five-cell target uses glazed power separation, tagged loads6–8, and passes full exact10000 ticks plus80/80 cases at wholePL59. Hybrid separate-back/front closure did not route in16 bounded attempts. Native final results: `WIP/experiments/overnight_20260930/NATIVE_AUDIT_CHECKPOINT.md`.

## User direction — 2026-09-30, helper helpers

Current goal: lower the minimum push limits for **3 bps and 3.333 bps**, improving the PL12–20 speed frontier. Do not pursue designs above **PL24** or try to shrink a PL30 architecture into PL18; stop unpromising bounded families. Shared coordination: `flyers/chat.txt`.

**New explicit suggestion:** put a **helper-helper segment directly in front of each helper**. It has two jobs: **provide the power source for the helper's sticky piston**, and **pull the helper forward one block**, so the main back chain does not have to supply that push. These are independent of compact side pickup and can be combined. A segment in front of a helper can supply its power; it need not be routed back from a distant circular placement. Keep the helper/pull target axially aligned. The user warns that slime/honey behind a piston being transported generally signals a poor pickup arrangement; prefer side contacts and short connections.

This is a proposed architecture, not a new verified flyer. Every added helper/helper-helper still needs a complete movement, recovery and power contract; check actual action loads and source ownership. Current experiments and bounded negative results: `WIP/experiments/speed_range_20260930/FINDINGS.md`. The separate agent reports banking the existing PL18/3 bps and PL21/3.333 bps leads under the speed/conservation/80-sample standard agreed in its chat; strict nominal-cycle recurrence remains a separate property.
User clarification: begin with PL18 and one segment (possibly the segment after the highest-load one). Add two FORWARD NORMAL pistons sharing a redstone block, at most two extra piston passengers on one existing segment. Do not add a six-cell power route to that segment. Helpers are separate bodies; the helper pushes the helper-helper. New generators distinguish original-body loads from separate-helper loads. Enlarged-existing-body variants atPL22/24 are closed. Current proposed seven-body/no-added-original-glue construction: `WIP/experiments/speed_range_20260930/separate_helpers.py`; findings retain exact bounds and corrected group/pull contracts.
2026-09-30 helper-helper run: no lower limit; six-body126-block PL21 passes80 cases; two-normal helper fixture passes240 cases; eight-body closure blocked by one connector overlap (bypass untested). Details: `WIP/experiments/speed_range_20260930/FINDINGS.md`.

2026-10-01/02 exclusive-roles task: see the 2026-10-02 (agent J) update above.
