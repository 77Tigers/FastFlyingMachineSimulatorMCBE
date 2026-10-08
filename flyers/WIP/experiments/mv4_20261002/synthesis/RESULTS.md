# Bounded mv4 geometry synthesis, 2026-10-02

The corrected seed28 fixture physically runs three mv4 cores with starts
100100100100 /010010010010 /001001001001. Over 10,000 ticks it advances 3333,
starts 10,000 extensions, has zero extension/movement/conservation failures,
and reaches maximum successful action load101. This is a working high-PL
timing witness, not a low-PL result or bank claim.

The preserved diagnostic is s28_v3_diagnostic_pl512.flyer; the encoded
PL101 copy is s28_v3_pl101.flyer. Evidence: s28_v3.audit.txt,
s28_v3.10000.bodytrack.txt, s28_v3.bodytrack.txt, s28_v3_pl101.audit.txt.
Its sticky counts are74/89/86 plus four observers per body, with twelve
normal +X pistons total. Every core is connected. No simulator, editor
format, bank, or existing experiment files were changed.

## Bounded original screen

Thirty grid layouts of the same architecture were attempted: four normal
pistons per target core, observer sources on the following phase, and fixed
transverse pickup ports. Two phase1 pickup cells share an axial ribbon.
Sixteen routed; eight were rejected for same-material contact, two for
foreign-source contact, four for routing. All16 were screened for120ticks
at diagnostic PL512. Thirteen had no failed-discovery/conservation event,
but all violated core timing and later stalled or changed schedule. Best
distance was23 in120ticks. Successful action loads rose to278-326 after
multiple cores were incorrectly recruited. Evidence: manifest.json,
screen.csv, screen.txt, candidates/ (2026-10-08 cleanup kept only the diagnosed
s2/s28 candidates; the other 14 are in FastFlyer_WIP_uncommitted_backup_20261008).

The second attempt reused these30 placements after a preliminary keepout
change; mutable external owner-index semantics kept it ineffective. Its
evidence remains in screen_v2.csv (manifest_v2.json and candidates_v2/ were
byte-identical to manifest.json and candidates/; removed in 2026-10-08 cleanup;
`git show 1222fbe:flyers/WIP/experiments/mv4_20261002/synthesis/manifest_v2.json`).
The final causal correction was applied only to seed28; no wider search
was launched.

## First discrepancy and tested correction

Original seed28 has correct core starts through ticks0-6. At tick7 the
phase1 action selects P11 at world(16,9,20). Its destination(17,9,20) is
occupied by the phase2 core's mandatory drive cell. Occupied-destination
discovery recruits that98-block core one tick before its required tick8
move. Load193 comprises87 core1 blocks,98 core2 blocks and eight pistons.
At tick9 all three cores are recruited, load280.

The adjacency that selects P11 is an optional routing cell at
world(16,10,20), original core1-local(-2,9,4). The required pickup cell is
(-3,9,4). P11 was moving at the start of tick7, but could settle before
core1's action. The old router treated its moving flag as immutable for
the whole tick and allowed the unintended additional pickup. Its actual
preceding transports were core0 at3, core1 at4, core0 at6.

The final generator uses the complete reachable competition state union,
symmetrized across interchangeable members, rather than nominal one-fire
per12tick identity trajectories. It maps movement-owner port indices to
their phases, includes same-tick finish before pickup, and indexes pickup
exemptions by both body and member. Contact automaton snapshots preserve
the imported interface during concurrent edits. These corrections remove
the extra routing cell and physically resolve the witnessed failure.

Evidence: s28.trace.txt (raw trace, removed in 2026-10-08 cleanup;
`git show 1222fbe:flyers/WIP/experiments/mv4_20261002/synthesis/s28.trace.txt`),
s28.bodytrack.txt, s28.diagnosis.json.
diagnose.py follows persistent identities through successful SOURCE lists.

## Initial states and recurrence limit

The phase2 core and passengers P1,P3,P5,P7 start moving, owned by P11 in
state1, derived from the preceding nominal cycle. P10 starts state2;
P9 starts state3. Phase1 observers start powered; phase2 observers start
moving. The initial owner list includes the core and all those passengers.

Core motion repeats every3ticks, but exact member identities need not
repeat every12ticks. The audit finds one translated encoded-state repeat
between744 and1176 (+144), not strict12tick recurrence. No bank claim is
made. Low-PL compaction and broad phase/RNG validation remain separate work.

Reproduce corrected fixture:

```
target/release/fastflyer-research audit flyers/WIP/experiments/mv4_20261002/synthesis/s28_v3_pl101.flyer 10000 12
cargo build --release --manifest-path tools/Cargo.toml --target-dir target
target/release/mv4-bodytrack-ticks flyers/WIP/experiments/mv4_20261002/synthesis/s28_v3_pl101.flyer 10000 0 12
```

Pipeline feedback: before routing, keepouts must cover every reachable
power/contact trajectory and both possible same-tick finish/start orders.
Check a transported passenger's occupied destination as well as source
adjacency. A start-of-tick moving flag alone cannot justify a connector.
