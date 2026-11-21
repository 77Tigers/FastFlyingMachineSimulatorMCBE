# Hill climb: 3.333 bps minimum push limit

## The hill

- **Target.** Beat the current 3.333 bps bank record (**PL18**) and drive minimum verified push limit `PL` downward toward **PL12** (`>= 3333` blocks in 10,000 ticks, 0 extension or movement failures, 0 conservation mismatches, no ballast/debris, passing 20/20 climbing + 60/60 held-out = 80/80 canonical RNG x phase cases, and failing at `PL - 1`).
- **Scope.** Work inside `flyers/WIP/experiments/hill_climb_3p333/` on branch `hill-climb-3p333`. Do not modify `src/`, `fastsim/`, `fastflyer/`, `viewer/`, or existing `flyers/bank/` files.
- **Baseline.** Commit `d0aaacc` (`master`), record holder `flyers/bank/pl18/nk_lat_n4.flyer` at **PL18** (224 blocks, `4x14x14`, 3.334 bps, 80/80 at PL18, 0/80 at PL17). Secondary reference: `flyers/bank/pl19/nk_stack_n4.flyer` at **PL19** (756 blocks, `15x19x19`, 3.333 bps).
- **Budget.** Climb until held-out verified PL stalls for 2 consecutive rounds, we reach PL12, or Neon quota runs out.
- **Noise floor.** `0` (verified across two identical Round 0 baseline runs: both 20/20 climbing, 60/60 held-out, min distance 3334 at PL18).
- **Headroom.** `6 PL` (PL18 down to PL12).

## Roles

- **Orchestrator & independent verifier.** `verify_climb.py` (fixed seed-42 split: 20 climbing cases, 60 held-out cases).
- **Builder-reasoner.** `gpt-6.2-astra` (`reasoningEffort: xhigh`, `serviceTier: default`).
- **Judge panel.** `gpt-6.2-astra` (`xhigh`, `default`), `gemini-4-neon` (`high`), `claude-fable-5-2` (`high`).

## Round 0 panel synthesis

Fundamental N4 load law (derived independently by Neon and Fable): `avg_action_load = 4 + avg(non-piston cells per body)` (`<= 13` for PL17, `<= 12` for PL16, `<= 11` for PL15).

| Judge | `nk_lat_n4` (PL18) Overall | `nk_stack_n4` (PL19) Overall | Top bets |
| --- | ---: | ---: | --- |
| Astra (`high`) | 8.6 | 7.3 | 1. 1-RB central `+` lat ring with relaxed pickup connectivity in `joint_cp.py` (PL17/PL16). 2. 1-RB 3-hopper stack back + `tm_smol` L1 side pickup (PL17). |
| Neon (`high`) | 7.2 | 5.8 | 1. Non-uniform `gap=3` stacked-loop N4 towers with `links-in=[1,0,-3]` and unpulled `p0` (PL17/PL16/PL15). 2. 6-body alternating-material 3D interleaved hopper ring with `t=[-1,-1,0]` x2 and `rbcol` (PL17/PL16). |
| Fable (`high`) | 6.0 | 4.5 | 1. Self-pulled 12-body ring where PREV's sticky pulls victim's cover cell (PL17/PL16). 2. Self-pulled 3-body cluster with mutually adjacent power body (PL16/PL15). |

Known dead ends (do not retry):
- 2-body 3.333 rings (proven infeasible by both-move-slot induction).
- `mmwmmw` 3-body pull-twice routing (ILP-optimal at PL22 for banked placements; 5-rider floor).
- Local tuning of `nk_lat_n4` inside the fixed 12-body planar square ring (balanced offsets, rods, `latbig`, `slab`, `terrace`, `modsearch`, `reseat` all failed to beat PL18).
- Loop hoppers across `t >= -1` links in stacks (`t <= -2` / `t = -3` required).
- Victim-observer power at N4 (pulses 1 slot early at the same relative offset).

## Ledger

| Round | Commit | Candidate | Verified PL | Climbing (/20) | Held-out (/60) | Blocks | Speed (bps) | Panel summary | Decision |
| --- | --- | --- | ---: | --- | --- | ---: | ---: | --- | --- |
| 0 (baseline run 1) | `d0aaacc` | `flyers/bank/pl18/nk_lat_n4.flyer` | 18 | 20/20 | 60/60 | 224 | 3.334 | Astra 8.6, Neon 7.2, Fable 6.0 | Baseline |
| 0 (baseline run 2) | `d0aaacc` | `flyers/bank/pl18/nk_lat_n4.flyer` | 18 | 20/20 | 60/60 | 224 | 3.334 | Noise floor = 0 | Confirmed |
| 0 (ref) | `d0aaacc` | `flyers/bank/pl19/nk_stack_n4.flyer` | 19 | 20/20 | 60/60 | 756 | 3.333 | Astra 7.3, Neon 5.8, Fable 4.5 | Reference |
| 1 | `021b309` | `round1/screw6_pl18.flyer` | 18 | 20/20 | 60/60 | 108 | 3.333 | Astra 8.0, Neon 7.8, Fable 7.0 (3-0 A/B over `nk_lat_n4`); unanimous Option C pivot | Kept as compact PL18 control; pure 6-body hopper ring hit `sum <= -6` wall (stall 1/2 on PL) |
| 2 | `9f9a3a4` | `round2/openplus6_pl18.flyer` | 18 | 20/20 | 60/60 | 107 | 3.333 | Astra 7.5, Neon 7.4, Fable 7.3 (3-0 A/B over `screw6_pl18`); 2-1 STOP vs Neon CONTINUE | Kept as new 107b self-pulled control (stall 2/2 on PL); orchestrator override for 1 final Round 3 test of Neon's exact `A4->T3->O3` + `gap=3` tower blueprint |
| 2 (alt) | `9f9a3a4` | `round2/openplus3_pl19.flyer` | 19 | 20/20 | 60/60 | 55 | 3.333 | Noted by panel (`6x6x6` cube) | Tiny 55-block 3-body self-pulled reference |
| 3 | `bcc0ac1` | `round3/mixed_screw_pl16.flyer` | **16** | 20/20 | 60/60 | 262 | 3.334 | Astra 8.8, Neon 8.7, Fable 8.3 (3-0 valid, zero ballast); unanimous CONTINUE for PL15 | **NEW RECORD (-2 PL vs baseline PL18)!** Stall counter reset to 0 |
| 3 (alt) | `bcc0ac1` | `round3/mixed_screw_pl17.flyer` | **17** | 20/20 | 60/60 | 256 | 3.334 | Verified stepping stone | Verified PL17 (4-hopper A4 + 2 loop hoppers/half-ring) |
| 4 | `98717ad` | `round4/mixed_screw_pl15.flyer` | **15** | 20/20 | 60/60 | 282 | 3.333 | Astra 9.0, Neon 9.1, Fable 8.4 (3-0 valid, zero ballast); Astra & Neon independently invented `Obs2+P+S` for PL14/13 | **NEW RECORD (-3 PL vs baseline PL18)!** 20-body `O3->T3->A3c+S` + 4-lvl towers on col 2/5; stall counter 0 |
| 5 | `da41845` | `round5/` (no closed PL14 flyer) | 15 (record held) | — | — | — | — | 3-0 CONTINUE: Neon verified all 3 links of `(B0,B2)` double-`Obs2` at `(0,-3,+1)`; Astra ran 24-body `(B0,B1)` fixture 10k ticks at PL14; Fable invented towerless `S1/P2` `Rod(0h)` unit | Proved `B1(5G+2R) -> B2(Obs2+S)` pickup & PL13 local witness in sim; B0 failed 11-cell routing across 3.12M clear poses (stall 1/2 on PL) |
| 6 | `58e8c48` | `round6/` (no closed PL14 flyer) | 15 (record held) | — | — | — | — | 3-0 STOP (Astra, Neon, Fable): 100% `work missing something`; `ext_a` solves towers down to PL10-12 but does not close PL14 back ring (`max sum(t) = -3` vs `-2` required) | **STOPPED at 2-round stall bar; verified PL15 record locked (-3 PL vs baseline PL18)** |
| 7 (Hail Mary) | `e97328d` | `round7/` (bounds + `two_plane.fixture` + 4 novel demos) | 15 (record held) | — | — | — | — | Max-reasoning panel (`astra` max, `neon` xhigh, `fable` xhigh) + `astra` max 500k builder + strict `verify_climb.py`/`harness.py` (Opus 5.5 high) | **FINAL STOP at verified PL15 (-3 PL vs baseline PL18);** proved PL15+ 3D CP-SAT bounds on `P0-S1-h2-S3`, 2nd-pull towered backs, Glazed/rod bridges, asymmetric crossed pickups, and 4 novel 3.333 bps flight families |

## Round 7 Hail Mary bounds & novel mechanics

- **Strict tooling (`9d7180d`, Opus 5.5 high):** Hardened `verify_climb.py` into a non-zero-on-failure promotion gate with `flyer_sha256`, `git_head`, `engine_sha256`, and `fastsim-bank-stats` (`rounds/r4_pl15_strict.json`: `PASS`, 80/80 at PL15, 0/80 at PL14). Added `harness.py` (`preflight` 9/9 green, `replay` 7/7 green, `manifest validate` green on `round7/manifest.json`).
- **Two-plane `ROD(-X)` + Glazed conductor + dragged-leaf rod double-pull (`round7/two_plane.fixture`, `local_witness`):** 32/32 runs passed at PL12 (0/32 at PL11). In `P0-S1-h2-S3`, exact single-body 3D CP-SAT across 403,920 unique port poses proved `>= 13` rigid cells required -> PL15 minimum with rider and dragged sticky.
- **Second pull on towered back (`round7/second_pull.py`, `round7/back_body.py`):** 12 ten-cell bodies admitted 70 survivors; max 6-link offset sum `-6` vs `-4` required.
- **Glazed bridges & donor conductors (`round7/plates.py`, `round7/conductors.py`):** 38,080 carrier poses + 98,736 donor poses across all 6 near-closing edges yielded 0 passing hopper-order checks.
- **Asymmetric 6-body & crossed pickups (`round7/offsets.cpp`, `round7/world.cpp`):** 314,432 assignments yielded 216 X-viable placements and 0 six-slot compatible hardware sets.
- **Novel autonomous-flight demonstrators (`round7/novel_demos/`):** Four spacious 3.333 bps flyers passing 10,000-tick `fastsim-bank-stats` with 0 failures and conservation intact: `mmwmmw_glazed_conductor_demo.flyer` (9-body `3 mmwmmw + 6 mmmmww`, Glazed obstruction-conductor gating 4 hoppers across 2 bodies), `all_sticky_3leafpush_demo.flyer` (0-hopper 3-simultaneous-leaf-push ring), `two_hopper_two_sticky_demo.flyer`, and `nine_slot_double_pull_pl150.flyer` (9-slot `wwwmmmmmm` double-pull ring). Single-body 3D CP-SAT bounds all four standalone families at PL15-18.

## Round 6 stall triage & final bounds

- **Stall buckets (Rounds 5-6):** `work missing something` = 100% (all 5 tested PL14 families hit geometric/order walls); `grader wrong` = 0; `case vague` = 0; `infrastructure` = 0; `variance` = 0 (noise floor = 0).
- **Double-`Obs2` `(B0, B2)` mixed screw (`round6/flex.cpp`, `round6/sweep.py`):** 30,042 joins (fixed) + 7,241 (joint) + 1,013,410 (crossed) gave 0 backs at caps `(10, 11, 6)`. Relaxed `(0, -3, +1)` closed at `B0=14` (`relaxed_back.backs`, B0 load 18, B1/B2 = 14) with 0 at B0 caps 12-13.
- **Double-`Obs2` `(B0, B1)` rear-pickup search (`round6/backup.cpp`, `round6/three.cpp`):** 8.71M + 7.13M armed front placements gave 0 compatible opposite halves within PL14 B0 budget.
- **Towerless `S1/P2` mid-stroke rigid push (`round6/midstroke.rs`, `round6/midstroke_order.fixture`):** real update-order collision at Rod slot 3 when P2's carrier retracts first and pushes Rod into its own extended pulling arm (`immovable obstruction` even at PL15).
- **Maintainer `ext_a` back-ring bounds (Round 6 panel):**
  - Lightning rods adhere to both slime and honey identically to redstone blocks (`src/sim.rs:279-287`); `ext_a` avoids sticking through move-order asymmetry and uses `t = -4` coaxial links.
  - Exhaustive pairwise search with `ext_a` rear-rod `B2` across `{O3, T3}^3` at PL14 caps `(11, 11, 7+1S)` gives `max(t0 + t1 + t2) = -5` (needs `-2`).
  - Even removing `B2`'s back sticky via a 6-tower `ext_a` setup across all 27 `{O3, T3, A3c}^3` triples at `(11, 11, 8)` tops out at `max(t0 + t1 + t2) = -3`, 1 X-step short of `-2`.
  - Dual-`O3` same-phase 2-RB sharing: 0 valid 2D configurations. 6-phase pull-first rings fail on early hopper firing at `s = 2`.

## Maintainer references added after Round 6

- `refs/3_3.33_ext_a.flyer` (60b, `17x3x3`, engine-less open extension: 0 standalone distance, finite 48-extension startup sequence clears PL12 and fails PL11 across 80/80 cases; with 3 prescribed rear pushes per 12-tick period, passes 80/80 at PL12 and 0/80 at PL11): single rear-facing `-X` lightning rod behind a 5-slime cross (`5G + 1Rod + 1S = 7` fixed -> load 10 interior, load 11 four-push plate, load 11 tip, load 12 transition). Worth reusing as the tower template in any future climb that discovers a PL14-capable back ring.
- `refs/3_3.33_ext_b.flyer` (74b, `16x6x6`, engine-less open extension: 0 standalone distance, finite 65-extension startup sequence clears PL13 and fails PL12 across 80/80 cases): downward-rod 8-fixed interior plates (load 11-12).

## Round 5 dead ends logged

- Fixed-stencil `B2(Obs2+S)` + `B0(3-hopper + P)` mixed screw (`round5/spine.cpp`, `round5/handoff.cpp`): `B1(5G+2R) -> B2(Obs2+S)` pickup passed real sim at both hopper orders and phases, and `round5/towers.cpp` is ready for 4/5-level PL14 towers, but `B0` failed to connect within 11 glue+RB across 40,019 (front P) and 3,123,090 (rear P) clear arrangements (`T3->O3` needed 15, `T3->T3` needed 14).
- Standalone 6-body `Obs2+P+S` ring with shared diagonal pickup + side observer (`round5/ring.cpp`): local 9-cell witness flew 4 moves at PL13 (loads 13/12/11/11), and 9,942/19,746 PL14 triples had connected core routes before rigid actuators, yet 0 completed all 6 paired actuator placements inside that fixed stencil (repeating the witness's exact X-geometry sums to rest-offset `-24` vs required `-4`).

## Round 4 PL14 dead ends logged

- Staggered-X 3-phase half-turn back rings (`round4/stretch.cpp`): offsetting one of three back hoppers by ±1..2 along X across O3/T3/A3c footprints at `t1 = -3` and caps `(11, 11, 7)` yielded 4,000 middle-to-sticky placements across 2,216 oriented pairs and 0 closed rings. Breaking PL14 requires changing the back-ring mechanism (e.g. 6-phase odd+even double-pulling, rigid pushes, or 2-hopper cores).

## Round 2 stall triage (buckets)

- **Work missing something:** 100% (160/160 PL17 failures across Rounds 1-2; both rounds stayed in uniform 4-rider single rings).
- **Grader wrong / Case vague / Infrastructure / Variance:** 0%.
- **Panel vote:** Astra STOP, Fable STOP, Neon CONTINUE.
- **Orchestrator decision:** Take one strictly bounded Round 3 shot at Neon's arithmetic-verified 6-body mixed screw (`A4 -> T3 -> O3` x2, `B0/B3` towerless) + 4 `gap=3` vertical towers (first multi-level architecture of the climb). Stop immediately if Round 3 does not clear PL17.

## Round 2 dead ends logged

- Self-pulled 6-body and 3-body rings (`round2/openplus6_pl18.flyer` 107b PL18, `round2/openplus3_pl19.flyer` 55b PL19): flew cleanly 80/80 with lightning-rod sticky power and cross-body shared RB on body 2 (loads: bodies 0,3,5 = 18; bodies 1,2,4 = 17). Bounded PL17 negatives in `round2/search-results.txt`: fixed-hardware `contract.py` proves bodies 0,3,5 need 11 glue; 256,983 local edit/piston/face perturbations of `openplus6_pl18` all failed; 18,462,838 open-plus 6-body closed link combos, 165,848 3-body template placements, and 1,866,004 perturbed placements found no routed PL17 flyer.

## Round 1 dead ends logged

- Pure 6-body 4-hopper ring built from compact flat/two-level modules (`round1/flexible.py`, 1,360 PL17 links across 4 core shapes + 30 flat templates + 39 free-pickup + 48 rod-powered + 366 two-level split layouts): every PL17 link obeys `t <= -1 + p[to] - p[from]`, capping 6-link offset sum at `-6` (needs `-4`). Single handoff reached PL16 (`round1/pl16_handoff.json`), and `screw6_pl18.flyer` hit 4 bodies at load 17 and 2 bodies at load 18 (108 blocks, 80/80).
