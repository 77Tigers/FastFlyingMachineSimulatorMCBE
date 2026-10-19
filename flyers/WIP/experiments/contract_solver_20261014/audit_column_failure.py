"""Save identity-based native failure witnesses; failed sets are partial bounds.

This one-sample diagnostic never substitutes for independent or long proofs.
"""
import argparse,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run',type=Path)
    ap.add_argument('--phase-z',type=int,default=7)
    a=ap.parse_args();p=a.run
    r=subprocess.run([str(ROOT/'target/release/extension-prescribe.exe'),str(p/'problem.flyer'),'30',str(p/'drive.txt'),'before','0','0',str(a.phase_z)],cwd=ROOT,capture_output=True,text=True)
    (p/f'trace_failure_0_0_{a.phase_z}.jsonl').write_text(r.stdout,encoding='utf-8')
    rows=[json.loads(s) for s in r.stdout.splitlines()]
    state={tuple(c[:3]):c[3] for c in rows[0]['trace']['initial']}
    origins={q:q for q,b in state.items() if b&15!=10}
    ports={tuple(x['at']):x['name'] for x in json.loads((p/'before_natural.json').read_text(encoding='utf-8'))['ports']}
    actions=[];failures=[]
    for w in rows:
      for s in w['trace']['steps']:
        m=s.get('movement') or {};src=list(map(tuple,m.get('sources',[])));dst=list(map(tuple,m.get('destinations',[])))
        info={'tick':w['tick'],'action':s['action'],'actor':s.get('active_piston'),'failure':m.get('failure'),
              'identities':[[*q,state.get(q),origins.get(q)] for q in src],
              'moved_ports':[ports[origins[q]] for q in src if origins.get(q) in ports]}
        if m.get('failure'):
            info.update({'partial_discovery_count':len(src),'links':m.get('links')});failures.append(info)
        elif src and dst:
            assert len(src)==len(dst)
            info['successful_load']=len(src);actions.append(info)
            entries={q:origins[sr] for sr,q in zip(src,dst) if sr in origins}
            for q in src:origins.pop(q,None)
            origins.update(entries)
        for x,y,z,b in s['changes']:
            if b is None:state.pop((x,y,z),None)
            else:state[x,y,z]=b
    result={'scope':__doc__,'sample':{'rng':0,'phase_x':0,'phase_z':a.phase_z,'order':'before'},
            'actions':actions,'failed_partial_discoveries':failures,'stderr':r.stderr}
    (p/f'failure_audit_0_0_{a.phase_z}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'actions':[{k:v for k,v in x.items() if k!='identities'} for x in actions if x['tick']<=2],
                      'first_failures':[{k:v for k,v in x.items() if k not in ['links','identities']} for x in failures[:2]]}))


if __name__=='__main__':main()
