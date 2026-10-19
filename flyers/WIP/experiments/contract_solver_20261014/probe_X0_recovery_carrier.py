"""Test an explicitly supplied wwmmm rear pickup against natural X0 startup.

This adds no realized driver for the pickup body. It is a causal diagnostic,
not a complete flyer or an accepted component. Encoded push limit stays12.
"""
import argparse,json,hashlib,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind

ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    f=Flyer.load(a.base/'problem.flyer');at=(13,3,11)
    assert at not in f._cells and f.push_limit==12
    f.set(at,Block(Kind.HONEY));f.save(a.out/'problem.flyer')
    assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    rows=[(10*cycle+2*slot,at[0]+3*cycle+slot-2,at[1],at[2],12) for cycle in range(3) for slot in [2,3,4]]
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in rows),encoding='utf-8')
    for order in ['before_natural','after_natural','interleaved']:
        c=json.loads((a.base/'natural.json').read_text(encoding='utf-8'))
        c['name']='rear_pickup_timing_probe';c['prescribed_order']=order;c['prescribed_script']='drive.txt'
        c['ports'].append({'name':'rear_pickup','at':at,'role':'input','word':'wwmmm','provenance':[None,None,'supplied','supplied','supplied']})
        (a.out/f'{order}.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    (a.out/'preparation.json').write_text(json.dumps({'scope':__doc__,'base':str(a.base),'rear_pickup_original':[13,1,11],'rear_pickup_saved':at,'word':'wwmmm','input_sha256':hashlib.sha256((a.base/'problem.flyer').read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    proc=subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True,text=True)
    assert (a.out/'native.json').exists(),proc.stderr
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
