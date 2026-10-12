# Rear challenge: split the K0/N slot-1 pull below load 7

## Concrete target

Use the saved, real PL7 rear-cap witness
[`bank/pl7/tm_7pl_2.5bps.flyer`](../../../bank/pl7/tm_7pl_2.5bps.flyer) as
the baseline. Preserve the original K0 and N identities and their schedules,
but test a local side/relay alternative in which K0's slot-1 `+X` move no
longer shares one load-7 pull action with N. Require K0 `mmww`, N `wmmw`, and
actual simulator-discovered actions of at most 6 sources for any action moving
K0 within the rear cap. This is a focused subproblem, not a solved PL6 back:
the published backcheck also finds load-7 rider/front actions at distances 4
and 5, outside this local change.

The first candidate should move N on its required slot-1 tick through a
separate side action while the K1 sticky pulls K0 alone. This may need a local
power/transport cell, so its own movement and source set must be counted. Do
not assume independent motion is order-safe; run the real simulation across
phase/RNG samples after one deterministic trace passes.

## Witness and baseline

The PL6-back findings identify the only rear-cap load-7 event as K1's slot-1
pull of K0+N. `bodytrack` on this flyer reports K0 as five blocks (`mmww`), N
as two blocks (`wmmw`), and this event at load 7. A new raw trace confirms the
cause at the identity level: at tick 2, the sticky actor at `[3,1,16]` retracts
with seven sources. Five are K0's original blocks; the other two are N's
original slime at `[2,0,15]` and piston at `[2,1,15]`. At tick 0, N's sticky at
`[2,1,15]` pulls K0 in a five-source action. After that move the N piston sits
next to the moved K0 glue and is reset/movable, so the next pull recruits the
whole two-block N identity. Full source coordinates and original identities
are in [`rear_challenge/stroke_sources.json`](rear_challenge/stroke_sources.json).

The existing extension contract passes the original witness for 3 bounded
cycles, checking the original K0/N identities and words. Its observed K0
source maxima are `[5, 7, null, null]`; whole-assembly max is 7. The baseline
contract records those measured values honestly. For a candidate, keep the
port/recurrence checks and compare the reported slot-1 `input_max_action_loads`
against the challenge threshold 6. Contract v1 has no independent objective
maximum field, so do not mislabel the target 6 as the current baseline or
change the reference budget to manufacture a pass.

## First causal check

Can a redesigned N still move at slot 1 and keep its slot-0 K0 pull while
avoiding K0's face-neighbor recruitment of N's movable piston? The real tick-2
source list shows that this is the exact extra two-source coupling; it is not
an unexplained global load. A side-mounted independent transfer is only a
hypothesis. Check powered reach, required clear cells, same-tick collisions,
and whether N and K0 remain distinct, original identities before routing or
full PL changes.

The PL12 evidence suggests choosing this small cap over another generic side
payload: the current 3 bps contract already validates a glass side payload, and
the tm_smol compaction findings say its packed rear has zero-slack load-12
events and no successful local retrofit. That report's fresh-layout rule
requires a reserved observer lane rather than a blind edit. The PL7 cap instead
has a named, identity-traced 5→7 source-set change and a sharply stated load-6
target.

## Reproduction

From the repository root:

```powershell
target/release/bodytrack.exe flyers/bank/pl7/tm_7pl_2.5bps.flyer 96 48 8
python flyers/WIP/experiments/extension_contract_20261011/rear_challenge/analyze_strokes.py
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/rear_challenge/rear_cap.json --out flyers/WIP/experiments/extension_contract_20261011/rear_challenge/baseline.json
```

The body report derives the roles and words from the saved file; the trace
extractor uses RNG 5, phases 0/0, and follows the original K0 identity through
the first period. The contract uses the same saved-file gauge, a 8-tick period,
`+2` advance, three cycles, and the initial `[0,0,15]`–`[9,3,18]` hardware
envelope. The checked baseline passes the port schedule with loads 5 and 7; it
does not claim the rear meets the load-6 target. The source trace binary is
`target/release/extension-trace.exe`.

Provenance: [`RESEARCH_LOG.md`](../../../RESEARCH_LOG.md) points to
[`pl6_back_20261011/FINDINGS.md`](../pl6_back_20261011/FINDINGS.md), which
documents the user's PL6-back goal, the load-7 relay law, and bounded-model
negatives. The PL12 comparison is in
[`tm_smol_rebalance_20261001/FINDINGS.md`](../tm_smol_rebalance_20261001/FINDINGS.md)
and [`FRESH_LAYOUT_CONTRACT.md`](../tm_smol_rebalance_20261001/FRESH_LAYOUT_CONTRACT.md).
The corresponding saved-witness `bodytrack` output and exact source-set
extraction are retained beside this challenge.
