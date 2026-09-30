"""Prune the routedPL102 pure-pull candidate without altering its bank evidence."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'trim_pull3.py').read_text()
a=s.index('    m=next(');b=s.index('    raw=',a)
s=s[:a]+"    m=json.loads((HERE/'reroute_pull3/geometry.json').read_text())\n    f=Flyer.load(HERE/'pull3_reroute_pl102.flyer');f.push_limit=1000\n"+s[b:]
s=s.replace("out=HERE/'trim_pull3'","out=HERE/'trim_pull3_rerouted'").replace('pull3_trim_pl','pull3_reroute_trim_pl')
s=s.replace(",('samples',[str(path),'--period','10','--advance','3','--out',str(path.with_suffix('.samples.csv'))])",'')
exec(compile(s,str(h/'trim_pull3_rerouted.py'),'exec'),dict(__file__=str(h/'trim_pull3_rerouted.py'),__name__='__main__'))
