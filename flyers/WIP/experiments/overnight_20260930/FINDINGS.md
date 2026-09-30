# Overnight research, 2026-09-30

## Current authoritative checkpoint

- Banked mmwmmw3.333bps: **PL36**,105 boundary blocks, all80 full exact
  10000-tick cases with833 nominal +4/12 recurrences, zero failures and
  conservation mismatches. Bank `flyers/bank/pl36/planar_mmwmmw.flyer`, SHA
  `30793bbea94549f6347680bfbef707cda5de8524bbabe7587c93c3ccb7d38470`.
  Preserved stepsPL37 (109 blocks) andPL57 (161), also all80 exact.
- Banked pulling-only3bps: **PL102**, all80 full exact10000-tick cases.
  Bank `flyers/bank/pl102/pulling3_tenbody.flyer`. Earlier106/126/127
  steps preserved. Further trimming/rerouting lowers cell counts but not102.
- Mixed local11 and local8: literal1/2/4/8 copies pass full encoded10000
  ticks and tagged ledgers; both1-copy and8-copy assemblies pass all80 full
  cases. Local8 targets have five sticky cells; driver limits66/83/119/195
  remain separate from local action loads. No globalPL8 flyer claim.
- Pull-first front interface: full exact10000 ticks and all80 cases pass at
  wholePL59; five-cell target's tagged actions range6–8,3000 actions.
  Glazed power separation allows pull/push/push with real helper transport.
  Hybrid separate-back/front closure16 attempts all fail routing at cap40;
  gauges80 attempts also fail routing at cap38. Neither improves3bpsPL19.
- Glazed mmmmww interface: short attachment reduces47 to40; full encoded
 10000-tick recurrence/conservation audit passes. No globalPL22 improvement.
- Circular pure-pull placement16 attempts all fail routing at cap110.

- N4 compact48 attempts:48 clean240 cases, best21; selected full cases
  sustain3333 but fail nominal exact recurrence. No mmmmww record change.
- mmwmmw single-output extensions:24/24 clean240; target counts23–27,
  need full12/+4 checks, tagged loads and copying.
- Distributed mixed8-cell role ring v2:32 attempts,5 routed/clean240,
  loads54–56. Compact5-cell closure48 attempts at cap32/body yields no
  candidate. Gauged closure61702 tests shorter phase-group X spans at
  radii6/7, cap38/body,80 attempts; outputs `mixed_role_gauged_*`.
- Extra planar placement batch43778 completed72 attempts, best38, no
  improvement over36. Rerouting68474 completed full exact10k at36 with
  no lower-load improvement; don't repeat80 audits for that equivalent lead.

Later sections retain chronological bounds; this checkpoint supersedes old
pending/bank status statements. Inspect live handles before restarting jobs.

User authorized continued work until the account usage limit, prioritizing
lower limits for3bps, for3.333bps in both `mmmmww` and `mmwmmw`, and a
pulling-only3bps flyer. Main-chain and front-helper bodies remain distinct.
Use chainable interfaces and the two-push/one-pull trick, and improve the
abstraction against concrete failures. No simulator/editor/format changes.

An active research goal and an idle-chat follow-up are configured. The latter
checks every30 minutes for at most24 scheduled occurrences; it must not
interrupt or duplicate running experiments. Pause the follow-up after an
account usage-limit stop; do not purchase credits or apply the available
account usage reset. Automation id: `overnight-flyer-research`.

## mmwmmw transverse placement

`mmw_layout_search.py` retains the proven three-body/six-slot lifecycle and
changes only six transverse module centres. Five layouts ×32 seeds =160
attempts at adhesive cap65/body. Checkpointed source hash, parameters and
rejections are in `mmw_layout_manifest.json`; derived source is retained.
Original fixed geometry/evidence is untouched. One OneDrive checkpoint write
failed; atomic pending-file replacement was added and the search completed.

Grid4 routed4; hex4 routed5; the other layouts routed0. All9 candidates
ran80/240 cleanly at diagnosticPL512. Best: **hex4 seed14, maximum62**, centre
list `[(0,0),(4,0),(6,3),(4,6),(0,6),(-2,3)]`. Encoded
`mmw_hex4_s014_pl62.flyer` passed10000 ticks:3333 displacement, zero failures
and conservation errors, all833 exact +4/twelve-tick cell/owner boundaries.
This supplied the untrimmed lead for the banked result below. Other
selected full candidates passed at65 and67. Raw screen and verify files kept.

`trim_mmw.py` finished: connected-cell deletions removed6 then2 then0 cells,
leaving135 sticky cells and161 boundary blocks. **PL57 is fully banked** at
`flyers/bank/pl57/three_segment_mmwmmw.flyer`, SHA256
`f8e949eaf914de75a2e1564737b41756deb5f2b5ad21514aa8785b910f7c6496`.
All80 full10000-tick RNG/phase samples pass all833 exact block/owner recurrences,
3333 displacement and zero failures or conservation errors. Maximum action57.
Evidence: `mmw_hex_trim_pl57.{verify.txt,samples.csv,audit.txt,certificate.json}`,
`trim_mmw/results.json` and `trim_mmw/geometry.json`. Native session1012 finished.
This improves mmwmmwPL65; the separate mmmmwwPL22 threshold remains unchanged.

## Pulling-only3bps: explicit saturated member transport

`pull3_v3_5body.py` preserves the five-body prototype. Each body has three
movement slots out of five; each of15 pistons extends in f-1, pulls in f,
and must be transported in the other three slots. Every member therefore
has +3 displacement and a declared five-slot recurring hardware lifecycle.
Power sources have independently named owners and phase-labelled positions.
This is a proposed contract, not yet a realized mechanism.

Initial random power choices rejected64/64 mandatory contacts (spacings3/4,
seeds0–31). Restricting source choices to avoid unintended power windows and
foreign source/target adhesion moved the first failure to pickup realization:
64/64 rejected before routing. Evidence: `pull3_v2_manifest.json`,
`pull3_v3_manifest.json`, `pull3_run_v2.txt`, `pull3_run_v3.txt`.

`last_pull3_pickup_failure.json` and `pull3_rejection_sites.json` give seed0
spacing4 witness: piston `(0,12,4)`, action slot3, remaining recovery slot1.
Its ideal carrier moves slots0/1/4, but local contacts and same-material
intermediate adhesion prevent the chosen assignment. A source is not valid
merely because it aligns at the intended extension: forbid powering at all
other ready/retract boundaries before routing. This check was added and tested.

A conservative ban on two moving bodies sharing a ready piston was removed:
either +X body may carry it once if the other loses contact afterward and
the destination is clear. Full Rust validation remains mandatory; removing
that ban alone yielded no candidate. This is an explicit hypothesis about
interchangeable transport, not a universal order proof.

`pull3_synthesis.py` now tests10 separately represented bodies: each of the
five schedules has an independent slime and honey carrier, allowing an
opposite-material helper to service a piston without collapsing equal-motion
bodies. Thirty -X sticky members provide all30 required moves. This widens
the helper architecture; it is **not** a verified3bps flyer or lower bound.
The bounded run is spacing3/4 ×16 seeds, native session14145; inspect
`pull3_run_v4_10body.txt`, `pull3_10body_manifest.json` and candidate/screens.

That search finished:31 routing rejections and1 routed candidate out of32.
Native session14145 exited0. Do not rerun the same family unchanged.

Spacing4 seed3 routes successfully (sticky counts59/74/88/84/72/117/60/114/77/79).
The actual encoded `pull3_10body_candidates/g4_s003.flyer` passes200 ticks with
60 displacement, all20 exact ten-tick/+3 block/owner boundaries, no failures
or conservation errors, maximum action127. This is a concrete pure-pulling
3bps lead, **not banked yet**. `validate_pull3_lead.py` encodesPL127 and runs
10000-tick verify/audit plus all80 full samples (native session32585).

Full verify and traced audit both pass:3000 displacement,890 boundary blocks,
30000 empty extensions, zero failures/conservation mismatches and all1000
exact ten-tick/+3 block/owner boundaries. Encoded inspection confirms30 -X
sticky pistons; first-cycle trace/summary confirms30 empty extensions and30
nonempty retractions. All80 samples are still running; do not bank prematurely.
`PULL3_MEMBER_CONTRACT.md` describes the now-realized member obligations and
distinguishes this closed geometry from an unproved chainable extension.

`trim_pull3.py` finished deletion probing (182 probes,8 accepted across rounds)
and full diagnostic verify: maximum126,3000 displacement and all1000 exact
boundaries. Encoded `pull3_trim_pl126.flyer` is undergoing verify/audit/80 full
samples in native session18049. Check its evidence files and live session.
`pull3_compact_layouts.py` rearranges the ten distinct bodies into three
layouts, chooses among three nearer source owners, and tests8 seeds/layout.
Native session36734 is running. This is changed geometry, not a repeat of the
exhausted original32 seeds. Save its screens before deciding the next layout.

`mixed3_synthesis.py` preserves a derived five-body two-normal-push/one-sticky-
pull lifecycle. Spacings3/4 ×32 seeds all64 reject mandatory contacts before
routing. No simulated candidate or impossibility claim. This embedding still
lacks distinct opposite-material duplicate helpers; inspect a specific failed
contact before widening it. Source and `mixed3_manifest.json` are retained.

`diagnose_mixed3.py` retained `mixed3_mandatory_witness.json`: seed0/spacing4,
target1 contact `(3,4,8)`, observer owned by body2 at `(2,4,9)`, slot0. Endpoint
positions alone were insufficient: source-first movement made a side contact
and allowed the target push to recruit the observer. Filtering intermediate
source/target contact at source selection moves the mixed search past that
rejection. `mixed3_synthesis.py` v2 now routes candidates; seed3/spacing3 passes
240 ticks with72 displacement, all24 exact ten-tick/+3 recurrences, zero
failures/conservation errors, max61. This is worse than the existing3bpsPL19
record; it is a working realization of the changed lifecycle, not a new record.
The full64-attempt v2 search runs in native session31099. A partial240-tick
screen runs in96336; inspect `mixed3_v2_partial_screen.csv` for the best lead.

Both sessions finished. Full64-attempt result:21 route failures,4 no-pickup,
39 routed; all39 clean at200 ticks with60 displacement. Best load52 is
spacing3 seed14; no3bps record change. Full screen and manifest retained.
The intermediate-source-contact correction is now documented in stage4 of
`flyers/ABSTRACTION_PIPELINE.md`, with the bounded tested result.

## Current additional bounded experiments

`mmmmww_pl21_samples.csv` fills the older twelve-body lead's missing80 full
RNG/phase audit (native session76258). Early cases all sustain3333/10000 at21
without failures/conservation errors, but exact nominal recurrence remains0.
Do not bank based on speed alone. The full scope remains80 cases.

`reroute_mmw.py` first preserved every cell adjacent to any hardware in any
phase:16 seeds/body, no smaller rails, full run stays57. Evidence directory
`reroute_mmw`. A refined terminal set captures the original selected contact
cover before connection routing and intersects it with the trimmed winner.
Two rounds ×16 seeds/body reduce honey41→38; both slime bodies remain47.
Full10000 ticks still pass all833 exact boundaries at max57, so this reduces
body size without improving the load record. Evidence `reroute_mmw_ports`,
`mmw_reroute_ports_pl57.flyer`; session43037 finished. No new80-case bank.

The compact pure-pull placement search is still running in36734. Paired-line
8/8 route failures; paired-grid seeds2/3 route and pass240 ticks with72 travel,
zero failures/conservation errors, maximum106/109. These improve the short
load lead but need full evidence. `certify_candidate.py` is running seed2's
full10000-tick diagnostic/encoded verify/audit and80 samples in20925; inspect
`pull3_paired_grid_s002*` and `certify_pull3_compact_run.txt`. Original127 and
trimmed126 audits are still live in32585/18049; do not duplicate those jobs.

Seed2's full10000-tick diagnostic now passes:3000 displacement, all1000 exact
boundaries and no failures/conservation errors, maximum106. Encoded106
verification/audit and all80 cases continue in20925. No bank claim yet.

`mixed3_compact.py` places the three target action ports in one initial X
plane and uses two pentagonal layouts, two transverse power orientations,
16 seeds each (64 attempts, cap70/body). This changes the previous dispersed
row geometry; it is not a rerun of that family. Session19702 is live.
First two routed candidates fail sustained motion: seed7 stalls after29,
first failure tick80; seed10 stalls after23, first failure tick70 (immovable
obstruction at serialized `(38,7,21)`). The partial240-tick screen is retained.
Diagnose the first changed contact before expanding this family further.

The original compact session19702 finished. `phase_snapshots.rs` exports even
tick worlds using public Rust APIs; `compare_mixed_phases.py` compares them
with declared body/member trajectories. For pentagon_v0 seed10 the first
settled discrepancy is tick8 (pistons7/8 positions and states), well before
tick70's obstruction. Tick6's focused trace shows redstone at `(16,5,22)`
soft-powering both `(16,5,21)` and `(16,6,22)`; the wrong normal member fires
and carries away the intended one. This is cross-power, not an unexplained
routing failure. Snapshot CSV, phase-diff JSON and first trace retained.
Diagnostic comparison masks angry bits only to locate the first geometric
discrepancy; bank verification still checks complete encoded cells/owners.

Compact v1 source/wrapper are retained with `_v1` suffixes. V2 adds every-source
direct power checks against every member, plus observer-to-solid mediated
power keepouts during routing. Both original32-attempt layouts reject all64
before routing with `cross_power`; v2 source/results retained. V3 doubles
the three cardinal port offsets and tests wider pentagons (two layouts ×two
orientations ×16 seeds=64). Session98439 is live. First partial screen25/25
clean240 ticks with72 displacement; best maximum49, files
`pentagon_wide_v1_s012.flyer` (215 blocks) and `pentagon7_v1_s000.flyer` (232).
Still worse than the3bpsPL19 reference; no record/bank claim. All-source power
checking and this tested witness are added to abstraction stage4.

V3 completed64 attempts: pentagon-wide9 routed/5 route/7 mandatory/4 arm
overlap/7 fixed overlap; pentagon7 routed28/4 route. **37/37** routed candidates
ran240 ticks cleanly with72 displacement. Session98439 finished. The49-load,
215-block pentagon-wide seed12 lead is undergoing full diagnostic/encoded
verify/audit in94237 (`certify_mixed3_compact_run.txt`);80-case sampling is
deliberately not requested for this nonrecord candidate. Exact full evidence
can make it a driver for subsequent interfaces.

That lead completed encodedPL49 verify and traced audit:3000/10000,215
boundary blocks,15000 extensions, all1000 exact ten-tick/+3 block/owner
recurrences, zero failures and conservation errors. Session94237 finished.
`mixed3_compact_v3_s012_pl49.flyer` is a working fixed-member two-push/one-pull
driver candidate. It still exceedsPL19, has no80-case audit and is not banked.

The original24-attempt compact pure-pull search finished: paired-line8 route
failures; paired-grid6 route failures and2 routed; split-grid8 route failures.
Both routed candidates clean240 ticks, max106/109. Session36734 finished.
The106 candidate has now passed encoded10000-tick verify and traced audit,
852 boundary blocks,3000 displacement and all1000 exact boundaries; no
failures/conservation mismatches. All80 samples still run in20925.

Next pure-pull bounded variants: `pull3_planar_ports.py` aligns each target's
three ports into one initial X plane, tests paired-grid/cyclic-line/paired-line,
12 seeds each, cap110/body and all-source power checks. Session14912 is live.
`reroute_pull3.py` preserves the selected pre-routing contacts and tries8
route seeds for each of the four largest bodies in the106 lead; current
session7032 is live. It exports the final full diagnostic result and encoded
load;80-case certification remains a separate gate.

First planar-port partial screen: paired-grid seed3/4 both pass240 ticks,
72 displacement, zero failures/conservation errors, maxima105/104. These are
short leads only; the36-attempt search is still live. No new full-load claim.

For mmmmww, `n4_compact_ring.py` tests twelve-body rings at transverse spacings
3.2/3.5/4.0, two rotations and8 seeds each (48 attempts), keeping all48 normal
pistons. It rejects lost initial members rather than silently accepting a
different architecture. Session52003 is live; it will screen240 ticks and
verify the three smallest-load clean candidates for10000 ticks. This changes
the placement family and covers twelve bodies not in the earlier96-seed
three-/six-body screens. Actual identical-chain proof remains unattempted.

First N4 partial screen (spacing3.2, rotation0,8 seeds) is8/8 clean240 ticks
with80 displacement, all max23. It does not improve21; retain the remaining
changed layouts' bounded outcomes before interpreting compact placement.

## Latest completed audits and the small mixed interface

The old N4 twelve-body PL21 audit completed all80 full10000-tick samples.
Every case advances3333 with zero extension/movement/conservation/displacement
errors. Every case has0 exact initial/consecutive nominal-cycle matches;
strict passes0/80. Session76258 exited1 for that expected gate failure. This
strengthens sustained-speed evidence, but does not bank21 or solve identical
extensions. CSV/text evidence retained; do not rerun this missing audit.

`reroute_pull3.py` completed: selected contact-cover routing reduces the106
lead's measured maximum to **102**, full10000 ticks with3000 displacement,
all1000 exact boundaries, zero failures/conservation errors. Session7032
finished. `pull3_reroute_pl102.flyer` is encoded102 but has no encoded full
verify/80-case audit yet; current authoritative full test is diagnostic1000
on the same geometry. Keep the106 full80 audit running in20925.

`mixed_extension.py` appends a new phase0 target to the verifiedPL49 driver,
using separate driver bodies2/3/4 for helper transport/power.24 attempts:
three placements ×8 contact/routing seeds, native39214. First partial9/9
clean240 ticks. The dy12/seed1 target has **eight adhesive cells**. Its1000-
tick tagged ledger gives300 successful target actions, min10/max11; core
helper maxima52/56. Full encodedPL56 verify/audit pass10000 ticks,3000 travel,
all1000 exact boundaries, no failures/conservation errors;258 boundary blocks.
Session71067 finished. This is a low-load local output with a larger driver,
not a globalPL11 flyer. `MIXED_TILE_CONTRACT.md` records realized roles and ports.

`duplicate_mixed_tile.py` froze that exact target/helper patch and tested
1/2/4/8 copies, translated `(0,12,0)` per copy, without fresh routing. One
copy passes; larger copies stall after2 cells with no movement failure, because
helper bodies2/3/4 are disconnected. Connectivity checks retained that cause.
`bridge_mixed_tile.py` adds fixed14/10/4-cell connectors for those helpers;
the same connector cells are copied in every tile. All1/2/4/8 bridged copies
then pass240 ticks with72 travel, all24 exact boundaries and no failures or
conservation errors. Whole assembly loads70/91/133/217 are driver growth;
all new target bodies remain eight-cell literal copies.

`validate_mixed_tiles.py` runs full10000-tick diagnostic/encoded verify and
tagged body ledgers for all four chains, then all80 full samples for1 and8.
Native16380 is live. At this checkpoint1/2/4 copies have passed full checks
and10000-tick ledgers, each added body3000 actions and max11. Eight-copy full
verification and both80-case audits remain pending; inspect
`mixed_chain_validation.json`, `mixed_chain_*` and live session before claiming
completion. Public-API `three_bps_loads.rs`/compiled runner maps every nonempty
action to an exact tagged sticky set and rejects unmatched/mixed body actions.

`extract_mixed_contact_cover.py` preserves the seed1 pre-routing cover:
T has5 mandatory cells, H2 one, H3 two, F4 one. Target-only routing adds3
cells to make8. See `mixed_tile_contact_cover.json` and the tile contract.
This exposes a four-cell helper obligation hidden by the existing driver's
long rails, and is a concrete input to the next lower-load architecture.
The front helpers remain separate from the added target chain. Next distribute
helper drive/transport across separately driven bodies to prevent linear
helper-load growth, keep literal-copy proof, then attempt closure.

## Further completed bounds and current design implications

N4 compact search52003 finished: all48 layouts clean240 ticks, smallest21.
Three selected encoded21 full10000-tick runs sustain3333 without failures or
conservation errors, but exact nominal boundaries all fail. No bank change.
Pure planar search14912 finished36 cases: paired-grid4 routed/8 route failures;
cyclic-line12 route failures; paired-line12 route failures. All4 short candidates
clean3bps, maxima105/104/106/103. Rerouted102 remains the better full lead.

First pure bank: `bank/pl127/pulling3_tenbody.flyer`, SHA256
`4a3f77459d670a75f06a1ce7f38d7f7164b8ec06325ef7be8d5846e2959c8223`.
Then `bank/pl126/pulling3_tenbody.flyer`, SHA256
`0a7e35438d343494fa4fbece5a611565626451f1a8e85da10f490f8b7681dde7`.
Both all80 full samples pass every1000 exact block/owner boundary,3000 travel,
zero failures/conservation mismatches. Sessions32585/18049/20925 finished;
banked106 evidence uses `pull3_paired_grid_s002_pl106.*`. Catalogue/results
append preserves old evidence. `validate_encoded.py` now certifies102 without
repeating the completed diagnostic run; native15441 is live.

`compact_mixed_extension.py` uses target5 connected cells, one H2 support for
the puller, one H3 support shared between both normal recoveries and one F4
source attachment. All24 single-extension attempts clean240 ticks. Dy12 seed0
at wholePL53 passes full10000-tick verify/audit,247 boundary blocks,18000
extensions, all1000 exact boundaries. Its target ledger is7–8 versus helper
53. Source/body tags retained. Session91802 needs a final completion poll.
The smaller template changes contacts rather than deleting disconnected rails.

`mixed_role_ring.py` composes ten phase-labelled bodies, phase3n mod5, even
nodes back/slime and odd front/honey. Every body receives its own two normal
pushes and pull; normal recovery comes from n+1, pull recovery n-1 and front
power n+3. Thus front/helper and back/main body sets stay separate. V1 radii
5/6/7 ×two schemes ×four seeds=24:22 noncallable fixed/power gates (initial
counter called them cross_power),2 mandatory rejects. V2 records the exact
gate reason, radii8/10 ×two schemes ×eight seeds=32, cap50; native50516 live.
First4 routed cases all short3bps/max54–56. Preserve its final bounds before
making a geometry claim. Helper material changes are checked, not assumed.

`mixed_role_ring_compact.py` substitutes the new target5/three-helper-cell
cover; radii4/5/6 ×two schemes ×eight seeds=48, cap32. Completed:7 fixed overlap,
4 arm overlap,5 source overlap,14 cross_power,2 mandatory,16 route failures.
No candidate. Source/runtime checkpoint retry preserves completed cases after
a transient OneDrive denial. `mixed_role_axial_bounds.json` evaluates2401
phase gauges in[-3,3], F0=0; smallest maximum mandatory X span5, total span23.
For this symmetric template, summing pull-support minus normal-support X
positions cancels the ten body gauges and gives44, so some body spans≥5 in X.
This is a port-span constraint, not a proof of a minimum load or general
impossibility. A different front-body actuation order may reduce that span.

`mmw_extension.py` adapts the realized contact-cover/driver workflow to six
slots, +4/twelve ticks, from the trimmedPL57 core. Startup adaptations fixed
tuple concatenation and a textual modulo replacement that had retained5 in
the generated checker; failed startup logs retained. The corrected run66310
finished24/24 routed and short-clean240 ticks with80 travel. Added target
counts23–27 in the dy12 layout, whole diagnostic loads typically72–77. No full
or tagged-load claim yet. The six-slot generated source/geometry are retained.
Next promising mmw compaction: put all four target ports into one front plane,
using first-pair bases F-1, second-pair F-2, and four radial own-source sites.
The own-source offset prevents the second pair firing during the first burst.
This explicit identity-preserving proposal has not yet been geometry-tested.

## Abstraction assessment

Helpful: member displacement/recovery contracts, source ownership and
forbidden power windows expose failures before routing; the previous
chain-first pulling work led to the fully bankedPL9 result. Not yet a solved
fast-interface synthesis abstraction. Equal schedules cannot identify bodies;
phase transition contacts and destination-mediated recruitment are essential.
Record improvements with an executable witness, and keep unsuccessful bounded
geometry separate from an impossibility claim.

Next independent tracks: mixed3bps front helpers with only two push members
per driven front segment; actual open N3/N4 modules and separate driver loads;
diagnose the PL21 mmmmww lead's hardware permutations and seek smaller loads
without weakening bank recurrence standards. Existing exhausted seed-only
N3/N4 families in `continuation_20260930` should not be rerun unchanged.

## Coplanar mmwmmw ports and smaller literal mixed chains

`mmw_planar.py` keeps the three different movement words and twelve normal
piston lifecycles, places each body's four target contacts on one initial
X plane, and uses nine mandatory sticky cells in a transverse cross. The
two late-burst pistons start one cell farther back, keeping their owned
sources unaligned during the first burst. Per-source observer directions
and intermediate contact/cross-power gates are enforced before routing.
Recovery is covered with physical contacts, then connected rails are routed;
no helper movement is assumed externally.

48 bounded attempts (three triangle layouts,16 seeds) gave11 routed/clean
240-tick cases. The safe triangle seed1 needs onlyPL37 and109 boundary
blocks:55 slime,28 honey,6 redstone,6 observers,12 pistons and2 arms.
`mmw_planar_safe_s001_pl37.flyer` passes full encoded10k verification at
+4/12 and all833 exact cell/owner boundaries, conservation and zero failures.
The independent80-case sweep is pending. This is a strong pattern-specific
lead, not a banked record yet and not an improvement on mmmmwwPL22.
`trim_planar_mmw.py` reuses the existing connected deletion/exact-cycle gate;
its diagnostics and geometry go to `trim_planar_mmw`, not prior evidence.

The smaller five-cell mixed target now has literal translated1/2/4/8 copies.
`duplicate_compact_mixed_tile.py` freezes one interface, and
`bridge_compact_mixed_tile.py` creates fixed helper connectors from two
copies which are then repeated unchanged. All assemblies remain connected
and match complete +3/10 boundaries in240-tick checks, with whole loads
66/83/119/195. `validate_compact_mixed_tiles.py` checks every copy for3000
actions/10000 ticks and max local load8, then runs1/8-copy80-case sweeps.
Driver overhead remains separate; this is not a wholePL8 flyer.

Live native sessions at this checkpoint:15441 purePL102 encoded80;
16380 old eight-tilePL21780;67993 planarPL37 encoded80;35226 compact tile
full validation;26367 trimmedPL36 encoded80;43778 extra planar layouts. Resume confirmed live
sessions rather than restarting observation timeouts. Native32070 bridge
finished all four short checks;30646 planar synthesis finished.

## Fully banked planar result and continuation

`bank_planar_mmw.py` reuses the strict pure-pull bank gate with12 normal/+X
pistons,3333 distance and833 exact twelve-tick boundaries substituted. It
refuses incomplete case grids and requires full encoded verify plus audit.
BothPL37 andPL36 banked successfully. The36 pruning removes four cells;
final adhesive counts26/27/26. No simulator/editor/format changes.

The additional72-case coplanar placement batch completes with best38. The
fixed-port rerouting trial preserves surviving ports after prior deletions
(some old selected contacts were redundant), checks every rebuilt body with
the exact simulator, and yields no accepted lower-load lead. Full diagnostic
still passes36. Its first assertion failure is preserved in the first run;
corrected run uses the intersection with surviving, already validated ports.

Compact mixed chains now pass full10000-tick exact recurrence and tagged
load accounting for **all four copy counts**. Their max local8 claim is a
measured per-body movement load, with separate driver overhead. The1/8-copy
80-case sweeps are pending; inspect native35226 before restarting.

Live sessions:15441 pure10280;16380 old local11 eight-copy80;35226 compact
local8 endpoint80;44497 pure102 connected pruning;61702 gauged mixed closure.
The37/36 sweeps completed and banked. The planar synthesis/extra placement/
rerouting jobs are terminal. Active goal remains until account usage limit;
no reset or purchase authorized. Latest usage ordinaryAllowed,75% five-hour,
97% weekly. Keep the fallback quiet and pause it only at actual limit stop.

## mmmmww late-burst source separation

`mmmm_planar.py` derives a planar four-port interface for mmmmww. The first
two sources belong to the target (redstone then observer); the next two
belong to the separate body with phase4 (redstone then observer). The
one-dimensional source alignment enumeration admits exactly these four
choices: target supplies0/1, phase4 helper supplies2/3. This is a timing
result only.32 physical layouts all reject:29 mandatory contact conflicts,
3 source attachment failures. `mmmm_planar_mandatory_witness.json` shows
the target's port temporarily becomes adjacent to the foreign source after
its first move. Direct side power does not preserve that source owner.

`mmmm_glazed_ports.py` then separates the late-burst source by a glazed
solid terminal: a rod powers the first late member through the terminal,
and a helper observer powers the second. The helper pushes its glazed
terminal by a sticky cell immediately behind; glazed does not adhere to
the target. Six separate bodies permit every target/helper pair to have
opposite materials. All four movements of every target still require a
physical piston and all four recovery movements require legal contacts;
no helper motion is injected externally. Terminal trajectories are fixed
obligations, with global mediated-power gates added before routing.

The first eight narrow layouts give7 mandatory failures/1 source overlap.
`mmmm_glazed_mandatory_witness.json` localizes this failure to neighbouring
module sources, rather than the target's own late-burst source. The wider
six-module placement (`--wide`, native41199) now passes that gate and has
one routed candidate after three attempts. Short physical simulation is
pending; the terminal transport assumptions are not proven until it passes.
This is not a higher-speed record and does not change mmmmwwPL22.

Pure-pull all-body rerouting77512 operates on the already trimmed102 lead,
intersects prior selected ports with surviving contacts, and preserves the
first102 bank evidence.5-cell pruning passed full encoded verification and
audit but did not lower the maximum load. New rerouting reduces more cell
counts while keeping102 in short exact checks; full result pending.

`bank_pending_pull3.py` (native50608) waits for the already-live15441 sample
command's completion report, then invokes the unchanged strict `bank_pull3`
gate. It will bank102 only on all80 complete, full10000-tick exact cases;
the result goes to `pending_pull3_bank_result.json`. A failed/partial sweep
does not bank. This completes an authorized audit even if model usage stops
before the native sweep finishes. No reset, purchase or simulator change.

Current live sessions:15441 pure102 samples;50608 gated bank follow-through;
16380 old local11 eight-copy80;35226 compact local8 endpoint80;61702 mixed
gauged closure;77512 pure all-body reroute;41199 wider glazed mmmmww ports.
Latest usage ordinary allowed,80% five-hour and98% weekly. Goal remains active.

## Glazed power ports realized; full result pending

The first wide glazed batch routes5/8 nominal assemblies, but all stall after
0–1 moves. Snapshots and `compare_glazed_mmmm.py` locate the first mismatch
at tick2. The cause is a generator conversion error: `sample(range(6),3)`
routes only three of six bodies. Corrected code routes all six and asserts
every body is connected before saving. This correction does not change the
simulator or excuse the failed candidates. Preserve the v1 screen/trace and
snapshot evidence; it is not a physical impossibility of glazed terminals.

Corrected wide v2 (79897) has route failures because the last helper connects
across the long open transverse placement. A closed hexagonal placement
(`mmmm_glazed_ports.py --hex`,7473) gives8/8 routed, all8 clean240-tick
3.333bps/80-cell advances. Best `mmmm_glazed_hex_six_s006_pl47.flyer` needs47;
full12/+4 encoded verification and conservation audit live87820. No80-case
sweep is scheduled because it does not improve existing mmmmwwPL22.

The successful short layouts discharge the glued terminal's motion with an
actual helper push, keep source power two transverse cells from the normal
member, and use glazed nonadhesion to avoid target recruitment. Rod/observer
directions follow each rotated port. This is a reusable power interface proof
lead; it is not a low-push-limit record. Compact this interface or apply its
source separation to the proposed pull-first front body before more blind
layout searches.

All-body pure102 rerouting completes its full exact diagnostic run at102;
it removes additional cells but does not lower maximum load. No equivalent
80-case sweep is launched. `pull3_circular.py` (47682) next tests16 bounded
placements of ten bodies around radii10/12, with opposite-material phase
pairs adjacent. It preserves the saturated lifecycle and actual source and
pickup gates; output/evidence prefix `pull3_circular_*`. Initial bounds are
cap110/body; no result yet. A working smaller closed placement is needed to
reduce the mandatory port separation, rather than repeatedly trimming rails.

Live:15441 pure102 samples;50608 strict bank follow-through;16380 old local11
eight-copy80;35226 compact local8 endpoint80;61702 gauged mixed closure;
79897 corrected wide glazed route;87820 hexPL47 full audit;47682 circular
pure placements.77512 full reroute and7473 hex synthesis completed.

HexPL47 full result: encoded verify and audit both pass10000 ticks, distance3334 (partial final cycle),833 exact +4/12 cell/owner recurrences,269 boundary blocks, all permanent kinds conserved, zero extension/movement failures, max47. Complete power/terminal transport proof for this layout; no80-case sweep or bank record. Evidence: mmmm_glazed_hex_six_s006_pl47.verify.txt and .audit.txt.

Final audit results inspected after native completion: pure102 banked; both mixed-chain endpoint sweeps pass80/80; pull-firstPL59 passes80/80. See `NATIVE_AUDIT_CHECKPOINT.md` and individual certificates. Hybrid closure, circular placement and gauged closure completed with no candidate. No simulator changes.
