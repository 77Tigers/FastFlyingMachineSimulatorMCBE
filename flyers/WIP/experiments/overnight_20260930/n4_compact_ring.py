"""Test closer twelve-body normal rings; full-copy modularity remains unproved."""
from pathlib import Path
import sys,math,json,collections,csv,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe'
spec=importlib.util.spec_from_file_location('n4',HERE.parent/'sol_reference_20260928/derived_generator.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def main():
    out=HERE/'n4_compact_candidates';out.mkdir(exist_ok=True);stats=collections.Counter();manifest=[]
    for spacing in (3.2,3.5,4.0):
        for angle in (0,math.pi/12):
            radius=spacing/(2*math.sin(math.pi/12));centers=[(round(radius*math.cos(2*math.pi*i/12+angle)),round(radius*math.sin(2*math.pi*i/12+angle))) for i in range(12)]
            for seed in range(8):
                ans=mod.make(4,centers,seed,100)
                if ans is None:stats['route']+=1
                else:
                    f,counts,_=ans
                    if sum(b.kind==Kind.PISTON for b in f._cells.values())!=48:stats['lost_initial_member']+=1
                    else:
                        name=f'd{spacing}_a{int(angle>0)}_s{seed:03}';f.save(out/(name+'.flyer'));manifest.append(dict(file=name+'.flyer',spacing=spacing,angle=angle,seed=seed,centers=centers,counts=counts));stats['routed']+=1
                pending=HERE/'n4_compact_manifest.pending.json';pending.write_text(json.dumps(dict(stats=stats,candidates=manifest,current_spacing=spacing,current_angle=angle,next_seed=seed+1),indent=2));pending.replace(HERE/'n4_compact_manifest.json')
                print(spacing,angle,seed,dict(stats),flush=True)
    screen=HERE/'n4_compact_screen.csv';r=subprocess.run([str(RUNNER),'screen',str(out),'240','--out',str(screen)],capture_output=True,text=True);(HERE/'n4_compact_screen.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
    rows=[r for r in csv.DictReader(screen.open()) if r['clean']=='true' and r['distance']=='80'];rows.sort(key=lambda r:(int(r['max_successful_action']),int(r['end_blocks'])))
    for row in rows[:3]:
        f=Flyer.load(row['file']);f.push_limit=int(row['max_successful_action']);path=HERE/f'n4_compact_{Path(row["file"]).stem}_pl{f.push_limit}.flyer';f.save(path)
        r=subprocess.run([str(RUNNER),'verify',str(path),'10000','--period','12','--advance','4'],capture_output=True,text=True);path.with_suffix('.verify.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True)
if __name__=='__main__':main()
