import six,search,json,random,subprocess,collections
best=json.loads((search.OUT.parent/'contacts/compact/six_bank.json').read_text())['best']
out=search.OUT/'quick_six';out.mkdir(exist_ok=True)
stats=collections.Counter();records=[]
for seed in range(160):
 rng=random.Random(seed);centers=[list(p) for p in best['centers']]
 # Local repairs of saved mandatory placement, including corrected observer sites.
 for j in rng.sample(range(6),1+seed%3):
  centers[j][0]+=rng.choice((-2,-1,0,1,2));centers[j][1]+=rng.choice((-2,-1,0,1,2))
 placement=(centers,[r for r,m in best['orientations']],[-1 if m else 1 for r,m in best['orientations']])
 ans,why=six.build(seed,placement,cap=38)
 stats['routed' if ans else why[0]]+=1
 rec=dict(seed=seed,failure=why,centers=centers)
 if ans:
  f,m=ans;f.push_limit=49;p=out/f's{seed}_pl49.flyer';f.save(p);rec['metadata']=m
  run=subprocess.run([str(search.ROOT/'target/release/fastflyer-research.exe'),'audit',str(p),'120','12'],capture_output=True,text=True)
  rec['audit']=run.stdout+run.stderr;print(rec['audit'],flush=True)
  records.append(rec);(out/'results.json').write_text(json.dumps(dict(stats=stats,records=records),indent=2))
  if 'distance=40 ' in rec['audit'] and 'movement_failures=0' in rec['audit'] and 'conservation_mismatch_ticks=0' in rec['audit']:
   print('WORKING',p,flush=True);break
 else:records.append(rec)
 if seed%20==0:print(seed,dict(stats),flush=True)
(out/'results.json').write_text(json.dumps(dict(stats=stats,records=records),indent=2))
