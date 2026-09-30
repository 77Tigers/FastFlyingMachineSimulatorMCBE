"""Apply the unchanged full-case bank gate to planar mmwmmw candidates."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'bank_pull3.py').read_text()
s=s.replace('assert len(pistons)==30 and all(b.sticky and b.direction==1 for b in pistons)','assert len(pistons)==12 and all(not b.sticky and b.direction==0 for b in pistons)')
s=s.replace("r['distance']=='3000'","r['distance']=='3333'").replace("r[k]=='1000'","r[k]=='833'")
s=s.replace("'distance=3000 '","'distance=3333 '").replace("'boundaries=1000 '","'boundaries=833 '").replace("'initial_matches=1000 '","'initial_matches=833 '").replace("'consecutive_matches=1000 '","'consecutive_matches=833 '")
s=s.replace('distance=3000','distance=3333').replace('speed_bps=3.0','speed_bps=3.333').replace('cycle_ticks=10,cycle_advance=3','cycle_ticks=12,cycle_advance=4')
s=s.replace("pulling_only=True,pistons=30,piston_direction='-X',sticky_pistons_only=True","movement_words=['mmwmmw','wmmwmm','mwmmwm'],pistons=12,piston_direction='+X',normal_pistons_only=True")
s=s.replace('pulling3_tenbody','planar_mmwmmw').replace('{end},3000,','{end},3333,')
exec(compile(s,str(h/'bank_planar_mmw.py'),'exec'),dict(__file__=str(h/'bank_planar_mmw.py'),__name__='__main__'))
