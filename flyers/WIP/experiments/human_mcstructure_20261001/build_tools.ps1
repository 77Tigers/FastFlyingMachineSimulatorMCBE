# Builds ledger.rs against the current release rlib (same method as build_research_runner.ps1).
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$msgs = & cargo build --release --lib --message-format=json --manifest-path (Join-Path $repoRoot 'Cargo.toml')
if ($LASTEXITCODE -ne 0) { throw 'lib build failed' }
$lib = $msgs | ForEach-Object { $m = $_ | ConvertFrom-Json; if ($m.reason -eq 'compiler-artifact' -and $m.target.name -eq 'fastflyer') { $m.filenames | Where-Object { $_ -like '*.rlib' } } } | Select-Object -Last 1
$out = Join-Path $PSScriptRoot '../bin'
New-Item -ItemType Directory -Force -Path $out | Out-Null
foreach ($t in 'ledger','bodytrack','snapshot') {
  & rustc --edition=2021 -O (Join-Path $PSScriptRoot "$t.rs") --extern "fastflyer=$lib" -L "dependency=$(Join-Path $repoRoot 'target/release/deps')" -o (Join-Path $out "human_$t.exe")
  if ($LASTEXITCODE -ne 0) { throw "$t failed" }
}
