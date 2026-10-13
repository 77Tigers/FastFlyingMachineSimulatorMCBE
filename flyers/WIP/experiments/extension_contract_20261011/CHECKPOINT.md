# Current research checkpoint

The 4:44am resumption completed shared-contract integration: Python and Rust
now enforce compiled provenance, contacts and required cells; Rust protects
required cells during mutation. Three preserved bank seeds pass 400 samples
per evaluator, 26 migration differential checks pass, and 25 old bank contracts
still pass in both. Current Python suite: 81 tests. See
`../shared_design_20261013/README.md`. The following earlier snapshots retain
historical limitations that this integration has superseded.

## Update, 2026-10-13

The scheduled shared-design implementation is complete; its one-time automation
is paused. See `flyers/docs/EXTENSION_DESIGN.md` and
`../shared_design_20261013/README.md`. One design now compiles contact plan,
contract and ordered schedule, with runtime supplied/internal provenance and
named contacts. Required initial cells and `advance` identity recurrence are
supported by the base Python checker. Structured failures expose load sources,
port mismatches and recurrence differences. Both 80-case rear-cap sweeps pass.
The combined Python regression suite passes 75 tests.

Claude added `flyers/extension_bank/` (14 entries, 25 published order contracts)
and `tools/src/bin/contract-search.rs`. All 25 contracts independently replayed
successfully here; saved reports total 2,000 passing cases. Its frozen-body
search was still running when inspected and was left untouched. Required cells
address its body-deletion loophole. Its Rust evaluator does not yet enforce
all shared-design assertions; final validation should use the design CLI.

The earlier implementation has since been committed as `92344df`; this update
and some other work remain local. The following is the prior checkpoint.

User explicitly resumed work after the two earlier authorized usage windows.
Workspace is writable again. The old wake-up automation remains paused; no
new timer or credits were requested or used. No commits or pushes were made.

## Verified current state

- Prescribed checker supports ordered multiple same-tick intents with a full
  pending ledger and exact next-tick settlement. Placement is checked against
  all natural chunk/piston steps. Later intents may reuse vacated sources but
  cannot touch prior moving destinations.
- 50 Python tests pass across contract, plan, route and explain. Core unchanged
  this continuation; its previous 28 Rust tests passed. Four old/new ordinary
  40-tick traces previously matched after dropping new metadata fields.
- Primitive calibration: 640/640 cases over four words and both action orders.
- Real separate-body interface: prescribed_fixture/rear_cap/README.md. Fifteen
  original cells from the PL7 2.5bps witness; redstone is supplied at ticks0/2,
  K1 only at tick6 each8-tick period. K0 must naturally push K1 at tick4.
  Both 80-sample runs pass exact translated cell/owner recurrence over three
  periods. Redstone input loads1/1; K1 loads6/6; whole maximum7. This is a
  mixed natural/prescribed subassembly, not an autonomous flyer.
- diagnostic_trial_v2/REPORT.md: fresh low-effort weaker agent repaired the
  frozen broken candidate with one added redstone block, using the diagnostic
  without manual hints or reference access. One occupied-cell proposal was
  rejected before simulation; one simulated repair passed default and80/80.
  Parent confirmed exact original copy, unchanged contract, and one addition.
  No controlled tool-effectiveness comparison is claimed.
- Route bound and failed previous repair evidence remain preserved. The fixed
  diagonal 3bps topology needs at least13 combined blocks; this is scoped.

## Next useful work

Reduce the rear cap's load-7 K0/N pull under the saved executable interface,
or build a genuinely new 3bps extension with similarly explicit obligations.
Keep per-stroke budgets fixed and distinguish endogenous from supplied moves:
replacing an endogenous push can recruit its former actor and break recurrence.
Use boundary state diffs to expose untagged passengers; input words alone are
not a complete causal contract. A new weak-agent task can use these tools, but
avoid turning a single successful repair into a general capability claim.

Reproduce via README and RESEARCH_RUNNER. No lower push-limit flyer or PL6 rear
has been achieved. RESEARCH_LOG remains under5,500 words. All prior failed
variants are labelled in the rear-cap ATTEMPTS.md; current builder and mixed
contracts request exact recurrence and a supplied K1 cap6.
