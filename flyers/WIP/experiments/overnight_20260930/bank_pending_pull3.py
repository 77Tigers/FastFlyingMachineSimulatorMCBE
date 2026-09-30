"""Finish an already-live full audit with the strict bank gate when it ends."""
from pathlib import Path
import time,subprocess,sys,json
h=Path(__file__).resolve().parent;source=h/'pull3_reroute_pl102.flyer';report=source.with_suffix('.samples.txt')
while not report.exists():time.sleep(15)
text=report.read_text(encoding='utf-8-sig')
assert 'samples passed=80/80' in text and 'ticks=10000' in text,text
r=subprocess.run([sys.executable,str(h/'bank_pull3.py'),str(source)],capture_output=True,text=True)
(h/'pending_pull3_bank_result.json').write_text(json.dumps(dict(source=source.name,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2),encoding='utf-8')
print(r.stdout+r.stderr,flush=True);raise SystemExit(r.returncode)
