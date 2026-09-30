"""Test a five-cell target with a shared normal-recovery support contact."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    s=(HERE/'mixed_extension.py').read_text()
    start=s.index('            new=[]');end=s.index('            if not reason and any',start)
    replacement='''            # Target5 is connected before routing. Shared H3 contact carries
            # A in2/3/4 and B in3/4; B rides T in0. H2 carries the puller.
            ss[5].update(translate(p) for p in ((0,0,-1),(0,0,1),(0,1,-1),(0,1,0),(0,1,1)))
            ss[2].add(translate((3,0,0)));ss[3].add(translate((-1,0,0)));ss[4].add(translate((3,2,0)))
            new=[(translate((-1,0,1)),[0,0,0,1,2],0,5,False),(translate((-1,0,-1)),[0,1,1,1,2],1,5,False),(translate((3,1,0)),[0,1,1,1,2],2,5,True)]
            ps.extend(new)
            sources.extend([(translate((-1,1,1)),5,False),(translate((-1,1,-1)),5,True),(translate((4,2,0)),4,False)])
            legal=ns['make_legal'](ss,ps,sources)
            if not callable(legal):
                stats[legal[1]]+=1
                (HERE/'mixed_extension_compact_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2))
                continue
            reason=None
'''
    s=s[:start]+replacement+s[end:]
    s=s.replace('mixed_extension_candidates','mixed_extension_compact_candidates').replace('mixed_extension_manifest','mixed_extension_compact_manifest').replace('mixed_extension_screen','mixed_extension_compact_screen').replace('mixed_extension_legal.py','mixed_extension_compact_legal.py')
    # Avoid a doubled filename introduced by the generated explicit checkpoint.
    s=s.replace('mixed_extension_compact_compact_manifest','mixed_extension_compact_manifest')
    s=s.replace("if __name__=='__main__':main()",'');target=HERE/'derived_compact_mixed_extension.py';target.write_text(s);ns={'__file__':str(target)};exec(compile(s,str(target),'exec'),ns);ns['main']()
if __name__=='__main__':main()
