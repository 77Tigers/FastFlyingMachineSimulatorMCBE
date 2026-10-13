# Shared extension designs

`tools/extension_design.py` compiles one JSON design into a contact plan, physical
contract, ordered prescribed schedule and readable runtime metadata. Its `--check` command
runs contact preflight and simulation with the same named ports. `--samples`
runs the existing 80 RNG/phase cases instead of one case. The source design is
the authoritative interface; generated files are views of it.

From the repository root:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin extension-prescribe
python tools/extension_design.py flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap/rear_cap_design.json --out-dir target/rear-design --check
```

Use `--order before_natural` or `--order after_natural` explicitly when comparing
orders. A passing result applies only to the selected order and tested cases.
Generated outputs are `plan.json`, `contract.json`, `prescribed.txt`,
`runtime.json` and, when checking, `result.json`. Output directories should be
separate from source files. The compiler rebases the relative flyer path.

## Source fields

The version-1 design contains `name`, `flyer`, `period_ticks`, `advance`, `cycles`,
`ports`, `contacts` and `supplied_order`. One slot is two ticks, moving +1 X;
initial coordinates and contact checks are at the boundary before an even tick.

Each port has `name`, `role`, `at`, `word` and a per-slot `provenance` array:

- `internal`: a natural piston action must move this original identity.
- `supplied`: a prescribed action must move it, including carriage as a passenger.
- `null`: a waiting slot.

An input's optional `prescribed_max_load` array identifies explicitly injected
strokes. Non-null entries must have `supplied` provenance and a positive cap.
`supplied_order` is an array per slot listing these explicit inputs in execution
order. A supplied passenger has no explicit injection of its own. Same-tick
order is significant. Optional `baseline_load` and `spare_load` arrays retain
the existing per-input bounds, including bounds on internally generated strokes.

Contacts use the existing plan fields: `name`, `a`, `b`, `slots`, `relation`
(`same`, `adjacent`, `offset`), optional `offset`, and optional `required`.
At least one declared contact is required in this initial design format.
Preflight checks predicted positions; runtime checks the original identities'
actual positions at those same boundaries. Contacts are geometric assertions,
not assertions of powered or legal piston actions.

Optional `required_cells` entries are `{"at": [x,y,z], "cell": encoded_integer}`.
These pin exact initial cells, including material and state, while permitting
additional hardware. They are also enforced by the ordinary Python contract
checker. This prevents initial target-body deletion from silently changing a
challenge. Choose the required subset deliberately: the rear-cap example pins
all 15 initial cells as a conservative reproduction example. This does not
declare rigid bodies or require each member to share a trajectory during a cycle.

`recurrence` supports three distinct obligations in the Python checker:

| Mode | Period-boundary obligation |
|---|---|
| `exact` (default) | Translated cells and piston owners match the initial state. |
| `advance` | Every permanent original identity reaches its own translated origin; piston states may differ. |
| `bounded` | Permanent identities remain in the translating `boundary_envelope`. |

Only `bounded` accepts an envelope. Named port trajectories and identity
conservation are checked in every mode. None of these finite sample results
proves safety under all update interleavings.

## Failure reports and compatibility

`result.json` contains `passed`, the preflight result, simulation case(s) and
`first_failure`: `stage`, `code`, `tick`, `port`, `expected`, `actual`, `message`.
Unknown fields are rejected. A schema error exits 2; a failed check exits 1;
a passing check exits 0. A simulation failure can never be promoted to success
because structured diagnostic details are missing.

The base checker reports structured motion, settlement, input-load and recurrence
failures. Overload details include the actual source set; exact recurrence
reports the first differing cell and mismatch count. Other failures retain their
diagnostic text under a generic failure code. Power-cause analysis remains in
`extension_explain.py`; the design runner does not invent such causes.

Compiled contracts now include per-port `provenance` and root `contacts`.
The ordinary Python checker enforces those assertions directly, together with
trajectories, loads, required cells and recurrence. `runtime.json` is a readable
view rather than an additional required source of obligations. Legacy contracts
without these optional fields retain their previous behavior.

The Rust `contract-search` evaluator also checks required cells, provenance
(including prescribed passengers), and named contacts at pre-action boundaries.
Required coordinates are always protected from mutation, independently of the
older `--freeze-bodies` heuristic. Build the executable actually used by the tools:

```powershell
cargo build --release --manifest-path tools/Cargo.toml --target-dir target --bin contract-search
```

For evaluator comparisons pass explicit `--order before` or `--order after`
matching the contract's `prescribed_order`, and explicit `--recurrence` matching
its mode. The Rust CLI retains its older search defaults (both orders and
identity advance). An order override changes the scenario being tested.
Rust eval-only failure is indicated by JSON `pass:false`; do not infer success
from exit status alone. Search samples and final Python validation remain
necessary; these additions do not prove universal evaluator equivalence.

The format currently covers prescribed +X extensions. `internal` does not bind
a particular actuator identity, push/pull kind or power source. Shared body
membership and routing are not yet represented.
