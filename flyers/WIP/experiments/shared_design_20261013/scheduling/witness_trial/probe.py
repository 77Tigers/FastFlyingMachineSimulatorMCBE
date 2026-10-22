from __future__ import annotations
import os as _research_os
import copy, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / 'tools'))
from extension_contract import load_contract, run_case
DRIVER = ROOT / ('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))
SAMPLES = [(0,0,0),(0,0,7),(0,7,0),(1,7,8),(2,8,8),(5,15,15),(42,7,8),(42,15,0)]
BASE = ROOT / 'flyers/WIP/experiments/shared_design_20261013/bank_migration'
OUT = Path(__file__).parent
results=[]
for fixture in ('n2_05','n4_13'):
  source=BASE/fixture/'before_natural'/'contract.json'
  raw=json.loads(source.read_text(encoding='utf-8'))
  for mode in ('before_natural','after_natural','interleaved'):
    folder=OUT/fixture/mode
    folder.mkdir(parents=True,exist_ok=True)
    compiled=copy.deepcopy(raw)
    compiled['name']=f'{fixture}-witness-{mode}'
    compiled['prescribed_order']=mode
    for key in ('flyer','prescribed_script','drive_script'):
      if key in compiled and compiled[key]:
        compiled[key]=os.path.relpath((source.parent/compiled[key]).resolve(),folder)
    contract_path=folder/'contract.json'
    contract_path.write_text(json.dumps(compiled,indent=2)+'\n',encoding='utf-8')
    contract=load_contract(contract_path)
    for sample in SAMPLES:
      result=run_case(contract,DRIVER,sample)
      row={'fixture':fixture,'mode':mode,'sample':sample,'passed':result['passed'],'diagnostic':result.get('diagnostic'),'realized_action_order':result.get('realized_action_order'),'schedule_seeds':result.get('schedule_seeds')}
      results.append(row)
      print(f"{fixture:6} {mode:15} {sample!s:16} passed={result['passed']} {result.get('diagnostic') or ''}",flush=True)
      (folder/(f'case_{sample[0]}_{sample[1]}_{sample[2]}.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
