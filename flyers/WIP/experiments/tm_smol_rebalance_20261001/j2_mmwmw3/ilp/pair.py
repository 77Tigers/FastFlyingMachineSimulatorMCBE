import sys,itertools,os
sys.path.insert(0,'../../j2_front_smol'); sys.argv=['x']
from layered import *
DG=directed_graph('../../base.bodytrack.txt',2,TM)
for (V,k) in list(DG): DG[(V,k)]|=TM_ALLOW[V]
words=[''.join('m' if k in s else 'w' for k in range(5)) for s in itertools.combinations(range(5),3)]
CAP=int(os.environ.get('CAP','17'))
kinds0={(n,s):('pull' if (n,s) in TM_PULLS else 'push') for n in TM for s in range(L) if TM[n][0][s]=='m'}
best=[]
for oth in ('B9','B18','B10','B11'):
  for w in words:
    if w==TM[oth][0]: continue
    T=dict(TM);T['B15']=('mwmwm',TM['B15'][1]);T[oth]=(w,TM[oth][1])
    ms=[i for i,c in enumerate(w) if c=='m']
    for pp in itertools.combinations(ms,2) if False else [None]:
      kk={('B15',0):'pull',('B15',2):'pull',('B15',4):'push'}
      r=solve(T,kk,TM_REAR,allow=DG,K=2,cap=CAP,excess=True,time_limit=30,ref_allow=TM_ALLOW,c_edge=25)
      if r:
        n12=sum(1 for v in r['loads'].values() if v>=12); n12r=sum(1 for (n,t),v in r['loads'].items() if n in TM_REAR and v>=12)
        print('FEAS cap',CAP,oth,w,'maxrear',r['max_rear'],'maxall',r['max_all'],'n>=12',n12,'rear>=12',n12r,flush=True)
        best.append((n12r,n12,oth,w,r,T))
best.sort(key=lambda x:x[:2])
if best:
  n12r,n12,oth,w,r,T=best[0]
  print('BEST',oth,w,n12r,n12);report(r,T,TM_REAR)
  new=[(V,d) for V,ds in r['touch'].items() for d in ds if d not in TM_ALLOW[V]]
  drop=[(V,d) for V in TM for d in TM_ALLOW[V] if d not in r['touch'][V]]
  print('new edges',new,'dropped',drop)
  for k,v in sorted(r['carry'].items()):
    if k[0] in ('B15',oth,'B9','B18'): print('carry',k,v)
