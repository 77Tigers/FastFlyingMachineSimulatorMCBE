# Findings: extension-contract calibration

This calibration connects sparse contact plans to checks against real simulator
movement. It does not show that weaker agents build or repair flyers better;
there was no controlled with-tools/without-tools agent comparison. The task's
long-term goal remains independent extension construction, and this experiment now includes a reference-derived mixed-input rear cap
and a successful bounded diagnostic-assisted repair.

## Reproduction and reference

From the repository root:

```powershell
python flyers/WIP/experiments/extension_contract_20261011/build.py
python flyers/WIP/experiments/extension_contract_20261011/check.py --samples --out flyers/WIP/experiments/extension_contract_20261011/RESULTS.json
```

The builder copies `flyers/bank/pl12/human_tm_smol_3bps.flyer` through the
Python save/load path, then traces 30 ticks with RNG 5 and phases 0/0. Ports are
recorded after save/load normalization. The named input glue at `(13,4,7)` has
word `mmmww` and actual whole-action source loads `[9,8,7,null,null]`. The
downstream honey port at `(7,1,4)` has the different-phase word `wwmmm`; its
measured action loads are `[null,null,10,11,12]`. The checker schema only allows
load arrays on input ports, so output load measurements remain in
[`build_summary.json`](build_summary.json), not in the output port contract.

The driver advances three blocks over each 10-tick cycle, but its complete
hardware state does not recur exactly. The contract therefore uses bounded
recurrence with the explicit initial envelope `[0,0,1]` to `[17,7,9]`, shifted
by three in X at each 10-tick boundary. This supports a bounded hardware claim;
it is not evidence of indefinite closure or exact cell/owner recurrence.

## Candidate and calibration outcomes

The builder scanned transverse exposed faces and accepted the first legal one:
glass at `(13,3,7)`, adjacent to the input glue. It remains in the same fixture
at push limit 12. Its named `side_payload` output follows `mmmww`; the input
loads rise to `[10,9,8,null,null]`, the downstream port keeps its schedule and
measured loads, and the 30-tick trace has no failed moves.

[`RESULTS.json`](RESULTS.json) records 80/80 passes for both the reference and
payload at 30 ticks per RNG/phase case (4,800 simulated ticks across those two
batches), plus all expected negative outcomes. The refreshed result took 22.1
seconds including the contact-plan checks. The wrong-phase fixture fails at tick 2 when
the downstream output waits instead of moving. The zero-spare payload fixture
fails at tick 0 when an action uses 10 sources against a budget of 9. The
missing-source fixture removes the redstone block at `(12,5,8)` beside the
tick-zero driver piston and fails the input schedule at tick 2; its real trace
later reports a failed extension at tick 6 from push-limit overflow. Three
contact plans also match their expected results, including rejection of the
wrong second contact window at slot 3 / tick 6.

These are short sampled fixture checks, not the bank's 10,000-tick standard.
The current combined contract/planner suite passes 37/37 tests, including
real-Rust-backend integration. `RESULTS.json` is the refreshed benchmark output
from the checker version described here; 37/37 is the current suite result.

## Review corrections and limits

The final payload contract names the added glass identity as `side_payload`;
the first reviewed draft named only the input and downstream ports, so it could
not enforce the new block's schedule. Output ports do not accept baseline-load
arrays in the current schema; the measured output loads are preserved in the
builder summary. The human driver also required bounded recurrence after full
cell/owner comparison disproved exact recurrence. These choices are stated in
the fixtures instead of being hidden behind a pass result.

The separate external-drive harness injects temporary piston and redstone
fixtures from an explicit script and still uses ordinary simulator movement
discovery. The checker tracks piston arms as hardware too: they cannot be used
as movement sources, change encoded state, or disappear before scheduled
ordinary retraction. It validates short commanded primitives only; it does not convert
this passive payload into an autonomous extension mechanism. No capability,
time-saving, or token-saving claim is supported without a controlled agent
comparison.

## Post-trial causal audit: missing-source failure

The blind repair trial remained unsolved. A later audit used the original
reference as a diagnostic comparison; it is post-trial evidence, not a blind
repair result or capability claim. At candidate tick 2 the tagged input is at
`(14,4,7)`. Its previous actuator `(12,4,7)` is in state 2 and retracts as
expected. The geometric extension pushers that reach the tagged slime through
the current passenger cluster are `(13,4,8)` and `(13,5,9)`; both are state 0
but unpowered. The candidate's tick-0 stroke moved the tag from `(13,4,7)` to
`(14,4,7)` and redstone from `(12,5,7)` to `(13,5,7)`, which is not adjacent
to either next pusher. The prior actuator's reset was observed but was not the
cause of the miss.

With RNG/phase overrides `0/0/0`, the reference tick-0 action moves the tag and
carries redstone from `(12,5,8)` to `(13,5,8)`. At tick 2, piston `(13,5,9)`
uses that adjacent source to move the tagged block to `(15,4,7)`, while the
previous actuator `(12,4,8)` retracts in the same tick. This is the corrected
causal chain behind the missing-source failure. The reusable
[`extension_explain.py`](../../../tools/extension_explain.py) helper reports
these tagged identities, actor states, geometric pushers, and source origins;
its extension reach is diagnostic only, not a legality proof or full actuator
inventory, and sticky pull reach is not enumerated.

## Scripted external-drive calibration

The companion [external-drive builder](external_drive/build.py) saves a fresh
three-glue column at push limit 12. It drives only the two end glues, tagged as
input ports with baseline load 3 and spare load 0; the middle glue is a tagged
output passenger. The declared schedules are `mmmww` (10 ticks, +3), `mmmmww`
(12 ticks, +4), and `mmwmmw` (12 ticks, +4), each repeated for three cycles.
The script lists target contacts and caps; the Rust adapter injects temporary
fixtures and lets the simulator discover the actual movement set.

[`external_drive/RESULTS.json`](external_drive/RESULTS.json) aggregates 80/80
passes for each word, with exact translated candidate-state recurrence and
tagged port schedules checked over 30 or 36 ticks per sample. This is 240
cases and 8,160 sampled ticks, with measured whole-action maximum 3. The
external piston/redstone source is part of the harness, so these outcomes are
primitive interface calibration only, not evidence for an autonomous flyer.
Two negative controls also reject as expected: a source cap of 2 fails when
three glues move, and a fixture-site collision stops injection before tick 0.
The raw per-case JSON is retained under `external_drive/out/`. The refreshed
combined contract/planner suite passes 37/37 tests, including real-backend
integration and arm-lifecycle regressions. The three external batches took 7.40
seconds summed across cases (about 10.7 seconds including CLI orchestration).

Reproduce the batches from the repository root with the commands in the
[experiment README](README.md), or invoke each contract
with `--samples --out ...` and regenerate the compact aggregate with
`external_drive/summarize.py`. `extension-drive` and `extension-trace` are
separate tools under `tools/`; their use does not require simulator changes.

## Prescribed-input checker calibration

The separate `extension-prescribe` backend exercises the prescribed-action
trace API. Its contract mode verifies that each scripted input is the declared
moving port at its expected phase coordinate, that every actual source moves
exactly +X within the declared whole-source cap, and that the returned move ID
and destinations remain pending until the next tick's settlement. Settlement
sources must match those pending destinations; settlement is not counted as a
second translation. The checker also enforces ordering around natural chunk
processing, checks the existing port and recurrence contract, and rejects
pending moves at a cycle boundary. Its result explicitly labels the run as
prescribed input and does not claim a natural actuator realizes the move.

The focused three-glue `mmmww_before` calibration passed one real-backend case
for 30 ticks: exact translated candidate-state recurrence, whole-action maximum
3, and input loads `[3,3,3,null,null]`. This validates the adapter and checker
ledger for that primitive. It is not a separate-body success, an autonomous
mechanism result, or broad RNG/phase evidence. The reproducible command and
fixture are in the [experiment README](README.md).

## Current results

The prescribed primitive matrix passed 640/640 cases (21,120 ticks); see
[prescribed results](prescribed_primitive/RESULTS.json). Multiple same-tick
intents now use an ordered pending ledger. Tests cover complete settlement,
forged/missing records, ordering against all natural actions, and valid reuse
of a vacated source cell. The final Python suite passes 50 tests; the unchanged
core Rust suite previously passed 28.

The [15-cell rear cap](prescribed_fixture/rear_cap/README.md) passes 80/80
samples in both before/after-natural orders, with exact translated cell and
piston-owner state at each 8-tick/+2 boundary. Redstone input `mmww` consumes
one source per stroke; K1 `wwmm` consumes six. K0 `mmww` and N `wmmw` remain
separate checked outputs. The whole-assembly maximum remains 7.

The important interface correction was to leave K1's first move to K0's
natural push and supply only its second move. Prescribing both moves removed
the natural actuator's exclusion from its own movement set, allowing K0's
piston to ride away and break the following cycle. The boundary diff exposed
that omitted obligation. Timing alone was insufficient; stroke provenance
must remain part of the interface.

A fresh low-effort weaker-agent [repair trial](diagnostic_trial_v2/REPORT.md)
used only the broken candidate, frozen contract, simulator documentation and
tools. After one rejected occupied-cell proposal, it added a redstone block
at `(12,5,8)`: one simulated repair candidate, default pass and 80/80 samples.
The parent independently confirmed the original copy and unchanged contract,
and exactly one added block. No reference lookup or mid-trial manual hint was
provided. This is a bounded successful task, not a controlled before/after
capability comparison. The prior unsuccessful trial and corrected causal
interpretation remain preserved.

No improved push-limit flyer is claimed. The next concrete target is reducing
the rear cap's load-7 K0/N pull while preserving the now-executable interface.
