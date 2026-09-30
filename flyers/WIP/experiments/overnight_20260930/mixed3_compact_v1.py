"""Compact target ports into one moving plane, with separated front helpers."""
from pathlib import Path
import json,collections,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
def main():
    s=(HERE/'derived_mixed3.py').read_text()
    s=s.replace('rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[]','rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[];fronts=[rng.choice((-1,0,1)) for _ in S]')
    s=s.replace('base=rng.choice((-1,0,1));p=(base,target*spacing,j*spacing)',
        'base=fronts[target]+DISP[target][f]-dp[f]-(-2 if sticky else 1);p=(base,CENTERS[target][0]+PORTS[j][0],CENTERS[target][1]+PORTS[j][1])')
    s=s.replace('(rx,p[1],p[2]+1)','(rx,p[1]+POWER[0],p[2]+POWER[1])').replace('Block.observer(5,','Block.observer(POWER_DIR,')
    s=s.replace('-4<=q[1]<=4*spacing+4 and -4<=q[2]<=2*spacing+4','-6<=q[1]<=max(c[0] for c in CENTERS)+5 and -6<=q[2]<=max(c[1] for c in CENTERS)+5')
    s=s.replace("if __name__=='__main__':main()",'')
    source=HERE/'derived_mixed3_compact.py';source.write_text(s);ns={'__file__':str(source)};exec(compile(s,str(source),'exec'),ns)
    out=HERE/'mixed3_compact_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for layout,centers in [('pentagon',[(0,0),(0,4),(3,5),(5,2),(3,-1)]),('pentagon_wide',[(0,0),(0,5),(4,6),(7,2),(4,-2)])]:
        for variant,(ports,power,direction) in enumerate([([(1,0),(-1,0),(0,1)],(0,1),5), ([(0,1),(0,-1),(1,0)],(1,0),3)]):
            ns.update(CENTERS=centers,PORTS=ports,POWER=power,POWER_DIR=direction)
            for seed in range(16):
                ans,reason=ns['build'](seed,4,cap=70)
                if ans is None:stats[layout+':'+reason]+=1
                else:
                    f,m=ans;name=f'{layout}_v{variant}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(layout=layout,variant=variant,file=name+'.flyer',**m));stats[layout+':routed']+=1
                pending=HERE/'mixed3_compact_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,current_layout=layout,variant=variant,next_seed=seed+1),indent=2));pending.replace(HERE/'mixed3_compact_manifest.json')
                print(layout,variant,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'mixed3_compact_screen.csv')],capture_output=True,text=True);(HERE/'mixed3_compact_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
