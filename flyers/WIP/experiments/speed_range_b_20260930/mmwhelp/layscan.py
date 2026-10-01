import gen5,itertools,collections,sys,time
res={}
t0=time.time()
for a in (4,5,6):
  for b in range(1,7):
    for c in range(0,5):
        if b==0 and c==0: continue
        st=collections.Counter()
        for seed in range(25):
            ans,reason=gen5.build2(seed,[(0,0),(0,a),(b,c)],share_rs=True,share_obs='diag',lane_perm='rand',stop_after_mandatory=True)
            st['ok' if ans=='mand_ok' else reason]+=1
        res[(a,b,c)]=st['ok']
        print((a,b,c),st['ok'],dict(st),flush=True)
print('%.0fs'%(time.time()-t0))
