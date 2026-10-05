param([Parameter(Mandatory=$true)][string]$Fixture,[Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][string]$FeedBase)
$ErrorActionPreference='Stop'
trap { Write-Output $_.Exception.ToString(); Write-Output $_.ScriptStackTrace; exit 1 }
. (Join-Path $Package 'UpdateTools.ps1')
$results=[Collections.Generic.List[object]]::new()
function Pass([string]$Name){$results.Add(@{test=$Name;result='PASS'})}
function Reject([string]$Name,[scriptblock]$Action){$caught=$false;try{& $Action}catch{$caught=$true};if(!$caught){throw "Not rejected: $Name"};Pass $Name}
function global:Get-Process {param($Name,$ErrorAction) return $null}
$env:ANIIMO_SK_BACKUP_ROOT=Join-Path $Fixture 'backups'
$game=Join-Path $Fixture 'game';$lua=Join-Path $game 'Aniimo_Data/cvs/res/lua'
$trusted=Get-TrustedManifest
foreach($f in $trusted.sourceFiles.PSObject.Properties){Copy-Verified (Join-Path $Fixture ('originals/'+$f.Name)) (Get-GameFile $lua $f.Name) $f.Value}
[AniimoSafePath]::WriteText((Join-Path $game 'Aniimo.exe'),'FIXTURE ONLY')
[AniimoSafePath]::WriteText((Join-Path $game 'verlist.txt'),'3634150,test,0')
function OriginalBackups {
 $c=Get-InstallContext $game
 foreach($f in $trusted.sourceFiles.PSObject.Properties){if((Get-SHA256 (Join-Path $c.backup $f.Name)) -ne $f.Value){throw 'English backup changed'}}
}
function AssertEnglish {
 foreach($f in $trusted.sourceFiles.PSObject.Properties){if((Get-SHA256 (Get-GameFile $lua $f.Name)) -ne $f.Value){throw 'English restore differs'}}
}
$feed=Read-UpdateFeed ($FeedBase+'/version.json')
if($feed.translation_version -ne '0.06' -or $feed.game_build -ne '3634150'){throw 'Feed mismatch'}
Pass 'HTTP feed/metadata'
Invoke-OnlineUpdate $game ($FeedBase+'/version.json') '0.06'
if((Get-InstallContext $game).version -ne '0.06'){throw 'Clean install failed'}
OriginalBackups;Pass 'clean online 0.06 + English backup'
& (Join-Path $Package 'Restore.ps1') -GamePath $game
AssertEnglish;Pass 'clean install Restore English byte-identical'
Invoke-PayloadInstall $game (Join-Path $Fixture 'package-0.05')
$before=(Get-InstallContext $game).hashes
$stateBefore=Get-SHA256 (Join-Path (Get-BackupPath $game) 'translation-state.json')
function Unchanged {
 foreach($f in $trusted.sourceFiles.PSObject.Properties){if((Get-SHA256 (Get-GameFile $lua $f.Name)) -ne $before[$f.Name]){throw ('Partial update '+$f.Name)}}
 if((Get-InstallContext $game).version -ne '0.05'){throw 'Version changed'}
 if((Get-SHA256 (Join-Path (Get-BackupPath $game) 'translation-state.json')) -ne $stateBefore){throw 'State differs'}
 OriginalBackups
}
Reject 'SHA-256 mismatch' {Invoke-OnlineUpdate $game ($FeedBase+'/bad-hash.json') '0.06'};Unchanged
Reject 'corrupt ZIP with valid transport hash' {Invoke-OnlineUpdate $game ($FeedBase+'/corrupt.json') '0.06'};Unchanged
Reject 'tampered payload with valid ZIP hash' {Invoke-OnlineUpdate $game ($FeedBase+'/tampered.json') '0.06'};Unchanged
Reject 'invalid feed' {Read-UpdateFeed ($FeedBase+'/invalid.json')};Unchanged
Reject 'wrong game build' {Invoke-OnlineUpdate $game ($FeedBase+'/wrong-build.json') '0.06'};Unchanged
Reject 'feed/package version mismatch' {Invoke-OnlineUpdate $game ($FeedBase+'/wrong-version.json') '0.07'};Unchanged
Reject 'ZIP traversal' {Expand-DataPackage (Join-Path $Fixture 'web/traversal.zip') (Join-Path $Fixture 'traversal-output')};Unchanged
Reject 'ZIP incomplete allowlist' {Expand-DataPackage (Join-Path $Fixture 'web/incomplete.zip') (Join-Path $Fixture 'incomplete-output')};Unchanged
$realCopy=${function:Copy-Verified};$script:injected=$false;$script:writes=0
function Copy-Verified([string]$Source,[string]$Destination,[string]$Hash){
 & $realCopy $Source $Destination $Hash
 if($Source -like '*\stage\*' -and $Destination.StartsWith($game) -and !$script:injected){$script:writes++;if($script:writes -eq 3){$script:injected=$true;throw 'SIMULATED WRITE FAILURE'}}
}
Reject 'injected mid-write failure' {Invoke-OnlineUpdate $game ($FeedBase+'/version.json') '0.06'}
${function:Copy-Verified}=$realCopy
if(!$script:injected){throw 'Rollback not exercised'}
Unchanged;Pass 'rollback byte-identical files + metadata + original backups'
# Exact junction reproduction: valid allowed ZIP, pre-existing data junction.
$outside=Join-Path $Fixture 'outside';$dest=Join-Path $Fixture 'junction-output'
New-Item -ItemType Directory -Path $outside,$dest | Out-Null
New-Item -ItemType Junction -Path (Join-Path $dest 'data') -Target $outside | Out-Null
Reject 'original 1.3 extraction junction reproduction' {Expand-DataPackage (Join-Path $Fixture 'web/package.zip') $dest}
if(@(Get-ChildItem $outside -Recurse -File).Count -ne 0){throw 'Outside write'}
Reject 'copy through junction' {Copy-Verified (Join-Path $Fixture 'web/version.json') (Join-Path $dest 'data/test.json') (Get-SHA256 (Join-Path $Fixture 'web/version.json'))}
Reject 'backup path junction' { [AniimoSafePath]::WriteText((Join-Path $dest 'data/receipt.json'),'test') }
Reject 'rollback/restore copy junction' {Copy-Safe (Join-Path $Fixture 'web/version.json') (Join-Path $dest 'data/test.json')}
Reject 'cleanup junction' {Remove-WorkDirectory $dest $Fixture}
Reject 'archive move junction' {Archive-Backup (Join-Path $dest 'data')}
$link=Join-Path $Fixture 'hardlink.json';$sentinel=Join-Path $outside 'sentinel.json'
[IO.File]::WriteAllText($sentinel,'UNCHANGED')
New-Item -ItemType HardLink -Path $link -Target $sentinel | Out-Null
Reject 'hardlink overwrite' {[AniimoSafePath]::WriteText($link,'BAD')}
if([IO.File]::ReadAllText($sentinel) -ne 'UNCHANGED'){throw 'Hardlink target modified'}
Reject 'ADS path' {[AniimoSafePath]::WriteText(($sentinel+':stream'),'BAD')}
Reject 'lexical parent traversal' {[AniimoSafePath]::Within($dest,(Join-Path $dest '../outside/bad'))}
$symlink=Join-Path $Fixture 'symlink-output'
try {New-Item -ItemType SymbolicLink -Path $symlink -Target $outside -ErrorAction Stop | Out-Null;$symlinkCreated=$true}catch{$symlinkCreated=$false}
if($symlinkCreated){Reject 'directory symlink' {[AniimoSafePath]::WriteText((Join-Path $symlink 'bad'),'BAD')}}else{$results.Add(@{test='directory symlink';result='NOT_RUN';reason='Windows privilege/developer mode unavailable'})}
# Ancestor handles remain pinned while the output stream is open.
$pinDir=Join-Path $Fixture 'pinned';$stream=[AniimoSafePath]::OpenWrite((Join-Path $pinDir 'x'),$false,$true)
try{Reject 'ancestor rename while writing' {Move-Item -LiteralPath $pinDir -Destination ($pinDir+'-moved') -ErrorAction Stop}}finally{$stream.Dispose()}
Invoke-OnlineUpdate $game ($FeedBase+'/version.json') '0.06'
if((Get-InstallContext $game).version -ne '0.06'){throw 'Update to 0.06 failed'}
OriginalBackups;Pass '0.05 -> 0.06'
# Check the actual status decision code; substitute only the feed address in an isolated copy.
$statusDir=Join-Path $Fixture 'status-copy'
New-Item -ItemType Directory -Path $statusDir|Out-Null
foreach($f in Get-ChildItem -LiteralPath $Package -File){Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $statusDir $f.Name)}
$statusSource=[IO.File]::ReadAllText((Join-Path $Package 'Status.ps1'))
$statusSource=$statusSource.Replace('$url=Get-FeedUrl',('$url='''+$FeedBase+'/future.json'''))
[IO.File]::WriteAllText((Join-Path $statusDir 'Status.ps1'),$statusSource,[Text.UTF8Encoding]::new($true))
$status= & (Join-Path $statusDir 'Status.ps1') -GamePath $game | ConvertFrom-Json
if(!$status.canUpdate -or $status.onlineVersion -ne '0.07' -or $status.installed -ne '0.06'){throw 'Status did not offer future update'}
Pass 'Status GUI decision offers 0.07 over 0.06 (loopback feed injection)'
$next=Read-UpdateFeed ($FeedBase+'/future.json')
if([version]$next.translation_version -le [version](Get-InstallContext $game).version){throw 'Future detection failed'}
Invoke-OnlineUpdate $game ($FeedBase+'/future.json') '0.07'
if((Get-InstallContext $game).version -ne '0.07'){throw 'Future update failed'}
OriginalBackups;Pass 'simulated 0.06 -> 0.07 same installer'
# Reparse redirect in the actual game path must block Restore before any replacement.
$gameI18N=Join-Path $lua 'LuaScripts/Data/I18N'
$savedI18N=Join-Path $Fixture 'outside-game-I18N'
$savedHash=Get-SHA256 (Join-Path $gameI18N 'Compress_en.bin')
[AniimoSafePath]::MoveDirectory($gameI18N,$savedI18N)
New-Item -ItemType Junction -Path $gameI18N -Target $savedI18N|Out-Null
Reject 'full Restore English through game junction' {& (Join-Path $Package 'Restore.ps1') -GamePath $game}
Reject 'full install through game junction' {Invoke-PayloadInstall $game $Package}
if((Get-SHA256 (Join-Path $savedI18N 'Compress_en.bin')) -ne $savedHash){throw 'Outside-game file modified'}
# Delete only this fixture link, never its target or user data; both paths verified below.
if(!$gameI18N.StartsWith($Fixture+'\') -or !$savedI18N.StartsWith($Fixture+'\')){throw 'Fixture containment failed'}
[IO.Directory]::Delete($gameI18N)
[AniimoSafePath]::MoveDirectory($savedI18N,$gameI18N)
& (Join-Path $Package 'Restore.ps1') -GamePath $game
AssertEnglish;Pass 'Restore English after future update byte-identical'
Invoke-PayloadInstall $game $Package
if((Get-InstallContext $game).version -ne '0.06'){throw 'Offline payload install failed'}
Pass 'clean bundled/offline 0.06'
& (Join-Path $Package 'Restore.ps1') -GamePath $game
AssertEnglish;Pass 'offline Restore English byte-identical'
if(@(Get-ChildItem -LiteralPath $outside -Recurse -File).Count -ne 1 -or [IO.File]::ReadAllText($sentinel) -ne 'UNCHANGED'){throw 'Unexpected outside write'}
@{tests=@($results.ToArray());outside_writes=0;fixture_only=$true}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $Fixture 'result.json') -Encoding UTF8
