"""Checkpoint already-authorized native audits when they finish after model usage."""
from pathlib import Path
import time,json,csv,hashlib
h=Path(__file__).resolve().parent;root=h.parents[3];last=None
required={(r,x,z) for r in (0,1,2,5,42) for x in (0,7,8,15) for z in (0,7,8,15)}
def check_chain(name,copies,local):
 p=h/name;report=p.with_suffix('.samples.txt')
 if not report.exists():return dict(status='running',file=name)
 output=report.read_text(encoding='utf-8-sig')
 if not output.strip():return dict(status='running',file=name)
 rows=list(csv.DictReader(p.with_suffix('.samples.csv').open()))
 valid='samples passed=80/80' in output and 'ticks=10000' in output and len(rows)==80
 valid=valid and {(int(r['rng']),int(r['phase_x']),int(r['phase_z'])) for r in rows}==required
 valid=valid and all(r['pass']=='true' and r['distance']=='3000' and all(r[k]=='1000' for k in ('boundaries','initial_matches','consecutive_matches')) and all(r[k]=='0' for k in ('extension_failures','movement_failures','conservation_mismatch_ticks','displacement_mismatches')) for r in rows)
 result=dict(status='passed' if valid else 'failed',file=name,copies=copies,full_cases=len(rows),ticks=10000,period=10,advance=3,baseline_tagged_local_max=local,whole_limit=int(rows[0]['limit']) if rows else None,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 if valid:p.with_suffix('.chain_certificate.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 return result
while True:
 bank_report=h/'pending_pull3_bank_result.json'
 bank=dict(status='running',file='pull3_reroute_pl102.flyer')
 if bank_report.exists():
  result=json.loads(bank_report.read_text(encoding='utf-8'))
  bank=dict(status='passed' if result['exit_code']==0 else 'failed',file='pull3_reroute_pl102.flyer',bank_file='flyers/bank/pl102/pulling3_tenbody.flyer' if result['exit_code']==0 else None)
  if bank['status']=='passed':
   target=root/bank['bank_file'];entry=json.loads((root/'flyers/bank/catalogue.json').read_text(encoding='utf-8'))['entries'][bank['bank_file']]
   assert hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256'] and entry['full_rng_phase_samples']==80
 results=dict(pulling3=bank,mixed_local11=check_chain('mixed_chain_8tiles_pl217.flyer',8,11),mixed_local8=check_chain('compact_mixed_chain_8tiles_pl195.flyer',8,8))
 encoded=json.dumps(results,sort_keys=True)
 if encoded!=last:
  pending=h/'native_audit_checkpoint.pending.json';pending.write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8');pending.replace(h/'native_audit_checkpoint.json')
  lines=['# Native full-audit checkpoint','', 'Updated directly from completed native audit reports; no account reset or purchase.','']
  for name,result in results.items():lines.append(f'- {name}: {result["status"]}; '+json.dumps(result,sort_keys=True))
  (h/'NATIVE_AUDIT_CHECKPOINT.md').write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))
  print(encoded,flush=True);last=encoded
 if all(result['status']!='running' for result in results.values()):break
 time.sleep(15)
