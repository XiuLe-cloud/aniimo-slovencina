// Shared Windows filesystem boundary for GUI extraction and PowerShell operations.
// Reject reparse points and hard links; pin ancestors while a handle is in use.
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

public static class AniimoSafePath {
    const uint OPEN_REPARSE=0x00200000, BACKUP=0x02000000, DELETE=0x00010000;
    [StructLayout(LayoutKind.Sequential)] struct Info {
        public uint Attributes; public System.Runtime.InteropServices.ComTypes.FILETIME Creation,Access,Write;
        public uint Volume,SizeHigh,SizeLow,Links,IndexHigh,IndexLow;
    }
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
    static extern SafeFileHandle CreateFile(string p,uint access,uint share,IntPtr security,uint mode,uint flags,IntPtr template);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool GetFileInformationByHandle(SafeFileHandle h,out Info info);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool SetFileInformationByHandle(SafeFileHandle h,int kind,IntPtr data,uint size);
    [StructLayout(LayoutKind.Sequential,CharSet=CharSet.Unicode)] struct RenameLayout { public byte Replace; public IntPtr Root; public uint Length; public char First; }
    static Exception Error(string path) { return new IOException("Bezpečný prístup k ceste zlyhal: "+path,new Win32Exception(Marshal.GetLastWin32Error())); }
    public static string Full(string p) {
        if(String.IsNullOrWhiteSpace(p) || p.Length<3 || !Char.IsLetter(p[0]) || p[1]!=':' || (p[2]!='\\' && p[2]!='/')) throw new IOException("Vyžaduje sa absolútna lokálna cesta.");
        if(p.Substring(2).Contains(":") || p.Contains("\0")) throw new IOException("Nepovolená cesta alebo alternatívny dátový prúd.");
        foreach(string part in p.Substring(3).Replace('/','\\').Split('\\')) {
            if(part==".." || part==".") throw new IOException("Relatívny úsek cesty nie je povolený.");
            if(part.EndsWith(".") || part.EndsWith(" ")) throw new IOException("Nejednoznačná cesta.");
            string stem=part.Split('.')[0].ToUpperInvariant();
            if(stem=="CON"||stem=="PRN"||stem=="AUX"||stem=="NUL"||System.Text.RegularExpressions.Regex.IsMatch(stem,@"^(COM|LPT)[0-9]$")) throw new IOException("Rezervovaný názov cesty.");
        }
        return Path.GetFullPath(p).TrimEnd('\\');
    }
    public static string Within(string root,string target) {
        root=Full(root);target=Full(target);
        if(!target.StartsWith(root+"\\",StringComparison.OrdinalIgnoreCase)) throw new IOException("Cesta smeruje mimo povoleného koreňa.");
        return target;
    }
    static SafeFileHandle Open(string p,uint access,uint mode,bool directory,uint share) {
        var h=CreateFile(p,access,share,IntPtr.Zero,mode,OPEN_REPARSE|(directory?BACKUP:0),IntPtr.Zero);
        if(h.IsInvalid){h.Dispose();throw Error(p);}
        Info i;
        if(!GetFileInformationByHandle(h,out i)){h.Dispose();throw Error(p);}
        if((i.Attributes&0x400)!=0 || (!directory && i.Links!=1)) {h.Dispose();throw new IOException("Presmerovaná cesta (reparse point alebo hard link) nie je povolená: "+p);}
        if(((i.Attributes&0x10)!=0)!=directory){h.Dispose();throw new IOException("Neočakávaný typ súboru: "+p);}
        return h;
    }
    sealed class Pins:IDisposable {
        public List<SafeFileHandle> Handles=new List<SafeFileHandle>();
        public void Dispose(){for(int i=Handles.Count-1;i>=0;i--)Handles[i].Dispose();Handles.Clear();}
    }
    static Pins Parents(string path,bool create) {
        var pins=new Pins();
        try {
            string parent=Path.GetDirectoryName(Full(path));
            var chain=new Stack<string>();
            while(parent!=null && parent.Length>3){chain.Push(parent);parent=Path.GetDirectoryName(parent);}
            if(parent!=null) pins.Handles.Add(Open(parent,0,3,true,1));
            while(chain.Count>0){
                string d=chain.Pop();
                // Parent is already pinned. Never truncate/create a file before inspecting its handle.
                if(create && !Directory.Exists(d)) Directory.CreateDirectory(d);
                pins.Handles.Add(Open(d,0,3,true,1));
            }
            return pins;
        }catch{pins.Dispose();throw;}
    }
    public static void Validate(string path) {
        path=Full(path);
        // Validate every existing ancestor, including a dangling reparse point.
        string p=path;
        while(p!=null && p.Length>=3){
            try {
                var a=File.GetAttributes(p);
                if((a&FileAttributes.ReparsePoint)!=0) throw new IOException("Presmerovaná cesta nie je povolená: "+p);
            }catch(FileNotFoundException){}catch(DirectoryNotFoundException){}
            p=Path.GetDirectoryName(p);
        }
        if(File.Exists(path)) using(var pins=Parents(path,false)) using(var h=Open(path,0,3,false,1)){}
    }
    public static void DirectorySafe(string path) {
        path=Full(path);
        using(var pins=Parents(path,true)) {
            if(!Directory.Exists(path))Directory.CreateDirectory(path);
            using(var h=Open(path,0,3,true,1)){}
        }
    }
    sealed class PinnedStream:Stream {
        Stream stream;Pins pins;
        public PinnedStream(Stream s,Pins p){stream=s;pins=p;}
        public override bool CanRead{get{return stream.CanRead;}} public override bool CanWrite{get{return stream.CanWrite;}}
        public override bool CanSeek{get{return stream.CanSeek;}} public override long Length{get{return stream.Length;}}
        public override long Position{get{return stream.Position;}set{stream.Position=value;}}
        public override int Read(byte[] b,int o,int c){return stream.Read(b,o,c);} public override void Write(byte[] b,int o,int c){stream.Write(b,o,c);}
        public override long Seek(long o,SeekOrigin s){return stream.Seek(o,s);} public override void SetLength(long n){stream.SetLength(n);}
        public override void Flush(){stream.Flush();}
        protected override void Dispose(bool disposing){if(disposing){try{stream.Dispose();}finally{pins.Dispose();}}base.Dispose(disposing);}
    }
    public static Stream OpenWrite(string path,bool exclusive,bool truncate) {
        path=Full(path);var pins=Parents(path,true);SafeFileHandle h=null;
        try {
            h=Open(path,0x40000000,4,false,exclusive?0u:1u);
            var s=new FileStream(h,FileAccess.Write);h=null;
            if(truncate)s.SetLength(0);
            return new PinnedStream(s,pins);
        }catch{if(h!=null)h.Dispose();pins.Dispose();throw;}
    }
    public static Stream OpenRead(string path) {
        path=Full(path);var pins=Parents(path,false);SafeFileHandle h=null;
        try{h=Open(path,0x80000000,3,false,1);var s=new FileStream(h,FileAccess.Read);h=null;return new PinnedStream(s,pins);}
        catch{if(h!=null)h.Dispose();pins.Dispose();throw;}
    }
    public static void Copy(string source,string destination) {
        using(var input=OpenRead(source)) using(var output=OpenWrite(destination,false,true))input.CopyTo(output);
    }
    public static void WriteText(string path,string text) {
        using(var output=OpenWrite(path,false,true)){byte[] bytes=new UTF8Encoding(false).GetBytes(text);output.Write(bytes,0,bytes.Length);}
    }
    public static void DeleteFile(string path) {
        path=Full(path);using(var pins=Parents(path,false)) using(var h=Open(path,DELETE,3,false,1))Disposition(h);
    }
    static void Disposition(SafeFileHandle h) {
        IntPtr p=Marshal.AllocHGlobal(4);try{Marshal.WriteInt32(p,1);if(!SetFileInformationByHandle(h,4,p,4))throw Error("delete");}finally{Marshal.FreeHGlobal(p);}
    }
    public static void ValidateTree(string path) {
        Validate(path);if(!Directory.Exists(path))return;
        using(var pins=Parents(path,false))using(var h=Open(path,0,3,true,1))
            foreach(string child in Directory.GetFileSystemEntries(path))ValidateTree(child);
    }
    public static void DeleteTree(string path,string root) {
        path=Within(root,path);ValidateTree(path);
        using(var pins=Parents(path,false)){
          using(var h=Open(path,0,3,true,1)){
            foreach(string child in Directory.GetFileSystemEntries(path)){
                if(Directory.Exists(child))DeleteTree(child,path);else DeleteFile(child);
            }
          }
          using(var h=Open(path,DELETE,3,true,1))Disposition(h);
        }
    }
    public static void MoveDirectory(string source,string destination) {
        source=Full(source);destination=Full(destination);ValidateTree(source);Validate(destination);
        using(var p1=Parents(source,false))using(var p2=Parents(destination,true))using(var h=Open(source,DELETE,3,true,1)){
            int offset=(int)Marshal.OffsetOf(typeof(RenameLayout),"First");
            byte[] name=Encoding.Unicode.GetBytes(destination);int size=Math.Max(Marshal.SizeOf(typeof(RenameLayout)),offset+name.Length+2);
            IntPtr data=Marshal.AllocHGlobal(size);
            try{
                for(int i=0;i<size;i++)Marshal.WriteByte(data,i,0);
                Marshal.WriteInt32(data,(int)Marshal.OffsetOf(typeof(RenameLayout),"Length"),name.Length);
                Marshal.Copy(name,0,IntPtr.Add(data,offset),name.Length);
                if(!SetFileInformationByHandle(h,3,data,(uint)size))throw Error(destination);
            }finally{Marshal.FreeHGlobal(data);}
        }
    }
}
