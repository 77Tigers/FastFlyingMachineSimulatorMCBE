"""Trade G0 motor recovery to T0 for equal X2 recovery on X1; unchanged PL12."""
import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROLE=HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py'
def main():
 out=HERE/'out/quarter_ring_contacts/G0_T0_recovery_trade_budget';out.mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('role',ROLE);role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
 for identity in [1,2]:
  src=HERE/'out/quarter_ring_contacts/T1_both_on_X1_budget/T1_slot1_on_X1.json';r=json.loads(src.read_text(encoding='utf-8'));r['scope']=__doc__+' Necessary complete39 allocation only; transferred hardware and full flyer remain unbuilt.'
  for slot in range(1,identity+1):
   for target,old,new in [('G0','X1','T0'),('X2','T0','X1')]:
    action=next(x for x in r['actions'] if x['target']==target and x['slot']==slot and x['kind']=='push')
    c=next(c for c in action['contacts'] if c['body']==old and c['carries_at']);assert c['carries_at']==([0,3,4] if slot==1 else [0,4]);c['body']=new
  r['required_carriers']=[x for x in r['required_carriers'] if not any(x.startswith(f'{target}:{slot}:') for target in ['G0','X2'] for slot in range(1,identity+1))]+[f'{target}:{slot}:{body}:'+('034' if slot==1 else '04') for slot in range(1,identity+1) for target,body in [('G0','T0'),('X2','X1')]]
  r['explicit_mass_changes_from_parent']={};loads={b:{str(t):r['permanent_masses'][b] for t,v in enumerate(w) if v=='m'} for b,w in r['words'].items()}
  for action in r['actions']:
   tr=role.trajectory(role.moves(r['words'][action['target']]),action['kind'],action['slot'])
   for c in action['contacts']:
    assert c['touch'] in [list(o) for o in role.options(role.moves(r['words'][action['target']]),role.moves(r['words'][c['body']]),c['body']==action['target'],action['kind'],*tr[:2],*tr[2:])]
    actual=[t for t in range(5) if action['piston_word'][t]=='m' and r['words'][c['body']][t]=='m' and c['touch'][t]];assert actual==c['carries_at']
    for t in actual:loads[c['body']][str(t)]+=1
   for t,v in enumerate(action['piston_word']):assert any(t in c['carries_at'] for c in action['contacts'])==(v=='m')
  assert len(r['actions'])==39 and max(v for b in loads.values() for v in b.values())==12
  assert loads==json.loads(src.read_text(encoding='utf-8'))['loads']
  r.update(status='INDEPENDENT_CONTACT_COVERAGE_AND_LOADS_CHECKED',loads=loads,peak=12,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),recovery_trade={'G0_slots_on_T0':list(range(1,identity+1)),'X2_slots_on_X1':list(range(1,identity+1)),'permanent_mass_change':0,'load_change':0,'geometry_unbuilt':True});(out/f'G0_slots_{identity}_on_T0.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(identity,{b:loads[b] for b in ['T0','X1','G0']})
 (out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
