$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot

git -C (Join-Path $projectRoot "psxrecomp") apply `
    (Join-Path $projectRoot "patches\psxrecomp-einhander.patch")
git -C (Join-Path $projectRoot "recomp-ui") apply `
    (Join-Path $projectRoot "patches\recomp-ui-einhander.patch")

Write-Host "Einhänder framework patches applied."
