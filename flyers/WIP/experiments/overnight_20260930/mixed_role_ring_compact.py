"""Close the new five-cell interface while preserving separate back/front roles."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def main():
    lead=next(m for m in json.loads((HERE/'mixed_extension_compact_manifest.json').read_text())['candidates'] if m['file']=='dy12_dz0_s000.flyer');delta=lead['delta']
    def point(p):return [p[a]+delta[a] for a in range(3)]
    cover=dict(delta=delta,patches=[[],[],[point((3,0,0))],[point((-1,0,0))],[point((3,2,0))],lead['segments'][5]],pistons=lead['pistons'][-3:],sources=lead['sources'][-3:])
    (HERE/'compact_mixed_tile_contact_cover.json').write_text(json.dumps(cover,indent=2))
    s=(HERE/'mixed_role_ring.py').read_text().replace('mixed_tile_contact_cover.json','compact_mixed_tile_contact_cover.json').replace('mixed_extension_manifest.json','mixed_extension_compact_manifest.json').replace("'dy12_dz0_s001.flyer'","'dy12_dz0_s000.flyer'")
    s=s.replace('mixed_role_ring_v2','mixed_role_ring_compact').replace('mixed_role_ring_legal.py','mixed_role_ring_compact_legal.py').replace('for radius in (8,10):','for radius in (4,5,6):').replace('cap=50','cap=32')
    # OneDrive briefly held the manifest during atomic replacement. Resume
    # completed cases from the intact pending checkpoint, and retry replaces.
    retry='''import time
def retry_replace(source,target):
    for attempt in range(30):
        try:return source.replace(target)
        except PermissionError:
            if attempt==29:raise
            time.sleep(0.1)
'''
    s=retry+s;s=s.replace('pending.replace(', 'retry_replace(pending,')
    s=s.replace('stats=collections.Counter();manifest=[]',"checkpoint=HERE/'mixed_role_ring_compact_manifest.pending.json';checkpoint=checkpoint if checkpoint.exists() else HERE/'mixed_role_ring_compact_manifest.json';resume=json.loads(checkpoint.read_text()) if checkpoint.exists() else {};stats=collections.Counter(resume.get('stats',{}));manifest=resume.get('candidates',[])")
    s=s.replace('            for seed in range(8):','''            for seed in range(8):
                if resume and ((4,5,6).index(radius),('uniform','radial').index(scheme),seed)<=((4,5,6).index(resume['radius']),('uniform','radial').index(resume['scheme']),resume['next_seed']-1):continue''')
    s=s.replace("if __name__=='__main__':main()",'');target=HERE/'derived_mixed_role_ring_compact.py';target.write_text(s);ns={'__file__':str(target)};exec(compile(s,str(target),'exec'),ns);ns['main']()
if __name__=='__main__':main()
