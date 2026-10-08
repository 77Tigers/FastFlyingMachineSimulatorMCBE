"""Run the mv4-peak tool (tools/src/bin/mv4-peak.rs) and attribute its piston passengers to bank roles."""
from pathlib import Path
import sys, subprocess, json, collections
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
source=ROOT/'flyers/bank/pl43/mv4_symmetric_easy_compact.flyer'
import os
exe=ROOT/'target'/'release'/('mv4-peak'+('.exe' if os.name=='nt' else ''))  # cargo build --release --manifest-path tools/Cargo.toml --target-dir target
trial=subprocess.run([str(exe),str(source)],capture_output=True,text=True)
(HERE/'peak.csv').write_text(trial.stdout,encoding='utf-8')
if trial.returncode:raise SystemExit(trial.stderr)
rows=[s.split(',') for s in trial.stdout.splitlines()]
assert rows[0][:2]==['PEAK','122'],rows[0]
assert len(rows)==9,rows
meta=json.loads((HERE.parent/'mv4_easy_20261004/compact43/reroute_best.json').read_text())
initial_piston_yz={(q[1],q[2]) for q,b in Flyer.load(source)._cells.items() if b.kind==Kind.PISTON}
dy=min(y for y,z in initial_piston_yz)-min(p['y'] for p in meta['pistons'])
dz=min(z for y,z in initial_piston_yz)-min(p['z'] for p in meta['pistons'])
by_yz={(p['y']+dy,p['z']+dz):p for p in meta['pistons']}
assert len(by_yz)==24
assert set(by_yz)==initial_piston_yz,(dy,dz)
active=by_yz[(int(rows[0][3]),int(rows[0][4]))]
bank=active['bank']
passengers=[]
for row in rows[1:]:
    assert row[0]=='P',row
    p=by_yz[(int(row[2]),int(row[3]))]
    owner=p['bank']
    relation='own' if owner==bank else 'following' if (owner+1)%6==bank else 'previous' if (owner+2)%6==bank else 'other'
    passengers.append(dict(pid=p['pid'],bank=owner,role=relation,state=int(row[4]),
                           x=int(row[1]),y=int(row[2]),z=int(row[3])))
roles=dict(collections.Counter(p['role'] for p in passengers))
state=dict(tick=122,active_piston_pid=active['pid'],active_bank=bank,
           passenger_count=len(passengers),roles=roles,passengers=passengers,
           save_translation_yz=[dy,dz],
           identity_basis='Unique piston YZ coordinates; all simulator movements in this bank are along X',
           source=str(source))
(HERE/'peak.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in state.items() if k!='passengers'}))
