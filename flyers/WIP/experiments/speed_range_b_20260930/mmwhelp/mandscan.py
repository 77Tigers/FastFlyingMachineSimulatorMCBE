import sys,itertools,collections,time
import gen4
# reuse build2 up to mandatory check by calling with cost_cap tiny? Instead replicate: call build2 and read reason 'mandatory'
def mand_ok(centers,fronts_t,rots):
    # call build with seed and fixed fronts/rots but stop early: use a tiny cap so routing fails quickly; we only care whether reason=='mandatory'
    ans,reason=gen4.build2(0,centers,front_choice=fronts_t,rots=rots,share_rs=True,cost_cap=9)
    return reason!='mandatory' and reason!='source_overlap' and reason!='cross_power' and (reason is None or reason in ('pickup','route','cap'))
lay=eval(sys.argv[1]); 
c=[(0,0),(0,lay[0]),(lay[1],lay[2])]
ok=0;tot=0;t0=time.time()
st=collections.Counter()
for fr in itertools.product((-1,0,1),repeat=3):
    for rt in itertools.product(range(4),repeat=3):
        ans,reason=gen4.build2(0,c,front_choice=fr,rots=rt,share_rs=True,cost_cap=1)
        st[reason]+=1
print(lay,dict(st),'%.0fs'%(time.time()-t0))
