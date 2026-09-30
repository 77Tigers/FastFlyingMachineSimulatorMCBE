"""Reuse the realized extension workflow for the six-slot mmwmmw contract."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def main():
    g=json.loads((HERE/'trim_mmw/geometry.json').read_text());order=[i for i,p in enumerate(g['pistons']) if p[3]==0]+[i for i,p in enumerate(g['pistons']) if p[3]!=0]
    prepared=dict(segments=g['segments'],pistons=[g['pistons'][i]+[False] for i in order],sources=[g['sources'][i] for i in order]);(HERE/'mmw_extension_core.json').write_text(json.dumps(prepared,indent=2))
    s=(HERE/'mixed_extension.py').read_text()
    s=s.replace("HERE/'derived_mixed3_compact_v3.py'","HERE/'derived_mmw.py'")
    mline=next(line for line in s.splitlines() if line.startswith('M=next('));s=s.replace(mline,"M=json.loads((HERE/'mmw_extension_core.json').read_text())")
    old="source=(HERE/'derived_mmw.py').read_text();snippet=source[source.index(' fixed=[]'):source.index(' if any(not legal')]"
    replacement="source=(HERE/'mixed_extension_legal.py').read_text();snippet=source.split('def make_legal(ss,ps,sources):\\n',1)[1].rsplit(' return legal\\n',1)[0];snippet=snippet.replace('range(5)','range(6)').replace('%'+str(5),'%'+str(6))"
    assert old in s;s=s.replace(old,replacement)
    s=s.replace('POWER=(1,0),POWER_DIR=3','POWER=(0,1),POWER_DIR=5')
    s=s.replace('model.S+[model.S[0]]','list(model.S)+[model.S[0]]').replace('model.K+[model.K[0]]','list(model.K)+[model.K[0]]')
    s=s.replace("M['pistons'][:3]","M['pistons'][:4]").replace("M['sources'][:3]","M['sources'][:4]")
    s=s.replace('(translate(pp),dp,f,5,sticky)','(translate(pp),dp,f,3,sticky)').replace('ss[5]','ss[3]').replace('5 if owner==0','3 if owner==0')
    s=s.replace('for t in range(5)','for t in range(6)').replace('%5','%6').replace('for i in [5]+rng.sample(range(5),5):','for i in [3]+rng.sample(range(3),3):').replace('i==5','i==3')
    s=s.replace('Block.observer(3,','Block.observer(5,').replace("ns['S'][owner][4]","ns['S'][owner][5]")
    s=s.replace('mixed_extension_candidates','mmw_extension_candidates').replace('mixed_extension_manifest','mmw_extension_manifest').replace('mixed_extension_screen','mmw_extension_screen').replace('mixed_extension_legal.py','mmw_extension_legal.py')
    # The extraction input is the already tested mixed checker, not this new output.
    s=s.replace("source=(HERE/'mmw_extension_legal.py').read_text()","source=(HERE/'mixed_extension_legal.py').read_text()")
    s=s.replace("if not callable(legal):stats['cross_power']+=1;continue", "if not callable(legal):\n                stats[legal[1]]+=1\n                (HERE/'mmw_extension_manifest.json').write_text(json.dumps(dict(stats=stats,candidates=manifest,delta=delta,next_seed=seed+1),indent=2))\n                continue")
    s=s.replace("if __name__=='__main__':main()",'');target=HERE/'derived_mmw_extension.py';target.write_text(s);ns={'__file__':str(target)};exec(compile(s,str(target),'exec'),ns);ns['main']()
if __name__=='__main__':main()
