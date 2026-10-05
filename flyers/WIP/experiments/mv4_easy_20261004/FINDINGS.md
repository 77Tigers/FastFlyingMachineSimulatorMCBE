# mv4: easy improvements and difficult handoff

The user asked to finish straightforward work in Astra's saved directions,
improve PL where possible, and leave difficult questions for the user and Astra.
The additional minimum-size pickup-face enumeration was explicitly approved.
All work retains exact half-turn pairs, six driving mv4 bodies, fixed four-piston
positions and observer/power arrangement. No simulator/editor/viewer/format
code was changed. The whole flyer must stay below PL50; PL<36 is preferred.

## Verified best

**[PL43 compact symmetric flyer](../../../bank/pl43/mv4_symmetric_easy_compact.flyer)**:
three glue templates of33/31/33 cells, each repeated opposite (194 glue total,
97 slime and97 honey). There are12 observers and24 normal +X pistons:230
permanent blocks,234 including arms in the initial/final measurement state.
All six persistent bodies use mv4: two each at phases0/1/2rt, moving+1 across2rt
then waiting1rt. Opposite copies rotate180 degrees and exchange slime/honey.

The full10,000-tick checker passes80/80 RNG/chunk-phase cases; every run travels
3333 blocks. Core geometry, moving duration and conservation are checked every
tick. The traced run has20,000 extensions, maximum action43 and zero failures.
At PL42 the traced run stalls after41 blocks with9 failures. **Full piston/owner
state recurrence remains unestablished**; these results do not certify all
possible update orders. This is the same validation scope as the user-approved
original PL49 mechanism.

Direct per-action load accounting (`load_profile.rs/.csv/.txt`) shows that the
43-cell peak consists of33 glue, eight piston passengers and two observers,
occurring84 times in10,000 ticks. There are no movement failures. With that
overhead unchanged, that peak body would need25 glue to reach PL35. This is a
redesign target, not a lower bound for other interfaces. The diagnostic uses
the pre-action world and applies trace changes in order; failed discoveries
are excluded from load profiles.

Evidence: `validation/compact43_reroute_best/summary.json`, `full80.csv`,
`audit10000.txt`, `lower.audit10000.txt`. SHA256:
`bbcdbe089b3f63630af21cb4bd04aa8fb80d6abe7870a5ce40c1bfb4bae41c47`.
Geometry metadata: `compact43/reroute_best.json`. WIP copy:
`../../mv4_symmetric_easy_compact_pl43.flyer`. Bank ledger: `../../../bank/results.csv`.

PL45 and the196-glue PL43 are also verified and retained. Compared with the
previous symmetric PL46/198-glue flyer, this improves the maximum action by3
and removes4 glue cells. The original irregular PL49 used225 glue.

## Completed original easy sweeps

| Sweep | Cases | Outcome |
| --- | ---: | --- |
| Saved symmetric placements, caps35/34/33, two seeds |342|4 short80 passes; best verified PL43 |
| Five soft rail layers on top12 placements |360|11 short80 passes; no better limit |
| Five bend/rail profiles on top12 placements |360|8 short80 passes; no better limit |
| Nine hard one/two-backbone domains |216|No route;142 disconnected domains,74 routing failures |
| Nine previously recorded pickup-face variants |648|9 short80 passes; best194-glue PL43 starting point |
| Smaller caps32/31 on deduplicated best interface |20|No route |

Total:1946 routing cases. The nine recorded port variants include equivalent
physical glue sets. These finite ledgers are bounded search evidence, not a
global optimum or impossibility proof. Each route gets at most3 seconds.

Paired pruning and local shortcuts tested184 patches on PL46,181 on basic PL43,
196 whole-corridor patches on PL46,192 on rerouted PL43, and189 on compact PL43:
942 trials including overlaps/repeats. None reduced the glue count. Fixed-pair
rerouting tested360/540/360 attempts respectively, accepting2/3/2 short-screen
improvements. Distinct-template bends changed37→35,39→36,34→31 respectively.
The final compact result has31 bends and16 branch cells across its three distinct
templates (62/32 over six bodies), with4–5 X-layers per body. Exact symmetry is
established; a simple straight backbone remains unresolved. `layout.svg` is a
phase/template diagram, not a block-by-block construction plan.

## Approved compact pickup-face extension

Completed. Enumerate all4^4 side-face assignments for the unchanged four piston
sites, deduplicate physical glue sets, and retain minimum-size covers. There
are eight distinct two-cell covers. Survey all8×8 pairs on57 saved symmetric
placements:3648 cases, of which82 pass interface checks,2414 violate body contact,
and1152 violate hardware keepouts. Route the valid interfaces in ranked order,
with caps35/33/31, flat/bend preferences and two seeds. The initial chunk uses
64 interfaces; a separate worker covers the remaining18 without changing case
IDs:984 routes total. A cap32 companion checks another328 routes on all82
interfaces, directly targeting PL42. Every process chunk is at most2700 seconds.
See `compact_faces/` and `faces32/` for evidence.

All984 face routes completed: six short80 passes at PL44/45,978 routing failures.
All328 cap32 routes failed to route. No better PL or geometry was found. The
main worker finished in2562 seconds, the18-interface worker in690 seconds, and
the cap32 worker in1035 seconds; each stayed below the45-minute cutoff. The
canonical ledgers are retained; `merge_faces.py` merged the disjoint tail cases
into the canonical ledger and checked that no case was missing. Overall this
session completed3258 finite routing cases, plus3648 mandatory-interface survey
cases,1328 pruning/shortcut trials and1620 fixed-pair reroutes (including repeats).

The known banked interface appears at parent1 in the face plan. Fresh routes
there found PL44/45, while the earlier194-glue PL43 remains valid. This concrete
example shows why a bounded routing failure cannot establish interface
impossibility or an optimum. The best new PL44 route also received193 pruning
trials,360 fixed-pair reroutes, then193 more pruning trials: one bend removed,
no glue or PL saving. `faces_local/`, `faces_local_final/`.

Lower-limit checks use a deduplicated geometry manifest in `limits42/`.
`audit_one.exe` checks RNG5/XZ0 and stops at first failure. A negative suffices
to reject that80-case claim; a positive would still need the full80 cases and
traced audit. The original portable batch deliberately retains14 negative rows
in an interrupted partial CSV; it is not a complete matrix. All45 distinct saved
geometries/start states checked at PL42 were rejected:14 portable negatives and
31 focused single-case negatives. No single-case positive remains awaiting full
validation. This includes the earlier root-level local variants and pruned inputs.

## Reproduction and handoff

`common.py` uses unchanged lifecycle/contact builders and rebuilds moving owner
lists correctly. `prune.py`/`reroute.py` perform paired fixed-interface edits.
`bend_bridge.py` adds a bend cost to bridge routing; it is not a global Steiner
solver. `sweeps.py`/`run_group.py` and `compact_faces.py` have finite resumable
ledgers. `validate.py` performs a traced10,000-tick audit, full80×10,000 core
matrix and one-lower trace before banking. Keep short and full evidence separate.

```powershell
python flyers/WIP/experiments/mv4_easy_20261004/compact_faces.py 2700
python flyers/WIP/experiments/mv4_easy_20261004/faces32.py 2700
python flyers/WIP/experiments/mv4_easy_20261004/progress.py
python flyers/WIP/experiments/mv4_easy_20261004/limit_scan.py 42
python flyers/WIP/experiments/mv4_easy_20261004/prune.py 600 INPUT_META.json OUTPUT_SUBDIR
python flyers/WIP/experiments/mv4_easy_20261004/reroute.py 1200 OUTPUT_SUBDIR
python flyers/WIP/experiments/mv4_easy_20261004/validate.py CANDIDATE.flyer --bank --name UNIQUE_NAME
```

The remaining mechanism/global-layout questions are in
[DIFFICULT_QUESTIONS.md](DIFFICULT_QUESTIONS.md). No new mechanism family was
investigated. Check with the user before exploring a direction outside Astra's
listed work or this explicitly approved face extension.

All planned easy sweeps and the approved extension are complete. No research
worker or validation process from this session remains active. The preferred
PL<36 target and a simple backbone remain open; use the hard questions before
another mechanism search. Re-running the completed sweeps resumes their ledgers
and does no additional routing unless their finite plans are intentionally changed.

## Cleanup and redesign handoff

The user requested cleanup and a minimal Astra plan for Sol. `CLEANUP.json`
records142 deleted disposable files (4,147,395 bytes): debug symbols, Python
caches, duplicate display text, the already-merged tail ledger, and PL42 input
clones/metadata. Original candidates, source, canonical ledgers, negative CSV/text
evidence, all bank validations and useful compiled diagnostics remain. Historical
manifest paths to deleted clones are provenance, not live artifact links; recreate
each clone by loading its retained `source`, setting `push_limit=42`, and saving.

[ASTRA_PLAN.md](ASTRA_PLAN.md) answers the six questions and gives eight small
tasks. Priority: explicit carrier-graph reassignment with unchanged timing,
then shared-hub feasibility and balanced2+2 modules. The three-member capacity
argument is conditional on four unavailable ticks per firing; test the reset/
pickup loophole before treating it as a bound. No new search has been started.
