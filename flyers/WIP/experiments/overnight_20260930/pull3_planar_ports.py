"""Shorten pulling target rails by putting all three target ports in one plane."""
from pathlib import Path
import collections,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
def main():
    s=(HERE/'derived_pull3_compact.py').read_text()
    s=s.replace('rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[]','rng=random.Random(seed);ss=[set() for _ in S];ps=[];sources=[];fronts=[rng.choice((-1,0,1)) for _ in S]')
    s=s.replace('base=rng.choice((-1,0,1));p=(base,*place(target,j,spacing))','base=fronts[target]+DISP[target][f]-dp[f]+2;p=(base,*place(target,j,spacing))')
    # All-source direct and mediated checks cover compact power interference.
    cross='''
 for t in range(5):
  for pp,dp,f,target in ps:
   basepos=shift(pp,dp[t])
   if t==(f-1)%5:continue
   for rp,owner,observer in sources:
    if observer and not S[owner][(t-1)%5]:continue
    sourcepos=shift(rp,DISP[owner][t])
    direct=(add(sourcepos,D[5])==basepos if observer else sum(abs(a-b) for a,b in zip(sourcepos,basepos))==1)
    if direct and sourcepos!=shift(basepos,-1):return None,'cross_power'
'''
    s=s.replace(' @functools.lru_cache(None)',cross+' @functools.lru_cache(None)')
    mediated='''
    if t!=(f-1)%5 and near and q!=shift(r,-1):
     for rp,owner,observer in sources:
      if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[5])==q:return False
'''
    s=s.replace('    if t!=f and t!=(f-1)%5:',mediated+'    if t!=f and t!=(f-1)%5:')
    # Accommodate the changed axial ports; this is not a score modification.
    s=s.replace('-5<=q[0]<=6','-6<=q[0]<=8')
    source=HERE/'derived_pull3_planar.py';source.write_text(s);ns={'__file__':str(source)};exec(compile(s,str(source),'exec'),ns)
    out=HERE/'pull3_planar_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for layout in ('paired_grid','cyclic_line','paired_line'):
        def place(i,j,spacing):
            if layout=='paired_grid':return ((i%5)*2*spacing,(i//5)*4*spacing+j*spacing)
            if layout=='cyclic_line':return ((i%5+5*((i%5)%2!=(i//5)))*spacing,j*spacing)
            return ((2*(i%5)+i//5)*spacing,j*spacing)
        ns['place']=place
        for seed in range(12):
            ans,reason=ns['build'](seed,3,cap=110)
            if ans is None:stats[layout+':'+reason]+=1
            else:
                f,m=ans;name=f'{layout}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(layout=layout,file=name+'.flyer',**m));stats[layout+':routed']+=1
            pending=HERE/'pull3_planar_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,current_layout=layout,next_seed=seed+1),indent=2));pending.replace(HERE/'pull3_planar_manifest.json')
            print(layout,seed,dict(stats),flush=True)
    r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(HERE/'pull3_planar_screen.csv')],capture_output=True,text=True);(HERE/'pull3_planar_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
