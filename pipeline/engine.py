import copy
import json
import re
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path
from .data import Memory, PROTECTED, digest, read_json, write_json, load_source, snapshot, encode_source, now, retry_io
from .qa import check, profile, reference, cross_check, semantic_row, validate_glossary
from .providers import Provider

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORK = ROOT/'pipeline-work'
DEFAULT_PACKAGE = ROOT/'dist/Aniimo-SK-3629693-strojovy-preklad'

def detect_build(game):
    # Invoke the existing detector: no second interpretation of game version strings.
    script=ROOT/'pipeline/detect.ps1'
    p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(script),'-GamePath',str(game)],capture_output=True,text=True,encoding='utf-8')
    if p.returncode or not re.fullmatch(r'\d+',p.stdout.strip()): raise ValueError('Cannot reliably detect game build')
    return p.stdout.strip()

def initialize(work=DEFAULT_WORK):
    work=Path(work)
    if (work/'memory.sqlite3').exists(): raise ValueError('Already initialized')
    source,_=load_source(ROOT/'source')
    full=read_json(ROOT/'translations.full.sk.json'); manual=read_json(ROOT/'translations.sk.json'); context=read_json(ROOT/'translations.by-id.sk.json')
    for k,r in context.items():
        if source.get(k)!=r['source']: raise ValueError('Stale manual override: '+k)
    for build in ('3616231','3629693'):
        snapshot(work,build,ROOT/('source-'+build),'Existing preserved EN source; see original-report and verification/check_new_originals.py')
    memory=Memory(work,create=True)
    try:
        with memory.db:
            for k,en in source.items():
                sk=context[k]['translation'] if k in context else full[en]
                protected=k in context or en in manual
                row=dict(key=k,source_en=en,source_hash=digest(en),translation_sk=sk,
                    status='manual_locked' if protected else 'needs_review',
                    origin='legacy_correction_unverified' if protected else 'legacy_import',
                    first_seen_build='3629693',last_seen_build='3629693',translation_version='0.03',
                    notes='Preserved without claiming human verification; historical first-seen unknown.',
                    suggestion=None,protected_status='manual_locked' if protected else None)
                memory.put(row,'Initial import: preserve exact released SK')
            memory.set_meta('build','3629693');memory.set_meta('version','0.03');memory.set_meta('schema','1')
        shutil.copy2(ROOT/'pipeline/glossary.seed.json',work/'glossary.json')
        memory.checkpoint()
    finally: memory.close()
    return {'imported':len(source),'build':'3629693','public_changes':False}

def diff(old,new):
    return {'UNCHANGED':[k for k in new if k in old and old[k]==new[k]],
            'NEW':[k for k in new if k not in old],
            'CHANGED':[k for k in new if k in old and old[k]!=new[k]],
            'REMOVED':[k for k in old if k not in new]}

def approved_matches(rows):
    choices={}
    for r in rows.values():
        # Context-specific entries are never reused for a different key by default.
        if r['status'] in PROTECTED and 'reuse_approved' in r['notes']:
            choices.setdefault(r['source_en'],set()).add(r['translation_sk'])
    return {en:next(iter(values)) for en,values in choices.items() if len(values)==1}

def update(work,build,source_dir,version,provider,dry_run=False,ref_config=None,allow_large=False):
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?',version): raise ValueError('Invalid numeric translation version')
    work=Path(work);memory=Memory(work)
    try:
        previous=memory.meta('build'); oldrows=memory.rows()
        if str(build)==previous:
            return {'status':'NO UPDATE REQUIRED','old_build':previous,'new_build':str(build)}
        new,new_meta=load_source(source_dir)
        _,old_meta=load_source(work/'builds'/previous/'source')
        if new_meta['_version']!=old_meta['_version']: raise ValueError('SOURCE_FORMAT_CHANGE: review extractor before continuing')
        old={k:r['source_en'] for k,r in oldrows.items() if r['status']!='removed'}
        changes=diff(old,new)
        if not allow_large and (len(changes['CHANGED'])+len(changes['REMOVED']))/max(len(old),1)>.25:
            raise ValueError('Major structure/content change >25%; inspect input before --allow-large-diff')
        tm=approved_matches(oldrows)
        report={'status':'DRY RUN' if dry_run else 'WAITING FOR XIU TEST','old_build':previous,'new_build':str(build),
                'counts':{k:len(v) for k,v in changes.items()},'existing_sk_preserved':len(changes['UNCHANGED']),
                'manual_verified_preserved':sum(oldrows[k]['status']=='manual_verified' for k in changes['UNCHANGED']),
                'manual_locked_preserved':sum(oldrows[k]['status']=='manual_locked' for k in changes['UNCHANGED']),
                'estimated_ai_translations':sum(new[k] not in tm for k in changes['NEW']+changes['CHANGED']),
                'translation_memory_matches':0,'ai_translations':0,'source_changed':len(changes['CHANGED'])}
        if dry_run: return dict(report,diff=changes)
        snapshot(work,build,source_dir,'Explicit EN input supplied to update; never read from translated live archive')
        glossary=read_json(work/'glossary.json'); newrows=copy.deepcopy(oldrows); audit=[]
        for kind in ('UNCHANGED','NEW','CHANGED','REMOVED'):
            for k in changes[kind]:
                oldr=oldrows.get(k); row=copy.deepcopy(oldr) if oldr else dict(key=k,source_en=new[k],source_hash=digest(new[k]),
                    translation_sk='',status='needs_review',origin='ai',first_seen_build=str(build),notes='',suggestion=None,protected_status=None)
                if kind=='UNCHANGED':
                    row['last_seen_build']=str(build);newrows[k]=row;continue
                if kind=='REMOVED':
                    if row['status'] in PROTECTED: row['protected_status']=row['status']
                    row['status']='removed'
                else:
                    en=new[k]
                    if en in tm:
                        candidate=tm[en];origin='approved_tm';report['translation_memory_matches']+=1
                    else:
                        candidate=provider.translate(k,en,glossary);origin='ai';report['ai_translations']+=1
                    row.update(source_en=en,source_hash=digest(en))
                    if kind=='CHANGED' or oldr:
                        # Do not overwrite even an unverified previous translation on source change.
                        if row['status'] in PROTECTED: row['protected_status']=row['status']
                        row.update(status='source_changed',suggestion=candidate)
                    else: row.update(translation_sk=candidate,status='ai_translated',origin=origin)
                row.update(last_seen_build=str(build),translation_version=version)
                newrows[k]=row;audit.append((row,kind+': '+('proposal from '+origin if kind!='REMOVED' else 'inactive'),oldr))
        issues,semantic,ref_status=run_qa(newrows,glossary,build,ref_config,provider)
        report.update(qa_errors=sum(i['severity']=='ERROR' for i in issues),qa_warnings=sum(i['severity']=='WARNING' for i in issues),
                      italian_semantic_warnings=len(semantic),reference=ref_status)
        # AI/extraction failure happens before transaction. QA errors persist reviewable work but block packaging.
        checkpoint=memory.checkpoint()
        with memory.db:
            for row,reason,oldr in audit: memory.put(row,reason,oldr)
            for k in changes['UNCHANGED']: memory.db.execute('UPDATE entries SET last_seen_build=? WHERE key=?',(str(build),k))
            memory.set_meta('build',build);memory.set_meta('version',version)
        report['checkpoint']=str(checkpoint)
        write_json(work/'reports'/('update-'+str(build)+'.json'),dict(report,diff=changes,
            changed=[{'key':k,'old_en':oldrows[k]['source_en'],'old_sk':oldrows[k]['translation_sk'],
                      'new_en':new[k],'old_status':oldrows[k]['status'],'new_ai_suggestion':newrows[k]['suggestion']} for k in changes['CHANGED']],
            new=[newrows[k] for k in changes['NEW']],removed=[oldrows[k] for k in changes['REMOVED']]))
        report['rc']=create_rc(work,version,ref_config,provider)
        return report
    finally: memory.close()

def run_qa(rows,glossary,build,ref_config=None,provider=None):
    validate_glossary(glossary)
    refs,warning=reference(ref_config,build);issues=[];semantic=[];matched=0;semantic_count=0
    for k,r in rows.items():
        if r['status']=='removed': continue
        checks=check(k,r['source_en'],r['translation_sk'],glossary);issues.extend(checks)
        if r['status']=='source_changed': issues.append({'key':k,'severity':'ERROR','code':'SOURCE_CHANGED_REQUIRES_MANUAL'})
        if r.get('suggestion') is not None:
            issues.extend(dict(x,code='SUGGESTION:'+x['code']) for x in check(k,r['source_en'],r['suggestion'],glossary))
        mapped=k in refs and refs[k]['source_sha256']==r['source_hash']
        if not mapped: continue
        matched+=1
        item=cross_check(k,r['source_en'],r['translation_sk'],refs,checks)
        if item: semantic.append(item)
        if provider and provider.config.get('semantic_argv'):
            try:
                proposal=provider.review(semantic_row(k,r['source_en'],r['translation_sk'],refs[k]['it'],[]))
                semantic_count+=1
                if proposal:
                    semantic.append(semantic_row(k,r['source_en'],r['translation_sk'],refs[k]['it'],proposal['problem'],proposal['suggested_sk'],proposal['confidence']))
            except Exception:
                warning='REFERENCE_UNAVAILABLE: semantic provider failed'; provider=None
    return issues,semantic,{'warning':warning,'mapped':matched,'mode':'heuristic_triage','semantic_model_reviewed':semantic_count,
                            'note':'No automatic SK edits. Null suggestion means human review needed, not a generated fix.'}

def manual(work,key,translation,status,notes=''):
    if status not in PROTECTED: raise ValueError('Manual status must be manual_verified or manual_locked')
    mem=Memory(work)
    try:
        old=mem.rows()[key]
        if old['status']=='removed': raise ValueError('Cannot activate removed key with manual correction')
        errors=[x for x in check(key,old['source_en'],translation,read_json(Path(work)/'glossary.json')) if x['severity']=='ERROR']
        if errors: raise ValueError('Correction fails technical QA: '+json.dumps(errors))
        mem.checkpoint(); row=dict(old,translation_sk=translation,status=status,origin='xiu_manual',notes=notes,suggestion=None,protected_status=status)
        with mem.db: mem.put(row,'Explicit manual correction',old)
    finally: mem.close()

def set_glossary(work,path):
    work=Path(work);value=validate_glossary(read_json(path));mem=Memory(work)
    try:
        checkpoint=mem.checkpoint()
        old=read_json(work/'glossary.json')
        write_json(work/'reports'/('glossary-'+uuid.uuid4().hex+'.json'),
                   {'old':old,'new':value,'origin':'xiu_manual','timestamp':now(),'checkpoint':str(checkpoint)})
        write_json(work/'glossary.json',value)
    finally: mem.close()
    return {'glossary':str(work/'glossary.json'),'checkpoint':str(checkpoint)}

def rc_seal(path):
    return digest(json.dumps({p.relative_to(path).as_posix():digest(p.read_bytes()) for p in sorted(path.rglob('*'))
                              if p.is_file() and p.name not in {'seal.json','approval.json'}},sort_keys=True))

def create_rc(work,version,ref_config=None,provider=None):
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?',version): raise ValueError('Invalid numeric translation version')
    work=Path(work);mem=Memory(work)
    try: rows=mem.rows();build=mem.meta('build')
    finally: mem.close()
    glossary=read_json(work/'glossary.json');issues,semantic,ref_status=run_qa(rows,glossary,build,ref_config,provider)
    source_dir=work/'builds'/build/'source'
    source,_=load_source(source_dir)
    snapmeta=read_json(source_dir.parent/'metadata.json')
    if any(digest((source_dir/n).read_bytes())!=h for n,h in snapmeta['hashes'].items()): raise ValueError('Corrupt snapshot')
    active={k:r['translation_sk'] for k,r in rows.items() if r['status']!='removed'}
    if set(active)!=set(source): raise ValueError('Active keys differ from snapshot')
    if any(rows[k]['source_en']!=en or rows[k]['source_hash']!=digest(en) for k,en in source.items()):
        raise ValueError('Translation Memory source differs from immutable snapshot')
    parent=work/'rc';parent.mkdir(exist_ok=True)
    index=1
    while (parent/(version+'-RC'+str(index))).exists(): index+=1
    rcid=version+'-RC'+str(index);target=parent/rcid;stage=parent/('.'+uuid.uuid4().hex)
    try:
        stage.mkdir()
        encode_source(source_dir,active,stage/'data')
        write_json(stage/'entries.json',rows);write_json(stage/'glossary.json',glossary)
        write_json(stage/'qa.json',issues);write_json(stage/'semantic-review.json',semantic)
        write_json(stage/'token-profile.json',profile(source))
        reportfile=work/'reports'/('update-'+build+'.json')
        report=read_json(reportfile) if reportfile.exists() else {'counts':{'NEW':0,'CHANGED':0,'REMOVED':0,'UNCHANGED':len(active)},'diff':{},'note':'Baseline RC; no build update processed'}
        write_json(stage/'update-report.json',report)
        for name in ('NEW','CHANGED','REMOVED'):
            write_json(stage/(name+'.json'),[rows[k] for k in report.get('diff',{}).get(name,[])])
        write_json(stage/'SOURCE_CHANGED.json',[r for r in rows.values() if r['status']=='source_changed'])
        errors=sum(i['severity']=='ERROR' for i in issues);warnings=sum(i['severity']=='WARNING' for i in issues)
        write_json(stage/'rc.json',{'rc':rcid,'version':version,'build':build,'created':now(),
                   'status':'QA BLOCKED' if errors else 'WAITING FOR XIU TEST','qa_errors':errors,'qa_warnings':warnings,'reference':ref_status})
        (stage/'CHANGELOG.md').write_text(f'ANIIMO Slovenčina {version} — {rcid}\n\nBuild {build}.\n'+
             f'Kontrolovaných {len(active)} položiek; QA ERROR {errors}, WARNING {warnings}.\n'+
             'Zachované existujúce preklady. Rozsah zmien je v update-report.json, ak vznikol update.\n'+
             'RC nebolo automaticky schválené ani publikované; herné testovanie vykoná Xiu.\n',encoding='utf-8')
        write_json(stage/'seal.json',{'sha256':rc_seal(stage)})
        retry_io(lambda: stage.rename(target))
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return str(target)

def validate_rc(rc):
    rc=Path(rc);meta=read_json(rc/'rc.json')
    if rc_seal(rc)!=read_json(rc/'seal.json')['sha256']: raise ValueError('RC modified after sealing; create a new RC')
    rows=read_json(rc/'entries.json');glossary=read_json(rc/'glossary.json')
    if any(r['key']!=k or r['source_hash']!=digest(r['source_en']) for k,r in rows.items()):
        raise ValueError('RC source hash/key mismatch')
    issues,_,_=run_qa(rows,glossary,meta['build'])
    if any(i['severity']=='ERROR' for i in issues): raise ValueError('QA ERROR: release blocked')
    active={k:r['translation_sk'] for k,r in rows.items() if r['status']!='removed'}
    actual,_=load_source(rc/'data')
    if active!=actual: raise ValueError('RC data differs from reviewed entries')
    return meta

def approve(rc,statement):
    rc=Path(rc);meta=validate_rc(rc)
    if statement!='APPROVE RELEASE '+meta['rc']: raise ValueError('Explicit approval of exact RC required')
    write_json(rc/'approval.json',{'statement':statement,'approver':'Xiu','rc_sha256':rc_seal(rc),'timestamp':now()})
    return {'approved':meta['rc'],'published':False}

def package(rc,template,output,base_url=None,test=False):
    rc=Path(rc);template=Path(template);output=Path(output);meta=validate_rc(rc)
    if not test:
        approval=read_json(rc/'approval.json')
        if approval.get('statement')!='APPROVE RELEASE '+meta['rc'] or approval.get('rc_sha256')!=rc_seal(rc):
            raise ValueError('Approval missing or stale')
        if not base_url or not base_url.startswith('https://'): raise ValueError('HTTPS release URL required')
    manifest=read_json(template/'manifest.json')
    if str(manifest['gameBuild'])!=meta['build']:
        raise ValueError('INSTALLER_BASELINE_REQUIRED: new game build needs reviewed compatible template/installer')
    _,textmeta=load_source(rc/'data')
    if 'textVersion' in manifest and manifest['textVersion']!=textmeta['_version']:
        raise ValueError('Localization format differs from trusted template')
    if 'records' in manifest and manifest['records']!=textmeta['_count']:
        raise ValueError('Localization keys/count differ from trusted template; baseline review required')
    if output.exists(): raise ValueError('Output exists; never overwrite release')
    # Allowlist comes from existing trusted installer manifest. Only localization binaries are regenerated.
    stage=output.with_name('.'+output.name+'-'+uuid.uuid4().hex);stage.mkdir(parents=True)
    try:
        (stage/'data').mkdir()
        for name,h in manifest['payloadFiles'].items():
            if Path(name).name!=name or '\\' in name or '/' in name: raise ValueError('Unsafe payload name')
            src=template/'data'/name
            if digest(src.read_bytes())!=h: raise ValueError('Template hash mismatch')
            shutil.copy2(rc/'data'/name if name in {'NewTextMap_en.json','Compress_en.bin'} else src,stage/'data'/name)
        manifest.update(translationVersion=meta['version'],releaseVersion=meta['rc'] if test else meta['version'],releaseChannel='rc' if test else 'stable',gameTested=False)
        rcrows=read_json(rc/'entries.json')
        manifest.update(records=textmeta['_count'],textVersion=textmeta['_version'],
                        changedRecords=sum(r['translation_sk']!=r['source_en'] for r in rcrows.values() if r['status']!='removed'))
        manifest['payloadFiles']={n:digest((stage/'data'/n).read_bytes()) for n in manifest['payloadFiles']}
        write_json(stage/'manifest.json',manifest)
        archive=stage/('Aniimo-Slovencina-'+(meta['rc'] if test else meta['version'])+'.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            z.write(stage/'manifest.json','manifest.json')
            for n in manifest['payloadFiles']: z.write(stage/'data'/n,'data/'+n)
        sha=digest(archive.read_bytes());archive.with_suffix('.zip.sha256').write_text(sha+'  '+archive.name+'\n',encoding='ascii')
        shutil.copy2(rc/'CHANGELOG.md',stage/'CHANGELOG.md')
        if not test:
            write_json(stage/'version.json',{'translation_version':meta['version'],'game_build':meta['build'],
                'package_url':base_url.rstrip('/')+'/'+archive.name,'sha256':sha,'status':'stable',
                'changelog':['Podpora zostavy '+meta['build']+'.','Schválený kandidát '+meta['rc']+'.']})
        write_json(stage/'production-proof.json',{'rc':meta['rc'],'rc_sha256':rc_seal(rc),'test_only':test,'created':now()})
        retry_io(lambda: stage.rename(output))
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return {'output':str(output),'sha256':sha,'published':False,'test_only':test}
