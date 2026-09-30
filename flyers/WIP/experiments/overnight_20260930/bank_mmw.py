"""Preserve the fully audited pattern-specific mmwmmw improvement."""
from pathlib import Path
import sys,csv,json,hashlib,re,shutil
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer
HERE=Path(__file__).resolve().parent
def main():
 source=HERE/'mmw_hex_trim_pl57.flyer';f=Flyer.load(source)
 samples=list(csv.DictReader(source.with_suffix('.samples.csv').open()))
 assert f.push_limit==57 and len(samples)==80
 assert {(int(r['rng']),int(r['phase_x']),int(r['phase_z'])) for r in samples}=={(r,x,z) for r in (0,1,2,5,42) for x in (0,7,8,15) for z in (0,7,8,15)}
 assert all(r['pass']=='true' and r['limit']=='57' and r['distance']=='3333' and r['boundaries']=='833' and r['initial_matches']=='833' and r['consecutive_matches']=='833' and all(r[k]=='0' for k in ('extension_failures','movement_failures','conservation_mismatch_ticks','displacement_mismatches')) for r in samples)
 audit=source.with_suffix('.audit.txt').read_text(encoding='utf-8-sig')
 assert all(t in audit for t in ('distance=3333 ','extension_failures=0 ','conservation_mismatch_ticks=0 ','max_successful_action=57 ','movement_failures=0'))
 target=ROOT/'flyers/bank/pl57/three_segment_mmwmmw.flyer';target.parent.mkdir(exist_ok=True);shutil.copyfile(source,target)
 relative=target.relative_to(ROOT).as_posix();digest=hashlib.sha256(target.read_bytes()).hexdigest()
 entry=dict(sha256=digest,ticks=10000,distance=3333,speed_bps=3.333,extensions=int(re.search(r'extensions=(\d+)',audit)[1]),extension_failures=0,endpoint_conserved=True,cycle_ticks=12,cycle_advance=4,full_rng_phase_samples=80,exact_block_owner_recurrence=True,max_successful_action=57,movement_words=['mmwmmw','wmmwmm','mwmmwm'])
 catalogue=ROOT/'flyers/bank/catalogue.json';data=json.loads(catalogue.read_text(encoding='utf-8'))
 if relative in data['entries']:assert data['entries'][relative]==entry
 else:
  raw=catalogue.read_bytes();index=raw.rfind(b'\n    }');assert index>=0
  ending=raw[index:].split(b'\n',2)[2]
  block='\n'.join('  '+line for line in json.dumps({relative:entry},indent=2).splitlines()[1:-1])
  catalogue.write_bytes(raw[:index]+b'\n    },\n'+block.encode()+b'\n'+ending)
 result=ROOT/'flyers/bank/results.csv';raw=result.read_bytes()
 if b'57,three_segment_mmwmmw,' not in raw:
  start=int(re.search(r'start_min_x=(-?\d+)',audit)[1]);end=int(re.search(r'end_min_x=(-?\d+)',audit)[1]);blocks=int(re.search(r'end_blocks=(\d+)',audit)[1])
  row=f'57,three_segment_mmwmmw,{start},{end},3333,{blocks},{entry["extensions"]}\n'.encode()
  result.write_bytes(raw+(b'' if raw.endswith(b'\n') else b'\n')+row)
 (HERE/'mmw_hex_trim_pl57.certificate.json').write_text(json.dumps(dict(bank_file=relative,**entry,evidence=['mmw_hex_trim_pl57.verify.txt','mmw_hex_trim_pl57.samples.csv','mmw_hex_trim_pl57.audit.txt','trim_mmw/geometry.json']),indent=2)+'\n',encoding='utf-8')
 print(relative,digest)
if __name__=='__main__':main()
