# Flyer research handoff — 2026-09-26, diagonal breakthrough

Keep this active handoff below **3,000 words**. Prior evidence is preserved in [RESEARCH_LOG_PRE_DIAGONAL_2026-09-26.md](RESEARCH_LOG_PRE_DIAGONAL_2026-09-26.md), [RESEARCH_LOG_ARCHIVE_2026-09-26.md](RESEARCH_LOG_ARCHIVE_2026-09-26.md), and experiment findings. Read root `SIMULATION.md` before implementing mechanics. Do not change the simulator, editor library, format, viewer, or unrelated project files to obtain a score.

## Objectives and verified records

**New best, 2026-09-27: PL10 at 2.5 bps, pulling-only.** `bank/pl10/pulling_alternating.flyer` uses four -X sticky pistons and travels **2,500 blocks in 10,000 Rust ticks**. All 80 RNG/phase samples passed conservation and complete translated state/owner-list recurrence every eight ticks, with zero extension failures. A full traced run confirms maximum successful load 10 and zero movement failures. `bank/results.csv` includes the result. Details below.

The previous normal-piston PL11/PL12 records remain banked as `bank/pl11/diagonal_alternating.flyer` and `bank/pl12/diagonal_alternating.flyer`. Each also moves 2,500/10,000 with 5,000 extensions and 21 end blocks and passed the same 80-case audit: RNG `[0,1,2,5,42]`, independent X/Z phases `[0,7,8,15]`.

**Primary objective: 3 bps at PL17 or lower.** The user's friend reports a **PL12/3 bps** two-push/one-pull design; this is the stronger aspiration, but no coordinates or file were supplied. It is guidance, not a verified result here. The user explicitly authorized improving **3.333 bps concurrently**, superseding the earlier deferral of that track. Current verified references remain `WIP/three_push_ring_pl19.flyer` (3,000/10,000) and `WIP/four_push_ring_pl22.flyer` (3,333/10,000).

The user permits Sol subagents and any format-valid initial state. Give each agent a concrete, distinct task and its own experiment directory. Sol agents hit a usage limit during this continuation; unfinished scripts/results remain on disk. Do not mistake an interrupted task for an exhausted search.

## PL11 diagonal alternating engine

Generator: `WIP/experiments/astra_diagonal/search_mwmw.py`. Winning generated file: `astra_diagonal/mwmw/c58.flyer`. Metadata: second-interface offset `(-3,0,1)`, transverse transform `(swap=1,sy=-1,sz=-1)`, observer choices `oa=ob=1`, geometry seed 0. Simulation RNG 5, phase `(0,0)`.

It has **8 slime, 6 honey, 2 observers, 4 normal pistons**, plus one arm at the sampled boundary. Loads alternate **11/9/11/9**. The two carriers alternate actions (`mwmw`), each advancing two cells every eight ticks. One piston starts extended, a valid advanced-cycle initialization.

The successful local module uses support honey H `(0,0,0)`, +X pistons P0 `(0,0,1)` and P1 `(-1,1,0)`, and target slime `{(-1,1,1),(0,1,1),(1,1,1),(1,0,1),(1,1,0)}`. An observer at `(0,-1,0)` outputs +Y into H, or use its rotated equivalent. **Diagonal piston sites let one rear corner slime pick either piston**, reducing the previous eight-slime sketch to five local rail cells. Two routed modules close the cycle.

Evidence: `astra_diagonal/c58_pl11_audit.csv`, `c58_pl12_audit.csv`, and corresponding trace files. Rebuild `astra_diagonal/verify.rs` against the current release rlib. It checks all 80 cases, permanent-kind counts, encoded blocks and owner lists at all 1,250 translated cycles. Sol independently verified PL11 with `sol_diagonal/audit_cycle.rs`.

PL10 local screen: c58 cannot start its 11-cell move. All eight generated 7/7-sticky layouts stalled; every single slime deletion from c58 broke motion even at diagnostic PL20. c244's moved observer powers the wrong piston for an extra slot, causing a tick-4 immovable collision. Relocation repairs that action but changes observer ownership, loses the next pulse, and still exceeds ten. See `sol_diagonal/FINDINGS.md`; do not repeat those deletion screens or infer global impossibility.

## Pulling-only exploration — 2026-09-27

All artifacts are under `WIP/experiments/astra_pullonly_20260927/`. The PL10 winner has **7 slime, 7 honey, 2 observers, 4 -X sticky pistons**, plus one sampled arm. Its extensions move no blocks; each alternating retraction moves 10. Retracted pistons transfer between the two carriers. Generator `pull_mwmw.py`, candidate `mwmw/c448.flyer`; offset `(1,-1,2)`, transform `(swap=0,sy=1,sz=-1)`, both observer choices 0, geometry seed 0. Encoded-limit copy `mwmw_best.flyer`; evidence `mwmw_audit.csv`, `mwmw_load_audit.txt`, `mwmw_cycle.txt`.

Local target rail: `{(2,0,0),(1,0,0),(0,0,0),(0,0,1),(0,1,0)}`. Opposite-material support: `(2,1,1)`. Sticky P0 `(2,0,1)` starts extended, P1 `(2,1,0)` retracted. Target observer `(2,-1,0)` outputs +Y. Target moves slots 0/2, support 1/3. P0 extends in slot 3 and pulls in 0; P1 extends in 1 and pulls in 2. Two routed interfaces close the cycle.

Search: 504 layouts, 272 travelled 40/160 at diagnostic PL100. Ranking short successful loads found PL10; the winner then passed the full 80 × 10,000 audit. All 14 single sticky-cell deletions failed to preserve 40/160 at both PL9 and PL100. A cap-six-per-material closure screen over offsets `[-3,3]^3`, eight transverse transforms, and four observer combinations routed no candidates (10,976 parameter sets); this is not a global lower bound.

Earlier baselines: `baseline.flyer` repeats at 1.25 bps (short audit, load 10). `ring3_best.flyer` achieves 1,666/10,000 at encoded PL8, full six-tick recurrence and all 80 samples passed. The three-carrier generator routed 407 of 600 seeds. These are retained as simpler mechanisms, not banked speed improvements.

Faster lead: `three_pull_burst.flyer` makes three consecutive +X pulls at ticks 0/2/4, loads 17/18/19, then **stalls**. All 80 short samples conserve blocks and advance three; a 10,000-tick run still advances only three. `burst.py` and traces preserve the finite mechanism. It is not a repeating flyer or a speed record. Closing the piston reset/transport cycle is the next speed question; a naive shared support can recapture a piston during its intended extension slot.

## Friend's 3 bps mechanism

**2026-09-27 feedback:** “add even more front segments to reduce the back segments pl.” The intended revision is to distribute the front workload across additional carriers so each back segment only needs **two pistons** to push the segments in front, and to shorten the connections substantially. Sol acted on this in `WIP/experiments/sol_extra_front_20260927/`; see its `FINDINGS.md`.

Sol traced the prior helper's 30-block pull and screened 48 bridge deletions/material substitutions; none exceeded its transient distance 10/160. The new four-role architecture adds five front relays (20 carriers total), moving the next back's two-piston support burden onto a relay and reducing each nominal back sticky shape to five cells. An early one-drive relay incorrectly assumed three advances: all 54 Rust screens stalled at distance zero. The corrected three-drive relay routed no complete candidates in a bounded 50-seed screen (19 middle-route failures, 13 relay-route failures, 9 mandatory collisions, 8 middle distance-cap failures, 1 unwanted adhesion). This is unfinished geometry, **not a new 3 bps result**. Next: compact the relay's three drive sites near their supporting middle carrier without crossing the back pickup corridor. Do not repeat the invalid one-drive relay screen.

**New category, 2026-09-27:** explore pulling-only fast flyers. Every piston used to move anything must be a **sticky piston facing -X**. The user explicitly permits any motion caused by those pistons, including extension pushes; prioritize speed at any push limit. Intended net travel remains +X. Work is separate from the mixed 3 bps track, under `WIP/experiments/astra_pullonly_20260927/`.

The friend proposes five main back carriers. A back carrier drives the next back carrier and an additional middle carrier; the middle drives a front carrier. A backward sticky on the middle is powered by the front, making the back's **third movement a pull after two normal pushes**. Additional middle/front carriers may distribute hardware and shorten the back routes. Derive the layout; no build file exists in the conversation.

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
2. **Extra middle/front branches.** `astra_pull3/helper_ring.py` implements separate back, middle, and front carriers. Version 2 screened 6,000 layouts: five routed at nominal back cap 11, but none completed the 160-tick screen. The best, `helper_ring_v2/c1s1287.flyer`, moved 10 blocks; its early trace shows an unintended 30-block sticky pull at tick 6. Diagnose the merged carrier and power/arm timing before widening the search. The nominal cap suggests a possible PL17 family, not a validated flyer; PL12 remains open.
3. **3.333 bps PL21 lead.** Earlier `n4_bridge`/phase-sample findings identify a short route that later captures a 22nd block. Diagnose the first owner/contact change before tick 153. New `sol_mwmw_fixture/n4/` contains diagonal rear-corner screens: `summary.csv`, `reduction.csv`, `swaps.csv`. Some high-limit layouts repeat, but no lower-limit record has been established. Inspect interrupted artifacts before restarting.
4. **Avoid exhausted N3 patches.** `sol_n3_retrofit/` contains 40 rear-corner substitutions and 186 glazed-connector variants that did not improve PL19. Existing shortened bridges collide with an immovable/moving block near `(18,0,16)` around tick 14 even at higher limits. Address ownership/timing rather than the limit alone.

## Suggestions that would most help Astra and Sol

These are proposed research helpers, not simulator changes or claims that they already exist. Implement under `WIP/experiments/` using public Rust APIs.

- **One portable runner:** a checked-in Rust diagnostic plus rebuild script for batch screening, exact scoring, arbitrary-period repeat checks, conservation, RNG/phase samples, JSON/CSV output. Replace host-specific TEMP dependencies. Current `verify.rs` hardcodes period eight; N3 needs ten, N4 twelve.
- **Movement ledger with stable block identities:** source/destination, kind, initiating piston, owner before/after, and carried hardware for each action. Highlight the exact extra cell exceeding a limit. Clearly separate a failed discovery's partial set from a diagnostic complete set.
- **Power/contact timeline:** source → hard-powered solid → piston, plus arms and retraction states. Diff a failure against its repeating parent at the first divergent tick. This would expose c244's extra pulse immediately.
- **Temporal router:** check all scheduled phases with explicit allowed pickups and forbidden arm/destination sweeps. Current heuristics can both reject useful contacts and accept wrong timed contacts. A failed finite route search is not a lower bound.
- **Checkpointed manifests:** save hash, generator parameters/revision, geometry seed, simulation RNG, phases, limit, tick budget, distance, conservation, first failure, and next untested index after each batch. Flush findings before long jobs so usage interruptions do not lose work.
- **Short shared experiment queue:** each item states one causal question, bounded family, expected action ledger, owned directory, and success/stop criterion. Prefer role reuse and contact timing over unstructured one-cell edits. Preserve negative evidence with exact bounds.

## Mechanics and proof contract

One Rust tick is 0.1 seconds. Speed is `10 × displacement / ticks`. Score is final minus initial minimum X **within the same in-memory simulation**, exactly 10,000 ticks. Saving renormalizes coordinates; never score by comparing separately saved minima. Directions: `+X=0,-X=1,+Y=2,-Y=3,+Z=4,-Z=5`.

Power runs before piston updates. Redstone/rods soft-power adjacent pistons; observers output only along their direction. Rods/observers hard-power a solid ahead: slime, honey, stone, glazed terracotta. Pistons ignore sources directly in front. Moving sources/targets do not supply/receive power. A moved observer pulses when movement finishes; the next power stage consumes it. Initial unpowered `angry=True` does not start a stationary piston.

States 0/1/2/3 are retracted/extending/extended/retracting; a clean cycle takes four ticks. Sticky retraction removes its front/arm cell, then discovers from **two cells ahead**, moving toward the base. Moving cells, arms and state-1/2/3 pistons are immovable. Adhesion skips an immovable neighbor; an immovable destination fails. Slime/honey do not adhere to each other or glazed terracotta. Discovery recursively adds allowed sticky face-neighbors and occupied destinations. The initiating piston/arm do not count. Two pistons cannot pool capacity.

Screen 120–300 ticks, then longer, then exactly 10,000 at the encoded claimed limit. Verify permanent-kind conservation every tick and full translated repeat including states, moving bits, observer power and owner lists. Run all 80 phase/RNG samples before banking; this remains a sample, not a universal RNG proof. No ballast/debris or friendly-start tricks. Preserve references and unrelated dirty files. Simulator results require separate Bedrock testing before claiming in-game compatibility.

## Reproducible tools

Work from repository root. `fastflyer/` edits files; Rust `src/` simulates. Static sticky counts are not action loads. Compile diagnostics against the current `target/release/deps/libfastflyer-*.rlib`, not a hardcoded hash.

```powershell
& "$env:TEMP/flyer_measure.exe" 10000 flyers/bank/pl11/diagonal_alternating.flyer
& "$env:TEMP/flyer_batch.exe" 160 CANDIDATE_DIRECTORY
& flyers/WIP/experiments/bin/archive/flyer_trace_window.exe CANDIDATE.flyer 0 24
```

TEMP helpers are host-local. Keep scripts, representative candidates, compact results, and findings. Never bank a diagnostic copy or a short-lived lead.
