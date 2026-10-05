param([string]$GamePath)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'PackageTools.ps1')
Assert-GameClosed
$GamePath = Resolve-Game $GamePath
$parent=[IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath))
[AniimoSafePath]::DirectorySafe($parent)|Out-Null
$operationLock=[AniimoSafePath]::OpenWrite((Join-Path $parent 'operation.lock'),$true,$false)
try {
if(Test-Path -LiteralPath (Join-Path $parent 'pending.json')){throw 'Najprv obnov prerušenú operáciu.'}
$lua = Join-Path $GamePath 'Aniimo_Data\cvs\res\lua'
$backup = Get-BackupPath $GamePath
[AniimoSafePath]::ValidateTree($backup)
$receipt = Get-Content -LiteralPath (Join-Path $backup 'receipt.json') -Raw | ConvertFrom-Json
$allowed = @('LuaScripts.xdf','LuaScripts.xdt','LuaCacheVer.txt','LuaScripts/Data/I18N/Compress_en.bin','builtin/LuaScripts.xdf','builtin/LuaScripts.xdt','fonts/xgui_font_94caf04d33b30d3bf95fff3d59018c81.uab','fonts/xgui_font_asset_0_7c59a01880d83ee3f861970de35c3ce3.uab','fonts/xpt21_ar_resx_04a564c8_xgui_font_0_9b0f7d72fb917cb12ac86710360d45c8.uab','fonts/xpt21_mres_exall_0_56f2e8c16cb439a06833bfae669c0e6c.uab','fonts/xpt22_mres_exall_0_9fd11bcc7e5149929c8fc6622a551ae9.uab','boot/resources.assets.resS')
if (@($receipt).Count -notin @(4,6,8,10,12) -or @($receipt.path | Select-Object -Unique).Count -ne @($receipt).Count) { throw 'Neplatny zaznam zalohy.' }
foreach ($file in $receipt) {
    if ($file.path -notin $allowed) { throw 'Neplatna cesta v zalohe.' }
    if ((Get-SHA256 (Join-Path $backup $file.path)) -ne $file.original) { throw 'Zaloha je poskodena.' }
    $hash = Get-SHA256 (Get-GameFile $lua $file.path)
    if ($hash -ne $file.patched -and $hash -ne $file.original) {
        throw 'Hra bola medzicasom aktualizovana. Stara zaloha sa neobnovi. Pouzi overenie suborov hry v Steame.'
    }
}
foreach ($file in $receipt) {
    Copy-Safe -LiteralPath (Join-Path $backup $file.path) -Destination (Get-GameFile $lua $file.path) -Force
    if ((Get-SHA256 (Get-GameFile $lua $file.path)) -ne $file.original) { throw 'Obnovenie suboru sa nepodarilo.' }
}
$archive = Archive-Backup $backup
Write-Host 'Povodne anglicke subory boli obnovene.'
Write-Host "Kopia zalohy zostala v: $archive"

} finally { $operationLock.Dispose() }
