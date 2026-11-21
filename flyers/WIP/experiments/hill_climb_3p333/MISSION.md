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
| 1 | pending | `round1/screw6_pl18.flyer` | 18 | 20/20 | 60/60 | 108 | 3.333 | Pending Round 1 panel | Kept as compact PL18 control; pure 6-body hopper ring hit `sum <= -6` wall (stall 1/2 on PL) |

## Round 1 dead ends logged

- Pure 6-body 4-hopper ring built from compact flat/two-level modules (`round1/flexible.py`, 1,360 PL17 links across 4 core shapes + 30 flat templates + 39 free-pickup + 48 rod-powered + 366 two-level split layouts): every PL17 link obeys `t <= -1 + p[to] - p[from]`, capping 6-link offset sum at `-6` (needs `-4`). Single handoff reached PL16 (`round1/pl16_handoff.json`), and `screw6_pl18.flyer` hit 4 bodies at load 17 and 2 bodies at load 18 (108 blocks, 80/80).
