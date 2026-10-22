"""Snapshot-based phase+1 observer/pull calibration: G0 wmmmw, T0 mwwmm.

Extract the accepted fixture before oldslot4, including extended arm and
observer bits. Only T0 pull0 is natural; all other moves are supplied. This
timing component does not establish a loaded power replacement or flyer.
"""
import os as _research_os
import argparse,hashlib,json,subprocess
from pathlib import Path
from assemble import Flyer
from fastflyer import Block,Kind

ROOT=Path(__file__).resolve().parents[4]
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('base',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    trace=a.base/'trace_failure_0_0_7.jsonl';rows=[json.loads(s) for s in trace.read_text(encoding='utf-8').splitlines()]
    state={tuple(c[:3]):c[3] for c in rows[0]['trace']['initial']}
    ports={'G0_carrier':(14,0,11),'T0_target':(13,1,11)}
    for row in rows:
        if row['tick']>=8:break
        for step in row['trace']['steps']:
            m=step.get('movement') or {};src=list(map(tuple,m.get('sources',[])));dst=list(map(tuple,m.get('destinations',[])))
            if dst and not m.get('failure'):
                assert len(src)==len(dst)
                ports={name:dst[src.index(p)] if p in src else p for name,p in ports.items()}
            for x,y,z,b in step['changes']:
                if b is None:state.pop((x,y,z),None)
                else:state[x,y,z]=b
    f=Flyer(push_limit=12)
    for p,b in state.items():f.set(p,Block.decode(b))
    assert state[(17,1,11)]&15==int(Kind.PISTON) and state[(16,1,11)]&15==int(Kind.PISTON_ARM)
    f.set_piston_blocks((17,1,11),[(16,1,11)])
    f.save(a.out/'problem.flyer');assert Flyer.load(a.out/'problem.flyer')._cells==f._cells
    spec=[('G0_carrier','wmmmw',[None,'supplied','supplied','supplied',None]),
          ('T0_target','mwwmm',['internal',None,None,'supplied','supplied'])]
    drive=[]
    for name,word,provenance in spec:
        for cycle in range(3):
            for slot,source in enumerate(provenance):
                if source=='supplied':drive.append((10*cycle+2*slot,ports[name][0]+3*cycle+word[:slot].count('m'),*ports[name][1:],12))
    (a.out/'drive.txt').write_text(''.join(' '.join(map(str,row))+'\n' for row in sorted(drive)),encoding='utf-8')
    c={'version':1,'name':a.out.name,'flyer':'problem.flyer','period_ticks':10,'advance':3,'cycles':3,'recurrence':'bounded',
       'ports':[{'name':name,'at':ports[name],'role':'input','word':word,'provenance':provenance} for name,word,provenance in spec],
       'required_cells':[],'boundary_envelope':{'min':[10,0,9],'max':[24,5,13]},'prescribed_script':'drive.txt'}
    for order in ['before_natural','after_natural','interleaved']:dump(a.out/f'{order}.json',{**c,'prescribed_order':order})
    dump(a.out/'preparation.json',{'scope':__doc__,'phase_snapshot':'before oldtick8/slot4','state':[[*p,b] for p,b in sorted(state.items())],
         'ports':ports,'source_trace_sha256':hashlib.sha256(trace.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    (a.out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
    subprocess.run([str(ROOT/('target/release/contract-verify' + ('.exe' if _research_os.name == 'nt' else ''))),str(a.out/'before_natural.json'),str(a.out/'native.json'),'30','2'],cwd=ROOT,capture_output=True,check=True)
    print((a.out/'native.json').read_text(encoding='utf-8'))


if __name__=='__main__':main()
