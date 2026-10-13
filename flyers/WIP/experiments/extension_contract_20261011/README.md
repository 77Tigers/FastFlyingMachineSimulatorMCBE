# Extension contracts: first executable bridge

The research goal is easier construction and repair by weaker agents, measured
on real flyer problems. Long-term target: 3.333 bps at PL12. Intermediate targets
include useful 3 bps interfaces at loads 10–11, compact mechanisms and a PL6 rear.
This increment supplies **contact and route preflight, actuator diagnostics,
concrete-driver validation, and physical or prescribed input harnesses**. The harness validates short commanded
primitives; it does not establish an autonomous mechanism. None of these tools
is a router or a general feasibility solver.

## Start here

From the repository root, build the isolated trace backend:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-trace
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-drive
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-prescribe
python flyers/WIP/experiments/extension_contract_20261011/build.py
python tools/extension_plan.py flyers/WIP/experiments/extension_contract_20261011/plans/burst_relay.json
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/benchmarks/reference.json
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/benchmarks/payload.json --samples --out flyers/WIP/experiments/extension_contract_20261011/out/payload_samples.json
```

Build the named binaries individually: unrelated older research binaries have
an existing trace API mismatch. Prescribed mode uses the opt-in
`PrescribedSession` API in this checkout; rebuild its backend after simulator
API changes.

Calibration results are in [RESULTS.json](RESULTS.json), with interpretation
and limits in [FINDINGS.md](FINDINGS.md). The human 3 bps reference and its
tagged side-payload variant each passed 80/80 RNG/phase cases at 30 ticks.
These are short bounded-hardware checks, not bank-standard runs or a controlled
test of weaker-agent capability.

The separate [external-drive fixture](external_drive/RESULTS.json) tests three
commanded glue-column schedules: `mmmww`, `mmmmww`, and `mmwmmw`, each over 80
RNG/phase cases. Regression tests include real-backend integration. Rebuild it with
`python flyers/WIP/experiments/extension_contract_20261011/external_drive/build.py`,
then run `python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/external_drive/contracts/mmmww.json --samples --out flyers/WIP/experiments/extension_contract_20261011/external_drive/out/mmmww_samples.json`
and summarize with `python flyers/WIP/experiments/extension_contract_20261011/external_drive/summarize.py`.
The commanded fixtures validate the adapter and its diagnostics; they do not
claim a self-running mechanism.

## Cheap contact preflight (pipeline stages 3–4)

`tools/extension_plan.py PLAN.json` accepts named points with initial world
coordinates and movement words. All positions are **before power at slot 0**;
one slot is two ticks. Each `m` means a +1 X movement starts in that slot and
settles on its second tick. Positions at a later slot include preceding moves.
All objects must have the same declared cycle advance.

Each contact names two points, the slots in which to check them, a relation
(`adjacent`, `same`, or `offset`), and whether it is required or forbidden.
For `offset`, the vector is **b minus a**. Unlisted relations remain unresolved.
Aliased points are permitted; connectivity and overlap are not inferred.

The saved `mmmmww` and `mmwmmw` examples compare contact windows at 3.333 bps.
`split_relay_wrong_window.json` incorrectly asks for the second of two identical
relative configurations to be separated. It should fail at slot 3 / tick 6,
without generating or routing a single block.

**CONSISTENT is not FEASIBLE.** These are kinematic contact checks only. They
do not prove actuator recovery, material adhesion, power, moving-source
availability, intermediate update-order safety, connection routes or load.
In particular, an adjacent named "source" is not automatically a powered piston.

Exit codes: 0 consistent, 1 contradicted, 2 malformed input. `--out FILE.json`
saves the verdict and the first failed declared obligation with coordinates.

## Concrete-driver contracts (pipeline stages 5–7)

`tools/extension_contract.py CONTRACT.json` streams actual Rust simulation
steps. A contract contains:

- `version: 1`, a `name`, and `flyer` relative to the contract file;
- an even `period_ticks`, positive `advance`, and `cycles` (default 3);
- `ports`, each with a unique name, role `input` or `output`, initial world `at`
  coordinate, and a movement `word` with `period_ticks / 2` characters;
- input `baseline_load` and `spare_load` arrays, one entry per slot;
- `recurrence: "exact"` or `"bounded"`; bounded mode also requires
  `boundary_envelope: {"min": [x,y,z], "max": [x,y,z]}` in the initial gauge.

A port names an **original permanent block identity**, not whichever block
later occupies its position. The validator follows all identities through each
successful movement and checks named ports after every tick. Exact mode compares
complete translated cell states and piston ownership at cycle boundaries.
Bounded mode instead requires all permanent identities to remain inside the
declared envelope, translated by the cycle advance at each boundary. Even ticks
start moves; odd ticks settle them. Save/load normalization matters: derive port
coordinates from the saved file, not a pre-save editor gauge.

For an input action, actual load is the whole discovered movement set, including
the original driver load, every passenger, and collision-recruited blocks.
The permitted load is `baseline_load[slot] + spare_load[slot]`. Baseline includes
the input block itself. Each declared input bound is checked independently;
two ports in the same action never pool their capacities. Null entries describe
waiting slots. Freeze baseline budgets before constructing a candidate.

With no `drive_script`, the checker uses an actual self-running driver and
**observes and checks** the declared inputs; it does not impose their movements
or power. With a `drive_script`, it injects and removes only the declared
temporary piston/redstone fixtures, then checks ordinary simulator movement
and tagged port identities. It tracks each temporary piston arm as hardware:
the arm must remain attached and unchanged through its scheduled extension,
and can disappear only at the ordinary retraction tick. Arms cannot be movement
sources. This is a scripted primitive harness, not a self-running machine. The
simulated file's encoded push limit still applies to every piston action. A
higher whole-assembly limit does not waive any input budget. Preserve the
distinction between local extension cost and whole-flyer PL.

With `prescribed_script` and `prescribed_order`, `extension-prescribe` injects
the declared input block's +X move directly, while the simulator continues to
run its ordinary piston updates. Each script row is `tick x y z max_load`; the
tick is an even start tick, and the following tick settles that move. The
contract must name the moving input at its expected phase coordinate. The
checker verifies every injected movement source and destination, the source
cap, monotonically assigned move IDs, and the pending-to-settled lifecycle; it
counts the whole discovered set, including passengers. Settlement overlays are
checked against pending destinations and are not counted as another
translation. `prescribed_order` is `before_natural` or `after_natural` and must
match the trace's placement relative to all natural chunk and piston steps. This mode
checks port words, candidate-state recurrence, and load budgets under an
explicit prescribed-input assumption. It does **not** establish that a natural
actuator can realize the injected move or that the flyer is self-running.

The three-glue `prescribed_primitive` fixture is a focused adapter calibration.
Its `mmmww_before` contract passes the real backend integration test at 30
ticks, with whole-action maximum 3 and input loads `[3,3,3,null,null]`. This is
one prescribed primitive smoke case, not a separate-body mechanism result or
an autonomy claim. Reproduce it with:

```powershell
python tools/extension_contract.py flyers/WIP/experiments/extension_contract_20261011/prescribed_primitive/contracts/mmmww_before.json
```

`--samples` checks the established 80 RNG/phase combinations. This is sampled
evidence, not an all-orders proof. Three cycles are an early contract screen,
not the 10,000-tick bank standard. Exact hardware recurrence is a deliberately
strict fixture option, not a new requirement on every valid flyer. The human
3 bps benchmark uses bounded mode because its interchangeable piston states
vary: this checks sampled port motion and hardware confinement, not indefinite
closure or exact-state recurrence. Odd-tick/variable-duration movement remains
future work.

Exit codes: 0 all requested cases pass, 1 a physical contract fails, 2 malformed
input/tool setup. Use `--out FILE.json` to preserve compact per-case results.

## Trace-guided failure explanation

`tools/extension_explain.py FLYER --contract CONTRACT.json --tick T` replays the
real `extension-trace` backend through zero-based tick `T` and prints one compact
JSON object. It follows the contract port's original identity through movement
overlays, then reports its pre-power position and observed move, nearby piston
actions, nearby power-source transport history, and extension `candidate_pushers`.
For a contract with several ports, select one with `--port-name NAME`. Without
a contract, provide `--port X Y Z --tick T` to tag the permanent block at that
initial saved coordinate. Optional `--rng N --phase-x N --phase-z N` overrides
reproduce a chosen trace ordering; omit all three to use the flyer state.

```powershell
python tools/extension_explain.py flyers/WIP/experiments/extension_contract_20261011/blind_repair/out/candidate.flyer --contract flyers/WIP/experiments/extension_contract_20261011/benchmarks/missing_source.json --tick 2
python tools/extension_explain.py INPUT.flyer --port 13 4 7 --tick 2
```

The report distinguishes adjacent sources from power eligibility and computes
pre-power status using `SIMULATION.md`, including moving-source/target and
piston-front rules. `candidate_pushers` is a geometric extension-front,
obstruction, and adhesion screen; it does not prove a legal move, complete
actuator inventory, push-limit fit, or destination safety. Sticky retraction
and pull reach are not enumerated. The helper diagnoses a trace and does not
repair a flyer or establish a contract pass.

## Working on a challenge

1. Freeze the input driver, port names, movement words and spare budgets.
2. State required and forbidden contact windows. Run the cheap preflight.
3. Build a small interface and run one concrete contract case immediately.
4. Repair the first reported contradiction; do not relax a benchmark to pass.
5. Once the case passes, run phase samples and increase duration as warranted.
6. Report external assumptions, local loads and whole-driver cost separately.

Favor side pickup and short glue connections. Before routing, count hardware
and mandatory connectors already committed to each action. Treat expensive
axial piston pickup as a warning to explain, rather than a universal ban.

## Next increments

The passive side payload is a harness calibration, not a novel extension
mechanism. The scripted fixture is likewise a primitive calibration, not
independent mechanism discovery. The rear-cap example below now provides
separate target phases. Two targets and literal repeated modules remain useful
additional benchmark shapes.
Scripted drives must retain explicit ordering and ordinary simulator movement
discovery; never teleport exactly a listed set and hide its adhesive passengers.

Other missing pieces: connecting the sparse plan to named realized contacts,
local swept-space and power checks, load lower bounds, and an agent-facing
view of the first failure. Preserve state-based exceptions to adjacency rules.
Run controlled fresh-agent tasks with/without the tools before claiming a
reduction in time, tokens or stronger-agent interventions.

## Multiple inputs and a separate-body fixture

Multiple script rows may share a tick. Their order is significant and is
preserved by the backend and checker. Each action has its own pending record;
all discovered destinations stay moving until the next tick. A later action
may enter an earlier action's vacated source cell, but cannot use its still-
moving destination. IDs, full ledgers, per-action loads and every settlement
are checked. Input movement words need not be entirely prescribed: omit a
scripted stroke when the candidate's internal actuator must provide it.

The [15-cell rear cap](prescribed_fixture/rear_cap/README.md) is a reference-
derived mixed interface with separate output phases. It passes 80/80 samples
for each natural-action order with exact translated cell/owner recurrence.
The [fresh diagnostic trial](diagnostic_trial_v2/REPORT.md) repaired a supplied
broken candidate with one added block and passed 80/80 without manual hints.
These establish bounded task results, not a new flyer record or a controlled
measurement of weaker-agent improvement. See the current checkpoint for test counts.
