from __future__ import annotations
import os as _research_os
import copy,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(ROOT/'tools'))
from extension_contract import load_contract,run_case
OUT=Path(__file__).parent/'n4_14_validation'
OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'flyers/extension_bank/n4/n4_14/before_natural.json'
raw=json.loads(source.read_text(encoding='utf-8'))
sample=(0,0,0)
rows=[]
for mode,short in [('before_natural','before'),('after_natural','after'),('interleaved','interleaved')]:
 folder=OUT/mode; folder.mkdir(parents=True,exist_ok=True)
 compiled=copy.deepcopy(raw); compiled['name']='n4_14-witness-'+mode; compiled['prescribed_order']=mode
 for key in ('flyer','prescribed_script','drive_script'):
  if key in compiled and compiled[key]: compiled[key]=os.path.relpath((source.parent/compiled[key]).resolve(),folder)
 contract_path=folder/'contract.json'; contract_path.write_text(json.dumps(compiled,indent=2)+'\n',encoding='utf-8')
 contract=load_contract(contract_path)
 py=run_case(contract,ROOT/('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else '')),sample)
 rust_cmd=[str(ROOT/('target/release/contract-search' + ('.exe' if _research_os.name == 'nt' else ''))),str(contract_path),'0','1',str(folder/'eval'),'--eval-only','--order',short,'--recurrence',raw.get('recurrence','exact'),'--high','0','--rng','0','--phase-x','0','--phase-z','0']
 rp=subprocess.run(rust_cmd,capture_output=True,text=True,timeout=60)
 row={'mode':mode,'python':py,'rust_command':rust_cmd,'rust_returncode':rp.returncode,'rust_stdout':rp.stdout,'rust_stderr':rp.stderr}
 rows.append(row); (folder/'result.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8')
 print(f"{mode}: Python passed={py['passed']} diag={py.get('diagnostic')}; Rust rc={rp.returncode} {rp.stdout.strip()}",flush=True)
# Actual driver trace, retaining stdout even though the failing prescribed event exits nonzero.
flyer=(source.parent/raw['flyer']).resolve(); script=(source.parent/raw['prescribed_script']).resolve()
cmd=[str(ROOT/('target/release/extension-prescribe' + ('.exe' if _research_os.name == 'nt' else ''))),str(flyer),str(raw['period_ticks']*raw['cycles']),str(script),'interleaved','0','0','0']
p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
(OUT/'actual_interleaved.trace.jsonl').write_text(p.stdout,encoding='utf-8')
(OUT/'actual_interleaved.stderr.txt').write_text(p.stderr,encoding='utf-8')
(OUT/'summary.json').write_text(json.dumps({'driver_command':cmd,'driver_returncode':p.returncode,'driver_stderr':p.stderr,'results':rows},indent=2)+'\n',encoding='utf-8')
print(f"trace: rc={p.returncode}, lines={len(p.stdout.splitlines())}, stderr={p.stderr.strip()}")
