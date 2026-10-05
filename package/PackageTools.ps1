if (-not ('AniimoSafePath' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'SafePath.cs') }
function Copy-Safe([string]$LiteralPath,[string]$Destination,[switch]$Force) { [AniimoSafePath]::Copy($LiteralPath,$Destination) }
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-SafeHash([string]$Path,[string]$Algorithm) {
    $stream=[AniimoSafePath]::OpenRead($Path)
    $hash=[Security.Cryptography.HashAlgorithm]::Create($Algorithm)
    try { return [BitConverter]::ToString($hash.ComputeHash($stream)).Replace('-','').ToLowerInvariant() }
    finally { $hash.Dispose(); $stream.Dispose() }
}
function Get-SHA256([string]$Path) {
    return Get-SafeHash $Path 'SHA256'
}
function Write-Utf8([string]$Path, [string]$Text) {
    [AniimoSafePath]::WriteText($Path, $Text)
}
function Assert-GameClosed {
    if (Get-Process -Name 'Aniimo' -ErrorAction SilentlyContinue) {
        throw 'Najprv ukonci hru Aniimo a zopakuj instalaciu.'
    }
}
function Get-GameFile([string]$LuaRoot, [string]$Name) {
    if ($Name -in @('fonts/xgui_font_94caf04d33b30d3bf95fff3d59018c81.uab','fonts/xgui_font_asset_0_7c59a01880d83ee3f861970de35c3ce3.uab','fonts/xpt21_ar_resx_04a564c8_xgui_font_0_9b0f7d72fb917cb12ac86710360d45c8.uab','fonts/xpt21_mres_exall_0_56f2e8c16cb439a06833bfae669c0e6c.uab','fonts/xpt22_mres_exall_0_9fd11bcc7e5149929c8fc6622a551ae9.uab')) {
        return [IO.Path]::GetFullPath((Join-Path $LuaRoot ('..\..\..\StreamingAssets\cvs\res\uab\win\DefaultPackage\' + [IO.Path]::GetFileName($Name))))
    }
    if ($Name -eq 'boot/resources.assets.resS') { return [IO.Path]::GetFullPath((Join-Path $LuaRoot '..\..\..\resources.assets.resS')) }
    if ($Name -in @('builtin/LuaScripts.xdf','builtin/LuaScripts.xdt')) {
        return [IO.Path]::GetFullPath((Join-Path $LuaRoot ('..\..\..\StreamingAssets\cvs\res\lua\' + [IO.Path]::GetFileName($Name))))
    }
    if ($Name -notin @('LuaScripts.xdf','LuaScripts.xdt','LuaCacheVer.txt','LuaScripts/Data/I18N/Compress_en.bin')) { throw 'Neplatna cesta suboru hry.' }
    return Join-Path $LuaRoot $Name
}
function Find-Aniimo {
    $libraries = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($key in @('HKCU:\Software\Valve\Steam','HKLM:\SOFTWARE\WOW6432Node\Valve\Steam','HKLM:\SOFTWARE\Valve\Steam')) {
        $value = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
        foreach ($candidate in @($value.SteamPath, $value.InstallPath)) {
            if ($candidate) { $null = $libraries.Add($candidate.Replace('/', '\').TrimEnd('\')) }
        }
    }
    foreach ($base in @(${env:ProgramFiles(x86)}, $env:ProgramFiles)) {
        if ($base) { $null = $libraries.Add((Join-Path $base 'Steam')) }
    }
    # Read Steam's registered libraries; inspect only known locations, not disks recursively.
    foreach ($library in @($libraries)) {
        foreach ($relative in @('steamapps\libraryfolders.vdf','config\libraryfolders.vdf')) {
            $vdf = Join-Path $library $relative
            if (Test-Path -LiteralPath $vdf) {
                $content = Get-Content -LiteralPath $vdf -Raw -ErrorAction SilentlyContinue
                foreach ($match in [regex]::Matches($content, '"(?:path|[0-9]+)"\s+"([A-Za-z]:[^"\r\n]*)"')) {
                    $null = $libraries.Add($match.Groups[1].Value.Replace('\\', '\').TrimEnd('\'))
                }
            }
        }
    }
    foreach ($drive in (Get-PSDrive -PSProvider FileSystem)) {
        foreach ($relative in @('SteamLibrary','Steam','Games\Steam')) {
            $null = $libraries.Add((Join-Path $drive.Root $relative))
        }
    }
    $found = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($library in $libraries) {
        $candidate = Join-Path $library 'steamapps\common\Aniimo'
        if ((Test-Path -LiteralPath (Join-Path $candidate 'Aniimo.exe')) -and
            (Test-Path -LiteralPath (Join-Path $candidate 'Aniimo_Data'))) {
            $null = $found.Add((Resolve-Path -LiteralPath $candidate).Path)
        }
    }
    return @($found | Sort-Object)
}
function Resolve-Game([string]$Path) {
    if (!$Path) {
        Write-Host 'Hladam Aniimo v knizniciach Steamu...'
        $found = @(Find-Aniimo)
        if ($found.Count -eq 1) {
            Write-Host "Najdena hra: $($found[0])"
            $answer = Read-Host 'Stlac Enter pre tuto cestu, alebo zadaj inu cestu'
            if ([string]::IsNullOrWhiteSpace($answer)) { $Path = $found[0] } else { $Path = $answer }
        } elseif ($found.Count -gt 1) {
            for ($i=0; $i -lt $found.Count; $i++) { Write-Host ("{0}. {1}" -f ($i+1), $found[$i]) }
            $answer = Read-Host 'Zadaj cislo instalacie alebo vlastnu cestu k hre'
            $number = 0
            if ([int]::TryParse($answer, [ref]$number) -and $number -ge 1 -and $number -le $found.Count) {
                $Path = $found[$number-1]
            } else { $Path = $answer }
        } else {
            Write-Host 'Hra sa automaticky nenasla.'
            $Path = Read-Host 'Zadaj cestu k hre Aniimo (priecinok s Aniimo.exe)'
        }
    }
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Nebola vybrana cesta k hre.' }
    $Path = $Path.Trim().Trim('"')
    [AniimoSafePath]::Validate($Path)
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    [AniimoSafePath]::Validate($resolved)
    if (!(Test-Path -LiteralPath (Join-Path $resolved 'Aniimo.exe'))) {
        throw 'Vo vybranom priecinku chyba Aniimo.exe.'
    }
    return $resolved
}

# Read the ZIP central directory to recover actual data offsets, including
# archives written by different .NET versions. No game code is executed.
if (-not ('AniimoZipIndex' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
public class AniimoZipLocation {
    public long Offset;
    public long Size;
    public long CompressedSize;
    public int Index;
}
public class AniimoStoredZip : IDisposable {
    private BinaryWriter writer;
    private List<byte[]> central = new List<byte[]>();
    private static readonly uint[] crcTable = MakeCrcTable();
    private static uint[] MakeCrcTable() {
        var table=new uint[256];
        for(uint i=0;i<256;i++) {uint c=i; for(int n=0;n<8;n++) c=(c&1)!=0 ? 0xedb88320U^(c>>1) : c>>1; table[i]=c;}
        return table;
    }
    public AniimoStoredZip(Stream output) {writer=new BinaryWriter(output);}
    public void Add(string name,byte[] data,DateTime date) {
        byte[] text=Encoding.UTF8.GetBytes(name);
        uint crc=0xffffffffU;
        foreach(byte b in data) crc=crcTable[(crc^b)&255]^(crc>>8);
        crc^=0xffffffffU;
        uint offset=checked((uint)writer.BaseStream.Position);
        uint size=checked((uint)data.Length);
        ushort time=(ushort)((date.Hour<<11)|(date.Minute<<5)|(date.Second/2));
        ushort day=(ushort)(((Math.Max(1980,date.Year)-1980)<<9)|(date.Month<<5)|date.Day);
        writer.Write(0x04034b50U); writer.Write((ushort)20); writer.Write((ushort)0x800); writer.Write((ushort)0);
        writer.Write(time); writer.Write(day); writer.Write(crc); writer.Write(size); writer.Write(size);
        writer.Write((ushort)text.Length); writer.Write((ushort)0); writer.Write(text); writer.Write(data);
        using(var m=new MemoryStream()) using(var w=new BinaryWriter(m)) {
            w.Write(0x02014b50U); w.Write((ushort)20); w.Write((ushort)20); w.Write((ushort)0x800); w.Write((ushort)0);
            w.Write(time); w.Write(day); w.Write(crc); w.Write(size); w.Write(size); w.Write((ushort)text.Length);
            w.Write((ushort)0); w.Write((ushort)0); w.Write((ushort)0); w.Write((ushort)0); w.Write(0U); w.Write(offset); w.Write(text);
            central.Add(m.ToArray());
        }
    }
    public void Dispose() {
        if(writer==null) return;
        uint offset=checked((uint)writer.BaseStream.Position);
        foreach(var record in central) writer.Write(record);
        uint length=checked((uint)writer.BaseStream.Position-offset);
        writer.Write(0x06054b50U); writer.Write((ushort)0); writer.Write((ushort)0);
        writer.Write(checked((ushort)central.Count)); writer.Write(checked((ushort)central.Count));
        writer.Write(length); writer.Write(offset); writer.Write((ushort)0);
        writer.Dispose(); writer=null;
    }
}
public static class AniimoZipIndex {
    public static Dictionary<string,AniimoZipLocation> Read(string path) {
        var result = new Dictionary<string,AniimoZipLocation>(StringComparer.Ordinal);
        using (var f = File.OpenRead(path)) using (var r = new BinaryReader(f)) {
            long end = -1;
            for (long p=f.Length-22; p>=Math.Max(0,f.Length-65557); p--) {
                f.Position=p;
                if(r.ReadUInt32()!=0x06054b50) continue;
                f.Position=p+20;
                if(p+22+r.ReadUInt16()==f.Length) {end=p;break;}
            }
            if(end<0) throw new InvalidDataException("Missing ZIP end record");
            f.Position=end+10; int count=r.ReadUInt16();
            f.Position=end+16; long central=r.ReadUInt32();
            f.Position=central;
            for(int i=0;i<count;i++) {
                long start=f.Position;
                if(r.ReadUInt32()!=0x02014b50) throw new InvalidDataException("Bad central record");
                f.Position=start+20; long compressed=r.ReadUInt32(); long size=r.ReadUInt32();
                int nameLen=r.ReadUInt16(); int extraLen=r.ReadUInt16(); int commentLen=r.ReadUInt16();
                f.Position=start+42; long local=r.ReadUInt32();
                string name=Encoding.UTF8.GetString(r.ReadBytes(nameLen));
                long next=start+46+nameLen+extraLen+commentLen;
                f.Position=local;
                if(r.ReadUInt32()!=0x04034b50) throw new InvalidDataException("Bad local record");
                f.Position=local+26; int ln=r.ReadUInt16(); int le=r.ReadUInt16();
                result.Add(name,new AniimoZipLocation {Offset=local+30+ln+le,Size=size,CompressedSize=compressed,Index=i});
                f.Position=next;
            }
        }
        return result;
    }
}
'@
}

function Build-AniimoArchive([string]$LuaRoot, [string]$DataRoot, [string]$Stage) {
    [AniimoSafePath]::DirectorySafe($Stage) | Out-Null
    $source = [IO.Compression.ZipFile]::OpenRead((Join-Path $LuaRoot 'LuaScripts.xdf'))
    $target = [AniimoStoredZip]::new([AniimoSafePath]::OpenWrite((Join-Path $Stage 'LuaScripts.xdf'),$false,$true))
    $replacements = @{
        'xfs/luascripts/Data/I18N/Compress_en.bin' = (Join-Path $DataRoot 'Compress_en.bin')
        'xfs/luascripts/Data/I18N/NewTextMap_en.json' = (Join-Path $DataRoot 'NewTextMap_en.json')
    }
    $found = 0
    try {
        foreach ($entry in $source.Entries) {
            $dest = [IO.MemoryStream]::new()
            try {
                if ($replacements.ContainsKey($entry.FullName)) {
                    $inputStream = [AniimoSafePath]::OpenRead($replacements[$entry.FullName]); $found++
                } else { $inputStream = $entry.Open() }
                try { $inputStream.CopyTo($dest) } finally { $inputStream.Dispose() }
                $target.Add($entry.FullName, $dest.ToArray(), $entry.LastWriteTime.DateTime)
            } finally { $dest.Dispose() }
        }
    } finally { $target.Dispose(); $source.Dispose() }
    if ($found -ne 2) { throw 'Archiv neobsahuje ocakavane jazykove subory.' }
    $archivePath = Join-Path $Stage 'LuaScripts.xdf'
    $index = [AniimoZipIndex]::Read($archivePath)
    $metadata = Get-Content -LiteralPath (Join-Path $LuaRoot 'LuaScripts.xdt') -Raw | ConvertFrom-Json
    if ($metadata.CMEntryNum -ne $index.Count) { throw 'Nesuhlasi pocet poloziek archivu.' }
    foreach ($record in $metadata.CMList) {
        $location = $index[$record.CEName]
        if (!$location) { throw "Chybajuca polozka: $($record.CEName)" }
        if ($location.Size -ne $location.CompressedSize) { throw 'Ocakavany nekomprimovany archiv.' }
        $record.CEOffset = $location.Offset
        $record.CEIndex = $location.Index
        $record.CESize = $location.Size
        $record.CECSize = $location.CompressedSize
        if ($replacements.ContainsKey($record.CEName)) {
            $record.CEMD5 = (Get-SafeHash $replacements[$record.CEName] 'MD5')
        }
    }
    $metadata.CMDataLen = (Get-Item -LiteralPath $archivePath).Length
    $metadata.CMDataMD5 = (Get-SafeHash $archivePath 'MD5')
    $indexPath = Join-Path $Stage 'LuaScripts.xdt'
    Write-Utf8 $indexPath ($metadata | ConvertTo-Json -Depth 12)
    $cache = (Get-Content -LiteralPath (Join-Path $LuaRoot 'LuaCacheVer.txt') -Raw).Split(',')
    if ($cache.Count -ne 3) { throw 'Neznamy format LuaCacheVer.txt.' }
    $cacheText = $cache[0] + ',' + (Get-Item -LiteralPath $indexPath).Length + ',' + (Get-SafeHash $indexPath 'MD5')
    Write-Utf8 (Join-Path $Stage 'LuaCacheVer.txt') $cacheText
    $loose = Join-Path $Stage 'LuaScripts\Data\I18N'
    [AniimoSafePath]::DirectorySafe($loose) | Out-Null
    Copy-Safe -LiteralPath (Join-Path $DataRoot 'Compress_en.bin') -Destination (Join-Path $loose 'Compress_en.bin')
}

function Get-NewBackupPath([string]$GamePath) {
    $base = $env:ANIIMO_SK_BACKUP_ROOT
    if (!$base) { $base = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'AniimoSlovencina\backups' }
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $key = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes([IO.Path]::GetFullPath($GamePath).TrimEnd('\').ToLowerInvariant()))).Replace('-','').Substring(0,24) } finally { $sha.Dispose() }
    $build=[string](Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json).gameBuild
    if($build -notmatch '^\d+$'){throw 'Neplatná zostava v dôveryhodnom manifeste.'}
    $path=Join-Path (Join-Path $base $key) ('build-'+$build)
    [AniimoSafePath]::Validate($path)
    return $path
}
function Get-BackupPath([string]$GamePath) { return (Get-NewBackupPath $GamePath) }
function Get-PreviousBackupPaths([string]$GamePath) {
    return @((Join-Path ([IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath))) 'build-3629693'),(Join-Path ([IO.Path]::GetDirectoryName((Get-NewBackupPath $GamePath))) 'current'),(Join-Path $GamePath 'Aniimo-SK-zaloha'))
}
function Archive-Backup([string]$Backup) {
    $parent = [IO.Path]::GetFullPath([IO.Path]::GetDirectoryName($Backup)).TrimEnd('\') + '\'
    $destination = Join-Path $parent ('Aniimo-SK-archiv-' + [Guid]::NewGuid().ToString('N'))
    if (![IO.Path]::GetFullPath($Backup).StartsWith($parent,[StringComparison]::OrdinalIgnoreCase) -or ![IO.Path]::GetFullPath($destination).StartsWith($parent,[StringComparison]::OrdinalIgnoreCase)) { throw 'Neplatna cesta zalohy.' }
    [AniimoSafePath]::MoveDirectory($Backup,$destination)
    return $destination
}
