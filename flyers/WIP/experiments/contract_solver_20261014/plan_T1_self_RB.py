"""Necessary complete39 allocation for a self-powered two-push/pull T1."""
import importlib.util,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
 parent=HERE/'out/quarter_ring_contacts/G0_face_swap_preflight/glue_root_budget.json';r=json.loads(parent.read_text(encoding='utf-8'));rolepath=HERE.parent/'tm_smol_rebalance_20261001/j2_front_smol/layered.py';spec=importlib.util.spec_from_file_location('roles',rolepath);role=importlib.util.module_from_spec(spec);spec.loader.exec_module(role)
 r['permanent_masses']['G1_power']-=1;loads={b:{str(t):r['permanent_masses'][b] for t,v in enumerate(w) if v=='m'} for b,w in r['words'].items()}
 for action in r['actions']:
  tr=role.trajectory(role.moves(r['words'][action['target']]),action['kind'],action['slot'])
  for c in action['contacts']:
   assert c['touch'] in [list(o) for o in role.options(role.moves(r['words'][action['target']]),role.moves(r['words'][c['body']]),c['body']==action['target'],action['kind'],*tr[:2],*tr[2:])]
   actual=[t for t in range(5) if action['piston_word'][t]=='m' and r['words'][c['body']][t]=='m' and c['touch'][t]];assert actual==c['carries_at']
   for t in actual:loads[c['body']][str(t)]+=1
  for t,v in enumerate(action['piston_word']):assert any(t in c['carries_at'] for c in action['contacts'])==(v=='m')
 assert len(r['actions'])==39 and max(v for ds in loads.values() for v in ds.values())==12
 r.update(scope=__doc__+' Six connected T1 glue plus RB replace seven-glue/external-observer source. G1 loses only its T1 source observer. Hardware/power/off/recovery UNBUILT; budget evidence only.',loads=loads,peak=12,source_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),T1_source_allocation={'glue_cap':6,'own_RB':1,'permanent':7,'G1_T1_source_observer':0,'G1_permanent':8,'status':'UNBUILT_ARCHITECTURE_HYPOTHESIS'})
 r['source_allocation']['T1']={'glue_cap':6,'own_RB':1,'mass':7};r['source_allocation']['G1_power']['T1_source_observer']=0;r['source_allocation']['G1_power']['mass']=8
 out=HERE/'out/quarter_ring_contacts/T1_self_RB_budget';out.mkdir(exist_ok=False);(out/'full39.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');(out/'generator_snapshot.py').write_bytes(Path(__file__).read_bytes());print({'global_peak':12,'T1':loads['T1'],'G1':loads['G1_power']})
if __name__=='__main__':main()
