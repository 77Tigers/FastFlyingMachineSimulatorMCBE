"""Move T1 normal17,2,12 on X1 at slot0 with a compensating glue removal.

Keep the selected joint T0/G0/H0 design and all other hardware fixed. Each
encoded12 candidate must pass native80x3 before independent/long verification.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind

ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    prep=json.loads((a.base/'preparation.json').read_text(encoding='utf-8'));delta=prep.get('normalization_delta',[0,0,0])
    tr=lambda p:tuple(x+y for x,y in zip(p,delta))
    results=[]
    # First is an uncompensated negative control; final two removals are
    # connected controls that are expected to disrupt other carrier duties.
    for removed in [None,(18,4,11),(18,4,10),(16,4,12),(17,3,10)]:
        out=a.out/f'case{len(results):03d}';out.mkdir()
        f=Flyer.load(a.base/'problem.flyer');added=tr((17,3,12))
        assert added not in f._cells
        f.set(added,Block(Kind.HONEY))
        if removed is not None:
            assert f._cells[tr(removed)].kind==Kind.HONEY
            f._cells.pop(tr(removed))
        f.save(out/'problem.flyer');assert Flyer.load(out/'problem.flyer')._cells==f._cells
        shutil.copyfile(a.base/'drive.txt',out/'drive.txt')
        for order in ['before_natural','after_natural','interleaved']:
            c=json.loads((a.base/f'{order}.json').read_text(encoding='utf-8'));c['name']=out.name
            assert all(tuple(p['at']) in f._cells for p in c['ports'])
            (out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
        (out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),'add_original':[17,3,12],'remove_original':removed,'normalization_delta':delta,'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.base/'problem.flyer',Path(__file__)]}},indent=2)+'\n',encoding='utf-8')
        r=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(out/'before_natural.json'),str(out/'native.json'),'30','2'],cwd=ROOT,capture_output=True,text=True)
        assert (out/'native.json').exists(),r.stderr
        d=json.loads((out/'native.json').read_text(encoding='utf-8'));results.append({'case':str(out),'remove_original':removed,**d})
        print(json.dumps({'case':out.name,'removed':removed,'verified':d['verified'],'failure':d['failure']}),flush=True)
    (a.out/'report.json').write_text(json.dumps({'scope':__doc__,'cases':results},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
