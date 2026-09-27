from pathlib import Path
import sys,subprocess,re,json
sys.path.insert(0,'.')
from fastflyer import Flyer
out=Path('flyers/WIP/experiments/astra_pullonly_20260927'); rows=[]
for p in sorted((out/'ring3').glob('*.flyer')):
 r=subprocess.run(['flyers/WIP/experiments/bin/research_runner.exe','audit',str(p),'12','6'],capture_output=True,text=True).stdout
 if 'distance=2 ' not in r or 'conservation_mismatch_ticks=0 ' not in r:continue
 load=int(re.search(r'max_successful_action=(\d+)',r)[1]);rows.append((load,Flyer.load(p).occupied_count(),p.name))
rows.sort();print(rows[:12]);(out/'ring3_rank.json').write_text(json.dumps(rows))
if rows:
 load,_,name=rows[0];f=Flyer.load(out/'ring3'/name);f.push_limit=load;f.save(out/'ring3_best.flyer');print('best',name,load)
