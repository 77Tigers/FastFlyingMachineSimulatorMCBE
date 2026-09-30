"""Shorten the largest pure-pull helper rails, retaining the selected ports."""
from pathlib import Path
import sys,json,random,heapq,subprocess,re,importlib.util
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Block
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
def main():
    source_path=HERE/'derived_pull3_compact.py';source=source_path.read_text();spec=importlib.util.spec_from_file_location('pullmodel',source_path);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    model.place=lambda i,j,spacing:((i%5)*2*spacing,(i//5)*4*spacing+j*spacing)
    m=next(m for m in json.loads((HERE/'pull3_compact_manifest.json').read_text())['candidates'] if m['file']=='paired_grid_s002.flyer');segments=[set(map(tuple,s)) for s in m['segments']];ps=m['pistons'];sources=m['sources']
    f=Flyer.load(HERE/'pull3_compact_candidates'/m['file']);stickyactual=[p for p,b in f._cells.items() if b.kind in model.K];raw=list(set.union(*segments));offset=tuple(min(p[a] for p in stickyactual)-min(p[a] for p in raw) for a in range(3))
    def unshift(p):return tuple(p[a]-offset[a] for a in range(3))
    f._cells={unshift(p):b for p,b in f._cells.items()};f._piston_blocks={unshift(p):tuple(unshift(q) for q in own) for p,own in f._piston_blocks.items()};f.push_limit=1000
    snippet=source[source.index(' fixed=[]'):source.index(' if any(not legal')];helper='def make_legal(ss,ps,sources):\n'+snippet+' return legal\n';(HERE/'reroute_pull3_legal.py').write_text(helper);ns=model.__dict__.copy();exec(compile(helper,str(HERE/'reroute_pull3_legal.py'),'exec'),ns)
    original_ports=[];route_line=next(n for n,line in enumerate(source.splitlines(),1) if 'for i in rng.sample(range(N),N)' in line)
    class Captured(Exception):pass
    def capture(frame,event,arg):
        if frame.f_code is model.build.__code__ and event=='line' and frame.f_lineno==route_line:
            original_ports.extend(set(s) for s in frame.f_locals['ss']);raise Captured()
        return capture
    sys.settrace(capture)
    try:model.build(2,3)
    except Captured:pass
    finally:sys.settrace(None)
    assert len(original_ports)==10
    assert all(original_ports[i]<=segments[i] for i in range(10)), 'port regeneration differs from saved witness'
    out=HERE/'reroute_pull3';out.mkdir(exist_ok=True);records=[];current_max=106
    for i in sorted(range(10),key=lambda i:-len(segments[i]))[:4]:
        for seed in range(8):
            rng=random.Random(100*i+seed);candidate=original_ports[i]&segments[i];legal=ns['make_legal'](segments,ps,sources)
            if not all(legal(p,i) for p in candidate):continue
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
                        if not(-5<=q[0]<=6 and -4<=q[1]<=31 and -4<=q[2]<=22):continue
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
            probe=out/'probe.flyer';f.save(probe);r=subprocess.run([str(RUNNER),'verify',str(probe),'240','--period','10','--advance','3'],capture_output=True,text=True);max_load=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);accepted=r.returncode==0 and max_load<=current_max
            records.append(dict(body=i,seed=seed,old_count=len(old),new_count=len(candidate),ports=len(original_ports[i]),accepted=accepted,result=r.stdout.strip()))
            if accepted:segments[i]=candidate;current_max=max_load;f.save(out/'best.flyer');print('accepted',i,seed,len(old),len(candidate),max_load,flush=True)
            else:
                for p in candidate:f._cells.pop(p)
                for p in old:f._cells[p]=Block(model.K[i])
            pending=out/'results.pending.json';pending.write_text(json.dumps(records,indent=2));pending.replace(out/'results.json')
        print('body complete',i,len(segments[i]),flush=True)
    f.save(out/'best.flyer');(out/'geometry.json').write_text(json.dumps(dict(segments=[sorted(s) for s in segments],pistons=ps,sources=sources),indent=2))
    r=subprocess.run([str(RUNNER),'verify',str(out/'best.flyer'),'10000','--period','10','--advance','3'],capture_output=True,text=True);(out/'diagnostic_full.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
    if r.returncode==0:
        f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);f.save(HERE/f'pull3_reroute_pl{f.push_limit}.flyer')
if __name__=='__main__':main()
