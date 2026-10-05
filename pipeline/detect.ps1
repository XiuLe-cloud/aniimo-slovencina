param([Parameter(Mandatory=$true)][string]$GamePath)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../package/UpdateTools.ps1')
Get-GameBuild $GamePath
