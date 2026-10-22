"""Budget a G0 observer / G1 stone pull gate, removing X1 gate reach."""
import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROLE=HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py'
def main():
 out=HERE/'out/quarter_ring_contacts/T1_front_stone_budget';out.mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('role',ROLE);role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
 for identity in [1,2]:
  src=HERE/f'out/quarter_ring_contacts/T1_split_source_budget/T1_slot{identity}_on_X1.json';r=json.loads(src.read_text(encoding='utf-8'));r['scope']=__doc__+' Necessary complete39 budget only; G1 source/piston recovery geometry and full flyer remain unbuilt.';r['permanent_masses']['H0']-=1;r['permanent_masses']['G1_power']+=1;r['permanent_masses']['X1']-=1
  row=next(x for x in r['actions'] if x['target']=='H1_power' and x['slot']==3);contact=next(x for x in row['contacts'] if x['body']=='G1_power' and x['carries_at']==[0,1]);assert not any(x['body']=='H0' for x in row['contacts']);contact['body']='H0'
  r['required_carriers'].append('H1_power:3:H0:01');r.pop('H0_source_allocation',None);r.pop('gate_hardware_trade',None);r['explicit_mass_changes_from_parent']={'H0':-1,'G1_power':1,'X1':-1,'G0':0};loads={b:{str(t):r['permanent_masses'][b] for t,v in enumerate(w) if v=='m'} for b,w in r['words'].items()}
  for action in r['actions']:
   tr=role.trajectory(role.moves(r['words'][action['target']]),action['kind'],action['slot'])
   for c in action['contacts']:
    assert c['touch'] in [list(o) for o in role.options(role.moves(r['words'][action['target']]),role.moves(r['words'][c['body']]),c['body']==action['target'],action['kind'],*tr[:2],*tr[2:])]
    actual=[t for t in range(5) if action['piston_word'][t]=='m' and r['words'][c['body']][t]=='m' and c['touch'][t]];assert actual==c['carries_at']
    for t in actual:loads[c['body']][str(t)]+=1
   for t,v in enumerate(action['piston_word']):assert any(t in c['carries_at'] for c in action['contacts'])==(v=='m')
  assert len(r['actions'])==39 and max(v for b in loads.values() for v in b.values())==12
  r.update(status='INDEPENDENT_CONTACT_COVERAGE_AND_LOADS_CHECKED',loads=loads,peak=12,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_allocation={'H0':{'future_glue':4,'local_glue_cap':2,'RB':1,'observers':0,'mass':7},'G1_power':{'total_glue_cap':5,'RB':1,'own_observer':1,'T1_source_observer':1,'gate_stone':1,'mass':9},'G0':{'glue':6,'RB':1,'existing_observers':2,'new_gate_observer':1,'mass':10},'X1':{'glue':6,'future_source_reserve':1,'mass':7},'change':'Move gate observer H0->G0 and gate stone X1->G1. G0 consumes its existing one-cell conservative mass reserve on the accepted upper interface. H1 push3 motor recovery moves G1->H0 on0/1. These are necessary front role and power budgets, not physical construction.'});(out/f'T1_slot{identity}_on_X1.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(identity,{b:loads[b] for b in ['H0','G1_power','G0','T0','X1']})
 (out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
