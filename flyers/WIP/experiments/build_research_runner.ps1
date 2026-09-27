$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$buildMessages = & cargo build --release --lib --message-format=json --manifest-path (Join-Path $repoRoot 'Cargo.toml')
if ($LASTEXITCODE -ne 0) { throw 'Release library build failed.' }
$researchLib = $buildMessages | ForEach-Object {
    $message = $_ | ConvertFrom-Json
    if ($message.reason -eq 'compiler-artifact' -and $message.target.name -eq 'fastflyer') {
        $message.filenames | Where-Object { $_ -like '*.rlib' }
    }
} | Select-Object -Last 1
if (-not $researchLib) { throw 'Cargo did not report a fastflyer release library.' }
$researchOutputDir = Join-Path $PSScriptRoot 'bin'
New-Item -ItemType Directory -Force -Path $researchOutputDir | Out-Null
$researchOutput = Join-Path $researchOutputDir 'research_runner.exe'
& rustc --edition=2021 -O (Join-Path $PSScriptRoot 'research_runner.rs') --extern "fastflyer=$researchLib" -L "dependency=$(Join-Path $repoRoot 'target/release/deps')" -o $researchOutput
if ($LASTEXITCODE -ne 0) { throw 'Research runner compilation failed.' }
Write-Output $researchOutput
