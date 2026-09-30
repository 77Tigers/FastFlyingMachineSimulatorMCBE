"""Test axial gauges that shorten the sparse mixed-role support spans."""
from pathlib import Path
h=Path(__file__).resolve().parent
s=(h/'mixed_role_ring.py').read_text().replace('mixed_tile_contact_cover.json','compact_mixed_tile_contact_cover.json').replace('mixed_extension_manifest.json','mixed_extension_compact_manifest.json').replace('dy12_dz0_s001.flyer','dy12_dz0_s000.flyer')
s=s.replace('mixed_role_ring_v2','mixed_role_gauged').replace('mixed_role_ring_legal.py','mixed_role_gauged_legal.py').replace('for radius in (8,10):','for radius in (6,7):').replace('range(8)','range(20)').replace('cap=50','cap=38')
s=s.replace('fronts=[rng.choice((-1,0,1)) for _ in range(10)]',"gauges=json.loads((HERE/'mixed_role_axial_bounds.json').read_text())['winners'];gauge=gauges[seed%len(gauges)][0];fronts=[gauge[3*i%5] for i in range(10)]")
exec(compile(s,str(h/'mixed_role_gauged.py'),'exec'),dict(__file__=str(h/'mixed_role_gauged.py'),__name__='__main__'))
