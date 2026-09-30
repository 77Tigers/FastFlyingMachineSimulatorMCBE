"""Additional coplanar-port placements; preserve the first batch's evidence."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'mmw_planar.py').read_text().replace('mmw_planar_candidates','mmw_planar_more_candidates').replace('mmw_planar_manifest.json','mmw_planar_more_manifest.json').replace('mmw_planar_screen','mmw_planar_more_screen')
s=s.replace("[('tight',[(0,0),(0,4),(3,1)]),('medium',[(0,0),(0,5),(4,2)]),('safe',[(0,0),(0,6),(5,3)])]","[('safe',[(0,0),(0,6),(5,3)]),('offset',[(0,0),(0,6),(6,2)]),('short',[(0,0),(0,5),(5,3)])]").replace('range(16)','range(16,40)')
exec(compile(s,str(h/'mmw_planar_more.py'),'exec'),dict(__file__=str(h/'mmw_planar_more.py'),__name__='__main__'))
