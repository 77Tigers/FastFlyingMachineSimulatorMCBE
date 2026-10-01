import json,glob,est,model,csv,os,sys
scr=sys.argv[1] if len(sys.argv)>1 else 'screen1.csv'
def base(p): return os.path.basename(p.replace(chr(92),'/'))
rows={base(r['file']):int(r['max_successful_action']) for r in csv.DictReader(open(scr))}
out=[]
for fn in sorted(glob.glob('cand/*.json')):
    d=json.load(open(fn))
    name=base(fn).replace('.json','.flyer')
    if name not in rows: continue
    ss=[set(map(tuple,s)) for s in d['segments']];ps=[(tuple(p),dp,f,t,st) for p,dp,f,t,st in d['pistons']];src=[(tuple(p),o,ob,dr) for p,o,ob,dr in d['sources']]
    w,_=est.est_load(ss,ps,src)
    out.append((rows[name],w,name,d['counts']))
out.sort()
for r in out[:25]: print(r)
