import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
import zipfile
import re
import uuid
from contextlib import closing
from pathlib import Path
from .data import Memory, read_json, write_json, digest, load_source, snapshot, now
from .engine import ROOT, DEFAULT_WORK, DEFAULT_PACKAGE, initialize, detect_build, update, manual, create_rc, approve, package, run_qa, set_glossary
from .providers import Provider

def extract(game,destination,expected_hash):
    build=detect_build(game)
    assert_cache_build(game,build)
    archive=Path(game)/'Aniimo_Data/cvs/res/lua/LuaScripts.xdf'
    if not expected_hash or digest(archive.read_bytes())!=expected_hash:
        raise ValueError('EN_ORIGINAL_PROOF_REQUIRED: supply independently verified original XDF SHA-256; never extract translated game data')
    with zipfile.ZipFile(archive) as z:
        for name in ('NewTextMap_en.json','Compress_en.bin'):
            entry='xfs/luascripts/Data/I18N/'+name
            matches=[x for x in z.infolist() if x.filename==entry]
            if len(matches)!=1 or matches[0].file_size>128*1024*1024: raise ValueError('Unknown archive structure')
            (Path(destination)/name).write_bytes(z.read(matches[0]))
    load_source(destination)
    return build

def assert_cache_build(game,build):
    cache=(Path(game)/'Aniimo_Data/cvs/res/lua/LuaCacheVer.txt').read_text(encoding='utf-8-sig')
    match=re.match(r'^1\.0\.(\d+),',cache)
    if not match: raise ValueError('Unknown Lua cache version format')
    if match.group(1)!=str(build):
        raise ValueError('GAME_UPDATE_INCOMPLETE: game build '+str(build)+' / Lua cache '+match.group(1)+'. Finish game update and verify original EN before extraction.')

def main(argv=None):
    p=argparse.ArgumentParser(description='ANIIMO EN -> SK production pipeline. Never publishes.')
    p.add_argument('--work',type=Path,default=DEFAULT_WORK)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    u=sub.add_parser('update');u.add_argument('--game',type=Path,required=True)
    u.add_argument('--source-dir',type=Path);u.add_argument('--build');u.add_argument('--original-xdf-sha256')
    u.add_argument('--version',default='0.04');u.add_argument('--dry-run',action='store_true');u.add_argument('--allow-large-diff',action='store_true')
    u.add_argument('--config',type=Path,default=ROOT/'pipeline/config.local.json')
    m=sub.add_parser('manual');m.add_argument('--key',required=True);m.add_argument('--text',required=True)
    m.add_argument('--status',choices=['manual_verified','manual_locked'],required=True);m.add_argument('--notes',default='')
    q=sub.add_parser('qa');q.add_argument('--config',type=Path,default=ROOT/'pipeline/config.local.json')
    r=sub.add_parser('rc');r.add_argument('--version',default='0.04');r.add_argument('--config',type=Path,default=ROOT/'pipeline/config.local.json')
    a=sub.add_parser('approve');a.add_argument('--rc',type=Path,required=True);a.add_argument('--statement',required=True)
    b=sub.add_parser('package');b.add_argument('--rc',type=Path,required=True);b.add_argument('--template',type=Path,default=DEFAULT_PACKAGE)
    b.add_argument('--output',type=Path,required=True);b.add_argument('--base-url');b.add_argument('--test-only',action='store_true')
    rb=sub.add_parser('restore-memory');rb.add_argument('--checkpoint',type=Path,required=True)
    g=sub.add_parser('glossary-set');g.add_argument('--file',type=Path,required=True)
    args=p.parse_args(argv)
    try:
        cfg=read_json(args.config) if hasattr(args,'config') and args.config.exists() else {'provider':{'type':'local'}}
        provider=Provider(cfg.get('provider',{}),ROOT)
        if args.command=='init': result=initialize(args.work)
        elif args.command=='update':
            build=args.build or detect_build(args.game)
            if args.source_dir and not args.build: raise ValueError('--source-dir requires explicit --build')
            mem=Memory(args.work);same=mem.meta('build')==build;mem.close()
            if same: result={'status':'NO UPDATE REQUIRED','build':build}
            elif args.source_dir:
                result=update(args.work,build,args.source_dir,args.version,provider,args.dry_run,cfg.get('italian'),args.allow_large_diff)
            else:
                assert_cache_build(args.game,build)
                if not args.original_xdf_sha256:
                    raise ValueError('NEW BUILD DETECTED: '+build+'. EN_ORIGINAL_PROOF_REQUIRED: supply verified original XDF SHA-256 or --source-dir with --build.')
                tmp=args.work/('.extract-'+uuid.uuid4().hex);tmp.mkdir(parents=True)
                try:
                    extracted=extract(args.game,tmp,args.original_xdf_sha256)
                    if extracted!=build: raise ValueError('Game build changed during extraction')
                    result=update(args.work,build,tmp,args.version,provider,args.dry_run,cfg.get('italian'),args.allow_large_diff)
                finally:
                    if tmp.resolve().parent!=args.work.resolve():raise ValueError('Unsafe extraction cleanup path')
                    shutil.rmtree(tmp)
        elif args.command=='manual':
            manual(args.work,args.key,args.text,args.status,args.notes);result={'saved':args.key,'status':args.status}
        elif args.command=='rc': result={'rc':create_rc(args.work,args.version,cfg.get('italian'),provider)}
        elif args.command=='qa':
            mem=Memory(args.work)
            try: issues,semantic,ref=run_qa(mem.rows(),read_json(args.work/'glossary.json'),mem.meta('build'),cfg.get('italian'),provider)
            finally: mem.close()
            write_json(args.work/'reports/qa.json',issues);write_json(args.work/'reports/semantic-review.json',semantic)
            result={'errors':sum(x['severity']=='ERROR' for x in issues),'warnings':sum(x['severity']=='WARNING' for x in issues),'semantic_review':len(semantic),'reference':ref}
            write_json(args.work/'reports/qa-summary.json',result)
        elif args.command=='approve': result=approve(args.rc,args.statement)
        elif args.command=='glossary-set':result=set_glossary(args.work,args.file)
        elif args.command=='package': result=package(args.rc,args.template,args.output,args.base_url,args.test_only)
        elif args.command=='restore-memory':
            cp=args.checkpoint.resolve();root=(args.work/'checkpoints').resolve()
            if cp.parent!=root or cp.suffix!='.sqlite3': raise ValueError('Choose a local checkpoint')
            with closing(sqlite3.connect('file:'+cp.as_posix()+'?mode=ro',uri=True)) as db:
                if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise ValueError('Corrupt checkpoint')
                mem=Memory(args.work)
                try: saved=mem.checkpoint();db.backup(mem.db)
                finally: mem.close()
            glossary=cp.with_suffix('.glossary.json')
            if glossary.exists(): write_json(args.work/'glossary.json',read_json(glossary))
            result={'restored':str(cp),'previous_state':str(saved)}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except Exception as e:
        # Diagnostics intentionally omit provider stderr and credentials.
        result={'status':'STOPPED','error_type':type(e).__name__,'error':str(e),'published':False,'timestamp':now()}
        if not getattr(args,'dry_run',False): write_json(args.work/'reports/last-failure.json',result)
        print(json.dumps(result,ensure_ascii=False,indent=2),file=sys.stderr)
        return 1

if __name__=='__main__': sys.exit(main())
