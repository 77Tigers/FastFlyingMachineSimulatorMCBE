"""Move T1 power observer to G1, trading a future piston recovery to H0."""
import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROLE=HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py'
def main():
 out=HERE/'out/quarter_ring_contacts/T1_split_source_budget';out.mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('role',ROLE);role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
 for identity in [1,2]:
  src=HERE/f'out/quarter_ring_contacts/joint_T1_mixed_recovery_budget/T1_slot{identity}_on_X1.json';r=json.loads(src.read_text(encoding='utf-8'));r['scope']=__doc__+' Necessary complete39 budget only; G1 source/piston recovery geometry and full flyer remain unbuilt.';r['permanent_masses']['H0']-=1;r['permanent_masses']['G1_power']+=1
  row=next(x for x in r['actions'] if x['target']=='H1_power' and x['slot']==4);contact=next(x for x in row['contacts'] if x['body']=='G1_power' and x['carries_at']==[1]);assert not any(x['body']=='H0' for x in row['contacts']);contact['body']='H0'
  r['required_carriers'].append('H1_power:4:H0:1');loads={b:{str(t):r['permanent_masses'][b] for t,v in enumerate(w) if v=='m'} for b,w in r['words'].items()}
  for action in r['actions']:
   tr=role.trajectory(role.moves(r['words'][action['target']]),action['kind'],action['slot'])
   for c in action['contacts']:
    assert c['touch'] in [list(o) for o in role.options(role.moves(r['words'][action['target']]),role.moves(r['words'][c['body']]),c['body']==action['target'],action['kind'],*tr[:2],*tr[2:])]
    actual=[t for t in range(5) if action['piston_word'][t]=='m' and r['words'][c['body']][t]=='m' and c['touch'][t]];assert actual==c['carries_at']
    for t in actual:loads[c['body']][str(t)]+=1
   for t,v in enumerate(action['piston_word']):assert any(t in c['carries_at'] for c in action['contacts'])==(v=='m')
  assert len(r['actions'])==39 and max(v for b in loads.values() for v in b.values())==12
  r.update(status='INDEPENDENT_CONTACT_COVERAGE_AND_LOADS_CHECKED',loads=loads,peak=12,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_allocation={'H0':{'future_glue':4,'local_glue_cap':2,'RB':1,'gate_observer':1,'mass':8},'G1_power':{'total_glue_cap':5,'RB':1,'own_observer':1,'new_T1_observer':1,'mass':8},'change':'New observer uses G1 existing five-glue budget, not an additional append-only connector. Both words mmwwm preserve pulse1/2 and relative source timing. H1 power push4 motor recovery moves G1 -> H0 on1. These front hardware roles still need construction.'});(out/f'T1_slot{identity}_on_X1.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(identity,{b:loads[b] for b in ['H0','G1_power','T0','X1']})
 (out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
