# Builds loadhist.rs against the current release rlib (same method as human_mcstructure_20261001/build_tools.ps1).
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$msgs = & cargo build --release --lib --message-format=json --manifest-path (Join-Path $repoRoot 'Cargo.toml')
if ($LASTEXITCODE -ne 0) { throw 'lib build failed' }
$lib = $msgs | ForEach-Object { $m = $_ | ConvertFrom-Json; if ($m.reason -eq 'compiler-artifact' -and $m.target.name -eq 'fastflyer') { $m.filenames | Where-Object { $_ -like '*.rlib' } } } | Select-Object -Last 1
& rustc --edition=2021 -O (Join-Path $PSScriptRoot 'loadhist.rs') --extern "fastflyer=$lib" -L "dependency=$(Join-Path $repoRoot 'target/release/deps')" -o (Join-Path $PSScriptRoot 'loadhist.exe')
if ($LASTEXITCODE -ne 0) { throw 'loadhist failed' }
