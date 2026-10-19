"""Rotate macro37's free G0 normal row; preserve its shared-power offsets."""
import argparse,hashlib,json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('parent',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();m=json.loads(a.parent.read_text(encoding='utf-8'))['results'][37]
    cells={tuple(c[:3]):c[3] for c in m['macro_cells']}
    for old,new,kind in [((17,1,15),(17,2,14),9),((19,1,15),(19,2,14),2)]:
        assert cells[old]==kind and new not in cells
        cells[new]=cells.pop(old)
    m['macro_cells']=[[*p,b] for p,b in sorted(cells.items())]
    m['G0_normals_at_initial']=[[17,2,14] if q==[17,1,15] else q for q in m['G0_normals_at_initial']]
    m['parent_macro_index']=37
    m['change']='Rotate the otherwise unused G0 normal row around its shared RB: base17,1,15 to17,2,14 and matching glue19,1,15 to19,2,14. Other actors, source, initial states and recovery contacts stay fixed.'
    assert all(abs(q[0]+1-18)+abs(q[1]-1)+abs(q[2]-14)==1 for q in m['G0_normals_at_initial'])
    a.out.write_text(json.dumps({'scope':'Changed geometry hypothesis, not native acceptance. Shared-source offsets and matching push-contact coordinates calibrated; H0 recovery contacts retained.','parent_sha256':hashlib.sha256(a.parent.read_bytes()).hexdigest(),'results':[m]},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
