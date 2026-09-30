from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[3]
def read(p):return p.read_text(encoding='utf-8')
def write(p,s):p.write_bytes(s.encode('utf-8'))
p=h/'FINDINGS.md';s=read(p)
s=s.replace('All-ten-body rerouting77512 is live; accepted smaller bodies so far keep102.','All-ten-body rerouting77512 completed: several smaller rails, full exact\n+  diagnostic10k still102. Preserve first102 encoded80-case evidence.')
s+='''
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
'''
write(p,s)
p=root/'flyers/RESEARCH_LOG.md';s=read(p);s=s.replace('and all-body rerouting continues.','and all-body rerouting also passes full exact10k at102 without lowering load; circular placements are being tested.')
s=s.replace('Separate-role closures and mmwmmw extensions are being tested;','Separate-role closures and mmwmmw extensions are being tested. A glazed-terminal/rod power interface for mmmmww now works in8/8 short hexagonal layouts (best47, full exact audit pending), separating late-burst helper sources from targets; it does not beat mmmmwwPL22.');write(p,s)
p=root/'flyers/WIP/experiments/INDEX.md';s=read(p);s=s.replace('mixed local8/11 full literal chains, endpoint sweeps pending','mixed local8/11 full literal chains, endpoint sweeps pending; glazed mmmmww power ports work short, pure circular placements active');write(p,s)
