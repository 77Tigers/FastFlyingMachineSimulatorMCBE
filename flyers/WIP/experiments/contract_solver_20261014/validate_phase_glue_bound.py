"""Calibrate phase exclusions against explicit per-slot movement states."""
import itertools,json,random,hashlib,argparse
from pathlib import Path
from phase_glue_bound import phase_witness
from fastflyer import Kind

def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);args=ap.parse_args()
 words=[''.join(v) for v in itertools.product('mw',repeat=5) if v.count('m')==3];rng=random.Random(20261021);count=0
 for a,b in itertools.product(words,repeat=2):
  for same in [False,True]:
   for i in range(25):
    pos=tuple(rng.randrange(-3,4) for _ in range(3));obs=tuple(rng.randrange(-3,4) for _ in range(3));blocked=False;ax=bx=0
    for aa,bb in zip(a,b):
     for da in ([0,1] if aa=='m' else [0]):
      for db in ([0,1] if bb=='m' else [0]):
       distance=abs(pos[0]+ax+da-obs[0]-bx-db)+abs(pos[1]-obs[1])+abs(pos[2]-obs[2]);blocked|=distance<=(1 if same else 0)
     ax+=aa=='m';bx+=bb=='m'
    result=phase_witness({pos},[{pos}],1,a,Kind.SLIME,[('B',{obs},Kind.SLIME if same else Kind.HONEY,b)])
    assert (not result['cap_feasible'])==blocked,(a,b,pos,obs,same,result)
    count+=1
 report={'seed':20261021,'fixtures':count,'pass':True,'scope':'independent explicit per-slot before/after movement configurations vs phase exclusion helper','helper_sha256':hashlib.sha256(Path(__file__).with_name('phase_glue_bound.py').read_bytes()).hexdigest()}
 args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
