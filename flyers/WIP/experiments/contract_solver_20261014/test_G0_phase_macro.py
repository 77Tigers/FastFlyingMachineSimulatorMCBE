"""Bounded native tests of a phase-shifted G0/H0 macro with T0 glue rerouting.

Keep T0 own push targets, source connection and X0 puller support. Replace
its two optional upper glue cells with connected pickups, keeping<=6 glue.
Macro states/arms/owners come from a real validated phase snapshot. New
G0/H0 moves and T0 pull0 are natural; only X0 pushes0/1 remain supplied.
This constructor/screen does not itself imply complete-flyer verification.
"""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind
ROOT=Path(__file__).resolve().parents[4]
D=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]


def adj(p):return [tuple(x+d for x,d in zip(p,v)) for v in D]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('macro',type=Path);ap.add_argument('out',type=Path)
    ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--max-tests',type=int,default=12)
    ap.add_argument('--seven-route',action='store_true',help='Test macro0 with a specific connected seven-glue detour around its source-corner piston')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    f=Flyer.load(a.base/'problem.flyer');macro=json.loads(a.macro.read_text(encoding='utf-8'))
    old={(17,1,12),(17,1,13),(17,2,13),(17,3,13),(17,0,13),(18,3,13)}
    core={(17,1,12),(17,1,13),(17,2,13),(17,0,13)};fixed=set(f._cells)-old
    results=[];generated=0;complete=True
    for mi,m in enumerate(macro['results']):
      if a.seven_route and mi!=0:continue
      cells={tuple(c[:3]):c[3] for c in m['macro_cells']}
      if cells.keys()&fixed:continue
      shapes={frozenset(core)};pool=set(shapes)
      for _ in range(2):
        shapes={s|{p} for s in shapes for q in s for p in adj(q)
                if p not in s and p not in fixed and p not in cells and
                16<=p[0]<=20 and -1<=p[1]<=5 and 10<=p[2]<=15}
        pool.update(shapes)
      if a.seven_route:
        pool={frozenset({(17,1,12),(17,2,13),(17,0,13),(16,1,12),(16,2,12),(16,2,13),(17,0,12)})}
      for shape in sorted(pool,key=lambda s:(len(s),sorted(s))):
       if set(cells)&shape:continue
       if tuple(m['target']) not in shape:continue
       if not all(any(g in shape for g in adj(tuple(p))) for p in m['G0_normals_at_initial']):continue
       for flip in [False,True]:
        generated+=1
        if time.monotonic()-start>=a.seconds or len(results)>=a.max_tests:complete=False;break
        out=a.out/f'case{len(results):03d}';out.mkdir()
        ff=Flyer.load(a.base/'problem.flyer')
        for p in old:ff._cells.pop(p)
        for p in shape:ff.set(p,Block(Kind.HONEY))
        assert not set(cells)&set(ff._cells)
        for p,value in cells.items():
            b=Block.decode(value)
            if flip and b.kind in (Kind.SLIME,Kind.HONEY):b=Block(Kind.HONEY if b.kind==Kind.SLIME else Kind.SLIME)
            ff.set(p,b)
        owned={}
        for owner,block in m['macro_owners']:
            owned.setdefault(tuple(owner),[]).append(tuple(block))
        for owner,blocks in owned.items():ff.set_piston_blocks(owner,blocks)
        ff.save(out/'problem.flyer');assert Flyer.load(out/'problem.flyer')._cells==ff._cells
        c=json.loads((a.base/'before_natural.json').read_text(encoding='utf-8'));t=next(p for p in c['ports'] if p['name']=='T0')
        remove={(10*cy,t['at'][0]+3*cy,t['at'][1],t['at'][2]) for cy in range(3)}
        rows=[tuple(map(int,s.split())) for s in (a.base/'drive.txt').read_text(encoding='utf-8').splitlines()]
        assert sum(row[:4] in remove for row in rows)==3
        (out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows if row[:4] not in remove),encoding='utf-8')
        for order in ('before_natural','after_natural','interleaved'):
            c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=f'G0_macro_{mi}_{flip}'
            next(p for p in c['ports'] if p['name']=='T0')['provenance'][0]='internal'
            # Identify macro glue representatives by the original unflipped kind.
            for name,kind,word in [('G0',2,'wmmmw'),('H0',1,'mmwwm')]:
                at=next(p for p,v in cells.items() if v&15==kind)
                c['ports'].append({'name':name,'at':at,'role':'input','word':word,
                                   'provenance':['internal' if x=='m' else None for x in word]})
            for axis in range(3):
                c['boundary_envelope']['min'][axis]=min(c['boundary_envelope']['min'][axis],min(p[axis] for p in ff._cells))
                c['boundary_envelope']['max'][axis]=max(c['boundary_envelope']['max'][axis],max(p[axis] for p in ff._cells))
            (out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        prep={'scope':__doc__,'base':str(a.base),'macro_index':mi,'flip_materials':flip,'T0_glue':sorted(shape),
              'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',a.macro,Path(__file__)]}}
        (out/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
        run=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,capture_output=True,text=True)
        assert (out/'native.json').exists(),run.stderr
        result=json.loads((out/'native.json').read_text(encoding='utf-8'))
        results.append({'case':str(out),'macro_index':mi,'flip':flip,'T0_glue':sorted(shape),**result})
        print(json.dumps({'case':len(results)-1,'verified':result['verified'],'failure':result['failure']}),flush=True)
        if result['verified']:complete=False;break
       if not complete:break
      if not complete:break
    report={'scope':__doc__,'complete':complete,'generated':generated,'results':results,'elapsed_seconds':time.monotonic()-start}
    (a.out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
