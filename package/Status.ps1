param([string]$GamePath)
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'UpdateTools.ps1')
$r=@{state='missing';message='Vyber priečinok s Aniimo.exe.';installed='Nezistené';canInstall=$false;canRestore=$false;running=$false;backup='';onlineVersion='';onlineMessage='';changelog='';canUpdate=$false;canRecover=$false}
try {
    $feed=$null;$url=Get-FeedUrl
    if($url){try{$feed=Read-UpdateFeed $url;$r.onlineVersion=[string]$feed.translation_version;$r.onlineMessage='Online kontrola dokončená. Najnovší preklad: '+$feed.translation_version+'; podporovaná zostava: '+$feed.game_build+'.'}catch{$r.onlineMessage='Online kontrola sa nepodarila. '+$_.Exception.Message}}
    else{$r.onlineMessage='Online aktualizácie: nastav adresu version.json.'}
    if(!$GamePath -or !(Test-Path -LiteralPath (Join-Path $GamePath 'Aniimo.exe'))){$r|ConvertTo-Json -Compress;return}
    $r.running=[bool](Get-Process -Name Aniimo -ErrorAction SilentlyContinue)
    $pending=Join-Path ([IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath))) 'pending.json'
    if(Test-Path -LiteralPath $pending){$r.state='recovery';$r.message='Predchádzajúca operácia bola prerušená. Obnov predchádzajúci stav.';$r.canRecover=!$r.running;$r|ConvertTo-Json -Compress;return}
    $c=Get-InstallContext $GamePath;$r.backup=$c.backup;$trusted=Get-TrustedManifest
    if($c.pristine){$r.state='ready';$r.installed='Nenainštalovaný';$r.canInstall=$true;$r.message='Hra je kompatibilná. Môžeš nainštalovať slovenčinu.'}
    else{
        $r.canRestore=!$c.migrating;$r.installed=if($c.version){$c.version}else{'Staršia verzia'}
        if($c.version -and [version]$c.version -ge [version]$trusted.translationVersion){$r.state='current';$r.message='Slovenčina '+$c.version+' je aktuálna. Môžeš pokračovať v hraní.'}
        else{$r.state='update';$r.canInstall=$true;$r.message='Rozpoznaný preklad. Môžeš aktualizovať slovenčinu.'}
    }
    if($feed){
        if([string]$feed.game_build -ne (Get-GameBuild $GamePath)){
            $r.onlineMessage='Online balík je pre inú zostavu hry. Pre túto zostavu môžeš použiť overený pribalený preklad.'
        }elseif(!$c.version -or [version]$feed.translation_version -gt [version]$c.version){
            if([string]$feed.game_build -ne [string]$trusted.gameBuild){throw 'Zostava hry potrebuje novší inštalátor.'}
            $r.onlineVersion=[string]$feed.translation_version;$r.canUpdate=$true
            $r.message='Dostupná je nová verzia slovenčiny '+$r.onlineVersion+'.';$r.onlineMessage=$r.message
            $r.changelog=(@($feed.changelog)|ForEach-Object{[string]$_}) -join [Environment]::NewLine
        }else{$r.onlineMessage='Online kontrola: používaš aktuálnu alebo novšiu verziu.'}
    }
    if($r.running){$r.canInstall=$false;$r.canRestore=$false;$r.canUpdate=$false;$r.message='Hra je spustená. Po jej ukončení klikni na Skontrolovať znova.'}
}catch{$r.state='blocked';$r.message=$_.Exception.Message;$r.canInstall=$false;$r.canRestore=$false;$r.canUpdate=$false}
$r|ConvertTo-Json -Compress
