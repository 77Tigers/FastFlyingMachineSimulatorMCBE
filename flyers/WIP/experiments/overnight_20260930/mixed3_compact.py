"""Compact target ports into one moving plane, with separated front helpers."""
from pathlib import Path
import json,collections,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RUNNER=ROOT/'target/release/fastflyer-research.exe'
def main():
    s=(HERE/'derived_mixed3.py').read_text()
    s=s.replace('rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[]','rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[];fronts=[rng.choice((-1,0,1)) for _ in S]')
    s=s.replace('base=rng.choice((-1,0,1));p=(base,target*spacing,j*spacing)',
        'base=fronts[target]+DISP[target][f]-dp[f]-(-2 if sticky else 1);p=(base,CENTERS[target][0]+PORTS[j][0],CENTERS[target][1]+PORTS[j][1])')
    s=s.replace('(rx,p[1],p[2]+1)','(rx,p[1]+POWER[0],p[2]+POWER[1])').replace('Block.observer(5,','Block.observer(POWER_DIR,')
    s=s.replace('-4<=q[1]<=4*spacing+4 and -4<=q[2]<=2*spacing+4','-6<=q[1]<=max(c[0] for c in CENTERS)+5 and -6<=q[2]<=max(c[1] for c in CENTERS)+5')
    # Check every source against every actuator. The first compact witness
    # soft-powered a neighbouring normal member, which fired ahead of its
    # intended phase and displaced the correct member before it could act.
    cross='''
 for t in range(5):
  for pp,dp,f,target,sticky in ps:
   basepos=shift(pp,dp[t]);ext=(f-1)%5 if sticky else f
   if t==ext:continue
   for rp,owner,observer in sources:
    if observer and not S[owner][(t-1)%5]:continue
    sourcepos=shift(rp,DISP[owner][t])
    direct=(add(sourcepos,D[POWER_DIR])==basepos if observer else sum(abs(a-b) for a,b in zip(sourcepos,basepos))==1)
    if direct and sourcepos!=shift(basepos,-1 if sticky else 1):return None,'cross_power'
'''
    s=s.replace(' @functools.lru_cache(None)',cross+' @functools.lru_cache(None)')
    mediated='''
    if t!=((f-1)%5 if sticky else f) and near and q!=shift(r,-1 if sticky else 1):
     for rp,owner,observer in sources:
      if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[POWER_DIR])==q:return False
'''
    s=s.replace('    if t not in ((f,(f-1)%5)',mediated+'    if t not in ((f,(f-1)%5)')
    s=s.replace("if __name__=='__main__':main()",'')
    source=HERE/'derived_mixed3_compact_v3.py';source.write_text(s);ns={'__file__':str(source)};exec(compile(s,str(source),'exec'),ns)
    out=HERE/'mixed3_compact_v3_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for layout,centers in [('pentagon_wide',[(0,0),(0,5),(4,6),(7,2),(4,-2)]),('pentagon7',[(0,0),(0,7),(5,9),(9,3),(5,-3)])]:
        for variant,(ports,power,direction) in enumerate([([(2,0),(-2,0),(0,2)],(0,1),5), ([(0,2),(0,-2),(2,0)],(1,0),3)]):
            ns.update(CENTERS=centers,PORTS=ports,POWER=power,POWER_DIR=direction)
            for seed in range(16):
                ans,reason=ns['build'](seed,4,cap=70)
                if ans is None:stats[layout+':'+reason]+=1
                else:
                    f,m=ans;name=f'{layout}_v{variant}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(layout=layout,variant=variant,file=name+'.flyer',**m));stats[layout+':routed']+=1
                pending=HERE/'mixed3_compact_v3_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,current_layout=layout,variant=variant,next_seed=seed+1),indent=2));pending.replace(HERE/'mixed3_compact_v3_manifest.json')
                print(layout,variant,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'mixed3_compact_v3_screen.csv')],capture_output=True,text=True);(HERE/'mixed3_compact_v3_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
