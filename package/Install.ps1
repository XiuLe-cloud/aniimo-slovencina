param([string]$GamePath)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'UpdateTools.ps1')
Invoke-PayloadInstall $GamePath $PSScriptRoot
Write-Host 'Slovenčina bola nainštalovaná. V hre vyber English.'
