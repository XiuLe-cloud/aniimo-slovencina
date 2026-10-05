param([ValidateSet('install','restore','update','recover')][string]$Mode='install',[string]$GamePath,[switch]$NonInteractive,[string]$ExpectedVersion)
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$ErrorActionPreference='Stop'
$result=0
try {
    if($Mode -eq 'restore'){& (Join-Path $PSScriptRoot 'Restore.ps1') -GamePath $GamePath}
    elseif($Mode -eq 'install'){& (Join-Path $PSScriptRoot 'Install.ps1') -GamePath $GamePath}
    else{
        . (Join-Path $PSScriptRoot 'UpdateTools.ps1')
        if($Mode -eq 'update'){Invoke-OnlineUpdate $GamePath '' $ExpectedVersion}
        else{
            Assert-GameClosed
            $parent=[IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath));$lock=[AniimoSafePath]::OpenWrite((Join-Path $parent 'operation.lock'),$true,$false)
            try{$pending=Join-Path $parent 'pending.json';$j=Get-Content -LiteralPath $pending -Raw|ConvertFrom-Json;Restore-Transaction $GamePath $pending;Remove-WorkDirectory $j.work $parent}finally{$lock.Dispose()}
        }
    }
}catch{Write-Host $_.Exception.Message;$result=1}
if($result -ne 0 -and !$NonInteractive){Read-Host 'Stlac Enter na zatvorenie okna'|Out-Null}
exit $result
