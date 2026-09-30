"""Reuse exact connected-cell pruning on the planar mmw lead."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'trim_mmw.py').read_text().replace('from derived_mmw import build,conn','from mmw_planar import build\nfrom derived_mmw import conn')
s=s.replace('centers=[(0,0),(4,0),(6,3),(4,6),(0,6),(-2,3)]','centers=[(0,0),(0,6),(5,3)]').replace('build(14,spacing=4,cap=65,centers=centers)','build(1,centers)').replace('f.push_limit=62','f.push_limit=37').replace('mmw_hex4_s014_pl62.flyer','mmw_planar_safe_s001_pl37.flyer').replace("out=HERE/'trim_mmw'","out=HERE/'trim_planar_mmw'").replace('mmw_hex_trim_pl','mmw_planar_trim_pl')
s=s[:s.index(' if r.returncode==0:')]+"\nif __name__=='__main__':main()\n"
exec(compile(s,str(h/'trim_planar_mmw.py'),'exec'),dict(__file__=str(h/'trim_planar_mmw.py'),__name__='__main__'))
