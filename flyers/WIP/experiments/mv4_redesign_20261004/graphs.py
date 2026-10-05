"""Finite carrier-graph survey. 4096 graphs x 57 saved regular placements.

Usage: python graphs.py [seconds=2700]. Initial ranking is arithmetic only;
actual static contact/power checks are resumed from attempts.jsonl.
"""
import sys,json,time,itertools,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
EASY=Path(__file__).resolve().parent.parent/'mv4_easy_20261004'
sys.path.insert(0,str(EASY))
import common as c
import builder
HERE=Path(__file__).resolve().parent
START=time.monotonic();DEADLINE=START+min(2700,int(sys.argv[1]) if len(sys.argv)>1 else 2700)
source=json.loads((EASY/'compact43/reroute_best.json').read_text())
config0=dict(own=source['parent']['own'],previous=source['parent']['previous'])
raw=json.loads((EASY.parent/'mv4_elegant_20261004/survey.json').read_text())['ranked']
placements=[];seen=set()
for item in raw:
    key=json.dumps(item['placement'])
    if key not in seen:seen.add(key);placements.append(item['placement'])
assert len(placements)==57,len(placements)
pair_choices=lambda i,offset:tuple(j for j in range(6) if j%3==(i+offset)%3)
choices_f=[pair_choices(i,1) for i in range(6)]
choices_p=[pair_choices(i,2) for i in range(6)]

def graph(mask):
    return (tuple(choices_f[i][(mask>>i)&1] for i in range(6)),
            tuple(choices_p[i][(mask>>(i+6))&1] for i in range(6)))

def connected(f,p):
    seen={0};stack=[0]
    while stack:
        i=stack.pop()
        for j in (f[i],p[i]):
            if j not in seen:seen.add(j);stack.append(j)
        for j in range(6):
            if i in (f[j],p[j]) and j not in seen:seen.add(j);stack.append(j)
    return len(seen)==6

def equivalence(f,p):
    # Relabel paired phase copies. Material labels move with their old cores.
    keys=[]
    for swap in itertools.product((0,1),repeat=3):
        perm=tuple(i+3 if swap[i%3] and i<3 else i-3 if swap[i%3] else i for i in range(6))
        nf=[0]*6;np=[0]*6;nk=[0]*6
        for i in range(6):
            j=perm[i];nf[j]=perm[f[i]];np[j]=perm[p[i]];nk[j]=i%2
        for flip in (0,1):keys.append((tuple(nf),tuple(np),tuple(k^flip for k in nk)))
    return min(keys)

dist=[]
for placement in placements:
    centers=placement[0]
    dist.append([[sum(abs(centers[i][k]-centers[j][k]) for k in range(2)) for j in range(6)] for i in range(6)])
ordered=[];equiv=set();category=collections.Counter();control_mask=None
for mask in range(4096):
    f,p=graph(mask)
    if f==tuple((i+1)%6 for i in range(6)) and p==tuple((i+2)%6 for i in range(6)):control_mask=mask
    if not connected(f,p):category['disconnected']+=1;continue
    equiv.add(equivalence(f,p));category['connected']+=1
    symmetric=all(f[i+3]==(f[i]+3)%6 and p[i+3]==(p[i]+3)%6 for i in range(3))
    category['symmetric' if symmetric else 'relaxed']+=1
    motifs=len({((f[i]-i)%6,(p[i]-i)%6) for i in range(6)})
    incf=collections.Counter(f);incp=collections.Counter(p)
    load_est=max(6+6*incf[i]+2*incp[i] for i in range(6))
    for pi,D in enumerate(dist):
        spans=[sum(2*D[j][i] for j in range(6) if f[j]==i)+sum(D[j][i] for j in range(6) if p[j]==i) for i in range(6)]
        score=(load_est,max(spans),sum(spans),motifs)
        ordered.append((score,mask,pi))
ordered.sort()
assert control_mask is not None
c.write_json(HERE/'graph_plan.json',dict(total_graphs=4096,placements=len(placements),
            graph_categories=category,material_preserving_relabel_classes=len(equiv),
            control_mask=control_mask,control_graph=graph(control_mask),
            ranking='estimated peak mandatory+observer cells, max/total weighted center span, distinct role motifs',
            score_is_heuristic=True))

ledger=HERE/'graph_attempts.jsonl'
attempts=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
done={(r['mask'],r['placement']) for r in attempts}
valid_graphs={r['mask'] for r in attempts if r['outcome']=='interface_valid'}
valid_relaxed={r['mask'] for r in attempts if r['outcome']=='interface_valid' and not r['symmetric'] and r['motifs']<=2}
lastprint=0
for score,mask,pi in ordered:
    if (mask,pi) in done:continue
    if time.monotonic()+4>=DEADLINE:break
    # Keep contrasting examples: at least seven graphs overall and three new
    # repeated-motif, non-opposite graphs before closing the finite top sample.
    if len(valid_graphs)>=10 and len(valid_relaxed)>=3:break
    f,p=graph(mask);sym=all(f[i+3]==(f[i]+3)%6 and p[i+3]==(p[i]+3)%6 for i in range(3))
    motifs=score[3]
    # A six-unique-motif graph is not an elegant redesign. It is still counted
    # in the 4096-graph arithmetic census above.
    if motifs>3:continue
    config=dict(config0,following=f,previous_carrier=p)
    captured={}
    def take(must,fixed,bounds,cap,rng):
        captured.update(mandatory=[set(s) for s in must],fixed=fixed,bounds=bounds)
        return None
    _,why=builder.build(0,placements[pi],cap=39,joint_router=take,config=config)
    record=dict(mask=mask,placement=pi,score=score,following=f,previous=p,
                symmetric=sym,motifs=motifs,outcome='interface_valid' if captured else why[0])
    if captured:
        must=captured['mandatory']
        counts=[len(s) for s in must]
        components=[len(c.base.components(s)) for s in must]
        record.update(mandatory_counts=counts,component_counts=components,
                      max_mandatory=max(counts),sum_mandatory=sum(counts))
        valid_graphs.add(mask)
        if not sym and motifs<=2:valid_relaxed.add(mask)
    with ledger.open('a') as out:out.write(json.dumps(record)+'\n')
    attempts.append(record);done.add((mask,pi))
    if time.monotonic()-lastprint>30:
        status=dict(elapsed=round(time.monotonic()-START),attempts=len(attempts),
                    outcomes=dict(collections.Counter(r['outcome'] for r in attempts)),
                    distinct_valid=len(valid_graphs),relaxed_motif_valid=len(valid_relaxed))
        c.write_json(HERE/'graph_status.json',status);print(json.dumps(status),flush=True);lastprint=time.monotonic()

valid=sorted((r for r in attempts if r['outcome']=='interface_valid'),
             key=lambda r:(max(r['mandatory_counts']),r['score'][0],r['score'][1],r['score'][2],r['motifs']))
selected=[];taken=set()
for r in valid:
    if r['mask'] not in taken:
        selected.append(r);taken.add(r['mask'])
    if len(selected)>=7:break
for r in valid:
    if not r['symmetric'] and r['motifs']<=2 and r['mask'] not in taken:
        selected.append(r);taken.add(r['mask'])
    if len(selected)>=10:break
# Retain the exact original graph/layout as a non-ranking control.
control=dict(mask=control_mask,placement=None,following=graph(control_mask)[0],previous=graph(control_mask)[1],
             source='compact43/reroute_best.json')
state=dict(status='completed' if len(valid_graphs)>=10 and len(valid_relaxed)>=3 else 'sample_incomplete',
           attempted=len(attempts),distinct_valid=len(valid_graphs),relaxed_motif_valid=len(valid_relaxed),
           selected=selected[:10],control=control)
c.write_json(HERE/'graph_results.json',state)
print(json.dumps({k:v for k,v in state.items() if k!='selected'}),flush=True)
