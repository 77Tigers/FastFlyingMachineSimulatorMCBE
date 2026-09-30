from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[3]
def read(p):return p.read_text(encoding='utf-8')
def write(p,s):p.write_bytes(s.encode('utf-8'))
p=h/'FINDINGS.md';s=read(p);a=s.index('## Current authoritative checkpoint');b=s.index('Later sections retain',a)
s=s[:a]+'''## Current authoritative checkpoint

- Banked mmwmmw3.333bps: **PL36**,105 boundary blocks, all80 full exact
  10000-tick cases with833 nominal +4/12 recurrences, zero failures and
  conservation mismatches. Bank `flyers/bank/pl36/planar_mmwmmw.flyer`, SHA
  `30793bbea94549f6347680bfbef707cda5de8524bbabe7587c93c3ccb7d38470`.
  Preserved stepsPL37 (109 blocks) andPL57 (161), also all80 exact.
- Banked pulling-only3bps:PL106 (852 blocks), plus preservedPL126/127.
  PurePL102 passes diagnostic/encoded10k and is undergoing80 samples15441.
  New connected pruning44497 removes5 cells in first round; full run pending.
- Mixed local11: literal1/2/4/8 copies all pass full encoded10000 ticks and
  tagged ledgers;1-copy80/80 passes,8-copy samples live16380.
- Mixed local8: literal1/2/4/8 bridged copies **all pass full encoded10000
  ticks and tagged body ledgers**, each five-cell added target3000 actions,
  local7–8. Whole driver/helper limits66/83/119/195. Endpoint1/8-copy80
  sweeps live35226; not a globalPL8 flyer.
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

'''+s[b:]
s+='''
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
'''
write(p,s)
p=root/'flyers/RESEARCH_LOG.md';s=read(p);a=s.index('**New banked mmwmmw result:**');b=s.index('\n\nThe user reopened',a)
s=s[:a]+'''**New banked mmwmmw result: PL36 at3.333bps.** Coplanar four-port choreography plus connected pruning gives3333/10000 with105 boundary blocks, improving pattern-specificPL65→57→37→36. All80 full cases pass all833 exact twelve-tick/+4 cell/owner recurrences, conservation and zero failures. Bank: `bank/pl36/planar_mmwmmw.flyer`. The separate mmmmww record remainsPL22. **Pulling-only3bps is banked atPL106**, with all80 full exact audits; ten distinct bodies and30 -X sticky pistons. PreservedPL126/127 steps also pass; PL102 is undergoing80-case certification and further connected pruning. Every extension is empty in the127 trace. See current overnight findings before duplicating work.'''+s[b:]
s=s.replace('Literal1/2/4/8 copies now pass short exact tests at whole limits66/83/119/195; full tagged and80-case audits are running.','Literal1/2/4/8 copies all pass full10000-tick exact checks and tagged ledgers at whole limits66/83/119/195;1/8-copy80-case audits are running.')
write(p,s)
p=root/'flyers/WIP/experiments/INDEX.md';s=read(p)
s=s.replace('Active; mmwmmwPL57 and pure-pull3bpsPL106 banked; pure102 diagnostic/106 audit; mixed3bps local8 single interface and local11 full literal chains','Active; mmwmmwPL36 and pure-pull3bpsPL106 banked; pure10280-case pending; mixed local8/11 full literal chains, endpoint sweeps pending').replace('overnight_20260930/mmw_hex_trim_pl57.flyer','overnight_20260930/mmw_planar_trim_pl36.flyer')
s=s.replace('Working at PL65; routes remain bulky','Banked coplanarPL36; olderPL65 timing witness preserved').replace('PL21 twelve-carrier lead; 80-sample audit outstanding','mmmmwwPL21 twelve-carrier lead passes80 speed/conservation cases, fails strict nominal recurrence').replace('Reopened by user;PL9/2.5 bps now banked; PL10 smaller two-carrier reference retained','BankedPL106/3bps andPL9/2.5bps; pure102 full-case sweep pending; olderPL10 reference retained')
s=s[:s.index('\nLatest overnight checkpoint:')]+'\nLatest overnight checkpoint: mmwmmwPL36 banked; compact mixed local8 literal chains pass full tagged1/2/4/8-copy checks. See authoritative overnight findings for live sessions and pending endpoint sweeps.\n'
write(p,s)
p=root/'flyers/ABSTRACTION_PIPELINE.md';s=read(p);anchor='## 4. Piston-group contact choreography'
s=s.replace(anchor,'''For route-heavy schedules, optimize each target's drive ports in the axial
table before routing. Different member recovery histories can put their
initial bases on different X planes while making their action contacts share
one target plane. Preserve the resulting source alignment windows, including
early bursts where a later member must remain unpowered. This was physically
tested by the overnight `mmw_planar.py`: the three different mmwmmw body
timings and twelve normal members produce a bankedPL36 mechanism after
pruning, with80 full exact audits. It improves this family's routing overhead;
it does not establish that coplanar ports always minimize load.

'''+anchor)
write(p,s)
