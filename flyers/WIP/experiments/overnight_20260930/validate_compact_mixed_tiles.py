"""Full literal-copy validation and separate driver/extension load ledgers."""
from pathlib import Path
import sys,json,csv,re,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
def _tb(n):
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from fastflyer.research import binary
    return binary(n)
HERE=Path(__file__).resolve().parent;RUNNER=ROOT/'target/release/fastflyer-research.exe';LEDGER=_tb('three-bps-loads')
def main():
    manifest=json.loads((HERE/'compact_mixed_tile_bridged/manifest.json').read_text());certified=[]
    for m in manifest['assemblies']:
        copies=m['copies'];source=HERE/f'compact_mixed_tile_bridged/copies{copies}.flyer';f=Flyer.load(source)
        assert all(m['connected']) and m['short_pass']
        r=subprocess.run([str(RUNNER),'verify',str(source),'10000','--period','10','--advance','3'],capture_output=True,text=True);source.with_suffix('.full_verify.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
        f.push_limit=int(re.search(r'max_successful_action=(\d+)',r.stdout)[1]);path=HERE/f'compact_mixed_chain_{copies}tiles_pl{f.push_limit}.flyer';f.save(path)
        r=subprocess.run([str(RUNNER),'verify',str(path),'10000','--period','10','--advance','3'],capture_output=True,text=True);path.with_suffix('.verify.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
        raw=[p for s in m['segments'] for p in s];actual=[p for p,b in f._cells.items() if b.kind in (Kind.SLIME,Kind.HONEY)];offset=[min(p[a] for p in actual)-min(p[a] for p in raw) for a in range(3)]
        bodies=path.with_suffix('.bodies.csv')
        with bodies.open('w',newline='') as stream:
            w=csv.writer(stream);w.writerow(['body','phase','x','y','z']);w.writerows((i,i if i<5 else 0,*[p[a]+offset[a] for a in range(3)]) for i,s in enumerate(m['segments']) for p in s)
        r=subprocess.run([str(LEDGER),str(path),str(bodies),'10000'],capture_output=True,text=True);path.with_suffix('.loads.csv').write_text(r.stdout);path.with_suffix('.loads.txt').write_text(r.stderr);print(r.stdout+r.stderr,flush=True);assert r.returncode==0
        rows=list(csv.DictReader(r.stdout.splitlines()));added=[r for r in rows if int(r['body'])>=5]
        assert len(added)==copies and all(r['sticky_cells']=='5' and r['successful_actions']=='3000' and int(r['max_load'])<=8 for r in added)
        certified.append(dict(copies=copies,file=path.name,limit=f.push_limit,full_verify=True,tagged_ledger=True,local_extension_max=8))
        (HERE/'compact_mixed_chain_validation.json').write_text(json.dumps(dict(tile_translation=manifest['translation'],assemblies=certified),indent=2))
    for m in (certified[0],certified[-1]):
        path=HERE/m['file'];r=subprocess.run([str(RUNNER),'samples',str(path),'--period','10','--advance','3','--out',str(path.with_suffix('.samples.csv'))],capture_output=True,text=True);path.with_suffix('.samples.txt').write_text(r.stdout+r.stderr);print(r.stdout,flush=True);assert r.returncode==0
if __name__=='__main__':main()
