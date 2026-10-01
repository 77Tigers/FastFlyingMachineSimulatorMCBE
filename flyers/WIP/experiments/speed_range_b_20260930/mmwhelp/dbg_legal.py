import model,re,sys,collections
OV=model.OV
src=(OV/'mixed_role_ring_legal.py').read_text().replace('range(5)','range(6)').replace('%5','%6')
i0=src.index(' @functools.lru_cache(None)\n def legal')
head,body=src[:i0],src[i0:]
cnt=[0]
def rep(mo):
    cnt[0]+=1
    return 'return _dbg(%d)'%cnt[0]
body2=re.sub(r'return False',rep,body)
LAST={}
def _dbg(n):
    LAST['n']=n; return False
ns2=model.m.__dict__.copy(); ns2['_dbg']=_dbg
exec(compile(head+body2,'dbg','exec'),ns2)
src_g=open('gen6.py').read().replace("ns['make_legal']","NS2['make_legal']")
src_g=src_g.replace("                if not cands:\n                    return None, 'templatecell'","                if not cands:\n                    for d in m.D[2:]:\n                        p=(cx, pp[1] + d[1], pp[2] + d[2]); legal.cache_clear(); LAST.clear(); r=legal(p,X); CL[LAST.get('n')]+=1\n                    return None, 'templatecell'")
CL=collections.Counter()
g2=dict(NS2=ns2,CL=CL,LAST=LAST)
exec(compile(src_g,'g6b','exec'),g2)
for seed in range(40):
    g2['build2'](seed,[(0,0),(0,4),(4,2)],share_rs=True,share_obs='diag',lane_perm='rand',template=True)
print(CL)
lines=body2.split('\n')
for k,l in enumerate(lines):
    mo=re.search(r'_dbg\((\d+)\)',l)
    if mo: print(mo.group(1),l.strip()[:160])
