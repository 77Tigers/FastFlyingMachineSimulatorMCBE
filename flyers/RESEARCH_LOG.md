# Flyer research handoff — 2026-09-26, diagonal breakthrough

Keep this active handoff below **5,000 words**. Prior evidence is preserved in [RESEARCH_LOG_PRE_DIAGONAL_2026-09-26.md](RESEARCH_LOG_PRE_DIAGONAL_2026-09-26.md), [RESEARCH_LOG_ARCHIVE_2026-09-26.md](RESEARCH_LOG_ARCHIVE_2026-09-26.md), and experiment findings. Read root `SIMULATION.md` before implementing mechanics. Do not change the simulator, editor library, format, viewer, or unrelated project files to obtain a score.

**Research workflow and tooling:** Start with the short [active-experiment index](WIP/experiments/INDEX.md), then read only the linked files needed for the current question. [RESEARCH_RUNNER.md](WIP/experiments/RESEARCH_RUNNER.md) documents portable `screen`, `verify`, `samples`, and focused `trace` commands. Save full batch results and traces in the experiment directory; show compact summaries and the first relevant failure in chat. Search named directories with bounded output instead of listing all `.flyer` files. Reuse the runner before writing a one-off diagnostic. **Do not remove or shorten information about existing research tools unless a replacement tool and its usage are documented and available.** Preserve paths and evidence needed to reproduce prior claims.

**Maintain the handoff yourself:** Before finishing a research turn, update this log and the [active-experiment index](WIP/experiments/INDEX.md) when priorities, leads, status, best candidates, evidence paths, or next steps change. Update the experiment's `FINDINGS.md` with its bounds and outcome, and update [RESEARCH_RUNNER.md](WIP/experiments/RESEARCH_RUNNER.md) whenever runner commands or output meanings change. Keep the index short by moving completed detail to findings; do not leave stale pointers or ask the user to maintain these files.

## Highest-priority directions — 2026-09-28

**Abstraction workflow (2026-09-29):** The current discussion/research task is to improve and test the [abstraction pipeline](ABSTRACTION_PIPELINE.md), delegating implementation to GPT-6 Sol Medium. Use piston-group lifecycle/contact contracts to keep high-level reasoning out of cell-by-cell repairs. Future agents should improve the pipeline when a concrete weakness appears, or record the example and proposed improvement in their findings; state whether the change was tested. Preserve old evidence and distinguish abstraction tests from new performance claims. The current geometry trial is `mwmw`; `mmwmmw` must be representable but is not being geometry-tested in this iteration.

**Trial result:** A fresh Sol Medium worker built a PL10 `mwmw` flyer from the reference-derived sparse group/contact handoff without the full reference body geometry or old generator. Exact 10,000-tick verification and all 80 full RNG/phase samples passed. This establishes constrained realization, not novel architecture discovery or measured token savings. [Results and limits](WIP/experiments/abstraction_medium_20260929/RESULTS.md).

These supersede the older closed-engine search priorities below. Pulling-only remains an important direction, but the user explicitly defers it until later.

1. **Simple three-segment `mmwmmw` flyer at 3.333 bps.** All three segments must have different timings. Ignore push-limit optimization initially, while keeping the geometry reasonably compact; do not inflate it unnecessarily. Confirm the intended timing notation if needed before choosing an architecture.
2. **Repeatable low-push-limit extensions at both 3 bps and 3.333 bps.** Prioritize extensions whose geometry reaches at least as far back as the previous segment. They must be chainable repeatedly, not merely produce a finite burst or work as a single special attachment. Closing them into an engine is a later task the user plans to give Sol. Use the friend's additional front segments/pulling assistance where useful. Test with an existing engine or a long chain, and record timing, attachment geometry, actual action loads, conservation, and repeated translated behaviour. Distinguish driver overhead from extension loads and validate that adding copies preserves operation.

The user permits Sol subagents for sufficiently easy, concrete subtasks. The 5,000-word limit is a ceiling, not a target.

### Results from this direction — 2026-09-28

**Working three-segment `mmwmmw` mechanism:** `WIP/three_segment_mmwmmw_pl65.flyer`. Three connected sticky carriers follow `mmwmmw`, `wmmwmm`, and `mwmmwm`. Four cells per twelve ticks; the encoded PL65 copy travels **3,333 in 10,000 ticks**, with 177 sampled blocks, zero failures, permanent-kind conservation, and complete translated cell/owner-list recurrence every twelve ticks. It uses 12 normal pistons, six redstone blocks, six observers, and 151 sticky cells, plus two sampled arms. This is a working timing proof with substantial routing overhead, not a compactness or push-limit record. The user requested an immediate wrap-up; further compaction is deferred.

Artifacts: `WIP/experiments/astra_mmwm_20260928/`. `search.py` synthesizes time-dependent pickup contacts and routes three carriers; `trim.py` trims connected rails. The final geometry comes from seed19, module spacing4, followed by five successful sticky deletions. Final evidence: `trim/pl65_full.txt`, `trim/pl65_80_samples.csv` (**all80 full10,000-tick samples passed**, every833 cycle boundaries matched exact cells/owner lists and +4 displacement), and `trim/geometry.json`. The earlier 206-block PL82 version passed all80 full-length exact-recurrence samples; Sol's evidence is `sol_reference_20260928/mmw_3segment_pl82_exact_samples.csv`.

Key correction: a free recovering piston grabbed by carrier A can push an occupied destination belonging to B, merging their loads and stealing B's scheduled firing piston. Routing must exclude that ownership transfer, not merely overlapping cells and direct sticky adhesion. Versions1/2 preserve failed screens; version3 fixes it. Use `diagnose.py`/`annotate.py` as diagnostic examples, noting they regenerate against the current generator and their original seed0 failure refers to version2. No simulator/editor changes were made.

**Extension work is unfinished.** Sol tested closed rings containing 1/2/4 phase blocks, not identical attachable extensions: N3 loads18/18/20; N4 loads22/23/21. All six baselines sustained the intended speed for10,000 ticks without conservation or movement failures. `sol_reference_20260928/chain_metadata.json` records changing full-cycle rear offsets. Do not mistake a positive gap in one phase for a general impossibility, or these varying routed rings for a proven chainable module. Actual open-chain duplication and the friend's pull-assisted low-load architecture remain next steps.

Useful side leads: `sol_reference_20260928/n3_copies1_s0_pl18.flyer` runs3bps at PL18 and passes all80 full-length speed/conservation samples; exact ten-tick cell/owner recurrence varies, even after masking angry bits, so it is not banked. `n4_copies4_s0_pl21.flyer` runs3.333bps at PL21 with twelve carriers/256 blocks; one full traced run passed, phase/RNG audit outstanding. See that directory's `FINDINGS.md`. These are leads, not replacements for the requested extension proof.

## Objectives and verified records

**New best, 2026-09-27: PL10 at 2.5 bps, pulling-only.** `bank/pl10/pulling_alternating.flyer` uses four -X sticky pistons and travels **2,500 blocks in 10,000 Rust ticks**. All 80 RNG/phase samples passed conservation and complete translated state/owner-list recurrence every eight ticks, with zero extension failures. A full traced run confirms maximum successful load 10 and zero movement failures. `bank/results.csv` includes the result. Details below.

The previous normal-piston PL11/PL12 records remain banked as `bank/pl11/diagonal_alternating.flyer` and `bank/pl12/diagonal_alternating.flyer`. Each also moves 2,500/10,000 with 5,000 extensions and 21 end blocks and passed the same 80-case audit: RNG `[0,1,2,5,42]`, independent X/Z phases `[0,7,8,15]`.

**Primary objective: 3 bps at PL17 or lower.** The user's friend reports a **PL12/3 bps** two-push/one-pull design; this is the stronger aspiration, but no coordinates or file were supplied. It is guidance, not a verified result here. The user explicitly authorized improving **3.333 bps concurrently**, superseding the earlier deferral of that track. Current verified references remain `WIP/three_push_ring_pl19.flyer` (3,000/10,000) and `bank/pl22/four_push_ring.flyer` (3,333/10,000; original retained in WIP). The bank now spans PL8–PL24; empty limits are not evidence of a working design.

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

The portable runner below now exists. The other items remain proposed research helpers, not simulator changes or claims that they already exist. Implement them under `WIP/experiments/` using public Rust APIs.

- **Portable runner (implemented):** `WIP/experiments/research_runner.rs`, built by `build_research_runner.ps1`, now supports compact CSV `screen`, exact encoded-state/owner-list `verify` at arbitrary period and advance, 80-case `samples`, conservation checks, maximum successful action loads, and focused `trace`. See `RESEARCH_RUNNER.md` for complete commands and limits. It does not yet produce JSON or persistent block identities. The older `astra_diagonal/verify.rs` still hardcodes period eight; use the portable runner for N3/10 and N4/12.
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

Preferred portable workflow: run `WIP/experiments/build_research_runner.ps1`, then `bin/research_runner.exe screen CANDIDATE_DIRECTORY 160 --out RESULTS.csv`, `verify CANDIDATE.flyer 10000 --period 12 --advance 4`, or `samples CANDIDATE.flyer --period 12 --advance 4 --out SAMPLES.csv`. Replace 12/+4 with the candidate's actual cycle contract. The runner prints short summaries and saves per-candidate/per-sample CSV; use `trace FILE START END` only around a relevant failure. Full syntax and interpretation are in [RESEARCH_RUNNER.md](WIP/experiments/RESEARCH_RUNNER.md).

```powershell
& "$env:TEMP/flyer_measure.exe" 10000 flyers/bank/pl11/diagonal_alternating.flyer
& "$env:TEMP/flyer_batch.exe" 160 CANDIDATE_DIRECTORY
& flyers/WIP/experiments/bin/archive/flyer_trace_window.exe CANDIDATE.flyer 0 24
```

TEMP helpers are host-local. Keep scripts, representative candidates, compact results, and findings. Never bank a diagnostic copy or a short-lived lead.
