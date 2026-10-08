import six,search,json,itertools,subprocess,collections
best=json.loads((search.OUT.parent/'contacts/compact/six_bank.json').read_text())['best']
records=json.loads((search.OUT/'quick_six/results.json').read_text())['records']
placements=[r['centers'] for r in records if r['failure'][0]=='route']
rots=[r for r,m in best['orientations']];refs=[-1 if m else 1 for r,m in best['orientations']]
out=search.OUT/'quick_ports';out.mkdir(exist_ok=True);stats=collections.Counter();log=[]
cases=[(six.OWN,six.PREVIOUS)]
for b in [(-1,1),(-2,0)]:
 for c in [(1,1),(-1,1)]:
  for pc in [(0,2),(1,1),(-1,1)]:
   if pc==c:continue
   own=((1,1),b,c,(1,1));previous=((2,0),(-2,0) if b==(-1,1) else (-1,1),pc,(2,0))
   cases.append((own,previous))
for ci,(six.OWN,six.PREVIOUS) in enumerate(cases):
 for pi,centers in enumerate(placements):
  for rs in range(4):
   ans,why=six.build(rs,(centers,rots,refs),cap=39)
   stats['routed' if ans else why[0]]+=1
   rec=dict(case=ci,placement=pi,route_seed=rs,failure=why,own=six.OWN,previous=six.PREVIOUS)
   if ans:
    f,m=ans;f.push_limit=49;p=out/f'c{ci}_p{pi}_r{rs}_pl49.flyer';f.save(p);rec['metadata']=m
    run=subprocess.run([str(search.ROOT/'target/release/fastflyer-research.exe'),'audit',str(p),'120','12'],capture_output=True,text=True)
    rec['audit']=run.stdout+run.stderr;print(rec['audit'],flush=True)
    log.append(rec);(out/'results.json').write_text(json.dumps(dict(stats=stats,records=log),indent=2))
    if 'distance=40 ' in rec['audit'] and 'movement_failures=0' in rec['audit'] and 'conservation_mismatch_ticks=0' in rec['audit']:
     print('WORKING',p,flush=True);raise SystemExit(0)
   else:log.append(rec)
 print(ci,dict(stats),flush=True)
(out/'results.json').write_text(json.dumps(dict(stats=stats,records=log),indent=2))
