"""Replace connecting rails while retaining every existing hardware contact."""
from pathlib import Path
import sys,json,random,heapq,subprocess,re
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block
import derived_mmw as model
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'
def main():
    g=json.loads((HERE/'trim_mmw/geometry.json').read_text());segments=[set(map(tuple,s)) for s in g['segments']];ps=g['pistons'];reds=g['sources']
    source=(HERE/'derived_mmw.py').read_text();snippet=source[source.index(' fixed=[]'):source.index(' if any(not legal')]
    helper='def make_legal(ss,ps,reds):\n'+snippet+' return legal\n'
    (HERE/'reroute_mmw_legal.py').write_text(helper);ns=model.__dict__.copy();exec(compile(helper,str(HERE/'reroute_mmw_legal.py'),'exec'),ns)
    f,_=model.build(14,spacing=4,cap=65,centers=[(0,0),(4,0),(6,3),(4,6),(0,6),(-2,3)])[0]
    oldsticky={p for p,b in f._cells.items() if b.kind in model.K}
    for p in oldsticky:f._cells.pop(p)
    for i,s in enumerate(segments):
        for p in s:f._cells[p]=Block(model.K[i])
    f.push_limit=57;assert f.content_hash()==Flyer.load(HERE/'mmw_hex_trim_pl57.flyer').content_hash();f.push_limit=1000
    # Preserve the selected contact cover before the original connecting
    # rails were routed. Merely being near hardware is not a required port.
    original_ports=[]
    route_line=next(n for n,line in enumerate(source.splitlines(),1) if 'for i in rng.sample(range(3),3)' in line)
    def capture(frame,event,arg):
        if frame.f_code is model.build.__code__ and event=='line' and frame.f_lineno==route_line and not original_ports:
            original_ports.extend(set(s) for s in frame.f_locals['ss'])
        return capture
    sys.settrace(capture)
    try:model.build(14,spacing=4,cap=65,centers=[(0,0),(4,0),(6,3),(4,6),(0,6),(-2,3)])
    finally:sys.settrace(None)
    assert len(original_ports)==3
    def terminals(i):return original_ports[i]&segments[i]
    out=HERE/'reroute_mmw_ports';out.mkdir(exist_ok=True);records=[];current_max=57
    for round_index in range(2):
        changes=0
        for i in sorted(range(3),key=lambda i:-len(segments[i])):
            ports=terminals(i)
            for seed in range(16):
                rng=random.Random(200*round_index+20*i+seed);candidate=set(ports);legal=ns['make_legal'](segments,ps,reds)
                if not all(legal(p,i) for p in candidate):continue
                # Randomize the initial connected component, then use shortest
                # paths to the other components under full phase keepouts.
                start=rng.choice(sorted(candidate));reached={start};stack=[start]
                def flood():
                    while stack:
                        p=stack.pop()
                        for d in model.D:
                            q=model.add(p,d)
                            if q in candidate and q not in reached:reached.add(q);stack.append(q)
                flood();failed=False
                while reached!=candidate:
                    targets=candidate-reached;pq=[(0,rng.random(),p) for p in reached];heapq.heapify(pq);dist={p:0 for p in reached};prev={};end=None
                    while pq:
                        cost,_,p=heapq.heappop(pq)
                        if cost!=dist[p]:continue
                        if p in targets:end=p;break
                        if cost>len(segments[i])-len(candidate):continue
                        for d in rng.sample(model.D,6):
                            q=model.add(p,d)
                            if not(-5<=q[0]<=7 and -6<=q[1]<=10 and -4<=q[2]<=10):continue
                            if q not in candidate and not legal(q,i):continue
                            nc=cost+int(q not in candidate)
                            if nc<dist.get(q,10000):dist[q]=nc;prev[q]=p;heapq.heappush(pq,(nc,rng.random(),q))
                    if end is None:failed=True;break
                    path=[]
                    while end not in reached:path.append(end);end=prev[end]
                    candidate.update(path);stack.extend(path);reached.update(path);flood()
                if failed or len(candidate)>=len(segments[i]):continue
                old=segments[i]
                for p in old:f._cells.pop(p)
                for p in candidate:f._cells[p]=Block(model.K[i])
                probe=out/'probe.flyer';f.save(probe)
                r=subprocess.run([str(RUNNER),'verify',str(probe),'240','--period','12','--advance','4'],capture_output=True,text=True)
                max_load=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);accepted=r.returncode==0 and max_load<=current_max
                records.append(dict(round=round_index,body=i,seed=seed,old_count=len(old),new_count=len(candidate),ports=len(ports),accepted=accepted,result=r.stdout.strip()))
                if accepted:segments[i]=candidate;current_max=max_load;changes+=1;f.save(out/'best.flyer');print('accepted',i,seed,len(old),len(candidate),max_load,flush=True)
                else:
                    for p in candidate:f._cells.pop(p)
                    for p in old:f._cells[p]=Block(model.K[i])
                (out/'results.pending.json').write_text(json.dumps(records,indent=2));(out/'results.pending.json').replace(out/'results.json')
            print('body complete',round_index,i,len(segments[i]),flush=True)
        if not changes:break
    f.save(out/'best.flyer');(out/'geometry.json').write_text(json.dumps(dict(segments=[sorted(s) for s in segments],pistons=ps,sources=reds),indent=2))
    r=subprocess.run([str(RUNNER),'verify',str(out/'best.flyer'),'10000','--period','12','--advance','4'],capture_output=True,text=True)
    (out/'diagnostic_full.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
    f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);path=HERE/f'mmw_reroute_ports_pl{f.push_limit}.flyer';f.save(path)
    if f.push_limit<57:
        for name,args in [('verify',[str(path),'10000','--period','12','--advance','4']),('audit',[str(path),'10000','12']),('samples',[str(path),'--period','12','--advance','4','--out',str(path.with_suffix('.samples.csv'))])]:
            r=subprocess.run([str(RUNNER),name,*args],capture_output=True,text=True);path.with_suffix('.'+name+'.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
if __name__=='__main__':main()
