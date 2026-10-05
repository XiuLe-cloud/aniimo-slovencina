using System;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Diagnostics;
using System.Drawing;
using System.Windows.Forms;

internal sealed class AccentButton : Button {
    protected override void OnPaint(PaintEventArgs e) {
        var bg = Enabled ? (Focused ? Color.FromArgb(255,180,80) : Color.FromArgb(255,155,55)) : Color.FromArgb(224,231,237);
        using(var brush = new SolidBrush(bg)) e.Graphics.FillRectangle(brush, ClientRectangle);
        using(var pen = new Pen(Enabled ? Color.FromArgb(194,96,12) : Color.FromArgb(159,178,193))) e.Graphics.DrawRectangle(pen,0,0,Width-1,Height-1);
        TextRenderer.DrawText(e.Graphics,Text,Font,ClientRectangle,Enabled ? Color.FromArgb(12,46,77) : Color.FromArgb(65,84,101),TextFormatFlags.HorizontalCenter|TextFormatFlags.VerticalCenter);
        if(Focused && ShowFocusCues) ControlPaint.DrawFocusRectangle(e.Graphics,Rectangle.Inflate(ClientRectangle,-5,-5));
    }
    protected override void OnEnabledChanged(EventArgs e) {base.OnEnabledChanged(e);Invalidate();}
}
internal static class Installer {
    private const string PayloadHash = "PAYLOAD_SHA256";
    private const string PackageName = "Aniimo-SK-package";
    [STAThread]
    private static int Main(string[] args) {
        try {
            if(args.Length==2 && args[0]=="--extract-only") {
                Extract(args[1]);
                return 0;
            }
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            using(var form = CreateForm()) {
                if(args.Length==2 && args[0]=="--preview") {
                    form.Show(); install.Enabled=true; Application.DoEvents();
                    using(var bitmap=new Bitmap(form.Width,form.Height)) {
                        form.DrawToBitmap(bitmap,new Rectangle(Point.Empty,form.Size));
                        using(var imageOutput=AniimoSafePath.OpenWrite(Path.GetFullPath(args[1]),false,true)) bitmap.Save(imageOutput,System.Drawing.Imaging.ImageFormat.Png);
                    }
                    form.Close(); return 0;
                }
                Application.Run(form);
            }
            return 0;
        } catch(Exception ex) {
            if(args.Length==2 && args[0]=="--extract-only") return 1;
            MessageBox.Show(ex.Message,"Inštaláciu nemožno spustiť",MessageBoxButtons.OK,MessageBoxIcon.Error);
            return 1;
        }
    }
    private static string Extract(string destination) {
        string root=Path.GetFullPath(destination);
        AniimoSafePath.ValidateTree(root);
        AniimoSafePath.DirectorySafe(root);
        using(var stream=Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip")) {
            if(stream==null) throw new InvalidDataException("Chýbajú inštalačné dáta.");
            using(var sha=SHA256.Create()) {
                var digest=BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
                if(digest!=PayloadHash) throw new InvalidDataException("Inštalačné dáta sú poškodené.");
            }
            stream.Position=0;
            using(var zip=new ZipArchive(stream,ZipArchiveMode.Read)) {
                string prefix=root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar;
                foreach(var entry in zip.Entries) {
                    string target=Path.GetFullPath(Path.Combine(root,entry.FullName.Replace('/',Path.DirectorySeparatorChar)));
                    if(!target.StartsWith(prefix,StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Neplatná cesta v balíku.");
                    if(entry.FullName.EndsWith("/")) { AniimoSafePath.DirectorySafe(target); continue; }
                    AniimoSafePath.DirectorySafe(Path.GetDirectoryName(target));
                    using(var input=entry.Open()) using(var output=AniimoSafePath.OpenWrite(target,false,true)) input.CopyTo(output);
                }
            }
        }
        string package = Path.Combine(root,PackageName);
        if(!File.Exists(Path.Combine(package,"Status.ps1"))) throw new InvalidDataException("V inštalačnom balíku chýba priečinok so skriptom kontroly.");
        return package;
    }
    private static TextBox gamePath;
    private static Label status, installedLabel;
    private static ProgressBar progress;
    private static Button install,restore,browse,refresh,backups,settings;
    private static string actionMode="install", onlineVersion="";
    private static bool busy;
    private static string packagePath, backupPath;
    private static TextBox details;
    private static Label TextLabel(string text,int x,int y,int width,int height,float size,Color color) {
        return new Label {Text=text,Left=x,Top=y,Width=width,Height=height,Font=new Font("Segoe UI",size),ForeColor=color,BackColor=Color.Transparent};
    }
    private static Button ActionButton(string text,int x,int y,int width,bool primary) {
        Button b=primary ? (Button)new AccentButton() : new Button();
        b.Text=text;b.Left=x;b.Top=y;b.Width=width;b.Height=44;b.FlatStyle=FlatStyle.Flat;
        b.BackColor=primary?Color.FromArgb(255,155,55):Color.White;
        b.ForeColor=Color.FromArgb(12,46,77);b.Cursor=Cursors.Hand;
        b.Font=new Font("Segoe UI",10,primary?FontStyle.Bold:FontStyle.Regular);
        b.UseVisualStyleBackColor=false;
        b.FlatAppearance.BorderColor=Color.FromArgb(164,194,217);
        b.FlatAppearance.MouseOverBackColor=Color.FromArgb(225,240,251);
        return b;
    }
    private static Form CreateForm() {
        var f=new Form {Text="Aniimo | Slovenčina",ClientSize=new Size(740,700),Font=new Font("Segoe UI",10),
            BackColor=Color.FromArgb(242,248,253),FormBorderStyle=FormBorderStyle.FixedDialog,
            MaximizeBox=false,StartPosition=FormStartPosition.CenterScreen,AutoScaleMode=AutoScaleMode.Dpi};
        var header=new Panel {Left=0,Top=0,Width=740,Height=140,BackColor=Color.FromArgb(12,46,77)};
        header.Controls.Add(TextLabel("ANIIMO  /  SLOVENČINA OD XIU_LE",30,20,580,24,10,Color.FromArgb(255,177,85)));
        header.Controls.Add(TextLabel("Dobrodružstvo po slovensky",28,51,570,45,24,Color.White));
        header.Controls.Add(TextLabel("Inštalátor 1.4  •  Pribalený preklad BUNDLED_TRANSLATION_VERSION  •  Testovacie vydanie",30,106,580,26,10,Color.FromArgb(208,231,249)));
        using(var iconStream=Assembly.GetExecutingAssembly().GetManifestResourceStream("penguin.ico"))
            if(iconStream!=null) f.Icon=new Icon(iconStream);
        var mascotStream=Assembly.GetExecutingAssembly().GetManifestResourceStream("penguin.png");
        if(mascotStream!=null) {
            var mascot=new PictureBox {Left=620,Top=16,Width=100,Height=100,SizeMode=PictureBoxSizeMode.Zoom,Image=Image.FromStream(mascotStream),BackColor=Color.Transparent};
            header.Controls.Add(mascot);mascot.BringToFront();
            f.Disposed+=(a,b)=>{mascot.Image.Dispose();mascotStream.Dispose();};
        }
        header.Controls.Add(new Panel {Left=0,Top=135,Width=740,Height=5,BackColor=Color.FromArgb(255,155,55)});
        f.Controls.Add(header);
        f.Controls.Add(TextLabel("PRIEČINOK HRY",30,158,680,24,9,Color.FromArgb(63,96,123)));
        gamePath=new TextBox {Left=30,Top=190,Width=550,Height=30,Font=new Font("Segoe UI",11),Text=FindGame()};
        browse=ActionButton("Vybrať…",592,183,118,false);
        browse.Click+=(a,b)=> {using(var d=new FolderBrowserDialog {Description="Vyber priečinok s Aniimo.exe",SelectedPath=gamePath.Text}) {if(d.ShowDialog(f)==DialogResult.OK) {gamePath.Text=d.SelectedPath;Run(f,"status");}}};
        gamePath.TextChanged+=(a,b)=> {install.Enabled=restore.Enabled=backups.Enabled=false;status.Text="Cesta sa zmenila. Klikni na Skontrolovať znova.";};
        f.Controls.AddRange(new Control[]{gamePath,browse});
        installedLabel=TextLabel("Nainštalovaný preklad: zisťujem…",30,245,680,28,12,Color.FromArgb(12,46,77));
        status=TextLabel("Kontrolujem kompatibilitu herných súborov…",30,281,680,57,11,Color.FromArgb(12,46,77));
        refresh=ActionButton("Skontrolovať znova",30,343,220,false);
        backups=ActionButton("Otvoriť zálohy",262,343,200,false);
        refresh.Click+=(a,b)=>Run(f,"status");
        backups.Click+=(a,b)=> {try {string dir=Directory.Exists(backupPath)?backupPath:Path.GetDirectoryName(backupPath);if(Directory.Exists(dir))Process.Start(new ProcessStartInfo(dir){UseShellExecute=true});}catch(Exception ex){status.Text=ex.Message;}};
        settings=ActionButton("Nastaviť aktualizácie",474,343,236,false);
        settings.Click+=(a,b)=>ConfigureUpdates(f);
        f.Controls.AddRange(new Control[]{installedLabel,status,refresh,backups,settings});
        f.Controls.Add(TextLabel("ČO JE NOVÉ",30,408,680,23,9,Color.FromArgb(63,96,123)));
        f.Controls.Add(TextLabel("• Online aktualizácie prekladu bez nového EXE.\n• Kontrola SHA-256 a obnova pri neúspešnej aktualizácii.\n• Posilnená ochrana cieľových ciest a záloh.",30,436,680,77,10,Color.FromArgb(12,46,77)));
        f.Controls.Add(TextLabel("V hre vyber English. Preklad sa priebežne jazykovo opravuje.",30,518,680,24,10,Color.FromArgb(63,96,123)));
        progress=new ProgressBar {Left=30,Top=552,Width=680,Height=5,Visible=false,Style=ProgressBarStyle.Marquee};
        install=ActionButton("Nainštalovať slovenčinu",30,574,334,true);
        restore=ActionButton("Obnoviť angličtinu",376,574,334,false);
        install.Enabled=restore.Enabled=backups.Enabled=false;
        install.Click+=(a,b)=>Run(f,actionMode);restore.Click+=(a,b)=>Run(f,"restore");
        details=new TextBox {Left=30,Top=632,Width=680,Height=48,ReadOnly=true,Multiline=true,ScrollBars=ScrollBars.Vertical,BorderStyle=BorderStyle.FixedSingle,Text="Podporovaná zostava: BUNDLED_GAME_BUILD. Kontrola stavu nemení súbory hry."};
        f.Controls.AddRange(new Control[]{progress,install,restore,details});
        f.FormClosing+=(a,b)=> {if(busy)b.Cancel=true;};
        f.Shown+=(a,b)=> {if(Environment.GetCommandLineArgs().Length==1)Run(f,"status");};
        return f;
    }
    private static void ConfigureUpdates(Form owner) {
        string folder=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"AniimoSlovencina");
        string config=Path.Combine(folder,"updater.json");
        using(var dialog=new Form {Text="Online aktualizácie",ClientSize=new Size(600,185),StartPosition=FormStartPosition.CenterParent,FormBorderStyle=FormBorderStyle.FixedDialog,MaximizeBox=false,MinimizeBox=false}) {
            dialog.Controls.Add(TextLabel("Adresa version.json od autora prekladu (HTTPS):",20,18,560,28,10,Color.Black));
            var url=new TextBox {Left=20,Top=53,Width=560};
            try {if(File.Exists(config))url.Text=(string)new System.Web.Script.Serialization.JavaScriptSerializer().Deserialize<System.Collections.Generic.Dictionary<string,object>>(File.ReadAllText(config))["version_url"];}catch { }
            var save=ActionButton("Uložiť a skontrolovať",20,108,270,true);
            dialog.Controls.AddRange(new Control[]{url,save});
            save.Click+=(a,b)=> {try {
                string value=url.Text.Trim();Uri uri;
                if(value.Length>0&&(!Uri.TryCreate(value,UriKind.Absolute,out uri)||uri.UserInfo.Length>0||(uri.Scheme!="https"&&!(uri.Scheme=="http"&&uri.IsLoopback))))throw new Exception("Zadaj platnú HTTPS adresu version.json.");
                AniimoSafePath.DirectorySafe(folder);
                AniimoSafePath.WriteText(config,new System.Web.Script.Serialization.JavaScriptSerializer().Serialize(new {version_url=value}));
                dialog.DialogResult=DialogResult.OK;dialog.Close();
            }catch(Exception ex){MessageBox.Show(dialog,ex.Message,"Nastavenie sa nepodarilo uložiť");}};
            if(dialog.ShowDialog(owner)==DialogResult.OK)Run(owner,"status");
        }
    }
    private static string FindGame() {
        var roots=new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);
        using(var key=Microsoft.Win32.Registry.CurrentUser.OpenSubKey(@"Software\Valve\Steam")) {
            if(key!=null) {var value=key.GetValue("SteamPath") as string;if(value!=null)roots.Add(value);}
        }
        roots.Add(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),"Steam"));
        foreach(var drive in DriveInfo.GetDrives()) if(drive.IsReady) roots.Add(Path.Combine(drive.RootDirectory.FullName,"SteamLibrary"));
        foreach(var root in new System.Collections.Generic.List<string>(roots)) {
            var vdf=Path.Combine(root,"steamapps","libraryfolders.vdf");
            if(File.Exists(vdf)) foreach(System.Text.RegularExpressions.Match m in System.Text.RegularExpressions.Regex.Matches(File.ReadAllText(vdf), "\"path\"\\s+\"([^\"]+)\"")) roots.Add(m.Groups[1].Value.Replace(@"\\",@"\"));
        }
        foreach(var root in roots) {var path=Path.Combine(root,"steamapps","common","Aniimo");if(File.Exists(Path.Combine(path,"Aniimo.exe")))return path;}
        return "";
    }
    private static string Execute(string mode,string selected,string expectedVersion) {
        if(packagePath==null)packagePath=Extract(Path.Combine(Path.GetTempPath(),"Aniimo-SK",Guid.NewGuid().ToString("N")));
        string script=mode=="status"?"Status.ps1":"Run-Installer.ps1";
        var info=new ProcessStartInfo {
            FileName=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),"WindowsPowerShell","v1.0","powershell.exe"),
            Arguments="-NoProfile -NonInteractive -ExecutionPolicy Bypass -File \""+Path.Combine(packagePath,script)+"\" -GamePath \""+selected+"\""+(mode=="status"?"":" -Mode "+mode+" -NonInteractive"+(mode=="update"?" -ExpectedVersion "+expectedVersion:"")),
            WorkingDirectory=packagePath,UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true,
            StandardOutputEncoding=System.Text.Encoding.UTF8,StandardErrorEncoding=System.Text.Encoding.UTF8
        };
        var log=new System.Text.StringBuilder();
        using(var child=new Process {StartInfo=info}) {
            child.OutputDataReceived+=(a,b)=>{if(b.Data!=null)lock(log)log.AppendLine(b.Data);};
            child.ErrorDataReceived+=(a,b)=>{if(b.Data!=null)lock(log)log.AppendLine(b.Data);};
            child.Start();child.BeginOutputReadLine();child.BeginErrorReadLine();child.WaitForExit();
            if(child.ExitCode!=0)throw new Exception(log.ToString());
        }
        return log.ToString();
    }
    private static void Run(Form form,string mode) {
        if(busy)return;
        string selected=gamePath.Text.Trim().Trim('"');
        if(selected.Contains("\"") || selected.Contains("\r") || selected.Contains("\n")) {status.Text="Neplatná cesta k hre.";return;}
        if(mode!="status" && Process.GetProcessesByName("Aniimo").Length>0) {status.Text="Najprv ukonči Aniimo a klikni na Skontrolovať znova.";install.Enabled=restore.Enabled=false;return;}
        busy=true;install.Enabled=restore.Enabled=browse.Enabled=refresh.Enabled=backups.Enabled=settings.Enabled=gamePath.Enabled=false;progress.Visible=true;
        status.Text=mode=="update"?"Sťahujem a overujem aktualizáciu. Okno nechaj otvorené…":mode=="recover"?"Obnovujem predchádzajúci stav…":mode=="status"?"Kontrolujem súbory a zálohu. Hru môžeš ďalej testovať…":mode=="install"?"Pripravujem preklad a zálohujem pôvodné súbory…":"Obnovujem pôvodné anglické súbory…";
        var worker=new System.ComponentModel.BackgroundWorker();
        string expectedVersion=onlineVersion;
        worker.DoWork+=(sender,e)=> {e.Result=Execute(mode,selected,expectedVersion);};
        worker.RunWorkerCompleted+=(sender,e)=> {
            busy=false;progress.Visible=false;browse.Enabled=refresh.Enabled=settings.Enabled=gamePath.Enabled=true;
            if(e.Error!=null) {status.Text="Operácia sa nepodarila. Podrobnosti sú nižšie; po náprave skontroluj stav znova.";details.Text=e.Error.Message;return;}
            if(mode=="install") {form.Close();return;}
            if(mode!="status") {
                details.Text=mode=="update"?"Aktualizácia slovenčiny bola dokončená.":"Hotovo. Predchádzajúce súbory sú obnovené a záloha zostala zachovaná.";
                Run(form,"status");return;
            }
            try {
                var data=new System.Web.Script.Serialization.JavaScriptSerializer().Deserialize<System.Collections.Generic.Dictionary<string,object>>((string)e.Result);
                status.Text=(string)data["message"];installedLabel.Text="Nainštalovaný preklad: "+(string)data["installed"];
                install.Text=(string)data["state"]=="update"?"Aktualizovať slovenčinu":(string)data["state"]=="current"?"Slovenčina je aktuálna":"Nainštalovať slovenčinu";
                onlineVersion=(string)data["onlineVersion"];
                actionMode=(bool)data["canRecover"]?"recover":(bool)data["canUpdate"]?"update":"install";
                if(actionMode=="update")install.Text="Aktualizovať na "+onlineVersion;
                if(actionMode=="recover")install.Text="Obnoviť prerušenú operáciu";
                install.Enabled=(bool)data["canInstall"]||(bool)data["canUpdate"]||(bool)data["canRecover"];restore.Enabled=(bool)data["canRestore"];
                details.Text=(string)data["onlineMessage"]+Environment.NewLine+(string)data["changelog"];
                backupPath=(string)data["backup"];backups.Enabled=!String.IsNullOrEmpty(backupPath)&&Directory.Exists(backupPath);
            } catch(Exception ex) {status.Text="Stav sa nepodarilo načítať. Skús kontrolu znova.";details.Text=ex.Message+Environment.NewLine+(string)e.Result;}
        };
        worker.RunWorkerAsync();
    }
}

