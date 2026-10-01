import sys,itertools,time,json
sys.path.insert(0,'flyers/WIP/experiments/speed_range_b_20260930/mmw6')
import est,gen6
def hexc(R):
    return [(0,0),(0,R),(R*5//6,R*3//2),(R*5//3,R),(R*5//3,0),(R*5//6,-R//2)]
def gridc(a,b):  # 2 rows x 3 cols
    return [(r*a,c*b) for r in range(2) for c in range(3)]
base={}
for R in (4,5,6):base['hex%d'%R]=hexc(R)
for a,b in ((4,4),(4,5),(5,5)):base['g%d_%d'%(a,b)]=gridc(a,b)
perms={'ring':[0,1,2,3,4,5],'twinadj':[0,3,1,4,2,5],'alt':[0,1,2,5,4,3],'alt2':[0,2,1,3,5,4]}
res=[]
for name,c in base.items():
    for pn,perm in perms.items():
        centers=[None]*6
        for pos,body in enumerate(perm):centers[body]=c[pos]
        fails={};vals=[]
        t=time.time()
        for seed in range(6):
            ans,r=gen6.build(seed,centers,pickup_only=True)
            if ans is None:fails[r]=fails.get(r,0)+1;continue
            e=est.estimate(ans[2]);vals.append((sum(e),max(e)))
        print(name,pn,'fails',fails,'est',sorted(vals)[:3],round(time.time()-t),flush=True)
