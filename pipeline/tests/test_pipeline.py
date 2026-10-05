import copy
import json
import shutil
import sqlite3
import struct
import tempfile
import unittest
import uuid
from pathlib import Path
from pipeline.data import Memory, digest, write_json, read_json, snapshot, load_source
from pipeline.engine import update, diff, manual, create_rc, approve, package, validate_rc, run_qa, set_glossary
from pipeline.qa import check, reference, cross_check

EMPTY={'schema':1,'terms':[]}

def source(path,rows):
    path.mkdir(parents=True,exist_ok=True);raw=bytearray(struct.pack('<I',1));mapping={'_version':1,'_count':len(rows)}
    for k,v in rows.items():
        data=v.encode();mapping[k]=[len(raw),len(data)];raw.extend(data)
    (path/'Compress_en.bin').write_bytes(raw);write_json(path/'NewTextMap_en.json',mapping)
    return path

def seed(work,src,rows,build='100'):
    snapshot(work,build,src,'synthetic test')
    m=Memory(work,create=True)
    with m.db:
        for k,(en,sk,status) in rows.items():
            m.put(dict(key=k,source_en=en,source_hash=digest(en),translation_sk=sk,status=status,origin='fixture',
                first_seen_build=build,last_seen_build=build,translation_version='0.03',notes='',suggestion=None,
                protected_status=status if status.startswith('manual') else None),'seed')
        m.set_meta('build',build);m.set_meta('version','0.03')
    m.close();write_json(work/'glossary.json',EMPTY)

class FakeProvider:
    config={}
    def __init__(self,values=None,fail=False):self.values=values or {};self.calls=[];self.fail=fail
    def translate(self,key,en,glossary):
        self.calls.append(key)
        if self.fail: raise RuntimeError('provider failure')
        return self.values.get(key,'Nový preklad')

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(__file__).resolve().parent/'output'/uuid.uuid4().hex;self.root.mkdir(parents=True);self.work=self.root/'work'
        self.en={'1':'Cook','2':'Take {0} items.'}
        self.src=source(self.root/'source',self.en)
        seed(self.work,self.src,{'1':('Cook','Variť','manual_locked'),'2':('Take {0} items.','Vezmi {0} predmetov.','manual_verified')})
    def tearDown(self):
        allowed=Path(__file__).resolve().parent/'output'
        assert self.root.resolve().parent==allowed.resolve()
        shutil.rmtree(self.root)
    def rows(self):
        m=Memory(self.work)
        try:return m.rows()
        finally:m.close()
    def test_A_same_build(self):
        p=FakeProvider(fail=True);r=update(self.work,'100',self.src,'0.04',p)
        self.assertEqual(r['status'],'NO UPDATE REQUIRED');self.assertEqual(p.calls,[])
    def test_B_new_only_and_D_locked_preserved(self):
        new=source(self.root/'new',dict(self.en,**{'3':'New text'}));p=FakeProvider()
        r=update(self.work,'101',new,'0.04',p)
        self.assertEqual(p.calls,['3']);self.assertEqual(self.rows()['1']['translation_sk'].encode(),'Variť'.encode())
        self.assertEqual(self.rows()['2']['status'],'manual_verified');self.assertEqual(r['counts']['NEW'],1)
    def test_C_E_changed_locked(self):
        new=source(self.root/'new',dict(self.en,**{'1':'Cook food'}));p=FakeProvider({'1':'Variť jedlo'})
        update(self.work,'101',new,'0.04',p,allow_large=True)
        row=self.rows()['1'];self.assertEqual(row['translation_sk'],'Variť');self.assertEqual(row['status'],'source_changed')
        self.assertEqual(row['protected_status'],'manual_locked');self.assertEqual(row['suggestion'],'Variť jedlo')
        m=Memory(self.work);a=m.db.execute("SELECT old_sk FROM audit WHERE reason LIKE 'CHANGED%'").fetchone();m.close()
        self.assertEqual(a[0],'Variť')
    def test_F_removed_history(self):
        new=source(self.root/'new',{'1':'Cook'})
        r=update(self.work,'101',new,'0.04',FakeProvider(),allow_large=True)
        self.assertEqual(self.rows()['2']['status'],'removed');active,_=load_source(Path(r['rc'])/'data');self.assertNotIn('2',active)
    def test_G_placeholder(self):
        self.assertTrue(any(x['severity']=='ERROR' for x in check('1','Take {0}','Vezmi {1}',EMPTY)))
        self.assertTrue(any(x['severity']=='ERROR' for x in check('1','#kRaw/GamepadRightShoulder#z','#kRaw/GamepadrightShoulder#z',EMPTY)))
    def test_H_markup(self):
        self.assertTrue(any(x['code']=='MARKUP' for x in check('1','<b>Text</b>','<b>Text',EMPTY)))
        self.assertFalse(any(x['severity']=='ERROR' for x in check('1','<customRichText(a,b)>%','<customRichText(a,b)>%',EMPTY)))
    def test_I_provider_failure_atomic(self):
        before=(self.work/'memory.sqlite3').read_bytes();new=source(self.root/'new',dict(self.en,**{'3':'New'}))
        with self.assertRaises(RuntimeError):update(self.work,'101',new,'0.04',FakeProvider(fail=True))
        self.assertEqual(before,(self.work/'memory.sqlite3').read_bytes());self.assertFalse((self.work/'rc').exists())
    def test_J_reference_unavailable(self):
        r=update(self.work,'101',self.src,'0.04',FakeProvider(),ref_config={'enabled':True,'license':'unknown'})
        self.assertIn('REFERENCE_UNAVAILABLE',r['reference']['warning']);self.assertEqual(r['qa_errors'],0)
    def test_K_L_approval_package_sha_manifest(self):
        rc=Path(create_rc(self.work,'0.04'));template=self.root/'template';(template/'data').mkdir(parents=True)
        for n in ('NewTextMap_en.json','Compress_en.bin'):shutil.copy2(self.src/n,template/'data'/n)
        write_json(template/'manifest.json',{'gameBuild':100,'translationVersion':'0.03','sourceFiles':{},
             'payloadFiles':{n:digest((template/'data'/n).read_bytes()) for n in ('NewTextMap_en.json','Compress_en.bin')}})
        with self.assertRaises(FileNotFoundError):package(rc,template,self.root/'out','https://example.test/v0.04')
        self.assertFalse((self.root/'out').exists())
        with self.assertRaises(ValueError):approve(rc,'APPROVE RELEASE 0.04-RC2')
        approve(rc,'APPROVE RELEASE 0.04-RC1')
        result=package(rc,template,self.root/'out','https://example.test/v0.04')
        feed=read_json(self.root/'out/version.json');self.assertEqual(feed['sha256'],result['sha256'])
        self.assertEqual(digest((self.root/'out/Aniimo-Slovencina-0.04.zip').read_bytes()),result['sha256'])
        self.assertFalse(result['published']);self.assertTrue((self.root/'out/CHANGELOG.md').exists())
    def test_dry_run_no_mutation(self):
        new=source(self.root/'new',dict(self.en,**{'3':'New'}));before={p.relative_to(self.work):digest(p.read_bytes()) for p in self.work.rglob('*') if p.is_file()}
        p=FakeProvider();update(self.work,'101',new,'0.04',p,dry_run=True)
        after={p.relative_to(self.work):digest(p.read_bytes()) for p in self.work.rglob('*') if p.is_file()}
        self.assertEqual(before,after);self.assertEqual(p.calls,[])
    def test_snapshot_immutable(self):
        new=source(self.root/'new',{'1':'Different'})
        with self.assertRaises(ValueError):snapshot(self.work,'100',new,'test')
    def test_bad_encoding_duplicates_bounds(self):
        (self.src/'NewTextMap_en.json').write_text('{"1":[4,1],"1":[4,1]}')
        with self.assertRaises(ValueError):load_source(self.src)
    def test_rc_mutation_invalidates_approval(self):
        rc=Path(create_rc(self.work,'0.04'));approve(rc,'APPROVE RELEASE 0.04-RC1')
        (rc/'CHANGELOG.md').write_text('changed')
        with self.assertRaises(ValueError):validate_rc(rc)
    def test_manual_checkpoint_audit(self):
        manual(self.work,'1','Uvariť','manual_verified')
        self.assertEqual(self.rows()['1']['translation_sk'],'Uvariť');self.assertTrue(list((self.work/'checkpoints').glob('*.sqlite3')))
    def test_tm_requires_explicit_reuse(self):
        manual(self.work,'1','Variť','manual_verified',notes='reuse_approved')
        new=source(self.root/'new',dict(self.en,**{'3':'Cook'}));p=FakeProvider(fail=True)
        r=update(self.work,'101',new,'0.04',p);self.assertEqual(p.calls,[]);self.assertEqual(r['translation_memory_matches'],1)
    def test_numbers_escapes_duplicate_tokens(self):
        for en,sk in [('20%','30%'),('a\\n','a'),('{0}','{0}{0}')]:
            self.assertTrue(any(x['severity']=='ERROR' for x in check('1',en,sk,EMPTY)))
    def test_wrong_build_package_blocked(self):
        rc=Path(create_rc(self.work,'0.04'));t=self.root/'template';t.mkdir();write_json(t/'manifest.json',{'gameBuild':999})
        with self.assertRaisesRegex(ValueError,'BASELINE'):package(rc,t,self.root/'out',test=True)
    def test_qa_errors_block_approval_and_test_package(self):
        new=source(self.root/'new',dict(self.en,**{'3':'Take {0}'}))
        r=update(self.work,'101',new,'0.04',FakeProvider({'3':'Vezmi {1}'}))
        self.assertGreater(r['qa_errors'],0)
        with self.assertRaisesRegex(ValueError,'QA ERROR'):approve(r['rc'],'APPROVE RELEASE 0.04-RC1')
        with self.assertRaisesRegex(ValueError,'QA ERROR'):package(r['rc'],self.root,self.root/'out',test=True)
    def test_reference_requires_exact_key_and_hash(self):
        refs={'1':{'source_sha256':digest('Cook'),'it':'Cucinare'}}
        self.assertIsNotNone(cross_check('1','Cook','Cook',refs,[{'severity':'WARNING','code':'ENGLISH'}]))
        self.assertIsNone(cross_check('2','Cook','Cook',refs,[]))
        self.assertIsNone(cross_check('1','Cook now','Cook',refs,[]))
    def test_semantic_suggestion_does_not_overwrite(self):
        import csv
        path=self.root/'it.csv'
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(['key','source_sha256','it']);w.writerow(['1',digest('Cook'),'Cucinare'])
        config={'enabled':True,'license':'MIT','license_reviewed':True,'game_build':'100','csv':str(path),'sha256':digest(path.read_bytes())}
        class Reviewer:
            config={'semantic_argv':['fixture']}
            def review(self,row):return {'problem':'fixture','suggested_sk':'Uvariť','confidence':'MEDIUM'}
        before=self.rows();issues,report,ref=run_qa(before,EMPTY,'100',config,Reviewer())
        self.assertEqual(report[0]['suggested_sk'],'Uvariť');self.assertEqual(before,self.rows())
        config['game_build']='999';self.assertIn('build mismatch',reference(config,'100')[1])
    def test_corrupt_tm_detected(self):
        m=Memory(self.work)
        with m.db:m.db.execute("UPDATE entries SET source_hash='bad' WHERE key='1'")
        m.close()
        with self.assertRaises(ValueError):Memory(self.work)
    def test_glossary_checkpoint(self):
        file=self.root/'g.json';write_json(file,EMPTY)
        result=set_glossary(self.work,file)
        self.assertTrue(Path(result['checkpoint']).with_suffix('.glossary.json').exists())
    def test_snapshot_tamper_blocks_rc(self):
        (self.work/'builds/100/source/Compress_en.bin').write_bytes(b'bad')
        with self.assertRaises(ValueError):create_rc(self.work,'0.04')
    def test_ai_failure_after_one_success_preserves_memory(self):
        new=source(self.root/'new',dict(self.en,**{'3':'New','4':'Other'}))
        class FailSecond(FakeProvider):
            def translate(self,key,en,glossary):
                if key=='4': raise RuntimeError('second failure')
                return 'Nový'
        before=self.rows()
        with self.assertRaises(RuntimeError):update(self.work,'101',new,'0.04',FailSecond())
        self.assertEqual(before,self.rows())
    def test_game_cache_build_mismatch(self):
        from pipeline.cli import assert_cache_build
        game=self.root/'game';folder=game/'Aniimo_Data/cvs/res/lua';folder.mkdir(parents=True)
        (folder/'LuaCacheVer.txt').write_text('1.0.100,0,hash')
        with self.assertRaisesRegex(ValueError,'GAME_UPDATE_INCOMPLETE'):assert_cache_build(game,'101')
        assert_cache_build(game,'100')
    def test_unknown_source_format_version_stops(self):
        new=source(self.root/'new',self.en);mapping=read_json(new/'NewTextMap_en.json');mapping['_version']=2
        write_json(new/'NewTextMap_en.json',mapping);b=(new/'Compress_en.bin').read_bytes();(new/'Compress_en.bin').write_bytes(struct.pack('<I',2)+b[4:])
        with self.assertRaisesRegex(ValueError,'SOURCE_FORMAT_CHANGE'):update(self.work,'101',new,'0.04',FakeProvider())

if __name__=='__main__':unittest.main()
