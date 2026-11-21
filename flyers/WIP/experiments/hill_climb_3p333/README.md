# 3.333 bps push-limit hill climb

This folder records a 7-round hill climb lowering the minimum verified push limit for 3.333 bps Minecraft Bedrock flying machines from the baseline **PL18** (`flyers/bank/pl18/nk_lat_n4.flyer`, 224 blocks) down to verified **PL15** (`round4/mixed_screw_pl15.flyer`, 282 blocks).

## Quick start

Verify all 7 headline flyers in one command:

```bash
python flyers/WIP/experiments/hill_climb_3p333/harness.py replay
```

Run the strict 80-case 10,000-tick promotion gate on the PL15 record:

```bash
python flyers/WIP/experiments/hill_climb_3p333/verify_climb.py \
  flyers/WIP/experiments/hill_climb_3p333/round4/mixed_screw_pl15.flyer \
  --pl 15
```

## Verified flyers

All flyers below passed 80/80 canonical RNG x chunk-phase cases for 10,000 ticks with distance at least 3,333, zero extension or movement failures, zero conservation mismatches, zero ballast, and 0/80 passing at `PL - 1`.

| Flyer | Verified PL | Blocks | Dims (X x Y x Z) | Speed | Notes |
| --- | ---: | ---: | --- | ---: | --- |
| [round4/mixed_screw_pl15.flyer](round4/mixed_screw_pl15.flyer) | **15** | 282 | 14x12x17 | 3.333 bps | Best result. 20-body mixed-screw back ring with 3-level and 4-level towers |
| [round3/mixed_screw_pl16.flyer](round3/mixed_screw_pl16.flyer) | **16** | 262 | 14x16x10 | 3.334 bps | 18-body mixed screw, 3-level towers, 3 loop hoppers per half-ring |
| [round3/mixed_screw_pl17.flyer](round3/mixed_screw_pl17.flyer) | **17** | 256 | 14x11x13 | 3.334 bps | 18-body mixed screw, 3-level towers, 2 loop hoppers per half-ring |
| [round2/openplus6_pl18.flyer](round2/openplus6_pl18.flyer) | 18 | 107 | 6x8x10 | 3.333 bps | Towerless 6-body self-pulled ring with rod-timed stickies |
| [round1/screw6_pl18.flyer](round1/screw6_pl18.flyer) | 18 | 108 | 5x10x11 | 3.333 bps | Compact 6-body pure hopper screw |
| [round2/openplus3_pl19.flyer](round2/openplus3_pl19.flyer) | 19 | 55 | 6x6x6 | 3.333 bps | Compact 3-body self-pulled cluster |

## Novel mechanism demos and fixtures

- [round7/novel_demos/](round7/novel_demos/README.md): four spacious 3.333 bps proof-of-concept flyers that pass 10,000-tick `fastsim-bank-stats` with zero failures, demonstrating glazed-terracotta obstruction-conductor gating (`mmwmmw_glazed_conductor_demo.flyer`), 3 simultaneous leaf-pushed stickies (`all_sticky_3leafpush_demo.flyer`), 2-hopper + 2-sticky leaf-push timing (`two_hopper_two_sticky_demo.flyer`), and a 9-slot double-pull ring (`nine_slot_double_pull_pl150.flyer`).
- [round5/local_witness_pl13.fixture](round5/local_witness_pl13.fixture): 16-block PL13 local witness using a rigid push, two observer-gated hoppers, and a sticky pull.
- [round7/two_plane.fixture](round7/two_plane.fixture): 16-block PL12 local witness where a moving rear-facing lightning rod powers 3 actuators and drives a second rod by obstruction.
- [refs/](refs/): maintainer rod-extension references `3_3.33_ext_a.flyer` and `3_3.33_ext_b.flyer` used in Round 6 and Round 7 back-ring bounds.

## Full ledger and per-round notes

- [MISSION.md](MISSION.md): full 7-round ledger, panel scores, and dead-end log.
- Per-round summaries: [round1](round1/SUMMARY.md), [round2](round2/SUMMARY.md), [round3](round3/SUMMARY.md), [round4](round4/SUMMARY.md), [round5](round5/SUMMARY.md), [round6](round6/SUMMARY.md), [round7](round7/SUMMARY.md).
- Strict verification artifacts live in `rounds/`, including [rounds/r4_pl15_strict.json](rounds/r4_pl15_strict.json) for the PL15 record.
