"""Independent240 then strict native240x10000 proof of a supplied column interface."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path)
    ap.add_argument('--phase',choices=('all','independent','long'),default='all')
    ap.add_argument('--long-seconds',type=int,default=600,help='Native long-proof wall-clock budget; incomplete samples are not acceptance')
    a=ap.parse_args();run=a.run.resolve()
    for order in ('before_natural','after_natural','interleaved'):
        dest=run/f'independent_{order}.json'
        if a.phase!='long':
            if dest.exists(): raise RuntimeError(f'refusing existing proof {dest}')
            subprocess.run([sys.executable,str(ROOT/'tools/extension_contract.py'),str(run/f'{order}.json'),
                            '--samples','--out',str(dest)],check=True,cwd=ROOT)
        data=json.loads(dest.read_text(encoding='utf-8'))
        assert data['passed'] and len(data['cases'])==80 and all(c['passed'] for c in data['cases'])
    proof_files=['problem.flyer','drive.txt']+[f'{o}.json' for o in ('before_natural','after_natural','interleaved')]
    identity={n:hashlib.sha256((run/n).read_bytes()).hexdigest() for n in proof_files}
    identity_file=run/'independent_inputs.json'
    if a.phase=='long':assert json.loads(identity_file.read_text(encoding='utf-8'))==identity,'independent proof inputs changed'
    else:identity_file.write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
    if a.phase=='independent':
        print('Independent240 complete; long proof deliberately not started.',flush=True)
        return
    contract=json.loads((run/'before_natural.json').read_text(encoding='utf-8'))
    contract['cycles']=1000
    contract['prescribed_script']='long_drive.txt'
    rows=[]
    for p in contract['ports']:
        for slot,source in enumerate(p['provenance']):
            if source!='supplied': continue
            prefix=p['word'][:slot].count('m')
            for cycle in range(1000):
                rows.append((cycle*10+slot*2,p['at'][0]+cycle*3+prefix,p['at'][1],p['at'][2],12))
    (run/'long_drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(rows)),encoding='utf-8')
    (run/'long_contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    subprocess.run([str(ROOT/'target/release/contract-verify.exe'),str(run/'long_contract.json'),
                    str(run/'long_result.json'),str(a.long_seconds),'4'],check=True,cwd=ROOT)
    result=json.loads((run/'long_result.json').read_text(encoding='utf-8'))
    assert result['verified'] and result['passed']==80 and result['orders_per_sample']==3
    assert result['ticks_per_order']==10000 and result['encoded_limit']==12 and result['max_action']<=12
    print('Interface proof complete: independent240 + native240x10000; supplied strokes remain explicit.',flush=True)


if __name__=='__main__':main()
