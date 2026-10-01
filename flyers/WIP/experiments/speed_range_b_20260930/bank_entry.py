"""Append one speed+conservation-audited flyer to the bank without rewriting existing bytes (files have mixed EOLs).
Usage: bank_entry.py SRC PL NAME CYC ADV DIST ENDBLOCKS EXT MAXLOAD SAMPLES X0 X1 NOTE"""
import sys, json, shutil, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
src,pl,name,cyc,adv,dist,endb,ext,maxload,samples,x0,x1,note=sys.argv[1:14]
dst=ROOT/f'flyers/bank/pl{pl}/{name}.flyer'
dst.parent.mkdir(exist_ok=True)
shutil.copyfile(src,dst)
sha=hashlib.sha256(dst.read_bytes()).hexdigest()
key=f'flyers/bank/pl{pl}/{name}.flyer'
entry=dict(sha256=sha,ticks=10000,distance=int(dist),speed_bps=int(dist)/1000,extensions=int(ext),extension_failures=0,endpoint_conserved=True,cycle_ticks=int(cyc),cycle_advance=int(adv),full_rng_phase_samples=int(samples),exact_block_owner_recurrence=False,speed_conservation_audit_only=True,max_successful_action=int(maxload),note=note)
cat=ROOT/'flyers/bank/catalogue.json'
b=cat.read_bytes()
tail=b'\n  }\r\n}\r\n'
assert b.endswith(tail)
body=json.dumps({key:entry},indent=2).split('\n')[1:-1]  # entry lines at 2-space indent
text=',\n'+'\n'.join(body).replace('\n','\r\n')
b=b[:-len(tail)]+text.encode()+tail
json.loads(b)  # validity check
cat.write_bytes(b)
with open(ROOT/'flyers/bank/results.csv','ab') as f:
    f.write(f'{pl},{name},{x0},{x1},{dist},{endb},{ext}\n'.encode())
print(key,sha)
