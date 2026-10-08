from pathlib import Path
import re,subprocess,json,sys
sys.path.insert(0,'.');from fastflyer import Flyer
out=Path('flyers/WIP/experiments/astra_pullonly_20260927');rows=[]
for line in (out/'mwmw_screen.txt').read_text().splitlines():
 if 'distance=40 ' not in line or 'conservation_mismatch_ticks=0 ' not in line:continue
 path=re.search(r'file=(.*?) limit=',line)[1]
 r=subprocess.run(['target/release/fastflyer-research.exe','audit',path,'16','8'],capture_output=True,text=True).stdout
 load=int(re.search(r'max_successful_action=(\d+)',r)[1]);rows.append((load,Flyer.load(path).occupied_count(),Path(path).name))
rows.sort();print(rows[:20]);(out/'mwmw_rank.json').write_text(json.dumps(rows))
load,_,name=rows[0];f=Flyer.load(out/'mwmw'/name);f.push_limit=load;f.save(out/'mwmw_best.flyer');print('best',name,load)
