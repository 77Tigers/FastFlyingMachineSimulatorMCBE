from pull_chain import *

def main():
    meta=json.loads((HERE/'pull_port_tiles_manifest.json').read_text())['candidates'][0]
    r0,o0=map(tuple,meta['placements'][0]);r1,o1=map(tuple,meta['placements'][1]);v=tuple(meta['translation'])
    certificate=[]
    for tiles in (1,2,4,8):
        placements=[(r,tuple(o[a]+j*v[a] for a in range(3))) for j in range(tiles) for r,o in [(r0,o0),(r1,o1)]]
        f,m=build(tuple(meta['anchor']),r0,v,2*tiles,placements=placements)
        f.push_limit=11;path=HERE/f'pull_chain_{tiles}tiles_pl11.flyer';f.save(path)
        loaded=Flyer.load(path)
        delta=tuple(min(p[a] for p in loaded._cells)-min(p[a] for p in f._cells) for a in range(3))
        with path.with_suffix('.bodies.csv').open('w') as w:
            w.write('body,phase,x,y,z\n')
            for i,s in enumerate(m['segments']):
                for p in s:w.write(f"{i},{m['phase'][i]},"+','.join(str(p[a]+delta[a]) for a in range(3))+'\n')
        path.with_suffix('.geometry.json').write_text(json.dumps(m,indent=2))
        p=subprocess.run([str(RUNNER),'verify',str(path),'10000','--period','8','--advance','2'],capture_output=True,text=True)
        path.with_suffix('.verify.txt').write_text(p.stdout+p.stderr);print(p.stdout.strip(),flush=True)
        certificate.append(dict(tiles=tiles,path=path.name,sha256=loaded.content_hash(),verify_exit=p.returncode))
    (HERE/'tile_certificate.json').write_text(json.dumps(certificate,indent=2))
    for tiles in (1,8):
        path=HERE/f'pull_chain_{tiles}tiles_pl11.flyer'
        p=subprocess.run([str(RUNNER),'samples',str(path),'--period','8','--advance','2','--out',str(path.with_suffix('.samples.csv'))],capture_output=True,text=True)
        path.with_suffix('.samples.txt').write_text(p.stdout+p.stderr);print(p.stdout.strip(),flush=True)

if __name__=='__main__':main()
