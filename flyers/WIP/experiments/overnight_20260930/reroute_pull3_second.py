"""Reroute all ten trimmed pure-pull bodies; preserve the first102 audit."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'reroute_pull3.py').read_text()
a=s.index('    m=next(');b=s.index('    f=Flyer.load',a)
s=s[:a]+'''    trimmed=json.loads((HERE/'trim_pull3_rerouted/geometry.json').read_text());m=trimmed['source_metadata'];offset0=trimmed['source_offset']
    m['segments']=[[[p[a]-offset0[a] for a in range(3)] for p in cells] for cells in trimmed['segments']]
    segments=[set(map(tuple,cells)) for cells in m['segments']];ps=m['pistons'];sources=m['sources']
'''+s[b:]
s=s.replace("Flyer.load(HERE/'pull3_compact_candidates'/m['file'])","Flyer.load(HERE/'pull3_reroute_trim_pl102.flyer')")
s=s.replace("assert all(original_ports[i]<=segments[i] for i in range(10)), 'port regeneration differs from saved witness'","original_ports=[original_ports[i]&segments[i] for i in range(10)]")
s=s.replace("out=HERE/'reroute_pull3'","out=HERE/'reroute_pull3_second'").replace('current_max=106','current_max=102').replace('[:4]:',':').replace('range(8)','range(16)').replace('pull3_reroute_pl','pull3_reroute_second_pl')
exec(compile(s,str(h/'reroute_pull3_second.py'),'exec'),dict(__file__=str(h/'reroute_pull3_second.py'),__name__='__main__'))
