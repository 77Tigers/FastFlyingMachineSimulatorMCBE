"""Full core matrix, traced load, one-lower check; optional verified bank export.

Usage: python validate.py FILE.flyer [--bank]. No full passenger recurrence claim.
"""
import sys,json,csv,re,subprocess,hashlib,shutil
from pathlib import Path
import common as c
from fastflyer import Flyer
path=Path(sys.argv[1]).resolve();out=c.HERE/'validation'/(path.parent.name+'_'+path.stem);out.mkdir(parents=True,exist_ok=True)

trial=subprocess.run([str(c.RUNNER),'audit',str(path),'10000','12'],capture_output=True,text=True,timeout=300)
trace=trial.stdout+trial.stderr;(out/'audit10000.txt').write_text(trace)
fields=dict(re.findall(r'\b(start_min_x|end_min_x|distance|extensions|extension_failures|movement_failures|end_blocks|conservation_mismatch_ticks|max_successful_action|limit)=(-?\d+)',trace))
good=trial.returncode==0 and all(fields.get(k)=='0' for k in ('extension_failures','movement_failures','conservation_mismatch_ticks'))
if good:
    trial=subprocess.run([str(c.AUDIT),str(path),'10000',str(out/'full80.csv')],capture_output=True,text=True,timeout=900)
    (out/'full80.txt').write_text(trial.stdout+trial.stderr)
    rows=list(csv.DictReader((out/'full80.csv').open()))
    good=trial.returncode==0 and len(rows)==80 and all(r['pass']=='true' and r['ticks']=='10000' for r in rows)
else:rows=[]
state=dict(status='verified' if good else 'failed',source=str(path),fields=fields,
           cases=len(rows),passed=sum(r['pass']=='true' for r in rows),
           full_passenger_state_recurrence=False)
if good:
    f=Flyer.load(path);lower=out/f'lower_pl{f.push_limit-1}.flyer';f.push_limit-=1;f.save(lower)
    trial=subprocess.run([str(c.RUNNER),'audit',str(lower),'10000','12'],capture_output=True,text=True,timeout=300)
    lowertext=trial.stdout+trial.stderr;(out/'lower.audit10000.txt').write_text(lowertext)
    lowerfields=dict(re.findall(r'\b(extension_failures|movement_failures|distance)=(-?\d+)',lowertext))
    state['one_lower']=lowerfields
    if '--bank' in sys.argv:
        limit=int(fields['limit']);flyers=c.HERE.parents[2]
        name=sys.argv[sys.argv.index('--name')+1] if '--name' in sys.argv else 'mv4_symmetric_easy'
        dest=flyers/f'bank/pl{limit}/{name}.flyer';dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(path,dest);shutil.copyfile(path,flyers/f'WIP/{name}_pl{limit}.flyer')
        ledger=flyers/'bank/results.csv'
        record=','.join([str(limit),name,fields['start_min_x'],fields['end_min_x'],fields['distance'],fields['end_blocks'],fields['extensions']])
        if record not in ledger.read_text().splitlines():
            with ledger.open('a',newline='') as fp:fp.write(record+'\n')
        state.update(artifact=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
(out/'summary.json').write_text(json.dumps(state,indent=2));print(json.dumps(state,indent=2),flush=True)
sys.exit(0 if good else 1)
