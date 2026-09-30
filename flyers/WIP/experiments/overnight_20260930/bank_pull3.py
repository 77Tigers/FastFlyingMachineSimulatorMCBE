"""Bank a fully audited pure-pull3bps candidate; never accept a partial audit."""
from pathlib import Path
import sys,json,csv,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
def main():
    source=Path(sys.argv[1]);f=Flyer.load(source);limit=f.push_limit
    pistons=[b for b in f._cells.values() if b.kind==Kind.PISTON]
    assert len(pistons)==30 and all(b.sticky and b.direction==1 for b in pistons)
    rows=list(csv.DictReader(source.with_suffix('.samples.csv').open()))
    required={(r,x,z) for r in (0,1,2,5,42) for x in (0,7,8,15) for z in (0,7,8,15)}
    assert len(rows)==80 and {(int(r['rng']),int(r['phase_x']),int(r['phase_z'])) for r in rows}==required
    assert all(r['pass']=='true' and int(r['limit'])==limit and r['distance']=='3000' and all(r[k]=='1000' for k in ('boundaries','initial_matches','consecutive_matches')) and all(r[k]=='0' for k in ('extension_failures','movement_failures','conservation_mismatch_ticks','displacement_mismatches')) and int(r['max_successful_action'])<=limit for r in rows)
    verify=source.with_suffix('.verify.txt').read_text(encoding='utf-8-sig');audit=source.with_suffix('.audit.txt').read_text(encoding='utf-8-sig')
    assert all(t in verify for t in ('pass=true ','ticks=10000 ','distance=3000 ','boundaries=1000 ','initial_matches=1000 ','consecutive_matches=1000 '))
    expected=dict(limit=limit,ticks=10000,distance=3000,extension_failures=0,movement_failures=0,conservation_mismatch_ticks=0,max_successful_action=limit)
    assert all(re.search(r'\b'+key+'='+str(value)+r'(?=\s|$)',audit) for key,value in expected.items())
    target=ROOT/f'flyers/bank/pl{limit}/pulling3_tenbody.flyer';target.parent.mkdir(exist_ok=True);shutil.copyfile(source,target);relative=target.relative_to(ROOT).as_posix();digest=hashlib.sha256(target.read_bytes()).hexdigest()
    entry=dict(sha256=digest,ticks=10000,distance=3000,speed_bps=3.0,extensions=int(re.search(r'extensions=(\d+)',audit)[1]),extension_failures=0,endpoint_conserved=True,cycle_ticks=10,cycle_advance=3,full_rng_phase_samples=80,exact_block_owner_recurrence=True,max_successful_action=limit,pulling_only=True,pistons=30,piston_direction='-X',sticky_pistons_only=True)
    catalogue=ROOT/'flyers/bank/catalogue.json';data=json.loads(catalogue.read_text())
    if relative in data['entries']:assert data['entries'][relative]==entry
    else:
        raw=catalogue.read_bytes();index=raw.rfind(b'\n    }');assert index>=0;ending=raw[index:].split(b'\n',2)[2];block='\n'.join('  '+line for line in json.dumps({relative:entry},indent=2).splitlines()[1:-1]);catalogue.write_bytes(raw[:index]+b'\n    },\n'+block.encode()+b'\n'+ending)
    results=ROOT/'flyers/bank/results.csv';raw=results.read_bytes()
    if f'{limit},pulling3_tenbody,'.encode() not in raw:
        start=int(re.search(r'start_min_x=(-?\d+)',audit)[1]);end=int(re.search(r'end_min_x=(-?\d+)',audit)[1]);blocks=int(re.search(r'end_blocks=(\d+)',audit)[1]);results.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+f'{limit},pulling3_tenbody,{start},{end},3000,{blocks},{entry["extensions"]}\n'.encode())
    source.with_suffix('.certificate.json').write_text(json.dumps(dict(bank_file=relative,**entry,evidence=[source.with_suffix('.verify.txt').name,source.with_suffix('.audit.txt').name,source.with_suffix('.samples.csv').name]),indent=2)+'\n')
    print(relative,digest)
if __name__=='__main__':main()
