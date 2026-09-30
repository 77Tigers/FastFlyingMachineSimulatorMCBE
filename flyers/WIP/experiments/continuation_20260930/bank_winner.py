"""Bank only after the saved full audit establishes the research contract."""
from pathlib import Path
import sys,csv,json,hashlib,shutil,re
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from fastflyer import Flyer,Kind
HERE=Path(__file__).resolve().parent

def main():
 source=HERE/'pulling_loop4_pl9.flyer';f=Flyer.load(source)
 rows=list(csv.DictReader((HERE/'pulling_loop4_pl9.samples.csv').open()))
 assert len(rows)==80 and {(int(r['rng']),int(r['phase_x']),int(r['phase_z'])) for r in rows}=={(r,x,z) for r in (0,1,2,5,42) for x in (0,7,8,15) for z in (0,7,8,15)}
 assert all(r['pass']=='true' and r['limit']=='9' and r['distance']=='2500' and r['boundaries']=='1250' and r['initial_matches']=='1250' and r['consecutive_matches']=='1250' and r['displacement_mismatches']=='0' and r['max_successful_action']=='9' and all(r[k]=='0' for k in ('extension_failures','movement_failures','conservation_mismatch_ticks')) for r in rows)
 assert f.push_limit==9 and all(b.sticky and b.direction==1 for b in f._cells.values() if b.kind==Kind.PISTON)
 audit=(HERE/'pulling_loop4_pl9.audit.txt').read_text(encoding='utf-8-sig')
 assert all(s in audit for s in ('distance=2500 ','extensions=10000 ','extension_failures=0 ','conservation_mismatch_ticks=0 ','max_successful_action=9 ','movement_failures=0'))
 destination=ROOT/'flyers/bank/pl9/pulling_loop4.flyer';destination.parent.mkdir(exist_ok=True);shutil.copyfile(source,destination)
 digest=hashlib.sha256(destination.read_bytes()).hexdigest();relative=destination.relative_to(ROOT).as_posix()
 catalogue=ROOT/'flyers/bank/catalogue.json';data=json.loads(catalogue.read_text(encoding='utf-8'))
 entry=dict(sha256=digest,ticks=10000,distance=2500,speed_bps=2.5,extensions=10000,extension_failures=0,endpoint_conserved=True,cycle_ticks=8,cycle_advance=2,full_rng_phase_samples=80,exact_block_owner_recurrence=True,max_successful_action=9)
 if relative in data['entries']:
  assert data['entries'][relative]==entry
 else:
  raw=catalogue.read_bytes();index=raw.rfind(b'\n    }');assert index>=0
  ending=raw[index:].split(b'\n',2)[2]
  block='\n'.join('  '+line for line in json.dumps({relative:entry},indent=2).splitlines()[1:-1])
  catalogue.write_bytes(raw[:index]+b'\n    },\n'+block.encode()+b'\n'+ending)
 results=ROOT/'flyers/bank/results.csv'
 with results.open(newline='',encoding='utf-8') as reader:reader=csv.DictReader(reader);columns=reader.fieldnames;existing=list(reader)
 existing=[r for r in existing if not (r['push_limit']=='9' and r['name']=='pulling_loop4')]
 start=int(re.search(r'start_min_x=(-?\d+)',audit)[1]);end=int(re.search(r'end_min_x=(-?\d+)',audit)[1])
 existing.append(dict(push_limit=9,name='pulling_loop4',start_min_x=start,end_min_x=end,distance=2500,end_blocks=38,extensions=10000))
 # Preserve existing evidence rows and their original line endings.
 raw=results.read_bytes();lines=raw.splitlines(keepends=True)
 lines=[line for line in lines if not line.startswith(b'9,pulling_loop4,')]
 row=f'9,pulling_loop4,{start},{end},2500,38,10000\n'.encode()
 results.write_bytes(b''.join(lines)+(b'' if not lines or lines[-1].endswith(b'\n') else b'\n')+row)
 certificate=dict(bank_file=relative,sha256=digest,generator='build_pull_winner.py',period_ticks=8,translation_x=2,push_limit=9,ticks=10000,distance=2500,speed_bps=2.5,full_rng_phase_samples=80,exact_block_owner_boundaries_per_sample=1250,max_successful_action=9,all_pistons_sticky_facing_minus_x=True,permanent_kinds={k.name:sum(b.kind==k for b in f._cells.values()) for k in (Kind.SLIME,Kind.HONEY,Kind.OBSERVER,Kind.PISTON)},evidence=['pulling_loop4_pl9.verify.txt','pulling_loop4_pl9.samples.csv','pulling_loop4_pl9.audit.txt'])
 (HERE/'pulling_loop4_pl9.certificate.json').write_text(json.dumps(certificate,indent=2)+'\n',encoding='utf-8');print(relative,digest)

if __name__=='__main__':main()
