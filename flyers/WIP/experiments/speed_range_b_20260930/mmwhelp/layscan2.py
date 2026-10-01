import gen5,collections,sys,time
fr=eval(sys.argv[1]); 
for lay in eval(sys.argv[2]):
    (p,q),(b,c)=lay
    st=collections.Counter()
    for seed in range(30):
        ans,reason=gen5.build2(seed,[(0,0),(p,q),(b,c)],share_rs=True,share_obs='diag',lane_perm='rand',fronts=fr,stop_after_mandatory=True)
        st['ok' if ans=='mand_ok' else reason]+=1
    print(lay,st['ok'],dict(st),flush=True)
