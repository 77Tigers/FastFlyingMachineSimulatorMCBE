"""Preserve the successful extension's sparse contacts before driver routing."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    s=(HERE/'mixed_extension.py').read_text()
    s=s.replace('for delta in ((0,12,0),(0,15,0),(0,0,15)):', 'for delta in ((0,12,0),):').replace('for seed in range(8):','for seed in (1,):')
    s=s.replace('            for i in [5]+rng.sample(range(5),5):', '''            assert reason is None,reason
            patches=[ss[i]-set(map(tuple,M['segments'][i])) for i in range(5)]+[ss[5]]
            (HERE/'mixed_tile_contact_cover.json').write_text(json.dumps(dict(delta=delta,seed=seed,patches=[sorted(p) for p in patches],counts=list(map(len,patches)),pistons=ps[-3:],sources=sources[-3:]),indent=2))
            print('sparse contact counts',list(map(len,patches)),flush=True)
            return
            for i in [5]+rng.sample(range(5),5):''')
    s=s.replace("if __name__=='__main__':main()",'')
    ns={'__file__':str(HERE/'mixed_extension.py')};exec(compile(s,str(HERE/'mixed_extension.py'),'exec'),ns);ns['main']()
if __name__=='__main__':main()
