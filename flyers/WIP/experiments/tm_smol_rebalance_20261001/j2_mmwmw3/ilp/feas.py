import sys,itertools
sys.path.insert(0,'../../j2_front_smol'); sys.argv=['x']
from layered import *
DG=directed_graph('../../base.bodytrack.txt',2,TM)
for (V,k) in list(DG): DG[(V,k)]|=TM_ALLOW[V]
words=[''.join('m' if k in s else 'w' for k in range(5)) for s in itertools.combinations(range(5),3)]
CAP=int(__import__('os').environ.get('CAP','17'))
def run(T,R,pp):
    kk={}
    for s in pp: kk[(R,s)]='pull'
    r=solve(T,kk,TM_REAR,allow=DG,K=2,cap=CAP,excess=True,time_limit=30,ref_allow=TM_ALLOW,c_edge=25)
    return r
mode=sys.argv[1] if len(sys.argv)>1 else 'single'
import os
mode=os.environ.get('MODE','single')
for R in TM_REAR:
  for w in words:
    if w==TM[R][0]: continue
    ms=[i for i,c in enumerate(w) if c=='m']
    others=[None] if mode=='single' else [(o,w2) for o in TM_REAR if o!=R for w2 in words if w2!=TM[o][0]]
    for oth in others:
      T=dict(TM);T[R]=(w,TM[R][1])
      if oth:T[oth[0]]=(oth[1],TM[oth[0]][1])
      for pp in itertools.combinations(ms,2):
        r=run(T,R,pp)
        if r:
            n12=sum(1 for v in r['loads'].values() if v>=12)
            print('FEAS',R,w,oth,'pulls',pp,'maxrear',r['max_rear'],'maxall',r['max_all'],'n>=12',n12,flush=True)
            break
