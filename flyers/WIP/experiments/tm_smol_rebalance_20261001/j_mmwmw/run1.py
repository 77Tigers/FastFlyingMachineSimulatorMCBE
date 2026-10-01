import itertools, sys, time
import rider_floor as R
D=[0,1,2,3,4]
maxadj=int(sys.argv[1]) if len(sys.argv)>1 else None
for base in ['mmmww','mmwmw']:
    mslots=[t for t in range(5) if base[t]=='m']
    for kinds in itertools.product(['pull','push'],repeat=3):
        k=dict(zip(mslots,kinds))
        t0=time.time()
        r=R.solve(base,D,k,maxadj)
        if r is None:
            print(base,kinds,'INFEASIBLE'); continue
        best,pats,meta=r
        print(base,kinds,'maxrid=%d sum=%d'%best[0], 'npat',[len(p) for p in pats], '%.1fs'%(time.time()-t0), flush=True)
