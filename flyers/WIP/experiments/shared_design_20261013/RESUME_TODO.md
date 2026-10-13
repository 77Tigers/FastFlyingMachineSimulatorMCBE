# Integration TODO and decisions, 2026-10-13

This task-specific work record is separate from the task-neutral AGENT_HANDOFF.
The scheduled resumption is authorized and its one-time automation is paused.

## Prescribed-event scheduling coverage

- [x] Address scheduling coverage before claiming that an extension is reusable
  under arbitrary update order. Previously natural chunks and pistons were shuffled,
  but prescribed moves ran as one batch before or after all natural piston updates;
  same-tick prescribed moves retain script order. Previous prescribed moves settle
  after the power snapshot and before natural updates. Seeds do not vary these
  choices, and passing both batch positions does not cover intermediate interleavings.
- [x] Characterize the limit: external inputs have no actuator coordinate or
  driver ownership; a concrete actuator visits its chunk/piston schedule and
  settles through its owner. The new mode is synthetic stress, not uniform
  sampling or a physically validated driver model.
- [x] Add explicit reproducible `interleaved` mode. Preserve legacy before/after
  modes and their script order; only the opt-in mode shuffles supplied events.
- [x] Cover natural A -> supplied input -> natural B and relevant permutations of
  multiple same-tick supplied inputs. Record the realized order and seed in failure
  output. Check movement/settlement timing, observer pulses, load limits, and
  passenger provenance; preserve normal simulation behavior without supplied events.
- [x] Add a real-bank regression demonstrating that passing both batch positions need not
  imply passing an intermediate interleaving. Check Python/Rust evaluator agreement
  on the new mode and rerun affected real extension fixtures. Report exactly which
  schedules were tested, without upgrading finite samples to a universal guarantee.

This is a prerequisite to a robustness claim in the planned weaker-agent extension
challenge, not a reason to add rigid-body or mandatory actuator-identity features.

Evidence and reproduction: scheduling/README.md and scheduling/evidence/report.json.
Four unchanged fixtures, three modes, 80 samples: 960 individual Python/Rust
comparisons agree. n4_14 passes both batch modes but fails 0/80 interleaved checks
due to supplied-input ordering (load 17/cap 16); do not mislabel it as a strict
natural-A/input/natural-B witness. n2_05 and n4_13 pass 80/80 interleaved samples.
A separate core regression now witnesses that strict intermediate gap: A settles
a moving stone, the supplied slime input temporarily recruits it (load 2/cap 1),
then B moves it away. The same seed passes both endpoint modes. Current suites:
87 Python tests, 31 core Rust tests and 2 Rust evaluator tests pass.

## Next implementation increment: construction usefulness

1. Choose a known feasible separate-output, phase-shifted extension challenge.
   Freeze its supplied motion, caps, protected cells, output identities/motion,
   recurrence and editing region using the existing schema.
2. Keep the complete mechanism as a hidden witness; remove a functional part for
   the starting candidate. Verify pass/fail and exclude a mere passenger solution.
3. Package task files, one evaluation command, acceptance checks and an attempt
   budget separately from the task-neutral AGENT_HANDOFF. Keep revealing reference
   history out of the agent's supplied context.
4. Run a fresh weaker-agent attempt. Record candidates, latency, feedback,
   interventions and outcome. Identify the largest demonstrated obstacle.
5. Implement one targeted feedback/usability improvement, add relevant regression
   coverage and cross-check both evaluators if semantics change.
6. Test transfer on a second challenge; then tighten one load or size requirement
   while keeping the rest of the interface fixed. Save evidence and a checkpoint.
7. Before claiming a reusable physical extension, validate its inputs with a
   concrete driver, including physically possible action and settlement orders.

Rigid-body requirements and mandatory actuator identity remain deferred until a
real trial demonstrates their necessity. No broad search campaign is scheduled.

## Completed integration: priority and completion boundary

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
  are allowed. Legacy prescribed action order remains the script row order;
  explicit interleaved mode shuffles supplied events.
- Preserve exact/advance/bounded distinctions, input budgets for natural strokes,
  and explicit action order. Do not silently turn a one-order contract into both.
- Internal means a natural piston movement; binding actuator identity/action/power
  is deferred. Do not infer power causation from geometry or resetting alone.
- Keep the design CLI as source of generated views, but have the base checker
  enforce compiled assertions. Avoid duplicate competing runtime validators.

## Known code and evidence

`tools/extension_design.py` compiles the current design. Standalone Python and
Rust contracts enforce compiled provenance and contacts. Python also supports
required_cells, advance recurrence, structured first_failure and the compatibility
run_case(checker_factory=...) hook. The prior 75-test/160-sample baseline is
historical; current scheduling evidence is linked above.

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
