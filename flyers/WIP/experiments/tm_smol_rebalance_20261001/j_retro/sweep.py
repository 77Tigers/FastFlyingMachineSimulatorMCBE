import sys, itertools
sys.argv=['x']; sys.path.insert(0,'j_retro')
import planner2 as p
bodies, ev = p.parse('base.bodytrack.txt')
table = p.loads_table(bodies, ev)
glue=[b for b in bodies if bodies[b]['glue']]
res=[]
for P in glue:
  wp=bodies[P]['word']
  for V in glue:
    if V==P: continue
    wv=bodies[V]['word']
    for s in range(5):
      sm1=(s-1)%5
      if not (p.moves(wv,s) and not p.moves(wp,s) and not p.moves(wp,sm1)): continue
      cur=[m for m in table if m['victim']==V and m['s']==s]
      if not cur or cur[0]['kind']!='push': continue
      A=cur[0]['actor']
      try: r=p.plan2('base.bodytrack.txt',P,V,s,{A},newrb=True,rbconn=2,conn=2,vconn=2,box=4,quiet=True)
      except Exception as e: print('err',P,V,s,e); continue
      for x in r:
        for o in x['opts']:
          extra={P:1+len(o[-1])+0}
          extra[V]=extra.get(V,0)+len(x['vpath'])
          if o[0]=='new': extra[o[1]]=extra.get(o[1],0)+1+len(o[3])
          t=[dict(m) for m in table]
          for m in t:
            if m['victim']==V and m['s']==s: m['kind']='pull'; m['actor']=P
          n12,r12,mx=p.count12(bodies,t,extra,removed={A})
          res.append((mx>12,r12,n12,mx,P,V,s,A,x['c'],x['vpath'],o))
res.sort(key=lambda r:(r[3],r[1]))
print(len(res))
seen=set()
for r in res[:60]:
  print(r[1:9], r[8], len(r[9]), r[10][:2], len(r[10][3]) if r[10][0]=='new' else '', len(r[10][-1]))
