"""mmwmmw module placement search, preserving the six-slot lifecycle.

Reference-derived contacts with explicit alternative transverse embeddings;
no simulator edits. Copies the old generator into this experiment so its
diagnostic writes cannot overwrite prior evidence. Every result needs Rust.
"""
from pathlib import Path
import sys,subprocess,json,csv,collections,hashlib,time
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'flyers/WIP/experiments/bin/research_runner.exe'
ORIGINAL=ROOT/'flyers/WIP/experiments/astra_mmwm_20260928/search.py'

def checkpoint(data):
    target=HERE/'mmw_layout_manifest.json';pending=HERE/'mmw_checkpoint.pending.json'
    for retry in range(5):
        try:
            pending.write_text(json.dumps(data,indent=2),encoding='utf-8')
            pending.replace(target)
            return
        except OSError:
            if retry==4:raise
            time.sleep(.25*(retry+1))

def main():
    source=ORIGINAL.read_text(encoding='utf-8').split("if __name__=='__main__':")[0]
    source=source.replace('def build(seed,spacing=5,cap=140):','def build(seed,spacing=5,cap=140,centers=None):')
    source=source.replace('cy=(j%3)*spacing;cz=(j//3)*spacing','cy,cz=centers[j] if centers is not None else ((j%3)*spacing,(j//3)*spacing)')
    source=source.replace('-4<=q[1]<=2*spacing+4 and -4<=q[2]<=spacing+4','min(c[0] for c in centers)-4<=q[1]<=max(c[0] for c in centers)+4 and min(c[1] for c in centers)-4<=q[2]<=max(c[1] for c in centers)+4')
    (HERE/'derived_mmw.py').write_text(source,encoding='utf-8')
    ns={'__file__':str(HERE/'derived_mmw.py')};exec(compile(source,str(HERE/'derived_mmw.py'),'exec'),ns)
    layouts=[
       ('grid4',[(j%3*4,j//3*4) for j in range(6)]),
       ('stagger3',[(0,0),(3,0),(6,0),(1,3),(4,3),(7,3)]),
       ('stagger4',[(0,0),(3,0),(6,0),(1,4),(4,4),(7,4)]),
       ('hex3',[(0,0),(3,0),(5,3),(3,6),(0,6),(-2,3)]),
       ('hex4',[(0,0),(4,0),(6,3),(4,6),(0,6),(-2,3)]),
    ]
    manifest=[];stats=collections.Counter();out=HERE/'mmw_layouts';out.mkdir(exist_ok=True)
    for name,centers in layouts:
        for seed in range(32):
            ans,reason=ns['build'](seed,spacing=4,cap=65,centers=centers)
            if ans is None:stats[name+':'+reason]+=1
            else:
                f,m=ans;path=out/f'{name}_s{seed:03}.flyer';f.save(path);m.update(layout=name,centers=centers,path=path.name)
                manifest.append(m);stats[name+':routed']+=1
            checkpoint(dict(original_sha256=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),stats=stats,candidates=manifest,next_seed=seed+1,current_layout=name))
        print(name,dict(stats),flush=True)
    csvpath=HERE/'mmw_layout_screen.csv'
    p=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(csvpath)],capture_output=True,text=True)
    (HERE/'mmw_layout_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
    rows=list(csv.DictReader(csvpath.open()));good=[r for r in rows if r['clean']=='true' and r['distance']=='80']
    good.sort(key=lambda r:(int(r['max_successful_action']),int(r['end_blocks'])))
    for row in good[:3]:
        from fastflyer import Flyer
        f=Flyer.load(row['file']);f.push_limit=int(row['max_successful_action']);path=HERE/f"mmw_{Path(row['file']).stem}_pl{f.push_limit}.flyer";f.save(path)
        p=subprocess.run([str(RUNNER),'verify',str(path),'10000','--period','12','--advance','4'],capture_output=True,text=True)
        path.with_suffix('.verify.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)

if __name__=='__main__':main()
