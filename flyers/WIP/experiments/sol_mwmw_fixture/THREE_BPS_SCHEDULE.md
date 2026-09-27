# Conditional 3 bps schedule analysis

This is a timing derivation, not a tested 3 bps flyer. It does not change the
priority of verifying PL12/2500 before any PL17 experiments.

Three blocks per ten Rust ticks require three forward actions in five
two-tick slots. The local diagonal interface uses a simple recycle rule:
for target action in slot `s`, the source carrier must move in slot `s−1`
to finish an observer pulse immediately before firing, and it must move in
slot `s+2` to pick the retracted piston. Slot indices are modulo five.

If one target A moves in any three of five slots and one source B is also
allowed only three moves, the same B cannot service all A actions. B must
cover `(A−1) ∪ (A+2)`, which has at least four distinct slots for every
three-element `A` subset of a five-slot cycle. For example, A moving in
`{0,2,4}` needs B in `{1,2,3,4}`. A moving in `{0,1,2}` needs B in all
five slots. Thus the two-carrier, one-shared-H/O generalization fails under
this exact pulse and two-slot recycle schedule. A different pulse source,
pickup lag, or sticky pull can escape the condition.

The five-carrier N3 template offers a schedule with separate supports.
Choose A's target actions in `{0,1,2}`. A firing in slot 0 needs a source
that moves in slots 4 and 2; a three-move consecutive carrier with phase 2
can do that. Slot 1 needs source moves in 0 and 3 (phase 3), and slot 2
needs source moves in 1 and 4 (phase 4). These are three different support
carriers, which the five-carrier ring can contain. Each support's own motion
and power still need a full closure ledger.

For fixed P0/P1 diagonal piston coordinates in `diagonal.rs`, the five
slime cells form a minimal connected rail. Rear pickup terminal
`(-1,1,1)` is Manhattan distance 3 from P0 face `(1,0,1)`; P1 face
`(1,1,0)` is off every shortest path between them, so at least four edges
and five cells are required. The current rail realizes that bound. A third
front piston face can share the central junction, but it must have its own
power/source assignment. A candidate transverse face `(1,0,-1)` can be
connected from the existing `(1,1,0)` through `(1,1,-1)`, adding two slime
cells, subject to testing the third piston's pickup route and unwanted
adhesion. Placing a third piston beside the existing H risks firing it with
P0 or P1 at the wrong time.

The existing N3 pure-template geometry and traces should be used as the
starting control when this track becomes active. The diagonal pair may save
pickup/contact routing cells, but by itself does not reduce the number of
source interfaces or solve their power and load timing.
