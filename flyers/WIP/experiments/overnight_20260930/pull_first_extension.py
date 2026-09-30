"""Test a separate front body's pull-first/two-push drive with glazed power."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'mixed_extension.py').read_text()
s=s.replace("helper='def make_legal(ss,ps,sources):\\n'+snippet+' return legal\\n'","""snippet=snippet.replace('  w={}','  w={shift(p,DISP[owner][t]):Block(Kind.GLAZED_TERRACOTTA) for p,owner in GLAZED}')
    gate=''' for t in range(5):
  for pp,dp,f,target,sticky in ps:
   ext=(f-1)%5 if sticky else f
   if t==ext:continue
   base=shift(pp,dp[t])
   for gp,gowner in GLAZED:
    solid=shift(gp,DISP[gowner][t])
    if solid==shift(base,-1 if sticky else 1) or sum(abs(a-b) for a,b in zip(base,solid))!=1:continue
    for rp,owner,observer in sources:
     if observer and S[owner][(t-1)%5] and add(shift(rp,DISP[owner][t]),D[POWER_DIR])==solid:return None,'glazed_cross_power'
'''
    marker=' @functools.lru_cache(None)';snippet=snippet.replace(marker,gate+marker)
    helper='def make_legal(ss,ps,sources):\\n'+snippet+' return legal\\n'""")
a=s.index('            new=[]');b=s.index('            if not reason and any',a)
s=s[:a]+'''            ss[5].update(translate(p) for p in ((0,0,-1),(0,0,0),(0,0,1),(0,1,0),(0,1,1)))
            ss[3].add(translate((-1,0,0)))
            ss[4].update(translate(p) for p in ((2,1,-1),(-1,1,-1),(-1,2,-1)))
            ss[1].add(translate((2,2,0)))
            glazed=[(translate((0,1,-1)),4)];ns['GLAZED']=glazed
            new=[(translate((2,1,0)),[0,0,1,2,3],0,5,True),(translate((-1,0,1)),[0,1,1,1,2],1,5,False),(translate((-1,0,-1)),[0,1,2,2,2],2,5,False)]
            ps.extend(new);sources.extend([(translate((3,2,0)),1,False),(translate((-1,1,1)),5,True),(translate((0,2,-1)),4,True)])
            legal=ns['make_legal'](ss,ps,sources)
            if not callable(legal):stats[legal[1]]+=1;continue
            reason=None
'''+s[b:]
s=s.replace("f=Flyer(rng_state=5,push_limit=1000)","f=Flyer(rng_state=5,push_limit=1000)\n                for p,owner in glazed:f._cells[p]=Block(Kind.GLAZED_TERRACOTTA)")
s=s.replace('pistons=ps,sources=sources,counts=','pistons=ps,sources=sources,glazed=glazed,counts=')
s=s.replace('mixed_extension_candidates','pull_first_extension_candidates').replace('mixed_extension_manifest','pull_first_extension_manifest').replace('mixed_extension_screen','pull_first_extension_screen').replace('mixed_extension_legal.py','pull_first_extension_legal.py')
import sys
if '--movingcontacts' in sys.argv:
 s=s.replace("snippet=snippet.replace('  w={}'", "snippet=snippet.replace('K[i]==K[j] and any','K[i]==K[j] and not (delta and S[i][t] and S[j][t]) and any')\n    snippet=snippet.replace('  w={}'")
 s=s.replace('pull_first_extension_candidates','pull_first_movingcontacts_candidates').replace('pull_first_extension_manifest','pull_first_movingcontacts_manifest').replace('pull_first_extension_screen','pull_first_movingcontacts_screen').replace('pull_first_extension_legal.py','pull_first_movingcontacts_legal.py')
if '--diagnose' in sys.argv:
 s=s.replace('((0,12,0),(0,15,0),(0,0,15))','((0,0,15),)').replace('range(8)','range(1)')
 s=s.replace("            if not reason and any(not legal(p,i) for i,s in enumerate(ss) for p in s):reason='mandatory'",'''            witnesses=[]
            def capture(frame,event,arg):
                if frame.f_code.co_name=='legal' and event=='return' and arg is False:
                    witnesses.append(dict(line=frame.f_lineno,locals={k:v for k,v in frame.f_locals.items() if k in ('p','i','t','q','r','j','delta','pp','f','target','rp','owner','observer')}))
                return capture
            legal.cache_clear();sys.settrace(capture)
            bad=[(i,p) for i,body in enumerate(ss) for p in body if not legal(p,i)]
            sys.settrace(None)
            if bad:
                reason='mandatory';(HERE/'pull_first_mandatory_witness.json').write_text(json.dumps(dict(bad=bad,witnesses=witnesses),indent=2))
''')
 s=s.replace('pull_first_extension_candidates','pull_first_extension_diagnostic_candidates').replace('pull_first_extension_manifest','pull_first_extension_diagnostic_manifest').replace('pull_first_extension_screen','pull_first_extension_diagnostic_screen')
target=h/'derived_pull_first_extension.py';target.write_text(s)
exec(compile(s,str(target),'exec'),dict(__file__=str(target),__name__='__main__'))
