"""Prepare compact bank hardware and a current-engine research runner."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from fastflyer import Flyer, Kind

root = Path(__file__).resolve().parents[2]
out = root / '2way_bank' / 'seeds'
out.mkdir(exist_ok=True)
n = 0
for p in (root/'flyers/bank').rglob('*.flyer'):
    f = Flyer.load(p)
    if len(f.blocks()) <= 45 and len(f.blocks_of_type(Kind.PISTON)) <= 8:
        f.push_limit = 12
        f.save(out / (p.parent.name+'_'+p.stem+'.flyer'))
        n += 1
source = (root/'tools/src/bin/fastflyer-research.rs').read_text()
start = source.index('        let mut printed_power = false;')
end = source.index('            if let Some(m) = &step.info.movement', start)
source = source[:start] + '        for step in tr.steps {\n' + source[end:]
(root/'2way_bank/research/audit.rs').write_text(source)
print(f'Prepared {n} compact seeds; copied runner with obsolete power-overlay printing removed.')
