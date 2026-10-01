import sys,time,json,itertools
import model, gen4
mp=model.mp
def run(worker,nworkers,layouts,seeds,thresh,outdir):
    stats={}
    best=[]
    jobs=[(L,s) for L in layouts for s in seeds]
    for k,(L,s) in enumerate(jobs):
        if k%nworkers!=worker: continue
        centers=[(0,0),(0,L[0]),(L[1],L[2])]
        t0=time.time()
        try:
            ans,reason=gen4.build2(s,centers,share_rs=True,share_obs=True)
        except Exception as e:
            ans,reason=None,'exc:'+type(e).__name__
        key=str(L)
        st=stats.setdefault(key,{})
        if ans is None: st[reason]=st.get(reason,0)+1; continue
        f,data=ans
        c=data['counts']
        st['ok']=st.get('ok',0)+1
        if max(c)<=thresh:
            name=f"L{L[0]}_{L[1]}_{L[2]}_s{s:05d}"
            f.push_limit=200
            f.save(f"{outdir}/{name}.flyer")
            json.dump(data,open(f"{outdir}/{name}.json",'w'))
            best.append((max(c),sum(c),name,c))
            print('KEEP',name,c,flush=True)
    print('STATS',worker,json.dumps(stats),flush=True)
if __name__=='__main__':
    worker=int(sys.argv[1]);nw=int(sys.argv[2]);s0=int(sys.argv[3]);s1=int(sys.argv[4]);thresh=int(sys.argv[5]);out=sys.argv[6]
    layouts=json.loads(sys.argv[7])
    run(worker,nw,layouts,range(s0,s1),thresh,out)
