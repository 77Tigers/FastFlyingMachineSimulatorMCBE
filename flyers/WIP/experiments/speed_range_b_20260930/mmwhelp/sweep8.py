import sys,time,json
import model, gen5, est
VAR=dict(diag=dict(share_rs=True,share_obs='diag'),diagp=dict(share_rs=True,share_obs='diag',lane_perm='rand'))
def run(worker,nw,variant,layouts,seeds,thresh,outdir,fronts):
    kw=VAR[variant];jobs=[(L,s) for s in seeds for L in layouts];dist=[]
    for k,(L,s) in enumerate(jobs):
        if k%nw!=worker: continue
        centers=[(0,0),(L[0],L[1]),(L[2],L[3])]
        try: ans,reason=gen5.build2(s,centers,fronts=fronts,**kw)
        except Exception as e: ans,reason=None,'exc'
        if ans is None: continue
        f,d=ans
        w,_=est.est_load([set(map(tuple,x)) for x in d['segments']],[(tuple(p),dp,ff,t,st) for p,dp,ff,t,st in d['pistons']],[(tuple(p),o,ob,dr) for p,o,ob,dr in d['sources']])
        dist.append(w)
        if w<=thresh:
            name=f"{variant}_M{L[0]}_{L[1]}_{L[2]}_{L[3]}_s{s:05d}"
            f.push_limit=200;f.save(f"{outdir}/{name}.flyer");json.dump(d,open(f"{outdir}/{name}.json",'w'))
            print('KEEP',name,d['counts'],w,flush=True)
    dist.sort();print('DIST',variant,worker,len(dist),dist[:10],flush=True)
if __name__=='__main__':
    worker,nw=int(sys.argv[1]),int(sys.argv[2]);variant=sys.argv[3];s0,s1=int(sys.argv[4]),int(sys.argv[5]);thresh=int(sys.argv[6]);out=sys.argv[7];layouts=json.loads(sys.argv[8]);fronts=tuple(json.loads(sys.argv[9]))
    run(worker,nw,variant,layouts,range(s0,s1),thresh,out,fronts)
