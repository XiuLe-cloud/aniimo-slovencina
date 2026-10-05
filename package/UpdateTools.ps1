# Trusted updater engine. Downloaded packages contain data only, never scripts.
. (Join-Path $PSScriptRoot 'PackageTools.ps1')
function Get-TrustedManifest { return (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json) }
function Get-GameBuild([string]$GamePath) {
    $ver = Join-Path $GamePath 'verlist.txt'
    if (Test-Path -LiteralPath $ver) {
        $value = (Get-Content -LiteralPath $ver -Raw).Split(',')[0].Trim()
        if ($value -match '^\d+$') { return $value }
        throw 'Neznámy formát verzie ANIIMO.'
    }
    $cache = Get-Content -LiteralPath (Join-Path $GamePath 'Aniimo_Data\cvs\res\lua\LuaCacheVer.txt') -Raw
    if ($cache -match '^1\.0\.(\d+),') { return $Matches[1] }
    throw 'Nepodarilo sa zistiť zostavu ANIIMO.'
}
function Assert-Build([string]$GamePath,[string]$Build) {
    $actualBuild=Get-GameBuild $GamePath
    if ($actualBuild -ne $Build) { throw ('Zostava hry '+$actualBuild+' nie je podporovaná. Preklad je overený pre '+$Build+'. Súbory sa nezmenili.') }
}
function Remove-WorkDirectory([string]$Path,[string]$Parent) {
    $full=[IO.Path]::GetFullPath($Path); $prefix=[IO.Path]::GetFullPath($Parent).TrimEnd('\')+'\'
    if (!$full.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or $full -eq $prefix.TrimEnd('\')) { throw 'Neplatný dočasný priečinok.' }
    if (Test-Path -LiteralPath $full) { [AniimoSafePath]::DeleteTree($full,$Parent) }
}
function Get-InstallContext([string]$GamePath) {
    [AniimoSafePath]::Validate($GamePath)
    $trusted=Get-TrustedManifest; Assert-Build $GamePath ([string]$trusted.gameBuild)
    $lua=Join-Path $GamePath 'Aniimo_Data\cvs\res\lua'; $backup=Get-BackupPath $GamePath
    $receipt=@();$hashes=@{};$originalSources=@{};$migrating=$false;$pristine=$true
    foreach($f in $trusted.sourceFiles.PSObject.Properties) {
        $hashes[$f.Name]=Get-SHA256 (Get-GameFile $lua $f.Name)
        if($hashes[$f.Name] -ne $f.Value){$pristine=$false}
    }
    if(Test-Path -LiteralPath (Join-Path $backup 'receipt.json')) {
        $receipt=Get-Content -LiteralPath (Join-Path $backup 'receipt.json') -Raw | ConvertFrom-Json
        if(@($receipt).Count -notin @(4,6,8,10,12) -or @($receipt.path | Select-Object -Unique).Count -ne @($receipt).Count){throw 'Neplatný záznam pôvodnej zálohy.'}
        foreach($f in $receipt){
            if(!$hashes.ContainsKey($f.path)){throw 'Neplatná cesta v zálohe.'}
            if($f.original -ne $trusted.sourceFiles.($f.path) -or (Get-SHA256 (Join-Path $backup $f.path)) -ne $f.original){throw 'Pôvodná anglická záloha je poškodená alebo patrí inej zostave.'}
            if($hashes[$f.path] -notin @($f.original,$f.patched)){throw 'Herné súbory sa zmenili. Aktualizácia bola zastavená.'}
        }
        foreach($f in $trusted.sourceFiles.PSObject.Properties){if($f.Name -notin $receipt.path -and $hashes[$f.Name] -ne $f.Value){throw 'Neznáme zmenené herné súbory.'}}
     } elseif(!$pristine){
        # The game update may retain byte-identical font/texture patches from 0.02.
        # Only accept an exact trusted payload and an independently verified original.
        foreach($f in $trusted.sourceFiles.PSObject.Properties){
            if($hashes[$f.Name] -eq $f.Value){continue}
            if(!$f.Name.StartsWith('fonts/') -and !$f.Name.StartsWith('boot/')){throw 'Neznáme zmenené herné súbory.'}
            $payloadName=[IO.Path]::GetFileName($f.Name)
            if($hashes[$f.Name] -ne $trusted.payloadFiles.$payloadName){throw 'Neznáme zmenené písmo alebo obrázok.'}
            foreach($previous in (Get-PreviousBackupPaths $GamePath)){
                $original=Join-Path $previous $f.Name
                if((Test-Path -LiteralPath $original) -and (Get-SHA256 $original) -eq $f.Value){$originalSources[$f.Name]=$original;break}
            }
            if(!$originalSources.ContainsKey($f.Name)){throw 'Chýba overená anglická záloha zachovaných úprav. Over súbory hry v Steame.'}
        }
        $migrating=$true
    }
    $version=$null
    if(!$pristine){
        $statePath=Join-Path $backup 'translation-state.json'
        if(Test-Path -LiteralPath $statePath){
            $state=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
            if($state.receipt_sha256 -eq (Get-SHA256 (Join-Path $backup 'receipt.json')) -and $state.text_sha256 -eq $hashes['LuaScripts/Data/I18N/Compress_en.bin']){$version=[string]$state.translation_version}
        }
        if(!$version -and $hashes['LuaScripts/Data/I18N/Compress_en.bin'] -eq $trusted.payloadFiles.'Compress_en.bin'){$version=[string]$trusted.translationVersion}
    }
    if($migrating){$version=$null}
    return @{lua=$lua;backup=$backup;receipt=$receipt;hashes=$hashes;pristine=$pristine;version=$version;migrating=$migrating;originalSources=$originalSources}
}
function Assert-Payload([string]$Root) {
    $trusted=Get-TrustedManifest
    $m=Get-Content -LiteralPath (Join-Path $Root 'manifest.json') -Raw | ConvertFrom-Json
    if([string]$m.translationVersion -notmatch '^\d+\.\d+(\.\d+)?$'){throw 'Neplatné číslo verzie prekladu.'}
    if([string]$m.gameBuild -ne [string]$trusted.gameBuild){throw 'Balík nie je kompatibilný s touto zostavou ANIIMO.'}
    foreach($section in @('sourceFiles','payloadFiles')){
        $expected=@($trusted.$section.PSObject.Properties.Name);$actual=@($m.$section.PSObject.Properties.Name)
        if($expected.Count -ne $actual.Count -or @($actual | Where-Object {$_ -notin $expected}).Count){throw 'Balík obsahuje nepovolené súbory.'}
    }
    foreach($f in $trusted.sourceFiles.PSObject.Properties){if($m.sourceFiles.($f.Name) -ne $f.Value){throw 'Balík má nekompatibilný základ hry.'}}
    foreach($f in $m.payloadFiles.PSObject.Properties){
        if($f.Value -notmatch '^[a-fA-F0-9]{64}$' -or (Get-SHA256 (Join-Path $Root ('data\'+$f.Name))) -ne $f.Value){throw 'Kontrolný súčet súboru v balíku nesedí. Aktualizácia bola zrušená.'}
    }
    return $m
}
function Copy-Verified([string]$Source,[string]$Destination,[string]$Hash) {
    [AniimoSafePath]::DirectorySafe([IO.Path]::GetDirectoryName($Destination)) | Out-Null
    Copy-Safe -LiteralPath $Source -Destination $Destination -Force
    if((Get-SHA256 $Destination) -ne $Hash){throw 'Kontrola zápisu súboru zlyhala.'}
}
function Invoke-PayloadInstall([string]$GamePath,[string]$PayloadRoot) {
    Assert-GameClosed; $GamePath=Resolve-Game $GamePath
    $parent=[IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath))
    [AniimoSafePath]::DirectorySafe($parent) | Out-Null
    $lock=$null;$work=$null;$keep=$false
    try {
        try {$lock=[AniimoSafePath]::OpenWrite((Join-Path $parent 'operation.lock'),$true,$false)}catch{throw 'Pre túto hru už prebieha iná operácia.'}
        $pending=Join-Path $parent 'pending.json'
        if(Test-Path -LiteralPath $pending){throw 'Predchádzajúca operácia bola prerušená. Najprv použi Obnoviť prerušenú operáciu.'}
        [AniimoSafePath]::ValidateTree($PayloadRoot)
        $m=Assert-Payload $PayloadRoot; Assert-Build $GamePath ([string]$m.gameBuild)
        $c=Get-InstallContext $GamePath; $lua=$c.lua;$backup=$c.backup
        [AniimoSafePath]::ValidateTree($backup)
        if($c.version -eq [string]$m.translationVersion -and $c.hashes['LuaScripts/Data/I18N/Compress_en.bin'] -eq $m.payloadFiles.'Compress_en.bin'){throw 'Zaloha uz existuje. Táto verzia je už nainštalovaná.'}
        if($c.version -and ([version]$m.translationVersion -lt [version]$c.version)){throw 'Staršia verzia neprepíše novší nainštalovaný preklad.'}
        $work=Join-Path $parent ('txn-'+[Guid]::NewGuid().ToString('N').Substring(0,12));$stage=Join-Path $work 'stage';$rollback=Join-Path $work 'rollback'
        Build-AniimoArchive $lua (Join-Path $PayloadRoot 'data') $stage
        [AniimoSafePath]::DirectorySafe((Join-Path $stage 'builtin')) | Out-Null
        foreach($name in @('LuaScripts.xdf','LuaScripts.xdt')){Copy-Safe -LiteralPath (Join-Path $stage $name) -Destination (Join-Path $stage ('builtin\'+$name))}
        foreach($f in $m.sourceFiles.PSObject.Properties){
            if($f.Name.StartsWith('fonts/') -or $f.Name.StartsWith('boot/')){
                $dest=Join-Path $stage $f.Name;[AniimoSafePath]::DirectorySafe([IO.Path]::GetDirectoryName($dest)) | Out-Null
                Copy-Safe -LiteralPath (Join-Path $PayloadRoot ('data\'+[IO.Path]::GetFileName($f.Name))) -Destination $dest
            }
        }
        $newReceipt=@();$snapshot=@()
        foreach($f in $m.sourceFiles.PSObject.Properties){
            Copy-Verified (Get-GameFile $lua $f.Name) (Join-Path $rollback $f.Name) $c.hashes[$f.Name]
            $snapshot += @{path=$f.Name;hash=$c.hashes[$f.Name]}
            # Existing originals are immutable. Missing legacy originals must still be pristine.
            $original=Join-Path $backup $f.Name
            if(!(Test-Path -LiteralPath $original)){
                if($c.originalSources.ContainsKey($f.Name)){Copy-Verified $c.originalSources[$f.Name] $original $f.Value}
                else{
                    if($c.hashes[$f.Name] -ne $f.Value){throw 'Slovenské súbory nemožno použiť ako pôvodnú anglickú zálohu.'}
                    Copy-Verified (Get-GameFile $lua $f.Name) $original $f.Value
                }
            }
            if((Get-SHA256 $original) -ne $f.Value){throw 'Pôvodná záloha nesúhlasí.'}
            $newReceipt += [PSCustomObject]@{path=$f.Name;original=$f.Value;patched=(Get-SHA256 (Join-Path $stage $f.Name))}
        }
        $metadata=@()
        foreach($name in @('receipt.json','translation-state.json')){
            $path=Join-Path $backup $name;$exists=Test-Path -LiteralPath $path
            if($exists){Copy-Safe -LiteralPath $path -Destination (Join-Path $rollback $name)}
            $metadata+=@{name=$name;exists=$exists}
        }
        # No game writes have occurred yet. Re-check after staging and immediately before commit.
        Assert-GameClosed;Assert-Build $GamePath ([string]$m.gameBuild)
        foreach($f in $snapshot){if((Get-SHA256 (Get-GameFile $lua $f.path)) -ne $f.hash){throw 'Hra sa zmenila počas prípravy aktualizácie.'}}
        Write-Utf8 $pending (@{work=$work;backup=$backup;snapshot=$snapshot;metadata=$metadata}|ConvertTo-Json -Depth 8)
        try {
            foreach($f in $newReceipt){Assert-GameClosed;Copy-Verified (Join-Path $stage $f.path) (Get-GameFile $lua $f.path) $f.patched}
            Write-Utf8 (Join-Path $backup 'receipt.json') ($newReceipt|ConvertTo-Json -Depth 5)
            $state=@{translation_version=[string]$m.translationVersion;game_build=[string]$m.gameBuild;text_sha256=$m.payloadFiles.'Compress_en.bin';receipt_sha256=(Get-SHA256 (Join-Path $backup 'receipt.json'))}
            Write-Utf8 (Join-Path $backup 'translation-state.json') ($state|ConvertTo-Json)
            [AniimoSafePath]::DeleteFile($pending)
        } catch {
            $errorText=$_.Exception.Message
            try { Restore-Transaction $GamePath $pending } catch {$keep=$true;throw ('Obnova predchádzajúcej verzie sa nedokončila. Záloha bola zachovaná. '+$_.Exception.Message)}
            throw ('Aktualizácia zlyhala. Predchádzajúca verzia bola obnovená. '+$errorText)
        }
    } finally {
        if($work -and !$keep){Remove-WorkDirectory $work $parent}
        if($lock){$lock.Dispose()}
    }
}
function Restore-Transaction([string]$GamePath,[string]$Pending) {
    $parent=[IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath));$j=Get-Content -LiteralPath $Pending -Raw|ConvertFrom-Json
    $prefix=[IO.Path]::GetFullPath($parent).TrimEnd('\')+'\'
    if(![IO.Path]::GetFullPath($j.work).StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Neplatný priečinok obnovy.'}
    if([IO.Path]::GetFullPath($j.backup) -ne [IO.Path]::GetFullPath((Get-BackupPath $GamePath))){throw 'Neplatná záloha obnovy.'}
    [AniimoSafePath]::ValidateTree($j.work)
    [AniimoSafePath]::ValidateTree($j.backup)
    $trusted=Get-TrustedManifest;$lua=Join-Path $GamePath 'Aniimo_Data\cvs\res\lua'
    if(@($j.snapshot).Count -ne 12 -or @($j.snapshot.path|Select-Object -Unique).Count -ne 12){throw 'Neplatný záznam obnovy.'}
    foreach($f in $j.snapshot){
        if($f.path -notin $trusted.sourceFiles.PSObject.Properties.Name){throw 'Neplatná cesta obnovy.'}
        $source=Join-Path (Join-Path $j.work 'rollback') $f.path
        if((Get-SHA256 $source) -ne $f.hash){throw 'Poškodená dočasná záloha.'}
    }
    foreach($f in $j.snapshot){[AniimoSafePath]::Validate((Get-GameFile $lua $f.path))}
    foreach($f in $j.snapshot){Copy-Verified (Join-Path (Join-Path $j.work 'rollback') $f.path) (Get-GameFile $lua $f.path) $f.hash}
    foreach($f in $j.metadata){
        if($f.name -notin @('receipt.json','translation-state.json')){throw 'Neplatné metadáta.'}
        $dest=Join-Path $j.backup $f.name
        if($f.exists){Copy-Safe -LiteralPath (Join-Path (Join-Path $j.work 'rollback') $f.name) -Destination $dest -Force}
        elseif(Test-Path -LiteralPath $dest){[AniimoSafePath]::DeleteFile($dest)}
    }
    [AniimoSafePath]::DeleteFile($Pending)
}
function Assert-DownloadUri([string]$Url) {
    $uri=$null
    if(![Uri]::TryCreate($Url,[UriKind]::Absolute,[ref]$uri) -or $uri.UserInfo){throw 'Neplatná adresa aktualizácie.'}
    if($uri.Scheme -ne 'https' -and !($uri.Scheme -eq 'http' -and $uri.IsLoopback)){throw 'Aktualizácie vyžadujú HTTPS. HTTP je povolené iba na lokálny test.'}
    return $uri
}
function Receive-UpdateFile([string]$Url,[string]$Destination,[long]$Limit) {
    $uri=Assert-DownloadUri $Url
    [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12
    for($redirect=0;$redirect -lt 6;$redirect++){
        $request=[Net.HttpWebRequest]::Create($uri);$request.AllowAutoRedirect=$false;$request.Timeout=15000;$request.ReadWriteTimeout=30000;$request.UserAgent='AniimoSlovencina/1.4'
        $response=$request.GetResponse()
        try {
            if([int]$response.StatusCode -in @(301,302,303,307,308)){$uri=Assert-DownloadUri ([Uri]::new($uri,$response.Headers['Location']).AbsoluteUri);continue}
            if([int]$response.StatusCode -ne 200){throw 'Server neposkytol aktualizačný súbor.'}
            if($response.ContentLength -gt $Limit){throw 'Aktualizačný súbor prekročil povolenú veľkosť.'}
            $input=$response.GetResponseStream();$output=[AniimoSafePath]::OpenWrite($Destination,$false,$true)
            try {$buffer=New-Object byte[] 65536;$total=0;while(($read=$input.Read($buffer,0,$buffer.Length)) -gt 0){$total+=$read;if($total -gt $Limit){throw 'Aktualizačný súbor je príliš veľký.'};$output.Write($buffer,0,$read)}}finally{$output.Dispose();$input.Dispose()}
            return
        } finally {$response.Dispose()}
    }
    throw 'Príliš veľa presmerovaní servera.'
}
function Get-FeedUrl {
    $config=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'AniimoSlovencina\updater.json'
    if(!(Test-Path -LiteralPath $config)){$config=Join-Path $PSScriptRoot 'updater.json'}
    if(Test-Path -LiteralPath $config){return [string](Get-Content -LiteralPath $config -Raw|ConvertFrom-Json).version_url}
    return ''
}
function Read-UpdateFeed([string]$Url) {
    $temp=Join-Path ([IO.Path]::GetTempPath()) ('aniimo-feed-'+[Guid]::NewGuid().ToString('N')+'.json')
    try {
        Receive-UpdateFile $Url $temp 1048576
        $feed=Get-Content -LiteralPath $temp -Raw -Encoding UTF8|ConvertFrom-Json
        if([string]$feed.translation_version -notmatch '^\d+\.\d+(\.\d+)?$' -or [string]$feed.game_build -notmatch '^\d+$' -or [string]$feed.sha256 -notmatch '^[a-fA-F0-9]{64}$'){throw 'Server vrátil neplatný version.json.'}
        $null=Assert-DownloadUri ([string]$feed.package_url)
        return $feed
    } finally {if(Test-Path -LiteralPath $temp){[AniimoSafePath]::DeleteFile($temp)}}
}
function Expand-DataPackage([string]$Zip,[string]$Destination) {
    $trusted=Get-TrustedManifest;$allowed=@('manifest.json')+@($trusted.payloadFiles.PSObject.Properties.Name|ForEach-Object{'data/'+$_})
    [AniimoSafePath]::ValidateTree($Destination)
    $archive=[IO.Compression.ZipFile]::OpenRead($Zip)
    try {
        $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase);$total=0L
        foreach($entry in $archive.Entries){
            if($entry.FullName -notin $allowed -or !$seen.Add($entry.FullName)){throw 'Balík obsahuje nepovolenú cestu, program alebo duplicitný súbor.'}
            $null=[AniimoSafePath]::Within($Destination,(Join-Path $Destination $entry.FullName))
            [AniimoSafePath]::Validate((Join-Path $Destination $entry.FullName))
            $total+=$entry.Length;if($total -gt 536870912 -or $entry.Length -gt 268435456){throw 'Rozbalený balík je príliš veľký.'}
            if($entry.FullName -eq 'manifest.json' -and $entry.Length -gt 1048576){throw 'Neplatný manifest.'}
        }
        if($seen.Count -ne $allowed.Count){throw 'Aktualizačný balík je neúplný.'}
        foreach($entry in $archive.Entries){
            $dest=Join-Path $Destination $entry.FullName
            [AniimoSafePath]::DirectorySafe([IO.Path]::GetDirectoryName($dest))|Out-Null
            $input=$entry.Open();$output=[AniimoSafePath]::OpenWrite($dest,$false,$true)
            try{$input.CopyTo($output)}finally{$output.Dispose();$input.Dispose()}
        }
    } finally {$archive.Dispose()}
}
function Invoke-OnlineUpdate([string]$GamePath,[string]$FeedUrl,[string]$ExpectedVersion) {
    if(!$FeedUrl){$FeedUrl=Get-FeedUrl}
    if(!$FeedUrl){throw 'Najprv nastav adresu version.json v nastaveniach aktualizácií.'}
    $feed=Read-UpdateFeed $FeedUrl
    if($ExpectedVersion -and $feed.translation_version -ne $ExpectedVersion){throw 'Ponuka aktualizácie sa zmenila. Klikni na Skontrolovať znova.'}
    Assert-Build $GamePath ([string]$feed.game_build)
    $trusted=Get-TrustedManifest
    if([string]$feed.game_build -ne [string]$trusted.gameBuild){throw 'Táto zostava hry potrebuje novší inštalátor.'}
    $context=Get-InstallContext $GamePath
    if($context.version -and [version]$feed.translation_version -le [version]$context.version){throw 'Táto verzia je už nainštalovaná alebo je staršia.'}
    $parent=Join-Path ([IO.Path]::GetTempPath()) 'Aniimo-SK-updates';[AniimoSafePath]::DirectorySafe($parent)|Out-Null
    $work=Join-Path $parent ([Guid]::NewGuid().ToString('N'));[AniimoSafePath]::DirectorySafe($work)|Out-Null
    try {
        $zip=Join-Path $work 'update.zip';Receive-UpdateFile ([string]$feed.package_url) $zip 268435456
        if((Get-SHA256 $zip) -ne $feed.sha256){throw 'SHA-256 nesedí. Stiahnutý balík je poškodený alebo zmenený. Aktualizácia bola zrušená; hra zostala nezmenená.'}
        Assert-GameClosed;Assert-Build $GamePath ([string]$feed.game_build)
        $root=Join-Path $work 'payload';Expand-DataPackage $zip $root
        $m=Assert-Payload $root
        if([string]$m.translationVersion -ne [string]$feed.translation_version -or [string]$m.gameBuild -ne [string]$feed.game_build){throw 'Verzia balíka nezodpovedá version.json.'}
        Invoke-PayloadInstall $GamePath $root
    } finally {Remove-WorkDirectory $work $parent}
}
