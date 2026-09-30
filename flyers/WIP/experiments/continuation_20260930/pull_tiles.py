"""Find a literal two-interface tile with support ports on existing rails."""
from pull_chain import *

def off_for(anchor,rot):
    h=pull.transform((2,1,1),*rot,(0,0,0))
    return tuple(anchor[a]-h[a] for a in range(3))
def rail_for(index,rot,off):
    return {pull.transform(p,*rot,off) for p in pull.interface((index+1)%2,0,0)[0]}

def main():
    dest=HERE/'pull_port_tiles';dest.mkdir(exist_ok=True);manifest=[];tested=0
    singles=json.loads((HERE/'pull_single_manifest.json').read_text())
    for m in singles:
        anchor=tuple(m['anchor']);r0=tuple(m['rot']);o0=off_for(anchor,r0)
        for a1,r1 in itertools.product(sorted(rail_for(0,r0,o0)),itertools.product((0,1),(-1,1),(-1,1))):
            o1=off_for(a1,r1)
            if build(anchor,r0,(0,0,0),2,placements=[(r0,o0),(r1,o1)]) is None:continue
            for a2 in sorted(rail_for(1,r1,o1)):
                o2=off_for(a2,r0);translation=tuple(o2[a]-o0[a] for a in range(3))
                if translation==(0,0,0):continue
                placements=[(r0, o0),(r1,o1)]+[(r0,o2),(r1,tuple(o1[a]+translation[a] for a in range(3)))]
                tested+=1
                ans=build(anchor,r0,translation,4,placements=placements)
                if ans is None:continue
                f,meta=ans;meta['translation']=translation;meta['id']=len(manifest)
                f.save(dest/f"c{len(manifest):04}.flyer");manifest.append(meta)
    (HERE/'pull_port_tiles_manifest.json').write_text(json.dumps(dict(tested=tested,candidates=manifest),indent=2))
    p=subprocess.run([str(RUNNER),'screen',str(dest),'240','--out',str(HERE/'pull_port_tiles_screen.csv')],capture_output=True,text=True)
    (HERE/'pull_port_tiles_screen.txt').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
    print('tested tiles',tested,'routed',len(manifest),flush=True)

if __name__=='__main__':main()
