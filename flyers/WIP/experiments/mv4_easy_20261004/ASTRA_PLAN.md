# mv4 redesign handoff to Sol

Planning only; no new searches started. Read `SIMULATION.md`. Preserve the PL43
bank. Rear mv4 cores must drive the machine; helpers may pull/support them.
Whole-flyer PL<50 is mandatory, PL<36 preferred. Keep simple repeated modules.
User approved relaxing exact opposite-pair symmetry when the replacement has a
simpler repeated structure. Keep repetition/elegance as a design criterion;
arbitrary coordinate jitter is not the objective. Each search <=45 minutes.
Work on one numbered task at a time; save a
small JSON result and first counterexample, then follow its gate. Do not repeat
the finished routing sweeps or pursue the old push-driven helper closure.

**Sol starts here:** task1, then task2, then the finite task3 graph survey.
The listed redesign directions are authorized; do not ask again about symmetry.
No search is running and no user answer is pending. Implement and investigate
these tasks; the remaining coding and experiments are deliberately left to Sol.

## Answers to the six questions

1. **Minimum core size:** unknown. The present peak is33 glue +8 pistons +2
   observers. PL35 needs an eight-cell reduction in that action; geometry and
   passenger savings can combine. The old routing failures prove no lower bound.
2. **One shared hub:** four cardinal piston positions consume every transverse
   neighbor. In the unchanged ribbon contract, the rear axial neighbor of the
   firing-plane hub is required pickup glue; a front axial observer touches the
   driven core's front glue. Thus a direct fourth-spoke replacement has a concrete
   obstruction. Check the finite positions below; sharing power needs a changed
   pickup interface or another hub. Hard power does not propagate through glue.
3. **Three members:** prioritize four-member redesigns. A conditional capacity
   bound explains the difficulty: if each firing costs four unavailable ticks
   and each block of transport costs two, a member matching speed1/3 needs
   T >= 4 + 2T/3, hence T>=12; a bank firing every3 ticks needs >=4 members.
   The unresolved premise is whether reset and pickup can reliably share a tick.
   This is not a universal proof, especially for different actuator mechanisms.
4. **Simple backbone:** change which cores serve each bank before trying more
   path seeds. Long inter-bank connections may be imposed by the current assignment.
5. **Passenger overhead:** eight is measured, not proved necessary. Attribute the
   passengers to their firing banks; optimize peak concentration, not just total
   piston count. Removing a required pickup alone already failed.
6. **Certification:** retain80x10,000 core cases plus traced failures/load for
   bank candidates. Defer full-state proof. An abstract closed reachable-state
   set can screen a mechanism; it does not certify the Rust simulation. A future
   exact state must include owners, cached power/angry behavior and chunk residue;
   repeated sampled states do not cover all update orders.

## Small tasks, in order

**1. Freeze a reusable control.** Copy the builder into a new redesign experiment;
do not edit the old baseline. Parameterize piston sites, hub ribbons, observer
sites/directions, OWN/PREVIOUS faces and carrier assignments. Default values must
reproduce `compact43/reroute_best.json` geometry and the bank's short80 result.
Use `common.py` for saving/owner lists and physical checks. Output: control JSON
and a passing short CSV. Stop and repair any mismatch before further tasks.

**2. Record one peak's passengers.** Extend `tools/src/bin/mv4-load-profile.rs` locally to output
coordinates and piston states for the first43-load action (tick122 in the saved
start). Track piston identity through successful source->destination moves from
the metadata's initial `pistons` list; normalized X is not a persistent identity.
Align metadata coordinates with the loaded flyer's save-origin translation first.
Group the eight passengers by bank and carrier role. Output one small load table.
This supplies a concrete target for tasks3 and7; no long search is needed.

**3. Enumerate carrier graphs (medium redesign, highest priority).** Keep six
cores, phases i%3. Each bank i drives core i; choose its following carrier F(i)
from the two phase(i+1)%3 cores, and previous carrier P(i) from the two phase
(i+2)%3 cores. Existing assignments are F=i+1, P=i+2 modulo6.
Use F(i+3)=F(i)+3 and P(i+3)=P(i)+3 modulo6 for the64-assignment control family.
Symmetry relaxation also permits all4096 assignments; survey/rank them before
routing, retaining a simple repeated layout or module arrangement. Prefer
balanced incoming carrier duties, but do not assume imbalance is impossible.
Keep connected dependency graphs and deduplicate phase-preserving relabelings.
Carry material labels through relabeling; preserve distinct material adjacencies.
In `six.py`, replace every ownership shortcut, including source owners, fixed
passenger keepouts and canonical initial moving owners, with explicit phase->core
mapping. Keep displacement phase-based. Do not change only the terminal positions.
Rank by mandatory cell count and connection span on the saved57 regular placements;
apply actual material/observer/swept-contact checks. Output the best10 valid
graph/layout interfaces, retaining the existing assignment as a control.

**4. Route only task3 survivors.** First try the existing three templates mapped
to the new roles as warm starts where valid. Use the paired router only when
the interface really has its required symmetry; otherwise use the general
six-body routing code in `synthesis/final_router.py`, preserving the chosen
repeated motif. Do not silently mirror away the new carrier assignments.
Two seeds each at glue caps32,29,25, three seconds per attempt. Glue+10 is only a
screening allowance; measure actual passenger loads after simulation. Test short80
before full validation. Stop this batch after the finite list, even if none route.
Output: best candidate or one bounded negative summary. PL<=40 is useful progress;
do not demand PL35 before retaining an improvement.

**5. Test the four-spoke hub obstruction (small interface test).** Use piston
YZ sites (1,0),(-1,0),(0,1),(0,-1), following hub ribbon X=-1,0 at YZ=(0,0).
Enumerate observers facing either hub cell from its six face neighbors, owned by
the following carrier. Reject occupied positions, foreign-core adhesion and
wrong firing-plane power. Reproduce the old three-spoke control first. Output
the rejection table; if all fail, stop this family with the unchanged ribbon.
Do not run global routing for a failed local power interface.

**6. Try balanced2+2 hubs (medium geometric redesign).** Keep two pulse sources,
but replace the3+1 arrangement with a repeated pair. Two concrete YZ seeds:
  - hubs(-1,0),(1,0); pistons(-1,-1),(-1,1),(1,-1),(1,1);
    observers(-2,0)->+Y and(2,0)->-Y;
  - hubs(0,0),(2,0); pistons(-1,0),(0,1),(2,1),(3,0);
    observers(0,-1),(2,-1), both facing+Z.
Hub ribbons stay X=-1,0; observers start on X=0. Enumerate each piston’s four
side faces for own/previous pickup; deduplicate physical sets and retain sets
of at most3 cells per role, rather than insisting on the minimum two. All are
hypotheses requiring local keepout/power checks. Keep only the best3 local
interfaces, test them on the best3 task3 graphs, then use task4's small route
batch. Savings must come from simpler connections; two observers are still used.

**7. Check the four-member capacity premise (large-redesign gate).** From actual
traces, tabulate firing->reset->first pickup->next firing for identified pistons.
Look specifically for same-tick reset/pickup. In a small replay fixture, reverse
their order with the existing abstract competition checker and report whether
the pickup is still guaranteed; confirm promising fixtures with Rust. If four
unavailable ticks are forced in this family, stop ordinary three-member searches.
If an order-robust counterexample exists, save its precise power/contact/state
contract before attempting a three-member bank. Do not remove one member from
the current layout and launch another geometric sweep.

**8. Prepare a front-pulling contract only if tasks3–6 stall (large redesign).**
Use the current peak table to identify one transport duty that can be shifted
to a front carrier with mmwmmw or mmmmww timing. Enumerate only that helper's
phase and axial offset, with one backward-facing sticky pulling a rear core.
Output a12rt table: each core move, initiator, carrier, power-on/off and pickup.
Require all three rear mv4 phases and no core-speed deficit; explain how the
helper itself advances at matching mean speed. A prescribed moving helper is
only a local fixture: stop before geometry until its actuation/closure is specified.
Ask the user to choose the duty if the peak table offers no clear candidate.

Reuse `synthesis/competition_contract_snapshot.py` and
`observer_contract_snapshot.py` for abstract screens; they assume a specific
power/contact contract. Change and recheck that contract when interfaces change.
For completed four-member/all-mv4 geometry, reuse `mv4-audit-cores` (cargo bin,
`tools/src/bin/mv4-audit-cores.rs`) and
`validate.py`. Mixed helper words or changed persistent-body classification need
a checker extension first; do not weaken the mv4 checks to accept a candidate.
