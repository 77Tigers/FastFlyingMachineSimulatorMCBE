# Elegant mv4 feasibility

Follow-up: [compact symmetric PL43](../../../bank/pl43/mv4_symmetric_easy_compact.flyer)
is fully core-verified at80/80×10,000 ticks,194 glue, three repeated templates.
The [easy-sweep findings](../mv4_easy_20261004/FINDINGS.md) retain the improvement
and handoff. The PL46 results below are the original elegance-session evidence.

The user explicitly authorized banking the verified PL49 mv4 flyer and asked for
a roughly 30-minute session, mostly running code, to explore elegant layouts and
identify future research directions. PL<50 remains mandatory; all six cores stay
mv4, with two bodies per 0/1/2rt phase and no other-timing engine pushing them.

## Operational elegance constraint

Use regular rectangular or integer hexagonal six-bank rings. Opposite banks have
the same phase and are exact half-turn copies in the transverse YZ plane, with
slime/honey exchanged. Required ports, observers and routed glue are copied.
This leaves three body templates instead of six unrelated routes. No independent
coordinate jitter is permitted. Optional rail preferences encourage one X-layer
backbone with terminal stubs; this preference is not a hard guarantee of few bends.

`paired_router.py` retains the existing reachable-state hardware/pickup keepouts,
routes three representatives, checks both copies, and rejects asymmetric geometry.
The symmetry concerns geometry, not equality of random passenger trajectories.
Only cap39 assemblies, encoded at PL49, can reach real simulation.

## Result: PL46, with three repeated templates

The original PL49 artifact was banked on explicit user authorization at
[`../../../bank/pl49/mv4.flyer`](../../../bank/pl49/mv4.flyer). The stronger result
from this session is [`../../../bank/pl46/mv4_symmetric.flyer`](../../../bank/pl46/mv4_symmetric.flyer),
also exported to `../../mv4_symmetric_pl46.flyer`.

- All six persistent bodies remain mv4, with two per phase; no other-timing helper
  pushes a passive mv4 attachment. Opposite templates have glue counts
  **36/30/33 repeated twice**, with zero cell differences under the half-turn.
- 198 glue cells (99 slime,99 honey),12 observers and24 normal +X pistons:
  234 permanent blocks,238 including sampled arms. The previous PL49 had225 glue
  cells; this removes27 cells (12%). See `geometry_comparison.json` and `layout.svg`.
- **80/80 cases pass10,000 ticks at PL46**, every case traveling3333 blocks.
  Exact core geometry, direction, moving duration, conservation and absence of
  extension failures are checked every tick. `symmetric_pl46.full80.csv` / `.txt`.
- A separate traced10,000-tick run measures maximum successful action46 with zero
  movement/extension/conservation failures: `symmetric_pl46.audit10000.txt`.
- PL45 passes the300-tick trace but fails the10,000-tick trace, stalling at184
  blocks with8 movement/extension failures. This is an actual long-run requirement
  of this saved layout, not a short-screen minimum guess. `symmetric_pl45.audit*.txt`.
- Full piston passenger/owner-state recurrence remains **unestablished**, as with
  the user-authorized PL49 bank entry. The traced complete state has no repeat at
  sampled12-tick boundaries. Exact core timing is not exact whole-state recurrence.
- SHA256 `e82b00ec0024fcbd59ecc2ba1be5a915227f0df00b19b4572f0acd0cb182a8cc`.
  `verification_summary.json` records the checked bank export.

Repetition is a substantial improvement in learnability, but not a claim that
every route is simple: the three templates still use4–5 X layers, have37 glue
elbows and13 branch cells between them (each template appears twice). The older
layout had90 elbows and24 branch cells overall; this has74 elbows and26 branches.
The copied modules are simpler to describe, while reducing branches remains open.

## Experiments and bounds

`python flyers/WIP/experiments/mv4_elegant_20261004/search.py 1380`

The primary search and its validation share a1,380-second deadline, with210 seconds
reserved for validation and12 seconds per route. `search.py` uses the frozen
`paired_router_initial.py`, preserving the actual router used by that process.
It screens candidates with80 cases of300 ticks at encoded PL49. The initial search
finished at1,170 seconds:217 placements,71 hardware rejects,48 body-contact rejects,
98 routing attempts,96 route failures and2 assemblies. One was accepted by the old
checker; the other exposed the observer classification issue below and became the
fully verified PL48 intermediate. The primary process reached its1,380-second
deadline during seed67's full matrix, after67/80 successful cases; that partial
CSV is **not** a full validation claim. The separate PL48 and PL46 matrices both
completed80/80. `status.json`, `winner.full80.csv`, `symmetric_pl48.full80.csv` and
`symmetric_pl46.full80.csv` distinguish these outcomes.

`survey.py 12000` is bounded at120 seconds; it completed6,756 placements, with2,757
passing mandatory interface checks,2,782 hardware rejects and1,217 body-contact
rejects. An axis-span lower bound excludes1,016 of the interface-valid placements
from a25-glue-cell budget. It excludes none from39 cells, so this cheap bound alone
does not resolve PL49 routing. A component Manhattan MST ranks the remaining
layouts; this is a heuristic, not a Steiner lower-bound proof. `survey.json`.

`ranked_search.py 420` deduplicated the best survey records into57 placements and
tried53 in420.2 seconds. At cap36, four routed and all four passed80 short cases;
49 did not route. Attempt1 supplies the verified PL46 geometry. This router also
negotiates optional conflicts between a template and its own opposite copy;
the initial router rejected those intermediate solutions. Both ranking and this
router change contributed, so the measured improvement cannot be attributed to
either in isolation. `ranked_status.json`, `ranked_a1.json`, `paired_router.py`.

`lower_cap_search.py 180` completed22 attempts at cap33 in180 seconds, all routing
failures. `lower_status.json` records the sample. This does not show that PL43,
PL35, or other elegant architectures are impossible.

A direct observer-to-rod substitution in the PL46 layout stalled after2 blocks
over300 ticks with1,750 extension/movement failures, while conserving permanent
blocks. `rod_substitution.audit300.txt`. Continuous power cannot simply replace
these settlement pulses in this geometry/start state. This is one bounded test,
not a general rejection of rod-based power mechanisms.

All searches overlapped within the requested approximately30-minute session;
all search/audit processes have finished and all generated evidence is retained.
Candidates were encoded at49 or lower; the simulator/editor/viewer/format were
unchanged. This is a restricted-family feasibility study, not an exhaustive
impossibility proof.

## Checker correction and reproduction

The old fast checker traversed adjacent observers as if they joined sticky bodies,
which reported "Missing initial core phase" for seed56 before simulation. The
local `audit_cores.rs` traverses same-kind glue and attaches adjacent observers as
leaves; it rejects an observer touching multiple cores. The moving-duration,
geometry, conservation and extension tests are unchanged. The existing banked
PL49 also passes80 short cases with this checker (`checker_bank120.csv`).

```powershell
rustc --edition 2021 -O flyers/WIP/experiments/mv4_elegant_20261004/audit_cores.rs --extern fastflyer=target/release/libfastflyer.rlib -L dependency=target/release/deps -o flyers/WIP/experiments/mv4_elegant_20261004/audit_cores.exe
& flyers/WIP/experiments/mv4_elegant_20261004/audit_cores.exe flyers/bank/pl46/mv4_symmetric.flyer 10000 flyers/WIP/experiments/mv4_elegant_20261004/recheck.csv
& flyers/WIP/experiments/bin/research_runner.exe audit flyers/bank/pl46/mv4_symmetric.flyer 10000 12
```

Use the current release library when rebuilding; the compile command modifies
only the local diagnostic. `bank_result.py` gates exports on the complete80-case
CSV and traced results. `analyze.py` generates the geometry comparison and bank
structure diagram. These do not claim full passenger recurrence.

## Research directions supported by this session

1. **Keep template symmetry as a hard constraint.** It is compatible with working
   mv4 and reduced the result from PL49 to46. Rank mandatory interfaces before
   negotiated routing; the ranked sample produced four usable routes quickly.
2. **Route a small number of straight backbones with terminal stubs.** Add a bend
   cost or a comb-template restriction; current optional routing still sprawls
   across several X layers. Paired pruning or connectivity optimization can keep
   required timing/power ports while reducing template complexity and load.
3. **Redesign shared pickup/power interfaces for the next large reduction.** The
   present mechanism still uses four piston members and two observer sources per
   bank. Co-locating terminal clusters or sharing the fourth member's power may
   reduce both cells and explanatory complexity. Preserve the pulse timing and
   enumerate reachable passenger states before geometric search. A casual rod
   replacement fails, and simply deleting required rear pickups failed in earlier
   work. PL<36 remains open; do not mistake more routing time for proof that this
   interface family can reach it.
