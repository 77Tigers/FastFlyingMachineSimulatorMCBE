# Run from the repository root. This uses the original generator and known winner
# parameters, so the candidate is a reference-assisted reconstruction.
$out = 'flyers/WIP/experiments/abstraction_trial_20260929/extraction'
python -c "from pathlib import Path; from flyers.WIP.experiments.astra_pullonly_20260927.pull_mwmw import make; f,_=make((1,-1,2),(0,1,-1),0,0,0); f.push_limit=10; f.save(Path('$out')/'candidate.flyer')"
if ($LASTEXITCODE -ne 0) { throw 'candidate generation failed' }

$runner = 'flyers/WIP/experiments/bin/research_runner.exe'
& $runner audit "$out/candidate.flyer" 160 8 | Set-Content "$out/audit_160.txt"
if ($LASTEXITCODE -ne 0) { throw '160-tick audit failed' }
& $runner audit "$out/candidate.flyer" 10000 8 | Set-Content "$out/audit_10000.txt"
if ($LASTEXITCODE -ne 0) { throw '10000-tick audit failed' }

Get-FileHash "$out/candidate.flyer" -Algorithm SHA256
Get-FileHash 'flyers/bank/pl10/pulling_alternating.flyer' -Algorithm SHA256
