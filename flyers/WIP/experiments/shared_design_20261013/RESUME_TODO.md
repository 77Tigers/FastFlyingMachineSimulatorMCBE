# Integration TODO and decisions, 2026-10-13

This task-specific work record is separate from the task-neutral AGENT_HANDOFF.
The scheduled resumption is authorized and its one-time automation is paused.

## Priority and completion boundary

Python priorities 1 and Rust priority 2 have been implemented during this
resumption. Full Python suite: 81 passing tests. Rust assertion tests: 2 passing
tests. The rebuilt `target/release/contract-search` agrees with Python on the
rear baseline plus four negative cases and all 25 legacy bank contracts.
Bank migration and its differential/sample validation are complete: five
supported orders pass 400 samples in each evaluator; 26 migration differential
checks pass, including the separately labelled unsupported order. Three seed
files are byte-identical to the original bank fixtures. See README.md for evidence.

1. Put movement provenance and contact assertions into compiled contracts so
   running a contract directly cannot omit them. Preserve legacy contracts.
2. Enforce required initial cells, provenance and contacts in Claude's Rust
   evaluator; protect required cells from mutation as well as checking them.
3. Migrate representative bank examples into shared designs in a separate
   experiment directory: n2_05 (rear), n2_04 (supplied passenger/one order),
   n4_13 (aliased input/output and piston rides). Preserve original bank files.
4. Validate positive and deliberately broken examples across both evaluators;
   run the existing regression suite and sample migrated passing orders.
5. Document exact support and any remaining gaps. No large search campaign,
   new physics, new flyer-record claim, or broad abstraction rewrite is needed.

## Representation decisions

- Add optional per-port `provenance`: internal/supplied/null per movement slot.
  Null only on waits; supplied includes passengers of a prescribed move.
- Add optional root `contacts` using the existing named-port plan contact schema.
  Check contacts before even-tick actions, following original identities.
- Existing required_cells stays `{at:[x,y,z],cell:encoded_integer}` and constrains
  exact initial cells. It does not imply rigid bodies or intermediate trajectories.
- Old contracts without new fields retain old behavior. Same-identity aliases
  are allowed. Explicit prescribed action order remains the script row order.
- Preserve exact/advance/bounded distinctions, input budgets for natural strokes,
  and explicit action order. Do not silently turn a one-order contract into both.
- Internal means a natural piston movement; binding actuator identity/action/power
  is deferred. Do not infer power causation from geometry or resetting alone.
- Keep the design CLI as source of generated views, but have the base checker
  enforce compiled assertions. Avoid duplicate competing runtime validators.

## Known code and evidence

`tools/extension_design.py` compiles the current design. Its runtime mixin checks
provenance and contacts, which standalone contracts currently omit.
`tools/extension_contract.py` already supports required_cells, advance recurrence,
structured first_failure and run_case(checker_factory=...). Baseline: 75 tests,
160 shared rear-cap samples; 25 old bank contracts replayed successfully.

`tools/src/bin/contract-search.rs` uses a small custom JSON parser. Relevant hooks:
Port/Ctx, load_ctx, run_order (identity map before each tick and action labels),
and immutable construction before MutCtx. `--freeze-bodies` is optional and
heuristic; explicit required_cells must always be honored independently of it.
Rust search defaults to advance recurrence and both orders; pass explicit
`--recurrence` and `--order` for comparisons with Python contract semantics.
Build only named binaries; unrelated research bins have older API mismatches.

Claude's files: flyers/extension_bank and
flyers/WIP/experiments/extension_bank_20261012. Its frozen batch now has log entries
through n4_14, with no reported endogenous-load improvement. Inspect actual
results before summarizing. Failed local search is not an impossibility proof.

## Checks and safeguards

- Reject body deletion/material change through required_cells in both languages.
- Reject supplied passengers mislabeled internal, and wrong named contacts.
- Ensure malformed fields fail rather than silently disappearing.
- Test same-identity input/output aliases and distinct same-tick caps.
- Test standalone compiled contract parity with design CLI.
- Replay all published old contracts once; preserve their original evidence.
- Save migrated design sources/generators, sample results and differential report.
- Run Python test_extension_{design,required_cells,advance,contract,plan,route,explain}.
- Build Rust contract-search specifically and run relevant new Rust tests.
- Do not overwrite Claude's bank/search results, bulk stage unrelated work,
  reset Git, buy credits, or restart recurring timers.

Current checkout may need scoped sandbox escalation for shell Git/Python commands
in scheduled sessions; ordinary apply_patch worked in the previous session.
Inspect actual permissions and errors rather than assuming unavailable access.
