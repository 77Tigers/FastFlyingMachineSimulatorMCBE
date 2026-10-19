"""Preserve strict short/independent/long proof of an explicitly supplied component."""
import argparse
import hashlib
import json
from pathlib import Path
from assemble import Flyer

HERE=Path(__file__).resolve().parent


def preserve(run,artifact):
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    short,long=read(run/'native.json'),read(run/'long_result.json')
    for report,ticks in ((short,30),(long,10000)):
        assert report['verified'] and report['passed']==report['total']==80
        assert report['orders_per_sample']==3 and report['ticks_per_order']==ticks
        assert report['encoded_limit']==12 and report['max_action']<=12 and report['failure'] is None
    orders=('before_natural','after_natural','interleaved')
    cases={o:read(run/f'independent_{o}.json') for o in orders}
    for report in cases.values():
        assert report['passed'] and len(report['cases'])==80
        assert all(c['passed'] and c['whole_assembly_max_action']<=12 for c in report['cases'])
    flyer=Flyer.load(run/'problem.flyer');assert flyer.push_limit==12
    contracts={o:read(run/f'{o}.json') for o in orders}
    for o,c in contracts.items():
        assert c['prescribed_order']==o and c['prescribed_script']=='drive.txt' and c['flyer']=='problem.flyer'
        assert all('provenance' in p for p in c['ports'])
    long_contract=read(run/'long_contract.json')
    assert long_contract['flyer']=='problem.flyer' and long_contract['ports']==contracts[orders[0]]['ports']
    assert long_contract['cycles']==1000 and long_contract['prescribed_script']=='long_drive.txt'
    files=['problem.flyer','drive.txt','long_drive.txt','preparation.json','native.json','long_result.json']
    data={
        'version':1,'name':run.name,
        'claim':'Verified supplied column interface; omitted actors and supplied third/neighbor strokes remain explicit; not a complete natural flyer',
        'flyer_parameters':{k:getattr(flyer,k) for k in ('phase_x','phase_z','rng_state','push_limit')},
        'cells':[[*p,b.encode()] for p,b in sorted(flyer._cells.items())],
        'piston_owners':[{'at':list(p),'blocks':[list(x) for x in members]} for p,members in sorted(flyer._piston_blocks.items())],
        'content_hash':flyer.content_hash(),'construction':read(run/'preparation.json'),
        'contracts':contracts,'prescribed_drive':(run/'drive.txt').read_text(encoding='utf-8'),
        'native_short':short,'native_longrun':long,'independent_cases':cases,
        'longrun_contract':long_contract,
        'longrun_drive_generation':'verify_column_interface.py: repeat supplied provenance at10*cycle+2*slot, X+3*cycle, cap12',
        'sha256':{n:hashlib.sha256((run/n).read_bytes()).hexdigest() for n in files},
        'tool_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('build_column_interface.py','verify_column_interface.py',Path(__file__).name)},
    }
    artifact.parent.mkdir(parents=True,exist_ok=True)
    artifact.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(f'Preserved {len(flyer._cells)} cells: independent240 and native240x10000, max{long["max_action"]}; supplied component only')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path);ap.add_argument('artifact',type=Path)
    a=ap.parse_args();preserve(a.run,a.artifact)
