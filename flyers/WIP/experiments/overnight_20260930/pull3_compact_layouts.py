"""Shorten the ten-body lead's helper routes by rearranging distinct bodies."""
from pathlib import Path
import json,subprocess,collections,random
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
RUNNER=ROOT/'target/release/fastflyer-research.exe'
def main():
    s=(HERE/'pull3_synthesis.py').read_text()
    s=s.replace('p=(base,target*spacing,j*spacing)','p=(base,*place(target,j,spacing))')
    s=s.replace('owner,observer,rx=rng.choice(viable)',
        'ranked=sorted(viable,key=lambda v:sum(abs(a-b) for a,b in zip(place(v[0],1,spacing),(p[1],p[2]+1))))\n   owner,observer,rx=rng.choice(ranked[:3])')
    s=s.replace('-4<=q[2]<=2*spacing+4','-4<=q[2]<=6*spacing+4')
    s=s.replace("if __name__=='__main__':main()",'')
    source=HERE/'derived_pull3_compact.py';source.write_text(s)
    ns={'__file__':str(source)};exec(compile(s,str(source),'exec'),ns)
    out=HERE/'pull3_compact_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for layout in ('paired_line','paired_grid','split_grid'):
        def place(i,j,spacing):
            if layout=='paired_line':return ((2*(i%5)+i//5)*spacing,j*spacing)
            if layout=='paired_grid':return ((i%5)*2*spacing,(i//5)*4*spacing+j*spacing)
            return ((i%5)*spacing,(i//5)*4*spacing+j*spacing)
        ns['place']=place
        for seed in range(8):
            ans,reason=ns['build'](seed,3)
            if ans is None:stats[layout+':'+reason]+=1
            else:
                f,m=ans;name=f'{layout}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(layout=layout,file=name+'.flyer',**m));stats[layout+':routed']+=1
            pending=HERE/'pull3_compact_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,current_layout=layout,next_seed=seed+1),indent=2));pending.replace(HERE/'pull3_compact_manifest.json')
            print(layout,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'pull3_compact_screen.csv')],capture_output=True,text=True)
    (HERE/'pull3_compact_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
