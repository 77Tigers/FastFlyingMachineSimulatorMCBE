$ErrorActionPreference = 'Stop'
$pullRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$pullMessages = & cargo build --release --lib --message-format=json --manifest-path (Join-Path $pullRoot 'Cargo.toml')
if ($LASTEXITCODE -ne 0) { throw 'Release library build failed.' }
$pullLibrary = $pullMessages | ForEach-Object {
    $pullMessage = $_ | ConvertFrom-Json
    if ($pullMessage.reason -eq 'compiler-artifact' -and $pullMessage.target.name -eq 'fastflyer') {
        $pullMessage.filenames | Where-Object { $_ -like '*.rlib' }
    }
} | Select-Object -Last 1
if (-not $pullLibrary) { throw 'Cargo did not report the release library.' }
& rustc --edition=2021 -O (Join-Path $PSScriptRoot 'verify.rs') --extern "fastflyer=$pullLibrary" -L "dependency=$(Join-Path $pullRoot 'target/release/deps')" -o (Join-Path $PSScriptRoot 'verify.exe')
if ($LASTEXITCODE -ne 0) { throw 'Verifier compilation failed.' }
