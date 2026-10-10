param([Parameter(Mandatory=$true)][string]$PackageZip,[Parameter(Mandatory=$true)][string]$Manifest)
$ErrorActionPreference = 'Stop'
[IO.Directory]::CreateDirectory((Join-Path $PSScriptRoot 'dist')) | Out-Null
$payload = (Resolve-Path -LiteralPath $PackageZip).Path
$hash = (Get-FileHash -LiteralPath $payload -Algorithm SHA256).Hash.ToLowerInvariant()
$manifestData=Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$build = Join-Path $PSScriptRoot 'verification\exe-build'
[IO.Directory]::CreateDirectory($build) | Out-Null
$source = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'installer/Installer.cs') -Raw).Replace('PAYLOAD_SHA256',$hash)
$source=$source.Replace('BUNDLED_TRANSLATION_VERSION',[string]$manifestData.translationVersion).Replace('BUNDLED_GAME_BUILD',[string]$manifestData.gameBuild)
$sourcePath = Join-Path $build 'Installer-1.4.1.cs'
[IO.File]::WriteAllText($sourcePath,$source,[Text.UTF8Encoding]::new($true))
$output = Join-Path $PSScriptRoot ('dist\Aniimo-Slovencina-Instalator-1.4.1-preklad-'+$manifestData.translationVersion+'.exe')
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
& $compiler /nologo /target:winexe /platform:anycpu /optimize+ /codepage:65001 /reference:System.Web.Extensions.dll /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll "/win32icon:$PSScriptRoot\assets\penguin.ico" "/resource:$PSScriptRoot\assets\penguin.ico,penguin.ico" "/resource:$PSScriptRoot\assets\penguin.png,penguin.png" "/resource:$payload,payload.zip" "/out:$output" $sourcePath (Join-Path $PSScriptRoot 'package/SafePath.cs')
if ($LASTEXITCODE -ne 0) { throw 'Kompilacia instalatora zlyhala.' }
$digest=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText(($output+'.sha256'),($digest+'  '+[IO.Path]::GetFileName($output)),[Text.Encoding]::ASCII)
Copy-Item -LiteralPath $output -Destination (Join-Path $PSScriptRoot 'dist\Aniimo-Slovencina-Instalator.exe') -Force
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'dist\Aniimo-Slovencina-Instalator.exe.sha256'),($digest+'  Aniimo-Slovencina-Instalator.exe'),[Text.Encoding]::ASCII)
Get-Item -LiteralPath $output | Select-Object FullName,Length
