from pathlib import Path
import subprocess,sys
h=Path(__file__).resolve().parent
s=(h/'validate_mixed_tiles.py').read_text().replace('mixed_tile_bridged','compact_mixed_tile_bridged').replace('mixed_chain_','compact_mixed_chain_').replace("r['sticky_cells']=='8'","r['sticky_cells']=='5'").replace('<=11','<=8').replace('local_extension_max=11','local_extension_max=8')
p=h/'validate_compact_mixed_tiles.py';p.write_text(s)
raise SystemExit(subprocess.call([sys.executable,str(p)]))
